"""Summarize fixed-camera natural-flow signals over fixed wall-clock windows.

This module is deliberately estimator-agnostic. Dense flow, feature tracking,
registration, or a human annotation pipeline can produce the timestamped input
signals. This layer makes the long-horizon evaluation rule reproducible:

* windows have a fixed duration in seconds rather than a fraction of the clip;
* every axis retains its own applicability and coverage;
* direction uses time-weighted signed transport, not motion magnitude;
* an aggregate leaderboard score is never produced;
* failure thresholds are optional external calibration artifacts.

Input JSON can be a single record, a list of records, or ``{"records": [...]}``.
Each record contains identifying fields and a ``samples`` list. A sample must
have ``t_s`` and may contain any of these signals:

``support_error_px``
    Registration residual/displacement on rigid support. Lower is better.
``dynamic_speed_px_s``
    Motion magnitude in the intended-motion region. This establishes presence,
    not correctness. Higher is not unconditionally better.
``signed_path_speed_px_s``
    Dynamic-region motion projected on the annotated path. Positive is the
    requested direction; negative is the opposite direction.
``incoming_flux_px_s``
    Signed boundary-crossing flux. Positive points into the annotated target.
``long_lag_recurrence``
    Long-lag recurrence similarity in [0, 1]. Higher means more replay-like.
``reset_seam_score``
    Reset/seam evidence in [0, 1]. Higher means more seam-like.

Records also require a ``medium`` identifier. Threshold JSON may be a flat axis
mapping, or ``{"default": {...}, "by_medium": {"ocean_waves": {...}}}``.
The latter keeps medium-specific replay and motion floors explicit while
sharing any axis threshold that has a defensible common calibration.

The script reports descriptive trajectories without thresholds. Supplying a
threshold JSON additionally reports first failure and longest failing run.
Threshold selection belongs to held-out real/corruption calibration.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import median
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


PROTOCOL_VERSION = "snf-long-trajectory-0.1"

AXES = {
    "support_stability": {
        "signal": "support_error_px",
        "polarity": "lower",
        "threshold_key": "max",
    },
    "flow_presence": {
        "signal": "dynamic_speed_px_s",
        "polarity": "higher",
        "threshold_key": "min",
    },
    "directional_transport": {
        "signal": "signed_path_speed_px_s",
        "polarity": "higher",
        "threshold_key": "min",
    },
    "incoming_transport": {
        "signal": "incoming_flux_px_s",
        "polarity": "higher",
        "threshold_key": "min",
    },
    "non_recurrence": {
        "signal": "long_lag_recurrence",
        "polarity": "lower",
        "threshold_key": "max",
    },
    "reset_continuity": {
        "signal": "reset_seam_score",
        "polarity": "lower",
        "threshold_key": "max",
    },
}


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def make_windows(duration_s: float, window_s: float, stride_s: float) -> List[Tuple[float, float]]:
    """Return complete half-open windows [start, end) in wall-clock seconds."""
    if not (_finite_number(duration_s) and duration_s > 0):
        raise ValueError("duration_s must be a positive finite number")
    if not (_finite_number(window_s) and window_s > 0):
        raise ValueError("window_s must be a positive finite number")
    if not (_finite_number(stride_s) and stride_s > 0):
        raise ValueError("stride_s must be a positive finite number")
    if duration_s + 1e-9 < window_s:
        raise ValueError("duration_s is shorter than one complete analysis window")
    windows = []
    start = 0.0
    while start + window_s <= duration_s + 1e-9:
        windows.append((round(start, 9), round(start + window_s, 9)))
        start += stride_s
    return windows


def _quantile(values: Sequence[float], q: float) -> float:
    vals = sorted(float(v) for v in values)
    if not vals:
        raise ValueError("quantile requires at least one value")
    pos = (len(vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - pos) + vals[hi] * (pos - lo)


def _time_weights(times: Sequence[float], start: float, end: float) -> List[float]:
    """Voronoi-duration weights for irregular point samples within a window."""
    if not times:
        return []
    if len(times) == 1:
        return [end - start]
    bounds = [start]
    bounds.extend((times[i - 1] + times[i]) / 2.0 for i in range(1, len(times)))
    bounds.append(end)
    return [max(0.0, bounds[i + 1] - bounds[i]) for i in range(len(times))]


def _weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    total = sum(weights)
    if total <= 0:
        return float("nan")
    return sum(v * w for v, w in zip(values, weights)) / total


def _theil_sen(points: Sequence[Tuple[float, float]]) -> Optional[float]:
    slopes = []
    for i, (x0, y0) in enumerate(points):
        for x1, y1 in points[i + 1 :]:
            if x1 != x0:
                slopes.append((y1 - y0) / (x1 - x0))
    return float(median(slopes)) if slopes else None


def _validate_samples(samples: Any, duration_s: float) -> List[Dict[str, Any]]:
    if not isinstance(samples, list) or not samples:
        raise ValueError("samples must be a non-empty list")
    clean = []
    last_t = -math.inf
    for i, sample in enumerate(samples):
        if not isinstance(sample, dict) or not _finite_number(sample.get("t_s")):
            raise ValueError(f"sample {i} needs a finite t_s")
        t_s = float(sample["t_s"])
        if t_s < 0 or t_s > duration_s + 1e-9:
            raise ValueError(f"sample {i} t_s is outside [0, duration_s]")
        if t_s <= last_t:
            raise ValueError("sample timestamps must be strictly increasing")
        last_t = t_s
        row = {"t_s": t_s}
        for spec in AXES.values():
            key = spec["signal"]
            if key in sample and sample[key] is not None:
                if not _finite_number(sample[key]):
                    raise ValueError(f"sample {i} has non-finite {key}")
                value = float(sample[key])
                if key in ("support_error_px", "dynamic_speed_px_s") and value < 0:
                    raise ValueError(f"sample {i} has negative {key}")
                if key in ("long_lag_recurrence", "reset_seam_score") and not 0 <= value <= 1:
                    raise ValueError(f"sample {i} has {key} outside [0, 1]")
                row[key] = value
        clean.append(row)
    return clean


def _applicability(record: Mapping[str, Any], axis: str) -> Tuple[str, Optional[str]]:
    entry = record.get("applicability", {}).get(axis)
    if entry is None:
        return "applicable", None
    if isinstance(entry, str):
        return entry, None
    if not isinstance(entry, dict):
        raise ValueError(f"applicability.{axis} must be a string or object")
    return entry.get("status", "applicable"), entry.get("reason")


def _window_rows(samples: Sequence[Mapping[str, Any]], signal: str,
                 windows: Sequence[Tuple[float, float]], min_samples: int,
                 signed: bool = False) -> List[Dict[str, Any]]:
    rows = []
    for wi, (start, end) in enumerate(windows):
        chosen = [s for s in samples if start <= s["t_s"] < end and signal in s]
        values = [float(s[signal]) for s in chosen]
        times = [float(s["t_s"]) for s in chosen]
        row: Dict[str, Any] = {
            "window_index": wi,
            "start_s": start,
            "end_s": end,
            "n_samples": len(values),
            "status": "scored" if len(values) >= min_samples else "unscorable",
        }
        if len(values) < min_samples:
            row["reason"] = "insufficient_samples"
            rows.append(row)
            continue
        weights = _time_weights(times, start, end)
        row.update({
            "mean": _weighted_mean(values, weights),
            "median": float(median(values)),
            "p05": _quantile(values, 0.05),
            "p95": _quantile(values, 0.95),
            "min": min(values),
            "max": max(values),
        })
        if signed:
            abs_transport = sum(abs(v) * w for v, w in zip(values, weights))
            net_transport = sum(v * w for v, w in zip(values, weights))
            row["net_transport"] = net_transport
            row["absolute_transport"] = abs_transport
            row["directional_persistence"] = (
                net_transport / abs_transport if abs_transport > 1e-12 else None
            )
            total_w = sum(weights)
            row["wrong_way_fraction"] = (
                sum(w for v, w in zip(values, weights) if v < 0) / total_w
                if total_w > 0 else None
            )
        rows.append(row)
    return rows


def _window_value(axis: str, row: Mapping[str, Any]) -> Optional[float]:
    if row.get("status") != "scored":
        return None
    if axis in ("directional_transport", "incoming_transport"):
        return row.get("directional_persistence")
    if axis in ("non_recurrence", "reset_continuity", "support_stability"):
        return row.get("p95")
    return row.get("median")


def _failure_summary(axis: str, rows: Sequence[Mapping[str, Any]],
                     threshold: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    scored = [(r, _window_value(axis, r)) for r in rows]
    scored = [(r, v) for r, v in scored if v is not None]
    if not scored:
        return {"calibrated": bool(threshold), "first_failure_s": None,
                "longest_failing_run": 0}
    if threshold is None:
        return {"calibrated": False, "first_failure_s": None,
                "longest_failing_run": None}
    spec = AXES[axis]
    key = spec["threshold_key"]
    if key not in threshold or not _finite_number(threshold[key]):
        raise ValueError(f"threshold for {axis} requires finite '{key}'")
    limit = float(threshold[key])
    if spec["polarity"] == "lower":
        failed = [(r, v > limit) for r, v in scored]
    else:
        failed = [(r, v < limit) for r, v in scored]
    first = next((r["start_s"] for r, is_bad in failed if is_bad), None)
    longest = run = 0
    for _, is_bad in failed:
        run = run + 1 if is_bad else 0
        longest = max(longest, run)
    return {"calibrated": True, "rule": {key: limit},
            "first_failure_s": first, "longest_failing_run": longest}


def summarize_axis(axis: str, record: Mapping[str, Any], samples: Sequence[Mapping[str, Any]],
                   windows: Sequence[Tuple[float, float]], min_samples: int,
                   threshold: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    status, reason = _applicability(record, axis)
    if status != "applicable":
        if not reason:
            raise ValueError(f"non-applicable axis {axis} requires a reason")
        return {"status": status, "reason": reason, "coverage": 0.0, "windows": []}
    signal = AXES[axis]["signal"]
    if not any(signal in s for s in samples):
        return {"status": "unscorable", "reason": f"missing_signal:{signal}",
                "coverage": 0.0, "windows": []}
    rows = _window_rows(
        samples, signal, windows, min_samples,
        signed=axis in ("directional_transport", "incoming_transport"),
    )
    values = [
        ((r["start_s"] + r["end_s"]) / 2.0, _window_value(axis, r))
        for r in rows
    ]
    values = [(t, v) for t, v in values if v is not None]
    coverage = len(values) / len(windows)
    if not values:
        return {"status": "unscorable", "reason": "no_complete_scored_window",
                "coverage": coverage, "windows": rows}
    polarity = AXES[axis]["polarity"]
    worst = max(values, key=lambda tv: tv[1]) if polarity == "lower" else min(values, key=lambda tv: tv[1])
    trajectory = {
        "early": values[0][1],
        "late": values[-1][1],
        "late_minus_early": values[-1][1] - values[0][1],
        "theil_sen_slope_per_s": _theil_sen(values),
        "worst_value": worst[1],
        "worst_window_mid_s": worst[0],
    }
    result = {
        "status": "scored" if coverage == 1.0 else "partially_scored",
        "signal": signal,
        "polarity": polarity,
        "coverage": coverage,
        "trajectory": trajectory,
        "failure": _failure_summary(axis, rows, threshold),
        "windows": rows,
    }
    if axis == "incoming_transport":
        support_threshold = record.get("_support_threshold_available", False)
        result["interpretation"] = (
            "support_gated" if support_threshold else "descriptive_until_support_threshold_is_calibrated"
        )
    return result


def _thresholds_for_medium(thresholds: Optional[Mapping[str, Any]],
                           medium: str) -> Tuple[Dict[str, Any], str]:
    if not thresholds:
        return {}, "none"
    if "default" not in thresholds and "by_medium" not in thresholds:
        return dict(thresholds), "flat"
    default = thresholds.get("default", {})
    by_medium = thresholds.get("by_medium", {})
    if not isinstance(default, Mapping) or not isinstance(by_medium, Mapping):
        raise ValueError("threshold default and by_medium entries must be objects")
    override = by_medium.get(medium, {})
    if not isinstance(override, Mapping):
        raise ValueError(f"threshold override for medium {medium} must be an object")
    resolved = dict(default)
    resolved.update(override)
    scope = f"medium:{medium}" if override else "default"
    return resolved, scope


def summarize_record(record: Mapping[str, Any], window_s: float = 5.0,
                     stride_s: Optional[float] = None, min_samples: int = 2,
                     thresholds: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    required = ("video_id", "scene_id", "model_id", "seed", "track", "medium", "duration_s")
    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError(f"record missing required fields: {', '.join(missing)}")
    duration_s = float(record["duration_s"])
    stride_s = window_s if stride_s is None else stride_s
    windows = make_windows(duration_s, window_s, stride_s)
    samples = _validate_samples(record.get("samples"), duration_s)
    thresholds, threshold_scope = _thresholds_for_medium(thresholds, str(record["medium"]))
    augmented = dict(record)
    augmented["_support_threshold_available"] = "support_stability" in thresholds
    axes = {
        axis: summarize_axis(axis, augmented, samples, windows, min_samples,
                             thresholds.get(axis))
        for axis in AXES
    }
    if "support_stability" in thresholds:
        support_limit = float(thresholds["support_stability"]["max"])
        support_rows = {
            row["window_index"]: row
            for row in axes["support_stability"].get("windows", [])
        }
        gate_counts = {"passed_windows": 0, "failed_windows": 0,
                       "unscorable_windows": 0}
        for row in axes["incoming_transport"].get("windows", []):
            support = support_rows.get(row["window_index"])
            if row.get("status") != "scored" or not support or support.get("status") != "scored":
                row["support_gate_pass"] = None
                gate_counts["unscorable_windows"] += 1
                continue
            passed = float(support["p95"]) <= support_limit
            row["support_gate_pass"] = passed
            row["interpretation_status"] = (
                "eligible" if passed else "withheld_support_unstable"
            )
            gate_counts["passed_windows" if passed else "failed_windows"] += 1
        axes["incoming_transport"]["support_gate"] = {
            "rule": {"support_error_px_p95_max": support_limit},
            **gate_counts,
        }
    return {
        "protocol_version": PROTOCOL_VERSION,
        "video_id": record["video_id"],
        "scene_id": record["scene_id"],
        "model_id": record["model_id"],
        "seed": record["seed"],
        "track": record["track"],
        "medium": record["medium"],
        "threshold_scope": threshold_scope,
        "duration_s": duration_s,
        "window_s": float(window_s),
        "stride_s": float(stride_s),
        "n_windows": len(windows),
        "aggregation": "none; report axes separately",
        "axes": axes,
    }


def _records(payload: Any) -> List[Mapping[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "records" in payload:
        if not isinstance(payload["records"], list):
            raise ValueError("records must be a list")
        return payload["records"]
    if isinstance(payload, dict):
        return [payload]
    raise ValueError("input JSON must be a record, list, or {'records': [...]} object")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--window-s", type=float, default=5.0)
    parser.add_argument("--stride-s", type=float)
    parser.add_argument("--min-samples", type=int, default=2)
    parser.add_argument("--thresholds", type=Path,
                        help="held-out calibration JSON; omit for descriptive output")
    args = parser.parse_args(argv)
    if args.min_samples < 1:
        parser.error("--min-samples must be at least 1")
    payload = json.loads(args.input.read_text())
    thresholds = json.loads(args.thresholds.read_text()) if args.thresholds else None
    results = [summarize_record(r, args.window_s, args.stride_s,
                                args.min_samples, thresholds)
               for r in _records(payload)]
    output = {
        "protocol_version": PROTOCOL_VERSION,
        "thresholds_supplied": thresholds is not None,
        "records": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Run the exploratory M2 endpoint probe on the frozen shared-control subset.

This is deliberately a small public-model pilot.  It compares the new
timestamped endpoint summaries with frozen v1.1 per-video factors on the same
clips.  The quantities have different estimands and units, so the output does
not compute a replacement delta or model ranking.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from flow_endpoint_probes import (  # noqa: E402
    PROBE_VERSION,
    audit_public_cache,
    extract_endpoint_samples,
)
from long_horizon_protocol import summarize_record  # noqa: E402


MODELS = ("chunk6", "f2s_framewise")
NOMINAL_DURATION_S = 60.0
V1_FIELDS = ("fBD", "BFR", "FP", "MCFF_early", "MCFF_late", "DD_raw_late",
             "drift_frac_late", "DAR_signed")


def _categories(path: Path):
    with path.open(newline="") as stream:
        return {(row["track"], row["duration"], row["prompt_id"]): row["category"]
                for row in csv.DictReader(stream)}


def _v1_rows(model: str):
    path = ROOT / "raw" / "i2v" / model / "60s" / "snf_task_metrics.json"
    data = json.loads(path.read_text())
    if data.get("metric_spec_version") != "1.1":
        raise ValueError(f"expected frozen v1.1 metrics in {path}")
    return {row["video"]: row for row in data["per_video"]}


def _axis_summary(trajectory, axis):
    result = trajectory["axes"][axis]
    return {
        "status": result["status"],
        "coverage": result["coverage"],
        "trajectory": result.get("trajectory"),
        "scored_windows": [
            {key: row[key] for key in ("window_index", "start_s", "end_s", "n_samples",
                                       "observed_span_fraction", "median", "p95")
             if key in row}
            for row in result.get("windows", []) if row["status"] == "scored"
        ],
    }


def _median(rows, path):
    values = []
    for row in rows:
        value = row
        for key in path:
            value = value.get(key) if isinstance(value, dict) else None
        if value is not None:
            values.append(float(value))
    return statistics.median(values) if values else None


def run() -> dict:
    started = time.perf_counter()
    category = _categories(ROOT / "manifest" / "prompt_categories.csv")
    mask_dir = ROOT / "manifest" / "shared_auto_control" / "i2v" / "60s" / "masks"
    prompts = sorted(json.loads(path.read_text())["prompt_id"] for path in mask_dir.glob("*.json"))
    if len(prompts) != 4:
        raise ValueError(f"expected the frozen four-scene shared-control subset, found {len(prompts)}")
    records = []
    for model in MODELS:
        frozen = _v1_rows(model)
        for prompt_id in prompts:
            video = prompt_id + ".mp4"
            cache_path = ROOT / ".flow_fields" / "i2v" / model / "60s" / (video + ".npz")
            if not cache_path.is_file() or video not in frozen:
                raise FileNotFoundError(f"missing paired cache or v1.1 record for {model}/{video}")
            medium = category.get(("i2v", "60s", prompt_id), "unknown")
            with np.load(cache_path, allow_pickle=False) as stored:
                samples, cache_audit = extract_endpoint_samples(stored)
            applicability = {
                "directional_transport": {"status": "unscorable", "reason": "missing_reviewed_path"},
                "incoming_transport": {"status": "unscorable", "reason": "missing_reviewed_boundary"},
                "non_recurrence": {"status": "unscorable", "reason": "appearance_frames_not_cached"},
                "reset_continuity": {"status": "unscorable", "reason": "appearance_frames_not_cached"},
            }
            trajectory = summarize_record({
                "video_id": video,
                "scene_id": prompt_id,
                "model_id": model,
                "seed": "recorded_unknown",
                "track": "i2v",
                "medium": medium,
                "duration_s": NOMINAL_DURATION_S,
                "applicability": applicability,
                "samples": samples,
            })
            old = {key: frozen[video].get(key) for key in V1_FIELDS}
            records.append({
                "model_id": model,
                "video": video,
                "scene_id": prompt_id,
                "medium": medium,
                "cache_audit": cache_audit,
                "v1_1_frozen": old,
                "m2_endpoint": {
                    "support_stability": _axis_summary(trajectory, "support_stability"),
                    "flow_presence": _axis_summary(trajectory, "flow_presence"),
                    "abstentions": {
                        axis: trajectory["axes"][axis]["reason"]
                        for axis in ("directional_transport", "incoming_transport",
                                     "non_recurrence", "reset_continuity")
                    },
                },
            })
    aggregates = []
    for model in MODELS:
        selected = [row for row in records if row["model_id"] == model]
        aggregates.append({
            "model_id": model,
            "n_clips": len(selected),
            "v1_1_subset_medians": {
                key: _median(selected, ("v1_1_frozen", key)) for key in V1_FIELDS
            },
            "m2_endpoint_subset_medians": {
                "support_early_p95_px": _median(
                    selected, ("m2_endpoint", "support_stability", "trajectory", "early")),
                "support_late_p95_px": _median(
                    selected, ("m2_endpoint", "support_stability", "trajectory", "late")),
                "dynamic_early_median_px_s": _median(
                    selected, ("m2_endpoint", "flow_presence", "trajectory", "early")),
                "dynamic_late_median_px_s": _median(
                    selected, ("m2_endpoint", "flow_presence", "trajectory", "late")),
            },
        })
    return {
        "schema_version": 1,
        "status": "exploratory_not_release_admitted",
        "probe_version": PROBE_VERSION,
        "trajectory_protocol_version": "snf-long-trajectory-0.2",
        "selection": {
            "track": "i2v",
            "duration": "60s",
            "models": list(MODELS),
            "scenes": len(prompts),
            "paired_records": len(records),
            "basis": "frozen four-scene held-out automatic shared-partition control subset",
        },
        "public_cache_audit": audit_public_cache(ROOT / ".flow_fields"),
        "comparison_contract": {
            "v1_1": "frozen clip-level early/late factors using each clip's automatic partition",
            "m2_endpoint": "timestamped five-second early/late windows from the same cached RAFT correspondences",
            "direct_replacement_delta": False,
            "reason": "units, robust summaries, and temporal aggregation differ",
        },
        "limitations": [
            "automatic model-specific partitions are unreviewed",
            "only first and last complete five-second windows are observed",
            "the middle 76 percent of a nominal 60-second clip is absent from this cache",
            "direction, boundary flux, recurrence, and reset continuity abstain",
            "four scenes and two public systems are a code-path pilot, not a model comparison",
            "no threshold was calibrated",
        ],
        "aggregates": aggregates,
        "records": records,
        "runtime_s": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "manifest" / "m2_endpoint_pilot.json")
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(f"wrote {args.output}: {len(result['records'])} records in {result['runtime_s']:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

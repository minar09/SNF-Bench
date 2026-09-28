"""Extract provisional M2 motion signals from persisted SNF v1.1 flow fields.

The existing cache stores RAFT correspondences only for the early and late
windows used by the frozen v1.1 metrics.  This module turns those
correspondences into timestamped v2 signals without pretending that the
missing middle of a clip was measured.

The support signal is the image displacement induced by a robust similarity
fit on cached rigid-support samples.  Dynamic speed is measured after removing
that fitted support transform.  Signed transport is emitted only when a
reviewed image-plane direction vector is supplied; prompt language such as
"downstream" is not enough to infer a screen-space direction.

These estimators are exploratory until reviewed role masks, a second flow
backbone, real fixed-camera anchors, and held-out corruption validation exist.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from long_horizon_protocol import summarize_record  # noqa: E402
from registry import contestants  # noqa: E402


PROBE_VERSION = "snf-flow-endpoint-probes-0.1"
CACHE_FORMAT = "snf-v1.1-early-late-sampled-flow"
REQUIRED_KEYS = {"early_static", "early_dyn", "late_static", "late_dyn", "meta"}


def _finite_rows(points: np.ndarray) -> np.ndarray:
    points = np.asarray(points, dtype=np.float32)
    if points.ndim != 2 or points.shape[1] != 4:
        raise ValueError("flow samples must have shape [points, 4] as x,y,u,v")
    return points[np.isfinite(points).all(axis=1)]


def _robust_median(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=np.float32)
    values = values[np.isfinite(values)]
    return float(np.median(values)) if values.size else float("nan")


def fit_support_similarity(points: np.ndarray, *, ransac_px: float = 1.5,
                           min_points: int = 12) -> Dict[str, Any]:
    """Fit a similarity transform to one frame of support correspondences."""
    clean = _finite_rows(points)
    if len(clean) < min_points:
        return {"status": "unscorable", "reason": "insufficient_support_points",
                "n_points": int(len(clean))}
    # OpenCV 4.9 rejects the strided two-column view even though its values and
    # dtype are valid, so materialize both correspondence arrays explicitly.
    src = np.ascontiguousarray(clean[:, :2], dtype=np.float32)
    dst = np.ascontiguousarray(src + clean[:, 2:], dtype=np.float32)
    matrix, inliers = cv2.estimateAffinePartial2D(
        src, dst, method=cv2.RANSAC, ransacReprojThreshold=float(ransac_px),
        maxIters=2000, confidence=0.99, refineIters=10,
    )
    if matrix is None or inliers is None or not np.isfinite(matrix).all():
        return {"status": "unscorable", "reason": "similarity_fit_failed",
                "n_points": int(len(clean))}
    predicted = src @ matrix[:, :2].T + matrix[:, 2]
    fitted_displacement = predicted - src
    residual = dst - predicted
    support_error = _robust_median(np.linalg.norm(fitted_displacement, axis=1))
    residual_px = _robust_median(np.linalg.norm(residual, axis=1))
    a, b = float(matrix[0, 0]), float(matrix[1, 0])
    return {
        "status": "scored",
        "matrix": matrix.astype(float).tolist(),
        "support_error_px": support_error,
        "support_fit_residual_px": residual_px,
        "translation_x_px": float(matrix[0, 2]),
        "translation_y_px": float(matrix[1, 2]),
        "rotation_deg": math.degrees(math.atan2(b, a)),
        "scale": math.hypot(a, b),
        "n_points": int(len(clean)),
        "n_inliers": int(np.asarray(inliers).sum()),
        "inlier_fraction": float(np.asarray(inliers).mean()),
    }


def residual_dynamic_signal(points: np.ndarray, matrix: Sequence[Sequence[float]],
                            fps: float,
                            path_unit_xy: Optional[Sequence[float]] = None) -> Dict[str, float]:
    """Measure dynamic motion after removing the fitted support transform."""
    clean = _finite_rows(points)
    if not len(clean):
        raise ValueError("no finite dynamic samples")
    affine = np.asarray(matrix, dtype=np.float32)
    if affine.shape != (2, 3) or not np.isfinite(affine).all():
        raise ValueError("matrix must be finite shape [2, 3]")
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError("fps must be positive and finite")
    src = clean[:, :2]
    fitted = src @ affine[:, :2].T + affine[:, 2] - src
    residual = clean[:, 2:] - fitted
    out = {"dynamic_speed_px_s": _robust_median(
        np.linalg.norm(residual, axis=1)) * float(fps)}
    if path_unit_xy is not None:
        unit = np.asarray(path_unit_xy, dtype=np.float32)
        if unit.shape != (2,) or not np.isfinite(unit).all():
            raise ValueError("path direction must contain two finite values")
        norm = float(np.linalg.norm(unit))
        if norm <= 1e-8:
            raise ValueError("path direction must be non-zero")
        unit /= norm
        out["signed_path_speed_px_s"] = _robust_median(residual @ unit) * float(fps)
    return out


def _meta(values: np.ndarray) -> Tuple[int, int, int, int, float]:
    vals = np.asarray(values).reshape(-1)
    if len(vals) != 5:
        raise ValueError("cache meta must contain F, window, width, height, fps")
    frames, window, width, height, fps = (int(x) for x in vals)
    if min(frames, window, width, height, fps) <= 0 or window > frames - 1:
        raise ValueError("invalid cache metadata")
    return frames, window, width, height, float(fps)


def extract_endpoint_samples(cache: Mapping[str, np.ndarray],
                             path_unit_xy: Optional[Sequence[float]] = None,
                             ransac_px: float = 1.5) -> Tuple[list, Dict[str, Any]]:
    """Return timestamped early/late samples and honest cache coverage."""
    missing = REQUIRED_KEYS - set(cache)
    if missing:
        raise ValueError(f"cache is missing keys: {sorted(missing)}")
    frames, window, width, height, fps = _meta(cache["meta"])
    samples = []
    fit_failures: Dict[str, int] = {}
    scored = 0
    for phase, first_transition in (("early", 0), ("late", frames - 1 - window)):
        static = np.asarray(cache[f"{phase}_static"])
        dynamic = np.asarray(cache[f"{phase}_dyn"])
        if static.ndim != 3 or dynamic.ndim != 3 or static.shape[0] != dynamic.shape[0]:
            raise ValueError(f"{phase} arrays must be [time, points, 4] with matching time")
        for offset, (support_points, dynamic_points) in enumerate(zip(static, dynamic)):
            fit = fit_support_similarity(support_points, ransac_px=ransac_px)
            if fit["status"] != "scored":
                reason = fit["reason"]
                fit_failures[reason] = fit_failures.get(reason, 0) + 1
                continue
            try:
                motion = residual_dynamic_signal(
                    dynamic_points, fit["matrix"], fps, path_unit_xy=path_unit_xy)
            except ValueError as exc:
                reason = str(exc)
                fit_failures[reason] = fit_failures.get(reason, 0) + 1
                continue
            transition = first_transition + offset
            samples.append({
                "t_s": (transition + 0.5) / fps,
                "cache_phase": phase,
                "support_error_px": fit["support_error_px"],
                "support_fit_residual_px": fit["support_fit_residual_px"],
                "support_inlier_fraction": fit["inlier_fraction"],
                **motion,
            })
            scored += 1
    samples.sort(key=lambda row: row["t_s"])
    total_transitions = frames - 1
    audit = {
        "cache_format": CACHE_FORMAT,
        "sampled_video_frames": frames,
        "cached_window_transitions": window,
        "frame_width": width,
        "frame_height": height,
        "effective_fps": fps,
        "available_transition_count": min(total_transitions, 2 * window),
        "scored_transition_count": scored,
        "full_clip_transition_count": total_transitions,
        "temporal_coverage": scored / total_transitions,
        "missing_middle": max(0, total_transitions - 2 * window),
        "fit_failures": fit_failures,
    }
    return samples, audit


def _public_cache_paths(root: Path) -> Iterable[Tuple[str, str, str, Path]]:
    public = {(m["track"], m["key"]) for track in ("t2v", "i2v")
              for m in contestants(track)}
    for path in sorted(root.rglob("*.npz")):
        parts = path.relative_to(root).parts
        if len(parts) >= 4 and (parts[0], parts[1]) in public:
            yield parts[0], parts[1], parts[2], path


def audit_public_cache(root: Path) -> Dict[str, Any]:
    rows: Dict[Tuple[str, str, str], int] = {}
    for track, model, duration, _ in _public_cache_paths(root):
        key = (track, model, duration)
        rows[key] = rows.get(key, 0) + 1
    return {
        "public_cache_files": sum(rows.values()),
        "coverage": [
            {"track": key[0], "model_id": key[1], "duration": key[2], "files": count}
            for key, count in sorted(rows.items())
        ],
        "limitations": [
            "cache contains early and late windows only",
            "public T2V systems have no persisted flow fields",
            "cached role masks are automatic and model-specific",
            "no screen-space path annotation is inferred from prompt text",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-root", type=Path, default=ROOT / ".flow_fields")
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--cache", type=Path, help="one NPZ to extract")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--video-id")
    parser.add_argument("--scene-id")
    parser.add_argument("--model-id")
    parser.add_argument("--track", choices=("t2v", "i2v"), default="i2v")
    parser.add_argument("--medium", default="unknown")
    parser.add_argument("--duration-s", type=float)
    parser.add_argument("--path-direction", nargs=2, type=float, metavar=("DX", "DY"))
    parser.add_argument("--window-s", type=float, default=5.0)
    args = parser.parse_args()

    if args.audit_only:
        result: Dict[str, Any] = {
            "schema_version": 1,
            "probe_version": PROBE_VERSION,
            "status": "asset_audit_only",
            **audit_public_cache(args.cache_root),
        }
    else:
        if args.cache is None:
            parser.error("--cache is required unless --audit-only is used")
        with np.load(args.cache, allow_pickle=False) as stored:
            samples, cache_audit = extract_endpoint_samples(
                stored, path_unit_xy=args.path_direction)
        duration_s = args.duration_s or cache_audit["sampled_video_frames"] / cache_audit["effective_fps"]
        applicability = {
            "incoming_transport": {"status": "unscorable", "reason": "missing_reviewed_boundary"},
            "non_recurrence": {"status": "unscorable", "reason": "appearance_frames_not_cached"},
            "reset_continuity": {"status": "unscorable", "reason": "appearance_frames_not_cached"},
        }
        if args.path_direction is None:
            applicability["directional_transport"] = {
                "status": "unscorable", "reason": "missing_reviewed_path"
            }
        record = {
            "video_id": args.video_id or args.cache.name.removesuffix(".npz"),
            "scene_id": args.scene_id or "unassigned",
            "model_id": args.model_id or args.cache.parent.parent.name,
            "seed": "unknown",
            "track": args.track,
            "medium": args.medium,
            "duration_s": duration_s,
            "applicability": applicability,
            "samples": samples,
        }
        result = {
            "schema_version": 1,
            "probe_version": PROBE_VERSION,
            "status": "exploratory_endpoint_probe",
            "cache_audit": cache_audit,
            "trajectory": summarize_record(record, window_s=args.window_s),
        }
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

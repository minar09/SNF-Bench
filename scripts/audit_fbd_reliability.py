#!/usr/bin/env python3
"""Trace the match support behind frozen fBD values.

The historical scorer returns one number or None. This audit reproduces that
number while exposing the ORB keypoint, cross-check match, RANSAC inlier,
fallback, and usable-late-frame counts that determine whether fBD is reliable.

The default 12 clips are the exact references in the frozen perturbation sweep.
Masks are rebuilt with the frozen v1.1 early-flow path. Results are written per
clip so the GPU stage is resumable, then summarized by scene category.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest"
VIDEO_ROOT = ROOT / "videos/t2v/self_forcing/60s"
BASELINE_PATH = ROOT / "raw/t2v/self_forcing/60s/snf_task_metrics.json"


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def prompt_id(clip):
    return re.sub(r"-\d+-\d+\.\d+\.mp4$", "", clip)


def trace_orb_drift(grays, static, late_idx):
    """Reproduce frozen orb_drift and return its hidden support counts."""
    height, width = grays[0].shape
    diagonal = float(np.hypot(height, width))
    orb = cv2.ORB_create(nfeatures=1500)
    static_u8 = static.astype(np.uint8) * 255
    kp0, des0 = orb.detectAndCompute(grays[0], static_u8)
    base_keypoints = len(kp0)
    result = {
        "base_keypoints": base_keypoints,
        "late_frames_requested": len(late_idx),
        "late_frames": [],
        "fBD": None,
        "abstention_reason": None,
    }
    if des0 is None or base_keypoints < 12:
        result["abstention_reason"] = "base_descriptors_or_keypoints_below_12"
        return result

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    displacements = []
    for frame_index in late_idx:
        kp1, des1 = orb.detectAndCompute(grays[frame_index], static_u8)
        row = {
            "frame_index": int(frame_index),
            "keypoints": len(kp1),
            "matches": 0,
            "ransac_inliers": None,
            "used": False,
            "used_ransac_inliers": False,
            "fallback_raw_matches": False,
            "skip_reason": None,
            "median_displacement_px": None,
        }
        if des1 is None or len(kp1) < 12:
            row["skip_reason"] = "descriptors_or_keypoints_below_12"
            result["late_frames"].append(row)
            continue
        matches = matcher.match(des0, des1)
        row["matches"] = len(matches)
        if len(matches) < 12:
            row["skip_reason"] = "matches_below_12"
            result["late_frames"].append(row)
            continue
        pts0 = np.float32([kp0[match.queryIdx].pt for match in matches])
        pts1 = np.float32([kp1[match.trainIdx].pt for match in matches])
        _homography, inliers = cv2.findHomography(pts0, pts1, cv2.RANSAC, 3.0)
        n_inliers = int(inliers.sum()) if inliers is not None else 0
        row["ransac_inliers"] = n_inliers
        if inliers is None or n_inliers < 8:
            distances = np.linalg.norm(pts1 - pts0, axis=1)
            row["fallback_raw_matches"] = True
        else:
            keep = inliers.ravel().astype(bool)
            distances = np.linalg.norm(pts1[keep] - pts0[keep], axis=1)
            row["used_ransac_inliers"] = True
        displacement = float(np.median(distances))
        row["median_displacement_px"] = displacement
        row["used"] = True
        displacements.append(displacement)
        result["late_frames"].append(row)

    if not displacements:
        result["abstention_reason"] = "no_usable_late_frames"
        return result
    result["fBD"] = float(st.mean(displacements) / diagonal * 100.0)
    return result


def compact_trace(trace):
    frames = trace["late_frames"]
    used = [row for row in frames if row["used"]]
    matches = [row["matches"] for row in used]
    ransac = [row["ransac_inliers"] for row in used
              if row["ransac_inliers"] is not None]
    return {
        "fBD": trace["fBD"],
        "abstention_reason": trace["abstention_reason"],
        "base_keypoints": trace["base_keypoints"],
        "late_frames_requested": trace["late_frames_requested"],
        "usable_late_frames": len(used),
        "usable_late_fraction": len(used) / max(1, trace["late_frames_requested"]),
        "ransac_frames": sum(row["used_ransac_inliers"] for row in used),
        "raw_match_fallback_frames": sum(row["fallback_raw_matches"] for row in used),
        "late_descriptor_failures": sum(
            row["skip_reason"] == "descriptors_or_keypoints_below_12" for row in frames),
        "late_match_failures": sum(
            row["skip_reason"] == "matches_below_12" for row in frames),
        "matches_median": st.median(matches) if matches else None,
        "matches_min": min(matches) if matches else None,
        "ransac_inliers_median": st.median(ransac) if ransac else None,
        "trace": frames,
    }


def selected_clips():
    data = json.loads((MANIFEST / "validation_response_geom.json").read_text())
    return sorted({row["clip"] for row in data["records"]})


def category_map():
    return {row["prompt_id"]: row["category"]
            for row in csv.DictReader((MANIFEST / "prompt_categories.csv").open())
            if row["track"] == "t2v" and row["duration"] == "60s"}


def baseline_map():
    data = json.loads(BASELINE_PATH.read_text())
    return {row["video"]: row for row in data["per_video"]}


def summarize(records):
    groups = defaultdict(list)
    for row in records:
        groups[row["category"]].append(row)

    def group_summary(rows):
        usable = [row["usable_late_fraction"] for row in rows]
        fallbacks = [row["raw_match_fallback_frames"] /
                     max(1, row["usable_late_frames"]) for row in rows]
        matches = [row["matches_median"] for row in rows
                   if row["matches_median"] is not None]
        return {
            "n_clips": len(rows),
            "fbd_abstentions": sum(row["fBD"] is None for row in rows),
            "median_usable_late_fraction": st.median(usable),
            "minimum_usable_late_fraction": min(usable),
            "median_raw_match_fallback_fraction": st.median(fallbacks),
            "maximum_raw_match_fallback_fraction": max(fallbacks),
            "median_crosscheck_matches": st.median(matches) if matches else None,
            "minimum_base_keypoints": min(row["base_keypoints"] for row in rows),
        }

    return {
        "schema_version": 1,
        "track": "t2v",
        "model": "self_forcing",
        "duration": "60s",
        "scope": "12 perturbation-reference clips; pilot, not full public-panel coverage",
        "frozen_thresholds": {
            "minimum_base_keypoints": 12,
            "minimum_late_keypoints": 12,
            "minimum_crosscheck_matches": 12,
            "minimum_ransac_inliers_before_raw_match_fallback": 8,
            "minimum_usable_late_frames_for_reported_fBD": 1,
        },
        "overall": group_summary(records),
        "by_category": {category: group_summary(rows)
                        for category, rows in sorted(groups.items())},
        "records": [{key: value for key, value in row.items() if key != "trace"}
                    for row in records],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpu", default="4")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--out-dir", type=Path,
                        default=MANIFEST / "fbd_reliability_pilot")
    parser.add_argument("--summary", type=Path,
                        default=MANIFEST / "fbd_reliability_pilot.json")
    args = parser.parse_args()

    clips = selected_clips()
    categories = category_map()
    baselines = baseline_map()
    for clip in clips:
        if not (VIDEO_ROOT / clip).is_file() or clip not in baselines:
            raise FileNotFoundError(f"missing video or v1.1 baseline: {clip}")
        if prompt_id(clip) not in categories:
            raise ValueError(f"missing category: {clip}")
    print(f"{len(clips)} clips ready")
    if args.check_only:
        return 0

    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    import torch
    import snf_metrics_v11 as V11
    model = V11.S.load_raft("cuda" if torch.cuda.is_available() else "cpu")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for index, clip in enumerate(clips, 1):
        output = args.out_dir / f"{clip}.json"
        if output.exists():
            print(f"SKIP {index}/{len(clips)} {clip}", flush=True)
            continue
        tensors, grays = V11.S.read_frames(str(VIDEO_ROOT / clip), device)
        if tensors is None:
            raise RuntimeError(f"cannot decode {clip}")
        window = max(V11.S.MIN_WIN, int(len(tensors) * V11.S.WIN_FRAC))
        early = np.mean([
            V11.S.flow_mag(model, tensors[i], tensors[i + 1]).astype(np.float32)
            for i in range(min(window, len(tensors) - 1))
        ], axis=0)
        _dynamic, static = V11.S.build_masks(early)
        trace = compact_trace(trace_orb_drift(
            grays, static, list(range(len(tensors) - window, len(tensors)))))
        baseline = baselines[clip]
        trace.update({
            "video": clip,
            "category": categories[prompt_id(clip)],
            "metric_spec_version": baseline.get("metric_spec_version"),
            "baseline_fBD": baseline.get("fBD"),
            "absolute_reproduction_error": abs(trace["fBD"] - baseline["fBD"])
            if trace["fBD"] is not None and baseline.get("fBD") is not None else None,
            "sampled_frames": len(tensors),
            "late_window_frames": window,
            "static_fraction_rebuilt": float(static.mean()),
            "static_fraction_baseline": baseline.get("static_frac"),
        })
        atomic_json(output, trace)
        del tensors
        torch.cuda.empty_cache()
        error = trace["absolute_reproduction_error"]
        error_text = f"{error:.3g}" if error is not None else "n/a"
        print(f"OK {index}/{len(clips)} usable={trace['usable_late_frames']}/{window} "
              f"fallback={trace['raw_match_fallback_frames']} "
              f"error={error_text}", flush=True)

    records = [json.loads((args.out_dir / f"{clip}.json").read_text())
               for clip in clips]
    result = summarize(records)
    atomic_json(args.summary, result)
    print(f"{len(records)} traces -> {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

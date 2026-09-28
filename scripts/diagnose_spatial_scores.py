#!/usr/bin/env python3
"""Read-only M1 audit of NBF distributions and fBD value coverage.

A non-null fBD is not ORB match coverage: the current scorer stores no match
count or abstention reason. This report keeps those concepts separate.
"""

import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

from registry import ALL

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manifest"
RAW = ROOT / "raw"


def analyze():
    public = {m["key"] for m in ALL if m["track"] == "t2v" and m["status"] == "public"}
    values = defaultdict(list)
    for r in csv.DictReader((MAN / "per_video_scores.csv").open()):
        if r["track"] == "t2v" and r["duration"] == "60s" and r["model"] in public \
                and r["metric"] == "NBF_mean":
            values[r["model"]].append((float(r["value"]), r["prompt_id"]))
    report = {"track": "t2v", "duration": "60s", "models": {},
              "caveat": "fBD non-null counts do not measure ORB match coverage; matches are not stored"}
    for model in sorted(public):
        sorted_values = sorted(values[model], reverse=True)
        nums = [v for v, _ in sorted_values]
        raw_path = RAW / "t2v" / model / "60s" / "snf_task_metrics.json"
        records = json.loads(raw_path.read_text()).get("per_video", []) if raw_path.exists() else []
        report["models"][model] = {
            "nbf_n_prompts": len(nums),
            "nbf_mean": st.mean(nums) if nums else None,
            "nbf_median": st.median(nums) if nums else None,
            "nbf_max": max(nums) if nums else None,
            "nbf_top1_share_of_sum": nums[0] / sum(nums) if nums and sum(nums) else None,
            "nbf_top3_share_of_sum": sum(nums[:3]) / sum(nums) if nums and sum(nums) else None,
            "nbf_top3_prompt_ids": [prompt for _, prompt in sorted_values[:3]],
            "fbd_nonnull": sum(r.get("fBD") is not None for r in records),
            "fbd_total_records": len(records),
        }
    return report


def main():
    report = analyze()
    out = MAN / "spatial_score_diagnosis.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    for model, record in report["models"].items():
        print(f"{model:20s} NBF median {record['nbf_median']:.2f} "
              f"top3 share {record['nbf_top3_share_of_sum']:.2f} "
              f"fBD non-null {record['fbd_nonnull']}/{record['fbd_total_records']}")
    print(out)


if __name__ == "__main__":
    main()

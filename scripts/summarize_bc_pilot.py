#!/usr/bin/env python3
"""Summarize paired VBench background-consistency pilot responses by medium."""

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def summarize(records, categories):
    by_clip = defaultdict(dict)
    for row in records:
        by_clip[row["clip"]][(row["family"], row["level"])] = row
    rows = []
    for clip, pair in sorted(by_clip.items()):
        prompt = re.sub(r"-\d+-\d+\.\d+\.mp4$", "", clip)
        baseline = pair[("translation", 0.0)]
        moved = pair[("translation", 80.0)]
        frozen = pair[("freeze", 0.75)]
        rows.append({"clip": clip, "category": categories[prompt],
                     "bc_baseline": baseline["VB_BC"],
                     "bc_translation_delta": moved["VB_BC"] - baseline["VB_BC"],
                     "bc_freeze_delta": frozen["VB_BC"] - baseline["VB_BC"],
                     "nbf_translation_delta": moved["NBF"] - baseline["NBF"],
                     "dd_translation_delta": moved["VB_DD"] - baseline["VB_DD"]})
    return {"n_clips": len(rows),
            "bc_translation_positive": sum(r["bc_translation_delta"] > 0 for r in rows),
            "bc_freeze_positive": sum(r["bc_freeze_delta"] > 0 for r in rows),
            "limitation": "one clip per medium; 24 strided frames; pilot only",
            "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "manifest" / "validation_response_bc_stratified_pilot.json")
    parser.add_argument("--out", type=Path,
                        default=ROOT / "manifest" / "bc_stratified_pilot_summary.json")
    args = parser.parse_args()
    records = json.loads(args.input.read_text())["records"]
    categories = {r["prompt_id"]: r["category"]
                  for r in csv.DictReader((ROOT / "manifest" / "prompt_categories.csv").open())
                  if r["track"] == "t2v" and r["duration"] == "60s"}
    result = summarize(records, categories)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"BC higher after translation: {result['bc_translation_positive']}/{result['n_clips']}")
    print(f"BC higher after freezing: {result['bc_freeze_positive']}/{result['n_clips']}")
    print(args.out)


if __name__ == "__main__":
    main()

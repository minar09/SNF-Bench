#!/usr/bin/env python3
"""Audit current T2V prompts before authoring the SNF-Bench v2 suite.

This is a deterministic screening tool, not a semantic prompt judge. It screens every T2V text file for model-visible evaluation instructions and
reports exact cross-horizon matches for the canonical duration files. `--strict` is a release
gate for those instructions; heuristic contradiction flags are review-only.

    python scripts/audit_prompt_design.py --out manifest/prompt_design_audit.json
    python scripts/audit_prompt_design.py --strict  # expected to fail on v1 prompts
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DURATIONS = ("60s", "120s", "240s")

# Prompts must describe a video, not direct a scorer or refer to model internals.
LEAKAGE = re.compile(
    r"\b(?:evaluators?|evaluation metrics?|dynamic degree|optical.flow score|"
    r"kv.cache|rope.limit|positional.encoding|attention collapse|"
    r"pond effect|frame\s+[\d,]+\s+onward)\b",
    re.IGNORECASE,
)

# Deliberately broad: these are candidates for human review, never auto-fails.
STATIC_VEGETATION = re.compile(
    r"\b(?:vegetation|trees?|branches|leaves|foliage)\b.{0,65}"
    r"\b(?:motionless|perfectly static|immovable|completely static)\b|"
    r"\b(?:motionless|perfectly static|immovable|completely static)\b.{0,65}"
    r"\b(?:vegetation|trees?|branches|leaves|foliage)\b",
    re.IGNORECASE,
)
VEGETATION_MOTION = re.compile(r"\b(?:sway\w*|thrash\w*|bending|windblown)\b", re.I)
TRAILING_DURATION = re.compile(r"\s*\[(?:5|60|120|240)s\]\s*$", re.I)


def normalize(text):
    """Normalize only formatting and the trailing duration token."""
    return " ".join(TRAILING_DURATION.sub("", text).casefold().split())


def prompt_rows(prompt_dir):
    rows = []
    for path in sorted(prompt_dir.glob("*.txt")):
        canonical = path.name in {f"prompts{d}.txt" for d in DURATIONS}
        match = re.search(r"(5|60|120|240)s", path.stem)
        duration = f"{match.group(1)}s" if match else "unspecified"
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if raw.strip():
                try:
                    display_path = str(path.relative_to(ROOT))
                except ValueError:
                    display_path = str(path)
                rows.append({"duration": duration, "canonical": canonical,
                             "file": display_path, "line": lineno,
                             "text": raw.strip()})
    return rows


def audit(prompt_dir):
    rows = prompt_rows(prompt_dir)
    by_duration = {d: set() for d in DURATIONS}
    findings = []
    for row in rows:
        text = row["text"]
        if row["canonical"]:
            by_duration[row["duration"]].add(normalize(text))
        for match in LEAKAGE.finditer(text):
            findings.append({"kind": "evaluation_instruction", "severity": "blocking",
                             "file": row["file"], "line": row["line"],
                             "match": match.group(0)})
        if STATIC_VEGETATION.search(text) and VEGETATION_MOTION.search(text):
            findings.append({"kind": "possibly_conflicting_vegetation",
                             "severity": "review", "file": row["file"],
                             "line": row["line"]})
    overlaps = {}
    for i, left in enumerate(DURATIONS):
        for right in DURATIONS[i + 1:]:
            overlaps[f"{left}|{right}"] = len(by_duration[left] & by_duration[right])
    return {"scope": "all T2V text files screened; canonical 60/120/240 files used for exact overlap",
            "files_scanned": sorted({r["file"] for r in rows}),
            "prompts_screened": len(rows),
            "counts": {d: sum(r["canonical"] and r["duration"] == d for r in rows)
                       for d in DURATIONS},
            "distinct_text_counts": {d: len(by_duration[d]) for d in DURATIONS},
            "overlaps": overlaps,
            "blocking_count": sum(x["severity"] == "blocking" for x in findings),
            "blocking_prompt_count": len({(x["file"], x["line"]) for x in findings
                                          if x["severity"] == "blocking"}),
            "review_count": sum(x["severity"] == "review" for x in findings),
            "findings": findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-dir", type=Path, default=ROOT / "prompts" / "t2v")
    parser.add_argument("--out", type=Path, help="optional JSON report path")
    parser.add_argument("--strict", action="store_true",
                        help="exit nonzero when model-visible evaluation instructions exist")
    args = parser.parse_args()
    result = audit(args.prompt_dir)
    report = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    if args.strict and result["blocking_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

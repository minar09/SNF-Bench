#!/usr/bin/env python3
"""Static release gate for the whitelisted anonymous review export."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
EXACT = {
    ".gitignore",
    "README.md",
    "RELEASE_MANIFEST.md",
    "USAGE_NOTICE.md",
    "benchmark_manifest.json",
    "bootstrap_analysis.py",
    "check_release.py",
    "configs/common_t2v.yaml",
    "evaluate.py",
    "example_predictions/example_scores.csv",
    "expected_outputs/bootstrap.json",
    "expected_outputs/metric_record.json",
    "expected_outputs/perturbation_curve.json",
    "generate_perturbations.py",
    "make_partition.py",
    "metric_spec_v1.1.md",
    "requirements.txt",
    "smoke_test.py",
    "snf_core.py",
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".csv", ".txt"}
FORBIDDEN = re.compile(
    r"/(?:home|Users)/|drive\.google|(?:github\.com[:/])|git@|"
    r"wandb|spreadsheet_id|\.git/config",
    re.IGNORECASE,
)


def allowed(relative: str) -> bool:
    if relative in EXACT:
        return True
    return relative.startswith("example_predictions/translation_") and relative.endswith(".npz")


def main() -> int:
    files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and "run_outputs" not in path.parts
        and ".venv" not in path.parts
    )
    unexpected = [
        str(path.relative_to(ROOT))
        for path in files
        if not allowed(str(path.relative_to(ROOT)))
    ]
    leaks = []
    for path in files:
        relative = str(path.relative_to(ROOT))
        if relative == "check_release.py":
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if FORBIDDEN.search(text):
                leaks.append(relative)
        elif path.suffix == ".npz":
            with np.load(path, allow_pickle=False) as bundle:
                if any(bundle[key].dtype.hasobject for key in bundle.files):
                    leaks.append(f"{relative}:object-array")
    if unexpected:
        print("FAIL unexpected files:")
        print("\n".join(f"  {name}" for name in unexpected))
    if leaks:
        print("FAIL identity/internal-data scan:")
        print("\n".join(f"  {name}" for name in leaks))
    if unexpected or leaks:
        return 1
    print(f"RELEASE CLEAN: {len(files)} whitelisted files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

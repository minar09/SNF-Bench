#!/usr/bin/env python3
"""Paired per-item percentile-bootstrap comparison used by the paper."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", required=True)
    parser.add_argument("--out", default="run_outputs/bootstrap.json")
    parser.add_argument("--resamples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rows = list(csv.DictReader(Path(args.scores).open(newline="", encoding="utf-8")))
    differences = np.array(
        [float(row["method_a"]) - float(row["method_b"]) for row in rows],
        dtype=np.float64,
    )
    if len(differences) < 2:
        raise ValueError("at least two paired items are required")
    rng = np.random.default_rng(args.seed)
    draws = rng.choice(differences, size=(args.resamples, len(differences)), replace=True)
    means = draws.mean(axis=1)
    result = {
        "n_paired": int(len(differences)),
        "mean_difference_a_minus_b": float(differences.mean()),
        "ci95": [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))],
        "resamples": args.resamples,
        "seed": args.seed,
    }
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

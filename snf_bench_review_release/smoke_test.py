#!/usr/bin/env python3
"""Run the anonymous review artifact end to end and verify expected outputs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def close(actual: float, expected: float, tolerance: float = 1e-6) -> bool:
    return abs(actual - expected) <= tolerance * max(1.0, abs(expected))


def main() -> int:
    run("generate_perturbations.py")
    run(
        "evaluate.py",
        "--manifest",
        "benchmark_manifest.json",
        "--pred_dir",
        "example_predictions",
        "--out",
        "run_outputs/metric_record.json",
    )
    run(
        "evaluate.py",
        "--manifest",
        "run_outputs/perturbation_manifest.json",
        "--pred_dir",
        "example_predictions",
        "--out",
        "run_outputs/perturbation_curve.json",
    )
    run(
        "bootstrap_analysis.py",
        "--scores",
        "example_predictions/example_scores.csv",
        "--out",
        "run_outputs/bootstrap.json",
    )

    expected = json.loads((ROOT / "expected_outputs/metric_record.json").read_text())
    actual = json.loads((ROOT / "run_outputs/metric_record.json").read_text())
    expected_row, actual_row = expected["records"][0], actual["records"][0]
    keys = ("fBD", "NBF", "MCFF_E", "MCFF_L", "FP", "DLR", "DAR_signed")
    failures = [key for key in keys if not close(actual_row[key], expected_row[key])]
    if failures:
        raise AssertionError(f"metric smoke-test mismatch: {failures}")

    curve = json.loads((ROOT / "run_outputs/perturbation_curve.json").read_text())
    expected_curve = json.loads((ROOT / "expected_outputs/perturbation_curve.json").read_text())
    nbf = [row["NBF"] for row in curve["records"]]
    if any(right <= left for left, right in zip(nbf, nbf[1:])):
        raise AssertionError(f"translation curve is not strictly increasing in NBF: {nbf}")
    expected_nbf = [row["NBF"] for row in expected_curve["records"]]
    if any(not close(a, b) for a, b in zip(nbf, expected_nbf)):
        raise AssertionError("translation curve differs from expected output")
    bootstrap = json.loads((ROOT / "run_outputs/bootstrap.json").read_text())
    expected_bootstrap = json.loads((ROOT / "expected_outputs/bootstrap.json").read_text())
    if not close(
        bootstrap["mean_difference_a_minus_b"],
        expected_bootstrap["mean_difference_a_minus_b"],
    ) or any(not close(a, b) for a, b in zip(bootstrap["ci95"], expected_bootstrap["ci95"])):
        raise AssertionError("bootstrap result differs from expected output")
    print("SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Endpoint and paired-analysis tests for the consolidated response audit."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_response_analysis import (  # noqa: E402
    INTERVENTIONS, TARGETS, analyze, category_bootstrap, paired_dz,
)


def test_task_defined_endpoints_fix_numeric_sorting_errors():
    assert INTERVENTIONS["repetition"]["endpoint"] == 6.0
    assert INTERVENTIONS["repetition"]["severity_order"] == [0.0, 24.0, 12.0, 6.0]
    assert INTERVENTIONS["mask_erode"]["baseline"] == 0.0
    assert INTERVENTIONS["mask_erode"]["endpoint"] == -4.0
    assert INTERVENTIONS["mask_dilate"]["baseline"] == 0.0
    assert INTERVENTIONS["mask_dilate"]["endpoint"] == 4.0


def test_selectivity_uses_every_predeclared_target_family():
    assert TARGETS["MCFF_L"] == ("freeze", "attenuation")
    assert TARGETS["FP"] == ("freeze", "attenuation")
    assert TARGETS["DLR"] == ("translation", "rotation", "scale")
    assert TARGETS["DAR"] == ("translation", "rotation", "scale")


def test_paired_dz_uses_sample_standard_deviation():
    # mean=2, sample SD=1, whereas population SD would be sqrt(2/3).
    assert paired_dz([1.0, 2.0, 3.0]) == 2.0


def test_category_macro_bootstrap_does_not_overweight_large_group():
    result = category_bootstrap({"water": [10.0] * 10, "fire": [-2.0, -2.0]},
                                draws=100, seed=0)
    assert result["category_macro_delta"] == 4.0
    assert result["n_clips"] == 12
    assert result["n_categories"] == 2


def test_mask_erosion_is_compared_with_zero_not_dilation():
    categories = {"clip": "water"}
    records = []
    for level, value in ((-4.0, 1.0), (-2.0, 2.0), (0.0, 5.0),
                         (2.0, 8.0), (4.0, 9.0)):
        row = {"family": "mask_radius", "clip": "clip-0-1.0.mp4", "level": level}
        for metric in ("fBD", "NBF", "MCFF_L", "FP", "DLR", "DAR", "VB_DD"):
            row[metric] = value
        records.append(row)
    result = analyze(records, categories, draws=20, seed=0)
    rows = {(r["intervention"], r["metric"]): r for r in result["rows"]}
    assert rows[("mask_erode", "fBD")]["category_macro_delta"] == -4.0
    assert rows[("mask_dilate", "fBD")]["category_macro_delta"] == 4.0

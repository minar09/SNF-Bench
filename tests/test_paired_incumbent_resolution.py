"""Check that paired, category-macro uncertainty uses prompts as units."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from paired_incumbent_resolution import paired_category_bootstrap  # noqa: E402


def test_category_macro_is_not_dominated_by_large_group():
    result = paired_category_bootstrap({"water": [10] * 10, "smoke": [-2, -2]}, n=100)
    assert result["difference"] == 4
    assert result["n_prompts"] == 12
    assert result["n_categories"] == 2
    assert result["ci95"] == [4, 4]


def test_paired_uncertainty_can_include_zero():
    result = paired_category_bootstrap({"water": [-1, 1]}, n=5000)
    assert result["difference"] == 0
    assert result["ci95"][0] < 0 < result["ci95"][1]
    assert not result["ci_excludes_zero"]
    assert result["order_probability"] is None

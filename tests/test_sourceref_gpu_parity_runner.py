"""Parity comparison must report missing values and abstention mismatches."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_sourceref_gpu_parity import FLAGS, SCORES, compare  # noqa: E402


def _record():
    return {**{key: 1.0 for key in SCORES}, **{key: False for key in FLAGS}}


def test_parity_records_previous_and_rescored_values():
    a, b = _record(), _record()
    b["MCFF_late"] = 1.0005
    out = compare(a, b)
    assert out["status"] == "PASS"
    assert out["scores"]["MCFF_late"] == {"previous": 1.0, "rescore": 1.0005}


def test_missing_and_abstention_mismatch_cannot_pass():
    a, b = _record(), _record()
    b.pop("FP")
    b["fBD_abstained"] = True
    out = compare(a, b)
    assert out["status"] == "FAIL"
    assert out["missing_required_keys"] == ["FP"]
    assert out["abstention_mismatches"] == ["fBD_abstained"]


def test_null_disagreement_and_numeric_difference_cannot_pass():
    a, b = _record(), _record()
    a["fBD_src"] = None
    b["BFR"] = 1.1
    out = compare(a, b)
    assert out["status"] == "FAIL"
    assert out["null_mismatches"] == ["fBD_src"]
    assert any(row["key"] == "BFR" for row in out["outside_tolerance"])

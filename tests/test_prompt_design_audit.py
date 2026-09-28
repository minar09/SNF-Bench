"""Behavioral checks for the prompt release gate and horizon accounting."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_prompt_design import audit  # noqa: E402


def test_leakage_and_matching_ignore_only_duration_suffix(tmp_path):
    (tmp_path / "prompts60s.txt").write_text(
        "A fixed camera watches water flow right past a rock. [60s]\n",
        encoding="utf-8")
    (tmp_path / "prompts120s.txt").write_text(
        "A fixed camera watches water flow right past a rock. [120s]\n",
        encoding="utf-8")
    (tmp_path / "prompts240s.txt").write_text(
        "A fixed camera watches water flow left. Evaluators must inspect dynamic degree. [240s]\n",
        encoding="utf-8")
    (tmp_path / "prompts_ext.txt").write_text(
        "The evaluator checks a river.\n", encoding="utf-8")
    result = audit(tmp_path)
    assert result["prompts_screened"] == 4
    assert result["overlaps"]["60s|120s"] == 1
    assert result["overlaps"]["60s|240s"] == 0
    assert result["blocking_count"] == 3
    assert result["blocking_prompt_count"] == 2
    assert all(f["line"] == 1 for f in result["findings"])


def test_vegetation_conflict_is_review_only(tmp_path):
    (tmp_path / "prompts60s.txt").write_text(
        "Windblown leaves sway, while all vegetation remains motionless. [60s]\n",
        encoding="utf-8")
    result = audit(tmp_path)
    assert result["blocking_count"] == 0
    assert result["review_count"] == 1

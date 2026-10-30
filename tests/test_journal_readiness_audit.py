"""Evidence audit must not mistake approvals/counts for independent validation."""

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_journal_readiness import build_audit, mask_summary, study_summary


def test_study_export_whitelists_aggregates_and_drops_identifiers():
    data = {
        "status": "interim", "snapshot_utc": "2026-10-29T00:00:00Z",
        "raters": {"secret-participant": {"code_hash": "secret"}},
        "counts": {"original": {"valid_complete": 12, "responses": 100,
                                 "participant_ids": ["secret-participant"]},
                   "secret-participant": {"valid_complete": 1}},
        "extensions": {"validation": {"raters": {"private-rater": {}}}},
    }
    result = study_summary(data)
    assert result["counts_by_module"] == {"original": {"responses": 100, "valid_complete": 12}}
    assert "secret" not in json.dumps(result)
    assert "private-rater" not in json.dumps(result)
    assert result["status"] == "aggregate_snapshot_only_not_metric_admission"


def test_approved_ai_masks_do_not_become_independent_annotation(tmp_path):
    folder = tmp_path / "masks"
    (folder / "scene").mkdir(parents=True)
    (folder / "scene/labels.png").write_bytes(b"inventory-does-not-decode")
    (folder / "review_manifest.json").write_text(json.dumps({"scenes": {
        "scene": {"status": "approved", "reviewer": "Codex (AI visual review)"}
    }}))
    result = mask_summary(tmp_path, "masks")
    assert result["label_png_count"] == 1
    assert result["review_status_counts"] == {"approved": 1}
    assert result["ai_reviewer_mentioned_count"] == 1
    assert result["human_approval_mentioned_count"] == 0
    assert "not established" in result["independent_human_annotation"]


def test_missing_artifacts_remain_missing_and_raw_snapshots_are_refused(tmp_path):
    result = build_audit(tmp_path, benchmark_root=tmp_path)
    assert result["cohorts"]["method_fresh"]["status"] == "missing"
    assert result["human_study"]["status"] == "missing"
    assert result["rights_metadata"]["snf_i2v_pairs"] == 0
    with pytest.raises(ValueError, match="aggregate"):
        build_audit(tmp_path, benchmark_root=tmp_path, study_relative="snapshot_readonly.json")

"""Tests for transport annotation geometry and review admission."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_transport_annotations import validate  # noqa: E402


def test_draft_pilot_is_structurally_valid_but_not_release_admitted():
    payload = json.loads((ROOT / "manifest" / "transport_annotation_pilot.json").read_text())
    errors, warnings = validate(payload)
    assert errors == []
    assert len(warnings) == 4
    strict_errors, _ = validate(payload, strict_release=True)
    assert len(strict_errors) == 4
    assert all("human review" in error for error in strict_errors)


def test_applicable_direction_requires_path_and_roi():
    payload = json.loads((ROOT / "manifest" / "transport_annotation_pilot.json").read_text())
    payload["entries"] = [dict(payload["entries"][0])]
    payload["entries"][0]["direction"] = {"status": "applicable", "path_xy": [[0.5, 0.5]]}
    errors, _ = validate(payload)
    assert any("path_xy" in error for error in errors)
    assert any("transport_roi_xy" in error for error in errors)

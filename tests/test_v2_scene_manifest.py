"""Tests for the structured 96-scene authoring and release gate."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_v2_scene_manifest import validate  # noqa: E402

CONTRACT = json.loads((ROOT / "configs" / "snf_v2_scene_contract.json").read_text())


def _base(scene_id, medium, tracks=None):
    tracks = tracks or ["t2v"]
    row = {
        "scene_id": scene_id,
        "variant_id": "base",
        "variant_kind": "base",
        "tracks": tracks,
        "medium": medium,
        "split": "development",
        "model_visible_prompt": "A fixed tripod view shows material moving continuously through the scene.",
        "duration_policy": {"mode": "matched_prefix", "prefixes_s": [60, 120, 240], "max_duration_s": 240},
        "rigid_support_description": "rocks at the image edge",
        "moving_material_description": "the visible natural material",
        "motion_regime": "one_way_transport",
        "direction": {"status": "applicable", "path": [[0.1, 0.5], [0.9, 0.5]],
                      "transport_roi": [[0.1, 0.2], [0.9, 0.2], [0.9, 0.8], [0.1, 0.8]]},
        "incoming": {"status": "not_applicable", "reason": "no source boundary"},
    }
    if "i2v" in tracks:
        row["i2v_source"] = {"source_image_id": scene_id, "crop_policy": "reviewed-content-preserving"}
    return row


def test_valid_authoring_record_reports_allocation_shortfall_without_failing():
    result = validate([_base("scene-001", "river_stream")], CONTRACT)
    assert result["valid_records"] is True
    assert result["release_ready"] is False
    assert result["exit_failure"] is False
    assert result["release_failures"] == ["base_scene_target", "per_medium_target", "water_share"]


def test_prompt_leakage_and_missing_i2v_source_are_blocking():
    row = _base("scene-001", "windborne", tracks=["i2v"])
    row["model_visible_prompt"] += " The evaluator should inspect the benchmark score."
    del row["i2v_source"]
    result = validate([row], CONTRACT)
    assert result["valid_records"] is False
    assert {error["code"] for error in result["errors"]} >= {"prompt_leakage", "i2v_source"}


def test_counterfactual_does_not_increase_base_count():
    base = _base("scene-001", "fire_smoke")
    variant = dict(base)
    variant.update({"variant_id": "reverse", "variant_kind": "counterfactual",
                    "parent_variant_id": "base"})
    result = validate([base, variant], CONTRACT)
    assert result["allocation"]["base_scene_count"] == 1
    assert result["allocation"]["counterfactual_count"] == 1


def test_balanced_96_scene_suite_clears_release_allocation_gate():
    records = []
    for medium in CONTRACT["media"]:
        for index in range(16):
            records.append(_base(f"{medium}-{index:02d}", medium))
    result = validate(records, CONTRACT, strict_release=True)
    assert result["release_ready"] is True
    assert result["exit_failure"] is False
    assert result["allocation"]["open_or_channel_water_share"] == 32 / 96


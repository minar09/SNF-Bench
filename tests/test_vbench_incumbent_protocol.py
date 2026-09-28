"""Consistency checks for the pinned VBench-family incumbent panel."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_incumbent_protocol_is_pinned_to_the_audited_revision():
    protocol = json.loads((ROOT / "configs" / "vbench_incumbent_protocol.json").read_text())
    audit = json.loads((ROOT / "manifest" / "vbench_extension_audit.json").read_text())
    assert protocol["official_revision"] == audit["repository"]["commit"]
    assert len(protocol["official_revision"]) == 40


def test_long_incumbent_keeps_continuous_scene_and_slow_fast_branch():
    protocol = json.loads((ROOT / "configs" / "vbench_incumbent_protocol.json").read_text())
    long = protocol["vbench_long"]
    assert long["mode"] == "long_custom_input"
    assert long["dev_flag"] is True
    assert long["use_semantic_splitting"] is False
    assert long["slow_fast_weights"] == {"within_clip": 0.5, "clip_to_clip": 0.5}
    assert long["store_split_clip_and_fused_per_video_results"] is True


def test_i2v_incumbent_requires_static_camera_and_five_recorded_samples():
    protocol = json.loads((ROOT / "configs" / "vbench_incumbent_protocol.json").read_text())
    i2v = protocol["vbench_i2v"]
    assert set(i2v["dimensions"]) == {"i2v_subject", "i2v_background", "camera_motion"}
    assert i2v["camera_motion_target"] == "static"
    assert i2v["samples_per_image_prompt"] == 5


"""Contract tests tying the trajectory implementation to the v2 axis registry."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from long_horizon_protocol import AXES, summarize_record  # noqa: E402


def test_machine_contract_matches_implemented_axes_and_forbids_total_score():
    contract = json.loads((ROOT / "configs" / "snf_v2_dimension_contract.json").read_text())
    registered = {axis["id"] for axis in contract["headline_candidates"]}
    assert registered == set(AXES)
    assert contract["reporting"]["aggregate_score"] is False
    assert contract["reporting"]["uncertainty_unit"] == "scene_id"
    assert all(axis["required_controls"] for axis in contract["headline_candidates"])


def test_incoming_windows_are_withheld_when_support_gate_fails():
    record = {
        "video_id": "incoming-1",
        "scene_id": "scene-1",
        "model_id": "model-1",
        "seed": 0,
        "track": "i2v",
        "medium": "river_stream",
        "duration_s": 10.0,
        "samples": [
            {"t_s": 0.0, "support_error_px": 0.2, "incoming_flux_px_s": 1.0},
            {"t_s": 4.0, "support_error_px": 0.4, "incoming_flux_px_s": 1.0},
            {"t_s": 5.0, "support_error_px": 3.0, "incoming_flux_px_s": 1.0},
            {"t_s": 9.0, "support_error_px": 4.0, "incoming_flux_px_s": 1.0},
        ],
    }
    result = summarize_record(
        record,
        thresholds={
            "support_stability": {"max": 2.0},
            "incoming_transport": {"min": 0.5},
        },
    )
    incoming = result["axes"]["incoming_transport"]
    assert incoming["support_gate"]["passed_windows"] == 1
    assert incoming["support_gate"]["failed_windows"] == 1
    assert incoming["windows"][0]["interpretation_status"] == "eligible"
    assert incoming["windows"][1]["interpretation_status"] == "withheld_support_unstable"


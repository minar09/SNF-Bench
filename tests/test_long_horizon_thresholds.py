"""Tests for frozen default and medium-specific failure thresholds."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from long_horizon_protocol import summarize_record  # noqa: E402


def test_medium_override_replaces_default_axis_threshold():
    record = {
        "video_id": "ocean-1",
        "scene_id": "scene-ocean",
        "model_id": "model-1",
        "seed": 0,
        "track": "t2v",
        "medium": "ocean_waves",
        "duration_s": 10.0,
        "samples": [
            {"t_s": 0.0, "long_lag_recurrence": 0.8},
            {"t_s": 4.0, "long_lag_recurrence": 0.8},
            {"t_s": 5.0, "long_lag_recurrence": 0.8},
            {"t_s": 9.0, "long_lag_recurrence": 0.8},
        ],
    }
    thresholds = {
        "default": {"non_recurrence": {"max": 0.7}},
        "by_medium": {"ocean_waves": {"non_recurrence": {"max": 0.9}}},
    }
    result = summarize_record(record, thresholds=thresholds)
    recurrence = result["axes"]["non_recurrence"]
    assert result["threshold_scope"] == "medium:ocean_waves"
    assert recurrence["failure"]["rule"] == {"max": 0.9}
    assert recurrence["failure"]["first_failure_s"] is None


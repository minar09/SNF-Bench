"""Behavioral tests for the fixed-duration long-horizon protocol."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from long_horizon_protocol import make_windows, summarize_record  # noqa: E402


def _record(samples, duration_s=10.0, applicability=None):
    return {
        "video_id": "video-1",
        "scene_id": "scene-1",
        "model_id": "model-1",
        "seed": 7,
        "track": "i2v",
        "medium": "river_stream",
        "duration_s": duration_s,
        "applicability": applicability or {},
        "samples": samples,
    }


def test_windows_use_seconds_and_only_include_complete_intervals():
    assert make_windows(12.0, 5.0, 5.0) == [(0.0, 5.0), (5.0, 10.0)]
    assert make_windows(20.0, 5.0, 5.0) == [
        (0.0, 5.0), (5.0, 10.0), (10.0, 15.0), (15.0, 20.0)
    ]


def test_direction_is_time_weighted_for_irregular_samples():
    samples = [
        {"t_s": 0.0, "signed_path_speed_px_s": 1.0},
        {"t_s": 4.0, "signed_path_speed_px_s": -1.0},
        {"t_s": 5.0, "signed_path_speed_px_s": 1.0},
        {"t_s": 9.0, "signed_path_speed_px_s": 1.0},
    ]
    out = summarize_record(_record(samples), window_s=5.0, min_samples=2)
    first = out["axes"]["directional_transport"]["windows"][0]
    # Voronoi weights are 2 s forward and 3 s backward in the first window.
    assert first["directional_persistence"] == pytest.approx(-0.2)
    assert first["wrong_way_fraction"] == pytest.approx(0.6)


def test_missing_and_non_applicable_axes_are_preserved_not_imputed():
    samples = [
        {"t_s": 0.0, "support_error_px": 0.1},
        {"t_s": 4.0, "support_error_px": 0.2},
        {"t_s": 5.0, "support_error_px": 0.3},
        {"t_s": 9.0, "support_error_px": 0.4},
    ]
    out = summarize_record(_record(
        samples,
        applicability={
            "directional_transport": {
                "status": "not_applicable",
                "reason": "periodic_wave_prompt",
            }
        },
    ))
    assert out["aggregation"] == "none; report axes separately"
    assert out["axes"]["directional_transport"]["status"] == "not_applicable"
    assert out["axes"]["flow_presence"]["status"] == "unscorable"
    assert out["axes"]["flow_presence"]["reason"].startswith("missing_signal:")


def test_failure_time_requires_external_threshold_and_uses_worst_tail():
    samples = [
        {"t_s": 0.0, "support_error_px": 0.5},
        {"t_s": 4.0, "support_error_px": 0.8},
        {"t_s": 5.0, "support_error_px": 2.5},
        {"t_s": 9.0, "support_error_px": 3.0},
    ]
    descriptive = summarize_record(_record(samples))
    assert descriptive["axes"]["support_stability"]["failure"]["calibrated"] is False
    assert descriptive["axes"]["support_stability"]["failure"]["first_failure_s"] is None

    calibrated = summarize_record(
        _record(samples), thresholds={"support_stability": {"max": 2.0}}
    )
    failure = calibrated["axes"]["support_stability"]["failure"]
    assert failure["first_failure_s"] == 5.0
    assert failure["longest_failing_run"] == 1


def test_recurrence_range_is_validated():
    with pytest.raises(ValueError, match="outside"):
        summarize_record(_record([
            {"t_s": 0.0, "long_lag_recurrence": 1.2},
            {"t_s": 4.0, "long_lag_recurrence": 0.5},
            {"t_s": 5.0, "long_lag_recurrence": 0.4},
            {"t_s": 9.0, "long_lag_recurrence": 0.3},
        ]))


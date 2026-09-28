"""Controlled-field tests for the exploratory M2 endpoint probes."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from flow_endpoint_probes import (  # noqa: E402
    extract_endpoint_samples,
    fit_support_similarity,
    residual_dynamic_signal,
)
from long_horizon_protocol import summarize_record  # noqa: E402


def _points(dx, dy, n=64):
    side = int(np.sqrt(n))
    x, y = np.meshgrid(np.linspace(10, 90, side), np.linspace(10, 70, side))
    xy = np.stack([x.ravel(), y.ravel()], axis=1).astype(np.float32)
    uv = np.tile(np.array([[dx, dy]], dtype=np.float32), (len(xy), 1))
    return np.concatenate([xy, uv], axis=1)


def test_support_fit_recovers_coherent_camera_translation():
    fit = fit_support_similarity(_points(3.0, -2.0))
    assert fit["status"] == "scored"
    assert fit["translation_x_px"] == pytest.approx(3.0, abs=1e-4)
    assert fit["translation_y_px"] == pytest.approx(-2.0, abs=1e-4)
    assert fit["support_error_px"] == pytest.approx(np.hypot(3, 2), abs=1e-4)
    assert fit["support_fit_residual_px"] == pytest.approx(0.0, abs=1e-4)


def test_dynamic_signal_removes_global_motion_and_reversal_flips_sign():
    fit = fit_support_similarity(_points(3.0, -2.0))
    forward = _points(7.0, -2.0)
    reverse = _points(-1.0, -2.0)
    a = residual_dynamic_signal(forward, fit["matrix"], 8.0, [1.0, 0.0])
    b = residual_dynamic_signal(reverse, fit["matrix"], 8.0, [1.0, 0.0])
    assert a["dynamic_speed_px_s"] == pytest.approx(32.0, abs=1e-4)
    assert b["dynamic_speed_px_s"] == pytest.approx(32.0, abs=1e-4)
    assert a["signed_path_speed_px_s"] == pytest.approx(32.0, abs=1e-4)
    assert b["signed_path_speed_px_s"] == pytest.approx(-32.0, abs=1e-4)


def test_ping_pong_has_motion_but_zero_directional_persistence():
    samples = []
    for t_s, sign in zip([0.1, 1.35, 2.65, 3.9], [1, -1, 1, -1]):
        samples.append({"t_s": t_s, "dynamic_speed_px_s": 8.0,
                        "signed_path_speed_px_s": 8.0 * sign})
    record = {"video_id": "v", "scene_id": "s", "model_id": "m", "seed": 0,
              "track": "i2v", "medium": "river_stream", "duration_s": 4.0,
              "samples": samples}
    result = summarize_record(record, window_s=4.0, min_samples=2)
    motion = result["axes"]["flow_presence"]["windows"][0]
    direction = result["axes"]["directional_transport"]["windows"][0]
    assert motion["median"] == pytest.approx(8.0)
    assert direction["directional_persistence"] == pytest.approx(0.0)
    assert direction["wrong_way_fraction"] == pytest.approx(0.5)


def test_endpoint_extraction_preserves_the_unmeasured_middle():
    early_support = np.stack([_points(0.0, 0.0)] * 2)
    late_support = np.stack([_points(1.0, 0.0)] * 2)
    early_dynamic = np.stack([_points(2.0, 0.0)] * 2)
    late_dynamic = np.stack([_points(3.0, 0.0)] * 2)
    cache = {
        "early_static": early_support,
        "early_dyn": early_dynamic,
        "late_static": late_support,
        "late_dyn": late_dynamic,
        "meta": np.array([10, 2, 100, 80, 2]),
    }
    samples, audit = extract_endpoint_samples(cache, path_unit_xy=[1, 0])
    assert [s["t_s"] for s in samples] == pytest.approx([0.25, 0.75, 3.75, 4.25])
    assert audit["missing_middle"] == 5
    assert audit["temporal_coverage"] == pytest.approx(4 / 9)
    assert samples[0]["signed_path_speed_px_s"] == pytest.approx(4.0, abs=1e-4)
    assert samples[-1]["signed_path_speed_px_s"] == pytest.approx(4.0, abs=1e-4)

"""Known answers for cand-coverage-0 on synthetic masks and flows."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import realism_extent as X  # noqa: E402

H, W, T = 120, 200, 16


def masks():
    mat = np.zeros((H, W), bool)
    mat[:, :100] = True
    return mat, ~mat


def noise(sigma=0.03, seed=0):
    return np.random.default_rng(seed).normal(0, sigma, (T, H, W, 2)).astype(np.float32)


@pytest.mark.parametrize("p", [0.05, 0.15, 0.30, 1.0])
def test_coverage_equals_the_moving_share(p):
    mat, sup = masks()
    f = noise()
    cols = int(round(p * 100))
    f[:, :, :cols, 0] += 1.0                      # a patch of p of the material moves
    out = X.coverage(f, mat, sup)
    assert out["C"] == pytest.approx(p, abs=0.01)
    if p <= 0.15:
        assert out["E10"] > 0.5                   # concentrated: local motion
    if p == 1.0:
        assert out["E10"] == pytest.approx(0.1, abs=0.02)


def test_frozen_material_has_zero_coverage():
    mat, sup = masks()
    out = X.coverage(noise(), mat, sup)
    assert out["C"] < 0.02


def test_motion_that_stops_shows_in_the_sub_windows():
    mat, sup = masks()
    f = noise()
    f[: T // 2, :, :100, 0] += 1.0                # moves, then stops half way
    out = X.coverage(f, mat, sup)
    assert out["C_sub"][0] > 0.95 and out["C_end"] < 0.05 and out["C_min"] < 0.05


def test_abstains_on_tiny_material():
    mat = np.zeros((H, W), bool)
    mat[:2, :2] = True
    assert "abstain" in X.coverage(noise(), mat, ~mat)

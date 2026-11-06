"""Known answers for the DAMP port."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import realism_transport as TR  # noqa: E402

H, W, T = 60, 100, 12


def setup():
    mat = np.zeros((H, W), bool)
    mat[:, :50] = True
    noise = np.random.default_rng(0).normal(0, 0.05, (T, H, W, 2)).astype(np.float32)
    return mat, noise


def test_steady_transport_scores_high_and_noise_low():
    mat, f = setup()
    f[:, :, :50, 0] += 1.0
    out = TR.transport(f, mat, ~mat)
    assert out["damp_material"] > 0.95 and out["damp_support"] < 0.4 and out["delta"] > 0.5


def test_motion_without_transport_scores_low():
    mat, f = setup()
    ang = np.random.default_rng(1).uniform(0, 2 * np.pi, (T, H, 50))
    f[..., :50, 0] += np.cos(ang)
    f[..., :50, 1] += np.sin(ang)                     # active every pair, no net displacement
    out = TR.transport(f, mat, ~mat)
    assert out["damp_material_active"] < 0.4 and out["delta"] < 0.15


def test_global_slide_gives_no_paired_contrast():
    mat, f = setup()
    f[..., 0] += 1.0                                  # whole frame translates
    assert abs(TR.transport(f, mat, ~mat)["delta"]) < 0.02

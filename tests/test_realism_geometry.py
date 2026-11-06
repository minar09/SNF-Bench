"""Known answers for the geometry-referenced direction candidates (synthetic masks and flows)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import realism_geometry as G  # noqa: E402

H, W, T = 240, 416, 12


def river(angle_deg=0.0, half_width=40):
    """A straight channel through the frame centre at the given angle (deg, image coords)."""
    yy, xx = np.mgrid[:H, :W]
    a = np.deg2rad(angle_deg)
    d = -(xx - W / 2) * np.sin(a) + (yy - H / 2) * np.cos(a)
    return np.abs(d) <= half_width


def uniform_flow(angle_deg, speed=2.0, noise=0.0, seed=0):
    a = np.deg2rad(angle_deg)
    f = np.zeros((T, H, W, 2), np.float32)
    f[..., 0], f[..., 1] = speed * np.cos(a), speed * np.sin(a)
    if noise:
        f += np.random.default_rng(seed).normal(0, noise, f.shape).astype(np.float32)
    return f


@pytest.mark.parametrize("angle", [0, 30, 90, 135])
def test_along_channel_scores_plus_one_and_across_minus_one(angle):
    m = river(angle)
    assert G.channel_alignment(uniform_flow(angle), m, 0.5)["A"] == pytest.approx(1.0, abs=0.02)
    assert G.channel_alignment(uniform_flow(angle + 90), m, 0.5)["A"] == pytest.approx(-1.0, abs=0.02)


def test_alignment_is_sign_free_and_reversal_invariant():
    m = river(20)
    fwd = G.channel_alignment(uniform_flow(20), m, 0.5)["A"]
    rev = G.channel_alignment(uniform_flow(200), m, 0.5)["A"]
    assert fwd == pytest.approx(rev, abs=1e-6)


def test_isotropic_random_flow_scores_near_zero():
    m = river(0)
    rng = np.random.default_rng(1)
    ang = rng.uniform(0, 2 * np.pi, (H, W))
    f = np.broadcast_to(np.stack([np.cos(ang), np.sin(ang)], -1) * 2.0, (T, H, W, 2)).astype(np.float32)
    assert abs(G.channel_alignment(f, m, 0.5)["A"]) < 0.05


def test_alignment_abstains_without_banks_or_flow():
    full = np.ones((H, W), bool)                      # material fills the frame: no bank
    assert "abstain" in G.channel_alignment(uniform_flow(0), full, 0.5)
    assert "abstain" in G.channel_alignment(uniform_flow(0, speed=0.1), river(0), 0.5)


def test_sign_stability_drops_under_a_mid_horizon_reversal():
    m = river(0)
    f = uniform_flow(0)
    steady = G.channel_alignment(f, m, 0.5)["sign_stability"]
    f[T // 2:] *= -1.0
    f[T // 2:] *= 0.5                                 # keep a net mean so the weights stay positive
    flipped = G.channel_alignment(f, m, 0.5)
    assert steady == pytest.approx(1.0, abs=1e-6)
    assert flipped.get("sign_stability") is None or flipped["sign_stability"] < 0.5


def test_gravity_sign_follows_image_down():
    m = river(90)
    assert G.gravity_sign(uniform_flow(90), m, 0.5)["G"] == pytest.approx(1.0)
    assert G.gravity_sign(uniform_flow(-90), m, 0.5)["G"] == pytest.approx(-1.0)
    assert G.gravity_sign(uniform_flow(0), m, 0.5)["G"] == pytest.approx(0.0, abs=1e-6)


def still_noise(seed=0, sigma=0.03):
    """Codec/RAFT noise on a still video: tiny, and identical in every pair (identical frames)."""
    n = np.random.default_rng(seed).normal(0, sigma, (1, H, W, 2)).astype(np.float32)
    return np.repeat(n, T, axis=0)


def test_v1_gate_abstains_on_a_freeze_where_v0_scores_it():
    m = river(90)
    f = still_noise()
    sup = ~m
    tau0 = float(np.percentile(np.linalg.norm(f.mean(0), axis=-1)[sup], 95))
    assert "G" in G.gravity_sign(f, m, tau0)                    # the v0 defect
    assert "abstain" in G.geometry_v1("down", uniform_flow(90), m, sup)   # support moves as much
    assert "abstain" in G.geometry_v1("down", f, m, sup)
    assert "abstain" in G.geometry_v1("channel", f, m, sup)


def test_v1_gate_passes_real_motion_and_keeps_v0_values():
    m = river(90)
    f = uniform_flow(90) * m[None, ..., None] + still_noise()     # only the material moves
    out = G.geometry_v1("down", f, m, ~m)
    assert out["G"] == pytest.approx(1.0, abs=0.01)
    assert out["gravity_stability"] == pytest.approx(1.0, abs=0.01)


def test_gravity_stability_drops_under_pingpong_but_G_does_not():
    m = river(90)
    f = uniform_flow(90) * m[None, ..., None]
    f[5:10] *= -1.0                                  # 7 pairs down, 5 up: an unequal share of each phase
    out = G.geometry_v1("down", f, m, ~m)
    assert out["G"] == pytest.approx(1.0, abs=0.01)  # the mean still points down
    assert out["gravity_stability"] < 0.25

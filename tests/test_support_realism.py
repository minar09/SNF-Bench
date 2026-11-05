"""Synthetic checks for the support-realism pilot statistics and the composite controls."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import composite_ops as ops        # noqa: E402
import pilot_support_realism as S  # noqa: E402

H, W = 480, 832


def masks():
    dyn = np.zeros((H, W), bool)
    dyn[:, :300] = True
    return dyn, ~dyn


def texture(seed=0):
    rng = np.random.default_rng(seed)
    import cv2
    return cv2.GaussianBlur(rng.uniform(0, 255, (H + 40, W + 40)), (0, 0), 3)


def test_still_support_is_zero_change_and_zero_step():
    dyn, sup = masks()
    s = S.stats(np.where(dyn, 10.0, 0.0), dyn, sup)
    assert s["support_change"] == 0.0
    assert s["boundary_step"] < 1e-6


def test_uniform_activity_has_unit_ratios():
    dyn, sup = masks()
    s = S.stats(np.ones((H, W)), dyn, sup)
    assert abs(s["edge_spill"] - 1) < 1e-9 and abs(s["boundary_step"] - 1) < 1e-9


def test_no_dynamic_region_abstains_with_reason():
    s = S.stats(np.ones((H, W)), np.zeros((H, W), bool), np.ones((H, W), bool))
    assert "edge_spill" not in s and s["abstain"]["edge_spill"] == "no dynamic region"


def test_compensation_removes_drift_and_illumination_but_not_change():
    _, sup = masks()
    t = texture()
    drift = np.stack([t[20:20 + H, 20 + k:20 + k + W] + 3 * k for k in range(6)])
    assert np.median(S.late_activity(drift)[sup]) > 2
    comp, info = S.compensated_activity(drift, sup)
    assert info["pairs_rejected"] == 0 and np.nanmedian(comp[sup]) < 0.5
    rng = np.random.default_rng(1)
    boil = np.stack([t[20:20 + H, 20:20 + W] + rng.normal(0, 4, (H, W)) for _ in range(6)])
    assert np.nanmedian(S.compensated_activity(boil, sup)[0][sup]) > 2


def test_composite_modes_touch_only_support():
    dyn, sup = masks()
    rng = np.random.default_rng(2)
    frames = rng.integers(0, 256, (6, H, W, 3), dtype=np.uint8)
    src = rng.integers(0, 256, (H, W, 3), dtype=np.uint8)
    assert (ops.compose("passthrough", frames, src, sup) == frames).all()
    paste = ops.compose("paste", frames, src, sup)
    assert (paste[:, sup] == src[sup]).all() and (paste[:, dyn] == frames[:, dyn]).all()
    for m in ops.MODES:
        assert (ops.compose(m, frames, src, sup)[:, dyn] == frames[:, dyn]).all(), m


def test_residual_paste_keeps_parent_successive_change():
    dyn, sup = masks()
    rng = np.random.default_rng(3)
    base = rng.integers(60, 190, (H, W, 3)).astype(np.int16)
    frames = np.clip(base + rng.integers(-5, 6, (8, H, W, 3)), 0, 255).astype(np.uint8)
    src = np.full((H, W, 3), 128, np.uint8)
    out = ops.compose("paste_residual", frames, src, sup)
    d_parent = np.abs(np.diff(frames[:, sup].astype(int), axis=0)).mean()
    d_out = np.abs(np.diff(out[:, sup].astype(int), axis=0)).mean()
    assert abs(d_parent - d_out) < 0.05 * d_parent


def test_feather_is_source_deep_inside_support():
    _, sup = masks()
    frames = np.zeros((2, H, W, 3), np.uint8)
    src = np.full((H, W, 3), 200, np.uint8)
    out = ops.compose("paste_feather", frames, src, sup)
    assert (out[:, :, 700] == 200).all() and out[0, 240, 301, 0] < 100


def test_boundary_bands_start_past_the_ignore_gap():
    dyn = np.zeros((H, W), bool)
    dyn[:, :300] = True
    sup = np.zeros((H, W), bool)
    sup[:, 312:] = True                      # 12 px ignore band, wider than NEAR
    act = np.where(dyn, 10.0, 0.0)
    act[:, 312:340] = 5.0                    # change in the support's first ~28 px, none further out
    s = S.stats(act, dyn, sup)
    assert s["support_gap_px"] >= 12 and "boundary_step" in s
    assert abs(s["boundary_step"] - 0.5) < 0.05


def test_textureless_support_rejects_compensation():
    _, sup = masks()
    flat = np.full((4, H, W), 100.0)
    try:
        S.compensated_activity(flat, sup)
    except S.Abstain as e:
        assert "texture" in str(e) or "rejected" in str(e)
    else:
        raise AssertionError("a textureless support must not yield a drift estimate")

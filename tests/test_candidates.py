"""Candidate kernels: reference data and the single-cause controls they target."""
import os
import sys

import cv2
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))
import snf_candidates as C  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ciede2000_sharma.txt")
H, W = 480, 832


def test_ciede2000_matches_the_authors_test_pairs():
    rows = np.loadtxt(DATA, comments="#")
    got = C.ciede2000(rows[:, 0:3], rows[:, 3:6])
    assert np.max(np.abs(got - rows[:, 6])) < 1e-4, np.max(np.abs(got - rows[:, 6]))


def test_ciede2000_is_symmetric_and_zero_on_identity():
    rows = np.loadtxt(DATA, comments="#")
    assert np.allclose(C.ciede2000(rows[:, 3:6], rows[:, 0:3]), rows[:, 6], atol=1e-4)
    assert np.allclose(C.ciede2000(rows[:, 0:3], rows[:, 0:3]), 0)


@pytest.mark.parametrize("bgr, lab", [
    ((255, 255, 255), (100.0, 0.0, 0.0)),
    ((0, 0, 255), (53.2408, 80.0925, 67.2032)),     # sRGB red
    ((0, 0, 0), (0.0, 0.0, 0.0)),
])
def test_srgb_to_lab_reference_colours(bgr, lab):
    got = C.srgb_to_lab(np.array([[bgr]], np.uint8))[0, 0]
    assert np.allclose(got, lab, atol=0.01), got


def _textured(seed=0):
    rng = np.random.default_rng(seed)
    return cv2.GaussianBlur(rng.integers(0, 256, (H, W, 3), dtype=np.uint8), (0, 0), 2)


def test_equal_mean_texture_swap_is_seen_pixelwise_but_not_by_region_means():
    src = _textured(0)
    sup = np.zeros((H, W), bool); sup[:240] = True
    swapped = src.copy()
    region = swapped[:240].reshape(-1, 3)
    swapped[:240] = np.random.default_rng(1).permutation(region).reshape(240, W, 3)
    # region means are unchanged by a permutation ...
    lab_s, lab_w = C.srgb_to_lab(src)[sup].mean(0), C.srgb_to_lab(swapped)[sup].mean(0)
    assert np.linalg.norm(lab_s - lab_w) < 1e-6
    # ... pixelwise CIEDE2000 is not fooled
    r = C.support_de00([src, swapped], src, sup)
    assert r["mean"][0] < 1e-6 and r["mean"][1] > 5


def _clip(kind, n=48):
    src = _textured(2)
    dyn = np.zeros((H, W), bool); dyn[256:448, 64:768] = True
    rng = np.random.default_rng(3)
    frames = []
    for t in range(n):
        f = src.copy()
        if kind == "moving":                      # a texture that keeps changing
            f[dyn] = cv2.GaussianBlur(rng.integers(0, 256, (H, W, 3), dtype=np.uint8),
                                      (0, 0), 2)[dyn]
        elif kind == "glassy":                    # progressively smoothed material
            f[dyn] = cv2.GaussianBlur(src, (0, 0), 0.5 + 0.2 * t)[dyn]
        frames.append(f)                          # "frozen": the sharp source, unchanged
    return frames, src, dyn


def test_detail_drops_for_glassy_material_but_not_for_frozen_sharp():
    g, src, dyn = _clip("glassy")
    z, _, _ = _clip("frozen")
    rg = C.material_detail_activity(g, src, dyn)
    rz = C.material_detail_activity(z, src, dyn)
    assert rg["detail_ratio_src"][-1] < 0.2
    assert abs(rz["detail_ratio_src"][-1] - 1) < 1e-6      # frozen keeps its detail ...
    assert max(rz["activity"]) == 0                          # ... and that is why activity is read beside it


def test_activity_separates_moving_from_frozen():
    m, src, dyn = _clip("moving")
    z, _, _ = _clip("frozen")
    assert np.mean(C.material_detail_activity(m, src, dyn)["activity"][1:]) > 10
    assert np.mean(C.material_detail_activity(z, src, dyn)["activity"][1:]) == 0


def test_recurrence_finds_an_exact_loop_and_not_fresh_motion():
    m, src, dyn = _clip("moving", n=24)            # 3 s of distinct frames
    loop = m + m + m                               # replayed twice
    r_loop = C.recurrence(loop, dyn, min_lag_s=2.0, run_s=1.0)
    fresh, _, _ = _clip("moving", n=72)
    r_fresh = C.recurrence(fresh, dyn, min_lag_s=2.0, run_s=1.0)
    assert r_loop["score"] > 0.99 and abs(r_loop["lag_s"] - 3.0) < 1e-9
    assert r_fresh["score"] < 0.5


def test_tiles_lie_entirely_inside_the_mask():
    dyn = np.zeros((H, W), bool); dyn[10:100, 10:300] = True
    for y, x in C.interior_tiles(dyn):
        assert dyn[y:y + C.TILE, x:x + C.TILE].all()

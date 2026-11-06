"""Known geometry of the spatial controls."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import spatial_ops as SO  # noqa: E402

H, W = 120, 240


def band(angle_deg, half=20):
    yy, xx = np.mgrid[:H, :W]
    a = np.deg2rad(angle_deg)
    return np.abs(-(xx - W / 2) * np.sin(a) + (yy - H / 2) * np.cos(a)) <= half


@pytest.mark.parametrize("angle", [0, 30, 90])
def test_along_follows_the_channel_and_across_is_perpendicular(angle):
    m = band(angle)
    along, across = SO.direction("conveyor_along", m), SO.direction("conveyor_across", m)
    a = np.deg2rad(angle)
    assert abs(along @ np.array([np.cos(a), np.sin(a)])) == pytest.approx(1.0, abs=0.02)
    assert abs(along @ across) < 1e-9


def test_conveyor_translates_the_material_only():
    m = band(0)
    rng = np.random.default_rng(0)
    frames = np.repeat(rng.integers(0, 255, (1, H, W, 3), dtype=np.uint8), 8, axis=0)
    out = SO.compose("conveyor_down", frames, m, t0=2)
    assert np.array_equal(out[:, ~m], frames[:, ~m])                 # support untouched
    k = 4
    tile, x0, y0 = SO.texture_tile(frames[2], m)
    assert np.array_equal(out[2][m], frames[2][m])                    # k = 0 is frame t0 itself
    shifted = SO.compose("conveyor_down", frames, m, t0=2)[2 + k]
    yy, xx = np.nonzero(m)
    want = tile[(yy - y0 - int(SO.CONVEYOR_PX * k)) % tile.shape[0], (xx - x0) % tile.shape[1]]
    assert np.array_equal(shifted[m], want)                           # 6 px down, inside the material


@pytest.mark.parametrize("mode,share", list(SO.PATCH.items()))
def test_patch_holds_the_share_and_is_compact(mode, share):
    m = band(0, half=40)
    p = SO.patch(m, share)
    assert p.sum() / m.sum() == pytest.approx(share, abs=0.01)
    ys, xs = np.nonzero(p)
    assert xs.max() - xs.min() < W                                     # one compact disc, not the band


def test_tile_is_periodic_and_holds_material_texture():
    m = band(0)
    frame = np.random.default_rng(1).integers(0, 255, (H, W, 3), dtype=np.uint8)
    tile, x0, y0 = SO.texture_tile(frame, m)
    h, w = tile.shape[0] // 2, tile.shape[1] // 2
    assert np.array_equal(tile[:h, :w][m[y0:y0 + h, x0:x0 + w]], frame[m])
    assert np.array_equal(tile[:, :w], tile[:, w:][:, ::-1]) and np.array_equal(tile[:h], tile[h:][::-1])

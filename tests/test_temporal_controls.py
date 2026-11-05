"""Known-answer tests for scripts/temporal_ops.py on a translating synthetic pattern."""
import os
import sys

import cv2
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import temporal_ops as T  # noqa: E402

N, T0, P, FADE = 40, 20, 6, 2


def clip(v=1):
    """A random texture translating right by v px per frame (circularly), plus a static band at the bottom."""
    tex = cv2.GaussianBlur(np.random.default_rng(0).uniform(0, 255, (64, 96)), (0, 0), 1.5)
    tex = np.clip(np.rint(128 + 3 * (tex - tex.mean())), 0, 255).astype(np.uint8)
    f = np.empty((N, 64, 96, 3), np.uint8)
    for t in range(N):
        f[t] = np.roll(tex, v * t, axis=1)[..., None]
    f[:, 48:] = 90
    return f


def shift(a, b):
    (dx, _), _ = cv2.phaseCorrelate(a[..., 0].astype(np.float64), b[..., 0].astype(np.float64))
    return dx


def steps(f):
    return np.abs(np.diff(f.astype(np.float64), axis=0)).mean(axis=(1, 2, 3))


@pytest.mark.parametrize("mode", T.MODES)
def test_length_kept_and_head_untouched(mode):
    f = clip()
    dyn = np.zeros(f.shape[1:3], bool)
    dyn[:48] = True
    out = T.compose(mode, f, dyn=dyn, t0=T0, period=P, fade=FADE)
    assert out.shape == f.shape and out.dtype == np.uint8
    assert np.array_equal(out[:T0], f[:T0])


def test_reverse_tail_flips_direction_at_matched_speed():
    f = clip()
    out = T.compose("reverse_tail", f, t0=T0)
    fwd = [shift(f[t], f[t + 1]) for t in range(T0, N - 1)]
    rev = [shift(out[t], out[t + 1]) for t in range(T0, N - 1)]
    assert np.median(fwd) == pytest.approx(1.0, abs=0.1)
    assert np.median(rev) == pytest.approx(-1.0, abs=0.1)


def test_pingpong_has_no_net_motion_and_no_cut():
    f = clip()
    out = T.compose("pingpong", f, t0=T0, period=P)
    assert np.array_equal(out[T0], out[T0 + 2 * P])
    assert steps(out[T0:]).max() <= steps(f).max() + 1e-9


def test_loop_exact_repeats_and_cuts():
    f = clip()
    out = T.compose("loop_exact", f, t0=T0, period=P)
    assert np.array_equal(out[T0], out[T0 + P])
    # at each repeat the pattern jumps back by the period's travel
    assert shift(out[T0 + P - 1], out[T0 + P]) == pytest.approx(-(P - 1), abs=0.15)


def test_loop_xfade_softens_the_cut():
    f = clip()
    hard = steps(T.compose("loop_exact", f, t0=T0, period=P))
    soft = steps(T.compose("loop_xfade", f, t0=T0, period=P, fade=FADE))
    assert soft[T0 + P - 1] < hard[T0 + P - 1]


def test_freeze_has_zero_change():
    out = T.compose("freeze", clip(), t0=T0)
    assert steps(out[T0:]).max() == 0


def test_speed2_doubles_step_and_ends_on_last_frame():
    f = clip()
    out = T.compose("speed2", f, t0=T0)
    assert np.array_equal(out[-1], f[-1])
    assert np.median([shift(out[t], out[t + 1]) for t in range(T0, N - 1)]) == pytest.approx(2.0, abs=0.15)


def test_speed05_halves_step_and_ends_on_last_frame():
    f = clip(v=2)
    out = T.compose("speed05", f, t0=T0)
    assert np.array_equal(out[-1], f[-1])
    # every second output frame is an unblended parent frame; between them the parent moved one frame
    exact = [t for t in range(T0, N) if (N - 1 - t) % 2 == 0]
    assert np.median([shift(out[a], out[b]) for a, b in zip(exact, exact[1:])]) == pytest.approx(2.0, abs=0.15)


def test_shuffle_is_a_fixed_permutation_of_the_tail():
    f = clip()
    a, b = T.compose("shuffle", f, t0=T0), T.compose("shuffle", f, t0=T0)
    assert np.array_equal(a, b)
    key = lambda x: sorted(map(bytes, x))  # noqa: E731
    assert key(a[T0:]) == key(f[T0:])
    assert not np.array_equal(a[T0:], f[T0:])


def test_noise_warp_moves_dynamic_region_only_without_transport():
    f = clip()
    dyn = np.zeros(f.shape[1:3], bool)
    dyn[:48] = True
    out = T.compose("noise_warp", f, dyn=dyn, t0=T0)
    assert np.array_equal(out[:, 48:], f[:, 48:])
    assert steps(out[T0:, :48]).mean() > 0
    # no transport: the tail stays anchored on frame t0 instead of following the parent
    # (the mean of warped copies is blurred, so it is only closer to t0, not equal to it)
    mean = out[T0:, :48].astype(np.float64).mean(0)
    assert np.abs(mean - f[T0, :48]).mean() < 0.75 * np.abs(mean - f[-1, :48]).mean()
    with pytest.raises(ValueError):
        T.compose("noise_warp", f, t0=T0)

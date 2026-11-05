"""Temporal realism controls (numpy + cv2): replay, direction, speed and incoherent motion.

Each op takes decoded frames (T, H, W, 3 uint8) and returns T new frames. Frames
before `t0` (default T // 2) are the parent's own; from `t0` on the op is
applied, so every late analysis window sees it. Targets
(docs/SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md §2):

* R3 direction: `reverse_tail` (the tail played backwards: matched speed,
  opposite direction), `pingpong` (forward and back every `period` frames: no
  net direction).
* R4 replay: `loop_exact` (the first `period` tail frames repeated, a cut at
  every repeat), `loop_xfade` (the same, cross-faded over `fade` frames at each
  repeat), `pingpong` again (replay without a cut), `freeze` (frame t0 held).
* R5 plausibility: `speed2` (every second frame: twice the speed, ending on the
  parent's last frame), `speed05` (half speed, neighbours linearly blended, so
  it ghosts rather than stutters), `shuffle` (tail frames in a fixed random
  order: each frame plausible, motion between them incoherent), `noise_warp`
  (frame t0 inside the dynamic region displaced by a fresh random smooth field
  each frame: motion without transport).

These are graded interventions, not ground truth for "unrealistic": whether a
human sees one as unnatural is a separate, labelled question.
"""
import cv2
import numpy as np

MODES = ("reverse_tail", "pingpong", "loop_exact", "loop_xfade", "freeze",
         "speed2", "speed05", "shuffle", "noise_warp")
PERIOD = 48         # frames: 3 s at 16 fps
FADE = 8            # frames
SEED = 20261105
WARP_PX = 4.0       # field amplitude, px
WARP_SIGMA = 24.0   # field smoothness, px


def tail_index(mode, T, t0, period=PERIOD):
    """Source frame index for every output frame, for the index-only modes."""
    t = np.arange(T)
    k = t - t0
    idx = t.copy()
    tail = t >= t0
    if mode == "reverse_tail":
        idx[tail] = T - 1 - k[tail]
    elif mode == "pingpong":
        ph = k[tail] % (2 * period)
        idx[tail] = t0 + np.where(ph < period, ph, 2 * period - 1 - ph)
    elif mode == "loop_exact":
        idx[tail] = t0 + k[tail] % period
    elif mode == "freeze":
        idx[tail] = t0
    elif mode == "speed2":
        idx[tail] = T - 1 - 2 * (T - 1 - t[tail])
    elif mode == "shuffle":
        idx[tail] = t0 + np.random.default_rng(SEED).permutation(T - t0)
    else:
        raise ValueError(mode)
    return np.clip(idx, 0, T - 1)


def smooth_field(rng, shape):
    f = rng.standard_normal(shape).astype(np.float32)
    f = cv2.GaussianBlur(f, (0, 0), WARP_SIGMA)
    return f * (WARP_PX / max(float(np.abs(f).max()), 1e-6))


def compose(mode, frames, dyn=None, t0=None, period=PERIOD, fade=FADE):
    T = len(frames)
    t0 = T // 2 if t0 is None else t0
    if mode in ("reverse_tail", "pingpong", "loop_exact", "freeze", "speed2", "shuffle"):
        return frames[tail_index(mode, T, t0, period)]
    out = frames.copy()
    if mode == "loop_xfade":
        # loop of length `period`; the last `fade` frames of each repeat blend into its first frames
        for t in range(t0, T):
            ph = (t - t0) % period
            a = frames[t0 + ph].astype(np.float64)
            if t - t0 >= period and ph < fade:
                w = (ph + 1) / (fade + 1)
                b = frames[t0 + period - fade + ph].astype(np.float64)
                a = w * a + (1 - w) * b
            out[t] = np.clip(np.rint(a), 0, 255).astype(np.uint8)
    elif mode == "speed05":
        for t in range(t0, T):
            s = (T - 1) - 0.5 * (T - 1 - t)
            i = int(np.floor(s))
            w = s - i
            j = min(i + 1, T - 1)
            out[t] = np.clip(np.rint((1 - w) * frames[i] + w * frames[j]), 0, 255).astype(np.uint8)
    elif mode == "noise_warp":
        if dyn is None:
            raise ValueError("noise_warp needs the dynamic mask")
        rng = np.random.default_rng(SEED)
        H, W = dyn.shape
        gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        base = frames[t0]
        for t in range(t0, T):
            mx = gx + smooth_field(rng, (H, W))
            my = gy + smooth_field(rng, (H, W))
            warped = cv2.remap(base, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            out[t] = np.where(dyn[..., None], warped, frames[t])
    else:
        raise ValueError(mode)
    return out

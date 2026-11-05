"""Support-composite constructions for realism controls (numpy only).

Each op takes the decoded parent frames (T, H, W, 3 uint8 RGB), the source image
(H, W, 3 uint8 RGB) and the rigid-support mask (H, W bool, label 1), and returns
new frames. Only support pixels change, except `passthrough`, which changes
nothing; it exists so that every control can be compared with a parent that has
the same decode/re-encode history (docs/SNF_PP_REALISM_REVIEW_2026_11_04.md §2).

* `passthrough`: parent unchanged.
* `paste`: source pixels in the support.
* `paste_residual`: source + the parent's own support residual about its
  temporal median. This matches the parent's support change by construction;
  it tests whether anything other than successive-frame change separates a paste.
* `paste_residual_shift`: the same residual delayed by half the clip, keeping
  its statistics but breaking its timing relative to the dynamic region.
* `paste_feather`: source blended in over `feather_px` from the support edge.
* `paste_illum`: source scaled per frame and channel to the parent's support mean.
"""
import cv2
import numpy as np

MODES = ("passthrough", "paste", "paste_residual", "paste_residual_shift",
         "paste_feather", "paste_illum")
MEDIAN_SAMPLES = 64
FEATHER_PX = 8


def temporal_median(frames, n=MEDIAN_SAMPLES):
    idx = np.linspace(0, len(frames) - 1, min(n, len(frames))).round().astype(int)
    return np.median(frames[idx], axis=0)


def compose(mode, frames, source, support, feather_px=FEATHER_PX):
    if mode not in MODES:
        raise ValueError(mode)
    out = frames.copy()
    if mode == "passthrough":
        return out
    src = source.astype(np.float64)
    if mode == "paste":
        out[:, support] = source[support]
    elif mode in ("paste_residual", "paste_residual_shift"):
        med = temporal_median(frames)[support]
        shift = len(frames) // 2 if mode == "paste_residual_shift" else 0
        for t in range(len(frames)):
            r = frames[(t + shift) % len(frames)][support].astype(np.float64) - med
            out[t][support] = np.clip(np.rint(src[support] + r), 0, 255).astype(np.uint8)
    elif mode == "paste_feather":
        d = cv2.distanceTransform(support.astype(np.uint8), cv2.DIST_L2, 5)
        a = np.clip(d / feather_px, 0, 1)[..., None]
        for t in range(len(frames)):
            out[t] = np.clip(np.rint(a * src + (1 - a) * frames[t]), 0, 255).astype(np.uint8)
    elif mode == "paste_illum":
        s_mean = src[support].mean(0)
        for t in range(len(frames)):
            g = frames[t][support].astype(np.float64).mean(0) / np.maximum(s_mean, 1e-6)
            out[t][support] = np.clip(np.rint(src[support] * g), 0, 255).astype(np.uint8)
    return out

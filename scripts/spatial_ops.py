"""Spatial realism controls (numpy + cv2): wrong direction and local-only motion.

Like scripts/temporal_ops.py, frames before `t0` (default T // 2) are the
parent's own and the op applies from `t0` on, inside the material (role label 2)
only; the support keeps the parent's frames. Targets
(docs/SNF_PP_METRIC_EXTENSION_DESIGN_2026_11_05.md §2-3):

* direction (B1/B2): `conveyor_along` / `conveyor_across` (channel_flow scenes):
  the material's own texture translated rigidly by CONVEYOR_PX per frame along /
  across the scene's dominant bank tangent (realism_geometry.bank_tangent_field).
  The texture is the material's bounding box in frame t0, non-material pixels
  inpainted from the material, mirrored into a tile that is periodic in both
  axes, so the slide never runs out of water texture. (A first build wrapped
  the whole frame, which swept sky and grass into the water; it was discarded
  before scoring.) Same speed, same texture, only the orientation differs, so a
  direction statistic must separate them and an activity statistic must not.
  `conveyor_down` / `conveyor_up` (falling_water, buoyant_plume, combustion):
  the same slide along image y.
* extent (C1): `local_patch_05/15/30`: only a compact patch holding 5, 15 or 30%
  of the material keeps the parent's motion; the rest of the material holds
  frame t0. The patch is the material inside the smallest disc around the
  material pixel deepest inside it that reaches that share.

These are graded interventions with known geometry, not ground truth for
"unrealistic".
"""
import cv2
import numpy as np

import realism_geometry as G

MIN_MATERIAL_PX = 1000  # scenes with less material get no spatial control
CONVEYOR_PX = 1.5      # px per frame at 832x480 (24 px/s at 16 fps)
PATCH = {"local_patch_05": 0.05, "local_patch_15": 0.15, "local_patch_30": 0.30}
SCOPE = {"conveyor_along": ("channel",), "conveyor_across": ("channel",),
         "conveyor_down": ("down", "up"), "conveyor_up": ("down", "up"),
         **{m: ("channel", "down", "up", "none") for m in PATCH}}
MODES = tuple(SCOPE)


def dominant_tangent(dyn):
    """Unit vector of the material's dominant bank tangent (sign arbitrary), and its coherence."""
    c2, s2, coh, _ = G.bank_tangent_field(dyn)
    w = coh * dyn
    mc, ms = float((w * c2).sum()), float((w * s2).sum())
    th = 0.5 * np.arctan2(ms, mc)
    return np.array([np.cos(th), np.sin(th)]), float(np.hypot(mc, ms) / max(w.sum(), 1e-9))


def direction(mode, dyn):
    if mode in ("conveyor_down", "conveyor_up"):
        return np.array([0.0, 1.0 if mode == "conveyor_down" else -1.0])
    t, _ = dominant_tangent(dyn)
    return t if mode == "conveyor_along" else np.array([-t[1], t[0]])


def patch(dyn, share):
    d = cv2.distanceTransform(dyn.astype(np.uint8), cv2.DIST_L2, 5)
    cy, cx = np.unravel_index(int(np.argmax(d)), d.shape)
    yy, xx = np.mgrid[:dyn.shape[0], :dyn.shape[1]]
    r = np.hypot(yy - cy, xx - cx)
    rmax = np.quantile(r[dyn], share)
    return dyn & (r <= rmax)


def texture_tile(frame, dyn):
    """(tile, x0, y0): a mirror-periodic tile of the material texture and the bounding-box origin."""
    ys, xs = np.nonzero(dyn)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = frame[y0:y1, x0:x1]
    hole = (~dyn[y0:y1, x0:x1]).astype(np.uint8)
    if hole.any():
        crop = cv2.inpaint(crop, hole, 5, cv2.INPAINT_TELEA)
    top = np.hstack([crop, crop[:, ::-1]])
    return np.vstack([top, top[::-1]]), x0, y0


def compose(mode, frames, dyn, t0=None):
    T, H, W = frames.shape[:3]
    t0 = T // 2 if t0 is None else t0
    out = frames.copy()
    if mode in PATCH:
        hold = dyn & ~patch(dyn, PATCH[mode])
        out[t0:] = np.where(hold[None, ..., None], frames[t0][None], frames[t0:])
        return out
    if mode not in SCOPE:
        raise ValueError(mode)
    v = direction(mode, dyn) * CONVEYOR_PX
    tile, x0, y0 = texture_tile(frames[t0], dyn)
    th, tw = tile.shape[:2]
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32) - x0, np.arange(H, dtype=np.float32) - y0)
    for t in range(t0, T):
        k = t - t0
        mx = np.mod(gx - v[0] * k, tw).astype(np.float32)
        my = np.mod(gy - v[1] * k, th).astype(np.float32)
        moved = cv2.remap(tile, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        out[t] = np.where(dyn[..., None], moved, frames[t])
    return out

#!/usr/bin/env python3
"""Geometry-referenced direction candidates (construct B).

Design: docs/SNF_PP_METRIC_EXTENSION_DESIGN_2026_11_05.md §2. The expected
direction comes from the scene, not from the caption.

* `cand-channel-alignment-0` (B1): axial agreement of the mean material flow
  with the bank-tangent field, A = sum w cos 2(theta_u - theta_t) / sum w in
  [-1, 1]: +1 along the channel, -1 across it, 0 isotropic. Sign-free by design,
  so time reversal leaves it unchanged. The bank-tangent field is the doubled-
  angle tangent of the material contour (frame edges excluded), spread into the
  material by normalized convolution, a cheap stand-in for the harmonic
  (Laplace) interpolation of the design. `coherence` reports how well the banks
  agree locally (near 0 where banks cross, e.g. pools).
* `cand-gravity-sign-0` (B2): G = sum w u_y/|u| / sum w with image y down:
  about +1 for falling water; U = -G for plumes and flames.
* `cand-sign-stability-0` (B5): |sum_t,x w u_t.t| / sum_t,x w |u_t.t|, about 1
  when the along-channel sign holds over time, low under reversals.

Weights: w = |u_mean| * R * [|u_mean| > tau], R = |sum_t u_t| / sum_t |u_t|.
Flow estimation is the caller's (RAFT, similarity-compensated, per the spec);
these functions take flow fields so they can be tested on known answers.

Version 1 (`-1` identities, `cand-gravity-stability-0`), after the v0 run on
2026-11-05 (manifest/realism_dev_2026_11_05/geometry_scenetether.json) scored
frozen tails instead of abstaining: tau there is relative to the support's own
speed, so on a still video the top 5% of codec/RAFT noise on the material
passes it, and identical frames give identical noise flow (R = 1).
* `activity_gate`: per-pixel activity = median over pairs of |u_t| (motion
  exists, whatever its direction, so ping-pong is not mistaken for a freeze).
  tau1 = max(TAU_ABS, Q95 of support activity). The material must exceed it on
  at least MIN_ACTIVE of its pixels, three times the support's own 5%, else
  every v1 statistic abstains ("material not more active than the support").
* `cand-gravity-stability-0`: |sum_t,x w u_y,t| / sum_t,x w |u_y,t|, about 1 when
  the vertical sign holds over the window and low under ping-pong; G alone
  cannot see ping-pong, because the window holds an unequal share of each
  phase and G normalizes the mean flow to unit length.
"""
import cv2
import numpy as np

IDENTITY = {"channel_alignment": "cand-channel-alignment-0", "gravity_sign": "cand-gravity-sign-0",
            "sign_stability": "cand-sign-stability-0",
            "channel_alignment_1": "cand-channel-alignment-1", "gravity_sign_1": "cand-gravity-sign-1",
            "sign_stability_1": "cand-sign-stability-1", "gravity_stability": "cand-gravity-stability-0"}
BORDER = 4            # px: contour within this of the frame edge is not a bank
SPREAD_SIGMA = 40.0   # px: normalized-convolution scale for the tangent field
MIN_BANK_PX = 200
MIN_COHERENCE = 0.5
NEAR_FRAC = 0.25      # near-bank band: distance <= this fraction of the local half-width
TAU_ABS = 0.1         # px per pair at flow resolution: below this nothing counts as motion
MIN_ACTIVE = 0.15     # active share of the material required by the v1 gate


def bank_tangent_field(material, border=BORDER, sigma=SPREAD_SIGMA):
    """(cos 2theta, sin 2theta, coherence, bank_px) of the bank tangent at every pixel."""
    m = material.astype(np.uint8)
    grad = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    h, w = m.shape
    grad[:border], grad[-border:], grad[:, :border], grad[:, -border:] = False, False, False, False
    sm = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2.0)
    gy, gx = np.gradient(sm)
    # normal angle phi; tangent = phi + 90 deg; in doubled angles that is a sign flip
    phi = np.arctan2(gy, gx)
    c2, s2 = -np.cos(2 * phi), -np.sin(2 * phi)
    wgt = grad.astype(np.float32)
    bc = cv2.GaussianBlur(c2 * wgt, (0, 0), sigma)
    bs = cv2.GaussianBlur(s2 * wgt, (0, 0), sigma)
    bw = cv2.GaussianBlur(wgt, (0, 0), sigma)
    with np.errstate(invalid="ignore", divide="ignore"):
        mc, ms = bc / bw, bs / bw
    coh = np.sqrt(mc ** 2 + ms ** 2)
    norm = np.where(coh > 0, coh, 1)
    return np.nan_to_num(mc / norm), np.nan_to_num(ms / norm), np.nan_to_num(coh), int(grad.sum())


def weights(flows, tau):
    """flows (T, H, W, 2) -> mean flow (H, W, 2), steadiness R, weights w."""
    mean = flows.mean(axis=0)
    mag = np.linalg.norm(mean, axis=-1)
    R = np.linalg.norm(flows.sum(axis=0), axis=-1) / np.maximum(np.linalg.norm(flows, axis=-1).sum(axis=0), 1e-9)
    return mean, R, mag * R * (mag > tau)


def channel_alignment(flows, material, tau):
    mean, R, w = weights(flows, tau)
    c2, s2, coh, bank = bank_tangent_field(material)
    ok = material & (coh >= MIN_COHERENCE)
    if bank < MIN_BANK_PX:
        return dict(identity=IDENTITY["channel_alignment"], abstain=f"bank {bank} px < {MIN_BANK_PX}")
    ww = w * ok
    if ww.sum() <= 0:
        return dict(identity=IDENTITY["channel_alignment"], abstain="no steady material flow above tau on coherent banks")
    th = np.arctan2(mean[..., 1], mean[..., 0])
    # cos 2(theta_u - theta_t) = cos2u cos2t + sin2u sin2t
    agree = np.cos(2 * th) * c2 + np.sin(2 * th) * s2
    d_in = cv2.distanceTransform(material.astype(np.uint8), cv2.DIST_L2, 5)
    near = ok & (d_in <= NEAR_FRAC * max(float(d_in.max()), 1.0))
    out = dict(identity=IDENTITY["channel_alignment"], A=float((ww * agree).sum() / ww.sum()),
               weight=float(ww.sum()), bank_px=bank, coherent_frac=float(ok.sum() / max(material.sum(), 1)))
    wn = ww * near
    out["A_near"] = float((wn * agree).sum() / wn.sum()) if wn.sum() > 0 else None
    # sign stability along the local tangent: pick the tangent sign by the mean flow (sign is not identifiable)
    tang = np.stack([np.cos(np.arctan2(s2, c2) / 2), np.sin(np.arctan2(s2, c2) / 2)], -1)
    along = (flows * tang).sum(-1)                                      # (T, H, W)
    sgn = np.sign((mean * tang).sum(-1))
    num = abs(float((along * sgn * ww).sum()))
    den = float((np.abs(along) * ww).sum())
    out["sign_stability"] = num / den if den > 0 else None
    return out


def gravity_sign(flows, material, tau):
    mean, R, w = weights(flows, tau)
    ww = w * material
    if ww.sum() <= 0:
        return dict(identity=IDENTITY["gravity_sign"], abstain="no steady material flow above tau")
    uy = mean[..., 1] / np.maximum(np.linalg.norm(mean, axis=-1), 1e-9)
    return dict(identity=IDENTITY["gravity_sign"], G=float((ww * uy).sum() / ww.sum()), weight=float(ww.sum()))


def activity_gate(flows, material, support, tau_abs=TAU_ABS, min_active=MIN_ACTIVE):
    """(tau1, report, abstain reason or None) of the v1 gate."""
    act = np.median(np.linalg.norm(flows, axis=-1), axis=0)
    sup = act[support] if support.any() else np.zeros(1)
    tau1 = max(tau_abs, float(np.percentile(sup, 95)))
    frac = float((act[material] > tau1).mean()) if material.any() else 0.0
    rep = dict(tau1=tau1, active_frac=frac, support_active_frac=float((sup > tau1).mean()),
               material_activity_median=float(np.median(act[material])) if material.any() else 0.0)
    why = None if frac >= min_active else f"material active share {frac:.3f} < {min_active} (not more active than the support)"
    return tau1, rep, why


def gravity_stability(flows, ww):
    num = abs(float((flows[..., 1] * ww).sum()))
    den = float((np.abs(flows[..., 1]) * ww).sum())
    return num / den if den > 0 else None


def geometry_v1(route, flows, material, support):
    """All v1 statistics for one routed video: gate first, then A/sign stability or G/gravity stability."""
    tau1, rep, why = activity_gate(flows, material, support)
    if why is not None:
        return dict(gate=rep, abstain=why)
    if route == "channel":
        r = channel_alignment(flows, material, tau1)
        out = {k: v for k, v in r.items() if k != "identity"}
        out["identity"] = [IDENTITY["channel_alignment_1"], IDENTITY["sign_stability_1"]]
    else:
        r = gravity_sign(flows, material, tau1)
        out = {k: v for k, v in r.items() if k != "identity"}
        out["identity"] = [IDENTITY["gravity_sign_1"], IDENTITY["gravity_stability"]]
        if "abstain" not in r:
            mean, R, w = weights(flows, tau1)
            out["gravity_stability"] = gravity_stability(flows, w * material)
    out["gate"] = rep
    return out

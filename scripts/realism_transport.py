#!/usr/bin/env python3
"""`cand-material-transport-persistence-0`: SceneTether's DAMP on SNF role maps.

Ported from ar-image-animation tools/arm_motion.py (`damp`, docs/12_MOTION_DECOMPOSITION.md
§6.1): per pixel |sum_t u_t| / (sum_t |u_t| + 1e-6) on similarity-compensated
flow, averaged over a mask. The headline is the paired contrast within one video,
delta = DAMP(material) - DAMP(support): a rigidly translating frame scores about
1 everywhere, so absolute DAMP is not flow quality. Changes from the source:
the masks are SNF role maps (eroded material and support), the window is the
SNF late window of the cached flows, and a gated twin `damp_material_active`
averages only material pixels above the v1 activity threshold, so a mostly
frozen material is not scored by its noise. No sign: pair it with the
direction candidates (scripts/realism_geometry.py).
"""
import numpy as np

from realism_geometry import TAU_ABS

IDENTITY = "cand-material-transport-persistence-0"
EPS = 1e-6


def damp_map(flows):
    return np.linalg.norm(flows.sum(0), axis=-1) / (np.linalg.norm(flows, axis=-1).sum(0) + EPS)


def transport(flows, material, support, tau_abs=TAU_ABS):
    p = damp_map(flows)
    act = np.median(np.linalg.norm(flows, axis=-1), axis=0)
    sup = act[support] if support.any() else np.zeros(1)
    tau = max(tau_abs, float(np.percentile(sup, 95)))
    active = material & (act > tau)
    out = dict(identity=IDENTITY, damp_material=float(p[material].mean()), damp_support=float(p[support].mean()),
               damp_material_active=float(p[active].mean()) if active.sum() >= 50 else None,
               active_px=int(active.sum()))
    out["delta"] = out["damp_material"] - out["damp_support"]
    return out

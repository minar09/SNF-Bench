#!/usr/bin/env python3
"""Extent candidates (construct C): how much of the material moves, not whether something does.

Design: docs/SNF_PP_METRIC_EXTENSION_DESIGN_2026_11_05.md §3. I2V only: the
material mask comes from the source image's role map, so it does not depend on
the video (T2V masks are Otsu on the video's own early flow, which would make
coverage circular).

`cand-coverage-0` (C1), on compensated flow over the late window:
* activity a(x) = median over pairs of |u_t(x)|; tau = max(TAU_ABS, Q95 of a on
  the support), the same threshold as the v1 geometry gate
  (scripts/realism_geometry.py), so "moving" means "moving more than the
  support's own codec/RAFT noise";
* C = share of material pixels with a > tau (recall of the role map; support
  motion stays with fBD);
* E10 = share of the material's total activity carried by its 10% most active
  pixels: 0.1 for uniform motion, near 1 when one patch moves;
* C(t) over N_SUB consecutive sub-windows, reported as C_min and C_end, so motion
  that stops inside the window is visible.
Abstains when the material is under MIN_MATERIAL of the frame.

`cand-coverage-1`: the same with `static=True`: pixels marked by
realism_geometry.static_bias (RAFT's fixed output on identical frames; computed
per sub-window for C_sub) never count as moving and carry no activity in E10.
Coverage-0 gave C up to 0.72 on frozen tails of ocean and lake scenes.
"""
import numpy as np

from realism_geometry import TAU_ABS, static_bias

IDENTITY = {"coverage": "cand-coverage-0", "coverage_1": "cand-coverage-1"}
MIN_MATERIAL = 0.02
N_SUB = 4


def _activity(flows):
    return np.median(np.linalg.norm(flows, axis=-1), axis=0)


def coverage(flows, material, support, tau_abs=TAU_ABS, static=False):
    ident = IDENTITY["coverage_1" if static else "coverage"]
    if material.mean() < MIN_MATERIAL:
        return dict(identity=ident, abstain=f"material {material.mean():.3f} of the frame < {MIN_MATERIAL}")
    act = _activity(flows)
    sup = act[support] if support.any() else np.zeros(1)
    tau = max(tau_abs, float(np.percentile(sup, 95)))

    def moving(f, a):
        return a > tau if not static else (a > tau) & ~static_bias(f)
    mov = moving(flows, act)
    a = np.where(mov, act, 0.0)[material] if static else act[material]
    top = np.sort(a)[::-1][:max(1, int(round(0.1 * a.size)))]
    subs = [float(moving(c, _activity(c))[material].mean()) for c in np.array_split(flows, N_SUB) if len(c)]
    return dict(identity=ident, tau=tau, C=float(mov[material].mean()),
                E10=float(top.sum() / a.sum()) if a.sum() > 0 else None,
                C_sub=subs, C_min=min(subs), C_end=subs[-1], material_frac=float(material.mean()))

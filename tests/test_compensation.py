"""Gate tests for METRIC_SPEC v1.1 similarity compensation.

These run on synthetic flow fields with a KNOWN injected transform, so they test
the estimator rather than the flow backbone. They are the tripwire the reviewer
asked for: if rotation or scale compensation is not monotone, the benchmark does
not run, because the validation suite would otherwise indict our own estimator
rather than the models it is meant to audit.

    ~/miniconda3/envs/snfeval/bin/python -m pytest -q tests/test_compensation.py
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))
from snf_metrics_v11 import estimate_similarity                # noqa: E402

H, W = 120, 200


def _grid():
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32),
                         np.arange(H, dtype=np.float32))
    return gx, gy


def synth_flow(tx=0.0, ty=0.0, rot_deg=0.0, scale=1.0, local=None):
    """Flow induced by a global similarity about the frame centre, plus optional
    local motion confined to the dynamic region."""
    gx, gy = _grid()
    cx, cy = W / 2.0, H / 2.0
    th = np.radians(rot_deg)
    ct, st = np.cos(th) * scale, np.sin(th) * scale
    xw = ct * (gx - cx) - st * (gy - cy) + cx + tx
    yw = st * (gx - cx) + ct * (gy - cy) + cy + ty
    f = np.stack([xw - gx, yw - gy], -1).astype(np.float32)
    if local is not None:
        f = f + local
    return f


def masks():
    """Static = left 60% of frame, dynamic = right 40%. Disjoint by construction."""
    static = np.zeros((H, W), bool)
    dyn = np.zeros((H, W), bool)
    static[:, : int(0.6 * W)] = True
    dyn[:, int(0.6 * W):] = True
    return static, dyn


def residual(f, d, region):
    r = np.sqrt((f[..., 0] - d[..., 0]) ** 2 + (f[..., 1] - d[..., 1]) ** 2)
    return float(r[region].mean())


def raw_mag(f, region):
    return float(np.sqrt(f[..., 0] ** 2 + f[..., 1] ** 2)[region].mean())


# --------------------------------------------------------------------------
# A / B / C: the estimator recovers what was injected
# --------------------------------------------------------------------------
@pytest.mark.parametrize("tx,ty", [(2.0, 0.0), (0.0, -3.0), (5.0, 4.0)])
def test_translation_recovered(tx, ty):
    static, _ = masks()
    f = synth_flow(tx=tx, ty=ty)
    d, mode, ratio, rot, sc = estimate_similarity(f, static, np.random.default_rng(0))
    assert mode == "similarity"
    assert residual(f, d, static) < 0.05 * max(1.0, raw_mag(f, static))
    assert abs(rot) < 0.05 and abs(sc - 1.0) < 0.005


@pytest.mark.parametrize("deg", [0.25, 0.5, 1.0, 2.0])
def test_rotation_recovered(deg):
    """The case v1.0 could not handle: median static flow is ~0 for a centred
    rotation, so translation-only compensation removes essentially nothing."""
    static, _ = masks()
    f = synth_flow(rot_deg=deg)
    d, mode, ratio, rot, sc = estimate_similarity(f, static, np.random.default_rng(0))
    assert mode == "similarity"
    assert abs(rot - deg) < 0.05, f"recovered {rot:.3f} vs injected {deg}"
    assert residual(f, d, static) < 0.05 * raw_mag(f, static)


@pytest.mark.parametrize("s", [1.005, 1.01, 1.02, 1.04])
def test_scale_recovered(s):
    static, _ = masks()
    f = synth_flow(scale=s)
    d, mode, ratio, rot, sc = estimate_similarity(f, static, np.random.default_rng(0))
    assert mode == "similarity"
    assert abs(sc - s) < 0.002, f"recovered {sc:.4f} vs injected {s}"
    assert residual(f, d, static) < 0.05 * raw_mag(f, static)


# --------------------------------------------------------------------------
# The regression that motivated v1.1
# --------------------------------------------------------------------------
def test_similarity_beats_translation_on_rotation():
    static, _ = masks()
    f = synth_flow(rot_deg=1.0)
    d_sim, _, _, _, _ = estimate_similarity(f, static, np.random.default_rng(0))
    med = np.zeros_like(f)
    med[..., 0] = np.median(f[..., 0][static])
    med[..., 1] = np.median(f[..., 1][static])
    r_sim, r_med = residual(f, d_sim, static), residual(f, med, static)
    assert r_sim < 0.25 * r_med, f"similarity {r_sim:.4f} vs translation {r_med:.4f}"


# --------------------------------------------------------------------------
# Monotonicity: the property the validation suite depends on
# --------------------------------------------------------------------------
@pytest.mark.parametrize("kind", ["translation", "rotation", "scale"])
def test_monotone_response_and_local_motion_preserved(kind):
    """Injected global motion must raise the raw dynamic-region magnitude
    monotonically, while compensation holds the *local* motion roughly constant.
    If compensation ate the local motion, MCFF would fall as drift rose and the
    benchmark would report freezing where there is drift."""
    static, dyn = masks()
    local = np.zeros((H, W, 2), np.float32)
    local[..., 0] = 1.5                      # constant local motion in the dyn region
    levels = {"translation": [0.0, 1.0, 2.0, 4.0, 8.0],
              "rotation": [0.0, 0.25, 0.5, 1.0, 2.0],
              "scale": [1.0, 1.005, 1.01, 1.02, 1.04]}[kind]

    raws, comps = [], []
    for lv in levels:
        kw = {"translation": dict(tx=lv), "rotation": dict(rot_deg=lv),
              "scale": dict(scale=lv)}[kind]
        f = synth_flow(local=local, **kw)
        d, _, _, _, _ = estimate_similarity(f, static, np.random.default_rng(0))
        raws.append(raw_mag(f, dyn))
        comps.append(residual(f, d, dyn))

    assert all(b >= a - 1e-6 for a, b in zip(raws, raws[1:])), \
        f"raw not monotone under {kind}: {raws}"
    base = comps[0]
    assert all(abs(c - base) < 0.15 * max(base, 1.0) for c in comps), \
        f"compensated local motion drifted under {kind}: {comps}"


def test_fallback_is_reported_not_silent():
    """Too few static correspondences must degrade loudly."""
    static = np.zeros((H, W), bool)
    static[0, :10] = True                    # 10 points, below MIN_CORRESP
    f = synth_flow(tx=3.0)
    _, mode, ratio, _, _ = estimate_similarity(f, static, np.random.default_rng(0))
    assert mode == "translation_fallback"

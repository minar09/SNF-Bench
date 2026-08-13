"""SNF task metrics, METRIC_SPEC v1.1 — with robust similarity compensation.

This supersedes the v1.0 estimator for every compensation-dependent quantity.
`metric_code/snf_task_metrics.py` is kept verbatim as the v1.0 provenance
record; nothing here edits it, and the RAFT/ORB machinery is imported from it
unchanged so the flow and feature backbones are provably identical between
versions.

What changes versus v1.0
------------------------
v1.0 estimated global motion as the per-component **median** of static-region
flow -- a pure translation. Under rotation or zoom the static-region flow field
is not constant and its median is near zero for a centred rotation, so the
estimator leaves precisely the corruptions the validation suite injects
uncompensated. v1.1 fits a robust **similarity** transform
`T_t(x) = s_t R_t x + b_t` to static-region correspondences under RANSAC,
forms the dense displacement field `d_t(x) = T_t(x) - x`, and subtracts it
pointwise.

Similarity rather than unrestricted affine: fixed-camera generation failures
plausibly look like translation, slight rotation and zoom, whereas affine shear
can absorb legitimate local deformation and over-correct.

What is unchanged
-----------------
fBD and NBF do not depend on compensation and are computed exactly as in v1.0,
so v1.0 and v1.1 values for those two are directly comparable.

New outputs
-----------
`MCFF_early` is now stored explicitly (v1.0 kept it only implicitly inside FP),
along with per-video `compensation_mode`, RANSAC `inlier_ratio`, and the
estimated rotation/scale, so the fallback rate is auditable rather than hidden.
"""

import os
import sys

import cv2
import numpy as np

SNF_EVAL = "/home/minar/region-forcing/snf_eval"
if SNF_EVAL not in sys.path:
    sys.path.insert(0, SNF_EVAL)
os.environ.setdefault("VBENCH_CACHE_DIR", "/home/minar/ckpt/vbench")

import snf_task_metrics as S                                   # noqa: E402

SPEC_VERSION = "1.1"
RANSAC_THRESH = 1.5        # px reprojection tolerance
MIN_CORRESP = 50           # below this, similarity is not identifiable
MAX_SAMPLE = 4000          # static pixels sampled per frame for the fit


def estimate_similarity(flow, static, rng):
    """Robust similarity fit to static-region correspondences.

    -> (d_field HxWx2, mode, inlier_ratio, rotation_deg, scale)

    Falls back to median translation when the fit is not identifiable, and says
    so: a silent fallback would make the estimator look better than it is and
    would hide exactly the frames where compensation is weakest.
    """
    H, W = static.shape
    ys, xs = np.nonzero(static)
    n = len(xs)
    if n < MIN_CORRESP:
        f, mode = _translation_field(flow, static, H, W)
        return f, mode, 0.0, 0.0, 1.0

    if n > MAX_SAMPLE:
        pick = rng.choice(n, size=MAX_SAMPLE, replace=False)
        ys, xs = ys[pick], xs[pick]

    src = np.stack([xs, ys], 1).astype(np.float32)
    dst = src + np.stack([flow[ys, xs, 0], flow[ys, xs, 1]], 1).astype(np.float32)

    M, inliers = cv2.estimateAffinePartial2D(
        src, dst, method=cv2.RANSAC, ransacReprojThreshold=RANSAC_THRESH,
        maxIters=2000, confidence=0.995)
    if M is None:
        f, mode = _translation_field(flow, static, H, W)
        return f, mode, 0.0, 0.0, 1.0

    ratio = float(inliers.mean()) if inliers is not None else 0.0
    # M = [[a, -b, tx], [b, a, ty]]  ->  scale = hypot(a, b), theta = atan2(b, a)
    a, b = float(M[0, 0]), float(M[1, 0])
    scale = float(np.hypot(a, b))
    rot = float(np.degrees(np.arctan2(b, a)))

    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32),
                         np.arange(H, dtype=np.float32))
    xw = M[0, 0] * gx + M[0, 1] * gy + M[0, 2]
    yw = M[1, 0] * gx + M[1, 1] * gy + M[1, 2]
    d = np.stack([xw - gx, yw - gy], -1)
    return d, "similarity", ratio, rot, scale


def _translation_field(flow, static, H, W):
    if static.sum() > 0:
        dvx = float(np.median(flow[..., 0][static]))
        dvy = float(np.median(flow[..., 1][static]))
    else:
        dvx = dvy = 0.0
    d = np.empty((H, W, 2), np.float32)
    d[..., 0] = dvx
    d[..., 1] = dvy
    return d, "translation_fallback"


def process_video(model, path, device, seed=0):
    """v1.1 replacement for S.process_video. Same masks, same backbones."""
    tens, grays = S.read_frames(path, device)
    if tens is None:
        return None
    F = len(tens)
    win = max(S.MIN_WIN, int(F * S.WIN_FRAC))
    rng = np.random.default_rng(seed)

    # ---- Pass A: early-window magnitude -> masks (identical to v1.0) ----
    early_maps = [S.flow_mag(model, tens[i], tens[i + 1]).astype(np.float32)
                  for i in range(min(win, F - 1))]
    early = np.mean(early_maps, 0)
    dyn, static = S.build_masks(early)
    Wpx = early.shape[1]

    # ---- Pass B: vector flow -> similarity-compensated scalars ----
    P = F - 1
    stat_mag = np.zeros(P, np.float64)
    dyn_raw = np.zeros(P, np.float64)
    dyn_res = np.zeros(P, np.float64)
    modes, ratios, rots, scales = [], [], [], []

    for i in range(P):
        f = S.flow_vec(model, tens[i], tens[i + 1])
        mag = np.sqrt(f[..., 0] ** 2 + f[..., 1] ** 2)
        if static.sum() > 0:
            stat_mag[i] = mag[static].mean()
        d, mode, ratio, rot, sc = estimate_similarity(f, static, rng)
        modes.append(mode)
        ratios.append(ratio)
        rots.append(rot)
        scales.append(sc)
        if dyn.sum() > 0:
            res = np.sqrt((f[..., 0] - d[..., 0]) ** 2 + (f[..., 1] - d[..., 1]) ** 2)
            dyn_raw[i] = mag[dyn].mean()
            dyn_res[i] = res[dyn].mean()

    ref = dyn_res[win:2 * win].mean() if P >= 2 * win else dyn_res[:win].mean()
    late = dyn_res[-win:].mean()
    fp = min(float(late / (ref + 1e-6)), 2.0)

    bfr = float(stat_mag.mean() / Wpx * 1000.0)
    dlr = float(stat_mag[-win:].mean() / (dyn_raw[-win:].mean() + 1e-6))
    raw_late = float(dyn_raw[-win:].mean())
    dar = float(1.0 - late / (raw_late + 1e-6))

    late_idx = list(range(F - win, F))
    fbd = S.orb_drift(grays, static, late_idx)

    n_sim = sum(1 for m in modes if m == "similarity")
    return {
        "video": os.path.basename(path),
        "fBD": fbd,
        "BFR": bfr,                       # stored under the v1.0 key; NBF at table time
        "FP": fp,
        "MCFF_early": float(ref),
        "MCFF_late": float(late),
        "DD_raw_late": raw_late,
        "drift_frac_late": dlr,           # v1.0 key; surfaced as DLR
        "DAR_signed": dar,
        "static_frac": float(static.mean()),
        "n_frames_sampled": F,
        # --- compensation provenance (METRIC_SPEC v1.1 sec.3) ---
        "compensation_mode": "similarity" if n_sim == P else "mixed",
        "similarity_frac": float(n_sim / max(1, P)),
        "inlier_ratio_mean": float(np.mean(ratios)) if ratios else 0.0,
        "rotation_deg_mean": float(np.mean(rots)) if rots else 0.0,
        "scale_mean": float(np.mean(scales)) if scales else 1.0,
        "metric_spec_version": SPEC_VERSION,
    }

#!/usr/bin/env python
"""Repetition DIAGNOSTIC for 60 s fixed-camera videos (docs/120 stream C, §1.5). CPU only. New module; nothing here
changes the locked method or any existing scorer.

It answers the WACV criticism that a seamless 2 s loop repeated for 60 s scores perfectly on persistence metrics and has
no transient seam. It is a diagnostic: it REPORTS recurrence scores per video and never states realism. Genuine
periodic motion (waves, foliage sway, fire flicker) is a hard negative for the replay scores and gets its own label,
"periodic, not replay": phase-consistent flow at the best lag but texture residual above the codec floor.

Inputs (spec C0):
  frames   ALL frames at native fps (no temporal resampling: resampling blurs exact replays), BGR -> grey float32,
           INTER_AREA to 208x120 (the flash_events thumbnail size).
  region   results/factorial/source_masks/<sid>/labels.png label 2 (dynamic), INTER_NEAREST to the thumbnail (the
           sourcefixed_flow rule). If label 2 < 1 % of the frame (overlay-medium scenes): label 2 U 3, region =
           "dyn+overlay"; if still < 1 %: abstain. Dev / other-generator scenes use source_masks_dev/.
  windows  W = round(fps) frames (1 s), stride S = W // 2  (961 fr @ 16 fps -> 119 windows). Reported on the full video
           and on the late half (start >= 30 s).

Descriptors per window a (start s_a):
  PIX   d_a[t, p] = I[t, p] - mean_t I[t, p]   (t in [0, W), p in region). The per-pixel temporal mean removal deletes
        the stationary texture and any luminance / colour drift, leaving the motion signature: two windows with the same
        scene texture but different motion are far apart, a replay is identical. Scale sigma_a = mean_p std_t I.
  FLOW  Farneback (0.5, 3, 15, 3, 5, 1.2) t -> t+1 on the grey thumbnails, region-masked, f_a[t, p, :] (W-1 fields).
        Scale mu_a = mean |f_a|.
  DINO  (--features dino, OFF by default, exploratory column only, NOT used in the replay scores: semantic features
        assign the same embedding to the same wave / flame state, i.e. they measure state recurrence, not replay).

Similarities (a vs an earlier candidate window b at every integer start frame, lag s_a - s_b >= L_min):
  nres(a, b)   = mean |d_a - d_b| / (0.5 (sigma_a + sigma_b))     ~1.1 for independent motion with equal statistics,
                 ~floor / sigma for a replay, ~alpha * 1.1 for a cross-faded window.
  q(a, b)      = fraction of region voxels with |d_a - d_b| < FLOOR_MULT * floor   (floor = codec noise at the thumbnail
                 scale, calibrated from identity re-encodes by `validate`, provisional 1.0 grey level).
  cos(a, b)    = sum f_a . f_b / (|f_a| |f_b|)  over region voxels;  nres_f = mean |f_a - f_b| / (0.5 (mu_a + mu_b)).
  Search: coarse pass on <= 2048 fixed random region pixels (seed 0) by Gram matrix, top-5 lags per window separated by
  >= 4 frames, refined on the full region; b* = argmin nres over the top-5 and R_ex, q_ex, cos_ex are b*'s. LAG (v1.1):
  when b* passes the exact criterion (q >= Q_MIN, R <= R_MAX), the reported lag is the SMALLEST lag, over every
  candidate start whose coarse distance is <= LAG_D2_MULT x the coarse distance that the criterion's residual would
  give (local minima >= 4 frames apart, up to MAX_LAG_REFINE refinements in ascending lag order), at which the
  full-region descriptor also passes the criterion; R_lag / q_lag are the values at that lag. Otherwise the lag is
  b*'s. For an exact loop of period P this is the smallest multiple of P that is >= L_min = 2 W (P itself when P >= 2 s
  at 16 fps): "P or a multiple of P", never the fundamental when P < 2 W. v1.0 chose the smallest lag within an
  absolute near-tie (0.02) of the best over the top-5 coarse candidates only, so 7 of the 12 P = 2 s validation loops
  reported 4-14 s (and x264 reproduces bit-identical frames, residual 0, at some multiples but not at P, which beat any
  absolute tie margin); detection was unaffected.
  EXACT      L_min = 2 W.                      R_ex(a), q_ex(a), lag_ex(a), cos_ex(a).
  PING-PONG  candidates time-reversed, L_min = W (flow reversed in order and negated).  R_pp, q_pp, lag_pp.
  FREEZE     F(a) = mean region |I[t+1] - I[t]| in the window; frozen iff F < max(FLOOR_MULT * floor_freeze, FREEZE_MIN)
             where floor_freeze is the held-segment codec residual (amendment, see FREEZE_MIN); the spec variant
             F < FLOOR_MULT * floor is reported as freeze_frac_spec. Frozen windows are excluded from EXACT / PING-PONG
             (d ~ 0 would match everything).
  flags  exact(a)    iff q_ex >= 0.90 and R_ex <= 0.25
         pp(a)       iff q_pp >= 0.90 and R_pp <= 0.25 and R_pp < R_ex
         periodic(a) iff cos_ex >= 0.5 and not exact(a)             ("periodic, not replay")

Video-level (full and late half): exact_frac, pp_frac, freeze_frac, periodic_frac (denominator: non-frozen windows for
exact / pp / periodic, all windows for freeze); exact_run_max_s; lag_dominant_s (mode of the exact-window lags);
lag_period_s (smallest value >= LAG_MIN_PERIOD frames among the exact lags and their pairwise differences of which
>= 80 % of the exact lags are within LAG_TOL frame of a multiple; else the mode) with lag_consistency (that fraction,
relative to lag_period_s) and lag_min_s; continuous backups R_ex_p10, R_pp_p10, F_p10; diagnostics floor_est_in_video
(5th pct of F, reported only), sigma_median, region, n_windows, fps, n_frames, sha256 of video, labels and module.

WHAT "EXACT" MEANS (disclosure, v1.1). exact(a) states that the per-pixel 1 s window-mean-removed signature of the
dynamic region recurs, at some earlier lag >= 2 s, within FLOOR_MULT x the cross-encode codec floor (3 x 1.89 = 5.7 grey
levels at the thumbnail scale) on >= 90 % of the region voxels, with the mean residual <= 0.25 of the window's own
temporal std. The window-mean removal discards texture evolution slower than ~1 s. A deterministic oscillation of a
FIXED texture (a rigid warp of one still with slow haze, synth_osc_rigid in the validation set) therefore satisfies the
definition and IS reported as exact on high-contrast bases: it is a replay of the sub-second motion signature, though
no frame is a copy of an earlier frame. The genuinely periodic natural material (waves, foliage, fire, plumes: 6 valset
originals, 84 periodic-category test videos across 4 cells, 14 SVI / Helios videos) is never flagged (exact_frac 0,
R_ex_p10 >= 0.86) because its texture evolves at the sub-second scale well above the floor. The synthetic negatives
measure that margin: the evolving-texture variants (synth_osc_evolving*) show how much sub-second texture change per
window is needed to leave the exact definition. Other disclosed limits: FREEZE_MIN = 0.25 grey / frame at the
thumbnail scale labels genuinely sub-pixel motion as frozen (a synthetic 0.75 px warp of the low-contrast ial04 base
scores F_p10 0.235, freeze_frac 0.67; the smallest real-negative F_p10 is 0.60, Helios goyang-si-flood, a 2.4 x
margin); and ifw05 (falling water, a slow near-static static-sink video with sigma_median ~3) is partly missed by every
loop transform (see the report's per-scene table). None of this promises physical realism; the scores are reported as
they are. Provisional reading thresholds (declared, reported with sensitivity,
not promoted to a verdict): replay-suspect if exact_frac >= 0.25, ping-pong-suspect if pp_frac >= 0.25, freeze-suspect
if freeze_frac >= 0.25.

CLI (PY=/home/minar/miniconda3/envs/snfeval/bin/python, CUDA_VISIBLE_DEVICES=):
  $PY tools/factorial_scoring/repetition.py score <video.mp4> --mask <labels.png> [--out x.json] [--features dino]
  $PY tools/factorial_scoring/repetition.py validate [--jobs 12]      # builds the validation set (21 transforms x 12
                                                                       # scenes, incl. adversarial loops and synthetic
                                                                       # periodic negatives), calibrates the floor,
                                                                       # scores it, writes the AUROC report
  $PY tools/factorial_scoring/repetition.py batch --cells hfm spatial3 echo1 sliding1 [--jobs 12]
Outputs: results/factorial/tables/repetition_oct15/{valset/, calibration.json, validation_report.{json,md},
         scores_<cell>.json, per_video/<cell>/<sid>.json}
"""
import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(f"{HERE}/../..")
OUT_ROOT = f"{REPO}/results/factorial/tables/repetition_oct15"
MASK_ROOT = f"{REPO}/results/factorial/source_masks"
MASK_ROOT_DEV = f"{REPO}/results/factorial/source_masks_dev"
SCORE_INPUTS = f"{REPO}/results/factorial/scores/cfpp/{{cell}}/seed42/inputs/60s"
# the helios conda ffmpeg has no libx264 (only libopenh264); the imageio-ffmpeg v7.0.2 binary in the same env has it
FFMPEG_CANDIDATES = ["/home/minar/miniconda3/envs/helios/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2",
                     "/home/minar/miniconda3/envs/helios/bin/ffmpeg"]
FFMPEG = next((f for f in FFMPEG_CANDIDATES if os.path.exists(f)), "ffmpeg")

CELLS = {  # short name -> cell directory (seed 42 test split, 48 scenes)
    "hfm": "echo_nfpb1_h1_frozen_noband_lr",
    "spatial3": "echo_spatial_nfpb3_default_lr",
    "echo1": "echo_nfpb1_default_lr",
    "sliding1": "sliding_nfpb1_default_lr",
    "sink3": "static_sink_nfpb3_default_lr",
}
# other-generator material (dev scenes, dev masks)
NATIVE = {
    "svi_pro_native60": f"{REPO}/results/i2v_all_v2/svi_pro_native60/{{sid}}.mp4",
    "helios_distilled60": f"{REPO}/results/i2v_all_v2/helios_distilled60/{{sid}}/video.mp4",
}
DEV_SCENES = ["goyang-si-flood", "pexels-fire", "pexels-flood", "pexels-rain", "seoul-flood", "sinchon_gyu", "sk-rain-flood"]
CATEGORY = {"ial": "accumulating_level", "ibp": "buoyant_plume", "icb": "combustion", "icf": "channel_flow",
            "ifp": "falling_precip", "ifw": "falling_water", "igt": "geothermal", "iow": "oscillatory_water",
            "iwb": "windborne"}
# the hard-negative categories: genuinely periodic / quasi-periodic natural motion
PERIODIC_CATEGORIES = {"oscillatory_water", "combustion", "windborne", "buoyant_plume"}

# validation set (spec C0 §4): 12 scenes, 9 categories, 4 cells, seed 42
VAL_SCENES = [("ial04", "hfm"), ("icb01", "hfm"), ("icf03", "hfm"), ("iow01", "hfm"),
              ("ibp03", "spatial3"), ("ifp02", "spatial3"), ("iow02", "spatial3"),
              ("icf04", "echo1"), ("igt03", "echo1"),
              ("icb03", "sink3"), ("ifw05", "sink3"), ("iwb04", "sink3")]
VAL_T0_S = 20.0  # base segment start (past the early transients)
VAL_ONSET_S = 30.0  # late-onset loop / freeze onset

THUMB_W, THUMB_H = 208, 120
FLOOR_PROVISIONAL = 1.0  # grey levels at the thumbnail scale
FLOOR_MULT = 3.0
# FREEZE amendment (validation C1, 2026-10-15): the spec's single floor is the cross-encode residual (1.89 grey levels
# after calibration, threshold 5.67), which exceeds the frame-to-frame change of slow real scenes (ial04 original:
# F median 1.4), so it flags whole slow videos as frozen. The residual between consecutive decoded frames of a HELD
# segment inside one encode is ~0.002 (x264 skips identical frames). Frozen therefore uses its own floor,
# floor_freeze (calibrated from the held segments of the validation freeze clips), with a minimum of FREEZE_MIN grey
# levels per frame; the spec variant (F < FLOOR_MULT * floor) is still reported as freeze_frac_spec.
FREEZE_MIN = 0.25
FLOOR_FREEZE_PROVISIONAL = 0.01
Q_MIN, R_MAX, COS_MIN = 0.90, 0.25, 0.5
SUSPECT_FRAC = 0.25
N_SUB, TOPK, SEP = 2048, 5, 4
LAG_D2_MULT = 4.0  # v1.1 smallest-lag search: coarse prefilter D2 <= LAG_D2_MULT * nsub * W * (R_MAX * sigma_a)^2
MAX_LAG_REFINE = 64  # v1.1: bound on full-region refinements per window in the smallest-lag search
LAG_TOL, LAG_MIN_PERIOD, LAG_CONS_MIN = 1, 6, 0.8  # v1.1: lag_period_s estimator (frames, frames, fraction)
REGION_MIN_FRAC = 0.01
FARNEBACK = dict(pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0)
VERSION = "repetition-v1.1-oct15"


# ---------------------------------------------------------------------------------------------------------- utilities
def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def module_sha():
    return sha256_file(os.path.abspath(__file__))


def _limit_threads(n=2):
    for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ.setdefault(k, str(n))
    try:
        import cv2
        cv2.setNumThreads(n)
    except Exception:
        pass


def read_video_gray(path, size=(THUMB_W, THUMB_H)):
    """All frames at native fps -> (T, H, W) float32 grey thumbnails (INTER_AREA), fps, (orig_h, orig_w)."""
    import cv2
    cap = cv2.VideoCapture(path)
    fps = float(cap.get(cv2.CAP_PROP_FPS)) or 16.0
    frames, shape = [], None
    while True:
        ok, f = cap.read()
        if not ok:
            break
        shape = f.shape[:2]
        s = cv2.resize(f, size, interpolation=cv2.INTER_AREA)
        frames.append(cv2.cvtColor(s, cv2.COLOR_BGR2GRAY))
    cap.release()
    if not frames:
        raise RuntimeError(f"no frames decoded from {path}")
    return np.stack(frames).astype(np.float32), fps, shape


def load_region(labels_path, shape=(THUMB_H, THUMB_W)):
    """(region bool (H, W), region name, abstain_reason or None). label 2; fallback 2 U 3; abstain if < 1 %."""
    import cv2
    lab = cv2.imread(labels_path, 0)
    if lab is None:
        return None, "none", f"labels not readable: {labels_path}"
    if lab.shape != tuple(shape):
        lab = cv2.resize(lab, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)
    dyn = lab == 2
    if dyn.mean() >= REGION_MIN_FRAC:
        return dyn, "dyn", None
    both = dyn | (lab == 3)
    if both.mean() >= REGION_MIN_FRAC:
        return both, "dyn+overlay", None
    return None, "none", f"label 2 U 3 covers {both.mean() * 100:.2f} % < {REGION_MIN_FRAC * 100:.0f} % of the frame"


def farneback_flows(gray_u8):
    """(T-1, H, W, 2) float32 forward flows t -> t+1 on uint8 grey frames."""
    import cv2
    T = gray_u8.shape[0]
    out = np.empty((T - 1,) + gray_u8.shape[1:] + (2,), np.float32)
    for t in range(T - 1):
        out[t] = cv2.calcOpticalFlowFarneback(gray_u8[t], gray_u8[t + 1], None, **FARNEBACK)
    return out


def _topk_separated(order, cand_starts, k=TOPK, sep=SEP):
    """Greedy top-k candidate indices (in `order`, best first) whose start frames differ by >= sep."""
    chosen = []
    for i in order:
        s = cand_starts[i]
        if all(abs(s - cand_starts[j]) >= sep for j in chosen):
            chosen.append(i)
            if len(chosen) >= k:
                break
    return chosen


# ------------------------------------------------------------------------------------------------------------ core
def score_frames(gray, region, fps, floor=FLOOR_PROVISIONAL, flows=None, compute_flow=True,
                 floor_freeze=FLOOR_FREEZE_PROVISIONAL):
    """Core diagnostic on (T, H, W) float32 grey frames and a (H, W) bool region.

    Returns dict(windows=list of per-window records, full=video-level, late=video-level on windows starting >= T/2,
    W, S, fps, ...). `flows` (T-1, H, W, 2) may be given (tests); else Farneback is computed when compute_flow."""
    T = gray.shape[0]
    W = int(round(fps))
    S = max(1, W // 2)
    if T < 3 * W:
        raise ValueError(f"video too short: {T} frames < 3 W = {3 * W}")
    thr = FLOOR_MULT * floor
    thr_freeze = max(FLOOR_MULT * floor_freeze, FREEZE_MIN)
    P_idx = np.flatnonzero(region.ravel())
    X = gray.reshape(T, -1)[:, P_idx]  # (T, P)
    P = X.shape[1]
    nS = T - W + 1  # candidate starts 0 .. T-W
    starts = np.arange(0, nS, S)

    # freeze statistic for every integer start: mean region |I[t+1] - I[t]| in the window
    fd = np.abs(np.diff(X, axis=0)).mean(1).astype(np.float64)  # (T-1,)
    cfd = np.concatenate([[0.0], np.cumsum(fd)])
    F_all = (cfd[np.arange(nS) + W - 1] - cfd[np.arange(nS)]) / (W - 1)
    # sigma for every integer start: mean_p std_t I (per-pixel within-window temporal std)
    X64 = X.astype(np.float64)
    c1 = np.concatenate([np.zeros((1, P)), np.cumsum(X64, 0)])
    c2 = np.concatenate([np.zeros((1, P)), np.cumsum(X64 * X64, 0)])
    idx = np.arange(nS)
    m = (c1[idx + W] - c1[idx]) / W
    v = (c2[idx + W] - c2[idx]) / W - m * m
    sigma_all = np.sqrt(np.clip(v, 0, None)).mean(1)  # (nS,)
    del c1, c2, X64

    # flows restricted to the region
    if flows is None and compute_flow:
        flows = farneback_flows(np.clip(np.rint(gray), 0, 255).astype(np.uint8))
    FL = flows.reshape(T - 1, -1, 2)[:, P_idx, :] if flows is not None else None  # (T-1, P, 2)

    # coarse pass: fixed random subset of region pixels, all integer starts, Gram-matrix squared distances
    rng = np.random.RandomState(0)
    sub = np.sort(rng.choice(P, min(N_SUB, P), replace=False))
    Xs = X[:, sub]
    Bw = np.lib.stride_tricks.sliding_window_view(Xs, W, axis=0)  # (nS, nsub, W)
    Bw = np.ascontiguousarray(np.transpose(Bw, (0, 2, 1)))  # (nS, W, nsub)
    Bw -= Bw.mean(1, keepdims=True)
    B = Bw.reshape(nS, -1)
    Brev = np.ascontiguousarray(Bw[:, ::-1, :]).reshape(nS, -1)
    A = B[starts]
    na2 = (A * A).sum(1)
    nb2 = (B * B).sum(1)
    D2 = na2[:, None] + nb2[None, :] - 2.0 * (A @ B.T)
    D2r = na2[:, None] + nb2[None, :] - 2.0 * (A @ Brev.T)
    del Bw, B, Brev, A

    def dwin(s):
        d = X[s:s + W]
        return d - d.mean(0, keepdims=True)

    def refine(s_a, s_b, reverse):
        da, db = dwin(s_a), dwin(s_b)
        if reverse:
            db = db[::-1]
        diff = np.abs(da - db)
        nres = float(diff.mean() / max(0.5 * (sigma_all[s_a] + sigma_all[s_b]), 1e-6))
        q = float((diff < thr).mean())
        cos = nres_f = float("nan")
        if FL is not None:
            fa = FL[s_a:s_a + W - 1]
            fb = FL[s_b:s_b + W - 1]
            if reverse:
                fb = -fb[::-1]
            na, nb = np.linalg.norm(fa.ravel()), np.linalg.norm(fb.ravel())
            cos = float((fa * fb).sum() / max(na * nb, 1e-9))
            mu = 0.5 * (np.linalg.norm(fa, axis=-1).mean() + np.linalg.norm(fb, axis=-1).mean())
            nres_f = float(np.linalg.norm(fa - fb, axis=-1).mean() / max(mu, 1e-6))
        return nres, q, cos, nres_f

    windows = []
    for ia, s_a in enumerate(starts):
        rec = dict(start=int(s_a), t_s=round(float(s_a / fps), 3), F=float(F_all[s_a]), sigma=float(sigma_all[s_a]),
                   frozen=bool(F_all[s_a] < thr_freeze), frozen_spec=bool(F_all[s_a] < thr))
        for key, Dm, Lmin, reverse in (("ex", D2, 2 * W, False), ("pp", D2r, W, True)):
            lim = s_a - Lmin  # candidates s_b <= lim
            best = dict(R=float("nan"), q=float("nan"), lag=float("nan"), cos=float("nan"), nres_f=float("nan"),
                        lag_argmin_frames=None, R_lag=float("nan"), q_lag=float("nan"), n_refined=0)
            if lim >= 0 and not rec["frozen"]:
                cand = np.arange(0, lim + 1)
                cand = cand[~(F_all[cand] < thr_freeze)]  # frozen candidates carry no motion signature
                if len(cand):
                    order = cand[np.argsort(Dm[ia, cand], kind="stable")]
                    top = _topk_separated(order, np.arange(nS))
                    res = {int(s_b): refine(s_a, int(s_b), reverse) for s_b in top}
                    r_best = min(r[0] for r in res.values())
                    s_best = max(s for s, r in res.items() if r[0] == r_best)  # b* = argmin nres (smallest lag on ties)
                    nres, q, cos, nres_f = res[s_best]
                    s_lag = s_best
                    passes = lambda r: r[1] >= Q_MIN and r[0] <= R_MAX  # the exact / pp criterion at candidate level
                    if passes(res[s_best]):
                        # Reported lag (v1.1): the SMALLEST lag at which the criterion also passes, over every candidate
                        # whose coarse distance is below what a criterion-level residual would give (local minima >= SEP
                        # apart, ascending lag, at most MAX_LAG_REFINE refinements). v1.0 looked at the top-k only and
                        # used an absolute near-tie, which made the lag an arbitrary multiple of the period.
                        d2_crit = LAG_D2_MULT * len(sub) * W * (R_MAX * float(sigma_all[s_a])) ** 2
                        near = cand[(Dm[ia, cand] <= d2_crit) & (cand > s_best)]  # only smaller lags can improve
                        if len(near):
                            order_n = near[np.argsort(Dm[ia, near], kind="stable")]
                            pool = sorted(_topk_separated(order_n, np.arange(nS), k=len(near)), reverse=True)
                            for s_c in pool[:MAX_LAG_REFINE]:  # ascending lag
                                s_c = int(s_c)
                                r = res.get(s_c)
                                if r is None:
                                    r = res[s_c] = refine(s_a, s_c, reverse)
                                if passes(r):
                                    s_lag = s_c
                                    break
                    best = dict(R=nres, q=q, lag=float((s_a - s_lag) / fps), lag_frames=int(s_a - s_lag), cos=cos,
                                nres_f=nres_f, lag_argmin_frames=int(s_a - s_best), R_lag=float(res[s_lag][0]),
                                q_lag=float(res[s_lag][1]), n_refined=len(res))
            for k2, v2 in best.items():
                rec[f"{k2}_{key}"] = v2
        R_ex, q_ex, R_pp, q_pp = rec["R_ex"], rec["q_ex"], rec["R_pp"], rec["q_pp"]
        rec["exact"] = bool(not rec["frozen"] and q_ex == q_ex and q_ex >= Q_MIN and R_ex <= R_MAX)
        rec["pp"] = bool(not rec["frozen"] and q_pp == q_pp and q_pp >= Q_MIN and R_pp <= R_MAX
                         and (R_ex != R_ex or R_pp < R_ex))
        rec["pp_any"] = bool(not rec["frozen"] and q_pp == q_pp and q_pp >= Q_MIN and R_pp <= R_MAX)
        rec["periodic"] = bool(not rec["frozen"] and rec["cos_ex"] == rec["cos_ex"] and rec["cos_ex"] >= COS_MIN
                               and not rec["exact"])
        windows.append(rec)

    late_from = T / 2.0
    out = dict(version=VERSION, fps=fps, n_frames=int(T), W=W, S=S, floor=floor, floor_mult=FLOOR_MULT,
               floor_freeze=floor_freeze, freeze_threshold=thr_freeze,
               region_frac=float(region.mean()), n_region_px=int(P), n_windows=len(windows),
               full=summarize(windows, W, S, fps), late=summarize([w for w in windows if w["start"] >= late_from], W, S, fps),
               windows=windows)
    return out


def _nz(v):
    """None (a rounded NaN from a cached JSON) -> NaN."""
    return float("nan") if v is None else v


def _pct(x, p):
    x = np.asarray([v for v in x if v is not None and v == v], float)
    return float(np.percentile(x, p)) if len(x) else float("nan")


def lag_summary(lags, fps):
    """lag_dominant_s: mode of the exact-window lags. lag_period_s: the smallest value >= LAG_MIN_PERIOD frames among the
    lags and their pairwise differences of which >= LAG_CONS_MIN of the lags lie within LAG_TOL frame of a multiple
    (fallback: the mode); lag_consistency: that fraction at lag_period_s; lag_min_s: the smallest exact lag. For an
    exact loop of period P the lags are multiples of P and lag_period_s = P when P >= 2 W, else the smallest multiple of
    P that is >= 2 W (differences then recover P only when several multiples occur). Reported, not a verdict."""
    lags = [int(L) for L in lags]
    if not lags:
        return dict(lag_dominant_s=float("nan"), lag_period_s=float("nan"), lag_consistency=float("nan"),
                    lag_min_s=float("nan"), n_lags=0)
    mode = Counter(lags).most_common(1)[0][0]
    uniq = sorted(set(lags))

    def cons(c):
        ok = 0
        for L in lags:
            k = max(1, int(round(L / c)))
            ok += abs(L - k * c) <= LAG_TOL
        return ok / len(lags)

    cands = set(uniq) | {abs(a - b) for a in uniq for b in uniq if a != b}
    cands = sorted(c for c in cands if c >= LAG_MIN_PERIOD)
    period, c_best = mode, cons(mode)
    for c in cands:
        if c >= mode:
            break
        f = cons(c)
        if f >= LAG_CONS_MIN:
            period, c_best = c, f
            break
    return dict(lag_dominant_s=float(mode / fps), lag_period_s=float(period / fps), lag_consistency=float(c_best),
                lag_min_s=float(min(lags) / fps), n_lags=len(lags))


def summarize(windows, W, S, fps):
    """Video-level scores on a list of window records."""
    n = len(windows)
    nf = [w for w in windows if not w["frozen"]]
    searchable = [w for w in nf if w["R_ex"] == w["R_ex"]]  # had an EXACT candidate (lag >= 2 W available)
    searchable_pp = [w for w in nf if w["R_pp"] == w["R_pp"]]
    ex = [w for w in nf if w["exact"]]
    out = dict(n_windows=n, n_nonfrozen=len(nf), n_searchable=len(searchable),
               freeze_frac=(sum(w["frozen"] for w in windows) / n) if n else float("nan"),
               freeze_frac_spec=(sum(w["frozen_spec"] for w in windows) / n) if n else float("nan"),
               exact_frac=(len(ex) / len(searchable)) if searchable else float("nan"),
               pp_frac=(sum(w["pp"] for w in nf) / len(searchable_pp)) if searchable_pp else float("nan"),
               pp_any_frac=(sum(w["pp_any"] for w in nf) / len(searchable_pp)) if searchable_pp else float("nan"),
               periodic_frac=(sum(w["periodic"] for w in nf) / len(searchable)) if searchable else float("nan"),
               R_ex_p10=_pct([w["R_ex"] for w in nf], 10), R_pp_p10=_pct([w["R_pp"] for w in nf], 10),
               q_ex_p90=_pct([w["q_ex"] for w in nf], 90), q_pp_p90=_pct([w["q_pp"] for w in nf], 90),
               cos_ex_p90=_pct([w["cos_ex"] for w in nf], 90),
               F_p10=_pct([w["F"] for w in windows], 10), floor_est_in_video=_pct([w["F"] for w in windows], 5),
               sigma_median=_pct([w["sigma"] for w in windows], 50))
    # longest contiguous run of exact-flagged grid windows (seconds covered)
    run = best = 0
    for w in windows:
        run = run + 1 if w["exact"] else 0
        best = max(best, run)
    out["exact_run_max_s"] = float(((best - 1) * S + W) / fps) if best else 0.0
    out["exact_run_max_windows"] = int(best)
    lags = [w["lag_frames_ex"] for w in ex]
    out.update(lag_summary(lags, fps))
    out["replay_suspect"] = bool(out["exact_frac"] == out["exact_frac"] and out["exact_frac"] >= SUSPECT_FRAC)
    out["pingpong_suspect"] = bool(out["pp_frac"] == out["pp_frac"] and out["pp_frac"] >= SUSPECT_FRAC)
    out["freeze_suspect"] = bool(out["freeze_frac"] == out["freeze_frac"] and out["freeze_frac"] >= SUSPECT_FRAC)
    return out


# ------------------------------------------------------------------------------------------------- DINO (exploratory)
def dino_column(video_path, starts, W, fps):
    """Exploratory: DINOv2 ViT-B/14 CLS embedding of each window's centre frame (cached offline hub code + weights);
    per window the max cosine similarity to an earlier window at lag >= 2 W. State recurrence, NOT replay."""
    import cv2
    import torch
    hub = os.path.expanduser("~/.cache/torch/hub/facebookresearch_dinov2_main")
    model = torch.hub.load(hub, "dinov2_vitb14", source="local", pretrained=False)
    sd = torch.load(os.path.expanduser("~/.cache/torch/hub/checkpoints/dinov2_vitb14_pretrain.pth"), map_location="cpu")
    model.load_state_dict(sd)
    model.eval()
    centres = {int(s + W // 2) for s in starts}
    cap = cv2.VideoCapture(video_path)
    feats, t = {}, 0
    mean = np.array([0.485, 0.456, 0.406], np.float32)
    std = np.array([0.229, 0.224, 0.225], np.float32)
    with torch.no_grad():
        while True:
            ok, f = cap.read()
            if not ok:
                break
            if t in centres:
                x = cv2.cvtColor(cv2.resize(f, (224, 224), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
                x = (x.astype(np.float32) / 255.0 - mean) / std
                e = model(torch.from_numpy(x).permute(2, 0, 1)[None])[0].numpy()
                feats[t] = e / max(np.linalg.norm(e), 1e-9)
            t += 1
    cap.release()
    out = []
    for s in starts:
        c = int(s + W // 2)
        best = float("nan")
        for s2 in starts:
            if s - s2 >= 2 * W and int(s2 + W // 2) in feats and c in feats:
                v = float(feats[c] @ feats[int(s2 + W // 2)])
                best = v if best != best else max(best, v)
        out.append(best)
    return out


# ------------------------------------------------------------------------------------------------------ per video
def load_floor(path=None):
    """(floor, floor_freeze, source) from calibration.json, else the provisional values."""
    p = path or f"{OUT_ROOT}/calibration.json"
    if os.path.exists(p):
        try:
            c = json.load(open(p))
            return float(c["floor"]), float(c.get("floor_freeze", FLOOR_FREEZE_PROVISIONAL)), p
        except Exception:
            pass
    return FLOOR_PROVISIONAL, FLOOR_FREEZE_PROVISIONAL, "provisional"


def score_video(video, mask, floor=None, features=(), meta=None, floor_freeze=None):
    _limit_threads()
    t0 = time.time()
    cf, cff, src = load_floor()
    floor_src = "arg" if floor is not None else src
    floor = cf if floor is None else floor
    floor_freeze = cff if floor_freeze is None else floor_freeze
    gray, fps, shape = read_video_gray(video)
    region, region_name, abstain = load_region(mask, gray.shape[1:])
    doc = dict(video=os.path.relpath(video, REPO) if video.startswith(REPO) else video, labels=mask,
               video_sha256=sha256_file(video), labels_sha256=sha256_file(mask) if os.path.exists(mask) else None,
               module_sha256=module_sha(), version=VERSION, region=region_name, abstain_reason=abstain,
               fps=fps, n_frames=int(gray.shape[0]), orig_shape=list(shape), floor=floor, floor_freeze=floor_freeze,
               floor_source=floor_src,
               meta=meta or {})
    if abstain:
        doc.update(full=None, late=None, windows=[])
        doc["seconds"] = round(time.time() - t0, 2)
        return doc
    res = score_frames(gray, region, fps, floor, floor_freeze=floor_freeze)
    if "dino" in features:
        col = dino_column(video, [w["start"] for w in res["windows"]], res["W"], fps)
        for w, c in zip(res["windows"], col):
            w["dino_cos_max"] = c
        res["full"]["dino_cos_max_p90"] = _pct(col, 90)
        res["late"]["dino_cos_max_p90"] = _pct([c for w, c in zip(res["windows"], col) if w["start"] >= gray.shape[0] / 2], 90)
    doc.update(res)
    doc["seconds"] = round(time.time() - t0, 2)
    return doc


def _round(o, nd=4):
    if isinstance(o, float):
        return None if o != o else round(o, nd)
    if isinstance(o, dict):
        return {k: _round(v, nd) for k, v in o.items()}
    if isinstance(o, list):
        return [_round(v, nd) for v in o]
    return o


def _score_job(args):
    video, mask, floors, features, meta, out = args
    floor, floor_freeze = floors
    if out and os.path.exists(out):
        try:
            d = json.load(open(out))
            if (d.get("module_sha256") == module_sha() and d.get("video_sha256") == sha256_file(video)
                    and d.get("floor") == floor and d.get("floor_freeze") == floor_freeze):
                return d
        except Exception:
            pass
    d = _round(score_video(video, mask, floor, features, meta, floor_freeze))
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        tmp = out + ".tmp"
        json.dump(d, open(tmp, "w"))
        os.replace(tmp, out)
    return d


# ---------------------------------------------------------------------------------------------- validation set
def _read_video_bgr(path):
    import cv2
    cap = cv2.VideoCapture(path)
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    fr = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fr.append(f)
    cap.release()
    return np.stack(fr), fps


def _encode(frames, path, fps, ffmpeg=FFMPEG):
    """decode -> transform -> encode with libx264 crf 23 preset medium yuv420p (identity transform for originals)."""
    h, w = frames.shape[1:3]
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
           "-r", f"{fps:g}", "-i", "-", "-c:v", "libx264", "-crf", "23", "-preset", "medium", "-pix_fmt", "yuv420p",
           "-threads", "4", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    _, err = p.communicate(np.ascontiguousarray(frames).tobytes())
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {path}: {err.decode(errors='replace')[-500:]}")


# validation transforms (v1.1): the spec C0 §4 set (10) + adversarial loops (8) + synthetic periodic negatives (3)
CLIP_NAMES = ["original", "loop_2s", "loop_5s", "loop_10s", "late_loop_2s", "xfade_2s_0.25s", "xfade_2s_0.5s", "pp_2s",
              "pp_5s", "freeze",
              "xfade_2s_1s", "loop_9fr", "loop_23fr", "loop_43fr", "jitter_loop_2s", "timewarp_loop_2s",
              "loop_2s_drift_add25", "loop_2s_drift_gain",
              "synth_osc_rigid", "synth_osc_evolving4", "synth_osc_evolving12"]
# synthetic periodic negatives: rigid sinusoidal warp (3 px, period 2 s, +-0.6 rad random phase per cycle) of one still
# of the scene plus additive AR(1) haze; (rho per frame, full-res blur sigma, haze std at the THUMBNAIL scale in grey)
SYNTH_OSC = {"synth_osc_rigid": (0.99, 8.0, 6.0),        # slow haze (> 1 s): fixed texture oscillating -> exact by definition
             "synth_osc_evolving4": (0.90, 3.0, 4.0),    # sub-second texture evolution near the 3 x floor threshold
             "synth_osc_evolving12": (0.90, 3.0, 12.0)}  # sub-second texture evolution well above it (real-scene-like)
SYNTH_TYPES = ["synth_rigid", "synth_evolving4", "synth_evolving12"]
POS_TYPES = ["loop", "late_loop", "xfade", "pingpong", "freeze", "loop_odd", "jitter_loop", "timewarp_loop", "drift_loop"]


def _tile(seg, n):
    reps = int(np.ceil(n / len(seg)))
    return np.concatenate([seg] * reps)[:n]


def synth_osc_frames(base, T, fps, rho, blur_sigma, amp_thumb, rng, period_s=2.0, amp_px=3.0, jitter_rad=0.6):
    """Synthetic PERIODIC NON-REPLAY: a rigid sinusoidal warp of a single still (period period_s, amp_px pixels, a random
    phase step of +-jitter_rad per cycle so no cycle repeats a previous one exactly) plus additive AR(1) haze (rho per
    frame, low-passed with blur_sigma at full resolution, std amp_thumb grey levels at the 208x120 thumbnail scale).
    No output frame is a copy of an earlier frame; the motion signature of the warp recurs every cycle."""
    import cv2
    base = base.astype(np.float32)
    h, w = base.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    P = period_s * fps

    def lp():
        return cv2.GaussianBlur(rng.randn(h, w).astype(np.float32), (0, 0), blur_sigma)

    n0 = lp()
    thumb_std = cv2.resize(n0, (THUMB_W, THUMB_H), interpolation=cv2.INTER_AREA).std()
    scale = amp_thumb / max(thumb_std, 1e-6)
    noise = n0 * scale
    phase = 0.0
    out = np.empty((T,) + base.shape, np.uint8)
    for t in range(T):
        if t % int(P) == 0:
            phase += rng.uniform(-jitter_rad, jitter_rad)
        d = amp_px * np.sin(2 * np.pi * t / P + phase)
        mapx = xx + d * np.sin(yy / 25.0)
        mapy = yy + 0.5 * d * np.cos(xx / 30.0)
        noise = rho * noise + np.sqrt(1 - rho ** 2) * lp() * scale
        f = cv2.remap(base, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT) + noise[..., None]
        out[t] = np.clip(f, 0, 255).astype(np.uint8)
    return out


def iter_clips(frames, fps, t0_s=VAL_T0_S, onset_s=VAL_ONSET_S, skip=(), seed=0):
    """Yields (clip name, frames or None if name in skip, label dict) for every CLIP_NAMES transform of a (T, H, W, 3)
    uint8 source, one clip alive at a time. Output length = T frames for every clip."""
    T = len(frames)
    t0 = int(round(t0_s * fps))
    onset = int(round(onset_s * fps))
    P2 = int(round(2 * fps))
    rng = np.random.RandomState(seed)

    def xfade(F_s):
        F = int(round(F_s * fps))
        seg = frames[t0 - F:t0 + P2].astype(np.float32)  # F frames before the head, then the P-frame period
        loop = seg[F:F + P2].copy()
        for j in range(F):
            k = P2 - F + j
            w = (j + 1) / (F + 1)
            loop[k] = (1 - w) * seg[F + k] + w * seg[j]  # tail fades into the frames that precede the head
        return _tile(np.clip(np.rint(loop), 0, 255).astype(np.uint8), T)

    def jitter_loop():  # each repetition of the 2 s segment is cut with +-2 frames at both ends (period 28..36)
        seg = frames[t0:t0 + P2]
        parts, n = [], 0
        while n < T:
            a = rng.randint(-2, 3)
            b = rng.randint(-2, 3)
            part = seg[max(0, a):P2 + b] if b <= 0 else np.concatenate([seg[max(0, a):], frames[t0 + P2:t0 + P2 + b]])
            parts.append(part)
            n += len(part)
        return np.concatenate(parts)[:T]

    def timewarp_loop():  # the 2 s segment replayed at rates 0.9..1.1 (a new rate per cycle), frame index rounded
        seg = frames[t0:t0 + P2]
        idx, t = [], 0.0
        while len(idx) < T:
            rate = rng.uniform(0.9, 1.1)
            for _ in range(P2):
                idx.append(int(round(t)) % P2)
                t += rate
        return seg[np.array(idx[:T])]

    builders = {
        "original": (lambda: frames, dict(cls="original", type="original", period_s=None, onset_s=None)),
        "late_loop_2s": (lambda: np.concatenate([frames[:onset], _tile(frames[onset - P2:onset], T - onset)]),
                         dict(cls="exact", type="late_loop", period_s=2, onset_s=onset_s)),
        "freeze": (lambda: np.concatenate([frames[:onset], np.repeat(frames[onset - 1:onset], T - onset, 0)]),
                   dict(cls="freeze", type="freeze", period_s=None, onset_s=onset_s)),
        "jitter_loop_2s": (jitter_loop, dict(cls="exact", type="jitter_loop", period_s=2, onset_s=0.0, param="jitter+-2fr")),
        "timewarp_loop_2s": (timewarp_loop, dict(cls="exact", type="timewarp_loop", period_s=2, onset_s=0.0, param="rate0.9-1.1")),
        "loop_2s_drift_add25": (lambda: np.clip(_tile(frames[t0:t0 + P2], T).astype(np.float32)
                                                + np.linspace(0, 25, T)[:, None, None, None], 0, 255).astype(np.uint8),
                                dict(cls="exact", type="drift_loop", period_s=2, onset_s=0.0, param="add+25")),
        "loop_2s_drift_gain": (lambda: np.clip(_tile(frames[t0:t0 + P2], T).astype(np.float32)
                                               * np.linspace(0.8, 1.2, T)[:, None, None, None], 0, 255).astype(np.uint8),
                               dict(cls="exact", type="drift_loop", period_s=2, onset_s=0.0, param="gain0.8-1.2")),
    }
    for P_s in (2, 5, 10):
        P = int(round(P_s * fps))
        builders[f"loop_{P_s}s"] = ((lambda P=P: _tile(frames[t0:t0 + P], T)),
                                    dict(cls="exact", type="loop", period_s=P_s, onset_s=0.0))
    for Pf in (9, 23, 43):  # periods that are not multiples of the window (9 fr < W)
        builders[f"loop_{Pf}fr"] = ((lambda Pf=Pf: _tile(frames[t0:t0 + Pf], T)),
                                    dict(cls="exact", type="loop_odd", period_s=Pf / fps, period_frames=Pf, onset_s=0.0))
    for F_s in (0.25, 0.5, 1.0):
        builders[f"xfade_2s_{F_s:g}s"] = ((lambda F_s=F_s: xfade(F_s)),
                                          dict(cls="exact", type="xfade", period_s=2, fade_s=F_s, onset_s=0.0))
    for P_s in (2, 5):
        P = int(round(P_s * fps))
        builders[f"pp_{P_s}s"] = ((lambda P=P: _tile(np.concatenate([frames[t0:t0 + P], frames[t0:t0 + P][-2:0:-1]]), T)),
                                  dict(cls="pp", type="pingpong", period_s=P_s, onset_s=0.0))
    for name, (rho, bs, amp) in SYNTH_OSC.items():
        builders[name] = ((lambda rho=rho, bs=bs, amp=amp: synth_osc_frames(frames[t0], T, fps, rho, bs, amp, rng)),
                          dict(cls="synthetic_negative", type=name.replace("synth_osc_", "synth_"), period_s=2,
                               onset_s=0.0, param=f"rho{rho}_blur{bs:g}_amp{amp:g}"))
    for name in CLIP_NAMES:
        fn, lab = builders[name]
        if name in skip:
            yield name, None, lab
            continue
        fr = fn()
        assert len(fr) == T, (name, len(fr), T)
        yield name, fr, lab


def make_clips(frames, fps, t0_s=VAL_T0_S, onset_s=VAL_ONSET_S):
    """{clip name: (frames, label dict)}: all transforms at once (tests, small inputs). Large sources: iter_clips."""
    return {name: (fr, lab) for name, fr, lab in iter_clips(frames, fps, t0_s, onset_s)}


def _build_scene(args):
    sid, cell_short, out_dir = args
    _limit_threads(4)
    cell = CELLS[cell_short]
    src = f"{SCORE_INPUTS.format(cell=cell)}/{sid}.mp4"
    frames, fps = _read_video_bgr(src)
    rows = []
    skip = {n for n in CLIP_NAMES if os.path.exists(f"{out_dir}/{sid}__{n}.mp4")}
    for name, fr, lab in iter_clips(frames, fps, skip=skip):
        path = f"{out_dir}/{sid}__{name}.mp4"
        if fr is not None:
            _encode(fr, path + ".tmp.mp4", fps)
            os.replace(path + ".tmp.mp4", path)
            del fr
        rows.append(dict(clip=f"{sid}__{name}", path=os.path.relpath(path, REPO), scene=sid,
                         category=CATEGORY.get(sid[:3], "?"), cell=cell, source=os.path.relpath(src, REPO),
                         source_sha256=sha256_file(src), sha256=sha256_file(path), n_frames=int(len(frames)), fps=fps,
                         **lab))
    return rows


def build_validation(out_dir=f"{OUT_ROOT}/valset", jobs=12):
    os.makedirs(out_dir, exist_ok=True)
    man_path = f"{out_dir}/manifest.json"
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(jobs, len(VAL_SCENES))) as ex:
        rows = [r for rs in ex.map(_build_scene, [(s, c, out_dir) for s, c in VAL_SCENES]) for r in rs]
    man = dict(version=VERSION, module_sha256=module_sha(), ffmpeg=FFMPEG,
               encode="libx264 crf 23 preset medium yuv420p, every clip (originals included) decoded -> transformed -> encoded",
               t0_s=VAL_T0_S, onset_s=VAL_ONSET_S, transforms=CLIP_NAMES, synth_osc=SYNTH_OSC, n=len(rows),
               seconds=round(time.time() - t0, 1), clips=rows)
    json.dump(man, open(man_path, "w"), indent=1)
    return man


def calibrate(man, out_path=f"{OUT_ROOT}/calibration.json"):
    """Codec floor at the thumbnail scale: mean region |thumb(identity re-encode) - thumb(original)|."""
    per = {}
    for r in man["clips"]:
        if r["type"] != "original":
            continue
        g0, _, _ = read_video_gray(f"{REPO}/{r['source']}")
        g1, _, _ = read_video_gray(f"{REPO}/{r['path']}")
        region, name, ab = load_region(f"{MASK_ROOT}/{r['scene']}/labels.png", g0.shape[1:])
        if ab:
            continue
        n = min(len(g0), len(g1))
        d = np.abs(g0[:n] - g1[:n])[:, region]
        per[r["scene"]] = dict(mean=float(d.mean()), p95=float(np.percentile(d, 95)), region=name)
    floor = float(np.mean([v["mean"] for v in per.values()]))
    held = {}
    for r in man["clips"]:
        if r["type"] != "freeze":
            continue
        g, fps, _ = read_video_gray(f"{REPO}/{r['path']}")
        region, name, ab = load_region(f"{MASK_ROOT}/{r['scene']}/labels.png", g.shape[1:])
        if ab:
            continue
        W = int(round(fps))
        X = g.reshape(len(g), -1)[:, region.ravel()]
        fd = np.abs(np.diff(X[int(round(r["onset_s"] * fps)) + W:], axis=0)).mean(1)  # held segment, past the onset
        held[r["scene"]] = dict(mean=float(fd.mean()), p95=float(np.percentile(fd, 95)), max=float(fd.max()))
    floor_freeze = float(np.mean([v["p95"] for v in held.values()])) if held else FLOOR_FREEZE_PROVISIONAL
    doc = dict(version=VERSION, module_sha256=module_sha(), floor=floor, floor_mult=FLOOR_MULT,
               threshold=FLOOR_MULT * floor, provisional_floor=FLOOR_PROVISIONAL, per_scene=per,
               floor_freeze=floor_freeze, freeze_min=FREEZE_MIN,
               freeze_threshold=max(FLOOR_MULT * floor_freeze, FREEZE_MIN), held_segment_per_scene=held,
               note="floor: mean region |thumb(recoded) - thumb(orig)| over the identity re-encodes of the validation "
                    "originals (cross-encode residual, used by q and by freeze_frac_spec). floor_freeze: p95 of the "
                    "frame-to-frame region change inside the held segments of the freeze clips (within-encode residual); "
                    "frozen iff F < max(floor_mult * floor_freeze, freeze_min)")
    json.dump(doc, open(out_path, "w"), indent=1)
    return doc


def auroc(pos, neg):
    """Mann-Whitney AUROC with ties = 0.5 (NaN scores dropped)."""
    pos = [p for p in pos if p is not None and p == p]
    neg = [n for n in neg if n is not None and n == n]
    if not pos or not neg:
        return float("nan")
    s = 0.0
    for p in pos:
        for n in neg:
            s += 1.0 if p > n else (0.5 if p == n else 0.0)
    return s / (len(pos) * len(neg))


def _dist(xs):
    xs = [x for x in xs if x is not None and x == x]
    if not xs:
        return dict(n=0)
    return dict(n=len(xs), min=float(min(xs)), p25=float(np.percentile(xs, 25)), median=float(np.median(xs)),
                p75=float(np.percentile(xs, 75)), max=float(max(xs)), mean=float(np.mean(xs)))


def validation_report(docs, man, calib, extra=None):
    """AUROC per failure type against the originals; hard-negative distributions; threshold sensitivity."""
    by = {}
    for r, d in zip(man["clips"], docs):
        by[r["clip"]] = (r, d)
    neg = [(r, d) for r, d in by.values() if r["type"] == "original" and d.get("full")]
    types = POS_TYPES
    loop_cols = [("exact_frac", 1), ("R_ex_p10", -1), ("q_ex_p90", 1)]
    # score columns per type: (half, primary, backups...) ; higher = more suspect for all listed (sign flips applied)
    cols = {"loop": ("full", loop_cols), "late_loop": ("late", loop_cols), "xfade": ("full", loop_cols),
            "loop_odd": ("full", loop_cols), "jitter_loop": ("full", loop_cols), "timewarp_loop": ("full", loop_cols),
            "drift_loop": ("full", loop_cols),
            "pingpong": ("full", [("pp_frac", 1), ("pp_any_frac", 1), ("R_pp_p10", -1), ("exact_frac", 1)]),
            "freeze": ("late", [("freeze_frac", 1), ("freeze_frac_spec", 1), ("F_p10", -1)])}
    # negative pools: the 12 re-encoded originals (the pre-registered AUROC), plus stress pools with the synthetic
    # periodic negatives (evolving texture = real-like; rigid = fixed texture, exact by definition, see the module doc)
    synth = {t: [(r, d) for r, d in by.values() if r["type"] == t and d.get("full")] for t in SYNTH_TYPES}
    neg_pools = {"originals": neg,
                 "originals+synth_evolving": neg + synth["synth_evolving4"] + synth["synth_evolving12"],
                 "originals+synth_all": neg + sum(synth.values(), [])}
    rep = dict(version=VERSION, module_sha256=module_sha(), floor=calib["floor"], n_clips=len(docs), auroc={},
               auroc_stress={}, by_type={}, per_scene={}, hard_negatives={}, synthetic_negatives={}, sensitivity={},
               confusion={}, periodic_label={}, runtime={})

    def _auroc_row(items, negs, half, c, sgn):
        p = [sgn * _nz(d[half][c]) for r, d in items]
        n = [sgn * _nz(d[half][c]) for r, d in negs]
        pv = [v for v in p if v == v]
        nv = [v for v in n if v == v]
        return dict(auroc=auroc(p, n), n_pos=len(pv), n_neg=len(nv), n_pos_nan=len(p) - len(pv),
                    pos_min=float(min(pv)) * sgn if pv else None, neg_max=float(max(nv)) * sgn if nv else None)

    for t in types:
        half, cl = cols[t]
        pos = [(r, d) for r, d in by.values() if r["type"] == t and d.get("full")]
        groups = {"all": pos}
        for r, d in pos:  # per parameter (period / fade / other)
            key = ",".join(k for k in [f"P={r['period_s']:g}s" if r.get("period_s") is not None else "",
                                       f"fade={r['fade_s']:g}s" if r.get("fade_s") else "", r.get("param") or ""] if k)
            if key:
                groups.setdefault(key, []).append((r, d))
        rep["auroc"][t] = {g: {c: _auroc_row(items, neg, half, c, sgn) for c, sgn in cl} for g, items in groups.items()}
        rep["auroc_stress"][t] = {pool: {c: _auroc_row(pos, negs, half, c, sgn) for c, sgn in cl}
                                  for pool, negs in neg_pools.items()}
        rep["by_type"][t] = {c: _dist([d[half][c] for r, d in pos]) for c, _ in cl}
        rep["by_type"][t]["half"] = half
        for k in ("lag_dominant_s", "lag_period_s", "lag_min_s", "lag_consistency"):
            rep["by_type"][t][k] = {r["clip"]: d[half][k] for r, d in pos}
        rep["by_type"][t]["lag_consistency_dist"] = _dist([d[half]["lag_consistency"] for r, d in pos])
        rep["by_type"][t]["lag_period_expected_s"] = {r["clip"]: r.get("period_s") for r, d in pos}
        for r, d in pos:  # per-scene primary score (exposes scenes a transform misses)
            rep["per_scene"].setdefault(r["scene"], {})[r["clip"].split("__", 1)[1]] = d[half][cl[0][0]]
    keys_s = ["exact_frac", "pp_frac", "pp_any_frac", "freeze_frac", "periodic_frac", "R_ex_p10", "q_ex_p90",
              "cos_ex_p90", "F_p10", "sigma_median", "lag_period_s", "lag_consistency"]
    for t, items in synth.items():
        rep["synthetic_negatives"][t] = dict(construction=SYNTH_OSC["synth_osc_" + t[6:]], n=len(items),
                                            dist={k: _dist([d["full"][k] for r, d in items]) for k in keys_s},
                                            per_clip={r["clip"]: {k: d["full"][k] for k in keys_s} for r, d in items},
                                            n_replay_suspect=sum(d["full"]["replay_suspect"] for r, d in items),
                                            n_exact_nonzero=sum(_nz(d["full"]["exact_frac"]) > 0 for r, d in items))
    # hard negatives: originals, per category, all scores
    keys = ["exact_frac", "pp_frac", "pp_any_frac", "freeze_frac", "freeze_frac_spec", "periodic_frac", "R_ex_p10",
            "R_pp_p10", "F_p10", "cos_ex_p90", "q_ex_p90", "sigma_median"]
    rep["hard_negatives"]["originals_all"] = {k: _dist([d["full"][k] for r, d in neg]) for k in keys}
    rep["hard_negatives"]["originals_periodic_categories"] = {
        k: _dist([d["full"][k] for r, d in neg if r["category"] in PERIODIC_CATEGORIES]) for k in keys}
    rep["hard_negatives"]["originals_per_clip"] = {r["clip"]: {k: d["full"][k] for k in keys} for r, d in neg}
    if extra:
        for name, lst in extra.items():
            rep["hard_negatives"][name] = {k: _dist([d["full"][k] for d in lst if d.get("full")]) for k in keys}
            rep["hard_negatives"][name + "_per_video"] = {d["meta"].get("sid", d["video"]): {k: d["full"][k] for k in keys}
                                                          for d in lst if d.get("full")}
    # threshold sensitivity: fraction of clips flagged at exact_frac / pp_frac / freeze_frac >= thr
    for thr in (0.05, 0.10, 0.25, 0.50):
        row = {}
        for t in ["original"] + types + SYNTH_TYPES:
            half = cols.get(t, ("full", None))[0]
            items = [(r, d) for r, d in by.values() if r["type"] == t and d.get("full")]
            row[t] = {k: float(np.mean([_nz(d[half][k]) >= thr for r, d in items])) if items else None
                      for k in ("exact_frac", "pp_frac", "freeze_frac")}
        rep["sensitivity"][str(thr)] = row
    # confusion: mean of each score per type (full and late)
    for t in ["original"] + types + SYNTH_TYPES:
        items = [(r, d) for r, d in by.values() if r["type"] == t and d.get("full")]
        rep["confusion"][t] = {h: {k: float(np.nanmean([_nz(d[h][k]) for r, d in items])) if items else float("nan") for k in
                                   ("exact_frac", "pp_frac", "pp_any_frac", "freeze_frac", "freeze_frac_spec", "periodic_frac")} for h in ("full", "late")}
    rep["periodic_label"] = {r["clip"]: dict(category=r["category"], periodic_frac=d["full"]["periodic_frac"],
                                             cos_ex_p90=d["full"]["cos_ex_p90"], exact_frac=d["full"]["exact_frac"])
                             for r, d in neg}
    secs = [d["seconds"] for d in docs if "seconds" in d]
    rep["runtime"] = dict(per_video_s=_dist(secs))
    rep["thresholds"] = dict(Q_MIN=Q_MIN, R_MAX=R_MAX, COS_MIN=COS_MIN, SUSPECT_FRAC=SUSPECT_FRAC, FLOOR_MULT=FLOOR_MULT,
                             floor=calib["floor"], FREEZE_MIN=FREEZE_MIN, LAG_D2_MULT=LAG_D2_MULT,
                             MAX_LAG_REFINE=MAX_LAG_REFINE, LAG_TOL=LAG_TOL, LAG_MIN_PERIOD=LAG_MIN_PERIOD)
    # lag recovery check: exact-loop clips whose lag_period_s equals the expected period (or its smallest multiple >= 2 W)
    W = 2.0  # seconds, = 2 W at 16 fps
    chk = {}
    for t in ("loop", "late_loop", "xfade", "loop_odd", "drift_loop"):
        half = cols[t][0]
        for r, d in ((r, d) for r, d in by.values() if r["type"] == t and d.get("full")):
            P = r["period_s"]
            exp = P * int(np.ceil(W / P - 1e-9))  # smallest multiple of P that is >= 2 s
            got = d[half]["lag_period_s"]
            chk[r["clip"]] = dict(expected_s=exp, period_s=P, lag_period_s=got, lag_dominant_s=d[half]["lag_dominant_s"],
                                  ok=bool(got is not None and got == got and abs(got - exp) * 16 <= LAG_TOL + 0.01))
    rep["lag_check"] = dict(n=len(chk), n_ok=sum(v["ok"] for v in chk.values()), per_clip=chk)
    return rep


def _fmt(v, nd=3):
    if v is None or (isinstance(v, float) and v != v):
        return "—"
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


def report_md(rep, man, calib):
    L = [f"# Repetition diagnostic — validation report ({VERSION})", "",
         "A DIAGNOSTIC (docs/120 stream C): recurrence scores on label-2 multi-frame descriptors. It reports scores and does",
         "not state realism. Genuine periodic motion is a hard negative and carries its own label (\"periodic, not replay\").",
         "", f"Validation set: {man['n']} clips = {len(VAL_SCENES)} scenes x {man['n'] // len(VAL_SCENES)} transforms "
         f"(spec C0 set: original, loops 2/5/10 s, late loop, cross-fades 0.25/0.5 s, ping-pong 2/5 s, freeze; adversarial: "
         f"cross-fade 1 s, loops of 9/23/43 frames, jittered and time-warped 2 s loops, 2 s loops with additive and gain "
         f"drift; synthetic periodic negatives: rigid oscillation with slow haze, oscillation with sub-second texture "
         f"evolution of 4 and 12 grey), every clip (originals included) "
         f"decoded -> transformed -> encoded with libx264 crf 23 (manifest: valset/manifest.json). "
         f"Codec floor (thumbnail scale, cross-encode) = {calib['floor']:.3f} grey levels (provisional was {FLOOR_PROVISIONAL}); "
         f"threshold {FLOOR_MULT:g} x floor = {calib['threshold']:.3f}. Held-segment floor_freeze = {calib['floor_freeze']:.4f}; "
         f"freeze threshold max({FLOOR_MULT:g} x floor_freeze, {FREEZE_MIN}) = {calib['freeze_threshold']:.3f} (amendment: the "
         f"spec rule F < {FLOOR_MULT:g} x floor = {calib['threshold']:.2f} is reported as freeze_frac_spec). Flags: exact iff q_ex >= {Q_MIN} "
         f"and R_ex <= {R_MAX}; pp iff q_pp >= {Q_MIN}, R_pp <= {R_MAX}, R_pp < R_ex; periodic iff cos_ex >= {COS_MIN} and not exact. "
         f"Suspect reading threshold {SUSPECT_FRAC} (provisional, not a verdict).",
         "", "## AUROC per failure type (positives = that transform, negatives = the 12 re-encoded originals)", "",
         "| type | group | score (half) | AUROC | n_pos / n_neg | min(pos) | max(neg) |", "|---|---|---|---|---|---|---|"]
    halves = {"late_loop": "late", "freeze": "late"}
    for t, groups in rep["auroc"].items():
        for g, cols in groups.items():
            for c, v in cols.items():
                L.append(f"| {t} | {g} | {c} ({halves.get(t, 'full')}) | {_fmt(v['auroc'])} | {v['n_pos']} / {v['n_neg']} | "
                         f"{_fmt(v['pos_min'])} | {_fmt(v['neg_max'])} |")
    L += ["", "## Hard negatives: re-encoded originals (full video)", "",
          "| score | n | min | p25 | median | p75 | max |", "|---|---|---|---|---|---|---|"]
    for name in ("originals_all", "originals_periodic_categories"):
        L.append(f"| **{name}** | | | | | | |")
        for k, d in rep["hard_negatives"][name].items():
            if d.get("n"):
                L.append(f"| {k} | {d['n']} | {_fmt(d['min'])} | {_fmt(d['p25'])} | {_fmt(d['median'])} | {_fmt(d['p75'])} | {_fmt(d['max'])} |")
    for name, d in rep["hard_negatives"].items():
        if name.startswith("originals") or name.endswith("_per_video"):
            continue
        L.append(f"| **{name}** | | | | | | |")
        for k, dd in d.items():
            if dd.get("n"):
                L.append(f"| {k} | {dd['n']} | {_fmt(dd['min'])} | {_fmt(dd['p25'])} | {_fmt(dd['median'])} | {_fmt(dd['p75'])} | {_fmt(dd['max'])} |")
    L += ["", "### Originals per clip", "", "| clip | category | exact | pp | freeze | periodic | R_ex_p10 | R_pp_p10 | F_p10 | cos_ex_p90 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for clip, d in rep["hard_negatives"]["originals_per_clip"].items():
        cat = rep["periodic_label"][clip]["category"]
        L.append(f"| {clip} | {cat} | {_fmt(d['exact_frac'])} | {_fmt(d['pp_frac'])} | {_fmt(d['freeze_frac'])} | {_fmt(d['periodic_frac'])} | "
                 f"{_fmt(d['R_ex_p10'])} | {_fmt(d['R_pp_p10'])} | {_fmt(d['F_p10'])} | {_fmt(d['cos_ex_p90'])} |")
    L += ["", "## Mean scores per transform (confusion)", "", "| type | half | exact_frac | pp_frac | pp_any_frac | freeze_frac | freeze_frac_spec | periodic_frac |",
          "|---|---|---|---|---|---|---|---|"]
    for t, hs in rep["confusion"].items():
        for h, d in hs.items():
            L.append(f"| {t} | {h} | {_fmt(d['exact_frac'])} | {_fmt(d['pp_frac'])} | {_fmt(d['pp_any_frac'])} | {_fmt(d['freeze_frac'])} | {_fmt(d['freeze_frac_spec'])} | {_fmt(d['periodic_frac'])} |")
    L += ["", "## Threshold sensitivity: fraction of clips flagged at score >= thr (late half for late_loop / freeze)", "",
          "| thr | type | exact_frac | pp_frac | freeze_frac |", "|---|---|---|---|---|"]
    for thr, row in rep["sensitivity"].items():
        for t, d in row.items():
            L.append(f"| {thr} | {t} | {_fmt(d['exact_frac'])} | {_fmt(d['pp_frac'])} | {_fmt(d['freeze_frac'])} |")
    L += ["", "## Stress AUROC (primary score, group all): negatives = originals, + synthetic evolving-texture oscillations, + all synthetic incl. rigid", "",
          "| type | score (half) | originals | +synth_evolving | +synth_all |", "|---|---|---|---|---|"]
    for t, pools in rep["auroc_stress"].items():
        c = list(pools["originals"])[0]
        L.append(f"| {t} | {c} ({halves.get(t, 'full')}) | " + " | ".join(_fmt(pools[p][c]["auroc"]) for p in
                                                                         ("originals", "originals+synth_evolving", "originals+synth_all")) + " |")
    L += ["", "## Synthetic periodic negatives (disclosure)", "",
          "Rigid sinusoidal warp (3 px, period 2 s, +-0.6 rad random phase step per cycle) of one still of each scene plus AR(1) haze; no frame",
          "is a copy of an earlier frame. `exact` means: the per-pixel 1 s window-mean-removed signature of the dynamic region recurs at some",
          f"lag >= 2 s within {FLOOR_MULT:g} x floor ({calib['threshold']:.2f} grey) on >= {Q_MIN:.0%} of the voxels with mean residual <= {R_MAX} of",
          "the window's own std. The mean removal discards texture evolution slower than ~1 s, so a deterministic oscillation of a FIXED texture",
          "(synth_rigid: haze rho 0.99 / frame) satisfies the definition on high-contrast bases and is reported as exact: a replay of the",
          "sub-second motion signature. The evolving variants (rho 0.9 / frame, haze std 4 and 12 grey at the thumbnail scale) show the texture",
          "change per window needed to leave the definition. Real periodic footage is never flagged (its texture evolves far above the floor).",
          "", "| clip | exact | R_ex_p10 | q_ex_p90 | periodic | sigma_med | F_p10 | lag_period_s | replay_suspect |", "|---|---|---|---|---|---|---|---|---|"]
    for t, d in rep["synthetic_negatives"].items():
        L.append(f"| **{t}** (rho, blur, amp) = {d['construction']} | flagged {d['n_replay_suspect']} / {d['n']} (exact > 0: {d['n_exact_nonzero']}) | | | | | | | |")
        for clip, v in d["per_clip"].items():
            L.append(f"| {clip} | {_fmt(v['exact_frac'])} | {_fmt(v['R_ex_p10'])} | {_fmt(v['q_ex_p90'])} | {_fmt(v['periodic_frac'])} | "
                     f"{_fmt(v['sigma_median'], 1)} | {_fmt(v['F_p10'], 2)} | {_fmt(v['lag_period_s'])} | {_fmt(v['exact_frac']) != '—' and v['exact_frac'] >= SUSPECT_FRAC} |")
    L += ["", "## Per-scene primary score per transform (exact_frac; pp_frac for pingpong; late-half freeze_frac for freeze)", ""]
    tnames = [n for n in CLIP_NAMES if n != "original" and not n.startswith("synth_")]
    L += ["| scene | " + " | ".join(tnames) + " |", "|---|" + "---|" * len(tnames)]
    for sc, row in rep["per_scene"].items():
        L.append(f"| {sc} | " + " | ".join(_fmt(row.get(n), 2) for n in tnames) + " |")
    L += ["", "## Lag recovery", "",
          "lag_period_s is the smallest exact-window lag (or lag difference) of which >= 80 % of the exact lags are multiples (+-1 frame);",
          "lag_dominant_s is the mode. The search reports the smallest lag at which the window passes the exact criterion (q >= 0.9, R <= 0.25),",
          "over all coarse-near candidates (v1.1; v1.0 took the smallest of the top-5 coarse candidates within an absolute near-tie of the best,",
          "which x264's bit-identical frames at some multiples defeated, so the lag was an arbitrary multiple). For a loop of period P the expected value is P",
          "when P >= 2 s, else the smallest multiple of P that is >= 2 s (the minimum lag L_min = 2 W): 'P or a multiple of P', not the",
          "fundamental for P < 2 s. Jittered / time-warped loops have no fixed period, so their consistency is legitimately low.", ""]
    lc = rep["lag_check"]
    L.append(f"Lag check on the fixed-period loop clips (loop, late_loop, xfade, loop_odd, drift_loop): lag_period_s equals the expected "
             f"value (+-1 frame) on {lc['n_ok']} / {lc['n']} clips; misses: "
             + (", ".join(f"{k} (expected {v['expected_s']:g}, got {_fmt(v['lag_period_s'])})" for k, v in lc["per_clip"].items() if not v["ok"]) or "none") + ".")
    L.append("")
    for t, d in rep["by_type"].items():
        L.append(f"- {t}: lag_period_s per clip = " + ", ".join(f"{k.split('__')[0]}:{_fmt(v, 3)}" for k, v in d["lag_period_s"].items())
                 + f"; lag_dominant_s = " + ", ".join(f"{_fmt(v, 3)}" for v in d["lag_dominant_s"].values())
                 + f"; lag_consistency median {_fmt(d['lag_consistency_dist'].get('median'))} min {_fmt(d['lag_consistency_dist'].get('min'))}")
    L += ["", "## Known limitations (disclosed, not fixed)", "",
          f"- `exact` is a recurrence of the sub-second motion signature within {FLOOR_MULT:g} x the codec floor; a deterministic oscillation of a "
          "fixed texture satisfies it (synthetic negatives above). Real periodic footage is not flagged because its texture evolves; the margin "
          "is the texture-evolution amplitude per window, not a physical property.",
          f"- FREEZE_MIN = {FREEZE_MIN} grey / frame at the 208x120 thumbnail labels genuinely sub-pixel motion as frozen: a synthetic 0.75 px "
          "sinusoidal warp of the low-contrast ial04 base scores F_p10 0.235 and freeze_frac 0.67 (session check, not in the validation set); "
          "the smallest F_p10 among the real negatives is 0.60 (Helios goyang-si-flood), a 2.4 x margin.",
          "- ifw05 (falling water, static-sink k = 3, sigma_median ~3, F_p10 0.85) is partly or wholly missed by several loop transforms "
          "(per-scene table above: late loop, 1 s cross-fade, 9-frame loop, jittered / time-warped loops, drift loops); its slow "
          "low-contrast motion leaves little signature above the floor. Scenes like it would need a lower floor or a longer window.",
          "- The reported lag is P or the smallest multiple of P >= 2 s; a higher multiple is reported when the descriptor at the "
          f"smaller lag fails the exact criterion or the coarse prefilter (LAG_D2_MULT = {LAG_D2_MULT}, MAX_LAG_REFINE = "
          f"{MAX_LAG_REFINE}) does not reach it.",
          "- Scores are reported as they are; nothing here states physical realism."]
    rt = rep["runtime"]["per_video_s"]
    L += ["", f"## Runtime: per video (CPU, 961 frames) median {_fmt(rt.get('median'), 1)} s, max {_fmt(rt.get('max'), 1)} s "
          f"(n = {rt.get('n')}, includes decode, Farneback, search, hashing)", ""]
    return "\n".join(L)


def cmd_validate(args):
    os.makedirs(OUT_ROOT, exist_ok=True)
    man_path = f"{OUT_ROOT}/valset/manifest.json"
    if os.path.exists(man_path) and not args.rebuild:
        man = json.load(open(man_path))
        missing = [r for r in man["clips"] if not os.path.exists(f"{REPO}/{r['path']}")]
        if missing or man.get("n") != len(CLIP_NAMES) * len(VAL_SCENES) or man.get("transforms") != CLIP_NAMES:
            man = build_validation(jobs=args.jobs)
    else:
        man = build_validation(jobs=args.jobs)
    print(f"[validate] {man['n']} clips (build {man.get('seconds')} s)", flush=True)
    calib = calibrate(man)
    print(f"[validate] floor = {calib['floor']:.4f} (threshold {calib['threshold']:.3f}); floor_freeze = "
          f"{calib['floor_freeze']:.4f} (freeze threshold {calib['freeze_threshold']:.3f})", flush=True)
    floors = (calib["floor"], calib["floor_freeze"])
    jobs = [(f"{REPO}/{r['path']}", f"{MASK_ROOT}/{r['scene']}/labels.png", floors, tuple(args.features),
             dict(clip=r["clip"], scene=r["scene"], type=r["type"], cls=r["cls"]),
             f"{OUT_ROOT}/per_video/valset/{r['clip']}.json") for r in man["clips"]]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        docs = list(ex.map(_score_job, jobs))
    print(f"[validate] scored {len(docs)} clips in {time.time() - t0:.0f} s", flush=True)
    extra = {}
    if not args.no_native:
        for name, pat in NATIVE.items():
            vids = [(pat.format(sid=s), s) for s in DEV_SCENES if os.path.exists(pat.format(sid=s))]
            jl = [(v, f"{MASK_ROOT_DEV}/{s}/labels.png", floors, (), dict(sid=s, cell=name),
                   f"{OUT_ROOT}/per_video/{name}/{s}.json") for v, s in vids]
            with ProcessPoolExecutor(max_workers=args.jobs) as ex:
                extra[name] = list(ex.map(_score_job, jl))
            json.dump(dict(cell=name, floor=calib["floor"], module_sha256=module_sha(),
                           videos={d["meta"]["sid"]: dict(full=d["full"], late=d["late"], region=d["region"],
                                                          abstain_reason=d["abstain_reason"], seconds=d["seconds"]) for d in extra[name]}),
                      open(f"{OUT_ROOT}/scores_{name}.json", "w"), indent=1)
    rep = validation_report(docs, man, calib, extra)
    json.dump(_round(rep, 5), open(f"{OUT_ROOT}/validation_report.json", "w"), indent=1)
    open(f"{OUT_ROOT}/validation_report.md", "w").write(report_md(_round(rep, 5), man, calib))
    print(open(f"{OUT_ROOT}/validation_report.md").read())


def cmd_batch(args):
    os.makedirs(OUT_ROOT, exist_ok=True)
    floor, floor_freeze, src = load_floor()
    print(f"[batch] floor {floor:.4f} floor_freeze {floor_freeze:.4f} ({src})", flush=True)
    for cs in args.cells:
        t0 = time.time()
        if cs in NATIVE:
            vids = [(NATIVE[cs].format(sid=s), s, f"{MASK_ROOT_DEV}/{s}/labels.png") for s in DEV_SCENES]
            cell = cs
        else:
            cell = CELLS.get(cs, cs)
            d = SCORE_INPUTS.format(cell=cell)
            vids = [(p, os.path.basename(p)[:-4], f"{MASK_ROOT}/{os.path.basename(p)[:-4]}/labels.png")
                    for p in sorted(glob.glob(f"{d}/*.mp4"))]
        vids = [v for v in vids if os.path.exists(v[0])]
        jl = [(v, m, (floor, floor_freeze), tuple(args.features), dict(sid=s, cell=cell), f"{OUT_ROOT}/per_video/{cell}/{s}.json") for v, s, m in vids]
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            docs = list(ex.map(_score_job, jl))
        keys = ["exact_frac", "pp_frac", "pp_any_frac", "freeze_frac", "freeze_frac_spec", "periodic_frac", "R_ex_p10",
                "R_pp_p10", "F_p10", "cos_ex_p90", "exact_run_max_s", "lag_dominant_s", "sigma_median"]
        summ = {h: {k: _dist([d[h][k] for d in docs if d.get(h)]) for k in keys} for h in ("full", "late")}
        for h in ("full", "late"):
            summ[h]["n_scored"] = sum(1 for d in docs if d.get(h))
            summ[h]["n_abstain"] = sum(1 for d in docs if not d.get(h))
            for k in ("replay_suspect", "pingpong_suspect", "freeze_suspect"):
                summ[h][k] = [d["meta"]["sid"] for d in docs if d.get(h) and d[h][k]]
            summ[h]["by_category"] = {}
            for cat in sorted({CATEGORY.get(d["meta"]["sid"][:3], "dev") for d in docs}):
                dd = [d for d in docs if CATEGORY.get(d["meta"]["sid"][:3], "dev") == cat and d.get(h)]
                summ[h]["by_category"][cat] = {k: float(np.nanmean([_nz(d[h][k]) for d in dd])) if dd else None
                                               for k in ("exact_frac", "pp_frac", "freeze_frac", "periodic_frac", "R_ex_p10")}
        doc = dict(cell=cell, short=cs, floor=floor, floor_freeze=floor_freeze, floor_source=src, module_sha256=module_sha(), version=VERSION,
                   n=len(docs), seconds=round(time.time() - t0, 1),
                   per_video_seconds=_dist([d["seconds"] for d in docs]), summary=_round(summ, 4),
                   videos={d["meta"]["sid"]: dict(full=d["full"], late=d["late"], region=d["region"],
                                                  abstain_reason=d["abstain_reason"], video_sha256=d["video_sha256"],
                                                  seconds=d["seconds"]) for d in docs})
        json.dump(doc, open(f"{OUT_ROOT}/scores_{cs}.json", "w"), indent=1)
        f = summ["full"]
        print(f"[batch] {cs} ({cell}): n={len(docs)} in {doc['seconds']} s; exact_frac median {_fmt(f['exact_frac'].get('median'))} "
              f"max {_fmt(f['exact_frac'].get('max'))}; pp_frac max {_fmt(f['pp_frac'].get('max'))}; freeze_frac median "
              f"{_fmt(f['freeze_frac'].get('median'))} max {_fmt(f['freeze_frac'].get('max'))}; periodic_frac median "
              f"{_fmt(f['periodic_frac'].get('median'))}; suspects replay={f['replay_suspect']} pp={f['pingpong_suspect']} "
              f"freeze={f['freeze_suspect']}", flush=True)


def cmd_score(args):
    floor = args.floor
    d = _round(score_video(args.video, args.mask, floor, tuple(args.features), floor_freeze=args.floor_freeze))
    s = json.dumps(d if args.windows else {k: v for k, v in d.items() if k != "windows"}, indent=1)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        open(args.out, "w").write(json.dumps(d, indent=1))
        print(f"wrote {args.out}")
    else:
        print(s)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score", help="score one video -> JSON (replay / ping-pong / freeze / periodicity, per-window lags)")
    s.add_argument("video")
    s.add_argument("--mask", required=True, help="labels.png (label 2 = dynamic region)")
    s.add_argument("--out", default=None)
    s.add_argument("--floor", type=float, default=None, help="codec floor (default: calibration.json or provisional 1.0)")
    s.add_argument("--floor-freeze", type=float, default=None, help="held-segment floor (default: calibration.json or 0.01)")
    s.add_argument("--features", nargs="*", default=[], choices=["dino"])
    s.add_argument("--windows", action="store_true", help="print per-window records too (always in --out)")
    s.set_defaults(fn=cmd_score)
    v = sub.add_parser("validate", help="build the validation set, calibrate the floor, score, write the AUROC report")
    v.add_argument("--jobs", type=int, default=12)
    v.add_argument("--rebuild", action="store_true")
    v.add_argument("--no-native", action="store_true", help="skip the SVI / Helios other-generator videos")
    v.add_argument("--features", nargs="*", default=[], choices=["dino"])
    v.set_defaults(fn=cmd_validate)
    b = sub.add_parser("batch", help="score the seed-42 test videos of cells -> scores_<cell>.json")
    b.add_argument("--cells", nargs="+", required=True, help=f"short names {list(CELLS)} or {list(NATIVE)} or a cell directory name")
    b.add_argument("--jobs", type=int, default=12)
    b.add_argument("--features", nargs="*", default=[], choices=["dino"])
    b.set_defaults(fn=cmd_batch)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()

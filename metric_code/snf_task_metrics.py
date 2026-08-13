#!/usr/bin/env python
"""
SNF-Bench task-specific metrics for the Steady-Forcing rebuttal.

Computes, per video, the drift / stagnation quantities the reviewers requested,
as a RE-ANALYSIS of already-generated videos (no retraining):

  fBD  (feature-aligned Background Drift, %-of-diagonal, LOWER better)
        median displacement of ORB-matched STATIC-region keypoints,
        frame-0 vs. late-window frames. Camera is fixed -> any matched
        displacement of static structures is background drift.

  BFR  (Background Flow Ratio, x1000 of frame width per frame, LOWER better)
        mean RAFT optical-flow magnitude INSIDE the static mask, over the
        whole clip. Exposes drift that VBench mis-reads as Dynamic Degree.

  FP   (Flow Persistence, late/early, HIGHER better, ~1 = sustained)
        mean dynamic-region flow in the late window / early window.
        FP << 1 == motion stagnation ("pond effect").

Masks: the dynamic (fluid) region is identified from the EARLY window flow
(before drift accumulates) via Otsu; static = complement. This is what lets
us separate genuine fluid motion from drift-as-motion.

Usage (inside the infrope container):
  VBENCH_CACHE_DIR=/workspace/ckpt/vbench \
  python snf_task_metrics.py --videos_dir <dir> --out <json> --gpu 0
"""
import os, sys, glob, json, argparse
import numpy as np
import cv2
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
# Import RAFT directly (avoid vbench/__init__.py, which needs decord)
sys.path.insert(0, os.path.join(HERE, "vbench", "third_party", "RAFT"))
from core.raft import RAFT
from core.utils_core.utils import InputPadder
from easydict import EasyDict as edict

MAX_H = 288          # RAFT input height (native ~480 downscaled for speed)
SAMPLE_FPS = 8       # temporal sampling, matches dynamic_degree.py
WIN_FRAC = 0.12      # early / late window = first / last 12% of sampled pairs
MIN_WIN = 3


def load_raft(device):
    cache = os.environ.get("VBENCH_CACHE_DIR",
                           os.path.expanduser("~/.cache/vbench"))
    model_path = f"{cache}/raft_model/models/models/raft-things.pth"
    args = edict({"model": model_path, "small": False,
                  "mixed_precision": False, "alternate_corr": False})
    model = RAFT(args)
    ckpt = torch.load(model_path, map_location="cpu")
    model.load_state_dict({k.replace("module.", ""): v for k, v in ckpt.items()})
    model.to(device).eval()
    return model


def read_frames(path, device):
    """Return sampled frames as (tensor[1,3,H,W] float on device) list + gray uint8 list."""
    vid = cv2.VideoCapture(path)
    fps = vid.get(cv2.CAP_PROP_FPS) or 24.0
    interval = max(1, round(fps / SAMPLE_FPS))
    raw = []
    while vid.isOpened():
        ok, f = vid.read()
        if not ok:
            break
        raw.append(f)  # BGR
    vid.release()
    raw = raw[::interval]
    if len(raw) < 4:
        return None, None
    h, w = raw[0].shape[:2]
    scale = MAX_H / h
    nh, nw = MAX_H, int(round(w * scale))
    tens, grays = [], []
    for f in raw:
        f = cv2.resize(f, (nw, nh), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        t = torch.from_numpy(rgb.astype(np.uint8)).permute(2, 0, 1).float()[None].to(device)
        tens.append(t)
        grays.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
    return tens, grays


@torch.no_grad()
def flow_vec(model, a, b):
    padder = InputPadder(a.shape)
    a2, b2 = padder.pad(a, b)
    _, flow = model(a2, b2, iters=20, test_mode=True)
    return padder.unpad(flow)[0].permute(1, 2, 0).cpu().numpy()  # H,W,2


def flow_mag(model, a, b):
    f = flow_vec(model, a, b)
    return np.sqrt(f[..., 0] ** 2 + f[..., 1] ** 2)             # H,W


def build_masks(early_map):
    """early_map: mean flow magnitude over early window. Returns dynamic, static bool masks."""
    H, W = early_map.shape
    m = early_map / (early_map.max() + 1e-6)
    u8 = np.clip(m * 255, 0, 255).astype(np.uint8)
    thr, dyn = cv2.threshold(u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    dyn = dyn > 0
    # fallback: ensure dynamic region is non-trivial (>=3% pixels)
    if dyn.mean() < 0.03:
        k = np.percentile(early_map, 80)
        dyn = early_map >= max(k, 1e-6)
    # morphology cleanup
    kernel = np.ones((5, 5), np.uint8)
    dyn_u8 = cv2.morphologyEx(dyn.astype(np.uint8), cv2.MORPH_OPEN, kernel)
    dyn_u8 = cv2.morphologyEx(dyn_u8, cv2.MORPH_CLOSE, kernel)
    dyn = dyn_u8 > 0
    static = ~dyn
    # drop a 4% border from static (edge flow artifacts)
    bh, bw = int(H * 0.04), int(W * 0.04)
    border = np.zeros_like(static)
    border[bh:H - bh, bw:W - bw] = True
    static = static & border
    # erode static to avoid boundary bleed
    static = cv2.erode(static.astype(np.uint8), kernel).astype(bool)
    return dyn, static


def orb_drift(grays, static, late_idx):
    """Median displacement (% of diagonal) of ORB-matched static keypoints, frame0 vs late frames."""
    H, W = grays[0].shape
    diag = np.sqrt(H ** 2 + W ** 2)
    orb = cv2.ORB_create(nfeatures=1500)
    static_u8 = (static.astype(np.uint8)) * 255
    kp0, des0 = orb.detectAndCompute(grays[0], static_u8)
    if des0 is None or len(kp0) < 12:
        return None
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    disps = []
    for i in late_idx:
        kp1, des1 = orb.detectAndCompute(grays[i], static_u8)
        if des1 is None or len(kp1) < 12:
            continue
        matches = bf.match(des0, des1)
        if len(matches) < 12:
            continue
        pts0 = np.float32([kp0[m.queryIdx].pt for m in matches])
        pts1 = np.float32([kp1[m.trainIdx].pt for m in matches])
        # RANSAC homography to reject fluid/mismatch outliers, keep static inliers
        Hm, inl = cv2.findHomography(pts0, pts1, cv2.RANSAC, 3.0)
        if inl is None or inl.sum() < 8:
            d = np.linalg.norm(pts1 - pts0, axis=1)
        else:
            inl = inl.ravel().astype(bool)
            d = np.linalg.norm(pts1[inl] - pts0[inl], axis=1)
        disps.append(np.median(d))
    if not disps:
        return None
    return float(np.mean(disps) / diag * 100.0)


def process_video(model, path, device):
    tens, grays = read_frames(path, device)
    if tens is None:
        return None
    F = len(tens)
    win = max(MIN_WIN, int(F * WIN_FRAC))

    # ---- Pass A: early-window magnitude -> masks (before drift accumulates) ----
    early_maps = [flow_mag(model, tens[i], tens[i + 1]).astype(np.float32)
                  for i in range(min(win, F - 1))]
    early = np.mean(early_maps, 0)
    dyn, static = build_masks(early)
    Wpx = early.shape[1]

    # ---- Pass B: vector flow over all pairs -> drift-compensated scalars ----
    P = F - 1
    stat_mag = np.zeros(P)     # raw background flow (drift)
    dyn_raw = np.zeros(P)      # raw foreground flow (VBench-DD style, drift-contaminated)
    dyn_res = np.zeros(P)      # foreground flow AFTER removing background drift = true fluid motion
    for i in range(P):
        f = flow_vec(model, tens[i], tens[i + 1])
        mag = np.sqrt(f[..., 0] ** 2 + f[..., 1] ** 2)
        if static.sum() > 0:
            dvx = np.median(f[..., 0][static]); dvy = np.median(f[..., 1][static])
            stat_mag[i] = mag[static].mean()
        else:
            dvx = dvy = 0.0
        if dyn.sum() > 0:
            res = np.sqrt((f[..., 0] - dvx) ** 2 + (f[..., 1] - dvy) ** 2)
            dyn_raw[i] = mag[dyn].mean()
            dyn_res[i] = res[dyn].mean()

    # reference window skips the initial generation burst (10-20%), late = last 12%
    ref = dyn_res[win:2 * win].mean() if P >= 2 * win else dyn_res[:win].mean()
    late = dyn_res[-win:].mean()
    fp = min(float(late / (ref + 1e-6)), 2.0)          # drift-robust flow persistence

    bfr = float(stat_mag.mean() / Wpx * 1000.0)         # background flow (x1000 of width)
    # fraction of the raw dynamic-degree flow that is actually background drift (late window)
    drift_frac = float(stat_mag[-win:].mean() / (dyn_raw[-win:].mean() + 1e-6))

    late_idx = list(range(F - win, F))
    fbd = orb_drift(grays, static, late_idx)

    return {
        "video": os.path.basename(path),
        "fBD": fbd,                                  # background drift (ORB), % diag  (LOWER better)
        "BFR": bfr,                                  # background flow in static mask  (LOWER better)
        "FP": fp,                                    # drift-compensated flow persistence (HIGHER better)
        "MCFF_late": float(late),                    # true late fluid motion, drift-removed (px)
        "DD_raw_late": float(dyn_raw[-win:].mean()), # raw foreground flow, late (VBench-DD-like)
        "drift_frac_late": drift_frac,               # share of DD that is drift (HIGHER = motion is fake)
        "static_frac": float(static.mean()),
        "n_frames_sampled": F,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos_dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    device = "cuda"
    model = load_raft(device)
    vids = sorted(glob.glob(os.path.join(args.videos_dir, "*.mp4")))
    if args.limit:
        vids = vids[:args.limit]
    results = []
    for i, v in enumerate(vids):
        try:
            r = process_video(model, v, device)
        except Exception as e:
            r = {"video": os.path.basename(v), "error": repr(e)}
        if r:
            results.append(r)
        print(f"[{i+1}/{len(vids)}] {r.get('video','?')} "
              f"fBD={r.get('fBD')} BFR={r.get('BFR')} FP={r.get('FP')}", flush=True)

    def agg(key, fn):
        xs = [r[key] for r in results if r.get(key) is not None and "error" not in r]
        return float(fn(xs)) if xs else None
    summary = {
        "videos_dir": args.videos_dir,
        "n_videos": len(results),
        "fBD_mean": agg("fBD", np.mean), "fBD_median": agg("fBD", np.median),
        "BFR_mean": agg("BFR", np.mean), "BFR_median": agg("BFR", np.median),
        "FP_mean": agg("FP", np.mean),   "FP_median": agg("FP", np.median),
        "MCFF_late_mean": agg("MCFF_late", np.mean),
        "DD_raw_late_mean": agg("DD_raw_late", np.mean),
        "drift_frac_late_mean": agg("drift_frac_late", np.mean),
        "per_video": results,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n== {args.videos_dir} ==")
    print(f"fBD={summary['fBD_mean']}  BFR={summary['BFR_mean']}  FP={summary['FP_mean']}")


if __name__ == "__main__":
    main()

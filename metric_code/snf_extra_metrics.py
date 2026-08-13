#!/usr/bin/env python
"""Complementary task-specific metrics for fixed-camera nature-flow i2v, targeting the
failure modes we actually observe (blur, color/darkening drift, stagnation) that the
RAFT-based snf_task_metrics.py (fBD/BFR/FP) does not directly quantify.

cv2 + numpy ONLY (no torch / no model weights) -> runs anywhere, fast.

Per video (static/dynamic split from early-window frame-diff Otsu, camera is fixed):
  sharp_ratio   late/early Laplacian-variance sharpness   (LOWER = blur GROWS over time)
  sharp_mean    mean frame sharpness                        (HIGHER = sharper overall)
  dE_static     Lab color drift of static region, early->late (LOWER = color held)
  dL_static     lightness change late-early of static region (NEG = darkening "blackish")
  idPSNR_late   static-region PSNR frame0 vs late frames    (HIGHER = background identity held)
  FDP           dynamic frame-diff persistence late/early    (HIGHER~1 = motion sustained; <<1 stagnation)
  stag_onset    fraction of clip where dyn motion first < 0.5x early (1.0 = never stagnates)

    python scripts/snf_extra_metrics.py --videos_dir output/sweep/clean_4000 --out out.json
"""
import argparse
import glob
import json
import os

import cv2
import numpy as np

EARLY = 0.15          # early / late window = first / last 15% of frames
MAXF = 160            # cap sampled frames for speed
EPS = 1e-6


def read_frames(path):
    vid = cv2.VideoCapture(path)
    raw = []
    while True:
        ok, f = vid.read()
        if not ok:
            break
        raw.append(f)                       # BGR uint8
    vid.release()
    if len(raw) < 6:
        return None
    if len(raw) > MAXF:                     # uniform temporal subsample
        idx = np.linspace(0, len(raw) - 1, MAXF).round().astype(int)
        raw = [raw[i] for i in idx]
    return raw


def early_late(n):
    w = max(2, int(n * EARLY))
    return list(range(0, w)), list(range(n - w, n)), w


def build_masks(frames, early_idx):
    """dynamic = high frame-diff region in the early window (before drift); static = complement."""
    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames]
    diffs = [np.abs(grays[i + 1] - grays[i]) for i in early_idx if i + 1 < len(grays)]
    m = np.mean(diffs, 0) if diffs else np.zeros_like(grays[0])
    u8 = np.clip(m / (m.max() + EPS) * 255, 0, 255).astype(np.uint8)
    _, dyn = cv2.threshold(u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    dyn = dyn > 0
    if dyn.mean() < 0.03:
        dyn = m >= max(np.percentile(m, 80), EPS)
    k = np.ones((5, 5), np.uint8)
    dyn = cv2.morphologyEx(dyn.astype(np.uint8), cv2.MORPH_OPEN, k)
    dyn = cv2.morphologyEx(dyn, cv2.MORPH_CLOSE, k) > 0
    H, W = m.shape
    static = ~dyn
    border = np.zeros_like(static)
    bh, bw = int(H * 0.04), int(W * 0.04)
    border[bh:H - bh, bw:W - bw] = True
    static = cv2.erode((static & border).astype(np.uint8), k).astype(bool)
    return dyn, static


def process(path):
    frames = read_frames(path)
    if frames is None:
        return None
    n = len(frames)
    e_idx, l_idx, w = early_late(n)
    dyn, static = build_masks(frames, e_idx)
    if static.sum() < 50:
        static = np.ones(frames[0].shape[:2], bool)

    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    labs = [cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(np.float32) for f in frames]

    # --- sharpness (Laplacian variance) per frame ---
    sharp = np.array([cv2.Laplacian(g, cv2.CV_64F).var() for g in grays])
    s_early = sharp[e_idx].mean()
    s_late = sharp[l_idx].mean()
    sharp_ratio = float(s_late / (s_early + EPS))

    # --- color / darkening drift of the STATIC region (early window vs late window) ---
    def lab_mean(idx):
        return np.stack([labs[i][static] for i in idx]).reshape(-1, 3).mean(0)
    le, ll = lab_mean(e_idx), lab_mean(l_idx)
    dE_static = float(np.linalg.norm(ll - le))                     # Lab Euclidean (dE76)
    dL_static = float(ll[0] - le[0]) * (100.0 / 255.0)             # OpenCV L in [0,255] -> ~[0,100]

    # --- static-region identity: PSNR frame0 vs late frames ---
    g0 = grays[0].astype(np.float32) / 255.0
    sm = static
    psnrs = []
    for i in l_idx:
        gi = grays[i].astype(np.float32) / 255.0
        mse = ((g0[sm] - gi[sm]) ** 2).mean()
        psnrs.append(10 * np.log10(1.0 / max(mse, EPS)))
    idPSNR_late = float(np.mean(psnrs))

    # --- dynamic motion persistence (frame-diff based) + stagnation onset ---
    dyn_fd = np.array([np.abs(grays[i + 1].astype(np.float32) - grays[i].astype(np.float32))[dyn].mean()
                       if dyn.sum() > 0 else 0.0 for i in range(n - 1)])
    early_fd = dyn_fd[:w].mean()
    late_fd = dyn_fd[-w:].mean()
    FDP = float(min(late_fd / (early_fd + EPS), 2.0))
    below = np.where(dyn_fd < 0.5 * (early_fd + EPS))[0]
    stag_onset = float(below[0] / max(n - 1, 1)) if len(below) else 1.0

    return {
        "video": os.path.basename(path),
        "sharp_ratio": round(sharp_ratio, 3),
        "sharp_mean": round(float(sharp.mean()), 1),
        "dE_static": round(dE_static, 2),
        "dL_static": round(dL_static, 2),
        "idPSNR_late": round(idPSNR_late, 2),
        "FDP": round(FDP, 3),
        "stag_onset": round(stag_onset, 3),
        "static_frac": round(float(static.mean()), 3),
        "n_frames": n,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos_dir", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    vids = sorted(glob.glob(os.path.join(args.videos_dir, "*.mp4")))
    rows = []
    for i, v in enumerate(vids):
        try:
            r = process(v)
        except Exception as e:
            r = {"video": os.path.basename(v), "error": repr(e)}
        if r:
            rows.append(r)
            print(f"[{i+1}/{len(vids)}] {r.get('video','?')[:40]:40s} "
                  f"sharp_ratio={r.get('sharp_ratio')} sharp_mean={r.get('sharp_mean')} "
                  f"dE={r.get('dE_static')} dL={r.get('dL_static')} "
                  f"idPSNR={r.get('idPSNR_late')} FDP={r.get('FDP')} stag={r.get('stag_onset')}")

    keys = ["sharp_ratio", "sharp_mean", "dE_static", "dL_static", "idPSNR_late", "FDP", "stag_onset"]
    good = [r for r in rows if "error" not in r]
    agg = {k: round(float(np.mean([r[k] for r in good])), 3) for k in keys} if good else {}
    print("\n==== AGGREGATE (n=%d) ====" % len(good))
    for k in keys:
        print(f"  {k:12s} = {agg.get(k)}")
    print("  (sharp_ratio<1=blur grows; dE/dL small=color held (dL<0=darkening); "
          "idPSNR high=bg held; FDP~1=motion sustained; stag_onset 1.0=never stagnates)")
    if args.out:
        json.dump({"videos_dir": args.videos_dir, "aggregate": agg, "per_video": rows},
                  open(args.out, "w"), indent=2)
        print(f"[wrote] {args.out}")


if __name__ == "__main__":
    main()

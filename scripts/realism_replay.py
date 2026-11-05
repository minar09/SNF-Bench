#!/usr/bin/env python3
"""R4 replay candidates: does the dynamic region keep progressing, or replay, cut and freeze?

Plan: docs/SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md §2 (R4). CPU.
Window: the last WINDOW_S seconds, sampled at 8 fps, inside the eroded dynamic
role.

* `cand-recurrence-0` (incumbent, scripts/snf_candidates.py): appearance
  thumbnails. On generated videos it scored ~1 even without a loop
  (manifest/recurrence_controls_pilot_2026_10_30.json), because the static
  appearance dominates the correlation.
* `cand-recurrence-1`: the same sustained self-match at lag >= 2 s over a 1 s
  run, on the residual of each frame about the window's temporal median, so
  only what moves is compared. Abstains when the residual has no energy
  (a frozen region), which `activity` then reports.
* `cand-seam-0`: the largest successive-frame change in the window over its
  median, the signature of a cut.
* `activity`: median successive grey change, grey levels (diagnostic).

A scene whose eroded dynamic region is under MIN_PX abstains.

Natural periodic media (surf, flames, fountains) can recur legitimately; these
are separability tests against constructed controls, not loop verdicts.

    python scripts/realism_replay.py --videos <list.tsv> --controls <dir> \\
        --modes passthrough_crf18,loop_exact,... --label <cell> --out <json>
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths               # noqa: E402
import snf_candidates as C  # noqa: E402
import snf_sourceref as P   # noqa: E402
from pilot_support_realism import sha256, verify_chain  # noqa: E402

IDENTITY = {"recurrence_appearance": "cand-recurrence-0", "recurrence": "cand-recurrence-1",
            "seam": "cand-seam-0"}
WINDOW_S = 24
MIN_LAG_S, RUN_S = 2.0, 1.0
MIN_RESIDUAL = 0.5    # grey levels RMS; below it the region is treated as frozen
THUMB = (48, 27)
MIN_PX = 200


def window(path):
    frames, fps = C.read_sampled(path)
    n = int(round(WINDOW_S * fps))
    if len(frames) < n:
        raise ValueError(f"{len(frames)} sampled frames < {n}")
    return frames[-n:], fps


def thumbs(grey, dyn):
    ys, xs = np.nonzero(dyn)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    m = dyn[sl].astype(np.float32)
    return np.stack([cv2.resize(g[sl] * m, THUMB, interpolation=cv2.INTER_AREA).ravel() for g in grey])


def sustained_match(D, fps):
    """Max over lags >= MIN_LAG_S of the mean correlation over RUN_S consecutive frames (as cand-recurrence-0)."""
    D = D - D.mean(1, keepdims=True)
    D = D / np.maximum(np.linalg.norm(D, axis=1, keepdims=True), 1e-9)
    Cm, n = D @ D.T, len(D)
    k, Lmin = max(2, int(round(RUN_S * fps))), int(round(MIN_LAG_S * fps))
    best = (-1.0, None)
    for L in range(Lmin, n - k + 1):
        runs = np.convolve(np.diagonal(Cm, offset=-L), np.ones(k) / k, mode="valid")
        i = int(np.argmax(runs))
        if runs[i] > best[0]:
            best = (float(runs[i]), L / fps)
    return best


def measure(path, dyn):
    try:
        frames, fps = window(path)
    except ValueError as e:
        return {"abstain": str(e)}
    core = C.erode(dyn)
    if core.sum() < MIN_PX:
        return {"abstain": f"eroded dynamic region {int(core.sum())} px < {MIN_PX}"}
    grey = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames])
    steps = np.abs(np.diff(grey, axis=0))[:, core].mean(1)
    out = dict(fps=fps, frames=len(frames), activity=float(np.median(steps)),
               seam=float(steps.max() / max(np.median(steps), 1e-6)))
    a = C.recurrence(frames, core, fps_sampled=fps, min_lag_s=MIN_LAG_S, run_s=RUN_S)
    out["recurrence_appearance"] = a["score"]
    resid = grey - np.median(grey, axis=0)
    rms = float(np.sqrt((resid[:, core] ** 2).mean()))
    out["residual_rms"] = rms
    if rms < MIN_RESIDUAL:
        out["abstain"] = {"recurrence": f"residual RMS {rms:.2f} < {MIN_RESIDUAL}: frozen"}
    else:
        out["recurrence"], out["recurrence_lag_s"] = sustained_match(thumbs(resid, core), fps)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True)
    ap.add_argument("--controls", required=True)
    ap.add_argument("--modes", required=True, help="controls subdirectories, the pass-through first")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.exists(a.out):
        raise SystemExit(f"{a.out} exists; reports are never overwritten")
    masks = os.path.join(_paths.resolve("method_repo"), "results/factorial/source_masks")
    modes, rows = a.modes.split(","), []
    for line in open(a.videos):
        sid, video = line.rstrip("\n").split("\t")
        dyn, _, lsha, _ = P.load_role_masks(os.path.join(masks, sid, "labels.png"))
        chain = dict(parent_sha256=sha256(video), mask_labels_sha256=lsha,
                     source_sha256=sha256(os.path.join(_paths.ROOT, "prompts/v2/i2v/images", f"{sid}.jpg")))
        row = dict(scene=sid, chain=chain, controls={})
        for md in modes:
            path = f"{a.controls}/{md}/{sid}.mp4"
            verify_chain(path, chain)
            row["controls"][md] = dict(sha256=sha256(path), **measure(path, dyn))
        rows.append(row)
        print(sid, {md: row["controls"][md].get("recurrence") for md in modes}, flush=True)
    ref, summary = modes[0], {}
    for md in modes:
        summary[md] = {}
        for s in ("recurrence_appearance", "recurrence", "seam", "activity"):
            v = [r["controls"][md][s] for r in rows if r["controls"][md].get(s) is not None]
            summary[md][s] = dict(n=len(v), n_attempted=len(rows), median=float(np.median(v)) if v else None)
            p = [(r["controls"][ref][s], r["controls"][md][s]) for r in rows
                 if r["controls"][ref].get(s) is not None and r["controls"][md].get(s) is not None]
            if md != ref and p:
                x, y = np.array(p).T
                summary[md][s].update(n_paired=len(p), frac_control_above_reference=float(np.mean(y > x)))
    rep = dict(entrant=a.label, identity=IDENTITY, reference=ref, window_s=WINDOW_S, min_lag_s=MIN_LAG_S,
               run_s=RUN_S, min_residual=MIN_RESIDUAL, thumb=THUMB,
               caveat="development data (CF++ family); constructed controls only; no natural periodic negatives",
               summary=summary, rows=rows)
    json.dump(rep, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

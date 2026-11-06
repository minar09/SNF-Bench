#!/usr/bin/env python3
"""`cand-material-drift-0`: SceneTether's moving-region colour drift on SNF role maps (CPU).

Ported from ar-image-animation tools/analysis/h240_composite_endpoints_oct28.py
(`measure_video`, drift part; docs/171_ACCEPTANCE_PUSH_NOV03.md §1): the cv2 8-bit
Lab distance between a region's mean colour over a late window and over an
early window of the same video. The source fixes frames 25-48 and 640-959 at
16 fps; here the windows are in seconds, so entrants at 15 or 24 fps compare
like with like: early [EARLY_S), late = the last LATE_FRAC of the clip. Regions
are the SNF role maps (material = label 2, support = label 1), not SceneTether's
own frozen map. This is Euclidean distance in OpenCV's 8-bit encoded Lab space,
not CIEDE2000 or standard Delta E 76; report support and material separately.
The historical delta field is retained for reproducibility, but is confounded by
support changes and does not isolate material-specific drift. Lower drift is
colour stability, not realism.

    python scripts/realism_drift.py --videos <list.tsv> --controls <dir> --modes passthrough_crf18,... --out <json>
"""
import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths                   # noqa: E402
import snf_sourceref as P       # noqa: E402

IDENTITY = "cand-material-drift-0"
EARLY_S = (1.5, 3.0)            # source: frames 25-48 at 16 fps
LATE_FRAC = 1 / 3               # source: 40-60 s of a 60 s clip
MIN_PX = 50


def region_means(path, masks):
    """Per-frame mean Lab of each mask, and the frame rate."""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 16.0
    out = {k: [] for k in masks}
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if f.shape[:2] != next(iter(masks.values())).shape:
            f = cv2.resize(f, next(iter(masks.values())).shape[::-1], interpolation=cv2.INTER_AREA)
        L = cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(np.float32)
        for k, m in masks.items():
            out[k].append(L[m].mean(0))
    cap.release()
    return {k: np.array(v) for k, v in out.items()}, fps


def drift(means, fps):
    n = len(next(iter(means.values())))
    e0, e1 = int(round(EARLY_S[0] * fps)), int(round(EARLY_S[1] * fps))
    l0 = int(round(n * (1 - LATE_FRAC)))
    if e1 >= l0:
        return dict(identity=IDENTITY, abstain=f"clip of {n} frames too short for the windows")
    d = {k: float(np.linalg.norm(v[l0:].mean(0) - v[e0:e1].mean(0))) for k, v in means.items()}
    return dict(identity=IDENTITY, drift_material=d["material"], drift_support=d["support"],
                delta=d["material"] - d["support"], frames=n, fps=fps, early=[e0, e1], late=[l0, n])


def task(args):
    sid, md, path, labels = args
    dyn, sup, lsha, _ = P.load_role_masks(labels)
    if dyn.sum() < MIN_PX or sup.sum() < MIN_PX:
        return sid, md, dict(identity=IDENTITY, abstain="material or support under 50 px")
    means, fps = region_means(path, dict(material=dyn, support=sup))
    return sid, md, dict(**drift(means, fps), mask_labels_sha256=lsha)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True)
    ap.add_argument("--controls", required=True)
    ap.add_argument("--modes", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if os.path.exists(a.out):
        raise SystemExit(f"{a.out} exists; reports are never overwritten")
    from pilot_support_realism import sha256
    masks = os.path.join(_paths.resolve("method_repo"), "results/factorial/source_masks")
    modes = a.modes.split(",")
    jobs = [(sid, md, f"{a.controls}/{md}/{sid}.mp4", os.path.join(masks, sid, "labels.png"))
            for sid in [line.split("\t")[0] for line in open(a.videos)] for md in modes]
    jobs = [j for j in jobs if os.path.exists(j[2])]
    rows = {}
    with ProcessPoolExecutor(a.workers) as ex:
        for sid, md, res in ex.map(task, jobs):
            rows.setdefault(sid, dict(scene=sid, controls={}))["controls"][md] = res
            print(sid, md, {k: round(v, 2) for k, v in res.items() if isinstance(v, float)}, flush=True)
    for sid, md, path, _ in jobs:
        rows[sid]["controls"][md]["sha256"] = sha256(path)
    summary = {}
    for md in modes:
        v = [r["controls"][md] for r in rows.values() if md in r["controls"] and "abstain" not in r["controls"][md]]
        summary[md] = {k: float(np.median([x[k] for x in v])) if v else None
                       for k in ("drift_material", "drift_support", "delta")} | dict(n=len(v))
    rep = dict(entrant=a.label, identity=IDENTITY, early_s=EARLY_S, late_frac=LATE_FRAC,
               source="ar-image-animation tools/analysis/h240_composite_endpoints_oct28.py measure_video (drift)",
               caveat="development data; lower drift is colour stability, not realism",
               summary=summary, rows=[rows[k] for k in sorted(rows)])
    json.dump(rep, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

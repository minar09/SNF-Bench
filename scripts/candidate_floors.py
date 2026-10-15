#!/usr/bin/env python3
"""Floors of the candidate measurements on clips where nothing happens.

Each v2 source image is encoded as a 10 s static video with the generators' own
writer (`torchvision.io.write_video(fps=16)`, libx264 defaults, run inside the
generation image). Nothing moves, nothing drifts, so any value a measurement
reports on these clips is codec, mask-edge or measurement floor -- the
baseline every real score must clear before it means anything. This is the
"control mask edges, codec and resize effects" item of step 2 in
docs/I2V_METRIC_REVIEW_2026_10_08.md, and the colour/activity half of the
zero-motion floor the spec lists as open (the RAFT half, for MCFF, needs a GPU
pass).

Reads only method-independent inputs: the frozen v2 source images and the
shared role masks. No method output is read, so the floors cannot be tuned to
any arm.

    python scripts/candidate_floors.py --clips <dir of <id>.mp4> --masks <source_masks dir>
"""

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths               # noqa: E402
import snf_candidates as C  # noqa: E402
import snf_sourceref as P   # noqa: E402

ROOT = _paths.ROOT
OUT = os.path.join(ROOT, "manifest", "candidate_floors.json")


def q(xs, p):
    xs = [x for x in xs if x is not None]
    return float(np.percentile(xs, p)) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", required=True)
    ap.add_argument("--masks", default=None)
    a = ap.parse_args()
    masks = a.masks or os.path.join(_paths.resolve("method_repo"), "results/factorial/source_masks")
    manifest_sha = hashlib.sha256(open(os.path.join(masks, "MANIFEST.json"), "rb").read()).hexdigest()
    pairs = json.load(open(os.path.join(ROOT, "manifest/i2v_pairs_v2.json")))["pairs"]
    split = json.load(open(os.path.join(ROOT, "manifest/v2_splits.json")))

    rows = []
    for p in pairs:
        sid = p["id"]
        clip = os.path.join(a.clips, f"{sid}.mp4")
        labels = os.path.join(masks, sid, "labels.png")
        src_p = os.path.join(ROOT, "prompts/v2/i2v/images", f"{sid}.jpg")
        if not (os.path.exists(clip) and os.path.exists(labels)):
            rows.append(dict(id=sid, status="missing input")); continue
        dyn, sup, _, regions = P.load_role_masks(labels)
        src = cv2.imread(src_p)
        frames, fps = C.read_sampled(clip)
        r = dict(id=sid, category=p["category"], split="test" if sid in split["test"] else "seen_overlap",
                 n_frames=len(frames), support_frac=regions["support"], dynamic_frac=regions["dynamic"])
        for e in (0, C.ERODE_PX):
            d = C.support_de00(frames, src, sup, erode_px=e)
            r[f"de00_mean_e{e}"] = None if d is None else float(np.mean(d["mean"]))
            r[f"de00_p90_e{e}"] = None if d is None else float(np.max(d["p90"]))
        m = C.material_detail_activity(frames, src, dyn, fps_sampled=fps)
        if m:
            r.update(detail_ratio_src=float(np.median(m["detail_ratio_src"])),
                     activity_mean=float(np.mean(m["activity"][1:])),
                     activity_max=float(np.max(m["activity"][1:])), n_tiles=m["n_tiles"])
        rc = C.recurrence(frames, dyn, fps_sampled=fps)
        r["recurrence"] = None if not rc else rc.get("score")
        if sup.sum() >= 50:
            ex = P.extras_sourcefixed(clip, dyn, sup, src)
            r.update(sf_dE_static_src=ex.get("dE_static_src"), sf_idPSNR_late_src=ex.get("idPSNR_late_src"))
        r["status"] = "ok"
        rows.append(r)
        print(f"{sid:<6} dE00 {r.get('de00_mean_e6')}  detail {r.get('detail_ratio_src')}  "
              f"act {r.get('activity_mean')}  rec {r.get('recurrence')}", flush=True)

    ok = [r for r in rows if r.get("status") == "ok"]
    keys = ["de00_mean_e0", "de00_mean_e6", "de00_p90_e0", "de00_p90_e6", "detail_ratio_src",
            "activity_mean", "activity_max", "recurrence", "sf_dE_static_src", "sf_idPSNR_late_src"]
    summary = {k: dict(median=q([r.get(k) for r in ok], 50), p95=q([r.get(k) for r in ok], 95),
                       max=q([r.get(k) for r in ok], 100),
                       n=sum(1 for r in ok if r.get(k) is not None)) for k in keys}
    by_cat = defaultdict(dict)
    for k in ("de00_mean_e6", "activity_mean", "detail_ratio_src"):
        cats = defaultdict(list)
        for r in ok:
            cats[r["category"]].append(r.get(k))
        for c, xs in cats.items():
            by_cat[c][k] = q(xs, 50)
    rep = dict(role="floors on static clips (codec + mask edge + measurement), method-independent",
               encoder="torchvision.io.write_video(fps=16) in regfor:cuda12.1 (libx264 defaults, yuv420p)",
               clip_seconds=10, mask_manifest_sha256=manifest_sha, mask_review_scope="ai",
               n=len(ok), summary=summary, by_category=dict(by_cat), rows=rows)
    json.dump(rep, open(OUT, "w"), indent=1)
    print(f"\n{len(ok)} clips -> {os.path.relpath(OUT, ROOT)}")
    for k, v in summary.items():
        print(f"  {k:<20} median {v['median']}  p95 {v['p95']}  (n={v['n']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

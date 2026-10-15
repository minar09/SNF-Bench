#!/usr/bin/env python3
"""Does a mean-colour advantage survive pixelwise? Region-mean dE vs pixelwise CIEDE2000.

`dE_static` compares the *mean* colour of the support region with the source.
It is blind to content that is redrawn with the right average colour: an
equal-mean texture swap scores ~0 (tests/test_candidates.py). A method can
therefore show lower `dE_static` and lower source PSNR at once either because
colour is genuinely held, or because pixels changed while the mean did not.

Pixelwise CIEDE2000 (`snf_candidates.support_de00`, float64, eroded support,
validated against the formula authors' test pairs) separates the two. This
computes it on the same late window `dE_static` uses (the last 12% of the
uniformly subsampled frames, as `snf_extra_metrics.early_late`), for a target
cell against reference cells, both seeds pooled per scene, precipitation
excluded. Candidate measurement `cand-support-de00-0`; read-only.

    python scripts/audit_pixelwise_colour.py --target cfpp/<cell> --ref cfpp/<cell> ...
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
from audit_de_precision import boot_ci  # noqa: E402

ROOT = _paths.ROOT
OUT = os.path.join(ROOT, "manifest", "pixelwise_colour_audit.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--ref", action="append", required=True)
    ap.add_argument("--seeds", default="42,1042")
    a = ap.parse_args()
    method = _paths.resolve("method_repo")
    masks = os.path.join(method, "results/factorial/source_masks")
    _, _, E = P.snf_modules()
    pairs = json.load(open(os.path.join(ROOT, "manifest/i2v_pairs_v2.json")))["pairs"]
    seeds = a.seeds.split(",")
    cache = {}

    def late_de00(cell, seed, sid, sup, src, lsha):
        k = (cell, seed, sid)
        if k in cache:
            return cache[k]
        rp = os.path.join(method, "results/factorial/scores", cell, f"seed{seed}",
                          "sourcefixed_60s/staging", f"{sid}.json")
        if not os.path.exists(rp):
            cache[k] = None; return None
        rec = json.load(open(rp))
        if (rec.get("mask_sha256") or {}).get("labels") != lsha:
            cache[k] = None; return None
        fr = E.read_frames(rec["video_path"].replace("/workspace/", "/home/minar/"))
        _, l_idx, _ = E.early_late(len(fr))
        r = C.support_de00([fr[i] for i in l_idx], src, sup)
        cache[k] = None if r is None else (float(np.mean(r["mean"])), float(np.mean(r["p90"])),
                                          rec.get("dE_static"))
        return cache[k]

    out = {r: dict(mean=[], p90=[], dE_static=[], scenes=[]) for r in a.ref}
    for p in pairs:
        sid = p["id"]
        if p["category"] == "falling_precip":
            continue
        _, sup, lsha, _ = P.load_role_masks(os.path.join(masks, sid, "labels.png"))
        src = cv2.imread(os.path.join(ROOT, "prompts/v2/i2v/images", f"{sid}.jpg"))
        for r in a.ref:
            dm, dp, dd = [], [], []
            for s in seeds:
                t, b = late_de00(a.target, s, sid, sup, src, lsha), late_de00(r, s, sid, sup, src, lsha)
                if t and b:
                    dm.append(t[0] - b[0]); dp.append(t[1] - b[1])
                    if t[2] is not None and b[2] is not None:
                        dd.append(t[2] - b[2])
            if dm:
                out[r]["mean"].append(float(np.mean(dm)))
                out[r]["p90"].append(float(np.mean(dp)))
                out[r]["dE_static"].append(float(np.mean(dd)) if dd else np.nan)
                out[r]["scenes"].append(sid)
        print(f"{sid} done", flush=True)

    rep = dict(target=a.target, seeds=seeds, identity=C.IDENTITY["support_de00"],
               contrasts={r: dict(n_scenes=len(v["scenes"]),
                                  pixelwise_de00_mean=boot_ci(v["mean"]),
                                  pixelwise_de00_p90=boot_ci(v["p90"]),
                                  region_mean_dE_static=boot_ci([x for x in v["dE_static"] if x == x]),
                                  sign_agreement=float(np.mean(np.sign(v["mean"]) == np.sign(
                                      [x if x == x else 0 for x in v["dE_static"]]))))
                          for r, v in out.items()})
    json.dump(rep, open(OUT, "w"), indent=1)
    print()
    for r, c in rep["contrasts"].items():
        m, q, d = c["pixelwise_de00_mean"], c["pixelwise_de00_p90"], c["region_mean_dE_static"]
        print(f"vs {r:<38} n={c['n_scenes']}  region-mean dE {d[0]:+.2f} [{d[1]:+.2f},{d[2]:+.2f}]"
              f"  | pixelwise dE00 mean {m[0]:+.2f} [{m[1]:+.2f},{m[2]:+.2f}]"
              f"  p90 {q[0]:+.2f} [{q[1]:+.2f},{q[2]:+.2f}]  sign agree {c['sign_agreement']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

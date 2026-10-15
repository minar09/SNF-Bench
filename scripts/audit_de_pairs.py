#!/usr/bin/env python3
"""Float32 vs float64 `dE_static` for named method-project contrasts, both seeds pooled.

`audit_de_precision.py` showed the float32 accumulation defect in `dE_static`
barely moves the Echo-vs-sink interaction. Headline colour claims made with the
same measure against other references (e.g. "-5.54 vs spatial Echo k = 3")
were not covered by that audit. This recomputes them.

For each scene: dE per (cell, seed) in float32 (must equal the stored record)
and float64; a per-seed difference target - reference; then the scene mean
over seeds, because a scene is one cluster. Scenes are bootstrapped. Scenes
whose mask declares a static abstention (precipitation) are excluded, matching
the method project's corrected eligibility. Read-only; writes
manifest/de_pairs_audit.json.

    python scripts/audit_de_pairs.py --target cfpp/<cell> --ref cfpp/<cell> [--ref ...]
"""

import argparse
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths              # noqa: E402
import snf_sourceref as P  # noqa: E402
from audit_de_precision import boot_ci, de_both  # noqa: E402

ROOT = _paths.ROOT
OUT = os.path.join(ROOT, "manifest", "de_pairs_audit.json")


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
    cells = [a.target] + a.ref

    cache, mism = {}, []

    def de(cell, seed, sid, sup, src, lsha):
        k = (cell, seed, sid)
        if k in cache:
            return cache[k]
        rp = os.path.join(method, "results/factorial/scores", cell, f"seed{seed}",
                          "sourcefixed_60s/staging", f"{sid}.json")
        if not os.path.exists(rp):
            cache[k] = None; return None
        rec = json.load(open(rp))
        if (rec.get("mask_sha256") or {}).get("labels") != lsha or rec.get("dE_static") is None:
            cache[k] = None; return None
        f32, f64 = de_both(rec["video_path"].replace("/workspace/", "/home/minar/"), sup, src, E)
        if abs(f32 - rec["dE_static"]) > 1e-4:
            mism.append((cell, seed, sid, f32, rec["dE_static"]))
        cache[k] = (f32, f64)
        return cache[k]

    per_ref = {r: {"f32": [], "f64": []} for r in a.ref}
    used = {r: [] for r in a.ref}
    for p in pairs:
        sid = p["id"]
        if p["category"] == "falling_precip":          # declared static abstention
            continue
        _, sup, lsha, _ = P.load_role_masks(os.path.join(masks, sid, "labels.png"))
        if sup.sum() < 50:
            continue
        src = cv2.imread(os.path.join(ROOT, "prompts/v2/i2v/images", f"{sid}.jpg"))
        for r in a.ref:
            d32, d64 = [], []
            for s in seeds:
                t, b = de(a.target, s, sid, sup, src, lsha), de(r, s, sid, sup, src, lsha)
                if t and b:
                    d32.append(t[0] - b[0]); d64.append(t[1] - b[1])
            if d32:
                per_ref[r]["f32"].append(float(np.mean(d32)))
                per_ref[r]["f64"].append(float(np.mean(d64)))
                used[r].append(sid)
        print(f"{sid} done", flush=True)

    rep = dict(target=a.target, seeds=seeds, reproduces_stored=not mism, mismatches=mism[:10],
               contrasts={r: dict(n_scenes=len(used[r]), f32=boot_ci(v["f32"]), f64=boot_ci(v["f64"]))
                          for r, v in per_ref.items()})
    json.dump(rep, open(OUT, "w"), indent=1)
    print(f"\nreproduces stored dE_static exactly: {rep['reproduces_stored']} ({len(mism)} mismatches)")
    for r, c in rep["contrasts"].items():
        f32, f64 = c["f32"], c["f64"]
        print(f"vs {r:<40} n={c['n_scenes']}  f32 {f32[0]:+.2f} [{f32[1]:+.2f}, {f32[2]:+.2f}]"
              f"   f64 {f64[0]:+.2f} [{f64[1]:+.2f}, {f64[2]:+.2f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

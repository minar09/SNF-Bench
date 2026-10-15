#!/usr/bin/env python3
"""Are the fresh confirmation sources independent of the test split and of training?

The method project froze 24 "fresh" I2V sources (2026-10-07) as its strongest
protection against adaptive conclusions. They were drawn from the same
candidate pool as the 48 v2 test pairs, and that pool holds several photographs
of the *same physical scene* (for example, more than one view of one town
weir). A second photograph of a test scene passes every hash check while not
being an independent source. This uses the same three tests as
`audit_v2_split.py` -- exact bytes, perceptual hash on two crops, and ORB+RANSAC
geometric verification, which matches a different crop or rescale of the same
scene -- against:

  * the 48 v2 test sources (crops and originals);
  * every training, development, held-out, v1-evaluation and supplementary pool.

Read-only. Writes manifest/fresh_split_audit.json.
"""

import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths                      # noqa: E402
import audit_v2_split as A         # noqa: E402

ROOT = _paths.ROOT
OUT = os.path.join(ROOT, "manifest", "fresh_split_audit.json")


def main():
    method = _paths.resolve("method_repo")
    frozen = json.load(open(os.path.join(method, "results/fresh_sources/FRESH_SPLIT_FROZEN.json")))
    fresh = frozen["pairs"]

    seen = []
    for key, pat, role in A.POOLS:
        base = _paths.resolve(key, required=False)
        for p in sorted(glob.glob(os.path.join(base, pat))) if base else []:
            if p.lower().endswith(A.EXT) and os.path.isfile(p):
                seen.append((p, role, f"{key}:{os.path.relpath(p, base)}"))
    v2 = json.load(open(os.path.join(ROOT, "manifest/i2v_pairs_v2.json")))["pairs"]
    alias = json.load(open(os.path.join(ROOT, "manifest/i2v_pair_sources.json")))
    pools = {"v2_extra": "prompts/v2/v2_images_extra", "v1": "prompts/v1/i2v/60s/images",
             "commons": "prompts/v2/v2_images_commons"}
    for pr in v2:
        seen.append((os.path.join(ROOT, pr["image"]), "v2 test split (crop)", f"v2:{pr['id']}"))
        sf = alias.get(pr["id"], pr["source_file"]) if pr["pool"] == "v2_extra" else pr["source_file"]
        so = os.path.join(ROOT, pools[pr["pool"]], sf)
        if os.path.exists(so):
            seen.append((so, "v2 test split (original)", f"v2:{pr['id']}"))
    print(f"comparison pool: {len(seen)} images")

    desc, shas = [], {}
    for p, role, label in seen:
        img = A.load(p)
        if img is None:
            continue
        desc.append((label, role, A.describe(img), p))
        shas.setdefault(hashlib.sha256(open(p, "rb").read()).hexdigest(), []).append((label, role))

    rows = []
    for f in fresh:
        crop = os.path.join(method, f["image"])
        src = os.path.join(ROOT, "prompts/v2/v2_images_extra", f.get("source_file", ""))
        views = [(n, A.load(p)) for n, p in (("source", src), ("crop", crop)) if os.path.exists(p)]
        hits, cand = [], []
        for n, img in views:
            for label, role in shas.get(hashlib.sha256(open(src if n == "source" else crop, "rb").read()).hexdigest(), []):
                hits.append(dict(test="exact", match=label, role=role))
            d = A.describe(img)
            for label, role, sd, sp in desc:
                cand.append((min(A.ham(d[x], sd[y]) for x in d for y in sd), label, role, sp))
        cand.sort(key=lambda c: c[0])
        hits += [dict(test="phash", match=l, role=r, bits=b) for b, l, r, _ in cand if b <= A.PHASH_MAX]
        ref = A.orb(views[0][1]) if views else None
        checked = set()
        for b, label, role, sp in cand:
            if ref is None or label in checked or len(checked) >= A.TOPK:
                continue
            checked.add(label)
            n = A.inliers(ref, A.orb(A.load(sp)))
            if n >= A.MIN_INLIERS:
                hits.append(dict(test="geometric", match=label, role=role, inliers=n, bits=b))
        rows.append(dict(id=f["id"], category=f["category"], source_file=f.get("source_file"),
                         verdict="seen" if hits else "unseen",
                         matches=sorted({h["match"] for h in hits}),
                         roles=sorted({h["role"] for h in hits}), evidence=hits[:6],
                         nearest_bits=cand[0][0] if cand else None,
                         nearest=cand[0][1] if cand else None))
        r = rows[-1]
        print(f"{r['id']:<6} {r['verdict']:<7} {r['roles'] or ''} nearest {r['nearest']} ({r['nearest_bits']} bits)",
              flush=True)

    out = dict(n=len(rows), n_unseen=sum(r["verdict"] == "unseen" for r in rows),
               fresh_manifest_sha256=frozen.get("manifest_sha256"),
               thresholds=dict(phash_bits=A.PHASH_MAX, orb_inliers=A.MIN_INLIERS, candidates=A.TOPK),
               rows=rows)
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"\nfresh sources: {out['n']}   unseen {out['n_unseen']}   seen {out['n'] - out['n_unseen']}"
          f"   -> {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

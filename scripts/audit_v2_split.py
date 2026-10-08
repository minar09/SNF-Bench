#!/usr/bin/env python3
"""Is each v2 I2V source genuinely unseen by the method being evaluated?

A method project has declared the 48 v2 I2V pairs its CVPR test split. That is
only meaningful if none of those images was used to train, tune or select the
method. Two facts make the check necessary rather than ceremonial:

* v2 reuses 7 images from the v1 evaluation set, and the v1 set was the
  development set for months of method work.
* The method's own notes record that five v1 `eval/60s` images duplicate its
  training images -- found by md5, with a perceptual screen "still required".

This compares each v2 source against every image the method project and the
v1 generation repository hold (prompt trees: training, development, critic
held-out, supplementary, v1 evaluation). Three tests, in increasing tolerance:

  exact     identical bytes
  phash     64-bit DCT hash within PHASH_MAX bits, on the whole image and on a
            centred 16:9 window (v2 crops are 16:9 windows of an original)
  geometric ORB + RANSAC homography with >= MIN_INLIERS inliers against the
            nearest perceptual candidates -- catches a different crop or
            rescale of the same photograph, which a global hash misses

Reads only. Output: manifest/v2_split_audit.json.

    python scripts/audit_v2_split.py
"""

import glob
import hashlib
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths                # noqa: E402
import screen_i2v_images     # noqa: E402  (AVIF-capable decoder)

ROOT = _paths.ROOT
OUT = os.path.join(ROOT, "manifest", "v2_split_audit.json")
EXT = (".jpg", ".jpeg", ".png", ".webp", ".avif")
PHASH_MAX = 10
MIN_INLIERS = 40
TOPK = 4

# Pools, as (repo key, glob relative to that repo, role). Roles are the
# method's own vocabulary; anything matched is not unseen whatever its role.
POOLS = [
    ("method_repo", "prompts/train/images/*", "training"),
    ("method_repo", "prompts/i2v/sk_flood_etc/3-2/*", "development (7 scenes)"),
    ("method_repo", "prompts/i2v/rf_test/3-2/*", "development probe"),
    ("method_repo", "prompts/i2v/seed_probe/3-2/*", "development probe"),
    ("method_repo", "prompts/eval/*/16-9/*", "v1 evaluation (used for development)"),
    ("method_repo", "prompts/supp/16-9/*", "supplementary"),
    ("i2v_source_repo", "prompts/train/images/*", "training"),
    ("i2v_source_repo", "prompts/i2v/*/3-2/*", "development probe"),
    ("i2v_source_repo", "prompts/eval/*/16-9/*", "v1 evaluation (used for development)"),
    ("i2v_source_repo", "prompts/supp/16-9/*", "supplementary"),
]


def load(path):
    return screen_i2v_images.decode(path, open(path, "rb").read())


def phash(gray):
    g = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32)
    d = cv2.dct(g)[:8, :8]
    return np.packbits((d > np.median(d)).flatten())


def centre169(img):
    h, w = img.shape[:2]
    cw, ch = min(w, round(h * 16 / 9)), min(h, round(w * 9 / 16))
    x, y = (w - cw) // 2, (h - ch) // 2
    return img[y:y + ch, x:x + cw]


def ham(a, b):
    return int(np.unpackbits(np.bitwise_xor(a, b)).sum())


def describe(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return {"full": phash(g),
            "c169": phash(cv2.cvtColor(centre169(img), cv2.COLOR_BGR2GRAY))}


_orb = cv2.ORB_create(nfeatures=2000)
_bf = cv2.BFMatcher(cv2.NORM_HAMMING)


def orb(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    s = 640 / max(g.shape)
    if s < 1:
        g = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    return _orb.detectAndCompute(g, None)


def inliers(a, b):
    (ka, da), (kb, db) = a, b
    if da is None or db is None or len(ka) < 10 or len(kb) < 10:
        return 0
    good = [m for m, n in (p for p in _bf.knnMatch(da, db, k=2) if len(p) == 2)
            if m.distance < 0.75 * n.distance]
    if len(good) < 10:
        return 0
    src = np.float32([ka[m.queryIdx].pt for m in good])
    dst = np.float32([kb[m.trainIdx].pt for m in good])
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    return int(mask.sum()) if mask is not None else 0


def main():
    pairs = json.load(open(os.path.join(ROOT, "manifest/i2v_pairs_v2.json")))["pairs"]
    pools = {"v2_extra": os.path.join(ROOT, "prompts/v2/v2_images_extra"),
             "v1": os.path.join(ROOT, "prompts/v1/i2v/60s/images"),
             "commons": os.path.join(ROOT, "prompts/v2/v2_images_commons")}
    alias = json.load(open(os.path.join(ROOT, "manifest/i2v_pair_sources.json")))

    seen, missing_roots = [], []
    for key, pat, role in POOLS:
        base = _paths.resolve(key, required=False)
        if not base:
            missing_roots.append(key)
            continue
        for p in sorted(glob.glob(os.path.join(base, pat))):
            if p.lower().endswith(EXT) and os.path.isfile(p):
                seen.append((p, role, f"{key}:{os.path.relpath(p, base)}"))
    print(f"seen pool: {len(seen)} images"
          + (f" (unconfigured: {missing_roots})" if missing_roots else ""))

    seen_desc, seen_sha = [], {}
    for p, role, label in seen:
        img = load(p)
        if img is None:
            continue
        seen_desc.append((label, role, describe(img), p))
        seen_sha.setdefault(hashlib.sha256(open(p, "rb").read()).hexdigest(), []).append((label, role))

    rows = []
    for pr in pairs:
        pid, pool = pr["id"], pr["pool"]
        src = os.path.join(pools[pool], alias.get(pid, pr["source_file"]) if pool == "v2_extra"
                           else pr["source_file"])
        crop = os.path.join(ROOT, pr["image"])
        views = [("source", load(src)), ("crop", load(crop))]
        hits = []
        # exact
        for f in (src, crop):
            if os.path.exists(f):
                for label, role in seen_sha.get(hashlib.sha256(open(f, "rb").read()).hexdigest(), []):
                    hits.append({"test": "exact", "match": label, "role": role})
        # perceptual, both views against both seen views
        cand = []
        for vname, img in views:
            if img is None:
                continue
            d = describe(img)
            for label, role, sd, sp in seen_desc:
                dist = min(ham(d[a], sd[b]) for a in d for b in sd)
                cand.append((dist, label, role, sp, vname))
        cand.sort(key=lambda c: c[0])
        for dist, label, role, sp, vname in cand:
            if dist > PHASH_MAX:
                break
            hits.append({"test": "phash", "match": label, "role": role,
                         "bits": dist, "view": vname})
        # geometric verification against the nearest distinct candidates
        src_orb = orb(views[0][1]) if views[0][1] is not None else None
        checked = set()
        for dist, label, role, sp, vname in cand:
            if label in checked or len(checked) >= TOPK or src_orb is None:
                continue
            checked.add(label)
            n = inliers(src_orb, orb(load(sp)))
            if n >= MIN_INLIERS:
                hits.append({"test": "geometric", "match": label, "role": role,
                             "inliers": n, "bits": dist})
        uniq = {(h["match"], h["role"]) for h in hits}
        rows.append({"id": pid, "category": pr["category"], "pool": pool,
                     "source_file": pr["source_file"],
                     "verdict": "seen" if uniq else "unseen",
                     "matches": sorted({h["match"] for h in hits}),
                     "roles": sorted({h["role"] for h in hits}),
                     "evidence": hits[:6],
                     "nearest_bits": cand[0][0] if cand else None})

    seen_rows = [r for r in rows if r["verdict"] == "seen"]
    out = {"n": len(rows), "n_unseen": len(rows) - len(seen_rows),
           "n_seen": len(seen_rows), "seen_pool_size": len(seen_desc),
           "thresholds": {"phash_bits": PHASH_MAX, "orb_inliers": MIN_INLIERS,
                          "geometric_candidates": TOPK},
           "rows": rows}
    json.dump(out, open(OUT, "w"), indent=1)

    print(f"\nv2 I2V sources: {len(rows)}   unseen {out['n_unseen']}   seen {out['n_seen']}")
    for r in seen_rows:
        print(f"   SEEN  {r['id']:<6} {r['category']:<18} pool={r['pool']:<8} "
              f"roles={r['roles']}  via={sorted({h['test'] for h in r['evidence']})}")
    near = sorted((r for r in rows if r["verdict"] == "unseen" and r["nearest_bits"] is not None),
                  key=lambda r: r["nearest_bits"])[:5]
    print("closest unseen (perceptual bits to nearest seen image):",
          ", ".join(f"{r['id']}={r['nearest_bits']}" for r in near))
    print(f"-> {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

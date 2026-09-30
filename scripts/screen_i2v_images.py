"""Mechanical first-pass screen for candidate I2V source images.

The brief in docs/I2V_IMAGE_COLLECTION_BRIEF.md sets eight requirements. Four of
them are measurable without looking at the picture, and checking those first is
worth doing because it removes most of a large candidate pool before any
judgement is needed:

  * **Resolution / croppability.** We render 832x480, so an image must survive a
    16:9 crop at that size. Stock thumbnails (612x612, 250x250) cannot.
  * **Texture on the support.** fBD is ORB-based and abstains when too few
    repeatable keypoints survive; one v1 dust-storm scene abstained across all
    seven systems for exactly this reason. Screening with the same detector the
    metric uses is the principled filter, not a proxy.
  * **Diagram / schematic detection.** Engineering figures and catalogue shots on
    white backgrounds are common in this kind of search and are out of scope.
    A high near-white fraction with low saturation separates them cheaply.
  * **Duplicates.** Same picture under several filenames, and near-duplicates,
    both inflate a category without adding evidence.

What this cannot judge is scope: a steaming coffee cup passes every numeric test
and is not a fixed-camera environmental scene. Survivors therefore go to visual
review, and this script only ever *proposes* rejections.

    ~/miniconda3/envs/snfeval/bin/python scripts/screen_i2v_images.py
"""

import hashlib
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Defaults screen the v2 upload; `--src/--out` let the same thresholds be applied
# to the v1 pool, so a reused v1 image is held to the identical bar.
SRC = f"{ROOT}/prompts/v2/v2_images_extra"
OUT = f"{ROOT}/manifest/i2v_image_screen.json"

# We render 832x480 and an I2V conditioning image is resized anyway, so the bar
# is how much upscaling a 16:9 crop needs. <=8% is invisible; up to ~30% is
# usable and kept as a marginal tier to fall back on for a category that would
# otherwise be empty; beyond that the conditioning image is visibly soft and the
# softness propagates into the generated video.
MIN_W, MIN_H = 768, 432          # >=768x432 crop -> <=8% upscale to 832x480
MARGINAL_W, MARGINAL_H = 640, 360
MIN_ORB = 220                    # keypoints over the whole frame
WHITE_FRAC_MAX = 0.42            # above this with low saturation reads as a diagram
SAT_MIN = 22                     # mean saturation floor for photographs


def phash(gray):
    """8x8 DCT hash, for near-duplicate grouping."""
    g = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32)
    d = cv2.dct(g)[:8, :8]
    return "".join("1" if v > np.median(d) else "0" for v in d.flatten())


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def decode(path, data):
    """OpenCV first, Pillow second.

    The build of OpenCV here has no AVIF support, and six files in the first
    upload were AVIF -- including two that clear every numeric threshold. Reading
    them as "undecodable" would silently discard candidates for a format phone
    cameras and image CDNs now emit by default, so fall through to Pillow, which
    does decode it. Files that neither library reads are genuinely unusable.
    """
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is not None:
        return img
    try:
        with Image.open(path) as im:
            return cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)
    except Exception:
        return None


def measure(path):
    data = open(path, "rb").read()
    img = decode(path, data)
    if img is None:
        return {"error": "undecodable"}
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sat = float(hsv[:, :, 1].mean())
    white = float(((gray > 238) & (hsv[:, :, 1] < 30)).mean())
    orb = cv2.ORB_create(nfeatures=3000)
    kp = orb.detect(gray, None)
    # widest 16:9 crop this frame can yield
    crop_w = min(w, int(round(h * 16 / 9)))
    crop_h = min(h, int(round(w * 9 / 16)))
    return {"w": w, "h": h, "mp": round(w * h / 1e6, 2),
            "aspect": round(w / h, 3),
            "crop16x9": [crop_w, crop_h],
            "orb": len(kp),
            "saturation": round(sat, 1),
            "white_frac": round(white, 3),
            "sha1": hashlib.sha1(data).hexdigest()[:12],
            "phash": phash(gray)}


def verdict(m):
    if "error" in m:
        return "reject", ["undecodable"]
    r = []
    cw, ch = m["crop16x9"]
    marginal = False
    if cw < MARGINAL_W or ch < MARGINAL_H:
        r.append(f"16:9 crop only {cw}x{ch}, below {MARGINAL_W}x{MARGINAL_H}")
    elif cw < MIN_W or ch < MIN_H:
        marginal = True
    if m["orb"] < MIN_ORB:
        r.append(f"ORB keypoints {m['orb']} below {MIN_ORB} (fBD would abstain)")
    if m["white_frac"] > WHITE_FRAC_MAX and m["saturation"] < 60:
        r.append(f"white {m['white_frac']:.2f} at saturation {m['saturation']}"
                 f" reads as diagram or catalogue shot")
    if m["saturation"] < SAT_MIN:
        r.append(f"saturation {m['saturation']} very low")
    if r:
        return "reject", r
    return ("marginal" if marginal else "pass"), []


def main(argv):
    src, out = SRC, OUT
    for i, a in enumerate(argv):
        if a == "--src":
            src = argv[i + 1]
        elif a == "--out":
            out = argv[i + 1]
    files = sorted(f for f in os.listdir(src)
                   if not f.startswith("."))
    rows = []
    for f in files:
        m = measure(os.path.join(src, f))
        v, why = verdict(m)
        rows.append(dict(file=f, verdict=v, reasons=why, **m))

    # exact duplicates
    by_sha = {}
    for r in rows:
        if "sha1" not in r:
            continue
        by_sha.setdefault(r["sha1"], []).append(r["file"])
    dups = {k: v for k, v in by_sha.items() if len(v) > 1}
    dup_drop = set()
    for v in dups.values():
        dup_drop.update(sorted(v)[1:])

    # near-duplicates among the survivors
    live = [r for r in rows if r["verdict"] in ("pass", "marginal")
            and r["file"] not in dup_drop]
    near, used = [], set()
    for i, a in enumerate(live):
        if a["file"] in used:
            continue
        grp = [a["file"]]
        for b in live[i + 1:]:
            if b["file"] in used:
                continue
            if hamming(a["phash"], b["phash"]) <= 6:
                grp.append(b["file"])
                used.add(b["file"])
        if len(grp) > 1:
            near.append(grp)
    near_drop = {f for g in near for f in g[1:]}

    for r in rows:
        if r["file"] in dup_drop:
            r["verdict"], r["reasons"] = "reject", ["exact duplicate"]
        elif r["file"] in near_drop:
            r["verdict"], r["reasons"] = "reject", ["near duplicate"]

    n = len(rows)
    passed = [r for r in rows if r["verdict"] == "pass"]
    marg = [r for r in rows if r["verdict"] == "marginal"]
    print(f"screened {n} files")
    print(f"  pass     {len(passed)}  (>= {MIN_W}x{MIN_H} crop)")
    print(f"  marginal {len(marg)}  (>= {MARGINAL_W}x{MARGINAL_H}, usable with upscale)")
    print(f"  reject   {n - len(passed) - len(marg)}")
    from collections import Counter
    def kind(reason):
        """Group by cause, not by the exact dimensions in the message."""
        for k in ("16:9 crop", "ORB keypoints", "saturation", "white",
                  "exact duplicate", "near duplicate", "undecodable"):
            if reason.startswith(k):
                return k
        return reason
    why = Counter(kind(r["reasons"][0]) for r in rows if r["verdict"] == "reject")
    for k, c in why.most_common():
        print(f"     {c:4d}  {k}")
    print(f"\nexact-duplicate groups: {len(dups)}   near-duplicate groups: {len(near)}")
    if passed:
        orbs = sorted(r["orb"] for r in passed)
        mps = sorted(r["mp"] for r in passed)
        print(f"survivors: ORB median {orbs[len(orbs)//2]}, "
              f"megapixels median {mps[len(mps)//2]}")
    json.dump({"n": n, "n_pass": len(passed), "n_marginal": len(marg), "min_orb": MIN_ORB,
               "min_crop": [MIN_W, MIN_H], "rows": rows,
               "exact_duplicates": dups, "near_duplicate_groups": near},
              open(out, "w"), indent=2)
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

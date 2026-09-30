#!/usr/bin/env python3
"""Fetch candidate source images from Wikimedia Commons, with their licences.

Round 1 and 2 of the collection left one gap that could not be closed from the
delivered files, and left a second problem behind: none of the 451 delivered
images has a recorded licence, so none of them is redistributable with the
benchmark. Commons fixes both at once -- every file carries a machine-readable
licence, so a file fetched here arrives already attributable.

This does not replace the screen. Fetched files land in the same candidate pool
and go through `screen_i2v_images.py` and `classify_i2v_images.py` unchanged;
the only thing that differs is that provenance is known.

    ~/miniconda3/envs/snfeval/bin/python scripts/fetch_commons_images.py \
        --query "heavy rain street" --n 12 --out prompts/v2/v2_images_commons
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import time
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "snf-bench-image-collection/1.0 (research benchmark; contact via repo)"

# Only licences that permit redistribution with attribution. Commons also hosts
# fair-use and restricted files; those are rejected rather than silently kept.
OK_LICENCE = re.compile(
    r"^(cc0|cc-zero|cc-by(-sa)?-[0-9.]+|public domain|pd-.*)$", re.I)

MIN_W, MIN_H = 1280, 720
# Commons asks callers not to pull full originals in bulk and to request a
# listed thumbnail size instead; a 4608x3456 original is also ~5 MB of detail we
# discard at 832x480 anyway. 1920 wide leaves room for a 16:9 crop at render
# size with no upscaling.
THUMB_W = 1920
PAUSE = 1.0


def api(params):
    q = urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search(query, n):
    d = api({"action": "query", "generator": "search",
             "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": 6,
             "gsrlimit": n, "prop": "imageinfo",
             "iiprop": "url|size|extmetadata", "iiurlwidth": THUMB_W,
             "iiextmetadatafilter": "License|LicenseShortName|Artist|"
                                    "LicenseUrl|Credit"})
    return list(d.get("query", {}).get("pages", {}).values())


def field(meta, key):
    v = meta.get(key, {}).get("value", "")
    return re.sub(r"<[^>]+>", "", v).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--n", type=int, default=15)
    ap.add_argument("--out", default="prompts/v2/v2_images_commons")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    manifest_path = os.path.join(a.out, "licences.json")
    man = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}

    kept = 0
    for page in search(a.query, a.n):
        ii = page.get("imageinfo", [{}])[0]
        meta = ii.get("extmetadata", {})
        lic = field(meta, "LicenseShortName") or field(meta, "License")
        w, h = ii.get("width", 0), ii.get("height", 0)
        name = page["title"].removeprefix("File:").replace(" ", "_")
        if not OK_LICENCE.match(lic.replace(" ", "-")) and not OK_LICENCE.match(lic):
            print(f"  skip (licence {lic!r}): {name[:60]}")
            continue
        if w < MIN_W or h < MIN_H:
            print(f"  skip ({w}x{h}): {name[:60]}")
            continue
        dst = os.path.join(a.out, name)
        if not os.path.exists(dst):
            url = ii.get("thumburl") or ii["url"]
            for attempt in range(4):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        blob = r.read()
                    break
                except urllib.error.HTTPError as e:
                    if e.code != 429 or attempt == 3:
                        print(f"  skip ({e.code}): {name[:60]}")
                        blob = None
                        break
                    time.sleep(5 * (attempt + 1))
            else:
                blob = None
            if blob is None:
                continue
            with open(dst, "wb") as f:
                f.write(blob)
            time.sleep(PAUSE)
        tw, th = ii.get("thumbwidth", w), ii.get("thumbheight", h)
        man[name] = {"source": ii["descriptionurl"], "licence": lic,
                     "licence_url": field(meta, "LicenseUrl"),
                     "artist": field(meta, "Artist"),
                     "credit": field(meta, "Credit"),
                     "w": tw, "h": th, "original_wh": [w, h],
                     "query": a.query}
        print(f"  kept {tw}x{th:<5} {lic:<14} {name[:60]}")
        kept += 1

    json.dump(man, open(manifest_path, "w"), indent=1)
    print(f"\nkept {kept} for {a.query!r}  ->  {a.out}  ({len(man)} total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

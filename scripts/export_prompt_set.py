#!/usr/bin/env python3
"""Export the v2 prompt set in the file formats the generation pipelines read.

The v2 builders wrote authoritative manifests (`manifest/prompts_v2.json`,
`manifest/i2v_pairs_v2.json`) and the frozen 832x480 crops, but never the
per-horizon files a generator actually consumes. The first v2 I2V render
therefore had to hand-convert, wrote `target_crop` as a list where the loader
indexes a dict, and crashed before producing a frame. The T2V side had no
consumer files at all, so the same thing was waiting for the first v2 T2V run.

This writes them from the manifests, in exactly the conventions v1 used, so a
pipeline that ran v1 runs v2 by changing one path:

    prompts/v2/t2v/prompts{5s,60s,120s,240s}.txt
        one prompt per line, " [Hs]" duration marker (v1 T2V convention)
    prompts/v2/i2v/snf_v2_{5s,60s,120s,240s}/target_crop_info_v2.json
    prompts/v2/i2v/snf_v2_{...}/v2/<id>.jpg -> ../../images/<id>.jpg
        loader contract: `target_crop_info_<X>.json` with images in `<X>/`;
        captions carry "[Hs]" with no space (v1 I2V convention); target_crop is
        a dict; the bbox is the full 832x480 frame because the crop was already
        applied when the image was built, so the loader must not crop again.

Generators strip the marker before encoding, so the model-visible prompt is the
manifest text exactly. Nothing here touches the frozen images or manifests.

    python scripts/export_prompt_set.py           # write
    python scripts/export_prompt_set.py --check   # fail if any file is stale
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prompt_sets  # noqa: E402

HORIZONS = ("5s", "60s", "120s", "240s")
W, H = 832, 480
RATIO = "26-15"          # 832:480; the convention the I2V loaders already use


def t2v_files():
    s = prompt_sets.get("v2")
    scenes = json.load(open(os.path.join(ROOT, s["t2v_manifest"])))["scenes"]
    return {s["t2v_prompt_files"][h]:
            "".join(f"{r['text']} [{h}]\n" for r in scenes) for h in HORIZONS}


def i2v_files():
    s = prompt_sets.get("v2")
    pairs = json.load(open(os.path.join(ROOT, s["i2v_manifest"])))["pairs"]
    out, links = {}, {}
    for h in HORIZONS:
        d = s["i2v_dirs"][h]
        rows = [{"file_name": f"{p['id']}.jpg",
                 "caption": f"{p['text']}[{h}]",
                 "target_crop": {"target_bbox": [0, 0, W, H], "target_ratio": RATIO},
                 "type": p["category"],
                 "origin_width": W,
                 "origin_height": H,
                 "id": p["id"]} for p in pairs]
        out[f"{d}/{s['i2v_meta_name']}"] = json.dumps(rows, indent=1) + "\n"
        for p in pairs:
            links[f"{d}/v2/{p['id']}.jpg"] = f"../../images/{p['id']}.jpg"
    return out, links


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    files = t2v_files()
    i2v, links = i2v_files()
    files.update(i2v)

    stale = []
    for rel, body in sorted(files.items()):
        p = os.path.join(ROOT, rel)
        current = open(p).read() if os.path.exists(p) else None
        if current != body:
            stale.append(rel)
            if not a.check:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").write(body)
    for rel, target in sorted(links.items()):
        p = os.path.join(ROOT, rel)
        ok = os.path.islink(p) and os.readlink(p) == target
        if not ok:
            stale.append(rel)
            if not a.check:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                if os.path.lexists(p):
                    os.remove(p)
                os.symlink(target, p)
        if not os.path.exists(p) and not a.check:
            raise SystemExit(f"dangling link {rel} -> {target}")

    if a.check:
        if stale:
            print(f"STALE: {len(stale)} consumer file(s) differ from the manifests, e.g. "
                  f"{stale[0]}; run scripts/export_prompt_set.py")
            return 1
        print(f"v2 consumer files current ({len(files)} files, {len(links)} links)")
        return 0
    print(f"wrote/verified {len(files)} files and {len(links)} image links "
          f"({len(stale)} changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

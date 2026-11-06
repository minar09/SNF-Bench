#!/usr/bin/env python3
"""Run an official Wan `generate.py` once per staged scene (inside the container).

Reads the staged target_crop_info JSON (scripts/render_public_figure_set.py
stage_inputs) and calls `python generate.py <fixed args> --image <png> --prompt
<caption> --save_file <out>/<caption[:100]>.mp4` with list arguments, so no
prompt passes through a shell. The fixed args are everything after `--`.

    python wan_official_loop.py --json <info.json> --img_dir <dir> --out <dir> -- --task i2v-14B ...
"""
import argparse
import json
import os
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--json", required=True)
ap.add_argument("--img_dir", required=True)
ap.add_argument("--out", required=True)
a, rest = ap.parse_known_args()
fixed = rest[1:] if rest[:1] == ["--"] else rest
for r in json.load(open(a.json)):
    dst = os.path.join(a.out, r["caption"][:100] + ".mp4")
    cmd = [sys.executable, "generate.py", *fixed, "--image", os.path.join(a.img_dir, r["file_name"]),
           "--prompt", r["caption"], "--save_file", dst]
    print(r["file_name"], "->", dst, flush=True)
    subprocess.run(cmd, check=True)

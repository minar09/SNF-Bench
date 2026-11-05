#!/usr/bin/env python3
"""Matched pass-throughs for the method project's own composite controls, and adoption of those controls.

The method project built four control cells (results/factorial/cfpp/control_*;
ar-image-animation tools/analysis/output_composites_oct27.py and
copy_brackets_oct21.py). They were decoded with cv2 and re-encoded with ffmpeg
libx264 crf 18, preset medium, yuv420p, while their parents came from the
renderer's own writer. A composite is therefore compared with a pass-through of
its parent through the same decode/encode path, not with the parent itself
(docs/SNF_PP_REALISM_REVIEW_2026_11_04.md §2). That path was checked bit-exact:
rebuilding two `control_composite_untethered_lr` videos with this env
(snfeval, cv2 4.9.0) and this ffmpeg reproduced their SHA-256 (worklog
2026-11-05).

    PY=/home/minar/miniconda3/envs/snfeval/bin/python
    $PY scripts/native_controls.py passthrough <list.tsv> <out>/passthrough_crf18
    $PY scripts/native_controls.py adopt <cell> <list.tsv> <out>/<mode>
    $PY scripts/native_controls.py temporal <list.tsv> <out> reverse_tail,loop_exact,...

`list.tsv` rows are `<scene id>\\t<parent video path>`. `adopt` verifies every
hash the cell's RUN.json records against the files on disk, then links the
control (never copies or edits it) and writes a sidecar in the format
scripts/pilot_support_realism.py verifies. `temporal` writes the controls of
scripts/temporal_ops.py through the same decode/encode path, so
`passthrough_crf18` is their matched partner too. Nothing is ever overwritten.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths  # noqa: E402
import snf_sourceref as P  # noqa: E402
import temporal_ops as TO  # noqa: E402

FFMPEG = ("/home/minar/miniconda3/envs/helios/lib/python3.11/site-packages/"
          "imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")
ENCODE = ["-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p"]
W, H, FPS = 832, 480, 16
METHOD = _paths.resolve("method_repo")
MASKS = os.path.join(METHOD, "results/factorial/source_masks")
SOURCES = os.path.join(_paths.ROOT, "prompts/v2/i2v/images")
# control cell -> RUN.json key holding its parent's hash
PARENT_KEY = {"control_pasteback_nfpb1_copy_lr": "echo_sha256",
              "control_composite_untethered_lr": "base_sha256",
              "control_composite_framepack_lr": "base_sha256",
              "control_still_nfpb1_copy_lr": None}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def probe(path):
    """Frame count and rate from cv2's full decode; codec, pixel format and size from ffmpeg's stream line."""
    cap = cv2.VideoCapture(path)
    fps, n = cap.get(cv2.CAP_PROP_FPS), 0
    while cap.grab():
        n += 1
    cap.release()
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Video: (\w+).*?, (\w+)\(.*?(\d+)x(\d+)", err) or re.search(r"Video: (\w+).*?, (\w+), (\d+)x(\d+)", err)
    codec, pix, w, h = (m.group(1), m.group(2), int(m.group(3)), int(m.group(4))) if m else (None,) * 4
    return dict(frames=n, fps=float(fps), width=w, height=h, codec=codec, pix_fmt=pix)


def chain(sid, parent_sha):
    lab = os.path.join(MASKS, sid, "labels.png")
    return dict(parent_sha256=parent_sha, source_sha256=sha256(os.path.join(SOURCES, f"{sid}.jpg")),
                mask_labels_sha256=sha256(lab))


def refuse_taken(out_dir, sids):
    taken = [p for s in sids for p in (f"{out_dir}/{s}.mp4", f"{out_dir}/{s}.json") if os.path.lexists(p)]
    if taken:
        raise SystemExit(f"refusing to overwrite {len(taken)} existing outputs, e.g. {taken[0]}")
    os.makedirs(out_dir, exist_ok=True)


def decode(path):
    cap, frames = cv2.VideoCapture(path), []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    cap.release()
    return np.stack(frames)


def encode(frames, out_dir, sid, mode, parent, **params):
    """Encode BGR frames, verify the decoded file, then publish it with its sidecar."""
    out, tmp = f"{out_dir}/{sid}.mp4", f"{out_dir}/{sid}.partial.mp4"
    proc = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", *ENCODE, tmp],
                            stdin=subprocess.PIPE)
    for f in frames:
        proc.stdin.write(np.ascontiguousarray(f).tobytes())
    proc.stdin.close()
    got = probe(tmp) if proc.wait() == 0 else None
    want = dict(frames=len(frames), fps=float(FPS), width=W, height=H, codec="h264", pix_fmt="yuv420p")
    if got != want:
        os.remove(tmp)
        raise SystemExit(f"{sid}/{mode}: decoded {got}, expected {want}")
    os.rename(tmp, out)
    json.dump(dict(scene=sid, mode=mode, parent=parent, **chain(sid, sha256(parent)),
                   output_sha256=sha256(out), parent_frames=len(frames), output_decoded=got,
                   writer="cv2 decode -> ffmpeg rawvideo bgr24", ffmpeg=FFMPEG,
                   encoder=" ".join(ENCODE), cv2=cv2.__version__, **params),
              open(f"{out_dir}/{sid}.json", "w"), indent=1)
    print(sid, mode, flush=True)


def passthrough(listing, out_dir):
    scenes = [line.rstrip("\n").split("\t") for line in open(listing)]
    refuse_taken(out_dir, [s for s, _ in scenes])
    for sid, parent in scenes:
        encode(decode(parent), out_dir, sid, "passthrough_crf18", parent)


def temporal(listing, out_root, modes):
    modes = modes.split(",")
    bad = [m for m in modes if m not in TO.MODES]
    if bad:
        raise SystemExit(f"unknown modes {bad}; choose from {TO.MODES}")
    scenes = [line.rstrip("\n").split("\t") for line in open(listing)]
    for m in modes:
        refuse_taken(f"{out_root}/{m}", [s for s, _ in scenes])
    for sid, parent in scenes:
        frames = decode(parent)
        dyn = P.load_role_masks(os.path.join(MASKS, sid, "labels.png"))[0]
        for m in modes:
            encode(TO.compose(m, frames, dyn=dyn), f"{out_root}/{m}", sid, m, parent,
                   t0=len(frames) // 2, period=TO.PERIOD, fade=TO.FADE, seed=TO.SEED,
                   warp_px=TO.WARP_PX, warp_sigma=TO.WARP_SIGMA)


def adopt(cell, listing, out_dir):
    run_path = os.path.join(METHOD, "results/factorial/cfpp", cell, "seed42/60s/RUN.json")
    run, key = json.load(open(run_path)), PARENT_KEY[cell]
    scenes = [line.rstrip("\n").split("\t") for line in open(listing)]
    refuse_taken(out_dir, [s for s, _ in scenes])
    for sid, parent in scenes:
        rec = run["videos"][sid]
        video = rec["video"] if os.path.isabs(rec["video"]) else os.path.join(METHOD, rec["video"])
        out_sha, parent_sha = sha256(video), sha256(parent)
        bad = [k for k, a, b in (("sha256", out_sha, rec["sha256"]),
                                 (key, parent_sha, rec.get(key, parent_sha))) if a != b]
        if bad:
            raise SystemExit(f"{cell}/{sid}: RUN.json {bad} differ from the files on disk")
        os.symlink(video, f"{out_dir}/{sid}.mp4")
        json.dump(dict(scene=sid, mode=cell, adopted_from=run_path, run_sha256=sha256(run_path),
                       control=video, parent=parent if key else None, **chain(sid, parent_sha),
                       output_sha256=out_sha, output_decoded=probe(video), encoder=run["encoder"],
                       rule=run.get("rule") or run.get("beta_rule"),
                       evaluation_masks_used=run.get("evaluation_masks_used")),
                  open(f"{out_dir}/{sid}.json", "w"), indent=1)
        print(sid, "adopted", cell, flush=True)


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    {"passthrough": passthrough, "adopt": adopt, "temporal": temporal}[cmd](*args)

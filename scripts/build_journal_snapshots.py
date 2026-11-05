#!/usr/bin/env python3
"""Video snapshots and change maps for the TCSVT draft and its interactive companions.

Selection rule, fixed before any frame was viewed: every text-to-video prompt
at the 240 s horizon for which all seven published systems
(scripts/registry.py `contestants("t2v")`) have an output. Four prompts
qualify. The main figure uses the first in prompt-ID order; the appendix shows
all four. Steady-Forcing is left out until its single released configuration
is identified (two internal configurations exist locally).

Per video (decoded once, sequentially, so frame indices are exact):

* frames at t = 0, 60, 120, 180 s and the last frame: lossless PNG at native
  832x480 for the main figure; JPEG (quality 95, 4:4:4) at 416x240 for the
  appendix, where each image prints about an inch wide;
* `change` map: |mean grey of the first second - mean grey of the last second|,
  where the scene ended up differing from its start (drift, redraw or
  material that moved away);
* `motion` map: mean |successive grey change| over the last 12% of frames
  sampled at 8 fps, where the scene still moves at the end;
* JPEG thumbnails every 10 s at 416x240 for the companion viewer.

Maps are visualizations on a fixed colour scale, not metrics; they use no
region masks. The I2V role illustration uses ifp06, the only v2 source with a
CC BY 2.0 licence recorded (Metropolitan Transportation Authority of the State
of New York).

    MPLCONFIGDIR=/tmp/snf-mpl /home/minar/miniconda3/envs/snfeval/bin/python scripts/build_journal_snapshots.py
"""
import csv
import hashlib
import json
import os
import sys
from collections import defaultdict

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths                      # noqa: E402
from registry import contestants   # noqa: E402

ROOT = _paths.ROOT
J = os.path.join(ROOT, "JOURNAL_TCSVT")
SNAP = os.path.join(J, "figures/snapshots")
ASSETS = os.path.join(J, "interactive/assets")
DUR, FPS = "240s", 16
TIMES = (0, 60, 120, 180, 240)      # seconds; 240 maps to the last frame
THUMB_EVERY = 10                    # s
CHANGE_MAX, MOTION_MAX = 100.0, 12.0  # grey levels: fixed colour-scale tops
CMAP_CHANGE, CMAP_MOTION = "inferno", "viridis"
LATE = 0.12
JPEG_HQ = [cv2.IMWRITE_JPEG_QUALITY, 95, cv2.IMWRITE_JPEG_SAMPLING_FACTOR, cv2.IMWRITE_JPEG_SAMPLING_FACTOR_444]
ROLE_RGB = {0: (170, 170, 170), 1: (0, 114, 178), 2: (230, 159, 0), 3: (204, 121, 167)}  # Okabe-Ito


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def select():
    systems = contestants("t2v")
    keys = [m["key"] for m in systems]
    vids = defaultdict(dict)
    for r in csv.DictReader(open(os.path.join(ROOT, "manifest/video_index.csv"))):
        if r["track"] == "t2v" and r["duration"] == DUR and r["model"] in keys:
            pid = r["video"].split("-0-")[0]
            vids[pid][r["model"]] = os.path.join(_paths.resolve("t2v_source_repo"), r["source_rel"])
    prompts = sorted(p for p, v in vids.items() if len(v) == len(keys))
    return systems, prompts, vids


def colourize(x, top, cmap):
    rgba = plt.get_cmap(cmap)(np.clip(x / top, 0, 1))
    return (rgba[..., :3] * 255).astype(np.uint8)


def process(path, out_png, out_png_small, out_thumb, tag):
    cap = cv2.VideoCapture(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    want = {min(n - 1, int(round(t * FPS))): t for t in TIMES}
    thumbs = {min(n - 1, int(round(t * FPS))): t for t in range(0, 241, THUMB_EVERY)}
    step = FPS // 8
    first, last, sampled, i = [], [], [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)
        if i < FPS:
            first.append(g)
        if i >= n - FPS:
            last.append(g)
        if i % step == 0:
            sampled.append(g)
        if i in want:
            t = want[i]
            if out_png:
                cv2.imwrite(f"{out_png}/{tag}_t{t:03d}.png", f)
            cv2.imwrite(f"{out_png_small}/{tag}_t{t:03d}.jpg", cv2.resize(f, (416, 240), interpolation=cv2.INTER_AREA),
                        JPEG_HQ)
        if i in thumbs:
            cv2.imwrite(f"{out_thumb}/{tag}_t{thumbs[i]:03d}.jpg",
                        cv2.resize(f, (416, 240), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])
        i += 1
    cap.release()
    change = np.abs(np.mean(first, 0) - np.mean(last, 0))
    w = max(2, int(len(sampled) * LATE))
    motion = np.abs(np.diff(np.stack(sampled[-w:]), axis=0)).mean(0)
    maps = {"change": colourize(change, CHANGE_MAX, CMAP_CHANGE), "motion": colourize(motion, MOTION_MAX, CMAP_MOTION)}
    for k, rgb in maps.items():
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        if out_png:
            cv2.imwrite(f"{out_png}/{tag}_{k}.png", bgr)
        cv2.imwrite(f"{out_png_small}/{tag}_{k}.jpg", cv2.resize(bgr, (416, 240), interpolation=cv2.INTER_AREA),
                    JPEG_HQ)
        cv2.imwrite(f"{out_thumb}/{tag}_{k}.jpg", cv2.resize(bgr, (416, 240), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    return dict(frames=i, frame_index={str(t): k for k, t in want.items()},
                change_median=float(np.median(change)), motion_median=float(np.median(motion)))


def colourbars():
    for name, top, cmap in (("change", CHANGE_MAX, CMAP_CHANGE), ("motion", MOTION_MAX, CMAP_MOTION)):
        fig, ax = plt.subplots(figsize=(1.6, 0.32))
        fig.subplots_adjust(left=0.07, right=0.86, bottom=0.55, top=0.98)
        cb = matplotlib.colorbar.ColorbarBase(ax, cmap=plt.get_cmap(cmap), orientation="horizontal",
                                              norm=matplotlib.colors.Normalize(0, top))
        cb.set_ticks([0, top / 2, top])
        cb.set_ticklabels(["0", f"{top / 2:g}", f"$\\geq${top:g}"])
        cb.ax.tick_params(labelsize=6, length=2, pad=1)
        cb.outline.set_linewidth(0.4)
        fig.savefig(f"{SNAP}/colourbar_{name}.pdf")
        fig.savefig(f"{ASSETS}/colourbar_{name}.png", dpi=200)
        plt.close(fig)


def role_overlay():
    """ifp06 source with its role map blended in (CC BY 2.0 source)."""
    src = cv2.imread(os.path.join(ROOT, "prompts/v2/i2v/images/ifp06.jpg"))
    lab = cv2.imread(os.path.join(_paths.resolve("method_repo"),
                                  "results/factorial/source_masks/ifp06/labels.png"), cv2.IMREAD_GRAYSCALE)
    tint = np.zeros_like(src)
    for k, rgb in ROLE_RGB.items():
        tint[lab == k] = rgb[::-1]
    out = cv2.addWeighted(src, 0.55, tint, 0.45, 0)
    edges = cv2.Canny(lab * 60, 10, 30) > 0
    out[edges] = (255, 255, 255)
    cv2.imwrite(f"{SNAP}/role_ifp06.png", out)
    cv2.imwrite(f"{SNAP}/source_ifp06.png", src)
    cv2.imwrite(f"{ASSETS}/role_ifp06.jpg", cv2.resize(out, (416, 240), interpolation=cv2.INTER_AREA),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
    return {int(k): int(v) for k, v in zip(*np.unique(lab, return_counts=True))}


def main():
    for d in (SNAP, ASSETS):
        os.makedirs(d, exist_ok=True)
    systems, prompts, vids = select()
    rec = dict(rule="all 240 s T2V prompts with outputs from every published system; main = first by prompt ID",
               systems=[dict(key=m["key"], name=m["name"]) for m in systems], prompts=[], times_s=list(TIMES),
               maps=dict(change=dict(definition="|mean grey of first 1 s - mean grey of last 1 s|",
                                     top=CHANGE_MAX, cmap=CMAP_CHANGE),
                         motion=dict(definition="mean |successive grey change|, last 12% of frames at 8 fps",
                                     top=MOTION_MAX, cmap=CMAP_MOTION)),
               note="visualizations, not metrics; no region masks are used")
    for p_i, pid in enumerate(prompts):
        tag_dir = f"p{p_i}"
        big = f"{SNAP}/t2v240/{tag_dir}" if p_i == 0 else None
        small = f"{SNAP}/t2v240_hq/{tag_dir}"
        thumb = f"{ASSETS}/t2v240/{tag_dir}"
        for d in filter(None, (big, small, thumb)):
            os.makedirs(d, exist_ok=True)
        entry = dict(id=tag_dir, prompt=pid.replace("_", " "), videos={})
        for m in systems:
            path = vids[pid][m["key"]]
            entry["videos"][m["key"]] = dict(path=path, sha256=sha256(path),
                                             **process(path, big, small, thumb, m["key"]))
            print(tag_dir, m["key"], flush=True)
        rec["prompts"].append(entry)
    colourbars()
    rec["role_illustration"] = dict(scene="ifp06", licence="CC BY 2.0",
                                    attribution="Metropolitan Transportation Authority of the State of New York",
                                    source="https://commons.wikimedia.org/wiki/File:Snowy_Transit_in_Brooklyn_(12294431174).jpg",
                                    label_pixels=role_overlay(), colours_rgb=ROLE_RGB)
    json.dump(rec, open(f"{SNAP}/SNAPSHOTS.json", "w"), indent=1)
    js = {k: rec[k] for k in ("systems", "times_s", "maps")}
    js["prompts"] = [dict(id=e["id"], prompt=e["prompt"]) for e in rec["prompts"]]
    with open(f"{ASSETS}/snapshots.js", "w") as f:
        f.write("window.SNAPSHOTS = " + json.dumps(js) + ";\n")


if __name__ == "__main__":
    main()

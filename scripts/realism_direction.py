#!/usr/bin/env python3
"""R3 direction candidates: does the dynamic region move the way the scene text declares?

Plan: docs/SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md §2 (R3). GPU (RAFT).
The declared direction comes from the v2 scene text (manifest/i2v_pairs_v2.json
`direction`), so it is a *candidate* label, not verified truth; scenes without
one abstain. Flow is RAFT (VBench raft-things) on frames sampled at 8 fps and
resized to 288 px high, over the last 12% of sampled pairs, inside the eroded
dynamic role (scripts/snf_task_metrics.py settings, unchanged).

* `cand-direction-flux-0`: sum over pixels and pairs of the flow component
  along the declared unit vector, over the sum of flow magnitudes. In [-1, 1]:
  +1 all motion along the declared direction, -1 all against it, ~0 none net.
* `cand-direction-agreement-0`: fraction of pairs whose mean along-component
  is positive. Pairs with mean speed below MIN_SPEED do not vote.
* `speed`: mean flow magnitude, px per sampled frame at 288 px (diagnostic).

Abstains when there is no declared direction, the eroded dynamic region is
under MIN_PX at flow resolution, or the late mean speed is below MIN_SPEED.

    CUDA_VISIBLE_DEVICES=3 python scripts/realism_direction.py --videos <list.tsv> \\
        --controls <dir> --modes passthrough_crf18,reverse_tail,pingpong --out <json>
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths                         # noqa: E402
_paths.bootstrap_metric_imports()
import snf_task_metrics as S          # noqa: E402
import snf_sourceref as P             # noqa: E402
import snf_candidates as C            # noqa: E402
from pilot_support_realism import sha256, verify_chain  # noqa: E402

IDENTITY = {"flux": "cand-direction-flux-0", "agreement": "cand-direction-agreement-0"}
UNIT = {"left to right": (1, 0), "right to left": (-1, 0), "top to bottom": (0, 1), "upward": (0, -1),
        "upper left to lower right": (1, 1), "upper right to lower left": (-1, 1),
        "downward and to the left": (-1, 1)}
MIN_SPEED = 0.05    # px per sampled frame at 288 px; not calibrated
MIN_PX = 200


def declared():
    pairs = json.load(open(os.path.join(_paths.ROOT, "manifest/i2v_pairs_v2.json")))["pairs"]
    return {p["id"]: p["direction"] for p in pairs}


def late_frames(path, device):
    """S.read_frames, but only the late-window frames are resized and moved to the device (same values)."""
    vid = cv2.VideoCapture(path)
    fps = vid.get(cv2.CAP_PROP_FPS) or 24.0
    interval = max(1, round(fps / S.SAMPLE_FPS))
    raw, i = [], 0
    while True:
        ok, f = vid.read()
        if not ok:
            break
        if i % interval == 0:
            raw.append(f)
        i += 1
    vid.release()
    if len(raw) < 4:
        return None
    k = max(S.MIN_WIN, int(round((len(raw) - 1) * S.WIN_FRAC)))
    h, w = raw[0].shape[:2]
    nw = int(round(w * S.MAX_H / h))
    out = []
    for f in raw[-(k + 1):]:
        rgb = cv2.cvtColor(cv2.resize(f, (nw, S.MAX_H), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
        out.append(torch.from_numpy(rgb.astype(np.uint8)).permute(2, 0, 1).float()[None].to(device))
    return out


def measure(model, path, dyn, direction, device):
    if direction is None:
        return {"abstain": "no declared direction"}
    if direction not in UNIT:
        return {"abstain": f"direction {direction!r} has no image-plane vector"}
    tens = late_frames(path, device)
    if tens is None:
        return {"abstain": "too few frames"}
    h, w = tens[0].shape[2:]
    m = cv2.resize(C.erode(dyn).astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST) > 0
    if m.sum() < MIN_PX:
        return {"abstain": f"eroded dynamic region {int(m.sum())} px < {MIN_PX} at flow resolution"}
    d = np.float64(UNIT[direction])
    d /= np.linalg.norm(d)
    k = len(tens) - 1
    along, mag, votes = 0.0, 0.0, []
    speeds = []
    for i in range(k):
        f = S.flow_vec(model, tens[i], tens[i + 1])[m]
        a = f @ d
        s = np.hypot(f[:, 0], f[:, 1])
        along += a.sum()
        mag += s.sum()
        speeds.append(s.mean())
        if s.mean() >= MIN_SPEED:
            votes.append(a.mean() > 0)
    speed = float(np.mean(speeds))
    out = dict(direction=direction, pairs=k, pixels=int(m.sum()), speed=speed,
               along_mean=float(along / (k * m.sum())))
    if speed < MIN_SPEED:
        out["abstain"] = f"late mean speed {speed:.3f} < {MIN_SPEED}"
        return out
    out.update(flux=float(along / mag), agreement=float(np.mean(votes)) if votes else None, voting_pairs=len(votes))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True, help="tsv: scene id, parent video path")
    ap.add_argument("--controls", required=True)
    ap.add_argument("--modes", required=True, help="controls subdirectories, the pass-through first")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.exists(a.out):
        raise SystemExit(f"{a.out} exists; reports are never overwritten")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = S.load_raft(device)
    masks = os.path.join(_paths.resolve("method_repo"), "results/factorial/source_masks")
    dirs, modes, rows = declared(), a.modes.split(","), []
    for line in open(a.videos):
        sid, video = line.rstrip("\n").split("\t")
        dyn, _, lsha, _ = P.load_role_masks(os.path.join(masks, sid, "labels.png"))
        chain = dict(parent_sha256=sha256(video), mask_labels_sha256=lsha,
                     source_sha256=sha256(os.path.join(_paths.ROOT, "prompts/v2/i2v/images", f"{sid}.jpg")))
        row = dict(scene=sid, chain=chain, controls={})
        for md in modes:
            path = f"{a.controls}/{md}/{sid}.mp4"
            verify_chain(path, chain)
            row["controls"][md] = dict(sha256=sha256(path), **measure(model, path, dyn, dirs.get(sid), device))
        rows.append(row)
        print(sid, {md: row["controls"][md].get("flux") for md in modes}, flush=True)
    ref, summary = modes[0], {}
    for md in modes:
        summary[md] = {}
        for s in ("flux", "agreement"):
            v = [r["controls"][md][s] for r in rows if r["controls"][md].get(s) is not None]
            summary[md][s] = dict(n=len(v), n_attempted=len(rows),
                                  median=float(np.median(v)) if v else None,
                                  frac_positive=float(np.mean(np.array(v) > 0.5 if s == "agreement"
                                                              else np.array(v) > 0)) if v else None)
            if md != ref:
                p = [(r["controls"][ref][s], r["controls"][md][s]) for r in rows
                     if r["controls"][ref].get(s) is not None and r["controls"][md].get(s) is not None]
                if p:
                    x, y = np.array(p).T
                    summary[md][s].update(n_paired=len(p), frac_reference_above=float(np.mean(x > y)),
                                          median_reference_minus_control=float(np.median(x - y)))
    rep = dict(entrant=a.label, identity=IDENTITY, reference=ref, min_speed=MIN_SPEED, min_px=MIN_PX,
               flow=dict(model="RAFT raft-things (VBench)", max_h=S.MAX_H, sample_fps=S.SAMPLE_FPS,
                         window=S.WIN_FRAC, iters=20),
               labels="text-derived candidate directions, manifest/i2v_pairs_v2.json; not verified",
               caveat="development data (CF++ family); known-answer controls only; no human labels",
               summary=summary, rows=rows)
    json.dump(rep, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

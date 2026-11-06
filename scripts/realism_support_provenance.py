#!/usr/bin/env python3
"""A1/A2 support-provenance candidates: is the support frozen, and is it the source's own texture?

Design: docs/SNF_PP_METRIC_EXTENSION_DESIGN_2026_11_05.md §1. CPU. Development data only.

A paste composite holds the source pixels on the support, so after the codec the
support's high-frequency residual is (a) frozen in time and (b) the source's own
residual. A generated support that merely holds still is (a) but not (b): its
fine texture passes through the decoder. A real fixed camera is neither: sensor
noise keeps (a) above the codec floor.

* `cand-support-freeze-0` (A1): z = log(median over textured support pixels of
  the temporal std of the residual W(f_t), over the last WINDOW_S at native fps,
  divided by the same on the codec still of the source). Also the exact-repeat
  fraction: support pixels whose decoded grey value never changes in the window.
* `cand-support-hf-source-0` (A2), PROXY mode (no decoder ceiling): rho = mean
  over the window of NCC(W(f_t), W(x0)) on textured support pixels, and
  pi_proxy = rho / rho_codec, where rho_codec is the same NCC for the codec
  still. The decoder-referenced pi of the design needs the generator's VAE (A3).
* Paste flag (development reading, not a verdict): frozen (z < Z_FROZEN) and
  source-matching (pi_proxy > PI_MATCH). Thresholds are declared here before the
  controls are run and are reported with the data, not tuned on it.
  SUPERSEDED for the freeze part: the median per-pixel std is 0 on both stills and
  pastes, so z divides by the clamp and is degenerate
  (manifest/realism_dev_2026_11_05/support_provenance_default.json, 42% flagged).
* `cand-support-paste-fraction-0`: per TILE of textured support, the tile is
  pasted iff at least TILE_REPEAT of its pixels never change over the window and
  NCC(time-mean residual, source residual) >= TILE_NCC. The statistic is the
  pasted share of textured tiles, which also reads partial pastes (a control that
  pastes only part of the SNF support). Both thresholds were fixed on 2026-11-05
  from what a codec still does by construction (repeat 1.0, NCC 1.0) and from
  pass-throughs (repeat 0.0), after the -0 run above and before any composite
  cell was scored with them.

W(f) = grey - GaussianBlur(grey, sigma=1). Textured tiles: TILE px tiles of the
eroded support whose source residual std >= TEX_MIN grey levels, since flat
regions reconstruct well whatever their origin.

    python scripts/realism_support_provenance.py --videos <list.tsv> --controls <dir> \\
        --modes passthrough_crf18,control_pasteback,control_still --still control_still \\
        --label <cell> --out <json>
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths               # noqa: E402
import snf_candidates as C  # noqa: E402
import snf_sourceref as P   # noqa: E402
from pilot_support_realism import sha256, verify_chain, verify_reference  # noqa: E402

IDENTITY = {"freeze": "cand-support-freeze-0", "hf_source": "cand-support-hf-source-0",
            "paste_fraction": "cand-support-paste-fraction-0"}
TILE_REPEAT, TILE_NCC = 0.9, 0.8
WINDOW_S = 4.0
SIGMA = 1.0
TILE, TEX_MIN, MIN_TILES = 16, 2.0, 20
Z_FROZEN, PI_MATCH = 0.25, 0.8
ROOT = _paths.ROOT


def residual(grey):
    return grey - cv2.GaussianBlur(grey, (0, 0), SIGMA)


def late_grey(path, window_s=WINDOW_S):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 16.0
    n = int(round(window_s * fps))
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
        if len(frames) > n:
            frames.pop(0)
    cap.release()
    if len(frames) < n:
        raise ValueError(f"{len(frames)} frames < {n}")
    return np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames]), fps


def textured(support, src_res):
    core = C.erode(support)
    keep = np.zeros_like(core)
    tiles = []
    h, w = core.shape
    for y in range(0, h - TILE + 1, TILE):
        for x in range(0, w - TILE + 1, TILE):
            m = core[y:y + TILE, x:x + TILE]
            if m.mean() < 0.9:
                continue
            if src_res[y:y + TILE, x:x + TILE][m].std() >= TEX_MIN:
                keep[y:y + TILE, x:x + TILE] |= m
                tiles.append((y, x))
    return keep, tiles


def ncc(a, b):
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / max(np.sqrt((a * a).sum() * (b * b).sum()), 1e-9))


def measure(path, mask, src_res, tiles):
    try:
        grey, fps = late_grey(path)
    except ValueError as e:
        return {"abstain": str(e)}
    res = np.stack([residual(g) for g in grey])
    sigma_hf = float(np.median(res.std(axis=0)[mask]))
    still = np.abs(np.diff(grey, axis=0)).max(axis=0) == 0
    repeat = float(still[mask].mean())
    rho = float(np.mean([ncc(r[mask], src_res[mask]) for r in res]))
    mean_res, pasted = res.mean(axis=0), 0
    for y, x in tiles:
        m = mask[y:y + TILE, x:x + TILE]
        if (still[y:y + TILE, x:x + TILE][m].mean() >= TILE_REPEAT and
                ncc(mean_res[y:y + TILE, x:x + TILE][m], src_res[y:y + TILE, x:x + TILE][m]) >= TILE_NCC):
            pasted += 1
    return dict(fps=fps, frames=len(grey), sigma_hf=sigma_hf, exact_repeat_frac=repeat, rho=rho,
                paste_fraction=pasted / len(tiles))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True, help="tsv: scene id, parent video path")
    ap.add_argument("--controls", required=True)
    ap.add_argument("--modes", required=True, help="controls subdirectories, the pass-through first")
    ap.add_argument("--still", required=True, help="controls subdirectory holding the codec still of the source")
    ap.add_argument("--still-root", default=None, help="controls dir holding --still, if not --controls")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.exists(a.out):
        raise SystemExit(f"{a.out} exists; reports are never overwritten")
    masks = os.path.join(_paths.resolve("method_repo"), "results/factorial/source_masks")
    modes, rows = a.modes.split(","), []
    for line in open(a.videos):
        sid, video = line.rstrip("\n").split("\t")
        _, sup, lsha, _ = P.load_role_masks(os.path.join(masks, sid, "labels.png"))
        src_path = os.path.join(ROOT, "prompts/v2/i2v/images", f"{sid}.jpg")
        src_res = residual(cv2.cvtColor(cv2.imread(src_path), cv2.COLOR_BGR2GRAY).astype(np.float32))
        chain = dict(parent_sha256=sha256(video), mask_labels_sha256=lsha, source_sha256=sha256(src_path))
        mask, tiles = textured(sup, src_res)
        n_tiles = len(tiles)
        row = dict(scene=sid, chain=chain, textured_tiles=n_tiles, controls={})
        if n_tiles < MIN_TILES:
            row["abstain"] = f"{n_tiles} textured support tiles < {MIN_TILES}"
            rows.append(row)
            print(sid, row["abstain"], flush=True)
            continue
        still = f"{a.still_root or a.controls}/{a.still}/{sid}.mp4"
        # the still is the source alone: bind it to the source and mask, not to this cell's parent
        verify_chain(still, {k: chain[k] for k in ("source_sha256", "mask_labels_sha256")})
        floor = measure(still, mask, src_res, tiles)
        row["still"] = dict(sha256=sha256(still), **floor)
        for md in modes:
            path = f"{a.controls}/{md}/{sid}.mp4"
            verify_chain(path, chain)
            if md == modes[0]:
                verify_reference(path)
            m = measure(path, mask, src_res, tiles)
            if "abstain" not in m and "abstain" not in floor:
                m["freeze_z"] = float(np.log(max(m["sigma_hf"], 1e-6) / max(floor["sigma_hf"], 1e-6)))
                m["pi_proxy"] = float(m["rho"] / floor["rho"]) if floor["rho"] > 0.05 else None
                m["paste_flag"] = bool(m["freeze_z"] < Z_FROZEN and m["pi_proxy"] is not None
                                       and m["pi_proxy"] > PI_MATCH)
            row["controls"][md] = dict(sha256=sha256(path), **m)
        rows.append(row)
        print(sid, {md: (round(row["controls"][md].get("freeze_z", float("nan")), 2),
                         round(row["controls"][md].get("pi_proxy") or float("nan"), 2))
                    for md in modes}, flush=True)
    summary = {}
    for md in modes:
        v = [r["controls"][md] for r in rows if md in r.get("controls", {}) and "freeze_z" in r["controls"][md]]
        summary[md] = dict(n=len(v), n_attempted=len(rows),
                           paste_flag_frac=float(np.mean([x["paste_flag"] for x in v])) if v else None,
                           freeze_z_median=float(np.median([x["freeze_z"] for x in v])) if v else None,
                           pi_proxy_median=float(np.median([x["pi_proxy"] for x in v if x["pi_proxy"] is not None]))
                           if v else None,
                           exact_repeat_median=float(np.median([x["exact_repeat_frac"] for x in v])) if v else None,
                           paste_fraction_median=float(np.median([x["paste_fraction"] for x in v])) if v else None,
                           paste_fraction_range=[float(min(x["paste_fraction"] for x in v)),
                                                 float(max(x["paste_fraction"] for x in v))] if v else None)
    rep = dict(entrant=a.label, identity=IDENTITY, mode="proxy (no decoder ceiling)", window_s=WINDOW_S,
               residual=f"grey - GaussianBlur(sigma={SIGMA})", tile=TILE, tex_min=TEX_MIN, min_tiles=MIN_TILES,
               thresholds=dict(z_frozen=Z_FROZEN, pi_match=PI_MATCH, declared="before running the controls",
                               tile_repeat=TILE_REPEAT, tile_ncc=TILE_NCC),
               caveat="development data (CF++ family); constructed controls; no real footage; proxy A2",
               summary=summary, rows=rows)
    json.dump(rep, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

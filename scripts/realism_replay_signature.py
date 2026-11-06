#!/usr/bin/env python3
"""`cand-replay-signature-0`: the SceneTether repetition diagnostic v1.1, run on SNF role maps.

Design: docs/SNF_PP_METRIC_EXTENSION_DESIGN_2026_11_05.md §4 item 1. CPU.

The module is vendored byte-for-byte from the method project
(ar-image-animation tools/factorial_scoring/repetition.py, commit 81ee7b7) as
scripts/vendor/repetition_v1_1.py, with its codec-floor calibration as
manifest/vendor/repetition_calibration_oct15.json; both are hash-checked on
load. It reports exact replay, ping-pong, freeze and "periodic, not replay"
fractions of 1 s windows of the dynamic region's motion signature, full video
and late half. Upstream validation: 252 clips, AUROC 1.0 on loops, cross-fades,
ping-pong and late freeze, 0.958 on late-onset loops (method docs/122).

The calibration was made on x264 re-encodes through the same ffmpeg CRF 18 path
as the SNF controls (scripts/native_controls.py); entrants written by another
encoder need their own floor before their freeze and exact flags are read.

    python scripts/realism_replay_signature.py --videos <list.tsv> --controls <dir> \\
        --modes passthrough_crf18,loop_exact,... --label <cell> --out <json> [--jobs 12]
"""
import argparse
import hashlib
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "vendor"))
import _paths                     # noqa: E402
import repetition_v1_1 as REP     # noqa: E402
from pilot_support_realism import sha256, verify_chain, verify_reference  # noqa: E402

IDENTITY = "cand-replay-signature-0"
MODULE_SHA = "06f42a6bfc8cd19c47b74481f1cb8f433fb321eb096bb738a68d85123684597a"
CALIB = os.path.join(_paths.ROOT, "manifest/vendor/repetition_calibration_oct15.json")
CALIB_SHA = "44dafbf12c587362aa0af94a8666e76f30aac38399b727999fbe133214d19c70"
MASKS = os.path.join(_paths.resolve("method_repo"), "results/factorial/source_masks")
KEYS = ("exact_frac", "pp_frac", "freeze_frac", "periodic_frac", "replay_suspect", "pingpong_suspect",
        "freeze_suspect", "exact_run_max_s", "R_ex_p10", "lag_period_s")


def check_pins():
    if sha256(REP.__file__) != MODULE_SHA:
        raise SystemExit(f"{REP.__file__}: vendored module differs from the pinned upstream bytes")
    if sha256(CALIB) != CALIB_SHA:
        raise SystemExit(f"{CALIB}: calibration differs from the pinned copy")


def score(args):
    path, labels = args
    floor, floor_freeze, _ = REP.load_floor(CALIB)
    doc = REP.score_video(path, labels, floor=floor, floor_freeze=floor_freeze)
    if doc.get("abstain_reason"):
        return dict(abstain=doc["abstain_reason"], region=doc["region"])
    return dict(region=doc["region"], fps=doc["fps"], n_frames=doc["n_frames"], seconds=doc["seconds"],
                full={k: doc["full"].get(k) for k in KEYS}, late={k: doc["late"].get(k) for k in KEYS})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True, help="tsv: scene id, parent video path")
    ap.add_argument("--controls", required=True)
    ap.add_argument("--modes", required=True, help="controls subdirectories, the pass-through first")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    if os.path.exists(a.out):
        raise SystemExit(f"{a.out} exists; reports are never overwritten")
    check_pins()
    modes, jobs, rows = a.modes.split(","), [], []
    for line in open(a.videos):
        sid, video = line.rstrip("\n").split("\t")
        labels = os.path.join(MASKS, sid, "labels.png")
        chain = dict(parent_sha256=sha256(video), mask_labels_sha256=sha256(labels),
                     source_sha256=sha256(os.path.join(_paths.ROOT, "prompts/v2/i2v/images", f"{sid}.jpg")))
        row = dict(scene=sid, chain=chain, controls={})
        for md in modes:
            path = f"{a.controls}/{md}/{sid}.mp4"
            verify_chain(path, {k: chain[k] for k in ("parent_sha256", "source_sha256")})
            if md == modes[0]:
                verify_reference(path)
            row["controls"][md] = dict(sha256=sha256(path))
            jobs.append((sid, md, path, labels))
        rows.append(row)
    by = {r["scene"]: r for r in rows}
    with ProcessPoolExecutor(a.jobs) as ex:
        for (sid, md, _, _), res in zip(jobs, ex.map(score, [(p, l) for _, _, p, l in jobs])):
            by[sid]["controls"][md].update(res)
    summary = {}
    for md in modes:
        v = [r["controls"][md] for r in rows if "full" in r["controls"][md]]
        s = dict(n=len(v), n_attempted=len(rows))
        for part in ("full", "late"):
            for k in ("exact_frac", "pp_frac", "freeze_frac", "periodic_frac"):
                x = [d[part][k] for d in v if d[part][k] is not None and d[part][k] == d[part][k]]
                s[f"{part}_{k}_median"] = float(np.median(x)) if x else None
            for k in ("replay_suspect", "pingpong_suspect", "freeze_suspect"):
                s[f"{part}_{k}_rate"] = float(np.mean([bool(d[part][k]) for d in v])) if v else None
        summary[md] = s
    rep = dict(entrant=a.label, identity=IDENTITY, module="scripts/vendor/repetition_v1_1.py",
               module_sha256=MODULE_SHA, upstream="ar-image-animation tools/factorial_scoring/repetition.py @81ee7b7",
               calibration=os.path.relpath(CALIB, _paths.ROOT), calibration_sha256=CALIB_SHA,
               masks="method_repo results/factorial/source_masks (SNF v2 role maps)",
               reading="provisional suspect thresholds 0.25 (upstream), reported, not verdicts",
               caveat="development data; constructed controls; natural periodic negatives only as generated originals",
               summary=summary, rows=rows)
    json.dump(rep, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pilot: can support-realism statistics tell a pass-through video from its support composites?

Design: docs/SNF_PP_REALISM_DESIGN_2026_11_04.md, statistics S1 and S2 (CPU,
no flow); review: docs/SNF_PP_REALISM_REVIEW_2026_11_04.md. For each scene it
compares:

* the reference: the entrant's video re-encoded unchanged (`passthrough`), or
  with `--reference original`, the once-encoded original (2026-11-04 pilot only);
* each control built by scripts/build_composite_controls.py from the same
  decoded parent;
* the source encoded as a static clip (scripts/encode_static_controls.py).

Statistics are taken on the late window (last 12% of frames sampled at 8 fps),
on |grey(t+1) - grey(t)| averaged per pixel:

* S1 `support_change`: median over the eroded support of each pixel's mean
  absolute successive grey-level change. It is NOT sensor noise: drift, real
  support change, lighting, flicker and codec effects all enter it. (The
  2026-11-04 pilot manifest stores it under the old key `support_noise`.)
* S1 `support_change_comp`: the same after removing, per frame pair, the
  global translation of the support (phase correlation) and its median
  grey-level offset (global illumination);
* S2 `edge_spill`: mean over the first 8 px of support nearest the dynamic
  region, divided by the mean over support >= 32 px beyond where it starts;
* S2 `boundary_step`: that near-support band over dynamic 0-8 px inside its
  edge. Bands start where the support starts, past the role map's ignore band
  (`cand-edge-profile-1`); the 2026-11-04 pilot used bands measured from the
  dynamic edge itself (`-0`), which left most scenes ineligible.

A statistic that cannot be computed is recorded with its reason. There is no
real-footage band yet, so this measures *separability* from a constructed
control, not realism. Candidate identities below; read-only.

    python scripts/pilot_support_realism.py --videos <list.tsv> --controls <dir> \
        --modes paste,paste_residual --static <dir> --label <cell> --out <json>
"""

import argparse
import hashlib
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
from audit_de_precision import boot_ci  # noqa: E402

ROOT = _paths.ROOT
IDENTITY = {"support_change": "cand-support-change-0",
            "support_change_comp": "cand-support-change-comp-0",
            "edge_profile": "cand-edge-profile-1",   # -0 measured bands from the dynamic edge
            "edge_profile_guarded": "cand-edge-profile-2"}
# cand-edge-profile-2: the -1 ratios, abstaining when the denominator band's mean activity is
# below the codec floor. The floor was fixed before use from development controls: 41 frozen
# controls re-encoded with libx264 CRF 18 decode to 0.000 grey levels median successive change,
# and the lowest 5% of pass-through originals move 2.7 (manifest/realism_dev_2026_11_05/
# replay_scenetether.json). Below the floor the ratio measures codec noise, not spill.
ACT_FLOOR = 0.5   # grey levels, mean absolute successive change
STATS = ("support_change", "support_change_comp", "edge_spill", "boundary_step", "edge_spill_2",
         "boundary_step_2")
MIN_PX = 200
PHASE_MIN_RESPONSE = 0.05   # not calibrated; recorded in every report
TEXTURE_MIN = 2.0           # grey levels; below this the support cannot be registered
LATE = 0.12


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
NEAR, FAR = 8, 32           # px at 832x480


class Abstain(Exception):
    """A statistic cannot be computed; the message is the recorded reason."""


def late_grey(path):
    """Late-window grey frames (float64) sampled at 8 fps, and the sampling actually used."""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not cap.isOpened() or not np.isfinite(fps) or fps <= 0:
        raise Abstain(f"cannot decode or no frame rate: {path}")
    step = max(1, round(fps / C.SAMPLE_FPS))
    grey, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if i % step == 0:
            grey.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float64))
        i += 1
    cap.release()
    w = max(2, int(len(grey) * LATE))
    if len(grey) < 2 * w:
        raise Abstain(f"{i} frames decoded, too few for a late window")
    info = dict(native_fps=float(fps), step=step, effective_fps=float(fps / step),
                frames_decoded=i, frames_sampled=len(grey), window_frames=w)
    return np.stack(grey[-w:]), info


def late_activity(g):
    """Per-pixel mean |grey(t+1) - grey(t)|."""
    return np.abs(np.diff(g, axis=0)).mean(0)


def compensated_activity(g, sup):
    """As late_activity, after removing each pair's support translation and median grey offset.

    Translation comes from phase correlation on the mean-subtracted, windowed
    support. A support with grey std below TEXTURE_MIN abstains. A pair is
    rejected when the correlation peak is non-finite or below PHASE_MIN_RESPONSE
    (low texture). Pixels the shift brings in from outside the frame are not
    observed and are excluded. Rotation, zoom and spatially varying light are
    NOT removed. Returns (per-pixel mean over accepted pairs, NaN where a pixel
    was not observed in every accepted pair; info).
    """
    win = cv2.createHanningWindow(g.shape[1:][::-1], cv2.CV_64F) * sup
    acc, cnt = np.zeros(g.shape[1:]), np.zeros(g.shape[1:])
    ones = np.ones(g.shape[1:])
    rejected, responses = 0, []
    if np.median(g.std(axis=(1, 2), where=np.broadcast_to(sup, g.shape))) < TEXTURE_MIN:
        raise Abstain(f"support grey std below {TEXTURE_MIN}: too little texture to register")
    for a, b in zip(g[:-1], g[1:]):
        # Mean-subtracted inside the support, so the fixed mask edge carries no signal.
        (dx, dy), r = cv2.phaseCorrelate((a - a[sup].mean()) * win, (b - b[sup].mean()) * win)
        if not (np.isfinite(r) and np.isfinite(dx) and np.isfinite(dy)) or r < PHASE_MIN_RESPONSE:
            rejected += 1
            continue
        responses.append(r)
        M = np.float64([[1, 0, -dx], [0, 1, -dy]])
        back = cv2.warpAffine(b, M, b.shape[::-1], borderMode=cv2.BORDER_CONSTANT)
        valid = cv2.warpAffine(ones, M, b.shape[::-1], borderMode=cv2.BORDER_CONSTANT) > 0.999
        d = back - a
        acc += np.where(valid, np.abs(d - np.median(d[sup & valid])), 0)
        cnt += valid
    n = len(g) - 1
    info = dict(pairs=n, pairs_rejected=rejected, phase_min_response=PHASE_MIN_RESPONSE,
                texture_min=TEXTURE_MIN,
                response_median=float(np.median(responses)) if responses else None)
    if n - rejected < max(1, n // 2):
        raise Abstain(f"phase correlation rejected {rejected}/{n} pairs")
    out = np.full(g.shape[1:], np.nan)
    full = cnt == n - rejected
    out[full] = acc[full] / cnt[full]
    return out, info


def stats(act, dyn, sup, act_comp=None):
    out, why = {}, {}
    core = C.erode(sup)
    if core.sum() < MIN_PX:
        why["support_change"] = why["support_change_comp"] = \
            f"eroded support {int(core.sum())} px < {MIN_PX}"
    else:
        out["support_change"] = float(np.median(act[core]))
        if act_comp is not None:
            obs = core & np.isfinite(act_comp)
            if obs.sum() < MIN_PX:
                why["support_change_comp"] = f"observed eroded support {int(obs.sum())} px < {MIN_PX}"
            else:
                out["support_change_comp"] = float(np.median(act_comp[obs]))
    if not dyn.any():
        why["edge_spill"] = why["boundary_step"] = "no dynamic region"
    else:
        d_out = cv2.distanceTransform((~dyn).astype(np.uint8), cv2.DIST_L2, 5)
        d_in = cv2.distanceTransform(dyn.astype(np.uint8), cv2.DIST_L2, 5)
        # Role maps keep an ignore band between support and dynamic (3-108 px on
        # the v2 masks), so bands are measured from where the support starts.
        gap = float(d_out[sup].min()) if sup.any() else 0.0
        out["support_gap_px"] = gap
        near = sup & (d_out <= gap + NEAR)
        far = sup & (d_out >= gap + FAR)
        inner = dyn & (d_in <= NEAR)
        if near.sum() >= MIN_PX and far.sum() >= MIN_PX:
            out["edge_spill"] = float(act[near].mean() / max(act[far].mean(), 1e-6))
        else:
            why["edge_spill"] = f"near {int(near.sum())} / far {int(far.sum())} px < {MIN_PX}"
        if near.sum() >= MIN_PX and inner.sum() >= MIN_PX:
            out["boundary_step"] = float(act[near].mean() / max(act[inner].mean(), 1e-6))
        else:
            why["boundary_step"] = f"near {int(near.sum())} / inner {int(inner.sum())} px < {MIN_PX}"
        # cand-edge-profile-2: same bands, but a denominator under the codec floor abstains
        for key, num, den, name in (("edge_spill_2", near, far, "far support"),
                                    ("boundary_step_2", near, inner, "inner dynamic")):
            if num.sum() < MIN_PX or den.sum() < MIN_PX:
                why[key] = f"{name} band or near band < {MIN_PX} px"
            elif act[den].mean() < ACT_FLOOR:
                why[key] = f"{name} activity {act[den].mean():.3f} < codec floor {ACT_FLOOR}"
            else:
                out[key] = float(act[num].mean() / act[den].mean())
    if why:
        out["abstain"] = why
    return out


def measure(path, dyn, sup):
    """Statistics for one video; a video that cannot be measured is returned as an abstention."""
    try:
        g, sampling = late_grey(path)
    except Abstain as e:
        return {"abstain": {s: str(e) for s in STATS}}
    try:
        comp, comp_info = compensated_activity(g, sup)
    except Abstain as e:
        comp, comp_info = None, {"abstain": str(e)}
    out = stats(late_activity(g), dyn, sup, comp)
    if comp is None:
        out.setdefault("abstain", {})["support_change_comp"] = comp_info["abstain"]
    out.update(sampling=sampling, compensation=comp_info)
    return out


def verify_chain(path, chain):
    """Refuse a control whose sidecar is missing or whose parent/source/mask/output hashes differ."""
    side = path[:-4] + ".json"
    if not os.path.exists(side):
        raise SystemExit(f"{path}: no provenance sidecar; rebuild with build_composite_controls.py")
    prov = json.load(open(side))
    bad = [k for k in chain if prov.get(k) != chain[k]]
    if prov.get("output_sha256") != sha256(path):
        bad.append("output_sha256")
    if bad:
        raise SystemExit(f"{path}: provenance mismatch in {bad}")


def verify_reference(path):
    """Refuse a reference whose sidecar does not record an unmodified pass-through re-encode."""
    mode = json.load(open(path[:-4] + ".json")).get("mode", "")
    if not str(mode).startswith("passthrough"):
        raise SystemExit(f"{path}: reference sidecar records mode {mode!r}, not a pass-through")


STATIC_MIN_PSNR = 30.0   # dB vs source for both the first and the last frame; H.264 stills reach 39-40


def verify_static(path, source_path):
    """Static clips have no sidecar: check by content that the clip is the source, still at its end."""
    cap = cv2.VideoCapture(path)
    ok, first = cap.read()
    last = first
    while ok:
        ok, f = cap.read()
        if ok:
            last = f
    cap.release()
    src = cv2.imread(source_path)
    if first is None or src is None or first.shape != src.shape:
        raise SystemExit(f"{path}: static clip unreadable or not the source's size")
    def psnr(x):
        mse = float(np.mean((x.astype(np.float32) - src.astype(np.float32)) ** 2))
        return 10 * np.log10(255.0 ** 2 / max(mse, 1e-10))
    got = dict(psnr_first_db=psnr(first), psnr_last_db=psnr(last))
    if min(got.values()) < STATIC_MIN_PSNR:
        raise SystemExit(f"{path}: not a still of {source_path} ({got})")
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True, help="tsv: scene id, original video path")
    ap.add_argument("--controls", required=True, help="build_composite_controls.py output dir")
    ap.add_argument("--modes", default="paste")
    ap.add_argument("--reference", choices=("passthrough", "original"), default="passthrough")
    ap.add_argument("--reference-mode", default="passthrough",
                    help="controls subdirectory holding the pass-through, e.g. passthrough_crf18 "
                         "(scripts/native_controls.py)")
    ap.add_argument("--static", required=True)
    ap.add_argument("--label", required=True, help="entrant cell, recorded in the report")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.exists(a.out):
        raise SystemExit(f"{a.out} exists; reports are never overwritten")
    modes = a.modes.split(",")
    masks = os.path.join(_paths.resolve("method_repo"), "results/factorial/source_masks")
    rows = []
    for line in open(a.videos):
        sid, video = line.rstrip("\n").split("\t")
        video = video.replace("/workspace/", "/home/minar/")
        dyn, sup, lsha, _ = P.load_role_masks(os.path.join(masks, sid, "labels.png"))
        chain = dict(parent_sha256=sha256(video), mask_labels_sha256=lsha,
                     source_sha256=sha256(os.path.join(ROOT, "prompts/v2/i2v/images", f"{sid}.jpg")))
        if a.reference == "original":
            ref = video
        else:
            ref = f"{a.controls}/{a.reference_mode}/{sid}.mp4"
            verify_chain(ref, chain)
            verify_reference(ref)
        static = f"{a.static}/{sid}.mp4"
        static_check = verify_static(static, os.path.join(ROOT, "prompts/v2/i2v/images", f"{sid}.jpg"))
        row = dict(scene=sid, reference=a.reference, chain=chain, reference_sha256=sha256(ref),
                   static=measure(static, dyn, sup), static_check=static_check,
                   static_sha256=sha256(static),
                   ref=measure(ref, dyn, sup), controls={})
        for m in modes:
            path = f"{a.controls}/{m}/{sid}.mp4"
            verify_chain(path, chain)
            row["controls"][m] = dict(sha256=sha256(path), **measure(path, dyn, sup))
        rows.append(row)
        print(sid, "done", flush=True)

    summary = {}
    for m in modes:
        summary[m] = {}
        for s in STATS:
            v = [(r["ref"][s], r["controls"][m][s]) for r in rows
                 if s in r["ref"] and s in r["controls"][m]]
            if not v:
                continue
            x, y = np.array(v).T
            summary[m][s] = dict(n_eligible=len(v), n_attempted=len(rows),
                                 reference_median=float(np.median(x)),
                                 control_median=float(np.median(y)),
                                 reference_minus_control=boot_ci(x - y),
                                 frac_reference_above_control=float(np.mean(x > y)))
    rep = dict(entrant=a.label, reference=a.reference, reference_mode=a.reference_mode,
               identity=IDENTITY, late_window=LATE,
               near_px=NEAR, far_px=FAR, min_px=MIN_PX, erode_px=C.ERODE_PX,
               phase_min_response=PHASE_MIN_RESPONSE,
               sample_fps=C.SAMPLE_FPS,
               caveat="separability from constructed controls only; no real-footage band; "
                      "one entrant, one seed; development data",
               summary=summary, rows=rows)
    json.dump(rep, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

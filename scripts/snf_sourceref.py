"""Source-referenced SNF scoring, ported for SNF-Bench v2 (measurement `sourcefixed-1.0`).

Origin. A method project evaluating on SNF-Bench v2 found that legacy fBD
measures drift against the output's *own* frame 0, inside a mask each output
derives from its *own* early flow, and averages only frames that still
register. It built a scorer that fixes those three things -- shared
source-derived role masks, the source image as reference, and registration
failures reported rather than averaged away -- and parity-tested it against
SNF-Bench's call path. This module ports that scorer so SNF-Bench owns it.

What is ported, and how. The six scoring functions below are copied
**verbatim** from the upstream file by the Python parser, not retyped:

    upstream file   tools/factorial_scoring/sourcefixed_metrics.py
    upstream sha256 f4782bc63731c98b1cdd821a5ec4fbcb2eb573a6a5d6c42fe3af93a9f22e3440
    upstream commit 592747a3e28f1cb4587f828a3fc306be116f2c90

Their only external dependency is `snf_modules()`, which here imports SNF-Bench's
own `snf_task_metrics`, `snf_metrics_v11` and `snf_extra_metrics` -- the same
modules upstream imports from this repository. `tests/test_sourceref.py`
fails if any copied body drifts from the hashes in `UPSTREAM_FUNCTION_SHA256`,
and `scripts/check_sourceref_parity.py` runs both implementations on the same
clip and requires every output to be identical.

What is deliberately **not** changed, per the 2026-10-08 metric review:

* `dE_static` is the Euclidean distance between support-region *mean* colours
  in OpenCV uint8 Lab. It is not pixelwise CIEDE2000. Candidates are added
  later under new measurement identities, never by editing this one.
* windows remain 12 % of the sampled duration;
* headline compensated motion and `fBD_src` use registered frames only, with
  failures counted separately; `*_incl` and `fBD_f0` keep the v1.1
  fallback-inclusive, frame-0-referenced values for continuity.

What this module adds: role-mask loading with hashes, and records that declare
their measurement policy (`scripts/measurement.py` fields) so they can never
pool with v1.1 records.
"""

import hashlib
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths  # noqa: E402

SCORER_VERSION = "sourcefixed-1.0"          # upstream measurement identity, preserved
PORT_VERSION = "snf-sourceref-port-1"
UPSTREAM_SHA256 = "f4782bc63731c98b1cdd821a5ec4fbcb2eb573a6a5d6c42fe3af93a9f22e3440"
UPSTREAM_COMMIT = "592747a3e28f1cb4587f828a3fc306be116f2c90"
UPSTREAM_FUNCTION_SHA256 = {'to_eval_frame': 'a32b81a519fa3c332134887bb7461a81109411fee949c3c0465754523f7e5f36', 'resize_mask': '887b58208b4d3fba102b9ad8c72b38056f3f1e296ec77d2766081ede90cc4ef7', 'orb_drift_ref': '4b1684890653b229cb7f96dc6b4e76892c232be2a892c65c1fbec9fcc46d57ca', 'source_alignment': 'bbd128b93cc285ab842524ffde08236cdd29aa8b15d4439b46862f49bec12901', 'process_video_sourcefixed': '950bd1e84a5bae743474454e6ec5ede22582b9c5f77ab7cb6fdb8bde78c401aa', 'extras_sourcefixed': 'bec9730bba6f3ddc1dad2d00a47e25d1304d08fd7a4faf55a5be161f26a92bf3'}

# Measurement policy of the headline keys. `*_incl` and `fBD_f0` are kept for
# continuity and follow the v1.1 policy instead; tables must not mix the two.
POLICY = dict(
    metric_spec_version="sourcefixed-1.0",
    reference_policy="source_image",
    window_policy="frac12",
    sample_fps="8",
    failure_policy="registered_only",
)

SIZE = (832, 480)          # v2 I2V frame, pixels (w, h)
_mods = {}


def snf_modules():
    """(S, V11, E): this repository's metric modules, the ones upstream imports."""
    if not _mods:
        _paths.bootstrap_metric_imports()
        import snf_task_metrics as S       # noqa: E402
        import snf_metrics_v11 as V11      # noqa: E402
        import snf_extra_metrics as E      # noqa: E402
        _mods.update(S=S, V11=V11, E=E)
    return _mods["S"], _mods["V11"], _mods["E"]



# ---- copied verbatim from upstream (see module docstring) ----

def to_eval_frame(bgr, S):
    """Same geometry as S.read_frames: INTER_AREA resize to MAX_H rows, then BGR -> grey."""
    h, w = bgr.shape[:2]
    scale = S.MAX_H / h
    nh, nw = S.MAX_H, int(round(w * scale))
    f = cv2.resize(bgr, (nw, nh), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)


def resize_mask(mask_bool, shape_hw):
    return cv2.resize(mask_bool.astype(np.uint8), (shape_hw[1], shape_hw[0]), interpolation=cv2.INTER_NEAREST) > 0


def orb_drift_ref(ref_gray, grays, static, late_idx):
    """S.orb_drift with an explicit reference image and per-frame coverage.

    Logic of metric_code/snf_task_metrics.orb_drift (ORB 1500, cross-checked Hamming BF, RANSAC homography 3 px,
    inlier displacement median per frame, mean over frames, % of the diagonal) with `grays[0]` replaced by `ref_gray`
    and ONE strictness change: a late frame whose homography fit fails (< 8 inliers) is a registration failure and
    is excluded (v1.1 falls back to the raw displacement of all matches there). Returns (fBD or None, coverage dict
    with the abstention reason when None)."""
    H, W = ref_gray.shape
    diag = np.sqrt(H ** 2 + W ** 2)
    orb = cv2.ORB_create(nfeatures=1500)
    static_u8 = (static.astype(np.uint8)) * 255
    kp0, des0 = orb.detectAndCompute(ref_gray, static_u8)
    cov = dict(n_kp_ref=0 if des0 is None else len(kp0), frames=[], n_frames=len(late_idx), n_used=0)
    if des0 is None or len(kp0) < 12:
        cov["abstain_reason"] = f"reference has {cov['n_kp_ref']} ORB keypoints in the support (< 12)"
        return None, cov
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    disps = []
    for i in late_idx:
        kp1, des1 = orb.detectAndCompute(grays[i], static_u8)
        row = dict(i=int(i), n_kp=0 if des1 is None else len(kp1), n_matches=0, n_inliers=0, used=False)
        if des1 is None or len(kp1) < 12:
            cov["frames"].append(row)
            continue
        matches = bf.match(des0, des1)
        row["n_matches"] = len(matches)
        if len(matches) < 12:
            cov["frames"].append(row)
            continue
        pts0 = np.float32([kp0[m.queryIdx].pt for m in matches])
        pts1 = np.float32([kp1[m.trainIdx].pt for m in matches])
        Hm, inl = cv2.findHomography(pts0, pts1, cv2.RANSAC, 3.0)
        if inl is None or inl.sum() < 8:
            row["n_inliers"] = 0 if inl is None else int(inl.sum())
            row["ransac"] = False
            row["median_disp_px_raw"] = float(np.median(np.linalg.norm(pts1 - pts0, axis=1)))
            cov["frames"].append(row)
            continue                                  # registration failure: excluded (v1.1 would use raw displacements)
        inl = inl.ravel().astype(bool)
        d = np.linalg.norm(pts1[inl] - pts0[inl], axis=1)
        row["n_inliers"] = int(inl.sum())
        row["ransac"] = True
        row["median_disp_px"] = float(np.median(d))
        row["used"] = True
        disps.append(np.median(d))
        cov["frames"].append(row)
    cov["n_used"] = len(disps)
    if not disps:
        cov["abstain_reason"] = "no late frame registered to the reference (>= 12 cross-checked ORB matches in the support and a RANSAC homography with >= 8 inliers)"
        return None, cov
    return float(np.mean(disps) / diag * 100.0), cov


def source_alignment(ref_gray, frame0_gray, static, min_inliers=20, max_corner_shift=0.01):
    """Source -> emitted-frame-0 geometric check in the support (snf-bench external_masks.verify_alignment rule)."""
    H, W = ref_gray.shape
    orb = cv2.ORB_create(nfeatures=1500)
    m8 = static.astype(np.uint8) * 255
    k0, d0 = orb.detectAndCompute(ref_gray, m8)
    k1, d1 = orb.detectAndCompute(frame0_gray, m8)
    out = dict(n_kp_ref=0 if d0 is None else len(k0), n_kp_f0=0 if d1 is None else len(k1), n_matches=0,
               ransac_inliers=0, corner_shift_fraction=None, established=False, rule=f">= {min_inliers} inliers and corner shift <= {max_corner_shift}")
    if d0 is None or d1 is None or len(k0) < 4 or len(k1) < 4:
        return out
    matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d0, d1)
    out["n_matches"] = len(matches)
    if len(matches) < 4:
        return out
    p0 = np.float32([k0[m.queryIdx].pt for m in matches])
    p1 = np.float32([k1[m.trainIdx].pt for m in matches])
    Hm, inl = cv2.findHomography(p0, p1, cv2.RANSAC, 3.0)
    if Hm is None or inl is None:
        return out
    out["ransac_inliers"] = int(inl.sum())
    corners = np.float32([[0, 0], [W, 0], [W, H], [0, H]]).reshape(-1, 1, 2)
    moved = cv2.perspectiveTransform(corners, Hm).reshape(-1, 2)
    shift = float(np.linalg.norm(moved - corners.reshape(-1, 2), axis=1).mean() / np.hypot(W, H))
    out["corner_shift_fraction"] = shift
    out["established"] = bool(out["ransac_inliers"] >= min_inliers and shift <= max_corner_shift)
    return out


def process_video_sourcefixed(model, path, device, dyn_px, static_px, reference_bgr, seed=0):
    """snf_metrics_v11.process_video(external_masks=...) + source reference + coverage. See module doc.

    dyn_px / static_px: bool masks at the pixel resolution of the video (832x480); resized INTER_NEAREST to the
    evaluation frame (288 rows). reference_bgr: the source image (BGR, 832x480) or None (frame-0 reference only).
    Raises ValueError with the v1.1 wording when the masks overlap / are degenerate at the evaluation frame."""
    S, V11, _ = snf_modules()
    tens, grays = S.read_frames(path, device)
    if tens is None:
        return None
    F = len(tens)
    win = max(S.MIN_WIN, int(F * S.WIN_FRAC))
    rng = np.random.default_rng(seed)
    shape = grays[0].shape
    dyn = resize_mask(dyn_px, shape)
    static = resize_mask(static_px, shape)
    # ---- the v1.1 external-mask checks, verbatim ----
    if dyn.shape != grays[0].shape or static.shape != grays[0].shape:
        raise ValueError("external masks do not match evaluation frame")
    if np.any(dyn & static) or static.sum() < 50:
        raise ValueError("external masks overlap or have insufficient coverage")
    motion_ok = dyn.mean() >= 0.01                      # v1.1 refuses below this; we abstain on the motion metrics only
    Wpx = grays[0].shape[1]

    # ---- Pass B: vector flow -> similarity-compensated scalars (verbatim from snf_metrics_v11) ----
    P = F - 1
    stat_mag = np.zeros(P, np.float64)
    dyn_raw = np.zeros(P, np.float64)
    dyn_res = np.zeros(P, np.float64)
    modes, ratios, rots, scales = [], [], [], []
    for i in range(P):
        f = S.flow_vec(model, tens[i], tens[i + 1])
        mag = np.sqrt(f[..., 0] ** 2 + f[..., 1] ** 2)
        if static.sum() > 0:
            stat_mag[i] = mag[static].mean()
        d, mode, ratio, rot, sc = V11.estimate_similarity(f, static, rng)
        modes.append(mode)
        ratios.append(ratio)
        rots.append(rot)
        scales.append(sc)
        if dyn.sum() > 0:
            res = np.sqrt((f[..., 0] - d[..., 0]) ** 2 + (f[..., 1] - d[..., 1]) ** 2)
            dyn_raw[i] = mag[dyn].mean()
            dyn_res[i] = res[dyn].mean()
    # v1.1 values INCLUDING fallback transitions (parity with process_video; *_incl keys)
    ref = dyn_res[win:2 * win].mean() if P >= 2 * win else dyn_res[:win].mean()
    late = dyn_res[-win:].mean()
    fp = min(float(late / (ref + 1e-6)), 2.0)
    bfr = float(stat_mag.mean() / Wpx * 1000.0)
    dlr = float(stat_mag[-win:].mean() / (dyn_raw[-win:].mean() + 1e-6))
    raw_late = float(dyn_raw[-win:].mean())
    dar = float(1.0 - late / (raw_late + 1e-6))
    late_idx = list(range(F - win, F))
    ok_t = np.array([m == "similarity" for m in modes], bool)
    n_sim = int(ok_t.sum())
    # strict values: compensated quantities over successfully registered transitions only
    ref_sl = slice(win, 2 * win) if P >= 2 * win else slice(0, win)
    late_sl = slice(P - win, P)

    def strict_mean(x, sl):
        sel = ok_t[sl]
        return float(x[sl][sel].mean()) if sel.any() else None
    ref_s, late_s = strict_mean(dyn_res, ref_sl), strict_mean(dyn_res, late_sl)
    raw_late_s = strict_mean(dyn_raw, late_sl)
    fp_s = min(float(late_s / (ref_s + 1e-6)), 2.0) if (ref_s is not None and late_s is not None) else None
    dar_s = float(1.0 - late_s / (raw_late_s + 1e-6)) if (late_s is not None and raw_late_s is not None) else None
    motion_reason = None if motion_ok else f"dynamic region {dyn.mean():.4f} < 0.01 of the evaluation frame (overlay medium or empty mask)"

    # ---- fBD: frame-0 reference (v1.1 function, unchanged) and SOURCE reference (our copy with coverage) ----
    fbd_f0 = S.orb_drift(grays, static, late_idx)
    mo = lambda v: v if motion_ok else None  # noqa: E731
    result = {
        "video": os.path.basename(path),
        "fBD_f0": fbd_f0,
        "BFR": bfr,                                   # static-mask flow: no compensation involved (v1.1 formula)
        "FP": mo(fp_s), "MCFF_early": mo(ref_s), "MCFF_late": mo(late_s), "DAR_signed": mo(dar_s),   # strict (registered transitions)
        "FP_incl": mo(fp), "MCFF_early_incl": mo(float(ref)), "MCFF_late_incl": mo(float(late)), "DAR_signed_incl": mo(dar),
        "DD_raw_late": mo(raw_late),
        "drift_frac_late": mo(dlr),
        "motion_abstained": not motion_ok,
        "motion_abstain_reason": motion_reason,
        "static_frac": float(static.mean()),
        "dynamic_frac": float(dyn.mean()),
        "n_frames_sampled": F,
        "win": win,
        "compensation_mode": "similarity" if n_sim == P else "mixed",
        "similarity_frac": float(n_sim / max(1, P)),
        "registration": dict(interframe_success_frac=float(n_sim / max(1, P)), interframe_fallback_count=int(P - n_sim),
                             interframe_fallback_late_count=int((~ok_t[late_sl]).sum()), n_transitions=int(P)),
        "inlier_ratio_mean": float(np.mean(ratios)) if ratios else 0.0,
        "inlier_ratio_late_mean": float(np.mean(ratios[-win:])) if ratios else 0.0,
        "rotation_deg_mean": float(np.mean(rots)) if rots else 0.0,
        "scale_mean": float(np.mean(scales)) if scales else 1.0,
        "eval_size": [int(shape[1]), int(shape[0])],
    }
    if reference_bgr is not None:
        ref_gray = to_eval_frame(reference_bgr, S)
        if ref_gray.shape != grays[0].shape:
            raise ValueError(f"reference image maps to {ref_gray.shape}, frames are {grays[0].shape}")
        fbd_src, cov = orb_drift_ref(ref_gray, grays, static, late_idx)
        result["fBD_src"] = fbd_src
        result["fBD"] = fbd_src
        result["fBD_abstained"] = fbd_src is None
        result["fBD_abstain_reason"] = cov.get("abstain_reason")
        used = [r for r in cov["frames"] if r["used"]]
        result["registration"].update(source_success_frac=cov["n_used"] / max(1, cov["n_frames"]),
                                      source_failure_count=int(cov["n_frames"] - cov["n_used"]), n_late_frames=int(cov["n_frames"]))
        result["orb_coverage"] = dict(
            n_kp_ref=cov["n_kp_ref"], n_late_frames=cov["n_frames"], n_frames_used=cov["n_used"],
            frame_coverage=cov["n_used"] / max(1, cov["n_frames"]),
            n_kp_frame_mean=float(np.mean([r["n_kp"] for r in cov["frames"]])) if cov["frames"] else 0.0,
            n_matches_mean=float(np.mean([r["n_matches"] for r in used])) if used else 0.0,
            n_inliers_mean=float(np.mean([r["n_inliers"] for r in used])) if used else 0.0,
            n_inliers_min=int(min(r["n_inliers"] for r in used)) if used else 0,
            frames=cov["frames"])
        result["source_alignment"] = source_alignment(ref_gray, grays[0], static)
    else:
        result["fBD"] = fbd_f0
        result["fBD_abstained"] = fbd_f0 is None
    return result


def extras_sourcefixed(path, dyn_px, static_px, reference_bgr):
    """snf_extra_metrics.process with the shared pixel masks and the source as reference (see module doc)."""
    _, _, E = snf_modules()
    frames = E.read_frames(path)
    if frames is None:
        return None
    n = len(frames)
    e_idx, l_idx, w = E.early_late(n)
    Hh, Ww = frames[0].shape[:2]
    if dyn_px.shape != (Hh, Ww) or static_px.shape != (Hh, Ww):
        raise ValueError(f"pixel masks {dyn_px.shape} do not match the frames {(Hh, Ww)}")
    static, dyn = static_px, dyn_px
    if static.sum() < 50:
        raise ValueError("support has < 50 pixels")
    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    labs = {i: cv2.cvtColor(frames[i], cv2.COLOR_BGR2LAB).astype(np.float32) for i in set(e_idx) | set(l_idx)}

    def lab_mean(idx):
        return np.stack([labs[i][static] for i in idx]).reshape(-1, 3).mean(0)
    le, ll = lab_mean(e_idx), lab_mean(l_idx)
    out = dict(n_frames=n, early_window=w, static_frac=float(static.mean()), dynamic_frac=float(dyn.mean()),
               dE_static_early=float(np.linalg.norm(ll - le)), dL_static_early=float(ll[0] - le[0]) * (100.0 / 255.0))
    g0 = grays[0].astype(np.float32) / 255.0

    def psnr_vs(gref):
        ps = []
        for i in l_idx:
            gi = grays[i].astype(np.float32) / 255.0
            mse = ((gref[static] - gi[static]) ** 2).mean()
            ps.append(10 * np.log10(1.0 / max(mse, E.EPS)))
        return float(np.mean(ps))
    out["idPSNR_late_f0"] = psnr_vs(g0)
    if reference_bgr is not None:
        if reference_bgr.shape[:2] != (Hh, Ww):
            raise ValueError("reference image size differs from the frames")
        lab_src = cv2.cvtColor(reference_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)[static].mean(0)
        out["dE_static_src"] = float(np.linalg.norm(ll - lab_src))
        out["dL_static_src"] = float(ll[0] - lab_src[0]) * (100.0 / 255.0)
        out["dE_static_f0"] = float(np.linalg.norm(ll - labs.get(0, cv2.cvtColor(frames[0], cv2.COLOR_BGR2LAB).astype(np.float32))[static].mean(0)))
        gs = cv2.cvtColor(reference_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        out["idPSNR_late_src"] = psnr_vs(gs)
        out["idPSNR_src_f0"] = float(10 * np.log10(1.0 / max(((gs[static] - g0[static]) ** 2).mean(), E.EPS)))
        out["dE_static"], out["idPSNR_late"] = out["dE_static_src"], out["idPSNR_late_src"]
    else:
        out["dE_static"], out["idPSNR_late"] = out["dE_static_early"], out["idPSNR_late_f0"]
    # dynamic frame-diff persistence in the shared dynamic mask (cheap; same formula as the extras); None if no dynamic region
    if dyn.sum() > 0:
        dyn_fd = np.array([np.abs(grays[i + 1].astype(np.float32) - grays[i].astype(np.float32))[dyn].mean() for i in range(n - 1)])
        early_fd, late_fd = dyn_fd[:w].mean(), dyn_fd[-w:].mean()
        out["FDP"] = float(min(late_fd / (early_fd + E.EPS), 2.0))
    else:
        out["FDP"] = None
    return out


# ---- SNF-Bench wrapper (not upstream) -------------------------------------

def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_role_masks(labels_png):
    """Four-region role map -> (dynamic, support) bool masks at 832x480.

    Labels follow docs/SNF_V2_MASK_PROTOCOL.md: 0 ignore/uncertain, 1 rigid
    support (static metrics only), 2 dynamic (motion metrics only), 3 overlay
    (enters nothing). Anything else is refused rather than guessed.
    """
    lab = cv2.imread(labels_png, cv2.IMREAD_GRAYSCALE)
    if lab is None:
        raise FileNotFoundError(labels_png)
    if lab.shape != (SIZE[1], SIZE[0]):
        raise ValueError(f"{labels_png}: role map is {lab.shape[::-1]}, expected {SIZE}")
    bad = set(np.unique(lab).tolist()) - {0, 1, 2, 3}
    if bad:
        raise ValueError(f"{labels_png}: labels outside {{0,1,2,3}}: {sorted(bad)}")
    regions = {name: float((lab == v).mean())
               for name, v in (("ignore", 0), ("support", 1), ("dynamic", 2), ("overlay", 3))}
    return lab == 2, lab == 1, _sha256(labels_png), regions


def score_video(model, video, labels_png, source_image, device, *, native_fps=16.0,
                mask_set, mask_version, mask_review_scope, prompt_set="v2"):
    """One SNF-Bench record for one video under `sourcefixed-1.0`.

    `mask_set` identifies the whole role-mask set (e.g. its manifest sha256) and
    `mask_review_scope` states who reviewed it (`none`, `ai`,
    `human-independent`). Both are required: the 2026-10-08 review found masks
    labelled "approved" after AI-only review, and an unstated scope is exactly
    how that label would graduate to benchmark truth.
    """
    import registry
    dyn, sup, labels_sha, regions = load_role_masks(labels_png)
    src = cv2.imread(source_image)
    if src is None or src.shape[:2] != (SIZE[1], SIZE[0]):
        raise ValueError(f"{source_image}: source must be {SIZE}")
    r = process_video_sourcefixed(model, video, device, dyn, sup, src, seed=0)
    if not r:
        raise RuntimeError(f"{video}: no frames decoded")
    ex = extras_sourcefixed(video, dyn, sup, src)
    r.update({k: v for k, v in ex.items() if k not in r})
    for k, v in r.items():
        if isinstance(v, float) and not np.isfinite(v):
            raise ValueError(f"{video}: non-finite {k}={v}")
    eff = registry.effective_fps(native_fps)
    r.update(
        NBF=float(r["BFR"]) * eff, DLR=r.get("drift_frac_late"), DAR=r.get("DAR_signed"),
        native_fps=float(native_fps), effective_fps=eff,
        video_sha256=_sha256(video), source_sha256=_sha256(source_image),
        labels_sha256=labels_sha, mask_region_frac_px=regions,
        mask_set=mask_set, mask_version=mask_version, mask_review_scope=mask_review_scope,
        flow_backbone="RAFT", feature_backbone="ORB", prompt_set=prompt_set,
        scorer_version=SCORER_VERSION, port_version=PORT_VERSION,
        upstream_sha256=UPSTREAM_SHA256, upstream_commit=UPSTREAM_COMMIT,
        **POLICY)
    return r

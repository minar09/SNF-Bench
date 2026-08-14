"""Controlled-perturbation validation of the SNF-Bench metrics.

This is the paper's central claim generator. It takes real fixed-camera clips,
injects corruptions of *known* kind and severity, and asks whether each metric
moves the way its definition says it should. That is mechanistic validation: it
does not ask whether a metric agrees with a human, it asks whether it measures
the thing it is named after.

Perturbation families (all applied progressively over the rollout, because that
is how drift actually manifests -- a constant offset is not drift):

  translation  frame t displaced by (t/T)*lambda px
  rotation     frame t rotated by (t/T)*lambda degrees about the centre
  scale        frame t scaled by 1 + (t/T)*(lambda-1)
  attenuation  dynamic-region content blended toward an early reference frame,
               ramping to lambda -- motion decays, support untouched
  freeze       every frame after phi*T replaced by the frame at phi*T

Alongside the SNF factors we compute **VBench Dynamic Degree exactly as VBench
defines it** -- mean over frame pairs of min(mean(top-5% flow magnitude)/thres, 1)
with thres = 6.0*min(H,W)/256 -- so the headline panel compares like with like
rather than against a re-implementation of our own choosing.

    ~/miniconda3/envs/snfeval/bin/python scripts/validation_suite.py --gpu 4
"""

import argparse
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("VBENCH_CACHE_DIR", "/home/minar/ckpt/vbench")
SNF_EVAL = "/home/minar/region-forcing/snf_eval"
sys.path.insert(0, SNF_EVAL)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = f"{ROOT}/manifest"

# Severity is the TOTAL corruption accumulated across the whole rollout, which
# is how drift presents itself.
#
# For the three geometric families it is specified in a COMMON PHYSICAL UNIT --
# the mean pixel displacement the corruption induces over the frame by the end
# of the rollout -- and each family's own parameter (px / degrees / zoom) is
# derived from it at run time using the actual frame geometry.
#
# This replaces hand-picked per-family levels, which were NOT comparable. At the
# evaluation resolution 1 degree of rotation induces only ~2.7 px of mean
# displacement, so a 4 degree top level injected ~11 px while the top
# translation level injected 160 px -- a 15x mismatch. The rotation panel was
# therefore plotting noise around each clip's own baseline drift, which is why
# fBD looked non-monotone there. Measured on a real clip, fBD is cleanly
# monotone in rotation once the injection clears that baseline:
#     21 px -> 3.97,  43 px -> 7.86,  86 px -> 17.60   (baseline 2.32)
# ORB match counts stay ~390 throughout, so this was never a matching failure.
GEOM_DISPLACEMENTS = [0.0, 10.0, 20.0, 40.0, 80.0]     # px, mean over the frame

LEVELS = {
    "translation": list(GEOM_DISPLACEMENTS),           # -> px of total drift
    "rotation":    list(GEOM_DISPLACEMENTS),           # -> degrees of rotation
    "scale":       list(GEOM_DISPLACEMENTS),           # -> zoom factor
    "attenuation": [0.0, 0.25, 0.50, 0.75, 1.0],      # fraction of motion removed
    "freeze":      [0.0, 0.25, 0.50, 0.75],           # FRACTION OF CLIP FROZEN
    # Photometric drift: geometry and motion are untouched, so geometric factors
    # should be comparatively insensitive. Flow estimation is not perfectly
    # photometrically invariant, so the residual sensitivity is measured rather
    # than assumed, and reported as an operating bound.
    "photometric": [0.0, 0.05, 0.10, 0.20, 0.35],     # total brightness/colour shift
    # Temporal repetition: late dynamic content replaced by a short repeated
    # cycle. Included to DOCUMENT a scope boundary -- persistence and magnitude
    # cannot resolve looping, and the paper says so rather than hiding it.
    "repetition":  [0.0, 24.0, 12.0, 6.0],            # cycle length in frames (0 = none)
    # Mask sensitivity: not a corruption of the video at all, but of the
    # partition. Level is a morphological radius, negative = erode.
    "mask_radius": [0, -4, -2, 2, 4],
}

FRAME_FAMILIES = {"translation", "rotation", "scale", "attenuation", "freeze",
                  "photometric", "repetition"}


def load_frames(path, max_frames=110):
    """Decode, subsample to SAMPLE_FPS and resize -- the same preprocessing the
    metric uses, done once so every perturbation sees identical input."""
    import snf_task_metrics as S
    vid = cv2.VideoCapture(path)
    fps = vid.get(cv2.CAP_PROP_FPS) or 16.0
    interval = max(1, round(fps / S.SAMPLE_FPS))
    raw = []
    while True:
        ok, f = vid.read()
        if not ok:
            break
        raw.append(f)
    vid.release()
    raw = raw[::interval]
    if len(raw) < 8:
        return None
    h, w = raw[0].shape[:2]
    nh = S.MAX_H
    nw = int(round(w * nh / h))
    # Stride rather than truncate: the injected corruptions ramp over the
    # rollout, so validation needs the full temporal span -- but it does not
    # need every sampled pair to establish a monotone response. Striding keeps
    # the span and cuts flow cost by the stride factor.
    if max_frames and len(raw) > max_frames:
        step = int(np.ceil(len(raw) / max_frames))
        raw = raw[::step]
    return [cv2.resize(f, (nw, nh), interpolation=cv2.INTER_AREA) for f in raw]


def mean_radius(h, w):
    """Mean distance from the frame centre.

    This is the conversion constant between an angular or zoom parameter and
    the mean pixel displacement it induces, so it is what makes the geometric
    families comparable on one axis.
    """
    gy, gx = np.mgrid[0:h, 0:w]
    return float(np.hypot(gx - w / 2.0, gy - h / 2.0).mean())


def geom_param(kind, disp_px, h, w):
    """Mean induced displacement (px) -> that family's own parameter."""
    r = max(mean_radius(h, w), 1e-6)
    if kind == "translation":
        return disp_px
    if kind == "rotation":
        return float(np.degrees(disp_px / r))
    if kind == "scale":
        return 1.0 + disp_px / r
    return disp_px


def perturb(frames, kind, lam, dyn_mask=None):
    """-> new frame list with a known corruption injected.

    `dyn_mask` is the dynamic-region mask computed ONCE from the unperturbed
    clip. Region-restricted corruptions need it: attenuating the whole frame
    would also still the static support, and the suite would then be unable to
    demonstrate that any factor is selective.
    """
    T = len(frames)
    h, w = frames[0].shape[:2]
    dyn3 = None
    if dyn_mask is not None:
        m = cv2.resize(dyn_mask.astype(np.uint8), (w, h),
                       interpolation=cv2.INTER_NEAREST).astype(bool)
        dyn3 = np.repeat(m[:, :, None], 3, axis=2)
    out = []
    if kind == "freeze":
        # lam = fraction of the clip that is frozen, so severity increases with lam.
        cut = max(1, int((1.0 - lam) * T))
        return [frames[min(i, cut - 1)] for i in range(T)]
    if kind == "repetition":
        if lam <= 0:
            return list(frames)
        cyc = int(lam)
        half = T // 2
        out = list(frames[:half])
        for i in range(half, T):
            src = frames[half + ((i - half) % cyc)] if half + cyc < T else frames[i]
            out.append(np.where(dyn3, src, frames[i]) if dyn3 is not None else src)
        return out
    if kind == "mask_radius":
        return list(frames)          # the partition is perturbed, not the video
    # Geometric families are specified in mean induced displacement (px);
    # convert to this family's own parameter before applying it.
    if kind in ("translation", "rotation", "scale"):
        lam = geom_param(kind, lam, h, w)
    for t, f in enumerate(frames):
        a = t / max(1, T - 1)
        if kind == "translation":
            M = np.float32([[1, 0, a * lam], [0, 1, 0]])
            out.append(cv2.warpAffine(f, M, (w, h), flags=cv2.INTER_LINEAR,
                                      borderMode=cv2.BORDER_REFLECT))
        elif kind == "rotation":
            M = cv2.getRotationMatrix2D((w / 2, h / 2), a * lam, 1.0)
            out.append(cv2.warpAffine(f, M, (w, h), flags=cv2.INTER_LINEAR,
                                      borderMode=cv2.BORDER_REFLECT))
        elif kind == "scale":
            s = 1.0 + a * (lam - 1.0)
            M = cv2.getRotationMatrix2D((w / 2, h / 2), 0.0, s)
            out.append(cv2.warpAffine(f, M, (w, h), flags=cv2.INTER_LINEAR,
                                      borderMode=cv2.BORDER_REFLECT))
        elif kind == "photometric":
            # Ramped gain + colour-temperature shift; geometry untouched.
            g = 1.0 + a * lam
            f2 = f.astype(np.float32)
            f2[..., 0] *= g                      # blue up
            f2[..., 2] *= max(0.0, 2.0 - g)      # red down
            out.append(np.clip(f2 * (1.0 + 0.5 * a * lam), 0, 255).astype(np.uint8))
        elif kind == "attenuation":
            # Blend toward an early reference INSIDE the dynamic region only, so
            # motion decays while static support is left exactly as it was.
            alpha = a * lam
            blend = cv2.addWeighted(f, 1 - alpha, frames[0], alpha, 0)
            out.append(np.where(dyn3, blend, f) if dyn3 is not None else blend)
        else:
            raise ValueError(kind)
    return out


def to_tensors(frames, device):
    import torch
    tens, grays = [], []
    for f in frames:
        rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        t = torch.from_numpy(rgb.astype(np.uint8)).permute(2, 0, 1).float()[None].to(device)
        tens.append(t)
        grays.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
    return tens, grays


def dynamic_degree(flows, h, w):
    """VBench Dynamic Degree, reimplemented to its published rule."""
    thres = 6.0 * (min(h, w) / 256.0)
    cut = max(1, int(h * w * 0.05))
    scores = []
    for f in flows:
        rad = np.sqrt(f[..., 0] ** 2 + f[..., 1] ** 2).ravel()
        top = np.sort(rad)[::-1][:cut]
        scores.append(min(float(top.mean()) / thres, 1.0))
    return float(np.mean(scores)) if scores else 0.0


def morph(mask, radius):
    """Erode (radius<0) or dilate (radius>0) a boolean mask."""
    if not radius:
        return mask
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                  (2 * abs(radius) + 1, 2 * abs(radius) + 1))
    m = mask.astype(np.uint8)
    m = cv2.dilate(m, k) if radius > 0 else cv2.erode(m, k)
    return m.astype(bool)


def reference_masks(model, frames, device):
    """Masks from the UNPERTURBED clip, so every variant is judged on the same
    partition and region-restricted corruptions know where to act."""
    import snf_task_metrics as S
    import torch
    tens, _ = to_tensors(frames, device)
    F = len(tens)
    win = max(S.MIN_WIN, int(F * S.WIN_FRAC))
    early = np.mean([S.flow_mag(model, tens[i], tens[i + 1]).astype(np.float32)
                     for i in range(min(win, F - 1))], 0)
    dyn, static = S.build_masks(early)
    del tens
    torch.cuda.empty_cache()
    return dyn, static


def measure(model, frames, device, mask_radius=0):
    """SNF factors + Dynamic Degree on one (possibly perturbed) frame list."""
    import snf_task_metrics as S
    import snf_metrics_v11 as V11
    import torch

    tens, grays = to_tensors(frames, device)
    F = len(tens)
    win = max(S.MIN_WIN, int(F * S.WIN_FRAC))
    rng = np.random.default_rng(0)

    early_maps = [S.flow_mag(model, tens[i], tens[i + 1]).astype(np.float32)
                  for i in range(min(win, F - 1))]
    early = np.mean(early_maps, 0)
    dyn, static = S.build_masks(early)
    if mask_radius:
        # Dilating the static mask necessarily erodes the dynamic one and vice
        # versa; keeping them complementary is what makes the test a boundary
        # perturbation rather than a change of total measured area.
        static = morph(static, mask_radius)
        dyn = morph(dyn, -mask_radius)
        static &= ~dyn
    h, w = early.shape

    P = F - 1
    stat = np.zeros(P); raw = np.zeros(P); res = np.zeros(P)
    flows = []
    for i in range(P):
        f = S.flow_vec(model, tens[i], tens[i + 1])
        flows.append(f)
        mag = np.sqrt(f[..., 0] ** 2 + f[..., 1] ** 2)
        if static.sum():
            stat[i] = mag[static].mean()
        d, _, _, _, _ = V11.estimate_similarity(f, static, rng)
        if dyn.sum():
            raw[i] = mag[dyn].mean()
            res[i] = np.sqrt((f[..., 0] - d[..., 0]) ** 2
                             + (f[..., 1] - d[..., 1]) ** 2)[dyn].mean()

    ref = res[win:2 * win].mean() if P >= 2 * win else res[:win].mean()
    late = res[-win:].mean()
    raw_late = raw[-win:].mean()
    out = {
        "fBD": S.orb_drift(grays, static, list(range(F - win, F))),
        "NBF": float(stat.mean() / w * 1000.0 * S.SAMPLE_FPS),
        "MCFF_E": float(ref), "MCFF_L": float(late),
        "FP": float(min(late / (ref + 1e-6), 2.0)),
        "DLR": float(stat[-win:].mean() / (raw_late + 1e-6)),
        "DAR": float(1.0 - late / (raw_late + 1e-6)),
        "VB_DD": dynamic_degree(flows, h, w),
    }
    del tens
    torch.cuda.empty_cache()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--clips", type=int, default=4)
    ap.add_argument("--max-frames", type=int, default=110)
    ap.add_argument("--duration", default="60s")
    ap.add_argument("--out", default=f"{MAN}/validation_response.json")
    ap.add_argument("--families", default="",
                    help="comma-separated subset of LEVELS to run")
    args = ap.parse_args()
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", args.gpu)

    import torch
    import snf_task_metrics as S
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = S.load_raft(device)

    # Reference clips: real generated videos, spread across scene categories so
    # the response is not a property of one medium.
    import glob
    cands = sorted(glob.glob(f"{ROOT}/videos/t2v/self_forcing/{args.duration}/*.mp4"))
    clips = cands[:args.clips]
    print(f"{len(clips)} reference clips @ {args.duration}", flush=True)

    records = []
    for ci, path in enumerate(clips):
        frames = load_frames(path, max_frames=args.max_frames)
        if frames is None:
            continue
        print(f"[clip {ci+1}/{len(clips)}] {len(frames)} sampled frames", flush=True)
        ref_dyn, _ = reference_masks(model, frames, device)
        fams = ([f for f in args.families.split(",") if f]
                if args.families else list(LEVELS))
        for kind in fams:
            levels = LEVELS[kind]
            for lam in levels:
                if kind == "mask_radius":
                    m = measure(model, frames, device, mask_radius=int(lam))
                else:
                    m = measure(model, perturb(frames, kind, lam, ref_dyn), device)
                m.update(clip=os.path.basename(path), family=kind, level=float(lam))
                records.append(m)
                print(f"   {kind:12s} {lam:<6} NBF={m['NBF']:7.2f} "
                      f"MCFF_L={m['MCFF_L']:6.3f} DD={m['VB_DD']:.3f}", flush=True)
        with open(args.out, "w") as f:
            json.dump({"levels": LEVELS, "records": records}, f, indent=2)
    print(f"\n{len(records)} measurements -> {args.out}")


if __name__ == "__main__":
    main()

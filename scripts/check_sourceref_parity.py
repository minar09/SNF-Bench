#!/usr/bin/env python3
"""Parity: the ported scorer must reproduce upstream exactly on a real clip.

Runs, in one process and on the same RAFT weights:

  A  upstream  process_video_sourcefixed + extras_sourcefixed (the method project)
  B  port      the same two functions from scripts/snf_sourceref.py
  C  v1.1      snf_metrics_v11.process_video(external_masks=...) -- B with no
               source reference must reproduce it on the `*_incl` keys, which
               is the upstream claim that the copy only *adds* to SNF's path.

A and B must be identical to the last digit on every key (|d| = 0). Writes
manifest/sourceref_parity.json with the clip, mask, source and code hashes.

    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 python scripts/check_sourceref_parity.py \
        --scene ial01 --clip <5s prefix mp4>            # CPU
"""

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths              # noqa: E402
import snf_sourceref as P  # noqa: E402

ROOT = _paths.ROOT
OUT = os.path.join(ROOT, "manifest", "sourceref_parity.json")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def diff(a, b, path=""):
    """Every leaf where a and b differ, exact comparison (floats included)."""
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((f"{path}.{k}", "missing in " + ("A" if k not in a else "B")))
            else:
                out += diff(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, f"len {len(a)} vs {len(b)}"))
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
    elif a != b and not (isinstance(a, float) and isinstance(b, float) and np.isnan(a) and np.isnan(b)):
        out.append((path, f"{a!r} vs {b!r}"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--clip", required=True)
    ap.add_argument("--device", default="cpu")
    a = ap.parse_args()

    import cv2
    import torch
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))

    method = _paths.resolve("method_repo")
    up_dir = os.path.join(method, "tools", "factorial_scoring")
    sys.path.insert(0, up_dir)
    import sourcefixed_metrics as UP   # noqa: E402

    labels = os.path.join(method, "results/factorial/source_masks", a.scene, "labels.png")
    source = os.path.join(ROOT, "prompts/v2/i2v/images", f"{a.scene}.jpg")
    frozen = json.load(open(os.path.join(method, "results/snf_v2/TEST_SPLIT_FROZEN.json")))
    want_img = next((p.get("image_sha256") for p in frozen["pairs"]
                     if p.get("id") == a.scene or p.get("scene_id") == a.scene), None)
    if want_img and want_img != sha(source):
        raise SystemExit(f"{a.scene}: snf-bench source image differs from the method's frozen split")

    S, V11, _ = P.snf_modules()
    model = S.load_raft(a.device)
    dyn, sup, labels_sha, _ = P.load_role_masks(labels)
    src = cv2.imread(source)

    t = time.time()
    A = UP.process_video_sourcefixed(model, a.clip, a.device, dyn, sup, src, seed=0)
    A.update({k: v for k, v in UP.extras_sourcefixed(a.clip, dyn, sup, src).items() if k not in A})
    tA = time.time() - t
    t = time.time()
    B = P.process_video_sourcefixed(model, a.clip, a.device, dyn, sup, src, seed=0)
    B.update({k: v for k, v in P.extras_sourcefixed(a.clip, dyn, sup, src).items() if k not in B})
    tB = time.time() - t
    d_ab = diff(A, B)

    # C: v1.1 call path with the same masks; B without a source reference must match on *_incl
    t = time.time()
    shape = S.read_frames(a.clip, a.device)[1][0].shape
    C = V11.process_video(model, a.clip, a.device, seed=0,
                          external_masks=(P.resize_mask(dyn, shape), P.resize_mask(sup, shape)),
                          mask_provenance=dict(mask_version="parity"))
    B0 = P.process_video_sourcefixed(model, a.clip, a.device, dyn, sup, None, seed=0)
    tC = time.time() - t
    keymap = {"fBD": "fBD", "BFR": "BFR", "FP": "FP_incl", "MCFF_early": "MCFF_early_incl",
              "MCFF_late": "MCFF_late_incl", "DD_raw_late": "DD_raw_late",
              "drift_frac_late": "drift_frac_late", "DAR_signed": "DAR_signed_incl"}
    d_v11 = [(k, f"{C.get(k)!r} vs {B0.get(v)!r}") for k, v in keymap.items()
             if k in C and C.get(k) != B0.get(v)]

    rep = dict(
        scene=a.scene, clip=os.path.relpath(a.clip, method) if a.clip.startswith(method) else a.clip,
        clip_sha256=sha(a.clip), labels_sha256=labels_sha, source_sha256=sha(source),
        device=a.device, torch_threads=torch.get_num_threads(),
        upstream_sha256=P.UPSTREAM_SHA256, upstream_commit=P.UPSTREAM_COMMIT,
        port_sha256=sha(P.__file__),
        n_keys_compared=len(A), port_vs_upstream_differences=len(d_ab),
        v11_keys_compared=sum(1 for k in keymap if k in C), v11_differences=len(d_v11),
        examples=[f"{p}: {m}" for p, m in (d_ab + d_v11)[:10]],
        seconds=dict(upstream=round(tA, 1), port=round(tB, 1), v11_check=round(tC, 1)),
        headline=dict((k, B.get(k)) for k in ("fBD_src", "fBD_f0", "dE_static_src",
                                               "idPSNR_late_src", "FP", "MCFF_late", "BFR")),
        verdict="PASS" if not d_ab and not d_v11 else "FAIL")
    json.dump(rep, open(OUT, "w"), indent=1)
    print(json.dumps({k: rep[k] for k in ("scene", "n_keys_compared", "port_vs_upstream_differences",
                                          "v11_keys_compared", "v11_differences", "seconds", "verdict")}, indent=1))
    for e in rep["examples"]:
        print("  ", e)
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

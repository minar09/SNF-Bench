"""Crash-isolated worker for the SNF task-metric sweep.

Processes a list of videos, writing each result to its own file *immediately*
after it is computed. If the process dies -- CUDA OOM, poisoned cuDNN context,
anything -- every video already finished survives, and the orchestrator restarts
a fresh process on whatever is left. That is what makes the sweep resumable
rather than all-or-nothing, and it is why the original single-process sweep lost
29 of 30 CausVid videos to one cascading fault.

Two contracts this worker upholds that the original did not:

  1. A failure is NEVER written into the results stream. It goes to a separate
     file with a `.error.json` suffix. A metrics file therefore contains only
     measurements, so counting its records is the same as counting valid data.
  2. Every result carries provenance: spec version, fps, resolution, mask and
     compensation mode, backbone. This is what makes a paper/code parity test
     possible at all.

Optionally persists subsampled flow correspondences (--persist) so that the
similarity-compensation merge (METRIC_SPEC v1.1 §3) becomes a post-processing
pass over stored fields instead of a second GPU sweep over 1,881 videos.

Not run directly -- see scripts/rerun_metrics.py.
"""

import argparse
import json
import os
import sys
import traceback

import numpy as np

SPEC_VERSION = "1.0"
SNF_EVAL = "/home/minar/region-forcing/snf_eval"
sys.path.insert(0, SNF_EVAL)

# load_raft() resolves the RAFT checkpoint under VBENCH_CACHE_DIR, defaulting to
# ~/.cache/vbench, which does not exist on this machine. Pin it so the worker is
# not silently dependent on the caller's environment.
os.environ.setdefault("VBENCH_CACHE_DIR", "/home/minar/ckpt/vbench")

# Windows the frozen metrics actually read; only these need persisting.
PERSIST_POINTS = 4000        # subsampled pixels per region per frame


def atomic_write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def video_meta(path):
    import cv2
    c = cv2.VideoCapture(path)
    m = dict(fps=float(c.get(cv2.CAP_PROP_FPS)),
             n_frames=int(c.get(cv2.CAP_PROP_FRAME_COUNT)),
             width=int(c.get(cv2.CAP_PROP_FRAME_WIDTH)),
             height=int(c.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    c.release()
    return m


def persist_fields(model, path, device, out_npz):
    """Store subsampled (x, y, ux, uy) inside static and dynamic masks for the
    early and late windows, at fp16.

    Rationale for subsampling rather than dense storage: the affine recompute
    needs correspondences to fit T_t and dynamic-region vectors to re-evaluate
    MCFF, but both are means over large regions, so a few thousand sampled
    pixels per frame estimate them to far better precision than the flow
    estimator itself. Dense fp16 flow would be ~1.5 GB per 60 s clip; this is
    a few MB, which matters on a volume at 97%.
    """
    import snf_task_metrics as S
    import torch

    # NOTE: read_frames returns (tens, grays) -- tensors FIRST -- and it already
    # subsamples to S.SAMPLE_FPS, so F counts SAMPLED frames, not container
    # frames. Window extents must use the module's own constants, not a
    # re-derived 0.12, or the persisted windows will not be the windows the
    # metrics actually read.
    tens, _grays = S.read_frames(path, device)
    if tens is None:
        raise RuntimeError("read_frames returned no frames")
    F = len(tens)
    win = max(S.MIN_WIN, int(F * S.WIN_FRAC))

    early_maps = [S.flow_mag(model, tens[i], tens[i + 1]).astype(np.float32)
                  for i in range(min(win, F - 1))]
    early = np.mean(early_maps, 0)
    dyn, static = S.build_masks(early)

    idx_e = list(range(0, min(win, F - 1)))
    idx_l = list(range(max(0, F - 1 - win), F - 1))
    rng = np.random.default_rng(0)

    def sample(mask):
        ys, xs = np.nonzero(mask)
        if len(xs) == 0:
            return None
        take = min(PERSIST_POINTS, len(xs))
        pick = rng.choice(len(xs), size=take, replace=False)
        return ys[pick], xs[pick]

    # Flow is recomputed once per frame index and shared across both regions,
    # so the persistence pass costs one extra RAFT call per persisted frame
    # rather than two.
    store = {}
    picks = {r: sample(m) for r, m in (("static", static), ("dyn", dyn))}
    for tag, idxs in (("early", idx_e), ("late", idx_l)):
        rows = {r: [] for r in picks if picks[r] is not None}
        for i in idxs:
            f = S.flow_vec(model, tens[i], tens[i + 1])
            for r, pk in picks.items():
                if pk is None:
                    continue
                py, px = pk
                rows[r].append(np.stack([px, py, f[py, px, 0], f[py, px, 1]], 1))
        for r, v in rows.items():
            if v:
                store[f"{tag}_{r}"] = np.asarray(v, dtype=np.float16)
    store["meta"] = np.asarray([F, win, early.shape[1], early.shape[0],
                                int(S.SAMPLE_FPS)], dtype=np.int32)
    os.makedirs(os.path.dirname(out_npz), exist_ok=True)
    np.savez_compressed(out_npz, **store)
    del tens
    torch.cuda.empty_cache()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True, help="file holding one video path per line")
    ap.add_argument("--staging", required=True)
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--persist", default="")
    args = ap.parse_args()

    os.environ.setdefault("CUDA_VISIBLE_DEVICES", args.gpu)
    import torch
    import snf_task_metrics as S

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = S.load_raft(device)
    os.makedirs(args.staging, exist_ok=True)

    todo = [l.strip() for l in open(args.videos) if l.strip()]
    for v in todo:
        name = os.path.basename(v)
        done = os.path.join(args.staging, name + ".json")
        err = os.path.join(args.staging, name + ".error.json")
        if os.path.exists(done):
            continue
        try:
            r = S.process_video(model, v, device)
            if not r:
                raise RuntimeError("process_video returned empty")
            r.update(video_meta(v))
            r["metric_spec_version"] = SPEC_VERSION
            r["flow_backbone"] = "RAFT"
            r["feature_backbone"] = "ORB"
            r["mask_version"] = "pre-overlay-v0"
            # METRIC_SPEC v1.1 sec.3: compensation is still translation-only,
            # so every compensation-dependent field below is provisional and
            # will be recomputed when similarity compensation lands.
            r["compensation_mode"] = "translation_median"
            r["compensation_provisional"] = True
            r["provisional_fields"] = ["FP", "MCFF_late", "drift_frac_late"]
            for k, val in list(r.items()):
                if isinstance(val, float) and not np.isfinite(val):
                    raise ValueError(f"non-finite {k}={val}")
            if args.persist:
                try:
                    persist_fields(model, v, device,
                                   os.path.join(args.persist, name + ".npz"))
                    r["persisted_fields"] = True
                except Exception as e:                      # non-fatal
                    r["persisted_fields"] = False
                    r["persist_error"] = repr(e)
            atomic_write(done, r)
            print(f"OK   {name}", flush=True)
        except Exception as e:
            # Failures go to their OWN stream. They must never be mistaken for
            # measurements by a coverage counter.
            atomic_write(err, {"video": name, "path": v, "error": repr(e),
                               "traceback": traceback.format_exc()})
            print(f"FAIL {name}: {e!r}", flush=True)
            try:
                torch.cuda.empty_cache()
            except Exception:
                pass
            # A cuDNN/context fault poisons the process: exit so the
            # orchestrator restarts clean rather than failing every remaining
            # video for the same dead reason.
            if isinstance(e, RuntimeError) and (
                    "CUDNN" in str(e) or "CUDA" in str(e).upper()):
                print("context fault -- exiting for clean restart", flush=True)
                return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Compute and cache the flows for the construct-B geometry candidates (GPU), then score them.

Flow: VBench RAFT (raft-things, 20 iterations) on the late window at SNF
resolution (S.MAX_H), with the v1.1 similarity fit on the eroded support removed
from every pair (snf_metrics_v11.estimate_similarity), so camera motion does not
masquerade as material direction. Two frame rates over the same late window
(the last S.WIN_FRAC of the clip): `snf`, the S.SAMPLE_FPS sampling of the
frozen spec (identical frames to realism_direction.late_frames), and `native`,
every frame, because fast falling water can move further between 8 fps samples
than RAFT matches.

Each (rate, mode, scene) is cached as an npz under
videos/realism_cache/geometry_flows/<label>/ (float16 flow, eroded masks at flow
resolution, video SHA-256, category and route) and scored by
scripts/realism_geometry_score.py; a cached file whose SHA-256 matches is reused.
The 2026-11-05 v0 report (geometry_scenetether.json) came from the earlier,
uncached form of this script with the same flow code at the `snf` rate.

Category routing (I2V v2 manifest): channel_flow -> alignment and sign stability;
falling_water -> gravity sign (expected G > 0); buoyant_plume and combustion ->
gravity sign (expected G < 0). Scenes of other categories are cached at the
`snf` rate only (route "none"), for the extent candidates.

GPU 2 or 3 only, refused if the GPU has other compute processes (RAFT beside
other scorers corrupted cuDNN in 2026-10); refused below DISK_MIN free on /.

    python scripts/realism_geometry_run.py --videos <list.tsv> --controls <dir> \\
        --modes passthrough_crf18,reverse_tail,... --label <cell> --out <json> --gpu 2
"""
import argparse
import json
import os
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths                   # noqa: E402
_paths.bootstrap_metric_imports()
os.environ.setdefault("VBENCH_CACHE_DIR", _paths.vbench_cache())
import snf_candidates as C       # noqa: E402
import snf_metrics_v11 as V11    # noqa: E402
import snf_sourceref as P        # noqa: E402
import snf_task_metrics as S     # noqa: E402
from pilot_support_realism import sha256, verify_chain, verify_reference  # noqa: E402
from realism_direction import late_frames  # noqa: E402
from realism_geometry_score import ROUTE  # noqa: E402
from spatial_ops import SCOPE  # noqa: E402

MIN_PX = 200
RATES = ("snf", "native")
DISK_MIN = 110e9       # bytes free on / (AIA's 100 GiB guard, plus margin)
CACHE = os.path.join(_paths.ROOT, "videos/realism_cache/geometry_flows")


def gpu_free(gpu):
    uuid = subprocess.run(["nvidia-smi", "-i", str(gpu), "--query-gpu=uuid", "--format=csv,noheader"],
                          capture_output=True, text=True).stdout.strip()
    apps = subprocess.run(["nvidia-smi", "--query-compute-apps=gpu_uuid", "--format=csv,noheader"],
                          capture_output=True, text=True).stdout
    return uuid not in apps


def native_late_frames(path, device):
    """Every frame over the time span of late_frames: the last k sampled pairs = k * interval native pairs."""
    import torch
    vid = cv2.VideoCapture(path)
    fps = vid.get(cv2.CAP_PROP_FPS) or 24.0
    interval = max(1, round(fps / S.SAMPLE_FPS))
    raw = []
    while True:
        ok, f = vid.read()
        if not ok:
            break
        raw.append(f)
    vid.release()
    n_snf = (len(raw) - 1) // interval + 1
    if n_snf < 4:
        return None
    k = max(S.MIN_WIN, int(round((n_snf - 1) * S.WIN_FRAC))) * interval
    last = (n_snf - 1) * interval                      # the last sampled frame ends both windows
    h, w = raw[0].shape[:2]
    nw = int(round(w * S.MAX_H / h))
    out = []
    for f in raw[last - k:last + 1]:
        rgb = cv2.cvtColor(cv2.resize(f, (nw, S.MAX_H), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
        out.append(torch.from_numpy(rgb.astype(np.uint8)).permute(2, 0, 1).float()[None].to(device))
    return out


def flows_for(model, path, dyn, sup, device, rate):
    import torch
    tens = late_frames(path, device) if rate == "snf" else native_late_frames(path, device)
    if tens is None:
        return None, "too few frames"
    h, w = tens[0].shape[2:]
    rs = lambda m: cv2.resize(C.erode(m).astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST) > 0
    mat, stat = rs(dyn), rs(sup)
    if mat.sum() < MIN_PX:
        return None, f"eroded material {int(mat.sum())} px < {MIN_PX} at flow resolution"
    rng = np.random.default_rng(0)
    out, modes = [], []
    with torch.no_grad():
        for i in range(len(tens) - 1):
            f = S.flow_vec(model, tens[i], tens[i + 1]).astype(np.float32)
            d, mode, *_ = V11.estimate_similarity(f, stat, rng)
            out.append(f - d)
            modes.append(mode)
    return dict(flows=np.stack(out), material=mat, support=stat,
                compensation=max(set(modes), key=modes.count)), None


def disk_ok():
    """DISK_MIN free on / and on the cache's filesystem (the cache may be a symlink to another disk)."""
    return all(os.statvfs(p).f_bavail * os.statvfs(p).f_frsize >= DISK_MIN for p in ("/", os.path.realpath(CACHE)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True)
    ap.add_argument("--controls", required=True)
    ap.add_argument("--modes", required=True, help="controls subdirectories, the pass-through first")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gpu", type=int, required=True, choices=(2, 3))
    ap.add_argument("--rates", default=",".join(RATES), help="native is computed for routed scenes only")
    a = ap.parse_args()
    if os.path.exists(a.out):
        raise SystemExit(f"{a.out} exists; reports are never overwritten")
    if not gpu_free(a.gpu):
        raise SystemExit(f"GPU {a.gpu} has other compute processes; RAFT is not run beside them")
    if not disk_ok():
        raise SystemExit(f"less than {DISK_MIN / 1e9:.0f} GB free on / or the cache disk")
    os.environ["CUDA_VISIBLE_DEVICES"] = str(a.gpu)
    import torch
    device = torch.device("cuda")
    model = S.load_raft(device)
    cats = {r["id"]: r["category"] for r in json.load(open(os.path.join(_paths.ROOT, "manifest/i2v_pairs_v2.json")))["pairs"]}
    masks = os.path.join(_paths.resolve("method_repo"), "results/factorial/source_masks")
    cache = os.path.join(CACHE, a.label.replace("/", "__"))
    modes = a.modes.split(",")
    for line in open(a.videos):
        sid, video = line.rstrip("\n").split("\t")
        route = ROUTE.get(cats.get(sid), "none")
        rates = [r for r in a.rates.split(",") if r == "snf" or route != "none"]
        dyn, sup, lsha, _ = P.load_role_masks(os.path.join(masks, sid, "labels.png"))
        chain = dict(parent_sha256=sha256(video), mask_labels_sha256=lsha,
                     source_sha256=sha256(os.path.join(_paths.ROOT, "prompts/v2/i2v/images", f"{sid}.jpg")))
        for md in modes:
            if md in SCOPE and route not in SCOPE[md]:
                continue                                   # spatial control not defined for this category
            path = f"{a.controls}/{md}/{sid}.mp4"
            verify_chain(path, chain)
            if md == modes[0]:
                verify_reference(path)
            vsha = sha256(path)
            for rate in rates:
                dst = os.path.join(cache, rate, md, f"{sid}.npz")
                skip = dst[:-4] + ".skip.json"
                if os.path.exists(skip) and json.load(open(skip))["sha256"] == vsha:
                    continue
                if os.path.exists(dst):
                    if json.loads(str(np.load(dst)["meta"]))["sha256"] != vsha:
                        raise SystemExit(f"{dst} caches a different video; remove it by hand")
                    continue
                got, why = flows_for(model, path, dyn, sup, device, rate)
                if got is None:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    json.dump(dict(sha256=vsha, video=path, category=cats[sid], route=route, rate=rate, abstain=why),
                              open(skip, "w"), indent=1)
                    print(sid, md, rate, "abstained:", why, flush=True)
                    continue
                if not disk_ok():
                    raise SystemExit(f"less than {DISK_MIN / 1e9:.0f} GB free on / or the cache disk; stopped before {dst}")
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                meta = dict(sha256=vsha, video=path, category=cats[sid], route=route, rate=rate,
                            compensation=got["compensation"], mask_labels_sha256=lsha,
                            flow=dict(model="RAFT raft-things (VBench)", iters=20, max_h=S.MAX_H,
                                      sample_fps=S.SAMPLE_FPS if rate == "snf" else "native", window=S.WIN_FRAC,
                                      compensation="v1.1 similarity on eroded support"))
                np.savez_compressed(dst + ".part.npz", flows=got["flows"].astype(np.float16),
                                    material=got["material"], support=got["support"], meta=json.dumps(meta))
                os.replace(dst + ".part.npz", dst)
                print(sid, md, rate, len(got["flows"]), "pairs", flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, "realism_geometry_score.py"), "--cache", cache,
                    "--label", a.label, "--out", a.out], check=True)


if __name__ == "__main__":
    main()

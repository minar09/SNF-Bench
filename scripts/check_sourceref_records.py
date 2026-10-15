#!/usr/bin/env python3
"""Full-length parity: re-score method-project 60 s videos with the port, compare records.

The in-process check (`check_sourceref_parity.py`) proves the port and
upstream compute identical values on one 5 s clip. This proves it at the scale
the benchmark runs: 60 s videos already scored by the method project on GPU,
re-scored here with `snf_sourceref.score_video`, every numeric field compared.

A record is only compared when its inputs are provably the same: the video,
the source image and the role-mask labels must all match the hashes stored in
the record. GPU RAFT is not bit-deterministic across runs, so values are
compared with a relative tolerance and the largest deviation per key is
reported, alongside how many matched exactly.

Shares a GPU with another project, so before every video it:
  * requires --min-free-mib free on the chosen GPU (default 12288, the same
    gate the method project's own rescore loop uses), else waits;
  * honours that project's STOP / STOP_gpu<G> / PAUSE / PAUSE_gpu<G> flags.

    CUDA_VISIBLE_DEVICES=3 python scripts/check_sourceref_records.py --gpu 3 \
        --cell cfpp/echo_nfpb1_fd3_lr/seed42 --scenes ial01,icf04,ifp05,icb04,iow02,ifw03
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths              # noqa: E402
import snf_sourceref as P  # noqa: E402

ROOT = _paths.ROOT
OUT = os.path.join(ROOT, "manifest", "sourceref_record_parity.json")
SKIP = {"elapsed_s", "raft_pass_s", "time", "device", "gpu", "video_path", "cell", "seed",
        "scorer_sha256", "scorer_version", "metric_spec_version", "stem", "frames"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def leaves(d, prefix=""):
    if isinstance(d, dict):
        for k, v in d.items():
            if k in SKIP:
                continue
            yield from leaves(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(d, (int, float)) and not isinstance(d, bool):
        yield prefix, float(d)


def free_mib(gpu):
    out = subprocess.run(["nvidia-smi", "-i", str(gpu), "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout
    return int(out.strip() or 0)


def gate(gpu, min_free, loopdir):
    while True:
        flags = {n for n in ("STOP", f"STOP_gpu{gpu}", "PAUSE", f"PAUSE_gpu{gpu}")
                 if os.path.exists(os.path.join(loopdir, n))}
        if any(f.startswith("STOP") for f in flags):
            raise SystemExit(f"method project raised {sorted(flags)}; stopping")
        if not flags and free_mib(gpu) >= min_free:
            return
        print(f"   waiting (flags {sorted(flags)}, free {free_mib(gpu)} MiB)", flush=True)
        time.sleep(30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu", type=int, required=True)
    ap.add_argument("--cell", required=True)
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--min-free-mib", type=int, default=12288)
    ap.add_argument("--rtol", type=float, default=1e-3)
    a = ap.parse_args()

    method = _paths.resolve("method_repo")
    cdir = os.path.join(method, "results/factorial/scores", a.cell)
    loopdir = os.path.join(method, "results/factorial/scores/_loop")
    masks = os.path.join(method, "results/factorial/source_masks")
    manifest_sha = sha(os.path.join(masks, "MANIFEST.json"))

    S, _, _ = P.snf_modules()
    model = None
    rows = []
    for sid in a.scenes.split(","):
        rec_p = os.path.join(cdir, "sourcefixed_60s/staging", f"{sid}.json")
        if not os.path.exists(rec_p):
            rows.append(dict(scene=sid, status="skip", reason="no staged record")); continue
        rec = json.load(open(rec_p))
        video = rec["video_path"] if os.path.isabs(rec["video_path"]) else os.path.join(method, rec["video_path"])
        video = video.replace("/workspace/", "/home/minar/")
        labels = os.path.join(masks, sid, "labels.png")
        source = os.path.join(ROOT, "prompts/v2/i2v/images", f"{sid}.jpg")
        checks = dict(video=sha(video) == rec.get("video_sha256"),
                      source=sha(source) == rec.get("source_sha256"),
                      labels=sha(labels) == (rec.get("mask_sha256") or {}).get("labels"))
        if not all(checks.values()):
            rows.append(dict(scene=sid, status="skip", reason=f"input hash mismatch {checks}")); continue

        gate(a.gpu, a.min_free_mib, loopdir)
        if model is None:
            model = S.load_raft("cuda")
        t = time.time()
        mine = P.score_video(model, video, labels, source, "cuda", native_fps=rec.get("native_fps", 16.0),
                             mask_set=f"sha256:{manifest_sha[:12]}", mask_version=rec.get("mask_version"),
                             mask_review_scope="ai")
        dt = time.time() - t
        A, B = dict(leaves(rec)), dict(leaves(mine))
        common = sorted(set(A) & set(B))
        exact = sum(1 for k in common if A[k] == B[k])
        rel = {k: abs(A[k] - B[k]) / max(abs(A[k]), 1e-9) for k in common}
        worst = sorted(rel.items(), key=lambda kv: -kv[1])[:3]
        over = [k for k, r in rel.items() if r > a.rtol]
        abst = {k: (rec.get(k), mine.get(k)) for k in ("motion_abstained", "fBD_abstained")}
        abst_ok = all(x == y for x, y in abst.values())
        rows.append(dict(scene=sid, category=rec.get("category"), status="PASS" if not over and abst_ok else "FAIL",
                         n_common=len(common), n_exact=exact, n_over_rtol=len(over), over=over[:5],
                         worst_rel=[(k, round(v, 8)) for k, v in worst], abstention_agrees=abst_ok,
                         seconds=round(dt, 1)))
        print(f"{sid:<6} {rows[-1]['status']}  {exact}/{len(common)} exact, {len(over)} over rtol, "
              f"worst {worst[0][0]}={worst[0][1]:.2e}, {dt:.0f}s", flush=True)

    done = [r for r in rows if r["status"] in ("PASS", "FAIL")]
    rep = dict(cell=a.cell, gpu=a.gpu, rtol=a.rtol, mask_manifest_sha256=manifest_sha,
               port_sha256=sha(P.__file__), upstream_sha256=P.UPSTREAM_SHA256,
               n_compared=len(done), n_pass=sum(r["status"] == "PASS" for r in done), rows=rows,
               verdict="PASS" if done and all(r["status"] == "PASS" for r in done) else "FAIL")
    json.dump(rep, open(OUT, "w"), indent=1)
    print(f"\n{rep['verdict']}: {rep['n_pass']}/{rep['n_compared']} records reproduced -> "
          f"{os.path.relpath(OUT, ROOT)}")
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

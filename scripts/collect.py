#!/usr/bin/env python3
"""Gather every already-computed SNF evaluation score into snf-bench/raw/.

Re-runnable and non-destructive to the source repos: it only READS from
  the configured t2v_source_repo    (T2V track)
  the configured i2v_source_repo    (I2V track)
  the configured i2v_ablation_repo   (I2V-track ablation jsons; superset check only)
and WRITES only inside this repository.

No video is copied (that would be ~20 GB and the volume is 97% full); videos are
recorded by path + size + mtime in manifest/video_index.csv and symlinked under
videos/ so the eval harness can be pointed at them directly.

    python3 scripts/collect.py
"""
import csv
import glob
import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registry import ALL, DURATIONS, T2V, I2V  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths                              # noqa: E402

SF = _paths.resolve("t2v_source_repo")     # T2V
RF = _paths.resolve("i2v_source_repo")     # I2V
SFPP = _paths.resolve("i2v_ablation_repo", required=False)

RAW = os.path.join(ROOT, "raw")
MAN = os.path.join(ROOT, "manifest")
VID = os.path.join(ROOT, "videos")


def _w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)


def _spec_of(path):
    """Highest metric-spec version among a metrics file's valid records."""
    try:
        doc = json.load(open(path))
    except (OSError, ValueError):
        return None
    vs = [str(v.get("metric_spec_version", "1.0"))
          for v in doc.get("per_video", []) if "error" not in v]
    return max(vs) if vs else None


def _copy(src, dst):
    """Copy an upstream artifact in, but never over a better local one.

    Collection re-imports metrics from the source repos. A locally recomputed
    file can be *newer than upstream* -- it is the product of re-scoring under a
    later metric spec -- and a blind copy silently destroys that work and
    restores records the recompute existed to replace. This guard cost seven
    hours of GPU time once; it is the reason the check exists.
    """
    if not os.path.exists(src):
        return False
    if os.path.exists(dst) and dst.endswith("snf_task_metrics.json"):
        have, incoming = _spec_of(dst), _spec_of(src)
        if have and (incoming is None or have > incoming):
            print(f"   keep local {os.path.relpath(dst, ROOT)} "
                  f"(spec {have} > upstream {incoming})")
            return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _sha(path, nbytes=1 << 20):
    """Cheap content fingerprint: size + sha256 of first and last 1 MiB."""
    sz = os.path.getsize(path)
    h = hashlib.sha256()
    h.update(str(sz).encode())
    with open(path, "rb") as f:
        h.update(f.read(nbytes))
        if sz > 2 * nbytes:
            f.seek(-nbytes, os.SEEK_END)
            h.update(f.read(nbytes))
    return h.hexdigest()[:16]


def newest(pattern):
    fs = sorted(glob.glob(pattern))
    return fs[-1] if fs else None


def vbench_flatten(path):
    """VBench eval_results.json -> {dim: score}. Values are [score, [per-video...]]."""
    d = json.load(open(path))
    out = {}
    for k, v in d.items():
        out[k] = v[0] if isinstance(v, list) and v else v
    return out


def vbench_pervideo(path):
    d = json.load(open(path))
    out = {}
    for k, v in d.items():
        if isinstance(v, list) and len(v) > 1 and isinstance(v[1], list):
            for row in v[1]:
                vp = os.path.basename(row.get("video_path", ""))
                out.setdefault(vp, {})[k] = row.get("video_results")
    return out


# --------------------------------------------------------------------------
# T2V collection
# --------------------------------------------------------------------------
def collect_t2v(log):
    for m in T2V:
        k = m["key"]
        # --- SNF task metrics: only the 60s rebuttal sweep exists (r1_60s) ---
        if m.get("r1"):
            src = f"{SF}/SNF_Bench/task_results/r1_60s/{m['r1']}.json"
            if _copy(src, f"{RAW}/t2v/{k}/60s/snf_task_metrics.json"):
                log.append(("t2v", k, "60s", "snf_task_metrics", src))
        # --- VBench, all durations ---
        for d in DURATIONS:
            if d == "240s":
                # 240s VBench was run as four per-prompt subsets
                subs = sorted(glob.glob(f"{SF}/SNF_Bench/results/{k}/240s_*/combined_eval_results.json"))
                sub_scores = {}
                for s in subs:
                    tag = os.path.basename(os.path.dirname(s)).replace("240s_", "")
                    sub_scores[tag] = vbench_flatten(s)
                direct = newest(f"{SF}/SNF_Bench/results/{k}/240s/*eval_results.json")
                if direct:
                    sub_scores["_pooled"] = vbench_flatten(direct)
                if sub_scores:
                    _w(f"{RAW}/t2v/{k}/240s/vbench_subsets.json", sub_scores)
                    # macro-average across the per-prompt subsets
                    dims = sorted({dim for s in sub_scores.values() for dim in s})
                    agg = {}
                    for dim in dims:
                        vals = [s[dim] for t, s in sub_scores.items()
                                if t != "_pooled" and dim in s and s[dim] is not None]
                        if vals:
                            agg[dim] = sum(vals) / len(vals)
                    _w(f"{RAW}/t2v/{k}/240s/vbench.json",
                       {"_source": "macro-average over 240s_* per-prompt subsets",
                        "_n_subsets": len([t for t in sub_scores if t != "_pooled"]), **agg})
                    log.append(("t2v", k, "240s", "vbench(subset-macro)", f"{len(subs)} subsets"))
                continue
            src = newest(f"{SF}/SNF_Bench/results/{k}/{d}/*eval_results.json")
            if src:
                _w(f"{RAW}/t2v/{k}/{d}/vbench.json", vbench_flatten(src))
                _w(f"{RAW}/t2v/{k}/{d}/vbench_per_video.json", vbench_pervideo(src))
                log.append(("t2v", k, d, "vbench", src))


# --------------------------------------------------------------------------
# I2V collection
# --------------------------------------------------------------------------
def collect_i2v(log):
    base = f"{RF}/snf_eval/results/metrics"
    for m in I2V:
        k = m["key"]
        for d in DURATIONS:
            sd = f"{base}/{k}/{d}"
            if _copy(f"{sd}/snf_task_metrics.json", f"{RAW}/i2v/{k}/{d}/snf_task_metrics.json"):
                log.append(("i2v", k, d, "snf_task_metrics", f"{sd}/snf_task_metrics.json"))
            if _copy(f"{sd}/snf_extra_metrics.json", f"{RAW}/i2v/{k}/{d}/snf_extra_metrics.json"):
                log.append(("i2v", k, d, "snf_extra_metrics", f"{sd}/snf_extra_metrics.json"))
            src = newest(f"{sd}/vbench_std/*eval_results.json") or newest(f"{sd}/vbench/*eval_results.json")
            if src:
                _w(f"{RAW}/i2v/{k}/{d}/vbench.json", vbench_flatten(src))
                _w(f"{RAW}/i2v/{k}/{d}/vbench_per_video.json", vbench_pervideo(src))
                log.append(("i2v", k, d, "vbench", src))


# --------------------------------------------------------------------------
# Auxiliary: our own training-ablation sweeps (kept OUT of the benchmark, but
# preserved so nothing is lost).  Verified identical between the two repos.
# --------------------------------------------------------------------------
def _provenance(path):
    """Describe a source path without writing a machine-specific absolute path.

    The video index and collection log recorded `abs_path`/`src` verbatim, which
    put 1881 and 199 absolute paths into two tracked manifests -- every one of
    them naming a private upstream repository and a home directory. What a
    reader actually needs is which configured source the file came from and
    where inside it, which is reproducible for anyone who configures their own.
    """
    for key, base in (("t2v_source_repo", SF), ("i2v_source_repo", RF),
                      ("i2v_ablation_repo", SFPP)):
        if base and path.startswith(base.rstrip("/") + "/"):
            return key, os.path.relpath(path, base)
    if path.startswith(ROOT.rstrip("/") + "/"):
        return "repo", os.path.relpath(path, ROOT)
    return "external", os.path.basename(path)


def collect_internal_ablations(log):
    dst = f"{RAW}/_internal_ablations"
    for sub in ["drift_eval", "extra_eval", "novelty_eval", "novelty_extra",
                "penalty_eval", "redmd_eval"]:
        for f in sorted(glob.glob(f"{RF}/snf_eval/task_results/{sub}/*.json")):
            _copy(f, f"{dst}/region-forcing/{sub}/{os.path.basename(f)}")
        # Optional superset check; skipped when that repo is not configured.
        for f in (sorted(glob.glob(f"{SFPP}/snf_eval/task_results/{sub}/*.json"))
                  if SFPP else []):
            _copy(f, f"{dst}/steady-forcing-pp/{sub}/{os.path.basename(f)}")
    for f in sorted(glob.glob(f"{SF}/SNF_Bench/task_results/r2_60s/*.json")):
        _copy(f, f"{dst}/static-forcing/r2_60s_arch_ablation/{os.path.basename(f)}")
    for name in ["REBUTTAL_RESULTS.md", "TABLE_R1.md", "TABLE_R2.md"]:
        _copy(f"{SF}/SNF_Bench/task_results/{name}", f"{dst}/static-forcing/{name}")
    log.append(("-", "_internal_ablations", "-", "copied", "not benchmark data"))


# --------------------------------------------------------------------------
# Videos: index + symlink (never copy)
# --------------------------------------------------------------------------
def index_videos():
    rows = []
    for m in ALL:
        k, track = m["key"], m["track"]
        for d in DURATIONS:
            if track == "t2v":
                vdir = f"{SF}/output/{k}/t2v_{d}"
            else:
                vdir = f"{RF}/output/eval/{k}/{d}"
            mp4s = sorted(glob.glob(f"{vdir}/*.mp4"))
            if not mp4s:
                continue
            link = f"{VID}/{track}/{k}/{d}"
            os.makedirs(os.path.dirname(link), exist_ok=True)
            if os.path.islink(link):
                os.unlink(link)
            if not os.path.exists(link):
                os.symlink(vdir, link)
            for p in mp4s:
                rows.append(dict(track=track, model=k, name=m["name"], status=m["status"],
                                 setting=m["setting"], duration=d,
                                 video=os.path.basename(p), bytes=os.path.getsize(p),
                                 fingerprint=_sha(p),
                                 **dict(zip(("source", "source_rel"),
                                            _provenance(p)))))
    os.makedirs(MAN, exist_ok=True)
    with open(f"{MAN}/video_index.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rows


# --------------------------------------------------------------------------
# Prompts / conditioning assets
# --------------------------------------------------------------------------
def collect_prompts():
    for f in sorted(glob.glob(f"{SF}/SNF_Bench/prompts/*.txt")):
        _copy(f, f"{ROOT}/prompts/t2v/{os.path.basename(f)}")
    for d in DURATIONS:
        src = f"{RF}/prompts/eval/{d}/target_crop_info_16-9.json"
        _copy(src, f"{ROOT}/prompts/i2v/{d}/target_crop_info_16-9.json")
        imgs = sorted(glob.glob(f"{RF}/prompts/eval/{d}/16-9/*"))
        link = f"{ROOT}/prompts/i2v/{d}/images"
        if imgs:
            if os.path.islink(link):
                os.unlink(link)
            if not os.path.exists(link):
                os.makedirs(os.path.dirname(link), exist_ok=True)
                os.symlink(f"{RF}/prompts/eval/{d}/16-9", link)
    # metric code, verbatim
    for f, dst in [(f"{RF}/snf_eval/snf_task_metrics.py", "snf_task_metrics.py"),
                   (f"{RF}/snf_eval/snf_extra_metrics.py", "snf_extra_metrics.py"),
                   (f"{RF}/scripts/color_match.py", "color_match.py"),
                   (f"{SF}/SNF_Bench/build_tables.py", "build_tables_orig.py")]:
        _copy(f, f"{ROOT}/metric_code/{dst}")


def main():
    log = []
    collect_t2v(log)
    collect_i2v(log)
    collect_internal_ablations(log)
    collect_prompts()
    vids = index_videos()

    # coverage matrix
    cov = {}
    for f in glob.glob(f"{RAW}/*/*/*/*.json"):
        parts = f[len(RAW) + 1:].split(os.sep)
        if len(parts) != 4 or parts[0].startswith("_"):
            continue
        track, model, dur, fn = parts
        cov.setdefault(track, {}).setdefault(model, {}).setdefault(dur, []).append(fn[:-5])
    _w(f"{MAN}/coverage.json", cov)

    nvid = {}
    for r in vids:
        nvid.setdefault(r["track"], {}).setdefault(r["model"], {}).setdefault(r["duration"], 0)
        nvid[r["track"]][r["model"]][r["duration"]] += 1
    _w(f"{MAN}/video_counts.json", nvid)

    _w(f"{MAN}/collection_log.json",
       [dict(track=t, model=m, dur=d, kind=k,
             **dict(zip(("source", "source_rel"), _provenance(s))))
        for t, m, d, k, s in log])
    # Only the public roster is snapshotted. The registry also carries internal
    # and scratch entries, and their keys, checkpoint paths and notes name
    # unpublished work; shipping them in a reproducibility manifest would
    # deanonymise the submission and disclose that work in one file open. The
    # excluded entries are counted so the omission is visible, never named.
    public = [m for m in ALL if m.get("status") == "public"]
    _w(f"{MAN}/registry_snapshot.json", public)
    _w(f"{MAN}/registry_exclusions.json",
       {"n_excluded": len(ALL) - len(public),
        "reason": "non-public entries (internal, post-processed or scratch) are "
                  "excluded from the released roster by construction",
        "n_public": len(public)})

    print(f"collected {len(log)} metric artifacts")
    print(f"indexed  {len(vids)} videos across "
          f"{len({(r['track'], r['model']) for r in vids})} (track,model) pairs")


if __name__ == "__main__":
    main()

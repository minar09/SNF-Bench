"""Resumable, crash-isolated re-run of the SNF task-metric sweep.

Why this exists: the original sweep ran every video in one process and caught
per-video exceptions *into the results file*. One poisoned CUDA context
therefore cost 29 of 30 CausVid I2V-60s videos, and because the failures were
written as records, a coverage tool counting records called the entry complete.

Two structural fixes:

  * **Crash isolation with resume.** A worker processes videos one at a time and
    writes each result the moment it is computed. If the worker dies, the
    orchestrator starts a fresh process on whatever is left. Model load is
    amortised across a run but a fault never cascades.
  * **Separate failure stream.** Failures are written as `<video>.error.json`
    and assembled into `failures/<track>/<key>/<dur>.jsonl`. They are NEVER
    merged into `per_video`. This process exits non-zero if any failure
    survives, so a broken sweep cannot pass silently.

Usage
    python scripts/rerun_metrics.py --gate            # the 4 gate-relevant entries
    python scripts/rerun_metrics.py --all-broken      # every incomplete entry
    python scripts/rerun_metrics.py --entry i2v/causvid/60s --gpu 1
"""

import argparse
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, MAN = f"{ROOT}/raw", f"{ROOT}/manifest"
STAGE = f"{ROOT}/.metric_staging"
FAIL = f"{ROOT}/failures"
WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metric_worker.py")
PY = os.environ.get("SNF_PY", os.path.expanduser("~/miniconda3/envs/snfeval/bin/python"))

# Entries whose validity decides the Aug 16 I2V gate (">=3 distinct public I2V
# baselines running reliably at 60 s"). CausVid is the third distinct published
# model; without it the gate reads 2/3.
GATE = ["i2v/causvid/60s", "i2v/cf_framewise/60s",
        "i2v/causvid/120s", "i2v/cf_framewise/120s"]

MAX_ATTEMPTS = 3


def broken_entries():
    """-> [entry] where the metrics file has fewer valid records than videos."""
    out = []
    for p in sorted(glob.glob(f"{RAW}/*/*/*/snf_task_metrics.json")):
        parts = p.split(os.sep)
        track, key, dur = parts[-4], parts[-3], parts[-2]
        try:
            pv = json.load(open(p)).get("per_video", [])
        except (OSError, ValueError):
            continue
        good = sum(1 for v in pv if "error" not in v and v.get("fBD") is not None)
        if good < len(pv):
            out.append(f"{track}/{key}/{dur}")
    return out


def videos_for(entry):
    track, key, dur = entry.split("/")
    return sorted(glob.glob(f"{ROOT}/videos/{track}/{key}/{dur}/*.mp4"))


def run_entry(entry, gpu, persist=True, spec="1.1"):
    track, key, dur = entry.split("/")
    stage = f"{STAGE}/{track}/{key}/{dur}"
    pdir = f"{ROOT}/.flow_fields/{track}/{key}/{dur}" if persist else ""
    os.makedirs(stage, exist_ok=True)
    vids = videos_for(entry)
    if not vids:
        print(f"!! {entry}: no videos on disk -- generation gap, not a metric gap")
        return None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        todo = [v for v in vids
                if not os.path.exists(f"{stage}/{os.path.basename(v)}.json")
                and not os.path.exists(f"{stage}/{os.path.basename(v)}.error.json")]
        if not todo:
            break
        listfile = f"{stage}/_todo.txt"
        with open(listfile, "w") as f:
            f.write("\n".join(todo))
        print(f"   [{entry}] attempt {attempt}: {len(todo)} remaining", flush=True)
        cmd = [PY, WORKER, "--videos", listfile, "--staging", stage,
               "--gpu", str(gpu), "--spec", spec]
        if pdir:
            cmd += ["--persist", pdir]
        rc = subprocess.call(cmd)
        if rc == 0:
            break
        print(f"   [{entry}] worker exited {rc} -- restarting clean", flush=True)
        # A video that faulted got an .error.json; clear it so a fresh context
        # gets one more try, unless we are out of attempts.
        if attempt < MAX_ATTEMPTS:
            for e in glob.glob(f"{stage}/*.error.json"):
                os.remove(e)

    ok = [json.load(open(p)) for p in sorted(glob.glob(f"{stage}/*.json"))
          if not p.endswith(".error.json") and not p.endswith("_todo.txt")]
    bad = [json.load(open(p)) for p in sorted(glob.glob(f"{stage}/*.error.json"))]
    return assemble(entry, ok, bad)


def assemble(entry, ok, bad):
    """Write the metrics file from successes only; failures go to their own stream."""
    import numpy as np
    track, key, dur = entry.split("/")
    outp = f"{RAW}/{track}/{key}/{dur}/snf_task_metrics.json"
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    prev = {}
    if os.path.exists(outp):
        try:
            prev = json.load(open(outp))
        except ValueError:
            pass

    def agg(k, fn):
        xs = [r[k] for r in ok if r.get(k) is not None]
        return float(fn(xs)) if xs else None

    summary = dict(prev)
    summary.update({
        "videos_dir": f"{ROOT}/videos/{track}/{key}/{dur}",
        "n_videos": len(ok),
        "n_failed": len(bad),
        "metric_spec_version": "1.0",
        "fBD_mean": agg("fBD", np.mean), "fBD_median": agg("fBD", np.median),
        "BFR_mean": agg("BFR", np.mean), "BFR_median": agg("BFR", np.median),
        "FP_mean": agg("FP", np.mean), "FP_median": agg("FP", np.median),
        "MCFF_late_mean": agg("MCFF_late", np.mean),
        "DD_raw_late_mean": agg("DD_raw_late", np.mean),
        "drift_frac_late_mean": agg("drift_frac_late", np.mean),
        "per_video": ok,          # successes ONLY -- never failures
    })
    tmp = outp + ".tmp"
    with open(tmp, "w") as f:
        json.dump(summary, f, indent=2)
    os.replace(tmp, outp)

    fp = f"{FAIL}/{track}/{key}"
    os.makedirs(fp, exist_ok=True)
    fpath = f"{fp}/{dur}.jsonl"
    if bad:
        with open(fpath, "w") as f:
            for b in bad:
                f.write(json.dumps(b) + "\n")
    elif os.path.exists(fpath):
        os.remove(fpath)
    print(f"   [{entry}] {len(ok)} valid, {len(bad)} failed", flush=True)
    return len(ok), len(bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--all-broken", action="store_true")
    ap.add_argument("--entry", action="append", default=[])
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--no-persist", action="store_true")
    ap.add_argument("--spec", default="1.1")
    args = ap.parse_args()

    entries = list(args.entry)
    if args.gate:
        entries += GATE
    if args.all_broken:
        entries += [e for e in broken_entries() if e not in entries]
    if not entries:
        print("nothing selected; use --gate, --all-broken or --entry")
        return 2

    results, failed_any = {}, False
    for e in entries:
        r = run_entry(e, args.gpu, persist=not args.no_persist, spec=args.spec)
        if r is None:
            failed_any = True
            continue
        results[e] = r
        if r[1]:
            failed_any = True

    print("\n=== re-run summary ===")
    for e, (n_ok, n_bad) in results.items():
        total = len(videos_for(e))
        flag = "OK " if n_bad == 0 and n_ok == total else "!! "
        print(f"{flag}{e}: {n_ok}/{total} valid, {n_bad} failed")
    if failed_any:
        print("\nFAILURES PRESENT -- see failures/. Exiting non-zero so a broken "
              "sweep cannot pass silently.")
    return 1 if failed_any else 0


if __name__ == "__main__":
    sys.exit(main())

"""Retroactive validity scan over every SNF-Bench metric artifact.

The CausVid gap was found by chasing one odd count. That is not a method. This
scans all metric JSONs mechanically so nothing else is waiting to be discovered
by accident, and so the claim matrix can cite a scan rather than an anecdote as
evidence that coverage numbers are measurement counts.

Checks per per-video record:
  required keys present
  all numeric values finite (no NaN / inf)
  no error payload masquerading as a measurement
  region occupancy non-degenerate (static_frac strictly inside (0,1))
  sampled frame count consistent with container frames, fps and SAMPLE_FPS
  video referenced by the record actually exists on disk

Writes manifest/schema_scan.json and tables/schema_scan.md, and exits non-zero
if any BLOCKING problem is found.

    ~/miniconda3/envs/snfeval/bin/python scripts/schema_scan.py
"""

import csv
import glob
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registry import ALL, SAMPLE_FPS                       # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, MAN, TAB = f"{ROOT}/raw", f"{ROOT}/manifest", f"{ROOT}/tables"

REQUIRED_TASK = ["video", "fBD", "BFR", "FP", "MCFF_late", "DD_raw_late",
                 "drift_frac_late", "static_frac", "n_frames_sampled"]
# Sampled-count tolerance: read_frames uses raw[::interval] on the frames it
# actually decoded, and decoders disagree with container metadata by a frame or
# two at the tail. Anything beyond this is a real inconsistency.
FRAME_TOL = 3


def load_video_meta():
    p = f"{MAN}/video_meta.csv"
    if not os.path.exists(p):
        return {}
    return {(r["track"], r["model"], r["duration"], r["video"]):
            (float(r["fps"]), int(r["n_frames"])) for r in csv.DictReader(open(p))}


def expected_sampled(n_frames, fps):
    interval = max(1, round(fps / SAMPLE_FPS))
    return math.ceil(n_frames / interval)


def scan():
    meta = load_video_meta()
    reg = {m["key"]: m for m in ALL}
    problems = defaultdict(list)
    stats = Counter()

    for p in sorted(glob.glob(f"{RAW}/*/*/*/snf_task_metrics.json")):
        parts = p.split(os.sep)
        track, key, dur = parts[-4], parts[-3], parts[-2]
        entry = f"{track}/{key}/{dur}"
        try:
            doc = json.load(open(p))
        except (OSError, ValueError) as e:
            problems[entry].append(("BLOCKING", "unreadable", repr(e)))
            continue

        for v in doc.get("per_video", []):
            stats["records"] += 1
            name = v.get("video", "<unnamed>")
            if "error" in v:
                problems[entry].append(("BLOCKING", "error-in-results", name))
                stats["error_records"] += 1
                continue
            missing = [k for k in REQUIRED_TASK if v.get(k) is None]
            if missing:
                problems[entry].append(("BLOCKING", "missing-keys",
                                        f"{name}: {','.join(missing)}"))
                stats["missing_keys"] += 1
                continue
            for k, val in v.items():
                if isinstance(val, float) and not math.isfinite(val):
                    problems[entry].append(("BLOCKING", "non-finite", f"{name}: {k}={val}"))
                    stats["non_finite"] += 1
            sf = v.get("static_frac")
            if sf is not None and not (0.0 < sf < 1.0):
                problems[entry].append(("BLOCKING", "degenerate-mask",
                                        f"{name}: static_frac={sf}"))
                stats["degenerate_mask"] += 1

            mk = (track, key, dur, name)
            if mk not in meta:
                problems[entry].append(("WARN", "video-missing-on-disk", name))
                stats["video_missing"] += 1
            else:
                fps, nfr = meta[mk]
                exp = expected_sampled(nfr, fps)
                got = v.get("n_frames_sampled")
                if got is not None and abs(got - exp) > FRAME_TOL:
                    problems[entry].append(
                        ("BLOCKING", "frame-count-inconsistent",
                         f"{name}: sampled={got} expected~{exp} "
                         f"(container {nfr} @ {fps}fps, SAMPLE_FPS={SAMPLE_FPS})"))
                    stats["frame_mismatch"] += 1
            stats["valid"] += 1

        # Videos on disk with no record at all.
        vids = glob.glob(f"{ROOT}/videos/{track}/{key}/{dur}/*.mp4")
        have = {v.get("video") for v in doc.get("per_video", [])}
        gap = [os.path.basename(x) for x in vids if os.path.basename(x) not in have]
        if gap:
            problems[entry].append(("BLOCKING", "unmeasured-videos",
                                    f"{len(gap)} of {len(vids)} have no record"))
            stats["unmeasured"] += len(gap)

    return problems, stats, reg


def main():
    problems, stats, reg = scan()
    blocking = {e: [p for p in v if p[0] == "BLOCKING"] for e, v in problems.items()}
    blocking = {e: v for e, v in blocking.items() if v}

    report = {"stats": dict(stats),
              "entries_with_problems": {e: [list(x) for x in v]
                                        for e, v in sorted(problems.items())}}
    os.makedirs(MAN, exist_ok=True)
    with open(f"{MAN}/schema_scan.json", "w") as f:
        json.dump(report, f, indent=2)

    L = ["# Metric-artifact schema scan", "",
         "Mechanical validity check over every `snf_task_metrics.json`. Exists because "
         "the CausVid gap was found by chasing one odd count, which is luck rather than "
         "method; this makes the same class of defect discoverable by construction.", "",
         "| statistic | count |", "|---|---|"]
    for k in ["records", "valid", "error_records", "missing_keys", "non_finite",
              "degenerate_mask", "frame_mismatch", "video_missing", "unmeasured"]:
        L.append(f"| {k} | {stats.get(k, 0)} |")

    if blocking:
        L += ["", f"## Blocking problems — {len(blocking)} entries", "",
              "| entry | status | kind | detail |", "|---|---|---|---|"]
        for e, v in sorted(blocking.items()):
            key = e.split("/")[1]
            status = reg.get(key, {}).get("status", "?")
            kinds = Counter(k for _, k, _ in v)
            for kind, n in kinds.most_common():
                ex = next(d for _, k, d in v if k == kind)
                L.append(f"| `{e}` | {status} | {kind} ×{n} | {ex[:80]} |")
    else:
        L += ["", "## No blocking problems found.", ""]
    os.makedirs(TAB, exist_ok=True)
    with open(f"{TAB}/schema_scan.md", "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"scanned {stats.get('records', 0)} records; "
          f"{stats.get('valid', 0)} valid")
    for k in ["error_records", "missing_keys", "non_finite", "degenerate_mask",
              "frame_mismatch", "video_missing", "unmeasured"]:
        if stats.get(k):
            print(f"  !! {k}: {stats[k]}")
    print(f"entries with blocking problems: {len(blocking)}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())

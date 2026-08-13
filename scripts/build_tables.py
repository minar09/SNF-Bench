#!/usr/bin/env python3
"""Build every SNF-Bench paper table from snf-bench/raw/.

Emits into tables/ (markdown + LaTeX) and manifest/ (tidy CSV).
Statistics are prompt-level: bootstrap 95% CIs (percentile, 10k resamples,
fixed seed) and paired Wilcoxon-style sign statistics over shared prompts.

    python3 scripts/build_tables.py
"""
import csv
import glob
import json
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registry import (ALL, DURATIONS, EXTRA_KEYS, METRICS, SNF_TASK_KEYS,  # noqa: E402
                      VBENCH_KEYS, by_key, contestants)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, TAB, MAN = f"{ROOT}/raw", f"{ROOT}/tables", f"{ROOT}/manifest"
os.makedirs(TAB, exist_ok=True)

# per-video key -> aggregate key used in the summary tables
PV2AGG = {"fBD": "fBD_mean", "BFR": "BFR_mean", "FP": "FP_mean",
          "MCFF_late": "MCFF_late_mean", "DD_raw_late": "DD_raw_late_mean",
          "drift_frac_late": "drift_frac_late_mean"}
AGG2PV = {v: k for k, v in PV2AGG.items()}

_TS = re.compile(r"-\d+-\d+\.\d+\.mp4$")


def prompt_id(video, track):
    """Stable cross-model identifier for the conditioning item."""
    if track == "t2v":
        return _TS.sub("", video)          # strip -<seed>-<timestamp>.mp4
    return re.sub(r"\.mp4$", "", video)     # I2V filenames are the caption itself


# --------------------------------------------------------------------- load
def load_all():
    """-> rows: dict(track, model, duration, prompt_id, metric, value)"""
    rows = []
    for track in ("t2v", "i2v"):
        reg = by_key(track)
        for k, m in reg.items():
            for d in DURATIONS:
                base = f"{RAW}/{track}/{k}/{d}"
                # SNF task metrics
                p = f"{base}/snf_task_metrics.json"
                if os.path.exists(p):
                    j = json.load(open(p))
                    for v in j.get("per_video", []):
                        for pk, ak in PV2AGG.items():
                            if v.get(pk) is not None:
                                rows.append(dict(track=track, model=k, duration=d,
                                                 prompt_id=prompt_id(v["video"], track),
                                                 metric=ak, value=float(v[pk])))
                # cv2 extra metrics
                p = f"{base}/snf_extra_metrics.json"
                if os.path.exists(p):
                    j = json.load(open(p))
                    for v in j.get("per_video", []):
                        for ek in EXTRA_KEYS:
                            if v.get(ek) is not None:
                                rows.append(dict(track=track, model=k, duration=d,
                                                 prompt_id=prompt_id(v["video"], track),
                                                 metric=ek, value=float(v[ek])))
                # VBench per-video
                p = f"{base}/vbench_per_video.json"
                if os.path.exists(p):
                    j = json.load(open(p))
                    for vid, dims in j.items():
                        for dim, val in dims.items():
                            if val is None:
                                continue
                            rows.append(dict(track=track, model=k, duration=d,
                                             prompt_id=prompt_id(vid, track),
                                             metric=dim, value=float(val)))
    return rows


def index(rows):
    """(track,model,duration,metric) -> {prompt_id: value}

    A prompt_id can legitimately repeat when a model was sampled more than once for
    the same prompt (e.g. Rolling-Forcing has 24 clips over 23 prompts at 60s). Those
    are averaged, never dropped, and reported in manifest/duplicate_prompts.json.
    """
    acc, dups = {}, {}
    for r in rows:
        key = (r["track"], r["model"], r["duration"], r["metric"])
        acc.setdefault(key, {}).setdefault(r["prompt_id"], []).append(r["value"])
    ix = {}
    for key, pm in acc.items():
        ix[key] = {p: mean(v) for p, v in pm.items()}
        for p, v in pm.items():
            if len(v) > 1:
                dups.setdefault(f"{key[0]}/{key[1]}/{key[2]}", {})[p] = len(v)
    with open(f"{MAN}/duplicate_prompts.json", "w") as f:
        json.dump(dups, f, indent=1)
    return ix


# ---------------------------------------------------------------- statistics
def mean(xs):
    return sum(xs) / len(xs) if xs else None


def boot_ci(xs, n=10000, seed=0, lo=2.5, hi=97.5):
    if len(xs) < 2:
        return (None, None)
    rnd = random.Random(seed)
    N = len(xs)
    means = []
    for _ in range(n):
        means.append(sum(xs[rnd.randrange(N)] for _ in range(N)) / N)
    means.sort()
    return (means[int(lo / 100 * n)], means[min(n - 1, int(hi / 100 * n))])


def spearman(a, b):
    """a, b: equal-length lists."""
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = mean(ra), mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else None


def paired_sign_p(a, b):
    """Two-sided exact sign test over paired differences (a-b)."""
    diffs = [x - y for x, y in zip(a, b) if x != y]
    n = len(diffs)
    if n == 0:
        return 1.0, 0, 0
    wins = sum(1 for d in diffs if d > 0)
    k = min(wins, n - wins)
    p = 0.0
    for i in range(0, k + 1):
        p += math.comb(n, i)
    p = min(1.0, 2 * p / (2 ** n))
    return p, wins, n


# ------------------------------------------------------------------- render
def fmt(v, nd=3):
    if v is None:
        return "--"
    if abs(v) >= 100:
        return f"{v:.1f}"
    return f"{v:.{nd}f}"


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def latex_table(header, rows, caption, label):
    cols = "l" + "c" * (len(header) - 1)
    esc = lambda s: str(s).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")
    out = [r"\begin{table}[t]", r"\centering", r"\small",
           r"\begin{tabular}{" + cols + "}", r"\toprule",
           " & ".join(esc(h) for h in header) + r" \\", r"\midrule"]
    for r in rows:
        out.append(" & ".join(esc(x) for x in r) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}",
            r"\caption{" + caption + "}", r"\label{" + label + "}", r"\end{table}"]
    return "\n".join(out)


def write(name, body):
    with open(f"{TAB}/{name}", "w") as f:
        f.write(body.rstrip() + "\n")


# =========================================================================
def snf_leaderboard(ix, track, dur, keys, title, note, only_public=True):
    models = [m for m in ALL if m["track"] == track]
    if only_public:
        models = [m for m in models if m["status"] == "public"]
    header = ["Method", "setting", "n"] + [f"{METRICS[k][1]}{'↓' if METRICS[k][0]=='-' else ('↑' if METRICS[k][0]=='+' else '')}"
                                           for k in keys]
    rows, ltx = [], []
    for m in models:
        vals = {k: ix.get((track, m["key"], dur, k), {}) for k in keys}
        n = max((len(v) for v in vals.values()), default=0)
        if n == 0:
            continue
        cells, lcells = [], []
        for k in keys:
            xs = list(vals[k].values())
            mu = mean(xs)
            lo, hi = boot_ci(xs) if xs else (None, None)
            cells.append(f"{fmt(mu)} <sub>[{fmt(lo)}, {fmt(hi)}]</sub>" if mu is not None else "--")
            lcells.append(fmt(mu))
        rows.append([m["name"], m["setting"], n] + cells)
        ltx.append([m["name"], m["setting"], n] + lcells)
    body = [f"# {title}", "", note, "",
            "Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.", "",
            md_table(header, rows), "", "<details><summary>LaTeX (point estimates)</summary>", "",
            "```latex",
            latex_table([h.replace("↓", r"$\downarrow$").replace("↑", r"$\uparrow$") for h in header],
                        ltx, title, f"tab:{track}_snf_{dur}"),
            "```", "</details>"]
    return "\n".join(body), rows


def vbench_table(ix, track, dur):
    models = [m for m in ALL if m["track"] == track and m["status"] == "public"]
    dims = [k for k in VBENCH_KEYS
            if any(ix.get((track, m["key"], dur, k)) for m in models)]
    if not dims:
        return None
    header = ["Method", "n"] + [METRICS[k][1] for k in dims]
    rows = []
    for m in models:
        cells, n = [], 0
        for k in dims:
            xs = list(ix.get((track, m["key"], dur, k), {}).values())
            n = max(n, len(xs))
            cells.append(fmt(mean(xs), 4))
        if n:
            rows.append([m["name"], n] + cells)
    if not rows:
        return None
    return "\n".join([f"# VBench — {track.upper()} @ {dur}", "",
                      "Standard VBench dimensions on the same generated videos SNF-Bench scores.", "",
                      md_table(header, rows)])


def disagreement_table(ix, track, dur):
    """Rank correlation between generic video metrics and SNF-Bench metrics."""
    models = [m for m in ALL if m["track"] == track and m["status"] == "public"]
    generic = [k for k in ("dynamic_degree", "background_consistency", "motion_smoothness",
                           "temporal_flickering", "subject_consistency")
               if any(ix.get((track, m["key"], dur, k)) for m in models)]
    snf = [k for k in SNF_TASK_KEYS if any(ix.get((track, m["key"], dur, k)) for m in models)]
    if not generic or not snf:
        return None
    usable = [m for m in models
              if all(ix.get((track, m["key"], dur, k)) for k in generic + snf)]
    if len(usable) < 4:
        return None
    vec = {k: [mean(list(ix[(track, m["key"], dur, k)].values())) for m in usable]
           for k in generic + snf}
    header = ["generic metric"] + [METRICS[k][1] for k in snf]
    rows = []
    for g in generic:
        rows.append([METRICS[g][1]] + [fmt(spearman(vec[g], vec[s]), 2) for s in snf])
    # per-model rank table.  Context metrics ('~') have no intrinsic "better"; we rank
    # them 1 = MOST motion, because that is the conventional reading SNF-Bench audits.
    def rank_of(k):
        sign = 1 if METRICS[k][0] == "-" else -1     # '-' -> 1 = lowest; '+'/'~' -> 1 = highest
        order = sorted(range(len(usable)), key=lambda i: sign * vec[k][i])
        r = [0] * len(usable)
        for pos, i in enumerate(order):
            r[i] = pos + 1
        return r
    rk = {k: rank_of(k) for k in generic + snf}
    arrow = {"-": "↓", "+": "↑", "~": "(1=most)"}
    rhdr = ["Method"] + [f"{METRICS[k][1]}{arrow[METRICS[k][0]]}" for k in generic + snf]
    rrows = [[usable[i]["name"]] + [rk[k][i] for k in generic + snf] for i in range(len(usable))]
    return "\n".join([
        f"# Ranking disagreement — {track.upper()} @ {dur}  (n={len(usable)} public methods)", "",
        "Spearman rank correlation between each **generic** video metric and each **SNF-Bench** metric,",
        "computed over method-level means. Values near 0 or of the *wrong sign* mean the generic metric",
        "does not carry the information SNF-Bench measures.", "",
        md_table(header, rows), "",
        "## Per-method ranks", "",
        "Directed metrics (↓/↑) are ranked 1 = best. Context metrics marked `(1=most)` have no intrinsic",
        "\"better\" and are ranked 1 = most motion — the conventional reading SNF-Bench audits.", "",
        md_table(rhdr, rrows)])


def pairwise_stats(ix, track, dur, keys):
    """Paired sign tests between every pair of public methods on shared prompts."""
    models = [m for m in ALL if m["track"] == track and m["status"] == "public"]
    out = [f"# Paired significance — {track.upper()} @ {dur}", "",
           "Exact two-sided sign test over prompts evaluated by **both** methods.",
           "`wins` = number of prompts where the row method has the *better* value.", ""]
    any_rows = False
    for k in keys:
        rows = []
        avail = [m for m in models if ix.get((track, m["key"], dur, k))]
        for i, a in enumerate(avail):
            for b in avail[i + 1:]:
                A = ix[(track, a["key"], dur, k)]
                B = ix[(track, b["key"], dur, k)]
                shared = sorted(set(A) & set(B))
                if len(shared) < 5:
                    continue
                xa = [A[p] for p in shared]
                xb = [B[p] for p in shared]
                better_is_low = METRICS[k][0] == "-"
                p, wins, n = paired_sign_p([-x for x in xa] if better_is_low else xa,
                                           [-x for x in xb] if better_is_low else xb)
                rows.append([a["name"], b["name"], n, f"{fmt(mean(xa))} vs {fmt(mean(xb))}",
                             f"{wins}/{n}", f"{p:.4f}", "**yes**" if p < 0.05 else "no"])
        if rows:
            any_rows = True
            out += [f"## {METRICS[k][1]} ({'lower' if METRICS[k][0]=='-' else 'higher'} is better)", "",
                    md_table(["A", "B", "n paired", "mean A vs B", "A wins", "p (sign test)", "sig"], rows), ""]
    return "\n".join(out) if any_rows else None


def coverage_matrix():
    cov = json.load(open(f"{MAN}/coverage.json"))
    nv = json.load(open(f"{MAN}/video_counts.json"))
    out = ["# Asset & score coverage matrix", "",
           "`V` = generated videos present · `T` = SNF task metrics (RAFT+ORB) · "
           "`X` = cv2 extra metrics · `B` = VBench", ""]
    for track in ("t2v", "i2v"):
        reg = by_key(track)
        out += [f"## {track.upper()} track", "",
                "| Method | status | setting | " + " | ".join(DURATIONS) + " |",
                "|---|---|---|" + "|".join(["---"] * len(DURATIONS)) + "|"]
        for k, m in reg.items():
            cells = []
            for d in DURATIONS:
                have = cov.get(track, {}).get(k, {}).get(d, [])
                n = nv.get(track, {}).get(k, {}).get(d, 0)
                tag = ""
                if n:
                    tag += f"V{n}"
                for flag, name in (("T", "snf_task_metrics"), ("X", "snf_extra_metrics"), ("B", "vbench")):
                    if name in have:
                        tag += " " + flag
                cells.append(tag or "·")
            out.append(f"| {m['name']} | {m['status']} | {m['setting']} | " + " | ".join(cells) + " |")
        out.append("")
    return "\n".join(out)


def config_table():
    out = ["# Model configuration / provenance table", "",
           "Required by the E&D track: every evaluated system with its checkpoint and the",
           "configuration it was actually run under. **Setting A = native**, **Setting B = matched wrapper**.", ""]
    for track in ("t2v", "i2v"):
        out += [f"## {track.upper()} track", "",
                md_table(["Method", "status", "setting", "checkpoint", "note"],
                         [[m["name"], m["status"], m["setting"], f"`{m['ckpt']}`" if m["ckpt"] else "--",
                           m["note"] or ""]
                          for m in ALL if m["track"] == track]), ""]
    return "\n".join(out)


# =========================================================================
def main():
    rows = load_all()
    ix = index(rows)

    with open(f"{MAN}/per_video_scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["track", "model", "duration", "prompt_id", "metric", "value"])
        w.writeheader()
        w.writerows(rows)

    written = []

    # --- T2V ---
    body, _ = snf_leaderboard(
        ix, "t2v", "60s", SNF_TASK_KEYS,
        "SNF-Bench core metrics — T2V @ 60s",
        "All seven systems are **public external models run under their own native configuration** "
        "(Setting A). Our own systems are excluded by construction — see `docs/EXCLUSIONS.md`.")
    write("t2v_snf_60s.md", body)
    written.append("t2v_snf_60s.md")

    for d in DURATIONS:
        t = vbench_table(ix, "t2v", d)
        if t:
            write(f"t2v_vbench_{d}.md", t)
            written.append(f"t2v_vbench_{d}.md")
    t = disagreement_table(ix, "t2v", "60s")
    if t:
        write("t2v_disagreement_60s.md", t)
        written.append("t2v_disagreement_60s.md")
    t = pairwise_stats(ix, "t2v", "60s", SNF_TASK_KEYS)
    if t:
        write("t2v_paired_stats_60s.md", t)
        written.append("t2v_paired_stats_60s.md")

    # --- I2V ---
    for d in DURATIONS:
        body, r = snf_leaderboard(
            ix, "i2v", d, SNF_TASK_KEYS,
            f"SNF-Bench core metrics — I2V @ {d}",
            "**Read the `setting` column.** Entries marked `matched` were run in a common "
            "long-horizon I2V wrapper, *not* their authors' configuration; they are a "
            "stress-test result, not a native-capability ranking.")
        if r:
            write(f"i2v_snf_{d}.md", body)
            written.append(f"i2v_snf_{d}.md")
        body, r = snf_leaderboard(
            ix, "i2v", d, EXTRA_KEYS,
            f"Appearance / stagnation metrics — I2V @ {d}",
            "cv2-only metrics (blur growth, colour drift, background identity, stagnation onset).")
        if r:
            write(f"i2v_extra_{d}.md", body)
            written.append(f"i2v_extra_{d}.md")
        t = vbench_table(ix, "i2v", d)
        if t:
            write(f"i2v_vbench_{d}.md", t)
            written.append(f"i2v_vbench_{d}.md")
        t = pairwise_stats(ix, "i2v", d, SNF_TASK_KEYS)
        if t:
            write(f"i2v_paired_stats_{d}.md", t)
            written.append(f"i2v_paired_stats_{d}.md")

    write("coverage_matrix.md", coverage_matrix())
    write("model_config_table.md", config_table())
    written += ["coverage_matrix.md", "model_config_table.md"]

    print(f"wrote {len(written)} tables into tables/")
    print(f"tidy per-video scores: {len(rows)} rows -> manifest/per_video_scores.csv")


if __name__ == "__main__":
    main()

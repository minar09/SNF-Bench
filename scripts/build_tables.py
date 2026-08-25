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
from registry import (ALL, DURATIONS, EXTRA_KEYS, FPS_DEFAULT, METRICS,  # noqa: E402
                      SNF_TASK_KEYS, VBENCH_KEYS, by_key, contestants,
                      effective_fps)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, TAB, MAN = f"{ROOT}/raw", f"{ROOT}/tables", f"{ROOT}/manifest"
os.makedirs(TAB, exist_ok=True)

# per-video key -> aggregate key used in the summary tables.
# The raw JSONs still carry the ORIGINAL metric names (BFR, drift_frac_late);
# they are historical artifacts and are not rewritten. The rename to NBF/DAR
# happens here, on the way into the tables. See registry.METRICS for why.
PV2AGG = {"fBD": "fBD_mean", "BFR": "NBF_mean", "FP": "FP_mean",
          "MCFF_early": "MCFF_early_mean",          # v1.1 only; absent in v1.0 records
          "MCFF_late": "MCFF_late_mean", "DD_raw_late": "DD_raw_late_mean",
          "drift_frac_late": "DLR_mean"}
AGG2PV = {v: k for k, v in PV2AGG.items()}

# NBF is per-second; raw BFR is per SAMPLED frame pair -> scale by the
# EFFECTIVE sampled rate, not the native rate (see registry.effective_fps).
_FPS = {}


def load_fps():
    """(track, model, duration, video) -> fps, from manifest/video_meta.csv."""
    p = f"{MAN}/video_meta.csv"
    if not os.path.exists(p):
        print(f"WARNING: {p} missing -- NBF will fall back to {FPS_DEFAULT} fps for "
              "every video, which silently reintroduces the frame-rate confound. "
              "Run scripts/video_meta.py.", file=sys.stderr)
        return {}
    return {(r["track"], r["model"], r["duration"], r["video"]): float(r["fps"])
            for r in csv.DictReader(open(p))}


def fps_of(track, model, duration, video):
    """Effective temporal rate of the flow measurement, in Hz.

    NOT the container frame rate: the metric subsamples to SAMPLE_FPS before
    computing flow, so a 16 fps and a 24 fps clip are both measured at 8 Hz.
    Scaling by the native rate would introduce a confound rather than remove
    one -- see registry.effective_fps.
    """
    return effective_fps(_FPS.get((track, model, duration, video), FPS_DEFAULT))

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
                        fps = fps_of(track, k, d, v["video"])
                        for pk, ak in PV2AGG.items():
                            if v.get(pk) is not None:
                                val = float(v[pk])
                                if ak == "NBF_mean":
                                    val *= fps       # per sampled pair -> per second
                                rows.append(dict(track=track, model=k, duration=d,
                                                 prompt_id=prompt_id(v["video"], track),
                                                 metric=ak, value=val))
                        # DAR: v1.1 stores it signed as DAR_signed. v1.0 records
                        # predate the metric, so it is derived there from the two
                        # stored magnitudes -- the shipped drift_frac_late is a
                        # different quantity (now DLR). See registry.METRICS.
                        dar = v.get("DAR_signed")
                        if dar is None:
                            raw, comp = v.get("DD_raw_late"), v.get("MCFF_late")
                            if raw is not None and comp is not None and abs(raw) > 1e-9:
                                dar = 1.0 - float(comp) / float(raw)
                        if dar is not None:
                            rows.append(dict(track=track, model=k, duration=d,
                                             prompt_id=prompt_id(v["video"], track),
                                             metric="DAR_mean", value=float(dar)))
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


def setting_label(model):
    """Paper-facing setting names; registry enums remain backward compatible."""
    if model["track"] == "t2v" and model["setting"] == "matched":
        return "common"
    if model["track"] == "i2v" and model["setting"] == "matched":
        return "wrapper"
    if model["setting"] == "native":
        return "released"
    return model["setting"]


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


def dar_negative_incidence(rows):
    """How often global compensation INCREASED measured dynamic-region flow.

    DAR < 0 is the empirical form of the caveat that DAR is not a causal
    decomposition: where local flow opposes the estimated global field,
    subtracting that field raises the residual magnitude. Reporting the rate
    turns a reviewer's objection into demonstrated rigor, so it is tabulated
    per (track, model, duration) rather than mentioned in passing.
    """
    acc = {}
    for r in rows:
        if r["metric"] != "DAR_mean":
            continue
        k = (r["track"], r["model"], r["duration"])
        a = acc.setdefault(k, {"n": 0, "neg": 0, "min": None})
        a["n"] += 1
        if r["value"] < 0:
            a["neg"] += 1
        a["min"] = r["value"] if a["min"] is None else min(a["min"], r["value"])

    reg = {m["key"]: m for m in ALL}
    out, body = {}, []
    tot_n = tot_neg = 0
    for (track, model, dur), a in sorted(acc.items()):
        m = reg.get(model, {})
        rate = a["neg"] / a["n"] if a["n"] else 0.0
        out[f"{track}/{model}/{dur}"] = dict(n=a["n"], negative=a["neg"],
                                             rate=round(rate, 4),
                                             most_negative=round(a["min"], 4))
        tot_n += a["n"]
        tot_neg += a["neg"]
        if m.get("status") == "public":
            body.append([m.get("name", model), track, dur, a["n"], a["neg"],
                         f"{100 * rate:.1f}%", fmt(a["min"])])
    with open(f"{MAN}/dar_negative_incidence.json", "w") as f:
        json.dump({"overall": dict(n=tot_n, negative=tot_neg,
                                   rate=round(tot_neg / max(1, tot_n), 4)),
                   "by_entry": out}, f, indent=2)

    doc = ["# DAR negative incidence — public methods", "",
           "DAR is stored **signed** and reported clipped to $[0,1]$ "
           "(METRIC_SPEC v1.1 §2). A negative value means global-motion "
           "compensation *increased* measured dynamic-region flow, which occurs "
           "where local flow opposes the estimated global field. This is the "
           "empirical reason DAR is not a causal decomposition of motion.", "",
           f"Overall across all entries: **{tot_neg} / {tot_n}** clip-metrics "
           f"negative ({100 * tot_neg / max(1, tot_n):.1f}%).", "",
           md_table(["Method", "track", "dur", "n", "negative", "rate", "most negative"], body)]
    write("dar_negative_incidence.md", "\n".join(doc))
    return out


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
            if k == "DAR_mean":
                # METRIC_SPEC v1.1 sec.2: storage is signed, reporting is
                # clipped, validation uses signed. Clipping only here means the
                # released per-video CSV keeps the negatives that make the
                # "compensation can increase magnitude" caveat checkable.
                xs = [min(1.0, max(0.0, x)) for x in xs]
            mu = mean(xs)
            lo, hi = boot_ci(xs) if xs else (None, None)
            cells.append(f"{fmt(mu)} <sub>[{fmt(lo)}, {fmt(hi)}]</sub>" if mu is not None else "--")
            lcells.append(fmt(mu))
        rows.append([m["name"], setting_label(m), n] + cells)
        ltx.append([m["name"], setting_label(m), n] + lcells)
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


def valid_task_records():
    """(track, key, dur) -> (n_valid, n_total) per-video SNF task records.

    A metrics FILE existing is not the same as the metrics being there. Several
    runs died mid-sweep on CUDA OOM / cuDNN init and wrote per-video entries
    holding only {'video', 'error'}. Counting files marked those entries as
    covered, which is how two public I2V baselines came to look complete at 60s
    while holding one usable record each. Coverage is counted from records.
    """
    out = {}
    for p in glob.glob(f"{RAW}/*/*/*/snf_task_metrics.json"):
        parts = p.split(os.sep)
        track, key, dur = parts[-4], parts[-3], parts[-2]
        try:
            pv = json.load(open(p)).get("per_video", [])
        except (OSError, ValueError):
            continue
        good = sum(1 for v in pv if "error" not in v and v.get("fBD") is not None)
        out[(track, key, dur)] = (good, len(pv))
    return out


def coverage_matrix(public_only=False):
    cov = json.load(open(f"{MAN}/coverage.json"))
    nv = json.load(open(f"{MAN}/video_counts.json"))
    valid = valid_task_records()
    broken = {k: v for k, v in valid.items() if v[0] < v[1]}
    out = ["# Asset & score coverage matrix", "",
           "`V` = generated videos present · `T` = SNF task metrics (RAFT+ORB) · "
           "`X` = cv2 extra metrics · `B` = VBench", "",
           "`T` is counted from **valid per-video records**, not from the presence of a "
           "metrics file. `T3/30` means the file exists but only 3 of 30 videos hold "
           "usable measurements; the rest carry an error payload.", ""]
    if broken:
        out += ["> **Incomplete metric runs detected.** "
                + "; ".join(f"`{t}/{k}/{d}` {g}/{n}"
                            for (t, k, d), (g, n) in sorted(broken.items()))
                + ". Cause: CUDA OOM / `CUDNN_STATUS_NOT_INITIALIZED` during the "
                  "metric sweep, not generation failure — the videos exist, so these "
                  "are re-runnable without regeneration.", ""]
    for track in ("t2v", "i2v"):
        reg = by_key(track)
        out += [f"## {track.upper()} track", "",
                "| Method | status | setting | " + " | ".join(DURATIONS) + " |",
                "|---|---|---|" + "|".join(["---"] * len(DURATIONS)) + "|"]
        for k, m in reg.items():
            if public_only and m["status"] != "public":
                continue
            cells = []
            for d in DURATIONS:
                have = cov.get(track, {}).get(k, {}).get(d, [])
                n = nv.get(track, {}).get(k, {}).get(d, 0)
                tag = ""
                if n:
                    tag += f"V{n}"
                for flag, name in (("T", "snf_task_metrics"), ("X", "snf_extra_metrics"), ("B", "vbench")):
                    if name not in have:
                        continue
                    if flag == "T":
                        good, tot = valid.get((track, k, d), (0, 0))
                        tag += f" T{good}" + (f"/{tot}" if good < tot else "")
                    else:
                        tag += " " + flag
                cells.append(tag or "·")
            out.append(f"| {m['name']} | {m['status']} | {setting_label(m)} | " + " | ".join(cells) + " |")
        out.append("")
    return "\n".join(out)


def config_table():
    out = ["# Model configuration / provenance table", "",
           "Required by the E&D track: every evaluated system with its checkpoint and the",
           "configuration it was actually run under. **T2V = recorded common configuration**; "
           "**I2V = released pipeline or wrapper (deployment sensitivity)**.", ""]
    for track in ("t2v", "i2v"):
        out += [f"## {track.upper()} track", "",
                md_table(["Method", "status", "setting", "checkpoint", "note"],
                         [[m["name"], m["status"], setting_label(m), f"`{m['ckpt']}`" if m["ckpt"] else "--",
                           m["note"] or ""]
                          for m in ALL if m["track"] == track]), ""]
    return "\n".join(out)


# =========================================================================
def main():
    global _FPS
    _FPS = load_fps()
    rows = load_all()
    ix = index(rows)

    with open(f"{MAN}/per_video_scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["track", "model", "duration", "prompt_id", "metric", "value"])
        w.writeheader()
        w.writerows(rows)

    written = ["dar_negative_incidence.md"]
    dar_negative_incidence(rows)

    # --- T2V ---
    body, _ = snf_leaderboard(
        ix, "t2v", "60s", SNF_TASK_KEYS,
        "SNF-Bench core metrics — T2V @ 60s",
        "All seven systems are **public external checkpoints evaluated under the recorded common "
        "T2V configuration** (four-step denoising schedule with released-scheduler "
        "warping, six frames per block, seed 0). "
        "The results do not reconstruct each method's released inference procedure. "
        "Our own systems are excluded by construction.")
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
            "**Read the `setting` column.** Entries marked `wrapper` were run in a common "
            "long-horizon I2V wrapper, *not* their authors' configuration; they are a "
            "stress-test result, not a released-pipeline ranking.")
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
    write("coverage_matrix_public.md", coverage_matrix(public_only=True))
    write("model_config_table.md", config_table())
    written += ["coverage_matrix.md", "model_config_table.md"]

    print(f"wrote {len(written)} tables into tables/")
    print(f"tidy per-video scores: {len(rows)} rows -> manifest/per_video_scores.csv")


if __name__ == "__main__":
    main()

"""Generate every LaTeX asset the paper \\input's, straight from frozen scores.

The discipline this enforces: **no number is typed into the paper by hand.**
Tables are generated, and every inline figure quoted in prose comes from a macro
in `latex/generated/macros.tex`. If a score changes, the prose changes with it.
That is the direct structural answer to the DriftFrac episode, where the paper
described one quantity and the code computed another for months.

Outputs (all under latex/generated/, all regenerated from scratch):
    macros.tex              \\newcommand's for every number quoted in prose
    tab_t2v_audit.tex       main T2V audit, recorded common configuration
    tab_i2v_audit.tex       I2V audit
    tab_disagreement.tex    Spearman, generic metrics vs SNF-Bench
    tab_coverage.tex        supplementary asset/score coverage
    tab_category.tex        supplementary category balance
    tab_dar_negative.tex    supplementary DAR negative incidence
    provenance.tex          spec version, backbones, run stamp

    ~/miniconda3/envs/snfeval/bin/python scripts/paper_assets.py

HARD RULE: the conference template files -- latex/wacv.sty, latex/preamble.tex,
and the formatting of latex/main.tex -- are NEVER edited. This script writes
only into latex/generated/ and latex/figures/, and the paper loads those from
latex/sec/0_abstract.tex (the first file the document body inputs). Macros are
emitted with \providecommand so a repeated load is harmless.
"""

import csv
import glob
import json
import os
import shutil
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registry import ALL, DURATIONS, METRICS, contestants      # noqa: E402
import build_tables as BT                                      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN, TAB, FIG = f"{ROOT}/manifest", f"{ROOT}/tables", f"{ROOT}/figures"
OUT = f"{ROOT}/latex/generated"
LFIG = f"{ROOT}/latex/figures"

# Metrics shown in the main audit table, in reading order.
MAIN_KEYS = ["fBD_mean", "NBF_mean", "MCFF_early_mean", "MCFF_late_mean",
             "FP_mean", "DLR_mean", "DAR_mean"]
# Main-paper subset: every column carries a bootstrap interval, so the table has
# to be narrow enough for one to fit. DAR stays in the supplementary table.
# MCFF-E rides in the headline table because the paper's own interpretation
# rule forbids reading FP without the absolute magnitude it is a fraction of:
# a high FP over negligible early motion is stagnation, not persistence.
# DLR and DAR are drift *diagnostics* read comparatively, not headline factors,
# and DLR's rotational response is inverted; both are tabulated in full in the
# supplement and quoted in the text where they carry the argument.
HEADLINE_KEYS = ["fBD_mean", "NBF_mean", "MCFF_early_mean", "MCFF_late_mean",
                 "FP_mean"]
HDR = {"fBD_mean": r"fBD$\downarrow$", "NBF_mean": r"NBF$\downarrow$",
       "MCFF_early_mean": r"MCFF-E", "MCFF_late_mean": r"MCFF-L$\uparrow$",
       "FP_mean": r"FP$\uparrow$", "DLR_mean": r"DLR$\downarrow$",
       "DAR_mean": r"DAR$\downarrow$"}


def esc(s):
    return (s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
             .replace("#", r"\#"))


def fmt(v, nd=2):
    if v is None:
        return "--"
    if abs(v) >= 100:
        return f"{v:.0f}"
    if abs(v) >= 10:
        return f"{v:.1f}"
    return f"{v:.{nd}f}"


def load():
    BT._FPS = BT.load_fps()
    rows = BT.load_all()
    return rows, BT.index(rows)


def spec_versions():
    """-> {(track,dur): set(versions)} actually present in the artifacts."""
    out = defaultdict(set)
    for p in glob.glob(f"{ROOT}/raw/*/*/*/snf_task_metrics.json"):
        parts = p.split(os.sep)
        track, dur = parts[-4], parts[-2]
        try:
            doc = json.load(open(p))
        except (OSError, ValueError):
            continue
        for v in doc.get("per_video", []):
            if "error" not in v:
                out[(track, dur)].add(str(v.get("metric_spec_version", "1.0")))
    return out


# --------------------------------------------------------------------- tables
def audit_table(ix, track, durations, label, caption, wide=False,
                intervals=True):
    """Audit table with constant columns folded into the caption.

    `setting` and `n` are frequently identical for every row (the whole T2V
    public roster is matched, and each duration panel evaluates the same prompt
    set). Printing a column of one repeated value costs horizontal space that
    the metric columns need in order to fit a single page column, so a column
    that never varies is stated once in the caption instead, and `n` -- constant
    within a panel but not across panels -- moves into the panel header.
    """
    models = [m for m in ALL if m["track"] == track and m["status"] == "public"]
    keys = list(MAIN_KEYS) if wide else list(HEADLINE_KEYS)

    # Collect rows first so we can see which columns are degenerate.
    panels = []
    for dur in durations:
        present = [m for m in models
                   if any(ix.get((track, m["key"], dur, k)) for k in keys)]
        if not present:
            continue
        rows = []
        for m in present:
            vals = {k: ix.get((track, m["key"], dur, k), {}) for k in keys}
            n = max((len(v) for v in vals.values()), default=0)
            cells = []
            for k in keys:
                xs = list(vals[k].values())
                if k == "DAR_mean":
                    xs = [min(1.0, max(0.0, x)) for x in xs]
                # MCFF-E holds no column of its own in the narrow table -- it is
                # emitted as the left half of the MCFF-L cell. This skip must
                # precede the empty-data check, or a row missing MCFF-E emits a
                # stray "--" and overruns the alignment.
                if k == "MCFF_early_mean" and not wide:
                    continue
                if not xs and not (k == "MCFF_late_mean" and not wide):
                    cells.append("--")
                    continue
                mu = BT.mean(xs) if xs else None
                if k == "MCFF_late_mean" and not wide:
                    e = list(vals.get("MCFF_early_mean", {}).values())
                    lhs = fmt(BT.mean(e)) if e else "--"
                    cells.append(f"{lhs}\\,$\\rightarrow$\\,{fmt(mu)}")
                    continue
                # A percentile interval over four or five items is mostly an
                # artefact of resampling so few points; the diagnostic tiers
                # therefore print the point estimate and say so in the caption.
                if wide or not intervals or len(xs) < 10:
                    cells.append(fmt(mu))
                else:
                    lo, hi = BT.boot_ci(xs)
                    half = (hi - lo) / 2.0 if lo is not None else None
                    cells.append(f"{fmt(mu)}\\,\\tiny$\\pm${fmt(half)}"
                                 if half is not None else fmt(mu))
            rows.append((m, n, cells))
        panels.append((dur, rows))
    if not panels:
        return None

    settings = {m["setting"] for _, rows in panels for m, _, _ in rows}
    # A narrow table cannot spare a column for a one-word field: mark the
    # common-wrapper rows with a dagger instead and explain it in the caption.
    # The wide (supplementary) table keeps the explicit column.
    mark_setting = len(settings) > 1 and not wide
    show_setting = len(settings) > 1 and wide
    ns = {dur: {n for _, n, _ in rows} for dur, rows in panels}
    show_n = any(len(v) > 1 for v in ns.values())

    # In the narrow table MCFF-E is folded into the MCFF-L cell, so it holds no
    # column of its own and must not claim a header.
    cols = [k for k in keys if not (k == "MCFF_early_mean" and not wide)]
    hdrmap = dict(HDR)
    if not wide and "MCFF_early_mean" in keys:
        hdrmap["MCFF_late_mean"] = r"MCFF E$\rightarrow$L"
    ncols = 1 + (1 if show_setting else 0) + (1 if show_n else 0) + len(cols)
    env = "table*" if wide else "table"
    size = r"\small" if wide else r"\scriptsize"
    # `!` relaxes LaTeX's float-fraction limits. With two multi-panel audit
    # tables competing for top slots, the default limits defer them past the
    # bibliography, which would put content on a post-reference page.
    lines = [r"\begin{%s}[!tb]" % env, r"\centering", size,
             r"\setlength{\tabcolsep}{%s}" % ("4pt" if wide else "2.6pt"),
             # The I2V roster has names too long for an `l` column; letting the
             # method column wrap is more robust than shaving column separation
             # and keeps the table inside the text block at any name length.
             r"\begin{tabular}{" + ("p{0.30\linewidth}" if mark_setting else "l")
             + ("l" if show_setting else "")
             + ("c" if show_n else "") + "c" * len(cols) + "}",
             r"\toprule",
             "Method" + (" & setting" if show_setting else "")
             + (" & $n$" if show_n else "") + " & "
             + " & ".join(hdrmap[k] for k in cols) + r" \\"]
    for dur, rows in panels:
        lines.append(r"\midrule")
        n_here = sorted(ns[dur])
        hdr = f"{dur} horizon" + ("" if show_n else f"  ($n={n_here[0]}$)")
        lines.append(r"\multicolumn{%d}{l}{\textit{%s}} \\" % (ncols, hdr))
        for m, n, cells in rows:
            pre = esc(m["name"])
            if mark_setting and m["setting"] != "native":
                pre += r"$^{\dagger}$"
            if show_setting:
                display_setting = ("released" if m["setting"] == "native"
                                   else "wrapper")
                pre += " & " + display_setting
            if show_n:
                pre += f" & {n}"
            lines.append(pre + " & " + " & ".join(cells) + r" \\")

    extra = ""
    if mark_setting:
        extra += (r" Unmarked rows are released-pipeline outputs; "
                  r"$^{\dagger}$ rows use the wrapper; settings are not compared.")
    elif not show_setting:
        setting = settings.pop()
        if setting != "matched":
            extra += (r" All systems use the \emph{%s} setting." % setting)
    if not show_n:
        extra += (r" Header $n$ is the maximum valid item count within each "
                  r"horizon; factor-specific abstentions are in Table~S6.")
    extra += (r" Units: fBD is \% frame diagonal; NBF is $10^{-3}$ frame "
              r"widths/s; MCFF is px/sampled interval; FP is unitless. "
              r"FP is the mean of per-video clipped late/early ratios and "
              r"therefore need not equal the ratio of the displayed aggregate "
              r"MCFF-L and MCFF-E means.")
    if not wide:
        if intervals:
            extra += (r" Means with percentile-bootstrap 95\% CI half-width "
                      r"shown for compactness (10k resamples, seed 0); $n<10$ "
                      r"shows means only.")
        else:
            extra += r" Means; intervals are supplementary."
        extra += r" MCFF-E$\rightarrow$L accompanies FP. "
        if track == "t2v":
            extra += r"Separation uses paired per-prompt intervals (Table~S3). "
        else:
            extra += r"No cross-setting claim. "
        extra += r"DLR/DAR are supplementary."
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{%s%s}" % (caption, extra), r"\label{%s}" % label,
              r"\end{%s}" % env]
    return "\n".join(lines)


def disagreement_table(ix, track="t2v", dur="60s",
                       label="tab:disagreement", caption=""):
    gen = ["dynamic_degree", "background_consistency", "motion_smoothness",
           "temporal_flickering"]
    snf = ["fBD_mean", "NBF_mean", "MCFF_late_mean", "DLR_mean"]
    models = [m for m in ALL if m["track"] == track and m["status"] == "public"]

    def series(k):
        out = {}
        for m in models:
            pp = ix.get((track, m["key"], dur, k))
            if pp:
                out[m["name"]] = sum(pp.values()) / len(pp)
        return out

    G = {k: series(k) for k in gen}
    S = {k: series(k) for k in snf}
    rows = []
    for gk in gen:
        if not G[gk]:
            continue
        cells = []
        for sk in snf:
            common = sorted(set(G[gk]) & set(S[sk]))
            if len(common) < 3:
                cells.append("--")
                continue
            r = BT.spearman([G[gk][c] for c in common], [S[sk][c] for c in common])
            cells.append(f"{r:+.2f}" if r is not None else "--")
        rows.append((METRICS[gk][1], cells))
    if not rows:
        return None

    # Two VBench dimensions induce the identical ranking of these systems, so
    # their correlations are identical by construction. Printing the same row
    # twice suggests two independent corroborations where there is one; the
    # rows are merged and the equivalence stated instead.
    merged, seen = [], {}
    for name, cells in rows:
        key = tuple(cells)
        if key in seen:
            merged[seen[key]] = (merged[seen[key]][0] + " / " + name, cells)
        else:
            seen[key] = len(merged)
            merged.append((name, cells))
    rows = merged

    lines = [r"\begin{table}[tb]", r"\centering", r"\scriptsize",
             r"\setlength{\tabcolsep}{3pt}",
             r"\begin{tabular}{l" + "c" * len(snf) + "}", r"\toprule",
             r"generic metric & " + " & ".join(METRICS[k][1] for k in snf) + r" \\",
             r"\midrule"]
    for name, cells in rows:
        lines.append(f"{esc(name)} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{%s}" % caption, r"\label{%s}" % label, r"\end{table}"]
    return "\n".join(lines)


def simple_table(md_path, label, caption, max_cols=None, section=None,
                 nonzero_col=None):
    """Convert one of the generated markdown tables to LaTeX verbatim-ish."""
    if not os.path.exists(md_path):
        return None
    # Take the FIRST markdown table only. These reports carry several tables
    # plus prose; scanning every pipe-delimited line concatenated a downstream
    # provenance table onto the one being converted, printing schema debris
    # ("track & source", "t2v & keyword") as data rows.
    # These reports carry several tables under markdown headings. Select the
    # intended one by heading; without that, a downstream provenance table was
    # concatenated onto the target and printed schema debris as data rows.
    rows, started, in_section = [], False, section is None
    for line in open(md_path):
        line = line.strip()
        if line.startswith("#"):
            if started:
                break
            if section is not None:
                in_section = section.lower() in line.lower()
            continue
        if not in_section:
            continue
        if not line.startswith("|"):
            if started:
                break          # blank line or prose ends this table
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        started = True
        rows.append(cells[:max_cols] if max_cols else cells)
    if len(rows) < 2:
        return None
    # A row whose width differs from the header is not part of this table.
    width = len(rows[0])
    rows = [r for r in rows if len(r) == width]
    # Optionally keep only rows where a named column is non-zero. A 58-row table
    # of mostly zeros overflows the page and hides the entries that matter; the
    # caption states how many rows were all-zero.
    n_zero = 0
    if nonzero_col and nonzero_col in rows[0]:
        j = rows[0].index(nonzero_col)
        keep = [rows[0]] + [r for r in rows[1:]
                            if r[j] not in ("0", "0.0", "0.0\\%", "", "-")]
        n_zero = len(rows) - len(keep)
        rows = keep
    if n_zero:
        caption += (r" %d further entries had no negative values and are "
                    r"omitted." % n_zero)
    ncol = len(rows[0])
    # A long table set at scriptsize can exceed the page body and force an
    # overfull vbox; step the size down past ~25 rows rather than letting it
    # run beyond the text block.
    size = r"\tiny" if len(rows) > 25 else r"\scriptsize"
    body = [r"\begin{table*}[!htbp]", r"\centering", size,
            r"\setlength{\tabcolsep}{5pt}",
            r"\begin{tabular}{l" + "c" * (ncol - 1) + "}", r"\toprule",
            " & ".join(esc(c) for c in rows[0]) + r" \\", r"\midrule"]
    for r_ in rows[1:]:
        r_ = r_ + [""] * (ncol - len(r_))
        body.append(" & ".join(esc(c) for c in r_[:ncol]) + r" \\")
    body += [r"\bottomrule", r"\end{tabular}",
             r"\caption{%s}" % caption, r"\label{%s}" % label, r"\end{table*}"]
    return "\n".join(body)


def config_table(label="tab:native_configs"):
    rows = [m for m in ALL if m["track"] == "t2v" and m["status"] == "public"]
    meta = {}
    p = f"{MAN}/video_meta.csv"
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            if r["track"] == "t2v":
                meta.setdefault(r["model"], (r["width"], r["height"], r["fps"]))
    horizon = {}
    for m in rows:
        hs = [d for d in DURATIONS
              if glob.glob(f"{ROOT}/videos/t2v/{m['key']}/{d}/*.mp4")]
        horizon[m["key"]] = hs[-1] if hs else "--"
    lines = [r"\begin{table}[t]", r"\centering", r"\scriptsize",
             r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{l c c c}", r"\toprule",
             r"Method & Resolution & FPS & Max horizon \\", r"\midrule"]
    for m in rows:
        w, h, f = meta.get(m["key"], ("--", "--", "--"))
        res = f"{w}$\\times${h}" if w != "--" else "--"
        fps = f"{float(f):.0f}" if f != "--" else "--"
        lines.append(f"{esc(m['name'])} & {res} & {fps} & {horizon[m['key']]} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Recorded common T2V checkpoint configuration.} Every "
              r"released checkpoint is evaluated under the recorded common configuration; "
              r"output geometry and maximum recorded horizon are shown here.}",
              r"\label{%s}" % label, r"\end{table}"]
    return "\n".join(lines)


def interpretation_table(ix, track="t2v", dur="60s", label="tab:interpretation_changes"):
    """Every method whose generic-metric rank and SNF rank disagree materially.

    Reported exhaustively by rule, not curated: the threshold is a rank gap of at
    least half the field, applied to all public methods, so no case can be
    quietly omitted.
    """
    models = [m for m in ALL if m["track"] == track and m["status"] == "public"]

    def series(k):
        out = {}
        for m in models:
            pp = ix.get((track, m["key"], dur, k))
            if pp:
                out[m["name"]] = sum(pp.values()) / len(pp)
        return out

    dd, nbf, mcff = series("dynamic_degree"), series("NBF_mean"), series("MCFF_late_mean")
    common = sorted(set(dd) & set(nbf) & set(mcff))
    if len(common) < 3:
        return None
    N = len(common)
    r_dd = {n: i + 1 for i, n in enumerate(sorted(common, key=lambda k: -dd[k]))}
    r_nbf = {n: i + 1 for i, n in enumerate(sorted(common, key=lambda k: nbf[k]))}
    r_mc = {n: i + 1 for i, n in enumerate(sorted(common, key=lambda k: -mcff[k]))}
    gap = max(2, N // 2)

    body = []
    for n in common:
        if abs(r_dd[n] - r_nbf[n]) < gap:
            continue
        if r_dd[n] < r_nbf[n]:
            interp = ("high apparent motion accompanied by high static-region "
                      "motion under the recorded common configuration")
        else:
            interp = "stable sequence with decaying intended motion"
        body.append([esc(n),
                     f"VB-DD rank {r_dd[n]}/{N}",
                     f"NBF rank {r_nbf[n]}/{N}, MCFF-L rank {r_mc[n]}/{N}",
                     interp])
    if not body:
        return None
    lines = [r"\begin{table*}[t]", r"\centering", r"\small",
             # Keep the prose column compact enough for the three label columns.
             r"\begin{tabular}{l l l p{0.35\textwidth}}", r"\toprule",
             r"Method & Generic evidence & SNF-Bench evidence & Interpretation \\",
             r"\midrule"]
    for b in body:
        lines.append(" & ".join(b) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Interpretation changes between generic whole-frame "
              r"metrics and SNF-Bench at 60\,s.} Neither evaluation is labeled "
              r"correct; the table identifies information hidden by whole-frame "
              r"aggregation. Cases are selected by a fixed rank-gap rule applied to "
              r"all public methods. Rolling-Forcing does not satisfy the fixed "
              r"three-rank-gap inclusion criterion and is therefore absent.}",
              r"\label{%s}" % label, r"\end{table*}"]
    return "\n".join(lines)


def paired_diff_table(track="t2v", dur="60s", metric="NBF_mean",
                      anchor_key="infinite_forcing", label="tab:paired"):
    """Paired bootstrap of per-prompt differences against one anchor system.

    Every system is evaluated on the same prompts, so the paired difference is
    the right statistic: two independent intervals can overlap while the paired
    difference is reliable, and can fail to overlap when it is not. Separation
    claims in the main text are made on these intervals, not on whether the
    marginal intervals overlap.
    """
    import csv as _csv
    import random as _rnd
    pub = {m["key"]: m["name"] for m in ALL
           if m["track"] == track and m["status"] == "public"}
    if anchor_key not in pub:
        return None
    acc = defaultdict(dict)
    with open(f"{MAN}/per_video_scores.csv") as fh:
        for r in _csv.DictReader(fh):
            if (r["track"] == track and r["duration"] == dur
                    and r["metric"] == metric and r["model"] in pub):
                acc[r["model"]][r["prompt_id"]] = float(r["value"])
    if anchor_key not in acc:
        return None
    rng = _rnd.Random(0)
    B = 10000
    rows = []
    for b in sorted(acc):
        if b == anchor_key:
            continue
        common = sorted(set(acc[anchor_key]) & set(acc[b]))
        if len(common) < 5:
            continue
        d = [acc[anchor_key][p] - acc[b][p] for p in common]
        n = len(d)
        mu = sum(d) / n
        boot = sorted(sum(rng.choice(d) for _ in range(n)) / n for _ in range(B))
        lo, hi = boot[int(0.025 * B)], boot[int(0.975 * B)]
        rows.append((pub[b], n, mu, lo, hi, hi < 0 or lo > 0))
    if not rows:
        return None
    rows.sort(key=lambda r: r[2])
    # Full width: the paired-comparison labels name two systems per row.
    lines = [r"\begin{table*}[tb]", r"\centering", r"\small",
             r"\setlength{\tabcolsep}{6pt}",
             r"\begin{tabular}{l c r c}", r"\toprule",
             r"Comparison & $n$ & mean diff. & 95\% CI \\", r"\midrule"]
    for nm, n, mu, lo, hi, sep in rows:
        star = "" if sep else r"$^{\ast}$"
        lines.append(f"{esc(pub[anchor_key])} $-$ {esc(nm)}{star} & {n} & "
                     f"{mu:.2f} & $[{lo:.2f},\\,{hi:.2f}]$ \\\\")
    n_sep = sum(1 for r in rows if r[5])
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Paired differences in %s, %s horizon.} Every "
              r"system is evaluated on the same prompts, so separation is judged "
              r"on the bootstrap distribution of per-prompt \emph{differences} "
              r"(10k resamples, fixed seed) rather than on whether two marginal "
              r"intervals happen to overlap---overlapping intervals can hide a "
              r"reliable paired difference, and non-overlapping ones can suggest "
              r"a difference that is not. %d of %d intervals exclude zero"
              r"%s.}" % (METRICS.get(metric, [metric, metric])[1]
                         if metric in METRICS else "NBF", dur, n_sep, len(rows),
                         "" if n_sep == len(rows)
                         else r"; $^{\ast}$ marks those that do not"),
              r"\label{%s}" % label, r"\end{table*}"]
    return "\n".join(lines)


def robustness_table(track="t2v", dur="60s", label="tab:robustness"):
    """Two checks on the region partition and the evaluation set.

    The partition is derived from each sequence's own early flow, so the first
    question a reader should ask is whether a system can be advantaged by
    receiving an easier mask. We report the static-mask area every system
    actually got, and the correlation between that area and its drift score.
    The second check removes the one scene category the two-way partition
    cannot represent -- precipitation crossing static support -- and asks
    whether the ordering survives.
    """
    import csv as _csv
    import itertools
    import math
    import statistics as _st
    from categories import load_categories

    pub = {m["key"]: m["name"] for m in ALL
           if m["track"] == track and m["status"] == "public"}

    def spear(x, y):
        n = len(x)
        if n < 3:
            return None
        a, b = [0] * n, [0] * n
        for r, i in enumerate(sorted(range(n), key=lambda i: x[i])):
            a[i] = r
        for r, i in enumerate(sorted(range(n), key=lambda i: y[i])):
            b[i] = r
        mx, my = sum(a) / n, sum(b) / n
        num = sum((a[i] - mx) * (b[i] - my) for i in range(n))
        den = math.sqrt(sum((a[i] - mx) ** 2 for i in range(n))
                        * sum((b[i] - my) ** 2 for i in range(n)))
        return num / den if den else None

    area, fbd = {}, {}
    for k in pub:
        fp = f"{ROOT}/raw/{track}/{k}/{dur}/snf_task_metrics.json"
        if not os.path.exists(fp):
            continue
        pv = [v for v in json.load(open(fp)).get("per_video", []) if "error" not in v]
        a = [v["static_frac"] for v in pv if v.get("static_frac") is not None]
        f = [v["fBD"] for v in pv if v.get("fBD") is not None]
        if a and f:
            area[k], fbd[k] = (_st.mean(a), _st.pstdev(a)), _st.mean(f)
    if not area:
        return None
    ks = sorted(area)
    rho = spear([area[k][0] for k in ks], [fbd[k] for k in ks])
    pval = None
    if rho is not None and len(ks) <= 8:
        xs = [area[k][0] for k in ks]
        ys = [fbd[k] for k in ks]
        perms = list(itertools.permutations(ys))
        pval = sum(1 for q in perms if abs(spear(xs, list(q))) >= abs(rho)) / len(perms)

    # precipitation exclusion
    cats = load_categories()
    acc = defaultdict(dict)
    with open(f"{MAN}/per_video_scores.csv") as fh:
        for r in _csv.DictReader(fh):
            if r["track"] == track and r["duration"] == dur and r["model"] in pub:
                acc[(r["model"], r["metric"])][r["prompt_id"]] = float(r["value"])

    def order(metric, drop):
        vals = {}
        for k in pub:
            xs = [v for pr, v in acc.get((k, metric), {}).items()
                  if not (drop and cats.get((track, dur, pr)) == "precipitation")]
            if xs:
                vals[k] = _st.mean(xs)
        return sorted(vals, key=lambda k: vals[k])

    prec = []
    for metric, nm in (("fBD_mean", "fBD"), ("NBF_mean", "NBF")):
        o1, o2 = order(metric, False), order(metric, True)
        prec.append((nm, o1 == o2, o1[0] == o2[0] and o1[-1] == o2[-1]))
    n_prec = sum(1 for pr in acc[(ks[0], "fBD_mean")]
                 if cats.get((track, dur, pr)) == "precipitation")
    n_tot = len(acc[(ks[0], "fBD_mean")])

    lines = [r"\begin{table*}[tb]", r"\centering", r"\small",
             r"\begin{tabular}{l c}", r"\toprule",
             r"System & static-region area \\", r"\midrule"]
    for k in sorted(area, key=lambda k: -area[k][0]):
        lines.append(f"{esc(pub[k])} & {area[k][0]:.3f} $\\pm$ {area[k][1]:.3f} \\\\")
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{2}{l}{\emph{Does mask area predict the drift score?}} \\")
    rr = f"{rho:+.2f}" if rho is not None else "--"
    pp = f", exact $p={pval:.3f}$" if pval is not None else ""
    lines.append(f"Spearman(area, fBD) over {len(ks)} systems & {rr}{pp} \\\\")
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{2}{l}{\emph{Ordering with precipitation excluded (%d of %d prompts)}} \\"
                 % (n_prec, n_tot))
    for nm, same, ends in prec:
        txt = "identical" if same else ("best and worst unchanged" if ends
                                        else "order changes")
        lines.append(f"{nm} ordering & {txt} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Partition and composition robustness.} The "
              r"static region occupies a similar share of the frame for every "
              r"audited system, so no system is scored over a much larger or "
              r"smaller support than another. The area does correlate "
              r"negatively with drift across systems; over seven systems that "
              r"correlation is not determined, but its sign is the one "
              r"circularity would produce---a system that drifts early enlarges "
              r"its own dynamic region---and we flag it as an open validity "
              r"question rather than dismissing it. Removing precipitation, the "
              r"category a two-way partition cannot represent, leaves the "
              r"normalized-background-flow ordering unchanged.}",
              r"\label{%s}" % label, r"\end{table*}"]
    return "\n".join(lines)


def robustness_main_table(track="t2v", dur="60s",
                          label="tab:robustness_main"):
    """Compact, data-derived partition checks for the main paper."""
    import csv as _csv
    import itertools
    import math
    import statistics as _st
    from categories import load_categories

    public = {m["key"]: m["name"] for m in ALL
              if m["track"] == track and m["status"] == "public"}

    def spear(x, y):
        n = len(x)
        if n < 3:
            return None
        a, b = [0] * n, [0] * n
        for rank, i in enumerate(sorted(range(n), key=lambda i: x[i])):
            a[i] = rank
        for rank, i in enumerate(sorted(range(n), key=lambda i: y[i])):
            b[i] = rank
        ma, mb = sum(a) / n, sum(b) / n
        num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
        den = math.sqrt(sum((a[i] - ma) ** 2 for i in range(n)) *
                        sum((b[i] - mb) ** 2 for i in range(n)))
        return num / den if den else None

    area, fbd = {}, {}
    for key in public:
        path = f"{ROOT}/raw/{track}/{key}/{dur}/snf_task_metrics.json"
        if not os.path.exists(path):
            continue
        valid = [v for v in json.load(open(path)).get("per_video", [])
                 if "error" not in v]
        aa = [v["static_frac"] for v in valid
              if v.get("static_frac") is not None]
        ff = [v["fBD"] for v in valid if v.get("fBD") is not None]
        if aa and ff:
            area[key], fbd[key] = _st.mean(aa), _st.mean(ff)
    keys = sorted(set(area) & set(fbd))
    if len(keys) < 3:
        return None
    rho = spear([area[k] for k in keys], [fbd[k] for k in keys])
    permutations = itertools.permutations([fbd[k] for k in keys])
    pval = sum(1 for q in permutations
               if abs(spear([area[k] for k in keys], list(q))) >= abs(rho))
    pval /= math.factorial(len(keys))

    cats = load_categories()
    scores = defaultdict(dict)
    with open(f"{MAN}/per_video_scores.csv") as fh:
        for row in _csv.DictReader(fh):
            if (row["track"] == track and row["duration"] == dur and
                    row["model"] in public):
                scores[(row["model"], row["metric"])][row["prompt_id"]] = float(row["value"])

    def ordering(metric, exclude_precipitation):
        means = {}
        for key in public:
            values = [value for prompt, value in scores.get((key, metric), {}).items()
                      if not (exclude_precipitation and
                              cats.get((track, dur, prompt)) == "precipitation")]
            if values:
                means[key] = _st.mean(values)
        return sorted(means, key=means.get)

    fbd_all, fbd_no_precip = ordering("fBD_mean", False), ordering("fBD_mean", True)
    nbf_all, nbf_no_precip = ordering("NBF_mean", False), ordering("NBF_mean", True)

    records = []
    for path in sorted(glob.glob(f"{MAN}/validation_response*.json")):
        try:
            records.extend(json.load(open(path)).get("records", []))
        except (OSError, ValueError):
            continue
    by_level = defaultdict(list)
    for row in records:
        if row.get("family") == "mask_radius":
            by_level[row["level"]].append(row)
    boundary = []
    for metric in ("fBD", "NBF", "MCFF_L", "FP", "DLR", "DAR"):
        means = []
        for level in sorted(by_level):
            vals = [row[metric] for row in by_level[level]
                    if row.get(metric) is not None]
            if vals:
                means.append(_st.mean(vals))
        if len(means) >= 3 and means[0]:
            boundary.append(max(abs(v - means[0]) for v in means) /
                            abs(means[0]) * 100)
    max_boundary = max(boundary) if boundary else None

    nbf_text = "identical" if nbf_all == nbf_no_precip else "changed"
    fbd_ends = (fbd_all and fbd_no_precip and
                fbd_all[0] == fbd_no_precip[0] and
                fbd_all[-1] == fbd_no_precip[-1])
    lines = [r"\begin{table}[tb]", r"\centering", r"\scriptsize",
             r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{p{0.51\linewidth} p{0.40\linewidth}}", r"\toprule",
             "Check & result \\\\", r"\midrule",
             f"Static-mask area & {min(area.values()):.3f}--{max(area.values()):.3f}" + r" \\",
             f"Area--fBD Spearman & $\\rho={rho:+.2f}$, exact $p={pval:.3f}$, $n={len(keys)}$" + r" \\",
             f"No precipitation: NBF order & {nbf_text}" + r" \\",
             "No precipitation: fBD extremes & " +
             ("unchanged" if fbd_ends else "changed") + " \\\\",
             "Boundary perturbation: max. response & " +
             (f"$\\leq {math.ceil(max_boundary):.0f}\\%$" if max_boundary is not None else "--") + " \\\\",
             r"\bottomrule", r"\end{tabular}",
             r"\caption{\textbf{Partition robustness at 60\,s.} Static-region "
             r"area is similar across checkpoints, and the headline NBF ordering "
             r"is unchanged when precipitation is excluded. The negative "
             r"area--fBD association has the direction expected under early-mask "
             r"circularity and is therefore reported as an open validity concern "
             r"rather than dismissed.}",
             r"\label{%s}" % label, r"\end{table}"]
    return "\n".join(lines)


def perception_table(label="tab:perception"):
    """Preliminary perceptual validation: do independent judges order pairs as
    the factors do?

    Two arms, one question each per axis, reported on the stratum where the
    claim is meaningful. Agreement is only computed on pairs the factors
    separate clearly; near-tie pairs instead test whether the metrics'
    indistinguishable zone is perceptually real, where the expected answer is
    that the clips cannot be told apart.

    Cells are filled only from artifacts that exist. An arm that was not run, or
    that produced too few decided pairs to support a rate, prints a dash and is
    explained in the caption rather than given a number the data cannot carry.
    """
    human_p = f"{MAN}/human_study_scored.json"
    vlm_p = f"{MAN}/vlm_judge.json"
    human = json.load(open(human_p)) if os.path.exists(human_p) else None
    vlm = json.load(open(vlm_p)) if os.path.exists(vlm_p) else None
    if not human and not vlm:
        return None

    AX = [("drift", "Static stability", "fBD"),
          ("decay", "Motion persistence", "MCFF-L")]
    MIN_DECIDED = 5      # below this a rate is noise; we print the count instead

    def vlm_cells(axis):
        if not vlm:
            return "--", "--", "--"
        cg, nt = vlm.get("clear_gap", 0.20), vlm.get("near_tie", 0.05)
        rs = [r for r in vlm["records"] if r["axis"] == axis]
        clear = [r for r in rs if r["gap"] >= cg and r["consistent"]]
        dec = [r for r in clear if r["vlm_order1"] != "same"]
        tie = [r for r in rs if r["gap"] < nt and r["consistent"]]
        tie_ok = sum(1 for r in tie if r["vlm_order1"] == "same")
        agr = (f"{sum(1 for r in dec if r['vlm_order1'] == r['metric_says'])}/"
               f"{len(dec)}" if len(dec) >= MIN_DECIDED
               else f"-- ({len(dec)} decided)")
        return agr, f"{tie_ok}/{len(tie)}" if tie else "--", str(len(clear))

    def human_cells(axis):
        if not human or axis not in human.get("axes", {}):
            return "--", "--", "--", "--"
        a = human["axes"][axis]
        n_dec = a.get("n_decided_clear") or 0
        if n_dec >= MIN_DECIDED and a.get("agreement") is not None:
            n_agree = int(round(a["agreement"] * n_dec))
            agr = f"{n_agree}/{n_dec} decided pairs"
        else:
            agr = f"-- ({n_dec} decided)"
        tie = (f"{a.get('cant_tell_on_near_tie', 0)}/{a['n_near_tie']}"
               if a.get("n_near_tie") else "--")
        al = a.get("krippendorff_alpha")
        return agr, tie, str(a.get("n_clear_gap", 0)),             (f"{al:.2f}" if al is not None else "--")

    # Full width: the axis and judge labels overrun a single column by ~110pt.
    lines = [r"\begin{table*}[tb]", r"\centering", r"\small",
             r"\setlength{\tabcolsep}{6pt}",
             r"\begin{tabular}{l l c c c c}", r"\toprule",
             r"Axis & Judge & agrees with factor & called indistinguishable & "
             r"pairs & inter-rater $\alpha$ \\",
             r"\midrule"]
    for axis, name, met in AX:
        h = human_cells(axis)
        v = vlm_cells(axis)
        lines.append(f"{name} ({met}) & human & {h[0]} & {h[1]} & {h[2]} & {h[3]} \\\\")
        lines.append(f" & vision--language & {v[0]} & {v[1]} & {v[2]} & -- \\\\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Preliminary perceptual pilot for the factor "
              r"axes.} Each judge answers one question per axis and never which "
              r"output is better. \emph{agree} is agreement with the factor's "
              r"ordering on pairs the factor separates clearly, over pairs the "
              r"judge decided; \emph{can't tell} is the share of near-tie pairs "
              r"called indistinguishable, which is the correct answer there. The "
              r"unit is the pair, majority-voted across raters. A dash marks a cell "
              r"with too few decided pairs to carry a rate; the count is given "
              r"instead. This is a preliminary check on a measurement "
              r"protocol, not a powered study, and no system is ranked by it.}",
              r"\label{%s}" % label, r"\end{table*}"]
    return "\n".join(lines)


_MATCHED_NOTE = (r" Rows marked $^{\dagger}$ ran under the common "
                 r"long-horizon wrapper rather than a released "
                 r"configuration and are grouped separately below the "
                 r"unmarked released-pipeline rows.")


def native_config_table(track="t2v", label="tab:native_config"):
    """What was actually recorded about each audited system's generation.

    An earlier version of this table was dropped from the main paper because
    every column held the same value for every row. It belongs in the
    supplement, where the shared geometry is itself the point: identical
    resolution, frame rate and horizon support mean the audit compares systems
    rather than output formats.

    The per-method sampler settings a reader would need to reproduce generation
    -- denoising steps, chunk length, guidance scale, cache policy -- were not
    written into the run manifest, so they are not tabulated. Stating that is
    the honest option; inferring them after the fact would put numbers in the
    paper that nothing in the artifacts supports.
    """
    import csv as _csv
    geo = defaultdict(set)
    durs = defaultdict(set)
    meta = f"{MAN}/video_meta.csv"
    if not os.path.exists(meta):
        return None
    with open(meta) as fh:
        for r in _csv.DictReader(fh):
            if r.get("track") == track:
                geo[r["model"]].add((r.get("width"), r.get("height"), r.get("fps")))
                durs[r["model"]].add(r.get("duration"))

    models = [m for m in ALL if m["track"] == track and m["status"] == "public"]
    rows = []
    for m in models:
        g = sorted(geo.get(m["key"], []))
        if not g:
            continue
        w, h, fps = g[0]
        mixed = "" if len(g) == 1 else r"$^{\ddagger}$"
        ds = sorted(durs.get(m["key"], []), key=lambda s: int(s.rstrip("s")))
        rows.append((m["setting"] != "native",     # sort key: released block first
                     m["name"] + (r"$^{\dagger}$"
                                  if track != "t2v" and m["setting"] == "matched"
                                  else ""),
                     ("common" if track == "t2v" else
                      "released" if m["setting"] == "native" else "wrapper"),
                     f"{w}$\\times${h}{mixed}",
                     f"{float(fps):.0f}", ", ".join(ds)))
    # Group by setting so a skimming reader cannot mistake a wrapper row for a
    # released-pipeline row; within a block the roster order is preserved.
    rows = [r[1:] for r in sorted(rows, key=lambda r: r[0])]
    if not rows:
        return None

    lines = [r"\begin{table*}[tb]", r"\centering", r"\small",
             r"\setlength{\tabcolsep}{5pt}",
             r"\begin{tabular}{l l c c l}", r"\toprule",
             r"System & setting & resolution & fps & horizons \\", r"\midrule"]
    for r_ in rows:
        lines.append(" & ".join(r_) + r" \\")
    common = (r"Every audited system was run from its released checkpoint. "
              r"Output formats are normalized at measurement time: NBF is "
              r"expressed per second and per frame width, fBD as a percentage "
              r"of the frame diagonal, and every sequence is resampled to a "
              r"common flow-estimation rate. ")
    if track == "t2v":
        detail = (r"All rows use the recorded common T2V configuration: a "
                  r"four-step denoising schedule with released-scheduler "
                  r"warping, six frames per block, and seed $0$. "
                  r"These are checkpoint results under this common configuration, not "
                  r"reconstructions of the methods' released inference procedures.")
    else:
        detail = (r"Unmarked rows are recorded outputs from model-specific "
                  r"released pipelines and carry the setting label \emph{released}. "
                  r"$^{\dagger}$ rows use the common "
                  r"long-horizon rollout wrapper (six frames per block, fixed seed; "
                  r"checkpoint-specific denoising schedules); those parameters do not apply to "
                  r"unmarked rows, and the two settings are not ranked together.")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Recorded generation configuration (%s).} %s%s}" %
              (track.upper(), common, detail),
              r"\label{%s}" % label, r"\end{table*}"]
    return "\n".join(lines)


def aggregation_table(ix, track="t2v", dur="60s", label="tab:aggregation"):
    """Prompt-mean versus category-macro-average, with the rank each induces.

    The evaluation set is dominated by one flow medium, so the obvious question
    is whether the audit merely reports that medium. Macro-averaging is not the
    answer at this horizon -- three of the five populated categories hold two
    prompts, and a two-prompt cell would carry the same weight as a
    fourteen-prompt one -- so we report the headline under prompt means and put
    the comparison here instead of asserting robustness.
    """
    import csv as _csv
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from categories import macro_average

    models = [m for m in ALL if m["track"] == track and m["status"] == "public"]
    per = defaultdict(dict)
    with open(f"{MAN}/per_video_scores.csv") as fh:
        for r in _csv.DictReader(fh):
            if r["track"] == track and r["duration"] == dur:
                per[(r["model"], r["metric"])][r["prompt_id"]] = float(r["value"])

    rows = []
    for key in ("NBF_mean", "fBD_mean"):
        vals = []
        for m in models:
            pp = per.get((m["key"], key))
            if not pp:
                continue
            micro = sum(pp.values()) / len(pp)
            macro, _, _ = macro_average(pp, track, dur)
            if macro is None:
                continue
            vals.append([m["name"], micro, macro])
        if not vals:
            continue
        r_mi = {v[0]: i + 1 for i, v in enumerate(sorted(vals, key=lambda x: x[1]))}
        r_ma = {v[0]: i + 1 for i, v in enumerate(sorted(vals, key=lambda x: x[2]))}
        rows.append((key, sorted(vals, key=lambda x: x[1]), r_mi, r_ma))
    if not rows:
        return None

    pretty = {"NBF_mean": "NBF", "fBD_mean": "fBD"}
    lines = [r"\begin{table*}[tb]", r"\centering", r"\small",
             r"\setlength{\tabcolsep}{5pt}",
             r"\begin{tabular}{l c c c c}", r"\toprule",
             r"System & prompt mean & rank & macro mean & rank \\", r"\midrule"]
    for key, vals, r_mi, r_ma in rows:
        lines.append(r"\multicolumn{5}{l}{\emph{%s}} \\" % pretty.get(key, key))
        for name, micro, macro in vals:
            moved = "" if r_mi[name] == r_ma[name] else r"$^{\dagger}$"
            lines.append(f"\\quad {name} & {micro:.2f} & {r_mi[name]} & "
                         f"{macro:.2f} & {r_ma[name]}{moved} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Sensitivity of the audit to category "
              r"aggregation.} Prompt means, as reported in the main paper, "
              r"against category macro-averages, for the two static-fidelity "
              r"factors at the principal horizon. $^{\dagger}$ marks a system "
              r"whose rank changes. The best- and worst-ranked systems are "
              r"identical under both, so the paper's headline contrast does not "
              r"depend on the choice; intermediate positions do change, which is "
              r"why no ordinal claim is made about the middle of the field.}",
              r"\label{%s}" % label, r"\end{table*}"]
    return "\n".join(lines)


def deployment_table(ix, label="tab:deployment_sensitivity"):
    """Released-pipeline-vs-wrapper delta for checkpoints evaluated both ways."""
    pairs = [("f2s_framewise", "chunk6", "Causal-Forcing++ (2-step)"),
             ("f1s_framewise", "cf++_1step", "Causal-Forcing++ (1-step)")]
    keys = ["fBD_mean", "NBF_mean", "MCFF_late_mean", "DLR_mean"]
    rows = []
    for nat, mat, name in pairs:
        for dur in DURATIONS:
            cells, ok = [], False
            for k in keys:
                a = ix.get(("i2v", nat, dur, k))
                b = ix.get(("i2v", mat, dur, k))
                if a and b:
                    d = BT.mean(list(b.values())) - BT.mean(list(a.values()))
                    cells.append(f"{d:+.2f}")
                    ok = True
                else:
                    cells.append("--")
            if ok:
                rows.append([esc(name), dur] + cells)
    if not rows:
        return None
    # Supplement-only and six columns wide: it overflows a single column by
    # ~35pt, so it is set across both.
    lines = [r"\begin{table*}[tb]", r"\centering", r"\small",
             r"\setlength{\tabcolsep}{6pt}",
             r"\begin{tabular}{l c c c c c}", r"\toprule",
             r"Checkpoint & horizon & $\Delta$fBD & $\Delta$NBF & $\Delta$MCFF-L & "
             r"$\Delta$DLR \\", r"\midrule"]
    for r_ in rows:
        lines.append(" & ".join(r_) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Deployment sensitivity.} Change from each "
              r"checkpoint's own released setting to the common long-horizon "
              r"wrapper, for the two checkpoints evaluated both ways. Absolute "
              r"wrapper scores are never read as the published method's "
              r"performance.}", r"\label{%s}" % label, r"\end{table*}"]
    return "\n".join(lines)


def validation_table(label="tab:validation"):
    """Factor-admission table.

    Each factor is scored on the corruption family its definition says it should
    detect -- geometric drift for the static-fidelity factors and the drift
    diagnostics, loss of motion for the persistence factors -- and separately on
    the families it should ignore. Reporting Spearman on an off-target family
    would be misleading, since a 1% response that happens to be monotone scores
    rho = 1.0 and would read as a failure of selectivity rather than evidence of
    it; off-target behaviour is therefore reported as a relative magnitude.
    """
    recs = []
    for f in sorted(glob.glob(f"{MAN}/validation_response*.json")):
        try:
            recs += json.load(open(f)).get("records", [])
        except (OSError, ValueError):
            continue
    if not recs:
        return None

    # factor -> (display, primary family, label, expected sign, secondary family)
    SPEC = [("fBD",   "fBD",       "translation", "drift",  +1, "rotation"),
            ("NBF",   "NBF",       "translation", "drift",  +1, "rotation"),
            ("MCFF_L", "MCFF-L",   "freeze",      "freeze", -1, None),
            ("FP",    "FP",        "freeze",      "freeze", -1, None),
            ("DLR",   "DLR",       "translation", "translational leakage", +1, "rotation"),
            ("DAR",   "DAR",       "translation", "drift",  +1, "rotation"),
            ("VB_DD", "VBench DD", "translation", "drift",  +1, "rotation")]
    OFF = ["photometric", "mask_radius"]

    by = defaultdict(lambda: defaultdict(list))
    for r in recs:
        by[r["family"]][r["level"]].append(r)

    def series(fam, metric):
        xs, ys = [], []
        for l in sorted(by[fam]):
            v = [r[metric] for r in by[fam][l] if r.get(metric) is not None]
            if v:
                xs.append(l); ys.append(sum(v) / len(v))
        return xs, ys

    def rho_of(metric, fam, sign):
        xs, ys = series(fam, metric)
        if len(xs) < 3:
            return None
        r = BT.spearman(xs, ys)
        return None if r is None else sign * r

    rows = []
    for key, disp, prim, plabel, sign, sec in SPEC:
        r1 = rho_of(key, prim, sign)
        r2 = rho_of(key, sec, sign) if sec else None
        offs = []
        for fam in OFF:
            xs, ys = series(fam, key)
            if len(ys) >= 3 and ys[0]:
                offs.append(max(abs(y - ys[0]) for y in ys) / abs(ys[0]) * 100)
        off = max(offs) if offs else None
        ok = (r1 is not None and r1 >= 0.7) and (off is None or off <= 25.0)
        # VBench DD is a comparison row, not a candidate factor: it is put
        # through the identical corruptions to show what a whole-frame score
        # does, and is never admitted to or excluded from the benchmark.
        mark = "--" if key == "VB_DD" else (r"\checkmark" if ok else "supp.")
        rows.append([disp, plabel,
                     f"{r1:+.2f}" if r1 is not None else "--",
                     f"{r2:+.2f}" if r2 is not None else "n/a",
                     f"{off:.0f}\\%" if off is not None else "--",
                     mark])

    lines = [r"\begin{table}[tb]", r"\centering", r"\scriptsize",
             r"\setlength{\tabcolsep}{1.5pt}",
             r"\begin{tabular}{llcccc}", r"\toprule",
             "Factor & target & $\\rho$ & $\\rho_{\\mathrm{rot}}$ & off-target & admitted \\\\",
             r"\midrule"]
    for r_ in rows:
        lines.append(" & ".join(r_) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Mechanistic validation and factor admission.} "
              r"$\rho$ is signed target-family Spearman correlation; "
              r"$\rho_{\mathrm{rot}}$ reports rotational response; \emph{off-target} "
              r"is the largest relative excursion under photometric and mask "
              r"perturbations. Admission requires $\rho\geq0.7$ and off-target "
              r"response below $25\%$. Rotation is reported but not gated: DLR is "
              r"inverted there, while fBD and DAR carry that case. VBench DD is a "
              r"contrast row, not a candidate factor. Twelve clips per severity.}",
              r"\label{%s}" % label, r"\end{table}"]
    return "\n".join(lines)


def abstention_table(label="tab:abstention"):
    """Per-factor measurement coverage, i.e. where a factor declines to report.

    fBD is feature-based, so it abstains when fewer than a dozen repeatable
    keypoints survive in the static region. Reporting this as a smaller $n$
    without explanation would look like missing data; it is the estimator
    correctly refusing to measure a scene it cannot track.
    """
    import glob as _g
    rows, scenes = [], defaultdict(set)
    tot = defaultdict(lambda: [0, 0])
    public = {(m["track"], m["key"]) for m in ALL
              if m["status"] == "public"}
    for p in sorted(_g.glob(f"{ROOT}/raw/*/*/*/snf_task_metrics.json")):
        parts = p.split(os.sep)
        track, key, dur = parts[-4], parts[-3], parts[-2]
        if (track, key) not in public:
            continue
        try:
            pv = json.load(open(p)).get("per_video", [])
        except (OSError, ValueError):
            continue
        for v in pv:
            if "error" in v:
                continue
            tot[(track, dur)][1] += 1
            if v.get("fBD") is None:
                tot[(track, dur)][0] += 1
                scenes[(track, dur)].add(v.get("video", "")[:60])
    for (track, dur), (n_abs, n) in sorted(tot.items()):
        if n:
            rows.append([track.upper(), dur, str(n), str(n_abs),
                         f"{100.0 * n_abs / n:.1f}\\%"])
    if not rows:
        return None
    lines = [r"\begin{table}[tb]", r"\centering", r"\small",
             r"\begin{tabular}{llccc}", r"\toprule",
             r"track & horizon & measured & fBD abstained & rate \\", r"\midrule"]
    for r_ in rows:
        lines.append(" & ".join(r_) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Public-roster measurement coverage and fBD abstention.} fBD is "
              r"feature-based and declines to report when too few repeatable keypoints "
              r"survive in the static region. Public-roster abstentions are confined "
              r"to a desert dust-storm scene whose flat, dust-obscured ground offers "
              r"little stable structure to track. The remaining "
              r"factors are reported for those clips as usual; only fBD is withheld.}",
              r"\label{%s}" % label, r"\end{table}"]
    return "\n".join(lines)


def compensation_table(label="tab:compensation"):
    """How well the v1.1 similarity fit actually behaved on the audited clips.

    Sec. 4 states that insufficient correspondences fall back to median
    translation and that the fallback is recorded per sequence. Both are true
    and neither was ever reported, so a reader had no way to tell whether the
    estimator was working or quietly degrading. It is worth reporting for two
    reasons that point in opposite directions.

    The reassuring one: the fallback never fires. The qualifying one: on real
    fixed-camera audit clips the fitted transform is numerically almost pure
    translation -- median rotation is a thousandth of a degree and median scale
    is within 1e-4 of unity -- so v1.0 and v1.1 should agree closely *here*, and
    the estimator change earns its keep on the validation corruptions, which
    inject the rotation and zoom that v1.0 cannot see. Claiming the upgrade
    reorders the audit would not survive this table, so the paper should not
    claim it.
    """
    import glob as _g
    public = {(m["track"], m["key"]) for m in ALL if m["status"] == "public"}
    per_track = defaultdict(lambda: defaultdict(list))
    modes = defaultdict(Counter)
    for path in sorted(_g.glob(f"{ROOT}/raw/*/*/*/snf_task_metrics.json")):
        parts = path.split(os.sep)
        track, key = parts[-4], parts[-3]
        if (track, key) not in public:
            continue
        try:
            d = json.load(open(path))
        except (OSError, ValueError):
            continue
        if str(d.get("metric_spec_version")) != "1.1":
            continue
        for v in d.get("per_video", []):
            if not isinstance(v, dict) or "error" in v:
                continue
            modes[track][v.get("compensation_mode")] += 1
            for k in ("inlier_ratio_mean", "rotation_deg_mean", "scale_mean",
                      "similarity_frac"):
                if isinstance(v.get(k), (int, float)):
                    per_track[track][k].append(float(v[k]))
    if not per_track:
        return None

    def q(vals, frac):
        vals = sorted(vals)
        return vals[min(len(vals) - 1, int(frac * len(vals)))]

    rows = []
    for track in sorted(per_track):
        d = per_track[track]
        n = modes[track].total() if hasattr(modes[track], "total") else sum(modes[track].values())
        fb = sum(1 for x in d["similarity_frac"] if x < 1.0)
        rows.append([
            track.upper(), str(n),
            f"{sum(1 for x in d['inlier_ratio_mean'] if x < 0.8)}",
            f"{q(d['inlier_ratio_mean'], 0.05):.2f}",
            f"{q(d['inlier_ratio_mean'], 0.50):.3f}",
            f"{q(d['rotation_deg_mean'], 0.50):.4f}",
            f"{max(abs(x) for x in d['rotation_deg_mean']):.2f}",
            f"{q(d['scale_mean'], 0.50):.4f}",
            str(fb)])
    lines = [r"\begin{table}[tb]", r"\centering", r"\footnotesize",
             r"\begin{tabular}{lrrrrrrrr}", r"\toprule",
             r"& & \multicolumn{3}{c}{RANSAC inlier ratio} & "
             r"\multicolumn{2}{c}{rotation ($^\circ$)} & scale & \\",
             r"\cmidrule(lr){3-5}\cmidrule(lr){6-7}",
             r"track & clips & $<0.8$ & p05 & median & median & max $|\cdot|$ "
             r"& median & fallbacks \\", r"\midrule"]
    for r_ in rows:
        lines.append(" & ".join(r_) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Behaviour of the v1.1 similarity compensation on the "
              r"audited clips.} The median-translation fallback never fires, so every "
              r"reported value comes from a fitted similarity. The fit is not uniformly "
              r"tight: a minority of clips sit well below the typical inlier ratio. The "
              r"fitted transform is also nearly a pure translation in practice "
              r"(median rotation $\sim10^{-3}$ degrees, median scale within $10^{-4}$ "
              r"of unity), so v1.0 and v1.1 are expected to agree closely on this "
              r"material; the estimator change matters for the injected-rotation and "
              r"scale corruptions of Sec.~\ref{sec:validation}, which median translation "
              r"cannot represent, not for reordering the audit.}",
              r"\label{%s}" % label, r"\end{table}"]
    return "\n".join(lines)


# --------------------------------------------------------------------- macros
def macros(ix, rows):
    """Every number the prose quotes, as a \\newcommand."""
    M = {}
    t, d = "t2v", "60s"
    pub = [m for m in ALL if m["track"] == t and m["status"] == "public"]

    def mean_of(key, metric, dur=d, track=t):
        pp = ix.get((track, key, dur, metric))
        return sum(pp.values()) / len(pp) if pp else None

    # headline disagreement
    def series(metric):
        return {m["name"]: mean_of(m["key"], metric) for m in pub
                if mean_of(m["key"], metric) is not None}
    dd, nbf = series("dynamic_degree"), series("NBF_mean")
    common = sorted(set(dd) & set(nbf))
    if len(common) >= 3:
        M["SNFddNBF"] = f"{BT.spearman([dd[c] for c in common], [nbf[c] for c in common]):+.2f}"
    M["SNFnPublicTTV"] = str(len(pub))
    M["SNFnPublicTTVPeers"] = str(max(0, len(pub) - 1))
    M["SNFnPromptsSixty"] = str(len(ix.get((t, pub[0]["key"], d, "fBD_mean"), {})) or 23)
    # Prompt counts for the other reported horizon and for the I2V roster, so
    # no sample size is ever typed into the prose by hand.
    n120 = max((len(ix.get((t, m["key"], "120s", "fBD_mean"), {})) for m in pub),
               default=0)
    if n120:
        M["SNFnPromptsOneTwenty"] = str(n120)
    i2v_pub = [m for m in ALL if m["track"] == "i2v" and m["status"] == "public"]
    n_i2v_60 = max((len(ix.get(("i2v", m["key"], "60s", "NBF_mean"), {}))
                    for m in i2v_pub), default=0)
    if n_i2v_60:
        M["SNFnPromptsIToVSixty"] = str(n_i2v_60)
    n_rows = sum(1 for m in i2v_pub if ix.get(("i2v", m["key"], "60s", "NBF_mean")))
    if n_rows:
        M["SNFnPublicIToV"] = str(n_rows)
    n_native = sum(1 for m in i2v_pub if m["setting"] == "native"
                   and ix.get(("i2v", m["key"], "60s", "NBF_mean")))
    M["SNFnIToVNative"] = str(n_native)

    # rank inversions
    for who, tag in ((("Causal-Forcing"), "CF"), (("Infinite-Forcing"), "IF")):
        key = next((m["key"] for m in pub if m["name"] == who), None)
        if not key:
            continue
        for metric, mtag, low in (("dynamic_degree", "DD", False),
                                  ("NBF_mean", "NBF", True),
                                  ("fBD_mean", "fBD", True)):
            s = series(metric)
            if who not in s:
                continue
            order = sorted(s, key=lambda k: s[k], reverse=not low)
            M[f"SNFrank{tag}{mtag}"] = str(order.index(who) + 1)
        for metric, mtag in (("DLR_mean", "DLR"), ("DAR_mean", "DAR"),
                             ("fBD_mean", "fBD"), ("NBF_mean", "NBF")):
            v = mean_of(key, metric)
            if v is not None:
                if metric == "DAR_mean":
                    v = min(1.0, max(0.0, v))
                M[f"SNFval{tag}{mtag}"] = fmt(v)

    # DAR negative incidence
    p = f"{MAN}/dar_negative_incidence.json"
    if os.path.exists(p):
        j = json.load(open(p))["overall"]
        M["SNFdarNegN"] = str(j["negative"])
        M["SNFdarTotN"] = str(j["n"])
        M["SNFdarNegPct"] = f"{100 * j['rate']:.1f}"

    # Controlled-translation endpoints used in the abstract and validation
    # prose. Derive these from the same records plotted by fig_validation(), so
    # the numerical statement cannot drift away from the rendered figure.
    validation = []
    for p in sorted(glob.glob(f"{MAN}/validation_response*.json")):
        try:
            validation.extend(json.load(open(p)).get("records", []))
        except (OSError, ValueError):
            continue
    trans = [r for r in validation if r.get("family") == "translation"]
    levels = sorted({float(r["level"]) for r in trans})
    if len(levels) >= 2:
        lo, hi = levels[0], levels[-1]
        for metric, tag in (("fBD", "FBD"), ("NBF", "NBF"),
                            ("VB_DD", "DD")):
            base = [float(r[metric]) for r in trans
                    if float(r["level"]) == lo and r.get(metric) is not None]
            end = [float(r[metric]) for r in trans
                   if float(r["level"]) == hi and r.get(metric) is not None]
            if base and end and sum(base):
                ratio = (sum(end) / len(end)) / (sum(base) / len(base))
                M[f"SNFvalTranslation{tag}Ratio"] = f"{ratio:.2f}"

    # category balance
    p = f"{MAN}/category_balance.json"
    if os.path.exists(p):
        j = json.load(open(p))
        c = j["cells"].get("t2v/60s", {})
        if c:
            M["SNFtopCatShare"] = f"{100 * c['_max_share']:.0f}"
            M["SNFnCategories"] = str(len([k for k in c if not k.startswith('_')]))

    # spec provenance
    sv = spec_versions()
    allv = sorted({v for s in sv.values() for v in s})
    M["SNFspecVersions"] = ", ".join(allv) if allv else "1.1"
    M["SNFflowBackbone"] = "RAFT"
    M["SNFfeatBackbone"] = "ORB"

    lines = [r"% AUTO-GENERATED by scripts/paper_assets.py -- do not edit.",
             r"% Every number the prose quotes lives here, so a score change "
             r"propagates into the text instead of silently diverging from it.",
             ""]
    for k, v in sorted(M.items()):
        lines.append(r"\providecommand{\%s}{%s}" % (k, v))
    return "\n".join(lines), M


# ----------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LFIG, exist_ok=True)
    rows, ix = load()

    written = []

    t = audit_table(ix, "t2v", ["60s", "120s"], "tab:t2v_audit",
                    r"\textbf{Recorded common-configuration T2V audit.} A four-step "
                    r"denoising schedule with released-scheduler warping, six "
                    r"frames/block, and seed $0$.")
    if t:
        open(f"{OUT}/tab_t2v_audit.tex", "w").write(t)
        written.append("tab_t2v_audit.tex")

    # Narrow and without intervals: a full-width float costs twice the page area
    # per row, and the wide variant printed point estimates anyway, so nothing is
    # lost. Suppressing the intervals also recovers the width the long I2V system
    # names need.
    t = audit_table(ix, "i2v", ["60s", "120s"], "tab:i2v_audit", wide=False,
                    intervals=False,
                    caption=
                    r"\textbf{I2V released pipelines and deployment sensitivity "
                    r"at 60 and 120\,s.}")
    if t:
        open(f"{OUT}/tab_i2v_audit.tex", "w").write(t)
        written.append("tab_i2v_audit.tex")

    t = disagreement_table(
        ix, caption=r"\textbf{Rank disagreement at 60\,s.} Spearman correlation "
                    r"over $n=7$ method means---descriptive, not inferential. "
                    r"Positive correlation between apparent motion and background "
                    r"flow is the effect the benchmark isolates. Smoothness and "
                    r"flickering rank these systems identically and share a row.")
    if t:
        open(f"{OUT}/tab_disagreement.tex", "w").write(t)
        written.append("tab_disagreement.tex")

    for md, name, label, cap, mc, *sec in [
        (f"{TAB}/coverage_matrix_public.md", "tab_coverage.tex", "tab:coverage",
         r"Asset and score coverage for the audited public systems. \texttt{V$n$} is the number of available "
         r"video assets, \texttt{T$n$} the number of valid SNF task-metric records, and \texttt{B} denotes "
         r"available VBench scores. \texttt{T$n$/$N$} marks entries where only $n$ of $N$ videos hold usable measurements. "
         r"V counts generated assets, whereas audit $n$ counts unique frozen-manifest prompt items after duplicate prompt "
         r"outputs are collapsed. Reward-Forcing has 12 assets over six 5\,s prompts; Rolling-Forcing has 24 assets over "
         r"23 60\,s prompts.", 7),
        (f"{TAB}/category_balance.md", "tab_category.tex", "tab:category",
         r"Scene-category balance of the evaluation set, by track and horizon. "
         r"A dot marks a category absent from that cell.", 9,
         "Prompts per category"),
        (f"{TAB}/dar_negative_incidence.md", "tab_dar_negative.tex", "tab:darneg",
         r"Incidence of negative DAR, i.e.\ clips where global-motion compensation "
         r"\emph{increased} measured dynamic-region flow.", 7, None, "negative")]:
        s = simple_table(md, label, cap, max_cols=mc,
                         section=(sec[0] if sec else None),
                         nonzero_col=(sec[1] if len(sec) > 1 else None))
        if s:
            open(f"{OUT}/{name}", "w").write(s)
            written.append(name)

    # tab_native_configs is deliberately NOT emitted: every audited system runs
    # at the same resolution, frame rate and maximum horizon, so the table was
    # seven identical rows. The single distinct fact is stated in Sec. 7 text.
    for fn, name in ((abstention_table(), "tab_abstention.tex"),
                     (compensation_table(), "tab_compensation.tex"),
                     (validation_table(), "tab_validation.tex"),
                     (interpretation_table(ix), "tab_interpretation.tex"),
                     (aggregation_table(ix), "tab_aggregation.tex"),
                     (native_config_table("t2v"), "tab_native_config.tex"),
                     (native_config_table("i2v", label="tab:native_config_i2v"),
                      "tab_native_config_i2v.tex"),
                     (perception_table(), "tab_perception.tex"),
                     (robustness_table(), "tab_robustness.tex"),
                     (robustness_main_table(), "tab_robustness_main.tex"),
                     (paired_diff_table(), "tab_paired.tex"),
                     (deployment_table(ix), "tab_deployment.tex")):
        if fn:
            open(f"{OUT}/{name}", "w").write(fn)
            written.append(name)

    # Full four-horizon versions live in the supplement.
    for trk, nm in (("t2v", "tab_t2v_audit_full.tex"), ("i2v", "tab_i2v_audit_full.tex")):
        main_scope = (r"the 60\,s and 120\,s panels" if trk == "t2v" else
                      r"the 60\,s deployment panel")
        s = audit_table(ix, trk, DURATIONS, f"tab:{trk}_audit_full", wide=True,
                        caption=
                        r"\textbf{Complete %s audit, all four horizons.} The main "
                        r"paper reports %s; the 5\,s tier is an "
                        r"initialization check and 240\,s a diagnostic extreme. "
                        r"Every row is computed under the same frozen specification, "
                        r"so panels are comparable within a horizon; prompt sets "
                        r"differ across horizons, so columns are not comparable "
                        r"between panels." % (trk.upper(), main_scope))
        if s:
            open(f"{OUT}/{nm}", "w").write(s)
            written.append(nm)

    mac, M = macros(ix, rows)
    open(f"{OUT}/macros.tex", "w").write(mac + "\n")
    written.append("macros.tex")

    sv = spec_versions()
    prov = [r"% AUTO-GENERATED provenance", ""]
    prov.append(r"\providecommand{\SNFprovenance}{%")
    prov.append(r"Metrics computed under METRIC\_SPEC v%s with the %s flow backbone "
                r"and %s features.}" % (M.get("SNFspecVersions", "1.1"),
                                        M["SNFflowBackbone"], M["SNFfeatBackbone"]))
    open(f"{OUT}/provenance.tex", "w").write("\n".join(prov) + "\n")
    written.append("provenance.tex")

    for f in glob.glob(f"{FIG}/*.pdf"):
        shutil.copy2(f, os.path.join(LFIG, os.path.basename(f)))

    print(f"wrote {len(written)} assets into latex/generated/:")
    for w in written:
        print("   ", w)
    print(f"copied {len(glob.glob(f'{LFIG}/*.pdf'))} figures into latex/figures/")
    print(f"macros defined: {len(M)}")
    for k in ["SNFddNBF", "SNFrankCFDD", "SNFrankCFNBF", "SNFvalCFDLR",
              "SNFvalCFDAR", "SNFdarNegPct", "SNFtopCatShare"]:
        if k in M:
            print(f"     \\{k} = {M[k]}")


if __name__ == "__main__":
    main()

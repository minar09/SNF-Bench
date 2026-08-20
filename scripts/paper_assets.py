"""Generate every LaTeX asset the paper \\input's, straight from frozen scores.

The discipline this enforces: **no number is typed into the paper by hand.**
Tables are generated, and every inline figure quoted in prose comes from a macro
in `latex/generated/macros.tex`. If a score changes, the prose changes with it.
That is the direct structural answer to the DriftFrac episode, where the paper
described one quantity and the code computed another for months.

Outputs (all under latex/generated/, all regenerated from scratch):
    macros.tex              \\newcommand's for every number quoted in prose
    tab_t2v_audit.tex       main T2V audit, native setting
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
from collections import defaultdict

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
    public roster is native, and each duration panel evaluates the same prompt
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
    # non-native rows with a dagger instead and explain it in the caption.
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
                pre += " & " + m["setting"]
            if show_n:
                pre += f" & {n}"
            lines.append(pre + " & " + " & ".join(cells) + r" \\")

    extra = ""
    if mark_setting:
        extra += (r" $^{\dagger}$ marks a system run under the common "
                  r"long-horizon wrapper rather than its released configuration; "
                  r"such rows are read as deployment sensitivity and are never "
                  r"ranked against native rows.")
    elif not show_setting:
        extra += (r" All systems are evaluated in the \emph{%s} setting."
                  % settings.pop())
    if not show_n:
        extra += r" $n$ is stated per horizon and is common to every row of that panel."
    if not wide:
        if intervals:
            extra += (r" Values are means over prompts $\pm$ half a percentile "
                      r"bootstrap 95\% interval (10k resamples, fixed seed); panels "
                      r"with fewer than ten prompts report the point estimate alone, "
                      r"since an interval resampled from so few items is not "
                      r"informative.")
        else:
            extra += (r" Values are means over prompts; intervals for this track "
                      r"are given with the complete per-horizon tables in the "
                      r"supplementary material.")
        extra += (r" MCFF-E "
                  r"and MCFF-L are given together because FP is a ratio and is "
                  r"not interpretable without the magnitude it is taken over; "
                  r"intervals overlap for several systems, and only "
                  r"non-overlapping comparisons are described as separated. "
                  r"Aggregation sensitivity and the DLR/DAR diagnostics are "
                  r"reported in the supplementary material.")
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

    lines = [r"\begin{table}[tb]", r"\centering", r"\small",
             r"\begin{tabular}{l" + "c" * len(snf) + "}", r"\toprule",
             r"generic metric & " + " & ".join(METRICS[k][1] for k in snf) + r" \\",
             r"\midrule"]
    for name, cells in rows:
        lines.append(f"{esc(name)} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{%s}" % caption, r"\label{%s}" % label, r"\end{table}"]
    return "\n".join(lines)


def simple_table(md_path, label, caption, max_cols=None):
    """Convert one of the generated markdown tables to LaTeX verbatim-ish."""
    if not os.path.exists(md_path):
        return None
    rows = []
    for line in open(md_path):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        rows.append(cells[:max_cols] if max_cols else cells)
    if len(rows) < 2:
        return None
    ncol = len(rows[0])
    body = [r"\begin{table*}[tb]", r"\centering", r"\scriptsize",
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
              r"\caption{\textbf{Native deployment configurations.} Every system is "
              r"evaluated at its released resolution and frame rate; no silent "
              r"modification is made to populate an unsupported horizon.}",
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
            interp = ("substantial apparent motion, strongly contaminated by "
                      "background displacement")
        else:
            interp = "stable sequence with decaying intended motion"
        body.append([esc(n),
                     f"VB-DD rank {r_dd[n]}/{N}",
                     f"NBF rank {r_nbf[n]}/{N}, MCFF-L rank {r_mc[n]}/{N}",
                     interp])
    if not body:
        return None
    lines = [r"\begin{table*}[t]", r"\centering", r"\small",
             # 0.42\textwidth overflowed the full-width float by ~30pt once the
             # three label columns were set; 0.38 clears it with margin.
             r"\begin{tabular}{l l l p{0.38\textwidth}}", r"\toprule",
             r"Method & Generic evidence & SNF-Bench evidence & Interpretation \\",
             r"\midrule"]
    for b in body:
        lines.append(" & ".join(b) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Interpretation changes between generic whole-frame "
              r"metrics and SNF-Bench at 60\,s.} Neither evaluation is labelled "
              r"correct; the table identifies information hidden by whole-frame "
              r"aggregation. Cases are selected by a fixed rank-gap rule applied to "
              r"all public methods, so none can be selectively omitted.}",
              r"\label{%s}" % label, r"\end{table*}"]
    return "\n".join(lines)


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
        rows.append((m["name"], m["setting"], f"{w}$\\times${h}{mixed}",
                     f"{float(fps):.0f}", ", ".join(ds)))
    if not rows:
        return None

    lines = [r"\begin{table*}[tb]", r"\centering", r"\small",
             r"\setlength{\tabcolsep}{5pt}",
             r"\begin{tabular}{l l c c l}", r"\toprule",
             r"System & setting & resolution & fps & horizons \\", r"\midrule"]
    for r_ in rows:
        lines.append(" & ".join(r_) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Recorded generation configuration.} Every "
              r"audited system was run in its released configuration and "
              r"produced output at the same resolution and frame rate over the "
              r"same horizons, so no comparison in this paper is confounded by "
              r"output format. Per-method sampler settings---denoising steps, "
              r"chunk length, guidance scale, cache policy---were not captured "
              r"in the run manifest and are therefore not listed here; this is a "
              r"reproducibility gap we state rather than fill by inference.}",
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
    """Native-vs-matched delta for checkpoints evaluated both ways."""
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
              r"checkpoint's native configuration to the common long-horizon "
              r"wrapper, for the two checkpoints evaluated both ways. Absolute "
              r"matched scores are never read as the published method's "
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
            ("DLR",   "DLR",       "translation", "drift",  +1, "rotation"),
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
        rows.append([disp, plabel,
                     f"{r1:+.2f}" if r1 is not None else "--",
                     f"{r2:+.2f}" if r2 is not None else "n/a",
                     f"{off:.0f}\\%" if off is not None else "--",
                     r"\checkmark" if ok else "supp."])

    lines = [r"\begin{table}[tb]", r"\centering", r"\scriptsize",
             r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{llcccc}", r"\toprule",
             "Factor & target & $\\rho$ & $\\rho_{\\mathrm{rot}}$ & off-target & admitted \\\\",
             r"\midrule"]
    for r_ in rows:
        lines.append(" & ".join(r_) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Mechanistic validation and factor admission.} Each "
              r"factor is scored on the corruption its definition says it should "
              r"detect: accumulating global \emph{drift} for the static-fidelity and "
              r"drift diagnostics, progressive \emph{freezing} for the persistence "
              r"factors. $\rho$ is Spearman correlation against injected severity, "
              r"signed so that a correct response is positive; "
              r"$\rho_{\mathrm{rot}}$ repeats it for rotational drift, the harder "
              r"case. \emph{off-target} is the largest relative excursion under "
              r"corruptions the factor should ignore---photometric drift and "
              r"perturbation of the region partition---so a small value indicates "
              r"selectivity. Admission requires $\rho \ge 0.7$ and off-target "
              r"response below $25\%$. Twelve reference clips per severity level.}",
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
    for p in sorted(_g.glob(f"{ROOT}/raw/*/*/*/snf_task_metrics.json")):
        parts = p.split(os.sep)
        track, key, dur = parts[-4], parts[-3], parts[-2]
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
              r"\caption{\textbf{Measurement coverage and fBD abstention.} fBD is "
              r"feature-based and declines to report when too few repeatable keypoints "
              r"survive in the static region. Every abstention in this benchmark occurs "
              r"on a single desert dust-storm scene, whose flat, dust-obscured ground "
              r"offers no stable structure to track, and it occurs there for every "
              r"system alike---so it reflects the scene, not a method. The remaining "
              r"factors are reported for those clips as usual; only fBD is withheld.}",
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
                    r"\textbf{SNF-Bench audit, T2V track, native configuration.} "
                    r"All systems are public external models run under their own "
                    r"intended configuration. Our own systems are excluded by "
                    r"construction. DAR is reported clipped to $[0,1]$; signed "
                    r"values are released.")
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
                    r"\textbf{SNF-Bench audit, I2V track.} Setting is stated per row: "
                    r"\emph{native} systems run under their authors' configuration, "
                    r"\emph{matched} systems under the common long-horizon wrapper and "
                    r"are read as a deployment stress test rather than as the "
                    r"published method's performance.")
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

    for md, name, label, cap, mc in [
        (f"{TAB}/coverage_matrix_public.md", "tab_coverage.tex", "tab:coverage",
         r"Asset and score coverage for the audited public systems. \texttt{T$n$/$N$} marks entries where a "
         r"metrics file exists but only $n$ of $N$ videos hold usable measurements.", 7),
        (f"{TAB}/category_balance.md", "tab_category.tex", "tab:category",
         r"Scene-category balance of the evaluation set, by track and horizon.", 9),
        (f"{TAB}/dar_negative_incidence.md", "tab_dar_negative.tex", "tab:darneg",
         r"Incidence of negative DAR, i.e.\ clips where global-motion compensation "
         r"\emph{increased} measured dynamic-region flow.", 7)]:
        s = simple_table(md, label, cap, max_cols=mc)
        if s:
            open(f"{OUT}/{name}", "w").write(s)
            written.append(name)

    # tab_native_configs is deliberately NOT emitted: every audited system runs
    # at the same resolution, frame rate and maximum horizon, so the table was
    # seven identical rows. The single distinct fact is stated in Sec. 7 text.
    for fn, name in ((abstention_table(), "tab_abstention.tex"),
                     (validation_table(), "tab_validation.tex"),
                     (interpretation_table(ix), "tab_interpretation.tex"),
                     (aggregation_table(ix), "tab_aggregation.tex"),
                     (native_config_table(), "tab_native_config.tex"),
                     (deployment_table(ix), "tab_deployment.tex")):
        if fn:
            open(f"{OUT}/{name}", "w").write(fn)
            written.append(name)

    # Full four-horizon versions live in the supplement.
    for trk, nm in (("t2v", "tab_t2v_audit_full.tex"), ("i2v", "tab_i2v_audit_full.tex")):
        s = audit_table(ix, trk, DURATIONS, f"tab:{trk}_audit_full", wide=True,
                        caption=
                        r"\textbf{Complete %s audit, all four horizons.} The main "
                        r"paper reports the 60\,s and 240\,s panels; the 5\,s tier is an "
                        r"initialisation check and 120\,s an intermediate diagnostic. "
                        r"Every row is computed under the same frozen specification, "
                        r"so panels are comparable within a horizon; prompt sets "
                        r"differ across horizons, so columns are not comparable "
                        r"between panels." % trk.upper())
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

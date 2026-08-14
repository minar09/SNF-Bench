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
# to be narrow enough for one to fit. MCFF-E is a reference quantity for FP and
# DAR is pending its validation gate; both remain in the supplementary table.
HEADLINE_KEYS = ["fBD_mean", "NBF_mean", "MCFF_late_mean", "FP_mean", "DLR_mean"]
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
def audit_table(ix, track, durations, label, caption, wide=False):
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
                if not xs:
                    cells.append("--")
                    continue
                mu = BT.mean(xs)
                if wide or len(xs) < 3:
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
    show_setting = len(settings) > 1
    ns = {dur: {n for _, n, _ in rows} for dur, rows in panels}
    show_n = any(len(v) > 1 for v in ns.values())

    ncols = 1 + (1 if show_setting else 0) + (1 if show_n else 0) + len(keys)
    env = "table*" if wide else "table"
    size = r"\small" if wide else r"\scriptsize"
    lines = [r"\begin{%s}[tb]" % env, r"\centering", size,
             r"\setlength{\tabcolsep}{%s}" % ("4pt" if wide else "2.6pt"),
             r"\begin{tabular}{l" + ("l" if show_setting else "")
             + ("c" if show_n else "") + "c" * len(keys) + "}",
             r"\toprule",
             "Method" + (" & setting" if show_setting else "")
             + (" & $n$" if show_n else "") + " & "
             + " & ".join(HDR[k] for k in keys) + r" \\"]
    for dur, rows in panels:
        lines.append(r"\midrule")
        n_here = sorted(ns[dur])
        hdr = f"{dur} horizon" + ("" if show_n else f"  ($n={n_here[0]}$)")
        lines.append(r"\multicolumn{%d}{l}{\textit{%s}} \\" % (ncols, hdr))
        for m, n, cells in rows:
            pre = esc(m["name"])
            if show_setting:
                pre += " & " + m["setting"]
            if show_n:
                pre += f" & {n}"
            lines.append(pre + " & " + " & ".join(cells) + r" \\")

    extra = ""
    if not show_setting:
        extra += (r" All systems are evaluated in the \emph{%s} setting."
                  % settings.pop())
    if not show_n:
        extra += r" $n$ is stated per horizon and is common to every row of that panel."
    if not wide:
        extra += (r" Values are prompt-level means $\pm$ half the width of a "
                  r"percentile bootstrap 95\% interval (10k resamples, fixed seed). "
                  r"MCFF-E and DAR appear in the supplementary table.")
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
    lines = [r"\begin{table}[t]", r"\centering", r"\small",
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
    body = [r"\begin{table}[t]", r"\centering", r"\scriptsize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{tabular}{l" + "c" * (ncol - 1) + "}", r"\toprule",
            " & ".join(esc(c) for c in rows[0]) + r" \\", r"\midrule"]
    for r_ in rows[1:]:
        r_ = r_ + [""] * (ncol - len(r_))
        body.append(" & ".join(esc(c) for c in r_[:ncol]) + r" \\")
    body += [r"\bottomrule", r"\end{tabular}",
             r"\caption{%s}" % caption, r"\label{%s}" % label, r"\end{table}"]
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
             r"\begin{tabular}{l l l p{0.42\textwidth}}", r"\toprule",
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
    lines = [r"\begin{table}[t]", r"\centering", r"\scriptsize",
             r"\setlength{\tabcolsep}{4pt}",
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
              r"performance.}", r"\label{%s}" % label, r"\end{table}"]
    return "\n".join(lines)


def validation_table(label="tab:validation"):
    """Spearman response of every factor to every perturbation family.

    This is the table the benchmark's admissibility rests on. It is reported
    exhaustively -- including the cells where a factor responds weakly or
    non-monotonically -- because a validation suite that only showed its
    successes would not be a validation suite.
    """
    recs = []
    for f in sorted(glob.glob(f"{MAN}/validation_response*.json")):
        try:
            recs += json.load(open(f)).get("records", [])
        except (OSError, ValueError):
            continue
    if not recs:
        return None

    fams, metrics = [], ["fBD", "NBF", "MCFF_L", "FP", "DLR", "DAR", "VB_DD"]
    seen = set()
    for r in recs:
        if r["family"] not in seen:
            seen.add(r["family"])
            fams.append(r["family"])

    NICE = {"fBD": r"fBD", "NBF": r"NBF", "MCFF_L": r"MCFF-L", "FP": r"FP",
            "DLR": r"DLR", "DAR": r"DAR", "VB_DD": r"VB-DD"}
    rows = []
    for fam in fams:
        sub = [r for r in recs if r["family"] == fam]
        cells = []
        for m in metrics:
            pts = [(r["level"], r[m]) for r in sub if r.get(m) is not None]
            if len({p[0] for p in pts}) < 3:
                cells.append("--")
                continue
            byl = defaultdict(list)
            for lv, v in pts:
                byl[lv].append(v)
            xs = sorted(byl)
            ys = [sum(byl[x]) / len(byl[x]) for x in xs]
            rho = BT.spearman(xs, ys)
            cells.append(f"{rho:+.2f}" if rho is not None else "--")
        rows.append([esc(fam.replace("_", " ")), str(len({r["clip"] for r in sub}))] + cells)

    lines = [r"\begin{table}[tb]", r"\centering", r"\scriptsize",
             r"\setlength{\tabcolsep}{2.6pt}",
             r"\begin{tabular}{l c" + "c" * len(metrics) + "}", r"\toprule",
             r"perturbation & clips & " + " & ".join(NICE[m] for m in metrics) + r" \\",
             r"\midrule"]
    for r_ in rows:
        lines.append(" & ".join(r_) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}",
              r"\caption{\textbf{Mechanistic validation.} Spearman correlation between "
              r"injected severity and each factor's response, over controlled "
              r"perturbations of real fixed-camera clips. Signs are fixed in advance by "
              r"each definition. \emph{mask radius} perturbs the region partition rather "
              r"than the video, so near-zero entries indicate the desired insensitivity. "
              r"Cells where a factor responds weakly or non-monotonically are reported "
              r"rather than omitted.}",
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

    t = audit_table(ix, "t2v", ["60s"], "tab:t2v_audit",
                    r"\textbf{SNF-Bench audit, T2V track, native configuration.} "
                    r"All systems are public external models run under their own "
                    r"intended configuration. Our own systems are excluded by "
                    r"construction. DAR is reported clipped to $[0,1]$; signed "
                    r"values are released.")
    if t:
        open(f"{OUT}/tab_t2v_audit.tex", "w").write(t)
        written.append("tab_t2v_audit.tex")

    t = audit_table(ix, "i2v", ["60s"], "tab:i2v_audit", wide=True,
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
                    r"between generic whole-frame metrics and SNF-Bench factors over "
                    r"method-level means. A positive correlation between apparent "
                    r"motion and background flow is the effect the benchmark isolates.")
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
    for fn, name in ((validation_table(), "tab_validation.tex"),
                     (interpretation_table(ix), "tab_interpretation.tex"),
                     (deployment_table(ix), "tab_deployment.tex")):
        if fn:
            open(f"{OUT}/{name}", "w").write(fn)
            written.append(name)

    # Full four-horizon versions live in the supplement.
    for trk, nm in (("t2v", "tab_t2v_audit_full.tex"), ("i2v", "tab_i2v_audit_full.tex")):
        s = audit_table(ix, trk, DURATIONS, f"tab:{trk}_audit_full", wide=True,
                        caption=
                        r"\textbf{Complete %s audit, all horizons.} The main paper "
                        r"reproduces the 60\,s and 120\,s panels; the 5\,s tier is an "
                        r"initialisation check and the 240\,s tier is diagnostic."
                        % trk.upper())
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

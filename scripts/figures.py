"""SNF-Bench paper figures that are buildable from the CURRENT data.

Scope note, deliberately narrow: this builds only the figures whose inputs
already exist. The validation figure (Fig. 3) and the teaser's metric bars
(Fig. 1) depend on the affine drift compensation and the perturbation sweep,
neither of which has run yet -- see docs/FIGURE_TABLE_PLAN.md for their specs
and gate dates. Building them against translation-only compensation would bake
in numbers that the Aug-18 suite is expected to change.

Colour policy comes from scripts/palette.py and is not a matter of taste: under
an all-pairs pairlist only three categorical hues clear the CVD separation
floors, and every figure here has 7-9 methods. So **method identity is carried
by direct text labels, never by hue**. Hue carries magnitude (single-hue
sequential ramp) or marks at most two highlighted methods against muted grey.

Run with the snfeval env:
    ~/miniconda3/envs/snfeval/bin/python scripts/figures.py
"""

import csv
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib.lines import Line2D                  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette as P                                  # noqa: E402
from registry import METRICS, contestants            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN, FIG = f"{ROOT}/manifest", f"{ROOT}/figures"
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update(P.mpl_rc())

# Single-column and double-column widths for a CVF two-column paper, in inches.
COL, DCOL = 3.35, 7.0

# Marker shapes are the print/grayscale channel: never rely on hue alone.
MARKER_SEQ = ['o', 's', '^', 'D', 'v']

# Printed labels. Internal record keys (MCFF_L, VB_DD, river_stream, ...) must
# never reach a plate; every figure maps through here first.
PRETTY = {
    "fBD": "fBD", "NBF": "NBF", "MCFF_E": "MCFF-E", "MCFF_L": "MCFF-L",
    "FP": "FP", "DLR": "DLR", "DAR": "DAR", "VB_DD": "VBench DD",
}
PRETTY_CAT = {
    "river_stream": "River / stream", "ocean_waves": "Ocean waves",
    "precipitation": "Precipitation", "fire_smoke": "Fire / smoke",
    "lava_volcanic": "Lava / volcanic", "windborne": "Wind-borne",
}

# ---------------------------------------------------------------------------
# PRE-FREEZE GUARD
# ---------------------------------------------------------------------------
# Every figure rendered before the Aug-20 metric freeze is a DIAGNOSTIC, not a
# result. Global-motion compensation (METRIC_SPEC v1.1 sec.3) is still
# translation-only and the T2V masks are still pre-overlay, so MCFF, FP and DAR
# will all move when those land. Stamping is automatic rather than a convention
# so a stale PDF cannot quietly reach the paper: set the flag below to False
# only once the frozen metric package has been rerun end to end.
PRE_FREEZE = False
# Provenance footers are for internal review; a finished plate carries none.
SHOW_PROVENANCE = False
STAMP = "PRE-FREEZE DIAGNOSTIC — DO NOT USE IN PAPER"


def stamp(fig, provenance, prefreeze=True):
    """Watermark + provenance line. `provenance` names exactly which metrics and
    which spec version produced the numbers, so a figure can never be accused of
    surviving from a superseded table.

    `prefreeze=False` is for figures with NO measured-data dependency (protocol
    schematics): nothing in them can move when the metrics are refrozen, so
    watermarking them would train the eye to ignore the watermark.
    """
    if PRE_FREEZE and prefreeze:
        fig.text(0.5, 0.5, STAMP, ha="center", va="center", rotation=24,
                 fontsize=13, color=P.SERIES_2, alpha=0.16, zorder=100,
                 fontweight="bold")
    # Provenance is recorded in the manifest and the supplementary material, not
    # stamped on the plate: on a finished figure it reads as internal tooling.
    if SHOW_PROVENANCE:
        fig.text(0.005, 0.006, provenance, ha="left", va="bottom",
                 fontsize=4.6, color=P.MUTED, zorder=100, wrap=True)


def save(fig, out, provenance, prefreeze=True):
    stamp(fig, provenance, prefreeze)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG}/{out}.{ext}")
    plt.close(fig)
    return f"{out}.pdf"


# --------------------------------------------------------------------------
def load_scores():
    """-> {(track, model, duration, metric): {prompt_id: mean value}}"""
    acc = defaultdict(lambda: defaultdict(list))
    for r in csv.DictReader(open(f"{MAN}/per_video_scores.csv")):
        acc[(r["track"], r["model"], r["duration"], r["metric"])][r["prompt_id"]].append(
            float(r["value"]))
    return {k: {p: sum(v) / len(v) for p, v in d.items()} for k, d in acc.items()}


def method_means(scores, track, dur, metric, public_only=True, allow_agg=False):
    """-> [(display_name, mean, n)] for eligible contestants, dropping empties.

    `allow_agg` permits falling back to the method-level VBench aggregate when
    no per-video file exists. That is sound for a RANK figure, which needs only
    method-level ordering, and unsound for anything needing a CI -- so the
    fallback is opt-in per call site rather than automatic, and the caller
    reports which durations used it.
    """
    out = []
    for m in contestants(track) if public_only else []:
        pp = scores.get((track, m["key"], dur, metric))
        if pp:
            out.append((m["name"], sum(pp.values()) / len(pp), len(pp)))
        elif allow_agg:
            v = _agg_vbench(track, m["key"], dur, metric)
            if v is not None:
                out.append((m["name"], v, 0))       # n=0 marks "aggregate only"
    return out


def _agg_vbench(track, key, dur, metric):
    p = f"{ROOT}/raw/{track}/{key}/{dur}/vbench.json"
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p)).get(metric)
    except (OSError, ValueError):
        return None


def ranks(pairs, lower_is_better):
    """-> {name: rank}, 1 = best (or 1 = most, for context metrics)."""
    ordered = sorted(pairs, key=lambda kv: kv[1], reverse=not lower_is_better)
    return {n: i + 1 for i, (n, _) in enumerate(ordered)}


def _seq_color(t):
    """t in [0,1] -> a step of the single-hue sequential ramp."""
    i = min(len(P.SEQ) - 1, max(0, int(round(t * (len(P.SEQ) - 1)))))
    return P.SEQ[i]


# Candidate label placements, in points, tried in order of preference.
_OFFSETS = [(0, 9), (0, -15), (11, -3), (-11, -3), (11, 6), (-11, 6)]


def _place_labels(ax, points, fontsize=6.4, char_w=3.5, line_h=8.0):
    """Direct-label every point, greedily choosing an offset that collides with
    neither another point nor an already-placed label.

    Identity is carried by these labels (hue is spent on magnitude), so a
    collision here is not cosmetic -- it destroys the figure's only identity
    channel. Boxes are approximated in display space, which is enough to
    separate 7-9 labels.
    """
    ax.figure.canvas.draw()
    disp = {n: ax.transData.transform(xy) for n, xy in points.items()}
    placed = []                      # (x0, y0, x1, y1) in display coords
    dpi_scale = ax.figure.dpi / 72.0

    def overlaps(box, other):
        return not (box[2] < other[0] or box[0] > other[2]
                    or box[3] < other[1] or box[1] > other[3])

    # Points themselves are obstacles: keep labels off the markers.
    marker_boxes = [(x - 7, y - 7, x + 7, y + 7) for x, y in disp.values()]

    for n in sorted(points, key=lambda k: -disp[k][1]):
        px, py = disp[n]
        w = len(n) * char_w * dpi_scale
        h = line_h * dpi_scale
        chosen = _OFFSETS[0]
        for dx, dy in _OFFSETS:
            cx, cy = px + dx * dpi_scale, py + dy * dpi_scale
            # offsets are relative to the anchor; centre the box on the text
            x0 = cx - w / 2 if dx == 0 else (cx if dx > 0 else cx - w)
            y0 = cy - h / 2
            box = (x0, y0, x0 + w, y0 + h)
            if any(overlaps(box, b) for b in placed + marker_boxes):
                continue
            chosen = (dx, dy)
            placed.append(box)
            break
        else:
            cx, cy = px + chosen[0] * dpi_scale, py + chosen[1] * dpi_scale
            placed.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
        dx, dy = chosen
        ax.annotate(n, points[n], textcoords="offset points", xytext=(dx, dy),
                    ha="center" if dx == 0 else ("left" if dx > 0 else "right"),
                    va="center", fontsize=fontsize, color=P.INK_SECONDARY, zorder=5)


# --------------------------------------------------------------------------
# Fig. 4 -- the interpretation plot ("the scientific result")
# --------------------------------------------------------------------------
def fig_operating_regime(scores, track="t2v", dur="60s", out="fig4_operating_regime"):
    """x = static drift (fBD), y = surviving late dynamic-region motion (MCFF),
    colour = DAR. The point: a method can sit high on y only because its whole
    frame is sliding, and DAR is what tells those two apart."""
    fbd = {n: v for n, v, _ in method_means(scores, track, dur, "fBD_mean")}
    mcff = {n: v for n, v, _ in method_means(scores, track, dur, "MCFF_late_mean")}
    dar = {n: v for n, v, _ in method_means(scores, track, dur, "DAR_mean")}
    names = [n for n in fbd if n in mcff and n in dar]
    if not names:
        return None

    lo, hi = min(dar[n] for n in names), max(dar[n] for n in names)
    span = (hi - lo) or 1.0

    fig, ax = plt.subplots(figsize=(COL, COL * 0.70))
    for n in names:
        c = _seq_color((dar[n] - lo) / span)
        ax.scatter(fbd[n], mcff[n], s=95, color=c, zorder=3,
                   edgecolors=P.SURFACE, linewidths=1.6)   # 2px surface ring
    _place_labels(ax, {n: (fbd[n], mcff[n]) for n in names})

    ax.set_xlabel(f"static-region drift  fBD $\\downarrow$   ({METRICS['fBD_mean'][2].split(',')[1].strip()})")
    ax.set_ylabel("surviving late flow  MCFF")
    ax.grid(axis="both", alpha=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.margins(x=0.16, y=0.20)

    # Legend encodes the colour ramp's meaning, since hue is magnitude here.
    handles = [Line2D([], [], marker="o", linestyle="", markersize=6,
                      markerfacecolor=_seq_color(t), markeredgecolor=P.SURFACE,
                      label=lab)
               for t, lab in [(0.0, f"DAR {lo:.2f} (least drift-attributable)"),
                              (1.0, f"DAR {hi:.2f} (most)")]]
    ax.legend(handles=handles, loc="upper left", fontsize=6.2,
              handletextpad=0.4, borderpad=0.2)
    fig.tight_layout(pad=0.3, rect=(0, 0.055, 1, 1))
    return save(fig, out,
                f"{track.upper()} @{dur} public systems. x=fBD, y=MCFF-L, colour=DAR "
                f"(clipped for display; stored signed). METRIC_SPEC v1.1, robust "
                f"similarity compensation.")


# --------------------------------------------------------------------------
# Fig. 5 -- rank disagreement slopegraph
# --------------------------------------------------------------------------
def fig_rank_disagreement(scores, track="t2v",
                          durations=("5s", "60s", "120s", "240s"),
                          left="dynamic_degree", right="NBF_mean",
                          highlight=("Causal-Forcing", "Infinite-Forcing"),
                          out="fig5_rank_disagreement"):
    """Rank under VBench Dynamic Degree -> rank under SNF-Bench NBF, per horizon.

    Every endpoint is named. The figure's whole content is *which method* sits
    where, so dropping the names to save space would leave a picture of seven
    anonymous lines crossing -- visually tidy and scientifically empty. A 2x2
    grid buys the horizontal room the names need; the two highlighted methods
    additionally carry hue, and everything else is muted grey context.

    Both metrics are compensation-independent, so the figure is unaffected by
    the global-motion estimator and reads as a property of the two metrics.
    """
    panels = []
    for d in durations:
        lp = method_means(scores, track, d, left, allow_agg=True)
        rp = method_means(scores, track, d, right)
        common = {n for n, _, _ in lp} & {n for n, _, _ in rp}
        if len(common) < 3:
            continue
        n_prompt = max([c for nm, _, c in rp if nm in common] or [0])
        agg = any(c == 0 for nm, _, c in lp if nm in common)
        panels.append((d,
                       ranks([(n, v) for n, v, _ in lp if n in common], False),
                       ranks([(n, v) for n, v, _ in rp if n in common], True),
                       sorted(common), n_prompt, agg))
    if not panels:
        return None

    # Single page column, panels stacked vertically. A 2x2 grid at this width
    # would give each panel ~1.6in, which is not enough for method names at
    # either end -- and the names are the figure's content, so the layout bends
    # to them rather than the other way round.
    ncol, nrow = 1, len(panels)
    fig, axes = plt.subplots(nrow, ncol, figsize=(COL, 1.28 * nrow))
    axes = np.atleast_1d(axes).ravel()
    N = max(len(c) for _, _, _, c, _, _ in panels)

    for ax, (d, lr, rr, common, n_prompt, agg) in zip(axes, panels):
        for n in common:
            hl = n in highlight
            color = (P.SERIES_1 if n == highlight[0]
                     else P.SERIES_2 if n == highlight[1] else P.MUTED)
            ax.plot([0, 1], [lr[n], rr[n]], color=color, lw=1.8 if hl else 1.0,
                    alpha=1.0 if hl else 0.5, zorder=3 if hl else 2,
                    solid_capstyle="round")
            ax.scatter([0, 1], [lr[n], rr[n]], s=18 if hl else 9, color=color,
                       zorder=4 if hl else 2, edgecolors=P.SURFACE, linewidths=0.9)
            ax.annotate(n, (0, lr[n]), textcoords="offset points", xytext=(-5, 0),
                        ha="right", va="center", fontsize=5.6,
                        color=P.INK if hl else P.INK_SECONDARY,
                        fontweight="bold" if hl else "normal", zorder=5)
            ax.annotate(n, (1, rr[n]), textcoords="offset points", xytext=(5, 0),
                        ha="left", va="center", fontsize=5.6,
                        color=P.INK if hl else P.INK_SECONDARY,
                        fontweight="bold" if hl else "normal", zorder=5)
        # Just enough margin for the longest method name at either end; the
        # slope region keeps the remainder so the crossing stays legible.
        ax.set_xlim(-1.18, 2.18)
        ax.set_ylim(N + 0.6, 0.4)
        ax.set_xticks([])
        ax.set_yticks(range(1, N + 1))
        ax.tick_params(labelsize=6)
        for s in ("top", "right", "bottom"):
            ax.spines[s].set_visible(False)
        ax.grid(axis="y", alpha=0.45)
        ax.set_axisbelow(True)
        tr = ax.get_xaxis_transform()
        ax.text(0, 1.015, "VBench DD", ha="center", va="bottom", fontsize=5.8,
                color=P.INK_SECONDARY, transform=tr)
        ax.text(1, 1.015, "SNF-Bench NBF", ha="center", va="bottom", fontsize=5.8,
                color=P.INK_SECONDARY, transform=tr)
        ax.set_title(f"{d}   (n={n_prompt}{'*' if agg else ''})",
                     fontsize=7.0, color=P.INK, fontweight="bold", pad=11)
        ax.set_ylabel("rank", fontsize=6.0)

    for ax in axes[len(panels):]:
        ax.axis("off")
    # The footer is a fixed physical height, so it eats a larger fraction of a
    # short figure; scale the reserved band by panel count instead of fixing it.
    fig.tight_layout(pad=0.3, h_pad=1.1, rect=(0, 0.13 / nrow, 1, 1))
    star = ("  *DD from the method-level VBench aggregate (no per-video file at "
            "that horizon); sound for ranks, not used for CIs."
            if any(a for *_, a in panels) else "")
    return save(fig, out,
                f"{track.upper()} public systems. Left 1 = most apparent motion; "
                f"right 1 = least static drift. METRIC_SPEC v1.1.{star}")


# --------------------------------------------------------------------------
# Fig. S -- category balance (supplementary)
# --------------------------------------------------------------------------
def fig_category_balance(out="figS_category_balance"):
    """Horizontal stacked bars, one row per (track, duration). Uses the
    sequential ramp as an ordinal scale -- the categories are unordered, but
    they are a fixed named set shown with direct counts, so magnitude-ramp
    steps are legible and the count labels carry identity."""
    import categories as C
    rows = list(csv.DictReader(open(f"{MAN}/prompt_categories.csv")))
    cells = defaultdict(lambda: defaultdict(int))
    for r in rows:
        cells[(r["track"], r["duration"])][r["category"]] += 1
    order = [(t, d) for t in ("t2v", "i2v") for d in C.DURATIONS if (t, d) in cells]
    if not order:
        return None
    # Categories are unordered identity, so this is the CATEGORICAL palette, not
    # the sequential ramp -- a ramp made precipitation and fire_smoke
    # indistinguishable. Stacked segments touch, so the adjacent pairlist
    # applies and all six slots clear it (validated in palette.py).
    steps = P.CATEGORICAL[:len(C.CAT_ORDER)]
    inks = P.CATEGORICAL_ON[:len(C.CAT_ORDER)]

    fig, ax = plt.subplots(figsize=(DCOL, 0.42 * len(order) + 1.15))
    ypos = range(len(order))
    for y, key in zip(ypos, order):
        x = 0
        for cat, col, ink in zip(C.CAT_ORDER, steps, inks):
            n = cells[key].get(cat, 0)
            if not n:
                continue
            ax.barh(y, n, left=x, height=0.62, color=col,
                    edgecolor=P.SURFACE, linewidth=1.4)      # 2px surface gap
            # Every segment is labelled, including n=1: three of these slots sit
            # under 3:1 on the light surface, so the relief rule makes the count
            # label mandatory rather than decorative.
            ax.text(x + n / 2, y, str(n), ha="center", va="center",
                    fontsize=6.2, color=ink)
            x += n
    ax.set_yticks(list(ypos))
    ax.set_yticklabels([f"{t.upper()} {d}" for t, d in order], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("prompts in the evaluation set")
    ax.grid(axis="x", alpha=0.6)
    ax.set_axisbelow(True)
    handles = [Line2D([], [], marker="s", linestyle="", markersize=6.5,
                      markerfacecolor=c, markeredgecolor=P.SURFACE,
                      label=PRETTY_CAT.get(cat, cat))
               for cat, c in zip(C.CAT_ORDER, steps)]
    ax.legend(handles=handles, ncol=3, loc="lower center",
              bbox_to_anchor=(0.5, 1.01), fontsize=6.5, columnspacing=1.0)
    fig.tight_layout(pad=0.3)
    return save(fig, out,
                "Prompt counts from manifest/prompt_categories.csv. Mask- and "
                "compensation-independent: unaffected by the Aug-16/Aug-14 gates.")


# --------------------------------------------------------------------------
# Fig. 1 teaser -- exemplar SELECTION (frames are assembled by hand afterwards)
# --------------------------------------------------------------------------
def teaser_exemplars(scores, track="t2v", dur="60s", out="fig1_teaser_exemplars.md"):
    """Find the real (prompt, method) clips that instantiate the teaser's
    three cases, so Fig. 1 is built from actual benchmark videos rather than a
    hand-picked illustration:

        A  good flow, stable support   low fBD, high MCFF
        B  whole scene drifting        high fBD, high DD_raw, high DAR
        C  stable support, frozen flow low fBD, low MCFF

    All three should ideally share one prompt so the figure is a controlled
    comparison; we report the best shared-prompt triple we can find.
    """
    per = {}
    for m in contestants(track):
        d = {}
        for k in ("fBD_mean", "MCFF_late_mean", "DD_raw_late_mean", "DAR_mean"):
            s = scores.get((track, m["key"], dur, k))
            if s:
                d[k] = s
        if len(d) == 4:
            per[m["name"]] = d
    if not per:
        return None

    shared = set.intersection(*[set(d["fBD_mean"]) for d in per.values()])
    L = ["# Fig. 1 teaser — candidate exemplar clips", "",
         "Selected from real benchmark videos so the teaser is a controlled comparison,",
         "not an illustration. Each row is one prompt evaluated by three methods:", "",
         "- **A** desired behaviour — low drift, motion survives",
         "- **B** drift masquerading as motion — high drift, high *raw* dynamic degree, high DAR",
         "- **C** frozen — low drift, but motion has collapsed", ""]

    def norm(vals):
        lo, hi = min(vals.values()), max(vals.values())
        return {k: (v - lo) / ((hi - lo) or 1) for k, v in vals.items()}

    scored = []
    for p in shared:
        f = norm({n: per[n]["fBD_mean"][p] for n in per})
        mc = norm({n: per[n]["MCFF_late_mean"][p] for n in per})
        da = norm({n: per[n]["DAR_mean"][p] for n in per})
        A = max(per, key=lambda n: (1 - f[n]) + mc[n])
        B = max(per, key=lambda n: f[n] + da[n])
        C = max(per, key=lambda n: (1 - f[n]) + (1 - mc[n]))
        if len({A, B, C}) < 3:
            continue
        margin = ((1 - f[A]) + mc[A]) + (f[B] + da[B]) + ((1 - f[C]) + (1 - mc[C]))
        scored.append((margin, p, A, B, C))
    scored.sort(reverse=True)

    L += ["| rank | prompt (truncated) | A: good | B: drifting | C: frozen |",
          "|---|---|---|---|---|"]
    for i, (_, p, A, B, C) in enumerate(scored[:8]):
        L.append(f"| {i + 1} | `{p[:54]}…` | {A} | {B} | {C} |")
    L += ["", f"Searched {len(shared)} prompts shared by all {len(per)} public methods; "
              f"{len(scored)} yielded three distinct methods.", "",
          "## Metric values for the top candidate", ""]
    if scored:
        _, p, A, B, C = scored[0]
        L += [f"prompt: `{p}`", "",
              "| case | method | fBD ↓ | MCFF | DD_raw | DAR ↓ |", "|---|---|---|---|---|---|"]
        for case, n in (("A good", A), ("B drifting", B), ("C frozen", C)):
            d = per[n]
            L.append(f"| {case} | {n} | {d['fBD_mean'][p]:.2f} | {d['MCFF_late_mean'][p]:.3f} "
                     f"| {d['DD_raw_late_mean'][p]:.2f} | {d['DAR_mean'][p]:.3f} |")
        L += ["", "Video paths: `videos/" + track + "/<model-key>/" + dur + "/`"]
    with open(f"{FIG}/{out}", "w") as f:
        f.write("\n".join(L) + "\n")
    return out


def main():
    ok, rep = P.validate([P.SERIES_1, P.SERIES_2, P.MUTED])
    if not ok:
        print("PALETTE FAILED -- refusing to render", file=sys.stderr)
        for r in rep:
            print("   ", r, file=sys.stderr)
        return 1
    scores = load_scores()
    made = [fig_mask_protocol(),
            fig_validation(),
            fig_radar(scores),
            fig_operating_regime(scores),
            fig_rank_disagreement(scores),
            fig_category_balance(),
            teaser_exemplars(scores)]
    for m in made:
        print("  wrote figures/" + m if m else "  SKIPPED (no data)")
    return 0



# --------------------------------------------------------------------------
# Fig. 2 -- mask protocol and the two settings (schematic; no data dependency)
# --------------------------------------------------------------------------
def fig_mask_protocol(out="fig2_mask_protocol"):
    """How the static/dynamic partition is actually obtained, and what it cannot
    represent.

    Drawn to the implementation, not to an idealised protocol: the mask comes
    from an automatic Otsu threshold on early-window flow, identically for both
    tracks. Panel (b) states the known failure of a two-way partition rather
    than depicting a third label the metrics do not compute.
    """
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

    C_STATIC, C_FLOW, C_OVER = P.MUTED, P.SERIES_1, P.SERIES_2
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(DCOL, 1.95),
                                   gridspec_kw=dict(width_ratios=[1.42, 1.0]))

    def box(ax, x, y, w, h, label, fc="none", ec=P.AXIS, fs=5.9, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                    linewidth=0.9, edgecolor=ec, facecolor=fc, zorder=2))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs,
                color=P.INK, zorder=3, fontweight="bold" if bold else "normal")

    def arrow(ax, p0, p1):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=7,
                                     linewidth=0.9, color=P.AXIS, zorder=2,
                                     shrinkA=1, shrinkB=1))

    # ---- (a) how the partition is derived --------------------------------
    axa.set_xlim(0, 1); axa.set_ylim(0, 1); axa.axis("off")
    axa.text(0.0, 0.93, "(a)  how the partition is derived", fontsize=7.4,
             fontweight="bold", color=P.INK)

    y = 0.60
    box(axa, 0.02, y, 0.20, 0.15, "generated\nsequence", fs=5.8)
    box(axa, 0.26, y, 0.22, 0.15, "EARLY window\nfirst 12% of pairs", fc="#eef4fd",
        ec=C_FLOW, fs=5.5, bold=True)
    box(axa, 0.52, y, 0.20, 0.15, "mean flow\nmagnitude", fs=5.8)
    box(axa, 0.76, y, 0.22, 0.15, "Otsu threshold", fs=5.8)
    for x0, x1 in ((0.22, 0.26), (0.48, 0.52), (0.72, 0.76)):
        arrow(axa, (x0, y + 0.075), (x1, y + 0.075))

    y2 = 0.30
    box(axa, 0.30, y2, 0.19, 0.14, r"$\Omega_{\rm flow}$", fc="#eef4fd", ec=C_FLOW,
        fs=7, bold=True)
    box(axa, 0.53, y2, 0.19, 0.14, r"$\Omega_{\rm static}$", fc="#f2f2ef",
        ec=C_STATIC, fs=7, bold=True)
    arrow(axa, (0.87, y), (0.62, y2 + 0.14))
    arrow(axa, (0.87, y), (0.40, y2 + 0.14))
    axa.text(0.5, 0.215, "erode static + drop 4% border  =  ignored transition band",
             ha="center", va="center", fontsize=5.6, color=P.INK_SECONDARY)
    axa.text(0.5, 0.145,
             "the window precedes drift accumulation, so the partition is not\n"
             "defined by the temporal failure being measured\n"
             "(automatic, not human-verified \u2014 see limitations)",
             ha="center", va="top", fontsize=5.5, color=P.INK_SECONDARY)

    # ---- (b) what a two-way partition cannot represent -------------------
    axb.set_xlim(0, 1); axb.set_ylim(0, 1); axb.axis("off")
    axb.text(0.0, 0.93, "(b)  limitation: layered content", fontsize=7.4,
             fontweight="bold", color=P.INK)

    fx, fy, fw, fh = 0.05, 0.34, 0.60, 0.50
    axb.add_patch(Rectangle((fx, fy), fw, fh, facecolor="#f4f4f1",
                            edgecolor=P.AXIS, linewidth=0.9, zorder=1))
    for bx, bw, bh in ((0.07, 0.13, 0.30), (0.22, 0.10, 0.23), (0.34, 0.15, 0.35)):
        axb.add_patch(Rectangle((fx + bx, fy + 0.09), bw, bh, facecolor=C_STATIC,
                                edgecolor="none", alpha=0.55, zorder=2))
    axb.add_patch(Rectangle((fx, fy), fw, 0.09, facecolor=C_FLOW, edgecolor="none",
                            alpha=0.55, zorder=2))
    for i in range(15):
        x0 = fx + 0.02 + i * 0.038
        axb.plot([x0, x0 - 0.020], [fy + fh - 0.03, fy + 0.10], color=C_OVER,
                 linewidth=1.0, alpha=0.85, zorder=3, solid_capstyle="round")

    for yy, c, lab in ((0.235, C_STATIC, r"$\Omega_{\rm static}$  support"),
                       (0.150, C_FLOW, r"$\Omega_{\rm flow}$  intended motion"),
                       (0.065, C_OVER, "rain: assigned to one region by flow")):
        axb.add_patch(Rectangle((0.05, yy), 0.032, 0.042, facecolor=c,
                                edgecolor=P.SURFACE, linewidth=0.8, alpha=0.75))
        axb.text(0.10, yy + 0.021, lab, va="center", fontsize=5.8, color=P.INK)

    axb.text(0.70, 0.74, "rain crosses static\nsupport, so the same\npixels are BOTH",
             fontsize=5.7, color=P.INK_SECONDARY, va="top")
    axb.text(0.70, 0.47, "a two-way partition\ncannot separate them;\nprecipitation results\ncarry this caveat",
             fontsize=5.7, color=P.INK, va="top", fontweight="bold")

    fig.tight_layout(pad=0.35, rect=(0, 0.045, 1, 1))
    return save(fig, out,
                "Schematic of the implemented procedure; no measured data. Masks are "
                "automatic (Otsu on early-window flow), identical for both tracks.",
                prefreeze=False)


def fig_validation(out="fig3_validation"):
    """Five panels sharing an x-axis of injected corruption severity.

    Panels (a-d) ask whether each SNF factor moves the way its definition says
    it should under a corruption of known kind and magnitude. Panel (e) puts
    VBench Dynamic Degree through the identical corruption: if injected
    background drift *raises* a standard motion score while our static-fidelity
    factors flag it, the benchmark's thesis is visible in one panel, with no
    model comparison and no published method accused of anything -- the
    corruption is synthetic.
    """
    # Validation runs in several passes (families split across GPUs), so merge
    # every response file rather than depending on one.
    recs = []
    for p in sorted(glob.glob(f"{MAN}/validation_response*.json")):
        try:
            recs += json.load(open(p)).get("records", [])
        except (OSError, ValueError):
            continue
    if not recs:
        return None

    by = defaultdict(lambda: defaultdict(list))
    for r in recs:
        by[r["family"]][r["level"]].append(r)

    # (family, metric, label, normalise-to-baseline)
    # Four panels rather than six: the geometric families now share one severity
    # axis so translation and rotation make the same point, and the partition and
    # photometric controls belong with the full response matrix in the supplement.
    PANELS = [("translation", ["fBD", "NBF"], "(a) injected drift"),
              ("rotation",    ["fBD", "NBF"], "(b) injected rotation"),
              ("attenuation", ["MCFF_L", "FP"], "(c) motion attenuation"),
              ("translation", ["VB_DD", "DLR"], "(d) whole-frame score vs SNF-Bench")]
    PANELS = [(f, m, lab) for f, m, lab in PANELS if by.get(f)]
    if not PANELS:
        return None

    fig, axes = plt.subplots(1, len(PANELS), figsize=(DCOL, 1.44))
    if len(PANELS) == 1:
        axes = [axes]
    for ax, (fam, metrics, lab) in zip(axes, PANELS):
        levels = sorted(by[fam])
        for mi, metric in enumerate(metrics):
            ys, es = [], []
            for lv in levels:
                vals = [r[metric] for r in by[fam][lv] if r.get(metric) is not None]
                ys.append(sum(vals) / len(vals) if vals else float("nan"))
            base = ys[0] if ys and ys[0] not in (0, None) else 1.0
            norm = [y / base if base else y for y in ys]
            color = [P.SERIES_1, P.SERIES_2, P.SERIES_3][mi % 3]
            ax.plot(levels, norm, marker=MARKER_SEQ[mi % len(MARKER_SEQ)],
                    color=color, markersize=3.6, lw=1.6,
                    markeredgecolor=P.SURFACE, markeredgewidth=0.7,
                    label=PRETTY.get(metric, metric))
            ax.annotate(PRETTY.get(metric, metric), (levels[-1], norm[-1]),
                        textcoords="offset points",
                        xytext=(3, 0), fontsize=5.8, color=color, va="center")
        ax.axhline(1.0, color=P.AXIS, lw=0.7, ls=(0, (3, 3)), zorder=1)
        ax.set_title(lab, fontsize=6.6, color=P.INK, pad=4)
        ax.tick_params(labelsize=5.6)
        ax.grid(alpha=0.5)
        ax.set_axisbelow(True)
        ax.margins(x=0.22)
    axes[0].set_ylabel("relative to unperturbed", fontsize=6.2)
    for ax in axes:
        ax.set_xlabel("mean induced displacement (px)"
                      if fam in ("translation", "rotation", "scale", "photometric")
                      else "severity", fontsize=6.0, labelpad=1.5)
    # Leave a band at the bottom for the provenance footer; without it the
    # x-labels and the footer print on top of one another.
    fig.tight_layout(pad=0.3, rect=(0, 0.10, 1, 1))
    n_clips = len({r["clip"] for r in recs})
    return save(fig, out,
                f"Controlled perturbations of {n_clips} real fixed-camera clips; "
                f"values relative to the unperturbed clip. Dynamic Degree computed "
                f"to VBench's published rule. METRIC_SPEC v1.1, similarity compensation.")



# --------------------------------------------------------------------------
# Fig. S -- factor profile per track (radar), in the manner of general-purpose
# suites, but on axes that carry direction rather than a single quality score
# --------------------------------------------------------------------------
def fig_radar(scores, out="figS_radar"):
    """One radar per track: each factor rescaled to [0,1] across the audited
    systems, oriented so that outward is always better.

    A radar is the conventional way these suites summarise a profile, and it is
    useful here for the same reason: it shows at a glance that no audited system
    encloses the others. The orientation step matters -- plotting raw values
    would put "most background drift" outward on one axis and "most surviving
    motion" outward on another, and the shape would mean nothing.

    Hue still never carries identity for more than the two highlighted systems;
    the rest are muted, since seven radar polygons in seven hues is exactly the
    all-pairs case the palette cannot serve.
    """
    KEYS = [("fBD_mean", "fBD", True), ("NBF_mean", "NBF", True),
            ("MCFF_late_mean", "MCFF-L", False), ("FP_mean", "FP", False),
            ("DLR_mean", "DLR", True)]
    HIGHLIGHT = {"t2v": ("Causal-Forcing", "Infinite-Forcing"),
                 "i2v": ("Causal-Forcing (framewise)", "Self-Forcing")}
    tracks = []
    for track in ("t2v", "i2v"):
        vals = {}
        for k, lab, lower_better in KEYS:
            mm = method_means(scores, track, "60s", k)
            if len(mm) >= 3:
                vals[lab] = {n: v for n, v, _ in mm}
        if len(vals) == len(KEYS):
            common = set.intersection(*[set(v) for v in vals.values()])
            if len(common) >= 3:
                tracks.append((track, vals, sorted(common)))
    if not tracks:
        return None

    fig, axes = plt.subplots(1, len(tracks), figsize=(DCOL, 2.9),
                             subplot_kw=dict(projection="polar"))
    axes = np.atleast_1d(axes)
    for ax, (track, vals, names) in zip(axes, tracks):
        labs = [lab for _, lab, _ in KEYS]
        ang = np.linspace(0, 2 * np.pi, len(labs), endpoint=False).tolist()
        ang += ang[:1]
        hi = HIGHLIGHT.get(track, ())
        for n in names:
            r = []
            for k, lab, lower_better in KEYS:
                col = [vals[lab][m] for m in names]
                lo, hh = min(col), max(col)
                x = (vals[lab][n] - lo) / ((hh - lo) or 1.0)
                r.append(1.0 - x if lower_better else x)   # outward = better
            r += r[:1]
            is_hi = n in hi
            c = (P.SERIES_1 if n == (hi[0] if hi else None)
                 else P.SERIES_2 if n == (hi[1] if len(hi) > 1 else None)
                 else P.MUTED)
            ax.plot(ang, r, color=c, lw=1.7 if is_hi else 0.9,
                    alpha=1.0 if is_hi else 0.45, zorder=3 if is_hi else 2,
                    label=n if is_hi else None)
            if is_hi:
                ax.fill(ang, r, color=c, alpha=0.10, zorder=1)
        ax.set_xticks(ang[:-1])
        ax.set_xticklabels(labs, fontsize=6.2, color=P.INK)
        ax.set_yticks([0.25, 0.5, 0.75])
        ax.set_yticklabels([], fontsize=5)
        ax.set_ylim(0, 1)
        ax.grid(color=P.GRID, lw=0.6)
        ax.spines["polar"].set_color(P.AXIS)
        ax.set_title(f"{track.upper()} @ 60 s", fontsize=7.6,
                     color=P.INK, fontweight="bold", pad=12)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10),
                  fontsize=5.8, ncol=1, frameon=False)
    fig.tight_layout(pad=0.5, w_pad=2.0)
    return save(fig, out,
                "Each factor rescaled across the audited systems and oriented so "
                "outward is better. Grey polygons are the remaining public systems.",
                prefreeze=False)



if __name__ == "__main__":
    sys.exit(main())

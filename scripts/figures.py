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
import os
import sys
from collections import defaultdict

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

# ---------------------------------------------------------------------------
# PRE-FREEZE GUARD
# ---------------------------------------------------------------------------
# Every figure rendered before the Aug-20 metric freeze is a DIAGNOSTIC, not a
# result. Global-motion compensation (METRIC_SPEC v1.1 sec.3) is still
# translation-only and the T2V masks are still pre-overlay, so MCFF, FP and DAR
# will all move when those land. Stamping is automatic rather than a convention
# so a stale PDF cannot quietly reach the paper: set PRE_FREEZE = False only
# once the frozen metric package has been rerun end to end.
PRE_FREEZE = True
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
    fig.text(0.005, 0.004, provenance, ha="left", va="bottom",
             fontsize=4.6, color=P.MUTED, zorder=100)


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


def method_means(scores, track, dur, metric, public_only=True):
    """-> [(display_name, mean)] for eligible contestants, dropping empties."""
    out = []
    for m in contestants(track) if public_only else []:
        pp = scores.get((track, m["key"], dur, metric))
        if pp:
            out.append((m["name"], sum(pp.values()) / len(pp)))
    return out


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
    fbd = dict(method_means(scores, track, dur, "fBD_mean"))
    mcff = dict(method_means(scores, track, dur, "MCFF_late_mean"))
    dar = dict(method_means(scores, track, dur, "DAR_mean"))
    names = [n for n in fbd if n in mcff and n in dar]
    if not names:
        return None

    lo, hi = min(dar[n] for n in names), max(dar[n] for n in names)
    span = (hi - lo) or 1.0

    fig, ax = plt.subplots(figsize=(COL, COL * 0.86))
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
    fig.tight_layout(pad=0.3)
    return save(fig, out,
                f"{track.upper()} @{dur} - x=fBD, y=MCFF-L, colour=DAR (clipped for display; "
                f"stored signed). METRIC_SPEC v1.1; translation-only compensation, pre-overlay masks.")


# --------------------------------------------------------------------------
# Fig. 5 -- rank disagreement slopegraph
# --------------------------------------------------------------------------
def fig_rank_disagreement(scores, track="t2v", dur="60s",
                          left=("dynamic_degree",
                                ("VBench", "Dynamic Degree", "1 = most motion"), False),
                          right=("NBF_mean",
                                 ("SNF-Bench", "NBF (static drift)", "1 = least drift"), True),
                          highlight=("Causal-Forcing", "Infinite-Forcing"),
                          out="fig5_rank_disagreement"):
    """Two rank columns joined by lines. Highlighted methods carry the two
    validated hues; everything else is muted grey context."""
    lk, ll, l_low = left
    rk, rl, r_low = right
    lp, rp = method_means(scores, track, dur, lk), method_means(scores, track, dur, rk)
    common = {n for n, _ in lp} & {n for n, _ in rp}
    if len(common) < 3:
        return None
    lp = [(n, v) for n, v in lp if n in common]
    rp = [(n, v) for n, v in rp if n in common]
    lr, rr = ranks(lp, l_low), ranks(rp, r_low)
    N = len(common)

    fig, ax = plt.subplots(figsize=(COL, COL * 0.95))
    for n in sorted(common):
        hl = n in highlight
        color = (P.SERIES_1 if n == highlight[0]
                 else P.SERIES_2 if n == highlight[1] else P.MUTED)
        ax.plot([0, 1], [lr[n], rr[n]], color=color, lw=2.0 if hl else 1.1,
                alpha=1.0 if hl else 0.55, zorder=3 if hl else 2,
                solid_capstyle="round")
        ax.scatter([0, 1], [lr[n], rr[n]], s=26 if hl else 14, color=color,
                   zorder=4 if hl else 2, edgecolors=P.SURFACE, linewidths=1.2)
        ax.annotate(f"{n}", (0, lr[n]), textcoords="offset points", xytext=(-7, 0),
                    ha="right", va="center", fontsize=6.4,
                    color=P.INK if hl else P.INK_SECONDARY,
                    fontweight="bold" if hl else "normal")
        ax.annotate(f"{n}", (1, rr[n]), textcoords="offset points", xytext=(7, 0),
                    ha="left", va="center", fontsize=6.4,
                    color=P.INK if hl else P.INK_SECONDARY,
                    fontweight="bold" if hl else "normal")

    ax.set_xlim(-0.95, 1.95)
    ax.set_ylim(N + 0.6, 0.4)                       # rank 1 at the top
    ax.set_yticks(range(1, N + 1))
    ax.set_ylabel("rank")
    # Column headers live ABOVE the axes (x in data coords, y in axes coords).
    # As x-tick labels they centre on the tick and the two captions collide;
    # stacked onto short lines they clear the 1-unit column spacing.
    tr = ax.get_xaxis_transform()
    for x, (src, met, sub) in [(0, ll), (1, rl)]:
        ax.text(x, 1.15, src, ha="center", va="bottom", fontsize=7,
                color=P.INK, fontweight="bold", transform=tr)
        ax.text(x, 1.075, met, ha="center", va="bottom", fontsize=6.8,
                color=P.INK_SECONDARY, transform=tr)
        ax.text(x, 1.005, sub, ha="center", va="bottom", fontsize=6.2,
                color=P.MUTED, transform=tr)
    ax.set_xticks([])
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", alpha=0.55)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=0.3)
    return save(fig, out,
                f"{track.upper()} @{dur} - ranks from {lk} vs {rk}, prompt-level means over "
                f"{len(common)} public methods. NBF is per-second (METRIC_SPEC v1.1 s.2); "
                f"pre-overlay masks. Compensation-independent metrics only.")


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
                      markerfacecolor=c, markeredgecolor=P.SURFACE, label=cat)
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
    """Panel (a): where the partition comes from, and why it cannot be
    contaminated by the failure being measured. Panel (b): why the partition is
    three-way rather than binary.

    Drawn rather than photographed on purpose -- the claim is about the
    *protocol*, and a schematic states it without inviting the reader to argue
    about one particular frame.
    """
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

    C_STATIC, C_FLOW, C_OVER = P.MUTED, P.SERIES_1, P.SERIES_2
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(DCOL, 2.35),
                                   gridspec_kw=dict(width_ratios=[1.32, 1.0]))

    def box(ax, x, y, w, h, label, fc="none", ec=P.AXIS, fs=6.0, bold=False, tc=None):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                    linewidth=0.9, edgecolor=ec, facecolor=fc,
                                    zorder=2))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs,
                color=tc or P.INK, zorder=3,
                fontweight="bold" if bold else "normal")

    def arrow(ax, p0, p1, color=P.AXIS):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=7,
                                     linewidth=0.9, color=color, zorder=2,
                                     shrinkA=1, shrinkB=1))

    # ---- (a) provenance of the mask -------------------------------------
    axa.set_xlim(0, 1); axa.set_ylim(0, 1); axa.axis("off")
    axa.text(0.0, 0.955, "(a)  where the partition comes from", fontsize=7.4,
             fontweight="bold", color=P.INK)

    axa.text(0.0, 0.845, "I2V", fontsize=6.8, fontweight="bold", color=C_FLOW)
    box(axa, 0.10, 0.78, 0.24, 0.115, "source image", fc="#eef4fd", ec=C_FLOW)
    box(axa, 0.42, 0.78, 0.20, 0.115, "ONE mask", fc="#eef4fd", ec=C_FLOW, bold=True)
    box(axa, 0.70, 0.78, 0.28, 0.115, "every model scored\nagainst it", fs=5.6)
    arrow(axa, (0.34, 0.8375), (0.42, 0.8375)); arrow(axa, (0.62, 0.8375), (0.70, 0.8375))

    axa.text(0.0, 0.615, "T2V", fontsize=6.8, fontweight="bold", color=C_OVER)
    for i, yy in enumerate((0.47, 0.325, 0.18)):
        lbl = "model $k$" if i == 2 else f"model {i + 1}"
        box(axa, 0.10, yy, 0.20, 0.105, lbl, fs=5.8)
        box(axa, 0.38, yy, 0.24, 0.105, "its OWN\nframe 0", fs=5.4, fc="#fdf1ec", ec=C_OVER)
        box(axa, 0.70, yy, 0.24, 0.105, "its own mask", fs=5.6, fc="#fdf1ec",
            ec=C_OVER, bold=True)
        arrow(axa, (0.30, yy + 0.052), (0.38, yy + 0.052))
        arrow(axa, (0.62, yy + 0.052), (0.70, yy + 0.052))
    axa.text(0.5, 0.115, "annotator never sees a later frame", ha="center",
             fontsize=6.0, color=P.INK, style="italic")
    axa.text(0.5, 0.048,
             "layout-dependent, but FAILURE-independent:\n"
             "long-horizon drift cannot contaminate the mask",
             ha="center", fontsize=5.7, color=P.INK_SECONDARY)

    # ---- (b) three labels, not two --------------------------------------
    axb.set_xlim(0, 1); axb.set_ylim(0, 1); axb.axis("off")
    axb.text(0.0, 0.955, "(b)  three labels, not two", fontsize=7.4,
             fontweight="bold", color=P.INK)

    fx, fy, fw, fh = 0.045, 0.30, 0.62, 0.56
    axb.add_patch(Rectangle((fx, fy), fw, fh, facecolor="#f4f4f1",
                            edgecolor=P.AXIS, linewidth=0.9, zorder=1))
    # static support: buildings
    for bx, bw, bh in ((0.07, 0.13, 0.34), (0.22, 0.10, 0.26), (0.34, 0.15, 0.40)):
        axb.add_patch(Rectangle((fx + bx, fy + 0.10), bw, bh, facecolor=C_STATIC,
                                edgecolor="none", alpha=0.55, zorder=2))
    # dynamic flow: water band
    axb.add_patch(Rectangle((fx, fy), fw, 0.10, facecolor=C_FLOW, edgecolor="none",
                            alpha=0.55, zorder=2))
    # overlay: rain crossing BOTH
    for i in range(16):
        x0 = fx + 0.02 + i * 0.037
        axb.plot([x0, x0 - 0.022], [fy + fh - 0.03, fy + 0.13], color=C_OVER,
                 linewidth=1.0, alpha=0.85, zorder=3, solid_capstyle="round")

    for yy, c, lab in ((0.225, C_STATIC, r"$\Omega_{\mathrm{static}}$  support"),
                       (0.135, C_FLOW, r"$\Omega_{\mathrm{flow}}$  intended motion"),
                       (0.045, C_OVER, r"$\Omega_{\mathrm{overlay}}$  transits both")):
        axb.add_patch(Rectangle((0.045, yy), 0.035, 0.045, facecolor=c,
                                edgecolor=P.SURFACE, linewidth=0.8, alpha=0.75))
        axb.text(0.095, yy + 0.022, lab, va="center", fontsize=6.0, color=P.INK)

    axb.text(0.70, 0.74, "rain crosses\nstatic support:\nthe same pixels\nare BOTH",
             fontsize=5.8, color=P.INK_SECONDARY, va="top")
    axb.text(0.70, 0.44,
             r"$\Omega_{\mathrm{overlay}}$ is excluded"
             "\nfrom headline\nfBD and NBF",
             fontsize=5.8, color=P.INK, va="top", fontweight="bold")

    fig.tight_layout(pad=0.35)
    return save(fig, out,
                "Schematic; no measured data. Mask protocol per METRIC_SPEC v1.1 s.4 "
                "(three-label partition; T2V masks future-blind per model output).",
                prefreeze=False)

if __name__ == "__main__":
    sys.exit(main())

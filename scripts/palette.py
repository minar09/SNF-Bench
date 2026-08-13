"""Figure palette for SNF-Bench, with the colorblind-safety checks run in-process.

Paper figures are read in print, in grayscale photocopies, and by reviewers with
colour-vision deficiency, so the palette is *computed and checked*, not chosen by
eye. This is a Python port of the OKLab / Machado-CVD checks (the reference
implementation is JavaScript and this machine's node is too old to run it).

Design consequence that shapes every figure here: under an all-pairs pairlist
(which is what a scatter needs, since any two points can sit side by side) only
a **three-slot** categorical palette clears the separation floors. SNF-Bench has
7-9 methods per track. So method identity is NEVER carried by hue in these
figures -- it is carried by direct text labels, and hue is reserved for either
(a) magnitude, as a single-hue sequential ramp, or (b) at most two highlighted
methods against muted grey context.

    CVD_TARGET  8.0   OKLab dE x100, min over protan/deutan
    NORMAL_FLOOR 15.0 OKLab dE x100, unsimulated vision -- hard gate
"""

import math

CVD_TARGET, CVD_FLOOR, NORMAL_FLOOR = 8.0, 6.0, 15.0

# --- roles -----------------------------------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"          # axis / label / de-emphasised series
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

SERIES_1 = "#2a78d6"       # blue   -- primary highlight
SERIES_2 = "#eb6834"       # orange -- secondary highlight
SERIES_3 = "#1baf7a"       # aqua   -- third, only if all three are needed

# Full categorical order, in fixed slot order -- NEVER cycled, never reordered.
# Valid for the ADJACENT pairlist only (stacked bars, grouped bars, lines),
# where segments of different hue physically touch. For scatter/bubble, where
# any two marks can end up side by side, the all-pairs floors apply and only
# the first three slots clear them -- see the module docstring.
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
               "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

# Ink that stays legible on top of each categorical slot (>=4.5:1).
CATEGORICAL_ON = ["#ffffff", "#0b0b0b", "#0b0b0b", "#0b0b0b",
                  "#0b0b0b", "#ffffff", "#ffffff", "#0b0b0b"]

# Single-hue sequential ramp (blue), light -> dark. For magnitude encoding.
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281"]

# Print/grayscale secondary channel: never rely on hue alone.
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*", "<"]

MACHADO = {
    "protan": ((0.152286, 1.052583, -0.204868),
               (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968),
               (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779),
               (-0.078411, 0.930809, 0.147602),
               (0.004733, 0.691367, 0.303900)),
}


def _hex2srgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def _s2lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lin(h):
    return [_s2lin(c) for c in _hex2srgb(h)]


def _oklab_from_lin(rgb):
    r, g, b = rgb
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def _simulate(h, kind):
    r, g, b = _lin(h)
    M = MACHADO[kind]
    return [min(1.0, max(0.0, M[i][0] * r + M[i][1] * g + M[i][2] * b)) for i in range(3)]


def delta_e(h1, h2, kind=None):
    """Euclidean OKLab distance x100; kind=None is unsimulated vision."""
    a = _oklab_from_lin(_simulate(h1, kind) if kind else _lin(h1))
    b = _oklab_from_lin(_simulate(h2, kind) if kind else _lin(h2))
    return 100 * math.dist(a, b)


def relative_luminance(h):
    r, g, b = _lin(h)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def validate(palette, surface=SURFACE, pairs="all"):
    """-> (ok, report rows). `pairs='all'` is the right mode for scatter figures."""
    idx = (list(zip(range(len(palette) - 1), range(1, len(palette)))) if pairs == "adjacent"
           else [(i, j) for i in range(len(palette)) for j in range(i + 1, len(palette))])
    rows, ok = [], True
    for i, j in idx:
        c1, c2 = palette[i], palette[j]
        cvd = min(delta_e(c1, c2, "protan"), delta_e(c1, c2, "deutan"))
        nrm = delta_e(c1, c2)
        status = "PASS"
        if nrm < NORMAL_FLOOR:
            status, ok = "FAIL(normal)", False
        elif cvd < CVD_FLOOR:
            status, ok = "FAIL(cvd)", False
        elif cvd < CVD_TARGET:
            status = "WARN(cvd)"
        rows.append((c1, c2, round(cvd, 1), round(nrm, 1), status))
    for c in palette:
        cr = contrast(c, surface)
        if cr < 3.0:
            rows.append((c, surface, "-", round(cr, 2), "RELIEF(needs direct label)"))
    return ok, rows


def mpl_rc():
    """Matplotlib rcParams for print figures: recessive chrome, real text ink."""
    return {
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS, "axes.labelcolor": INK,
        "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
        "xtick.labelcolor": INK_SECONDARY, "ytick.labelcolor": INK_SECONDARY,
        "grid.color": GRID, "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.8, "lines.linewidth": 2.0,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
        "legend.frameon": False, "legend.fontsize": 7.5,
        "figure.dpi": 200, "savefig.dpi": 300, "savefig.bbox": "tight",
        "pdf.fonttype": 42, "ps.fonttype": 42,   # editable/embeddable text for camera-ready
    }


if __name__ == "__main__":
    for name, pal, mode in [
            ("highlight pair (scatter, Fig.4/5)", [SERIES_1, SERIES_2], "all"),
            ("three-slot max (scatter)", [SERIES_1, SERIES_2, SERIES_3], "all"),
            ("highlight + muted context", [SERIES_1, SERIES_2, MUTED], "all"),
            ("6 categories (stacked bar, Fig.S)", CATEGORICAL[:6], "adjacent")]:
        ok, rows = validate(pal, pairs=mode)
        print(f"\n{name}: {'PASS' if ok else 'FAIL'}  ({mode}-pairs)")
        for r in rows:
            print(f"   {r[0]} vs {r[1]}  cvdDE={r[2]:>5}  normDE={r[3]:>5}  {r[4]}")

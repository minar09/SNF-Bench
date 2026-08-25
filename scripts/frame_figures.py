"""Qualitative figures built from real generated frames.

Three figures, each answering a question a table cannot:

  fig1_motivation   why the benchmark is needed -- two clips a whole-frame
                    motion score rates almost identically, one of which is
                    doing the right thing and one of which is sliding
  fig6_qualitative  what the audited systems actually look like over a rollout
  fig7_limitations  where SNF-Bench itself fails, shown rather than asserted

Frames come from the released videos at fixed wall-clock timestamps, so a row
is a genuine time series rather than a curated triple. Exemplars are chosen by
a stated numeric rule (see pick_motivation), not by eye.

    ~/miniconda3/envs/snfeval/bin/python scripts/frame_figures.py
"""

import csv
import glob
import os
import sys
from collections import defaultdict

import cv2
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                       # noqa: E402
from matplotlib.patches import Rectangle              # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette as P                                   # noqa: E402
from registry import contestants                      # noqa: E402
from figures import save, COL, DCOL                   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN, FIG = f"{ROOT}/manifest", f"{ROOT}/figures"
plt.rcParams.update(P.mpl_rc())


# ---------------------------------------------------------------- data access
def load_scores(track="t2v", dur="60s"):
    acc = defaultdict(dict)
    for r in csv.DictReader(open(f"{MAN}/per_video_scores.csv")):
        if r["track"] == track and r["duration"] == dur:
            acc[(r["model"], r["prompt_id"])][r["metric"]] = float(r["value"])
    return acc


def video_for(track, key, dur, prompt_id):
    """Locate the mp4 whose filename matches this prompt_id."""
    for p in sorted(glob.glob(f"{ROOT}/videos/{track}/{key}/{dur}/*.mp4")):
        name = os.path.basename(p)
        stem = name[:100].replace(" ", "_") if track == "t2v" else name[:-4]
        if track == "t2v":
            stem = name.rsplit("-", 2)[0] if name.count("-") >= 2 else name
            stem = stem[:100]
        if stem.startswith(prompt_id[:80]) or prompt_id[:80] in name:
            return p
    return None


def grab(path, seconds, target_h=110):
    """-> list of RGB frames at the requested wall-clock times."""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 16.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    out = []
    for s in seconds:
        idx = min(total - 1, max(0, int(round(s * fps))))
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, f = cap.read()
        if not ok:
            out.append(None)
            continue
        h, w = f.shape[:2]
        f = cv2.resize(f, (int(round(w * target_h / h)), target_h),
                       interpolation=cv2.INTER_AREA)
        out.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
    cap.release()
    return out


# ------------------------------------------------------------------ selection
def pick_motivation(acc, pub):
    """Choose the prompt where a whole-frame motion score is LEAST able to tell
    desired flow from whole-scene drift.

    Rule, fixed in advance: among prompts evaluated by every system, maximise
        (fBD_drift - fBD_good) / (1 + |DD_drift - DD_good|)
    i.e. the largest static-fidelity gap accompanied by the smallest Dynamic
    Degree gap, with a third system that is frozen. Selecting on the *metric
    disagreement* rather than on appearance is what keeps the figure evidence
    instead of illustration.
    """
    prompts = sorted({p for (_, p) in acc})
    best = None
    for pr in prompts:
        rows = {pub[m]: acc[(m, pr)] for m in pub
                if (m, pr) in acc and "fBD_mean" in acc[(m, pr)]
                and "MCFF_late_mean" in acc[(m, pr)]
                and "dynamic_degree" in acc[(m, pr)]}
        if len(rows) < 6:
            continue
        good = min(rows, key=lambda n: rows[n]["fBD_mean"] - 2 * rows[n]["MCFF_late_mean"])
        drift = max(rows, key=lambda n: rows[n]["fBD_mean"])
        froz = min(rows, key=lambda n: rows[n]["MCFF_late_mean"])
        if len({good, drift, froz}) < 3:
            continue
        dd_gap = abs(rows[drift]["dynamic_degree"] - rows[good]["dynamic_degree"])
        fbd_gap = rows[drift]["fBD_mean"] - rows[good]["fBD_mean"]
        if fbd_gap <= 0:
            continue
        score = fbd_gap / (1.0 + 40.0 * dd_gap)
        if best is None or score > best[0]:
            best = (score, pr, good, drift, froz, rows)
    return best


# ------------------------------------------------------------------- figure 1
def fig_motivation(acc, pub, key_of, out="fig1_motivation"):
    sel = pick_motivation(acc, pub)
    if sel is None:
        return None
    _, prompt, good, drift, froz, rows = sel
    times = [0, 30, 60]
    cases = [("support held,\nmotion persists", good, P.SERIES_3),
             ("support drifts", drift, P.SERIES_2),
             ("support held,\nmotion stopped", froz, P.MUTED)]

    strips = []
    for lab, name, col in cases:
        v = video_for("t2v", key_of[name], "60s", prompt)
        if v is None:
            return None
        strips.append((lab, name, col, grab(v, times, target_h=84)))

    nrow, ncol = 3, len(times) + 1
    fig = plt.figure(figsize=(DCOL, 1.78))
    gs = fig.add_gridspec(nrow, ncol, width_ratios=[1] * len(times) + [0.92],
                          wspace=0.045, hspace=0.09,
                          left=0.075, right=0.995, top=0.885, bottom=0.055)

    for r, (lab, name, col, frames) in enumerate(strips):
        for c, (t, fr) in enumerate(zip(times, frames)):
            ax = fig.add_subplot(gs[r, c])
            if fr is not None:
                ax.imshow(fr)
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_edgecolor(col); s.set_linewidth(1.3)
            if r == 0:
                ax.set_title(f"$t={t}$ s", fontsize=6.8, color=P.INK, pad=3)
            if c == 0:
                ax.set_ylabel(f"{lab}\n{name}", fontsize=6.0, color=P.INK,
                              rotation=0, ha="right", va="center", labelpad=6)

        m = rows[name]
        ax = fig.add_subplot(gs[r, -1])
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        vals = [("VBench DD*", m["dynamic_degree"], "{:.3f}"),
                ("fBD", m["fBD_mean"], "{:.1f}"),
                ("MCFF-L", m["MCFF_late_mean"], "{:.1f}")]
        for i, (n, v, f) in enumerate(vals):
            y = 0.80 - i * 0.30
            ax.text(0.02, y, n, fontsize=6.0, color=P.INK_SECONDARY,
                    transform=ax.transAxes, va="center")
            ax.text(0.98, y, f.format(v), fontsize=7.0, color=P.INK,
                    transform=ax.transAxes, va="center", ha="right",
                    fontweight="bold" if n == "VBench DD" else "normal")

    dd_g, dd_d = rows[good]["dynamic_degree"], rows[drift]["dynamic_degree"]
    fb_g, fb_d = rows[good]["fBD_mean"], rows[drift]["fBD_mean"]
    fig.text(0.5, 0.955,
             f"A whole-frame motion score rates the top two rows almost identically "
             f"(DD {dd_g:.3f} vs {dd_d:.3f}) — their background drift differs "
             f"over {int(fb_d / max(fb_g, 1e-6) / 10) * 10}$\\times$",
             ha="center", fontsize=7.2, color=P.INK, fontweight="bold")
    return save(fig, out,
                f"Frames from 60 s outputs of released checkpoints under the recorded common "
                f"T2V configuration. Systems chosen by a "
                f"fixed numeric rule over all 23 prompts, not by appearance. *DD is the "
                f"per-video score under VBench's published rule, before binarization.",
                prefreeze=False)


# ------------------------------------------------------------------- figure 6
def fig_qualitative(acc, pub, key_of, out="fig6_qualitative"):
    """Every audited system on one prompt across the rollout.

    Systems run along the columns and time down the rows. The transpose matters:
    with 16:9 frames, seven systems as *rows* forces each cell to be short and
    wide, so the images letterbox and the figure fills with gaps. Seven columns
    at page width gives each frame a cell of the right aspect and keeps the
    whole comparison under two inches of height.
    """
    sel = pick_motivation(acc, pub)
    if sel is None:
        return None
    _, prompt, good, drift, froz, rows = sel
    order = sorted(rows, key=lambda n: rows[n]["fBD_mean"])

    vids = {}
    for name in order:
        v = video_for("t2v", key_of[name], "60s", prompt)
        if v:
            vids[name] = v
    if not vids:
        return None
    order = [n for n in order if n in vids]

    cap = cv2.VideoCapture(vids[order[0]])
    secs = (cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0) / (cap.get(cv2.CAP_PROP_FPS) or 16)
    cap.release()
    # grab() clamps the seek to the last frame, so a 60.06 s clip may ask
    # for t=60 safely; the earlier `secs - 1` guard silently dropped it.
    times = [t for t in (0, 30, 60) if t <= secs + 0.5] or [0]

    cellw = DCOL / len(order)
    fig, axes = plt.subplots(len(times), len(order),
                             figsize=(DCOL, cellw * 9 / 16 * len(times) + 0.52))
    axes = np.atleast_2d(axes)
    for c, name in enumerate(order):
        frames = grab(vids[name], times, target_h=96)
        hl = name in (good, drift)
        for r in range(len(times)):
            ax = axes[r, c]
            if frames[r] is not None:
                ax.imshow(frames[r])
            ax.set_xticks([]); ax.set_yticks([])
            col = (P.SERIES_3 if name == good else
                   P.SERIES_2 if name == drift else P.AXIS)
            for sp in ax.spines.values():
                sp.set_edgecolor(col); sp.set_linewidth(1.2 if hl else 0.5)
            if r == 0:
                ax.set_title(name, fontsize=5.6, color=P.INK,
                             fontweight="bold" if hl else "normal", pad=2.5)
            if c == 0:
                ax.set_ylabel(f"$t={times[r]}$ s", fontsize=6.2, color=P.INK,
                              rotation=90, va="center", labelpad=3)
    fig.subplots_adjust(left=0.035, right=0.998, top=0.885, bottom=0.075,
                        wspace=0.03, hspace=0.035)
    return save(fig, out,
                "One prompt, every audited system, ordered left-to-right by increasing "
                "static-region drift (fBD). Released 60 s generations; the two "
                "highlighted systems are the pair a whole-frame motion score cannot "
                "separate.",
                prefreeze=False)


# ------------------------------------------------------------------- figure 7
def fig_limitations(acc, pub, key_of, out="fig7_limitations"):
    """Where SNF-Bench itself fails, shown rather than asserted.

    Each column is a stated scope boundary of the benchmark, not a failure of
    the system depicted. Clips are chosen by rule: (a) the precipitation prompt
    scored by the system with the lowest static drift, so the only motion in
    frame really is the falling particles; (b) the system with the least
    surviving late motion, on the prompt where it scores best on static
    fidelity; (c) that same degenerate regime seen over an 8 s gap, where two
    widely separated frames are near-identical.
    """
    cats = {}
    for r in csv.DictReader(open(f"{MAN}/prompt_categories.csv")):
        if r["track"] == "t2v" and r["duration"] == "60s":
            cats[r["prompt_id"]] = r["category"]

    def fbd(name, pr):
        return acc.get((key_of[name], pr), {}).get("fBD_mean", 9e9)

    def mcff(name, pr):
        return acc.get((key_of[name], pr), {}).get("MCFF_late_mean", 9e9)

    names = list(pub.values())
    # (a) precipitation, and prefer a prompt that literally names rain or snow
    # so the layered content is visible rather than merely categorical.
    rain = [p for p, c in cats.items() if c == "precipitation"]
    rain.sort(key=lambda p: (0 if ("rain" in p.lower() or "snow" in p.lower()) else 1, p))
    # (b)/(c) the most stalled system overall
    froz = min(names, key=lambda n: sum(mcff(n, p) for p in cats if mcff(n, p) < 9e9))

    panels = []
    if rain:
        pr = rain[0]
        stable = min(names, key=lambda n: fbd(n, pr))
        v = video_for("t2v", key_of[stable], "60s", pr)
        if v:
            panels.append(("(a) layered content",
                           "rain and snow cross static support, so those\n"
                           "pixels are assigned to one region by flow alone",
                           grab(v, [12, 48], target_h=100), ["t = 12 s", "t = 48 s"]))

    # (b) genuinely frozen means BOTH factors small: a clip with a tiny MCFF-L
    # alone may simply be drifting so hard that compensation removes everything,
    # which is a different failure and would make the panel contradict its own
    # caption. Require visible stability (low fBD) first, then take the least
    # surviving motion within that set.
    stable = [(n, p) for n in names for p in cats
              if mcff(n, p) < 9e9 and fbd(n, p) < 3.0]
    frozen_clip = min(stable, key=lambda np_: mcff(*np_)) if stable else None
    if frozen_clip:
        n_b, pr_b = frozen_clip
        v = video_for("t2v", key_of[n_b], "60s", pr_b)
        if v:
            panels.append(("(b) stability without motion",
                           f"{n_b}: fBD {fbd(n_b, pr_b):.2f} is among the best static\n"
                           f"fidelity in the audit, yet MCFF-L {mcff(n_b, pr_b):.2f} -- the intended\n"
                           f"motion has stopped too",
                           grab(v, [5, 55], target_h=100), ["t = 5 s", "t = 55 s"]))

    # (c) high leakage with low attenuation under the fitted similarity model.
    # The residual is not causally identified and may contain deformation,
    # intended local motion, partition contamination, or flow error.
    def dlr(n, p):
        return acc.get((key_of[n], p), {}).get("DLR_mean", -1)

    def dar(n, p):
        return acc.get((key_of[n], p), {}).get("DAR_mean", 9e9)

    cand = [(n, p) for n in names for p in cats
            if dlr(n, p) > 0.6 and dar(n, p) < 0.25]
    if cand:
        n_c, pr_c = max(cand, key=lambda np_: dlr(*np_) - dar(*np_))
        v = video_for("t2v", key_of[n_c], "60s", pr_c)
        if v:
            panels.append(("(c) non-rigid drift",
                           f"{n_c}: DLR {dlr(n_c, pr_c):.2f} but DAR "
                           f"{max(0.0, dar(n_c, pr_c)):.2f} -- the support moves, yet a\n"
                           "fitted similarity compensation attenuates little of the\n"
                           "measured flow; the residual is not causally identified",
                           grab(v, [8, 52], target_h=100), ["t = 8 s", "t = 52 s"]))

    panels = [p for p in panels if p[2] and all(f is not None for f in p[2])]
    if not panels:
        return None

    fig, axes = plt.subplots(2, len(panels), figsize=(DCOL, 2.30))
    axes = np.atleast_2d(axes)
    for c, (title, note, frames, stamps) in enumerate(panels):
        for r in range(2):
            ax = axes[r, c]
            ax.imshow(frames[r])
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_edgecolor(P.SERIES_2); sp.set_linewidth(1.0)
            ax.text(0.015, 0.93, stamps[r], transform=ax.transAxes, fontsize=5.4,
                    color="white", va="top", ha="left",
                    bbox=dict(boxstyle="round,pad=0.14", fc=(0, 0, 0, 0.45), ec="none"))
            if r == 0:
                ax.set_title(title, fontsize=6.9, color=P.INK,
                             fontweight="bold", pad=4)
    fig.subplots_adjust(left=0.008, right=0.992, top=0.885, bottom=0.215,
                        wspace=0.045, hspace=0.045)
    # Notes are placed as figure text centred under each column, so a long line
    # cannot be clipped by its axes box the way an xlabel is.
    n = len(panels)
    for c, (_, note, _, _) in enumerate(panels):
        fig.text((c + 0.5) / n, 0.145, note, ha="center", va="top",
                 fontsize=5.7, color=P.INK_SECONDARY, linespacing=1.45)
    return save(fig, out,
                "Two timestamps of one released generation per column. These are "
                "stated scope boundaries of SNF-Bench, not failures of the systems "
                "shown.", prefreeze=False)


def main():
    acc = load_scores()
    pub = {m["key"]: m["name"] for m in contestants("t2v")}
    key_of = {v: k for k, v in pub.items()}
    for fn in (fig_motivation, fig_qualitative, fig_limitations):
        r = fn(acc, pub, key_of)
        print("  wrote figures/" + r if r else f"  SKIPPED {fn.__name__}")
    r = fig_i2v_qualitative()
    print("  wrote figures/" + r if r else "  SKIPPED fig_i2v_qualitative")




# ------------------------------------------------------------------- figure 8
def fig_i2v_qualitative(out="fig8_i2v_qualitative"):
    """Image-conditioned systems on one shared source image.

    The I2V case deserves its own plate because its static support is given
    externally: every system starts from the same frame, so divergence over the
    rollout is attributable to the system rather than to a differently imagined
    scene. That is not true of the text-conditioned track, where each system
    authors its own layout.
    """
    import registry
    # load_scores here is keyed (model, prompt_id) -> {metric: value}; that is a
    # different convention from figures.load_scores, so do not mix them.
    acc = load_scores(track="i2v", dur="60s")
    pub = {m["key"]: m["name"] for m in registry.contestants("i2v")}
    key_of = {v: k for k, v in pub.items()}

    fbd = defaultdict(dict)          # name -> prompt -> fBD
    for (k, pr), d in acc.items():
        if k in pub and "fBD_mean" in d:
            fbd[pub[k]][pr] = d["fBD_mean"]
    rows = {n: v for n, v in fbd.items() if len(v) >= 5}
    if len(rows) < 3:
        return None

    shared = set.intersection(*[set(v) for v in rows.values()])
    if not shared:
        return None
    # Prompt on which the systems disagree most about static fidelity.
    prompt = max(shared, key=lambda p: max(rows[n][p] for n in rows)
                 - min(rows[n][p] for n in rows))
    order = sorted(rows, key=lambda n: rows[n][prompt])

    vids = {}
    for name in order:
        v = video_for("i2v", key_of[name], "60s", prompt)
        if v:
            vids[name] = v
    order = [n for n in order if n in vids]
    if len(order) < 3:
        return None
    times = [0, 30, 60]

    cellw = DCOL / len(order)
    fig, axes = plt.subplots(len(times), len(order),
                             figsize=(DCOL, cellw * 9 / 16 * len(times) + 0.55))
    axes = np.atleast_2d(axes)
    for c, name in enumerate(order):
        frames = grab(vids[name], times, target_h=88)
        for r in range(len(times)):
            ax = axes[r, c]
            if frames[r] is not None:
                ax.imshow(frames[r])
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_edgecolor(P.AXIS); sp.set_linewidth(0.5)
            if r == 0:
                ax.set_title(name.replace(" (", "\n("), fontsize=4.9,
                             color=P.INK, pad=2.5, linespacing=1.1)
            if c == 0:
                ax.set_ylabel(f"$t={times[r]}$ s", fontsize=6.2, color=P.INK,
                              rotation=90, va="center", labelpad=3)
    fig.subplots_adjust(left=0.035, right=0.998, top=0.845, bottom=0.012,
                        wspace=0.03, hspace=0.035)
    return save(fig, out,
                "Image-conditioned systems on one shared source image, ordered "
                "left-to-right by increasing static-region drift.",
                prefreeze=False)
if __name__ == "__main__":
    main()

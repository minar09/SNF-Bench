"""Build the SNF-Bench axis-specific human study from the released I2V clips.

This is NOT a preference study. Raters answer two forced-choice questions, one
per failure axis, and are never asked which clip is better -- the whole point of
the benchmark is that "better" conflates the two failures it separates:

    drift  Which clip's BACKGROUND moves more?       -> compared against fBD / NBF
    decay  In which clip does the MOTION die out?    -> compared against MCFF-L / FP

Media. Clips are the image-conditioned 60 s rollouts already hosted on Drive for
an earlier study; `human_study/scenes_public.json` carries those URLs verbatim.
They are never regenerated here -- the file is data, and this script only reads
it. Only the three publicly released systems present in that set are used; the
internal ablations that shared the same scenes are excluded by the roster rule.

Pairs are chosen by rule, not by eye: for each axis, candidate pairs are binned
by the *relative gap* in the relevant factor and sampled across the range, so
agreement is measured over the whole operating range rather than only where any
metric would look good. Sentinel trials show one clip against itself, where the
only correct answer is "about the same"; a rater who does not say so is not
attending, and their session is flagged rather than silently averaged in.

    ~/miniconda3/envs/snfeval/bin/python scripts/make_human_study.py
"""

import csv
import json
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registry import ALL                                        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN, OUT = f"{ROOT}/manifest", f"{ROOT}/human_study"

TRACK, DUR = "i2v", "60s"
N_PER_AXIS = 9                 # 18 scored trials + 2 sentinels, about 8 minutes
N_SENTINELS = 2
GAP_BINS = [(0.05, 0.20), (0.20, 0.50), (0.50, 1.00)]

AXES = [
    ("drift", "NBF_mean", True),      # higher NBF  -> more background motion
    ("decay", "MCFF_late_mean", False),  # lower MCFF-L -> motion died out more
]


def load_scores(models):
    acc = defaultdict(dict)
    with open(f"{MAN}/per_video_scores.csv") as fh:
        for r in csv.DictReader(fh):
            if (r["track"] == TRACK and r["duration"] == DUR
                    and r["model"] in models):
                acc[(r["model"], r["prompt_id"])][r["metric"]] = float(r["value"])
    return acc


def pick(scenes, acc, metric, higher_means_more, n, seed):
    """Pairs of systems on a shared scene, stratified by relative metric gap."""
    rng = random.Random(seed)
    cand = []
    for sc in scenes:
        names = sorted(sc["videos"])
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                va = acc.get((a, sc["prompt_id"]), {}).get(metric)
                vb = acc.get((b, sc["prompt_id"]), {}).get(metric)
                if va is None or vb is None:
                    continue
                hi = max(abs(va), abs(vb))
                if hi <= 0:
                    continue
                # The factor's own verdict: which clip the metric says shows
                # *more* of the asked-about failure. Never shown to the rater.
                more = (a if va > vb else b) if higher_means_more else \
                       (a if va < vb else b)
                cand.append(dict(scene=sc["id"], prompt_id=sc["prompt_id"],
                                 a=a, b=b, va=va, vb=vb,
                                 gap=abs(va - vb) / hi, metric_says=more))
    out, per_bin = [], max(1, n // len(GAP_BINS))
    for lo, hi in GAP_BINS:
        pool = [c for c in cand if lo <= c["gap"] < hi]
        rng.shuffle(pool)
        out += pool[:per_bin]
    if len(out) < n:                      # top up from the widest gaps available
        rest = sorted((c for c in cand if c not in out),
                      key=lambda c: -c["gap"])
        out += rest[:n - len(out)]
    rng.shuffle(out)
    return out[:n]


def gs_literal(v):
    return json.dumps(v, ensure_ascii=False)


def main():
    scenes = json.load(open(f"{OUT}/scenes_public.json"))
    models = sorted({m for sc in scenes for m in sc["videos"]})
    names = {m["key"]: m["name"] for m in ALL if m["track"] == TRACK}
    acc = load_scores(models)
    print(f"{len(scenes)} scenes, {len(models)} public systems: "
          + ", ".join(names.get(m, m) for m in models))

    trials, study = [], {"track": TRACK, "duration": DUR, "axes": []}
    for axis, metric, higher in AXES:
        rows = pick(scenes, acc, metric, higher, N_PER_AXIS,
                    seed=0 if axis == "drift" else 1)
        if rows:
            g = [r["gap"] for r in rows]
            print(f"  {axis:6s} ({metric}): {len(rows)} pairs, "
                  f"gap {min(g):.2f}-{max(g):.2f}")
        else:
            print(f"  {axis:6s} ({metric}): NO PAIRS -- scores missing")
        study["axes"].append(dict(axis=axis, metric=metric, pairs=rows))
        trials += [dict(t, axis=axis, metric=metric, sentinel=False) for t in rows]

    # Sentinels: the same clip on both sides. Only "same" is correct.
    rng = random.Random(7)
    for sc in rng.sample(scenes, min(N_SENTINELS, len(scenes))):
        m = rng.choice(sorted(sc["videos"]))
        trials.append(dict(scene=sc["id"], prompt_id=sc["prompt_id"], a=m, b=m,
                           gap=0.0, metric_says="same", axis="drift",
                           metric="sentinel", sentinel=True))

    json.dump(study, open(f"{OUT}/pairs.json", "w"), indent=2)

    L = ["// AUTO-GENERATED by scripts/make_human_study.py -- do not hand-edit.",
         "// Drive URLs are copied verbatim from the existing hosted assets and",
         "// are never rewritten by the generator.",
         "",
         "const SCENES = ["]
    for sc in scenes:
        L += ["  {",
              f"    id: {gs_literal(sc['id'])},",
              f"    category: {gs_literal(sc['category'])},",
              f"    prompt: {gs_literal(sc['prompt'])},",
              f"    imageUrl: {gs_literal(sc['imageUrl'])},",
              "    videos: {"]
        L += [f"      {gs_literal(k)}: {gs_literal(v)}," for k, v in sc["videos"].items()]
        L += ["    }", "  },"]
    L += ["];", "", "const TRIALS = ["]
    for i, t in enumerate(trials):
        L += ["  {",
              f"    trialId: {i}, axis: {gs_literal(t['axis'])}, "
              f"scene: {gs_literal(t['scene'])},",
              f"    a: {gs_literal(t['a'])}, b: {gs_literal(t['b'])},",
              f"    sentinel: {'true' if t['sentinel'] else 'false'}, "
              f"gap: {round(t['gap'], 3)}",
              "  },"]
    L += ["];", ""]
    open(f"{OUT}/SCENES.gs", "w").write("\n".join(L))

    n_s = sum(1 for t in trials if t["sentinel"])
    print(f"\n  -> {OUT}/pairs.json   (scored pairs + the metric's own verdict)")
    print(f"  -> {OUT}/SCENES.gs    ({len(scenes)} scenes, {len(trials)} trials "
          f"incl. {n_s} sentinels)")
    print("     paste SCENES.gs into the Apps Script project alongside code.gs")


if __name__ == "__main__":
    main()

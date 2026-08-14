"""Select the comparison pairs for the axis-specific human study.

Design follows the reviewers' guidance: this is NOT a preference study. Raters
answer two forced-choice questions with no notion of overall quality:

    Q1  Which video's background moves more?      -> compare against fBD / NBF
    Q2  Which video's motion dies out more?       -> compare against MCFF-L / FP

Keeping the questions axis-specific is what makes the result interpretable. A
"which is better" study would confound the two failure modes the benchmark
exists to separate, and would tell us nothing about whether the factors measure
what they claim.

Pairs are chosen by rule, not by eye: for each axis we bin the audited clips by
the relevant factor and sample pairs spanning small, medium and large metric
gaps, so the study measures agreement across the whole operating range rather
than only on easy extremes. Ties are expected and permitted in the interface;
a study that forces a choice on indistinguishable pairs manufactures noise.

    ~/miniconda3/envs/snfeval/bin/python scripts/make_human_study.py
"""

import csv
import json
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registry import contestants                              # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = f"{ROOT}/manifest"
OUT = f"{ROOT}/human_study"

# 12 per axis = 24 trials, about 8 minutes per rater. Recruiting raters for
# long sessions is the binding constraint, and a short session that people
# actually finish attentively beats a long one they abandon or rush.
N_PER_AXIS = 12
GAP_BINS = [(0.05, 0.20), (0.20, 0.50), (0.50, 1.00)]   # relative metric gap


def load(track="t2v", dur="60s"):
    acc = defaultdict(dict)
    for r in csv.DictReader(open(f"{MAN}/per_video_scores.csv")):
        if r["track"] == track and r["duration"] == dur:
            acc[(r["model"], r["prompt_id"])][r["metric"]] = float(r["value"])
    return acc


def pick_pairs(acc, pub, metric, n, seed=0):
    """Pairs of systems on a shared prompt, stratified by relative metric gap."""
    rng = random.Random(seed)
    by_prompt = defaultdict(dict)
    for (m, p), d in acc.items():
        if m in pub and metric in d:
            by_prompt[p][m] = d[metric]

    cand = []
    for p, systems in by_prompt.items():
        names = sorted(systems)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                va, vb = systems[a], systems[b]
                hi = max(abs(va), abs(vb))
                if hi <= 0:
                    continue
                gap = abs(va - vb) / hi
                cand.append(dict(prompt=p, a=a, b=b, va=va, vb=vb, gap=gap,
                                 # the factor's own verdict, used only for scoring
                                 # afterwards -- never shown to the rater
                                 metric_says=(a if va > vb else b)))
    out, per_bin = [], max(1, n // len(GAP_BINS))
    for lo, hi in GAP_BINS:
        pool = [c for c in cand if lo <= c["gap"] < hi]
        rng.shuffle(pool)
        seen = set()
        for c in pool:
            key = (c["prompt"], c["a"], c["b"])
            if key in seen:
                continue
            seen.add(key)
            out.append(c)
            if len([o for o in out if lo <= o["gap"] < hi]) >= per_bin:
                break
    rng.shuffle(out)
    return out[:n]


def main():
    os.makedirs(OUT, exist_ok=True)
    acc = load()
    pub = {m["key"]: m["name"] for m in contestants("t2v")}

    axes = [("drift", "fBD_mean",
             "Which video's background (buildings, banks, ground, horizon) "
             "moves or warps more?"),
            ("decay", "MCFF_late_mean",
             "In which video does the moving content (water, fire, rain, smoke) "
             "slow down or stop more by the end?")]

    study = {"n_per_axis": N_PER_AXIS, "track": "t2v", "duration": "60s",
             "axes": []}
    for axis, metric, question in axes:
        pairs = pick_pairs(acc, pub, metric, N_PER_AXIS,
                           seed=0 if axis == "drift" else 1)
        study["axes"].append(dict(
            axis=axis, metric=metric, question=question,
            pairs=[dict(prompt=c["prompt"],
                        a=c["a"], b=c["b"],
                        a_name=pub[c["a"]], b_name=pub[c["b"]],
                        gap=round(c["gap"], 3),
                        metric_says=c["metric_says"]) for c in pairs]))
        gaps = [c["gap"] for c in pairs]
        print(f"  {axis:6s} ({metric}): {len(pairs)} pairs, "
              f"gap {min(gaps):.2f}-{max(gaps):.2f}")

    with open(f"{OUT}/pairs.json", "w") as f:
        json.dump(study, f, indent=2)

    # Apps Script fragment: paste into code.gs. Video URLs are filled in by the
    # operator after uploading the clips, so nothing here assumes a Drive layout.
    lines = ["// AUTO-GENERATED by scripts/make_human_study.py -- do not hand-edit.",
             "// Fill each videoA/videoB with a shareable URL for the final-window",
             "// excerpt of that system's generation for that prompt.",
             "const TRIALS = ["]
    for ax in study["axes"]:
        for i, p in enumerate(ax["pairs"]):
            lines.append("  {axis: %r, idx: %d, prompt: %r," % (ax["axis"], i, p["prompt"][:60]))
            lines.append("   a: %r, b: %r," % (p["a"], p["b"]))
            lines.append("   videoA: 'REPLACE_WITH_URL', videoB: 'REPLACE_WITH_URL'},")
    lines += ["];", ""]
    with open(f"{OUT}/TRIALS.gs", "w") as f:
        f.write("\n".join(lines))

    print(f"\n  -> {OUT}/pairs.json  ({sum(len(a['pairs']) for a in study['axes'])} trials)")
    print(f"  -> {OUT}/TRIALS.gs   (paste into the Apps Script project)")


if __name__ == "__main__":
    main()

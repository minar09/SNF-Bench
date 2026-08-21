"""Score the perceptual validation study: do raters order pairs as the factors do?

This is metric validation, not method preference. The only claim it supports is
that, on pairs the factors separate clearly, human judgments of one axis agree
with that factor's ordering. Nothing here ranks systems.

Three statistical choices matter, and each fixes a way small studies mislead:

  * **The unit of analysis is the pair, not the response.** Responses are
    clustered inside rater and inside pair, so a binomial interval over 72
    responses would claim precision the design does not have. Pairs are
    aggregated by majority vote across raters first, and the bootstrap
    resamples *pairs*.
  * **Clear-gap and near-tie pairs are reported separately.** Agreement is only
    meaningful where the factors actually separate; near-tie pairs instead test
    whether the metrics' indistinguishable zone is perceptually real, where the
    expected answer is "can't tell".
  * **Verdicts are recomputed from the frozen scores**, not read from a stored
    pair file, so a study scored after a re-scoring cannot silently use stale
    verdicts.

    ~/miniconda3/envs/snfeval/bin/python scripts/score_human_study.py \
        --responses human_study/responses.csv
"""

import argparse
import csv
import json
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = f"{ROOT}/manifest"

# Which factor each axis question is validated against, and whether a larger
# value means "more of the thing the rater was asked about".
AXIS_METRIC = {
    "drift": ("fBD_mean", True),        # larger fBD  -> background moves more
    "decay": ("MCFF_late_mean", False),  # smaller MCFF-L -> motion died out more
}
CLEAR_GAP = 0.20     # relative gap at or above which the factors separate
NEAR_TIE = 0.05      # relative gap below which they do not
BOOT = 10000
SEED = 0


def load_scores(track, dur):
    acc = defaultdict(dict)
    with open(f"{MAN}/per_video_scores.csv") as fh:
        for r in csv.DictReader(fh):
            if r["track"] == track and r["duration"] == dur:
                acc[(r["model"], r["prompt_id"])][r["metric"]] = float(r["value"])
    return acc


def resolve_prompt(acc, prompt):
    """Map a possibly-truncated prompt cell onto the full prompt id.

    The response export truncates the prompt to a fixed width, so an exact
    lookup misses every row. Resolve by unique prefix and refuse an ambiguous
    one rather than silently binding to the first match.
    """
    ids = {k[1] for k in acc}
    if prompt in ids:
        return prompt
    hits = [i for i in ids if i.startswith(prompt)]
    return hits[0] if len(hits) == 1 else None


def verdict(acc, metric, higher_more, a, b, prompt):
    va = acc.get((a, prompt), {}).get(metric)
    vb = acc.get((b, prompt), {}).get(metric)
    if va is None or vb is None:
        return None, None
    hi = max(abs(va), abs(vb))
    if hi <= 0:
        return None, None
    gap = abs(va - vb) / hi
    if higher_more:
        says = a if va > vb else b
    else:
        says = a if va < vb else b
    return says, gap


def majority(votes):
    """Majority label across raters; no strict majority -> 'same'."""
    tally = defaultdict(int)
    for v in votes:
        tally[v] += 1
    top = max(tally.values())
    winners = [k for k, n in tally.items() if n == top]
    return winners[0] if len(winners) == 1 else "same"


def boot_ci(flags, n=BOOT, seed=SEED):
    """Percentile CI for a proportion, resampling the pairs themselves."""
    if not flags:
        return None, None
    rng = random.Random(seed)
    k = len(flags)
    xs = sorted(sum(rng.choice(flags) for _ in range(k)) / k for _ in range(n))
    return xs[int(0.025 * n)], xs[int(0.975 * n)]


def krippendorff_nominal(units):
    """Krippendorff's alpha for nominal data over units with >=2 coders."""
    units = [u for u in units if len(u) >= 2]
    if not units:
        return None
    cats = sorted({v for u in units for v in u})
    n_total = sum(len(u) for u in units)
    Do = 0.0
    for u in units:
        m = len(u)
        disagree = sum(1 for i in range(m) for j in range(m) if i != j and u[i] != u[j])
        Do += disagree / (m - 1)
    Do /= n_total
    counts = {c: sum(u.count(c) for u in units) for c in cats}
    De = sum(counts[a] * counts[b] for a in cats for b in cats if a != b)
    De /= (n_total * (n_total - 1))
    return 1 - Do / De if De else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses", required=True,
                    help="CSV export of the study's response sheet")
    ap.add_argument("--track", default="t2v")
    ap.add_argument("--duration", default="60s")
    ap.add_argument("--out", default=f"{MAN}/human_study_scored.json")
    ap.add_argument("--exclude", default="",
                    help="comma-separated rater ids to drop (pilot or author "
                         "sessions); they are reported, never silently removed")
    args = ap.parse_args()

    acc = load_scores(args.track, args.duration)
    # Sheets exports are tab-separated as often as comma-separated, and the
    # workbook usually holds a summary tab as well as the response tab. Sniff
    # the delimiter rather than assuming, and verify the columns the join needs
    # are actually present -- a summary tab parses without error and would
    # otherwise score as "zero pairs", which reads like a null result rather
    # than the wrong file.
    raw = open(args.responses, newline="").read()
    if not raw.strip():
        print(f"{args.responses} is empty"); return 2
    delim = "\t" if raw.count("\t") > raw.count(",") else ","
    rows = list(csv.DictReader(raw.splitlines(), delimiter=delim))
    if not rows:
        print("no rows"); return 2

    REQUIRED = ("axis", "systema/systemb", "chosensystem", "prompt/scene")
    have = {k.strip().lower() for r in rows[:1] for k in r}
    ok = ("axis" in have and {"systema", "systemb"} <= have
          and ({"chosensystem", "chosen_system", "chosen"} & have))
    if not ok:
        print(f"{args.responses} does not look like the per-response export.")
        print(f"  columns found : {sorted(c for c in have if c)[:12]}")
        print(f"  columns needed: {', '.join(REQUIRED)}")
        print("  This is most likely the summary tab. Agreement needs one row "
              "per response, because each response must be joined to its own "
              "pair's metric verdict; per-axis totals cannot be un-aggregated.")
        return 2

    def col(r, *names):
        for n in names:
            for k in r:
                if k.strip().lower() == n:
                    return r[k].strip()
        return ""

    # Sentinel failures exclude a rater before anything is aggregated.
    failed = defaultdict(int)
    for r in rows:
        if col(r, "sentinel").upper() in ("TRUE", "1", "YES") and \
           col(r, "failedsentinel").upper() in ("TRUE", "1", "YES"):
            failed[col(r, "raterid", "rater_id", "rater")] += 1
    excluded = {k for k, n in failed.items() if n > 1}
    dropped = {r.strip() for r in args.exclude.split(",") if r.strip()}
    excluded |= dropped

    per_pair = defaultdict(list)
    prompts, unresolved = {}, set()
    for r in rows:
        rater = col(r, "raterid", "rater_id", "rater")
        if rater in excluded:
            continue
        if col(r, "sentinel").upper() in ("TRUE", "1", "YES"):
            continue
        axis = col(r, "axis")
        a, b = col(r, "systema", "systemA"), col(r, "systemb", "systemB")
        prompt = col(r, "prompt", "prompt_id", "scene")
        chosen = col(r, "chosensystem", "chosen_system", "chosen")
        if not (axis in AXIS_METRIC and a and b and chosen):
            continue
        full = resolve_prompt(acc, prompt)
        if full is None:
            unresolved.add(prompt)
            continue
        key = (axis, full, tuple(sorted((a, b))))
        per_pair[key].append(chosen)
        # the resolved id, not the truncated cell: the verdict lookup keys on it
        prompts[key] = full

    if unresolved:
        print(f"WARNING: {len(unresolved)} prompt(s) did not resolve to a scored "
              f"item; those responses are dropped")
    report = {"track": args.track, "duration": args.duration,
              "excluded_raters": sorted(excluded),
              "excluded_by_request": sorted(dropped),
              "n_raters": len({col(r, "raterid", "rater_id", "rater") for r in rows}),
              "axes": {}}
    print(f"raters: {report['n_raters']}   excluded for sentinels: "
          f"{sorted(excluded) or 'none'}")

    for axis, (metric, higher) in AXIS_METRIC.items():
        metric_says, gaps, human, votes = {}, {}, {}, {}
        for key, vs in per_pair.items():
            if key[0] != axis:
                continue
            a, b = key[2]
            says, gap = verdict(acc, metric, higher, a, b, prompts[key])
            if says is None:
                continue
            metric_says[key], gaps[key] = says, gap
            human[key] = majority(vs)
            votes[key] = vs

        clear = [k for k in gaps if gaps[k] >= CLEAR_GAP]
        tie = [k for k in gaps if gaps[k] < NEAR_TIE]
        agree = [1 if human[k] == metric_says[k] else 0 for k in clear
                 if human[k] != "same"]
        undecided = sum(1 for k in clear if human[k] == "same")
        lo, hi = boot_ci(agree)
        alpha = krippendorff_nominal([votes[k] for k in gaps])
        tie_ok = sum(1 for k in tie if human[k] == "same")

        report["axes"][axis] = {
            "metric": metric, "n_pairs": len(gaps),
            "n_clear_gap": len(clear), "n_decided_clear": len(agree),
            "agreement": (sum(agree) / len(agree)) if agree else None,
            "ci95": [lo, hi], "undecided_on_clear": undecided,
            "n_near_tie": len(tie), "cant_tell_on_near_tie": tie_ok,
            "krippendorff_alpha": alpha,
        }
        a_txt = (f"{sum(agree)}/{len(agree)} = {sum(agree)/len(agree):.0%}"
                 if agree else "n/a")
        ci_txt = f" [{lo:.0%}, {hi:.0%}]" if lo is not None else ""
        print(f"\n{axis} (vs {metric})")
        print(f"  pairs: {len(gaps)}  clear-gap: {len(clear)}  near-tie: {len(tie)}")
        print(f"  agreement on clear-gap, decided pairs: {a_txt}{ci_txt}")
        print(f"  'can't tell' on clear-gap pairs: {undecided}")
        print(f"  'can't tell' on near-tie pairs:  {tie_ok}/{len(tie)}")
        print(f"  inter-rater alpha: "
              f"{alpha:.2f}" if alpha is not None else "  inter-rater alpha: n/a")

    json.dump(report, open(args.out, "w"), indent=2)
    print(f"\n-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

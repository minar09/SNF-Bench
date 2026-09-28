#!/usr/bin/env python3
"""Paired prompt-level resolution audit for NBF and VBench background consistency.

This is descriptive: a bootstrap interval excluding zero is evidence of stable
ordering for these seven systems, not proof of human validity or family-wise
significance across 21 comparisons. Prompt categories are sampled separately
and equally weighted so the 14 channel-water prompts cannot dominate.

    python scripts/paired_incumbent_resolution.py
"""

import csv
import itertools
import json
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

from registry import ALL

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manifest"
METRICS = ("NBF_mean", "background_consistency")


def load_inputs():
    public = {m["key"] for m in ALL if m["track"] == "t2v" and m["status"] == "public"}
    cats = {(r["track"], r["duration"], r["prompt_id"]): r["category"]
            for r in csv.DictReader((MAN / "prompt_categories.csv").open())}
    acc = defaultdict(list)
    for r in csv.DictReader((MAN / "per_video_scores.csv").open()):
        if r["track"] == "t2v" and r["duration"] == "60s" and r["model"] in public \
                and r["metric"] in METRICS:
            acc[(r["metric"], r["model"], r["prompt_id"])].append(float(r["value"]))
    scores = {(metric, model, prompt): st.mean(values)
              for (metric, model, prompt), values in acc.items()}
    return sorted(public), cats, scores


def paired_category_bootstrap(differences, n=5000, seed=0):
    """differences: category -> paired per-prompt A-B values."""
    groups = [list(v) for _, v in sorted(differences.items()) if v]
    if not groups:
        raise ValueError("no paired prompts")
    point = st.mean(st.mean(g) for g in groups)
    rng = random.Random(seed)
    draws = []
    for _ in range(n):
        draws.append(st.mean(st.mean(g[rng.randrange(len(g))] for _ in g)
                             for g in groups))
    draws.sort()
    lo = draws[int(0.025 * n)]
    hi = draws[min(n - 1, int(0.975 * n))]
    if point > 0:
        order_probability = sum(v > 0 for v in draws) / n
    elif point < 0:
        order_probability = sum(v < 0 for v in draws) / n
    else:
        order_probability = None  # no observed ordering to confirm
    return {"difference": point, "ci95": [lo, hi],
            "order_probability": order_probability,
            "ci_excludes_zero": bool(lo > 0 or hi < 0),
            "n_prompts": sum(len(g) for g in groups), "n_categories": len(groups)}


def analyze(models, cats, scores, n=5000):
    output = {}
    for metric in METRICS:
        pairs = {}
        for left, right in itertools.combinations(models, 2):
            prompts = sorted({p for m, a, p in scores if m == metric and a == left}
                             & {p for m, a, p in scores if m == metric and a == right})
            grouped = defaultdict(list)
            for prompt in prompts:
                cat = cats.get(("t2v", "60s", prompt))
                if cat and cat != "unassigned":
                    grouped[cat].append(scores[(metric, left, prompt)]
                                        - scores[(metric, right, prompt)])
            if grouped:
                pairs[f"{left}|{right}"] = paired_category_bootstrap(grouped, n=n)
        output[metric] = {"pairs": pairs,
                          "n_pairs": len(pairs),
                          "n_ci_excludes_zero": sum(p["ci_excludes_zero"] for p in pairs.values())}
    return output


def main():
    models, cats, scores = load_inputs()
    result = {"track": "t2v", "duration": "60s", "models": models,
              "method": "paired prompt differences; category-macro bootstrap within category; 5000 draws; seed 0",
              "interpretation": "descriptive intervals; not multiple-comparison corrected or human validity",
              "metrics": analyze(models, cats, scores)}
    path = MAN / "paired_incumbent_resolution.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    for metric, record in result["metrics"].items():
        print(f"{metric}: {record['n_ci_excludes_zero']}/{record['n_pairs']} pairwise intervals exclude zero")
    print(path)


if __name__ == "__main__":
    main()

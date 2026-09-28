#!/usr/bin/env python3
"""Build the consolidated SNF v2 perturbation-response audit.

This analysis leaves the frozen score records untouched. It fixes two endpoint
errors in the earlier exploratory summary:

* a 6-frame repetition is more severe than a 24-frame repetition;
* mask erosion and dilation are each compared with radius 0, never with each
  other.

Outputs contain exact paired effects, hierarchical category/clip bootstrap
intervals, within-clip monotonicity, response and desirability signs, and an
explicit selectivity screen. The screen is mechanistic evidence only; it does
not establish agreement with human judgments.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import statistics as st
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest"

METRICS = ("fBD", "NBF", "MCFF_L", "FP", "DLR", "DAR", "VB_DD")
METRIC_LABEL = {
    "fBD": "fBD",
    "NBF": "NBF",
    "MCFF_L": "MCFF-L",
    "FP": "FP",
    "DLR": "DLR",
    "DAR": "DAR",
    "VB_DD": "VBench DD",
}

# Endpoint choices are semantic, rather than numeric max(). Repetition severity
# grows as the cycle gets shorter. Mask sensitivity is two-sided.
INTERVENTIONS = {
    "translation": {"family": "translation", "baseline": 0.0, "endpoint": 80.0,
                    "task": "penalty"},
    "rotation": {"family": "rotation", "baseline": 0.0, "endpoint": 80.0,
                 "task": "penalty"},
    "scale": {"family": "scale", "baseline": 0.0, "endpoint": 80.0,
              "task": "penalty"},
    "freeze": {"family": "freeze", "baseline": 0.0, "endpoint": 0.75,
               "task": "penalty"},
    "attenuation": {"family": "attenuation", "baseline": 0.0, "endpoint": 1.0,
                    "task": "penalty"},
    "repetition": {"family": "repetition", "baseline": 0.0, "endpoint": 6.0,
                   "task": "penalty", "severity_order": [0.0, 24.0, 12.0, 6.0]},
    "photometric": {"family": "photometric", "baseline": 0.0, "endpoint": 0.35,
                    "task": "nuisance"},
    "mask_erode": {"family": "mask_radius", "baseline": 0.0, "endpoint": -4.0,
                   "task": "nuisance", "severity_order": [0.0, -2.0, -4.0]},
    "mask_dilate": {"family": "mask_radius", "baseline": 0.0, "endpoint": 4.0,
                    "task": "nuisance", "severity_order": [0.0, 2.0, 4.0]},
}

# Predeclared mechanistic expectations from SNF_V2_VALIDATION_MATRIX.md and
# METRIC_SPEC_v1.1.md. "0" means target invariance or a documented capability
# gap, not proof that the metric is valid when it stays flat.
EXPECTED = defaultdict(lambda: "0")
for family in ("translation", "rotation", "scale"):
    for metric in ("fBD", "NBF", "DLR", "DAR", "VB_DD"):
        EXPECTED[(family, metric)] = "+"
for family in ("freeze", "attenuation"):
    for metric in ("MCFF_L", "FP", "VB_DD"):
        EXPECTED[(family, metric)] = "-"
    EXPECTED[(family, "DLR")] = "+"  # documented denominator confound

# On-target families used by the selectivity screen. Attenuation and freeze are
# both stated tests for persistence in the v2 validation matrix.
TARGETS = {
    "fBD": ("translation", "rotation", "scale"),
    "NBF": ("translation", "rotation", "scale"),
    "MCFF_L": ("freeze", "attenuation"),
    "FP": ("freeze", "attenuation"),
    "DLR": ("translation", "rotation", "scale"),
    "DAR": ("translation", "rotation", "scale"),
}
OFF_TARGET = ("photometric", "mask_erode", "mask_dilate")


def percentile(values, q):
    """Linear percentile without a NumPy dependency."""
    values = sorted(v for v in values if math.isfinite(v))
    if not values:
        return None
    pos = (len(values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - pos) + values[hi] * (pos - lo)


def average_ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + end - 1) / 2.0
        for idx in order[start:end]:
            ranks[idx] = rank
        start = end
    return ranks


def spearman(x, y):
    if len(x) < 3 or len(x) != len(y):
        return None
    a, b = average_ranks(x), average_ranks(y)
    ma, mb = st.mean(a), st.mean(b)
    num = sum((u - ma) * (v - mb) for u, v in zip(a, b))
    den = math.sqrt(sum((u - ma) ** 2 for u in a) *
                    sum((v - mb) ** 2 for v in b))
    return num / den if den else None


def paired_dz(values):
    """Paired standardized mean change using the sample SD of differences."""
    if len(values) < 2:
        return None
    spread = st.stdev(values)
    if spread == 0:
        return None
    return st.mean(values) / spread


def category_bootstrap(grouped, draws=10_000, seed=0):
    """Hierarchical category then clip bootstrap for paired changes.

    The point estimate is category-macro. The d_z point estimate remains the
    conventional clip-level paired effect; its interval resamples categories
    and clips so large media groups do not dominate uncertainty.
    """
    groups = {k: list(v) for k, v in grouped.items() if v}
    categories = sorted(groups)
    flat = [v for category in categories for v in groups[category]]
    if not categories or not flat:
        return None
    macro = st.mean(st.mean(groups[c]) for c in categories)
    rng = random.Random(seed)
    means, effects = [], []
    for _ in range(draws):
        sampled_categories = [rng.choice(categories) for _ in categories]
        sampled_groups, sampled_flat = [], []
        for category in sampled_categories:
            source = groups[category]
            sample = [rng.choice(source) for _ in source]
            sampled_groups.append(st.mean(sample))
            sampled_flat.extend(sample)
        means.append(st.mean(sampled_groups))
        effect = paired_dz(sampled_flat)
        if effect is not None and math.isfinite(effect):
            effects.append(effect)
    mean_ci = [percentile(means, 0.025), percentile(means, 0.975)]
    dz = paired_dz(flat)
    dz_ci = [percentile(effects, 0.025), percentile(effects, 0.975)]
    return {
        "n_clips": len(flat),
        "n_categories": len(categories),
        "category_macro_delta": macro,
        "delta_ci95": mean_ci,
        "delta_ci_excludes_zero": mean_ci[0] > 0 or mean_ci[1] < 0,
        "paired_dz": dz,
        "paired_dz_ci95": dz_ci,
    }


def prompt_id(clip):
    return re.sub(r"-\d+-\d+\.\d+\.mp4$", "", clip)


def load_categories(path=MANIFEST / "prompt_categories.csv"):
    return {row["prompt_id"]: row["category"] for row in csv.DictReader(path.open())
            if row["track"] == "t2v" and row["duration"] == "60s"}


def load_records(paths=None):
    paths = paths or [MANIFEST / f"validation_response_{name}.json"
                      for name in ("geom", "motion", "ctrl")]
    records = []
    for path in paths:
        records.extend(json.loads(Path(path).read_text())["records"])
    return records


def response_sign(summary):
    if not summary["delta_ci_excludes_zero"]:
        return "?"
    return "+" if summary["category_macro_delta"] > 0 else "-"


def desirability(intervention, metric, observed):
    task = INTERVENTIONS[intervention]["task"]
    if task == "nuisance":
        return "stable" if observed in ("0", "?") else "nuisance-sensitive"
    if intervention == "repetition":
        return "capability-gap" if observed in ("0", "?") else "unvalidated-response"
    if metric == "VB_DD" and intervention in ("translation", "rotation", "scale"):
        return "rewards-corruption" if observed == "+" else "uncertain"
    expected = EXPECTED[(intervention, metric)]
    if expected == "0":
        return "context-only"
    return "aligned" if observed == expected else "uncertain-or-wrong"


def analyze(records, categories, draws=10_000, seed=0):
    by_family_clip = defaultdict(dict)
    for row in records:
        key = (row["family"], row["clip"])
        level = float(row["level"])
        if level in by_family_clip[key]:
            raise ValueError(f"duplicate record for {key} level {level}")
        by_family_clip[key][level] = row

    rows = []
    for intervention, spec in INTERVENTIONS.items():
        family = spec["family"]
        eligible = {clip: levels for (fam, clip), levels in by_family_clip.items()
                    if fam == family}
        for metric in METRICS:
            grouped = defaultdict(list)
            correlations = []
            missing = []
            for clip, levels in sorted(eligible.items()):
                baseline, endpoint = spec["baseline"], spec["endpoint"]
                if baseline not in levels or endpoint not in levels:
                    missing.append(clip)
                    continue
                before = levels[baseline].get(metric)
                after = levels[endpoint].get(metric)
                category = categories.get(prompt_id(clip))
                if before is None or after is None or category is None:
                    missing.append(clip)
                    continue
                grouped[category].append(float(after) - float(before))

                order = spec.get("severity_order", sorted(levels))
                values = [levels[level].get(metric) for level in order if level in levels]
                if len(values) == len(order) and all(v is not None for v in values):
                    rho = spearman(list(range(len(order))), [float(v) for v in values])
                    if rho is not None:
                        correlations.append(rho)
            summary = category_bootstrap(grouped, draws=draws,
                                         seed=seed + len(rows) * 997)
            if summary is None:
                continue
            observed = response_sign(summary)
            expected = EXPECTED[(intervention, metric)]
            summary.update({
                "intervention": intervention,
                "source_family": family,
                "baseline_level": spec["baseline"],
                "endpoint_level": spec["endpoint"],
                "metric": metric,
                "expected_response": expected,
                "observed_response": observed,
                "expectation_met": observed == expected if expected != "0" else observed in ("?", "0"),
                "task_judgment": spec["task"],
                "desirability_interpretation": desirability(intervention, metric, observed),
                "median_within_clip_spearman": st.median(correlations) if correlations else None,
                "n_monotonicity_clips": len(correlations),
                "missing_clips": missing,
            })
            rows.append(summary)

    lookup = {(row["intervention"], row["metric"]): row for row in rows}
    selectivity = {}
    for metric, targets in TARGETS.items():
        on = [(name, abs(lookup[(name, metric)]["paired_dz"])) for name in targets
              if lookup.get((name, metric), {}).get("paired_dz") is not None]
        off = [(name, abs(lookup[(name, metric)]["paired_dz"])) for name in OFF_TARGET
               if lookup.get((name, metric), {}).get("paired_dz") is not None]
        if not on or not off:
            continue
        weakest = min(on, key=lambda item: item[1])
        strongest = max(off, key=lambda item: item[1])
        ratio = weakest[1] / strongest[1] if strongest[1] else None
        selectivity[metric] = {
            "target_families": list(targets),
            "weakest_on_target": {"intervention": weakest[0], "abs_paired_dz": weakest[1]},
            "strongest_off_target": {"intervention": strongest[0], "abs_paired_dz": strongest[1]},
            "ratio": ratio,
            "passes_minimal_separation": bool(ratio is not None and ratio > 1.0),
            "passes_twofold_admission_bar": bool(ratio is not None and ratio >= 2.0),
        }

    decisions = {
        "fBD": "retain as a spatial-drift diagnostic; it clears minimal nuisance separation, while feature-match coverage and a second backbone remain pending",
        "NBF": "scope-to-translation-and-scale; rotation response is weaker than partition sensitivity",
        "DAR": "supplementary-diagnostic; fails off-target selectivity",
        "DLR": "supplementary-diagnostic; fails off-target selectivity and freeze/attenuation are confounds",
        "MCFF_L": "motion-magnitude diagnostic; responds to freezing but fails the current attenuation-versus-nuisance selectivity screen",
        "FP": "decay-indicator only; must be reported with MCFF magnitudes and fails the current attenuation-versus-nuisance selectivity screen",
        "drift_leakage_axis": "remove from the headline set under the frozen rule because both DLR and DAR fail selectivity",
        "repetition": "existing factors do not constitute a replay/naturalness test",
    }
    return {"schema_version": 1,
            "analysis": "paired category-aware perturbation response audit",
            "effect_size": "paired d_z uses sample SD of per-clip differences",
            "bootstrap": {"method": "hierarchical category then clip", "draws": draws, "seed": seed},
            "endpoint_corrections": {"repetition": "0 to 6 frames, ordered 0/24/12/6",
                                     "mask_radius": "0 to -4 and 0 to +4 reported separately"},
            "rows": rows, "selectivity": selectivity, "scope_decisions": decisions}


def fmt(value, digits=2):
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


def render_markdown(result):
    lines = [
        "# Perturbation response and desirability audit",
        "",
        "Generated by `scripts/validation_response_analysis.py` from the frozen",
        "geometry, motion, and nuisance sweeps. Effects are paired within clip;",
        "uncertainty resamples scene category and clips. This is mechanistic",
        "validation, not human-alignment evidence.",
        "",
        "`+` and `−` describe the measured response as severity increases. `?`",
        "means the category-aware 95% interval includes zero. Response direction",
        "and whether that direction is desirable are separate columns.",
        "",
        "| Intervention | Metric | Expected | Observed | paired d_z | 95% CI | Median rho | Desirability | n |",
        "|---|---|:---:|:---:|---:|---:|---:|---|---:|",
    ]
    for row in result["rows"]:
        ci = row["paired_dz_ci95"]
        lines.append("| {intervention} | {metric} | {expected} | {observed} | {dz} | [{lo}, {hi}] | {rho} | {desirability} | {n} |".format(
            intervention=row["intervention"], metric=METRIC_LABEL[row["metric"]],
            expected={"+": "↑", "-": "↓", "0": "≈"}[row["expected_response"]],
            observed={"+": "↑", "-": "↓", "?": "?", "0": "≈"}[row["observed_response"]],
            dz=fmt(row["paired_dz"]), lo=fmt(ci[0]), hi=fmt(ci[1]),
            rho=fmt(row["median_within_clip_spearman"]),
            desirability=row["desirability_interpretation"], n=row["n_clips"]))

    lines += ["", "## Selectivity screen", "",
              "The ratio is the weakest on-target |d_z| divided by the strongest",
              "photometric or mask-boundary |d_z|. Ratios above 1 clear only the",
              "minimal separation check; the frozen DLR/DAR admission rule requires 2.", "",
              "| Metric | Weakest target | Strongest nuisance | Ratio | >1 | ≥2 |",
              "|---|---:|---:|---:|:---:|:---:|"]
    for metric, item in result["selectivity"].items():
        on, off = item["weakest_on_target"], item["strongest_off_target"]
        lines.append(f"| {METRIC_LABEL[metric]} | {on['intervention']} {on['abs_paired_dz']:.2f} | "
                     f"{off['intervention']} {off['abs_paired_dz']:.2f} | {item['ratio']:.2f} | "
                     f"{'yes' if item['passes_minimal_separation'] else 'no'} | "
                     f"{'yes' if item['passes_twofold_admission_bar'] else 'no'} |")

    lines += ["", "## Current scope decisions", ""]
    for metric, decision in result["scope_decisions"].items():
        lines.append(f"- **{metric}:** {decision}.")
    lines += ["", "## Endpoint correction", "",
              "The earlier exploratory `incumbent_analysis.json` sorted numeric levels.",
              "That made 24 frames the repetition endpoint and compared mask radius −4",
              "directly with +4. This audit uses the task-defined 6-frame repetition",
              "endpoint and reports erosion and dilation against radius 0 separately.",
              "It also uses the sample SD for paired d_z. Therefore its effect sizes",
              "supersede the old exploratory response/selectivity block; the incumbent",
              "method-level agreement analysis remains unaffected.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path,
                        default=MANIFEST / "validation_response_analysis.json")
    parser.add_argument("--table", type=Path,
                        default=ROOT / "tables" / "validation_response_matrix.md")
    args = parser.parse_args()
    result = analyze(load_records(), load_categories(), args.draws, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.table.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    args.table.write_text(render_markdown(result))
    print(f"{len(result['rows'])} response rows -> {args.out}")
    print(f"{len(result['selectivity'])} selectivity decisions -> {args.table}")


if __name__ == "__main__":
    main()

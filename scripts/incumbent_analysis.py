"""Answer the three reviewer objections that can be settled from frozen scores.

Every WACV reviewer raised the same three, and none needs new generation:

  1. **The incumbent was never scored.** VBench background consistency is the
     direct incumbent measure of the failure fBD/NBF target, and the paper
     compared only against Dynamic Degree. It is already in the manifest.
  2. **The sensitivity comparison was not scale-free.** Reporting that fBD
     reaches 3.2x baseline while Dynamic Degree reaches 1.1x compares raw
     multipliers on quantities with very different dispersions. Perturbations
     are injected into the *same* clip, so the correct statistic is a paired
     effect size.
  3. **Selectivity was reported on two off-target families only.** The full
     family x factor matrix is the actual deliverable of a mechanistic
     validation.

Run: ~/miniconda3/envs/snfeval/bin/python scripts/incumbent_analysis.py
"""

import csv
import json
import math
import os
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registry import ALL                                        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = f"{ROOT}/manifest"

VB = ["background_consistency", "motion_smoothness", "temporal_flickering",
      "dynamic_degree"]
SNF = ["NBF_mean", "fBD_mean", "MCFF_late_mean", "FP_mean"]
METS = ["fBD", "NBF", "MCFF_L", "FP", "DLR", "DAR", "VB_DD"]
FAMS = ["translation", "rotation", "scale", "freeze", "attenuation",
        "repetition", "photometric", "mask_radius"]
# Which families each factor's definition says it should detect.
TARGET = {"fBD": ["translation", "rotation", "scale"],
          "NBF": ["translation", "rotation", "scale"],
          "MCFF_L": ["freeze"], "FP": ["freeze"],
          "DLR": ["translation"], "DAR": ["translation", "rotation"],
          "VB_DD": []}
OFF = ["photometric", "mask_radius"]


def spearman(x, y):
    n = len(x)
    if n < 3:
        return None
    a, b = [0] * n, [0] * n
    for r, i in enumerate(sorted(range(n), key=lambda i: x[i])):
        a[i] = r
    for r, i in enumerate(sorted(range(n), key=lambda i: y[i])):
        b[i] = r
    mx, my = sum(a) / n, sum(b) / n
    num = sum((a[i] - mx) * (b[i] - my) for i in range(n))
    den = math.sqrt(sum((a[i] - mx) ** 2 for i in range(n))
                    * sum((b[i] - my) ** 2 for i in range(n)))
    return num / den if den else None


def load_audit(track="t2v", dur="60s"):
    names = {m["key"]: m["name"] for m in ALL
             if m["track"] == track and m["status"] == "public"}
    per = defaultdict(list)
    with open(f"{MAN}/per_video_scores.csv") as fh:
        for r in csv.DictReader(fh):
            if r["track"] == track and r["duration"] == dur and r["model"] in names:
                per[(r["model"], r["metric"])].append(float(r["value"]))
    return names, per


def incumbent_block(names, per):
    """Does the incumbent already measure this, and can it resolve systems?"""
    ks = [k for k in sorted(names) if (k, "NBF_mean") in per]
    mean = lambda k, m: st.mean(per[(k, m)]) if per.get((k, m)) else None
    out = {"n_systems": len(ks), "agreement": {}, "discriminability": {}}
    for v in VB:
        for s in SNF:
            xs = [mean(k, v) for k in ks]
            ys = [mean(k, s) for k in ks]
            if all(x is not None for x in xs) and all(y is not None for y in ys):
                out["agreement"][f"{v}|{s}"] = round(spearman(xs, ys), 3)
    # Ranking similarly is not the same as resolving: a metric whose between-
    # system range is small next to its within-system scatter cannot support
    # per-system claims however well it correlates in aggregate.
    for m in VB + SNF:
        mus = [mean(k, m) for k in ks if per.get((k, m))]
        sds = [st.pstdev(per[(k, m)]) for k in ks
               if per.get((k, m)) and len(per[(k, m)]) > 1]
        if not mus or not sds:
            continue
        rng, wsd = max(mus) - min(mus), st.mean(sds)
        out["discriminability"][m] = {
            "between_system_range": round(rng, 4),
            "mean_within_system_sd": round(wsd, 4),
            "ratio": round(rng / wsd, 2) if wsd else None}
    return out


def validation_records():
    recs = []
    for f in ("geom", "motion", "ctrl"):
        p = f"{MAN}/validation_response_{f}.json"
        if os.path.exists(p):
            recs += json.load(open(p))["records"]
    return recs


def paired_matrix(recs):
    """Paired effect size d_z per (family, factor) at maximum severity.

    The perturbation is applied to the same clip, so the null is that clip's own
    unperturbed value. Normalising by between-clip spread instead would
    understate every factor by folding in scene variability.
    """
    idx = defaultdict(dict)
    for r in recs:
        idx[(r["family"], r["clip"])][r["level"]] = r
    mat = {}
    for fam in FAMS:
        for m in METS:
            d = []
            for (f, _), lv in idx.items():
                if f != fam:
                    continue
                ls = sorted(lv)
                if len(ls) < 2:
                    continue
                a, b = lv[ls[0]].get(m), lv[ls[-1]].get(m)
                if a is not None and b is not None:
                    d.append(b - a)
            if len(d) < 3:
                mat[(fam, m)] = None
                continue
            s = st.pstdev(d)
            mat[(fam, m)] = round(st.mean(d) / s, 3) if s else None
    return mat


def main():
    names, per = load_audit()
    inc = incumbent_block(names, per)
    recs = validation_records()
    mat = paired_matrix(recs)

    print("=== 1. incumbent agreement (method-level Spearman) ===")
    for k, v in sorted(inc["agreement"].items()):
        if k.startswith(("background_consistency", "dynamic_degree")):
            print(f"   {k:44s} {v:+.3f}")
    print("\n=== 2. discriminability (between-system range / within-system SD) ===")
    for m, d in sorted(inc["discriminability"].items(),
                       key=lambda kv: -(kv[1]["ratio"] or 0)):
        print(f"   {m:24s} ratio {d['ratio']:5.2f}"
              f"   (range {d['between_system_range']}, sd {d['mean_within_system_sd']})")
    print("\n=== 3. paired effect size d_z at max severity ===")
    print(f"   {'family':13s}" + "".join(f"{m:>9s}" for m in METS))
    for fam in FAMS:
        row = f"   {fam:11s}"
        for m in METS:
            v = mat.get((fam, m))
            row += f"{v:9.2f}" if v is not None else f"{'--':>9s}"
        print(row)
    print("\n=== 4. selectivity: weakest on-target vs strongest off-target ===")
    sel = {}
    for m in METS:
        on = [abs(mat[(f, m)]) for f in TARGET[m] if mat.get((f, m)) is not None]
        off = [abs(mat[(f, m)]) for f in OFF if mat.get((f, m)) is not None]
        if not off:
            continue
        if on:
            ratio = min(on) / max(off) if max(off) else None
            sel[m] = {"on_target_min": round(min(on), 3),
                      "off_target_max": round(max(off), 3),
                      "ratio": round(ratio, 3) if ratio else None,
                      "passes": bool(ratio and ratio > 1.0)}
            flag = "" if sel[m]["passes"] else "   <-- FAILS: off-target exceeds on-target"
            print(f"   {m:7s} on {min(on):5.2f}  off {max(off):5.2f}  "
                  f"ratio {ratio:5.2f}{flag}")
        else:
            print(f"   {m:7s} comparison row, off {max(off):5.2f}")

    json.dump({"incumbent": inc,
               "paired_dz": {f"{f}|{m}": v for (f, m), v in mat.items()},
               "selectivity": sel},
              open(f"{MAN}/incumbent_analysis.json", "w"), indent=2)
    print(f"\n-> {MAN}/incumbent_analysis.json")


if __name__ == "__main__":
    main()

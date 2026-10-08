#!/usr/bin/env python3
"""Assign v2 I2V pairs to splits and preselect the 240 s stress subset.

Inputs are the overlap audit (`manifest/v2_split_audit.json`), nothing else --
in particular no metric value, no rendered video and no method output. That is
the point: the reviewer's request is that the test split and the stress subset
be fixed *before* any outcome is seen, so the selection here is a function of
provenance and a seed only.

Splits
  test          sources no development, validation or training pool contains
  seen_overlap  sources the method project has already worked on (the 7 reused
                v1 evaluation images). Not test. Reported separately, never
                pooled into a test claim.

Stress subset (240 s)
  One test pair per transport regime, chosen by a seeded hash of the id rather
  than by inspection, so the subset is preselected and cannot drift towards
  scenes a method happens to handle well.

    python scripts/assign_v2_splits.py            # write manifest/v2_splits.json
    python scripts/assign_v2_splits.py --check    # fail if the file disagrees
"""

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "manifest", "v2_split_audit.json")
OUT = os.path.join(ROOT, "manifest", "v2_splits.json")
SEED = "snf-bench-v2-stress-2026-10-02"
HORIZONS = {"principal": ["60s", "120s"], "stress": ["240s"]}


def rank(pid):
    return hashlib.sha256(f"{SEED}:{pid}".encode()).hexdigest()


def build():
    audit = json.load(open(AUDIT))
    test = sorted(r["id"] for r in audit["rows"] if r["verdict"] == "unseen")
    seen = sorted(r["id"] for r in audit["rows"] if r["verdict"] == "seen")
    cat = {r["id"]: r["category"] for r in audit["rows"]}

    by_cat = defaultdict(list)
    for pid in test:
        by_cat[cat[pid]].append(pid)
    stress = sorted(min(ids, key=rank) for ids in by_cat.values())

    per_cat = {c: {"test": len(by_cat[c]),
                   "seen_overlap": sum(1 for p in seen if cat[p] == c)}
               for c in sorted(set(cat.values()))}
    return {
        "role": "split assignment for SNF-Bench v2 I2V; inputs are provenance only",
        "audit": os.path.relpath(AUDIT, ROOT),
        "audit_sha256": hashlib.sha256(open(AUDIT, "rb").read()).hexdigest(),
        "seed": SEED,
        "horizons": HORIZONS,
        "test": test,
        "seen_overlap": seen,
        "stress_240s": stress,
        "per_category": per_cat,
        "notes": [
            "seen_overlap = reused v1 evaluation images; v1 was the method "
            "project's development set. Report separately; never pool into test.",
            "stress_240s: one test pair per transport regime, chosen by seeded "
            "hash, before any rendering or scoring of v2.",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    want = build()
    if a.check:
        have = json.load(open(OUT)) if os.path.exists(OUT) else None
        if have != want:
            print("STALE: manifest/v2_splits.json differs from the audit-derived assignment")
            return 1
        print(f"v2 splits current: test {len(want['test'])}, "
              f"seen_overlap {len(want['seen_overlap'])}, stress {len(want['stress_240s'])}")
        return 0
    json.dump(want, open(OUT, "w"), indent=1)
    print(f"test {len(want['test'])}   seen_overlap {len(want['seen_overlap'])}   "
          f"stress_240s {len(want['stress_240s'])}")
    print(f"{'category':<20}{'test':>5}{'seen':>6}   stress")
    cat = {r["id"]: r["category"] for r in json.load(open(AUDIT))["rows"]}
    for c, n in want["per_category"].items():
        pick = [p for p in want["stress_240s"] if cat[p] == c]
        print(f"{c:<20}{n['test']:>5}{n['seen_overlap']:>6}   {', '.join(pick)}")
    print("stress:", ", ".join(want["stress_240s"]))
    print(f"-> {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

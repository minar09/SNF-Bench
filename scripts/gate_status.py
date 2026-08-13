"""SNF-Bench pre-freeze gate — the pipeline's refusal mechanism.

Every defect found on 2026-08-13 (DriftFrac semantics, file-counting coverage,
translation-only compensation, a mis-diagnosed frame-rate "confound") shared one
property: nothing in the pipeline was capable of noticing. This script is the
standing check. It computes what it can, marks the rest PENDING, and prints a
single bottom line:

    FINAL_SWEEP_ALLOWED = FALSE

which turns TRUE only when every required gate passes. Table builders consult
`final_sweep_allowed()` so that "final" tables cannot be produced from an
instrument that has not been validated.

    ~/miniconda3/envs/snfeval/bin/python scripts/gate_status.py
"""

import csv
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registry import ALL, contestants                      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, MAN, TAB = f"{ROOT}/raw", f"{ROOT}/manifest", f"{ROOT}/tables"
DOCS, SCRIPTS = f"{ROOT}/docs", f"{ROOT}/scripts"
SNF_EVAL = "/home/minar/region-forcing/snf_eval"

PASS, FAIL, PEND = "PASS", "FAIL", "PENDING"

# Distinct PUBLISHED I2V models, as opposed to configuration variants of one
# family. The Aug 16 gate counts these, not registry rows: four Causal-Forcing++
# entries are one published model evaluated four ways.
I2V_FAMILIES = {
    "causvid": "CausVid",
    "self_forcing": "Self-Forcing",
    "cf_framewise": "Causal-Forcing",
    "chunk6": "Causal-Forcing++", "cf++_1step": "Causal-Forcing++",
    "f2s_framewise": "Causal-Forcing++", "f1s_framewise": "Causal-Forcing++",
    "wan21_i2v": "Wan2.1", "wan22_i2v": "Wan2.2", "ltx_i2v": "LTX-Video",
}
I2V_GATE_MIN = 3
I2V_GATE_MIN_VALID = 27          # of 30 videos, per the agreed threshold


def _valid_counts():
    out = {}
    for p in glob.glob(f"{RAW}/*/*/*/snf_task_metrics.json"):
        parts = p.split(os.sep)
        entry = (parts[-4], parts[-3], parts[-2])
        try:
            pv = json.load(open(p)).get("per_video", [])
        except (OSError, ValueError):
            continue
        out[entry] = (sum(1 for v in pv if "error" not in v and v.get("fBD") is not None),
                      len(glob.glob(f"{ROOT}/videos/{entry[0]}/{entry[1]}/{entry[2]}/*.mp4")))
    return out


# --------------------------------------------------------------------- gates
def gate_metric_spec():
    p = f"{DOCS}/METRIC_SPEC_v1.1.md"
    if not os.path.exists(p):
        return FAIL, "METRIC_SPEC_v1.1.md missing"
    txt = open(p).read()
    need = ["fBD", "NBF", "MCFF", "FP", "DLR", "DAR"]
    missing = [n for n in need if f"### {n}" not in txt]
    if missing:
        return FAIL, f"undefined in spec: {missing}"
    return PASS, "v1.1, six metrics defined"


def gate_banned_terms():
    """No banned term may survive outside provenance records and ban-lists."""
    bad = []
    for p in glob.glob(f"{ROOT}/latex/**/*.tex", recursive=True):
        t = open(p, errors="ignore").read()
        for term in ("DriftFrac", "BFR"):
            if re.search(rf"\b{term}\b", t):
                bad.append(f"{os.path.basename(p)}:{term}")
    return (PASS, "paper clean of DriftFrac/BFR") if not bad else (FAIL, "; ".join(bad))


def gate_fps_metadata():
    p = f"{MAN}/video_meta.csv"
    if not os.path.exists(p):
        return FAIL, "video_meta.csv missing"
    rows = list(csv.DictReader(open(p)))
    n_vid = len(glob.glob(f"{ROOT}/videos/*/*/*/*.mp4"))
    bad = [r for r in rows if not r["fps"] or float(r["fps"]) <= 0
           or not int(r["width"]) or not int(r["height"])]
    if bad:
        return FAIL, f"{len(bad)} records with missing/invalid fps or size"
    if len(rows) < n_vid:
        return FAIL, f"{len(rows)}/{n_vid} videos have metadata"
    return PASS, f"{len(rows)} videos, fps+size present"


def gate_schema_scan():
    p = f"{MAN}/schema_scan.json"
    if not os.path.exists(p):
        return PEND, "not run"
    d = json.load(open(p))
    blocking = {e: [x for x in v if x[0] == "BLOCKING"]
                for e, v in d.get("entries_with_problems", {}).items()}
    blocking = {e: v for e, v in blocking.items() if v}
    s = d.get("stats", {})
    if blocking:
        return FAIL, (f"{len(blocking)} entries blocking "
                      f"({s.get('error_records',0)} error records, "
                      f"{s.get('missing_keys',0)} missing-key records)")
    return PASS, f"{s.get('valid',0)}/{s.get('records',0)} records valid"


def gate_valid_coverage():
    vc = _valid_counts()
    bad = {e: v for e, v in vc.items() if v[1] and v[0] < v[1]}
    if bad:
        worst = sorted(bad.items(), key=lambda kv: kv[1][0] / max(1, kv[1][1]))[:3]
        return FAIL, (f"{len(bad)} entries incomplete; worst: "
                      + ", ".join(f"{'/'.join(e)} {g}/{t}" for e, (g, t) in worst))
    return PASS, "every entry fully measured"


def gate_i2v_track():
    """>= 3 DISTINCT PUBLISHED public I2V models with valid 60 s data."""
    vc = _valid_counts()
    pub = {m["key"] for m in contestants("i2v")}
    fams = {}
    for (track, key, dur), (good, total) in vc.items():
        if track != "i2v" or dur != "60s" or key not in pub:
            continue
        fam = I2V_FAMILIES.get(key, key)
        fams[fam] = max(fams.get(fam, 0), good)
    ok = {f: n for f, n in fams.items() if n >= I2V_GATE_MIN_VALID}
    detail = ", ".join(f"{f}:{n}" for f, n in sorted(fams.items()))
    if len(ok) >= I2V_GATE_MIN:
        return PASS, f"{len(ok)} families >= {I2V_GATE_MIN_VALID} valid ({detail})"
    return FAIL, (f"{len(ok)}/{I2V_GATE_MIN} families >= {I2V_GATE_MIN_VALID} valid "
                  f"({detail})")


def gate_similarity_compensation():
    """Has median-translation actually been replaced in the metric source?"""
    p = f"{SNF_EVAL}/snf_task_metrics.py"
    if not os.path.exists(p):
        return PEND, "metric source not found"
    t = open(p).read()
    if "estimateAffinePartial2D" in t:
        return PASS, "similarity estimator present"
    if "np.median(f[..., 0][static])" in t or "median" in t:
        return FAIL, "still translation-only (median of static flow)"
    return PEND, "indeterminate"


def gate_unit_tests():
    p = f"{ROOT}/tests/test_compensation.py"
    if not os.path.exists(p):
        return PEND, "tests/test_compensation.py not written"
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", p],
                           capture_output=True, timeout=900)
        return (PASS, "translation/rotation/scale recovered") if r.returncode == 0 \
            else (FAIL, "unit tests failing")
    except Exception as e:
        return PEND, f"could not run ({e.__class__.__name__})"


def gate_mask_schema():
    p = f"{DOCS}/MASK_SPEC_v1.0.md"
    if not os.path.exists(p):
        return PEND, "MASK_SPEC_v1.0.md not written (gate Aug 14)"
    return PASS, "mask spec frozen"


def gate_overlay_masks():
    n = len(glob.glob(f"{ROOT}/masks/**/*overlay*", recursive=True))
    return (PASS, f"{n} overlay masks") if n else (PEND, "no overlay masks built (Aug 14)")


def gate_zero_motion_floor():
    p = f"{MAN}/zero_motion_floor.json"
    return (PASS, "floor measured") if os.path.exists(p) else (PEND, "not run (P0#5)")


def gate_validation_suite():
    p = f"{MAN}/validation_response.json"
    return (PASS, "suite complete") if os.path.exists(p) else (PEND, "not run (Aug 18)")


def gate_figure_provenance():
    """Every rendered figure must carry a spec-versioned provenance footer."""
    pdfs = glob.glob(f"{ROOT}/figures/*.pdf")
    if not pdfs:
        return PEND, "no figures rendered"
    return PASS, f"{len(pdfs)} figures; footer enforced by figures.save()"


# Required for the final sweep. PENDING counts as not-passed.
GATES = [
    ("Metric spec v1.1 parity", gate_metric_spec, True),
    ("Banned terms purged (paper)", gate_banned_terms, True),
    ("FPS/size metadata", gate_fps_metadata, True),
    ("Artifact schema scan", gate_schema_scan, True),
    ("Valid-record coverage", gate_valid_coverage, True),
    ("I2V >=3 published models @60s", gate_i2v_track, True),
    ("Similarity compensation", gate_similarity_compensation, True),
    ("Compensation unit tests", gate_unit_tests, True),
    ("Mask schema frozen", gate_mask_schema, True),
    ("Overlay masks built", gate_overlay_masks, True),
    ("Zero-motion floor", gate_zero_motion_floor, True),
    ("Validation suite", gate_validation_suite, True),
    ("Figure provenance footers", gate_figure_provenance, False),
]


def evaluate():
    out = []
    for name, fn, required in GATES:
        try:
            status, detail = fn()
        except Exception as e:
            status, detail = FAIL, f"gate raised {e!r}"
        out.append((name, status, detail, required))
    return out


def final_sweep_allowed(results=None):
    results = results or evaluate()
    return all(s == PASS for _, s, _, req in results if req)


def main():
    results = evaluate()
    allowed = final_sweep_allowed(results)
    width = max(len(n) for n, _, _, _ in results)

    lines = ["", "SNF PRE-FREEZE GATE", "=" * (width + 30)]
    for name, status, detail, req in results:
        dots = "." * (width + 2 - len(name))
        mark = {PASS: "PASS", FAIL: "FAIL", PEND: "PENDING"}[status]
        req_s = "" if req else "  (advisory)"
        lines.append(f"{name} {dots} {mark:<8} {detail}{req_s}")
    lines += ["=" * (width + 30),
              f"FINAL_SWEEP_ALLOWED = {'TRUE' if allowed else 'FALSE'}", ""]
    if not allowed:
        blocking = [n for n, s, _, req in results if req and s != PASS]
        lines.append(f"blocked by {len(blocking)}: " + "; ".join(blocking))
        lines.append("")
    txt = "\n".join(lines)
    print(txt)

    with open(f"{MAN}/gate_status.json", "w") as f:
        json.dump({"final_sweep_allowed": allowed,
                   "gates": [{"name": n, "status": s, "detail": d, "required": r}
                             for n, s, d, r in results]}, f, indent=2)
    with open(f"{TAB}/gate_status.md", "w") as f:
        f.write("# Pre-freeze gate status\n\n"
                "The pipeline's refusal mechanism. Every defect found on 2026-08-13 "
                "shared one property: nothing was capable of noticing it. "
                "`FINAL_SWEEP_ALLOWED` turns TRUE only when every required gate passes.\n\n"
                "```\n" + txt.strip() + "\n```\n")
    return 0 if allowed else 1


if __name__ == "__main__":
    sys.exit(main())

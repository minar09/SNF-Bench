#!/usr/bin/env python3
"""How much of `dE_static` is float32 rounding? Recompute it in float64.

`snf_extra_metrics.process` (v1 extras) and the ported `sourcefixed-1.0`
`extras_sourcefixed` both average support-region Lab colour with
`np.stack(...).reshape(-1, 3).mean(0)` on float32 arrays. With ~300k support
pixels x 24 late frames the per-channel sum exceeds float32 precision and the
mean drifts: on a *static* clip of scene icb04 the late-window a* mean is
130.76 in float32 against 135.53 in float64, and dE_static reads 6.84 where
the true shift is 1.35.

This recomputes, for already-scored method-project videos:
  dE_f32  the scorer's exact arithmetic -- must equal the stored record value,
          otherwise nothing below is trustworthy;
  dE_f64  the same formula accumulated in float64;
and the arm contrasts D(k) = dE(echo) - dE(sink) and Gamma(3,1) = D(3) - D(1)
per scene in both precisions. Read-only on the method project; writes
manifest/de_precision_audit_seed<S>.json.

    python scripts/audit_de_precision.py --seed 42
"""

import argparse
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths              # noqa: E402
import snf_sourceref as P  # noqa: E402

ROOT = _paths.ROOT
OUT = os.path.join(ROOT, "manifest", "de_precision_audit_seed{seed}.json")
CELLS = {("echo", 1): "cfpp/echo_nfpb1_default_lr", ("echo", 3): "cfpp/echo_nfpb3_default_lr",
         ("sink", 1): "cfpp/static_sink_nfpb1_default_lr", ("sink", 3): "cfpp/static_sink_nfpb3_default_lr"}


def de_both(video, support, source_bgr, E):
    fr = E.read_frames(video)
    n = len(fr)
    _, l_idx, _ = E.early_late(n)
    labs = [cv2.cvtColor(fr[i], cv2.COLOR_BGR2LAB).astype(np.float32)[support] for i in l_idx]
    st = np.stack(labs).reshape(-1, 3)
    src = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)[support]
    f32 = float(np.linalg.norm(st.mean(0) - src.mean(0)))
    f64 = float(np.linalg.norm(st.astype(np.float64).mean(0) - src.astype(np.float64).mean(0)))
    return f32, f64


def boot_ci(x, n=4000, seed=0):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(n)]
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="42")
    a = ap.parse_args()
    method = _paths.resolve("method_repo")
    masks = os.path.join(method, "results/factorial/source_masks")
    _, _, E = P.snf_modules()
    pairs = json.load(open(os.path.join(ROOT, "manifest/i2v_pairs_v2.json")))["pairs"]

    per = {}
    mismatched = []
    for p in pairs:
        sid = p["id"]
        lp = os.path.join(masks, sid, "labels.png")
        _, sup, lsha, _ = P.load_role_masks(lp)
        if sup.sum() < 50:
            continue
        src = cv2.imread(os.path.join(ROOT, "prompts/v2/i2v/images", f"{sid}.jpg"))
        vals = {}
        for key, cell in CELLS.items():
            rp = os.path.join(method, "results/factorial/scores", cell, f"seed{a.seed}",
                              "sourcefixed_60s/staging", f"{sid}.json")
            if not os.path.exists(rp):
                break
            rec = json.load(open(rp))
            if (rec.get("mask_sha256") or {}).get("labels") != lsha or rec.get("dE_static") is None:
                break
            v = rec["video_path"].replace("/workspace/", "/home/minar/")
            f32, f64 = de_both(v, sup, src, E)
            if abs(f32 - rec["dE_static"]) > 1e-4:
                mismatched.append((sid, key, f32, rec["dE_static"]))
            vals[key] = dict(stored=rec["dE_static"], f32=f32, f64=f64)
        if len(vals) == 4:
            per[sid] = dict(category=p["category"], **{f"{k[0]}_k{k[1]}": v for k, v in vals.items()})
            print(f"{sid:<6} " + "  ".join(f"{k}: {v['f32']:.2f}->{v['f64']:.2f}" for k, v in per[sid].items()
                                         if isinstance(v, dict)), flush=True)

    def gamma(prec):
        return [(r["echo_k3"][prec] - r["sink_k3"][prec]) - (r["echo_k1"][prec] - r["sink_k1"][prec])
                for r in per.values()]
    def d(k, prec):
        return [r[f"echo_k{k}"][prec] - r[f"sink_k{k}"][prec] for r in per.values()]
    err = [abs(v["f32"] - v["f64"]) for r in per.values() for v in r.values() if isinstance(v, dict)]
    rep = dict(seed=a.seed, n_scenes=len(per), reproduces_stored=not mismatched,
               mismatches=mismatched[:10],
               abs_error_f32_vs_f64=dict(median=float(np.median(err)), p95=float(np.percentile(err, 95)),
                                         max=float(np.max(err))),
               D3=dict(f32=boot_ci(d(3, "f32")), f64=boot_ci(d(3, "f64"))),
               D1=dict(f32=boot_ci(d(1, "f32")), f64=boot_ci(d(1, "f64"))),
               Gamma_3_1=dict(f32=boot_ci(gamma("f32")), f64=boot_ci(gamma("f64"))),
               note="scene-bootstrap mean [95% CI], one seed; compare with the method's seed-specific rows",
               scenes=per)
    json.dump(rep, open(OUT.format(seed=a.seed), "w"), indent=1)
    print(f"\nreproduces stored dE_static exactly: {rep['reproduces_stored']} ({len(mismatched)} mismatches)")
    print(f"|f32 - f64| per video: median {rep['abs_error_f32_vs_f64']['median']:.2f}  "
          f"p95 {rep['abs_error_f32_vs_f64']['p95']:.2f}  max {rep['abs_error_f32_vs_f64']['max']:.2f}")
    for k in ("D1", "D3", "Gamma_3_1"):
        a32, a64 = rep[k]["f32"], rep[k]["f64"]
        print(f"{k:<10} f32 {a32[0]:+.2f} [{a32[1]:+.2f}, {a32[2]:+.2f}]   f64 {a64[0]:+.2f} [{a64[1]:+.2f}, {a64[2]:+.2f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

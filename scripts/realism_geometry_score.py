#!/usr/bin/env python3
"""Score the construct-B geometry candidates from cached flows (CPU only).

The flows come from scripts/realism_geometry_run.py, which writes one npz per
(rate, mode, scene) under videos/realism_cache/geometry_flows/<label>/:
compensated RAFT flow (float16), the eroded material and support masks at flow
resolution, and the video's SHA-256. This script never recomputes flow, so a
new candidate version is a CPU rescoring of the same evidence.

Statistics: `cand-coverage-0` (scripts/realism_extent.py) and
`cand-material-transport-persistence-0` (scripts/realism_transport.py) on every
cached scene; v0 (`cand-channel-alignment-0`, `cand-sign-stability-0`,
`cand-gravity-sign-0`, tau = TAU_K x Q95 of the support's mean speed) for
continuity with the v0 report, and v1 (activity gate, `-1` identities,
`cand-gravity-stability-0`; scripts/realism_geometry.py), and v2 with the
static-bias exclusion (`-2` identities, `cand-gravity-stability-1`,
`cand-coverage-1`, `cand-material-transport-persistence-1`) under `v2`,
`extent1` and `transport1`.

    python scripts/realism_geometry_score.py --cache <dir> --label <cell> --out <json>
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import realism_extent as X       # noqa: E402
import realism_geometry as G     # noqa: E402
import realism_transport as TR   # noqa: E402

TAU_K = 1.0
ROUTE = {"channel_flow": "channel", "falling_water": "down", "buoyant_plume": "up", "combustion": "up"}
EXPECT = {"channel": ("A", lambda x: x > 0), "down": ("G", lambda x: x > 0), "up": ("G", lambda x: x < 0)}


def score_v0(route, flows, material, support):
    sup = np.linalg.norm(flows.mean(0), axis=-1)[support] if support.any() else np.zeros(1)
    tau = TAU_K * float(np.percentile(sup, 95))
    res = G.channel_alignment(flows, material, tau) if route == "channel" else G.gravity_sign(flows, material, tau)
    return dict(tau=tau, **res)


def score(route, flows, material, support):
    flows = flows.astype(np.float32)
    out = dict(extent=X.coverage(flows, material, support), transport=TR.transport(flows, material, support),
               extent1=X.coverage(flows, material, support, static=True),
               transport1=TR.transport(flows, material, support, static=True))
    if route != "none":
        out.update(v0=score_v0(route, flows, material, support), v1=G.geometry_v1(route, flows, material, support),
                   v2=G.geometry_v1(route, flows, material, support, version=2))
    return out


def load(path):
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    return z["flows"], z["material"], z["support"], meta


def summarize(rows, modes, rates):
    out = {}
    for rate in rates:
        for md in modes:
            s = {}
            for route, (key, ok) in EXPECT.items():
                rs = [r for r in rows if r["route"] == route and md in r["rates"].get(rate, {})]
                for ver in ("v0", "v1", "v2"):
                    v = [r["rates"][rate][md][ver][key] for r in rs if r["rates"][rate][md][ver].get(key) is not None]
                    s[f"{route}_{ver}"] = dict(n=len(v), n_attempted=len(rs),
                                              median=float(np.median(v)) if v else None,
                                              frac_expected_sign=float(np.mean([ok(x) for x in v])) if v else None)
                stab = "sign_stability" if route == "channel" else "gravity_stability"
                for ver in ("v1", "v2"):
                    v = [r["rates"][rate][md][ver][stab] for r in rs if r["rates"][rate][md][ver].get(stab) is not None]
                    s[f"{route}_{ver}_{stab}_median"] = float(np.median(v)) if v else None
            for ek in ("extent", "extent1"):
                ext = [r["rates"][rate][md][ek] for r in rows if md in r["rates"].get(rate, {})]
                for key in ("C", "E10", "C_min"):
                    v = [e[key] for e in ext if e.get(key) is not None]
                    s[f"{ek}_{key}_median"] = float(np.median(v)) if v else None
                s[f"{ek}_n"] = sum(1 for e in ext if "C" in e)
            for tk in ("transport", "transport1"):
                tr = [r["rates"][rate][md][tk] for r in rows if md in r["rates"].get(rate, {})]
                for key in ("delta", "damp_material", "damp_material_active"):
                    v = [e[key] for e in tr if e.get(key) is not None]
                    s[f"{tk}_{key}_median"] = float(np.median(v)) if v else None
            out[f"{rate}/{md}"] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.exists(a.out):
        raise SystemExit(f"{a.out} exists; reports are never overwritten")
    files = sorted(glob.glob(os.path.join(a.cache, "*", "*", "*.npz")) +
                   glob.glob(os.path.join(a.cache, "*", "*", "*.skip.json")))
    if not files:
        raise SystemExit(f"no cached flows under {a.cache}")
    rows, modes, rates = {}, [], []
    for f in files:
        rate, md, sid = f.split(os.sep)[-3], f.split(os.sep)[-2], os.path.basename(f).split(".")[0]
        modes += [md] if md not in modes else []
        rates += [rate] if rate not in rates else []
        if f.endswith(".skip.json"):
            meta = json.load(open(f))
            row = rows.setdefault(sid, dict(scene=sid, category=meta["category"], route=meta["route"], rates={}))
            row["rates"].setdefault(rate, {})[md] = dict(sha256=meta["sha256"], abstain=meta["abstain"],
                                                        **{k: dict(abstain=meta["abstain"]) for k in ("v0", "v1", "v2", "extent", "transport",
                                                                                      "extent1", "transport1")})
            continue
        flows, mat, sup, meta = load(f)
        row = rows.setdefault(sid, dict(scene=sid, category=meta["category"], route=meta["route"], rates={}))
        res = score(meta["route"], flows, mat, sup)
        row["rates"].setdefault(rate, {})[md] = dict(sha256=meta["sha256"], pairs=int(len(flows)),
                                                    compensation=meta["compensation"], **res)
    rows = [rows[k] for k in sorted(rows)]
    rep = dict(entrant=a.label, cache=os.path.relpath(a.cache, os.path.dirname(HERE)),
               identity=G.IDENTITY, tau_k=TAU_K, tau_abs=G.TAU_ABS, min_active=G.MIN_ACTIVE, route=ROUTE,
               spread_sigma=G.SPREAD_SIGMA, min_coherence=G.MIN_COHERENCE,
               static_sigma=G.STATIC_SIGMA, static_mag=G.STATIC_MAG,
               caveat="development data; image y is assumed to be gravity (no roll estimate yet); "
                      "bank field by normalized convolution, not Laplace; v0 from float16-cached flows",
               summary=summarize(rows, modes, rates), rows=rows)
    json.dump(rep, open(a.out, "w"), indent=1)
    print(json.dumps(rep["summary"], indent=1))


if __name__ == "__main__":
    main()

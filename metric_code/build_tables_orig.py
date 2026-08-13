#!/usr/bin/env python
"""Aggregate snf_task_metrics JSONs in a dir into a markdown + LaTeX table."""
import json, glob, os, argparse

PRETTY = {
    "sf": "Steady-Forcing (Ours)", "cf": "Causal-Forcing",
    "self": "Self-Forcing", "rew": "Reward-Forcing",
    "steady_forcing_bt": "Steady-Forcing (Ours)",
    "steady_forcing": "Steady-Forcing (st)",
    "self_forcing": "Self-Forcing",
    "causal_forcing": "Causal-Forcing",
    "reward_forcing": "Reward-Forcing",
    "rolling_forcing": "Rolling-Forcing",
    "infinite_forcing": "Infinite-Forcing",
    "longlive": "LongLive",
    "CausVid": "CausVid",
    # clean ablation variants (regenerated on Infinite-Forcing base, only inference policy differs)
    "base": "Base (no sink)",
    "vsink": "V-Sink only",
    "ema": "EMA-Sink only",
    "dual": "Dual-Sink",
    "full": "Dual-Sink + Flush (Full)",
}
# order for baseline table
ORDER = ["CausVid","self_forcing","reward_forcing","rolling_forcing",
         "infinite_forcing","longlive","causal_forcing","steady_forcing_bt",
         # ablation order
         "base","vsink","ema","dual","full"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--order", nargs="*", default=None)
    args = ap.parse_args()
    files = {os.path.splitext(os.path.basename(f))[0]: f
             for f in glob.glob(os.path.join(args.dir, "*.json"))}
    order = args.order or [m for m in ORDER if m in files] + \
            [m for m in files if m not in ORDER]

    cols = [("fBD_mean", "fBD\\down", "%.2f"),
            ("BFR_mean", "BFR\\down", "%.3f"),
            ("FP_mean", "FP\\up", "%.3f"),
            ("MCFF_late_mean", "MCFF_late\\up", "%.3f"),
            ("drift_frac_late_mean", "DriftFrac\\down", "%.2f")]

    rows = []
    for m in order:
        if m not in files:
            continue
        d = json.load(open(files[m]))
        rows.append((m, d))

    # markdown
    print(f"\n### {args.dir}  (n videos per row shown)")
    hdr = f"| {'Method':<24} | n | " + " | ".join(c[1].replace('\\down','↓').replace('\\up','↑') for c in cols) + " |"
    print(hdr); print("|" + "---|" * (len(cols) + 2))
    for m, d in rows:
        cells = []
        for k, _, fmt in cols:
            v = d.get(k)
            cells.append((fmt % v) if v is not None else "--")
        print(f"| {PRETTY.get(m,m):<24} | {d['n_videos']} | " + " | ".join(cells) + " |")

    # latex (fBD, BFR, FP only — the 3 headline columns)
    print("\n% ---- LaTeX (headline 3 cols) ----")
    print("\\begin{tabular}{lccc}\n\\toprule")
    print("Method (60s) & fBD$\\downarrow$ & BFR$\\downarrow$ & FP$\\uparrow$ \\\\\n\\midrule")
    for m, d in rows:
        name = PRETTY.get(m, m)
        f = "%.2f" % d["fBD_mean"] if d.get("fBD_mean") is not None else "--"
        b = "%.3f" % d["BFR_mean"] if d.get("BFR_mean") is not None else "--"
        p = "%.3f" % d["FP_mean"] if d.get("FP_mean") is not None else "--"
        if m.startswith("steady_forcing_bt"):
            f, b, p = f"\\textbf{{{f}}}", f"\\textbf{{{b}}}", f"\\textbf{{{p}}}"
        print(f"{name} & {f} & {b} & {p} \\\\")
    print("\\bottomrule\n\\end{tabular}")


if __name__ == "__main__":
    main()

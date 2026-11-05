#!/usr/bin/env python3
"""Freeze the realism development/confirmation split and a hash inventory, before any new statistic is seen.

Gate 1 and 2 of docs/SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md §5. Reuse of
existing videos for new candidate statistics and derived controls was
authorized by the user on 2026-11-05; such videos are development data only.

    python scripts/freeze_realism_split.py <listing dir> <exploratory dir> <out.json>

<listing dir> holds one `<cell>.tsv` per development parent cell (scene id,
video path). <exploratory dir> is the 2026-11-04 pilot's scratch directory
(`c1b/scenetether_s42/**/*.mp4`, `static/*.mp4`). Refuses to overwrite.
"""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _paths  # noqa: E402

ROOT = _paths.ROOT


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main(listing_dir, exploratory_dir, out):
    if os.path.exists(out):
        raise SystemExit(f"{out} exists; the split is frozen once")
    v2 = json.load(open(os.path.join(ROOT, "manifest/v2_splits.json")))
    fresh = json.load(open(os.path.join(ROOT, "manifest/fresh_split_audit.json")))
    parents = {}
    for tsv in sorted(glob.glob(os.path.join(listing_dir, "*.tsv"))):
        rows = [line.rstrip("\n").split("\t") for line in open(tsv)]
        parents["cfpp/" + os.path.basename(tsv)[:-4] + "/seed42/60s"] = {
            sid: dict(path=p, sha256=sha256(p)) for sid, p in rows}
    exploratory = {}
    for p in sorted(glob.glob(os.path.join(exploratory_dir, "c1b/scenetether_s42/**/*.mp4"), recursive=True)
                    + glob.glob(os.path.join(exploratory_dir, "static/*.mp4"))):
        rel = os.path.relpath(p, exploratory_dir)
        exploratory[rel] = dict(sha256=sha256(p), sidecar=os.path.exists(p[:-4] + ".json"))
    for m in ("pixelwise_colour_audit_scenetether.json", "pixelwise_colour_audit_h1fm.json",
              "pixelwise_colour_audit_input_check.json", "support_realism_pilot_scenetether_s42.json"):
        exploratory["manifest/" + m] = dict(sha256=sha256(os.path.join(ROOT, "manifest", m)))
    rep = dict(
        created="2026-11-05",
        authorization=("user, 2026-11-05: new separately versioned candidate statistics and derived controls "
                       "may be computed on existing videos; originals, existing scores and frozen metric "
                       "identities untouched"),
        scenes=dict(
            development=dict(v2_i2v=sorted(v2["test"] + v2["seen_overlap"]),
                             fresh=sorted(r["id"] for r in fresh["rows"]),
                             why="every existing v2 and fresh scene, and outputs on them, has been inspected"),
            confirmation=dict(ids=[], rule=("new scenes collected after 2026-11-05 and never viewed by the "
                                            "people developing realism statistics; none exist yet"))),
        model_families=dict(
            development=["CF++ family: every cfpp/, cf1/ and _dev/ cell of the method project (Causal-Forcing++ "
                         "checkpoints, framewise and chunk), SceneTether and H1-FM cells included",
                         "the method project's control cells (control_still, control_pasteback, "
                         "control_composite_untethered, control_composite_framepack)"],
            withheld_from_development=["existing native SVI Pro and Helios Distilled records "
                                       "(results/i2v_all_v2/*, results/research/scenetether_eval_oct19/*): "
                                       "published families, seen by the method project but not used to tune "
                                       "realism statistics"],
            confirmation=["published-panel I2V renders on the v2 scenes, generated after this freeze"],
            caveat=("SceneTether and H1-FM belong to the development family, so their confirmation results "
                    "are not held out by model family and are reported as such")),
        development_parents=parents,
        exploratory_2026_11_04=dict(
            status="exploratory; ran before the reuse authorization; never confirmation data",
            artifacts=exploratory))
    json.dump(rep, open(out, "w"), indent=1)
    print(out, sha256(out), sum(len(v) for v in parents.values()), "parents", len(exploratory), "exploratory")


if __name__ == "__main__":
    main(*sys.argv[1:4])

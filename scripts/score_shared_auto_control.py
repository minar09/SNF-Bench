#!/usr/bin/env python3
"""Held-out automatic-partition control on matched I2V 60 s clips.

The partition comes from self_forcing early RAFT flow and is reused unchanged
for other systems on the same prompt. This is an unreviewed sensitivity control,
not a semantic mask or a replacement for the reviewed-mask experiment.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("fire_smoke", "windborne", "river_stream", "precipitation")
MODELS = ("chunk6", "f2s_framewise")
KEYS = ("fBD", "BFR", "FP", "MCFF_late", "drift_frac_late", "DAR_signed", "static_frac")


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def prompt_selection():
    rows = list(csv.DictReader((ROOT / "manifest/prompt_categories.csv").open()))
    result = {}
    for category in CATEGORIES:
        eligible = sorted(r["prompt_id"] for r in rows if
                          r["track"] == "i2v" and r["duration"] == "60s" and
                          r["category"] == category)
        if not eligible:
            raise ValueError(f"no prompts for {category}")
        result[category] = eligible[0]
    return result


def baseline(model, video):
    path = ROOT / "raw/i2v" / model / "60s/snf_task_metrics.json"
    data = json.loads(path.read_text())
    rows = [r for r in data["per_video"] if r["video"] == video.name]
    if len(rows) != 1 or rows[0].get("metric_spec_version") != "1.1":
        raise ValueError(f"no unique v1.1 baseline: {model}/{video.name}")
    return rows[0]


def check_pair_alignment(prompt):
    for model in ("self_forcing",) + MODELS:
        report = ROOT / "manifest" / ("i2v_alignment_pilot.json" if model == "self_forcing" else
                                      f"i2v_alignment_{'f2s' if model == 'f2s_framewise' else model}_60s.json")
        data = json.loads(report.read_text())
        rows = [r for r in data["rows"] if r["prompt_id"] == prompt]
        if len(rows) != 1 or rows[0].get("ransac_inliers", 0) < 20 or \
                rows[0].get("corner_shift_fraction", 1) > 0.01:
            raise ValueError(f"alignment not established: {model}/{prompt}")


def build_mask(raft, prompt, device, outdir):
    import snf_metrics_v11 as V11
    source = ROOT / "videos/i2v/self_forcing/60s" / f"{prompt}.mp4"
    mask_path = outdir / "masks" / f"{prompt}.png"
    meta_path = outdir / "masks" / f"{prompt}.json"
    if mask_path.exists() and meta_path.exists():
        labels = cv2.imread(str(mask_path), cv2.IMREAD_UNCHANGED)
        meta = json.loads(meta_path.read_text())
        digest = hashlib.sha256(mask_path.read_bytes()).hexdigest()
        if labels is None or labels.ndim != 2 or digest != meta["sha256"]:
            raise ValueError(f"stored mask corrupt: {mask_path}")
        return labels == 2, labels == 1, meta
    tens, grays = V11.S.read_frames(str(source), device)
    if tens is None:
        raise ValueError(f"cannot decode mask source: {source}")
    win = max(V11.S.MIN_WIN, int(len(tens) * V11.S.WIN_FRAC))
    maps = [V11.S.flow_mag(raft, tens[i], tens[i + 1]).astype(np.float32)
            for i in range(min(win, len(tens) - 1))]
    dyn, static = V11.S.build_masks(np.mean(maps, axis=0))
    if dyn.shape != grays[0].shape or static.sum() < 50 or dyn.mean() < 0.01 or np.any(dyn & static):
        raise ValueError(f"invalid anchor mask for {prompt}")
    labels = np.zeros(dyn.shape, np.uint8)
    labels[static] = 1
    labels[dyn] = 2
    mask_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(mask_path), labels):
        raise RuntimeError(f"cannot write {mask_path}")
    meta = {"prompt_id": prompt, "mask_source": "self_forcing_early_raft_otsu_unreviewed",
            "anchor_video": str(source.relative_to(ROOT)), "mask_png": str(mask_path.relative_to(ROOT)),
            "sha256": hashlib.sha256(mask_path.read_bytes()).hexdigest(),
            "shape_hw": list(labels.shape), "static_frac": float(static.mean()),
            "dynamic_frac": float(dyn.mean()), "early_window_pairs": len(maps),
            "sampled_frames": len(tens), "reviewed": False}
    atomic_json(meta_path, meta)
    return dyn, static, meta


def compare(outdir, selected):
    rows = []
    for category, prompt in selected.items():
        for model in MODELS:
            video = ROOT / "videos/i2v" / model / "60s" / f"{prompt}.mp4"
            result_path = outdir / "scores" / model / f"{video.name}.json"
            if not result_path.exists():
                continue
            old = baseline(model, video)
            new = json.loads(result_path.read_text())
            mask_meta = json.loads((outdir / "masks" / f"{prompt}.json").read_text())
            if new.get("metric_spec_version") != "2-mask-pilot" or new.get("mask_sha256") != mask_meta["sha256"]:
                raise ValueError(f"stale or mismatched rescore: {result_path}")
            row = {"category": category, "prompt_id": prompt, "model": model,
                   "video": video.name, "baseline_spec": old["metric_spec_version"],
                   "rescore_spec": new["metric_spec_version"]}
            for key in KEYS:
                a, b = old.get(key), new.get(key)
                row[f"v11_{key}"] = a
                row[f"shared_{key}"] = b
                row[f"delta_{key}"] = None if a is None or b is None else b - a
            rows.append(row)
    atomic_json(outdir / "comparison.json", {"design": "paired per-video v1.1 automatic mask vs held-out self_forcing shared automatic mask",
                                                "n_pairs": len(rows), "expected_pairs": len(selected) * len(MODELS),
                                                "complete": len(rows) == len(selected) * len(MODELS), "rows": rows,
                                                "limitations": "Exploratory; masks are automatic and unreviewed; model setting differences preclude ranking claims."})
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gpu", default="4")
    ap.add_argument("--limit", type=int, default=0, help="first N categories, in fixed order")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    selected = prompt_selection()
    if args.limit:
        selected = dict(list(selected.items())[:args.limit])
    for category, prompt in selected.items():
        check_pair_alignment(prompt)
        for model in ("self_forcing",) + MODELS:
            video = ROOT / "videos/i2v" / model / "60s" / f"{prompt}.mp4"
            if not video.is_file():
                raise FileNotFoundError(video)
            if model != "self_forcing":
                baseline(model, video)
        print(category, prompt, flush=True)
    if args.check_only:
        return 0
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    import torch
    import snf_metrics_v11 as V11
    device = "cuda" if torch.cuda.is_available() else "cpu"
    raft = V11.S.load_raft(device)
    outdir = ROOT / "manifest/shared_auto_control/i2v/60s"
    failures = 0
    for category, prompt in selected.items():
        dyn, static, meta = build_mask(raft, prompt, device, outdir)
        for model in MODELS:
            video = ROOT / "videos/i2v" / model / "60s" / f"{prompt}.mp4"
            path = outdir / "scores" / model / f"{video.name}.json"
            if path.exists():
                existing = json.loads(path.read_text())
                if existing.get("mask_sha256") != meta["sha256"] or existing.get("metric_spec_version") != "2-mask-pilot":
                    raise ValueError(f"stored score uses a different mask or spec: {path}")
                print("SKIP", model, category, flush=True)
                continue
            try:
                provenance = {"mask_source": meta["mask_source"], "mask_png": meta["mask_png"],
                              "mask_sha256": meta["sha256"], "mask_anchor_video": meta["anchor_video"],
                              "mask_reviewed": False, "mask_geometry": "shared_first_frame_coordinates"}
                result = V11.process_video(raft, str(video), device,
                                           external_masks=(dyn, static), mask_provenance=provenance)
                if result is None:
                    raise RuntimeError("scorer returned no result")
                result.update(track="i2v", model=model, duration="60s", category=category)
                atomic_json(path, result)
                print("OK", model, category, flush=True)
            except Exception as exc:
                atomic_json(path.with_suffix(".error.json"),
                            {"video": str(video), "error": repr(exc)})
                failures += 1
                print("FAIL", model, category, repr(exc), flush=True)
        compare(outdir, selected)
    print("paired rescores:", compare(outdir, selected), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

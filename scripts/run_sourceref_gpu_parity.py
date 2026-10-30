"""Checkpointed comparison of sourcefixed-1.0 GPU scores with stored records.

This is a parity study, not validation of the automatic source masks or of
perceptual correctness. It compares identical video/source/mask bytes, stores
selected scores side by side, and requires every requested scene to pass.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import _paths  # noqa: E402
import check_sourceref_records as prior  # noqa: E402
import snf_sourceref as scorer  # noqa: E402

VERSION = "sourceref-gpu-parity-0.1"
SCORES = ("fBD_src", "fBD_f0", "BFR", "NBF", "FP", "MCFF_early",
          "MCFF_late", "DAR_signed", "dE_static_src", "idPSNR_late_src")
FLAGS = ("motion_abstained", "fBD_abstained")


def sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compare(old, new, rtol=1e-3, atol=1e-6):
    """Compare common numeric leaves and require all named scores/abstentions."""
    old_num, new_num = dict(prior.leaves(old)), dict(prior.leaves(new))
    common = sorted(set(old_num) & set(new_num))
    differences = []
    for key in common:
        a, b = old_num[key], new_num[key]
        if not (math.isfinite(a) and math.isfinite(b) and
                math.isclose(a, b, rel_tol=rtol, abs_tol=atol)):
            differences.append({"key": key, "old": a, "new": b,
                                "abs_diff": abs(a - b),
                                "relative_diff": abs(a - b) / max(abs(a), 1e-9)})
    required_missing = [key for key in SCORES + FLAGS if key not in old or key not in new]
    null_mismatches = [key for key in SCORES if key in old and key in new and
                       ((old[key] is None) != (new[key] is None))]
    flag_mismatches = [key for key in FLAGS if key in old and key in new and old[key] != new[key]]
    return {
        "status": "PASS" if common and not (differences or required_missing or null_mismatches or flag_mismatches) else "FAIL",
        "n_common_numeric_leaves": len(common),
        "n_exact_numeric_leaves": sum(old_num[key] == new_num[key] for key in common),
        "n_outside_tolerance": len(differences),
        "outside_tolerance": differences,
        "missing_required_keys": required_missing,
        "null_mismatches": null_mismatches,
        "abstention_mismatches": flag_mismatches,
        "scores": {key: {"previous": old.get(key), "rescore": new.get(key)} for key in SCORES},
        "abstentions": {key: {"previous": old.get(key), "rescore": new.get(key)} for key in FLAGS},
    }


def write_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    os.replace(temp, path)


def gpu_info(gpu):
    result = subprocess.run(["nvidia-smi", "-i", str(gpu),
                             "--query-gpu=uuid,memory.free,utilization.gpu",
                             "--format=csv,noheader,nounits"],
                            check=True, capture_output=True, text=True)
    uuid, free, util = [x.strip() for x in result.stdout.strip().split(",")]
    return {"uuid": uuid, "free_mib": int(free), "utilization_percent": int(util)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", type=int, required=True)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--scenes", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-free-mib", type=int, default=12288)
    parser.add_argument("--rtol", type=float, default=1e-3)
    parser.add_argument("--atol", type=float, default=1e-6)
    args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != str(args.gpu):
        parser.error("CUDA_VISIBLE_DEVICES must equal the requested physical GPU index")
    scenes = [value for value in args.scenes.split(",") if value]
    if not scenes or len(set(scenes)) != len(scenes):
        parser.error("scenes must be non-empty and unique")
    if args.output.exists():
        parser.error("output already exists; choose a new run path to preserve prior progress")
    method = Path(_paths.resolve("method_repo"))
    mask_root = method / "results/factorial/source_masks"
    manifest_hash = sha(mask_root / "MANIFEST.json")
    cdir = method / "results/factorial/scores" / args.cell / "sourcefixed_60s/staging"
    loop = method / "results/factorial/scores/_loop"
    report = {
        "schema_version": 1, "version": VERSION, "status": "running",
        "measurement": "sourcefixed-1.0", "interpretation": "same-input parity, not human validity",
        "cell": args.cell, "gpu_index": args.gpu, "gpu_before": gpu_info(args.gpu),
        "rtol": args.rtol, "atol": args.atol, "requested_scenes": scenes,
        "mask_manifest_sha256": manifest_hash, "port_sha256": sha(scorer.__file__),
        "runner_sha256": sha(__file__), "upstream_scorer_sha256": scorer.UPSTREAM_SHA256,
        "rows": [], "n_requested": len(scenes), "n_pass": 0,
    }
    write_atomic(args.output, report)
    model = None
    try:
        import torch
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
            raise RuntimeError("requested CUDA device is unavailable or device visibility is not isolated")
        S, _, _ = scorer.snf_modules()
        for sid in scenes:
            t0 = time.monotonic()
            row = {"scene_id": sid, "status": "ERROR"}
            try:
                rec_path = cdir / f"{sid}.json"
                rec = json.loads(rec_path.read_text())
                video = Path(str(rec["video_path"]).replace("/workspace/", "/home/minar/"))
                if not video.is_absolute():
                    video = method / video
                source = ROOT / "prompts/v2/i2v/images" / f"{sid}.jpg"
                mask = mask_root / sid / "labels.png"
                checks = {"video": sha(video) == rec.get("video_sha256"),
                          "source": sha(source) == rec.get("source_sha256"),
                          "mask": sha(mask) == (rec.get("mask_sha256") or {}).get("labels"),
                          "upstream_scorer": rec.get("scorer_sha256") == scorer.UPSTREAM_SHA256}
                row.update(category=rec.get("category"), input_hash_checks=checks,
                           previous_record_sha256=sha(rec_path),
                           video_sha256=rec.get("video_sha256"), source_sha256=rec.get("source_sha256"),
                           mask_sha256=(rec.get("mask_sha256") or {}).get("labels"))
                if not all(checks.values()):
                    raise ValueError("input or upstream scorer hash mismatch")
                prior.gate(args.gpu, args.min_free_mib, str(loop))
                row["gpu_before"] = gpu_info(args.gpu)
                if model is None:
                    model = S.load_raft("cuda")
                new = scorer.score_video(model, str(video), str(mask), str(source), "cuda",
                                         native_fps=rec.get("native_fps", 16.0),
                                         mask_set=f"sha256:{manifest_hash[:12]}",
                                         mask_version=rec.get("mask_version"), mask_review_scope="ai")
                row.update(compare(rec, new, args.rtol, args.atol))
                row["registration"] = {"previous": rec.get("registration"),
                                       "rescore": new.get("registration")}
            except Exception as exc:
                row.update(status="ERROR", error=f"{type(exc).__name__}: {exc}")
                row["traceback"] = traceback.format_exc(limit=5)
            row["elapsed_s"] = round(time.monotonic() - t0, 2)
            report["rows"].append(row)
            report["n_pass"] = sum(r["status"] == "PASS" for r in report["rows"])
            write_atomic(args.output, report)
            print(f"{sid}: {row['status']} in {row['elapsed_s']}s; "
                  f"{report['n_pass']}/{len(report['rows'])} passed", flush=True)
            if row["status"] == "ERROR":
                # GPU/runtime errors must not trigger automatic repeated work.
                break
    finally:
        report["n_finished"] = len(report["rows"])
        report["status"] = ("PASS" if len(report["rows"]) == len(scenes) and
                            all(r["status"] == "PASS" for r in report["rows"]) else "INCOMPLETE_OR_FAILED")
        write_atomic(args.output, report)
    print(f"{report['status']}: {report['n_pass']}/{len(scenes)} requested scenes", flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

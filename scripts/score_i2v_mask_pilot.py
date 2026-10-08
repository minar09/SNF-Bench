#!/usr/bin/env python3
"""Score I2V videos with reviewed shared-source masks into a separate pilot tree.

Requires a human-reviewed label PNG per prompt and an alignment audit for the
selected model. It never writes under raw/ or the v1.1 metrics manifest.
Use --check-only before any GPU scoring.
"""

import argparse
import json
import sys
import os
from pathlib import Path

import cv2

from external_masks import ROOT, load_reviewed_mask, read_manifest, verify_alignment


def first_frame_eval_size(video):
    cap = cv2.VideoCapture(str(video))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise ValueError(f"cannot decode first frame: {video}")
    height, width = frame.shape[:2]
    return (int(round(width * 288 / height)), 288)


def prepared_items(mask_manifest, alignment_report, model, duration, limit=0):
    entries = read_manifest(mask_manifest)
    metadata_path = ROOT / "prompts" / "v1" / "i2v" / duration / "target_crop_info_16-9.json"
    metadata = {x["caption"][:100]: x for x in json.loads(metadata_path.read_text())}
    output = []
    for (entry_duration, prompt_id), entry in sorted(entries.items()):
        if entry_duration != duration:
            continue
        if prompt_id not in metadata:
            raise ValueError(f"mask prompt absent from conditioning manifest: {prompt_id}")
        expected_source = f"prompts/v1/i2v/{duration}/images/{metadata[prompt_id]['file_name']}"
        sys.path.insert(0, str(ROOT / "scripts"))
        import prompt_sets
        if prompt_sets.migrate_path(entry.get("source_image", "")) != expected_source:
            raise ValueError(f"source image mismatch for {prompt_id}")
        video_relative = f"videos/i2v/{model}/{duration}/{prompt_id}.mp4"
        video = ROOT / video_relative
        if not video.is_file():
            raise FileNotFoundError(f"generated video missing: {video_relative}")
        width_height = first_frame_eval_size(video)
        dynamic, static, provenance = load_reviewed_mask(entry, width_height)
        provenance.update(verify_alignment(alignment_report, video_relative))
        output.append((video, dynamic, static, provenance))
        if limit and len(output) >= limit:
            break
    if not output:
        raise ValueError(f"no reviewed masks for {duration}")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask-manifest", type=Path, required=True)
    parser.add_argument("--alignment-report", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--duration", default="60s")
    parser.add_argument("--gpu", default="0")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()
    items = prepared_items(args.mask_manifest, args.alignment_report,
                           args.model, args.duration, args.limit)
    print(f"{len(items)} reviewed masks and alignments ready")
    if args.check_only:
        return 0

    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    import torch
    import snf_metrics_v11 as V11
    model = V11.S.load_raft("cuda" if torch.cuda.is_available() else "cpu")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    out_dir = args.out_dir or (ROOT / "manifest" / "mask_pilot" / args.model / args.duration)
    out_dir.mkdir(parents=True, exist_ok=True)
    failures = 0
    for video, dynamic, static, provenance in items:
        path = out_dir / f"{video.name}.json"
        try:
            result = V11.process_video(model, str(video), device,
                                       external_masks=(dynamic, static),
                                       mask_provenance=provenance)
            if not result:
                raise RuntimeError("scorer returned no result")
            result.update(track="i2v", model=args.model, duration=args.duration)
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_text(json.dumps(result, indent=2) + "\n")
            temporary.replace(path)
            print("OK", video.name)
        except Exception as exc:
            failures += 1
            path.with_suffix(".error.json").write_text(json.dumps(
                {"video": str(video), "error": repr(exc)}, indent=2) + "\n")
            print("FAIL", video.name, repr(exc))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

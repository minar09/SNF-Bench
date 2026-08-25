#!/usr/bin/env python3
"""Create deterministic synthetic example data and a translation response curve."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def base_scene(height: int, width: int) -> np.ndarray:
    y, x = np.mgrid[0:height, 0:width]
    image = np.zeros((height, width, 3), dtype=np.uint8)
    support = y < int(0.64 * height)
    checker = ((x // 8 + y // 8) % 2) * 34
    image[..., 0] = np.where(support, 105 + checker, 38)
    image[..., 1] = np.where(support, 122 + checker, 108)
    image[..., 2] = np.where(support, 78 + checker, 168)
    for center_x, center_y in ((28, 24), (72, 42), (124, 26)):
        cv2.circle(image, (center_x, center_y), 8, (185, 170, 140), -1)
        cv2.circle(image, (center_x, center_y), 8, (55, 55, 48), 1)
    return image


def create_bundle(path: Path, extra_translation: float = 0.0) -> None:
    frames_count, height, width = 30, 96, 160
    source = base_scene(height, width)
    flow_y = int(0.64 * height)
    frames, flows = [], []
    for frame_index in range(frames_count):
        cumulative = (0.22 + extra_translation) * frame_index
        transform = np.float32([[1, 0, cumulative], [0, 1, 0]])
        frame = cv2.warpAffine(
            source,
            transform,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT,
        )
        water = frame[flow_y:].astype(np.float32)
        wave = 28.0 * np.sin(
            np.arange(width, dtype=np.float32)[None, :] / 7.0 + frame_index * 0.55
        )
        water[..., 2] = np.clip(water[..., 2] + wave, 0, 255)
        water[..., 1] = np.clip(water[..., 1] - 0.35 * wave, 0, 255)
        frame[flow_y:] = water.astype(np.uint8)
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if frame_index < frames_count - 1:
            field = np.zeros((height, width, 2), dtype=np.float32)
            field[..., 0] = 0.22 + extra_translation
            field[flow_y:, :, 0] += 1.35 + 0.35 * np.sin(frame_index * 0.4)
            flows.append(field)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        frames_rgb=np.stack(frames),
        flows=np.stack(flows),
        sample_fps=np.float32(8.0),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", default="example_predictions")
    parser.add_argument("--manifest", default="benchmark_manifest.json")
    parser.add_argument("--curve_manifest", default="run_outputs/perturbation_manifest.json")
    parser.add_argument("--levels", default="0.0,0.15,0.30,0.60")
    args = parser.parse_args()

    output_dir = Path(args.out_dir)
    levels = [float(value) for value in args.levels.split(",")]
    items = []
    for level in levels:
        name = f"translation_{level:.2f}.npz"
        create_bundle(output_dir / name, extra_translation=level)
        items.append({"id": f"translation_{level:.2f}", "prediction": name, "severity": level})
    # The primary manifest intentionally contains one record, as requested by
    # the review-artifact smoke command.
    Path(args.manifest).write_text(
        json.dumps({"schema_version": "1.0", "items": [items[0]]}, indent=2) + "\n",
        encoding="utf-8",
    )
    curve_path = Path(args.curve_manifest)
    curve_path.parent.mkdir(parents=True, exist_ok=True)
    curve_path.write_text(
        json.dumps({"schema_version": "1.0", "items": items}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(items)} bundles, {args.manifest}, and {curve_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Export the automatic early-window static/dynamic partition for inspection."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from snf_core import MIN_WIN, WIN_FRAC, build_masks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with np.load(args.prediction, allow_pickle=False) as bundle:
        flows = bundle["flows"]
    window = min(len(flows), max(MIN_WIN, int((len(flows) + 1) * WIN_FRAC)))
    early = np.mean(np.linalg.norm(flows[:window], axis=-1), axis=0)
    dynamic, static = build_masks(early)

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, dynamic=dynamic, static=static, early_magnitude=early)
    preview = np.zeros((*dynamic.shape, 3), dtype=np.uint8)
    preview[static] = (80, 160, 235)
    preview[dynamic] = (230, 130, 70)
    cv2.imwrite(str(output.with_suffix(".png")), cv2.cvtColor(preview, cv2.COLOR_RGB2BGR))
    print(f"wrote {output} and {output.with_suffix('.png')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

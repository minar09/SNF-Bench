#!/usr/bin/env python3
"""Pack the rollout viewer's thumbnails into one sprite per prompt and system.

Reads JOURNAL_TCSVT/interactive/assets/t2v240/p*/<key>_{t000..t240,change,motion}.jpg
(written by build_journal_snapshots.py) and writes assets/sprites/p*/<key>.jpg: a
COLS x ROWS grid of 416x240 cells in the order t000, t010, ..., t240, change, motion.
The viewer addresses a cell by index, so a hosted copy needs 32 image files instead of
about 860. Cells are copied pixel for pixel and re-encoded once at JPEG quality 90.

    /home/minar/miniconda3/envs/snfeval/bin/python scripts/build_companion_sprites.py
"""
import glob
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "JOURNAL_TCSVT", "interactive", "assets")
W, H, COLS, ROWS = 416, 240, 9, 3
CELLS = [f"t{t:03d}" for t in range(0, 241, 10)] + ["change", "motion"]


def main():
    n = 0
    for pdir in sorted(glob.glob(os.path.join(ASSETS, "t2v240", "p*"))):
        keys = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(pdir, "*_change.jpg"))})
        out = os.path.join(ASSETS, "sprites", os.path.basename(pdir))
        os.makedirs(out, exist_ok=True)
        for key in keys:
            sheet = np.zeros((H * ROWS, W * COLS, 3), np.uint8)
            for i, cell in enumerate(CELLS):
                img = cv2.imread(os.path.join(pdir, f"{key}_{cell}.jpg"))
                if img is None or img.shape[:2] != (H, W):
                    raise SystemExit(f"missing or misshaped cell: {pdir}/{key}_{cell}.jpg")
                r, c = divmod(i, COLS)
                sheet[r * H:(r + 1) * H, c * W:(c + 1) * W] = img
            cv2.imwrite(os.path.join(out, f"{key}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])
            n += 1
    print(f"{n} sprites, {COLS}x{ROWS} cells of {W}x{H}")


if __name__ == "__main__":
    main()

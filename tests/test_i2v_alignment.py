"""Check the alignment diagnostic on controlled image pairs."""

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_i2v_alignment import alignment  # noqa: E402


def test_same_textured_image_has_many_inliers():
    rng = np.random.default_rng(2)
    image = rng.integers(0, 256, (180, 320, 3), dtype=np.uint8)
    result = alignment(image, image.copy())
    assert result["relative_aspect_gap"] == 0
    assert result["ransac_inliers"] >= 20
    assert result["ransac_inlier_fraction"] > 0.8
    assert result["corner_shift_fraction"] < 0.01


def test_aspect_mismatch_is_reported_without_claiming_alignment():
    src = np.zeros((320, 180, 3), np.uint8)
    dst = np.zeros((180, 320, 3), np.uint8)
    result = alignment(src, dst)
    assert result["relative_aspect_gap"] > 0.5
    assert result["ransac_inliers"] == 0

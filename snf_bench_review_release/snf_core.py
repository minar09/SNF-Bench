"""Standalone SNF-Bench metric post-processing for the anonymous review artifact.

Inputs contain decoded RGB frames and optical-flow fields computed between
successive sampled frames. Keeping flow extraction outside this small module
makes the six metric definitions auditable and lets the included synthetic
smoke test run without downloading model weights. Paper results use RAFT flow;
the included example supplies deterministic analytic flow fields.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, Tuple

import cv2
import numpy as np


WIN_FRAC = 0.12
MIN_WIN = 3
FP_CAP = 2.0
EPS = 1e-6
RANSAC_THRESH = 1.5
MIN_CORRESP = 50
MAX_SAMPLE = 4000


def build_masks(early_magnitude: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return `(dynamic, static)` masks from early-window flow magnitude."""
    height, width = early_magnitude.shape
    scaled = early_magnitude / (float(early_magnitude.max()) + EPS)
    image = np.clip(scaled * 255.0, 0, 255).astype(np.uint8)
    _, dynamic = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    dynamic = dynamic > 0
    if float(dynamic.mean()) < 0.03:
        threshold = max(float(np.percentile(early_magnitude, 80)), EPS)
        dynamic = early_magnitude >= threshold

    kernel = np.ones((5, 5), np.uint8)
    dynamic_u8 = cv2.morphologyEx(
        dynamic.astype(np.uint8), cv2.MORPH_OPEN, kernel
    )
    dynamic_u8 = cv2.morphologyEx(dynamic_u8, cv2.MORPH_CLOSE, kernel)
    dynamic = dynamic_u8 > 0

    static = ~dynamic
    border = np.zeros_like(static)
    border_y, border_x = int(height * 0.04), int(width * 0.04)
    border[border_y : height - border_y, border_x : width - border_x] = True
    static = cv2.erode((static & border).astype(np.uint8), kernel).astype(bool)
    return dynamic, static


def _translation_field(
    flow: np.ndarray, static: np.ndarray
) -> Tuple[np.ndarray, str]:
    if static.any():
        dx = float(np.median(flow[..., 0][static]))
        dy = float(np.median(flow[..., 1][static]))
    else:
        dx = dy = 0.0
    field = np.empty_like(flow, dtype=np.float32)
    field[..., 0] = dx
    field[..., 1] = dy
    return field, "translation_fallback"


def estimate_similarity(
    flow: np.ndarray, static: np.ndarray, rng: np.random.Generator
) -> Tuple[np.ndarray, str, float]:
    """Fit a similarity displacement field to static-region correspondences."""
    height, width = static.shape
    ys, xs = np.nonzero(static)
    count = len(xs)
    if count < MIN_CORRESP:
        field, mode = _translation_field(flow, static)
        return field, mode, 0.0
    if count > MAX_SAMPLE:
        chosen = rng.choice(count, size=MAX_SAMPLE, replace=False)
        ys, xs = ys[chosen], xs[chosen]

    source = np.stack([xs, ys], axis=1).astype(np.float32)
    destination = source + np.stack(
        [flow[ys, xs, 0], flow[ys, xs, 1]], axis=1
    ).astype(np.float32)
    matrix, inliers = cv2.estimateAffinePartial2D(
        source,
        destination,
        method=cv2.RANSAC,
        ransacReprojThreshold=RANSAC_THRESH,
        maxIters=2000,
        confidence=0.995,
    )
    if matrix is None:
        field, mode = _translation_field(flow, static)
        return field, mode, 0.0

    grid_x, grid_y = np.meshgrid(
        np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32)
    )
    warped_x = matrix[0, 0] * grid_x + matrix[0, 1] * grid_y + matrix[0, 2]
    warped_y = matrix[1, 0] * grid_x + matrix[1, 1] * grid_y + matrix[1, 2]
    field = np.stack([warped_x - grid_x, warped_y - grid_y], axis=-1)
    ratio = float(inliers.mean()) if inliers is not None else 0.0
    return field.astype(np.float32), "similarity", ratio


def orb_drift(
    frames_rgb: np.ndarray, static: np.ndarray, late_indices: Iterable[int]
) -> float | None:
    """Mean late-window median ORB displacement as percent of frame diagonal."""
    grays = [cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) for frame in frames_rgb]
    height, width = grays[0].shape
    diagonal = math.hypot(height, width)
    orb = cv2.ORB_create(nfeatures=1500)
    mask = static.astype(np.uint8) * 255
    key0, desc0 = orb.detectAndCompute(grays[0], mask)
    if desc0 is None or len(key0) < 12:
        return None
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    displacements = []
    for index in late_indices:
        key1, desc1 = orb.detectAndCompute(grays[index], mask)
        if desc1 is None or len(key1) < 12:
            continue
        matches = matcher.match(desc0, desc1)
        if len(matches) < 12:
            continue
        points0 = np.float32([key0[m.queryIdx].pt for m in matches])
        points1 = np.float32([key1[m.trainIdx].pt for m in matches])
        _, inliers = cv2.findHomography(points0, points1, cv2.RANSAC, 3.0)
        if inliers is not None and int(inliers.sum()) >= 8:
            keep = inliers.ravel().astype(bool)
            points0, points1 = points0[keep], points1[keep]
        displacements.append(float(np.median(np.linalg.norm(points1 - points0, axis=1))))
    if not displacements:
        return None
    return float(np.mean(displacements) / diagonal * 100.0)


def evaluate_arrays(
    frames_rgb: np.ndarray, flows: np.ndarray, sample_fps: float, seed: int = 0
) -> Tuple[Dict[str, float | str | None], np.ndarray, np.ndarray]:
    """Compute the six SNF-Bench quantities from frames and sampled-pair flow."""
    if frames_rgb.ndim != 4 or frames_rgb.shape[-1] != 3:
        raise ValueError("frames must have shape [T,H,W,3]")
    expected = (frames_rgb.shape[0] - 1, *frames_rgb.shape[1:3], 2)
    if flows.shape != expected:
        raise ValueError(f"flows must have shape {expected}, got {flows.shape}")
    if len(frames_rgb) < 4 or len(flows) != len(frames_rgb) - 1:
        raise ValueError("at least four frames and one flow per adjacent pair are required")
    if sample_fps <= 0:
        raise ValueError("sample_fps must be positive")

    pair_count = len(flows)
    window = max(MIN_WIN, int(len(frames_rgb) * WIN_FRAC))
    window = min(window, pair_count)
    early_magnitude = np.mean(np.linalg.norm(flows[:window], axis=-1), axis=0)
    dynamic, static = build_masks(early_magnitude)

    static_magnitude = np.zeros(pair_count, dtype=np.float64)
    dynamic_raw = np.zeros(pair_count, dtype=np.float64)
    dynamic_compensated = np.zeros(pair_count, dtype=np.float64)
    modes, inlier_ratios = [], []
    rng = np.random.default_rng(seed)
    for index, flow in enumerate(flows.astype(np.float32)):
        magnitude = np.linalg.norm(flow, axis=-1)
        if static.any():
            static_magnitude[index] = float(magnitude[static].mean())
        field, mode, ratio = estimate_similarity(flow, static, rng)
        modes.append(mode)
        inlier_ratios.append(ratio)
        if dynamic.any():
            dynamic_raw[index] = float(magnitude[dynamic].mean())
            residual = np.linalg.norm(flow - field, axis=-1)
            dynamic_compensated[index] = float(residual[dynamic].mean())

    if pair_count >= 2 * window:
        early = float(dynamic_compensated[window : 2 * window].mean())
    else:
        early = float(dynamic_compensated[:window].mean())
    late = float(dynamic_compensated[-window:].mean())
    raw_late = float(dynamic_raw[-window:].mean())
    width = frames_rgb.shape[2]

    record: Dict[str, float | str | None] = {
        "fBD": orb_drift(
            frames_rgb, static, range(len(frames_rgb) - window, len(frames_rgb))
        ),
        "NBF": float(static_magnitude.mean() / width * 1000.0 * sample_fps),
        "MCFF_E": early,
        "MCFF_L": late,
        "FP": float(min(late / (early + EPS), FP_CAP)),
        "DLR": float(static_magnitude[-window:].mean() / (raw_late + EPS)),
        "DAR_signed": float(1.0 - late / (raw_late + EPS)),
        "DAR_report": float(np.clip(1.0 - late / (raw_late + EPS), 0.0, 1.0)),
        "static_fraction": float(static.mean()),
        "dynamic_fraction": float(dynamic.mean()),
        "compensation_mode": "similarity" if all(m == "similarity" for m in modes) else "mixed",
        "similarity_fraction": float(sum(m == "similarity" for m in modes) / pair_count),
        "inlier_ratio_mean": float(np.mean(inlier_ratios)),
        "metric_spec_version": "1.1",
    }
    return record, dynamic, static

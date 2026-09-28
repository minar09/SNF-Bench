"""Strict reviewed-mask input for the I2V shared-source M1 control.

Label PNG values: 0 ignore, 1 rigid support, 2 intended motion,
3 overlay/ambiguous. The source PNG is painted in source-image coordinates,
then resized once to the benchmark's evaluation frame. No automatic mask
proposal is accepted as reviewed ground truth.
"""

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LABELS = {0, 1, 2, 3}
MASK_VERSION = "v2-source-reviewed-pilot"


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(path):
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("mask manifest must be schema_version 1 object")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError("mask manifest entries must be a list")
    by_prompt = {}
    for entry in entries:
        if entry.get("track") != "i2v" or not entry.get("duration") or not entry.get("prompt_id"):
            raise ValueError("each mask entry needs i2v track, duration and prompt_id")
        key = (entry["duration"], entry["prompt_id"])
        if key in by_prompt:
            raise ValueError(f"duplicate mask entry {key}")
        by_prompt[key] = entry
    return by_prompt


def _inside_root(relative):
    if not isinstance(relative, str) or not relative:
        raise ValueError("mask and source paths must be nonempty repository-relative strings")
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"path leaves repository: {relative}")
    # Source-image directories are repository symlinks to the generation asset
    # store. Keep the lexical repository path, then verify the file hash.
    return ROOT / rel


def load_reviewed_mask(entry, frame_wh):
    """Return (dynamic, static, provenance) at evaluation resolution.

    `frame_wh` is `(width, height)` from the already decoded metric frame.
    The caller must separately verify source-to-video alignment for each model.
    """
    if entry.get("reviewed") is not True or not entry.get("reviewed_by"):
        raise ValueError("mask must have an explicit human review record")
    if entry.get("geometry") != "direct_resize":
        raise ValueError("only audited direct_resize geometry is supported")
    source = _inside_root(entry.get("source_image"))
    mask_path = _inside_root(entry.get("label_png"))
    if not mask_path.resolve().is_relative_to(ROOT):
        raise ValueError("reviewed label PNG must physically remain in repository")
    if not source.is_file() or not mask_path.is_file():
        raise FileNotFoundError("source image or reviewed label PNG is missing")
    source_hash = sha256(source)
    if source_hash != entry.get("source_sha256"):
        raise ValueError("source image hash differs from reviewed mask manifest")
    src = cv2.imread(str(source), cv2.IMREAD_UNCHANGED)
    labels = cv2.imread(str(mask_path), cv2.IMREAD_UNCHANGED)
    if src is None or labels is None or labels.ndim != 2 or labels.dtype != np.uint8:
        raise ValueError("source must decode and label PNG must be single-channel uint8")
    if labels.shape != src.shape[:2]:
        raise ValueError("label PNG must match exact source image geometry")
    invalid = set(np.unique(labels).tolist()) - LABELS
    if invalid:
        raise ValueError(f"unknown mask labels: {sorted(invalid)}")
    width, height = frame_wh
    if width < 1 or height < 1:
        raise ValueError("invalid evaluation frame dimensions")
    resized = cv2.resize(labels, (width, height), interpolation=cv2.INTER_NEAREST)
    static = resized == 1
    dynamic = resized == 2
    if static.sum() < 50 or dynamic.mean() < 0.01:
        raise ValueError("degenerate reviewed static or dynamic region after resize")
    provenance = {"mask_version": MASK_VERSION, "mask_source": "reviewed_i2v_source",
                  "mask_source_image": entry["source_image"],
                  "mask_source_sha256": source_hash,
                  "mask_label_png": entry["label_png"],
                  "mask_label_sha256": sha256(mask_path),
                  "mask_geometry": "direct_resize",
                  "mask_reviewer": entry["reviewed_by"],
                  "mask_static_frac": float(static.mean()),
                  "mask_dynamic_frac": float(dynamic.mean()),
                  "mask_overlay_frac": float((resized == 3).mean()),
                  "mask_ignore_frac": float((resized == 0).mean())}
    return dynamic, static, provenance


def verify_alignment(report_path, video_relative, min_inliers=20, max_corner_shift=0.01):
    """Require a recorded source-to-first-frame geometric transfer check."""
    report = json.loads(Path(report_path).read_text())
    matches = [r for r in report.get("rows", []) if r.get("video") == video_relative]
    if len(matches) != 1:
        raise ValueError(f"alignment report lacks exactly one row for {video_relative}")
    row = matches[0]
    shift = row.get("corner_shift_fraction")
    if row.get("ransac_inliers", 0) < min_inliers or shift is None or shift > max_corner_shift:
        raise ValueError(f"source-to-video alignment not established for {video_relative}")
    return {"alignment_inliers": row["ransac_inliers"],
            "alignment_corner_shift_fraction": shift,
            "alignment_report": str(report_path)}

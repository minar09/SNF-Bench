"""Validate SNF-v2 transport path/ROI annotations and their review gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DIRECTION = {"applicable", "not_applicable", "unscorable"}


def _inside_repo(relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("source_image must be a repository-relative path")
    # Recorded pilots keep the paths they were written with; v1 inputs have since
    # moved to prompts/v1/ byte-for-byte, and the sha256 check below still binds
    # the record to the exact image.
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    import prompt_sets
    return ROOT / prompt_sets.migrate_path(str(path))


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _points(value, minimum, field, errors, scene_id):
    if not isinstance(value, list) or len(value) < minimum:
        errors.append(f"{scene_id}: {field} needs at least {minimum} points")
        return []
    clean = []
    for index, point in enumerate(value):
        if (not isinstance(point, list) or len(point) != 2 or
                not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in point) or
                not all(0 <= float(v) <= 1 for v in point)):
            errors.append(f"{scene_id}: {field}[{index}] must be normalized [x,y]")
            continue
        clean.append((float(point[0]), float(point[1])))
    return clean


def validate(payload, strict_release=False):
    errors, warnings = [], []
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        return ["root: schema_version must equal 1"], []
    if payload.get("coordinate_space") != "normalized_source_image_xy":
        errors.append("root: coordinate_space must be normalized_source_image_xy")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("root: entries must be a nonempty list")
        return errors, warnings
    seen = set()
    for entry in entries:
        scene_id = entry.get("scene_id", "<missing-scene-id>")
        if scene_id in seen:
            errors.append(f"{scene_id}: duplicate scene_id")
        seen.add(scene_id)
        for key in ("scene_id", "track", "duration", "prompt_id", "medium",
                    "source_image", "source_sha256", "source_width", "source_height"):
            if entry.get(key) in (None, ""):
                errors.append(f"{scene_id}: missing {key}")
        try:
            source = _inside_repo(entry.get("source_image", ""))
            if not source.is_file():
                errors.append(f"{scene_id}: source image is missing")
            else:
                if _sha256(source) != entry.get("source_sha256"):
                    errors.append(f"{scene_id}: source hash mismatch")
                image = cv2.imread(str(source))
                if image is None:
                    errors.append(f"{scene_id}: source image does not decode")
                elif [image.shape[1], image.shape[0]] != [entry.get("source_width"), entry.get("source_height")]:
                    errors.append(f"{scene_id}: source dimensions mismatch")
        except ValueError as exc:
            errors.append(f"{scene_id}: {exc}")
        direction = entry.get("direction", {})
        status = direction.get("status")
        if status not in ALLOWED_DIRECTION:
            errors.append(f"{scene_id}: invalid direction status")
        elif status == "applicable":
            path = _points(direction.get("path_xy"), 2, "path_xy", errors, scene_id)
            roi = _points(direction.get("transport_roi_xy"), 3, "transport_roi_xy", errors, scene_id)
            if len(path) >= 2:
                distance = sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
                               for a, b in zip(path, path[1:]))
                if distance < 0.05:
                    errors.append(f"{scene_id}: path is too short")
            if len(roi) >= 3:
                area = abs(sum(roi[i][0] * roi[(i + 1) % len(roi)][1] -
                               roi[(i + 1) % len(roi)][0] * roi[i][1]
                               for i in range(len(roi))) / 2)
                if area < 0.005:
                    errors.append(f"{scene_id}: transport ROI is degenerate")
        elif not direction.get("reason"):
            errors.append(f"{scene_id}: non-applicable direction requires a reason")
        review = entry.get("review", {})
        human_reviewed = review.get("status") == "human_reviewed" and bool(review.get("reviewed_by"))
        if strict_release and not human_reviewed:
            errors.append(f"{scene_id}: strict release requires named human review")
        elif not human_reviewed:
            warnings.append(f"{scene_id}: pending human review; prohibited from scoring")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--strict-release", action="store_true")
    args = parser.parse_args()
    errors, warnings = validate(json.loads(args.manifest.read_text()), args.strict_release)
    for message in warnings:
        print("WARNING", message)
    for message in errors:
        print("ERROR", message)
    print(f"transport annotations: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

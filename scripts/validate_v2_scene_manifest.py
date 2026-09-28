"""Validate structured SNF-Bench v2 scene and prompt manifests.

The validator separates independent base scenes from counterfactual variants,
checks the matched-horizon contract, and blocks evaluator-facing prompt text.
It reports allocation shortfalls without failing during authoring. Use
``--strict-release`` to require the frozen 96-scene, 16-per-medium suite.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "configs" / "snf_v2_scene_contract.json"

LEAKAGE = re.compile(
    r"\b(?:evaluators?|evaluation metrics?|dynamic degree|optical.flow score|"
    r"kv.cache|rope.limit|positional.encoding|attention collapse|"
    r"pond effect|frame\s+[\d,]+\s+onward|benchmark score|failure detector)\b",
    re.IGNORECASE,
)
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _point_list(value: Any, minimum: int) -> bool:
    if not isinstance(value, list) or len(value) < minimum:
        return False
    for point in value:
        if not isinstance(point, list) or len(point) != 2:
            return False
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   and 0.0 <= float(v) <= 1.0 for v in point):
            return False
    return True


def _error(errors: List[Dict[str, Any]], index: int, code: str, detail: str) -> None:
    errors.append({"index": index, "code": code, "detail": detail})


def validate(records: Any, contract: Mapping[str, Any], strict_release: bool = False) -> Dict[str, Any]:
    if isinstance(records, dict) and "records" in records:
        records = records["records"]
    if not isinstance(records, list):
        raise ValueError("scene manifest must be a list or {'records': [...]} object")

    errors: List[Dict[str, Any]] = []
    seen_variants = set()
    base_by_scene: Dict[str, Mapping[str, Any]] = {}
    media = set(contract["media"])
    tracks = set(contract["tracks"])
    splits = set(contract["splits"])
    regimes = set(contract["motion_regimes"])
    prefixes = contract["required_prefixes_s"]

    required = (
        "scene_id", "variant_id", "variant_kind", "tracks", "medium", "split",
        "model_visible_prompt", "duration_policy", "rigid_support_description",
        "moving_material_description", "motion_regime", "direction", "incoming",
    )
    for index, row in enumerate(records):
        if not isinstance(row, dict):
            _error(errors, index, "record_type", "record must be an object")
            continue
        missing = [key for key in required if key not in row]
        if missing:
            _error(errors, index, "missing_fields", ", ".join(missing))
            continue
        scene_id, variant_id = row["scene_id"], row["variant_id"]
        if not isinstance(scene_id, str) or not ID_RE.fullmatch(scene_id):
            _error(errors, index, "scene_id", "use lowercase letters, digits, '.', '_' or '-'")
        if not isinstance(variant_id, str) or not ID_RE.fullmatch(variant_id):
            _error(errors, index, "variant_id", "use lowercase letters, digits, '.', '_' or '-'")
        key = (scene_id, variant_id)
        if key in seen_variants:
            _error(errors, index, "duplicate_variant", f"duplicate {scene_id}/{variant_id}")
        seen_variants.add(key)

        kind = row["variant_kind"]
        if kind not in contract["variant_kinds"]:
            _error(errors, index, "variant_kind", str(kind))
        elif kind == "base":
            if scene_id in base_by_scene:
                _error(errors, index, "duplicate_base", f"second base for {scene_id}")
            else:
                base_by_scene[scene_id] = row
        elif not row.get("parent_variant_id"):
            _error(errors, index, "counterfactual_parent", "counterfactual requires parent_variant_id")

        if not isinstance(row["tracks"], list) or not row["tracks"] or not set(row["tracks"]) <= tracks:
            _error(errors, index, "tracks", f"must be a non-empty subset of {sorted(tracks)}")
        if row["medium"] not in media:
            _error(errors, index, "medium", str(row["medium"]))
        if row["split"] not in splits:
            _error(errors, index, "split", str(row["split"]))
        if row["motion_regime"] not in regimes:
            _error(errors, index, "motion_regime", str(row["motion_regime"]))

        prompt = row["model_visible_prompt"]
        if not isinstance(prompt, str) or not prompt.strip():
            _error(errors, index, "prompt", "model_visible_prompt must be non-empty")
        elif LEAKAGE.search(prompt):
            _error(errors, index, "prompt_leakage", LEAKAGE.search(prompt).group(0))
        for field in ("rigid_support_description", "moving_material_description"):
            if not isinstance(row[field], str) or not row[field].strip():
                _error(errors, index, field, "must be non-empty")

        duration = row["duration_policy"]
        if not isinstance(duration, dict) or duration.get("mode") != "matched_prefix":
            _error(errors, index, "duration_policy", "mode must be matched_prefix")
        elif duration.get("prefixes_s") != prefixes or duration.get("max_duration_s") != max(prefixes):
            _error(errors, index, "duration_policy", f"requires prefixes {prefixes}")

        direction = row["direction"]
        if not isinstance(direction, dict) or direction.get("status") not in contract["direction_statuses"]:
            _error(errors, index, "direction", "invalid or missing status")
        elif direction["status"] == "applicable":
            if not _point_list(direction.get("path"), 2):
                _error(errors, index, "direction_path", "requires >=2 normalized points")
            if not _point_list(direction.get("transport_roi"), 3):
                _error(errors, index, "transport_roi", "requires >=3 normalized points")
        elif not direction.get("reason"):
            _error(errors, index, "direction_reason", "not_applicable requires reason")

        incoming = row["incoming"]
        if not isinstance(incoming, dict) or incoming.get("status") not in contract["direction_statuses"]:
            _error(errors, index, "incoming", "invalid or missing status")
        elif incoming["status"] == "applicable":
            if not _point_list(incoming.get("boundary"), 2):
                _error(errors, index, "incoming_boundary", "requires >=2 normalized points")
            if incoming.get("target_side") not in ("left", "right"):
                _error(errors, index, "incoming_target_side", "must be left or right")
        elif not incoming.get("reason"):
            _error(errors, index, "incoming_reason", "not_applicable requires reason")

        if "i2v" in row["tracks"]:
            source = row.get("i2v_source")
            if not isinstance(source, dict) or not source.get("source_image_id") or not source.get("crop_policy"):
                _error(errors, index, "i2v_source", "I2V requires source_image_id and crop_policy")

    for index, row in enumerate(records):
        if not isinstance(row, dict) or row.get("variant_kind") != "counterfactual":
            continue
        base = base_by_scene.get(row.get("scene_id"))
        if base is None:
            _error(errors, index, "counterfactual_scene", "no base variant for scene_id")
        elif row.get("parent_variant_id") != base.get("variant_id"):
            _error(errors, index, "counterfactual_parent", "parent must be the scene's base variant")

    counts = Counter(row["medium"] for row in base_by_scene.values()
                     if row.get("medium") in media)
    base_count = len(base_by_scene)
    water_count = sum(counts[m] for m in contract["open_or_channel_water_media"])
    water_share = water_count / base_count if base_count else 0.0
    allocation = {
        "base_scene_count": base_count,
        "counterfactual_count": sum(isinstance(r, dict) and r.get("variant_kind") == "counterfactual" for r in records),
        "per_medium": {m: counts[m] for m in contract["media"]},
        "open_or_channel_water_share": water_share,
        "target_base_scenes": contract["base_scene_target"],
        "target_per_medium": contract["per_medium_target"],
    }
    release_failures = []
    if base_count != contract["base_scene_target"]:
        release_failures.append("base_scene_target")
    if any(counts[m] != contract["per_medium_target"] for m in contract["media"]):
        release_failures.append("per_medium_target")
    if water_share > contract["max_open_or_channel_water_share"]:
        release_failures.append("water_share")
    return {
        "schema_version": contract["schema_version"],
        "valid_records": not errors,
        "release_ready": not errors and not release_failures,
        "strict_release": strict_release,
        "errors": errors,
        "allocation": allocation,
        "release_failures": release_failures,
        "exit_failure": bool(errors or (strict_release and release_failures)),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--strict-release", action="store_true")
    args = parser.parse_args(argv)
    result = validate(json.loads(args.manifest.read_text()),
                      json.loads(args.contract.read_text()), args.strict_release)
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output)
    else:
        print(output, end="")
    return 1 if result["exit_failure"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

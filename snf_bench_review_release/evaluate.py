#!/usr/bin/env python3
"""Evaluate manifest-listed precomputed frame/flow prediction bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from snf_core import evaluate_arrays


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError("unsupported manifest schema_version")
    if not isinstance(data.get("items"), list) or not data["items"]:
        raise ValueError("manifest must contain at least one item")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--pred_dir", required=True)
    parser.add_argument("--out", default="run_outputs/metric_record.json")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    prediction_dir = Path(args.pred_dir).resolve()
    manifest = load_manifest(manifest_path)
    rows = []
    for item in manifest["items"]:
        item_id = str(item["id"])
        bundle_path = prediction_dir / item["prediction"]
        if not bundle_path.is_file():
            raise FileNotFoundError(f"missing prediction for {item_id}: {bundle_path}")
        with np.load(bundle_path, allow_pickle=False) as bundle:
            frames = bundle["frames_rgb"]
            flows = bundle["flows"]
            sample_fps = float(bundle["sample_fps"])
        record, _, _ = evaluate_arrays(frames, flows, sample_fps, seed=0)
        record = {"id": item_id, "prediction": item["prediction"], **record}
        rows.append(record)

    output = {
        "schema_version": "1.0",
        "metric_spec_version": "1.1",
        "flow_input": "precomputed adjacent-pair fields",
        "records": rows,
    }
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

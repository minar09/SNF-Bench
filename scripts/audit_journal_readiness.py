"""Read-only, aggregate-only evidence audit for the future SNF journal plan.

Reads the configured method project and this benchmark. Never reads a raw
human-response snapshot, runs a scorer, changes a study, or launches inference.
Counts describe available artifacts, not independent validity or completed
evaluation coverage. Output has no participant IDs or machine-local paths.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "snf-journal-readiness-audit-0.1"
DEFAULT_STUDY = "results/human_study/progress_oct29_kit/analysis_interim.json"

METHOD_EVIDENCE = (
    "AGENTS.md",
    "docs/129_SCENETETHER_FINAL_LOCK_AND_EVALUATION_OCT16.md",
    "docs/140_LONG_HORIZON_TABLES_AND_VISUALS_OCT20.md",
    "docs/143_REVIEW_APPLICATION_AND_ADDITIVE_STUDY_OCT21.md",
    "docs/156_COMPOSITE_FULL_DURATION_HUMAN_STUDY_OCT28.md",
    "docs/161_ACCEPTANCE_EVIDENCE_DECISION_PLAN_OCT28.md",
    "docs/164_CVPR_LLM_AND_HUMAN_STUDY_STATUS_OCT29.md",
    "docs/locked_final_scenetether_oct16.json",
    "CVPR_2027_AR_I2V/sec/fm_5_protocol.tex",
    "CVPR_2027_AR_I2V/sec/fm_7_limitations.tex",
    "CVPR_2027_AR_I2V/sec/st_X_suppl.tex",
    "CVPR_2027_AR_I2V/tables/main_human_summary.tex",
    "CVPR_2027_AR_I2V/tables/human_all_pairs_interim_oct22.tex",
    "CVPR_2027_AR_I2V/tables/main_all_horizons_oct23.tex",
    "tools/factorial_scoring/sourcefixed_metrics.py",
    "tools/factorial_scoring/sourcefixed_flow.py",
    "tools/factorial_scoring/latereg.py",
    "tools/snf_v2/make_prefixes.py",
    "tools/snf_v2/run_snf_traj.py",
    "tools/analysis/copy_brackets_oct21.py",
    "tools/human_study/analyze.py",
    "tools/human_study/prepare_extensions_oct21.py",
    "tools/human_study/prepare_composite_matched_oct28.py",
)


def read_json(path):
    return json.loads(path.read_text()) if path.is_file() else None


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evidence_file(root, relative):
    path = root / relative
    return {"path": relative, "exists": path.is_file(),
            **({"sha256": sha256(path)} if path.is_file() else {})}


def mask_summary(root, relative):
    folder = root / relative
    data = read_json(folder / "review_manifest.json") or {}
    records = data.get("scenes", {})
    entries = [value for value in records.values() if isinstance(value, dict)]
    reviewers = [str(value.get("reviewer", "")).lower() for value in entries]
    return {
        "path": relative,
        "label_png_count": len(list(folder.glob("*/labels.png"))),
        "review_record_count": len(entries),
        "review_status_counts": dict(Counter(str(value.get("status", "unspecified"))
                                             for value in entries)),
        "ai_reviewer_mentioned_count": sum("ai" in value or "claude" in value
                                            or "codex" in value for value in reviewers),
        "human_approval_mentioned_count": sum("human approval" in value for value in reviewers),
        "independent_human_annotation": "not established by status or reviewer-name counts",
        "review_manifest": evidence_file(root, relative + "/review_manifest.json"),
    }


def cohort_summary(root, relative):
    data = read_json(root / relative)
    if data is None:
        return {"path": relative, "status": "missing"}
    pairs = data.get("pairs", [])
    ids = data.get("ids", [])
    return {
        "path": relative,
        "status": "manifest_present_not_a_video_completion_check",
        "count": len(pairs) if "pairs" in data else len(ids),
        "category_counts": dict(Counter(row.get("category", "unknown") for row in pairs)),
        "declared_role": data.get("role"),
        "sha256": sha256(root / relative),
    }


def study_summary(data):
    """Whitelist aggregate counts; never copy participant maps or trial rows."""
    if not isinstance(data, dict):
        return {"status": "missing"}
    fields = ("registered", "responses", "pilot_sessions", "valid_complete",
              "incomplete_real", "attention_excluded_real")
    counts = {}
    # Whitelist known module names as well as keys; an identifier accidentally
    # placed in a counts dictionary must not be exported as a module label.
    for module in ("original", "comparisons", "long", "validation", "full60", "composite60"):
        row = data.get("counts", {}).get(module)
        if isinstance(row, dict):
            counts[module] = {key: row[key] for key in fields
                              if isinstance(row.get(key), int) and not isinstance(row[key], bool)}
    return {"status": "aggregate_snapshot_only_not_metric_admission",
            "collection_status": data.get("status"),
            "snapshot_utc": data.get("snapshot_utc"),
            "counts_by_module": counts,
            "warning": "Modules, source coverage, questions and exclusions differ; do not sum valid_complete as unique raters or treat response counts as comparison votes."}


def build_audit(method_root, benchmark_root=ROOT, study_relative=DEFAULT_STUDY):
    method_root, benchmark_root = Path(method_root), Path(benchmark_root)
    study_path = Path(study_relative)
    if (study_path.is_absolute() or ".." in study_path.parts or
            not study_path.name.startswith("analysis_")):
        raise ValueError("study input must be a relative aggregate analysis_*.json file")
    source = read_json(benchmark_root / "manifest/i2v_pairs_v2.json") or {}
    pairs = source.get("pairs", [])
    splits = read_json(benchmark_root / "manifest/v2_splits.json") or {}
    fresh_audit = read_json(benchmark_root / "manifest/fresh_split_audit.json") or {}
    return {
        "schema_version": 1,
        "audit_version": VERSION,
        "assessment_date_kst": "2026-10-30",
        "status": "artifact_inventory_not_independent_validation",
        "method_project": "configured method repository",
        "source_masks": {
            "benchmark": mask_summary(method_root, "results/factorial/source_masks"),
            "fresh": mask_summary(method_root, "results/factorial/source_masks_fresh"),
        },
        "cohorts": {
            "method_benchmark": cohort_summary(method_root, "results/snf_v2/TEST_SPLIT_FROZEN.json"),
            "method_fresh": cohort_summary(method_root, "results/fresh_sources/FRESH_SPLIT_FROZEN.json"),
            "method_primary_240s": cohort_summary(method_root, "results/snf_v2/HORIZON240_SUBSET_FROZEN.json"),
            "snf_split_counts": {key: len(splits[key]) for key in ("test", "seen_overlap", "stress_240s")
                                 if isinstance(splits.get(key), list)},
            "historical_fresh_duplicate_audit": {
                "n": fresh_audit.get("n"), "n_without_detected_match": fresh_audit.get("n_unseen"),
                "meaning": "no match detected in that audited pool; not proof of current journal-test independence",
            },
        },
        "rights_metadata": {
            "snf_i2v_pairs": len(pairs),
            "nonempty_licence_fields": sum(bool(row.get("licence") or row.get("license")) for row in pairs),
            "meaning": "metadata completeness only; no rights clearance inferred",
        },
        "human_study": {"analysis_artifact": evidence_file(method_root, study_relative),
                        **study_summary(read_json(method_root / study_relative))},
        "method_evidence": [evidence_file(method_root, relative) for relative in METHOD_EVIDENCE],
        "journal_evidence_still_required": [
            "independent role annotation and visibility validation",
            "new confirmation sources not used to design methods or select metrics",
            "held-out natural-periodicity and replay/intent validation",
            "multi-family human metric alignment with source/rater uncertainty",
            "native T2V/I2V journal-profile adapters including author methods",
            "rights, portability and release/overlap verification",
        ],
        "raw_participant_data_exported": False,
        "code_metrics_or_existing_results_changed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method-root", type=Path)
    parser.add_argument("--study-analysis", default=DEFAULT_STUDY)
    parser.add_argument("--output", type=Path, default=ROOT / "manifest/journal_readiness_audit_2026_10_30.json")
    args = parser.parse_args()
    method_root = args.method_root
    if method_root is None:
        from _paths import resolve
        method_root = Path(resolve("method_repo"))
    if not method_root.is_dir():
        parser.error("method repository directory does not exist")
    result = build_audit(method_root, study_relative=args.study_analysis)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(f"Wrote {args.output.name}; aggregate evidence only, no scoring or participant export")


if __name__ == "__main__":
    main()

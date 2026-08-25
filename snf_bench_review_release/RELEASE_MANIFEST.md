# Release manifest

This is a whitelisted anonymous review export. Only the files listed below are
intended to ship.

- `README.md`: setup, scope, and smoke-test instructions.
- `USAGE_NOTICE.md`: review-use notice.
- `requirements.txt`: lightweight smoke-test dependencies.
- `check_release.py`: whitelist and identity/internal-data release gate.
- `benchmark_manifest.json`: one-record example manifest.
- `configs/common_t2v.yaml`: recorded common T2V evaluation configuration.
- `snf_core.py`: metric post-processing and partition implementation.
- `evaluate.py`: manifest-driven metric evaluator.
- `make_partition.py`: partition export and visual preview.
- `generate_perturbations.py`: deterministic example and perturbation-curve generator.
- `bootstrap_analysis.py`: paired percentile-bootstrap analysis.
- `smoke_test.py`: one-command end-to-end verification.
- `metric_spec_v1.1.md`: frozen metric specification.
- `example_predictions/example_scores.csv`: anonymous paired-score fixture.
- `example_predictions/translation_*.npz`: generated synthetic prediction fixtures.
- `expected_outputs/*.json`: deterministic metric, perturbation, and bootstrap outputs.

Explicitly excluded: repository history, remotes, usernames, absolute paths,
internal experiments or models, private videos, participant responses, hosted
media links, cache files, and incomplete sweep records.

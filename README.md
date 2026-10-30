# SNF-Bench

Evaluation of continuous nature videos with a fixed camera: source/support
fidelity, intended material motion, continuity and task validity.

The publication plan has two stages. SceneTether uses SNF v2 as a versioned
evaluation protocol for its CVPR 2027 method paper. A later standalone SCIE
journal paper will contribute independent measurement validation, broader
T2V/I2V coverage and a reusable evaluation resource. Its planned panel includes
Steady-Forcing and SceneTether alongside external released systems.

- [Current publication roadmap](docs/PUBLICATION_STRATEGY_AND_JOURNAL_ROADMAP.md)
- [SceneTether code/evidence reuse audit](docs/SCENETETHER_REUSE_AND_GAP_AUDIT_2026_10_30.md)
- [Journal venue assessment](docs/JOURNAL_VENUE_ASSESSMENT_2026_10_30.md)
- [Publication overlap ledger](docs/PUBLICATION_OVERLAP_LEDGER.md)
- [Current CVPR-era protocol](docs/SNF_V2_EVAL_SPEC.md)
- [WACV review assessment](docs/WACV2027_OFFICIAL_REVIEW_ASSESSMENT.md)
- [Version identities](docs/VERSIONS.md) and [contestant eligibility](docs/EXCLUSIONS.md)

Historical records remain frozen. The future journal plan is provisional;
candidate kernels and method-oriented human studies do not by themselves
establish independently validated benchmark scores. Planning decisions are
recorded in [the journal plan](configs/snf_journal_plan.json).

For a read-only inventory of reusable method-project assets, configure
`SNF_METHOD_REPO` and run:

```bash
python scripts/audit_journal_readiness.py
```

The audit emits aggregate counts and artifact hashes. It performs no generation,
scoring, study modification or raw participant export. Machine-local paths
belong in environment variables or ignored `configs/local_paths.json`.

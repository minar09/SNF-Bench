# SceneTether code and evidence audit for the SNF journal upgrade

Audit date: 2026-10-30 KST. Read-only review of the configured method repository,
including its root execution policy, current LaTeX, immutable method lock,
scoring/adaptation code, generated result tables, source-role records and
aggregate study analyses. The journal plan is
`PUBLICATION_STRATEGY_AND_JOURNAL_ROADMAP.md`.

The attached draft_02/draft_05 critiques are useful historical advice. Current
paper sources and later evidence records take precedence for completion and
sample counts. No running jobs, frozen definitions, study responses or hosted
settings were modified for this audit. No raw participant export is included.

## 1. The current method paper already makes the right distinction

`CVPR_2027_AR_I2V/sec/fm_5_protocol.tex` calls SNF v2 a source-fixed protocol,
states that masks were reviewed with AI assistance and are not independent
human annotations, and acknowledges that the 48 sources informed the research
program. Its benchmark-validation supplement explicitly reserves perceptual
validation until independent challenge and human evidence exist.

The current description distinguishes compensated RAFT activity at 8 Hz and
288-pixel image height from native-resolution, registered Farneback paired
activity over 40–60 seconds. These estimators have different units, intervals
and missing-data populations. They must not become one journal activity column
through a name change. Three metric suites run on the same sources are not
three independent datasets.

The final lock is `docs/locked_final_scenetether_oct16.json`, naming
`echo_nfpb1_h1_fm_tether100_lr`. Its frozen pipeline's `_forget_update` builds
generation-side roles from the student's clean latents and states that it does
not read an evaluation mask. This is useful separation from the source-fixed
scoring masks. It does not establish independence of the scientific design:
source fidelity is a target of both the method and its appearance evaluation.
The paper itself discloses overlap of tethered and scored support. Journal
validation therefore needs copying, redraw, integrity and independent human
controls, not only more source PSNR measurements.

## 2. What the code can contribute

Paths below are relative to the method repository, resolved locally by
`SNF_METHOD_REPO` or the ignored path configuration. They are reusable kernels
and patterns, not permission to import experiment-specific globals wholesale.

| Component | Code reviewed | Reuse and required work |
|---|---|---|
| Source-fixed reference and conditional scoring | `tools/factorial_scoring/sourcefixed_metrics.py` | Already ported in SNF `scripts/snf_sourceref.py`; preserve parity identity and add a separately versioned journal policy |
| Long-baseline registration accounting | `tools/factorial_scoring/latereg.py` | Hash-bound per-frame counts and parity are reusable; generalize the hardcoded 40–60-second window and separate instrument failure from scene failure |
| Native-resolution compensated activity | `tools/factorial_scoring/sourcefixed_flow.py` | Reuse explicit registered/fallback counts; replace global CF++ cell discovery with a typed input record |
| Same-rollout prefixes | `tools/snf_v2/make_prefixes.py` | Strong decoded-frame verification and frame-count/fps checks; migrate a portable adapter without hardcoded scene/variant registry |
| Fixed-second full-flow trajectories | `tools/snf_v2/run_snf_traj.py` | Correct effective sample rate, resumable traces and prefix truncation; automatic early-flow masks retain circularity, so source-role integration is still required |
| Copying and composite controls | `tools/analysis/copy_brackets_oct21.py`, current supplement's output-composite specification | Preserve pristine parent/run hashes and generation-side maps; keep early unfeathered pasteback distinct from later feathered untethered/FramePack composites |
| Blinded, versioned studies | `tools/human_study/prepare_extensions_oct21.py`, `analyze.py`, full-duration/matched-composite preparation | Reuse module digests, playback checks and crossed resampling; create a separate journal study instead of pooling post-result modules |
| Metric-human validation kernel | `tools/human_study/analyze.py::construct_validation` | Existing exploratory source-split thresholding and correlation are useful; exclude neither ties nor difficult missing scores without reporting their effect, and add rater uncertainty and model-family holdout |
| Reproducible method identity | method lock, immutable code and RUN/score records | Journal SceneTether adapter can reference the exact method; do not substitute historical H1-FM or a current mutable checkout |

The old validation kernel maps activity to a motion question, and its docstring
explicitly describes that question partly in terms of consistency/naturalness.
The newer optional study has a separate activity-amount question. Use the
proper question for each construct; a flow-magnitude correlation with generic
naturalness is not valid merely because the function computes it. Existing
source-clustered metric-validation intervals also do not automatically account
for rater uncertainty. A declared GLMM sensitivity is described but not
implemented in that code path.

## 3. Verified assets and independence limits

| Item | Observed state | Interpretation |
|---|---|---|
| Benchmark source maps | 48 label PNGs; all 48 review records approved | Reviewer strings name AI review on all 48; four explicitly mention project-lead human approval. This is not independent double annotation |
| Fresh source maps | 24 label PNGs; all 24 review records approved | Reviewer records name Claude AI review; separate human validation remains required |
| Method source cohorts | Frozen manifests contain 48 benchmark and 24 fresh pairs | Seventy-two inputs/maps are real assets, not 72 untouched journal test scenes |
| Older SNF split | 41 test / seven seen-overlap; older stress set nine | Retain those historical identities rather than relabeling all 48 independent |
| Method primary 240-second set | Frozen manifest contains 12 IDs | Different from the older SNF nine-source stress set; expanded all-48 analyses are secondary |
| Fresh duplicate audit | SNF artifact reports no detected pool match for 24/24 | Useful automated screening at that audit date; it does not establish absence of every related scene or later development exposure |
| Source rights metadata | SNF I2V manifest has nonempty license fields for 2/48 | Verify rights per source before release; frozen method cohort manifests do not themselves supply license clearance for the fresh 24 |

Current generated main tables contain 60/120/240-second rows for SceneTether
and many CF++ controls/ports. Some rows remain unavailable; a table is not a
proof that every source/seed/suite completed. Import from per-video records
with hashes, endpoint eligibility and attempted/failed counts. A complete
native multi-family T2V/I2V journal panel has not been established by these
method-family comparisons.

`docs/140` correctly distinguishes separately requested duration endpoints from
four checkpoints of the same 240-second rollout. Prefix tooling already exists
upstream despite older SNF documents saying it is absent. Port and validate
that capability; do not silently reinterpret the CVPR endpoint tables as
prefix measurements.

## 4. Human evidence: real progress, limited inference

The audited aggregate analysis is
`results/human_study/progress_oct29_kit/analysis_interim.json`, snapshot
`2026-10-29T05:34:33.276Z`. It marks collection interim and descriptive. Counts
of valid completed sessions by module are original 12, short comparisons 5,
four-minute 5, baseline validation 5, full-minute reference 4 and composite 4.
These are module counts, not a sum of unique people. Pair-specific rater and
source coverage can be lower and differs across questions. The raw responses
are private; only aggregate evidence belongs in this audit.

The generated original-study table gives SceneTether versus spatial Echo
motion preference 55.7% [37.3%, 72.7%], alongside stronger source-preservation
preference. That illustrates why source fidelity and motion naturalness must
remain distinct. The baseline-only module provides promising challenge
judgments, but its small number of comparator policies and shared backbone
do not establish cross-model metric validity. A catastrophic k=6/k=3 contrast
can inflate apparent pooled agreement; validate subtle cases separately.

Full-minute composite judgments and full-four-minute judgments are different
experiments. Older and matched-encoding composite modules are also distinct.
Read-only snapshots, original-exclusion analyses and broader all-response
sensitivities must not be merged or selectively chosen for the preferred
outcome. Consent and institutional-review reporting need accurate author
confirmation; no new approval or secondary-use permission is inferred here.

## 5. What changes the future benchmark design

The later composite is genuinely competitive on some source metrics. Its
extra compression history is documented. This is evidence for building a
metric-gaming/measurement challenge set, not for designing a new score that
forces SceneTether to win. Include stills, blurred/noisy motion, looped flow,
composites and invented objects alongside native generated and real footage.

Some source frames with the largest fidelity margins show invented objects in
the paper's own failure gallery. A selected rigid ROI cannot establish the
integrity of the entire scene. Add source-versus-video integrity judgments
and independently validated whole-scene checks. The out-of-scope articulated
examples motivate an application extension, but are selected, unscored and
have unresolved rights; they are not a validated subject-animation dataset.

The journal's strongest new result would be an independent meta-evaluation:
which compact measurements predict each human-labeled failure, at what
coverage and cost, on unseen scenes and external model families. Reusing the
existing toolkit makes that feasible. Its existence alone does not complete
the study.

## Reproducible inventory

Run `scripts/audit_journal_readiness.py` with `SNF_METHOD_REPO` configured, or
provide `--method-root`. It only reads selected artifacts and aggregate
analysis; it does not decode videos, score outputs, change study records or
launch GPU work. The stored audit is
`manifest/journal_readiness_audit_2026_10_30.json`. Its existence/hash checks
establish the reviewed inputs, not correctness of every underlying result.

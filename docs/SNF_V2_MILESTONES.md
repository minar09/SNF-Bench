# SNF-Bench v2 implementation milestones

Status: execution plan, 2026-09-28. The design and validity requirements are
in `SNF_V2_TASK_DESIGN.md`. This plan extends, and does not silently supersede,
`NEXT_VENUE_PLAN.md`. Existing v1.1 records remain frozen provenance.

## M0 — audit and protocol, no generation

**Deliver:** current-asset prompt audit; structured prompt-authoring contract;
validation matrix with expected response and desirability signs
(`SNF_V2_VALIDATION_MATRIX.md`); cost/variance
pilot plan. Audit all model-visible prompt text for evaluator instructions and
contradictions. Mark the existing horizon sets as unmatched. This repository's
`scripts/audit_prompt_design.py` is the first implementation step.

**Exit:** the audit runs reproducibly, reports counts and leakage candidates,
and fails the release gate for model-visible benchmark instructions. Human
review still decides whether a flagged prompt is truly defective.

## M1 — repair the current spatial claim, existing videos

**Deliver:** reviewed shared-source I2V masks; frozen first-frame-blind role-labeling policy for T2V;
layout-aligned T2V shared-pixel-mask control; rescored fBD/NBF/MCFF/FP/DLR/DAR;
VBench background consistency through existing perturbations; full response
matrix and corrected Table 1. Diagnose high-NBF outliers and fBD abstention.

**Exit:** mask disagreements, rank sensitivity, score coverage, and incumbent
comparison have paired prompt-level intervals. NBF/DAR are repaired or scoped
according to validation; FP is described as a decay indicator if it cannot
separate systems. Do not promote a revised metric under the v1.1 name.

## M2 — task-specific motion probes, existing videos plus corruptions

**Deliver:** prompt-annotated transport ROI/path pilot; support-registration
trajectory; signed transport and reversal probes; dynamic-region replay probe.
Construct foreground-only reversal, zoom-vs-incoming, ping-pong, exact-loop,
reset-seam, photometric, and natural-periodic controls. Add per-probe
`unscorable` reasons. Run cheap probes on existing videos before dense GPU
rescores.

**Exit:** held-out corruption detection, real-footage false positives,
abstention, mask/backbone sensitivity, and runtime are reported. A probe that
only recognizes its own synthetic corruption stays exploratory.

## M3 — benchmark assets and human reference

**Deliver:** roughly 96 independent base scenes with structured annotations,
counterfactual variants grouped by scene family, a matched 60/120/240-second
core, licensed real fixed-camera anchors, native-pipeline T2V rows, and a
multi-seed subset. Pilot prompt count with variance/power; freeze splits before
threshold tuning. I2V source masks are shared; T2V masks are first-frame-blind.

**Exit:** coverage and licensing audit pass; each scored stratum is populated;
no model-visible evaluator instructions; horizon analysis uses matched scenes;
the native/common settings and failed generations are transparently reported.

## M4 — validity study and release

**Deliver:** blind multi-rater axis judgments on stratified outputs and
adversarial controls, agreement and `cannot tell` rates, held-out model/prompt
validation, incumbent comparison, paired uncertainty, cost-vs-accuracy audit,
datasheet, versioned code/records, DOI and maintenance policy.

**Exit:** each public claim has an independent evidence row. Release only the
diagnostics that beat their task-specific baselines or explain a distinct,
human-validated failure. Report null results and category-specific failures.

## Current execution status

M0 documentation and audit tooling are in place. The canonical T2V files have
23/6/4 prompts at 60/120/240 seconds and no exact cross-horizon matches.
Across all nine T2V text files (57 prompt lines), eight 240-second prompt lines
contain model-visible evaluator instructions, including all four canonical
240-second prompts. See
`manifest/prompt_design_audit.json` for line-level findings. The audit flags
possible contradictions for human review rather than deleting prompts.

An M1 read-only control is complete: `scripts/paired_incumbent_resolution.py`
compares the seven public T2V systems on their 23 shared 60-second prompts,
with paired, category-macro bootstrap differences. NBF intervals exclude zero
for 14/21 system pairs; VBench background-consistency intervals do so for
13/21. These are unadjusted descriptive intervals, not evidence that either
metric matches human judgments. See `manifest/paired_incumbent_resolution.json`.
This result weakens the earlier broad NBF-resolution claim.

The incumbent perturbation path is also implemented as an optional
`--with-vbench-bc` mode in `scripts/validation_suite.py`, using VBench's CLIP
transform and background-consistency formula on identical validation-sampled
frames. A one-clip, 24-frame pilot on translation and late freezing is saved in
`manifest/validation_response_bc_pilot.json`. The incumbent score rose from
0.910 at baseline to 0.929 under maximum translation and 0.969 under 75%
late freezing. This is a code-path sanity check, not a validity result: it is
one clip, uses strided frames, and is not the published full-video VBench
score. A subsequent category-stratified pilot (five media, one clip each)
shows background consistency increasing under maximum translation in two of
five clips and under 75% late freezing in five of five. See
`manifest/bc_stratified_pilot_summary.json`. It uses 24 strided frames and is
not a full incumbent validation; the full protocol must use enough clips per
medium and check official full-video sampling.

M1 mask infrastructure is now ready for annotation, following
`SNF_V2_MASK_PROTOCOL.md`. The alignment audit found 30/30 source-to-first-frame
pairs geometrically aligned after direct resize in each of three 60-second I2V
settings (90/90 total); this is a pilot, not evidence for every setting.
A real 5-second code-path check found zero factor difference when the automatic
mask was fed through the external-mask interface. That check is software parity,
not independent mask validation. The external path refuses unreviewed labels,
records source/mask hashes and alignment evidence, and writes to a separate
pilot tree. No reviewed mask PNGs exist yet, so no reviewed-mask metric result
has been claimed.

A read-only NBF distribution audit shows that Causal-Forcing's high T2V-60s
NBF is broad across prompts: median 90.03 over 23 prompts, with the three
largest prompts contributing 24.9% of the sum. fBD is non-null on all 23
records, but the existing scorer stores no ORB match counts; value presence
must not be described as match reliability. See
`manifest/spatial_score_diagnosis.json`.

A held-out automatic shared-partition control now has 8/8 paired I2V-60s
rescores across four media and two scored systems. It keeps each prompt's
`self_forcing` early-flow partition fixed while rescoring the other outputs.
The exact v1.1 comparison is in `manifest/shared_auto_control/i2v/60s/comparison.json`
and the protocol and factor table are in `SHARED_AUTO_CONTROL.md`. The largest
observed fBD shift is 19.65 to 10.04 for a windborne clip; NBF and FP also
change. This is evidence of partition sensitivity, not mask validity: the
shared masks are unreviewed and anchor-dependent. Reviewed masks and the full
prompt/system panel remain M1 exit requirements.

The frozen geometry, motion, and nuisance sweeps are now consolidated by
`scripts/validation_response_analysis.py` into 63 paired response rows. The
analysis corrects two endpoint errors in the earlier exploratory summary:
short repetition cycles are more severe (6 frames, not 24), and mask erosion
and dilation must each be compared with radius 0. It separates observed
response from desirability, uses sample-SD paired effect sizes, adds a
category/clip hierarchical bootstrap, and stores the full table in
`tables/validation_response_matrix.md`. Under the frozen admission rule both
DLR and DAR fail nuisance selectivity, so the drift-leakage axis leaves the
headline set. NBF is scoped to translation and scale because its rotation
response is weaker than its mask-boundary response. FP remains a decay
indicator reported with MCFF magnitudes. These decisions still need backbone,
feature-match coverage, reviewed-mask, and human-validity checks before release.

The remaining M1 work and M2-M4 still require rescoring, annotation,
generation, or human collection and are not claimed complete. This order
protects the study from tuning measures against the same seven systems and
23 T2V-60s prompts used to define the problem.

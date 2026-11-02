# SNF-Bench++: TCSVT execution protocol and evidence gates

Decision date: 2026-11-01 (Asia/Seoul). **Target: IEEE Transactions on
Circuits and Systems for Video Technology (TCSVT).** The [IEEE society
scope](https://ieee-cas.org/publication/tcsvt) includes video processing,
analysis, synthesis, learning and software systems and accepts original
contributions and expanded conference versions. The society page displayed an
impact factor of 8.4 on the decision date without identifying its JCR year;
do not cite it as a year-specific JIF without checking. Verify the exact
journal title and ISSN against the current Clarivate Master Journal List/JCR
for SCIE status, category and year before submission; that independent check
has not been completed. Fees, page limits and the journal's current author
instructions also require submission-time verification. Do not infer acceptance,
quartile or review time. IEEE Access is excluded by the author's instruction.
The Exa search connection returned an exhausted-credit error; the official
publisher scope and CVPR policy were accessed directly.

The independent benchmark measurement paper follows the SceneTether CVPR
submission and review; consult the then-current [CVPR dual-submission policy](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines)
and [overlap ledger](PUBLICATION_OVERLAP_LEDGER.md) before journal submission.
Do not submit a substantially overlapping concurrent manuscript. The target
is a decision, not a claim that present evidence meets its standard.

The journal upgrade is named **SNF-Bench++**. This is a publication name, not
a retroactive renaming of SNF-Bench v1, SceneTether-era v2, sourcefixed-1.0,
or their stored score records. Its final measurement version remains to be
frozen and independently validated.

## Frozen execution decisions

1. **Core.** Fixed-camera, continuous natural-process T2V and I2V; separate
   human and animal extensions only when their subject/visibility and motion
   construct have their own validated study. Report cohorts by physical medium
   and regime; water includes channel, falling, oscillatory and accumulation.
2. **Horizons.** Nominal 5 s control, 60/120/240 s main, 480/600 s stress only
   where justified. Compare prefixes of the same rollout for accumulation and
   separately requested endpoints in a distinct analysis. Use equal sampled
   intervals and record the actual frame count, fps, window and codec.
3. **Reuse before execution.** Search project roots and the latest inventory by
   full video/content identity, model/checkpoint, image/prompt, seed and
   configuration. Reuse existing renders and scores. Under the user's current
   instruction generate and score only new model/image/prompt outputs; do not
   rescore old videos. A missing inventory entry or partial provenance is not
   proof of novelty; inspect before scheduling. Never pool old v1, sourcefixed
   v1.0 and new identities under one name.
4. **Model panel.** Include author-affiliated Steady-Forcing and SceneTether,
   their matched simple controls, and external released native T2V/I2V methods.
   Freeze native/adapted identity, revisions, weight hashes, precision, sampler,
   resolution, horizon, latency and seed policy; disclose model/compute
   differences. Select external families for coverage and availability before
   results; separately report scenes/outputs unavailable for each model.
5. **No single naturalness score.** Keep support/source fidelity, intended
   material behavior, continuity/replay and whole-scene integrity separate.
   Human/animal articulation adds separate identity, anatomy and contact axes.
   fBD is diagnostic; activity and recurrence are not naturalness; retain
   historical `dE_static_src` with its float32 limitation, and assign any
   corrected method a new measurement identity. Admit no unvalidated kernel.

## Ordered milestones and review gates

| Gate | Deliverable | Required completion evidence; current status |
|---|---|---|
| J0 | Freeze reuse/provenance and prior-publication ledger | Inventory, exact output identities and disclosure map exist; external roots and journal-overlap check remain open. |
| J1 | Independent source and model cohort | Rights-cleared fresh source families; medium-by-regime accounting, duplicate/near-duplicate review; predeclared independent confirmation split and model-family holdout. Existing 48+24 are exposed development/replication, not journal confirmation. |
| J2 | Source-only roles and observability | Two independent annotators on a stratified source subset; support/material/overlay/subject/ignore plus ambiguity and visibility; inter-annotator agreement, adjudication, and score/rank/coverage sensitivity across independent maps and erosions. |
| J3 | Candidate measurement meta-evaluation | Paired controls for drift, freeze, loop/reset/recolor, reversed/ping-pong and unrelated motion, nuisance photometric/partition changes; real surf/flame/foliage negatives and subject-only motion. Report errors, abstentions and paired effects with uncertainty; compare same-input VBench dimensions and simple baselines. Select thresholds only on development. |
| J4 | Human construct study | Freeze the protocol below after a pilot, feasibility/precision calculation and ethics/consent determination. Collect independent multi-system judgments, held-out sources/models and separate questions; do not assert completion from earlier interim study modules. |
| J5 | Full panel and reproducibility | Multi-seed native/adapted systems on identical inputs and applicable horizons; track failed and unscorable outputs, cold/warm runtime on uncontended GPU, memory and versions. Bootstrap source families, not frames or repeated windows. |
| J6 | Submission readiness | Freeze figures, release rights, clean-clone reproducibility, independent confirmation results and overlap disclosure; authors inspect every claim and finalize TCSVT instructions/indexing/fees. |

## Human metric-validation study: design ready for pilot, not preregistered

**Purpose.** Estimate whether each metric measures its intended observable
construct on real model outputs and targeted controls, including difficult
near-ties. We are not measuring a generic model preference or treating a
large score gap as a human label.

**Sampling and blinding.** Define source-family strata across medium, regime,
track, model family, horizon, difficulty, motion and coverage; sample before
viewing confirmation judgments. Draw real outputs from author and external
families, plus predeclared freeze, drift, replay, periodicity and wrong-way
controls. Partition by source family and hold out at least one model family;
never put transformations of the same parent across development and test.
Blind system names, metric values and intervention labels; counterbalance
presentation/order, preserve uniform playback and encoding, randomize trial
assignment, and log watched interval, device and completion. Natural video
negatives need separate source and rights provenance.

**Distinct ratings.** Ask separately: (1) fixed support/camera stability;
(2) source or prompt scene integrity, including additions/deletions;
(3) amount of motion of the *specified material* (not quality); (4) plausibility
of that material's evolution; (5) requested direction, only where actually
observable and well specified; (6) exact-looking repeated sequence or reset
versus plausible naturally periodic motion. Use clear ordinal anchors and
`cannot tell/not applicable` per question; do not force direction or replay on
ineligible content. Subject-extension studies additionally separate identity,
anatomy/articulation and contact from environment integrity. A rater need not
infer an unseen physical cause.

**Length and task.** Full-duration questions require viewing the actual full
interval or a clearly specified verified sequence; a short-window response is
not a full-duration label. Pilot cognitive load, browser playback, screen size,
retention and completion time. Balance a manageable number of tasks per rater
while guaranteeing repeated ratings per clip and shared anchor trials for
agreement. Set quantitative sample size and stopping rules using a pilot-based
simulation for scene and rater variance and desired interval widths for each
primary construct, with material strata and expected abstentions included.
No fixed participant count guarantees validity.

**Analysis plan.** Before confirmation, freeze population, primary constructs,
control definitions, threshold-training rule, raters-per-clip, exclusions,
cluster resampling, target precision, multiplicity and sensitivity analyses.
Report per-axis rater agreement, distributions, cannot-tell/not-applicable and
item/condition counts. Analyze ordinal human outcomes against the corresponding
metric and incumbent with source and rater clustering or a prespecified
crossed-effects model; include coverage and failures. Report replay detection
at development-selected thresholds including false positives on natural
periodic controls, with source-family-clustered intervals. Do not pool
correlated trials or existing study modules as independent participants.
Report ties and ambiguous clips; no metric, control or author method is
required to win. Final raters, compensation, privacy, consent and institutional
review or exemption status must be accurately established before collection.

## Current data and implementation state

The [existing score report](EXISTING_SCORE_COMPARISONS_2026_10_30.md)
provides matched 60 s and endpoint-window comparisons alongside historical
T2V. The [subject extension inventory](JOURNAL_SUBJECT_EXTENSION_AND_MODELS_2026_10_30.md)
is an exposed feasibility set, not a confirmation set. The
[TCSVT LaTeX draft](../JOURNAL_TCSVT/main.tex) is a working skeleton with
explicitly pending results. No new raters have been recruited and no journal
confirmation experiments have been completed as part of this decision.

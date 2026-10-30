# SNF-Bench publication strategy and journal roadmap

Project-lead decision recorded 2026-10-30 KST. This supersedes older
standalone-conference venue preferences and permanent exclusion of author
methods for the **future journal protocol**. Existing WACV results, SceneTether
measurements, study modules and experimental locks retain their identities.
The machine-readable plan is `configs/snf_journal_plan.json`; it is not an
executable scoring specification.

## 1. Two publications with distinct central contributions

| Publication | Central question | Role of SNF |
|---|---|---|
| SceneTether, CVPR 2027 | Does the proposed source-aligned value intervention improve long I2V animation under matched controls? | A named, versioned, source-fixed evaluation protocol, with its limitations disclosed |
| Standalone SNF journal paper | Do compact task-specific measurements identify sustained natural-process failures reliably, agree with independent judgments, and generalize across systems and tracks? | The independently validated measurement contribution and reusable benchmark |

The journal paper can reuse v1 perturbations, historical T2V runs and v2
infrastructure as attributed evidence. Its new contribution should include
validated failure measurements, independent annotations and subjective
evidence, a prospective confirmation population, and reproducible native
comparisons. Simply concatenating v1 and v2 does not establish those results.
Use “unified framework” for shared interfaces and reporting, not for pooling
different masks, references, units or horizons into one table cell.

The existing preprint, rejected WACV submission, SceneTether paper and any
Steady-Forcing publication/submission belong in the publication-history ledger.
Prepare a related-work and reuse statement, plus an editor-facing cover-letter
comparison, from that ledger. A WACV rejection is not an archival acceptance,
but the publicly available SNF preprint still needs attribution.

The recommended sequence is SceneTether submission and review, independent
benchmark development, then journal submission after the CVPR decision when
the manuscript's overlap can be assessed accurately. The official CVPR 2027
guidelines currently prohibit substantially similar concurrent journal work;
the page defines substantial similarity as at least 20% content overlap.
Changing the benchmark name is not a workaround. Do not reduce scientific
distinctness to a text-similarity percentage.
[Official CVPR policy](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines).

## 2. What is reusable and what remains open

The detailed code and evidence review is
`SCENETETHER_REUSE_AND_GAP_AUDIT_2026_10_30.md`. The main findings are:

- 48 benchmark and 24 fresh-source role maps exist. Review metadata records
  AI reviews and limited project-lead approvals; these are not independently
  double-annotated ground truth.
- Source-reference scoring, registration sidecars, fixed-time trajectory
  adapters, verified-prefix tooling, copying/composite controls, multi-seed
  analysis and a hosted study implementation are reusable components.
- The current method paper has real multi-minute measurements. Its
  separately requested duration endpoints, within-one-rollout checkpoints,
  12-source primary stress set and expanded all-48 results are distinct
  populations. SNF's earlier nine-source stress set is another population.
- Human judgments now exist, including baseline-only and full-duration
  modules. Collection remains interim; modules have different sources,
  questions, encoding histories, counts and exclusions. Their existence does
  not validate every SNF axis.
- All original 48 sources informed the research program. The fresh 24 were
  evaluated and inspected too. They can support replication and instrument
  development; they are no longer untouched journal confirmation sources.
- Source copying and competitive output composites show why fidelity must
  be interpreted with activity, continuity and integrity. The benchmark
  must remain useful even if a simple composite matches an author method.

Thus the WACV mask, diversity, replay and human-validity objections have
partial technical repairs. They are not all closed by asset counts or a
target of 15 raters.

## 3. A compact measurement design

Use four reporting families, with a small admitted core and a diagnostic
appendix. Freeze exact members only after candidate meta-evaluation.

| Family | Core evidence to qualify | Counterexamples that must be resolved |
|---|---|---|
| Source and support fidelity | Source-relative appearance plus absolute support displacement and registration coverage | Early redraw; same-layout retexturing; coherent camera drift; local deformation; invented objects outside conservative ROIs |
| Material behavior | Activity/active area plus signed path or boundary evidence where observable | Frozen sharp source; noise/flicker; reversed or ping-pong flow; boat motion hiding frozen water; zoom imitating approach |
| Continuity and replay | Whole-video sequence recurrence and discontinuity trajectories | Exact/recolored loops and resets, alongside legitimate surf, flame cycles and occlusion |
| Human task validity | Separate medium identity, source integrity, motion intent and naturalness judgments | Wrong medium; physically implausible but energetic motion; preference dominated by fidelity rather than motion |

Retain fBD as a geometric diagnostic. Retain historical PSNR/encoded-Lab
results under their original definitions; corrected float64 mean color and
pixelwise CIEDE2000 need distinct identities. Detail retention is not motion
and activity is not naturalness. A tracker/flow confidence failure is not
automatically a generation failure. Publish these distinctions as reason
codes and coverage, not merely prose qualifications.

Benchmark VBench-I2V/Long, appropriate VBench-2.0 dimensions, WorldScore,
DEVIL/DIVE and motion-specific comparators on shared inputs where applicable.
Distinguish official runs from region-masked or window-adapted variants.
Report agreeing incumbents and cases where the SNF candidate adds no value.
TRAJAN/FVMD and learned registration are candidate instruments, not automatic
solutions to natural flow or long-lag replay. The Oct 8 research review
remains the source for their applicability limits; refresh release versions
at the journal freeze.

## 4. Broaden coverage in stages

Keep a strong continuous fixed-camera nature core in both T2V and I2V.
Broaden first to multiple materials, precipitation overlays, lighting changes,
occlusion, accumulation and mixed subject/material motion. These directly
test the WACV counterexamples without changing the core task.

Moving cameras and articulated people/animals can form separately qualified
extension tracks. A camera motion requested by the prompt cannot receive the
same penalty as forbidden drift in the fixed-camera track. Such a track needs
its own camera-conditioned support rule, role/visibility annotation and
human validation before public scores. Selected unscored SceneTether examples
with unknown image rights are leads for task design, not release-ready data.

Represent both **medium** and **motion regime**. The current nine-regime set
has channel share 12.5%, but its channel/falling/oscillatory/accumulating water
regimes total 43.75% before precipitation. Reconcile that accounting with the
older six-medium 35% cap in a new version; do not claim that taxonomy changes
alone eliminate medium imbalance. Report micro and medium/regime macro results
with appropriate uncertainty. Choose new sample sizes from desired precision
and per-axis coverage, not an arbitrary larger prompt count.

Principal horizons are 60/120/240 seconds, with a short five-second control.
Prefer prefix scoring of the same rollout to study accumulation. Record
separately requested durations as an operating-point experiment. An optional
8–10-minute stress tier is useful after the main panel works, but is not a
substitute for replay validation at four minutes. No “infinite” claim follows
from finite stress tests. Each source/scene family remains the resampling
unit; windows, horizons, prompts and seeds do not multiply independent scenes.

For I2V, annotate one source independently of model output, including
support, each material, overlay, moving subject where present, ignore and
visibility conditions. For T2V, different layouts need output-specific,
future-blind role labeling under one frozen policy. Holdout-generator masks
are a sensitivity control, not automatically shared semantic truth. Do not
transfer an I2V source pixel mask to unrelated T2V layouts.

## 5. Include Steady-Forcing and SceneTether

The project lead explicitly includes **Steady-Forcing in T2V** and
**SceneTether in I2V** in the journal panel, beside contemporary released
external systems. They are eligible author-affiliated candidates; no claim
of superior performance is predeclared. The historical external-only WACV
policy stays attached to historical results.

Apply the same source cohorts, native recipes, seed budget, hardware reporting,
coverage and abstention rules to every contestant. Record affiliation, exact
checkpoint/code/config revisions, public availability and release date. Ports,
common-wrapper deployments, official native methods, short-only systems and
diagnostic composites receive separate row types. Multiple ports of CF++ are
not multiple independent backbone families. A method unavailable publicly
must be labeled author-supplied, with reproducibility limitations stated.

Freeze candidate metrics and thresholds without either author's result as a
selection objective. Validate on external systems, hold out a model family
where practical, and show human-alignment and ranking sensitivity with author
methods included and removed. This addresses author involvement more directly
than excluding their methods forever. Do not use a method's generation map as
the benchmark's scoring mask. Disclose training losses, reward metrics and
selection objectives shared with any evaluation measure.

At the journal freeze, select external released systems using declared criteria:
supported track and horizon, runnable released inference, documented license,
available weights/API version, reproducible settings and representation of
distinct model families. Historical seven-checkpoint T2V rows remain useful
anchors, but a common four-step audit is not a current native-system ranking.
Do not fill an unsupported long horizon by looping a short system's output.

`scripts/registry.py`, `collect.py`, table builders and `check_release.py`
still implement the historical policy. The next implementation must add an
explicit journal profile and affiliation metadata before journal results are
ingested. Do not turn off leakage checks globally or relabel old internal
ablations as released methods. See `EXCLUSIONS.md`.

## 6. Independent human validation

Keep method preference and metric validation as separate estimands. Journal
validation should contain multiple external systems, natural difficult cases,
controlled interventions and competitive simple controls; include author
systems only under the same blinded policy. Avoid selecting every pair for a
large predicted SNF gap or favorable showcase result.

Reuse the study infrastructure's blinded tokens, source display, balanced
positions, playback checks, ties, source/rater resampling, module digests and
fixed stopping rules. Prepare a separate journal module before collecting
new judgments. Document consent, privacy, institutional review status and
permitted secondary use accurately; current voluntary participation does not
establish consent for publicly releasing responses or a new journal study.

Each axis needs a matching question and viewing interval. Assess activity
amount independently of motion naturalness; geometry independently of source
appearance; replay independently of generic artifact preference. Endpoint
clips support end-state conclusions. Full-duration or independently validated
sampling is required for uninterrupted continuity claims. Match codec history
or report its sensitivity; a common final encoder does not remove an extra
earlier compression generation in a composite.

Measure agreement and tie/cannot-tell rates, per-video sign concordance and
rank/ordinal association with confidence intervals, calibration performance,
false-positive rates and abstention by medium. Compare every candidate with
incumbents and simple baselines. Report within-system as well as pooled
alignment so a catastrophic model contrast cannot drive the whole result.
Use held-out scene families and models for confirmation. Estimate source and
rater requirements from target interval widths/reliability using simulations
or a separate pilot. Fifteen raters is a possible recruitment count, not a
validity criterion. Neither repeated calls to one VLM nor synthetic study
responses count as independent raters.

## 7. Milestones and concrete exit evidence

| Gate | Practical work | Exit evidence |
|---|---|---|
| J0: CVPR archive and overlap | Freeze final paper/protocol, existing score identities, study versions and reuse ledger; preserve WACV/preprint history | Hash-linked archive and claim/asset overlap table; no ambiguous ownership of the benchmark contribution |
| J1: portable inputs and roles | Build clean import interface; resolve rights; define new independent sources, medium/regime taxonomy and role annotations | Licensed source manifest, deduplication/exposure audit, independently reviewed subset, annotation disagreement and frozen split |
| J2: measurement admission | Validate compact kernels against paired corruptions and real natural negatives; fix units, precision, coverage and missing-data handling | Target/nuisance response matrix, natural-video false positives, failure cases, estimator and mask sensitivity; frozen candidate decisions |
| J3: subjective validation | Separate journal study; align score and viewing windows; confirm on held-out scenes/models | Axis-specific agreement and human-alignment intervals, ties/exclusions, annotation provenance and consent-permitted deidentified evidence |
| J4: broad system evaluation | Native T2V/I2V panel including author methods; matched horizons/seeds; efficiency and optional application stress | Per-video outputs and provenance, within-/between-seed uncertainty, native-versus-port distinctions, runtime and missed-failure audit |
| J5: journal package | Compact manuscript plus diagnostic supplement, WACV concern closure table, artifact and publication-history disclosure | Every claim has evidence; clean-clone reproduction succeeds; reviewer access, rights, maintenance/versioning and venue checks complete |

Some implementation can overlap, but do not freeze thresholds on J3/J4
confirmation outcomes. Until SceneTether submission is complete, prioritize
read-only audit, planning and reusable CPU engineering without modifying its
locked method, queues or study. Schedule new expensive generation only after
the independent protocol and resource budget are concrete.

Efficiency is a benchmark result: log wall time per video-minute, GPU/CPU,
peak memory, storage, sampling and cache identity. Screen cheaply, then compare
the screening policy with dense scoring on a stratified held-out subset.
Report missed brief failures and rank changes. Low-rate coverage of a full
duration is not continuous temporal observation.

## 8. Journal manuscript shape and venue choice

Suggested structure: task and prior art; four measurement families;
independent validation; native T2V/I2V comparison and long-duration analysis;
limitations and artifact. Put the full candidate battery, estimator settings,
per-scene records, legacy comparisons and review-response matrix in the
supplement. Compactness comes from admitted axes and fewer repeated tables,
not from suppressing nulls or omitting strong simple baselines.

Provisional primary target: **IEEE TCSVT** if the final contribution provides
strong video measurement methodology and independent subjective evidence.
**ACM TOMM** is a strong alternative for a multimedia evaluation/resource
paper. CVIU, Pattern Recognition, The Visual Computer and IEEE Access are
conditional alternatives, not predetermined acceptance routes. Current
indexing, category/year-specific quartiles, fees and author rules require
verification at venue selection. The attached “guarantees acceptance” advice
is rejected. See `JOURNAL_VENUE_ASSESSMENT_2026_10_30.md`.

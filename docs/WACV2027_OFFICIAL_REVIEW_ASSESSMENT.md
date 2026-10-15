# WACV 2027 official-review assessment and v2 priorities

Reviewed 2026-10-15 KST from the author-provided OpenReview export for
submission 1825. This is an assessment of that supplied record, not an
independent query of OpenReview. The export contains four official reviews
and one AC meta-review; review and meta-review modification dates extend to
October 15. Earlier repository references to three official reviews and a
different score/confidence distribution are superseded by this record.

## Recorded outcome

| Reviewer | Recommendation | Confidence | Main concerns |
|---|---|---|---|
| YFhf | 2, Weak Reject | 4, high | Established premise and selective incumbent comparison; pilot scale; replay blind spot; absent construct validation; insufficient separation of motion sources |
| XNQG | 4, Borderline Accept | 3, moderate | Model-dependent masks; small and imbalanced assets; unmatched horizons; common inference configuration |
| XzUA | 3, Borderline Reject | 3, moderate | Semantic mask circularity; naturalness/semantic/replay validity; small scope and sample; inference settings and single seed |
| BsRf | 3, Borderline Reject | 3, moderate | Narrow demonstrated coverage, imbalance, semantic/physical motion limitations, manual mask verification and operating points |

The AC's final recommendation field says **Reject in round 2**. The AC
recognizes the problem and perturbation work, but endorses rejection on
benchmark scope, scale and validation, explicitly prioritizing a more diverse
evaluation set and human validation for a future submission.

XNQG's review form says Algorithm while the submission and the other reviews
say Evaluations and Datasets. The text still assesses the benchmark directly;
the supplied record does not establish that this form mismatch explains the
outcome.

## What the reviews actually require

The reviewers repeatedly praise controlled interventions, reporting motion
magnitude beside persistence, separate axes, transparent settings and the
reproducible artifact. YFhf additionally credits the frozen protocol, coverage
accounting and paired uncertainty. Preserve those strengths.

Their main objection is the validity of the inference made from a favorable
score. Detecting injected translation or freezing establishes responsiveness
to that intervention. It does not establish that the metric tracks perceived
support stability or natural material evolution on unmodified model outputs.
Adding more kernels without independent evidence would leave this objection
intact.

| Concern in the supplied reviews | State of current repository | Evidence still needed |
|---|---|---|
| Masks depend on the output's own early motion | Source-reference port and source-mask policies exist; automatic shared-mask control is stored | Independently reviewed source roles, annotation disagreement, paired mask/rank sensitivity and coverage. Source-derived does not mean semantically correct |
| 23 prompts, 61% channel water, sparse categories | v2 contains 96 T2V scenes and 48 I2V pairs; I2V splits identify 41 test and seven overlap | Actual scored native I2V coverage and uncertainty by regime. Two precipitation test items cannot sustain a category claim; an authored prompt count does not establish benchmark validity |
| Persistence rewards a repeated short river clip | CPU recurrence candidate and synthetic-loop tests exist | Full-duration held-out loop/reset detection plus false positives on real surf, fire and foliage; activity gating so freezing is not misreported as replay |
| No human construct validation in the submission | v2 human protocol exists; repository contains a historical eight-rater study | An adequately powered, blinded v2 axis study on real failures and controls; agreement, cannot-tell rates, per-video human alignment and uncertainty |
| Existing metrics already agree with static-fidelity factors | Incumbent audit and broader literature review acknowledge this | Same-input official incumbent results and axis-specific human comparisons; report agreement, limitations and null gains |
| Common four-step configuration is not every released system | Registry distinguishes common/wrapper from native settings | Native I2V panel, multiple seeds and explicit short-model horizon limits; method effects compared within the same backbone/configuration |
| Horizon changes confound prompt identity | v2 sources/prompts are matched across requested durations | Completed matched-source horizon measurements; distinguish prefixes of one rollout from separately requested rollouts |
| Binary flow regions mix unrelated motion sources and overlays | Four source roles distinguish support, material, overlay and ignore | Source-role review and counterexamples where a boat/car moves while water freezes; whole-scene integrity checks for invented objects; separate subject/instance roles if those scenes are scored |

These are partial repairs, not resolved review objections. Current
implementation evidence is recorded in `V2_METRIC_WORKLOG.md`; the protocol
and research decisions are in `SNF_V2_EVAL_SPEC.md` and
`I2V_METRIC_REVIEW_2026_10_08.md`.

**Taxonomy caveat.** The new nine-regime manifest reports channel flow at
12/96 (12.5%). Counting channel, falling-water, oscillatory-water and
accumulating-level regimes together gives 42/96 (43.75%) T2V scenes and
21/48 I2V pairs, before precipitation. This is a different accounting from
channel share. Reconcile the medium mapping with the older six-medium
contract's 35% open/channel-water cap before claiming compliance or that the
imbalance objection is closed. Freeze any amendment explicitly; renaming
water subtypes does not independently diversify media.

## How to interpret the strongest objections

### Novelty and incumbent comparison

YFhf directly challenges the premise as a new contribution: VBench already
discusses dynamics versus temporal consistency; WorldScore separates static
and dynamic behavior; DEVIL and DIVE address static-output bias. The supplied
review also points to the paper's own background-consistency and
motion-smoothness correlations. This is stronger than a request for extra
citations: the contribution must be positioned beyond the established
tradeoff and must demonstrate additional diagnostic value.

The earlier replacement claim that incumbents agree but cannot resolve the
systems is also unproven. Our paired incumbent analysis gives NBF separation
on 14/21 pairs versus 13/21 for background consistency, with unadjusted
descriptive intervals. Do not infer general metric superiority from the
range/SD ratio or a Dynamic Degree disagreement. Added value can be a
validated, interpretable failure trajectory even when model rankings agree.

The review calls a SLAM-based geometry instrument stronger than fBD. That is
the reviewer's assessment, not evidence that SLAM should become SNF's primary
fixed-camera metric. Select instruments for the target's visibility and
baseline conditions and establish validity on the same inputs.

### Scope and motion semantics

The fixed-camera nature task remains a coherent target for the I2V method
paper. It does not need to expand into camera choreography and human action
to answer the current task. It does need adequate diversity *within* its
declared media and explicit handling of overlays and multiple motion sources.

A river ROI that includes a moving boat cannot establish continued river
motion from aggregate flow. A conservative source mask can likewise miss a
new car or sign invented later. Qualify material separately, annotate visible
subjects when included, and use a full-scene integrity judgment. If a scene
is excluded for an unsupported regime, count the exclusion. Silently mapping
every unsupported moving object to material or ignoring it would retain the
reviewer's counterexample.

### Replay and naturalness

Address replay as a core continuity failure, not solely as a scope disclaimer.
Steady flow can be statistically stationary for minutes; useful continuity
does not require ever-increasing visual change. Detect copied temporal
sequences and reset discontinuities while allowing valid natural cycles.

Texture detail, activity, direction and recurrence explain different failure
modes. None alone establishes physical realism. For the CVPR paper, use
separate blind judgments of source fidelity, support stability, material
activity, intended direction, continuity and plausibility. The current Q2/Q4
questions combine several properties; avoid claiming that a combined answer
validates every component separately. Human metric-validation pairs should
also cover the full difficulty range and real counterexamples, rather than
only pairs selected for a large metric gap.

## Table and presentation repairs named by YFhf

1. Report observed response sign separately from task desirability. Increasing
   Dynamic Degree under camera translation is a measurable response; the
   fixed-camera task regards that corruption as undesirable. Apply declared
   admission criteria consistently to incumbents and proposed factors.
2. Correct the DLR admission claim. The later consolidated nuisance audit
   already demotes DLR/DAR and scopes NBF/FP; carry those decisions into the
   manuscript instead of retaining the submitted admission table.
3. Label Figure 1's extremal selection in its caption. Use a representative
   gallery selected by a frozen rule as the main demonstration. An extreme
   ratio is not an estimate of typical sensitivity.
4. Show the agreeing incumbent dimensions beside Dynamic Degree. A model-level
   correlation over seven systems does not establish per-video human validity.
5. Remove the scale-dependent sensitivity superiority argument. Our own paired
   analysis does not support comparing raw multipliers across metrics as a
   measure of relative sensitivity.

The supplied reviews do not specifically establish the later method-project
finding that fBD is weak for subtle source-fidelity contrasts. Keep that
evidence distinct: reviewer criticisms support rethinking validity, while
the source-fixed experiments motivate the source PSNR/color/registration
panel. The later float32 color-accumulation defect also needs its own metric
identity and absolute-value caveat, as recorded in `V2_METRIC_WORKLOG.md`.

## Practical priority for the CVPR 2027 method paper

1. **Freeze the claim and confirmation boundary.** Present SNF v2 as a
   task-specific evaluation component unless its independent validation is
   completed. Prior art, inspected factorials, seven overlapping sources and
   newly introduced metrics must be disclosed accurately.
2. **Qualify source roles and fidelity.** Independently review a stratified
   I2V subset, document uncertainty/visibility, and compare old versus shared
   masks on identical clips. Preserve registration failures and unsupported
   samples in denominators.
3. **Close continuity and intent counterexamples.** Test foreground reversal,
   ping-pong, loop/recolored loop, reset, frozen sharp flow, noise, and
   subject-only motion against real periodic/occlusion controls. The existing
   CPU recurrence candidate is a starting instrument, not a validated result.
4. **Collect axis-specific human evidence.** Include ordinary model failures,
   controlled counterexamples and near ties. Freeze pair selection and
   exclusion rules; estimate the required scene/rater count from precision and
   agreement, not from participant counts in unrelated benchmarks.
5. **Complete native matched-source evaluation.** Use the intended long I2V
   systems and principal 60/120-second settings, report seed variance and
   actual usable coverage, then evaluate the preselected 240-second stress
   subset where supported. Include official VBench-I2V/Long and applicable
   motion comparators on the same inputs.

The release criterion is evidence that the evaluation distinguishes the
target failures reliably and agrees with its corresponding human judgments.
A larger prompt file, a stronger feature matcher or a parity-passing scorer
does not by itself satisfy that criterion.

# SNF-Bench v2: fixed-camera natural-flow evaluation design

Status: design proposal, 2026-09-28. This document does not change the frozen
v1.1 metric definitions in `METRIC_SPEC_v1.1.md` or relabel existing scores.
All v2 diagnostics receive new names and versions after validation.

## 1. Task and evidence boundary

The unit is one continuous, single-scene video in which the viewpoint remains
fixed, identifiable support stays anchored, and specified natural material
continues to move. T2V and I2V are separate tracks. A model's released
inference procedure and a common-wrapper experiment are separate settings.

The benchmark should answer five questions, without collapsing them into one
number:

1. **Support stability:** do rigid scene anchors stay in the same image-plane
   position, including at long temporal baselines?
2. **Flow presence:** is there non-trivial motion in the intended region at
   early, middle, and late times?
3. **Motion intent:** where the prompt makes it observable, is net transport in
   the specified direction or toward the specified destination?
4. **Temporal evolution:** does motion persist without freezing, reversal when
   one-way transport is specified, exact replay, or reset seams?
5. **Plausibility and semantics:** does the generated scene depict the intended
   medium, and do human observers find its evolution physically credible?

Answers 1-4 may have mechanistic diagnostics. Answer 5 needs blind human
judgments as its primary validation. Optical flow is apparent image-pattern
motion; it is not measured water or smoke velocity. Surface waves, reflections,
glare, occlusion, and missing tracers can make the two disagree. A video may be
unscorable on one axis and still scorable on the others.

Existing comparators are mandatory: VBench background consistency, motion
smoothness, temporal flickering and dynamic degree; VMBench motion quality;
and a prompt/physics-oriented comparator such as VideoPhy-2 on a suitable
subset. No assertion that these benchmarks are blind to SNF's task is allowed.
The contribution to test is *task-specific resolution and interpretation*.

VBench-family comparison is versioned in
`VBENCH_EXTENSION_GAP_ANALYSIS.md` and
`manifest/vbench_extension_audit.json`. In particular, VBench-Long is a
required long-range incumbent, VBench-I2V source consistency and static-camera
classification are required on I2V, and the overlapping VBench-2.0 mechanics
or motion-rationality prompts are contextual physics incumbents. SNF's distinct
object is the time-resolved, spatially localized transport process.
Operational comparator settings and required provenance are pinned in
`configs/vbench_incumbent_protocol.json`.

Primary sources:

- VBench: https://openaccess.thecvf.com/content/CVPR2024/papers/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.pdf
- VBench++ (including I2V and VBench-Long): https://arxiv.org/abs/2411.13503
- VBench-2.0 intrinsic faithfulness: https://arxiv.org/abs/2503.21755
- VMBench: https://openaccess.thecvf.com/content/ICCV2025/html/Ling_VMBench_A_Benchmark_for_Perception-Aligned_Video_Motion_Generation_ICCV_2025_paper.html
- VideoPhy: https://research.google/pubs/videophy-evaluating-physical-commonsense-for-video-generation/
- T2V-CompBench (motion binding and human validation): https://openaccess.thecvf.com/content/CVPR2025/html/Sun_T2V-CompBench_A_Comprehensive_Benchmark_for_Compositional_Text-to-video_Generation_CVPR_2025_paper.html
- River image-velocimetry caveats: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022WR032251

## 2. Prompt and annotation contract

Target: pilot the variance and cost, then author about 96 **independent base
scenes** (initial allocation: 16 per existing medium category). Directional
counterfactuals are variants of a base scene, not independent prompts. Water
share and every cell size are checked by script, not asserted in prose. The
number is a planning target; freeze it only after a prompt-level power pilot.

The authoring record and release allocation are machine checked by
`configs/snf_v2_scene_contract.json` and
`scripts/validate_v2_scene_manifest.py`. Counterfactual variants never increase
the independent-scene count.

Every prompt has a stable `scene_id`, `variant_id`, track, medium, duration
policy, visual scene text, rigid support description, moving material, motion
regime, and whether image-plane direction is observable. Direction-eligible
items additionally carry source/destination or an image-plane path and a
transport ROI. Periodic, turbulent, and one-way transport items have separate
scoring rules. The `scene_id` is the resampling and holdout unit.

The model-visible text describes only the desired video. It must not address
evaluators or mention scores, algorithms, frames to inspect, RoPE, KV caches,
or model failure names. Avoid contradictory requirements such as immobile
windblown trees. Avoid generic negative lists that substitute for an observable
target. Human reviewers sign off on spatially plausible direction and on the
availability of an identifiable rigid anchor before prompts are frozen.

Mask labels are `rigid_support`, `intended_motion`, `overlay_or_ambiguous`, and
`ignore`. They are semantic roles, not a claim that every dynamic pixel is
foreground. For I2V, label the shared source image once, validate its geometry against
each model's first frame, and use the same source mask for every model. For T2V, apply one frozen labeling policy to each generated
output's first frame, blind to all later frames. A single pixel mask shared
across different T2V layouts is generally invalid. Audit exact shared masks
only on a layout-aligned T2V subset. Report mask coverage and abstention.

Do not score direction for a clip whose prompt has no view-specific direction,
or whose visible texture provides no reliable transport cue. Do not penalize
natural wave cycles or local eddies with a one-way-transport rule.

## 3. Proposed diagnostics (all provisional)

| Diagnostic | Observation | Required failure control |
| --- | --- | --- |
| Long-baseline support registration | First-to-later rigid-anchor displacement, rotation, scale, inlier coverage and residual; complement adjacent-frame NBF/fBD | Inject translation/rotation/zoom; stationary support with moving water; sparse nighttime anchors |
| Signed transport | Project reliable dynamic-region flow or tracer tracks onto the annotated image-plane path; report wrong-way fraction and abstention | Reverse dynamic motion only; preserve static support; turbulent natural control |
| Incoming flow | Source-to-near-boundary crossings plus foreground expansion/occlusion, with rigid anchors fixed | Zoom, swelling texture without transport, wrong-way flow |
| Reversal | Net signed path transport divided by absolute path transport in fixed-duration windows | Ping-pong motion; legitimate wave and eddy controls |
| Replay | Long-lag dynamic-region appearance and flow recurrence, plus seam evidence, calibrated per medium against real footage | Exact short loop, repeated-but-recolored loop, natural surf periodicity |
| Failure trajectory | Fixed-second window curve, robust slope, worst window, first calibrated failure and longest failing run | Same mean with one catastrophic late interval versus distributed mild error |
| Semantic/plausibility audit | Medium identity and blind human ratings; VLM can triage after independent validation | Moving fog scored as a river; visually realistic wrong-direction clip |

These diagnostics must be shown separately. A high optical-flow magnitude or a
high persistence ratio is not evidence of physical correctness. A scalar may
be promoted only if it has held-out validity and a clear failure interpretation.
The executable trajectory contract is `scripts/long_horizon_protocol.py`; its
axis registry is `configs/snf_v2_dimension_contract.json`. It intentionally
does not emit a combined benchmark score.

## 4. Validation and decision rules

Build an intervention matrix before tuning thresholds. Each row is a failure
family; each column is a diagnostic and an incumbent. Predeclare expected
response sign, whether that response is desirable, and which rows are
off-target. Compare paired changes on the same source clip, including effect
sizes and uncertainty. Also report absolute values and a zero-motion floor.

Use three evidence sources:

1. **Controlled corruptions** establish whether a measurement responds to a
   known change: camera drift, foreground-only reversal, freeze, attenuation,
   ping-pong, exact replay, reset seam, photometric change, mask perturbation,
   and medium substitution. Preserve a pristine parent clip for each variant.
2. **Licensed real fixed-camera footage** establishes a natural operating
   range and false-positive rate by medium. Synthetic loops alone cannot set a
   naturalness threshold. Record rights and provenance for released assets.
3. **Blind human assessment** establishes whether diagnostic differences
   matter perceptually. Ask separate, concrete questions on support stability,
   direction, continuity/replay, medium match, and plausibility. Include
   `cannot tell`, repeated anchors, multiple raters, agreement by axis, and
   adjudication of ambiguous items. Raters must see the full interval needed
   to judge long-horizon replay, not only a few attractive frames.

Hold out **scene families and models** during threshold selection. Use paired
prompt-level comparisons and hierarchical uncertainty over scene family and
seed. For each diagnostic report detection by failure type, false positives on
real footage, abstention, category spread, backbone/mask sensitivity, runtime,
and pairwise model-discrimination intervals. A between-system range divided by
within-system SD is descriptive; it is not by itself proof of resolution.

The current 60/120/240 T2V prompt sets are disjoint. A horizon claim needs a
matched core. Prefer one 240-second rollout with scored 60/120/240-second
prefixes when the inference protocol permits it; test separately generated
requested durations as a different experiment. Never count windows from one
clip as independent observations.

## 5. Efficiency and reporting

Decode the full video for coverage checks and low-rate replay screening.
Compute expensive dense flow on fixed *wall-clock-duration* windows at early,
middle, late, and suspected failures. Escalate uncertain clips to denser scoring
and human review. Compare sampled and full scoring on a stratified subset;
report missed failures, rank changes, GPU time, and storage. Window duration
must be fixed in seconds across horizon tiers; the current 12%-of-clip window
changes the measured time scale.

Store the full per-window trajectory even when the headline table shows only a
summary. At minimum report early, late, robust slope, worst interval, coverage,
and abstention. Add time-to-failure only after thresholds are frozen on
development scenes and licensed real-video anchors. Incoming-flow results are
descriptive until a support-stability gate has been calibrated.

Keep T2V/I2V, released/common inference, medium, horizon, seed, and
direction-eligible/unscorable strata visible in results. Publish per-video
records, masks/annotation policy, prompt family IDs, sampling code, asset
licenses, and versioned metric provenance. Avoid one leaderboard total:
show the support/flow/intent/continuity/plausibility profile and uncertainty.

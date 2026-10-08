# SNF-Bench v2 metric decision for the CVPR 2027 I2V paper

Reviewed 2026-10-08 KST. This is a research and design decision; no score
formula, stored measurement, mask disposition, or running method experiment
is changed by this document. Exa search used 15 calls and 77 result slots
(including duplicates), followed by primary-paper and official-code checks.
Local evidence hashes and repository revisions are stored in
`manifest/i2v_metric_review_2026_10_08.json`. It amends the recommendations in
`METRIC_UPGRADE_PROPOSAL_v2.md` and guides `SNF_V2_EVAL_SPEC.md`.

## 1. Decision and claim boundary

Demote fBD from the primary fidelity endpoint to a geometric diagnostic.
Retain source-referenced support PSNR, legacy color difference, and
registration coverage as the compatibility panel for the method project's
existing analysis. Add pixelwise CIEDE2000 and a regional perceptual distance
as **candidates**, with independent corruption and human validation before
admission. Keep material activity, direction/regime, replay, camera motion,
and plausibility separate. A single similarity, flow, or texture score cannot
establish the target task.

For the CVPR method paper, the defensible benchmark contribution is a
source-anchored, region-aware evaluation protocol for sustained fixed-camera
I2V, with explicit temporal coverage and failure accounting. Source fidelity
and regional motion separation have prior art. Novelty must rest on validated
long-duration failure analysis and task-specific interpretation, with code
and records that other methods can use.

The 48-scene factorial has already been inspected. Any new metric selected
because it distinguishes those arms is retrospective. Freeze the present
compatibility analysis as historical evidence; qualify new metrics on
independent development controls and confirm them on genuinely untouched
sources or a future locked study. A new seed alone does not remove source or
metric-selection exposure. Keep SNF's 41 test sources and seven overlapping
sources distinct; a method-side label of “48 test” does not supersede
`manifest/v2_splits.json`.

## 2. What the local findings establish

Reviewed method documents 85, 88–91 and 95–97, plus the scorer and current
pooled source-fixed table. The reported pooled Echo-versus-sink interaction
is −1.95 dB [−2.84, −1.15] for source support PSNR and +5.99 [2.17, 10.13]
for legacy color drift. Source-matched fBD is +1.11 [−0.53, 2.85]; the
registration-failure interaction is +0.12 [0.04, 0.22]. The matched fBD contrast uses 32 scenes, color/identity 42, and the failure
contrast 45 eligible scenes. These are different
endpoint populations and conditional measurements, not four interchangeable
estimates of camera drift. The table and protocol are:

- [pooled table](/home/minar/ar-image-animation/results/factorial/tables/interaction_pooled_sourcefixed.md)
- [factorial analysis and mask review scope](/home/minar/ar-image-animation/docs/89_FACTORIAL_ANALYSIS_PLAN.md)
- [source-fixed scorer](/home/minar/ar-image-animation/tools/factorial_scoring/sourcefixed_metrics.py)
- [CPU motion guard](/home/minar/ar-image-animation/tools/factorial_scoring/sourcefixed_flow.py)
- [latest development qualifications](/home/minar/ar-image-animation/docs/95_I2V_TAKEOVER_OCT08.md)

The findings support four repairs: shared source-defined masks, source-image
reference, an appearance channel alongside geometry, and explicit failure
denominators. They do **not** establish that fBD is useless: it detects the
large k=6 collapse in the same experiment. It is weak for the subtler k=1/k=3
comparison and can miss redraws that retain recognizable layout.

The method scorer is useful migration material, but it is not already a
portable v2 specification. It imports experiment-specific modules, keeps
12%-of-duration windows, and uses conditional means after excluding failed
registrations. Its color distance is the Euclidean distance between support
means in OpenCV uint8 Lab; this is neither pixelwise ΔE nor CIEDE2000. Its
CPU motion guard is SIFT registration plus Farneback, not the RAFT scorer.
Port kernels and establish parity while preserving these identities.

All 48 mask records say approved, but reviewer fields and docs/89 show AI
review with limited project-lead approval, not independent human annotation
of every source. Carry the actual review scope and mask hashes into SNF;
an `approved` string alone must not graduate them to independently reviewed
benchmark truth. Conservative masks can also miss invented objects outside
the chosen regions, as docs/95 explicitly observes.

## 3. Literature and implementation decisions

| Instrument | Verified contribution | Decision for SNF I2V | Main qualification |
|---|---|---|---|
| Pixelwise CIEDE2000 | Perceptual color difference with published implementation test pairs | First CPU candidate for support color | Fix D65 Lab conversion, color range and spatial aggregation; mean-color cancellation and valid relighting are controls |
| LPIPS and DreamSim | Learned image similarity at different perceptual scales | LPIPS regional map first; DreamSim on support tiles as a complement and official VBench-I2V incumbent | These are image measures; masking whole inputs introduces edges and context bias |
| SuperPoint + LightGlue | Learned sparse features and adaptive matching | Registration sensitivity comparison against ORB/SIFT | Better matching is plausible, not proven on our low-texture support; no method creates reliable points on a blank sky |
| CoTracker3 | Released online/offline tracking with visibility | Support-grid trajectories and short, reseeded material-tracer experiments | Visibility loss may be legitimate occlusion; foam/flame patterns are not persistent material points |
| TRAJAN | Track-autoencoder reconstruction AJ and motion embeddings | External motion-consistency comparator on a stratified subset | Published human alignment does not validate nature media or replay detection |
| FVMD | Fréchet comparison of PIPs++ velocity/acceleration feature distributions | Supplementary after real-footage reference and sample-size study | Distribution measure, not per-video ground truth; medium/viewpoint and tracking confounds |
| DISTS / VGG Gram | Structure/texture similarity tolerant of some texture resampling | Exploratory material appearance retention on interior tiles | Ordinary DISTS includes structure; an extracted texture term is a new diagnostic. Frozen and looping textures can score well |
| Spectral and temporal texture summaries | Frequency-domain drift and long-range correlation motivate cheap probes | Region-local spatial detail plus temporal activity curves | Noise increases detail; spatial FFT magnitude loses phase; these are not naturalness scores |
| Forward–backward flow cycle error | Measures disagreement between forward and backward estimated flow | Confidence and diagnostic channel | Consistent wrong flow, freezing and replay can pass; natural occlusion and transparency can fail |
| SGC / MEt3R | Regional camera-pose divergence / pose-free multi-view consistency | Cite; optional support-geometry sensitivity subset | Coherent camera movement can be geometrically consistent. The fixed-camera requirement needs absolute displacement too |

Primary sources and code:

- [CIEDE2000 authors' test data and implementation notes](https://www.hajim.rochester.edu/ece/sites/gsharma/ciede2000/)
- [LPIPS paper and code](https://github.com/richzhang/PerceptualSimilarity),
  [DreamSim paper](https://proceedings.neurips.cc/paper_files/paper/2023/hash/9f09f316a3eaf59d9ced5ffaefe97e0f-Abstract-Conference.html),
  [official DreamSim code](https://github.com/ssundaram21/dreamsim)
- [LightGlue](https://github.com/cvg/LightGlue),
  [CoTracker3](https://github.com/facebookresearch/co-tracker)
- [TRAJAN paper](https://arxiv.org/html/2505.00209v1),
  [released demo](https://github.com/google-deepmind/tapnet/blob/730cda1c730877cfedbe01bf87fb1cadb78a565d/colabs/trajan_demo.ipynb)
- [FVMD paper](https://arxiv.org/abs/2407.16124),
  [official implementation](https://github.com/DSL-Lab/FVMD-frechet-video-motion-distance)
- [DISTS paper](https://www.cns.nyu.edu/pub/lcv/ding20-preprint.pdf),
  [DISTS implementation](https://github.com/dingkeyan93/DISTS)
- [dynamic texture synthesis and shifted Gram losses](https://arxiv.org/html/2104.05940v2),
  [FreqForcing paper](https://arxiv.org/html/2607.27110v2)
- [SGC](https://arxiv.org/html/2603.19048),
  [MEt3R](https://arxiv.org/html/2501.06336)

### Benchmark comparisons that matter

**WorldScore is direct prior art.** Its dynamic world task requests a fixed
camera, covers fluid motion, and uses regional motion placement. At audited
commit `096c75f`, the implementation subtracts maximum background flow
magnitude from maximum object-region magnitude. This measures placement,
not signed material direction. Its flow-consistency implementation evaluates
a forward–backward cycle with rounded/clipped coordinates; it is not an RGB
photometric residual or a physical-law test. Keep the official comparator
separate from an occlusion-aware SNF adaptation. The paper's 400-person study
selects a subjective-quality metric combination; it does not individually
validate every dynamics metric. [Paper](https://arxiv.org/html/2504.00983v2),
[motion code](https://github.com/haoyi-duan/WorldScore/blob/096c75fc4ada9c7d92e03140c3c1f0c8f383b61f/worldscore/benchmark/metrics/third_party/motion_accuracy_metrics.py),
[cycle code](https://github.com/haoyi-duan/WorldScore/blob/096c75fc4ada9c7d92e03140c3c1f0c8f383b61f/worldscore/benchmark/metrics/third_party/flow_aepe_metrics.py).

**Keep VBench++/I2V/Long mandatory.** Source consistency, static-camera
classification and long-video temporal-quality dimensions are the closest
incumbent panel. Preserve official formulas and sample settings, and report
SNF's additional source-region curves separately. VBench-2.0 physics is
contextual; it does not replace local transport validation. See the existing
`VBENCH_EXTENSION_GAP_ANALYSIS.md` and
[official suite](https://github.com/Vchitect/VBench).

**DIVE, DEVIL, VMBench and AIGCBench belong in the comparison landscape.**
DIVE explicitly addresses low-dynamic bias in I2V; DEVIL evaluates dynamics
at multiple temporal scales; VMBench targets motion perception; AIGCBench
separates alignment, motion, temporal consistency and quality. Use released
applicable dimensions on the same subset rather than assuming SNF alone
handles the activity/quality tradeoff.
[DIVE](https://arxiv.org/abs/2505.19901v3),
[DEVIL](https://arxiv.org/abs/2407.01094),
[VMBench](https://openaccess.thecvf.com/content/ICCV2025/papers/Ling_VMBench_A_Benchmark_for_Perception-Aligned_Video_Motion_Generation_ICCV_2025_paper.pdf),
[AIGCBench](https://arxiv.org/html/2401.01651v1).

FVD is supplementary at most. Its documented content bias includes failures
on long sky videos, particularly relevant to our domain.
[Content-bias study](https://openaccess.thecvf.com/content/CVPR2024/papers/Ge_On_the_Content_Bias_in_Frechet_Video_Distance_CVPR_2024_paper.pdf).

### Availability and portability findings

TRAJAN's released model defaults to 150 output frames. Its demo pads shorter
tracks and crops longer episodes to 150; it samples 4,096 tracks, splits them
into 2,048 conditioning and 2,048 reconstruction targets, and computes AJ
over thresholds 1, 2, 4, 8 and 16. “Conditioning/support tracks” in that code
does not mean SNF rigid support. Pin window duration, fps and spatial
normalization. Substituting CoTracker tracks for BootsTAPIR creates an adapted
instrument, not an official TRAJAN result.
[Demo](https://github.com/google-deepmind/tapnet/blob/730cda1c730877cfedbe01bf87fb1cadb78a565d/colabs/trajan_demo.ipynb),
[model](https://github.com/google-deepmind/tapnet/blob/730cda1c730877cfedbe01bf87fb1cadb78a565d/tapnet/trajan/track_autoencoder.py).

FreqForcing exists and is relevant prior art for spectral anchoring, but its
audited repository at `2cdcdf1` has an unchecked “Release inference code”
item. It is a citation and conditional future baseline, not currently a
reproducible released-pipeline row. Its latent attention spectral anchoring
does not validate a new RGB “glassy-water index.”
[Repository](https://github.com/jiatongli2024/FreqForcing/tree/2cdcdf1753eafe97eebe260c4ab359e8fa18e967).

## 4. Concrete measurement design

**Source fidelity.** On a source-defined rigid ROI, retain unaligned source
PSNR and pixelwise ΔE00 at timestamped intervals. Calculate mean and tail
color errors over corresponding support pixels, not just distance between
region means. Add regional LPIPS after eroding the ROI by its effective
feature neighborhood, or use fully interior source tiles with coverage
reported. Use DreamSim tiles as a semantic complement. Aligned fidelity can
help diagnose content change, but must remain secondary: alignment can
erase the camera movement the task prohibits. Record source-to-output
frame-0 fidelity separately from subsequent accumulation.

**Camera/support motion.** Fit support transformations with spatially
distributed evidence and record displacement, rotation, scale, inliers and
fit residual. A coherent fit across support tiles suggests global motion;
disagreement suggests local deformation or contamination. Neither inference
is a physical camera pose guarantee. Qualify support on the source before
seeing outputs, then distinguish instrument abstention from output-time
registration failure. Show coverage beside conditional displacement; do not
impute an arbitrary physical displacement when matching fails.

**Material activity and intent.** Report residual speed and its distribution,
active area, and signed projection onto source-annotated paths. Normalize
coordinates and time explicitly. For each accepted local vector, take its
signed path component before aggregating net transport and absolute
transport; taking absolute value after spatial averaging hides simultaneous
opposing flows. Report confidence/occlusion coverage and wrong-way fraction.
Stable support and agreement between independently qualified flow/tracking
instruments are prerequisites for interpreting “incoming” motion. A depth
approach without observable tracers remains unscorable for 2D transport.

**Texture and replay.** Compute spatial detail on fully interior material
patches at a fixed scale, with both source and early-window references.
Compute temporal power/autocorrelation separately. A frozen sharp source
retains spatial detail; random flicker has high temporal energy; a loop can
retain both. Add a long-lag recurrence search across the whole video, require
multi-frame sequence evidence and test seams separately. Frame matching
alone produces false alarms on natural surf. Short-window TRAJAN scores are
an external consistency signal, not a replay detector.

**Applicability.** Flames/eddies/waves do not receive one-way penalties unless
an independently reviewed observable sub-process warrants them. Rain/snow
overlays require a separate event/direction/activity study rather than being
scored as dense water transport. Rigid geometry can remain scorable through
an overlay even when strict photometric identity is not. Allow intended
water-level changes, smoke occlusion, firelight and accumulation where the
prompt calls for them; qualify enduring support/visibility or abstain. Flow
measures apparent pattern motion, not material velocity; river-velocimetry
research documents the effects of reflections, texture and lighting.
[River study](https://hal.science/hal-03924808/document).

**Whole-scene integrity.** Conservative ROIs cannot catch every invented car,
sign or replaced object. Include a blind source-versus-video integrity
question and a full-frame semantic audit outside the scoring ROIs. A VLM may
triage after its own validation; source fidelity inside selected rocks must
not be interpreted as fidelity of the entire scene.

Keep all axis values visible when flow freezes. Mark joint task failure after
calibration; suppressing the fidelity measurements would hide the precise
tradeoff we need to understand. Report five-second curves, early/worst/late,
coverage and robust change. First failure time remains unset until calibration.

## 5. Losses worth testing on the method side

These are proposed method experiments, not benchmark changes:

| Loss or mechanism | Recommended use | Required control |
|---|---|---|
| Masked source reconstruction / perceptual loss | Rigid support with stable lighting and visibility; eroded ROIs | Freeze-prone model and independent source-integrity judgment |
| Track4Gen-style tracking supervision | Persistent rigid anchors and observable tracers | Compare to baseline without tracking; do not supervise disappearing flame/foam as durable objects |
| VideoJAM joint appearance–motion objective | Candidate motion-preserving training branch with qualified motion targets | Same-backbone ablation and independent direction/continuity measures |
| Spatial and shifted/temporal texture statistics | Teacher/real-video material patches, preserving stochastic evolution | Frozen source, repeated texture, white noise and blur controls |
| Frequency anchoring / band constraints | Investigate support low-band stability without pinning material motion | Disclose spectral intervention; evaluate with non-spectral fidelity and blind motion judgments |

[Track4Gen](https://openaccess.thecvf.com/content/CVPR2025/html/Jeong_Track4Gen_Teaching_Video_Diffusion_Models_to_Track_Points_Improves_Video_CVPR_2025_paper.html)
jointly supervises generation and tracking; it is not a plug-in video-quality
metric. [VideoJAM](https://proceedings.mlr.press/v267/chefer25a.html) changes
training and motion guidance; it is not simply a scalar flow reward. Do not
apply a generic zero-divergence or brightness-constancy loss to every natural
medium: projection, sources/sinks, flames and transparency break that premise.

Avoid rewarding arbitrary flow magnitude or forcing moving pixels to match
the source image. Record which metric backbones/formulas each method trained
against, including reward-based selection. Keep at least one independent
instrument and blind human endpoint per family; sharing a score with a loss
is disclosed evidence of optimization, not independent validation.

## 6. Practical order and validation gates

1. **Compatibility migration.** Extract portable source-reference kernels;
   test parity against method code on a fixed fixture. Preserve `sourcefixed-1.0`
   historical records and original units. Add source hash, role-mask hash,
   reviewer scope, reference policy, sampling/window policy and failure
   policy to measurement identity before writing new records. The present
   five-field no-pooling key does not encode all these distinctions.
2. **CPU candidate pilot.** Pixelwise ΔE00, source PSNR, interior-patch detail,
   temporal activity and long-lag recurrence. Validate color conversion with
   the authors' test pairs and control mask edges, codec and resize effects.
   Reuse full RGB decodes, not endpoint flow caches, for temporal coverage.
3. **Single-cause admission study.** Include output-frame-0 redraw, later
   redraw, equal-mean texture swap, support translation/zoom, lighting change,
   spatial blur, temporal smoothing, frozen-but-sharp flow, white noise,
   foreground reversal, ping-pong, exact/recolored loop and reset seam. Add
   real surf, turbulent flame, smoke occlusion and accumulating-water negatives.
   The frame-0-redraw control is what legacy fBD can miss; a change at two
   seconds is a different, later-drift control.
4. **Learned comparator subset.** Budget LPIPS/DreamSim first, then a matched
   ORB/SIFT/LightGlue registration and CoTracker/BootsTAPIR/TRAJAN study.
   Learned encoders are additional passes, even if technically runnable on
   CPU. Preserve official inputs and track provenance; adaptations get new
   measurement identities. Do not interfere with the method's active GPU jobs.
5. **Independent confirmation.** Freeze definitions and thresholds on
   independent development anchors; evaluate untouched scenes/models with
   scene-clustered intervals. Report target sensitivity, nuisance selectivity,
   real-video false positives, medium-specific abstention and mask/backbone
   sensitivity. Do not pool windows or seeds as independent scenes. Select
   the final primary endpoints by this validity study, not significance on
   Echo versus sink. FVMD follows only when reference/sample-size requirements
   are met.
6. **CVPR evidence package.** Keep native/common inference and 5-second native
   controls distinct from 60/120-second streaming rows. Use the existing
   preselected 240-second subset for stress, recording separately requested
   rollouts versus prefixes. Measure runtime per generated video-minute,
   memory, tracker/flow coverage and sparse-versus-dense missed failures. Human
   questions separately cover source fidelity, support motion, motion presence,
   intent, replay/continuity and naturalness at real-time playback.

Migrate the architecture now; admit metrics only after these gates. Do not
declare a validated metric-spec 2.0 merely because a copied scorer reproduces
historical numbers.

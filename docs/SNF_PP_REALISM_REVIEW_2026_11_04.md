# SNF-Bench++ realism review and validation plan

Date: 2026-11-04 (Asia/Seoul). This review covers the author-provided WACV
reviews, the pasted progress report, the current journal draft, the candidate
code and stored pilot. It is a plan and assessment, not a preregistration or a
claim that a realism metric has passed. No videos were generated or rescored.
Existing uncommitted work was preserved.

## Decision

Add **realism as a separate, conditional measurement family** to the
fixed-camera benchmark. Retain the v1/v2 source/support and material-motion
axes, VBench incumbents, eligibility and time-resolved reporting. A score
must specify *what* failure it detects; visual naturalness, physical
correctness, correct material, continuity and camera stability are related
but distinct constructs. Human and animal motion remain separate extension
tracks until independently annotated and validated. A broader list of images
or a new metric alone does not resolve the WACV construct-validity criticism.

Prior work already investigates these constructs. [VBench-2.0](https://arxiv.org/abs/2503.21755)
includes physics, human fidelity and commonsense dimensions, while
[TRAJAN](https://arxiv.org/abs/2505.00209) uses point-track representations
for per-video and distribution-level motion assessment and
[FVMD](https://arxiv.org/abs/2407.16124) compares distributions of tracked
motion. Their results motivate **baselines on the same eligible inputs**, not
a claim that they solve long-horizon fixed-camera fluid realism. The
[Generative Image Dynamics paper](https://openaccess.thecvf.com/content/CVPR2024/papers/Li_Generative_Image_Dynamics_CVPR_2024_paper.pdf)
also uses dynamic-texture video features: useful distribution-level
comparator, with domain and short-window limits to be measured. The
[HVEval+ paper](https://arxiv.org/abs/2607.16742) reports MOS and preference
labels for human-centric videos and says it was accepted by TCSVT; it is a
useful subjective-study design reference, not validation of nature flow.

## 1. What the current pilot actually establishes

`manifest/support_realism_pilot_scenetether_s42.json` contains 42 generated
60-second SceneTether clips, one seed, 42 source-pasted controls and encoded
stills; the [pilot implementation](../scripts/pilot_support_realism.py)
uses the last 12% of samples at nominal 8 fps. On these data:

- The median support statistic is 2.607 for the original clips and 0 for the
  pasted controls. Every original is greater than its paired paste; 30/42
  pasted medians are exactly zero and 12/42 are positive. All 42 static-clip
  medians happen to be zero. This is not a universal H.264 noise floor.
- Edge-spill behaves opposite the prior hypothesis, so the naive direction is
  rejected. The support/dynamic boundary ratio orders the original above the
  paste in 13/13 **eligible** scenes; only 13/42 qualify. This proves neither
  perceptual validity nor generalization beyond this one construction.
- The measured `support_noise` is the spatial median of each pixel's **mean
  absolute successive grey-level change**, not a temporal standard deviation,
  pure sensor noise, or a compensation-invariant score. It can respond to
  drift, actual support change, lighting, codec artifacts or flicker. The
  statistic must be renamed/documented before it is interpreted.
- The original and its composite do not have identical encoding histories:
  the latter is decoded, edited and re-encoded. Using the same writer is not
  evidence that codec effects disappear. The controls and measurement report
  lack complete content hashes, a parent-video hash chain, timestamp/decode
  and encoding provenance, per-video error/abstention reasons and verified
  registration. The comparison is unblinded, development-only and conditional
  on one source-fixed mask set. Keep it as a descriptive development result.

The separate color audit records video/source hash checks and mask hashes; its
`manifest/pixelwise_colour_audit_input_check.json` reports 384 checks and zero
mismatches per target, plus one stale record without a video path. These
hashes and its 42-scene source-color differences do not validate any realism
axis. The p90 is a percentile, not the average of the worst 10%.

## 2. Fix the candidate study before interpreting a number

**Start with paired, aligned controls.** For every selected parent video,
construct a pass-through re-encode using the *same decode/encode pipeline* as
the paste, then compare the control against that pass-through as well as the
original. Where original pre-encode frames are actually available, construct
all variants from them and record that fact. Save parent/source/mask/control
SHA-256 hashes, pixel format, codec and encoding parameters, frame count,
actual fps and intervals, generation ID and any resampling/registration.
Do not infer codec neutrality merely because both outputs end as H.264; vary
codec/resolution/bitrate in a prespecified robustness subset. A compression-
only detector or unchanged-control should be reported as a confound, not
subtracted into an unexplained realism score.

**Use controls that preserve or challenge specific attributes.** A source
paste alone has near-constant support by construction. Evaluate it alongside
(1) matched-grain pastes with several independent noise seeds and spatial and
temporal spectra; (2) independently generated or delayed support motion,
retexturing and global light changes; (3) boundary feathering, realistic
reflections/coupling where visible, and hard/soft masks; (4) benign still
support and truly low-noise tripod footage. Test boundary-only detectors
against source-derived and independently annotated masks, shifts, feathering,
small moving regions and overlay/occlusion. Explain that a scientifically
plausible cinemagraph can be a *valid artistic output*: the problem is only a
specified task or human-rated defect, not proof that compositing is wrong.

**Keep applicability honest.** Record n eligible / attempted, per-condition
and per-medium coverage, each abstention/reason, and registration/flow/tracker
failures; a detector failure is not necessarily a video defect. Report the
whole-scene view separately: an accurate static ROI does not detect a new
object outside it. Role masks must be based on source-only I2V annotation,
not on an output's own motion. In T2V, different models produce different
layouts: use independently annotated output-specific regions, blinded to model
and metric, rather than imposing incompatible fixed coordinates; report their
uncertainty and do not label them common-source masks.

## 3. Minimal candidate suite and construct-specific tests

| Construct | Candidate evidence | Discriminating checks and declared limits |
|---|---|---|
| Fixed support and source integrity | existing source-reference PSNR/color and fBD diagnostic; whole-scene integrity judgment | camera translation/rotation/zoom; local deformation or redraw; source-paste; lighting change; report low-texture/registration failures. fBD alone is not source fidelity; historical `dE_static` retains its float32 identity. |
| Target material and location | source/prompt-conditioned material/subject/overlay annotation; region-specific activity and active area | static water plus moving boat versus moving water plus static boat; wrong medium such as fog for water; rain crossing support; zero activity, noise and flicker. Activity is not a quality score. |
| Direction and incoming flow | robust component along independently annotated image-plane direction and boundary crossing/area change, paired with support-stability check | forward/reversed/ping-pong at matched magnitude, camera zoom, expanding texture without material entry; only where direction is visible and annotated. Optical flow is an appearance proxy, not 3D material velocity. |
| Replay and temporal continuity | multi-frame recurrence plus seam/reset evidence, active-area gate and window trajectories | exact, variable-period, cross-faded and recolored loops; freeze, transient events and natural surf/fire/foliage. Report detection and false-positive rates separately; high recurrence is not intrinsically wrong. |
| Motion appearance/plausibility | flow/track statistics, dynamic-texture features and TRAJAN/FVMD/VBench comparators where applicable; optional real-reference distribution | compare coherent transport, noise warp, boiling, flicker, varying true speeds and occlusion; sparse track/flow failure may be common in water, smoke and fire. No 2D metric alone verifies physical laws. |
| Whole-scene and subject extension | explicit scene-integrity judgments; subject identity, anatomy, interaction and motion annotations when in scope | frozen subject against moving background and vice versa; occlusion and out-of-frame cases; separately validate human and animal tracks before leaderboard admission. |

Report separate axes with direction and units, and per-time-window curves,
not an overall number that lets fidelity cancel frozen or implausible motion.
Use a source-pixel still and the copied/composite controls as references, but
avoid declaring that any one candidate must detect every unrelated defect.
The existing candidate `cand-recurrence-0` already scored two unaltered
*generated* windows above 0.99 and also scored freezes near 1; those windows
are not independently labeled natural negatives. This is a reason to test
specificity, not a false-positive-rate estimate.

## 4. Real footage, sampling and statistical independence

Record rights-cleared, genuinely fixed-camera footage for multiple sites,
media, lighting conditions and motion regimes; metadata should include camera,
exposure, stabilization, resolution, fps, compression, scene family and
license. Own capture can simplify rights management but does not automatically
prove permission to release every depicted person or location. Use the source
frame for I2V and retain the real continuation as **one plausible realization**,
not the only correct pixel trajectory. Natural waves, flames and wind can be
stationary or periodic. Near-static natural scenes can be valid when they match
the task and must not be labeled as failed by default.

A single 4–5-minute clip supplies correlated windows, not dozens of independent
reference scenes. A scene-specific p5–p95 band estimated from one sequence is
unstable and can reject a valid alternative flow. First test medium/regime
reference distributions with source-family-level uncertainty and instrument
floors; use scene-specific estimates only with independent repeats and enough
coverage. Avoid assuming a Gaussian or symmetric distribution, and show
reference-data size, distribution shift and sensitivity to camera/lighting.
Never compute validation labels or calibrate a candidate on the same test
outcomes used to report its performance.

For the first confirmatory question, lock development and confirmation splits
by scene family and model family; keep crops, horizons, controls and repeated
seeds of the same scene in the same split. Freeze intended constructs,
eligibility, primary thresholds, reference choice, baselines and uncertainty
procedure before looking at held-out scores. Report scene-level paired effect
sizes and source-family-clustered intervals and severity curves. Choose
false-positive targets and sample sizes through precision/power analysis rather
than claiming 0% false positives from a tiny sample. For illustration, zero
failures in 30 independent negative scenes leaves a one-sided 95% upper bound
of about 9.5%; correlated windows cannot be substituted for independent scenes.
A leave-one-medium-out test requires a calibration rule that does not use the
held-out medium; present it separately from within-medium source holdout.

The draft's proposed **AUC ≥ 0.9 for every metric on every control and medium**
is not a defensible universal admission requirement: a support-fidelity metric
should not have to detect every motion corruption. Define targeted families
per metric, nuisances on which invariance is expected, minimum coverage and a
predeclared comparison to a simple incumbent; retain uncertain or failed
candidates as diagnostics. Calibrate direction/desirability separately. A
binary real-versus-fake result does not measure the degree or cause of a
failure, and one underpowered model-level correlation does not establish
per-video human alignment.

## 5. Human ratings that answer the reviewers

Collect blinded ratings on natural and generated clips, covering each medium,
model family, interval, severity and near-tie; use matched encoding and
randomized presentation. Separate tasks for (a) scene/support stability and
integrity, (b) intended material presence/location, (c) *amount* of material
activity, (d) perceptual motion plausibility, (e) direction/arrival when
observable, and (f) repetitive replay versus legitimate periodic behavior.
Include `cannot tell` and `not applicable`. Rate artifacts and whole-scene
integrity separately from naturalness. Use actual full-duration viewing for
full-horizon claims and separate short-window questions for localization.

Ordinal per-video ratings enable MOS/rank analysis if enough independent
raters judge each clip; pairwise preference enables tie-aware paired analysis,
not automatic per-video MOS. Source-conditioned 2AFC real-versus-generated
is a *separate* realism discrimination question: it can be influenced by
sharpness, codec and image fidelity, and is not ground-truth physical validity.
Keep paired tasks, video MOS and model-level win ratios as different analyses.
Report rater/source clustering, agreement, exclusions, missing/ambiguous
ratings, counts and uncertainty; fit calibration or regression only on
training/development folds. Derive rater and scene counts from a pilot-based
precision/power plan. Existing interim SceneTether study modules are useful
secondary evidence only where the questions and consent match; do not pool
them as if they were the new prospective validation population.

## 6. Work order, reuse and go/no-go

1. **Evidence audit:** inventory and hash existing pilot parent/composite/still
   media, scene-level coverage, actual encoder history and annotation source;
   do not rerun or overwrite earlier videos/scores. The existing controls are
   secondary exploratory evidence until this provenance is reconstructed.
2. **Independent reference and annotations:** acquire a rights-cleared diverse
   reference set, pilot two independent source-role annotations, adjudicate and
   report agreement and boundary sensitivity. Separate development from fresh
   confirmation before reference bands or thresholds are chosen.
3. **Small focused challenge:** on newly generated outputs and newly constructed
   controls, first run the pass-through, matched-grain paste, explicit
   wrong-way/ping-pong/loop, unrelated-subject-motion and real periodic
   controls. Follow the user's standing instruction to reuse existing
   videos/scores and score only new model/image/prompt outputs; do not rescore
   old videos without an explicit change to that instruction.
4. **Same-input baseline comparison:** VBench, existing task factors, and
   appropriately validated open flow/track/texture comparators with compute,
   failures and masks disclosed. Frozen author and external released methods
   are evaluated fairly; use internal and synthetic controls as explicitly
   labeled measurement checks rather than silently omitting them.
5. **Human pilot and frozen confirmation:** check playback, rating wording,
   eligibility, rater agreement and effort. Power/precision-plan the main
   human study, preregister the final analysis, then run on held-out source and
   model families. Admit only constructs supported by all applicable gates.

## 7. Draft issues to correct before presenting as established

`JOURNAL_TCSVT/sec/05_validation.tex` currently says using one encoder ensures
codec signatures cannot distinguish controls; this must be tested, not
asserted. It also states the universal AUC rule and a blanket zero loop flags;
replace these with per-axis prespecified hypotheses and reported false-positive
rates. `sec/04_measurement.tex` describes the naive codec floor as zero
unconditionally, even though 12/42 pasted controls have nonzero median
support change. `sec/03_benchmark.tex` says no system resizes the input and
that fps/encoder are fixed per track, whereas differing native pipelines may
require resizing and encoding; state the actual comparability protocol, not a
future result. A real-versus-fake 2AFC is not a substitute for axis-specific
MOS or pairwise annotations. The HVEval+ and SceneTether bibliography entries
are still author placeholders. No existing benchmark or draft result should
be labeled validated until its evidence actually exists.

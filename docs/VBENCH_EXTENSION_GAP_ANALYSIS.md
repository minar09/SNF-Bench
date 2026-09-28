# VBench extensions and the SNF-Bench v2 boundary

Status: source and implementation audit, 2026-09-28.

This note fixes the comparison boundary for SNF-Bench v2. It is based on the
official [VBench repository](https://github.com/Vchitect/VBench) at commit
[`fd18b3d`](https://github.com/Vchitect/VBench/commit/fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490),
the [VBench++ paper](https://arxiv.org/abs/2411.13503), and the
[VBench-2.0 paper](https://arxiv.org/abs/2503.21755). The attempted broader
literature search could not run because the configured Exa account had no
remaining credits. Conclusions here are therefore limited to these primary
sources and their released code, rather than presented as an exhaustive survey.

## 1. Naming and scope

The three names refer to two generations of the suite:

- **VBench++** includes the original 16-dimension VBench evaluation, the
  VBench-I2V extension, VBench-Long, and trustworthiness evaluation.
- **VBench-I2V** is the I2V component of VBench++. It adds an image suite,
  source-image consistency, and prompted camera-motion classification.
- **VBench-Long** is the long-video component of VBench++. It adapts the 16
  VBench dimensions to long inputs.
- **VBench-2.0**, arXiv:2503.21755, is a later intrinsic-faithfulness suite. It
  is not the VBench-Long paper. Its five groups cover Human Fidelity,
  Controllability, Creativity, Physics, and Commonsense.

SNF-Bench must not claim novelty for generic long-video evaluation, I2V
evaluation, source-image consistency, camera-motion classification, generic
physics evaluation, or a multi-dimensional benchmark structure. Those are
already explicit in this family.

## 2. What the released implementations actually measure

### 2.1 VBench and VBench++

VBench decomposes evaluation into 16 dimensions rather than a single score.
The temporal-quality group includes subject consistency, background
consistency, temporal flickering, motion smoothness, and dynamic degree. The
paper uses roughly 100 tailored prompts per dimension, eight 100-prompt content
categories, per-dimension human pairwise preferences, and model-level Spearman
correlation between automatic and human win ratios.

This gives SNF two requirements. It must report a profile rather than hide
opposing behaviors in a single total, and every proposed axis needs its own
human-alignment study. Correlation of one aggregate SNF score with an overall
quality preference would not validate support stability, direction, replay,
and plausibility separately.

### 2.2 VBench-I2V

The released I2V suite contributes four practices SNF should adopt:

1. Input images are high resolution and manually cropped while preserving the
   main subject. Common crops include 1:1, 8:5, 7:4, and 16:9, with arbitrary
   ratios between 1:1 and 16:9 supported.
2. Images span foreground and background content categories and have reviewed
   captions with motion descriptions.
3. The sampling protocol requests five videos per image-prompt pair and records
   random seeds.
4. I2V-specific results are reported beside the ordinary video-quality axes.

Its source consistency metrics do not identify natural flow behavior. In the
released code, both subject and background scores use
`0.4 * max(source-to-frame similarity) + 0.3 * mean(consecutive similarity) +
0.3 * min(consecutive similarity)`. DINO features are used for subjects and
DreamSim for backgrounds. This can establish retained source content, but its
terms contain no signed path, boundary crossing, recurrence lag, or medium
specific flow rule.

The camera-motion dimension tracks a grid with CoTracker and classifies seven
types from edge-point displacement between the first and last frames: pan
left/right, tilt up/down, zoom in/out, and static. It is a required incumbent
for SNF's fixed-camera condition. It is not a replacement for measuring local
material transport because uniform camera motion and region-local flow have
different spatial support.

### 2.3 VBench-Long

VBench-Long optionally splits at scene cuts, then splits each scene into fixed
clips. The released mixed configuration uses 2-second clips for most
dimensions and 10-second clips for human action, temporal style, and overall
consistency. Most dimensions run the short-video scorer on every clip and
average the clip scores.

Subject and background consistency add a slow-fast path:

- the slow branch scores all frames inside each short clip;
- the fast branch concatenates the first frame of each clip and measures
  similarity across those sparse frames;
- the fast score is quantile-mapped to the within-clip score distribution;
- the development configuration weights the two branches 0.5/0.5.

This is useful long-range coverage, but it remains an average consistency
score. It does not preserve the time of failure, worst interval, recovery,
direction, reversal, source/sink behavior, or exact long-lag recurrence. A
model can therefore have the same mean after one catastrophic late failure or
many mild errors. SNF should run VBench-Long as an incumbent and retain a
trajectory rather than only its final mean.

VBench-Long's custom-input mode supports subject consistency, background
consistency, motion smoothness, dynamic degree, aesthetic quality, and imaging
quality. This is sufficient for a reproducible incumbent panel on SNF clips.

### 2.4 VBench-2.0

VBench-2.0 adds broader intrinsic questions. Its Physics group covers
mechanics, thermotics, material changes, and multi-view geometry. Mechanics
and motion rationality use video question answering; the released code
uniformly samples at most 64 frames and returns binary outcomes after one or
more yes/no questions. Its camera-motion taxonomy adds orbit and oblique
motion. The prompt suite targets about 70 prompts per dimension and explicitly
uses visually observable outcomes and disentangled test cases.

This is the closest conceptual incumbent for naturalness. It asks whether a
physical consequence occurred, such as material changing or an action having
its expected effect. It does not expose a calibrated continuous transport
trajectory for a single fixed-camera process over 60–240 seconds. Uniformly
sampling 64 frames also cannot by itself localize a brief reset seam or state
when a flow began to fail. SNF should include the overlapping VBench-2.0
physics and motion-rationality subset as contextual evidence, then validate
its own deterministic probes against axis-specific human judgments.

## 3. Comparison matrix

| Capability | VBench / VBench++ | VBench-I2V | VBench-Long | VBench-2.0 | SNF-Bench v2 target |
|---|---|---|---|---|---|
| Generic perceptual and prompt quality | 16 dimensions | inherits quality axes | adapts 16 dimensions | intrinsic dimensions | mandatory context only |
| Source-image retention | no | DINO/DreamSim order-statistic score | no special source rule | no | shared-source alignment and role masks |
| Camera motion | dynamic degree; no requested class | seven prompted classes including static | short-clip dynamic degree | nine prompted classes | continuous rigid-support registration plus incumbent class |
| Long range | short-video design | short I2V outputs | clip average and sparse first-frame branch | up to 64 uniform VLM frames in several axes | fixed-second curves, worst window, robust slope, time-to-failure |
| Global versus local motion | whole-frame or feature similarity | edge tracks for camera class | same dimensions per clip | task dependent | rigid support and intended-motion regions reported separately |
| Requested flow direction | no | camera direction only | no | dynamic relationships, broad event reasoning | signed projection on an annotated material path |
| Incoming/source/sink behavior | no | zoom class can be a confound | no | broad mechanics questions | signed boundary flux gated by support stability |
| Reversal / oscillation | smoothness and dynamics do not encode intent | no material direction rule | no | may be visible to VLM for a tailored prompt | net/absolute transport and wrong-way fraction |
| Replay / reset seam | temporal consistency may respond | no lag-specific rule | averages can dilute failure | clip anomaly or VLM may respond | long-lag recurrence plus seam evidence and adversarial periodic controls |
| Physical naturalness | limited generic proxies | no specific physics axis | inherited proxies | explicit broad physics and commonsense | blind human primary label; mechanistic probes are explanatory |
| Applicability / abstention | dimension-specific input support | content-specific image types | six custom dimensions | initial-state prefilters in some dimensions | per-video, per-axis reason codes |

## 4. SNF additions that remain distinct

### 4.1 Spatial roles instead of whole-frame motion

Every scorable item identifies rigid support, intended moving material,
ambiguous overlay, and ignored areas. I2V uses one reviewed source-image mask
for all systems after geometry validation. T2V labels each output's first frame
under a frozen policy while hiding later frames. The benchmark reports mask
coverage and mask-induced rank sensitivity.

### 4.2 Signed material transport

For direction-eligible prompts, apparent motion or reliable tracks are
projected onto an annotated image-plane path. Report net transport, absolute
transport, directional persistence `net / absolute`, and the fraction of time
moving the wrong way. A periodic wave, turbulent eddy, or visually ambiguous
surface is marked not applicable rather than forced into a one-way score.

### 4.3 Boundary flux for incoming flow

Incoming behavior is evaluated at an annotated source/target boundary. Positive
flux denotes crossings toward the target. This result is interpretable only
when rigid support passes its separately calibrated gate. Zoom, texture
swelling, and outward transport are mandatory counterexamples.

### 4.4 Long-horizon failure trajectories

Every signal is summarized in fixed wall-clock windows shared across 60, 120,
and 240 second horizons. Report early and late values, a Theil-Sen slope, worst
window, coverage, and, after held-out calibration, first failure time and
longest failing run. This preserves failure timing that a clip average loses.

The first implementation is `scripts/long_horizon_protocol.py`; its
machine-readable axis contract is `configs/snf_v2_dimension_contract.json`.
The implementation accepts estimator outputs and never emits a combined score.
Official comparator settings and required provenance are pinned in
`configs/vbench_incumbent_protocol.json`.

### 4.5 Recurrence with natural-periodicity controls

Replay evaluation searches long lags in the dynamic region and pairs high
appearance/flow recurrence with seam evidence. Thresholds are calibrated per
medium using real fixed-camera footage. Exact loops and reset seams are
positives; real surf, flame, foliage, and precipitation are false-positive
controls. A detector trained only on synthetic loops cannot graduate to the
headline set.

## 5. Practical execution order

1. **Freeze the contract.** Review axis definitions, applicability rules,
   source/path annotations, fixed window duration, reason codes, and incumbent
   versions. Keep all score thresholds unset.
2. **Run incumbent adapters.** Store official repository commit, model weights,
   sampling, scene-splitting flag, clip length, and per-video outputs for
   VBench, VBench-Long, I2V dimensions, and the selected VBench-2.0 subset.
3. **Produce cheap trajectories.** Reuse existing optical flow and registration
   traces to emit timestamped signals. Run the trajectory summarizer before
   any new generation.
4. **Build single-cause controls.** Add foreground-only reversal, ping-pong,
   exact loop, recolored loop, reset seam, incoming/outgoing flow, zoom, texture
   swelling, photometric drift, and frozen-flow variants. Preserve the parent
   clip and every transform parameter.
5. **Calibrate on independent anchors.** Use licensed real clips and development
   corruptions to set thresholds and false-positive targets per medium. Freeze
   them before evaluating held-out generated scenes and models.
6. **Expand to 96 base scenes.** Allocate 16 independent scenes to each of the
   six registered media: river/stream, ocean/waves, precipitation, fire/smoke,
   lava/volcanic, and windborne. River plus ocean is 32/96 (33.3%), below the
   35% channel/open-water cap. Variants stay nested under the same `scene_id`.
   Enforce this with `configs/snf_v2_scene_contract.json` and
   `scripts/validate_v2_scene_manifest.py --strict-release`.
7. **Generate matched horizons and seeds.** Prefer one 240-second rollout scored
   at 60/120/240-second prefixes; keep separately requested durations in a
   distinct analysis. Use five seeds for the primary I2V panel where feasible,
   following VBench-I2V, and a pre-powered multi-seed T2V subset.
8. **Validate each axis with humans.** Ask separate support, direction,
   continuity/replay, medium identity, and plausibility questions. Include
   `cannot tell`, repeated anchors, inter-rater agreement, and full-duration
   viewing for long-horizon judgments.
9. **Audit efficiency.** Compare sparse screening with dense scoring on a
   stratified subset. Publish missed failures, rank changes, coverage, runtime,
   peak memory, and storage per video-minute.
10. **Release only admitted axes.** A headline axis must detect held-out target
    failures at a frozen real-video false-positive rate, remain selective to
    nuisance controls, align with its corresponding human question, and expose
    failure and abstention cases. All other axes remain exploratory.

## 6. Claims enabled by this design

If the validation gates pass, the defensible claim is:

> SNF-Bench evaluates the temporal trajectory of spatially localized natural
> transport in continuous fixed-camera scenes, including support stability,
> signed direction, boundary flux, recurrence, and failure timing.

The claim is narrower than comprehensive video quality, long-video evaluation,
or general physical realism. That narrowness is the source of its resolution.


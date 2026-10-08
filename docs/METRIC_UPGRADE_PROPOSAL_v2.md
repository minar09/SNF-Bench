# Metric upgrade proposal for SNF-Bench v2

Status: reviewed proposal, 2026-10-08 KST. Inputs: the method project's source-fixed
re-score of the 48-scene test split and its factorial (its docs 85, 88, 89, 91,
96), and a literature pass (sources at the end). Nothing here changes a frozen
metric. The architecture decision is recorded in `I2V_METRIC_REVIEW_2026_10_08.md`: demote
fBD, migrate the source-reference kernels with parity, and qualify the new
candidates independently. The observed factorial is retrospective evidence;
a new headline set cannot be described as frozen before those outputs existed.

---

## 1. What the method project found about fBD

fBD is ORB keypoint drift in the static region, measured against the emitted
frame 0, inside a mask derived from the output's own early optical flow. On the
48-scene test split, with two seeds, five problems appear:

| finding | evidence (method project) | consequence for SNF-Bench |
|---|---|---|
| **Wrong reference.** fBD compares a frame to the output's own frame 0, never to the source image. | An early redraw followed by a stable wrong scene scores well: "low NBF with high fBD can also come from an early scene change followed by a stable wrong scene". | For I2V, fidelity must be measured against the source image. |
| **Circular support.** Each system is scored on its own mask. | The v1.1 static fraction of the same scene differs across the 12 factorial arms by a median 0.18 (max 0.52; 43/48 scenes > 0.10). | Systems are compared on different pixels. This is objection A again, now with numbers. |
| **Geometry-only.** ORB drift misses appearance re-synthesis that keeps the layout. | UnStep redraws scene content while source-registration coverage stays ≥ 0.9; the drift shows in colour (dE) and identity PSNR. | A photometric and a perceptual channel are needed beside the geometric one. |
| **Survivor bias.** fBD averages matched points on registered frames only. | Registration *failure* carries a significant interaction (Γ_F +0.12 [0.04, 0.22]) where fBD's own interaction does not (+1.11 [−0.53, 2.85]). | Report failures separately from conditional displacement; rank imputation is sensitivity only. |
| **Weak and unstable.** | Colour drift replicates across seeds (dE Γ +5.99 [2.17, 10.13]) while fBD does not. fBD's arm ranking across granularities has τ = 0.33, and P(same winner at all k) = 0.00. fBD abstains below 12 ORB keypoints (2/48 test scenes; small supports such as iwb03 at 0.8% of the frame are fragile). | As a headline factor fBD has low power, and its sparse detector abstains on low-texture nature scenes. |

The project's response, already built and parity-tested against the SNF-Bench
call path (`tools/factorial_scoring/sourcefixed_metrics.py`):

* **source-derived masks** — a four-label map (ignore / rigid support / dynamic /
  overlay) from the source image and prompt via CLIPSeg, with per-scene review
  status. Precipitation is treated as an overlay medium, so motion metrics
  abstain by construction.
* **source image as reference** — `fBD_src`; static colour `dE_static` (Lab
  distance, source support mean → late window); `idPSNR_late` (grey PSNR versus
  source in the support).
* **registration as a first-class result** — source-registration coverage, with
  c < 0.5 counted as a failure and never averaged; fallbacks never count as
  compensation; fBD on matched timestamps only, with < 25% common timestamps
  abstaining.
* **endpoint eligibility** per scene and family, frozen before scoring.

**Assessment.** These address reference, partition, appearance-channel, and failure-accounting
problems and provide a useful compatibility foundation. Port the kernels with
parity rather than importing the experiment harness wholesale. The scorer
still has fractional-duration windows and conditional motion means; the
review scope of masks must be carried explicitly. Matching failure is not
uniquely drift, and fBD remains informative on catastrophic k=6 collapse.

## 2. What the literature offers, by reporting family

### 2.1 Support fidelity (replacing fBD as the headline)

| instrument | what it adds | why it fits |
|---|---|---|
| **CIEDE2000** colour difference in the support, versus source, per second | pixelwise perceptual colour drift; retain the method's uint8-Lab mean distance under a separate legacy identity | the replicating signal in the factorial is colour |
| **LPIPS / DreamSim** on support crops versus source | perceptual and semantic re-synthesis that keeps geometry (the UnStep failure) | DreamSim combines CLIP, OpenCLIP and DINO features tuned to human similarity |
| **SuperPoint + LightGlue** in place of ORB for source registration | candidate for reduced matching failures; qualify against ORB/SIFT on our support scenes | reported to beat ORB by large margins in low-texture and blur conditions |
| **CoTracker3** dense tracks seeded on a support grid | per-point drift plus estimated visibility; report occlusion separately from drift and tracker failure | addresses survivor bias directly; online mode handles long clips in windows |
| **Low-band spectral drift** in the support: DC and low-frequency band energy versus source, per second | colour, tone and layout drift as a curve | FreqForcing shows autoregressive drift lives in DC/low bands but reports it only as plots; SNF-Bench can make it a region-resolved number |

Provisional candidate panel for support fidelity: **CIEDE2000 + idPSNR versus source,
plus registration failure rate**, with LPIPS/DreamSim as the perceptual check.
fBD continues as a *geometric diagnostic*, rebased to the source with coverage
and failure rates beside conditional values. Arbitrary displacement imputation
is prohibited; rank imputation may appear only as a labelled sensitivity.
This panel is provisional until independent validity gates pass.

### 2.2 Activity and persistence (the dynamic region)

| instrument | what it adds |
|---|---|
| camera-compensated late flow in the **source-derived** dynamic region | the method's motion guard; MCFF-L on a non-circular mask |
| **high-band energy retention**: spatial high-frequency energy, and temporal frame-difference energy, in the dynamic region relative to the source or early window | candidate detail/activity diagnostic; distinguish spatial from temporal bands and reject freeze/noise gaming. FreqForcing motivates the investigation but does not validate this RGB metric. |
| **texture-statistics retention**: Gram or DISTS-texture distance of dynamic-region patches versus the early window | tolerant of the pixel resampling natural flow *should* show, sensitive to the smoothing it should not. WorldScore uses first-vs-last Gram distance as "style consistency". |

The split matters. Support must be held to **strict** fidelity, because a
re-textured rock is the failure. The dynamic region must be held to
**statistical** fidelity, because water whose pixels match frame 0 is frozen.
DISTS explicitly tolerates texture resampling, but includes both structure and
texture terms. Prioritize it on material tiles as an exploratory appearance
measure; it does not detect freezing or replay. It may also be a supplementary
support metric after redraw sensitivity is established, rather than being
prohibited there by definition.

### 2.3 Direction and regime

Dense point tracks (CoTracker3) give net displacement per dynamic track. Compare
the displacement histogram with the declared direction, and abstain for
not-applicable regimes (spec rule R3). This supplies a second instrument alongside the M2 flow probe. Validate
tracer survival and path interpretation on each medium before using it: point
tracking accuracy on published datasets is not validation of material velocity.

### 2.4 Replay, flicker and naturalness

| instrument | what it measures | note |
|---|---|---|
| **TRAJAN** (DeepMind, code in `tapnet`) | point-track autoencoder reconstruction (Average Jaccard); reports human alignment on evaluated video subsets; no nature-specific or replay validity is established | score per window (a few seconds) to get a naturalness trajectory over 60–240 s |
| **FVMD** (ICML 2024) | Fréchet distance of track velocity and acceleration features | distribution-level; needs a *real* fixed-camera reference set, which is the Tier 1 item 9 real-footage anchor |
| **forward–backward flow cycle error** (AEPE) | estimator cycle disagreement | WorldScore's named photometric consistency; not proof of non-physical motion |
| **dynamic-region self-similarity over time** | replay and loops | with natural-periodicity controls, as M2 planned |
| **high-band temporal instability** | flicker | the other half of the spectral measure in §2.2 |

### 2.5 Runtime

Not an SNF measure. Required in every run record: seconds of compute per
generated second, GPU, steps.

## 3. Prior art the paper must cite

* **WorldScore** (2025): its *motion accuracy* is the maximum flow inside a
  SAM2-tracked dynamic mask minus the maximum flow outside it — a static/dynamic
  separation, published before SNF-Bench. It also defines Gram-based style
  consistency and a forward–backward photometric consistency, and a
  400-participant study used to select its subjective-quality metric combination;
  this does not validate all its motion dimensions individually. Add it to related work with SGC
  (`BENCHMARK_LANDSCAPE_2026.md` §1). SNF-Bench's distinct ground narrows further
  to **long horizons, region-resolved accumulation curves, and source-anchored
  natural-flow persistence**.
* **FreqForcing** (2026): a 60/120 s Self-Forcing-family method, and the
  frequency-band view of drift. It should be a baseline if code is released.
* **TRAJAN, FVMD, CoTracker3, DISTS, DreamSim, LightGlue** as instruments.

## 4. Losses (method side) — and a Goodhart warning

| loss | effect reported | use |
|---|---|---|
| **Track4Gen** (CVPR 2025): dense point-tracking loss on diffusion features | reduces appearance drift | support stability |
| **VideoJAM**: joint appearance–flow prediction | motion coherence | dynamic persistence |
| **frequency anchoring** (FreqForcing) | stabilises band energy over 60 s | long-horizon drift |
| masked **LPIPS / CIEDE2000 to source** in the support; **Gram/DISTS** texture loss in the dynamic region | direct optimisation of §2.1–2.2 | glassy-water prevention |

**Warning.** A method trained on a loss that *is* the benchmark measure is
optimising the score, not the phenomenon. For every family, at least one
reported measure must be one the method did not train on. Human judgement (spec
§6) remains the arbiter for naturalness. If a method uses any loss above, its
paper must say so beside the table.

## 5. Validation before anything becomes headline

Four of the six v1 factors failed the selectivity screen, so every new measure
goes through the same screen (`SNF_V2_VALIDATION_MATRIX.md`), with three new
corruption families that target what fBD missed:

1. **frame-0 redraw, then stable** — alter support before the emitted reference
   frame, then retain the wrong scene. Legacy frame-0 fBD can miss this;
   source-anchored measures must respond. A separate redraw at t = 2 s can
   affect frame-0 fBD and tests later drift instead.
2. **glassy water** — progressive temporal low-pass of the dynamic region only.
   High-band retention and texture statistics must respond; support measures
   must not.
3. **replay** — loop a short dynamic-region segment. Long-lag sequence
   recurrence must be tested against natural periodic controls. Short-window
   TRAJAN and persistence can both remain strong; neither is assumed to detect
   replay without a separate validation.

Admission requires the documented direction, monotonicity, off-target
selectivity and partition robustness; failing measures stay diagnostics.
Cost: RGB colour/detail/recurrence probes can use CPU decodes. LPIPS, DreamSim,
DISTS and LightGlue require additional learned-feature passes; CoTracker and
TRAJAN require tracking passes. Measure these costs rather than describing
all of steps 1–3 as existing-pass CPU work.

## 6. Recommended order

1. **Port and qualify source-fixed kernels** in a provisional integration:
   source-derived masks, source reference, registration coverage and failure
   accounting, eligibility. It is built and parity-tested, so this is
   compatibility integration, not automatic admission as validated spec 2.0.
   Extend measurement identity with source/reference, mask hash/review scope,
   temporal sampling/window and failure policies before producing new records;
   the current five-field key does not encode these distinctions.
2. Add **CIEDE2000, LPIPS/DreamSim** (support) and **high-band retention +
   texture statistics** (dynamic): CPU RGB candidates first, learned passes budgeted separately.
3. Build the three new corruption families and run the selectivity screen.
   Freeze the headline set on independent controls and confirmation sources.
   Existing factorial-driven metric changes are declared retrospective.
4. GPU pass: **CoTracker3** (survival, direction), **TRAJAN** (naturalness), and
   swapping ORB for **SuperPoint + LightGlue** on registration.
5. FVMD once the real-footage anchor set exists.

## Sources

* TRAJAN, Direct Motion Models for Assessing Generated Videos — [arXiv 2505.00209](https://arxiv.org/pdf/2505.00209), [project](https://trajan-paper.github.io/), [code](https://github.com/deepmind/tapnet/)
* FVMD — [arXiv 2407.16124](https://arxiv.org/abs/2407.16124), [code](https://github.com/DSL-Lab/FVMD-frechet-video-motion-distance)
* CoTracker3 — [arXiv 2410.11831](https://arxiv.org/html/2410.11831v1)
* DISTS — [arXiv 2004.07728](https://arxiv.org/pdf/2004.07728)
* DreamSim — [arXiv 2306.09344](https://arxiv.org/html/2306.09344v3)
* LightGlue — [arXiv 2306.13643](https://arxiv.org/pdf/2306.13643); low-texture comparison: [arXiv 2505.17973](https://arxiv.org/html/2505.17973v1)
* WorldScore — [arXiv 2504.00983](https://arxiv.org/html/2504.00983)
* FreqForcing — [arXiv 2607.27110](https://arxiv.org/html/2607.27110); FreeLong — [arXiv 2407.19918](https://arxiv.org/html/2407.19918)
* Track4Gen — [arXiv 2412.06016](https://arxiv.org/abs/2412.06016)
* Dynamic-texture evaluation (DT-FVD) — [arXiv 2104.05940](https://arxiv.org/pdf/2104.05940)

## Reviewed decision and practical limitations (2026-10-08 KST)

The controlling research review is [I2V_METRIC_REVIEW_2026_10_08.md](I2V_METRIC_REVIEW_2026_10_08.md).
It adds whole-scene integrity outside conservative ROIs, explicit output-time
occlusion versus source-level abstention, spatially distributed support
registration, noise/freeze counterexamples for spectral measures, and
independent human validation. FreqForcing's audited public repository has no
released inference pipeline yet. Official DreamSim code is
[ssundaram21/dreamsim](https://github.com/ssundaram21/dreamsim). No metric has
been changed or admitted by this documentation review.

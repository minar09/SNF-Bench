# SNF-Bench — METRIC SPEC v1.1 (FROZEN 2026-08-13)

**The metric family is closed at six names. No further renames are permitted.**

    fBD · NBF · MCFF-E / MCFF-L · FP · DLR · DAR

This document is the single authority and supersedes v1.0 in full. Where it
disagrees with `latex/`, `scripts/`, or `metric_code/`, this document wins and
the other is a bug.

Definitions may still be *removed* before the Aug 20 freeze if validation
(§5.6 of the paper) fails them. They may not be renamed or silently redefined.

**v1.0 → v1.1 changelog.** No per-video measurement semantics changed, so
records stamped `metric_spec_version: 1.0` remain valid as written.
1. §2 NBF — the temporal factor is the **effective sampled rate**, not the
   native container rate. The v1.0 claim of a frame-rate confound (and the
   "LTX rank 6→8" finding) is **retracted**; see §2.
2. §6 — the DLR/DAR tiebreak is **pre-committed**, before any validation
   numbers exist.
3. §8 (new) — sweep integrity contract: failure stream, resumability,
   provenance fields, and the schema scan.
4. §9 (new) — pre-registered decision rules for the Aug 14–18 gates.

---

## 0. Why v1.0 exists

Three mismatches between the shipped code and the frozen prose were found on
2026-08-13 by reading `metric_code/snf_task_metrics.py` against `sec/4_metrics.tex`.
All three were validity defects, not presentation issues:

| # | prose said | code did | consequence |
|---|---|---|---|
| 1 | `DriftFrac = clip(1 − F_comp/F_raw, 0, 1)` | `stat_mag/dyn_raw` — a **static-to-dynamic leakage ratio** that never touches the compensated flow | unbounded above; >1 on 20/161 clips; every causal reading void |
| 2 | "normalized to the benchmark evaluation resolution **and frame rate** before measurement" | no *container* resampling, but `read_frames` subsamples to `SAMPLE_FPS=8` before computing flow | prose and code describe different mechanisms; the metric is time-normalized by subsampling, which the prose never states |
| 3 | drift compensation described as removing "coherent global displacement" | per-component **median** of static flow — pure translation | rotation/scale validation would fail against our own estimator |

Defect 1 is why the family has six names instead of five: the shipped quantity
was a real and useful measurement wearing the wrong name.

---

## 1. Notation

$I_t$ is frame $t$ of a $T$-frame sequence at native frame rate $f$, $\Delta t = 1/f$.
$W$ is frame width in pixels, $d$ the frame diagonal.
$\mathbf{u}_t(\mathbf{x})$ is optical flow $I_t \to I_{t+1}$.
$\Omega_{\text{static}}$, $\Omega_{\text{flow}}$ are the two mask labels (§4).
$\mathcal{E}$, $\mathcal{L}$ are equal-duration early and late windows; $\mathcal{E}$ starts after warm-up.

**Region status (corrected 2026-08-13, third pass).** The implemented partition
is **two-way**: `build_masks()` thresholds early-window flow by Otsu into
dynamic and static, erodes the static region and drops a 4% border as the
ignored transition band. There is **no $\Omega_{\text{overlay}}$ label in the
metric code**, and no source-image mask for I2V -- both tracks derive the
partition from each generated sequence. Any earlier text in this spec or the
paper describing a three-label partition, human-verified first-frame
annotation, or inter-annotator agreement described an intended protocol rather
than the implemented one, and has been corrected. The consequence for layered
content (rain/snow over support) is stated as a limitation and quantified by
the mask erosion/dilation study rather than solved.

---

## 2. The six metrics

### fBD — Feature-aligned Background Drift ↓
Accumulated geometric displacement of persistent structure in the static region.

$$\mathrm{fBD} = \frac{100}{d}\cdot\frac{1}{|\mathcal{L}|}\sum_{t\in\mathcal{L}} \operatorname{median}_{(p,q)\in\mathcal{M}_t}\lVert p-q\rVert_2$$

Units: % of frame diagonal. Independent of drift compensation — **not** recomputed when §3 changes.
Must be reported with per-category **match coverage and abstention rate** (sparse ORB on night/fire scenes).

### NBF — Normalized Background Flow ↓
Instantaneous motion energy inside the static region, normalized in space **and time**.

$$\mathrm{NBF} = \frac{10^3}{W\,\Delta t}\cdot\frac{1}{T-1}\sum_{t}\ \operatorname{mean}_{\mathbf{x}\in\Omega_{\text{static}}}\lVert\mathbf{u}_t(\mathbf{x})\rVert_2$$

Units: $10^{-3}$ frame-widths **per second**.

- Formerly "BFR / Background Flow Ratio". **It was never a ratio** — there is no denominator that is itself a measured flow. The name asserted a relationship that does not exist.
- $\Delta t$ is the **effective** inter-frame interval of the measurement, not the container's. `read_frames` subsamples with `interval = max(1, round(f_native / 8))`, so flow is measured between *sampled* frames. In this corpus native rates are 16 and 24 fps -> intervals 2 and 3 -> **exactly 8.000 Hz for all 1881 videos**.
- **Retraction (2026-08-13, second pass).** An earlier version of this spec scaled by *native* fps and reported that LTX-Video moved from rank 6 to rank 8 on I2V-5s. That was wrong in both directions: the subsampling had already equalized the temporal rate, so scaling by native fps *introduced* a 1.5x error rather than removing one. LTX ranks 6th, ahead of both Wan models, as it always did. There was never a frame-rate confound in these flow magnitudes.
- The per-second unit is nevertheless kept: it makes NBF physically meaningful, and it stays correct for a future model whose native rate is not a clean multiple of `SAMPLE_FPS` (30 fps -> interval 4 -> 7.5 Hz). For this corpus it is a uniform x8 rescale that changes no ranking.
- Do **not** normalize by whole-frame flow: that couples background leakage to foreground behaviour and inflates NBF for methods whose dynamic motion decays.
- Independent of drift compensation — **not** recomputed when §3 changes.

### MCFF-E, MCFF-L — Motion-Compensated Foreground Flow ↑
Dynamic-region motion magnitude after global-motion compensation, in the early and late windows.

$$\mathrm{MCFF}(\mathcal{W}) = \frac{1}{|\mathcal{W}|}\sum_{t\in\mathcal{W}}\ \operatorname{mean}_{\mathbf{x}\in\Omega_{\text{flow}}}\lVert\tilde{\mathbf{u}}_t(\mathbf{x})\rVert_2$$

Both windows are always reported, so a uniformly-frozen method cannot look strong through a ratio alone.
**Depends on §3 — recomputed whenever compensation changes.**

### FP — Flow Persistence ↑
$$\mathrm{FP} = \min\!\left(\frac{\mathrm{MCFF}(\mathcal{L})}{\mathrm{MCFF}(\mathcal{E})+\epsilon},\ c\right)$$

Clipped at fixed $c$ to bound unstable ratios when early motion is small.
FP ≈ 1 means retained motion; ≪ 1 means decay; > 1 is **not** automatically better.
**FP is never reported without its MCFF magnitudes.** **Depends on §3.**

### DLR — Drift Leakage Ratio ↓
Static-region flow relative to *raw* dynamic-region flow, late window.

$$\mathrm{DLR} = \frac{F_{\text{static}}}{F_{\text{dyn,raw}}+\epsilon}$$

This is exactly the quantity the shipped code has always computed.

- **Unbounded above.** DLR > 1 means the background moves more than the subject. Empirically > 1 on 20/161 T2V-60s clips.
- Describe **only** as "background-flow magnitude relative to raw dynamic-region flow". **Never** as a fraction, share, or percentage.
- Independent of §3 (uses raw dynamic flow) — **not** recomputed when compensation changes.

### DAR — Drift Attenuation Ratio ↓
Signed relative change in dynamic-region flow after global-motion compensation.

$$\mathrm{DAR}_{\text{signed}} = 1 - \frac{F_{\text{dyn,comp}}}{F_{\text{dyn,raw}}+\epsilon}, \qquad \mathrm{DAR}_{\text{report}} = \operatorname{clip}(\mathrm{DAR}_{\text{signed}},\,0,\,1)$$

- **Storage is signed. Reporting is clipped. Validation uses signed.** Negative values are information, not noise: compensation *increased* measured foreground-flow magnitude, which happens when local flow opposes the estimated global field. Empirically negative on **22/161** T2V-60s clips.
- Negative incidence is tabulated per method in supplementary, with one limitations sentence. Volunteering it converts a vulnerability into demonstrated rigor.
- Interpret as "global compensation reduces measured dynamic-region flow by X% **under this estimator**". **Never** "X% of the motion is drift".
- **Depends on §3 — recomputed whenever compensation changes.**

### DLR and DAR are not substitutes

They answer different questions and cross-check each other:

| | question | depends on compensation? |
|---|---|---|
| DLR | *where* is the motion energy — static or dynamic region? | no |
| DAR | what is the signed relative attenuation of measured dynamic-region flow after global similarity compensation? | yes |

Causal-Forcing at DLR 0.939 / DAR 0.400 is the worked example: high
static-region motion energy accompanies a 40% reduction in measured
dynamic-region flow after fitted similarity compensation. This is an
attenuation diagnostic, not a causal decomposition; the residual may include
non-rigid instability, intended local motion, partition contamination, or flow
error.

**Neither is promoted to headline before validation.** DAR matching the draft
formula is not a reason to prefer it; DLR may prove the more stable measurement
despite being the less elegant one. The decision gate is §6.

---

## 3. Global-motion compensation (P0#1 — NOT YET MERGED)

**Current shipped behaviour (to be replaced):** $\mathbf{g}_t$ = per-component
median of $\mathbf{u}_t$ over $\Omega_{\text{static}}$; $\tilde{\mathbf{u}}_t = \mathbf{u}_t - \mathbf{g}_t$.
Translation only. Under centred rotation the median is near zero, so
compensation fails and Fig. 3(b) would indict our own estimator.

**Frozen replacement — robust *similarity*, not full affine:**

$$T_t(\mathbf{x}) = s_t R_t \mathbf{x} + \mathbf{b}_t, \qquad \mathbf{d}_t(\mathbf{x}) = T_t(\mathbf{x}) - \mathbf{x}, \qquad \tilde{\mathbf{u}}_t(\mathbf{x}) = \mathbf{u}_t(\mathbf{x}) - \mathbf{d}_t(\mathbf{x})$$

Similarity rather than unrestricted affine because fixed-camera generation
failures plausibly resemble translation, slight rotation and zoom, whereas
affine shear can absorb legitimate local deformation and over-correct.

Procedure per adjacent frame pair:
1. Sample points $\mathbf{x}_i \in \Omega_{\text{static}} \setminus \Omega_{\text{overlay}}$.
2. Correspondences $\mathbf{x}_i \to \mathbf{x}_i + \mathbf{u}_t(\mathbf{x}_i)$.
3. `cv2.estimateAffinePartial2D(..., method=cv2.RANSAC)`.
4. Compensate pointwise as above.

**Fallback, recorded not hidden:** on insufficient correspondences or RANSAC
failure, fall back to median translation and set
`compensation_mode="translation_fallback"` **per video**. Fallback frequency is
reported per category in supplementary.

**Gate before any full sweep:** on 5 clean clips with synthetic translation,
rotation and scale, the estimator must recover the injected parameters
approximately and reduce static-region residual flow monotonically. If rotation
or scale response is non-monotonic, **stop — do not run the benchmark.**

**Recompute scope on merge:** MCFF-E, MCFF-L, FP, DAR. **Not** fBD, NBF, DLR.
This is evaluation-only recomputation from stored videos; no regeneration.

> Correction to an earlier note in `docs/CLAIM_MATRIX.md`: DAR was "zero
> recompute" only under the *old* translation compensation. Once §3 lands, the
> stored `MCFF_late` / `dyn_res` values are obsolete and DAR must be recomputed
> with them.

---

## 4. Masks (P0#2 — NOT YET BUILT, gate Aug 14)

Three labels, not two: $\Omega_{\text{static}}$, $\Omega_{\text{flow}}$, $\Omega_{\text{overlay}}$.

$\Omega_{\text{overlay}}$ covers pixels where dynamic content transits static
support — rain and snow in front of buildings, smoke over background. These
pixels are **excluded from headline fBD and NBF**. Rain/snow static fidelity is
reported over $\Omega_{\text{static}} \setminus \Omega_{\text{overlay}}$.
Not a corner case: precipitation is 21 of 100 prompt-durations
(`tables/category_balance.md`).

**I2V:** one mask per benchmark item from the shared source image, identical for every model.

**T2V:** one mask **per model output**, derived from **that model's own first frame only**.
The annotator/segmenter never sees a later frame. The mask therefore depends on
generated layout but **not** on the failure being measured, so long-horizon
drift cannot contaminate it. A single shared spatial mask across models is
invalid for T2V and is not used.

Agreement reporting: automated proposal → one annotator corrects → a second
annotator independently labels a 20–25% subset. Report IoU, Cohen's $\kappa$,
and overlay fraction. Two annotators are not required on every frame.

---

## 5. Implementation conventions (frozen)

| convention | value |
|---|---|
| resolution | normalized to benchmark evaluation resolution before measurement |
| **frame rate** | container rate preserved; the metric subsamples to `SAMPLE_FPS = 8` before flow. $\Delta t$ in NBF is the **effective** sampled interval (`f_native / max(1, round(f_native/8))`), which is 8.000 Hz for every video in this corpus. |
| flow estimator | fixed globally, released with code; second backbone on a 10–20% stratified subset for robustness |
| feature extractor, robust thresholds, warm-up, window extents, $c$, transition band, $\epsilon$ | fixed globally before the final sweep |
| aggregation | prompt-level; category **macro**-average; bootstrap 95% CI, 10k resamples, seed 0 |
| storage | signed DAR; per-video `compensation_mode`; per-video fps |

The frame-rate row is a **change** from `sec/4_metrics.tex` line 74, which
claimed a frame-rate normalization the code performs by a different mechanism
(subsampling) than the prose implies (resampling).

---

## 6. Decision gate — which of DLR / DAR headlines

Run both through the full perturbation suite (§5 of the paper). Both get their
own row in the validation table; a metric we ship passes the same gate as any
other.

Keep a metric in the **main** family only if:
- strong monotonic correlation with injected global-motion strength;
- reasonably stable across scene categories;
- for DAR: negative values rare **or** interpretable;
- acceptable sensitivity to the flow backbone.

Otherwise it moves to supplementary as a diagnostic. **Do not force the
prettier formula to become the paper metric.**

### Pre-committed tiebreak (written 2026-08-13, before any numbers exist)

> **The headline drift-leakage metric is whichever of DLR and DAR passes
> selectivity and calibration with the stronger margin. The other is reported
> alongside it in Tab. 3 regardless.**

Margin is the *minimum* across the three admission criteria, each normalized to
its own threshold, so a metric cannot win by excelling on one axis while barely
clearing another:

    margin(m) = min( rho_calib(m) / 0.80,
                     selectivity(m) / 2.0,
                     (1 - cross_category_CV(m)) / 0.70 )

with `rho_calib` the Spearman correlation against injected global-motion
strength, `selectivity` the ratio of response under the targeted perturbation to
the largest response under an unrelated one, and `cross_category_CV` the
coefficient of variation of the metric's response slope across scene categories.
Thresholds are the admission bar; a metric with `margin < 1` on any term does not
enter the main family at all. Ties within 10% on margin resolve to **DLR**,
because it is compensation-independent and therefore cannot be invalidated by a
later change to the estimator.

Written now this is protocol. Written on Aug 18 it would be curve-fitting.

### DLR's own validation obligation

DLR now ships as a headline *candidate*, so it passes the same gate as every
other metric and gets **its own row in Tab. 2**, not a mention. Its expected
perturbation responses, fixed in advance:

| perturbation | expected DLR response |
|---|---|
| global translation / rotation / scale, increasing | **increase**, monotone |
| dynamic-region attenuation (static untouched) | **increase** — the denominator shrinks. This is a *confound*, not a success: DLR rises for a frozen video and for a drifting one alike, and Tab. 2 must show it, since it is the strongest argument for reading DLR jointly with MCFF. |
| late freeze | increase, for the same reason |
| zero-motion floor (duplicated frames) | undefined / dominated by estimator noise — report the floor, do not report a ratio |

That second row is the reason DLR is not automatically the safer choice despite
being compensation-independent.

---

## 7. Banned language (enforced by grep)

| banned | replacement |
|---|---|
| `DriftFrac` | `DLR` or `DAR` — name which |
| `BFR`, "Background Flow Ratio" | `NBF`, "Normalized Background Flow" |
| "94% of Causal-Forcing's motion is drift" | "static-region motion energy is ~94% of dynamic-region motion energy (DLR 0.94)" |
| "X% of the motion is drift" | "global compensation removes X% of measured dynamic-region flow under this estimator" |
| "fraction of motion", "share of DD that is drift" | "signed relative change in dynamic-region flow after compensation" |
| "SNF recovers true dynamic motion" | "flow surviving global-motion compensation" |
| "global compensation isolates physical foreground flow" | "…reports the signed relative attenuation after fitted global similarity compensation" |
| "VBench ranking is wrong" | "whole-frame motion and SNF's spatially resolved diagnostics can yield different interpretations of the same outputs" |

Historical artifacts under `raw/_internal_ablations/` and the verbatim
`metric_code/` are **provenance records and are not rewritten**; they carry
supersession headers instead. Raw metric JSONs keep their original keys; the
rename happens on the way into tables (`scripts/build_tables.py`).


---

## 8. Sweep integrity contract

Added in v1.1 after the CausVid gap: 29 of 30 videos were lost to one cascading
CUDA fault, and because failures were written *as records*, a coverage tool
counting records reported the entry complete.

1. **Failures never enter the results stream.** A failed video is written to
   `failures/<track>/<key>/<dur>.jsonl`, never to `per_video`. A metrics file
   therefore contains only measurements, so counting its records is the same as
   counting valid data. `scripts/rerun_metrics.py` exits non-zero if any failure
   survives, so a broken sweep cannot pass silently.
2. **Crash isolation with resume.** Each video's result is written atomically
   the moment it is computed; a worker that dies is restarted on the remainder
   (`scripts/metric_worker.py`). A context fault exits the process deliberately
   rather than failing every remaining video for the same dead reason.
3. **Provenance on every record**: `metric_spec_version`, `fps`, `n_frames`,
   `width`, `height`, `mask_version`, `compensation_mode`,
   `compensation_provisional`, `flow_backbone`, `feature_backbone`.
4. **Mechanical validity scan** (`scripts/schema_scan.py`) over every artifact:
   required keys, finite values, non-degenerate masks, sampled-frame count
   consistent with container frames and `SAMPLE_FPS`, and every video on disk
   accounted for. Exits non-zero on any blocking problem. Coverage claims cite
   this scan, not an anecdote.
5. **Coverage counts measurements, not files** (`valid_task_records()`), and the
   matrix prints `T<n>/<total>` whenever they disagree.

## 9. Pre-registered decision rules

Fixed in advance so the gates are mechanical rather than narrative.

**Aug 16 — I2V track.** The gate is ">= 3 distinct *published* public I2V
baselines with valid 60 s data", counting distinct published models rather than
configuration variants of one family.

- *Resolved 2026-08-13:* the CausVid and Causal-Forcing-framewise 60 s/120 s
  videos were verified intact on disk (30/30 and 20/20 readable, uniform frame
  counts). The gap is a **metric** failure, not a generation failure, and is
  therefore re-runnable. Had the videos been corrupt it would have counted as a
  generation failure under the frozen taxonomy: gate fails at 2/3, I2V moves to
  supplementary, the paper states the frozen outcome, and **no regeneration
  sprint is undertaken**.
- The gate reads **coverage**, not final values, so it does **not** wait on the
  affine merge. Compensation-dependent fields in the re-run records are stamped
  `compensation_provisional: true` and are recomputed sweep-wide afterwards.

**Aug 14 — masks.** If any of the seven pilot categories cannot be labelled
under the three-label schema without ambiguity that annotators cannot resolve
consistently, the affected category moves to a stress-test subset rather than
the headline set, and the mask definition is not stretched to cover it.

**Aug 18 — metric admission.** A metric failing §6 moves to supplementary. If
*both* DLR and DAR fail, the drift-leakage factor is reported as fBD + NBF only
and the paper's third axis is scoped down accordingly. That outcome is
acceptable and pre-approved; a benchmark may not ship a metric it could not
validate.

**Any date — a figure without a spec-versioned provenance footer does not enter
the LaTeX**, and the red-team checklist verifies no `PRE-FREEZE DIAGNOSTIC`
watermark survives in the submitted PDF.

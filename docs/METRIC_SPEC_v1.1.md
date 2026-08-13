# SNF-Bench — METRIC SPEC v1.0 (FROZEN 2026-08-13)

**The metric family is closed at six names. No further renames are permitted.**

    fBD · NBF · MCFF-E / MCFF-L · FP · DLR · DAR

This document is the single authority. Where it disagrees with `latex/`,
`scripts/`, or `metric_code/`, this document wins and the other is a bug.

Definitions may still be *removed* before the Aug 20 freeze if validation
(§5.6) fails them. They may not be renamed or silently redefined.

---

## 0. Why v1.0 exists

Three mismatches between the shipped code and the frozen prose were found on
2026-08-13 by reading `metric_code/snf_task_metrics.py` against `sec/4_metrics.tex`.
All three were validity defects, not presentation issues:

| # | prose said | code did | consequence |
|---|---|---|---|
| 1 | `DriftFrac = clip(1 − F_comp/F_raw, 0, 1)` | `stat_mag/dyn_raw` — a **static-to-dynamic leakage ratio** that never touches the compensated flow | unbounded above; >1 on 20/161 clips; every causal reading void |
| 2 | "normalized to the benchmark evaluation resolution **and frame rate** before measurement" | no resampling; native FPS preserved | 16 vs 24 fps confound survived undetected; LTX-Video's static drift understated 1.5× |
| 3 | drift compensation described as removing "coherent global displacement" | per-component **median** of static flow — pure translation | rotation/scale validation would fail against our own estimator |

Defect 1 is why the family has six names instead of five: the shipped quantity
was a real and useful measurement wearing the wrong name.

---

## 1. Notation

$I_t$ is frame $t$ of a $T$-frame sequence at native frame rate $f$, $\Delta t = 1/f$.
$W$ is frame width in pixels, $d$ the frame diagonal.
$\mathbf{u}_t(\mathbf{x})$ is optical flow $I_t \to I_{t+1}$.
$\Omega_{\text{static}}$, $\Omega_{\text{flow}}$, $\Omega_{\text{overlay}}$ are the three mask labels (§4).
$\mathcal{E}$, $\mathcal{L}$ are equal-duration early and late windows; $\mathcal{E}$ starts after warm-up.

**All region metrics are computed over $\Omega_{\bullet} \setminus \Omega_{\text{overlay}}$.**

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
- The $\Delta t$ term is not cosmetic. The audit preserves each method's native frame rate, so per-frame flow is a 1.5× confound between 16 and 24 fps methods. Measured (`manifest/video_meta.csv`): all methods 16 fps **except LTX-Video at 24**. Per-second normalization moves LTX from rank 6 to rank 8 on I2V-5s, past both Wan models.
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
- Interpret as "global compensation removes X% of measured dynamic-region flow **under this estimator**". **Never** "X% of the motion is drift".
- **Depends on §3 — recomputed whenever compensation changes.**

### DLR and DAR are not substitutes

They answer different questions and cross-check each other:

| | question | depends on compensation? |
|---|---|---|
| DLR | *where* is the motion energy — static or dynamic region? | no |
| DAR | how much apparent dynamic motion does a **global-displacement model explain**? | yes |

Causal-Forcing at DLR 0.939 / DAR 0.400 is the worked example: enormous
static-region motion energy, of which a rigid global model explains only ~40%.
The residual is **non-rigid** instability — warping, boiling — which a
translation-only account would have misdescribed entirely.

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
| **frame rate** | **native, preserved — NOT resampled.** Time-dependence is handled by the $\Delta t$ term in NBF. |
| flow estimator | fixed globally, released with code; second backbone on a 10–20% stratified subset for robustness |
| feature extractor, robust thresholds, warm-up, window extents, $c$, transition band, $\epsilon$ | fixed globally before the final sweep |
| aggregation | prompt-level; category **macro**-average; bootstrap 95% CI, 10k resamples, seed 0 |
| storage | signed DAR; per-video `compensation_mode`; per-video fps |

The frame-rate row is a **change** from `sec/4_metrics.tex` line 74, which
claimed frame-rate normalization that the code never performed.

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
| "global compensation isolates physical foreground flow" | "…removes the component explained by a global similarity model" |
| "VBench ranking is wrong" | "whole-frame motion and SNF's spatially resolved diagnostics can yield different interpretations of the same outputs" |

Historical artifacts under `raw/_internal_ablations/` and the verbatim
`metric_code/` are **provenance records and are not rewritten**; they carry
supersession headers instead. Raw metric JSONs keep their original keys; the
rename happens on the way into tables (`scripts/build_tables.py`).

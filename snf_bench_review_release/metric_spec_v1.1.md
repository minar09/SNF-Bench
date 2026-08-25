# SNF-Bench metric specification v1.1

This document is the paper-facing specification shipped with the anonymous
review artifact. The metric family contains six named quantities:

`fBD · NBF · MCFF-E / MCFF-L · FP · DLR · DAR`

No scalar composite score is defined.

## 1. Inputs and notation

For sampled RGB frames `I[0:T]`, the evaluator receives adjacent-pair optical
flow fields `u[0:T-1]` and the effective sampled rate `f_s`. Paper results use
RAFT flow. The synthetic fixture contains analytic flow so the post-processing
can be tested without model weights.

- `W`, `H`: frame width and height.
- `d = sqrt(W² + H²)`: frame diagonal.
- `Ω_static`, `Ω_flow`: automatic static and dynamic regions.
- `E`, `L`: equal-duration early and late windows.
- `epsilon = 1e-6`.

## 2. Automatic partition

1. Average flow magnitude over the early window.
2. Apply Otsu thresholding to obtain the dynamic region.
3. If the dynamic area is below 3%, use the 80th percentile as fallback.
4. Apply 5×5 morphological opening and closing.
5. Define static support as the complement, remove a 4% frame border, and
   erode it with a 5×5 kernel to limit boundary leakage.

The partition is a two-way evaluation role, not a semantic ontology. Layered
content such as rain crossing static support remains a stated limitation.

## 3. Global similarity compensation

For each adjacent pair, sample static-region correspondences
`x -> x + u(x)` and fit

`T(x) = s R x + b`

with `cv2.estimateAffinePartial2D` under RANSAC. The dense fitted displacement
is `g(x) = T(x) - x`, and compensated flow is `u_tilde(x) = u(x) - g(x)`.

When fewer than 50 static correspondences exist or fitting fails, the evaluator
falls back to median translation and records that fallback. A fallback is never
silent.

## 4. Metrics

### fBD — Feature-aligned Background Drift, lower is better

ORB features are detected within `Ω_static` in frame 0 and late-window frames.
Cross-checked Hamming matches are filtered by a RANSAC homography. fBD is the
mean across late frames of median inlier displacement, divided by the frame
diagonal and multiplied by 100.

Units: percent of frame diagonal. If too few repeatable features survive, fBD
abstains and is stored as `null`.

### NBF — Normalized Background Flow, lower is better

`NBF = 1000 * f_s / W * mean_t mean_{x in Ω_static} ||u_t(x)||_2`

Units: `10^-3` frame widths per second. NBF is a magnitude, not a ratio.

### MCFF-E and MCFF-L — Motion-Compensated Foreground Flow

`MCFF(window) = mean_{t in window} mean_{x in Ω_flow} ||u_tilde_t(x)||_2`

Both magnitudes are always reported; uniformly weak motion must not appear
strong through a ratio alone.

### FP — Flow Persistence, higher indicates greater retention

`FP = min(MCFF-L / (MCFF-E + epsilon), 2)`

Values above one do not automatically mean better quality.

### DLR — Drift Leakage Ratio, lower is better

`DLR = F_static_late / (F_dynamic_raw_late + epsilon)`

DLR is unbounded. It describes static-region flow magnitude relative to raw
dynamic-region flow; it is not a fraction of physical motion.

### DAR — Drift Attenuation Ratio, lower is better

`DAR_signed = 1 - F_dynamic_compensated_late / (F_dynamic_raw_late + epsilon)`

The signed value is stored and used for validation. The reported table value is
clipped to `[0,1]`. Negative values mean fitted compensation increased measured
dynamic-region flow magnitude. DAR is the signed relative attenuation after
fitted similarity compensation, not a causal decomposition of motion.

## 5. Reporting contract

- Report fBD and NBF separately from MCFF-E/L and FP.
- Never rank systems with a single composite SNF score.
- Report MCFF-E and MCFF-L whenever FP is reported.
- Report fBD abstention and measurement coverage.
- Treat DLR and DAR as interpretive diagnostics.
- Preserve signed DAR in stored records.
- Compare systems only within the same declared deployment setting.

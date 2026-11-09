# Plain-language metric names and reviewer-facing writing

2026-11-08. This is a presentation proposal for SNF-Bench++; it does not change any formula, input, score, legacy field or frozen protocol. Following the user's instruction, the journal draft uses the plain-English names in tables and figures; original metric IDs are confined to definitions and technical provenance.

## What the review and literature actually say

Reviewer BsRf wrote: “The metric design is a bit complicated relative to the fairly narrow setting.” This is a concern about design complexity, not an explicit request to rename acronyms. A better explanation helps, but addressing the review also requires fewer headline measurements, clear construct validity and appropriate controls. Replacing names alone does not fix that concern.

[VBench](https://openaccess.thecvf.com/content/CVPR2024/papers/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.pdf) separates recognizable dimensions such as background consistency, motion smoothness and dynamic degree, and validates dimensions with human judgments. [VBench++](https://arxiv.org/abs/2411.13503) extends the suite to image-conditioned generation. [VMBench](https://arxiv.org/abs/2503.10076) uses descriptive names such as motion smoothness and object integrity and tests human alignment. [WorldScore](https://arxiv.org/abs/2504.00983) groups measurements by controllability, quality and dynamics. These papers motivate understandable dimension names and visible validation; their terms are not interchangeable with our actual estimators, and their reported validation does not validate ours.

## Recommended core names

Use title case in tables, sentence case in prose. Do not coin new acronyms for these labels. Keep legacy IDs in textual definitions, equations and technical provenance, with the exact method/version and units in the caption or appendix when needed.

| Reader-facing label | Existing identity | What it actually measures | Direction and limitation |
|---|---|---|---|
| **Background displacement** | fBD; source-fixed variant `fBD_f0` must be identified separately | Displacement of matched background features relative to that protocol's reference. | Lower for fixed support; requires reliable feature matches and coverage, and does not capture all appearance drift. The legacy and source-fixed references are not the same. |
| **Background motion** | NBF, derived from stored `BFR` using effective sampling rate | Optical-flow magnitude in the background region, normalized in space and time. | Lower for intended static support; may include illumination and flow error. Stored `BFR` is per sampled interval and is not the same numeric unit as NBF per second. |
| **Early material motion** and **Late material motion** | MCFF-E and MCFF-L | Material-region optical-flow magnitude after estimated global-motion compensation. | Quantities, not universal higher-is-better scores. Report both together; high values can be flicker or implausible motion. |
| **Motion retention** | FP | The clipped late-to-early material-motion ratio. | About one means similar measured amounts; near one can still mean both amounts are tiny. Above one is not automatically better; report with both motion values. |

In concise result tables use **Background displacement**, **Background motion**, **Material motion: early**, **Material motion: late**, and **Motion retention**. Show arrows only where the task has a defensible unambiguous direction; do not add ↑ to material motion or retention as a blanket quality claim. Include numeric units, the reference frame, version, mask identity, horizon, eligibility and uncertainty as appropriate.

## Planned checks and supporting diagnostics

These names are construct labels, not claims that a validated score exists. Use the concrete candidate ID and version when reporting a measurement.

| Construct label | Existing work | What it does not establish |
|---|---|---|
| **Background coherence** | R1; support-change and edge-profile candidates | Low change does not prove pasting; a convincing composite can be valid. No general paste detector. |
| **Material motion location** | R2; planned role-aware checks | A moving mask does not by itself identify a material or handle occlusion/new objects. |
| **Motion direction** | R3; `cand-direction-flux-0`, channel alignment and gravity-sign candidates | A geometric flow statistic is not verified semantic direction or general fluid physics. Labels and applicability require independent annotation. |
| **Repetition and reset** | R4; recurrence, replay-signature and seam candidates | Recurrence is not necessarily an error: real surf and vegetation may be periodic; freeze is a separate observable. |
| **Motion plausibility** | R5; planned reference and human-based comparison | No current candidate establishes realistic physics; standard FVMD is set-level, not a per-video verdict. |
| **Moving-area coverage** | `cand-coverage-0/1` | An estimated active-mask fraction, not semantic correctness; patch controls show substantial leakage and imperfect monotonicity. |
| **Material colour change** / **Background colour change** | `cand-material-drift-0`, fields `drift_material` / `drift_support` | Euclidean distance in OpenCV 8-bit encoded Lab between window-averaged regional mean colours; not CIEDE2000, standard ΔE76, freeze detection or naturalness. Do not headline the difference between the two. |
| **Background-to-material flow ratio** | DLR, historical `drift_frac_late` | A contextual ratio, not a share or percentage of motion caused by drift. |
| **Compensation effect** | DAR, historical `DAR_signed` | Signed relative change under the fitted compensation estimator, not the amount of true camera drift. Preserve the signed/clipped reporting distinction. |

## Writing rules

1. Open with a concrete fixed-camera example, then pose the question before describing the algorithm. Prefer “background” and “moving material” to “static support” and “dynamic flow”; define the latter technical terms once where equations require them.
2. Separate task dimensions, measurable statistics and validation outcomes: “motion direction” is a question; signed flow is a candidate statistic; independent human agreement is evidence. A frozen implementation is not an admitted metric.
3. Report one compact core group, plus a separate group of explicitly provisional checks. Keep DLR/DAR and nonselective metrics in diagnostic material unless independent evidence justifies promotion. Do not collapse everything into a single total.
4. For each reported measure state region, reference, units, sampling and direction of interpretation; accompany numbers with eligibility and uncertainty. Example: “Background displacement is 2.3% of the frame diagonal on 38/41 eligible videos; lower indicates less feature displacement.” This example is illustrative, not a measured result.
5. Do not call a newly named metric “VBench background consistency,” imply equivalence to another benchmark's dimension, claim physical realism from flow, or change the encoded Lab statistic into ΔE00.
6. Use “planned,” “candidate,” “diagnostic” or “validated” consistently; do not introduce the new family as completed human-aligned research until the study and confirmation actually exist.

## What changed in the working draft

`JOURNAL_TCSVT/sec/01_introduction.tex` starts from a river example and explicitly states the draft's pending validation. `JOURNAL_TCSVT/sec/04_measurement.tex` provides a four-row reader-facing table, separates diagnostic ratios from the core and explains the five additional checks in plain language. Original identifiers are stated in the method definitions rather than the table or figure labels. Historical result files, metric definitions and source code identities are untouched.

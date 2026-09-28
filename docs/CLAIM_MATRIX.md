# SNF-Bench — claim → evidence matrix

Every claim the paper makes, and the exact artifact that backs it. NeurIPS/WACV
E&D criteria grade benchmark papers on rigor and reproducibility rather than on
beating a baseline, so an unbacked claim costs more here than a missing result.

**Rule for this table: if a claim has no BUILT evidence by the Aug 20 freeze, the
claim is cut, not softened.** There is no rebuttal round.

| # | claim | evidence | status |
|---|---|---|---|
| **C1** | In fixed-camera scenes, whole-frame motion metrics cannot distinguish desired local flow from static-support drift. | Fig. 1 teaser; Fig. 5 slopegraph; `tables/t2v_disagreement_60s.md` — Spearman(VBench-DD, NBF) = **+0.93** | Fig. 5 + table **BUILT**; Fig. 1 partial |
| **C2** | The disagreement is not a fluke of one metric pair: higher "dynamic degree" tracks *more background flow* across the board. | `tables/t2v_disagreement_60s.md` — DD vs NBF +0.93, DD vs MCFF +0.89, DD vs fBD +0.75 | **BUILT** |
| **C3** | The disagreement produces rank *inversions*, not just weak correlation. | Fig. 5; Causal-Forcing rank 1→7, Infinite-Forcing rank 7→1 | **BUILT** |
| **C4** | Low background flow can mean *frozen*, not *stable* — so static fidelity must be read jointly with flow persistence. | Fig. 4; Infinite-Forcing is rank 1 on NBF/fBD **and** rank 7 on MCFF | **BUILT** |
| **C5** | The conclusions survive the averaging choice. | micro vs category-macro: Causal-Forcing stays 1st on DD and 7th on NBF/fBD; Infinite-Forcing stays 1st/7th. Mid-field does move (Self-Forcing NBF rank 5→2). | **BUILT** (`scripts/categories.py`) |
| **C6** | ~~SNF metrics respond monotonically to translation, rotation, scale, and attenuation.~~ **SCOPED:** fBD responds across the three global transforms; NBF is retained for translation/scale; MCFF-L and FP do not clear the attenuation-versus-nuisance screen. | `tables/validation_response_matrix.md`; `manifest/validation_response_analysis.json` | **BROAD CLAIM REJECTED; SCOPED RESULTS BUILT** |
| **C7** | VBench Dynamic Degree moves in its rewarding direction under injected background translation that a fixed-camera benchmark should penalise. | `tables/validation_response_matrix.md`, translation VBench-DD row: paired d_z 1.22 | **BUILT FOR TRANSLATION**; rotation uncertain |
| **C8** | ~~DAR is calibrated as a headline drift factor.~~ DAR responds to global transforms but fails nuisance selectivity (0.58), so it remains supplementary. | `tables/validation_response_matrix.md`; §5.3 | **HEADLINE CLAIM REJECTED; DIAGNOSTIC BUILT** |
| **C9** | Conclusions are stable to the optical-flow backbone. | Tab. 2 backbone-agreement columns; Fig. S4 | **BLOCKED** — P0#5 |
| **C10** | Metrics have a documented noise floor. | Tab. 2 zero-motion floor (duplicated frames + real static regions) | **BLOCKED** — P0#5 |
| **C11** | fBD match support and fallback behavior are explicit rather than inferred from non-null values. | `docs/FBD_RELIABILITY_PILOT.md`; `manifest/fbd_reliability_pilot.json` | **12-CLIP PILOT BUILT** — 0 abstentions, but 37/684 frames use raw-match fallback; full public panel remains blocked |
| **C12** | Masks are not contaminated by the failure being measured. | Fig. 2(a); per-model first-frame-blind protocol | **BLOCKED** — Aug 14 |
| **C13** | Rain/snow do not break the partition. | Fig. 2(b); Ω_overlay excluded from headline fBD/NBF | **BLOCKED** — Aug 14 |
| **C14** | ~~Conclusions are stable to mask perturbation.~~ NBF is materially mask-sensitive; reviewed-mask and full rank-sensitivity studies remain required. | `tables/validation_response_matrix.md`; `docs/SHARED_AUTO_CONTROL.md` | **BROAD CLAIM REJECTED; PILOT BUILT** |
| **C15** | N is chosen for statistical power, not budget. | Tab. S8; "N selected such that CIs for primary metrics fall below a pre-specified tolerance" | **BLOCKED** — 60 s pilot (P0#7) |
| **C16** | Methods are not being penalised for semantic failure misread as flow behaviour. | Tab. 3 semantic-context column | **BLOCKED** — P0#6 |
| **C17** | The audit is scoped transparently: public T2V checkpoints share one recorded common configuration, I2V released-pipeline and wrapper rows are separated, and our own systems are excluded. | `tables/model_config_table.md`; `scripts/registry.py` status/setting fields; `docs/EXCLUSIONS.md` | **BUILT** except EXCLUSIONS.md |
| **C18** | Deployment configuration changes the conclusions. | Tab. 4 Δ-table | **BUILT**, needs compression |
| **C19** | ~~Frame rate is a hidden confound and normalizing changes rankings.~~ **RETRACTED 2026-08-13.** The metric subsamples to `SAMPLE_FPS=8` before computing flow, so all 1881 videos are already measured at exactly 8.000 Hz. Scaling by native fps *introduced* a 1.5× error; LTX ranks 6th as it always did. NBF keeps per-second units (uniform ×8, no ranking change) for physical meaning and future-proofing. | `manifest/video_meta.csv`; `registry.effective_fps` | **RETRACTED — do not claim** |
| **C20** | Results are reproducible from the released artifacts. | `manifest/video_index.csv` (SHA fingerprints), `per_video_scores.csv`, `video_meta.csv`, `prompt_categories.csv`, verbatim `metric_code/` | **BUILT** |
| **C21** | Coverage is counted from valid measurements, not from the presence of a metrics file. | `tables/coverage_matrix.md` — `T<n>/<total>` notation; 13 entries have incomplete metric runs (CUDA OOM / cuDNN init), incl. **two public I2V baselines holding 1/30 usable records at 60 s** | **BUILT** |
| **C22** | SNF's proposed v2 scope is distinct from VBench-I2V, VBench-Long, and VBench-2.0 at the protocol level. | `docs/VBENCH_EXTENSION_GAP_ANALYSIS.md`; `manifest/vbench_extension_audit.json`; official source snapshot `fd18b3d` | **SOURCE/CODE AUDIT BUILT; NOVELTY CLAIM REQUIRES BROADER LITERATURE AUDIT** |
| **C23** | Long-horizon results retain failure timing rather than only a clip mean. | `scripts/long_horizon_protocol.py`; fixed-window unit tests; later matched-horizon traces | **PROTOCOL BUILT; EMPIRICAL TRACES BLOCKED — M2/M3** |
| **C24** | Direction, incoming transport, reversal, replay, and reset seams are separately measurable and human-aligned. | controlled probes, licensed real-video false positives, per-axis human study | **BLOCKED — M2/M4** |
| **C25** | The v2 asset release contains 96 independent, balanced base scenes with matched 60/120/240-second prefixes; counterfactuals are not counted as independent scenes. | `configs/snf_v2_scene_contract.json`; `scripts/validate_v2_scene_manifest.py`; future frozen scene manifest | **RELEASE GATE BUILT; ASSET CLAIM BLOCKED — M3** |

---

## Claims that must NOT be made

| forbidden | why | say instead |
|---|---|---|
| "X% of method M's motion is drift" | DAR is not a causal decomposition. Vector interactions mean opposing local flow can make compensation *increase* magnitude — empirically negative on **22 of 161** T2V-60s clips. | "global compensation removes X% of measured dynamic-region flow under this estimator" |
| "94% of Causal-Forcing's motion is drift" | Doubly wrong. The 0.939 came from `drift_frac_late`, which is `mean\|u\|_static / mean\|u\|_dyn` — a *leakage ratio* (now **DLR**) that never touches the compensated flow and exceeds 1 on 20 of 161 clips. Under the actual attenuation definition, Causal-Forcing's DAR is **0.400**. | "Causal-Forcing's DLR is 0.94 — its static region moves almost as much as its dynamic region"; separately, "DAR 0.40" |
| "first long-video benchmark" | MovieBench (CVPR'25) precedes us on long video; WorldScore on world-scale. | "continuous single-scene fixed-camera behaviour over 60–120 s" |
| "unprecedented temporal horizon" | same | as above |
| "prior benchmarks are biased toward semantics" | VBench, EvalCrafter and VMBench all carry substantial low-level perceptual metrics. | "generic motion metrics do not encode the task-specific spatial role of each region" |
| "SNF metrics are perceptually faithful" | No human validation unless the Aug-15 go/no-go passes. | "mechanistically validated diagnostics" |
| "DAR measures the fraction of motion caused by drift" | DAR is a signed relative change under one estimator, not a causal share. | "signed relative change in dynamic-region flow after global-motion compensation" |
| "SNF recovers true dynamic motion" | Nothing here recovers ground-truth motion; MCFF is what survives a global model. | "flow surviving global-motion compensation" |
| "global compensation isolates physical foreground flow" | It reports signed relative attenuation after fitted global similarity compensation—no more. | "…reports the signed relative attenuation after fitted global similarity compensation" |
| "VBench ranking is wrong" | We show interpretation change, not error. Accusing a published metric of being wrong invites a fight we do not need. | "whole-frame motion and SNF's spatially resolved diagnostics can yield different interpretations of the same outputs" |
| "SNF-Bench measures physical realism" | It does not, by construction. | "persistence ≠ physical correctness" |
| "Steady-Forcing / RA-I2V performs well on SNF-Bench" | Our own systems are excluded by construction; including them would void the audit. | nothing — they do not appear |

---

## Numbers to reconcile before they are printed

| item | issue | owner action |
|---|---|---|
| Rolling-Forcing fBD @60s | 16.91 here vs **16.27** published in the Steady-Forcing rebuttal. It has 24 clips over 23 prompts; prompt-level averaging of the duplicate gives 16.91. Prompt-level is the correct unit. | reconcile against rebuttal text; state the unit explicitly |
| Every DAR value ever quoted | Pre-2026-08-13 DAR/DriftFrac numbers are DLR, not DAR. | re-quote from current `per_video_scores.csv` |
| **DAR was "zero recompute"** | True only under the *old* translation-only compensation. Once similarity compensation lands (METRIC_SPEC v1.1 §3), stored `MCFF_late`/`dyn_res` are obsolete and **MCFF-E, MCFF-L, FP and DAR must all be recomputed**. fBD, NBF and DLR are unaffected. | recompute on merge, Aug 16 |
| **Two public I2V baselines at 60 s** | CausVid and Causal-Forcing (framewise) hold **1 of 30** valid task records; the sweep died on CUDA OOM. Counting distinct published models, only **2** (Self-Forcing, Causal-Forcing++) currently clear the Aug-16 gate of ≥3. | re-run metrics — videos exist, no regeneration needed |
| Every NBF value ever quoted | NBF = BFR × **effective** sampled rate = ×8.000 uniformly. No ranking changes on any track. Any quoted "×16"/"×24" figure or LTX rank-change is from the retracted first pass. | re-quote from current tables |
| T2V SNF metrics at 5 s / 120 s / 240 s | do not exist — VBench only | metric re-run over videos already on disk, or scope the claim to 60 s |
| T2V 240 s per-video VBench | aggregate only; contributes no rows, so no CIs at 240 s | state, or re-run per-video |

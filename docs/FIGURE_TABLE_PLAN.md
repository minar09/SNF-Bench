# SNF-Bench — figure, table and list plan (main paper + supplementary)

WACV 2027 Evaluation & Dataset track. 8 pages, **no rebuttal**, submit Aug 28 AoE.
Everything a reviewer will object to has to be answered inside the submitted PDF.

Status vocabulary used throughout:

| tag | meaning |
|---|---|
| **BUILT** | rendered from current data; regenerate with `scripts/figures.py` / `build_tables.py` |
| **DIAGNOSTIC** | rendered, but watermarked `PRE-FREEZE` — the numbers will move at the Aug 14/16 gates |
| **BLOCKED** | inputs do not exist yet; blocking item and gate date named |
| **AUTHORED** | hand-drawn/hand-written asset, no data dependency |

---

## 1. How much visual space to spend, and where

Measured from the accepted comparators rather than guessed:

| paper | venue | main-paper figures | main-paper tables | where the figures go |
|---|---|---|---|---|
| T2V-CompBench | CVPR 2025 | 7 | 2 | prompt suite + taxonomy (their contribution *is* the suite); metric validation is a **table** of Kendall τ / Spearman ρ, not plots |
| VBench++ | arXiv (VBench, CVPR 2024) | 12 | 4 | radar charts per dimension; human alignment as a **grid of correlation scatters**; leaderboard = models × dimensions |
| EvalCrafter | CVPR 2024 | — | — | pipeline + multi-metric + human-opinion weighting |

Two lessons taken directly:

1. **Metric validation as a compact table is the cheap, accepted pattern.** T2V-CompBench spends *one table* on the thing its acceptance rests on. We copy that for the perturbation-response summary, and spend our figure budget on the one thing a table cannot show — that the response is monotone and that a standard metric moves the *wrong way*.
2. **Figure space follows the contribution.** T2V-CompBench's contribution is a prompt suite, so its figures are prompts. Ours is a metric decomposition and its validation, so **our figures are validation** — hence the page-4–5 centrepiece. We do *not* spend figures on prompt-suite statistics; those go to supplementary.

**Budget: 5 figures + 4 tables in the main paper.** Two figures are single-column.

| page | content | visual |
|---|---|---|
| 1 | motivation + teaser | Fig. 1 |
| 2 | related work, benchmark protocol | Tab. 1 |
| 3 | masks + metrics | Fig. 2 |
| **4–5** | **validation — the intellectual centrepiece** | **Fig. 3, Tab. 2** |
| 6–7 | public-model audit + interpretation change | Tab. 3, Tab. 4, Fig. 4, Fig. 5 |
| 8 | limitations + conclusion | — |

---

## 2. Main paper — figures

### Fig. 1 — "Whole-frame motion cannot tell these apart" (teaser)
**Status: PARTIAL.** Exemplar selection **BUILT** (`figures/fig1_teaser_exemplars.md`); metric bars **BLOCKED** on the DAR/affine fixes.

Three real benchmark clips of **one shared prompt**, as a 3×4 frame strip (t = 0, 20, 40, 60 s), with a metric bar group beneath each:

- **A** desired — flow persists, support stays put
- **B** drift masquerading as motion — whole frame slides
- **C** frozen — support stays put, flow has died

Beneath each: `VBench Dynamic Degree` ‖ `SNF Static Fidelity (fBD, NBF)` ‖ `SNF Flow Persistence (FP, MCFF)`.
The payload: **A and B get similar Dynamic Degree; SNF separates them.**

Selection is data-driven, not hand-picked — `teaser_exemplars()` searches the 23 prompts shared by all 7 public T2V methods and ranks triples by margin. Current top candidate (rural street-food scene, 60 s):

| case | method | fBD ↓ | MCFF | DD_raw | DLR ↓ |
|---|---|---|---|---|---|
| A good | CausVid | 0.68 | 8.08 | 8.09 | 0.147 |
| B drifting | Causal-Forcing | 30.65 | 2.21 | 2.60 | 2.583 |
| C frozen | Infinite-Forcing | 3.41 | 0.36 | 0.35 | 0.494 |

> Caveat to re-check after the affine fix: case B's fBD of 30.65 is extreme, and B's DD_raw (2.60) is *below* A's (8.09), which weakens the "similar Dynamic Degree" framing for this particular prompt. Re-run selection against VBench per-video Dynamic Degree, not DD_raw, and prefer a triple where A and B have **close DD**. That is the figure's whole point and the current top candidate does not yet deliver it. Rank-2 and rank-4 candidates are the next to check.

Form: frame strip + grouped bars. Double column. Frames exported at the four timestamps from `videos/t2v/<key>/60s/`.

---

### Fig. 2 — Mask protocol and the two settings
**Status: BUILT and FINAL** — `figures/fig2_mask_protocol.pdf`. No measured-data dependency, so it carries **no** pre-freeze watermark: nothing in it can move when the metrics are refrozen, and watermarking it would train the eye to ignore the watermark. Annotation still lands Aug 14; the *protocol* it depicts is frozen.

Two panels:

- **(a) Where the partition comes from.** I2V → one mask from the source image, identical across models. T2V → a mask per model from **that model's own first frame, blind to every later frame**, using the identical frozen procedure. Annotate the reason on the figure: the mask depends on generated layout but *not* on the failure being measured, so long-horizon drift cannot contaminate it.
- **(b) Three labels, not two.** Ω_static / Ω_flow / **Ω_overlay**, illustrated on a rain-over-buildings frame where the same pixels are simultaneously static support and desired particle motion. State on the figure that Ω_overlay is **excluded from headline fBD/NBF**, and that rain/snow static-fidelity is reported over Ω_static \ Ω_overlay.

Panel (b) is the single most important defensive figure in the paper: rain and snow are 21 of our 100 prompt-durations (see `tables/category_balance.md`), so a binary partition is not a corner case.

Form: schematic over real frames. Double column, ~1/3 page.

---

### Fig. 3 — Metric validation (the centrepiece)
**Status: BLOCKED** on affine compensation (P0#1, merged+unit-tested **Aug 16**) and the perturbation sweep (**Aug 18**).

Five panels, shared x = injected corruption severity:

| panel | inject | expect | guards against |
|---|---|---|---|
| (a) | global **translation** | fBD ↑, NBF ↑ monotone | — |
| (b) | global **rotation + scale** | fBD ↑, NBF ↑ monotone | **W4** — under translation-only compensation this panel *fails and indicts our own estimator*. Do not render before P0#1 lands. |
| (c) | progressive **flow attenuation** | FP ↓, MCFF ↓ monotone | — |
| (d) | known injected drift | DAR tracks injected fraction | calibrates DAR against ground truth |
| (e) | **the same perturbations, scored by VBench Dynamic Degree** | DD **rises** with injected background drift | this is the paper's thesis made visual |

Panel (e) is the review's best idea and costs one metric run over clips already being generated. It is adversarial to *no published method* — the corruption is synthetic — while showing a standard metric rewarding exactly the failure SNF-Bench detects.

Form: 5 small line panels, one row, double column. Each line direct-labelled; severity on x; no dual axes.
Mask dilation/erosion rank-stability moves to supplementary (Fig. S3) to buy the space.

---

### Fig. 4 — Operating regime (the scientific result)
**Status: BUILT** — `figures/fig4_operating_regime.pdf`. Numbers will shift after P0#1; regenerate.

x = static drift (fBD ↓) · y = surviving late flow (MCFF) · colour = DAR (single-hue sequential ramp).
Reads as a two-axis operating regime rather than a leaderboard, which is the point: there is no single scalar.

Causal-Forcing sits alone at the far right — most drift, most apparent surviving motion, darkest DAR. Infinite-Forcing sits bottom-left: least drift, but its motion has collapsed. Neither is "best".

Single column. **Method identity is carried by direct text labels, never hue** — see §5.

---

### Fig. 5 — Rank disagreement
**Status: BUILT** — `figures/fig5_rank_disagreement.pdf`.

Slopegraph: rank under VBench Dynamic Degree → rank under SNF-Bench NBF, 7 public T2V methods, both columns direct-labelled. Causal-Forcing (rank 1 → 7) and Infinite-Forcing (rank 7 → 1) carry the two validated hues; the other five are muted grey context.

A clean X. Backed numerically by `tables/t2v_disagreement_60s.md` (Spearman DD vs NBF = **+0.93**).

Single column, sits beside Fig. 4.

---

## 3. Main paper — tables

### Tab. 1 — Positioning against published video-**generation** benchmarks
**Status: AUTHORED.** Curated, not computed.

Rows: VBench (CVPR'24), EvalCrafter (CVPR'24), T2V-CompBench (CVPR'25), Video-Bench (CVPR'25), VMBench (ICCV'25), WorldScore (ICCV'25), T2VWorldBench (WACV'26), WYD (CVPR'26), Ref4D-VideoBench (CVPR'26), MovieBench (CVPR'25), **SNF-Bench**.
Columns: task · fixed-camera · minute-scale continuous · static/flow spatial decomposition · drift analysis · T2V+I2V · validation style.

Two hard rules:
- **No video-*understanding* benchmarks** (MVBench, Video-MME, LVBench). Mixing them is a category error the first review made; importing it invites a reviewer to dismiss the whole table.
- **No "first" claim.** Phrase as "we did not find a published benchmark combining all of: …". MovieBench already does long-video; WorldScore already does world-scale.

VMBench is the comparator to treat most carefully — it also claims better motion interpretation. The table must make clear why perception-aligned *motion quality* does not answer "is the background moving when it should not?"

### Tab. 2 — Metric validation summary
**Status: BLOCKED** (same gates as Fig. 3).

Rows = metrics (fBD, NBF, FP, MCFF, DLR, DAR, **VBench-DD as a contrast row**).
Columns = Spearman ρ vs injected severity for each corruption family (translation, rotation, scale, attenuation, **generation-like corruptions**), + zero-motion floor, + flow-backbone agreement (ρ between RAFT and the second backbone), + fBD match coverage / abstention rate.

This is the T2V-CompBench pattern: the load-bearing evidence, one compact table. The VBench-DD row is what makes it an audit rather than a self-report.

If the human axis-study runs (go/no-go **Aug 15**), it adds two columns: Kendall τ and Spearman ρ against human drift-ranking and human decay-ranking. If it does not, Tab. 2 stands alone and §8 states plainly that these are **mechanistically validated diagnostics**, not perceptually faithful measures.

### Tab. 3 — Public-model audit, matched T2V setting
**Status: BUILT for T2V @60s** (`tables/t2v_snf_60s.md`); I2V is split between recorded released-pipeline outputs and dagger-marked common-wrapper rows, and other durations are partial.

Rows = public methods, grouped by track. Columns = fBD ↓ · NBF ↓ · FP ↑ · MCFF · DLR ↓ · DAR ↓ · **one semantic-context column** (P0#6 — VBench semantic/overall-consistency or CLIP similarity; invent nothing).
Cells = `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0. Category-**macro**-averaged (`scripts/categories.py`).

Semantic column is the guardrail against "moving fog scored as a river" and reinforces that SNF-Bench complements rather than replaces general-purpose evaluation.

### Tab. 4 — Matched-deployment Δ (Setting B stress test)
**Status: BUILT as full tables**, needs compression to Δ form.

Δ per metric between native and matched configuration, one row per method that has both. **One table + one paragraph, and out of the abstract entirely** — the abstract clause currently invites fairness questions before the reader has seen the safeguards.

Contingency: if the matched results come back messy at the sweep, demote wholesale to supplementary. That is a one-day edit; the reverse is not.

---

## 4. Supplementary

Figures:

| id | content | status |
|---|---|---|
| S1 | Category balance by track × duration | **BUILT** `figS_category_balance.pdf` |
| S2 | Per-category breakdown of each headline metric | BUILT-able from `per_video_scores.csv` + `prompt_categories.csv` |
| S3 | Mask dilation/erosion rank stability | BLOCKED (mask build, Aug 14) |
| S4 | Flow-backbone agreement scatter (RAFT vs second backbone) | BLOCKED (P0#5) |
| S5 | Duration sweep 5 s → 240 s per metric | partial — see gaps |
| S6 | Qualitative failure grid: drift, freeze, overlay-region rain | AUTHORED |

Tables:

| id | content | status |
|---|---|---|
| S1 | Full asset & score coverage matrix | **BUILT** `tables/coverage_matrix.md` |
| S2 | Model/config/checkpoint provenance | **BUILT** `tables/model_config_table.md` |
| S3 | Category balance + thin-cell flags | **BUILT** `tables/category_balance.md` |
| S4 | Per-duration VBench tables (all 4 durations, both tracks) | **BUILT** 8 tables |
| S5 | Pairwise sign tests between public methods | **BUILT** 5 tables |
| S6 | Per-category macro-averages | BUILT-able |
| S7 | Exclusions: every internal system and why | to write (`docs/EXCLUSIONS.md`) |
| S8 | Power analysis behind N (P0#7) | BLOCKED on 60 s pilot |

Lists:

| id | content | status |
|---|---|---|
| L1 | Full T2V prompt list (35 prompts) | **BUILT** `prompts/t2v/*.txt` |
| L2 | Full I2V prompt+image list (65 pairs, with `type`) | **BUILT** `prompts/i2v/*/` |
| L3 | Per-video score dump (25,579 rows) | **BUILT** `manifest/per_video_scores.csv` |
| L4 | Per-video FPS/resolution/frame-count | **BUILT** `manifest/video_meta.csv` |
| L5 | Per-prompt category assignment with rule + evidence | **BUILT** `manifest/prompt_categories.csv` |
| L6 | Claim → evidence matrix | **BUILT** `docs/CLAIM_MATRIX.md` |
| L7 | Video fingerprints for reproducibility | **BUILT** `manifest/video_index.csv` |

---

## 5. Production rules

Colour is computed, not chosen — `scripts/palette.py` runs the OKLab + Machado-CVD checks in-process and `figures.py` refuses to render on a FAIL.

The binding constraint: under an **all-pairs** pairlist (scatter — any two marks can end up adjacent) only **three** categorical hues clear the separation floors, and every figure here has 7–9 methods. Therefore:

- **Method identity is always carried by direct text labels, never by hue.**
- Hue carries magnitude (single-hue sequential ramp, Fig. 4) or marks at most two highlighted methods against muted grey (Fig. 5).
- Stacked/grouped bars use the **adjacent** pairlist, where all six categorical slots pass — that is why Fig. S1 may use six hues while Fig. 4 may not.
- Three categorical slots sit under 3:1 on the light surface, so every bar segment carries a direct count label (the relief rule).

Sizes: single column 3.35 in, double column 7.0 in. Base font 8 pt, labels 6.2–7 pt.
Output: PDF (vector) + PNG, `pdf.fonttype=42` so camera-ready text stays selectable.
**Every figure must be opened and looked at after rendering** — the validator checks colour, not label collisions.

---

## 6. What blocks what

```
Aug 14  overlay-aware masks (P0#2)  ──► Fig. 2(b), Fig. S3, rain/snow headline numbers
Aug 15  human axis-study go/no-go   ──► Tab. 2 extra columns  OR  §8 claim scope-down
Aug 16  affine compensation (P0#1)  ──► Fig. 3(a-d), Fig. 4 numbers, Tab. 3 numbers
Aug 18  validation sweep + DD panel ──► Fig. 3, Tab. 2
Aug 20  FREEZE
Aug 28  submit (no rebuttal)
```

Fig. 3(b) is the tripwire: rendered against the current translation-only compensation it would **fail and indict our own estimator**, because the median of a rotational static-region flow field is near zero. That is why P0#1 precedes the sweep rather than following it.


---

## 7. Enforcement (added 2026-08-13)

Three mechanisms now make the plan self-policing rather than aspirational:

1. **`scripts/gate_status.py`** — the pipeline's refusal mechanism. Thirteen gates,
   computed where computable, printing a single bottom line:

       FINAL_SWEEP_ALLOWED = FALSE

   It turns TRUE only when every required gate passes. Table builders consult
   `final_sweep_allowed()`, so "final" tables cannot be produced from an
   instrument that has not been validated. Every defect found on 2026-08-13
   shared one property: nothing in the pipeline was capable of noticing it.

2. **Automatic figure stamping** — `figures.save()` applies the `PRE-FREEZE
   DIAGNOSTIC` watermark and a spec-versioned provenance footer naming the exact
   metrics, spec version, mask version and compensation mode. A figure cannot
   reach the LaTeX without one, and the red-team checklist verifies no watermark
   survives in the submitted PDF. Schematics with no data dependency (Fig. 2)
   opt out of the watermark only.

3. **Sweep integrity contract** (METRIC_SPEC v1.1 §8) — failures write to
   `failures/`, never into `per_video`; each video's result is written
   atomically so a crash cannot cascade; `scripts/schema_scan.py` validates every
   artifact mechanically; coverage counts measurements, not files.

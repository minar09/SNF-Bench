# SNF-Bench++ figure and table plan

**2026-11-06 update:** The user approved new 120/240 s scoring when genuinely needed. Historical v1.1 T2V results already exist for the seven checkpoints at those horizons, so do not rescore them; see `SNF_PP_DECISIONS_AND_HORIZON_AUDIT_2026_11_06.md`. Their prompt sets are disjoint and cannot support matched-horizon curves. Keep the overview, routing and scene composition as separate figures for readability; the five-figure budget below is provisional.

2026-11-05. Request (user): "similar interactive plots and figures and diagrams in the paper, look at the relevant benchmark papers how they present."

Basis: a survey of figure practice in VBench, VBench++, VBench-2.0, EvalCrafter, T2V-CompBench, Physics-IQ, VideoPhy and VideoPhy-2, PhyGenBench, WorldScore, WorldModelBench, ChronoMagic-Bench, FETV and TC-Bench; the long-video papers (Self-Forcing, Self-Forcing++, Rolling Forcing, LongLive, FramePack, Deep Forcing, LV-Bench); and two IEEE TCSVT benchmark papers (HVEval+, AGIQA-3K). Figure types were taken from captions and text, not seen as images.

## What the best benchmark papers do

1. **A teaser that makes an argument.** "The existing metric can't tell A from B" (WorldScore Fig. 1, WorldModelBench Figs. 1 and 9); "realism ≠ physics" (Physics-IQ Fig. 5); "VBench over-rates degraded late frames" (Self-Forcing++ Fig. 3).
2. **Reference lines and normalisation.** Physics-IQ draws physical variance as a dashed ceiling in every small multiple; VBench adds Empirical Min/Max rows.
3. **Small multiples and heatmaps** over category × metric (Physics-IQ Fig. 6; WorldModelBench Fig. 7, a model × 56-subdomain heatmap).
4. **Qualitative strips with the score under each video,** often with red boxes, and x–t slices (kymographs) for temporal failures (VBench A10, TC-Bench Fig. 1). The x–t slice is especially apt for a fixed camera.
5. **Human alignment:**
   - a scatter with one dot per model and ρ per dimension (VBench family);
   - or a τ/ρ table with an inter-annotator upper-bound row (FETV, TC-Bench).
6. **Table conventions:**
   - ↑/↓ in headers;
   - bold best, underlined second (TCSVT convention, HVEval+);
   - ranks in brackets (EvalCrafter);
   - grouped rows with highlighting (T2V-CompBench).
7. **A gap SNF-Bench++ fills.** No long-video paper plots a metric against horizon with uncertainty. They report a first-vs-last difference (Rolling Forcing, FramePack, Deep Forcing) or a per-segment table (LongLive, LV-Bench).

## Plan

The main paper has a budget of 5 figures and 4 tables.

| slot | content | status / data needed |
|---|---|---|
| **Fig. 1** (figure*) | Overview and argument. Keep the TikZ protocol. Panel (a) shows the role routing *on an exemplar frame* (the current Physics-IQ role map); panel (b) the measures with status; panel (c) adds a hook: two systems with similar VBench dynamic degree but very different support fidelity or coverage at 240 s. Merge the routing diagram (current Fig. 3) and the scene donut into it, as a two-ring sunburst inset. | needs per-video dynamic degree for the hook (T2V only today) |
| **Fig. 2** (figure*) | **Metric-vs-horizon small multiples. This is the centrepiece.** Columns: fBD↓, NBF↓, MCFF-E, MCFF-L, FP; rows: T2V and I2V. x-axis: horizon at 5/60/120/240 s. 95% scene-bootstrap ribbons; direct end labels; two highlighted systems with the rest in grey; a distinct marker per system; the 5 s value as a dashed no-drift reference. | **Blocked.** T2V SNF metrics exist at 60 s only (`snf-bench-open-gaps`); computing 120 and 240 s for the first time needs the user's decision (§Decisions) |
| **Fig. 3** | **Two-axis operating map.** x = support fidelity (oriented so right is better); y = material motion (MCFF-L or coverage). One trajectory per system running 5 → 240 s with arrowheads; quadrants labelled frozen-but-stable, alive-but-drifting, target, collapsed. Panels for T2V and I2V. This is the "two axes are not redundant" argument, after Physics-IQ Fig. 5. | same data as Fig. 2 |
| **Fig. 4** (figure*) | **Qualitative panel plus annotated failure-mode gallery.** Keep the 8-system 240 s grid (full version in the appendix). Add per-row score chips, red boxes on drifted support, and flow-arrow overlays on the material. Add one strip of x–t slices, one per failure mode: freeze, support drift, replay or loop, wrong direction, collapse. Each mode is labelled with the glyph its measure uses. Add the public-image I2V comparison (Physics-IQ and VBench-I2V conditioning) once rendered. | renders pending (GPU); x–t slices are CPU |
| **Fig. 5** | **Validity.** (a) Human alignment (VBench Fig. 5 style), with VBench dynamic degree and background consistency in grey to show weaker alignment. Until the study exists, use controlled-perturbation response curves (severity = mean induced displacement). (b) A rank-stability bump chart across horizons. | human study owned by the study owner (do not touch); perturbation curves possible now |
| **T1** | Benchmark comparison ✓/✗ matrix: max horizon, fixed camera, flow media, T2V+I2V, curves over horizon, uncertainty, human-validated, geometry-aware direction, composite gate. | text only |
| **T2** (table*) | Leaderboard. 240 s values with Δ from 5 s; single-hue cell shading per column; bold best, underlined second; ±CI; rank in brackets; a reference row. | after the gates |
| **T3** | Per-regime heatmap as a shaded table: 9 regimes, grouped by medium glyph, × systems. | after the gates |
| **T4** | Validation: τ/ρ against humans or perturbations, against VBench dimensions and a VLM judge, with an inter-annotator upper-bound row. | after the human study |

**Appendix:**
- the full qualitative grid;
- per-regime horizon plots;
- metric stability against the number of scenes (with a band);
- a coverage and valid-record matrix (the OOM truncations disclosed);
- graded-score strips showing what fBD = x looks like (ChronoMagic Fig. 8 style);
- the known-answer control results for every candidate measure.

## Implementation

- Packages go in `sec/packages.tex` only; the template is never touched:
  - `pgfplots` (compat 1.18) with the `groupplots` and `fillbetween` libraries;
  - `xcolor` with the `table` option for cell shading.

  The sizes below are for IEEE two-column pages: one column is 3.5 in, two columns 7.16 in.
- Line, scatter and bump plots are drawn in pgfplots from CSVs that scripts write. Kymographs, flow quivers and change maps are raster images built at final size, with TikZ annotations on top.
- **Type:** nothing below 7 pt (`\scriptsize`); ticks at 8 pt; axis labels at 9 pt.
- **Colour:** Okabe–Ito, always paired with a shape or dash, and checked in greyscale (TCSVT charges per colour page). Method identity is carried by direct labels and markers, never by hue alone (`snf-bench-figure-package`).
- **"Interactive" in an IEEE paper:**
  - a printed URL to the companion page (and a QR code in the arXiv build), plus multimedia supplementary material, which Xplore shows under "Media" and which needs a README;
  - an optional video summary (≤ 100 MB) and a graphical abstract (660 × 295 px), both peer-reviewed and submitted with the manuscript;
  - PDF JavaScript and animations do not survive IEEE's re-typesetting; `animate` is possible in the arXiv build only.

  Every claim must stand in the main PDF.
- **Format fix before submission:** IEEE accepts JPEG only for author photos. The appendix grid (`t2v240_hq/*.jpg`) must become PNG or a single PDF.

## Decisions for the user

1. **Fig. 2 and 3 data.** Computing the frozen v1.1 metrics at 120 and 240 s for T2V would be *first* scoring of those horizons, not rescoring. It still needs explicit approval under the frozen-metric rule, and GPU time on 2 and 3.
2. **Merging figures.** Fold the routing diagram and the donut into Fig. 1 to free two slots for Figs. 2 and 3.

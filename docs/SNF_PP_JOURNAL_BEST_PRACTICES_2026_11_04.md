# SNF-Bench++ for TCSVT: practices from benchmark papers in top venues

2026-11-04. The TCSVT draft (`JOURNAL_TCSVT/`) follows the section pattern
below. Each row names the practice, the papers it comes from, where SNF-Bench++
stands, and what still has to happen. Venue: IEEE TCSVT. The user confirmed it
is SCIE-indexed; recheck the current Clarivate entry at submission.

**Exemplars.**

* VBench (CVPR 2024) and VBench++ (TPAMI): dimension suite, per-dimension human
  alignment, open leaderboard.
* VBench-2.0, EvalCrafter (CVPR 2024), FETV and ChronoMagic-Bench (NeurIPS D&B),
  DEVIL (NeurIPS 2024), WorldScore, VMBench.
* HVEval+ (accepted at TCSVT, 2026): the closest venue match, a dataset of 20k
  videos from 24 T2V models with MOS and pairwise labels, reported with
  SRCC/PLCC/KRCC.
* T2VQA-DB (ACM MM 2024).
* NeurIPS D&B requirements: datasheet, Croissant metadata, persistent hosting,
  code release.

| # | practice | seen in | SNF-Bench++ status | to do |
|---|---|---|---|---|
| 1 | Named dimension taxonomy, each with one documented measure | VBench, VBench-2.0, EvalCrafter | four axes plus two-sided realism (§4 of the draft) | freeze names and identities after admission |
| 2 | Prompt/source suite with per-category statistics and a construction pipeline | VBench, FETV, ChronoMagic | v2 has 96 T2V scenes, 48 I2V pairs, nine regimes | statistics table; fresh rights-cleared set |
| 3 | Contamination / split audit | (rarely done; a strength) | v2: 41 test + 7 seen; fresh 24/24 unseen | rerun on the final confirmation set |
| 4 | Per-dimension human alignment | VBench(++): Spearman of model win ratios per dimension | human study owned by another engineer | consume its outputs; never edit it |
| 5 | Video-level MOS correlation, SRCC/PLCC/KRCC | TCSVT and QA venues: HVEval+, T2VQA-DB | not planned before today | ask the human-study owner whether its design yields per-video scores |
| 6 | Inter-rater reliability | QA datasets; NeurIPS D&B reviewers ask for it | — | Krippendorff α per question |
| 7 | Metric sanity checks with controlled perturbations | DEVIL, WorldScore, VBench-2.0 | synthetic controls and codec floors exist; adversaries C1–C6 designed | admission study (`SNF_PP_REALISM_DESIGN_2026_11_04.md` §4) |
| 8 | Incremental validity over established metrics | — (reviewers ask; the WACV reviewers did) | matched VBench-I2V/Long comparisons exist for development cells | repeat on the published panel only |
| 9 | Broad panel of open models under one protocol, with closed or API models in a separate tier | VBench, EvalCrafter, HVEval+ (24 models) | high-priority list in the model survey | release revision, row type (native/extension/wrapper), seeds and compute per entrant |
| 10 | Statistical reporting: intervals, seeds, per-category breakdown | VBench-2.0, WorldScore | bootstrap CIs, regime macro-average, eligibility counts | multi-seed coverage on the panel |
| 11 | A findings section, not only a leaderboard | VBench "insights", DEVIL, ChronoMagic | placeholder §7 | write from confirmation results only |
| 12 | Robustness of the ranking to evaluation choices | — (good practice) | not done | rank stability under seed, fps, encoder, mask erosion |
| 13 | Datasheet, licence per asset, hosting, Croissant metadata | NeurIPS D&B requirements; Gebru et al. | 2/48 I2V licences recorded; 21/24 fresh have none recorded | capture own footage (also gives real-reference bands); datasheet appendix |
| 14 | Public leaderboard and code, version-pinned | VBench (Hugging Face leaderboard) | versioned identities and gates exist | host after acceptance; pin metric identities |
| 15 | Statement of difference from the conference/preprint version | TPAMI/TCSVT extension practice | appendix A placeholder | itemized new-content list |
| 16 | Author-method neutrality | — | policy in `EXCLUSIONS.md`; results with and without author methods | enforce in the analysis scripts |

TCSVT specifics to confirm at submission:

* page limit and overlength charges;
* EDICS category;
* the APC of $2,800, reported for 2026 submissions (open access only, if chosen);
* the ScholarOne-only submission route, from the TCSVT guidelines page.

**What answers the WACV review.** Its main concerns were:

* masks derived from each model's own flow (circular);
* no human validation of the metrics (the AC's condition);
* blindness to repetition;
* a common few-step configuration with a single seed.

See `WACV27_OFFICIAL_REVIEW_RESPONSE.md`. Source-derived role maps (row 2 and
the draft's §3.4) answer the first. Rows 4–7 answer the second and third, and
rows 9–10 the fourth. These experiments, not the writing, are the critical
path.

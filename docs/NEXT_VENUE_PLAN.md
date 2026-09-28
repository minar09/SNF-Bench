# SNF-Bench — plan for the next venue

**2026-09-28 update:** The resolution claim in §2.1 is provisional. A
paired, category-macro prompt bootstrap on the same seven public T2V systems
finds NBF separation for 14/21 system pairs versus 13/21 for VBench background
consistency (unadjusted 95% intervals). See `SNF_V2_MILESTONES.md` and
`manifest/paired_incumbent_resolution.json`. Do not cite the 6.42 versus 1.66
range/SD ratio as proof of substantially better model resolution.

Status: WACV 2027 E&D returned three reviews (Reject/conf 5, Borderline-reject/conf 4,
Reject/conf 5). All three are competent and largely agree. This plan is organised by
what the reviews converge on, then by what we found when we actually computed the
things they asked for — which is worse than they knew.

## 1. What all three reviewers independently raised

Unanimity matters more than individual severity. These appeared in all three:

| # | Objection | Verdict |
|---|---|---|
| A | Partition is model-dependent and validated against nothing | **Fatal as submitted.** Decisive control (shared partition) never run |
| B | 23 prompts, 61% channel water, three strata of n=2, one declared stratum empty | **Fatal as submitted** for a community benchmark |
| C | T2V audit may measure configuration, not method — no released-pipeline rows | **Fatal as submitted.** R2 found the counter-evidence in our own Table 4 |
| D | VBench background consistency never scored, though it is the direct incumbent | **Answerable from disk** — see §2.1 |
| E | 120 s tier cannot support horizon claims; no matched-prompt sweep | **Confirmed unfixable** without regeneration — see §2.4 |
| F | Single seed | Needs regeneration |
| G | No license, DOI, hosting, maintenance plan, datasheet | Writing only |

Two sharp catches worth keeping:
- **Table 1 conflates direction of response with direction of desirability.** VBench DD
  satisfies both stated admission criteria yet is excluded by footnote. As printed it
  reads as a criterion built to exclude the incumbent. (R2, R3)
- **MCFF rotation response is "n/a"**, so the entire argument for the similarity
  compensation model in §4.2 is untested. (R3)

## 2. What we found on computing their requests (`scripts/incumbent_analysis.py`)

### 2.1 The incumbent partly does measure this
VBench background consistency agrees with NBF at method level, **rho = -0.71**
(and motion smoothness / temporal flickering at -0.82). "The incumbent cannot see
this" is not defensible.

What *is* defensible is resolution. Between-system range over mean within-system SD:

| metric | ratio |
|---|---|
| NBF | **6.42** |
| temporal flickering | 4.32 |
| motion smoothness | 3.06 |
| dynamic degree | 3.01 |
| MCFF-L | 1.92 |
| fBD | 1.81 |
| background consistency | **1.66** |
| FP | **0.67** |

Reframe the contribution from *"existing metrics cannot see this"* to *"existing
metrics rank it similarly but cannot resolve it"*. Note FP < 1.0: **FP cannot
separate these systems at all** and must stop being presented as if it can.

### 2.2 The headline sensitivity claim does not survive scale-free measurement
Perturbations are injected into the same clip, so the correct statistic is a paired
effect size. At maximum severity, `d_z`:

| family | fBD | NBF | VBench DD |
|---|---|---|---|
| translation | 1.53 | 1.70 | **1.27** |
| rotation | 1.02 | 0.35 | 0.82 |
| freeze | -1.32 | -0.82 | **-2.21** |

Dynamic Degree responds to injected translation at the same order as fBD, and responds
to freezing more strongly than any SNF factor. **The "3.2x versus 1.1x" framing is an
artifact of comparing raw multipliers across different dispersions** — exactly as R3
said. The claim that survives is about *direction of desirability*: DD moves in the
rewarding direction under a corruption a fixed-camera evaluation should penalise. That
is still a real and publishable finding; the magnitude framing must go.

### 2.3 Two factors fail selectivity once measured properly
Weakest on-target `|d_z|` against strongest off-target:

- **NBF: on 0.35 (rotation) vs off 0.68 (mask perturbation) — ratio 0.51. FAILS.**
- **DAR: on 0.43 vs off 0.75 (photometric) — ratio 0.58. FAILS.**
- fBD 1.59, FP 1.98, DLR 1.65, MCFF-L 1.28 pass.

NBF is a headline factor and it moves more under partition perturbation than under
rotational drift. This must be fixed or NBF must be scoped to translation/scale only.

### 2.4 The horizon sweep is impossible with current assets
Prompt sets are **fully disjoint**: 60∩120 = 0, 60∩240 = 0, 120∩240 = 0. No matched
horizon analysis can be computed from what exists. For a paper titled "Long-Horizon"
this is the structural gap R1 and R3 both named.

## 3. Work plan

### Tier 1 — no new generation (days)
1. Shared-partition rescoring: add an external-mask path to `metric_worker.py`, derive
   one partition per prompt (consensus across systems, or a held-out generator), rescore
   all systems, report whether Table 3 reorders. **This is the single highest-value item
   and the one reviewers said would decide acceptance.**
2. Add VBench background consistency to `validation_suite.py` and put it through the
   corruptions. Currently absent from validation records, so the incumbent has never
   been perturb-tested.
3. Rebuild Table 1: separate response sign from desirability sign; gate rotation or
   state why it is exempt; fill MCFF rotation instead of "n/a"; publish the full
   family x factor matrix (already computed).
4. Fix or scope NBF and DAR given §2.3.
5. Report FP's discriminability honestly; stop implying it separates systems.
6. Diagnose Causal-Forcing NBF 87.6/130: per-prompt distribution, is it one clip or all?
7. Otsu bimodality check per scene; horizon-dependent window analysis (12% = 7.1 s at
   60 s but ~29 s at 240 s, so the measurement definition changes across tiers).
8. Datasheet, license, DOI, hosting, maintenance and versioning policy.
9. Real fixed-camera footage as a null anchor and as a row in the audit table.

### Tier 2 — needs generation (weeks)
10. **Prompt set: 23 -> 80-120**, water share <= 35%, every declared stratum >= 8 items,
    with the authoring/sampling procedure written down. Without this the asset objection
    stands regardless of methodology.
11. **Matched-prompt horizon sweep**: same prompts at 60/120/240 s. Required to make any
    accumulation claim.
12. **Released-pipeline T2V panel**: each method at its own config, at least a subset,
    reported beside the common-setting rows exactly as the I2V track already does.
13. Multi-seed on a subset: 3 seeds, enough to compare between-system differences against
    within-system seed variance.
14. Manual future-blind masks: I2V first (shared source image, ~30 masks — cheapest), then
    a T2V subset.

### Tier 3 — scope decisions
15. Either add a repetition-sensitive diagnostic or state the loop-gaming hole as a
    scoped exclusion in the abstract.
16. Pair with one semantic-alignment score and show it rejects the drifting-fog case.

## 4. Venue

- **CVPR 2027** (Nov deadline): enough time for Tier 1 + most of Tier 2. Has a rebuttal,
  which materially helps a benchmark paper.
- **NeurIPS 2027 D&B** (May/Jun): the natural home; its criteria are what all three
  reviewers actually applied. Most time, strongest fit.
- **ICCV 2027** (Mar): viable if Tier 2 items 10-12 land.

Recommendation: target **NeurIPS 2027 D&B** as primary, with CVPR 2027 as the earlier
option if items 1, 2, 10, 11 and 12 all complete. Do not resubmit to a no-rebuttal
venue until item 1 is done.

## 5. What not to do

- Do not resubmit with the current prompt set. Three independent reviewers called it
  disqualifying; methodology fixes will not compensate.
- Do not retain the "existing metrics cannot see this" framing. It is measurably false
  (§2.1) and one reviewer already computed enough to notice.
- Do not keep the multiplier-based sensitivity claim (§2.2).

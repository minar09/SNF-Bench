# WACV 2027 official decision — what it requires, and where v2 stands

Decision (Area Chair cUBK, 9 Oct 2026, final 15 Oct): **Reject in round 2.**
Scores: YFhf 2 (Weak Reject, confidence 4), XzUA 3 (Borderline Reject), BsRf 3
(Borderline Reject), XNQG 4 (Borderline Accept).

The AC's two explicit conditions for a future submission:

1. **Substantially broaden and diversify the evaluation set.**
2. **Include human validation of the proposed metrics.**

Everything below is checked against the submitted version (commit `a11d926`,
25 Aug) and the current repository. "v2 today" means what exists and has been
verified, not what is planned.

---

## 1. Concern matrix

| # | concern | raised by | v2 today | still missing |
|---|---|---|---|---|
| A | **Scale and imbalance**: 23 prompts, 61% channel water, categories of n=2, lava empty | AC, YFhf, XNQG, XzUA, BsRf | 96 T2V scenes and 48 I2V pairs over 9 transport regimes; channel flow 12.5%; lava/geothermal populated (8 T2V, 4 I2V); every regime ≥ 8 T2V items | Under the six-medium scene contract, open/channel water is still **43.8%** (cap 35%) — taxonomy decision open. **No v2 T2V video has been generated or scored.** |
| B | **Different prompts per horizon** (120 s had 6 prompts) | XNQG, BsRf | Same scenes at every horizon; 41-source I2V test split; 9-pair 240 s stress subset preselected | Prefix scoring (60/120 s cut from one 240 s rollout) not implemented; separate rollouts of the same scenes instead |
| C | **Circular partition**: mask from each model's own early flow; ρ(area, fBD) = −0.75 | XNQG, XzUA, BsRf | Shared source-derived role masks (support / dynamic / overlay / ignore), source image as reference, registration failures counted. Ported (`snf_sourceref.py`); CPU parity exact (46/46 keys). The method project measured the old problem: the same scene's static fraction differs by median 0.18 across arms. | Masks are **AI-reviewed only** — BsRf asks for manual verification; human review of the 48 role maps is needed. T2V has no source image, so it needs an independent partition (first-frame-blind labels or held-out generator). 60 s GPU parity not yet run. |
| D | **No human validation** | AC, YFhf, XzUA (BsRf: manual mask check) | Protocol pre-registered (`SNF_V2_EVAL_SPEC.md` §6–7); v1 VLM failure diagnosed (8 frames ~8.6 s apart cannot show motion) | **Not run.** This is a condition, not an improvement. See §3. |
| E | **Blind to repetition** — a 2 s loop scores perfectly on MCFF-L/FP | YFhf (as a *failed admission*), XzUA, BsRf, AC | Recurrence candidate with synthetic controls (exact loop > 0.99 at the right lag, fresh motion < 0.5); codec floors measured — recurrence is 1.0 on frozen content, so it is read only where activity clears its floor | Admission study on independent controls, and validation against natural periodicity (surf). YFhf's framing is correct: in v1 it is a failed admission on the headline axis, and the next paper must say so. |
| F | **Premise already established** | YFhf | — | Reposition (§2) |
| G | **Table S11**: two of three VBench metrics agree with fBD/NBF | YFhf | Pilot evidence that agreement across systems ≠ sensitivity (§2) | Full corruption study of VBench background consistency (Tier 1 item 2) |
| H | **Common 4-step configuration**; single seed | XNQG, XzUA, BsRf | Plan: 3 seeds at 60 s. The method project already runs two seeds and native pipelines for its I2V baselines | **No native-config T2V panel.** Multi-seed v2 runs not done |
| I | **Narrow scope**: no camera motion, subjects, actions | BsRf, YFhf | v2 excludes people and moving vehicles by design | Scope must be stated as a choice, with YFhf's three-role argument answered (§2) |
| J | Not physical / semantic realism | BsRf, XzUA, AC | Out of scope by design | Pair with an alignment or physics score in the table, or state the boundary plainly |

### Minor points (YFhf), all still true of the submitted paper

* Table 1's ρ column mixes polarities; VBench Dynamic Degree passes the stated
  admission bar (ρ +0.70, 2% off-target) yet is excluded as "a contrast row".
  Either apply the rule uniformly or state why DD is not a candidate.
* DLR is marked admitted despite an inverted rotational response (−0.80). The
  Sep 28 response audit already moves DLR/DAR to supplementary diagnostics.
* Figure 1's prompt was chosen to maximise the fBD gap at minimum DD gap; the
  main caption must say it is an extremum, or the figure must use a
  rule-selected typical case.
* BsRf: the metric design is complicated for the setting. The demotions in the
  Sep 28 audit shrink the headline set, which helps.

### One reviewer claim that is a misreading — not worth contesting

YFhf says the supplement "advertises perceptual checks it does not contain".
The submitted supplement has an "Exploratory Perceptual Pilot" section that
opens "This section supports no perceptual-validity claim", and the main text
calls the pilots inconclusive. Only the overview sentence ("protocols for the
two complementary perceptual checks") could be read as more. The substance
stands: there is no human-alignment evidence. Fix the overview wording; don't
argue.

## 2. Repositioning (F, G, I)

**What is not ours.** VBench states the trade-off in "Trade-off across Ability
Dimensions": temporal-consistency dimensions and Dynamic Degree pull against
each other, and "relatively static scenes can 'cheat'" consistency (verified
against the paper, 2026-10-15). It does not discuss where motion occurs or
background drift. WorldScore already attributes motion spatially, at short
horizons (maximum flow in a SAM2 mask minus maximum flow outside it). SGC
separates static from dynamic for geometric consistency. DEVIL and DIVE penalise
static outputs. None of these may be presented as our discovery.

**What remains ours**, and must be demonstrated rather than asserted:

1. *Accumulation over minutes*, region-resolved, against the source: when
   support fidelity fails, how fast, and whether motion survives — not
   end-of-clip snapshots.
2. *Failure accounting*: registration failure, abstention and frozen flow
   reported as outcomes rather than filtered away. In the method project's
   data, registration failure carries a significant interaction that drift on
   registered frames does not.
3. *Persistence with repetition*: an activity, persistence and recurrence
   triple that can tell sustained, frozen and looped flow apart (once admitted).
4. *Validated selectivity*: each factor responds to its own corruption and not
   to others.

**Answer to Table S11.** Agreement across seven systems is expected, because
both families track stability. What matters is response to the failure. In the
5-clip pilot (`manifest/bc_stratified_pilot_summary.json`):

| corruption | VBench background consistency | NBF |
|---|---|---|
| injected translation | Δ −0.006 to +0.018; *increases* in 2 of 5 | +31 to +40 |
| progressive freezing | *increases* in 5 of 5 | — |

Background consistency barely responds to drift and rewards freezing. That is
the argument the paper needs, made on a full study rather than five clips:
same corruptions, all media, scene-clustered intervals.

**Answer to scope / three roles (I).** YFhf is right that a two-way split
coincides with semantics only when no subject exists. v2 already excludes
people and moving vehicles, and its role maps have four labels, including an
overlay role for precipitation. Make this explicit: SNF-Bench targets
subject-free scenes, where the failure is support drift and flow decay. Name
the three-role extension (static support / dynamic background / moving
subject) as future work rather than claiming generality.

## 3. Human validation — the gating item

The AC asks for human validation of **the metrics**, not of a method. Two
routes:

* **SNF-Bench's own study** (spec §6): public-baseline outputs on the v2 test
  split. Metric-stratified pairs — clear gap vs near tie on one family, matched
  on the others — plus method-comparison pairs. ≥ 20 raters, native speed,
  ties allowed, attention checks, and Kendall/Spearman between metric and human
  rankings. Needs the public-baseline renders first.
* **The method project's study** (its docs/90, collection Nov 1–7): blinded
  2AFC at native speed, three questions — scene preservation, natural
  persistent motion, seams/flicker/repetition — which map onto the SNF families
  one-to-one. Its per-pair majorities could be compared against per-pair metric
  differences as secondary agreement evidence. **But its stimuli are internal
  method arms**, which SNF-Bench's standing rule keeps out of the benchmark
  paper, and its pairs are not metric-stratified. Using it needs your decision.

Either way: no metric is called validated until its human agreement is
estimated with a stated α threshold, and VLM results appear only if their
controls pass.

## 4. Priorities

| priority | item | blocks | compute |
|---|---|---|---|
| 1 | Public-baseline renders on v2 (I2V test split first, then T2V), ≥ 2 seeds | A, B, D, H | GPU |
| 2 | Human validation study on those renders | D — AC condition | raters |
| 3 | Full corruption study of VBench background consistency and SNF factors | G | GPU / CPU |
| 4 | Recurrence admission on independent controls with natural periodicity | E | CPU |
| 5 | Human review of the 48 role masks; independent T2V partition | C | annotation |
| 6 | Native-config panel for representative T2V checkpoints | H | GPU |
| 7 | Rewrite the positioning (§2); fix Table 1 polarity, DD exclusion, DLR status, Fig. 1 caption, supplement overview | F, minor | writing |
| 8 | Decide the six-medium vs nine-regime taxonomy and the water cap | A | decision |

Items 1 and 2 are the AC's conditions; nothing else substitutes for them.

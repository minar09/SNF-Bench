# SNF-Bench v2 — evaluation specification (CVPR 2027 evidence package)

Status: 2026-10-02 protocol; research amendment 2026-10-08 KST. This is the single current specification of v2: what is
frozen, how it is split, what each reported number measures, and how human and
VLM judgements are collected. `VERSIONS.md` covers the version mechanics;
`NEXT_VENUE_PLAN.md` covers the benchmark paper. Where a decision is still open
it is listed in §1 with the date it must close.

---

## 1. Freeze status

| component | state | evidence |
|---|---|---|
| T2V scenes (96) | frozen | `manifest/prompts_v2.json`; fingerprint below |
| I2V pairs (48), images, captions | frozen | `manifest/i2v_pairs_v2.json`, `prompts/v2/i2v/images/` |
| consumer files (both tracks, 4 horizons) | frozen, exported | `scripts/export_prompt_set.py --check` |
| I2V splits + 240 s stress subset | frozen | `manifest/v2_splits.json` (§3) |
| measurement identity / no-pooling rule | enforced | `scripts/measurement.py`, gate *Single measurement per cell* |
| headline metric set and admission | **open** | §4; the Sep 28 response audit demotes four of six factors; the source-fixed re-score shows fBD's weaknesses; reviewed candidate decisions and independent validation plan in `I2V_METRIC_REVIEW_2026_10_08.md` |
| zero-motion floor ("glassy water" threshold) | **open, needs GPU** | gate *Zero-motion floor* is PENDING |
| direction / regime measure | **open, exploratory** | M2 probes, not validated |
| combustion direction rule (one rule, both tracks) | **open** | §2 |
| human and VLM protocol | specified here (§6–7) | pre-registered by this file's commit |

Input fingerprints (`python scripts/freeze_prompt_sets.py --fingerprint v2`):
v2 `sha256:ed0e79351381586f`, v1 `sha256:c004db4426968756`. Every render and
every score should record the v2 fingerprint.

**2026-10-08 amendment: selection exposure.** The 48-scene factorial
already exists and has been examined. Changes motivated by its endpoint
significance are retrospective; they cannot now be presented as frozen before
those results. Preserve the existing compatibility analysis, qualify new
metrics on independent controls, and confirm on untouched sources/models.
The benchmark's 41 test / seven overlapping split remains authoritative. See
`I2V_METRIC_REVIEW_2026_10_08.md` for the current decision and execution order.

## 2. Assets

| | T2V | I2V |
|---|---|---|
| items | 96 scenes | 48 image–text pairs |
| strata | 9 transport regimes, shares 12/12/10/10/12/10/12/8/10 | same strata, half size |
| horizons | 5, 60, 120, 240 s from the same scenes | same |
| model-visible text | scene, fixed camera, static support, medium + direction, light; no evaluator text, no negation, no metric vocabulary | same, transcribed from the image |
| conditioning image | — | exactly 832x480, so the pipeline resize is an identity |

Direction is declared for 69/96 T2V and 43/48 I2V items. *Not applicable*:
T2V oscillatory 10, combustion 10, windborne 4, geothermal 3; I2V oscillatory 5.

**Inconsistency to resolve before freeze (§1):** combustion abstains in T2V but
declares "upward" in I2V (5 items), and "upward" is in the I2V captions the
renders are already using. The captions stay as they are. The scoring rule is
the decision: either combustion abstains from net-direction scoring in both
tracks (recommended: flame tongues are turbulent, and a net-flow direction on
them is not a reliable measurement) or it is scored as upward in both. It must
be one rule for both tracks.

## 3. Splits (I2V)

From `scripts/audit_v2_split.py`, which compares every v2 source against every
image the method project and the v1 generation repository hold — training
(1,024 images across both repositories), the 7 development scenes, development
probes, the critic held-out pools, the v1 evaluation set and the supplementary
set — by exact hash, perceptual hash on two crops, and ORB+RANSAC geometric
verification (crop- and rescale-invariant).

| split | n | content |
|---|---|---|
| **test** | **41** | no match in any pool; nearest perceptual distance 12 bits, no geometric match |
| seen_overlap | 7 | the reused v1 evaluation images (`ifp01–04`, `iow01`, `iwb03–04`); exact matches. v1 was the method project's development set. Not training images. |
| stress_240s | 9 | one test pair per regime, chosen by seeded hash before any v2 output existed |

Per regime, test / seen: accumulating 5/0, buoyant plume 6/0, channel 6/0,
combustion 5/0, **falling precipitation 2/4**, falling water 5/0, geothermal 4/0,
oscillatory 4/1, windborne 4/2.

Consequences, stated rather than repaired, because v2 is frozen and the test
split must not be edited around results:

* The method project froze all 48 as its test split
  (`results/snf_v2/TEST_SPLIT_FROZEN.json`). Its test claims should be computed
  on the 41; the 7 are reported as a separate, labelled row.
* Falling precipitation has 2 test items. Overall claims are unaffected;
  category-level claims for precipitation are not supportable on test.
* The 41 sit inside the review's 30–60 planning range.

T2V has no development exposure (the 96 scenes were written for v2 and no method
has been tuned on them); all 96 are test. If a method needs a development set,
take it from the 7 `seen_overlap` sources and the method's own dev scenes,
never from test.

**Horizons.** 60 s and 120 s are principal. 240 s is a stress test run on the 9
preselected pairs only. All three use the same sources. The contract's
preference — scoring 60/120 s as prefixes of one 240 s rollout — is not
implemented in the scorer, so horizons are separate rollouts of the same scenes.

## 4. What the final table reports

Five families, never combined into a score, with this rule set:

* **R1** A low drift value cannot compensate for frozen or glassy flow. A clip
  whose late flow (MCFF-L) is below the zero-motion floor is reported as
  *frozen*. Keep its static-fidelity values visible so the activity/fidelity
  tradeoff is observable; a calibrated joint task outcome cannot pass on
  source fidelity alone.
* **R2** A high motion value cannot compensate for wrong-direction transport.
  Where direction is declared applicable, activity is reported beside direction
  correctness, not instead of it.
* **R3** Oscillatory and other non-translational regimes are never scored on net
  displacement. Their direction field abstains.

| family | SNF measure | status | incumbent / complement |
|---|---|---|---|
| source / geometry fidelity | source-support PSNR, legacy color distance and registration coverage as compatibility panel; pixelwise ΔE00 and regional perceptual distance as candidates; fBD/NBF diagnostics | no new candidate admitted; source reference and mask review scope required; fBD demoted, NBF scoped to translation/scale | official VBench-I2V source consistency; LPIPS/DreamSim candidates |
| activity and persistence | MCFF-E, MCFF-L; FP as decay indicator only | MCFF-L responds to freezing, fails the attenuation-vs-nuisance selectivity screen; FP fails it too | VBench dynamic degree |
| direction / regime | M2 endpoint probes against declared direction | **exploratory, not validated** | human judgement (§6) |
| replay / flicker / naturalness | none validated | **gap** | VBench temporal flickering; human and VLM (§6–7) |
| runtime | not measured by SNF | **gap** | seconds of compute per generated second, GPU type, steps — recorded by the generator in its run record |

Until §1's open rows close, fidelity and activity are available descriptive
measurements with known validity limits. Direction, naturalness and replay
require axis-specific human evidence; existing protocols do not establish
that this evidence has already been collected. VLM and official incumbents
remain complements. The architecture decision is frozen in the Oct 8 review;
candidate headline admission remains open.


### Measurement identity

A table cell aggregates only records with one signature: prompt set, metric
spec, mask version, flow backbone, feature backbone
(`scripts/measurement.py`). Output-derived masks, shared-source masks,
different temporal references and different fps conventions are different
measurements. Historical (v1) and current (v2) tables are never merged, and the
gate fails if any public cell mixes signatures. v2 scores live in `raw_v2/`
only and are written with `rerun_metrics.py --prompt-set v2`.

**Integration requirement (Oct 8).** The present five-field signature does
not distinguish all proposed candidates. Before migration, add explicit source
and reference policy, role-mask hash and review scope, fps/pair interval, fixed
window policy, crop/feature preprocessing and failure/occlusion accounting.
Different values in those fields are different measurements even when
`metric_spec_version` and backbone names match. **Enforced since 2026-10-08:**
`scripts/measurement.py` now keys on reference policy, mask set, mask review
scope, window policy, sample fps and failure policy, in addition to the original
five fields. v1.1 records predate these fields; their fixed policies are
derived from spec 1.1 (frame-0 reference, output-derived mask, 12% windows,
fallbacks included), so existing cells still pool. Any new record that declares
a different policy is refused. Remaining: crop/feature preprocessing has no
field yet, and a source-fixed writer must emit all of these explicitly.


## 5. Seeds

Every system is generated on the test split with **3 seeds** at 60 s, and the
seed count is reported. The 120 s principal horizon and the 240 s stress subset
use at least 1 seed, with 3 where compute allows. Seeds are fixed in the run
record as `base + item index`, matching the current render convention.

## 6. Human evaluation (pre-registered)

The goal is judgements of the specific natural-motion failures, which no
automatic measure here validly captures. The v1 pilot is the cautionary
reference: 8 raters, α = 0.18–0.24, and pairs that differed on more than the
axis being asked about. This design changes each of those.

**Units.** Two clips of the same source and horizon from two systems, shown
side by side, playing at each model's **native frame rate and real time**, with
no speed-up, scrubbing or looping until both have played once. The answer
controls unlock only after full playback.

**Blinding.** Systems are never named. Files are renamed to random tokens; the
key mapping tokens to systems is held outside the rater package. Left/right
position is randomised per trial; trial order is randomised per rater; each pair
is shown in both orders across raters.

**One question per trial,** each with a **"no clear difference"** option:

| id | question | family |
|---|---|---|
| Q1 | Which clip keeps the *background* (ground, buildings, rocks) more still? | fidelity |
| Q2 | Which clip's water/fire/smoke keeps moving *naturally until the end*, rather than slowing, freezing or turning glassy? | activity / persistence |
| Q3 | (direction-applicable items only) Does the moving material travel the way the caption says? — answered per clip: yes / no / can't tell | direction |
| Q4 | Which clip looks more like real footage — no repeating loops, flicker or sudden resets? | replay / naturalness |

**Two pair sets from the same clips:**

* *Method comparison* — proposed method vs each baseline on every test source,
  at 60 s.
* *Metric validation* — pairs chosen by the SNF measure for one family to be a
  **clear gap** (≥ 0.20 normalised difference) or a **near tie** (< 0.05), and
  **matched on the other families** (off-axis difference < 0.10). This is the
  axis isolation the v1 pilot lacked.

**Raters and checks.** At least 20 raters, at least 5 judgements per pair. Each
session includes identical-pair trials (correct answer: no difference) and
frozen-vs-moving trials on Q2 (correct: the moving clip). A rater failing more
than one check is excluded, by a rule fixed here, not after seeing their
answers.

**Analysis, fixed in advance.** Pair-level majority with a bootstrap over
pairs, not responses; Krippendorff's α per question; for metric validation, the
fraction of clear-gap pairs where the human majority agrees with the metric's
sign; at system level, Kendall's τ and Spearman's ρ between metric and human
rankings — the reporting standard of ChronoMagic-Bench and DEVIL. A metric
claim is made only where α ≥ 0.4 on that question.

## 7. VLM evaluation (complementary, gated)

Same pairs, same questions, same "no clear difference" option, using the
existing judge (`scripts/vlm_judge.py`, Qwen3-VL-8B-Instruct, greedy). It is
evidence beside human judgement, never a substitute.

* **Gates before any VLM result is reported:** identity control (same clip
  twice → SAME); position control (each pair in both orders — a verdict that
  flips with order counts as SAME); frozen-vs-moving swap on Q2. The v1 VLM
  passed identity and position but failed frozen-vs-moving (2/6), so Q2 VLM
  results are unreportable unless that control passes.
* **Frame sampling is the likely cause of the v1 VLM failure, and changes.**
  The v1 judge sampled 8 frames uniformly over a 60 s clip, about 8.6 s apart.
  At that spacing motion is not observable at all: a frozen clip and a flowing
  one give nearly the same frame set, which is consistent with the failed
  frozen-vs-moving control (2/6). v2 samples **bursts of consecutive frames** at
  the model's native rate — 4 bursts of 8 frames, at the start, middle, start of
  the late window (last 12%) and end — so motion is visible inside a burst and
  drift across bursts. The v1 sampler is left unchanged so v1 results remain
  reproducible.
* **Stated limitation:** even with bursts, a VLM sees about 5 s of a 60 s clip,
  not native-speed playback. That is why it is a complement to §6.
* A second open-weight VLM is run if compute allows; disagreement between the
  two is reported, not resolved.
* VBench dimensions (background consistency, temporal flickering, motion
  smoothness, dynamic degree) are reported beside SNF on the same clips, from
  the pinned protocol in `configs/vbench_incumbent_protocol.json`.

## 8. Method-side items (not SNF-Bench work, recorded so they are not lost)

* **Factorial on the test split.** The method plan schedules a granularity ×
  memory factorial at 60 s "on the v2 test split" (Oct 4–11). Choosing a
  configuration from that factorial is method selection on test. Run it on the
  7 development scenes plus the 7 `seen_overlap` sources, or treat its winner as
  fixed in advance and the factorial as an ablation reported after selection.
* **Teacher-window motion suppression.** The tranche-1 automatic filter kept
  windows with 0.22× the flow of rejected ones; the method's own anti-bias rule
  is < 0.8×. Visual admission qualifies sources, not the online teacher's score
  on student samples. Owned by the method project.

## 9. Gates that must pass before the CVPR tables are built

`python scripts/gate_status.py` — in particular *Prompt-set separation*,
*Single measurement per cell*, *v2 consumer files current*, *Records newer than
videos*, *Generated assets current*; plus `freeze_prompt_sets.py`,
`assign_v2_splits.py --check` and `export_prompt_set.py --check`, all in the
test suite.

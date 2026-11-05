# SNF-Bench++: adding realism checks while answering the WACV 2027 review

2026-11-04. The working plan. It merges three documents into one order of work:
the WACV review response (`WACV27_OFFICIAL_REVIEW_RESPONSE.md`), the realism
design (`SNF_PP_REALISM_DESIGN_2026_11_04.md`) and the independent realism
review (`SNF_PP_REALISM_REVIEW_2026_11_04.md`). Where those disagree, this file
follows the review. Nothing here is a result. No measurement is admitted, and
no frozen identity changes.

## 0. Position in one paragraph

SNF-Bench measures *where* motion occurs and whether it persists. The
reviewers' sharpest objection (XzUA W2, BsRf, YFhf, AC) is that it does not
say whether the motion is natural, correct or progressing, so a loop or a
paste can look good. SNF-Bench++ keeps its core axes:

* support fidelity;
* material behavior;
* continuity.

It adds a **separate realism family of five constructs**. Each construct is
validated on its own targeted controls and on its own human question, and is
reported beside the core axes, never summed with them. The incumbents (VBench,
VBench-2.0, WorldScore, TRAJAN, FVMD) are run on the same videos and controls
and held to the same admission rules. The contribution then rests on
measured, incremental validity, not on a premise the reviewers say is already
established.

## 1. Every review point, and what answers it

Status: **done** = in v2 and checked; **partial** = built, not validated;
**open** = not started.

| # | concern (reviewers) | answer in SNF-Bench++ | status |
|---|---|---|---|
| 1 | Masks from each model's own early flow: circular (XNQG, XzUA W1, BsRf) | I2V: source-derived 4-label role maps, identical for every system. This removes the feedback loop, but not semantic error, and it does not cover subjects that appear later. T2V: per-output annotation, blinded to model and metric, with uncertainty | I2V loop **done**, semantic accuracy **open** (row 2); T2V **open** |
| 2 | No manual mask verification (BsRf) | two independent annotators on all role maps, agreement reported, adjudication; current maps are AI-reviewed plus lead checks, never called "human-verified" | **open** |
| 3 | Scale and diversity: 23 prompts, 61% channel water (AC, XzUA W3, XNQG, BsRf) | v2: 96 T2V scenes and 48 I2V pairs over nine regimes, max regime share 12.5%, regime macro-average. The four water regimes together are still 44% of each track (42/96, 21/48), so water is reported as an aggregate group too. A fresh confirmation set is reserved | scene **specifications** done; renders, seeds, annotation and rights **open**. The 24 fresh sources were already inspected (21 have no licence recorded), so untouched confirmation scenes must still be reserved |
| 4 | 120 s used different prompts (XNQG) | v2 uses the same scenes at every horizon. Prefixes of one 240 s rollout are preferred, and are never called independent videos | same-scene specs **done**; matched rollouts and prefix scoring **open** |
| 5 | Single common 4-step configuration, single seed (XNQG, XzUA W4) | released native pipelines as the primary row type; common-configuration audit kept as a labelled secondary row; ≥ 3 seeds at 60 s | **open** (GPU) |
| 6 | No human alignment (AC, YFhf, XzUA) | §4: separate questions per construct; win-ratio Spearman, video-level SRCC/PLCC/KRCC where per-video scores exist, Krippendorff α | spec **partial**; owned by the human-study engineer |
| 7 | Blind to repetition: a 2 s loop scores perfectly (YFhf, XzUA, BsRf) | realism construct R4: recurrence plus seam/reset, active-area gate, natural periodic negatives; reported as detection and false-positive rates | kernel and synthetic tests **partial** |
| 8 | Does not measure natural, correct or meaningful motion (XzUA W2, BsRf) | realism constructs R2 (material), R3 (direction), R5 (plausibility) | **open** |
| 9 | Premise already in VBench's trade-off discussion, WorldScore static/dynamic, DEVIL, DIVE; S11 shows two incumbents already agree (YFhf) | Related Work engages them by name; the claim moves to *incremental validity on the same videos and controls*, including where incumbents agree | draft **done**; experiment **open** |
| 10 | Two-way partition too coarse: subject vs dynamic background (YFhf) | add a moving-subject role (label 4) in role maps **v2.1** (new mask version, not an edit). Boat-on-frozen-water control. Human/animal subjects stay an extension track | **open** |
| 11 | Narrow scope: no camera motion, objects, humans (BsRf) | stated as a task-specific benchmark. Camera motion is out of scope; the subject track is optional and separately validated | draft **done** |
| 12 | Metric design complicated for the setting (BsRf) | one headline measure per axis and per realism construct; the rest are diagnostics in the appendix | **open** (needs admission results) |
| 13 | Dynamic Degree met the admission bar but was excluded by fiat (YFhf minor) | incumbents follow the same admission rules; a passing incumbent is reported as passing | draft **done** |
| 14 | DLR admitted despite inverted rotational response (YFhf minor) | an admission is withdrawn when any targeted response has the wrong sign | rule **done**; applied at admission |
| 15 | Fig. 1 prompt chosen as an extremum (YFhf minor) | every selected qualitative example states its selection rule in the caption | **open** (writing) |
| 16 | Precipitation crosses support (XzUA W3) | overlay role (label 3) enters no measure; precipitation abstains where a measure needs a clean support. That is an exclusion, not a validated precipitation score | abstention **done**, reported with counts; precipitation measurement **open** |

## 2. The realism family

Each construct names one failure, its data, its candidate statistic, the
controls that target it and the nuisances it must ignore. Its human question
is in §4.

| id | construct | data it needs | candidate statistic | targeted controls | must be invariant to | comparator |
|---|---|---|---|---|---|---|
| R1 | **support integrity (diagnostic)**: describes support change and boundary coherence; it does *not* establish paste or redraw, since valid backgrounds can be still and good composites can look natural | role maps; real footage (medium level) | successive-frame support change after drift and illumination compensation (`cand-support-change-comp-0`); boundary step (`cand-edge-profile-0`) | pass-through vs paste, residual-matched paste, delayed-residual paste, feathered and illumination-matched paste; retexture; local redraw | global illumination change, small drift (handled by the support-fidelity axis), codec settings (tested subset) | source PSNR / ΔE00, VBench background consistency |
| R2 | **material presence and location**: the requested material carries the motion | role maps v2.1 with subject label; material label per source | per-role activity and active area; activity ratio material vs subject | boat moving over frozen water; fog moving instead of water; motion only in the subject | amount of motion within a plausible range | VBench dynamic degree (whole frame) |
| R3 | **direction**: material moves the declared way | declared direction (43/48 I2V, 69/96 T2V) is text-derived, so a *candidate* label; independent annotation with unknown, ambiguous and multi-direction options | flow component along the declared image-plane direction; inflow at the boundary | time-reversed and ping-pong clips at matched magnitude; zoom; expanding texture | speed; oscillatory and turbulent media abstain (combustion abstention to be decided, spec §1) | none direct; VLM judge as a secondary signal |
| R4 | **progression vs replay** (rates by medium and period; smooth long loops can be seamless) | real periodic and non-periodic footage (surf, fire, wind, foliage) as negatives | multi-frame recurrence with seam/reset evidence, active-area gate (`cand-recurrence-0`) | exact, variable-period, cross-faded, recoloured, ping-pong loops; late freeze | natural periodicity; transient events | none established |
| R5 | **motion plausibility**: flow looks like that material | real fixed-camera footage, medium level, multiple independent scenes | flow, track and dynamic-texture statistics inside the dynamic role, as distances to the medium's real distribution with source-family uncertainty | noise warp, boiling texture, flicker, real footage resampled to 0.25–4× speed (graded severity, natural appearance) | resolution, exposure, encoder settings | TRAJAN (per video), FVMD (set level only, never a per-video verdict; report sample-size sensitivity), VBench-2.0 physics (record any adaptation), VMBench, dynamic-texture features from Generative Image Dynamics |

Rules for the whole family:

* **Targeted, not universal.** A measure is tested only on its own control
  families, plus its declared invariances. The earlier "AUC ≥ 0.9 against every
  control" rule is withdrawn. The effect-size threshold, minimum eligible
  coverage and incumbent comparison are fixed per measure on development data.
* **Same encoding history.** Every control is compared with a pass-through
  re-encode of its own parent (`scripts/build_composite_controls.py`, mode
  `passthrough`). Whether the codec alone separates them is tested on a
  prespecified subset, never assumed.
* **Real footage gives distributions, not targets.** A real continuation is one
  plausible realization, so no pixel comparison is made against it. Bands are
  medium-level, built from multiple independent scenes; windows of one
  recording are correlated and never counted as independent.
* **A cinemagraph is not wrong by definition.** A paste counts as a defect
  only where the task or the human raters say so. R1 describes support change
  and boundary coherence; it does not establish that a support was pasted, and
  a separate human question decides whether what it shows is a defect.
* **No physics claim** is made from any 2D statistic.

## 3. Data the family needs

| item | size and why | source | status |
|---|---|---|---|
| Real fixed-camera footage | Start with an **8–12 scene capture pilot** to test capture and processing. Then size the collection per stratum: 0 false alarms in 30 independent scenes bounds the rate at about 9.5% (one-sided 95%), 0 in 59 at about 5%, *per stratum*, and only if scenes do not share sites or conditions. The budget below is a starting point, not a coverage guarantee. Groups: flowing water (channel, falling, accumulating), oscillatory water, plume and combustion, windborne and precipitation. That is about 120 scenes, each 1–5 min, plus ≥ 30 periodic negatives inside them | project-shot tripod footage plus rights-cleared external footage. Record creator, rights and permissions, site/session, duration, fps, stabilization, codec, medium and weather; split by site/session before any tuning. DynTex only for non-commercial diagnostics | **open**; the critical path |
| Role maps v2.1 | layered design, §3.1; two independent annotators plus an adjudicator; new mask version and identity, v2 maps untouched | v2 test + fresh sources | **open** |
| Published-entrant renders | native pipelines, ≥ 3 seeds at 60 s; 120/240 s on the frozen subset; same scenes across horizons | model survey high-priority list | **open** (GPU 2/3 only, when free) |
| Controls | built from the panel's own renders and from real footage, with provenance sidecars | `build_composite_controls.py` (six support modes, hash chain); loop, reversal, speed and noise builders still to write | support modes **done** (synthetic smoke test only) |

### 3.1 Role maps v2.1: proposed representation (not built)

One exclusive label per pixel cannot represent a boat over water, an occluded
subject or an object that appears later. Proposal, per source:

* `labels.png`: unchanged v2 semantics (0 ignore, 1 support, 2 dynamic,
  3 overlay), so every v2 reader and identity keeps working.
* `subjects/<k>.png`: one binary layer per moving-subject instance, allowed
  to overlap the material, plus `subjects.json` with each instance's class,
  visibility (full / partial / occluded) and an *unknown* option.
* `material.json`: the requested material per dynamic region, or *ambiguous*.
* `direction.json`: image-plane sector(s), or *isotropic*, *multi*, *unknown*,
  *ambiguous*, drawn independently of the caption.
* Each file records its annotator. Adjudicated files are kept separately.

`snf_sourceref.load_role_masks` rejects any label above 3, which is correct for
v2. A separate v2.1 reader, schema check and compatibility test must exist
before any annotator writes a v2.1 file. Output-specific annotation stays
necessary for subjects that appear after the first frame.

## 4. Human questions (proposal for the human-study owner)

The human study is owned by another engineer and is not edited here. Spec §6
has four questions; the review asks that constructs not share one. Proposed
split, each with *no clear difference*, *cannot tell* and *not applicable*:

| current | proposed | construct |
|---|---|---|
| Q1 background more still | keep | support fidelity |
| Q2 moves naturally until the end | split: **Q2a** *still moving at the end?* (amount, persistence); **Q2b** *does the motion look like real water/fire/smoke?* | core axis; R5 |
| Q3 direction as the caption says | keep, per clip | R3 |
| Q4 real footage: no loops, flicker, resets | split: **Q4a** *does any part visibly repeat or reset?*; **Q4b** moves into Q2b | R4; R5 |
| — | **Q5** *is the moving thing the [material], or something else?* | R2 |
| — | **Q6** *does the background look like part of the same footage, or pasted?* | R1 |

* **Analyses.** Pairwise preferences, video-level ratings and model win ratios
  stay separate analyses. A source-conditioned real-vs-generated trial is an
  extra discrimination test only, because sharpness and codec cues drive it.
* **Sizing.** Rater and pair counts come from a pilot-based precision plan; the
  existing spec has ≥ 20 raters and ≥ 5 judgements per pair. Interim
  SceneTether study modules are secondary evidence and are not pooled.

## 5. Order of work and gates

| step | work | needs | gate to pass before the next step |
|---|---|---|---|
| 1 | Provenance audit of the 2026-11-04 pilot (parent, control and still hashes, encoder history) | CPU | each control has a hash chain, or is labelled exploratory |
| 2 | Real-footage capture plan and rights; v2.1 annotation protocol; human-question proposal to the owner | people | protocols frozen; development/confirmation split by scene family and model family, set before any score is seen |
| 3 | Remaining control builders: loops, reversal and ping-pong, speed resampling, noise warp, boiling, subject-only motion | CPU | unit tests with known answers |
| 4 | Development challenge: every candidate and incumbent on controls built from real development footage and from development renders | CPU, then GPU for flow and tracks | per-measure targeted effects and false-positive rates with intervals; failing measures demoted to diagnostics |
| 5 | Panel renders (native, ≥ 3 seeds) | GPU 2/3 | renders hash-bound and imported |
| 6 | Human pilot, then the main study (owner) | raters | agreement with uncertainty, analysed by source and rater cluster. α ≥ 0.4 is necessary but not sufficient; disagreement and not-applicable rates are investigated |
| 7 | Frozen confirmation on held-out scene and model families; preregistered analysis | CPU/GPU | admit only constructs that pass every applicable gate |

## 6. Decisions needed from the user

An independent decision review
(`SNF_PP_REALISM_DECISION_REVIEW_2026_11_04.md`) made recommendations on each
of the four decisions.

1. **Reuse: authorized by the user on 2026-11-05.** New, separately
   versioned candidate statistics and derived controls may be computed on
   existing videos; originals, existing scores, manifests and frozen metric
   identities stay untouched, and the frozen metrics are not rescored. All
   such videos are development data. The split was frozen before any new
   statistic (`manifest/realism_dev_split_2026_11_05.json`, §9). The
   2026-11-04 colour audit and paste pilot ran before the authorization: they
   are exploratory, the deviation is disclosed, and they can never become
   confirmation data.
2. **Footage.** Both project-shot and rights-cleared external footage, starting
   with an 8–12 scene pilot. The shooter is not yet assigned.
3. **Role maps v2.1.** Approve the §3.1 design, then name two annotators and an
   adjudicator. The reader and schema come first.
4. **Human questions.** The review drafted a version for the study owner (its
   last section). Neither it nor §4 has been sent; the owner's study is
   unchanged. What must be prepared before sending, reconciled into one
   question set (H1–H8), is in `SNF_PP_HUMAN_QUESTION_PROPOSAL_PREP_2026_11_05.md`.

## 7. What may and may not be claimed now

* **May:** a SceneTether-vs-paste separation on 42 scenes for successive-frame
  support change, and on 13 eligible scenes for boundary step. That is one
  model, one seed, development data, an unblinded comparison against the
  once-encoded original, with no real band. Also: edge spill is rejected in its
  naive form.
* **May not:** that any measure detects realism, natural motion, physical
  correctness or composites in general; that one encoder removes codec cues;
  that the H.264 still floor is zero in general (12 of 42 pastes had a nonzero
  median).

## 8. Safeguards added (2026-11-04, after the decision review)

Tested on synthetic data only; no existing video was read.

* `build_composite_controls.py`:
  * refuses to start if any output exists;
  * writes each output under a temporary name;
  * re-decodes it with PyAV and requires the parent's frame count, 16 fps,
    832×480, h264 and yuv420p before the file and its sidecar are put in
    place;
  * the sidecar records what was decoded.
* `pilot_support_realism.py`:
  * requires a sidecar for every control and for the pass-through, and checks
    parent, source, mask and output hashes against the inputs it was given;
  * refuses to overwrite a report;
  * records sampling actually used and abstention reasons;
  * empty eroded support abstains.
* Drift compensation:
  * a support with too little texture abstains;
  * a frame pair with a weak or non-finite phase-correlation peak is
    rejected;
  * pixels the shift brings in from outside the frame are excluded.
  * It still removes only translation and a global grey offset; rotation,
    zoom and spatially varying light remain.
* **Bug found by the new tests.** On the masked support, the fixed mask edge
  dominated phase correlation: a textureless support gave a 0.998 peak at
  zero shift, so drift on weakly textured supports would have gone
  uncompensated silently. Fixed by mean-subtracting inside the support.
* **Eligibility explained.** v2 role maps keep an ignore band between support
  and dynamic: 3–108 px, median 7, over 8 px in 15 of 41 scenes. Bands
  measured from the dynamic edge therefore missed most supports (13/41
  eligible). Measured from where the support starts (`cand-edge-profile-1`),
  37/41 are eligible, checked on the masks alone.
* **Codec observation.** On a synthetic clip, about 5 grey levels of i.i.d.
  per-pixel noise was erased by default H.264 encoding (support change 0). Fine
  grain does not survive the renders' encoder, so real-footage references
  must pass through the same encoder, and `support_change` sees only change
  that survives compression.


## 9. Development round 1 (2026-11-05, after the reuse authorization)

Development data only: CF++-family videos on already-inspected scenes. Every
number here is separability from constructed controls, not realism, and none
can become confirmation evidence.

**Split frozen first.** `manifest/realism_dev_split_2026_11_05.json`
(sha256 `55e71f6496ff370d…`), written by `scripts/freeze_realism_split.py`
before any new statistic was computed:

* development scenes are all 48 v2 I2V and 24 fresh scenes, since all have
  been inspected; confirmation needs new scenes, and none exist yet;
* development model family: every CF++ cell, plus the method project's
  control cells;
* confirmation model families: published-panel I2V renders made after the
  freeze;
* existing native SVI Pro and Helios records are withheld from development;
* SceneTether and H1-FM are in the development family, so their confirmation
  is not held out by model family;
* 168 parent videos are hashed. The 94 artifacts of 2026-11-04 (42 pastes,
  48 stills, 4 manifests) have no sidecars and are labelled exploratory, which
  passes gate 1.

**Matched encoding history.** The method project's composite controls
(`control_pasteback`, `control_composite_untethered`,
`control_composite_framepack`, `control_still`):

* were built from its own generation maps, not from our evaluation masks;
* were decoded with cv2 and re-encoded with libx264 at CRF 18.

Rebuilding two of them with `snfeval` (cv2 4.9.0) and the same ffmpeg
reproduced their SHA-256 exactly. Each composite is therefore compared with a
pass-through of its own parent through that path
(`scripts/native_controls.py passthrough`). The controls are adopted by hash
and linked, never copied. The new temporal controls use the same path.

### R1: support (`manifest/realism_dev_2026_11_05/support_*.json`; 42 scenes, matched pass-through as reference)

| statistic: pass-through vs composite | paste-back (hard) | feathered, untethered | feathered, FramePack |
|---|---|---|---|
| support change | 2.98 vs 0.00, 42/42 | 4.55 vs 0.36, 42/42 | 4.46 vs 0.67, 42/42 |
| boundary step (37 eligible) | 0.83 vs 0.34, 89% | 0.70 vs 0.57, 84% | 0.78 vs 0.78, 73% |
| edge spill, composite higher | 81% | 97% | 92% |

* **Support change separates only because this generator's support changes.**
  The generator's support changes by 3–4.5 grey levels per sampled frame, and
  a composite removes that change.
  * A truly fixed real background would also be near zero; the CRF-18 still
    scores 0.00.
  * The statistic is therefore confounded with fidelity, and stays a
    diagnostic, as §2 says.
* **Boundary step does not separate the most natural composite.** On the
  feathered FramePack composite, built from its own pixel map, it is 0.78
  for both.
* **Edge spill is undefined when the far support is static.** The 1e-6 floor
  turns the ratio into values around 10⁵. It needs an abstention rule and a new
  identity before any further use.

### R3: direction (`direction_*.json`; RAFT on GPU 3, text-derived labels)

Generated parents (pass-throughs), 36 scored scenes each:

| cell | median flux | flux above 0 |
|---|---|---|
| framewise Echo | 0.07 | 56% |
| untethered | 0.17 | 72% |
| FramePack-style | 0.28 | 75% |

* **Accumulating level ("upward") is negative in every video.** That holds for
  all three cells, so the label probably does not describe image-plane
  texture motion. Candidate: abstain for this medium.
* **Falling water ("top to bottom") sits near 0.** Streaky falling water is a
  quasi-stationary pattern, which optical flow at 288 px and 8 fps barely
  tracks.
* **Four scenes are negative in all three cells** (ial02, ial05, iwb01,
  iwb05). These go first to the independent direction annotation.
* **icb04 has no dynamic pixels in its role map**, already flagged in the
  mask coverage report. It abstains.
* **Doubled speed collapses the flux to about 0 instead of keeping its sign**
  (smoke scene). The texture decorrelates beyond what RAFT can match, so this
  measure is not speed-invariant.

R3 known-answer controls on SceneTether (`direction_scenetether.json`; 36 of
42 scored: 5 have no declared direction and icb04 has no dynamic region):

| control | expected | observed |
|---|---|---|
| reverse tail | sign flips | flipped in 81% of scenes (88% of the 25 with \|flux\| > 0.2); r = −0.87 |
| ping-pong | flux toward 0 | \|flux\| fell in 83%; median 0.09 vs 0.34 |
| freeze | abstain | 42/42 abstain |
| noise warp | flux toward 0 | \|flux\| fell in 94%; median 0.03 |
| shuffle | flux toward 0 | \|flux\| fell in 81% |
| speed ×2 / ×0.5 | same sign, speed ×2 / ×0.5 | same sign in 78% / 94%; measured speed ×1.31 / ×0.69 |

* Flow-measured speed is compressed: a doubled speed reads as about 1.3×.
  Speed controls are therefore graded, not calibrated.

### R4: replay (`replay_scenetether.json`; 41 scored)

| statistic | pass-through | exact loop | cross-faded loop | ping-pong | shuffle |
|---|---|---|---|---|---|
| `cand-recurrence-0` (appearance), median | 0.981 | 1.000 | 1.000 | 1.000 | 0.972 |
| `cand-recurrence-1` (residual), median | 0.52 | 1.00 | 1.00 | 1.00 | 0.41 |
| `cand-seam-0`, control above pass-through | – | 71% | 41% | 20% | 46% |

* **The incumbent `-0` cannot separate loops.** 34 of 41 generated videos
  score ≥ 0.95 without a loop (maximum 0.9999), so no threshold works.
* **The residual version `-1` peaks at 0.941 on pass-throughs** (90th
  percentile 0.85).
  * Exact repeats score 1.0 by construction, so this is a weak known answer.
  * The next round needs jittered and variable-period loops, and natural
    periodic negatives.
* **Freeze is caught by activity (0.00), not by the residual floor.** Encoder
  noise on a frozen frame gives a residual RMS of up to 0.72, so 11 of 41
  freezes scored a recurrence of 1.0 instead of abstaining.
* **The seam statistic is weak** and only detects hard cuts.

### Next round (development)

1. Give edge spill an abstention rule for a static far support, under a new
   identity.
2. Raise the residual floor above codec noise, or abstain on zero activity,
   under a new identity.
3. Add jittered and variable-period loops and partial-region loops.
4. Make medium-level abstention rules for R3: accumulating level, and falling
   water if the flow failure is confirmed on real footage.
5. Run every control on a second parent family, ideally real footage once the
   pilot exists.

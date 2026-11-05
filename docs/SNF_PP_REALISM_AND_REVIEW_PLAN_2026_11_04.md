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
   unchanged.

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


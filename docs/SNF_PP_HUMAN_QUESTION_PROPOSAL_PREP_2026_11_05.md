# Human-question proposal: what to prepare before it goes to the study owner

2026-11-05. A preparation list, not the proposal itself and not a change to the
study. The human study belongs to another engineer: nothing in `human_study/`
or its protocol is edited here, and nothing has been sent. The user decides
when the finished package goes to the owner.

Sources:
* `SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md` §4 (Q1–Q6 split);
* `SNF_PP_REALISM_DECISION_REVIEW_2026_11_04.md`, last section (draft
  questions a–f);
* `SNF_PP_REALISM_ROUND1_DECISION_REVIEW_2026_11_05.md`, "People and study
  decisions";
* `TCSVT_JOURNAL_EXECUTION_PROTOCOL_2026_11_01.md`, "Human metric-validation
  study" (six distinct ratings).

## 1. What the owner's study is today (read-only snapshot)

| item | observed |
|---|---|
| instrument | `snf-bench-axis-study-v1`, Apps Script web app (`human_study/code.gs`, `index.html`) |
| questions | two pairwise questions: background drift (*which background moves more?*) and motion decay (*which moving content slows or stops more?*); ties allowed |
| responses | 192 (96 per axis): 24 trial IDs, 17 prompts, 7 systems |
| raters | 8 rater IDs, one of them named `test` |
| systems | CausVid, Causal Forcing, Infinite Forcing, LongLive, Reward Forcing, Rolling Forcing, Self Forcing |
| track | the responses are T2V 60 s (`manifest/human_study_scored.json`) |
| controls | 2 sentinel trials (a clip against itself); order and left/right randomised; dwell time and playback problems logged |

The README describes 8 I2V scenes × 3 systems, but the responses are T2V with
7 systems. That is the first thing to ask the owner (§5); we do not resolve it
ourselves.

The proposal therefore **extends** a pairwise, two-axis instrument. It does
not revise a six-question one, and the realism questions are not in it yet.

## 2. The question set to propose (reconciled from the three sources)

Each question measures one construct and is answered with *cannot tell* and
*not applicable* available. Pairwise questions also allow *no clear
difference*. Wording is neutral: no question presupposes that compositing,
stillness or periodic motion is bad.

| id | question (draft wording) | construct | eligible clips | validates |
|---|---|---|---|---|
| H1 | Which clip's **background** (the parts that should stay fixed) moves or changes more? | support stability | all | frozen NBF, fBD; R1 diagnostic |
| H2 | Has anything **appeared, disappeared or changed shape** in the scene compared with the start image? | scene integrity | I2V; T2V against its first frame | source fidelity axes |
| H3 | Is the [material] **still moving in the last part** of the clip? | persistence | all | frozen MCFF-L, FP |
| H4 | Does the [material]'s motion **look like real** [water/fire/smoke/dust]? | plausibility | all | R5 |
| H5 | Is the [material] moving **[declared direction]**? | direction | only scenes with a verified, observable direction | R3 |
| H6 | Does any part **visibly repeat, jump back or reset**? | replay | all; naturally periodic media flagged | R4 |
| H7 | Is the thing that moves the **[material]**, or something else? | material | all | R2 |
| H8 | Does the **background look like part of the same footage** as the moving parts? | support coherence | all | R1 diagnostic |

* Bracketed text comes from the scene record. H5 and H7 need the v2.1
  annotations (§3, item 2), not the text-derived labels.
* H1 and H3 are the owner's existing axes, rephrased so that H3 asks about
  *amount* (persistence), not quality. Ask the owner whether H1/H3 should keep
  their exact current wording, so the v1 responses stay comparable.

## 3. Materials we must prepare

Status: **ready** = exists; **draftable** = we can write it now; **blocked** =
waits on people or data.

| # | item | what it contains | status / blocker |
|---|---|---|---|
| 1 | Question sheet | final wording of H1–H8, ordinal anchors (e.g. 5-point for per-clip, A/B/no difference for pairs), help text, the *cannot tell* / *not applicable* rules | draftable |
| 2 | Per-clip eligibility table | for every stimulus: which of H1–H8 apply, material name, verified direction (or *unknown*/*multi*/*isotropic*), periodic-medium flag, overlay present | **blocked**: H5/H7 need v2.1 direction and material annotation (two annotators + adjudicator, unassigned) |
| 3 | Anchor examples | 1–2 clear and 1 borderline example per question, for rater training; drawn from development data only, never from confirmation stimuli | draftable from development videos; real-footage anchors **blocked** on the footage pilot |
| 4 | Stimulus sampling plan | strata (medium, track, model family, horizon, failure severity); counts per stratum; the development/confirmation rule from `manifest/realism_dev_split_2026_11_05.json` and its pending amendment (seen scenes/new families vs new scenes) | draftable; final counts need the pilot |
| 5 | Control stimuli list | freeze, drift, exact/varied/partial loops, reversal, ping-pong, paste-back, feathered composite, still; each with its provenance sidecar | partly ready (`videos/realism_controls_2026_11_05/`, development only); varied/partial loops not built yet |
| 6 | Natural negatives | real fixed-camera footage, including naturally periodic media (surf, flames, fountains) and genuinely still backgrounds, with rights records | **blocked**: footage shooter unassigned |
| 7 | Playback and encoding spec | one encoder for all stimuli (the verified CRF-18 path), 832×480, 16 fps, full duration; which windows are shown (full 60 s for H3/H6, or verified early/late segments) | draftable |
| 8 | Hosting list | new clips only, with new links; **existing Drive links are not touched** | blocked on item 4 |
| 9 | Trial design options | per-clip ordinal vs pairwise per question; anchor trials repeated across raters; sentinels; tasks per rater | draftable as options for the owner to choose |
| 10 | Rater burden estimate | e.g. one 60 s clip + 8 questions ≈ 2.5 min, so 12 clips ≈ 30 min a session; to be measured in a pilot | draftable |
| 11 | Pilot and sizing plan | pilot size; target interval width per construct; simulation of scene and rater variance; stopping rule | draftable; numbers come from the pilot |
| 12 | Analysis plan | each question mapped to its metric or candidate; source- and rater-clustered intervals; how ties, *cannot tell* and *not applicable* are handled; v1 responses analysed separately, never pooled | draftable |
| 13 | Blinding rules | no system names, metric values or control labels shown; randomised order and side; controls mixed in at a fixed rate | draftable |
| 14 | Response schema additions | new columns: question id, clip id, shown window, eligibility, answer, *cannot tell* / *not applicable* | draftable, as a proposal; the owner implements |
| 15 | Ethics and consent | consent text, compensation, privacy and retention, institutional review or exemption status | owner/institution; we only list the requirement |

## 4. Order of preparation

1. Draft items 1, 7, 9, 10, 12, 13 and 14 now. They need no people or new
   data.
2. Draft items 4 and 11 with placeholder counts.
3. After the v2.1 annotation exists: item 2, and H5/H7 become usable.
4. After the footage pilot: items 3 (real anchors) and 6.
5. Build the missing controls in item 5 (varied and partial loops) under the
   round-1 review's fixes: fail-closed adoption, and reliability guards for
   seam and edge spill.
6. Assemble the package, then the user decides whether to send it.

## 5. Questions only the owner can answer

1. Which study is current: the T2V 7-system responses, or the I2V 8 × 3 design
   in the README? Is v1 closed?
2. Should H1–H8 be a new module beside v1, or a revision of v1?
3. Can the web app support per-clip ordinal ratings, or only pairs?
4. What is the maximum session length, and how large is the rater pool?
5. Can raters watch full 60 s clips (and 120/240 s, or verified segments)?
6. Who hosts the new clips, and where?
7. What is the consent, compensation and review status for a new module?
8. Will each clip get enough repeated ratings, and enough independent scenes,
   for clustered analysis?

## 6. Not in scope

* No change to `human_study/` or its protocol, and no contact with the owner,
  without the user's instruction.
* No change to existing Drive links.
* Human answers do not enter the frozen metrics; they validate them.

# Evaluation and figure status, 2026-11-09

This is a progress snapshot, not a completion claim. Preserve existing scores and videos. The journal requires distinct qualitative examples from the simultaneous Steady-Forcing and SceneTether papers; the cross-paper search is documented in the [figure audit](SNF_PP_TRACK_BALANCE_AND_CROSS_PAPER_AUDIT_2026_11_08.md). A search without a match is not proof of independence.

## Evidence already available

| Track | Available reuse | Important limits |
|---|---|---|
| T2V | Legacy SNF and VBench scores for 22 shared 60 s prompt identifiers; 6 and 4 prompts per method at 120 and 240 s for seven checkpoints. | Prompt sets differ across durations. The legacy masks were inferred from generated motion, and identifiers lack independently verified video hashes. Old 240 s figure examples overlap the simultaneous Steady-Forcing manuscript and are excluded from this paper. |
| I2V | Existing source-fixed SNF, VBench-I2V and custom-input VBench-Long scores for 48 appearance and 41 motion-eligible scenes at 60, 120 and 240 s. | Exposed development scenes and adapted CF++ variants; 120/240 s scores use the final 60 s of separate requested generations. The VBench-Long values are not official leaderboard values. Do not claim independent confirmation or a within-rollout trend. |
| Human study | Existing T2V pairwise responses address background motion and slowing. | The available study does not validate replay, direction, material or plausibility; rater eligibility and protocol need owner clarification. See [study review](SNF_PP_HUMAN_STUDY_PREPARATION_REVIEW_2026_11_05.md). |

The actual descriptive tables, populations and metric caveats are in [existing comparisons](EXISTING_SCORE_COMPARISONS_2026_10_30.md), with linked machine-readable score inventories. Existing values do not establish human alignment or naturalness. VBench-I2V and VBench-Long results are for the inputs and configurations recorded there, not additional independent datasets.

## Current visual coverage

The active draft has an I2V four-pipeline illustration on two public sources, at **5 seconds only**, and a track-by-horizon evidence coverage table. Its interactive I2V comparison is `JOURNAL_TCSVT/interactive/i2v_comparison.html`. There is currently no eligible long-duration T2V or I2V comparison figure; the previous T2V figure was excluded for simultaneous-submission overlap. A single new model render cannot by itself become a comparison. Complete, rights-cleared, overlap-reviewed examples from multiple models are still needed in both tracks.

## Newly completed control record

The previously queued FramePack-style freeze check has produced [its report](../manifest/realism_dev_2026_11_05/geometry_v2_fp_freeze_2026_11_08.json). In its `native/freeze` group, the second-version directional outputs abstain on all 21 attempted directional cases (6 channel, 5 down, 10 up), while the prior version emits one result in each group. This supports the freeze gate on these controls; it does not establish sensitivity, natural-motion validity or generalization. The corresponding pass-through has eligible outputs, and each group's eligibility must accompany further analysis. The candidate metrics are not frozen.

## New work and remaining gates

* The first 240 s CausVid common-wrapper run for `cf01` failed with `UnboundLocalError` before producing a video. The failed record is retained. A new guarded retry on GPU 2 uses a workspace-only copy of `causal_model.py` with its shadowing local `os` import removed; hashes of the original and patched files are recorded in the retry `RUN.json`. This is an adapted development run, not a native-pipeline benchmark or completed multi-model figure. Check `240s_retry1/RUN.final.json` and the video before claiming success.
* The prespecified `cb01` T2V scene is queued on GPU 2 after `cf01` reports success and GPU and disk guards pass. A failed first run stops the chain. This creates two scene examples for one adapted method, not a multi-model comparison.
* A second guarded worker prepares a 60 s SVI 2.0 Pro pilot on the exposed `vb161950` public source. It hashes model inputs, then waits for GPU 3 and the disk guards. The long-video wrapper is read-only from the method project and uses its documented per-clip seed deviation. Output, checkpoints, logs and provenance use a new directory. A pilot is not independent validation or a 120/240 s comparison. Inspect `i2v/svi_pro/vb161950/60s/RUN.final.json` before claiming success.
* For each track, obtain multiple methods on the same non-overlapping, rights-cleared inputs. Record realized duration, frame rate, hashes, checkpoints, wrapper, seeds and the exact times displayed. For a trajectory, extract 60/120/240 s prefixes of the same 240 s rollout; for separate endpoint runs, label them as such. Do not treat short outputs as long videos.
* Match existing and new scores by exact input and scorer identity, and score only genuinely missing combinations. Report SNF and relevant VBench dimensions side by side with sample counts and uncertainty, without pooling incompatible masks or claiming official leaderboard comparability. Add VBench-Long on appropriately documented inputs; apply image-conditioned dimensions only to I2V.
* Complete independent region/direction annotations, real-footage controls and the planned blinded human study. The study owner must resolve the active instrument, consent and rater eligibility before collecting ratings. Analyze agreement and metric association per construct on held-out units with uncertainty; abstentions and exclusions must be disclosed. No existing human record validates all realism checks.
* Only then populate separate T2V and I2V qualitative and quantitative figures/tables for 60, 120 and 240 s. Keep development and confirmation, native and adapted pipelines, and historical and new metric definitions visibly separate.

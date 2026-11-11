# Matched-horizon renders and scores for both tracks (queue started 2026-11-10)

This queue is intended to produce development comparisons at nominal 60, 120 and 240 s for both tracks. A bounded screen found no overlaps with the simultaneous Steady-Forcing and SceneTether submissions; it cannot rule out visual or semantic near-duplicates. The later [queue audit](SNF_PP_QUEUE_AND_ROLE_MAP_REVIEW_2026_11_10.md) records role-map holds, dependencies, contention and the CF++ endpoint discrepancy.

## Design

- **One nominal 240 s rollout per (method, input):** 60, 120 and the last available frame near 240 s are prefixes of the same rollout. CF++ is configured for a last timestamp of 239.75 s; verify actual lengths for each finished file. Changing SNF mask support and windows across prefixes limits interpretation of the resulting curve.
  - The existing 120/240 s records come from separate endpoint generations with different T2V prompts, so they are never pooled with these.
  - Prefixes are lossless cuts (libx264 `-qp 0`) of the first 16·H + 1 frames, verified frame by frame by framemd5. The 240 s horizon is the original file.
- **T2V inputs:** the first prompt of each of the nine v2 categories (`manifest/prompts_v2.json`): cf01, fp01, ow01, al01, bp01, cb01, wb01, gt01, fw01. The first-per-category rule was fixed before any render, so no cherry-picking.
  - On 2026-11-10 all 96 v2 settings were screened against the Steady-Forcing, SceneTether/AIA and Region-Forcing trees: text files plus 354,092 image and video filenames. There were no hits.
- **T2V methods:** the eight published checkpoints of the historical panel: Steady-Forcing (released `steady_forcing_t2v.pt`), CausVid, Self-Forcing, LongLive, Rolling-Forcing, Infinite-Forcing, Reward-Forcing and Causal-Forcing. Seed 0.
  - **Disclosed setting:** every checkpoint runs through the historical common wrapper, Steady-Forcing's `inference.py` with `steady_forcing_infer.yaml` (EMA sink 3 + local attention 18).
  - This is how the WACV-era panel was produced. It is **not** each method's released native long rollout, and it lends every baseline Steady-Forcing's long-video mechanism.
  - Whether the journal should replace it with native long rollouts where they exist (LongLive, Rolling-Forcing, Self-Forcing) is an open decision for the author.
- **I2V inputs:** the 12 licence-cleared public sources (`manifest/public_figure_set_2026_11_05.json`; Physics-IQ CC BY 4.0, VBench-I2V Pexels items).
- **I2V systems:** SceneTether (the locked paper configuration), the CF++ checkpoint with Steady-Forcing-derived adaptation (labelled adapted), and the CausVid and Self-Forcing I2V wrappers (adapted).
  - Native 5 s references are already rendered: Causal-Forcing, LTX-Video, Wan2.1 and Wan2.2.
  - SVI 2.0 Pro (about 11.6 h per 240 s clip) and Helios (240 s untested) are pilots only.
- **Scores per horizon:**
  - frozen SNF v1.1 (`scripts/metric_worker.py --spec 1.1`; T2V automatic masks; I2V role maps produced automatically by CLIPSeg, unreviewed);
  - VBench-Long with the incumbent protocol (fd18b3d, dev_flag dinov2/dreamsim);
  - for I2V, VBench-I2V subject/background on the 60 s window ending at each horizon.
  - Window policy `prefix` is recorded in every record, so the pooling gate keeps these apart from whole-file records.

## Queue

- `scripts/journal_queue.py` runs one worker per GPU (2, 3), started detached.
- Jobs live in `manifest/journal_queue_2026_11_10/jobs.jsonl`. The worker re-reads the file before every pick, so jobs can be appended live.
- Scoring jobs sit first in the file and depend on their render, so each finished render is scored before the next render starts.
- **Guards before every job:**
  - no compute process on that GPU at two checks 60 s apart;
  - at least 110 GB free on `/` and `/data1`;
  - no `STOP` or `STOP_gpu<N>` file in the queue directory.
- **Claims:** each job is claimed atomically under `claims/`, and a failed job is not retried automatically.
  - A job that refuses before writing anything (GPU taken at launch) is released.
  - A worker stops after two consecutive failures.
- **To pause:** `touch manifest/journal_queue_2026_11_10/STOP` takes effect at the next job boundary; a running job is never killed.

| stage | jobs | approx. cost |
|---|---|---|
| T2V renders | 72 (2 reused: CausVid cf01/cb01 from 2026-11-09, same wrapper, config, seed and patch) | ~15 min each, ~17.5 GPU-h |
| T2V SNF (3 horizons) | 72 | ~3–4 min each incl. prefix cuts |
| T2V VBench-Long | 72 (being added) | to be estimated |
| I2V renders + scores | 48 renders (4 systems × 12) (being added) | ~8–22 min each |

Renders are under `videos/journal_matched_2026_11_10/`, scores under `raw_matched_2026_11_10/`, and logs and claims under `manifest/journal_queue_2026_11_10/`.

## What this does and does not give the paper

- **It gives:** separate T2V and I2V tables and figures at 60/120/240 s on identical inputs per track, with per-scene values for uncertainty. It also gives new, non-overlapping qualitative examples for both tracks.
- **It does not give** human validation of the new candidate checks: direction, replay, material and plausibility. The existing human study covers only T2V background motion and slowing. The cross-paper screen found no match, which is not proof of independence for crops or semantic near-duplicates.

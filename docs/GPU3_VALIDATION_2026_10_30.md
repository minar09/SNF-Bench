# GPU 3 validation and recurrence pilot — 2026-10-30

## Purpose and scope

The GPU study checks whether SNF-Bench's `sourcefixed-1.0` port reproduces
existing SceneTether source-fixed 60-second scores on the **same bytes**. It
is a software parity check, not an independent evaluation of fBD, naturalness,
source masks, registration, long-horizon behavior, or human alignment. The
input videos are generated clips from one CF++ baseline cell, one seed, and
one horizon; they are not a model comparison.

The GPU runner checkpoints results atomically after every clip and preserves the
previous score alongside the rescore. It checks hashes for video, source image,
role map and upstream scorer before scoring; it checks numerical leaves at
`rtol=0.001, atol=0.000001`, required values and abstention flags. The same
record also stores the registration summaries and score identities. Existing
records and previous parity artifacts are not overwritten. If interrupted,
completed rows remain available; start a separate run with a new output path
and only the remaining scene IDs after investigating the interruption. No
automatic GPU retry is performed.

Command (physical GPU 3 only):

```sh
CUDA_VISIBLE_DEVICES=3 OMP_NUM_THREADS=8 /home/minar/miniconda3/envs/snfeval/bin/python -u scripts/run_sourceref_gpu_parity.py --gpu 3 --cell cfpp/echo_nfpb1_default_lr/seed42 --scenes ial01,icf04,ifp05,icb04,iow02,ifw03,ibp03,igt02,iwb03 --output manifest/sourceref_gpu_parity_2026_10_30.json
```

GPU execution checks stop/pause flags and available memory before each clip.
The manifest is the authoritative progress and score record. Automatic source
role maps are not independent human ground truth. Historical `dE_static_src`
retains the documented float32 accumulation error in `sourcefixed-1.0`; parity
does not establish the correctness of its absolute value. See
[V2 metric worklog](V2_METRIC_WORKLOG.md).

## GPU parity result

**PASS: 9/9 scenes**, with all **547/547 common numeric leaves exactly equal**
to their stored values; all required score keys, null values and both
abstention flags agree. The numerical tolerance was therefore not needed in
this run. Total per-scene processing time was 270.10 seconds on the A100 80 GB
GPU 3, including model loading in the first scene. The machine-readable
[parity report](../manifest/sourceref_gpu_parity_2026_10_30.json) records the
side-by-side scores, hashes, registration summaries and timings per scene.

| Scene | Regime | Previous and rescored fBD_src | Comparable numeric fields |
|---|---|---:|---:|
| ial01 | accumulating level | 2.93417 | 64 |
| icf04 | channel flow | 0.58772 | 64 |
| ifp05 | falling precipitation | 0.36811 | 51 |
| icb04 | combustion | 0.71603 | 51 |
| iow02 | oscillatory water | 0.32423 | 64 |
| ifw03 | falling water | 2.64668 | 64 |
| ibp03 | buoyant plume | abstains | 61 |
| igt02 | geothermal | 1.47124 | 64 |
| iwb03 | windborne | 1.64679 | 64 |

Motion metrics abstain for `ifp05` and `icb04`; fBD abstains for `ibp03`.
The comparison is against the method project's stored `sourcefixed-1.0`
records, not against all original SNF-Bench v1 scores. The fBD values above
are raw measures, not rankings of natural flow.

The full local CPU test suite passed **111 tests**; the tests specifically for
this turn's comparison and control construction passed 4/4. `git diff --check`
also passed.

## Exploratory recurrence controls

[scripts/pilot_recurrence_controls.py](../scripts/pilot_recurrence_controls.py)
scores six existing generated-video windows, 12 seconds sampled at 4 Hz, using
`cand-recurrence-0` (minimum lag 2 s, 1 s run). For each scene, it keeps the
original support pixels and replaces the dynamic-role pixels with either a
3-second exact loop or a frozen first frame. It uses the source-fixed role map,
checks video and mask hashes against the existing score records, and saves
scores and settings per scene in
[recurrence_controls_pilot_2026_10_30.json](../manifest/recurrence_controls_pilot_2026_10_30.json).
`PASS` in that file means the computation completed; it is not metric admission.
The 4 Hz short-window pilot differs from the candidate's default 8 Hz and is
not directly comparable with its codec-floor study.

| Scene | Regime | Original window | Exact loop | Freeze |
|---|---|---:|---:|---:|
| icf04 | channel flow | 0.99548 | ~1.00000 | ~1.00000 |
| iow02 | oscillatory water | 0.98740 | ~1.00000 | ~1.00000 |
| ifw03 | falling water | 0.99661 | ~1.00000 | ~1.00000 |
| ibp03 | buoyant plume | 0.96405 | ~1.00000 | ~1.00000 |
| iwb03 | windborne | 0.98853 | ~1.00000 | ~1.00000 |
| icb04 | combustion | abstains | abstains | abstains |

All five nonempty masks recovered the imposed 3-second loop lag. Frozen frames
also score approximately 1, as expected; some scores slightly exceed 1 because
of floating-point arithmetic. The unaltered windows already have high scores,
and two exceed 0.99. These windows could themselves contain generated
repetition or freeze, so they do **not** establish false positives or
natural-video specificity. The combustion mask has no dynamic-labeled
pixels, so the candidate abstains on all three variants. In particular, these
results do not justify a universal threshold, a recurrence leaderboard, or an
interpretation of the score as flow naturalness. The high baseline values and
freeze ambiguity motivate paired activity reporting, diverse natural-video
nulls, duration/rate sensitivity and human-labeled loop and periodicity
controls before any metric admission.

Reproduce the pilot on the same local assets with a fresh output path:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/minar/miniconda3/envs/snfeval/bin/python -u scripts/pilot_recurrence_controls.py --output manifest/recurrence_controls_pilot_NEW.json
```

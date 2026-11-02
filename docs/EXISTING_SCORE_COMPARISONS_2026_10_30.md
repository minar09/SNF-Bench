# Existing SNF and VBench results: reuse-first comparison

Snapshot: 2026-10-30. This report reads saved records only; no video was generated or rescored. The [score inventory](../manifest/existing_scores_inventory_2026_10_30.json) indexes 119 source-fixed staging groups (5714 records), 260 VBench summary groups, and 28134 legacy SNF CSV rows. It is a bounded snapshot of the method project's factorial score tree and the legacy CSV, not an exhaustive scan of all disks or proof of release eligibility. Active project jobs may add records after this snapshot.

## I2V: same-source 60-second results

The following means use existing source-fixed SNF, VBench-I2V and VBench-Long results on the same fixed-nature source cohort. Each method is paired to SceneTether with matching source-image and mask hashes, actual per-scene seed, scorer identity, recorded VBench entrypoint, flags, sampling and environment-file hashes, and input-video hashes. Recorded hashes were cross-checked; the video files themselves were not rehashed. For every column below, the included scene IDs are identical across all rows. The VBench suites are evaluations on the same inputs, not independent datasets. Ports are CF++ adaptations, not their authors’ native model pipelines.

| Method | SNF source PSNR (dB), n=48 | SNF late MCFF, n=41 | I2V subject, n=48 | I2V background, n=48 | Long background, n=48 | Long dynamic degree, n=48 |
|---|---:|---:|---:|---:|---:|---:|
| Framewise Echo k=1 | 17.208 | 1.005 | 0.981 | 0.971 | 0.968 | 0.219 |
| Spatial Echo k=3 | 16.895 | 0.492 | 0.970 | 0.961 | 0.967 | 0.050 |
| Static sink k=3 | 17.069 | 0.676 | 0.969 | 0.962 | 0.966 | 0.082 |
| Age-decay read | 18.108 | 1.140 | 0.952 | 0.948 | 0.959 | 0.154 |
| ALG-inspired port | 16.048 | 1.049 | 0.977 | 0.969 | 0.965 | 0.249 |
| DyMoS port | 17.080 | 0.959 | 0.979 | 0.969 | 0.967 | 0.228 |
| UnStep port | 16.421 | 0.539 | 0.966 | 0.960 | 0.962 | 0.065 |
| PackCache-style | 16.602 | 1.187 | 0.963 | 0.956 | 0.962 | 0.249 |
| FramePack-style | 14.676 | 1.931 | 0.979 | 0.969 | 0.965 | 0.394 |
| TetherCache port | 14.641 | 1.302 | 0.978 | 0.969 | 0.967 | 0.276 |
| SceneTether (author method) | 22.064 | 1.930 | 0.979 | 0.969 | 0.970 | 0.366 |

The 41-scene MCFF subset excludes motion-abstaining cases. fBD is omitted from this overview because paired eligibility differs across comparisons; the full [panel record](../manifest/existing_snf_vbench_panel_60s_2026_10_30_v2.json) contains fBD and per-scene scores with counts. VBench-Long here uses the saved custom-input/dev configuration and its own clip aggregation; numbers should not be labeled official leaderboard scores. Dynamic degree and MCFF measure activity-related signals, not whether motion is physically correct. Historical `dE_static_src` is omitted because of the documented float32 accumulation defect. These are exposed development sources; paired descriptive means are not evidence of statistical significance or human-aligned naturalness. Stored SceneTether-paper summary tables may use different estimator paths or populations; do not mix cells without a separate provenance audit.

## Existing 120/240-second endpoint windows

These rows score the final 60-second window of separately requested 120- and 240-second generations. They are not prefixes of one common rollout and must not be interpreted as within-rollout accumulation. For each endpoint, the two rows below use identical paired scenes per metric. The [horizon panel](../manifest/existing_snf_vbench_horizons_2026_10_30_v2.json) contains nine matched configurations per endpoint and records the missing TetherCache VBench-I2V provenance explicitly.

| Endpoint / method | SNF source PSNR (dB), n=48 | SNF late MCFF, n=41 | I2V subject, n=48 | I2V background, n=48 | Long background, n=48 | Long dynamic degree, n=48 |
|---|---:|---:|---:|---:|---:|---:|
| 120 s / Framewise Echo k=1 | 17.243 | 0.761 | 0.914 | 0.916 | 0.967 | 0.218 |
| 120 s / SceneTether | 22.090 | 2.053 | 0.954 | 0.947 | 0.970 | 0.360 |
| 240 s / Framewise Echo k=1 | 17.200 | 0.823 | 0.892 | 0.900 | 0.965 | 0.200 |
| 240 s / SceneTether | 22.111 | 1.867 | 0.953 | 0.948 | 0.971 | 0.344 |

VBench-Long here operates on the extracted 60-second endpoint window, not the entire 120- or 240-second video. The scoring window, codec and sampling remain part of each metric definition.

## Historical T2V: shared legacy prompt identifiers

The following means come from the existing legacy per-video CSV and use the intersection of 22 unambiguous stored prompt identifiers for each shown metric across all eight models. One duplicate Rolling-Forcing identifier is excluded. Identifiers are truncated strings, not independently verified prompt/video hashes; these are provisional matching results. The author method is shown separately by name. Legacy automatic masks and metric definitions are not comparable in absolute scale to the I2V source-fixed rows.

| Model | SNF fBD_mean | SNF NBF_mean | VBench background | VBench motion smoothness | VBench dynamic degree |
|---|---:|---:|---:|---:|---:|
| CausVid | 8.417 | 9.647 | 0.926 | 0.990 | 0.426 |
| self_forcing | 11.375 | 12.896 | 0.905 | 0.987 | 0.653 |
| infinite_forcing | 8.051 | 3.741 | 0.927 | 0.992 | 0.268 |
| rolling_forcing | 17.456 | 11.532 | 0.919 | 0.986 | 0.486 |
| reward_forcing | 14.768 | 8.666 | 0.906 | 0.986 | 0.439 |
| longlive | 15.842 | 14.337 | 0.907 | 0.984 | 0.607 |
| causal_forcing | 22.390 | 84.194 | 0.877 | 0.971 | 0.910 |
| steady_forcing_bt (author method) | 6.656 | 4.055 | 0.955 | 0.991 | 0.378 |

The [T2V record](../manifest/existing_t2v_matched_60s_2026_10_30.json) includes excluded duplicate rows, prompt IDs and additional scores. These are historical SNF-Bench v1 results; the automatically inferred masks, prompt-set size and prior metric selectivity limitations remain. High scores or motion magnitude alone do not establish natural flow.

## Reuse and future scheduling

Before any generation, check model/adapter and checkpoint, source-image or full prompt, preprocessing, actual seed, requested and realized duration, fps and codec against existing records. Before scoring, additionally check video-content hash, suite/version, weights, metric configuration, mask and time windows. Reuse an exact eligible result; a missing hash or ambiguous legacy identifier requires investigation, not a presumed match or an automatic rerun. Under the current reuse instruction, do not rescore existing videos; score only new model/image/prompt outputs. Preserve prior failures and partial records. The inventory does not authorize a new run merely because an item is absent from this bounded snapshot.

Rebuild the inventory and reports with new output names before a new scheduling decision; avoid overwriting existing snapshots. The executable comparison and inventory scripts are `scripts/compare_existing_snf_vbench.py`, `scripts/compare_existing_panel.py`, `scripts/summarize_existing_t2v.py` and `scripts/inventory_existing_scores.py`. Use `scripts/lookup_existing_video.py --inventory manifest/existing_scores_inventory_2026_10_30.json --video-sha256 <full-lowercase-sha256>` to find indexed evidence before scheduling; it checks whether VBench provenance changed since the snapshot. A hit still requires a matching metric configuration and input policy. The exploratory pair report with suffix `_v2` adds provenance checks to the earlier preliminary pair report.

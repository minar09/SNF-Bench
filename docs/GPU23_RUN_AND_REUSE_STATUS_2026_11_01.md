# GPU 2/3 execution and score reuse snapshot — 2026-11-01

The SNF-Bench++ evaluation is **not finished**. This is a read-only snapshot,
not a new generation or scoring job. At inspection, two existing
SceneTether-project tasks were simultaneously active on the user-authorized
GPUs:

- GPU 2: CF++ one-step framewise Echo 120-second I2V generation, 48-item
  evaluation request. The active process and partial `RUN.json` do not prove
  that 48 outputs or scores have completed.
- GPU 3: VBench-Long temporal-flicker filtering for the TetherCache-style
  240-second endpoint, `long_tf_filter`, unit `b01`; this is a 60-second
  endpoint window, not a score for a complete 240-second clip. A log showed
  69/248 clip evaluations around inspection; this is unit progress, not
  scene-level completed coverage. Other units and metrics may remain pending.

Both processes were identified via the GPU process list. No job was interrupted,
and no new heavy generation was started while they were occupying the GPUs.
Available memory alone does not establish that an actively used GPU is idle.
The Helios container `helios:cuda12.6` was confirmed present and could import
PyTorch, OpenCV and Diffusers with networking disabled; this is a CPU import
check, not a GPU inference smoke test. Host conda environment `helios` did not
contain `torch`; future work must use a verified runtime.

## Newly found existing comparison records

The previous October 30 [comparison report](EXISTING_SCORE_COMPARISONS_2026_10_30.md)
said the TetherCache-style port lacked expected VBench-I2V provenance at 120/240
s **at that snapshot**. Those records now exist. The source-fixed and main
VBench-I2V / VBench-Long score files were read and joined, with the exact
source/mask/seed/video-hash and recorded scorer/protocol checks in
`scripts/compare_existing_snf_vbench.py`. No video was regenerated or scored.
The full per-scene data and input provenance are in
[tethercache_reuse_snapshot_2026_11_01.json](../manifest/tethercache_reuse_snapshot_2026_11_01.json).

The values below are descriptive means for the **final 60-second window of
separately requested endpoints**; `n` is the number of matched scenes. The
TetherCache row is a CF++ adaptation, not official native TetherCache:

| Endpoint | Method | Source PSNR dB, n=48 | Late MCFF, n=41 | I2V background, n=48 | Long dynamic degree, n=48 |
|---|---|---:|---:|---:|---:|
| 120 s | TetherCache-style port | 14.325 | 1.332 | 0.875 | 0.228 |
| 120 s | SceneTether | 22.090 | 2.053 | 0.947 | 0.360 |
| 240 s | TetherCache-style port | 13.637 | 1.041 | 0.818 | 0.251 |
| 240 s | SceneTether | 22.111 | 1.867 | 0.948 | 0.344 |

Neither MCFF nor dynamic degree establishes correct or natural motion. These
are exposed development scenes, not independent confirmation evidence. The
main VBench score summaries used in the table were recorded `complete`, while
the *separate* temporal-flicker filtering task was still active. The old
report remains an unchanged historical snapshot; this snapshot supersedes its
statement about missing TetherCache provenance only.

## New-run preflight

The model project contains a streaming Helios I2V integration and a local
container/image and model shards. A search of 82 Helios-related metadata
files in `/home/minar/ar-image-animation/results` found no occurrence of
source IDs `icf04` or `ifw03` or their exact source-image SHA-256 hashes.
This is a bounded preliminary duplicate check, **not** proof that a matching
result is absent from every project root. Before generation, complete the
all-root identity check, verify actual method and checkpoint/configuration,
choose a frozen input/seed/horizon, ensure disk reserve, check GPU ownership
and availability, then write to a new SNF-Bench workspace path. A new Helios
60 s rollout on either input is not a completed result. Do not rerun existing
videos or existing scores.

The requested experiments, independent annotations and human-rating study
remain incomplete; see [execution protocol](TCSVT_JOURNAL_EXECUTION_PROTOCOL_2026_11_01.md).

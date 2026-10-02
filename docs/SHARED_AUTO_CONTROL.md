# Shared automatic partition control: 60-second I2V pilot

Status: exploratory M1 rescore. The script and stored per-video output are under
`scripts/score_shared_auto_control.py` and `manifest/shared_auto_control/i2v/60s/`.
Run the command below in the `snfeval` environment after the linked videos and
RAFT checkpoint are available:

```bash
python scripts/score_shared_auto_control.py --check-only
python scripts/score_shared_auto_control.py --gpu 4
```

## What is held fixed

For each prompt, the early-window RAFT magnitude map of `self_forcing` is
partitioned by the frozen v1.1 Otsu routine. The resulting PNG is stored once
and reused, without refitting, to score the matching `chunk6` and
`f2s_framewise` 60-second outputs. The anchor model is not scored with its
own mask. Source-to-first-frame alignment is checked from existing audit
records for all three systems. The scorer still computes each scored video's
flow, similarity compensation, and ORB drift normally.

This removes the **scored video's** own early-flow mask from the comparison.
It does not give a model-independent or semantically correct mask: the
partition still depends on one other generator and RAFT. The PNGs are
explicitly marked `reviewed: false`. They must not be passed to the
reviewed-mask manifest path or cited as human labels.

## Comparison contract

`comparison.json` pairs each rescore with the existing v1.1 row for the same
model and filename. Baselines must report `metric_spec_version: 1.1`; the
rescores report `2-mask-pilot`. Raw BFR is compared with raw BFR; tables may
convert both to NBF with the same 8 Hz multiplier. Values under `delta_*` are
shared-mask minus v1.1. There is no cross-model win/loss claim because the
pilot has few prompts and the models do not all share one generation setting.

The fixed category order selects the first lexicographic prompt from
fire/smoke, windborne, river/stream, and precipitation. This is deterministic
and intentionally diverse, but it is **not** a random or representative
sample. Completed records are written atomically; reruns skip them. Each mask
has a SHA-256 hash and each score records the mask hash and anchor video.

## Exit checks before a paper claim

1. Finish the full matched prompt × system panel, including T2V, and report
   failures rather than silently excluding them.
2. Add independent, future-blind, human-reviewed source masks for I2V and a
   reviewed T2V subset; quantify agreement with the automatic partition.
3. Compare category-macro paired changes, rank sensitivity, uncertainty, and
   mask coverage. Include both common and native generation settings, clearly
   labeled.
4. Repeat with alternative held-out anchors or leave-one-system-out consensus
   to test dependence on the chosen anchor.
5. Test actual motion semantics and repetition separately; a shared spatial
   partition alone cannot determine correct direction, natural flow, or loops.

## Pilot result

All 8 planned pairs completed without scorer failure on 2026-09-28. Values below
are v1.1 automatic-mask → held-out shared-mask, for exactly the same video.
NBF is shown as `8 × BFR`, matching the 8 Hz table conversion.

| Medium | Scored system | Static fraction | fBD | NBF | FP |
|---|---|---:|---:|---:|---:|
| Fire/smoke | chunk6 | .668 → .692 | .55 → .57 | 3.34 → 3.37 | .62 → .92 |
| Fire/smoke | f2s_framewise | .674 → .692 | 7.15 → 5.89 | 10.68 → 10.69 | .34 → .67 |
| Windborne | chunk6 | .675 → .476 | 19.65 → 10.04 | 6.65 → 7.12 | 1.55 → 1.20 |
| Windborne | f2s_framewise | .488 → .476 | 29.06 → 25.26 | 11.06 → 15.32 | 2.00 → 1.70 |
| River/stream | chunk6 | .566 → .652 | 9.71 → 6.32 | 8.31 → 8.23 | 1.54 → 1.48 |
| River/stream | f2s_framewise | .652 → .652 | .70 → .74 | 3.02 → 3.06 | 1.43 → 1.45 |
| Precipitation | chunk6 | .793 → .573 | 26.19 → 26.84 | 2.53 → 2.52 | .45 → .92 |
| Precipitation | f2s_framewise | .622 → .573 | 13.01 → 10.90 | 3.57 → 3.54 | .55 → .59 |

The largest fBD change is 19.65 → 10.04 on one windborne clip; the largest
NBF change is 11.06 → 15.32 on the other windborne clip. FP changes by as
much as .48. These examples show that the automatic partition can materially
change reported factors, even when the scored video's pixels and flow are
fixed. They do **not** establish which partition is correct, whether the
motion is natural, or whether system rankings are valid. Four handpicked
prompts and two scored systems are a control pilot, not the full M1 exit gate.
`comparison.json` is the machine-readable source, including the other factor
deltas and exact, unrounded values.

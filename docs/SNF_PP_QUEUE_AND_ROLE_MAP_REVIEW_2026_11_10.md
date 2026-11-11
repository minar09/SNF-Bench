# Queue audit and role-map review — 2026-11-10

This audit is of development runs. It does not certify semantic masks or human alignment.

## Changes to the live job list

The 48 I2V source-fixed SNF jobs now depend on an unfulfilled `gate/i2v_role_map_review_2026_11_10`. The automatic maps have visible semantic errors, so spending GPU time on them would create scores that would need replacement. Rendering is unaffected. The 96 I2V VBench jobs no longer depend on SNF; VBench-I2V depends on its render and VBench-Long follows VBench-I2V so their shared prefix files are not created concurrently. T2V jobs and I2V smoke gates are unchanged. The unmodified job list and intermediate list are preserved beside `jobs.jsonl` under `jobs.before_*`.

The gate is deliberately not an instruction to create a marker by itself. Before releasing it: make a new version of the masks, independently review and adjudicate them, update the scorer to read that version and record its hashes and review scope, audit abstentions, then explicitly record the approved version and protocol in the marker. Never overwrite `masks/public_role_maps_2026_11_10/` or its provenance. Render/VBench completion does not imply role-map validity.

## Source-map triage

The full automatically generated contact sheet is `.metric_staging/i2v_matched_2026_11_10/role_maps_sheet.png`; consult it together with full-resolution source images, label layers and the exact task definition. It is a triage view, not an annotation or independent review.

* `vb1236906` (Iguazu): substantial foliage and sky are labelled as the moving material, while some waterfall regions are omitted. Redraw moving water and static land separately; treat ambiguous mist/boundaries as ignore.
* `vb10462563` (kettle): moving-material and overlay regions extend into the kettle, wood and background; the small flame needs close review. Do not infer moving flame from an apparently orange object without resolving uncertainty.
* `pq0140` (smouldering paper): most of the support is ignored or overlay and the moving region is a small uncertain fragment. Smoke is translucent; use an uncertainty region and assess whether a source-only mask can capture the target at all.
* `pq0092`, `pq0065`, `pq0089` and `vb2385898` have automatic motion-region abstentions. An absence of a usable region is not a score of zero. In particular, precipitation is excluded under the current task protocol; don't silently convert the snow scene into a validated moving-material score.
* Several other scenes have small support regions or boundaries mixing sky, spray, buildings and water. Review **all 12**, not only the three initially named, with the same protocol. Some scenes may remain out of scope or abstain.

The existing design calls for two independent annotators and adjudication. Their identities and the study owner cannot be invented from repository evidence. A new material/subject layer and independently labelled direction also need their own versioning; this review does not claim either is complete.

## Baseline decision and exact horizon

Keep the common-wrapper panel as an explicitly adapted, controlled comparison. Add released **native long-video settings** as a separate, equally prominent panel where an actual native mode, usable checkpoint and matching input exist. These results answer different questions; do not label common-wrapper checkpoints as native or combine them as interchangeable rows. First verify code revision, configuration, checkpoint/LoRA, temporal length, seed, pretrained components and resource needs; smoke-test one matched prompt before appending a full batch. The local LongLive checkout documents an infinite-attention configuration and the local Self-Forcing checkout documents its own CLI, but their runnable 240 s configurations, weights and environment have not yet been verified for this panel. Rolling-Forcing's checkpoint was located; its exact native checkout/configuration still needs checking. Reuse exact existing results rather than rerendering.

The CF++ I2V wrapper is configured for 3,837 frames at 16 fps: its first-to-last timestamp is **239.75 s**, not exactly 240 s. Other listed systems expect 3,841 frames. The code records this and VBench-I2V clamps its last 60 s window to the actual end; consequently these are near-240 s endpoints with a 0.25 s mismatch, not identical frame endpoints. Report actual lengths and window boundaries; if exact matched endpoints are required, render enough frames under a separately identified corrected protocol and verify the prefix without overwriting the original. Other systems must be checked from their actual completed sidecars, not assumed to match their configuration.

T2V SNF v1.1 also rebuilds an early-flow-derived mask for each scored prefix and uses a window proportional to prefix length. A horizon curve therefore changes measurement support and temporal windows as well as generation length; it is descriptive and is not a controlled estimate of accumulation with fixed measurement support.

## Runtime status and contention

The 408 original jobs include three-horizon bundles, not 408 independent single-horizon operations. Do not treat the original 2–3 day estimate as verified: the first T2V SNF bundle was still running more than seven minutes after starting, versus the quoted 3–4 minutes. Measure completed jobs before re-estimating.

At the audit, three unrelated processes joined GPU 2 after the worker's idle checks while the first SNF bundle was running. No unrelated process was stopped. The queue's two checks only establish pre-launch idleness and cannot reserve a GPU or prevent a later tenant from starting; record contention and do not use this run as an uncontended timing measurement. GPU 3 completed its first new render and started scoring. Check `worker_gpu*.log`, claim results and each `RUN.final.json`/`SCORE.json` for current status rather than relying on this snapshot.

# M2 endpoint motion-probe pilot

Status: exploratory code-path and asset-coverage result, 2026-09-28. This is
not a benchmark result and does not admit a new public metric.

## Purpose

The first M2 step reuses the persisted RAFT correspondences from SNF-Bench
v1.1 before requesting a full dense-flow rescore. It asks three practical
questions:

1. Can rigid-support motion and residual intended-region motion be emitted as
   timestamped signals for the v2 trajectory protocol?
2. Does the existing cache cover enough of a long video to support trajectory
   claims?
3. Can signed direction be added without inventing a screen-space label from
   prompt prose?

The implementation is `scripts/flow_endpoint_probes.py`. The reproducible
eight-clip run is `scripts/run_flow_endpoint_pilot.py`, and the stored record is
`manifest/m2_endpoint_pilot.json`.

## Estimator

For each cached transition, a robust partial-affine transform is fit from
support-region correspondences `(x, y) -> (x + u, y + v)`. The support signal
is the median magnitude of the fitted transform's displacement over those
points. This measures adjacent-frame coherent support motion; it is not a
first-to-later-frame registration error. The dynamic signal subtracts the
fitted support transform from intended-region flow and reports the median
residual magnitude in pixels per second.

When a reviewed image-plane path exists, the same residual vectors can be
projected on its unit direction. Reversing only those vectors flips signed
transport while preserving motion magnitude, and alternating their sign
produces nonzero motion with zero net directional persistence in the controlled
tests. No legacy prompt is scored for direction merely because its text says
"downstream", "toward", or "upward".

## Asset audit

The cache contains 1,342 files in total but only 336 belong to registered
public systems. Those 336 cover 24 model-duration cells, all in the I2V track.
There are no cached fields for the seven public T2V systems.

Every cache stores only the early and late windows used by v1.1. A nominal
60-second clip has 480 sampled transitions; the common cache retains 114
(23.75%). After requiring each five-second result to span at least 80% of its
window, only the first and last windows are admitted: 2/12 windows (16.7%).
The middle ten windows remain explicitly unscorable.

This audit found and fixed a protocol bug. Version 0.1 accepted a window based
only on sample count, so two seconds of endpoint observations could stand in
for a five-second window. `snf-long-trajectory-0.2` adds
`min_time_span_fraction`, stores the observed span, and labels incomplete
windows `insufficient_temporal_span`.

## Paired pilot

The pilot uses four existing I2V-60s scenes across two public systems:
Causal-Forcing++ (2-step) and its native two-step frame-wise configuration.
The four media are precipitation, fire/smoke, river/stream, and windborne.
The partitions are automatic, model-specific, and unreviewed.

| system key | v1.1 fBD median | v1.1 FP median | support early p95 px | support late p95 px | dynamic early median px/s | dynamic late median px/s |
|---|---:|---:|---:|---:|---:|---:|
| `chunk6` | 14.676 | 1.079 | 0.756 | 0.384 | 2.501 | 1.131 |
| `f2s_framewise` | 10.077 | 0.993 | 0.656 | 0.355 | 4.975 | 1.145 |

These columns are side-by-side provenance, not replacement deltas. v1.1 uses
clip-level endpoint means and its frozen factor definitions; M2 uses robust
per-transition summaries inside fixed five-second windows, and dynamic speed is
scaled to pixels per second. With four scenes, no system rank, correlation, or
validity conclusion is warranted.

The per-scene values expose a useful disagreement to investigate. On the
windborne scene, v1.1 FP is 1.55 for `chunk6` and 2.00 for `f2s_framewise`, but
M2 median dynamic speed falls from 9.41 to 1.44 px/s and from 4.85 to 1.22 px/s,
respectively. This may reflect mean-versus-median sensitivity, the v1.1 ratio,
or mask/backbone behavior. A reviewed partition and human motion judgment are
needed before choosing an estimator.

## Direction annotation gate

`manifest/transport_annotation_pilot.json` records a draft review of the same
four source scenes. Only the winter river has a plausible single image-plane
path: from the central vanishing point toward the lower foreground. Campfire is
turbulent, the puddle combines falling drops with radial ripples, and the dust
storm approaches mainly in depth, so all three are marked not applicable to a
single path rule.

`scripts/validate_transport_annotations.py` checks source hashes and geometry,
normalized paths, nondegenerate ROIs, reason codes, and review state. The draft
passes structural validation with four warnings and fails `--strict-release`
with four errors because no named human has reviewed it. Therefore the stored
endpoint pilot abstains on direction, incoming flux, recurrence, and reset
continuity.

## What this closes and what remains

This step closes the probe mathematics, corruption behavior for reversal and
ping-pong vector fields, public cache inventory, endpoint trajectory adapter,
and annotation review gate. It does not close the M2 exit criteria.

The next practical order is:

1. obtain named human review of the four draft direction decisions and a
   reviewed role mask for the river;
2. add low-rate full-clip RGB screening for exact recurrence and reset seams;
3. construct pixel-level foreground reversal, ping-pong, exact-loop, and reset
   controls from pristine parents;
4. use screening timestamps to request dense flow only around early, middle,
   late, and suspected-failure windows;
5. evaluate real fixed-camera controls and a second motion backbone before
   setting any threshold or promoting a probe.

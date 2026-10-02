# fBD match-support reliability pilot

Status: M1 pilot on the 12 T2V-60s clips used by the frozen perturbation
sweep. Run with:

```bash
python scripts/audit_fbd_reliability.py --check-only
python scripts/audit_fbd_reliability.py --gpu 4
```

## Why this audit exists

The v1.1 scorer stores fBD or `null`, but it does not store the evidence behind
the value. A non-null number only proves that at least one late frame supplied
12 cross-check matches. It does not reveal how many late frames were usable,
how many homographies had enough inliers, or how often the scorer fell back to
the unfiltered raw matches.

`scripts/audit_fbd_reliability.py` rebuilds the exact early RAFT/Otsu mask,
then reproduces the frozen ORB path while recording base and late keypoints,
cross-check matches, RANSAC inliers, skipped frames, fallback frames, and each
frame's median displacement. Per-clip traces are stored under
`manifest/fbd_reliability_pilot/`; the compact summary is
`manifest/fbd_reliability_pilot.json`.

## Result

The reproduction check passes on all 12 clips. The maximum absolute difference
from the stored v1.1 fBD is `8.95e-7` percentage points.

| Check | Pilot result |
|---|---:|
| Clips | 12 |
| Scene media | 5 |
| fBD abstentions | 0 |
| Usable late frames | 684 / 684 |
| Median cross-check matches per clip | 285.5 |
| Minimum frame-0 static-region keypoints | 352 |
| Frames using raw-match fallback | 37 / 684 (5.4%) |
| Clips using fallback at least once | 2 / 12 |
| Largest within-clip fallback fraction | 25 / 57 (43.9%) |

The two fallback cases are one river/stream clip (12/57 frames) and the sole
ocean-wave clip (25/57). Their fallback frames have 75–278 cross-check matches,
but only 6–7 RANSAC inliers; the frozen scorer therefore uses all raw matches
for those frames. This is not abstention, and it should not be presented as
robust geometric support.

## Consequence for the benchmark

The pilot rules out silent late-frame skipping for these 12 clips, including
fire/smoke and precipitation examples. It also shows that fBD's raw-match
fallback is common enough to expose in every future record. A release record
should include usable-frame fraction, match and inlier counts, and fallback
fraction beside fBD. A minimum-support admission threshold must be frozen using
the larger public-model panel and hard real-camera controls; this pilot is too
small and has only one ocean and one windborne clip.

This result does not establish ORB-backbone robustness, reviewed-mask validity,
or full-dataset coverage. Those remain separate M1 gates.

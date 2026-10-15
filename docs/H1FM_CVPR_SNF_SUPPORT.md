# SNF-Bench support for the H1-FM CVPR 2027 submission

2026-10-15. For the method team. Records what the benchmark side has checked
for the H1-FM paper and its "SNF-Bench v2" contribution, where the three
advisories (received 15 Oct) agree or conflict with SNF-Bench's own evidence,
and what this project can deliver before the 28 Oct experiment freeze. All
checks below are CPU-only and read-only on method-project data.

---

## 1. Checks run today

### 1.1 The colour claims survive the float32 defect

`dE_static` (stored as "static colour error ΔE" in doc 119) accumulates
support-region Lab means in float32. With ~300k support pixels × 24 late
frames, the sum outgrows float32 precision; on a static control clip it reads
6.84 where the true shift is 1.35 (`V2_METRIC_WORKLOG.md`). It was inherited
from SNF-Bench's own v1 extras.

Recomputed for H1-FM against all three references
(`scripts/audit_de_pairs.py` → `manifest/de_pairs_audit.json`; both seeds
pooled per scene, precipitation excluded, n = 42). The float32 rerun
reproduces every stored value exactly (0 mismatches) and the advisories'
numbers to the digit:

| H1-FM vs | float32 (as reported) | float64 |
|---|---|---|
| spatial Echo k = 3 | −5.54 [−8.66, −2.63] | **−5.49** [−8.57, −2.59] |
| plain Echo k = 1 | −4.57 [−7.80, −1.43] | **−4.82** [−8.00, −1.73] |
| static sink k = 3 | −3.32 [−6.12, −0.55] | **−3.38** [−6.18, −0.65] |

**No colour conclusion changes.** For the paper: recompute in float64 and say
so in a footnote, because a reviewer who reruns the code on static content will
find the floor.

### 1.2 What the colour measure can and cannot mean

`dE_static` is the distance between the support region's *mean* colour and the
source's, in OpenCV 8-bit Lab. It is not a perceptual or pixelwise colour
difference. In particular, it is blind to content that is redrawn with the
right average colour: an equal-mean texture swap scores ~0
(`tests/test_candidates.py`). "Lower colour error with lower source PSNR"
therefore has two readings: colour is genuinely held, or pixels changed while
the region mean did not. Do not describe it as a perceptual colour improvement
until §1.3 says which.

### 1.3 Pixelwise CIEDE2000 on the same videos

*(pending — see §5)*

### 1.4 The fresh split is independent

`scripts/audit_fresh_split.py` → `manifest/fresh_split_audit.json`. Each of the
24 fresh sources was compared with the 48 v2 test sources (crops and originals)
and every training, development, held-out, v1-evaluation and supplementary
image (1,296 in all), by exact hash, perceptual hash and geometric
verification. **24/24 unseen.**

That candidate pool holds several photographs of single physical scenes (e.g.
one town weir from different positions). Perceptual nearest-neighbour checks
can miss those, so fresh × test was also matched exhaustively (24 × 96 image
pairs, ORB + RANSAC). The strongest match is 17 inliers, between unrelated
scenes in different categories; the same-scene threshold is 40. No leakage.

Licence: 3 fresh sources come from Wikimedia Commons with recorded licences;
**21 come from the upload pool, which has none.**

## 2. Facts the paper must state correctly

| item | SNF-Bench record | consequence |
|---|---|---|
| **Test split** | `manifest/v2_splits.json`: **41 test + 7 seen-overlap**. The 7 (`ifp01–04`, `iow01`, `iwb03–04`) are reused v1 evaluation images, matched byte-for-byte; the v1 set was the development set for earlier Echo-family work. | Doc 119 calls all 48 "unseen test scenes". Report the 41-source result as primary, or at least as a sensitivity row, and drop "unseen" for the 48. |
| **240 s subset** | Two frozen subsets exist: SNF-Bench's 9 (Oct 2) and the method project's 12 (Oct 14; seeded random, frozen with 0 videos generated). | Adopt the 12 as canonical, since it is what will be rendered, and retire the 9; two frozen subsets invite a "chosen after the fact" question. 2 of the 12 (`ifp04`, `iwb03`) are seen-overlap and 2 (`ifp04`, `ifp06`) are precipitation, which abstains on most endpoints. |
| **Masks** | 48 test masks: AI review plus project-lead checks. 24 fresh masks: AI review, lead check pending. | Never "human-verified". Advisory 3's "72 human-verified masks" is wrong. |
| **Measure names** | "colour error" = region-mean 8-bit-Lab distance; "activity" = late compensated flow, not naturalness; "events" = spike-and-return detections, natural and artefactual alike | Name them for what they measure. |
| **Eligibility** | Appearance 42/48, fBD 45/48, flow 40/48; paired populations smaller (e.g. 32 for flow vs spatial Echo) | Publish counts after eligibility beside every contrast. |

## 3. Reading the three advisories

Advisories 1 and 2 are consistent with SNF-Bench's evidence. Advisory 3
overclaims in four places that matter for the benchmark contribution:

* **"Fully resolved" for circularity, scale and overlays.** Source-fixed masks
  remove the dependence on each output. But abstention is not measurement:
  precipitation is excluded, not scored. Looping and human alignment are open.
* **"72 human-verified masks"** — see §2.
* **"120 s/240 s extend the exact same pairs"** — the cohort design is right,
  but nothing at 120 s or 240 s has been generated.
* **"Proves"** for the mechanism controls — the intervals support placement and
  "this alternative is worse"; use interval language.

Advisory 2 calls the colour measure "a perceptual color distance". It is not;
see §1.2.

On WorldScore, advisories 1 and 2 match SNF-Bench's earlier verification of the
released code: SAM2 masks propagated from the input frame, maximum flow inside
minus outside. Source-anchored regional motion is prior art.

## 4. What SNF-Bench can deliver by the 28 Oct freeze

Both advisories make v2's contribution bullet conditional on (a) human
alignment beyond H1-FM and (b) a repetition axis. SNF-Bench can carry its share
of both without GPU time:

| deliverable | for | status | needs from the method team |
|---|---|---|---|
| **Recurrence diagnostic, validated**: exact, cross-faded and ping-pong loops; freeze; hard negatives from real periodic surf and foliage | (b) | kernel and synthetic tests exist (`snf_candidates.recurrence`); codec floors measured | a few real periodic clips (real footage preferred), or approval to use test-split outputs as hard negatives |
| **Metric–human concordance analysis**: per pair, sign of each metric difference vs the matching question's majority; source-clustered intervals; per-question α | (a) | not built; ~1 day | the trial file and response format of human study v2.0 |
| **Eligibility-after counts table**, per endpoint × category | §2 | ~hours | none |
| **Pixelwise ΔE00** as an independent colour check | §1.3 | running | none |
| **60 s GPU parity** of the ported source-fixed scorer | port validity | ready; waits for GPU 2/3 to free and STOP/PAUSE flags to clear | GPU window |

## 5. Pixelwise CIEDE2000 result

*(to be filled when `scripts/audit_pixelwise_colour.py` finishes)*

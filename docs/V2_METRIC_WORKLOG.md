# SNF-Bench v2 metric work log

Execution record for the order in `I2V_METRIC_REVIEW_2026_10_08.md` §6.
Newest entries first. Nothing here changes a frozen measurement; each result
names the artifact that holds it.

---

## 2026-10-08 — step 1 (port) and step 2 (CPU floors)

### Step 1: source-referenced scorer ported, parity exact

`scripts/snf_sourceref.py` ports the method project's `sourcefixed-1.0`
scorer. The six scoring functions are copied verbatim by the Python parser
from upstream commit `592747a3e2` (file sha256 `f4782bc6…`), and their body
hashes are pinned. `tests/test_sourceref.py` fails if a copy is edited locally
or if upstream changes, and a deliberate re-port is required either way. Each
record declares the full measurement policy: source reference, mask set and
review scope, 12% windows, sampling rate, registered-only failure handling.
`scripts/measurement.py` therefore refuses to pool these records with v1.1.

**Parity on a real clip, CPU, one process, same RAFT weights**
(`manifest/sourceref_parity.json`, scene `ial01`, 5 s prefix):
46 of 46 output keys identical between port and upstream (|d| = 0), and the
8 v1.1-equivalent keys identical to `snf_metrics_v11.process_video`.

**Full-length GPU parity is prepared but not run.**
`scripts/check_sourceref_records.py` will re-score 9 already-scored 60 s
videos, one per regime and covering every abstention path, and compare them
with the stored records. It waits for ≥ 12 GB free and obeys the method
project's STOP/PAUSE flags. At the time of writing GPU 2 was saturated, and
GPU 3 was at 100% with `STOP_gpu3` and `PAUSE_gpu3` raised, so it has not run.

**Regression found and fixed on the way.** On 2026-09-30 the RAFT cache path
was moved behind `scripts/_paths.py`. The default became `~/.cache/vbench`,
which is empty on this machine, so SNF-Bench's own RAFT entry points (metric
worker, validation suite, v1.1 scorer) would have failed. The method project
sets `VBENCH_CACHE_DIR` itself and was unaffected. The real location is now in
`configs/local_paths.json`, and `vbench_cache()` raises when the checkpoint is
missing instead of creating an empty directory.

### Step 2: candidate kernels and their floors

`scripts/snf_candidates.py` holds four candidates, none admitted: pixelwise
CIEDE2000 on the eroded support, interior-tile detail retention, interior-tile
activity, and multi-frame recurrence. Colour uses an explicit D65 conversion.
CIEDE2000 matches all 35 rows of Sharma, Wu & Dalal's test data to < 1e-4
(`tests/data/ciede2000_sharma.txt`). Synthetic controls in
`tests/test_candidates.py`:

* an equal-mean texture swap is invisible to region-mean colour and clear to
  pixelwise ΔE00;
* glassy smoothing drops detail, while a frozen sharp clip keeps it (so detail
  is read only beside activity);
* an exact loop scores recurrence > 0.99 at the right lag; fresh motion < 0.5.

**Floors** (`manifest/candidate_floors.json`). Each of the 48 sources was
encoded as a 10 s static clip with the generators' own writer, inside the
generation image on CPU: `torchvision.io.write_video(fps=16)`, libx264
defaults, the same stream type as the renders. Nothing moves and nothing drifts:

| measure | median | p95 | reading |
|---|---:|---:|---|
| pixelwise ΔE00, support mean | 1.04 | 1.35 | codec floor ≈ one just-noticeable difference |
| pixelwise ΔE00, support p90 | 2.32 | 3.12 | tail floor |
| mask-edge effect (no erosion − 6 px) | 0.006 | max 0.29 | small; erosion kept |
| detail ratio vs source | 1.00 | 1.20 | encoding can *add* up to 20% high-frequency energy (ringing) |
| activity, grey levels | 0.019 | 0.038 | zero-motion floor; per-frame max 0.29–0.63 at keyframes, so use a robust window statistic |
| recurrence | 1.000 | 1.000 | a frozen region is a perfect loop: only meaningful where activity clears its floor |
| `sourcefixed-1.0` source PSNR | 44.9 dB | 47.2 dB | ceiling, not floor |
| `sourcefixed-1.0` dE_static | 1.43 | 4.53 | **see below** — mostly arithmetic error |

Seven scenes have no interior dynamic tile: all six precipitation scenes
(overlay medium) and `icb04`. This matches the method project's own endpoint
eligibility.

### Defect: float32 accumulation in `dE_static`

`metric_code/snf_extra_metrics.py` (v1 extras, lines 96–99) and the ported
`extras_sourcefixed` average support Lab colour with
`np.stack(...).reshape(-1, 3).mean(0)` on **float32**. With about 300k support
pixels × 24 late frames, the per-channel sum outgrows float32 precision.

On the static `icb04` clip, the late-window a* mean is 130.76 in float32 and
135.53 in float64. `dE_static` reads **6.84 where the true shift is 1.35**:
every frame is shifted by the same 1.35, a small, uniform darkening (ΔL* ≈
−0.5) from the H.264/yuv420p path.

* **The v1 SNF-Bench paper is unaffected:** no table, figure or macro uses
  `dE_static`. The 83 v1 extras records carry the error in that field.
* **`sourcefixed-1.0` keeps the defect deliberately**, because it must reproduce
  upstream. A corrected measure needs a new identity. Pixelwise ΔE00 in
  `snf_candidates.py` is float64 throughout and is not affected.
* **The method project's colour results are measured with it.** The size of
  the effect on their contrasts is the audit below.

**Audit result** (`scripts/audit_de_precision.py`,
`manifest/de_precision_audit_seed{42,1042}.json`). The method project's 60 s
records for Echo and the static sink at k = 1 and k = 3, all 48 scenes, were
recomputed both ways. The float32 recomputation reproduces every stored
`dE_static` exactly (0 mismatches on either seed), so the comparison is
trustworthy.

| | seed 42 | seed 1042 |
|---|---|---|
| per-video |float32 − float64| | median 0.09, p95 1.44, max 3.73 | median 0.11, p95 1.35, max 4.33 |
| D(1) | −3.51 → −3.53 | −4.83 → −5.00 |
| D(3) | +1.22 → +1.17 | +3.68 → +3.55 |
| **Γ(3,1)** | **+4.73 → +4.70** | **+8.51 → +8.56** |

The error is real per video, but it is nearly common to the two arms of a
pair, which share a scene, a support and similar colours, so it cancels in the
contrasts. **The method project's colour-drift interaction stands.** It
matters where values are read absolutely: a per-video error up to ~4 units
exceeds their ±0.5 "tied" margin, and on static or near-static content the
mean-colour distance is dominated by it. Recommendation: any future
mean-colour measure accumulates in float64 under a new identity. Pixelwise
ΔE00 (candidate) is already float64.


### 2026-10-30: full-length GPU parity and recurrence pilot

The planned nine-regime, 60-second `sourcefixed-1.0` GPU port comparison
completed on GPU 3: 9/9 scenes passed, with 547/547 comparable numeric leaves
exactly matching the stored method-project records, including matching nulls
and abstention flags. The report and side-by-side scores are in
[`manifest/sourceref_gpu_parity_2026_10_30.json`](../manifest/sourceref_gpu_parity_2026_10_30.json).
This establishes same-input parity, not validity of the metrics or masks.

An exploratory generated-video recurrence pilot found original-window scores
of 0.964–0.997, exact-loop and freeze scores near 1.0, and an abstention on
the zero-dynamic-pixel combustion mask. The baseline clips are not independently
labeled natural nulls, so these results cannot estimate false-positive rates.
See the [GPU validation report](GPU3_VALIDATION_2026_10_30.md) for settings,
raw result links, limitations, and next validation requirements. All 111
local tests passed.

### 2026-10-30: SceneTether parity and subject-track inventory

On GPU 2, nine additional 60 s SceneTether clips reproduced 549/549 common
numeric fields exactly. A hash-matched, descriptive Echo–SceneTether paired
comparison was stored separately; it is not a naturalness or population
validation. Fourteen VBench-I2V-derived subject images and existing 60 s
clips were inventoried and smoke-tested, but they are exposed development data,
not a held-out benchmark. See [subject extension and model inventory](JOURNAL_SUBJECT_EXTENSION_AND_MODELS_2026_10_30.md)
for results, candidate model readiness and remaining experimental gates.

### 2026-10-30: existing score reuse and comparisons

A read-only inventory indexed 5,714 source-fixed staging records, 260
VBench summary groups and 28,134 historical SNF CSV rows within the specified
roots. No existing video was rescored or regenerated. The
[comparison report](EXISTING_SCORE_COMPARISONS_2026_10_30.md) shows matched
source-fixed, VBench-I2V and VBench-Long 60 s results across eleven CF++-family
configurations, selected 120/240 s endpoint-window comparisons, and separate
historical T2V results. It documents the distinct sample sets, old metric
limitations, and one ambiguous duplicate T2V identifier. Exact input/protocol
identity must be verified before scheduling new work; the inventory is not an
exhaustive all-disk search. A video-hash lookup identifies indexed existing
results without making a reuse decision automatically. The full local suite
passed 117 tests.

### 2026-11-01: GPU occupancy and TetherCache score reuse

The two authorized GPUs were both actively running existing method-project
jobs. Previously missing 120/240 s TetherCache-style endpoint-window score
records were found and imported without generation or rescoring. See the
[GPU and reuse snapshot](GPU23_RUN_AND_REUSE_STATUS_2026_11_01.md) for exact
coverage, values and pending work.

### 2026-11-04: pixelwise colour for SceneTether; first support-realism pilot

* **SceneTether pixelwise colour.** CIEDE2000 on the late window, n = 42
  (`manifest/pixelwise_colour_audit_scenetether.json`). Against all three
  references, the mean and the 90th percentile are lower with intervals
  excluding zero. H1-FM's region-mean advantage does not hold pixelwise (see
  `H1FM_CVPR_SNF_SUPPORT.md` §5).
* **Input hashes.** All 384 records behind both audits match their stored
  video and source hashes. The audit script now enforces this on every run.
* **Support-realism pilot.** On SceneTether vs its source-pixel composite
  (`SNF_PP_REALISM_DESIGN_2026_11_04.md` §5.1):
  * successive-frame support change (renamed from `support_noise`) separates 42/42, but the paste was re-encoded and the original was not, so encoding histories differ; rerun against pass-through re-encodes (`SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md`);
  * edge spill is inverted by codec bleed and is rejected;
  * boundary step separates 13/13 eligible scenes.
  * No real-footage band exists yet, so none of this measures realism.
* 120 tests pass.


### 2026-11-04 (later): control and pilot safeguards; three findings on synthetic data

Following `SNF_PP_REALISM_DECISION_REVIEW_2026_11_04.md`. No existing video
was read; the reuse question in `SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md`
§6 is still open.

* **Builder.** `build_composite_controls.py` never overwrites. It checks each
  output's decoded metadata with PyAV before publishing the file.
* **Pilot.** `pilot_support_realism.py` requires and verifies the full
  parent/source/mask/output hash chain and never overwrites a report. It
  records abstention reasons and the sampling actually used.
* **Bug: mask-edge bias in drift compensation.** Phase correlation on the
  masked support locked onto the fixed mask edge: a textureless support gave a
  0.998 peak at zero shift. Drift on weakly textured supports would have been
  left in, silently. Fixed by mean-subtracting inside the support, plus a
  texture floor and a peak-response floor that abstain.
* **Ignore band explains the 13/41 eligibility.** The v2 role maps keep 3–108
  px (median 7) between support and dynamic. Measuring boundary bands from
  where the support starts (`cand-edge-profile-1`) makes 37/41 scenes
  eligible, checked on the masks alone.
* **Codec erases fine grain.** On a synthetic clip, about 5 grey levels of
  i.i.d. noise came out of default H.264 encoding as zero support change.
* 126 tests pass.


### 2026-11-05: reuse authorized; split frozen; development round 1 (R1, R3, R4)

The user authorized new, versioned candidate statistics and derived controls
on existing videos; originals, scores and frozen identities are untouched.
Full results are in `SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md` §9;
reports are in `manifest/realism_dev_2026_11_05/`; controls (gitignored)
are in `videos/realism_controls_2026_11_05/`.

* **Split frozen before any new statistic.**
  `manifest/realism_dev_split_2026_11_05.json` (`scripts/freeze_realism_split.py`)
  records:
  * all existing scenes and the CF++ family as development;
  * published-panel renders made after the freeze as confirmation;
  * 168 hashed parents;
  * the 2026-11-04 artifacts as exploratory.
* **Matched encoding path, verified bit-exact.** Two of the method project's
  composites were rebuilt and their SHA-256 matched. The new
  `scripts/native_controls.py`:
  * builds pass-throughs of the composites' parents through that path;
  * adopts the 4 × 42 native controls by hash, as links;
  * builds 9 × 42 temporal controls (`scripts/temporal_ops.py`).
* **R1:** support change separates 42/42 only because the generator's support
  changes; boundary step ties on the feathered FramePack composite (0.78
  each); edge spill is undefined on a static far support.
* **R3:** new `scripts/realism_direction.py` on GPU 3.
  * Reversal flips the sign in 81% of scenes; freeze abstains 42/42; noise
    warp and ping-pong drive flux toward 0.
  * Generated videos agree with the text labels in only 56–75% of scenes;
    accumulating level is negative in every video, and falling water is
    near 0.
  * Measured speed is compressed: ×2 reads as ×1.31.
* **R4:** new `scripts/realism_replay.py`.
  * Incumbent `cand-recurrence-0` fails: 34/41 pass-throughs score ≥ 0.95.
  * Residual `cand-recurrence-1` peaks at 0.941 on pass-throughs, against
    1.0 for exact loops; this is an easy known answer.
* **Process notes:**
  * A replay crash on icb04 (empty dynamic region) was fixed by an explicit
    abstention; the run was restarted, and no report is partial.
  * The direction reader now prepares only window frames; its results are
    bit-identical on the smoke scene.
* 23 new tests (temporal controls, candidates).

## 2026-11-05 (later): round-1 review fixes

Source: `docs/SNF_PP_REALISM_ROUND1_DECISION_REVIEW_2026_11_05.md`. No video or
existing report was changed, and every old identity still computes its old value.

* **Adoption fails closed.** `native_controls.adopt` used to substitute the expected
  parent hash when a RUN.json record lacked it. It now refuses:
  * a record missing a declared hash;
  * a cell with no declared parent key.

  Adoption sidecars now name the RUN.json key they rely on (`parent_evidence`),
  which is not independent evidence.
* **Codec-floor abstentions under new identities:**
  * `cand-seam-1` in `realism_replay.py`;
  * `cand-edge-profile-2` (`edge_spill_2`, `boundary_step_2`) in
    `pilot_support_realism.py`.

  Each abstains when its denominator activity is below `ACT_FLOOR` = 0.5 grey
  levels. The floor was fixed from development controls before use:
  * 41 frozen controls re-encoded with x264 CRF 18 decode to 0.000 median
    successive change, and their `cand-seam-0` reaches about 10^4 to 10^6;
  * the lowest 5% of pass-through originals move 2.7.

  The old `cand-seam-0` and `cand-edge-profile-1` are unchanged.
* **Reference check.** The direction, replay and support scripts now refuse a
  baseline whose sidecar does not record a pass-through. The support pilot's
  `--static` clips, which have no sidecar, are checked by content: the first
  and last frames must each reach 30 dB PSNR against the source (H.264 stills
  reach 39–40). All 42 existing still controls pass.
* **Split amendment.** `manifest/realism_dev_split_2026_11_05_amendment_1.json`
  references the original by SHA-256 (`55e71f64…`). It:
  * records that published-panel renders on v2 scenes are held out by model
    family only;
  * defines the confirmation factorial (seen scenes × new families, new scenes
    × seen families, new scenes × new families);
  * requires confirmation data to be locked by hash before inspection;
  * classifies public-benchmark figure renders (Physics-IQ, VBench-I2V) as
    exposure-logged visual material, not confirmation data.
* 10 new tests (`tests/test_round1_fixes.py`); the suite passes 159.

## 2026-11-05 (later): metric extension design, first composite statistics, public figure set

* **Design.** `docs/SNF_PP_METRIC_EXTENSION_DESIGN_2026_11_05.md` covers three constructs:
  * A, support integrity (composite detection);
  * B, direction realism from geometry and physics;
  * C, extent and coherence.

  It also lists what to import from SceneTether, the order of work and the claim limits. The figure and table plan is `docs/SNF_PP_FIGURE_PLAN_2026_11_05.md`; render recipes are in `docs/SNF_PP_I2V_RENDER_RECIPES_2026_11_05.md`.
* **First statistics:** `scripts/realism_support_provenance.py`, A1/A2 in proxy mode, with no decoder ceiling yet.
  * The `-0` freeze z was degenerate: the median per-pixel std is 0 on both stills and pastes, so 42% of pastes were flagged. The report is kept.
  * `cand-support-paste-fraction-0` is the per-tile rule (≥ 90% of pixels never change and NCC with the source residual ≥ 0.8). Its thresholds were fixed before any composite cell was scored. Median pasted fraction:

    | cell | median | range | pass-throughs |
    |---|---|---|---|
    | hard paste | 0.90 | 0.05–1.0 | 0.000 in every scene |
    | stills | 1.00 | — | — |
    | feathered composite (fp) | 0.13 | — | 0.000 |
    | untethered composite | 0.05 | — | 0.000 |

    The composites are not frozen (about 21% of pixels repeat exactly), so the freeze condition misses them.
  * Source-match alone (π proxy) separates every construction from its pass-throughs. AUROC: hard paste 0.996, fp 1.000, untethered 1.000.
  * The boundary depends on the model family. Echo-default pass-throughs reach π = 0.37 because that method re-injects the source through its decoder; partial-mask composites go as low as 0.09. A threshold needs the decoder-range ceiling (A3) and per-tile maps, so none is set from these data.
* **Public figure set.** `scripts/build_public_figure_set.py` writes `manifest/public_figure_set_2026_11_05.json`: 12 scenes, 4 from Physics-IQ (CC BY 4.0) and 8 Pexels-sourced from VBench-I2V. The Pexels licence was read by the user. Images and prompts use the v2 crop rule and prompt validator.
* **Renders.** `scripts/render_public_figure_set.py` runs released recipes only. Causal-Forcing 5 s is queued to start once GPU 2 has no co-tenants.
* **`cand-replay-signature-0`** (`scripts/realism_replay_signature.py`).
  * Ported from SceneTether: the upstream repetition diagnostic v1.1, vendored byte-for-byte and hash-pinned (module `06f42a6b…`, calibration `44dafbf1…`), run on SNF role maps.
  * Results on the 41 eligible scenes of the h1_fm_tether100 cell, late-half suspect rates:

    | input | replay | ping-pong | freeze |
    |---|---|---|---|
    | pass-through | 0 | 0 | 0 |
    | exact loop | 1.00 | — | — |
    | cross-fade loop | 1.00 | — | — |
    | ping-pong | 1.00 | 0.37 | — |
    | freeze | — | — | 1.00 |
    | reverse tail, shuffle, ×2, ×0.5, noise warp | 0 | — | — |

    Ping-pong is caught mostly as exact replay at twice its period.
  * Pass-through windows read as "periodic, not replay" with a median of 0.34, which is the intended home for natural periodicity.
  * It supersedes `cand-recurrence-0/1` for development. Real periodic footage (surf, flames, fountains) is still needed as a negative.

## 2026-11-05 (evening): direction candidates v0 → v1, extent and spatial controls

* **v0 run.** `manifest/realism_dev_2026_11_05/geometry_scenetether.json` (h1_fm_tether100 cell, 22 routed scenes, `snf` rate, GPU 2 uncontended).

  | control | channel A median (expected sign) | falls G median (expected sign) | plumes/flames G median (expected sign) |
  |---|---|---|---|
  | pass-through | 0.67 (5/6) | 0.17 (3/5) | −0.70 (9/9) |
  | reverse tail | 0.72 (5/6) | −0.42 (0/5) | 0.82 (3/9) |
  | ping-pong | 0.66 | −0.44 | 0.52 |
  | noise warp | 0.06 | −0.00 | −0.57 (6 of 11 scored) |
  | freeze | −0.13 | −0.43 | −0.35 (10 of 11 scored) |

  * **Passed:** reversal flips G for plumes and falls and leaves the axial A unchanged; the noise warp drives A to about 0; sign stability drops under ping-pong and the noise warp (channel medians 0.95 → 0.2–0.5).
  * **Failed: freeze was scored instead of abstaining.** tau is relative to the support's speed (Q95), so on a still tail the top 5% of codec/RAFT noise on the material passes it. Identical frames also give identical noise flow, so R = 1 and sign stability = 1.0 on every frozen channel. The v0 numbers are therefore not interpretable without an activity gate.
  * **Expectation corrected: ping-pong does not lower |G|.** The window holds an unequal share of the two phases and G normalizes the mean flow to unit length. Ping-pong needs a time-resolved sign statistic.
  * Several pass-throughs (icb01–03, icf02, ifw02, ifw05) carry as little material motion as their freezes; the generator's late window is near-static there, so direction is undefined rather than wrong.
  * Falls agree only 3/5 even unmodified. Fast falling water may outrun RAFT at 8 fps; hence the `native` rate below.
* **v1** (`scripts/realism_geometry.py`, tests in `tests/test_realism_geometry.py`, 12 pass):
  * activity gate: per-pixel activity is the median over pairs of |u_t|; tau1 = max(0.1 px/pair, Q95 of support activity); at least 15% of the material (three times the support's own 5%) must exceed it, otherwise every statistic abstains;
  * new identities `cand-channel-alignment-1`, `cand-gravity-sign-1`, `cand-sign-stability-1`;
  * new `cand-gravity-stability-0`, |Σ w u_y| / Σ w |u_y| over pairs and pixels, for ping-pong.
* **Flow cache.** `scripts/realism_geometry_run.py` now caches compensated flow (float16 npz, eroded masks, video hash) under `videos/realism_cache/geometry_flows/<cell>/<rate>/<mode>/` at two rates over the same late window:
  * `snf`: the frozen-spec 8 fps frames, verified identical to `realism_direction.late_frames`;
  * `native`: every frame, routed scenes only.

  `scripts/realism_geometry_score.py` rescores the cache on CPU (v0, v1 and extent), so later versions need no GPU. Disk guard: 110 GB free on `/`. Scene lists were moved from the scratchpad to `manifest/realism_dev_2026_11_05/lists/`.
* **Extent** `cand-coverage-0` (`scripts/realism_extent.py`, I2V only, tests in `tests/test_realism_extent.py`): C = share of the material above the same tau1; E10 = the share of material activity held by its top 10% of pixels; C over four sub-windows (C_min, C_end).
* **Spatial controls** (`scripts/spatial_ops.py`, `native_controls.py spatial`, tests in `tests/test_spatial_ops.py`):
  * `conveyor_along/across` (channel scenes) and `conveyor_down/up` (falls, plumes, flames): a rigid slide of the material's own texture at 1.5 px/frame. Only the orientation differs, so A must separate along (+1) from across (−1) and G must separate down from up, while activity must not separate them.
  * `local_patch_05/15/30`: only a compact patch holding that share of the material keeps the parent's motion.
  * A first conveyor build wrapped the whole frame, which swept sky and grass into the water. It was seen on a contact sheet and deleted before any scoring, with the patch outputs of the same interrupted run.
  * The rebuilt texture is a mirror-periodic tile of the material's bounding box, with non-material pixels inpainted. Inpainting leaves smooth bands where masks are irregular (falls), which weakens flow there but does not reverse it.
* **`cand-material-drift-0`** (`scripts/realism_drift.py`, tests in `tests/test_realism_drift.py`). Ported from SceneTether's `measure_video` drift: cv2 Lab distance between a region's mean colour early (1.5–3 s) and late (the last third). Windows are in seconds. Regions are the SNF role maps. CPU, 41 scenes per cell (`manifest/realism_dev_2026_11_05/drift_*.json`), medians in Euclidean distance between mean OpenCV 8-bit encoded Lab vectors (not CIEDE2000 or standard ΔE76):

  | cell / control | material | support |
  |---|---|---|
  | source still | 0.01 | 0.02 |
  | default: pass-through / hard paste | 5.75 / 4.99 | 11.23 / 0.65 |
  | fp: pass-through / feathered composite | 7.24 / 6.18 | 7.83 / 2.84 |
  | unt: pass-through / untethered composite | 7.17 / 7.65 | 7.36 / 2.03 |
  | tether100: pass-through | 3.72 | 1.15 |
  | tether100: freeze / noise warp | 5.89 / 5.86 | 1.37 / 1.16 |

  * Reproduces the SceneTether result on SNF masks: pasting repairs the support's colour, not the material's.
  * The paired contrast material − support is **not** a usable headline. It turns positive for every composite only because the pasted support stops drifting. Report the two drifts separately.
  * Drift does not detect freezes. Freeze and noise warp compare one held mid-clip frame (t0 = 30 s) with the early window, where the pass-through compares a 20 s mean, so their drift is larger. That is expected and not a defect.

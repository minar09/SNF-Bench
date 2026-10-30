# Fixed-camera subject extension and local model inventory

Status: development and exploratory testing, 2026-10-30. This is a proposal for
separate human and animal/insect tracks alongside the continuous nature core;
it does not amend `sourcefixed-1.0`, the frozen SceneTether study, or existing
WACV measurements. It does not claim human/animal naturalness from any current
SNF score.

## Existing assets and candidate screen

The local VBench checkout identifies its Image Suite as diverse I2V material
and points to [the VBench repository](https://github.com/Vchitect/VBench/tree/master/vbench2_beta_i2v).
Its README reports Pexels and Pixabay as sources and describes its ratio-aware
cropping pipeline. The method project's `prompts/oos/vbench_i2v_download`
contains 30 local 7:4 crops with source URLs and stored hashes; its
`oos_v2_60s` contains 832×480 derivatives and prompts. Thirty-two
SceneTether single-seed, 60-second clips were found, including 30 crops and two
other images. Neither the original images nor the method project's selected
examples are an untouched confirmation set.

We visually screened the 30 local crops for localized action that might remain
meaningful with a fixed camera and recorded **14 exploratory candidates**:

- Animal/insect: `ovb05`, `ovb11`–`ovb17`, `ovb20`–`ovb22`: perched bird,
  bear in water, grazing hippopotamus, otter by water, cow, red panda, panda,
  frog, squirrel, two sheep, butterfly.
- Adult human: `ovb27`, `ovb29`, `ovb30`: saxophonist, flower holder and
  guitarist. The local subset is too small to establish demographic coverage;
  the initial short list deliberately does not use children as pilot subjects.

The [inventory](../manifest/vbench_subject_pilot_inventory_2026_10_30.json)
records each image's source URL, source/crop/video hashes, prompt, crop box and
reason for inclusion. Candidate admission requires inspecting the entire
source, prompt and resulting rollout: a still image alone cannot prove the
camera is fixed or that its depicted event is sustainable. Scene or identity
blur, weak support texture, interactions, subject disappearance, occlusion,
small subjects and legitimate stillness must be explicitly annotated. In
particular, a brief jump or a gallop through a small field of view should not
be turned into a 60-second perpetual action merely because a still image exists.
Original image license and applicable model releases/consent remain unverified;
check the original source and proposed use before public redistribution.

The [media audit](../manifest/vbench_subject_clip_audit_2026_10_30.json)
checked the hash and first/middle/last frame decode for all 14 existing
SceneTether clips. All completed; each reports 961 frames at 16 fps, 832×480
(60.0625 s by frame count). This is only a media-readiness check, not evidence
of motion quality or a matched-model comparison.

## Candidate models: local evidence, not a current leaderboard

This is an inventory of installed code and files. Repository names do not prove
working inference, license suitability, or complete checkpoint downloads. Pin
repository commits, weights/configuration hashes, preprocessing and adapters
before a reported comparison; smoke-test each model on its own native task.

| Candidate | Local evidence | Appropriate comparison and current constraint |
|---|---|---|
| Steady-Forcing | `/home/minar/static-forcing`, `/home/minar/steady-forcing-plus-plus`; `/home/minar/ckpt/Steady-Forcing/steady_forcing_t2v.pt` | Author T2V candidate; use released native pipeline and disclose its relationship to benchmark authors. A directory named static-forcing is an Infinity-RoPE-derived project checkout, not itself proof of a distinct released model. |
| SceneTether / CF++ | `/home/minar/ar-image-animation`, `/home/minar/region-forcing`; CF++ 1-/2-step weights and 14,000+ source-fixed score JSON files | Author I2V method and CF++ backbone. Compare frozen SceneTether with framewise Echo and native CF++ separately; don't call region-forcing directory a new method without identifying the actual configuration. |
| SVI-2.0 | `/home/minar/Stable-Video-Infinity`, Wan2.1 I2V 14B and SVI-2.0 LoRA files | Long I2V contender: official continuation workflow, substantially different model size and compute. Establish native execution and match prompts/inputs; do not claim finite output proves unlimited continuity. |
| Helios | `/home/minar/Helios`, official README advertises Base/Distilled T2V and I2V; `/home/minar/ckpt/Helios` exists | Promising long T2V/I2V candidate; the checkpoint path is a symlink to local Base, Mid and Distilled-named model directories with weight shards. All nine local index files reference shards that exist, as recorded in [the index audit](../manifest/helios_local_index_audit_2026_10_30.json); weight integrity, environment and native 60 s inference remain unverified. Its 33-frame chunk rounding must be accounted for when matching horizons. |
| ALG / DyMoS | Local clones and method-project native and adapted outputs; see method docs/94 | Native short-window I2V and separately labeled CF++ adaptations. Do not present a CF++ port as a native long-form run; a continuation wrapper is a new, disclosed configuration. |
| UnStep | `/home/minar/UnStep`, method-project native development scores | Runtime/cache modification to specified underlying models, not an independent backbone. Qualify native/adapted rows and benchmark speed only without concurrent GPU contention. |
| Wan2.1 I2V 14B / Wan2.2 TI2V 5B | Weight shards in `/home/minar/ckpt/wan_models` | Strong short-horizon references; a long result requires a separately described continuation wrapper. Verify all shards and workflow before scheduling. |
| LongLive / Rolling / Causal Forcing | Local repos/checkpoints plus historical SNF T2V results | Native T2V comparators where the native long-video workflow is supported. Do not equate T2V and I2V results or imply base short-window CF natively generates minutes. |

Read `/home/minar/ar-image-animation/docs/94_MANDATORY_BASELINES.md` and
`docs/103_RELATED_KV_MEMORY_BASELINES.md` for the method project's earlier
source review and license concerns. Those findings are dated; check present
upstream code, weight licenses and geographic applicability at experiment
freeze. Exa research on current releases could not be performed because the
connected plugin reported its credit limit; a fresh current-source survey
remains open.

## Experiment milestones

1. **Freeze exploratory input manifest.** Keep the above 14 in development,
   separately from a prospectively sampled, newly sourced confirmation set.
   Establish independent source-based role/visibility annotations: static
   support, articulated subject(s), nonrigid material, occlusion and ignore.
   Check inter-annotator agreement and adjudicate; record unsupported/empty
   roles, and validate each source's rights. Do not reuse a material-only
   dynamic mask as a body tracker.
2. **Establish intervention validity.** On paired clips test source identity,
   anatomy/articulation, interaction/contact, temporal identity, support
   displacement and prompt-congruent motion separately. Use source-copy and
   freeze, repeated motion, subject swap, limb/shape distortions, drift,
   occlusion and naturally periodic action as controls. Use real fixed-camera
   footage where rights permit as a negative/reference distribution. A still
   subject is not necessarily wrong; read activity against the specified task.
   Require human-label agreement and track loss/coverage alongside every
   candidate metric before admission. No composite headline score initially.
3. **Pilot matched generation.** On a small, predetermined diverse subject
   subset, generate the same image, prompt and seed under SceneTether, CF++
   and one verified native I2V long-form baseline. Treat already generated
   SceneTether clips as exploratory: compare only after matching actual image
   bytes, prompt, duration and codec, documenting any preprocessing. Inspect
   all failures; do not prune hard clips to improve scores. Select which model
   implementations are feasible from smoke tests, not their scores.
4. **Compare horizons.** Score 5 s controls and 60/120/240 s prefixes of the
   same rollout when technically possible. Record start frame, fps, sample
   times, codec and overlap; separately requested duration runs are not
   prefixes. Report trajectories, missing/failure rates, confidence intervals
   at the source level and sensitivity to masks and sampling, not window-count
   pseudo-replication.
5. **Independent confirmation and human study.** Freeze a disjoint source and
   model panel, collection and exclusion rules, judgments and analysis before
   seeing confirmation outcomes. Have independent raters assess the target
   attributes rather than pooling unrelated preference modules. Study sizes
   should follow a precision/power plan and source/rater heterogeneity.
   Report nature-core, animal and human results separately, including cases
   where an incumbent equals or exceeds a candidate metric.
6. **Reproducibility and cost.** Save exact commands, model and input hashes,
   raw per-scene scores, seeds, errors, timing and hardware. Measure speed,
   peak memory and cost only on exclusive, uncontended devices, recording
   warm-up and decoding. Preserve failed runs and do not infer results from
   missing cells. Review image rights before any public artifacts.

## Current GPU use

At inspection GPU 2 was running a SceneTether VBench-Long score worker and GPU 3
was running SceneTether generation. A second bounded source-fixed scorer was
admitted on GPU 2 with a 60 GiB free-memory gate, consistent with the method
project's maximum of two concurrent scorers; no other process was interrupted.
Concurrent runtime is not an efficiency benchmark. GPU 3 was left untouched
while generation continued. GPU parity records report progress independently
and cannot validate naturalness or establish the broader subject benchmark.

### Completed nine-scene GPU 2 run and paired descriptive comparison

The GPU 2 scorer finished the same nine-regime, 60-second seed-42 subset for
`cfpp/echo_nfpb1_h1_fm_tether100_lr`: **9/9 passed**, **549/549 common
numeric leaves exact**, with required score keys, nulls and abstention flags
matching existing records. The [GPU 2 report](../manifest/sourceref_gpu2_scenetether_parity_2026_10_30.json)
contains per-video scores, provenance and registration. Scene processing
summed to 305.98 s under shared GPU contention; this is not a model-speed
measurement.

The independently executed earlier GPU 3 parity report for framewise Echo was
joined on scene, category, source-image hash, role-mask hash, measurement,
scorer hashes and seed. The [paired file](../manifest/echo_vs_scenetether_9scene_2026_10_30.json)
retains each score, both sets of abstention flags and the simple difference
SceneTether minus Echo; `compare_parity_cells.py` rejects incomplete runs and
mismatched inputs. Examples of **descriptive medians**, without a claim of
population significance or human preference:

| Measurement | Paired scenes | Median SceneTether − Echo |
|---|---:|---:|
| fBD_src | 8 | −0.887 |
| MCFF_late | 7 | +0.875 |
| idPSNR_late_src | 9 | +3.100 dB |

This is a convenient single-seed, nine-scene subset selected for parity
coverage, not an independent or representative model panel. The `fBD_src`
median excludes one abstention; MCFF excludes two motion abstentions. These
measurements do not establish flow naturalness, and historical
`dE_static_src` in the same file retains the known float32 accumulation defect.
Do not treat these medians as a general ranking or pool them with different
horizons, masks or source groups. The full suite passed 113 tests.

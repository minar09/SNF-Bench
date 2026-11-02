# SNF-Bench++: model additions and reuse audit

Date: 2026-11-01 KST. **The experiments are not all finished.** This is a
source-checked shortlist, not a claim that any listed model is objectively
state of the art for fixed-camera natural flow. Recheck repository revisions,
weights, operating conditions and releases at the actual experiment freeze.
No GPU runs, score jobs or model downloads were started by this audit.

## What is already on disk

- Historical 60 s T2V SNF/VBench records include CausVid, Self-Forcing,
  Infinite-Forcing, Rolling-Forcing, Reward-Forcing, LongLive, Causal-Forcing
  and author-affiliated Steady-Forcing. Their [existing results](EXISTING_SCORE_COMPARISONS_2026_10_30.md)
  are development-era, common-setting records; one Rolling-Forcing prompt ID
  is duplicated. They do not establish a matched modern native panel.
- Existing source-fixed SNF, VBench-I2V and VBench-Long comparisons include
  SceneTether, CF++ Echo, static sink, age decay and several **adapted**
  configurations. They are not independent native implementations of ALG,
  DyMoS, UnStep, PackCache or FramePack.
- An earlier local audit found indexed Helios Base/Mid/Distilled-named weights.
  More specifically, `/home/minar/ar-image-animation/results/i2v_all_v2/helios_distilled60/batch.json`
  records a **complete seven-scene, nominal 60 s Helios Distilled batch**;
  the associated directories and VBench workflow artifacts exist. Some are
  segmented clips; do not count them as independent generated videos. The
  method project reported negative Helios behavior, which remains evidence to
  include rather than grounds to discard the method from a benchmark. Assess
  its exact input, codec, source and scoring provenance before reuse; do not
  assume it matches the 48-scene source-fixed cohort.
- SVI Pro has seven existing nominal 60 s files under
  `results/i2v_all_v2/svi_pro_native60`. The separate
  `results/research/scenetether_eval_oct19/native20_svi22pronative50_*` has
  completed status records at 60/120/240 s, including `ial01` at 120 s; the
  full per-scene/score coverage and actual protocol still require an import
  audit. SVI 2.0 and SVI 2.0 Pro, native inference and ports are separate
  identities.
- The method project's `docs/87`, `docs/92`, `docs/94`, `docs/100`, `docs/103`
  and `docs/141` are substantial prior surveys. Their availability, release and
  scheduling statements are dated (October 2026); `docs/168` also documented
  incomplete native and supplementary evaluation at its snapshot. Do not
  blindly treat old estimates or queue states as the live system.

The existing SNF inventory is bounded to factorial scores and the legacy CSV;
absence from it is not evidence that a video/score does not exist elsewhere.
Check exact hashes, seed, source/prompt, checkpoint, native versus port,
preprocessing, duration, and metric configuration across all project roots
before generating or scoring anything.

## High-priority candidate additions

| Candidate | Track and reason | Release / local state and action |
|---|---|---|
| **Context Forcing** | T2V long-context teacher/student and slow/fast memory; distinct from historical common-setting checkpoints. | [Official code and T2V checkpoint](https://github.com/TIGER-AI-Lab/Context-Forcing) are documented; Wan2.1 1.3B base exists locally, but the Context checkpoint and a local exact run were not found in this limited search. Verify full roots, checkpoint license and 60/120/240 s native smoke before the panel. |
| **Self Gradient Forcing+ (SGF+)** | T2V; October 2026 learned context-writing/denoising separation offers a meaningful new training-family comparison. | [Authors' repository](https://github.com/Zihan-Su/Self_Gradient_Forcing_Plus) says code and chunkwise/framewise inference checkpoints released October 7 and gives a 963-frame override. No exact local run located in the limited search; verify release revision, weights and actual runtime. Do not treat the authors' 24-hour demonstration as benchmark evidence. |
| **LongCat-Video** | T2V and I2V plus officially documented continuation; 13.6B alternative to Wan/CF++ memory mechanisms. | [Official repository](https://github.com/meituan-longcat/LongCat-Video) documents native T2V, I2V and long-video entrypoints and weights; it states MIT for weights. Verify whether each initial-image long workflow truly preserves source conditioning, expected sampling/continuation and A100 memory. No local run found in the limited search. |
| **SkyReels-V2 Diffusion Forcing** | T2V and I2V native long-form diffusion-forcing comparison with explicit extension, rather than a short-clip baseline silently looped. | [Official repository](https://github.com/SkyworkAI/SkyReels-V2) advertises 1.3B and 14B DF weights, both input types and long inference; separately identifies short T2V/I2V models. Check local reuse, license and exact DF variant before scheduling. |
| **SVI 2.0 / SVI Pro** | I2V continuation with source-anchor and previous-clip information; distinct from few-step causal models. | **Reuse the existing native 60/120/240 s records first.** Determine which exact sources, windows, scores, sampler and model variant are complete; only new source/model cells qualify for new generation. See [official project](https://github.com/vita-epfl/Stable-Video-Infinity). |
| **Helios Base/Distilled** | Native unified T2V/I2V long generation; important because local preliminary outputs can expose the metric to an unfavourable, previously observed failure. | [Official code](https://github.com/PKU-YuanGroup/Helios) offers both tracks and rounds to 33-frame chunks. Existing seven-scene I2V batch above must be audited and reused. More scenes/seeds/track are new cells only after all-root duplicate check. |
| **LTX-2.5 / 2.3** | Modern T2V/I2V high-quality short-reference family; useful to compare immediate appearance and motion. | [Official LTX-2 code](https://github.com/Lightricks/LTX-2) and [model card](https://huggingface.co/Lightricks/LTX-2.5) describe weights and native pipelines. Establish max native duration and continuation method for each exact release; mark short clips and any chained extension separately. Weights/terms, environment, VRAM and on-disk availability need verification. |

Optional richer subject/material extension: [MAGI-1](https://github.com/SandAI-org/MAGI-1)
adds a distinct autoregressive architecture (local repo and environment exist;
weights and usable long source-conditioned output must be checked). Model
selection must cover differently trained families rather than chase a long list
of near-identical checkpoints. Restricted or API-only methods belong in a
separate cost/disclosure tier, with no claimed open reproducibility.

## Recent T2V memory policies and watchlist

- **ID-Forcing:** [paper](https://arxiv.org/abs/2610.03120) is an October
  training-free cache policy tested on base T2V generators, not itself an
  independently trained backbone. Add as a **same-base, same-budget policy
  comparison** after verifying official code and checkpoint/seed settings.
- **RECAP-Forcing:** [authors' project page](https://xxuhaiyang.github.io/RECAP-Forcing/)
  describes an appearance-novelty cache hook on a Self-Forcing base and links
  code. A useful counterpoint to static-source preservation; verify the actual
  release and whether periodic nature without new objects is eligible.
- **Hybrid Forcing:** [paper](https://arxiv.org/abs/2604.10103) describes a
  distinct trained hybrid-memory generator, but the [official repository](https://github.com/leeruibin/hybrid-forcing)
  currently shows `xxx` checkpoint placeholders. Do not call it runnable until
  actual official inference weights are located and tested.
- **Recency Forcing** ([paper](https://arxiv.org/abs/2609.19729)) and
  **Ring Forcing** ([paper](https://arxiv.org/abs/2608.26794)) are relevant
  recent memory approaches; exact released inference code/weights were not
  established in this audit, so they remain watchlist entries.
- **Mix Forcing / LingBot-World 2** ([paper/project](https://zelingao98.github.io/mixforcing/),
  [official code](https://github.com/robbyant/lingbot-world-v2)) is a recent
  I2V world-model candidate. The checked examples require action inputs and
  4/8 GPUs, and the project uses CC BY-NC-SA. A neutral-action fixed-camera
  mode and a two-A100 configuration are unverified; do not label an
  action-conditioned output as directly comparable or launch its example on
  unauthorized GPUs.
- LongSANA, Rolling Sink, MemRoPE, FreqForcing, SAGA and Self-Forcing++ are in
  the local surveys; confirm current official code/checkpoints and treat native
  T2V, inference policies and hypothetical I2V adaptations as different rows.

## Practical order and completion criteria

1. Import and hash-bind **existing Helios/SVI** videos and stored scores,
   accounting for source set, model variant, score version, failures and clips.
   Do not re-encode or rescore the same videos under the current instruction.
2. Determine missing exact source/model/seed/horizon cells against every local
   project, not only `manifest/existing_scores_inventory_2026_10_30.json`.
   Resolve ambiguous provenance before deciding that an output is new.
3. For new models, review licenses and required hardware, pin official code,
   model/asset hashes, sampling recipe and duration semantics. Smoke a small,
   preregistered diverse set on authorized idle GPUs 2/3 without disturbing
   other jobs; verify first-frame and duration fidelity, save failures and cost.
4. Expand only after qualified smoke tests to held-out sources and balanced
   medium/regime pairs, at 60/120/240 s where the native workflow supports it.
   Use source-family as the statistical unit; use multiple seeds and separate
   same-rollout prefixes from requested endpoint generations.
5. The remaining metric and human study in
   [TCSVT execution protocol](TCSVT_JOURNAL_EXECUTION_PROTOCOL_2026_11_01.md)
   requires independent annotations, natural periodic negatives, replay and
   direction controls, and blinded human judgments. It is **not completed**.

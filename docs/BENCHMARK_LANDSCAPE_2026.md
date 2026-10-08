# Video-generation evaluation landscape, and what SNF-Bench should take from it

Status: research pass, 2026-09-30. Complements `VBENCH_EXTENSION_GAP_ANALYSIS.md`,
which already covers the VBench family in depth. This covers what that document
does not: non-VBench benchmarks, the meta-evaluation standard at the target
venue, and two pieces of prior work that overlap SNF-Bench's central claim.

Everything below is from published sources, listed at the end. Nothing here is
inferred from our own data.

---

## 1. The finding that matters most: an earlier paper makes our argument

**SGC — "Measuring 3D Spatial Geometric Consistency in Dynamic Video
Generation"** (arXiv 2603.19048, 19 Mar 2026, revised 5 Jul 2026; Dou, Zheng,
Chen, Zheng, Zhou, Lu).

Its premise is ours: *"consistency-focused benchmarks often penalize valid
foreground dynamics."* That is reviewer objection D restated, and it is the
observation SNF-Bench is built on. SGC separates the frame the same way we do —
a dynamic-region mask, static region as its complement — and it was public
**five months before our preprint** (SNF-Bench, arXiv 2608.28694, 27 Aug 2026).

**We do not cite it.** A reviewer who knows the area will find it, and "did not
know" is not a defence for a benchmark paper whose novelty claim is precisely
this separation. This needs to be in related work, with an honest statement of
what differs:

| | SGC | SNF-Bench |
|---|---|---|
| separation | SegAnyMo: classifies long-range spatio-temporal point tracks | Otsu threshold on the system's own early RAFT flow |
| what is measured in the static region | divergence among camera poses estimated from distinct local regions (3D geometric consistency) | ORB-based feature drift (fBD) and flow magnitude (NBF) |
| horizon | not a long-horizon benchmark | 5/60/120/240 s |
| baselines compared | FVD, MEt3R, VBench, FVMD, TRAJAN | VBench dimensions |

The defensible distinction is **horizon and failure mode**: SGC measures 3D
geometric consistency at ordinary lengths; we measure accumulation of static-
region error over minutes and the persistence of intended flow. The separation
itself is no longer novel and should not be claimed as such.

Two of its baselines — **FVMD** (Fréchet Video Motion Distance) and **TRAJAN** —
are motion-specific metrics we neither cite nor compare against.

### What to take: SegAnyMo, with the circularity claim stated correctly

SegAnyMo is a better automatic partition than Otsu-on-early-flow, because the
mask follows *content semantics* (what is a moving object) rather than *the
magnitude of the system's own motion*. That directly weakens the mechanism
behind our ρ(mask area, fBD) = −0.75.

**It does not eliminate circularity, and we must not claim it does.** SGC runs
SegAnyMo on the generated video itself; no external reference is used. The mask
still depends on the system's output, just through a generator-independent
*model* rather than a generator-dependent *threshold*. Our non-circular options
are unchanged:

* **I2V** — derive the partition from the shared source image. Non-circular by
  construction, and the reason the I2V track is the cheapest place to land the
  control reviewers asked for.
* **T2V** — held-out generator, cross-system consensus, or first-frame-blind
  manual labels, per `SNF_V2_MASK_PROTOCOL.md`.

Recommended: adopt SegAnyMo as the *automatic* partition (replacing Otsu), and
keep the independent partition as the *control*. Report both. That is a strictly
stronger answer to objection A than either alone.

---

### Addendum (2026-10-08): WorldScore is earlier still

WorldScore (arXiv 2504.00983, 2025) defines *motion accuracy* as the maximum
optical-flow magnitude inside a SAM2-tracked dynamic mask minus the maximum
outside it — a static/dynamic separation predating both SGC and SNF-Bench. It
also measures Gram-based style consistency (first vs last frame) and
forward–backward flow-cycle consistency. Its 400-participant study selects a
subjective-quality metric combination; it must not be presented as separate
validation of every dynamics instrument. Cite it beside SGC. See `METRIC_UPGRADE_PROPOSAL_v2.md` for what to adopt.

## 2. Our motion-vs-quality finding has prior art too

**DEVIL — "Evaluation of Text-to-Video Generation Models: A Dynamics
Perspective"** (NeurIPS 2024, arXiv 2407.01094).

DEVIL scores dynamics at three temporal granularities — inter-frame,
inter-segment, and whole-video — and defines three metrics: dynamics range,
dynamics controllability, and **dynamics-based quality**, the last of which
exists explicitly to address *"the common bias observed where higher dynamics
result in lower quality scores."*

That is the confound behind our Sec. 7.2 result (Dynamic Degree tracks
static-region flow at ρ = +0.929; more apparent motion means more background
motion). DEVIL identified it in 2024 and corrected for it. **Uncited.**

It also sets the meta-evaluation bar: **Pearson > 0.90 with human ratings.**

---

## 3. The loop-gaming hole has a published instrument

**ChronoMagic-Bench** (NeurIPS 2024 Datasets & Benchmarks; arXiv 2406.18522)
evaluates time-lapse generation with 1,649 prompts over 75 subcategories and two
new metrics: **MTScore** (metamorphic amplitude — degree of change over time)
and **CHScore** (temporal coherence — whether the video maintains logical
progression). Validated with **171 participants**, reporting Kendall's τ and
Spearman's ρ against human judgement.

Sec. 8 of our paper states that SNF-Bench "cannot distinguish progression from
repetition, and does not claim to." That scoped exclusion is honest, but it is
now a scoped exclusion *around an axis someone else has already instrumented*.
Tier 3 item 15 should be resolved by adopting or comparing against an
MTScore/CHScore-style progression measure rather than by restating the hole.

---

## 4. Where SNF-Bench is genuinely ahead, and should say so

Current long-horizon evaluation tiers are **10 s / 30 s / 1 min**. VBench-Long's
six dimensions (subject consistency, background consistency, temporal
flickering, motion smoothness, overall consistency, dynamic degree) are the
standard, and streaming/progressive tracks define drift as the **standard
deviation of imaging-quality scores along the temporal horizon**, with
endpoint comparisons between the first and last 30-second intervals.

Two things follow:

1. **Our 240 s tier is beyond where the field currently measures.** That is a
   real contribution and the paper under-states it.
2. **Our early/late 12% windows are a convergent design** with endpoint-drift
   metrics, which is supporting evidence for the window choice — but it also
   means "std of quality over the horizon" is an obvious comparator a reviewer
   will ask about, and we do not report it. It is cheap to add: we already have
   per-window values.

---

## 5. Submission requirements at the target venue

NeurIPS renamed the track to **Evaluations & Datasets (E&D)** — the same name as
the WACV track we submitted to. `NEXT_VENUE_PLAN.md` still calls it "D&B".

Requirements, from the 2026 call (2027 should be assumed similar; 2026's
deadlines were abstract 4 May, paper 6 May, notification 24 Sep):

* **Croissant machine-readable metadata, with core *and* Responsible AI (RAI)
  fields.** Auto-generated if hosted on Hugging Face, Kaggle, Dataverse or
  OpenML.
* **Hosting on a dedicated ML hosting site** (or a bespoke site), accessible to
  reviewers *at submission*. Datasets over 4 GB need a reviewer sample.
* **A clearly defined data licence** and a public dataset URL.
* **Code release is required at submission** when the contribution is a reusable
  executable artifact, such as a benchmark suite. That is us.
* DOI recommended; documentation via a datasheet or equivalent.
* Human-centred evaluation is *welcomed but not required* — which means our
  inconclusive human arm is not itself disqualifying, provided we do not claim
  perceptual validity from it.

**Two of these are currently hard blockers**, not writing tasks:

* Licence is recorded for **2 of 48** I2V pairs. A dataset with no licence
  cannot be submitted to this track at all.
* Code release is required, and `check_release.py` still reports **100 tracked
  files naming internal methods** (mostly generated manifests and tables that
  include internal rows). The scan is now clean of absolute paths and of
  would-ship internal artifacts, but the manifests still need regenerating with
  public-only filtering.

---

## 6. Concrete upgrades, in priority order

1. **Cite SGC and DEVIL, and narrow the novelty claim** to long-horizon
   accumulation plus flow persistence. Costs nothing, removes the largest
   reviewer-attack surface. *(writing only)*
2. **Swap the automatic partition to SegAnyMo**, keep Otsu as a documented
   ablation, and keep the independent partition as the control. Directly
   addresses objection A with a method that has an implementation. *(code, no
   generation)*
3. **Fix the licence gap** — hard blocker. See `I2V_IMAGE_COLLECTION_BRIEF.md`.
4. **Add "std of quality over horizon" as a comparator drift definition**, from
   values we already hold. *(analysis only)*
5. **Report metric-vs-human rank correlation** (Kendall/Spearman) rather than
   pairwise preference agreement, matching ChronoMagic and DEVIL. Our existing
   study cannot support it at n = 8 raters; the field bar is ~170. Either scale
   the study or report the metric comparison without a perceptual claim.
6. **Add a progression-vs-repetition measure** (MTScore/CHScore-style) or keep
   the exclusion but cite ChronoMagic-Bench as the instrument that covers it.
7. **Compare against FVMD and TRAJAN**, the motion-specific metrics SGC uses.
8. **Croissant + RAI metadata, Hugging Face hosting, datasheet, DOI.** Mechanical
   once the licence is settled.

---

## 7. Note on the preprint

SNF-Bench is public on arXiv (2608.28694) since 27 Aug 2026 under all four
author names. NeurIPS and CVPR permit prior arXiv posting, so this is not a
submission barrier, but the paper is non-anonymous and findable by title, and
the venue plan does not mention it. It does establish a public date for the fBD
and NBF definitions — after SGC, which matters for how §1 is worded.

---

## Sources

* SGC — [arXiv 2603.19048](https://arxiv.org/abs/2603.19048)
* SNF-Bench preprint — [arXiv 2608.28694](https://arxiv.org/abs/2608.28694)
* DEVIL — [arXiv 2407.01094](https://arxiv.org/abs/2407.01094),
  [NeurIPS 2024 proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/file/c6483c8a68083af3383f91ee0dc6db95-Paper-Conference.pdf),
  [code](https://github.com/MingXiangL/DEVIL)
* ChronoMagic-Bench — [arXiv 2406.18522](https://arxiv.org/abs/2406.18522),
  [NeurIPS 2024 D&B](https://proceedings.neurips.cc/paper_files/paper/2024/hash/25b9960c8a5bd887eb5476c951260403-Abstract-Datasets_and_Benchmarks_Track.html),
  [project page](https://pku-yuangroup.github.io/ChronoMagic-Bench/)
* Survey of AI-Generated Video Evaluation — [arXiv 2410.19884](https://arxiv.org/html/2410.19884v2)
* Geometrical consistency for AIGC video quality — [arXiv 2608.09594](https://arxiv.org/pdf/2608.09594)
* StreamAV-Bench (progressive/drift track) — [arXiv 2608.26336](https://arxiv.org/pdf/2608.26336)
* VBench — [CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/papers/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.pdf)
* NeurIPS 2026 Evaluations & Datasets call — [neurips.cc](https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets)
* NeurIPS D&B bar-raising / metadata — [blog](https://blog.neurips.cc/2025/03/10/neurips-datasets-benchmarks-raising-the-bar-for-dataset-submissions/),
  [RAI metadata](https://blog.neurips.cc/2026/05/04/responsible-ai-metadata-requirements-for-the-evaluations-and-datasets-track-neurips-2026/)

## 2026-10-08 I2V decision amendment

The current task-specific recommendation is documented in
[I2V_METRIC_REVIEW_2026_10_08.md](I2V_METRIC_REVIEW_2026_10_08.md). It qualifies
the proposals above: keep source-defined I2V masks as the main partition;
use generated-video segmentation only as a sensitivity/control instrument.
Generic temporal coherence and texture retention do not establish absence of
replay, and a longer horizon alone does not establish novelty. Source fidelity,
absolute fixed-camera motion, material intent, long-lag replay and independent
human validation define the evaluation profile. Published correlations and
study participant counts are context, not universal admission thresholds.

Additional direct I2V/motion comparators include
[DIVE](https://arxiv.org/abs/2505.19901v3),
[AIGCBench](https://arxiv.org/html/2401.01651v1), and
[VMBench](https://openaccess.thecvf.com/content/ICCV2025/papers/Ling_VMBench_A_Benchmark_for_Perception-Aligned_Video_Motion_Generation_ICCV_2025_paper.pdf).
The released TRAJAN model uses 150-frame episodes; fixed-duration windowing
requires documented sampling and does not make it a full-video loop detector.
FreqForcing is relevant spectral prior art but its audited repository still
lists inference release as TODO. All new SNF candidate metrics remain provisional.

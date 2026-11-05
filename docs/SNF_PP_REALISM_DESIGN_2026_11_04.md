# SNF-Bench++: scoring motion naturalism and support realism without rewarding exploits

2026-11-04. Design only. **Superseded for order of work by
`SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md`**, which adopts the corrections in
`SNF_PP_REALISM_REVIEW_2026_11_04.md`. Nothing here is admitted, and no frozen measurement
changes. **Every "catches" or "fails" below is a hypothesis to be tested by §4**,
not a guarantee: a careful composite can reproduce grain, lighting and boundary
effects, and a statistic is claimed only after it passes held-out real footage,
the constructed controls and a separate human judgement. Each proposed statistic gets its own candidate identity (`cand-*`),
following `snf_candidates.py`.

## 1. The two exploits current measures reward

| exploit | what it does | which current measures it wins |
|---|---|---|
| **E1: random motion** | noise-driven warps, texture boiling (appearance regenerated each frame without transport), jitter | every *monotone* activity measure: VBench `dynamic_degree`, mean compensated flow, our interior-tile activity. More motion always scores better. |
| **E2: pixel composite** | source pixels pasted into the support, any motion inside the dynamic mask; also what a classic cinemagraph does | every *source-referenced* fidelity measure: PSNR, ΔE, fBD to source, `sourcefixed-1.0`. A composite is the global optimum of all of them. |

Both are already live risks. The H1-FM audit showed a region-mean colour win
that reversed in the pixelwise tail (§5). A method team can also improve
"support fidelity" by moving toward E2 without becoming more realistic.

## 2. Principle: score two-sided against real footage

Never read a statistic as "more is better" or "less is better". For each
statistic *s* on a region, compare the generated video's *s* with the
distribution of *s* on **real fixed-camera footage of the same medium**,
processed by the same encoder and sampler:

* **band score**: the fraction of evaluation windows whose *s* lies inside the
  real [p5, p95] band;
* **distance**: the excess outside the band, in units of the real interquartile
  range, or Wasserstein-1 between the per-window distributions.

Boiling (too much, too incoherent) and freezing (too little) then both leave
the band. So does a composite's dead support (§3.2). Fidelity to the source
stays a separate axis; realism never offsets it, and it never offsets realism.

### 2.1 Reference footage, the critical resource

| option | gives | cost and risk |
|---|---|---|
| **A. Own capture, recommended.** Tripod clips, 4–5 min each, ≥ 3 sites per medium for the nine transport regimes. Take the first frame as the I2V source. | per-scene **real continuation**, unambiguous rights, and length matching the 240 s horizon | field days. It also closes the licence gap: 21 of 24 fresh sources have no licence recorded. |
| B. Rights-cleared stock (Pexels, Pixabay, Wikimedia Commons CC video), static-camera clips only | medium-level bands | clips are mostly < 60 s; camera stability has to be verified with the same registration we use for scoring |
| C. DynTex (CC BY-NC-SA, research use) | medium-level bands, an established dataset | short, low resolution, not long-horizon; diagnostic use only |

With option A, the fresh confirmation set *is* the real-reference set. Every
I2V scene then has its own real band, the scene-level analogue of Physics-IQ's
real-continuation comparison, made distributional because natural flow is
stochastic. Bands are compared only within medium and resolution. Reference
footage is disjoint from every source used for development.

## 3. Proposed statistics

All computed per window (early / mid / late) inside the source-derived role
masks, after the existing similarity compensation.

### 3.1 Motion naturalism (dynamic mask)

| id | statistic | catches |
|---|---|---|
| M1 | Wasserstein-1 of log-speed, and circular W1 of direction, vs real | wrong speed; wrong direction (for example water flowing uphill) |
| M2 | spatial coherence: flow autocorrelation length, and the slope of the flow energy spectrum | noise warps (white spectrum); rigid sliding (too coherent) |
| M3 | temporal persistence: decay time of flow temporal autocorrelation | boiling and jitter (fast decay); freeze and loops (none, or periodic) |
| M4 | advection residual: photometric error of `warp(frame_t, flow)` vs `frame_t+1`, two-sided | appearance regenerated without transport |
| M5 | point-track motion model: TRAJAN reconstruction error per video, and FVMD-style velocity/acceleration statistics vs real | implausible trajectories. FVMD alone misses shuffled velocities, so it is always read together with M3. |
| M6 | stationarity: drift of M1–M4 across windows, relative to real drift (≈ 0 for a fixed natural scene) | slow death of motion (the near-static collapse LongTake reports), acceleration, regime change |

### 3.2 Support realism (support mask): composites do not score as real

| id | statistic | real footage | composite |
|---|---|---|---|
| S1 | **support temporal noise**: per-pixel temporal std after compensation, robust median | sensor grain, micro-motion, lighting; above the codec floor | the codec floor only (static-clip median 0.019 grey levels; `manifest/candidate_floors.json`) |
| S2 | **boundary activity profile**: activity as a function of signed distance (−32 to +32 px) to the dynamic/support boundary | smooth transition from spray, wet edges, reflections, soft occlusion | a step |
| S3 | **noise-residual consistency across the boundary**: high-pass residual energy ratio inside vs outside (the splice-forensics cue) | ratio within the band | mismatch |
| S4 | **photometric coupling**: correlation between dynamic-region luminance fluctuation and the adjacent support (caustics, firelight, reflections) | medium-dependent, often clearly positive | ≈ 0 |

S1–S4 are two-sided. A generator that keeps support pixels *close* to the
source while giving them natural grain and coupling scores well on both
fidelity and realism; a paste scores well only on fidelity. That is the
intended separation, and the profile report makes it visible instead of
summing it away.

## 4. Admission tests: constructed adversaries per scene

Every adversary is encoded with the generators' writer (as for the floors), so
codec signatures cannot separate it from real footage.

| control | construction | must score |
|---|---|---|
| C1 source-paste composite | (a) real dynamic region + source support; (b) **each entrant's own video with source pixels pasted into its support** | worse than real on S1–S4. (b) must not beat the unpasted entrant on realism unless humans agree. |
| C2 noise warp | dynamic texture advected by a random flow with real-matched mean speed | worse than real on M1–M3 |
| C3 boiling | per-frame texture resynthesis with matched marginal statistics | worse than real on M3 and M4 |
| C4 loops | exact, cross-faded and ping-pong | caught by recurrence (existing candidate); M6 flat |
| C5 slow freeze | dynamic activity decaying over the horizon | M6 |
| C6 published cinemagraph | for example *Animating Pictures with Eulerian Motion Fields* (Holynski et al., CVPR 2021), which released code | a real-world composite-and-loop system, entered as a published method |

**Admission rule.** For each control and each medium, the statistic separates
real from control with AUC ≥ 0.9 (source-clustered 95% CI lower bound ≥ 0.8).
On natural periodic real clips (surf, fountains) it must not flag a loop.
Thresholds are set on development media and confirmed on held-out media.

**Human anchor.** A blinded 2AFC "which is real footage?" trial with real clips
hidden in the panel. The *fool rate* (how often generated clips are chosen over
real ones) is the direct naturalness endpoint that M\* and S\* are validated
against. This feeds the human-study design; it does not touch the existing
human-study code.

## 5. Evidence available now (2026-11-04)

Pixelwise CIEDE2000 vs region-mean `dE_static`, same late window, both seeds
pooled per scene, precipitation excluded (`scripts/audit_pixelwise_colour.py`):

| target vs reference | n | region-mean dE | pixelwise ΔE00 mean | pixelwise ΔE00 p90 |
|---|---:|---|---|---|
| H1-FM vs spatial Echo k3 | 42 | −5.54 [−8.66, −2.63] | −0.87 [−2.06, +0.35] | **+2.77** [+0.65, +5.02] |
| SceneTether vs spatial Echo k3 | 42 | −10.20 [−12.82, −7.80] | −5.63 [−6.73, −4.63] | −10.59 [−12.68, −8.60] |
| SceneTether vs plain Echo k1 | 42 | −9.24 [−12.40, −6.40] | −3.98 [−5.50, −2.80] | −9.44 [−12.13, −7.24] |
| SceneTether vs static sink k3 | 42 | −7.98 [−10.37, −5.78] | −4.79 [−6.06, −3.59] | −8.97 [−11.25, −6.79] |

Sources: `manifest/pixelwise_colour_audit_h1fm.json`,
`manifest/pixelwise_colour_audit_scenetether.json`.

* SceneTether's colour advantage holds pixelwise, in the mean and at the 90th percentile, against these three references on these 42 scenes.
* H1-FM's advantage exists only in the region mean.

This audit shows why §3.2 is needed: SceneTether holds the source more
closely, and a measure that only rewards closeness to the source cannot tell
whether that closeness is natural or a paste. S1–S4 on SceneTether and on its
C1(b) composite is the first real test.

### 5.1 First support-realism pilot (CPU, 2026-11-04)

`scripts/pilot_support_realism.py` → `manifest/support_realism_pilot_scenetether_s42.json`.

* Inputs:
  * SceneTether 60 s, seed 42, the 42 non-precipitation scenes;
  * control C1(b) of each video (`scripts/build_composite_controls.py`: source
    pixels pasted into label-1 support, re-encoded with the renders' writer);
  * the source encoded as a 10 s static clip.
* Window: late 12%, 8 fps.
* **This measures separability from a paste, not realism**: there is no
  real-footage band yet.

| statistic | eligible | SceneTether median | composite median | static clip | video − composite [95% CI] | video > composite |
|---|---:|---:|---:|---:|---|---:|
| S1 support noise (grey levels / step) | 42 | 2.61 | 0.00 | 0.00 | +2.71 [+2.24, +3.18] | 42/42 |
| S2 edge spill (near / far support) | 13 | 2.01 | 6.85 | — | −8.95 [−13.92, −4.81] | 0/13 |
| S2 boundary step (near support / inner dynamic) | 13 | 0.82 | 0.10 | — | +0.70 [+0.44, +0.99] | 13/13 |

What this shows:

* **A naive paste has near-zero support change** (median 0; 30/42 pastes and
  all 48 stills exactly 0, 12/42 pastes positive). This is not a universal
  H.264 floor. The paste was decoded and re-encoded while the original was not,
  so this comparison mixes encoding histories; the rerun compares each control
  with a pass-through re-encode of its own parent. A residual-matched paste
  defeats S1 by construction, so it is the next control. S1 is renamed
  `support_change`: it is mean successive grey change, not sensor noise, and
  drift, lighting and flicker all enter it.
* **The edge-spill hypothesis is wrong.** Encoding bleeds dynamic-region
  motion into adjacent support macroblocks, while far support of a paste is
  exactly still, so the near/far ratio is *larger* for the paste. The
  statistic is rejected in this form. Any boundary-profile statistic must be
  read against encoded controls, never against an idealized step.
* **Boundary step** (support beside the boundary relative to the dynamic side)
  separates 13/13. Only 13 scenes have ≥ 200 support pixels both within 8 px
  of and ≥ 32 px from the dynamic region; widening eligibility is needed.
* **SceneTether's support is not still**: its median frame-to-frame change is
  2.6 grey levels. Without a real band this is neither good nor bad. It is
  above the codec floor, and whether it is natural grain or support
  regeneration is exactly what the real-footage band (§2.1) must decide.
  The value is not compensated for global drift; SceneTether's source
  registration is established on these scenes.

## 6. Order of work and cost

1. **CPU:** S1 and S2 need no flow. First pilot done (§5.1). Next: C1(c)
   grain-matched composite; S2 eligibility; other published entrants' cells.
2. **GPU (RAFT at 8 fps, cheap):** M1–M4 and S3 on v2. Only v1 flows are stored
   (`.flow_fields/`, 1,342 files); `.flow_fields_v2/` is empty.
3. **Reference footage:** option A capture plan, nine media × ≥ 3 sites × 4–5
   min. This is the critical path for the journal.
4. **GPU, later:** TRAJAN / point tracking (M5), and the C6 cinemagraph entrant.
5. Admission study, then the human 2AFC anchor.

## 7. Related work these build on

* TRAJAN (Allen et al., 2025, arXiv 2505.00209): point-track autoencoder; per-video reconstruction error tracks human realism ratings.
* 3DSPA (arXiv 2602.20354): 3D extension of TRAJAN.
* FVMD (arXiv 2407.16124): Fréchet distance on point-track velocity and acceleration; its shuffle weakness is documented.
* Physics-IQ: real-continuation comparison. Here it is made distributional.
* StyleCineGAN: static-consistency LPIPS. It rewards a paste by construction and is the opposite of S1–S4.
* Image-splicing forensics: noise-residual inconsistency, used in S3.

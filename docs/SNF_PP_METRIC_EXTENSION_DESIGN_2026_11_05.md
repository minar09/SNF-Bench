# SNF-Bench++ metric extension design

2026-11-05. This design adds three constructs to SNF-Bench++. It draws on three sources:
- a literature review, recorded in §8 with how far each item was checked;
- an inventory of the SNF v2 metrics in the SceneTether method project (`/home/minar/ar-image-animation`, abbreviated AIA below);
- the round-1 realism development results (`SNF_PP_REALISM_AND_REVIEW_PLAN_2026_11_04.md` §9).

The user asked for:
- a metric that separates a generated static or low-activity support from a raw pixel composite;
- motion metrics that test realism, not only activity: does a river flow along its channel rather than across it, does a fall fall;
- whether motion is local or global (ocean, big falls).

The work is not deadline-driven. SNF-Bench++ is submitted after SceneTether.

## 0. Rules that bind every item

- **Frozen metrics stay frozen.** METRIC_SPEC v1.1 metrics are never redefined or rescored. Each statistic below is a new `cand-*` identity written to new paths, with abstentions recorded per video and per statistic.
- **Development and confirmation.** Development uses existing videos (authorized 2026-11-05) and derived controls. Confirmation follows the factorial in `manifest/realism_dev_split_2026_11_05_amendment_1.json`. A candidate is promoted only after it passes its known-answer controls *and* lands inside a real-footage band.
- **Flags gate scores.** Composite detectors are validity flags that gate the frozen support metrics, so a paste cannot win fBD. They are never quality scores. Fidelity to the source (PSNR/SSIM/LPIPS) is never reported as quality: a repeated still tops VBench-I2V (DIVE, arXiv 2505.19901), and in AIA a repeated source scores 41.65 dB against 28.30 for a paste-back.
- **Role maps must not depend on the video being scored.** Coverage and extent statistics read a role map that does not come from the evaluated video's own flow. Otherwise a video that moves only in a patch produces a small material mask and scores perfect coverage.
  - I2V: the source-image role map.
  - T2V: a frame-0 semantic map. This is an open dependency; see §6.
- **One plot, not one number.** Support stability is always reported jointly with material activity and coverage, as a two-axis plot or a dynamics-binned score in the DEVIL style.

## 1. Construct A: support integrity (composite detection)

A paste composite is a cinemagraph: a still frame composited with dynamic regions (Bai et al. 2012; Liao et al. 2013). Today it scores perfectly on fBD and NBF. Round 1 showed that the support-change statistic separates composites only because this generator's support changes (R1, diagnostic only). The tests below target the construct that can actually be enforced: **a frozen support whose high-frequency content is identical to the source.**

They cannot prove where the pixels came from. A paste laundered through the generator's own decoder is indistinguishable from a decoder-held static support. The paper must state this limit.

| id | statistic | inputs | track |
|---|---|---|---|
| `cand-support-freeze-0` (A1) | $z = \log(\mathrm{median}_S\,\sigma_{HF} / \sigma_{floor})$. $\sigma_{HF}$ is the per-pixel temporal std of a wavelet-denoiser residual $W(f_t)$ over 1 s windows. $\sigma_{floor}$ is the same quantity on the source encoded as a still clip with the release codec. Also reported: the bit-exact repeat fraction on the support. | frames, role map, codec | I2V; T2V against frame $t_0$ |
| `cand-support-hf-source-0` (A2) | $\pi = (\bar\rho - \rho_{dec})/(\rho_{codec} - \rho_{dec})$, where $\rho_t = \mathrm{NCC}_S(W(f_t), W(x_0))$. $\rho_{codec}$ uses Codec($x_0$); $\rho_{dec}$ uses the decoder reconstruction (A3) or, as a labelled proxy, $D(E(x_0))$. $\pi \approx 1$ means copied pixels; $\pi \le 0$ means the support is decoder-limited. A per-tile $\pi$ map shows a feather ramp. | frames, $x_0$, role map; VAE optional | I2V; T2V self-variant with $x_0 := f_{t_0}$ |
| `cand-support-decoder-margin-0` (A3) | $m_t = \mathrm{PSNR}_S(f_t, x_0) - \hat c^{*}_{S,\mathrm{codec}}$. The ceiling $\hat c^{*}$ is the best support PSNR any decoder output reaches, found by optimizing the latent of a static clip on the support loss starting from $E(x_0)$, then passed through the release codec. $t=0$ is reported separately. | generator VAE (public: Wan 2.1/2.2, LTX), $x_0$ | I2V only |
| `cand-support-seam-band-0` (A4) | Frozen, source-identical material within $b$ px of the support boundary versus at $2b$–$4b$; a joint feather ramp of $\pi$ and of material activity. A motion ramp alone is physical, because rivers slow at the banks. | A1, A2, role map | I2V |
| `cand-illum-coupling-0` (A5, exploratory) | Emissive scenes only. Lagged correlation between material brightness $m(t)$ and the near-support ring $r(t)$ (exposure removed by regressing out the far support), z-scored against circular shifts. | frames, role map | both |

**Decision rule (2×2 of A1 and A2).** Frozen and source-HF-matching gives the **paste flag**. Frozen and not matching is a frozen generated support, which is legitimate for the support construct. Not frozen means no flag.

**Abstentions:**
- fewer than $N$ textured support tiles (flat sky or water reconstructs well regardless; an AEROBLADE limitation);
- $\rho_{codec} - \rho_{dec} < \epsilon$ (weak-noise source);
- post-decoder stages such as super-resolution or frame interpolation;
- a non-public VAE (A3 only);
- non-emissive categories (A5).

**Why A3 is not $D(E(x_0))$.** SceneTether used the VAE round trip $r_0$ as a floor (`AIA/docs/32_RF_RETRY_THREE_LABEL.md:131-133`). The encoder is not the optimal inverse (amortization gap; Cremer et al., ICML 2018), so a generated frame can legitimately beat $D(E(x_0))$. Used as a ceiling it would raise false paste alarms. The decoder-range maximum is the defensible bound.

**Proxy available today.** For I2V families whose frame 0 is $r_0$ (prefix-I2V), the gap between `idPSNR_late_src` and `idPSNR_src_f0` (`scripts/snf_sourceref.py:345-347`) approximates A3 without any VAE call. It is invalid for jointly decoded windows (`AIA/tools/score_g1.py:11-13`).

**Known-answer controls.** Most already exist in `scripts/composite_ops.py` and `native_controls.py`.
- Positive controls:
  - hard paste;
  - feathered paste ($\sigma$ = 2, 8, 16 px);
  - mask dilated into the material by 8 and 24 px (A4 target);
  - paste re-encoded at CRF 18, 23, 28;
  - paste plus per-frame noise $\sigma$ = 1, 2, 4 (should evade A1 but not A2);
  - VAE-laundered paste $D(z^*)$ and $D(E(x_0))$ (should evade A2 and A3 but not A1; this documents the limit);
  - frame-0-only paste.
- Negative controls:
  - unmodified outputs;
  - real fixed-camera footage with $x_0$ = frame 0. Expected: A3 above the ceiling ("not from this decoder"), A1 above the floor (sensor noise). The paper must say these statistics measure "not decoder output", not "pasted".

## 2. Construct B: direction realism from scene geometry

No physics benchmark checked scores flow direction against scene geometry: Physics-IQ, VideoPhy-2, PhyGenBench and VBench-2.0 all leave it out. Round-1 R3 scored against text-derived labels, which agreed with generated videos in only 56–75% of scenes. Its accumulating-level and falling-water results were negative or near zero. The statistics below take the expected direction from geometry and physics instead of the caption.

Shared preprocessing:
- similarity-compensated RAFT flow on the material;
- mean field $\bar u$;
- steadiness $R = |\sum_t u_t| / \sum_t |u_t|$;
- weights $w = |\bar u|\, R\, \mathbb{1}[|\bar u| > \tau_{floor}]$, with $\tau_{floor}$ taken from the support null.

Each estimate is cross-checked with STIV (Fujita et al. 2007): the orientation of the space-time image along the expected axis. RAFT can report gravity-wave or flicker motion rather than current (Dolcetti et al. 2020; Fazekas et al. 2009).

| id | statistic | applies to | key abstentions |
|---|---|---|---|
| `cand-channel-alignment-0` (B1) | Axial alignment $A = \sum w \cos 2(\theta_{\bar u} - \theta_{\hat t}) / \sum w \in [-1, 1]$, where $\hat t$ is the bank-tangent field: the doubled-angle field solved by Laplace's equation with bank tangents as boundary conditions, which handles converging banks under perspective. $+1$ means along the channel, $-1$ across, 0 isotropic. Reported near the bank and over the full material. | channel flow (rivers, streams, weirs) | bank length below $L_{min}$; channel aspect below 2 (pools); material touching 3 or more frame edges; low $\sum w$ |
| `cand-gravity-sign-0` (B2) | $G = \sum w\, \bar u_y/|\bar u| / \sum w$, expected near $+1$ for falls. $U = -G$, expected positive for plumes and flames; STIV or oriented energy (Derpanis & Wildes 2012) is used for flames. | falling water, buoyant plume, combustion | camera roll above 10° (from support lines); wind stated in the prompt |
| `cand-wave-onshore-0` (B3) | $W = \sum_P e_P \cos(\theta_{k^*_P} - \theta_{\hat n_P}) / \sum e_P$. $k^*_P$ is the peak of the $\omega > 0$ half of a per-patch 3-D FFT; keeping only $\omega > 0$ resolves the 180° ambiguity (Young et al. 1985). $\hat n$ is the onshore normal. | oscillatory water with a visible shoreline | no shoreline; reflective rocky coast; surf-zone pixels |
| `cand-dispersion-0` (B4) | Fit the ridge $\omega = a|k|^\beta$ over at least $N$ $|k|$ bins. $\beta \in [0.5, 1]$ is physical for deep to shallow water and is invariant to pixel scale and to slow motion. Shell concentration $Q - Q_0$ uses a separable null; a phase-randomized null would preserve the spectrum exactly and is not used. For rivers, the Doppler offset gives the current direction as an independent check on B1. | waves at 60–240 s | short clips (frequency resolution); strong perspective inside a patch; breaking zone |
| `cand-sign-stability-0` (B5) | $S = |\sum_{t,x} w\, \bar u_t \cdot \hat t| / \sum_{t,x} w\, |\bar u_t \cdot \hat t|$. Geometry cannot fix a river's sign, so B5 catches mid-horizon reversals and drift instead. | channel flow | as B1 |

**Known-answer controls:**
- Flow rotated by 90°: $A \to -A$. Implemented as synthetic Eulerian warps of the source along $\hat t$ and along $\mathrm{rot}_{90}(\hat t)$, in the style of Holynski et al. 2021.
- Isotropic random flow: $A \approx 0$.
- Time reversal (existing `reverse_tail`): $G$, $U$ and $W$ flip sign; $A$ and $S$ stay invariant by design.
- Horizontal flip: $A$, $G$ and $U$ are invariant.
- Frozen material: every statistic abstains.

**Real-footage bands:**
- rivers: Perks et al. 2020 (ESSD 12:1545, 13 river videos with reference velocities; licence to be checked);
- waves, flames and pouring: Physics-IQ and other licensed footage.

**Gaming and its defence.** A rigid conveyor-belt texture slide scores $A = 1$ and $S = 1$. The defences are coherence length (C2) and dispersion (B4). Correct direction confined to a small patch is defeated by gating on coverage (C1).

## 3. Construct C: extent and coherence (local vs global)

VBench dynamic degree passes a video whose top 5% of flow magnitudes exceed a threshold, so a moving patch covering 5% of the frame is "dynamic". Motion smoothness gives a frozen video 1.0. Physics-IQ IoU is 1.0 when both masks are empty. None of them measures extent.

| id | statistic | notes |
|---|---|---|
| `cand-coverage-0` (C1) | $C = |\{x \in M_{role} : a(x) > \tau\}| / |M_{role}|$ with $\tau = \kappa\, Q_{95}$(activity on eroded support). Also the weighted twin $C_w$ (Physics-IQ weighted-spatial idea, with the role map as ground truth), the concentration $E_{10}$ (share of activity in the top 10% of pixels), and the per-window curve $C(t)$, reported as $C_{end}$ and $\min_t C(t)$. | Recall only; support motion stays with fBD. Abstains when $|M_{role}|$ is under 2% of the frame. Far-field material is weighted by an expected image-motion scale or reported near-field only. |
| `cand-coherence-length-0` (C2) | $\ell$ = integral of the fluctuation-flow autocorrelation up to its first zero, reported as $\ell/\sqrt{|M|}$ in row bands. Two-sided: very small $\ell$ is shimmer; $\ell/\sqrt{|M|} \to 1$ with $R \to 1$ is a rigid slide. | Unresolvable below about 16 px (RAFT 1/8 grid). Bands are calibrated per category on real footage. |
| `cand-propagation-0` (C3) | STIV along $\hat t$, $\hat g$ or $\hat k^*$: orientation coherence, linearity of the cross-correlation peak lag in offset ($R^2$, phase speed $c$), agreement of $c$ with $|\bar u|$, and propagated coverage $C_{prop}$. | Standing waves (rapids, hydraulic jumps) legitimately give $c \approx 0$ and are reported separately. |
| `cand-spectral-dynamism-0` (C4) | Flow-free, per tile: $\eta = \sum_{\omega \ne 0} E / \sum E$ minus the support floor, plus its coverage twin. An early-versus-late LDS innovation variance (Doretto et al. 2003) tracks freezing. | Covers fire and smoke, where brightness constancy fails. |

**Known-answer controls:**
- frozen material: $C \approx 0$;
- **local-patch-only motion** at $p$ = 5, 15 and 30% of $M$: $C \approx p$ and $E_{10}$ is high, while VBench dynamic degree still reports "dynamic" at $p \ge 5\%$, a useful demonstration;
- temporal fade (motion stops after $t_0$);
- incoherent shimmer: $\eta$ alone is fooled, which shows why the flow and propagation gates are needed;
- rigid conveyor slide;
- real full-coverage clips as the upper reference.

## 4. Imports from the SceneTether project

Sources are the inventory, `AIA/...` paths and the cited docs. Each import is vendored hash-pinned, adapted to SNF role maps, given windows defined in seconds and the effective frame rate (the SNF panel includes 15 and 24 fps entrants), and named as a new identity.

1. **`cand-replay-signature-0`**, ported from `AIA/tools/factorial_scoring/repetition.py` v1.1.
   - It reports exact, ping-pong, freeze and "periodic, not replay" flags.
   - Validation on 252 clips: AUROC 1.0 on loops, cross-fades, ping-pong and late freezes; 0.958 on late-onset loops; 0.956–1.0 with periodic negatives (`AIA/docs/122_REPETITION_DIAGNOSTIC_OCT15.md:13-18`).
   - It covers the round-1 R4 gaps: jittered, variable-period and late-onset loops, and natural periodic negatives.
   - Cost: about 20 s of CPU per video.
   - Limits: rigid oscillation of a fixed texture is flagged as exact; there are only 12 generated negatives and no real footage. The codec floor must be recalibrated for SNF encodes.
2. **`cand-material-transport-persistence-0`** (DAMP).
   - Definition: $\|\sum_t u_t\| / \sum_t \|u_t\|$, similarity-compensated, with support as the null and an activity gate, compared within categories.
   - Development evidence: advective minus non-advective difference +0.111, CI [0.042, 0.173] (`AIA/docs/12_MOTION_DECOMPOSITION.md:256-268`).
   - The source JSON is missing, so the evidence must be re-derived.
   - It has no sign, so it is paired with B1/B5 and with the reversal, ping-pong and noise-warp controls.
3. **`cand-transient-rate-0`** (flash events v4). This is the only measure of pop-in and pop-out inventions. It stays diagnostic until a human audit runs: an AI-only audit put P(artefact | detected) at 0.04–0.51. Smoke, foam, vehicles and emergency lights are false positives.
4. **`cand-material-drift-0`**: late-window versus early-window mean-Lab drift of the material, measured against the same video. It works for T2V and cannot be gamed by a composite (37/48 sources, `AIA/docs/171_ACCEPTANCE_PUSH_NOV03.md:9-28`).
5. **Protocol imports:**
   - matched-timestamp registered fBD with imputation sensitivity (`latereg`);
   - event-excluded activity as a sensitivity analysis;
   - the source image's own seam as the control for any pixel-seam statistic.
6. **Not imported:**
   - region measures defined on SceneTether's own token map (items 5–7 of the inventory), until rewritten on SNF role maps;
   - the edge ratio, because a paste scores the ideal 1;
   - FIF, until it is reworked: it read smoke as 89% motionless and rewards collapse;
   - the survival gate and quality-over-time measures, which are superseded or unreliable.

## 5. Order of work

Each step lists its compute and data needs.

1. **CPU, controls already exist:** A1 and A2 in proxy mode, plus `cand-replay-signature-0`. Run them on the round-1 composite and temporal controls.
2. **CPU:**
   - C1 on I2V with source-image role maps;
   - B1 on channel-flow scenes, which needs a bank-tangent field from the role map;
   - B2 on falls, plumes and flames.
   - Requires new local-patch, rotated-flow and conveyor controls. Uses existing flow where cached; otherwise RAFT on GPU 2 or 3 under low pressure.
3. **GPU, public VAEs:** A3 decoder-range margin for Wan and LTX families. One latent optimization per source, reused for every entrant of that family.
4. **Real-footage bands:**
   - Physics-IQ real takes (CC BY 4.0) for flame, smoke and pour, and as the negative control for A1–A3;
   - the Perks et al. river set, after a licence check;
   - licensed coastal clips for B3 and B4.
5. **B3, B4, C2–C4:** only after steps 1–4 hold, on the 60–240 s clips.

## 6. Open dependencies

- **T2V role maps that don't depend on the video.** The current masks are automatic Otsu thresholds on early flow (memory note `snf-bench-mask-divergence`), which makes coverage circular. Options:
  - text-prompted segmentation of frame 0 for the named medium;
  - the planned two-annotator role maps.

  Until one exists, C1 is I2V-only.
- **Human questions H1–H8.** The owner's study is not touched. Each construct here maps to one question (support coherence, direction, extent, replay), as listed in `SNF_PP_HUMAN_QUESTION_PROPOSAL_PREP_2026_11_05.md`.
- **Camera-roll estimate for the gravity tests.** Take it from support line orientations; abstain above 10°.

## 7. What the paper may and may not say

- **A1–A3:** they detect frozen, source-identical support, which is "not decoder output". They do not prove provenance, and a paste laundered through the decoder evades them.
- **B1–B5:** agreement with geometry or physics is not velocity accuracy. B1 is sign-free by design.
- **C1–C4:** coverage depends on the role map. T2V coverage waits for a role map that does not depend on the video.
- **All of them:** development evidence shows separability from constructed controls. Realism claims need real-footage bands and blinded human ratings.

## 8. Key references

Tags: [F] full text read, [A] abstract only, [S] search snippets only, to be verified before citing.

- **Composites and generated-image detection:**
  - Ricker et al., AEROBLADE, CVPR 2024 [F];
  - Rajan et al., ICLR 2025 [A];
  - Cremer et al., ICML 2018 [A];
  - Lukáš et al., IEEE TIFS 2006 [A];
  - Cozzolino & Verdoliva, Noiseprint, TIFS 2020 [A];
  - Guillaro et al., TruFor, CVPR 2023 [A];
  - Cozzolino et al., ZED, ECCV 2024 [A];
  - Grommelt et al. 2024 [A];
  - Vahdati et al., CVPRW 2024 [A];
  - Bai et al. 2012 [A]; Liao et al. 2013 [A];
  - Kee et al. 2013 [A].
- **Direction and waves:**
  - Fujita et al. 1998, 2007 (LSPIV, STIV) [A];
  - Perks et al., ESSD 2020 [A];
  - Pizarro et al., HESS 2020 [F];
  - Dolcetti et al. 2020 [A];
  - Holman & Stanley 2007 [A];
  - Stockdon & Holman 2000 [A];
  - Holman et al., cBathy 2013 [A];
  - Young et al., JGR 1985 [A];
  - Holynski et al., CVPR 2021 [A];
  - Mahapatra & Kulkarni, CVPR 2022 [A];
  - Pickup et al., CVPR 2014 [A]; Wei et al., CVPR 2018 [A].
- **Extent and evaluation:**
  - VBench and VBench++ (dynamic degree and smoothness code) [C/F];
  - DEVIL, NeurIPS 2024 [F];
  - FVMD 2024 [F];
  - TRAJAN 2025 [F];
  - Physics-IQ (code) [C];
  - Physics-IQ Verified 2026 [A];
  - Doretto et al., IJCV 2003 [A];
  - Derpanis & Wildes, TPAMI 2012 [A];
  - Li et al., Generative Image Dynamics, CVPR 2024 [F];
  - DIVE, arXiv 2505.19901 [F];
  - AIGCBench 2024 [F];
  - Zhao et al., NeurIPS 2024 [A].
- **To verify before citing:** RAFT-on-river papers [S]; DIVID [S]; the FVMD angle formula; the Cetegen–Ahmed flicker prefactor [S]; the Physics-IQ background initialization (paper and code differ).

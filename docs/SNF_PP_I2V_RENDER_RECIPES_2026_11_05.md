# I2V render recipes for the public figure set

2026-11-05. This is a read-only audit of how the published I2V systems were run on this machine, followed by the render plan for the public-benchmark figure set (`manifest/public_figure_set_2026_11_05.json`). The renders are driven by `scripts/render_public_figure_set.py`. File evidence (paths and line numbers) is in the audit transcript; the key items are quoted here. Abbreviations: AIA = `/home/minar/ar-image-animation`, RF = `/home/minar/region-forcing`.

## Findings that affect existing tables

1. **`f2s_framewise` is not a released configuration.**
   - `scripts/registry.py` labels it "native … configs/framewise_native_i2v.yaml". That file does not exist; the name is a neutral alias.
   - The run used `RF/configs/causal_forcing_dmd_f2s_steady.yaml`, which turns on Steady-Forcing mechanisms: relativistic RoPE, EMA sink with compression 0.99, sink 3, local attention 21. All of them are active at inference.
   - Upstream Causal-Forcing states it "does not natively support videos longer than 81 frames" and that using the 5 s model as a long-video baseline is "extremely unfair".
   - "Native" therefore means native block size only. **Decision 2026-11-06:** keep the historical row as a separately labelled CF++ checkpoint with a Steady-Forcing-derived adaptation, not a released native configuration. The registry key and historical score identities are unchanged; the corrected registry label must not silently rewrite frozen published outputs.
2. **The CausVid and Self-Forcing I2V rows are wrappers.** Both ran with nfpb 6, the Steady-Forcing cache, and the CF++ 2-step schedule [1000, 500] for both checkpoints. That contradicts the registry text "checkpoint-specific denoising schedule".
3. **The Wan "native" rows used driver defaults, not the official command line.**

   | setting | used | official |
   |---|---|---|
   | Wan2.1 shift | 5.0 | 3.0 (i2v, 832×480) |
   | Wan2.2 guidance | 5.0 | (3.5, 3.5) |
   | output size (both) | 832×464 | — |

4. **Two runners are broken today.**
   - Helios: the `AIA/helios_baseline` symlink is broken; pinned commit `babed98` is absent from the shallow `/home/minar/Helios` clone; the bounded-streaming patch is missing.
   - The common runner (`AIA/tools/run_common_i2v.py`): its `causal_forcing/` and `self_forcing/` checkouts and its suite file are missing.
5. **Disk is nearly full.** `/` has 152 GB free; `/data4` has 0 B. AIA's 100 GiB guard leaves about 50 GB usable.
6. **The earlier "1/30 valid records" for CausVid and cf_framewise** came from metric runs, not generation. RAFT ran beside VBench and corrupted cuDNN, and orphaned processes ran out of memory. The records were since repaired in `raw/`. Rule: one RAFT process per GPU, and never VBench on a GPU that is running RAFT.

## Released recipes and cost

Costs are per clip on an uncontended GPU, taken from earlier runs.

| system | released recipe | horizon | cost | VRAM | runnable now |
|---|---|---|---|---|---|
| Causal-Forcing (frame-wise) | upstream README I2V command, `configs/causal_forcing_dmd_framewise.yaml`, `--i2v --use_ema`, 21 latent frames = 81 frames, seed 0 | 5 s | ~30 s | ~25 GB | **yes**; local checkout differs only in checkpoint paths |
| LTX-Video 13B 0.9.8 distilled | LTX `inference.py`, `ltxv-13b-0.9.8-distilled.yaml`, 121 frames at 24 fps | 5 s | ~110 s | n/a | yes. Prompts under 120 words switch on prompt enhancement (Florence-2 + Llama-3.2-3B, not cached). Plan: threshold 0, disclosed as a deviation |
| Wan2.1-I2V-14B-480P | official `generate.py` (shift 3.0 at 832×480, 81 frames) | 5 s | ~18–20 min | ~53 GB | yes |
| Wan2.2-I2V-A14B | official config (guidance 3.5/3.5, 40 steps, shift 5, boundary 0.9) | 5 s | ~25 min (T5 on GPU) | ~41–52 GB | yes |
| Helios-Distilled | `run_helios_nature.py`, 1441 frames at 24 fps, pad to 64 | 60 s | ~15–17 min | 46.6 GiB | **no**: needs `babed98` and the patch restored |
| SVI 2.0 Pro | `AIA/tools/run_svi_pro_native.py`, 12 clips × 81 frames, CFG 4, 50 steps | 60 s | 2.4–2.9 h | ~74 GB, a whole free GPU | only with a whole free GPU 2 or 3 |
| CF++ 1-/2-step upstream | upstream frame-wise 2-step config | 5 s | ~30 s | ~25 GB | needs the CF++ config; it is not in `/home/minar/Causal-Forcing` |

## Plan

1. **Causal-Forcing 5 s:** about 6 min for 12 scenes. It starts automatically once GPU 2 has no other compute processes, so it never runs beside the RAFT and VBench scorers.
2. **LTX 5 s, then Wan2.1 and Wan2.2 5 s:** about 4 h each for Wan, on GPU 2 or 3 when quiet.
3. **Long horizon (60 s), from released long modes only:** Helios after a repair in a new directory (never editing `/home/minar/Helios`), and SVI 2.0 Pro on a subset of about 4 scenes when a whole GPU is free.
4. Every output gets a sidecar recording:
   - code commit and local diff;
   - config and checkpoint hashes;
   - container ID, seed rule and prompt hash;
   - the GPU co-tenant snapshot and a concurrency flag.

   Renders are never overwritten.

## Completed renders

| system | horizon | scenes | GPU | contention | wall clock | output |
|---|---|---|---|---|---|---|
| Causal-Forcing (frame-wise), upstream `8e1ef8f`, released I2V command | 5 s (81 frames, 16 fps, 832×480) | 12/12 | 2 | none (`concurrent: false`) | 463 s for all 12, including model load | `videos/public_bench/renders/causal_forcing/5s/` + `RUN.json` |
| LTX-Video 13B 0.9.8 distilled, official `inference.py`, prompt enhancement off (disclosed) | 5 s (121 frames, 24 fps, 832×480) | 12/12 | 2 | none | 1042 s for all 12 | `videos/public_bench/renders/ltx_video/5s/` + `RUN.json` |

**What a first look shows** (contact sheet of first, middle and last frames; not a metric). Every prompt asks for a fixed tripod camera, yet within 5 s:
- the viewpoint pans or zooms in all four Physics-IQ tabletop scenes and on the Skógafoss waterfall;
- the church clouds saturate to black;
- the lighthouse wave disappears.

These are the failure modes the benchmark measures, now visible on licence-cleared sources.

**LTX prepared.**
- The PixArt-XL-2-1024-MS text encoder (19 GB) was cached only inside the exited `regfor_eval` container. It was copied, read-only, to `/home/minar/ckpt/hf_cache_ltx`, leaving 133 GB free on `/`.
- The render uses a copy of the released config with prompt enhancement off, recorded in the run as a deviation.
- It is queued after the geometry run on GPU 2.

**LTX against Causal-Forcing** (contact sheet of first, middle and last frames; not a metric):
- LTX holds the camera on the four tabletop scenes, where Causal-Forcing pans and zooms.
- LTX zooms or reframes on Iguazu, the kettle and the church. On the church it replaces the sky with a different, saturated cloudscape.
- Both lose the lighthouse wave after the first frame.

**Wan queued** (`wan21`, `wan22` in `scripts/render_public_figure_set.py`, driven per scene by `scripts/wan_official_loop.py`):
- official README single-GPU commands with `generate.py`/config defaults: Wan2.1 shift 3.0 at 832×480 and guidance 5.0; Wan2.2 guidance (3.5, 3.5), shift 5.0, boundary 0.9, `--offload_model True --convert_model_dtype`;
- deviations recorded: `--base_seed 0`, and 832×480 for Wan2.2 (a supported size; the README example is 1280×720);
- checkpoint directories are hashed as a tree;
- each starts with a one-scene smoke render (`--tag _smoke`). Wan2.1 waits for an idle GPU 3; Wan2.2 runs on GPU 2 after the geometry runs.

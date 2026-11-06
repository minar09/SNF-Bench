# Public-benchmark sources for figure images

2026-11-05. Rule set by the user on 2026-11-05: real photographs and footage in figures and comparisons come only from public benchmarks with a documented licence. Numerical evaluation in the tables stays on SNF-Bench++. Generated outputs from our own text prompts contain no third-party content and may be shown.

All licence texts below were read on the cited pages on 2026-11-05, except Pexels (see "Open").

## In use

| Figure | Item | Licence | Credit in caption |
|---|---|---|---|
| Fig. 1(a), role-map illustration | Physics-IQ scene 0140 (paper smoke), centre view, take 1, first frame; roles from the benchmark's official motion masks | CC BY 4.0 ("All other materials are licensed under the Creative Commons Attribution 4.0 International License", github.com/google-deepmind/physics-IQ-benchmark README, commit d3f3de16) | Physics-IQ \cite{motamed2025physicsiq}, scene 0140, © 2024 DeepMind Technologies Limited, CC BY 4.0; resized, with roles overlaid |

- Source files: `videos/public_bench/physics_iq/` (gitignored). They are fetched and hash-checked by `scripts/build_journal_snapshots.py`.
- SHA-256 values and URLs are in `figures/snapshots/SNAPSHOTS.json` under `role_illustration`.
- CC BY 4.0 requires the same credit and a licence link wherever the image is redistributed, including the supplementary pages.

## Candidates (ranked)

1. **Physics-IQ** (CC BY 4.0, public GCS bucket, no login). Every scene is filmed with a static camera and has an official motion mask.
   - The scenes are indoor tabletop, not outdoor nature.
   - Usable for flame, smoke and liquid flow: 0140 paper smoke, 0065 pouring, 0089 overfill, 0185 water in juice, 0110 match.
   - 0092 (candle) has an empty motion mask over its first 150 frames.
2. **VBench-I2V image suite** (Pexels licence read 2026-11-05; usable): the best content match, with outdoor waterfalls, waves at a lighthouse, clouds, a snowy street and campfires.
   - VBench adds no licence of its own. It says only "The images are sourced from Pexels and Pixabay", and each image has a `url` field in `i2v-bench-info.json` (local copy: `/home/minar/ar-image-animation/prompts/oos/vbench_i2v_download/`).
   - Candidates, all Pexels:

     | image | Pexels ID |
     |---|---|
     | lighthouse wave | 2683365 |
     | hillside waterfall | 161950 |
     | church under clouds | 14357872 |
     | snowy night street | 2385898 |
     | kettle on campfire | 10462563 |

3. **Xiph Derf `riverbed`** (TUM/Taurus 1080p; "Restrictions of use: No restrictions / Copyright: No Copyright").
   - Real 1080p water over pebbles, with almost no dry support.
   - The camera setup is not documented.

## Excluded

| source | reason |
|---|---|
| DynTex | CC BY-NC-SA 2.5 |
| UVG | CC BY-NC |
| Netflix Chimera/El Fuente | CC BY-NC-ND 4.0. ToddlerFountain would otherwise fit well. |
| BVI-DVC, HomTex | non-commercial government licence |
| SVT MultiFormat | standards-development use only |
| NTIA/ITS clips | research-only |
| Holynski Eulerian and CLAW | Storyblocks rights chain unclear |
| YUP++, I2V-Bench, AIGCBench real images | licence or provenance unclear |

IEEE is a commercial publisher, so non-commercial and no-derivatives licences are not used.

## Open

- **Pexels licence: resolved 2026-11-05.** The user read https://www.pexels.com/license/ in a browser and pasted it. Verbatim excerpts:
  - "All photos and videos on Pexels are free to use."
  - "Attribution is not required."
  - "You can modify the photos and videos from Pexels."
  - Not allowed:
    - "Identifiable people may not appear in a bad light or in a way that is offensive."
    - "Don't sell unaltered copies of a photo or video ... without modifying it first."
    - "Don't imply endorsement of your product by people or brands on the imagery."
    - "Don't redistribute or sell the photos and videos on other stock photo or wallpaper platforms."
    - "Don't use the photos or videos as part of your trade-mark ..."

  Pexels-sourced VBench-I2V images may therefore appear in figures and on supplementary pages. Captions still name VBench-I2V and the Pexels photo ID for traceability. Rules for using them:
  - Use only Pexels-sourced items. Pixabay content cannot be distributed "on a Standalone basis".
  - Avoid images with identifiable people.
  - Do not bulk-redistribute the original image files.
- **I2V comparison figure.** It would condition the published I2V systems on public-benchmark images such as Physics-IQ or VBench-I2V. That needs new renders on a GPU the user releases.
- **Benchmark release.** The 48 v2 I2V sources may be scored internally. A public release needs redistribution rights for each source, or must ship URLs and a fetch script instead. Only ifp05 (CC BY-SA 2.0) and ifp06 (CC BY 2.0) have recorded licences.

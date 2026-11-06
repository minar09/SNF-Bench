#!/usr/bin/env python3
"""Conditioning images and prompts for the public-benchmark I2V figure set.

Rule (user, 2026-11-05): real images shown in figures come only from public
benchmarks with a documented licence; tables stay on SNF-Bench++. This set
conditions the published I2V systems for visual comparisons. It is
exposure-logged visual material, not confirmation data
(manifest/realism_dev_split_2026_11_05_amendment_1.json).

Sources (licence audit: docs/SNF_PP_PUBLIC_VISUAL_SOURCES_2026_11_05.md):

* Physics-IQ (Motamed et al., WACV 2026), CC BY 4.0: the benchmark's own
  switch frames, centre view, fetched from its public bucket.
* VBench-I2V image suite (Huang et al., VBench++), Pexels-sourced items only,
  Pexels licence (read 2026-11-05): VBench's 7:4 crops from the dc-ai/vbench_i2v
  mirror, with the Pexels photo ID recorded.

Images are cropped and resized exactly as the v2 I2V pairs are
(build_i2v_pairs_v2.crop_and_write: widest 16:9 window placed for ORB texture,
then 832x480), and prompts go through the same compose() and validate().
Scene fields are transcribed from each image.

    /home/minar/miniconda3/envs/snfeval/bin/python scripts/build_public_figure_set.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_i2v_pairs_v2 as pairs   # noqa: E402
import build_prompts_v2 as bp        # noqa: E402

ROOT = os.path.dirname(HERE)
PUB = os.path.join(ROOT, "videos/public_bench")          # gitignored
OUT_IMG = os.path.join(PUB, "conditioning")
OUT_MAN = os.path.join(ROOT, "manifest/public_figure_set_2026_11_05.json")
PIQ = "https://storage.googleapis.com/physics-iq-benchmark/switch-frames/"
VB = "https://huggingface.co/datasets/dc-ai/vbench_i2v/resolve/main/crop/7-4/"

SOURCES = {
    "physics_iq": dict(benchmark="Physics-IQ (Motamed et al., WACV 2026)", licence="CC BY 4.0",
                       licence_url="https://creativecommons.org/licenses/by/4.0/",
                       credit="Copyright 2024 DeepMind Technologies Limited, CC BY 4.0"),
    "vbench_i2v": dict(benchmark="VBench-I2V image suite (Huang et al., VBench++)", licence="Pexels License",
                       licence_url="https://www.pexels.com/license/",
                       credit="Pexels photo, via VBench-I2V; attribution not required"),
}

# id, source, file, origin id, category, direction, setting, static support, dynamic medium, light
SCENES = [
    ("pq0092", "physics_iq", "0092_switch-frames_anyFPS_perspective-center_trimmed-lit-candle.jpg", "0092",
     "combustion", "upward", "Two red candles in brass holders on a wooden table",
     "The candlesticks, the brass holders, the table and the wall",
     "The flame on the left candle flickers, licking", "Soft indoor daylight"),
    ("pq0140", "physics_iq", "0140_switch-frames_anyFPS_perspective-center_trimmed-paper-smoke.jpg", "0140",
     "buoyant_plume", "upward", "A scrap of smouldering paper on a glass board on a wooden table",
     "The glass board, the table top and the back wall",
     "Thin grey smoke curls off the paper, rising", "Bright window sidelight"),
    ("pq0065", "physics_iq", "0065_switch-frames_anyFPS_perspective-center_trimmed-fill-glass-red-drink.jpg",
     "0065", "falling_water", "top to bottom", "A drinks dispenser pouring into a glass on a wooden table",
     "The dispenser jar, its wicker stand, the glass and the table",
     "A thin red stream runs from the tap into the glass", "Soft indoor daylight"),
    ("pq0089", "physics_iq", "0089_switch-frames_anyFPS_perspective-center_trimmed-liquid-overfill.jpg", "0089",
     "falling_water", "top to bottom", "An overfull glass under a dispenser tap in a baking tray",
     "The dispenser, the wicker stand, the glass and the metal tray",
     "Red juice spills over the glass rim and runs down its sides", "Soft indoor daylight"),
    ("vb161950", "vbench_i2v", "a large waterfall in the middle of a lush green hillside.jpg", "161950",
     "falling_water", "top to bottom", "A tall waterfall dropping from a green cliff onto a gravel plain",
     "The cliff faces, the grassy slopes and the gravel bank",
     "White water plunges from the lip into the pool", "Bright midday sun"),
    ("vb1236906", "vbench_i2v", "a view of a waterfall from a distance.jpg", "1236906",
     "falling_water", "top to bottom", "Several waterfalls pouring into a forested gorge",
     "The cliffs, the rock ledges and the far rim of the gorge",
     "Brown water pours over the ledges into the river below", "Hazy afternoon light"),
    ("vb2683365", "vbench_i2v", "a large wave crashes into a lighthouse.jpg", "2683365",
     "oscillatory_water", None, "A harbour lighthouse at the end of a stone pier in a storm",
     "The lighthouse tower, its hut and the pier wall",
     "Waves burst against the pier and throw up white spray", "Pale overcast light"),
    ("vb11117140", "vbench_i2v", "a large wave crashes over a rocky cliff.jpg", "11117140",
     "oscillatory_water", None, "Storm waves breaking over a rocky headland",
     "The dark rock shelf and the distant houses",
     "Waves surge over the rocks and drain back in foam", "Grey stormy light"),
    ("vb14357872", "vbench_i2v", "a church sits on top of a hill under a cloudy sky.jpg", "14357872",
     "windborne", None, "A hilltop church under a towering cloudy sky",
     "The church towers, its walls and the hilltop",
     "Large white clouds roll and billow across the sky", "Warm late-afternoon sun"),
    ("vb2385898", "vbench_i2v", "a city street at night during a snow storm.jpg", "2385898",
     "falling_precip", None, "A city street at night in a snowstorm",
     "The building fronts, the lampposts, the advertising pillars and the railings",
     "Snow falls steadily through the lamplight", "Night street lamps"),
    ("vb10462563", "vbench_i2v", "a kettle is sitting on top of a campfire.jpg", "10462563",
     "combustion", "upward", "A blackened kettle hanging over a small campfire",
     "The kettle, its hook stick, the logs and the stony ground",
     "Small flames lick around the burning log, rising", "Low warm sunlight"),
    ("vb1165991", "vbench_i2v", "a foggy road with trees in the distance.jpg", "1165991",
     "windborne", None, "A country road through fields in morning fog",
     "The road surface, its verge and the field edges",
     "Low fog creeps slowly over the fields", "Soft golden backlight"),
]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    os.makedirs(OUT_IMG, exist_ok=True)
    rows = []
    for sid, src, fname, origin, cat, direction, setting, static, dyn, light in SCENES:
        local = os.path.join(PUB, "physics_iq/switch_frames" if src == "physics_iq" else "vbench_i2v/crop_7-4", fname)
        if not os.path.exists(local):
            raise SystemExit(f"{sid}: missing {local}")
        dst = os.path.join(OUT_IMG, f"{sid}.jpg")
        geom = pairs.crop_and_write(local, dst)
        rows.append(dict(id=sid, category=cat, direction=direction, setting=setting, static_support=static,
                         dynamic_medium=dyn, light=light,
                         text=bp.compose((sid, cat, direction, setting, static, dyn, light)),
                         source=src, **SOURCES[src], origin_id=origin,
                         origin_url=(PIQ + fname if src == "physics_iq" else VB + fname),
                         pexels_url=(f"https://www.pexels.com/photo/{origin}/" if src == "vbench_i2v" else None),
                         source_sha256=sha256(local), image=os.path.relpath(dst, ROOT),
                         image_sha256=sha256(dst), **geom))
    errs, warns, _ = bp.validate(rows)
    for w in warns:
        print("warn:", w)
    if errs:
        raise SystemExit("\n".join(errs))
    rep = dict(created="2026-11-05", role="public-benchmark I2V figure set; exposure-logged visual material, "
                                          "not confirmation data",
               rule="real images in figures come only from licence-documented public benchmarks",
               split_amendment="manifest/realism_dev_split_2026_11_05_amendment_1.json",
               render=dict(width=pairs.RENDER_W, height=pairs.RENDER_H, crop="build_i2v_pairs_v2.crop_and_write"),
               scenes=rows)
    json.dump(rep, open(OUT_MAN, "w"), indent=1)
    for r in rows:
        print(f"{r['id']:11s} {r['category']:17s} orb={r['orb_at_render']:4d} {len(r['text'].split()):2d}w  {r['text']}")


if __name__ == "__main__":
    main()

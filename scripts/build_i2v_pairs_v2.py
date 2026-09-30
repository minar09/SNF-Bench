#!/usr/bin/env python3
"""Compose the v2 image-conditioned pair set: source image + matched prompt.

The T2V set is built from a declared scene table because the scene is whatever
we write.  I2V is the other way round -- the scene is given by the photograph and
the prompt must describe *that* frame.  So the scene fields here are transcribed
from the image rather than invented, but they go through the **same** `compose()`
and `validate()` as the T2V set, for one reason: every v1 defect the reviewers
objected to was worse on the I2V side.  The v1 I2V captions in
`prompts/i2v/60s/target_crop_info_16-9.json` run past 200 words, open with the
camera boilerplate, and carry both evaluator framing and explicit negation
("does not move, tilt, pan, or zoom at any point"), which is exactly the text a
77-token encoder truncates and a diffusion model mishandles.

Provenance of each image is recorded, and both pools were screened at the same
thresholds by `screen_i2v_images.py`.  That screen disqualified 9 of the 30 v1
images on croppability alone: the v1 I2V tier conditioned on frames that cannot
yield a 768x432 crop, so some of its source images were upscaled into the
render.  Reused v1 images are only those that clear the current bar.

Support texture is reported as ORB count on the delivered 832x480 crop -- what
the detector actually sees at render resolution.  It is deliberately not called
a support-region density: Omega_static is derived from early optical flow of the
generated video, which does not exist for a still, so no honest per-region
number is available before generation.

    ~/miniconda3/envs/snfeval/bin/python scripts/build_i2v_pairs_v2.py
"""

import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_prompts_v2 as bp
import screen_i2v_images as screen   # reuse its AVIF-capable decoder

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOLS = {
    "v2_extra": f"{ROOT}/prompts/v2/v2_images_extra",
    "v1": f"{ROOT}/prompts/i2v/60s/images",
    # Fetched from Wikimedia Commons with a recorded licence. These are the only
    # images in the set whose redistribution is unambiguous today.
    "commons": f"{ROOT}/prompts/v2/v2_images_commons",
}
OUT_IMG = f"{ROOT}/prompts/v2/i2v/images"
OUT_TXT = f"{ROOT}/prompts/v2/i2v/core.txt"
MAN = f"{ROOT}/manifest/i2v_pairs_v2.json"

RENDER_W, RENDER_H = 832, 480
MIN_ORB = 220                   # same floor screen_i2v_images.py applies

# Same stratum shares as the T2V set, at half the size: the two tracks must be
# comparable by category, and a reviewer must not be able to say the I2V balance
# was chosen after seeing which images happened to arrive.
I2V_TARGETS = {k: v // 2 for k, v in bp.TARGETS.items()}

# `compose()` appends the direction to the dynamic phrase verbatim, so every
# dynamic phrase ends where a direction reads grammatically -- a comma plus a
# participle, or a bare motion verb. "The surface rises up the gauge" + "upward"
# is the failure to avoid.
#
# (id, category, pool, file, direction, setting, static support, dynamic, light)
P = [
 # ---- channel_flow ---------------------------------------------------------
 ("icf01","channel_flow","v2_extra","gully-drain-grate.jpg","left to right",
  "A kerbside storm drain in a paved street",
  "The cast-iron grate, the kerbstones and the asphalt surface",
  "Runoff sheets across the road and pours through the grate, moving",
  "Flat overcast daylight"),
 ("icf02","channel_flow","v2_extra","farm-box-culvert.jpg","right to left",
  "A concrete box culvert beneath a farm track",
  "The culvert headwall, the track surface and the earth batter",
  "Silty water pushes through the culvert barrel, running",
  "Grey winter daylight"),
 ("icf03","channel_flow","v2_extra","river-rock-gorge.jpg","upper left to lower right",
  "A river running through a bedded rock gorge",
  "The cliff benches, talus blocks and the shoreline ledge",
  "The river slides between the walls, travelling",
  "Clear midday sun on pale rock"),
 ("icf04","channel_flow","v2_extra","boulder-rapids.jpg","top to bottom",
  "Rapids over a bed of dark boulders",
  "Midstream boulders, the bedrock sill and the far bank",
  "White water breaks between the rocks and runs",
  "Bright open daylight"),
 ("icf05","channel_flow","v2_extra","flooded-winter-river.jpg","left to right",
  "A river in flood past a bare winter bank",
  "The eroded bank, a timber shed and the roadway embankment",
  "Brown floodwater carries past the bank, running",
  "Low cloud, soft grey light"),
 ("icf06","channel_flow","v2_extra","field-drainage-sluice.jpg","top to bottom",
  "A concrete drainage sluice across open farmland",
  "The sluice walls, the headwall coping and the marker posts",
  "Channel water pushes through the opening, running",
  "Overcast afternoon"),
 # ---- falling_precip -------------------------------------------------------
 ("ifp01","falling_precip","v1","394189.jpg","top to bottom",
  "A track through conifer forest during snowfall",
  "The banked track, the verge and the slope behind",
  "Snow settles across the track, falling",
  "Low sun behind the treeline"),
 ("ifp02","falling_precip","v1","blur-close-up-color-1529360.jpg","top to bottom",
  "A wet street surface during a downpour",
  "The asphalt, the kerbstones and a brick facade behind",
  "Rain bursts on the standing water, falling",
  "Dim evening light, colour bokeh behind"),
 ("ifp03","falling_precip","v1",
  "silhouetted-cityscape-reflections-captured-in-raindrop-speckled-window-post-deluge-calm-photo.jpg",
  "top to bottom",
  "A city avenue seen through a rain-covered window",
  "The window glass, the sill and the building silhouettes beyond",
  "Raindrops gather on the glass and slide",
  "Dusk, warm vehicle lights below"),
 ("ifp04","falling_precip","v1","snowy-urban-street-stockcake.webp","downward and to the left",
  "A city street under steady snowfall",
  "Parked cars, lampposts, kerbs and the building fronts",
  "Snow crosses the street, falling",
  "Flat white daylight"),
 ("ifp05","falling_precip","commons",
  "Snow_falling_in_Bessborough_Place,_Pimlico_-_geograph.org.uk_-_2183294.jpg",
  "top to bottom",
  "A residential close under heavy snowfall",
  "Parked cars, the brick terraces, the kerb line and the lit windows",
  "Snow crosses the close, falling",
  "Dusk, warm window light on white ground"),
 ("ifp06","falling_precip","commons",
  "Snowy_Transit_in_Brooklyn_(12294431174).jpg",
  "top to bottom",
  "A rail cutting in heavy snow",
  "The running rails, the retaining wall, the parapet fence and a stopped train",
  "Snow sweeps down the cutting, falling",
  "Flat white daylight, low contrast"),
 # ---- oscillatory_water ----------------------------------------------------
 ("iow01","oscillatory_water","v1","tropical-background-ppg3kwadk2qn15jc.jpg",None,
  "A tropical shoreline with a shallow reef break",
  "The wet sand bar, the headland and a leaning palm trunk",
  "Low swell runs in and breaks along the shore",
  "Bright tropical midday"),
 ("iow02","oscillatory_water","v2_extra","groyne-shingle.jpg",None,
  "A timber groyne running down a shingle beach",
  "The groyne posts, the plank waling and the timber capping",
  "Surf washes in along the groyne and draws back",
  "Pale sunset over the water"),
 ("iow03","oscillatory_water","v2_extra","breakwater-beacon.jpg",None,
  "A concrete breakwater with a beacon at its head",
  "The breakwater deck, the beacon tower and the armour blocks",
  "Swell strikes the breakwater and bursts over the deck",
  "Grey sea light, wind-torn sky"),
 ("iow04","oscillatory_water","v2_extra","seawall-promenade.jpg",None,
  "A seafront promenade behind a sloping seawall",
  "The wall face, the railing stanchions and the paved walkway",
  "A wave climbs the wall and throws spray over the rail",
  "Overcast, cold spray light"),
 ("iow05","oscillatory_water","v2_extra","stepped-seawall.jpg",None,
  "A stepped concrete seawall along a sand beach",
  "The wall blocks, the joint lines and the beach at its foot",
  "The wash runs up the sand and slides back at the wall",
  "Bright sun, deep blue sky"),
 # ---- accumulating_level ---------------------------------------------------
 ("ial01","accumulating_level","v2_extra","quay-ladder-night.jpg","upward",
  "A harbour quay wall with an access ladder at night",
  "The concrete quay face, the steel ladder and the coping stones",
  "The basin surface climbs the wall face, moving",
  "City lights across the water"),
 ("ial02","accumulating_level","v2_extra","pier-ladder-green-water.jpg","upward",
  "A timber pier with a ladder into green water",
  "The deck planks, the timber pile and its lashing",
  "The water rises past the ladder rungs, moving",
  "Overcast, flat green water"),
 ("ial03","accumulating_level","v2_extra","dock-emergency-ladder.jpg","upward",
  "A floating dock with an emergency ladder and piles",
  "The dock decking, the yellow ladder and the concrete piles",
  "The surface rises against the piles, moving",
  "Soft daylight, low contrast"),
 ("ial04","accumulating_level","v2_extra","dam-level-gauge.jpg","upward",
  "A concrete dam face carrying a painted level gauge",
  "The dam wall, the gauge board and the crest walkway",
  "The reservoir surface climbs the gauge board, moving",
  "High sun, hard shadow on the wall"),
 ("ial05","accumulating_level","v2_extra","bellmouth-spillway.jpg","upward",
  "A bell-mouth spillway shaft in a reservoir",
  "The shaft rim, the concrete apron and the bank riprap",
  "The reservoir surface creeps toward the rim, moving",
  "Even overcast light"),
 # ---- buoyant_plume --------------------------------------------------------
 ("ibp01","buoyant_plume","v2_extra","geothermal-station-plumes.jpg","upward",
  "A geothermal power station on an upland plain",
  "The plant buildings, the pipe runs and the ridge behind",
  "Steam plumes leave the stacks, climbing",
  "Clear cold daylight"),
 ("ibp02","buoyant_plume","v2_extra","stack-plume-orange.jpg","upward",
  "Industrial chimney stacks against evening sky",
  "The stack shells, the gantry steelwork and the plant roofline",
  "Tinted plumes leave the stack mouths, lifting",
  "Late sun colouring the plume"),
 ("ibp03","buoyant_plume","v2_extra","twin-stacks-white.jpg","upward",
  "A row of works chimneys above a yard",
  "The chimney shafts, the yard fence and the works buildings",
  "Dense white vapour leaves every chimney, rising",
  "Bright sky, high contrast"),
 ("ibp04","buoyant_plume","v2_extra","manhole-steam-night.jpg","upward",
  "A steaming street vent in a city at night",
  "The wet roadway, the road markings and the building fronts",
  "Steam opens into the street from the vent, lifting",
  "Sodium lamps and neon signs"),
 ("ibp05","buoyant_plume","v2_extra","street-vent-stack.jpg","upward",
  "An orange-and-white venting stack on a city pavement",
  "The stack tube, safety barriers, kerbs and parked cars",
  "Steam leaves the stack head, streaming",
  "Overcast daylight between buildings"),
 ("ibp06","buoyant_plume","v2_extra","plantation-well-pads.jpg","upward",
  "A geothermal plant among terraced plantation slopes",
  "The plant housings, the access road and the hillside terraces",
  "Vapour columns leave the well pads, rising",
  "Hazy morning sun"),
 # ---- combustion -----------------------------------------------------------
 ("icb01","combustion","v2_extra","patio-fire-pit.jpg","upward",
  "A circular fire pit on a paved terrace",
  "The pit rim, the paving, the garden chairs and the house wall",
  "Flames leave the burning logs, reaching",
  "Late afternoon, warm on the paving"),
 ("icb02","combustion","v2_extra","burn-barrel-field.jpg","upward",
  "A steel burn barrel standing on open ground",
  "The barrel drum, its stand and the field margin behind",
  "Fire breaks from the open top, reaching",
  "Sunset, sky going orange"),
 ("icb03","combustion","v2_extra","paver-fire-ring.jpg","upward",
  "A paved fire ring with a single split log",
  "The ring casting, the paver slabs and the joint lines",
  "Flame wraps the log and climbs",
  "Overcast daylight"),
 ("icb04","combustion","v2_extra","rusted-burn-barrel.jpg","upward",
  "A rusted barrel burning on a field margin",
  "The corroded drum, its rim and the stubble ground",
  "Fire rolls over the rim of the drum, reaching",
  "Dull daylight"),
 ("icb05","combustion","v2_extra","rotary-kiln-discharge.jpg","left to right",
  "A rotary kiln discharge hood inside a works hall",
  "The kiln shell, the support rollers, the gantry frames and the floor",
  "Fire streams from the kiln mouth, travelling",
  "Dark hall lit by the burner"),
 # ---- windborne ------------------------------------------------------------
 ("iwb01","windborne","v2_extra","desert-dust-front.jpg","right to left",
  "A dust front crossing open desert",
  "The gravel plain, a rock outcrop and the low ridge",
  "The dust wall advances across the plain, moving",
  "Sun through the haze"),
 ("iwb02","windborne","v2_extra","haboob-roadside.jpg","left to right",
  "A dust wall reaching a roadside building",
  "The building facade, its parapet and the car park kerbs",
  "The haboob front rolls in, travelling",
  "Ochre light under the front"),
 ("iwb03","windborne","v1","menacing-dust-storm-stockcake.webp","right to left",
  "A dust storm over dry rangeland",
  "The rangeland ground and the low horizon line",
  "A brown curtain crosses the horizon, moving",
  "Sunlight filtered ochre"),
 ("iwb04","windborne","v1",
  "tree-resisting-wind-in-heavy-cloudy-stormy-weather-wallpaper-1920x1080_48.jpg",
  "left to right",
  "An exposed clifftop under a storm sky",
  "The rock shelf, the cliff edge and a weathered boulder",
  "Storm cloud drives across the sky, travelling",
  "Hard light breaking through the cover"),
 ("iwb05","windborne","v2_extra","barn-dust-wall.jpg","left to right",
  "A dust wall reaching a red barn on open farmland",
  "The barn, its roof line and the bare field",
  "The dust front advances behind the barn, moving",
  "Flat light beneath the front"),
 ("iwb06","windborne","v2_extra","road-dust-storm.jpg","right to left",
  "A dust storm closing over a suburban road",
  "The carriageway, the lamp columns and the kerb line",
  "The dust wall rolls across the road, travelling",
  "Ochre daylight dimming under the dust"),
 # ---- geothermal -----------------------------------------------------------
 ("igt01","geothermal","v2_extra","lava-over-basalt-crust.jpg","upper right to lower left",
  "An active lava flow over a cooled basalt crust",
  "The crust plates, the pressure ridges and lava blocks",
  "Molten rock creeps between the plates, moving",
  "Dusk, glow on the crust"),
 ("igt02","geothermal","v2_extra","sinter-apron-outflow.jpg","top to bottom",
  "A hot-spring outflow over an orange sinter apron",
  "The sinter terraces, the pool rim and bleached timber",
  "Hot water spreads down the apron, running",
  "Cold overcast, strong colour on the sinter"),
 ("igt03","geothermal","v2_extra","sulphur-fumarole.jpg","upward",
  "A fumarole in a sulphur-stained rock field",
  "The encrusted rocks, the vent rim and the slope behind",
  "Vapour jets from the vent, rising",
  "Overcast, yellow mineral tones"),
 ("igt04","geothermal","v2_extra","terrace-steam-vent.jpg","upward",
  "A steam vent on a bare geothermal terrace",
  "The pale terrace ground, a rock shelf and the far ridge",
  "A steam jet leaves the vent, rising",
  "Bright thin sunlight"),
 # ---- falling_water --------------------------------------------------------
 ("ifw01","falling_water","v2_extra","downpipe-pebble-bed.jpg","top to bottom",
  "A downpipe discharging onto a pebble bed",
  "The pipe, the wall render, the bracket and the pebble bed",
  "Water leaves the pipe for the stones, falling",
  "Overcast, wet surfaces"),
 ("ifw02","falling_water","v2_extra","bellmouth-intake-spillway.jpg","top to bottom",
  "A dam spillway with bell-mouth intakes",
  "The spillway deck, the intake rings and the parapet",
  "Water spills over the rings into the shafts, falling",
  "Overcast, flat light on concrete"),
 ("ifw03","falling_water","v2_extra","gated-spillway-discharge.jpg","top to bottom",
  "A gated concrete spillway under discharge",
  "The gate piers, the bridge deck and the chute walls",
  "Water leaves the gates for the stilling basin, falling",
  "Bright daylight, spray catching the sun"),
 ("ifw04","falling_water","v2_extra","culvert-outfall-apron.jpg","top to bottom",
  "A culvert outfall below a concrete abutment",
  "The abutment face, the outfall lip and the apron slab",
  "A jet leaves the outfall for the apron, falling",
  "Dull daylight"),
 ("ifw05","falling_water","v2_extra","scalloped-canal-weir.jpg","top to bottom",
  "A scalloped overflow weir along a canal wall",
  "The weir crest, the scallop lip and the tiled bank",
  "Water tips over the crest to the lower channel, falling",
  "Even daylight on still water"),
]


# Offsets tried along whichever axis has slack, as a fraction of that slack.
CROP_OFFSETS = (0.0, 0.25, 0.5, 0.75, 1.0)


def _orb(bgr):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return len(cv2.ORB_create(nfeatures=3000).detect(gray, None))


def crop_and_write(src, dst):
    """Widest 16:9 crop, placed to keep the most ORB texture.

    A centred crop is the obvious choice and it is wrong here. On the roadside
    haboob frame the centre window lands entirely on the dust wall and drops to
    31 keypoints at render size, below the threshold at which fBD abstains --
    which is how a v1 dust-storm scene came to abstain across all seven systems.
    The support is usually off-centre in these photographs, so the window is
    placed by the same detector the metric uses. The chosen offset is recorded
    so the placement is auditable rather than a hidden preprocessing choice.
    """
    img = screen.decode(src, open(src, "rb").read())
    if img is None:
        raise SystemExit(f"undecodable: {src}")
    h, w = img.shape[:2]
    cw, ch = min(w, int(round(h * 16 / 9))), min(h, int(round(w * 9 / 16)))
    interp = cv2.INTER_AREA if cw >= RENDER_W else cv2.INTER_CUBIC

    best = None
    for f in CROP_OFFSETS:
        x, y = int(round((w - cw) * f)), int(round((h - ch) * f))
        out = cv2.resize(img[y:y + ch, x:x + cw], (RENDER_W, RENDER_H),
                         interpolation=interp)
        n = _orb(out)
        if best is None or n > best[0]:
            best = (n, f, out)
        if (w - cw) == 0 and (h - ch) == 0:
            break                      # already 16:9, nothing to place
    n, f, out = best
    cv2.imwrite(dst, out, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return {"source_wh": [w, h], "crop_wh": [cw, ch],
            "crop_offset": f,
            "upscale": round(RENDER_W / cw, 3),
            "upscaled": bool(cw < RENDER_W),
            "orb_at_render": n}


def resolve(pool, want):
    """Screened filenames are opaque; match on the recorded sha1 index instead."""
    return os.path.join(POOLS[pool], want)


def main():
    # `alias` maps a pair id to the opaque filename its image arrived under;
    # the review is consulted so a pair can never reference an image the visual
    # pass rejected, or one filed under a different category.
    sel = json.load(open(f"{ROOT}/manifest/i2v_image_review.json"))
    review = {r["file"]: r for r in sel["rows"]}
    alias = json.load(open(f"{ROOT}/manifest/i2v_pair_sources.json"))
    lic_path = f"{POOLS['commons']}/licences.json"
    licences = json.load(open(lic_path)) if os.path.exists(lic_path) else {}

    os.makedirs(OUT_IMG, exist_ok=True)
    rows = []
    for pid, cat, pool, fname, direction, setting, static, dyn, light in P:
        real = alias.get(pid, fname) if pool == "v2_extra" else fname
        if pool == "v2_extra":
            r = review.get(real)
            if r is None or r["review"] == "reject":
                raise SystemExit(f"{pid}: {real} is not a reviewed survivor")
            if r["category"] != cat:
                raise SystemExit(f"{pid}: review files {real} under "
                                 f"{r['category']}, pair claims {cat}")
        src = resolve(pool, real)
        if not os.path.exists(src):
            raise SystemExit(f"{pid}: missing source {src}")
        dst = os.path.join(OUT_IMG, f"{pid}.jpg")
        geom = crop_and_write(src, dst)
        rows.append({"id": pid, "category": cat, "direction": direction,
                     "setting": setting, "static_support": static,
                     "dynamic_medium": dyn, "light": light,
                     "text": bp.compose((pid, cat, direction, setting, static,
                                         dyn, light)),
                     "pool": pool, "source_file": real,
                     "licence": licences.get(real, {}).get("licence"),
                     "licence_source": licences.get(real, {}).get("source"),
                     "attribution": licences.get(real, {}).get("artist"),
                     "image": os.path.relpath(dst, ROOT), **geom})

    bp.TARGETS = I2V_TARGETS          # validate() reports coverage against these
    errs, warns, counts = bp.validate(rows)

    print(f"pairs: {len(rows)}   categories: {len(counts)}")
    shortfall = {}
    for cat, want in I2V_TARGETS.items():
        have = counts[cat]
        if have < want:
            shortfall[cat] = want - have
        print(f"  {cat:20s} {have:3d} / {want}"
              f"{'   SHORT ' + str(want - have) if have < want else ''}")
    low = [r for r in rows if r["orb_at_render"] < MIN_ORB]
    ups = sorted((r["upscale"], r["id"]) for r in rows if r["upscaled"])
    ws = sorted(len(r["text"].split()) for r in rows)
    print(f"\nwords: min {ws[0]} median {ws[len(ws)//2]} max {ws[-1]}"
          f"  (~CLIP tokens median {int(ws[len(ws)//2]*1.3)})")
    print(f"ORB at {RENDER_W}x{RENDER_H}: min {min(r['orb_at_render'] for r in rows)}"
          f"   below {MIN_ORB}: {[r['id'] for r in low] or 'none'}")
    print(f"crops upscaled to render size: {len(ups)}"
          f"   worst x{ups[-1][0] if ups else 1.0}")
    from collections import Counter
    print("pool: " + ", ".join(f"{k} {v}" for k, v in
                               Counter(r["pool"] for r in rows).items()))
    lic = sum(1 for r in rows if r.get("licence"))
    print(f"licence recorded: {lic}/{len(rows)}"
          f"   unlicensed: {len(rows) - lic}")

    if errs:
        print(f"\nVALIDATION FAILED ({len(errs)}):")
        for e in errs[:25]:
            print(f"  {e}")
        return 1
    print("\nvalidation: clean (no evaluator text, no metric vocabulary, no "
          "negation, static/dynamic disjoint, within word budget)")
    if shortfall:
        print("\nOUTSTANDING IMAGE NEED (target minus built):")
        for c, n in shortfall.items():
            print(f"  {c:20s} {n}")

    with open(OUT_TXT, "w") as f:
        for r in rows:
            f.write(r["text"] + "\n")
    json.dump({"version": "v2.0-draft", "n": len(rows),
               "render": [RENDER_W, RENDER_H],
               "targets": I2V_TARGETS, "counts": dict(counts),
               "shortfall": shortfall, "pairs": rows},
              open(MAN, "w"), indent=2)
    print(f"\n-> {OUT_TXT}\n-> {MAN}\n-> {OUT_IMG}/ ({len(rows)} crops)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

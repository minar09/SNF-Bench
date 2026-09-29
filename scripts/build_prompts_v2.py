"""Compose the v2 benchmark prompt set from a declared scene table.

Why this is code and not a text file. Three WACV reviewers objected that the v1
curation procedure was unspecified: how prompts were authored, why channel water
reached 61%, and which declared stratum was empty (it was lava, with zero items).
A generated set makes the procedure auditable and the balance a parameter.

Four defects in the v1 text are fixed here by construction:

  1. **Evaluator instructions were inside the prompts.** v1 240s prompts contain
     "Evaluators must inspect the segment from frame 5,800 onward for attention
     collapse ... exhaustion of positional encoding support". That text was fed
     to the generator as conditioning. Banned by the validator.
  2. **Metric vocabulary was inside the prompts** -- "no flicker", "no waves",
     "temporal continuity across all frames". A model that follows instructions
     then scores well for instruction-following rather than capability, and
     diffusion models handle negation poorly, so "no waves" can produce waves.
     Only positive description is allowed.
  3. **Moving vegetation was named as static support.** One v1 prompt asks trees
     to sway while the benchmark treats vegetation as static support, so the
     partition is wrong before any model runs. Static support and dynamic medium
     are now disjoint and checked.
  4. **Length.** v1 prompts run to a median ~127 CLIP tokens with the shared
     camera boilerplate first and the scene specifics last, so a 77-token
     encoder truncates exactly the differentiating content. v2 targets <=70
     words with the scene first.

Taxonomy is by **transport regime** rather than scene type, because that is what
the benchmark measures and what the v2 motion-intent axis needs: a one-way
channel has a scorable direction, an oscillatory swell does not, and penalising
a wave cycle with a one-way rule would be a measurement error.

    ~/miniconda3/envs/snfeval/bin/python scripts/build_prompts_v2.py
"""

import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{ROOT}/prompts/v2"
MAN = f"{ROOT}/manifest"

# Target share per transport regime. Channel water is capped at ~12% because it
# was 61% of the v1 primary tier and that single fact drew three reject votes.
TARGETS = {"channel_flow": 12, "falling_precip": 12, "oscillatory_water": 10,
           "accumulating_level": 10, "buoyant_plume": 12, "combustion": 10,
           "windborne": 12, "geothermal": 8, "falling_water": 10}

# Direction vocabulary. `None` means transport direction is not scorable for this
# scene and the motion-intent axis must abstain rather than guess.
DIRS = {"left to right", "right to left", "top to bottom", "upward",
        "downward and to the left", "upper left to lower right",
        "upper right to lower left", None}

# (id, category, direction, setting, static support, dynamic medium, light)
S = [
 # ---- channel_flow: one-way water in a channel, direction scorable ----------
 ("cf01","channel_flow","top to bottom","A granite mountain stream in a rural valley","Boulders, mossy banks and a fallen log","Clear water runs over the stones, travelling","Bright daylight through the valley"),
 ("cf02","channel_flow","upper left to lower right","A lowland river beneath a concrete road bridge","The bridge deck, steel railings and the far bank","The river slides past, carrying faint ripples","Overcast midday, muted greys"),
 ("cf03","channel_flow","left to right","An irrigation canal between flooded rice paddies","Earth embankments, a sluice post and distant sheds","Silty water moves along the canal","Low afternoon sun, warm side light"),
 ("cf04","channel_flow","right to left","A stone-walled city waterway with shallow rapids","Cut-stone walls, an iron footbridge and kerb copings","Fast water breaks white over a submerged sill, running","Golden late light across the surface"),
 ("cf05","channel_flow","top to bottom","A forest creek crossing a bed of pebbles","Roots, grey boulders and the shaded bank","Shallow water threads between the stones, moving","Dappled light through the canopy"),
 ("cf06","channel_flow","top to bottom","A weir spillway on a broad river","The concrete weir crest, wing walls and handrail","A smooth sheet of water leaves the crest and travels","Flat grey storm light"),
 ("cf07","channel_flow","left to right","A rectangular storm drain channel between retaining walls","Poured concrete walls, a steel access ladder and grating","Brown runoff pushes along the invert","Dim streetlight from above"),
 ("cf08","channel_flow","top to bottom","A glacial meltwater braid on a grey gravel flat","Gravel bars, a boulder train and the moraine ridge","Pale meltwater spreads through the braids, running","Hard high-altitude noon light"),
 ("cf09","channel_flow","right to left","A mangrove tidal creek on the ebb","Aerial roots, a timber landing and the far mud bank","Tea-coloured water draws out along the creek","Humid overcast, flat green tones"),
 ("cf10","channel_flow","left to right","A millrace beside an old stone mill","The mill wall, timber sluice frame and stone coping","Water runs the length of the race","Early morning, long shadows"),
 ("cf11","channel_flow","upper right to lower left","A desert wadi carrying silt after rain","Rock ledges, a gravel terrace and the canyon wall","Ochre floodwater advances down the wadi","Late sun, deep orange on rock"),
 ("cf12","channel_flow","top to bottom","A highland peat burn over dark stones","Peat banks, lichen-covered rock and a fence post","Amber water slides across the stones","Thin overcast, cool light"),
 # ---- falling_precip: downward through frame, static support behind ---------
 ("fp01","falling_precip","downward and to the left","A city street at night in heavy rain","Shopfronts, parked cars, kerbstones and lampposts","Rain falls in dense streaks and strikes the asphalt, drifting","Sodium streetlight, wet reflections"),
 ("fp02","falling_precip","top to bottom","A village lane during monsoon rain","Tin roofs, a brick wall and a concrete step","Rain descends steadily and bursts on the roofs","Grey daylight, heavy cloud"),
 ("fp03","falling_precip","top to bottom","A greenhouse glass roof seen from inside","Glazing bars, roof trusses and staging benches","Rain runs down the glass in rivulets, moving","Diffuse white daylight"),
 ("fp04","falling_precip","top to bottom","A residential street at night during snowfall","Parked cars, lampposts, railings and rooftops","Snow descends in slow flakes","Warm lamplight against dark sky"),
 ("fp05","falling_precip","downward and to the left","A stone courtyard in heavy snowfall","Flagstones, an arched doorway and a well head","Snow crosses the courtyard as it falls, drifting","Flat blue dusk light"),
 ("fp06","falling_precip","top to bottom","Sleet against a brick wall and an iron gate","Brickwork, the gate, its hinges and a stone sill","Sleet slants past the wall and rattles on the gate","Cold overcast, low contrast"),
 ("fp07","falling_precip","top to bottom","Rain on a flagstone temple forecourt","Flagstones, a stone lantern and timber posts","Rain falls across the forecourt and pocks the stone","Soft rainy daylight"),
 ("fp08","falling_precip","downward and to the left","Rain over a harbour quay","Bollards, mooring rings, the quay edge and a crane base","Rain sweeps over the quay as it falls, drifting","Grey marine light"),
 ("fp09","falling_precip","top to bottom","Snow onto a wooden footbridge","Bridge planks, handrails and the stone abutment","Snow settles as it falls past the rail","Dim blue afternoon"),
 ("fp10","falling_precip","top to bottom","Rain through the cone of a streetlight","The lamp standard, pavement slabs and a wall base","Rain crosses the lit cone and lands on the pavement","Single warm light source"),
 ("fp11","falling_precip","top to bottom","Snow over a field of stone grave markers","Stone markers, a low wall and a gravel path","Snow drops between the markers","Pale winter overcast"),
 ("fp12","falling_precip","downward and to the left","Rain onto terracotta rooftops from a fixed window","Roof tiles, a chimney stack and a parapet","Rain strikes the tiles and runs, drifting","Storm daylight, heavy grey"),
 # ---- oscillatory_water: cyclic, direction NOT scorable --------------------
 ("ow01","oscillatory_water",None,"A sandy beach with small surf","A timber groyne, scattered shells and a distant rock","Low waves roll in and withdraw at the shoreline","Low sun, warm gold"),
 ("ow02","oscillatory_water",None,"A rocky headland meeting open swell","Boulders, a rock shelf and the headland ridge","Swell rises against the rock and falls back","Bright hazy daylight"),
 ("ow03","oscillatory_water",None,"A harbour basin with wind chop","The quay wall, a ladder and moored fenders","Short chop slaps the wall and rebounds","Overcast marine light"),
 ("ow04","oscillatory_water",None,"A tidal rock pool","Pool rims, barnacled rock and weed-covered stone","The pool surface lifts and settles","Clear midday, hard light"),
 ("ow05","oscillatory_water",None,"A lake shore of coarse shingle","Shingle, a timber post and the far shore","Wavelets advance and retreat over the stones","Still morning, soft light"),
 ("ow06","oscillatory_water",None,"A sea cliff above a rock shelf","Cliff face, shelf edge and a weathered stack","Waves burst on the shelf and drain away","Flat storm light, spray haze"),
 ("ow07","oscillatory_water",None,"Pier pilings in passing swell","Timber pilings, cross braces and the deck underside","Swell passes the pilings, lifting and dropping","Shadowed underdeck light"),
 ("ow08","oscillatory_water",None,"An estuary mudflat under light wind","Mud banks, a channel marker and a stone groyne","Small wind waves run over the shallows and subside","Wide pale overcast"),
 ("ow09","oscillatory_water",None,"A concrete breakwater taking regular sets","Breakwater blocks, a light column and the harbour arm","Sets arrive against the blocks and recede","Late gold on the water"),
 ("ow10","oscillatory_water",None,"A fjord shoreline against granite slabs","Granite slabs, a boathouse footing and the far wall","Water laps the slabs and falls back","Cool high-latitude daylight"),
 # ---- accumulating_level: slow monotone rise -------------------------------
 ("al01","accumulating_level","upward","A flooded street beside a raised kerb","Kerbstones, a railing base, a bollard and shopfronts","Standing water climbs the kerb as the level builds, moving","Overcast, flat reflection"),
 ("al02","accumulating_level","upward","A flat stone bench during steady snowfall","The bench slab, its legs and the paving behind","Snow depth builds on the slab, rising","Cold blue daylight"),
 ("al03","accumulating_level","upward","A stone slipway on a rising tide","Slipway steps, a mooring ring and the sea wall","Water covers the steps one by one, advancing","Soft marine overcast"),
 ("al04","accumulating_level","upward","A carved stone basin filling with rain","The basin rim, its pedestal and the wall behind","Water level in the basin climbs","Grey rainy light"),
 ("al05","accumulating_level","upward","A brick wall carrying an old flood watermark","Brick courses, the watermark line and an air brick","Floodwater rises up the brickwork","Dim storm daylight"),
 ("al06","accumulating_level","upward","A parked car roof in continuous snowfall","The roof panel, window frames and a wall behind","Snow builds on the roof, deepening","Night lamplight"),
 ("al07","accumulating_level","upward","A concrete dam face as the reservoir fills","The dam face, a gauge plate and the abutment","The reservoir surface rises against the concrete","High bright overcast"),
 ("al08","accumulating_level","upward","A paddy field filling from an inlet","Bund walls, the inlet pipe and a marker stake","Water spreads across the field and deepens","Warm low sun"),
 ("al09","accumulating_level","upward","A frozen lake edge with meltwater pooling","Ice shelf, a rock outcrop and the bank","Meltwater collects at the edge and deepens","Thin spring sunlight"),
 ("al10","accumulating_level","upward","A harbour ladder as the tide comes in","Ladder rungs, the quay face and a mooring cleat","Water rises past the rungs","Overcast dockside light"),
 # ---- buoyant_plume: upward and dispersing --------------------------------
 ("bp01","buoyant_plume","upward","A street food stall with a charcoal grill","The stall frame, signage, baskets and the wall behind","Smoke leaves the grill and climbs, spreading","Warm daylight, soft shade"),
 ("bp02","buoyant_plume","upward","A tiled roof with a domestic chimney","Roof tiles, the chimney stack and a TV aerial","Smoke issues from the stack and rises","Cold clear morning"),
 ("bp03","buoyant_plume","upward","A manhole venting steam in a night street","The manhole ring, kerb, road surface and a hydrant","Steam pushes up from the opening and thins","Streetlight and headlight glow"),
 ("bp04","buoyant_plume","upward","A hot spring vent among wet rock","Rock terraces, mineral crust and a timber walkway","Steam lifts off the water and drifts upward","Overcast, pale steam-lit"),
 ("bp05","buoyant_plume","upward","Incense burning in a stone shrine alcove","The alcove, stone censer, offerings and a step","Incense smoke threads upward","Shaded interior, warm point light"),
 ("bp06","buoyant_plume","upward","A field burn seen beyond a boundary wall","The wall, a gate post and a distant hedgerow line","Smoke lifts from the field and climbs","Hazy afternoon sun"),
 ("bp07","buoyant_plume","upward","A laundry vent on a brick side wall","Brickwork, the vent cowl, a downpipe and a window sill","Vapour leaves the cowl and rises","Overcast alley light"),
 ("bp08","buoyant_plume","upward","A volcanic fumarole on an ash slope","Ash beds, a sulphur crust and a lava block","Vapour vents from the ground and ascends","Harsh high sun"),
 ("bp09","buoyant_plume","upward","A hot road steaming after rain","Asphalt, a kerb, a drain cover and a low wall","Steam lifts off the road surface","Bright sun after storm"),
 ("bp10","buoyant_plume","upward","A brick kiln stack in a yard","The stack, kiln shed and stacked bricks","Smoke rises from the stack head","Dusty warm daylight"),
 ("bp11","buoyant_plume","upward","A cooling tower above a concrete plinth","The tower shell, plinth and pipe gantry","Vapour rises from the tower rim and spreads","Cool morning, blue cast"),
 ("bp12","buoyant_plume","upward","A campfire between granite boulders","Boulders, a fire ring of stones and a log seat","Smoke climbs from the fire and disperses","Dusk, warm firelight"),
 # ---- combustion: local chaotic, direction NOT scorable -------------------
 ("cb01","combustion",None,"A debris fire in a walled yard at night","Brick walls, a steel door and broken pavers","Flames work over the pile and shift in place","Firelight against darkness"),
 ("cb02","combustion",None,"A hearth fire in a stone fireplace","The stone surround, iron grate and hearthstone","Flames move among the logs","Interior firelight"),
 ("cb03","combustion",None,"A charcoal brazier on a pavement","The brazier body, its legs and paving slabs","Coals glow and flames lick upward in place","Evening, low ambient light"),
 ("cb04","combustion",None,"A bonfire on a shingle beach","Shingle, a ring of stones and a driftwood pile","Flames climb and fold over the fire","Blue dusk, strong firelight"),
 ("cb05","combustion",None,"A gas flare on a metal stack","The stack, its ladder and guard rails","The flame streams and flutters at the tip","Night, isolated flame light"),
 ("cb06","combustion",None,"A bank of candles in a stone alcove","The alcove, candle stand and stone floor","Candle flames waver","Dim interior, warm points"),
 ("cb07","combustion",None,"Burning brush beside a dirt track","The track, a fence line and bare earth","Flames spread through the brush and toss","Smoky afternoon light"),
 ("cb08","combustion",None,"An oil-drum fire under a concrete overpass","The drum, concrete piers and the deck above","Flames rise from the drum mouth and toss","Deep shadow, orange glow"),
 ("cb09","combustion",None,"Wood stove flames behind a glass door","The stove body, door frame and hearth plate","Flames turn over the logs","Dark room, contained glow"),
 ("cb10","combustion",None,"Embers in a stone fire pit ring","Ring stones, gravel and a metal poker","Embers pulse and brighten in place","Late night, faint red light"),
 # ---- windborne: vegetation and particulates are the DYNAMIC medium -------
 ("wb01","windborne","left to right","A flat desert plain in a dust event","Rock outcrops, a fence post and the horizon ridge","Dust sheets across the plain, travelling","Bleached low-contrast sun"),
 ("wb02","windborne","downward and to the left","A park path during cherry blossom fall","Benches, stone paving, lampposts and a wall","Petals leave the branches and travel, moving","Bright spring sunlight"),
 ("wb03","windborne","right to left","A stone plaza in autumn wind","Paving, a fountain basin rim and building bases","Dry leaves skitter across the plaza, running","Low golden afternoon"),
 ("wb04","windborne","left to right","A dune crest under steady wind","The dune's rock core, a marker stake and far ridge","Sand streams off the crest, carried","Hard sidelight, sharp shadow"),
 ("wb05","windborne",None,"A pine canopy on a hillside in a gale","The forest floor, rock outcrops and a boundary wall","Branches and needles thrash and recoil","Dark storm light"),
 ("wb06","windborne",None,"A row of poplars in strong steady wind","The road surface, a wall and the poplar trunks","Crowns bend and spring back repeatedly","Overcast, flat light"),
 ("wb07","windborne","left to right","A field of dry grass under wind","A stone wall, a gate and a telegraph pole","Waves run through the grass heads, travelling","Warm evening light"),
 ("wb08","windborne","downward and to the left","Blossom against a temple wall in wind","The wall, its tiled coping and a stone step","Blossom tumbles along the wall, drifting","Soft overcast"),
 ("wb09","windborne","left to right","A ridge line with snow spindrift","Rock teeth, a cairn and the ridge crest","Spindrift lifts off the ridge and streams","Cold bright alpine sun"),
 ("wb10","windborne","left to right","A city skyline under moving cloud","Rooftops, water tanks, masts and parapets","Cloud crosses the sky above the roofline, travelling","Changing daylight"),
 ("wb11","windborne",None,"A reed bed beside a stone jetty","The jetty, its stone blocks and mooring post","Reeds lean and rise again","Still overcast"),
 ("wb12","windborne",None,"A bamboo grove in gusting wind","A stone path, a lantern and the grove floor","Culms sway and rebound","Green filtered daylight"),
 # ---- geothermal: slow viscous / venting ----------------------------------
 ("gt01","geothermal","left to right","A lava channel crossing dark cooled rock","Cooled crust ridges, a rock bluff and older flow lobes","Incandescent lava advances along the channel","Night, self-lit orange"),
 ("gt02","geothermal",None,"A lava fountain at a vent","The vent rim, spatter cone and surrounding crust","Molten spatter throws up and falls back","Dark sky, intense glow"),
 ("gt03","geothermal","upward","An ash column above a crater rim","The crater rim, scree slopes and a boulder field","Ash rises from the vent and builds upward","Grey daylight through haze"),
 ("gt04","geothermal",None,"A bubbling mud pool in a thermal field","Mud rims, silica crust and a boardwalk edge","Mud domes swell and collapse","Overcast, steam-diffused"),
 ("gt05","geothermal","top to bottom","A lava toe creeping onto an old road","Road asphalt, a kerb and a road sign post","A lava lobe pushes forward over the asphalt","Dusk, glow on the road"),
 ("gt06","geothermal","upward","A fumarole venting ash on a slope","The slope surface, rock blocks and a survey marker","Ash puffs from the vent and lifts","Flat volcanic haze"),
 ("gt07","geothermal","left to right","A pahoehoe lobe spreading over crust","Older crust, a levee edge and a rock island","The lobe inflates and creeps outward","Night, orange rim light"),
 ("gt08","geothermal",None,"A boiling geyser pool before eruption","The pool rim, sinter terraces and a fence rail","The pool surface heaves and drops","Bright steamy daylight"),
 # ---- falling_water: vertical fall plus spray -----------------------------
 ("fw01","falling_water","top to bottom","A multi-tier waterfall into a plunge pool","Cliff ledges, wet rock walls and a fallen trunk","Water drops tier to tier and strikes the pool","Overcast, soft diffuse"),
 ("fw02","falling_water","top to bottom","A cliff cascade throwing spray","The cliff face, a rock apron and a railing","Water falls the face and bursts at the base","Bright hazy sun"),
 ("fw03","falling_water","top to bottom","A weir overfall forming a smooth sheet","The weir lip, wing walls and stilling basin edge","Water leaves the lip and falls as a sheet","Flat grey light"),
 ("fw04","falling_water","top to bottom","An urban fountain overflowing its bowl","The bowl, pedestal, surrounding paving and kerb","Water spills the rim and falls to the basin","Midday sun, hard sparkle"),
 ("fw05","falling_water","top to bottom","A spring emerging and falling over rock","The rock face, moss shelves and a boulder","Water issues from the rock and drops","Shaded forest light"),
 ("fw06","falling_water","top to bottom","A downspout discharging onto flagstones","The downpipe, wall, bracket and flagstones","Water leaves the spout and falls to the stone","Rainy overcast"),
 ("fw07","falling_water","top to bottom","A veil waterfall in dense forest","Rock walls, fern shelves and a log","A thin veil of water descends the rock","Green shade, soft light"),
 ("fw08","falling_water","top to bottom","A dam spillway chute under discharge","The chute walls, piers and the crest structure","Water accelerates down the chute and falls","Bright open daylight"),
 ("fw09","falling_water","top to bottom","A cave waterfall into a dark pool","Cave walls, a rock ledge and the pool rim","Water falls from the opening into the pool","Single shaft of daylight"),
 ("fw10","falling_water","top to bottom","A stepped cascade in a stone garden","Cut stone steps, coping and a gravel border","Water steps down the cascade","Calm morning light"),
]

BANNED_METRIC = re.compile(
    r"\b(flicker|stagnat|drift|artifact|artefact|reset|jump|wobble|"
    r"temporal continuity|dynamic degree|attention collapse|rope|kv cache|"
    r"identity collapse|colour garbage|color garbage|seamless|uninterrupted)\b", re.I)
BANNED_EVAL = re.compile(r"\b(evaluator|evaluators|must inspect|inspect the|"
                         r"compare .*seconds|frame \d{3,})\b", re.I)
NEGATION = re.compile(r"\b(no|not|never|without|nor|none|avoid|remain unchanged|"
                      r"does not|doesn't|cannot)\b", re.I)
# Entities that can move under wind, flow or combustion. None of these may be
# declared static support.
MOBILE = ["vegetation", "foliage", "tree", "trees", "branch", "branches", "leaf",
          "leaves", "reed", "reeds", "grass", "bamboo", "canopy", "shrub",
          "bush", "blossom", "petal", "petals", "flag", "smoke", "flame",
          "flames", "water", "wave", "waves", "snow", "sand", "dust", "cloud",
          "steam", "vapour", "lava", "ash", "mud", "ember", "embers"]

# Compound nouns that contain a mobile word but name something rigid.
RIGID_COMPOUNDS = ["flagstone", "flagstones", "watermark", "water tank",
                   "water tanks", "mud bank", "mud banks", "mud rim", "mud rims",
                   "ash bed", "ash beds", "lava block", "lava lobe", "lava lobes",
                   "snow line", "sand bar", "sandstone"]

MAX_WORDS = 70


def compose(sc):
    _id, cat, direction, setting, static, dynamic, light = sc
    dyn = dynamic if direction is None else f"{dynamic} {direction}"
    return f"{setting}. A fixed tripod camera, unmoving. {static} hold their positions. {dyn}. {light}."


def validate(rows):
    errs, warns = [], []
    seen_text = {}
    for r in rows:
        i, t = r["id"], r["text"]
        if BANNED_EVAL.search(t):
            errs.append(f"{i}: evaluator instruction in prompt")
        m = BANNED_METRIC.search(t)
        if m:
            errs.append(f"{i}: metric vocabulary '{m.group(0)}' in prompt")
        n = NEGATION.search(t)
        if n:
            errs.append(f"{i}: negation '{n.group(0)}' in prompt")
        w = len(t.split())
        if w > MAX_WORDS:
            errs.append(f"{i}: {w} words exceeds {MAX_WORDS}")
        if r["direction"] not in DIRS:
            errs.append(f"{i}: unknown direction {r['direction']!r}")
        # The v1 bug was a *mobile* entity listed as static support: one prompt
        # asked trees to sway while the benchmark scored vegetation as static
        # support, so the partition was wrong before any model ran. Naming a
        # rigid surface that the medium acts on ("rain strikes the tiles") is
        # correct grounding and must not be flagged, so test the static list
        # against entities that can actually move rather than testing overlap.
        sl = r["static_support"].lower()
        for comp in RIGID_COMPOUNDS:      # "flagstones" is not a flag
            sl = sl.replace(comp, " ")
        moving = sorted({m for m in MOBILE if re.search(rf"\b{m}\b", sl)})
        if moving:
            errs.append(f"{i}: mobile entity in static support: {moving}")
        if t in seen_text:
            errs.append(f"{i}: duplicate text of {seen_text[t]}")
        seen_text[t] = i
    counts = Counter(r["category"] for r in rows)
    for cat, want in TARGETS.items():
        if counts[cat] != want:
            warns.append(f"category {cat}: {counts[cat]} scenes, target {want}")
    return errs, warns, counts


def main():
    ids = [s[0] for s in S]
    assert len(ids) == len(set(ids)), "duplicate scene ids"
    rows = [{"id": s[0], "category": s[1], "direction": s[2], "setting": s[3],
             "static_support": s[4], "dynamic_medium": s[5], "light": s[6],
             "text": compose(s)} for s in S]
    errs, warns, counts = validate(rows)

    print(f"scenes: {len(rows)}   categories: {len(counts)}")
    tot = sum(counts.values())
    for cat in TARGETS:
        n = counts[cat]
        print(f"  {cat:20s} {n:3d}  {100*n/tot:5.1f}%")
    chan = 100 * counts['channel_flow'] / tot
    scorable = sum(1 for r in rows if r["direction"] is not None)
    print(f"\nchannel water share: {chan:.1f}%  (v1 primary tier was 61%)")
    print(f"direction scorable : {scorable}/{len(rows)}"
          f"  ({len(rows)-scorable} abstain by design)")
    ws = sorted(len(r["text"].split()) for r in rows)
    print(f"words: min {ws[0]} median {ws[len(ws)//2]} max {ws[-1]}"
          f"  (~CLIP tokens median {int(ws[len(ws)//2]*1.3)})")

    if warns:
        print("\nwarnings:")
        for w in warns:
            print(f"  {w}")
    if errs:
        print(f"\nVALIDATION FAILED ({len(errs)}):")
        for e in errs[:25]:
            print(f"  {e}")
        return 1
    print("\nvalidation: clean (no evaluator text, no metric vocabulary, no "
          "negation, static/dynamic disjoint, within word budget)")

    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/core.txt", "w") as f:
        for r in rows:
            f.write(r["text"] + "\n")
    json.dump({"version": "v2.0-draft", "n": len(rows),
               "targets": TARGETS, "counts": dict(counts),
               "channel_water_share": round(chan, 1),
               "direction_scorable": scorable, "scenes": rows},
              open(f"{MAN}/prompts_v2.json", "w"), indent=2)
    print(f"-> {OUT}/core.txt")
    print(f"-> {MAN}/prompts_v2.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())

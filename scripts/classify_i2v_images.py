#!/usr/bin/env python3
"""Join the mechanical screen with a visual content review of every screened image.

`screen_i2v_images.py` decides whether a file is *usable* (resolution, texture,
saturation, duplication).  It cannot decide whether the picture shows the
phenomenon a category needs.  This script carries the visual pass: one label per
screened image, recorded by contact-sheet index so the judgement is auditable
against `scratchpad/sheets/index.json`.

Verdicts
  select  -- goes into the candidate pool for its category
  backup  -- usable but weaker (thin flow, framing, or provenance doubt);
             drawn on only if a category is short
  reject  -- content is outside the benchmark's scope; `reason` says why

Reject reasons
  render          synthetic / architectural visualisation, not a photograph
  ai              generative-model output or implausible colour grading
  watermark       stock-agency mark or camera overlay burned into the frame
  studio          product, macro or black-background shot with no scene support
  composite       two images in one frame, or a scene pasted into an interior
  long_exposure   silky water: the motion field is pre-averaged in the still
  off_scope       phenomenon the benchmark does not cover
  no_flow         nothing in the frame is moving fast enough to score
  trivial         technically fine but too little happening to be a prompt
"""
import json
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEETS = os.environ.get(
    "SNF_SHEET_DIR",
    "/tmp/claude-1011/-home-minar-snf-bench/"
    "07702d2a-73f2-4054-a1a5-4e036f9394b1/scratchpad/sheets",
)

# filename -> (verdict, category_or_reason, note). Keyed by name, not by
# contact-sheet position, so re-running the screen (which renumbers the sheet
# when survivors are added or dropped) cannot silently reassign a judgement.
REVIEW = {
    "03_equinox_16-10.jpg":
        ("reject", "render", "aerial architectural visualisation of a park"),
    "0f62dcd859db9ab82043275c6b818a05.jpg":
        ("select", "falling_water", "rain-chain downspout over garden pebbles"),
    "1000_F_2150261476_Py9sWVmzWl89jpHu26h4cjsjtHuLPazO.jpg":
        ("backup", "geothermal", "steam vent on barren ground; faint edge credit"),
    "1080x1080.webp":
        ("reject", "long_exposure", "silky cascade"),
    "197653-14969841.webp":
        ("select", "accumulating_level", "quay ladder and concrete wall at night"),
    "1_3df9c913-a564-4741-a52b-08a9e11f03fc.webp":
        ("select", "falling_water", "garden rock cascade"),
    "1_9d452d64-528d-4cc6-87b1-bb7b49e83e2d.jpg":
        ("select", "channel_flow", "planted garden stream over boulders"),
    "20030816-1725_DAS_large_1.jpg":
        ("select", "geothermal", "lava flow through cracked black crust"),
    "20200615-shutterstock_1756860194.jpg":
        ("backup", "falling_water", "downspout onto grass, top-down framing"),
    "20230307-full-steam-ahead-unearthing-power-geothermal-milgro-13995.jpg":
        ("select", "geothermal", "geyser column on a flat plain"),
    "20241004142954839_IAVUYXN8.jpg":
        ("reject", "off_scope", "fireworks"),
    "2310CC001-2-768x1024.jpg":
        ("select", "falling_water", "garden waterfall beside a house"),
    "233532-825-auto.webp":
        ("reject", "long_exposure", "silky forest stream"),
    "36209216475_fd0f35e506_b.jpg":
        ("select", "geothermal", "hot-spring runoff with steam over sinter"),
    "5472.webp":
        ("select", "geothermal", "branching lava flow, aerial"),
    "61csnM4u-LL._AC_UF894,1000_QL80_.jpg":
        ("select", "accumulating_level", "dock ladder on a timber pier"),
    "64608ff880c1eb001db43d84.jpg":
        ("reject", "long_exposure", "silky Skogafoss"),
    "6511cd70c3ea656101973d93_CCID-SiloLongCrestedWeir.png":
        ("select", "channel_flow", "concrete fish-pass weir in a field"),
    "71nby47myyr51.jpg":
        ("reject", "no_flow", "footbridge in fog, no moving medium"),
    "71yog4EaOVL._AC_UF894,1000_QL80_.jpg":
        ("reject", "studio", "dyed blue flame on black"),
    "74c8f2b2-df4b-4135-a8f1-73c2e74b20b0.jpg":
        ("reject", "ai", "generative watermark burned in"),
    "81NoKBHne1L._AC_UF894,1000_QL80_.jpg":
        ("select", "combustion", "patio fire pit with furniture"),
    "8a071de665c54c9395976f53c5f118d5.jpg":
        ("reject", "render", "urban riverside visualisation"),
    "8aj6umqgayrh1.jpg":
        ("backup", "channel_flow", "dark woodland stream, low contrast"),
    "9248_Curb-Guard-Plus_LIME-GREEN-scaled.jpg":
        ("reject", "trivial", "kerb gutter with a garden hose"),
    "98916065_1768439755937525_r.webp":
        ("backup", "combustion", "structure fire; disaster framing"),
    "AdobeStock_2023005374-gutter-downspout.webp":
        ("select", "falling_water", "downspout discharging onto pebbles"),
    "Annapolis+First+Set+07+039.webp":
        ("select", "accumulating_level", "emergency dock ladder and pilings"),
    "Bermuda-Triangle-Sapona-1024x1024.jpg.webp":
        ("backup", "accumulating_level", "derelict pier, calm sea"),
    "Brant_Broughton_Gauging_Station_-_geograph.org.uk_-_166904.jpg":
        ("select", "channel_flow", "concrete drainage sluice"),
    "C0VonJNrJgD9ZoYTtI0MUJtPSgiyddjDDeplpUP-piHEsAWfTvqV3cMISFiRCZlxLIt8jRTuJCqLq_31yODLOA.webp":
        ("select", "geothermal", "onsen pool with steam and snow"),
    "CDL-1841002_Brass-Chamberstick-Candle-Set-of-2_SSC-20.jpg":
        ("reject", "studio", "candle pair on a table"),
    "Candleburning.jpg":
        ("reject", "studio", "candle flame on black"),
    "Coffee_at_Christmas_(Unsplash).jpg":
        ("reject", "off_scope", "coffee cup in a living room"),
    "Don-Thomas-Michele-Sabad-_-HMS-Vixen.jpg":
        ("reject", "no_flow", "wreck in a calm lagoon"),
    "GettyImages-485878338-95d60d608ce24881a422e3de6512a38c.jpg":
        ("reject", "studio", "match lighting a candle, macro"),
    "GettyImages_624719836.webp":
        ("select", "windborne", "dust storm front over desert"),
    "HR_2.jpg":
        ("reject", "render", "bridge visualisation"),
    "Harbour_1,_South_Shields,_South_Tyneside,_Tyne_and_Wear,_England.jpg":
        ("backup", "accumulating_level", "boatyard slipway, weak surface motion"),
    "Hertford-scaled.webp":
        ("select", "channel_flow", "box culvert under a farm track, muddy"),
    "How-to-Make-a-Burn-Barrel_0013-scaled.jpeg":
        ("select", "combustion", "burn barrel on grass"),
    "Kalapana-Lava-Lobe-FOR-WEBSITE.jpg":
        ("select", "geothermal", "lava lobes on black crust"),
    "Kiln_interior_with_fire.jpg":
        ("select", "combustion", "glowing furnace mouth"),
    "Kolufossar-2-1-1024x683.webp":
        ("select", "falling_water", "wide ledge waterfall in pasture"),
    "Krafla_geothermal_power_station_wiki.jpg":
        ("select", "geothermal", "steam vents in snow, backlit"),
    "NesjavellirPowerPlant_edit2.jpg":
        ("select", "buoyant_plume", "geothermal plant plumes"),
    "Overflow_section_of_top_of_weir_from_the_rear.jpg":
        ("select", "accumulating_level", "buttress dam with intake tower"),
    "Pamukkale-Denizli-Turkey-GettyImages-539479634.webp":
        ("select", "geothermal", "travertine terraces at sunset"),
    "Star-Shaped-Spillway-Armania.webp":
        ("select", "falling_water", "spillway with bell-mouth intakes"),
    "Untitled-design-14-1.jpg":
        ("backup", "channel_flow", "planted pond, little surface motion"),
    "VentedFireRing_lifestyle1_2000x.webp":
        ("select", "combustion", "round fire pit with burning log"),
    "YELL-roaring-mountain.jpg":
        ("select", "geothermal", "steam over a dark lava field"),
    "aquascape-medium-pondless-waterfall-kit-16ft-stream-aquasurge-pump-feature-1000__71831.jpg":
        ("reject", "long_exposure", "silky rock cascade"),
    "autumn-creek-bridge-stockcake.jpg":
        ("select", "channel_flow", "autumn rapids under a timber bridge"),
    "bermuda-triangle.jpg":
        ("reject", "render", "ocean whirlpool composite"),
    "bermuda-triangle.webp":
        ("reject", "render", "tornado composite"),
    "black bridge flooding.png":
        ("reject", "watermark", "'Camera 02' overlay on flooded track"),
    "brown-muddy-river-water-flowing-over-concrete-dam-turbulent-flood-rushing-down-weir-rapid-current-silt-foam-451449949.webp":
        ("backup", "channel_flow", "eroding mud bank, flat light"),
    "c42569b8-35a6-400f-9cba-b4bc09814842_1920x1440.jpg":
        ("select", "windborne", "dust wall approaching a building"),
    "caption (1).jpg":
        ("select", "falling_water", "river weir below a village"),
    "caption (2).jpg":
        ("select", "falling_water", "town weir, wide spill"),
    "caption (3).jpg":
        ("select", "geothermal", "hot-spring pool with sinter rim"),
    "caption.jpg":
        ("select", "falling_water", "stepped weir below a town"),
    "catchbasin1.webp":
        ("select", "channel_flow", "storm-drain grate taking runoff"),
    "clean-water-pouring-chrome-faucet-modern-bathroom-sink-pure-fresh-flowing-hygiene-cleanliness-concept-household-387286955.webp":
        ("reject", "studio", "bathroom tap, product framing"),
    "concrete-outlet-directs-flowing-water-expelled-basin-beneath-wooden-structure-overflow-weir-spilling-drain-square-bordered-453332057.webp":
        ("select", "accumulating_level", "timber plunge pool overflowing"),
    "cup-hot-coffee-foam-sharp-focus-foam-coffee-beans-scattered-background-burlap-background-beautiful-light-photo-345328512.webp":
        ("reject", "studio", "coffee cup with beans"),
    "downspout-edit-4aa-winner_orig.jpg":
        ("select", "falling_water", "downspout splash, close framing"),
    "downspout.webp":
        ("select", "falling_water", "brick-wall downspout onto lawn"),
    "ecc0e40a-d448-49c6-840f-0c2a7b701f77.jpg":
        ("backup", "buoyant_plume", "steaming pool, tight crop"),
    "f2c0bdf2-b0cc-47a8-b976-e1e681427fb2.jpg":
        ("select", "falling_water", "bamboo spout feeding an onsen"),
    "fd84f587e029ceb61e0d0edcce82c0f9.webp":
        ("reject", "composite", "stream scene pasted behind an interior"),
    "forest-bridge-scene-stockcake.jpg":
        ("select", "channel_flow", "forest stream and arched footbridge"),
    "gauge-plate-staff-gauge.jpg":
        ("select", "accumulating_level", "dam face with painted level gauge"),
    "great-falls-mather-gorge-1.webp":
        ("select", "channel_flow", "river through a rock gorge"),
    "how-to-build-a-wood-kiln-for-ceramics-with-an-oil-barrel-burning.jpg":
        ("select", "combustion", "rusted burn barrel alight"),
    "images (100).jpg":
        ("select", "falling_water", "low dam over a boulder river"),
    "images (25).jpg":
        ("select", "falling_water", "plunge waterfall with mist"),
    "images (3).jpg":
        ("backup", "oscillatory_water", "mangrove waterline; support is vegetation only"),
    "images (30).jpg":
        ("select", "falling_water", "travertine cascade curtain"),
    "images (31).jpg":
        ("reject", "ai", "implausible magenta foliage grading"),
    "images (32).jpg":
        ("select", "falling_water", "gorge waterfall with bedded walls"),
    "images (33).jpg":
        ("select", "falling_water", "stepped town weir, second view"),
    "images (34).jpg":
        ("select", "accumulating_level", "buttress dam and reservoir"),
    "images (36).jpg":
        ("select", "falling_water", "downspout onto gravel bed"),
    "images (37).jpg":
        ("select", "falling_water", "house downspout under storm sky"),
    "images (4).jpg":
        ("reject", "watermark", "'dreamstime.com' banner"),
    "images (44).jpg":
        ("select", "falling_water", "spillway gates discharging"),
    "images (45).jpg":
        ("select", "accumulating_level", "bell-mouth spillway in a reservoir"),
    "images (53).jpg":
        ("reject", "render", "whirlpool visualisation"),
    "images (54).jpg":
        ("select", "channel_flow", "rocky river rapids"),
    "images (56).jpg":
        ("select", "channel_flow", "canyon rapids"),
    "images (6).jpg":
        ("select", "accumulating_level", "gated barrage structure"),
    "images (60).jpg":
        ("reject", "off_scope", "lawn sprinkler"),
    "images (7).jpg":
        ("backup", "channel_flow", "flood debris against an old bridge"),
    "images (77).jpg":
        ("select", "buoyant_plume", "stack plume, orange"),
    "images (78).jpg":
        ("select", "buoyant_plume", "stack plume, white"),
    "images (84).jpg":
        ("backup", "combustion", "wildfire at night; no rigid support"),
    "images (85).jpg":
        ("reject", "studio", "fire on black"),
    "images (86).jpg":
        ("reject", "studio", "flame on black"),
    "images (87).jpg":
        ("select", "buoyant_plume", "steam from a street manhole at night"),
    "images (89).jpg":
        ("select", "buoyant_plume", "striped steam stack in a street"),
    "images (9).jpg":
        ("backup", "channel_flow", "misty bridge over a river"),
    "images (91).jpg":
        ("select", "buoyant_plume", "steam burst on pavement"),
    "images (96).jpg":
        ("select", "geothermal", "travertine terraces"),
    "images (97).jpg":
        ("select", "channel_flow", "forest stream over rocks"),
    "images - 2026-09-29T171520.140.jpg":
        ("select", "buoyant_plume", "onsen steam among autumn leaves"),
    "images - 2026-09-29T171536.470.jpg":
        ("backup", "geothermal", "onsen with pagoda; heavy grading"),
    "images - 2026-09-29T171550.799.jpg":
        ("select", "geothermal", "steaming blue hot pool"),
    "images - 2026-09-29T172029.509.jpg":
        ("select", "combustion", "galvanised burn barrel on grass"),
    "images - 2026-09-29T172110.933.jpg":
        ("select", "combustion", "brazier in snow at dusk"),
    "images - 2026-09-29T172405.207.jpg":
        ("select", "combustion", "hearth fire, interior"),
    "images - 2026-09-29T172411.897.jpg":
        ("select", "combustion", "brick fireplace alight"),
    "images - 2026-09-29T172710.535.jpg":
        ("select", "geothermal", "fissure lava lines, aerial"),
    "images - 2026-09-29T172749.016.jpg":
        ("reject", "watermark", "photographer credit burned in"),
    "images - 2026-09-29T172814.831.jpg":
        ("reject", "watermark", "agency logo burned in"),
    "images - 2026-09-29T172819.672.jpg":
        ("select", "geothermal", "lava lake ring, aerial"),
    "images - 2026-09-29T172922.488.jpg":
        ("select", "geothermal", "fumarole over sulphur-stained rock"),
    "images - 2026-09-29T173127.677.jpg":
        ("select", "geothermal", "steaming geothermal field"),
    "images - 2026-09-29T173135.929.jpg":
        ("select", "buoyant_plume", "geothermal station plumes in a valley"),
    "images - 2026-09-29T173642.637.jpg":
        ("reject", "watermark", "site credit on a thermal pool"),
    "iuujmrdzl3411.jpg":
        ("select", "buoyant_plume", "roadworks steam vent at night"),
    "jubilee-river-weir-windsor-england-23660032.webp":
        ("select", "falling_water", "river weir with moored boat"),
    "karolinenwehr-weir-four-stepped-overfall-weir-landsberg-am-lech-at-CR1A9Y.jpg":
        ("reject", "watermark", "'alamy' tile"),
    "l-intro-1677611187.jpg":
        ("reject", "studio", "tea poured into a glass"),
    "large.jpg":
        ("select", "geothermal", "steaming thermal lake"),
    "las-dos-hermanas.jpg":
        ("select", "falling_water", "jungle waterfall"),
    "left-sprinkler-outside-during-a-storm-and-now-it-doesnt-v0-jn4ljlqdm8xg1.webp":
        ("reject", "off_scope", "lawn sprinkler"),
    "luminous-earth-kilauea-episode-44-hawaii.jpg":
        ("select", "geothermal", "lava fountain"),
    "main_image_1765165624_69364a38e150f.webp":
        ("reject", "composite", "kiln and oven side by side"),
    "main_image_1765171357_6936609dbc66a.webp":
        ("select", "combustion", "rotary kiln discharge"),
    "main_image_1765176046_693672ee6e623.webp":
        ("select", "combustion", "cement-plant kiln flame"),
    "main_image_1765176239_693673af96718.webp":
        ("select", "combustion", "rotary kiln, close view"),
    "nicola-river-from-rail-bridge-1280x640.jpg":
        ("select", "channel_flow", "flooded river through bare trees"),
    "nw-fumerole.webp":
        ("select", "geothermal", "fumarole jet over sulphur ground"),
    "old-wooden-bridge-over-pond-run-creek-dave-sandt.jpg":
        ("reject", "long_exposure", "silky stream under a bridge"),
    "overflow-water-weir-dam-exists-naturally-rainy-season-37934482.webp":
        ("select", "falling_water", "brown water over a concrete weir"),
    "p7140465.jpg":
        ("backup", "channel_flow", "cobble creek bed, thin flow"),
    "pexels-makayla-asuncion-2155237133-33894758.jpg":
        ("select", "channel_flow", "small cascade over rocks"),
    "product-grp-ladders-in-marina-environments.webp":
        ("select", "accumulating_level", "marina ladder against a pontoon"),
    "product-grp-ladders-rescue-and-emergency.webp":
        ("select", "accumulating_level", "marina ladder with sailboats"),
    "rocky-bottom-with-frothy-stream-of-water-flowing-under-wooden-bridge-through-gloomy-forest-in-mountains-in-cloudy-day-in-dolomites-italy-2CF9AHG.jpg":
        ("reject", "watermark", "'alamy' tile"),
    "room38.jpg":
        ("reject", "composite", "waterfall mural in a rendered interior"),
    "room41.jpg":
        ("reject", "composite", "waterfall mural in a rendered interior"),
    "seljalandsfoss-iceland-1-WATERFALLS1021-e9c2348a42c841d5b9d661d16dcdcf8c.jpg":
        ("backup", "falling_water", "waterfall landscape, heavy grading"),
    "shutterstock_2519533361.webp":
        ("select", "buoyant_plume", "plant plumes over a tea estate"),
    "square-stainless-steel-fire-ring-by-hpc-fire-lifestyle.webp":
        ("select", "combustion", "gas fire pit on a patio"),
    "start-your-day-right-with-a-steaming-hot-cup-of-coffee-or-tea-in-a-bright-and-sunny-space-photo.jpg":
        ("reject", "watermark", "'Vecteezy' tile"),
    "steaming-coffee-cup-wooden-table-sunrise-sits-weathered-bathed-warm-glow-creating-cozy-inviting-atmosphere-386415948.webp":
        ("reject", "watermark", "'dreamstime' tile"),
    "steps-next-to-mediteranean-2358166.webp":
        ("backup", "accumulating_level", "stone stair into a calm sea"),
    "stringio.jpg":
        ("select", "falling_water", "cantilevered house over a waterfall"),
    "travertine-hot-spring-california-HOTSPRINGSUS1020-9ccad160d3c84d47bc5c7b2e6fe4cd6a.jpg":
        ("select", "geothermal", "travertine pool over a rock lip"),
    "travertine-hot-springs-in-the-us.jpg":
        ("select", "geothermal", "sinter cone and hot pool"),
    "water-ramp-outflow.jpg":
        ("select", "falling_water", "culvert outfall onto concrete"),
    "weir-overflow-rate.webp":
        ("select", "falling_water", "scalloped overflow weir on a canal"),
    # Recovered by the Pillow fallback: AVIF the screen first read as
    # undecodable. Two more AVIF files decode but fail the crop bar.
    "321089861_695349371971696_4660676862073690088_n.avif":
        ("backup", "combustion", "building fire from street windows; emergency scene"),
    "99531041.cms":
        ("select", "buoyant_plume", "geothermal wellhead stacks venting over a ridge"),
    "Fire-Pit-Ring-Liner-Outdoor-DIY-Campfire-Wood-Burning-Fire-Pit-Ring-3mm-Thick-Heavy-Duty-Solid-In-Ground-Metal-Smokeless-Firepit-Rim-Insert-Bonfire-P_ca07c9fc-dbec-41aa-bf7b-45.avif":
        ("select", "combustion", "corten fire ring in woodland"),
    "social.avif":
        ("select", "falling_water", "cantilevered house over a snowbound fall"),
    # ---- round 2 upload (83 files, 47 new survivors) ----
    "1603565972_8.jpg":
        ("backup", "oscillatory_water", "boat on a glassy shallow flat; heavy grading"),
    "1655648195177.png":
        ("backup", "oscillatory_water", "aerial beach with a thin surf line"),
    "1_9hBGvMKiTzhG2KYS9T7TlQ.jpg":
        ("reject", "composite", "snowflake graphic overlaid on a winter scene"),
    "1d95c7_f8e8226afcad40f99a766e6bfd7d764d~mv2.avif":
        ("select", "oscillatory_water", "timber groyne posts with surf on shingle"),
    "2023-duststorm_1.jpg":
        ("select", "windborne", "dust wall behind a red barn"),
    "3422c558-4cb5-4e05-89f6-8a98de33a521_rw_1920.jpg":
        ("select", "oscillatory_water", "waves breaking over a breakwater beacon"),
    "40a9a107-d17f-469d-b476-22dbf0f510af.JPG":
        ("backup", "oscillatory_water", "boats on a calm tidal flat"),
    "41586_2012_Article_BFnature201210100_Figa_HTML.jpg":
        ("backup", "falling_precip", "rain on a leaf, dark ground; journal-figure provenance"),
    "59203949-6f59-41af-a069-c3afa543c242_rw_1920.jpg":
        ("backup", "oscillatory_water", "same breakwater as the selected frame"),
    "68dc7cd1b33543b0bbca60e9c5f2c127.webp":
        ("select", "windborne", "dust storm crossing a desert road"),
    "921bdde3ebd941a600fcf3c4b8cbc85b.jpg":
        ("backup", "falling_precip", "rain through foliage; support is vegetation only"),
    "Bruning-City-Apocalypse-Concept.jpg":
        ("reject", "render", "burning-city concept art"),
    "EXT_POST_APOCALYPTIC_STREET_DAY.jpg":
        ("reject", "render", "burning-ruins concept art"),
    "Gemini_Generated_Image_ou3ve8ou3ve8ou3v.webp":
        ("reject", "ai", "Gemini-generated dust storm"),
    "Hopes-High-Next-Phase-Of-Bali-Uluwatu-Sea-Wall-Project-To-Be-Started-By-Tourist-High-Season-.jpg":
        ("select", "oscillatory_water", "surf against a rock point"),
    "Mangrove-forest-and-shallow-waters.-Credit-Apomares-GettyImages-scaled-1.jpg":
        ("backup", "oscillatory_water", "mangrove roots at the waterline"),
    "Mangrove_Forest_in_Kuakata_Sea_Beach_Patuakhali_Bangladesh_(4).jpg":
        ("reject", "no_flow", "still mangrove swamp"),
    "Shape of water drop.webp":
        ("backup", "falling_precip", "drops on glass over a wet deck; backdrop stock shot"),
    "U-754-24.jpg":
        ("backup", "oscillatory_water", "breaking wave, open water with no support"),
    "Wind-borne-debris-forest-damage-scaled.jpg":
        ("backup", "windborne", "wind-bent trees on a ridge"),
    "attachment-153.png":
        ("reject", "no_flow", "met-ocean buoy; the buoy itself moves"),
    "autumn-leaves-falling-stockcake.jpg":
        ("reject", "off_scope", "blurred falling leaves"),
    "bigstock-207061999-dust-storm-1024x683.jpg":
        ("select", "windborne", "dust storm over a road with lampposts"),
    "bright-blue-full-moon-at-night-the-sky-is-clear-at-the-pine-forest-on-the-mountain-snow-at-the-beginning-of-winter-and-there-are-reflections-on-the-water-3d-rendering-video.jpg":
        ("reject", "composite", "oversized moon over water"),
    "cherry-blossom-petals-falling-into-lake-at-sunset-with-pink-trees-photo.jpeg":
        ("reject", "ai", "cherry petals on water, generated"),
    "down-to-earth_import_library_large_2021-12-22_0.31772000_1640155114_rain.avif":
        ("backup", "falling_precip", "rain off an umbrella edge, macro"),
    "heavy-rain-splashing-on-the-ground.jpg":
        ("reject", "trivial", "blurred gravel bank, no subject"),
    "images - 2026-09-30T101609.006.jpg":
        ("reject", "studio", "single drop ripple"),
    "images - 2026-09-30T101723.341.jpg":
        ("backup", "channel_flow", "autumn forest above a rocky shore"),
    "images - 2026-09-30T102249.898.jpg":
        ("select", "windborne", "palms bending in a storm over a town"),
    "img_3867.webp":
        ("reject", "no_flow", "flat calm beach"),
    "mArKEcSLQdjFWjbos9KjXW.jpg":
        ("reject", "render", "apocalyptic city concept art"),
    "maniava-waterfall-falling-precipitous-cliff-ledge-ukrainian-carpathians-layered-structure-end-narrow-395204391.webp":
        ("select", "falling_water", "waterfall over a cliff face"),
    "northern-end-completed-orewa-seawall-path.webp":
        ("select", "oscillatory_water", "surf lines along a seawall promenade"),
    "p2759081374-4.jpg":
        ("backup", "oscillatory_water", "boat on a beach with surf"),
    "palm-trees-in-windstorm-scaled.jpg":
        ("select", "windborne", "palms in a windstorm, monochrome"),
    "pexels-md-samiuzzaman-sakib_-499442624-28424617.jpg":
        ("backup", "oscillatory_water", "fishing boats off a surf beach"),
    "photo-1777808732486-293621607f51.avif":
        ("backup", "falling_precip", "raindrop splash on a puddle, macro"),
    "pngtree-a-full-moon-in-the-sky-with-clouds-blue-hue-picture-image_16375212.jpg":
        ("reject", "watermark", "moon over sea with agency mark"),
    "pngtree-autumn-tree-with-colorful-leaves-falling-on-a-grassy-hill-forest-picture-image_16326564.jpg":
        ("reject", "no_flow", "autumn tree in a park"),
    "sea-wall-protecting-1250x660.jpg":
        ("select", "oscillatory_water", "wave breaking over a seawall and railing"),
    "shutterstock-1816260440___24133143948.webp":
        ("reject", "off_scope", "autumn canopy from below"),
    "stunning-pink-cherry-blossoms-with-dew-drops-and-falling-petals-spring-naturegraphy-free-photo.jpeg":
        ("reject", "studio", "cherry blossom branch, macro"),
    "the-importance-of-seawall-structural-engineering.jpg":
        ("select", "oscillatory_water", "stepped concrete seawall on a beach"),
    "theduststorm.jpg":
        ("backup", "windborne", "dust wall over a bare hill"),
    "tzf7whpveuwodsnuruldpxzchiez6diq0w7njhry.jpeg":
        ("backup", "windborne", "storm surge with palms and beached boats"),
    "waves-on-the-beach-with-reflection-of-the-sunlight-on-the-surface-of-the-sand-with-audio-free-video.jpg":
        ("backup", "oscillatory_water", "calm sea at sunset"),
}

# Targets for the extra images, from docs/I2V_IMAGE_COLLECTION_BRIEF.md.
# sha1 of the file each judgement was made against. Round 2 replaced 16 files
# that kept their original names -- "images (3).jpg" went from a woodland stream
# to a mangrove waterline -- so a name-keyed table alone would have carried the
# old label onto a different picture. A mismatch here is a re-review, not a
# warning to skim past.
SHA = json.load(open(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "manifest",
    "i2v_review_sha.json"))) if os.path.exists(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "manifest",
    "i2v_review_sha.json")) else {}

BRIEF_TARGETS = {
    "accumulating_level": 8,
    "falling_water": 7,
    "buoyant_plume": 5,
    "combustion": 5,
    "geothermal": 2,
}


def main():
    screen = json.load(open(os.path.join(ROOT, "manifest", "i2v_image_screen.json")))
    rows = {r["file"]: r for r in screen["rows"]}

    live = [r["file"] for r in screen["rows"]
            if r["verdict"] in ("pass", "marginal")]
    missing = [f for f in live if f not in REVIEW]
    if missing:
        raise SystemExit("unreviewed survivors:\n  " + "\n  ".join(missing))
    dropped = [f for f in REVIEW if f not in set(live)]
    for f in dropped:
        print(f"note: reviewed file no longer survives the screen: {f}")
    moved = [f"{f}: reviewed {SHA[f]}, on disk {rows[f]['sha1']}"
             for f in live if f in SHA and rows[f].get("sha1") != SHA[f]]
    if moved:
        raise SystemExit("file content changed since review; re-review these:\n  "
                         + "\n  ".join(moved))

    out, by_cat, reasons = [], defaultdict(list), Counter()
    for fname in live:
        verdict, label, note = REVIEW[fname]
        r = rows[fname]
        rec = {
            "file": fname,
            "screen": r["verdict"],
            "review": verdict,
            "category": label if verdict != "reject" else None,
            "reject_reason": label if verdict == "reject" else None,
            "note": note,
            "w": r["w"],
            "h": r["h"],
            "crop16x9": r["crop16x9"],
            "orb": r["orb"],
            "sha1": r["sha1"],
        }
        out.append(rec)
        if verdict == "reject":
            reasons[label] += 1
        else:
            by_cat[label].append(rec)

    manifest = {
        "n_screened": len(live),
        "n_select": sum(1 for r in out if r["review"] == "select"),
        "n_backup": sum(1 for r in out if r["review"] == "backup"),
        "n_reject": sum(1 for r in out if r["review"] == "reject"),
        "reject_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
        "by_category": {
            c: {
                "select": sum(1 for r in v if r["review"] == "select"),
                "backup": sum(1 for r in v if r["review"] == "backup"),
                "brief_target": BRIEF_TARGETS.get(c),
            }
            for c, v in sorted(by_cat.items())
        },
        "rows": out,
    }
    json.dump({f: rows[f]["sha1"] for f in live if "sha1" in rows[f]},
              open(os.path.join(ROOT, "manifest", "i2v_review_sha.json"), "w"),
              indent=1)
    dst = os.path.join(ROOT, "manifest", "i2v_image_review.json")
    with open(dst, "w") as fh:
        json.dump(manifest, fh, indent=1)

    print(f"screened {manifest['n_screened']}  select {manifest['n_select']}  "
          f"backup {manifest['n_backup']}  reject {manifest['n_reject']}")
    print("\nreject reasons")
    for k, v in manifest["reject_reasons"].items():
        print(f"  {k:<14} {v}")
    print("\ncategory        select backup  brief-target")
    for c, v in manifest["by_category"].items():
        tgt = v["brief_target"]
        print(f"  {c:<20} {v['select']:>3} {v['backup']:>6}   "
              f"{'-' if tgt is None else tgt}")
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")


if __name__ == "__main__":
    main()

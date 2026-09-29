# I2V source-image collection brief (v2)

## Why these images matter more than the T2V prompts

Every WACV reviewer named the same load-bearing flaw: the static/dynamic partition is
derived from each system's *own* early output, so two systems on the same prompt are
scored over different pixels, and Table 2's area-vs-fBD association (rho = -0.75) is the
signature of that circularity.

**The I2V track can fix this outright.** All systems start from the identical source
image, so one partition can be derived from the *image* and applied unchanged to every
system. That is the decisive control the reviewers asked for, and it costs no new
metric design — only images chosen so the partition is derivable from the still.

So image selection is now a measurement decision, not asset gathering. The dominant
criterion is: **can a person (and a detector) mark static support and intended-motion
region from this single frame, before any video exists?**

## What we have

65 unique images, and they are **fully disjoint across horizons** (5s ∩ 60s ∩ 120s ∩
240s all empty) — the same structural defect the T2V set had. v2 uses **one core image
set scored at 60/120/240 s prefixes**, so each image is collected once.

Mapped onto the v2 nine-category taxonomy, roughly: channel flow ~18, falling
precipitation ~16, oscillatory water ~9, windborne ~10, fire/smoke ~6 (unsplit),
geothermal ~6. Two categories are at or near zero.

## What to collect

Target **8 per category, 72 total**. Minimum viable is 5 per category (45). Counts below
are *additional* images needed; I will filter, crop and finalise pairs from whatever you
gather, so over-collect by ~50% where convenient.

| category | need | what the still must show |
|---|---|---|
| **accumulating_level** | **8 (have 0)** | A graduated rigid reference the level will climb: kerb + railing base, slipway steps, harbour ladder rungs, a basin rim, a gauge plate, a wall with visible courses. Water (or snow) present but clearly *low* in frame so a rise is observable. **Highest priority.** |
| **falling_water** | **7** | Waterfall, weir overfall, cascade, downspout, spillway. Needs the fall line *and* rigid rock/concrete either side. Avoid long-exposure silky water — it implies motion already. |
| **buoyant_plume** | **5** | Chimney, grill, manhole steam, hot spring, incense, kiln. Plume source visible, sky or dark wall behind so the plume region is separable. |
| **combustion** | **5** | Fire in a contained rigid setting: brazier, hearth, fire pit ring, oil-drum, bonfire with stone ring. Flame visible in the still. |
| **geothermal** | **2** | Lava channel/lobe, fumarole, mud pool, geyser pool. Cooled crust or terraces as support. |
| **oscillatory_water** | 0 (trim to 8) | — |
| **windborne** | 0 (trim to 8) | — |
| **channel_flow** | 0 (trim to 8) | — |
| **falling_precip** | 0 (trim to 8) | see caveat below |

## Requirements for every image

1. **Rigid support >= ~30% of frame, textured and in focus.** fBD needs repeatable ORB
   keypoints. Flat sky, smooth concrete, fog and plain sand give none — one v1 dust-storm
   scene abstained across all seven systems for exactly this reason.
2. **The motion region must be identifiable in the still** (water surface, plume source,
   flame, grass field). This is what makes the shared partition possible.
3. **Fixed-camera plausible.** Level horizon, no implied pan, no vignette or crop that
   reads as a moving shot.
4. **No people, animals or moving vehicles.** They are neither static support nor
   intended flow, and they wreck the partition. Parked cars are fine.
5. **No motion blur on the medium** and no long-exposure water — it pre-loads the answer.
6. **>= 1280x720, croppable to 16:9** (we render 832x480).
7. **Redistributable licence** (CC0 / CC-BY / own photography). Reviewers flagged the
   absence of a licence plan; please note the source and licence per file. Your own
   photographs are ideal because redistribution is unambiguous.
8. One scene per image — no diptychs, no text overlays, no watermarks.

## Naming

`<category>_<nn>_<short-slug>.<ext>`, e.g. `accumulating_level_03_harbour-ladder.jpg`,
plus a line in a sidecar CSV: `filename, source_url_or_own, licence, location, notes`.

## One honest caveat

**Falling precipitation cannot have its motion region derived from a still** — a single
frame does not show rain in the air. For that category the partition must come from
context (sky region, wet surfaces) or the category abstains from the shared-partition
control. I would rather state that than fake it, so precipitation will be reported as
partition-derivable = no, and the shared-partition claim will be made on the other eight
categories. If you can include a few frames with *visible* streaks (long-ish exposure
rain against a dark background), those become the exception.

## What I do once you deliver

1. Screen against the eight requirements and reject with reasons.
2. Crop to 16:9, verify ORB keypoint density on the support region, reject low-texture.
3. Author the matched text prompt per image using the same v2 builder and validator that
   produced the T2V set (no metric vocabulary, no negation, explicit direction where
   scorable, static support disjoint from the medium).
4. Emit the frozen pair manifest with per-image category, direction applicability,
   declared static support, and licence.

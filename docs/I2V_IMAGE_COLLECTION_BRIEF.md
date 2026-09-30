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

## What we had before round 1

65 unique v1 images, **fully disjoint across horizons** (5s ∩ 60s ∩ 120s ∩ 240s all
empty) — the same structural defect the T2V set had. v2 uses **one core image set scored
at 60/120/240 s prefixes**, so each image is collected once.

Mapped onto the v2 nine-category taxonomy, roughly: channel flow ~18, falling
precipitation ~16, oscillatory water ~9, windborne ~10, fire/smoke ~6 (unsplit),
geothermal ~6 — with accumulating_level empty. Re-screening the 60 s pool at the current
thresholds then disqualified 9 of its 30 images on croppability, which is why the reuse
counts below are lower than this paragraph implies.

## Collection outcome: the set is complete at 48 pairs

Two rounds delivered 451 images. Screened by `scripts/screen_i2v_images.py`,
reviewed by `scripts/classify_i2v_images.py`, built into pairs by
`scripts/build_i2v_pairs_v2.py`.

| | round 1 | + round 2 | total |
|---|---|---|---|
| delivered | 368 | 83 | 451 |
| cleared the mechanical screen | 155 | 47 | 202 |
| passed visual review | 117 | 27 | 144 (111 select, 33 backup) |
| rejected on content | 42 | 16 | 58 |
| **built into the v2 pair set** | 33 | 6 | **39** |

Plus 7 reusable v1 images and 2 fetched from Wikimedia Commons: **48 pairs**, at
the same stratum shares as the 96-scene T2V set (channel_flow 6, falling_precip
6, oscillatory_water 5, accumulating_level 5, buoyant_plume 6, combustion 5,
windborne 6, geothermal 4, falling_water 5).

**What the screen removed was overwhelmingly resolution**: 242 of 451 files cannot
yield a 640x360 16:9 crop, most of them search-result thumbnails. Content
rejections concentrated in a few avoidable kinds — 11 studio/product shots, 9
stock watermarks, 9 renders or concept art, 6 composites, 5 long-exposure silky
water, 4 generated images.

### Four things the rounds exposed

* **AVIF now decodes.** Six round-1 files were AVIF and the screen read them as
  undecodable; it now falls back to Pillow, and three made the select list.
* **Nine of the 30 v1 images fail the current bar** on croppability, so the v1
  I2V tier conditioned on frames that had to be upscaled into the render. Only
  the 21 that clear the bar are reusable.
* **Round 2 replaced 16 files that kept their round-1 names.** `images (3).jpg`
  went from a woodland stream to a mangrove waterline, so a name-keyed review
  would have carried the old judgement onto a different picture. One label was
  affected and has been re-reviewed; no built pair was. The review table now
  records the sha1 each judgement was made against and refuses to run when a
  file's content has changed.
* **A centred crop is the wrong default.** On the roadside haboob frame the
  centre window lands entirely on the dust and falls to 31 ORB keypoints, below
  the level at which fBD abstains — which is how a v1 dust-storm scene came to
  abstain across all seven systems. The crop window is now placed by the same
  detector the metric uses. Minimum across all 48 crops is 580.

### Generated images cannot be used, and that is not a preference

Round 2 included one `Gemini_Generated_Image_*.webp` and three other generated
frames; all were rejected. Conditioning a video generator on another generator's
output makes the evaluation circular: the benchmark would be measuring how well
system A extends system B's hallucination, and a reviewer gets that objection for
free. Two of the three WACV reviewers already attacked the partition for being
derived from the system's own output — a generated conditioning image is the same
defect one step earlier. If a category cannot be filled with photographs, the
honest move is to report it short, not to synthesise it.

## The one gap that remains: licence, not images

**Licence is recorded for 2 of the 48 pairs.** Those two are the Commons fetches;
the other 46 arrived with no sidecar CSV and several are plainly agency-sourced.
Nothing in the pair set can be redistributed with the benchmark until that is
fixed, and no amount of further collection fixes it.

Two ways forward, in order of preference:

1. **Send the sidecar** for the 39 selected files listed in
   `manifest/i2v_pairs_v2.json` (`source_file` field): `filename, source_url,
   licence`. Anything that turns out to be non-redistributable gets swapped for a
   backup from the same category — there are 33 backups on hand.
2. **Refetch from Commons.** `scripts/fetch_commons_images.py` takes a query and
   keeps only CC0/CC-BY/CC-BY-SA/public-domain files at >=1280x720, recording
   source, licence and attribution per file. It already supplied both snowfall
   pairs. This trades image quality for unambiguous provenance and could replace
   the whole set if the sidecar is not available.

A third option — releasing only the prompts, the crop geometry and the source
URLs, and having users fetch the images themselves — is worth considering if
neither of the above lands, but it makes the benchmark harder to reproduce and
invites link rot.

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
6. **>= 1280x720, croppable to 16:9** (we render 832x480). This is the single most
   expensive requirement to miss: it removed 209 of the 368 round-1 files. JPEG, PNG,
   WebP and AVIF all decode.
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
2. Crop to 16:9 and verify ORB keypoint count on the delivered 832x480 crop. The crop
   window is placed by ORB rather than centred, because a centred window on a dust-storm
   frame landed entirely on the dust and fell to 31 keypoints. Note this is a whole-frame
   count, not a support-region density: Omega_static comes from early optical flow of the
   generated video, which does not exist for a still, so no honest per-region number is
   available before generation.
3. Author the matched text prompt per image using the same v2 builder and validator that
   produced the T2V set (no metric vocabulary, no negation, explicit direction where
   scorable, static support disjoint from the medium).
4. Emit the frozen pair manifest with per-image category, direction applicability,
   declared static support, and licence.

# Scene-category balance audit

SNF-Bench macro-averages by **flow medium** — what the dynamic region physically is —
because every task metric (NBF, MCFF, FP, DAR) measures optical flow inside the
dynamic mask, and media differ structurally in flow signature. Per-prompt assignments,
with the rule that fired and the text that triggered it, are in
`manifest/prompt_categories.csv` (all rows, hand-checkable).

## Taxonomy

| category | definition |
|---|---|
| river_stream | channel water: rivers, streams, creeks, canals, waterfalls, rapids, floods |
| ocean_waves | open water with wave action: surf, tides, coastal swell, seascapes |
| precipitation | falling water or ice: rain, snowfall, and the surfaces they wet |
| fire_smoke | combustion plumes: wildfire, campfire, hearth, urban fire, grill smoke |
| lava_volcanic | volcanic flow and ejecta: lava channels, ash columns, eruption smoke |
| windborne | air-carried particulates and wind-driven vegetation: dust, sand, blossom, leaves, thrashing trees, drifting cloud |

## Prompts per category

`n` = prompts in the eval set. `max share` = fraction held by the single largest
category. Cells with `0 < n < 3` are too thin to macro-average stably.

| track/duration | n | river_stream | ocean_waves | precipitation | fire_smoke | lava_volcanic | windborne | cats | max share |
|---|---|---|---|---|---|---|---|---|---|
| i2v/5s | 10 | 2 | · | 3 | 2 | 1 | 2 | 5 | 0.30 |
| i2v/60s | 30 | 9 | 4 | 9 | 1 | 3 | 4 | 6 | 0.30 |
| i2v/120s | 20 | 6 | 3 | 3 | 3 | 1 | 4 | 6 | 0.30 |
| i2v/240s | 5 | 1 | 2 | 1 | · | 1 | · | 4 | 0.40 |
| t2v/5s | 6 | 3 | 1 | 1 | 1 | · | · | 4 | 0.50 |
| t2v/60s | 23 | 14 | 2 | 3 | 2 | · | 2 | 5 | 0.61 |
| t2v/120s | 6 | 4 | · | 1 | · | · | 1 | 3 | 0.67 |
| t2v/240s | 4 | 2 | · | 1 | · | · | 1 | 3 | 0.50 |

## Label provenance

| track | source | prompts |
|---|---|---|
| i2v | meta | 65 |
| t2v | keyword | 34 |
| t2v | keyword-body | 4 |
| t2v | override | 1 |

- `meta` — the I2V eval set's curated `type` field (53 fine types over 65 prompts),
  mapped to the coarse axis. The fine type is retained in the CSV.
- `keyword` — T2V has no type field; the category is derived from the scene descriptor
  (the clause before the fixed-camera boilerplate) by ordered first-match rules.
- `override` — hand-assigned where first-match-wins is defensibly wrong; each is listed below.

## Overrides

| track | duration | prompt (prefix) | category | reason |
|---|---|---|---|---|
| t2v | 60s | A_completely_fixed,_tripod-mounted_camera_captur… | precipitation | 'flooded' fires the channel-water rule, but the dynamic content is falling rain plus a slowly rising waterline -- there is no channel flow in frame. |

## Findings

- Every evaluated prompt received a category; no `unassigned` rows.
- Every scored `prompt_id` traced back to a source prompt/caption (exact 100-char join).
- Thin cells (n < 3), macro-average unstable: i2v/5s/river_stream (n=2); i2v/5s/fire_smoke (n=2); i2v/5s/lava_volcanic (n=1); i2v/5s/windborne (n=2); i2v/60s/fire_smoke (n=1); i2v/120s/lava_volcanic (n=1); i2v/240s/river_stream (n=1); i2v/240s/ocean_waves (n=2); i2v/240s/precipitation (n=1); i2v/240s/lava_volcanic (n=1); t2v/5s/ocean_waves (n=1); t2v/5s/precipitation (n=1); t2v/5s/fire_smoke (n=1); t2v/60s/ocean_waves (n=2); t2v/60s/fire_smoke (n=2); t2v/60s/windborne (n=2); t2v/120s/precipitation (n=1); t2v/120s/windborne (n=1); t2v/240s/river_stream (n=2); t2v/240s/precipitation (n=1); t2v/240s/windborne (n=1)
- Categories absent entirely from a cell: 12 of 48 (track,duration,category) slots — i2v/5s/ocean_waves; i2v/240s/fire_smoke; i2v/240s/windborne; t2v/5s/lava_volcanic; t2v/5s/windborne; t2v/60s/lava_volcanic; t2v/120s/ocean_waves; t2v/120s/fire_smoke; t2v/120s/lava_volcanic; t2v/240s/ocean_waves; t2v/240s/fire_smoke; t2v/240s/lava_volcanic

Read the two together: a category absent from a duration means that duration's
macro-average is taken over a *different* medium mix than its neighbours, so
cross-duration comparison of a macro-average is only sound within a fixed category.

# Fig. 1 teaser — candidate exemplar clips

Selected from real benchmark videos so the teaser is a controlled comparison,
not an illustration. Each row is one prompt evaluated by three methods:

- **A** desired behaviour — low drift, motion survives
- **B** drift masquerading as motion — high drift, high *raw* dynamic degree, high DAR
- **C** frozen — low drift, but motion has collapsed

| rank | prompt (truncated) | A: good | B: drifting | C: frozen |
|---|---|---|---|---|
| 1 | `A_Norwegian_fjord_approach_scene_featuring_a_shallow_f…` | CausVid | Causal-Forcing | Infinite-Forcing |
| 2 | `A_South_Korean_countryside_scene_featuring_a_wide_rive…` | CausVid | Rolling-Forcing | Infinite-Forcing |
| 3 | `A_continuous_South_Korean_urban_town_street_scene_duri…` | Self-Forcing | Rolling-Forcing | Infinite-Forcing |
| 4 | `A_beautiful_rural_South_Korean_street_food_shop_scene,…` | CausVid | Rolling-Forcing | Infinite-Forcing |
| 5 | `A_Himalayan_foothills_scene_featuring_a_tidal_channel_…` | Self-Forcing | Causal-Forcing | CausVid |
| 6 | `A_stormy_sea_cliff_in_South_Korea,_recorded_by_a_stati…` | Rolling-Forcing | Causal-Forcing | Self-Forcing |
| 7 | `A_dangerous_South_Korean_hilly_forest_storm_scene,_rec…` | LongLive | Causal-Forcing | Infinite-Forcing |
| 8 | `A_continuous_South_Korean_rainy_city_street_scene,_rec…` | CausVid | Causal-Forcing | Self-Forcing |

Searched 23 prompts shared by all 7 public methods; 18 yielded three distinct methods.

## Metric values for the top candidate

prompt: `A_Norwegian_fjord_approach_scene_featuring_a_shallow_forest_creek_that_gushes_continuously_with_visi`

| case | method | fBD ↓ | MCFF | DD_raw | DAR ↓ |
|---|---|---|---|---|---|
| A good | CausVid | 5.00 | 12.589 | 14.69 | 0.143 |
| B drifting | Causal-Forcing | 21.96 | 1.429 | 7.49 | 0.809 |
| C frozen | Infinite-Forcing | 6.83 | 0.258 | 0.25 | -0.015 |

Video paths: `videos/t2v/<model-key>/60s/`

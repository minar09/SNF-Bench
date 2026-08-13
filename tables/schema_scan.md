# Metric-artifact schema scan

Mechanical validity check over every `snf_task_metrics.json`. Exists because the CausVid gap was found by chasing one odd count, which is luck rather than method; this makes the same class of defect discoverable by construction.

| statistic | count |
|---|---|
| records | 1460 |
| valid | 1339 |
| error_records | 115 |
| missing_keys | 6 |
| non_finite | 0 |
| degenerate_mask | 0 |
| frame_mismatch | 0 |
| video_missing | 0 |
| unmeasured | 0 |

## Blocking problems — 13 entries

| entry | status | kind | detail |
|---|---|---|---|
| `i2v/causvid/120s` | public | error-in-results ×19 | A completely fixed, static, aerial tripod-mounted camera records an active lava  |
| `i2v/causvid/60s` | public | error-in-results ×29 | A completely fixed, static, macro tripod-mounted camera records heavy urban rain |
| `i2v/cf++_1step/240s` | public | error-in-results ×4 | A completely fixed, static, close-range tripod-mounted camera records heavy trop |
| `i2v/cf++_1step/60s` | public | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a desert dust storm sw |
| `i2v/cf_framewise/120s` | public | error-in-results ×19 | A completely fixed, static, aerial tripod-mounted camera records an active lava  |
| `i2v/cf_framewise/60s` | public | error-in-results ×29 | A completely fixed, static, macro tripod-mounted camera records heavy urban rain |
| `i2v/phase7_000100/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |
| `i2v/phase7_000200/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |
| `i2v/phase7_000300/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |
| `i2v/phase7_000400/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |
| `i2v/phase7_500/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |
| `i2v/steady/120s` | internal | error-in-results ×11 | A completely fixed, static, aerial tripod-mounted camera records an active lava  |
| `i2v/steady/240s` | internal | error-in-results ×4 | A completely fixed, static, close-range tripod-mounted camera records heavy trop |

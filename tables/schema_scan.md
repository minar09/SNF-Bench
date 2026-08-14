# Metric-artifact schema scan

Mechanical validity check over every `snf_task_metrics.json`. Exists because the CausVid gap was found by chasing one odd count, which is luck rather than method; this makes the same class of defect discoverable by construction.

| statistic | count |
|---|---|
| records | 1578 |
| valid | 1571 |
| error_records | 0 |
| missing_keys | 7 |
| non_finite | 0 |
| degenerate_mask | 0 |
| frame_mismatch | 0 |
| video_missing | 0 |
| unmeasured | 0 |

## Blocking problems — 7 entries

| entry | status | kind | detail |
|---|---|---|---|
| `i2v/causvid/60s` | public | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a desert dust storm sw |
| `i2v/cf++_1step/60s` | public | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a desert dust storm sw |
| `i2v/phase7_000100/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |
| `i2v/phase7_000200/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |
| `i2v/phase7_000300/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |
| `i2v/phase7_000400/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |
| `i2v/phase7_500/60s` | internal | missing-keys ×1 | A completely fixed, static, tripod-mounted camera records a calm overcast coasta |

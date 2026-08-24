# Asset & score coverage matrix

`V` = generated videos present · `T` = SNF task metrics (RAFT+ORB) · `X` = cv2 extra metrics · `B` = VBench

`T` is counted from **valid per-video records**, not from the presence of a metrics file. `T3/30` means the file exists but only 3 of 30 videos hold usable measurements; the rest carry an error payload.

> **Incomplete metric runs detected.** `i2v/causvid/60s` 29/30; `i2v/cf++_1step/60s` 29/30; `i2v/phase7_000100/60s` 29/30; `i2v/phase7_000200/60s` 29/30; `i2v/phase7_000300/60s` 29/30; `i2v/phase7_000400/60s` 29/30; `i2v/phase7_500/60s` 29/30. Cause: CUDA OOM / `CUDNN_STATUS_NOT_INITIALIZED` during the metric sweep, not generation failure — the videos exist, so these are re-runnable without regeneration.

## T2V track

| Method | status | setting | 5s | 60s | 120s | 240s |
|---|---|---|---|---|---|---|
| CausVid | public | matched | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |
| Self-Forcing | public | matched | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |
| Infinite-Forcing | public | matched | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |
| Rolling-Forcing | public | matched | V6 T6 B | V24 T24 B | V6 T6 B | V4 T4 B |
| Reward-Forcing | public | matched | V12 T12 B | V23 T23 B | V6 T6 B | V4 T4 B |
| LongLive | public | matched | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |
| Causal-Forcing | public | matched | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |

## I2V track

| Method | status | setting | 5s | 60s | 120s | 240s |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | public | matched | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| Causal-Forcing++ (1-step) | public | matched | V10 T10 X B | V30 T29/30 X B | V20 T20 X B | V5 T5 X B |
| Causal-Forcing (frame-wise) | public | matched | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| Causal-Forcing++ (2-step, frame-wise) | public | native | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| Self-Forcing | public | matched | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| CausVid | public | matched | V10 T10 X B | V30 T29/30 X B | V20 T20 X B | V5 T5 X B |
| Wan2.1-I2V-14B-480P | public | native | V10 T10 X B | · | · | · |
| Wan2.2-I2V-A14B | public | native | V10 T10 X B | · | · | · |
| LTX-Video 13B-0.9.8-distilled | public | native | V10 T10 X B | · | · | · |
| Causal-Forcing++ (1-step, frame-wise) | public | native | · | V30 T30 | V20 T20 | · |

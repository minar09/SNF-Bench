# Asset & score coverage matrix

`V` = generated videos present · `T` = SNF task metrics (RAFT+ORB) · `X` = cv2 extra metrics · `B` = VBench

`T` is counted from **valid per-video records**, not from the presence of a metrics file. `T3/30` means the file exists but only 3 of 30 videos hold usable measurements; the rest carry an error payload.

> **Incomplete metric runs detected.** `i2v/causvid/60s` 29/30; `i2v/cf++_1step/60s` 29/30; `i2v/phase7_000100/60s` 29/30; `i2v/phase7_000200/60s` 29/30; `i2v/phase7_000300/60s` 29/30; `i2v/phase7_000400/60s` 29/30; `i2v/phase7_500/60s` 29/30. Cause: CUDA OOM / `CUDNN_STATUS_NOT_INITIALIZED` during the metric sweep, not generation failure — the videos exist, so these are re-runnable without regeneration.

## T2V track

| Method | status | setting | 5s | 60s | 120s | 240s |
|---|---|---|---|---|---|---|
| CausVid | public | common | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |
| Self-Forcing | public | common | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |
| Infinite-Forcing | public | common | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |
| Rolling-Forcing | public | common | V6 T6 B | V24 T24 B | V6 T6 B | V4 T4 B |
| Reward-Forcing | public | common | V12 T12 B | V23 T23 B | V6 T6 B | V4 T4 B |
| LongLive | public | common | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |
| Causal-Forcing | public | common | V6 T6 B | V23 T23 B | V6 T6 B | V4 T4 B |
| Steady-Forcing | internal | released | V6 | V23 | V6 | V5 |
| Steady-Forcing (BT) | internal | released | V6 B | V23 T23 B | V6 B | V6 B |

## I2V track

| Method | status | setting | 5s | 60s | 120s | 240s |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | public | wrapper | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| Causal-Forcing++ (1-step) | public | wrapper | V10 T10 X B | V30 T29/30 X B | V20 T20 X B | V5 T5 X B |
| Causal-Forcing (frame-wise) | public | wrapper | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| Causal-Forcing++ (2-step, frame-wise) | public | released | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| Self-Forcing | public | wrapper | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| CausVid | public | wrapper | V10 T10 X B | V30 T29/30 X B | V20 T20 X B | V5 T5 X B |
| Wan2.1-I2V-14B-480P | public | released | V10 T10 X B | · | · | · |
| Wan2.2-I2V-A14B | public | released | V10 T10 X B | · | · | · |
| LTX-Video 13B-0.9.8-distilled | public | released | V10 T10 X B | · | · | · |
| Steady-Forcing | internal | wrapper | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| RA-I2V (rt500) | internal | wrapper | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| RA-I2V-v1 (phase7_500) | internal | wrapper | V10 T10 X B | V30 T29/30 X B | V20 T20 X B | V5 T5 X B |
| nfpb=1 control | internal | wrapper | V10 T10 X | V30 T30 X | V20 T20 X | · |
| nfpb=1 control @nfpb=1 | internal | released | · | V30 T30 | · | · |
| phase7 @nfpb=1 | internal | released | V10 T10 X | V30 T30 X | V20 T20 X | · |
| ablation: region+static | internal | wrapper | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| ablation: Re-DMD | internal | wrapper | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| ablation: RS+Re-DMD | internal | wrapper | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| ablation: v2 | internal | wrapper | V10 T10 X B | V30 T30 X B | V20 T20 X B | V5 T5 X B |
| phase7 ckpt 100 | internal | wrapper | · | V30 T29/30 X | V20 T20 X | · |
| phase7 ckpt 200 | internal | wrapper | · | V30 T29/30 X | V20 T20 X | · |
| phase7 ckpt 300 | internal | wrapper | · | V30 T29/30 X | V20 T20 X | · |
| phase7 ckpt 400 | internal | wrapper | · | V30 T29/30 X | V20 T20 X | · |
| Causal-Forcing++ (1-step, frame-wise) | public | released | · | V30 T30 | V20 T20 | · |
| Causal-Forcing++ (2-step) +color-match | postproc | wrapper | V10 X | V30 X | V20 X | V5 X |
| RA-I2V +color-match | internal | wrapper | V10 X | V30 X | V20 X | V5 X |
| RA-I2V-v1 +color-match | internal | wrapper | V10 X | V30 X | V20 X | V5 X |
| nfpb=1 control +color-match | internal | wrapper | · | V30 X | V20 X | · |
| (scratch) | scratch | wrapper | · | · | · | · |

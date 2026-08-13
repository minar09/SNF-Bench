# Asset & score coverage matrix

`V` = generated videos present · `T` = SNF task metrics (RAFT+ORB) · `X` = cv2 extra metrics · `B` = VBench

## T2V track

| Method | status | setting | 5s | 60s | 120s | 240s |
|---|---|---|---|---|---|---|
| CausVid | public | native | V6 B | V23 T B | V6 B | V4 B |
| Self-Forcing | public | native | V6 B | V23 T B | V6 B | V4 B |
| Infinite-Forcing | public | native | V6 B | V23 T B | V6 B | V4 B |
| Rolling-Forcing | public | native | V6 B | V24 T B | V6 B | V4 B |
| Reward-Forcing | public | native | V12 B | V23 T B | V6 B | V4 B |
| LongLive | public | native | V6 B | V23 T B | V6 B | V4 B |
| Causal-Forcing | public | native | V6 B | V23 T B | V6 B | V4 B |
| Steady-Forcing | internal | native | V6 | V23 | V6 | V5 |
| Steady-Forcing (BT) | internal | native | V6 B | V23 T B | V6 B | V6 B |

## I2V track

| Method | status | setting | 5s | 60s | 120s | 240s |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | public | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| Causal-Forcing++ (1-step) | public | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| Causal-Forcing (framewise) | public | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| Causal-Forcing++ (2-step, native nfpb=1) | public | native | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| Self-Forcing | public | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| CausVid | public | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| Wan2.1-I2V-14B-480P | public | native | V10 T X B | · | · | · |
| Wan2.2-I2V-A14B | public | native | V10 T X B | · | · | · |
| LTX-Video 13B-0.9.8-distilled | public | native | V10 T X B | · | · | · |
| Steady-Forcing | internal | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| RA-I2V (rt500) | internal | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| RA-I2V-v1 (phase7_500) | internal | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| nfpb=1 control | internal | matched | V10 T X | V30 T X | V20 T X | · |
| nfpb=1 control @nfpb=1 | internal | native | · | V30 T | · | · |
| phase7 @nfpb=1 | internal | native | V10 T X | V30 T X | V20 T X | · |
| ablation: region+static | internal | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| ablation: Re-DMD | internal | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| ablation: RS+Re-DMD | internal | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| ablation: v2 | internal | matched | V10 T X B | V30 T X B | V20 T X B | V5 T X B |
| phase7 ckpt 100 | internal | matched | · | V30 T X | V20 T X | · |
| phase7 ckpt 200 | internal | matched | · | V30 T X | V20 T X | · |
| phase7 ckpt 300 | internal | matched | · | V30 T X | V20 T X | · |
| phase7 ckpt 400 | internal | matched | · | V30 T X | V20 T X | · |
| Causal-Forcing++ (1-step, native) | public | native | · | V30 T | V20 T | · |
| Causal-Forcing++ (2-step) +color-match | postproc | matched | V10 X | V30 X | V20 X | V5 X |
| RA-I2V +color-match | internal | matched | V10 X | V30 X | V20 X | V5 X |
| RA-I2V-v1 +color-match | internal | matched | V10 X | V30 X | V20 X | V5 X |
| nfpb=1 control +color-match | internal | matched | · | V30 X | V20 X | · |
| (scratch) | scratch | matched | · | · | · | · |

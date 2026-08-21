# Model configuration / provenance table

Required by the E&D track: every evaluated system with its checkpoint and the
configuration it was actually run under. **Setting A = native**, **Setting B = matched wrapper**.

## T2V track

| Method | status | setting | checkpoint | note |
|---|---|---|---|---|
| CausVid | public | native | `ckpt/CausVid/autoregressive_checkpoint/model.pt` | autoregressive DMD distillation of Wan2.1-T2V-1.3B |
| Self-Forcing | public | native | `ckpt/Self-Forcing/checkpoints/self_forcing_dmd.pt` |  |
| Infinite-Forcing | public | native | `(baseline repo)` | lowest NBF at 60s but lowest MCFF -> freeze-not-stability, the key confound case |
| Rolling-Forcing | public | native | `ckpt/RollingForcing` |  |
| Reward-Forcing | public | native | `ckpt/rewardforcing.pt` |  |
| LongLive | public | native | `ckpt/longlive_models` |  |
| Causal-Forcing | public | native | `ckpt/causal-forcing` | high apparent motion + high drift attenuation; the headline interpretation-change case |
| Steady-Forcing | internal | native | `ckpt/Steady-Forcing` | OUR prior work - excluded from SNF-Bench |
| Steady-Forcing (BT) | internal | native | `ckpt/Steady-Forcing` | OUR prior work - excluded from SNF-Bench |

## I2V track

| Method | status | setting | checkpoint | note |
|---|---|---|---|---|
| Causal-Forcing++ (2-step) | public | matched | `ckpt/causal-forcing++/framewise-2step.pt` | run in the common long-horizon I2V wrapper (configs/common_longhorizon_i2v.yaml, 6 frames per block, image-conditioned) -- NOT the model's native configuration. Read as deployment sensitivity only. |
| Causal-Forcing++ (1-step) | public | matched | `ckpt/causal-forcing++/framewise-1step.pt` | run in the common long-horizon I2V wrapper (configs/common_longhorizon_i2v.yaml, 6 frames per block, image-conditioned) -- NOT the model's native configuration. Read as deployment sensitivity only. |
| Causal-Forcing (frame-wise) | public | matched | `ckpt/causal-forcing/framewise/causal_forcing.pt` | run in the common long-horizon I2V wrapper (configs/common_longhorizon_i2v.yaml, 6 frames per block, image-conditioned) -- NOT the model's native configuration. Read as deployment sensitivity only. |
| Causal-Forcing++ (2-step, frame-wise) | public | native | `ckpt/causal-forcing++/framewise-2step.pt` | run at its native pure-framewise config (configs/framewise_native_i2v.yaml); a genuine native-setting run at 60s and beyond. |
| Self-Forcing | public | matched | `ckpt/Self-Forcing/checkpoints/self_forcing_dmd.pt` | run in the common long-horizon I2V wrapper (configs/common_longhorizon_i2v.yaml, 6 frames per block, image-conditioned) -- NOT the model's native configuration. Read as deployment sensitivity only. |
| CausVid | public | matched | `ckpt/CausVid/autoregressive_checkpoint/model.pt` | run in the common long-horizon I2V wrapper (configs/common_longhorizon_i2v.yaml, 6 frames per block, image-conditioned) -- NOT the model's native configuration. Read as deployment sensitivity only. |
| Wan2.1-I2V-14B-480P | public | native | `ckpt/wan_models/Wan2.1-I2V-14B-480P` | bidirectional 14B, native config, 5s only (fixed-length model) |
| Wan2.2-I2V-A14B | public | native | `ckpt/wan_models/Wan2.2-I2V-A14B` | bidirectional MoE, native config, 5s only |
| LTX-Video 13B-0.9.8-distilled | public | native | `baseline_repos/LTX-Video` | bidirectional, native config, 5s only |
| Steady-Forcing | internal | matched | `ckpt/Steady-Forcing/steady_forcing_t2v.pt` | OUR prior work - excluded |
| RA-I2V (rt500) | internal | matched | `runs/.../rt500` | OUR method - excluded |
| RA-I2V-v1 (phase7_500) | internal | matched | `runs/phase7_nfpb6/checkpoint_model_000500/model.pt` | OUR method - excluded |
| nfpb=1 control | internal | matched | -- | OUR training control - excluded |
| nfpb=1 control @nfpb=1 | internal | native | -- | OUR training control - excluded |
| phase7 @nfpb=1 | internal | native | -- | OUR training control - excluded |
| ablation: region+static | internal | matched | -- | OUR ablation - excluded |
| ablation: Re-DMD | internal | matched | -- | OUR ablation - excluded |
| ablation: RS+Re-DMD | internal | matched | -- | OUR ablation - excluded |
| ablation: v2 | internal | matched | -- | OUR ablation - excluded |
| phase7 ckpt 100 | internal | matched | -- | checkpoint ladder - excluded |
| phase7 ckpt 200 | internal | matched | -- | checkpoint ladder - excluded |
| phase7 ckpt 300 | internal | matched | -- | checkpoint ladder - excluded |
| phase7 ckpt 400 | internal | matched | -- | checkpoint ladder - excluded |
| Causal-Forcing++ (1-step, frame-wise) | public | native | `ckpt/causal-forcing++/framewise-1step.pt` | native pure-framewise config; partial coverage (50/65) |
| Causal-Forcing++ (2-step) +color-match | postproc | matched | -- | post-hoc color match of chunk6 |
| RA-I2V +color-match | internal | matched | -- | OUR method - excluded |
| RA-I2V-v1 +color-match | internal | matched | -- | OUR method - excluded |
| nfpb=1 control +color-match | internal | matched | -- | OUR control - excluded |
| (scratch) | scratch | matched | -- | debug run |

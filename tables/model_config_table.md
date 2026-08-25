# Model configuration / provenance table

Required by the E&D track: every evaluated system with its checkpoint and the
configuration it was actually run under. **T2V = recorded common configuration**; **I2V = released pipeline or wrapper (deployment sensitivity)**.

## T2V track

| Method | status | setting | checkpoint | note |
|---|---|---|---|---|
| CausVid | public | common | `ckpt/CausVid/autoregressive_checkpoint/model.pt` | released checkpoint evaluated in the recorded common T2V configuration (four scheduler-warped steps, six frames per block, seed 0); not the method's released inference procedure |
| Self-Forcing | public | common | `ckpt/Self-Forcing/checkpoints/self_forcing_dmd.pt` | released checkpoint evaluated in the recorded common T2V configuration (four scheduler-warped steps, six frames per block, seed 0); not the method's released inference procedure |
| Infinite-Forcing | public | common | `(baseline repo)` | released checkpoint evaluated in the recorded common T2V configuration (four scheduler-warped steps, six frames per block, seed 0); not the method's released inference procedure |
| Rolling-Forcing | public | common | `ckpt/RollingForcing` | released checkpoint evaluated in the recorded common T2V configuration (four scheduler-warped steps, six frames per block, seed 0); not the method's released inference procedure |
| Reward-Forcing | public | common | `ckpt/rewardforcing.pt` | released checkpoint evaluated in the recorded common T2V configuration (four scheduler-warped steps, six frames per block, seed 0); not the method's released inference procedure |
| LongLive | public | common | `ckpt/longlive_models` | released checkpoint evaluated in the recorded common T2V configuration (four scheduler-warped steps, six frames per block, seed 0); not the method's released inference procedure |
| Causal-Forcing | public | common | `ckpt/causal-forcing` | released checkpoint evaluated in the recorded common T2V configuration (four scheduler-warped steps, six frames per block, seed 0); not the method's released inference procedure |
| Steady-Forcing | internal | released | `ckpt/Steady-Forcing` | OUR prior work - excluded from SNF-Bench |
| Steady-Forcing (BT) | internal | released | `ckpt/Steady-Forcing` | OUR prior work - excluded from SNF-Bench |

## I2V track

| Method | status | setting | checkpoint | note |
|---|---|---|---|---|
| Causal-Forcing++ (2-step) | public | wrapper | `ckpt/causal-forcing++/framewise-2step.pt` | run in the common long-horizon I2V rollout wrapper (6 frames per block, image-conditioned; checkpoint-specific denoising schedule). Read as deployment sensitivity only. |
| Causal-Forcing++ (1-step) | public | wrapper | `ckpt/causal-forcing++/framewise-1step.pt` | run in the common long-horizon I2V rollout wrapper (6 frames per block, image-conditioned; checkpoint-specific denoising schedule). Read as deployment sensitivity only. |
| Causal-Forcing (frame-wise) | public | wrapper | `ckpt/causal-forcing/framewise/causal_forcing.pt` | run in the common long-horizon I2V rollout wrapper (6 frames per block, image-conditioned; checkpoint-specific denoising schedule). Read as deployment sensitivity only. |
| Causal-Forcing++ (2-step, frame-wise) | public | released | `ckpt/causal-forcing++/framewise-2step.pt` | run at its native pure-framewise config (configs/framewise_native_i2v.yaml); a genuine native-setting run at 60s and beyond. |
| Self-Forcing | public | wrapper | `ckpt/Self-Forcing/checkpoints/self_forcing_dmd.pt` | run in the common long-horizon I2V rollout wrapper (6 frames per block, image-conditioned; checkpoint-specific denoising schedule). Read as deployment sensitivity only. |
| CausVid | public | wrapper | `ckpt/CausVid/autoregressive_checkpoint/model.pt` | run in the common long-horizon I2V rollout wrapper (6 frames per block, image-conditioned; checkpoint-specific denoising schedule). Read as deployment sensitivity only. |
| Wan2.1-I2V-14B-480P | public | released | `ckpt/wan_models/Wan2.1-I2V-14B-480P` | bidirectional 14B, native config, 5s only (fixed-length model) |
| Wan2.2-I2V-A14B | public | released | `ckpt/wan_models/Wan2.2-I2V-A14B` | bidirectional MoE, native config, 5s only |
| LTX-Video 13B-0.9.8-distilled | public | released | `baseline_repos/LTX-Video` | bidirectional, native config, 5s only |
| Steady-Forcing | internal | wrapper | `ckpt/Steady-Forcing/steady_forcing_t2v.pt` | OUR prior work - excluded |
| RA-I2V (rt500) | internal | wrapper | `runs/.../rt500` | OUR method - excluded |
| RA-I2V-v1 (phase7_500) | internal | wrapper | `runs/phase7_nfpb6/checkpoint_model_000500/model.pt` | OUR method - excluded |
| nfpb=1 control | internal | wrapper | -- | OUR training control - excluded |
| nfpb=1 control @nfpb=1 | internal | released | -- | OUR training control - excluded |
| phase7 @nfpb=1 | internal | released | -- | OUR training control - excluded |
| ablation: region+static | internal | wrapper | -- | OUR ablation - excluded |
| ablation: Re-DMD | internal | wrapper | -- | OUR ablation - excluded |
| ablation: RS+Re-DMD | internal | wrapper | -- | OUR ablation - excluded |
| ablation: v2 | internal | wrapper | -- | OUR ablation - excluded |
| phase7 ckpt 100 | internal | wrapper | -- | checkpoint ladder - excluded |
| phase7 ckpt 200 | internal | wrapper | -- | checkpoint ladder - excluded |
| phase7 ckpt 300 | internal | wrapper | -- | checkpoint ladder - excluded |
| phase7 ckpt 400 | internal | wrapper | -- | checkpoint ladder - excluded |
| Causal-Forcing++ (1-step, frame-wise) | public | released | `ckpt/causal-forcing++/framewise-1step.pt` | native pure-framewise config; partial coverage (50/65) |
| Causal-Forcing++ (2-step) +color-match | postproc | wrapper | -- | post-hoc color match of chunk6 |
| RA-I2V +color-match | internal | wrapper | -- | OUR method - excluded |
| RA-I2V-v1 +color-match | internal | wrapper | -- | OUR method - excluded |
| nfpb=1 control +color-match | internal | wrapper | -- | OUR control - excluded |
| (scratch) | scratch | wrapper | -- | debug run |

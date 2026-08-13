# DAR negative incidence — public methods

DAR is stored **signed** and reported clipped to $[0,1]$ (METRIC_SPEC v1.0 §2). A negative value means global-motion compensation *increased* measured dynamic-region flow, which occurs where local flow opposes the estimated global field. This is the empirical reason DAR is not a causal decomposition of motion.

Overall across all entries: **129 / 1345** clip-metrics negative (9.6%).

| Method | track | dur | n | negative | rate | most negative |
|---|---|---|---|---|---|---|
| CausVid | i2v | 120s | 1 | 1 | 100.0% | -0.076 |
| CausVid | i2v | 240s | 5 | 0 | 0.0% | 0.000 |
| CausVid | i2v | 5s | 10 | 6 | 60.0% | -0.450 |
| CausVid | i2v | 60s | 1 | 0 | 0.0% | 0.028 |
| Causal-Forcing++ (1-step) | i2v | 120s | 20 | 1 | 5.0% | -0.012 |
| Causal-Forcing++ (1-step) | i2v | 240s | 1 | 0 | 0.0% | 0.403 |
| Causal-Forcing++ (1-step) | i2v | 5s | 10 | 0 | 0.0% | 0.041 |
| Causal-Forcing++ (1-step) | i2v | 60s | 30 | 0 | 0.0% | 0.035 |
| Causal-Forcing (framewise) | i2v | 120s | 1 | 0 | 0.0% | 0.311 |
| Causal-Forcing (framewise) | i2v | 240s | 5 | 0 | 0.0% | 0.046 |
| Causal-Forcing (framewise) | i2v | 5s | 10 | 2 | 20.0% | -0.043 |
| Causal-Forcing (framewise) | i2v | 60s | 1 | 0 | 0.0% | 0.297 |
| Causal-Forcing++ (2-step) | i2v | 120s | 20 | 0 | 0.0% | 0.008 |
| Causal-Forcing++ (2-step) | i2v | 240s | 5 | 0 | 0.0% | 0.053 |
| Causal-Forcing++ (2-step) | i2v | 5s | 10 | 1 | 10.0% | -0.102 |
| Causal-Forcing++ (2-step) | i2v | 60s | 30 | 0 | 0.0% | 0.005 |
| Causal-Forcing++ (1-step, native) | i2v | 120s | 20 | 1 | 5.0% | -0.062 |
| Causal-Forcing++ (1-step, native) | i2v | 60s | 30 | 3 | 10.0% | -0.770 |
| Causal-Forcing++ (2-step, native nfpb=1) | i2v | 120s | 20 | 3 | 15.0% | -0.192 |
| Causal-Forcing++ (2-step, native nfpb=1) | i2v | 240s | 5 | 2 | 40.0% | -0.164 |
| Causal-Forcing++ (2-step, native nfpb=1) | i2v | 5s | 10 | 1 | 10.0% | -0.133 |
| Causal-Forcing++ (2-step, native nfpb=1) | i2v | 60s | 30 | 2 | 6.7% | -0.014 |
| LTX-Video 13B-0.9.8-distilled | i2v | 5s | 10 | 4 | 40.0% | -0.031 |
| Self-Forcing | i2v | 120s | 20 | 3 | 15.0% | -0.131 |
| Self-Forcing | i2v | 240s | 5 | 2 | 40.0% | -0.012 |
| Self-Forcing | i2v | 5s | 10 | 2 | 20.0% | -0.026 |
| Self-Forcing | i2v | 60s | 30 | 8 | 26.7% | -0.569 |
| Wan2.1-I2V-14B-480P | i2v | 5s | 10 | 1 | 10.0% | -0.242 |
| Wan2.2-I2V-A14B | i2v | 5s | 10 | 1 | 10.0% | -0.490 |
| CausVid | t2v | 60s | 23 | 2 | 8.7% | -0.180 |
| Causal-Forcing | t2v | 60s | 23 | 3 | 13.0% | -0.594 |
| Infinite-Forcing | t2v | 60s | 23 | 1 | 4.3% | -0.047 |
| LongLive | t2v | 60s | 23 | 3 | 13.0% | -0.056 |
| Reward-Forcing | t2v | 60s | 23 | 5 | 21.7% | -0.308 |
| Rolling-Forcing | t2v | 60s | 24 | 4 | 16.7% | -0.204 |
| Self-Forcing | t2v | 60s | 23 | 4 | 17.4% | -0.148 |

# Paired significance — I2V @ 5s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 3.688 vs 5.279 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 10 | 3.688 vs 16.075 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 3.688 vs 1.218 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 3.688 vs 9.665 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 3.688 vs 15.230 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 3.688 vs 5.014 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 3.688 vs 6.308 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 3.688 vs 6.646 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 10 | 5.279 vs 16.075 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 5.279 vs 1.218 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 5.279 vs 9.665 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 5.279 vs 15.230 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 5.279 vs 5.014 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 5.279 vs 6.308 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 5.279 vs 6.646 | 6/10 | 0.7539 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 16.075 vs 1.218 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing (framewise) | Self-Forcing | 10 | 16.075 vs 9.665 | 3/10 | 0.3438 | no |
| Causal-Forcing (framewise) | CausVid | 10 | 16.075 vs 15.230 | 5/10 | 1.0000 | no |
| Causal-Forcing (framewise) | Wan2.1-I2V-14B-480P | 10 | 16.075 vs 5.014 | 2/10 | 0.1094 | no |
| Causal-Forcing (framewise) | Wan2.2-I2V-A14B | 10 | 16.075 vs 6.308 | 3/10 | 0.3438 | no |
| Causal-Forcing (framewise) | LTX-Video 13B-0.9.8-distilled | 10 | 16.075 vs 6.646 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 10 | 1.218 vs 9.665 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 10 | 1.218 vs 15.230 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.1-I2V-14B-480P | 10 | 1.218 vs 5.014 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.2-I2V-A14B | 10 | 1.218 vs 6.308 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | LTX-Video 13B-0.9.8-distilled | 10 | 1.218 vs 6.646 | 7/10 | 0.3438 | no |
| Self-Forcing | CausVid | 10 | 9.665 vs 15.230 | 9/10 | 0.0215 | **yes** |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 9.665 vs 5.014 | 3/10 | 0.3438 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 9.665 vs 6.308 | 4/10 | 0.7539 | no |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 9.665 vs 6.646 | 4/10 | 0.7539 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 15.230 vs 5.014 | 2/10 | 0.1094 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | 15.230 vs 6.308 | 2/10 | 0.1094 | no |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 15.230 vs 6.646 | 1/10 | 0.0215 | **yes** |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 5.014 vs 6.308 | 8/10 | 0.1094 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 5.014 vs 6.646 | 7/10 | 0.3438 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 6.308 vs 6.646 | 5/10 | 1.0000 | no |

## NBF (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 20.010 vs 22.863 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 10 | 20.010 vs 90.659 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 20.010 vs 21.227 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 20.010 vs 11.484 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 20.010 vs 21.502 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 20.010 vs 42.577 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 20.010 vs 50.584 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 20.010 vs 53.448 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 10 | 22.863 vs 90.659 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 22.863 vs 21.227 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 22.863 vs 11.484 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | CausVid | 10 | 22.863 vs 21.502 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 22.863 vs 42.577 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 22.863 vs 50.584 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 22.863 vs 53.448 | 7/10 | 0.3438 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 90.659 vs 21.227 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing (framewise) | Self-Forcing | 10 | 90.659 vs 11.484 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing (framewise) | CausVid | 10 | 90.659 vs 21.502 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing (framewise) | Wan2.1-I2V-14B-480P | 10 | 90.659 vs 42.577 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing (framewise) | Wan2.2-I2V-A14B | 10 | 90.659 vs 50.584 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing (framewise) | LTX-Video 13B-0.9.8-distilled | 10 | 90.659 vs 53.448 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 10 | 21.227 vs 11.484 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 10 | 21.227 vs 21.502 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.1-I2V-14B-480P | 10 | 21.227 vs 42.577 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.2-I2V-A14B | 10 | 21.227 vs 50.584 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | LTX-Video 13B-0.9.8-distilled | 10 | 21.227 vs 53.448 | 8/10 | 0.1094 | no |
| Self-Forcing | CausVid | 10 | 11.484 vs 21.502 | 7/10 | 0.3438 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 11.484 vs 42.577 | 5/10 | 1.0000 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 11.484 vs 50.584 | 9/10 | 0.0215 | **yes** |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 11.484 vs 53.448 | 8/10 | 0.1094 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 21.502 vs 42.577 | 3/10 | 0.3438 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | 21.502 vs 50.584 | 7/10 | 0.3438 | no |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 21.502 vs 53.448 | 8/10 | 0.1094 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 42.577 vs 50.584 | 8/10 | 0.1094 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 42.577 vs 53.448 | 7/10 | 0.3438 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 50.584 vs 53.448 | 6/10 | 0.7539 | no |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 0.884 vs 0.663 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 10 | 0.884 vs 0.395 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.884 vs 0.488 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.884 vs 0.649 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.884 vs 0.946 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.884 vs 1.035 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.884 vs 0.948 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 9 | 0.884 vs 0.899 | 5/9 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 10 | 0.663 vs 0.395 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.663 vs 0.488 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.663 vs 0.649 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.663 vs 0.946 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.663 vs 1.035 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.663 vs 0.948 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.663 vs 0.899 | 3/10 | 0.3438 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.395 vs 0.488 | 4/10 | 0.7539 | no |
| Causal-Forcing (framewise) | Self-Forcing | 10 | 0.395 vs 0.649 | 2/10 | 0.1094 | no |
| Causal-Forcing (framewise) | CausVid | 10 | 0.395 vs 0.946 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing (framewise) | Wan2.1-I2V-14B-480P | 10 | 0.395 vs 1.035 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing (framewise) | Wan2.2-I2V-A14B | 10 | 0.395 vs 0.948 | 2/10 | 0.1094 | no |
| Causal-Forcing (framewise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.395 vs 0.899 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 10 | 0.488 vs 0.649 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 10 | 0.488 vs 0.946 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.1-I2V-14B-480P | 10 | 0.488 vs 1.035 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.2-I2V-A14B | 10 | 0.488 vs 0.948 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | LTX-Video 13B-0.9.8-distilled | 10 | 0.488 vs 0.899 | 2/10 | 0.1094 | no |
| Self-Forcing | CausVid | 10 | 0.649 vs 0.946 | 4/10 | 0.7539 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 0.649 vs 1.035 | 3/10 | 0.3438 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 0.649 vs 0.948 | 4/10 | 0.7539 | no |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 0.649 vs 0.899 | 4/10 | 0.7539 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 0.946 vs 1.035 | 5/10 | 1.0000 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | 0.946 vs 0.948 | 5/10 | 1.0000 | no |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 0.946 vs 0.899 | 6/10 | 0.7539 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 1.035 vs 0.948 | 6/10 | 0.7539 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 1.035 vs 0.899 | 6/10 | 0.7539 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 0.948 vs 0.899 | 5/10 | 1.0000 | no |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 0.651 vs 0.508 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 10 | 0.651 vs 3.281 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.651 vs 0.830 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.651 vs 0.330 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.651 vs 0.902 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.651 vs 4.845 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.651 vs 9.079 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.651 vs 3.677 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 10 | 0.508 vs 3.281 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.508 vs 0.830 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.508 vs 0.330 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.508 vs 0.902 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.508 vs 4.845 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.508 vs 9.079 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.508 vs 3.677 | 3/10 | 0.3438 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 3.281 vs 0.830 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (framewise) | Self-Forcing | 10 | 3.281 vs 0.330 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing (framewise) | CausVid | 10 | 3.281 vs 0.902 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (framewise) | Wan2.1-I2V-14B-480P | 10 | 3.281 vs 4.845 | 8/10 | 0.1094 | no |
| Causal-Forcing (framewise) | Wan2.2-I2V-A14B | 10 | 3.281 vs 9.079 | 7/10 | 0.3438 | no |
| Causal-Forcing (framewise) | LTX-Video 13B-0.9.8-distilled | 10 | 3.281 vs 3.677 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 10 | 0.830 vs 0.330 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 10 | 0.830 vs 0.902 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.1-I2V-14B-480P | 10 | 0.830 vs 4.845 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.2-I2V-A14B | 10 | 0.830 vs 9.079 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | LTX-Video 13B-0.9.8-distilled | 10 | 0.830 vs 3.677 | 3/10 | 0.3438 | no |
| Self-Forcing | CausVid | 10 | 0.330 vs 0.902 | 4/10 | 0.7539 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 0.330 vs 4.845 | 3/10 | 0.3438 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 0.330 vs 9.079 | 1/10 | 0.0215 | **yes** |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 0.330 vs 3.677 | 2/10 | 0.1094 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 0.902 vs 4.845 | 3/10 | 0.3438 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | 0.902 vs 9.079 | 1/10 | 0.0215 | **yes** |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 0.902 vs 3.677 | 3/10 | 0.3438 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 4.845 vs 9.079 | 2/10 | 0.1094 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 4.845 vs 3.677 | 4/10 | 0.7539 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 9.079 vs 3.677 | 4/10 | 0.7539 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 0.811 vs 0.662 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 10 | 0.811 vs 3.564 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.811 vs 0.885 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.811 vs 0.346 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.811 vs 0.887 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.811 vs 5.707 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.811 vs 9.819 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.811 vs 3.945 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 10 | 0.662 vs 3.564 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.662 vs 0.885 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.662 vs 0.346 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.662 vs 0.887 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.662 vs 5.707 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.662 vs 9.819 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.662 vs 3.945 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 3.564 vs 0.885 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (framewise) | Self-Forcing | 10 | 3.564 vs 0.346 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing (framewise) | CausVid | 10 | 3.564 vs 0.887 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (framewise) | Wan2.1-I2V-14B-480P | 10 | 3.564 vs 5.707 | 8/10 | 0.1094 | no |
| Causal-Forcing (framewise) | Wan2.2-I2V-A14B | 10 | 3.564 vs 9.819 | 7/10 | 0.3438 | no |
| Causal-Forcing (framewise) | LTX-Video 13B-0.9.8-distilled | 10 | 3.564 vs 3.945 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 10 | 0.885 vs 0.346 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 10 | 0.885 vs 0.887 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.1-I2V-14B-480P | 10 | 0.885 vs 5.707 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.2-I2V-A14B | 10 | 0.885 vs 9.819 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | LTX-Video 13B-0.9.8-distilled | 10 | 0.885 vs 3.945 | 2/10 | 0.1094 | no |
| Self-Forcing | CausVid | 10 | 0.346 vs 0.887 | 5/10 | 1.0000 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 0.346 vs 5.707 | 3/10 | 0.3438 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 0.346 vs 9.819 | 0/10 | 0.0020 | **yes** |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 0.346 vs 3.945 | 2/10 | 0.1094 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 0.887 vs 5.707 | 3/10 | 0.3438 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | 0.887 vs 9.819 | 0/10 | 0.0020 | **yes** |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 0.887 vs 3.945 | 1/10 | 0.0215 | **yes** |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 5.707 vs 9.819 | 1/10 | 0.0215 | **yes** |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 5.707 vs 3.945 | 4/10 | 0.7539 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 9.819 vs 3.945 | 5/10 | 1.0000 | no |

## DLR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 0.672 vs 0.661 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 10 | 0.672 vs 0.678 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.672 vs 0.681 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.672 vs 0.737 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.672 vs 1.042 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.672 vs 0.524 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.672 vs 0.496 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.672 vs 0.388 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 10 | 0.661 vs 0.678 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.661 vs 0.681 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.661 vs 0.737 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.661 vs 1.042 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.661 vs 0.524 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.661 vs 0.496 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.661 vs 0.388 | 3/10 | 0.3438 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.678 vs 0.681 | 6/10 | 0.7539 | no |
| Causal-Forcing (framewise) | Self-Forcing | 10 | 0.678 vs 0.737 | 4/10 | 0.7539 | no |
| Causal-Forcing (framewise) | CausVid | 10 | 0.678 vs 1.042 | 7/10 | 0.3438 | no |
| Causal-Forcing (framewise) | Wan2.1-I2V-14B-480P | 10 | 0.678 vs 0.524 | 3/10 | 0.3438 | no |
| Causal-Forcing (framewise) | Wan2.2-I2V-A14B | 10 | 0.678 vs 0.496 | 2/10 | 0.1094 | no |
| Causal-Forcing (framewise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.678 vs 0.388 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 10 | 0.681 vs 0.737 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 10 | 0.681 vs 1.042 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.1-I2V-14B-480P | 10 | 0.681 vs 0.524 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.2-I2V-A14B | 10 | 0.681 vs 0.496 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | LTX-Video 13B-0.9.8-distilled | 10 | 0.681 vs 0.388 | 4/10 | 0.7539 | no |
| Self-Forcing | CausVid | 10 | 0.737 vs 1.042 | 7/10 | 0.3438 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 0.737 vs 0.524 | 4/10 | 0.7539 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 0.737 vs 0.496 | 4/10 | 0.7539 | no |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 0.737 vs 0.388 | 2/10 | 0.1094 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 1.042 vs 0.524 | 1/10 | 0.0215 | **yes** |
| CausVid | Wan2.2-I2V-A14B | 10 | 1.042 vs 0.496 | 1/10 | 0.0215 | **yes** |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 1.042 vs 0.388 | 2/10 | 0.1094 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 0.524 vs 0.496 | 5/10 | 1.0000 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 0.524 vs 0.388 | 3/10 | 0.3438 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 0.496 vs 0.388 | 4/10 | 0.7539 | no |

## DAR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 0.212 vs 0.243 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 10 | 0.212 vs 0.117 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.212 vs 0.092 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.212 vs 0.071 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.212 vs -0.057 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.212 vs 0.133 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.212 vs 0.213 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.212 vs 0.179 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 10 | 0.243 vs 0.117 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.243 vs 0.092 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.243 vs 0.071 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.243 vs -0.057 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.243 vs 0.133 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.243 vs 0.213 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.243 vs 0.179 | 2/10 | 0.1094 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 10 | 0.117 vs 0.092 | 7/10 | 0.3438 | no |
| Causal-Forcing (framewise) | Self-Forcing | 10 | 0.117 vs 0.071 | 5/10 | 1.0000 | no |
| Causal-Forcing (framewise) | CausVid | 10 | 0.117 vs -0.057 | 3/10 | 0.3438 | no |
| Causal-Forcing (framewise) | Wan2.1-I2V-14B-480P | 10 | 0.117 vs 0.133 | 7/10 | 0.3438 | no |
| Causal-Forcing (framewise) | Wan2.2-I2V-A14B | 10 | 0.117 vs 0.213 | 7/10 | 0.3438 | no |
| Causal-Forcing (framewise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.117 vs 0.179 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 10 | 0.092 vs 0.071 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 10 | 0.092 vs -0.057 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.1-I2V-14B-480P | 10 | 0.092 vs 0.133 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Wan2.2-I2V-A14B | 10 | 0.092 vs 0.213 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | LTX-Video 13B-0.9.8-distilled | 10 | 0.092 vs 0.179 | 2/10 | 0.1094 | no |
| Self-Forcing | CausVid | 10 | 0.071 vs -0.057 | 3/10 | 0.3438 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 0.071 vs 0.133 | 5/10 | 1.0000 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 0.071 vs 0.213 | 5/10 | 1.0000 | no |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 0.071 vs 0.179 | 4/10 | 0.7539 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | -0.057 vs 0.133 | 7/10 | 0.3438 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | -0.057 vs 0.213 | 7/10 | 0.3438 | no |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | -0.057 vs 0.179 | 6/10 | 0.7539 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 0.133 vs 0.213 | 4/10 | 0.7539 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 0.133 vs 0.179 | 3/10 | 0.3438 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 0.213 vs 0.179 | 3/10 | 0.3438 | no |

# Paired significance — I2V @ 5s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 3.688 vs 5.279 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 10 | 3.688 vs 16.075 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 3.688 vs 1.218 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 3.688 vs 9.665 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 3.688 vs 15.230 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 3.688 vs 5.014 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 3.688 vs 6.308 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 3.688 vs 6.646 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 10 | 5.279 vs 16.075 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 5.279 vs 1.218 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 5.279 vs 9.665 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 5.279 vs 15.230 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 5.279 vs 5.014 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 5.279 vs 6.308 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 5.279 vs 6.646 | 6/10 | 0.7539 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 10 | 16.075 vs 1.218 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing (frame-wise) | Self-Forcing | 10 | 16.075 vs 9.665 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | CausVid | 10 | 16.075 vs 15.230 | 5/10 | 1.0000 | no |
| Causal-Forcing (frame-wise) | Wan2.1-I2V-14B-480P | 10 | 16.075 vs 5.014 | 2/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | Wan2.2-I2V-A14B | 10 | 16.075 vs 6.308 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 16.075 vs 6.646 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 10 | 1.218 vs 9.665 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 10 | 1.218 vs 15.230 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.1-I2V-14B-480P | 10 | 1.218 vs 5.014 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.2-I2V-A14B | 10 | 1.218 vs 6.308 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 1.218 vs 6.646 | 7/10 | 0.3438 | no |
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
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 10.005 vs 11.432 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 10 | 10.005 vs 45.329 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 10.005 vs 10.614 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 10.005 vs 5.742 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 10.005 vs 10.751 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 10.005 vs 21.289 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 10.005 vs 25.292 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 10.005 vs 17.816 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 10 | 11.432 vs 45.329 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 11.432 vs 10.614 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 11.432 vs 5.742 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | CausVid | 10 | 11.432 vs 10.751 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 11.432 vs 21.289 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 11.432 vs 25.292 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 11.432 vs 17.816 | 5/10 | 1.0000 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 10 | 45.329 vs 10.614 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing (frame-wise) | Self-Forcing | 10 | 45.329 vs 5.742 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 10 | 45.329 vs 10.751 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing (frame-wise) | Wan2.1-I2V-14B-480P | 10 | 45.329 vs 21.289 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing (frame-wise) | Wan2.2-I2V-A14B | 10 | 45.329 vs 25.292 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing (frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 45.329 vs 17.816 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 10 | 10.614 vs 5.742 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 10 | 10.614 vs 10.751 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.1-I2V-14B-480P | 10 | 10.614 vs 21.289 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.2-I2V-A14B | 10 | 10.614 vs 25.292 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 10.614 vs 17.816 | 6/10 | 0.7539 | no |
| Self-Forcing | CausVid | 10 | 5.742 vs 10.751 | 7/10 | 0.3438 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 5.742 vs 21.289 | 5/10 | 1.0000 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 5.742 vs 25.292 | 9/10 | 0.0215 | **yes** |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 5.742 vs 17.816 | 7/10 | 0.3438 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 10.751 vs 21.289 | 3/10 | 0.3438 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | 10.751 vs 25.292 | 7/10 | 0.3438 | no |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 10.751 vs 17.816 | 7/10 | 0.3438 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 21.289 vs 25.292 | 8/10 | 0.1094 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 21.289 vs 17.816 | 7/10 | 0.3438 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 25.292 vs 17.816 | 5/10 | 1.0000 | no |

## MCFF-E (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 1.057 vs 1.048 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 10 | 1.057 vs 8.475 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 1.057 vs 2.228 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 1.057 vs 0.686 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 1.057 vs 0.761 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 1.057 vs 6.666 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 1.057 vs 4.326 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 1.057 vs 3.595 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 10 | 1.048 vs 8.475 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 1.048 vs 2.228 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 1.048 vs 0.686 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 1.048 vs 0.761 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 1.048 vs 6.666 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 1.048 vs 4.326 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 1.048 vs 3.595 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 10 | 8.475 vs 2.228 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (frame-wise) | Self-Forcing | 10 | 8.475 vs 0.686 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 10 | 8.475 vs 0.761 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing (frame-wise) | Wan2.1-I2V-14B-480P | 10 | 8.475 vs 6.666 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (frame-wise) | Wan2.2-I2V-A14B | 10 | 8.475 vs 4.326 | 8/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 8.475 vs 3.595 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 10 | 2.228 vs 0.686 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 10 | 2.228 vs 0.761 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.1-I2V-14B-480P | 10 | 2.228 vs 6.666 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.2-I2V-A14B | 10 | 2.228 vs 4.326 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 2.228 vs 3.595 | 5/10 | 1.0000 | no |
| Self-Forcing | CausVid | 10 | 0.686 vs 0.761 | 4/10 | 0.7539 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 0.686 vs 6.666 | 4/10 | 0.7539 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 0.686 vs 4.326 | 1/10 | 0.0215 | **yes** |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 0.686 vs 3.595 | 2/10 | 0.1094 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 0.761 vs 6.666 | 2/10 | 0.1094 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | 0.761 vs 4.326 | 1/10 | 0.0215 | **yes** |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 0.761 vs 3.595 | 2/10 | 0.1094 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 6.666 vs 4.326 | 2/10 | 0.1094 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 6.666 vs 3.595 | 4/10 | 0.7539 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 4.326 vs 3.595 | 6/10 | 0.7539 | no |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 0.607 vs 0.468 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 10 | 0.607 vs 2.793 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.607 vs 0.781 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.607 vs 0.263 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.607 vs 0.871 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.607 vs 5.575 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.607 vs 9.092 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.607 vs 3.477 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 10 | 0.468 vs 2.793 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.468 vs 0.781 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.468 vs 0.263 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.468 vs 0.871 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.468 vs 5.575 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.468 vs 9.092 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.468 vs 3.477 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 10 | 2.793 vs 0.781 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (frame-wise) | Self-Forcing | 10 | 2.793 vs 0.263 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 10 | 2.793 vs 0.871 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (frame-wise) | Wan2.1-I2V-14B-480P | 10 | 2.793 vs 5.575 | 8/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | Wan2.2-I2V-A14B | 10 | 2.793 vs 9.092 | 4/10 | 0.7539 | no |
| Causal-Forcing (frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 2.793 vs 3.477 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 10 | 0.781 vs 0.263 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 10 | 0.781 vs 0.871 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.1-I2V-14B-480P | 10 | 0.781 vs 5.575 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.2-I2V-A14B | 10 | 0.781 vs 9.092 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.781 vs 3.477 | 3/10 | 0.3438 | no |
| Self-Forcing | CausVid | 10 | 0.263 vs 0.871 | 3/10 | 0.3438 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 0.263 vs 5.575 | 2/10 | 0.1094 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 0.263 vs 9.092 | 0/10 | 0.0020 | **yes** |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 0.263 vs 3.477 | 2/10 | 0.1094 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 0.871 vs 5.575 | 3/10 | 0.3438 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | 0.871 vs 9.092 | 1/10 | 0.0215 | **yes** |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 0.871 vs 3.477 | 3/10 | 0.3438 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 5.575 vs 9.092 | 1/10 | 0.0215 | **yes** |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 5.575 vs 3.477 | 4/10 | 0.7539 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 9.092 vs 3.477 | 4/10 | 0.7539 | no |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 0.778 vs 0.640 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 10 | 0.778 vs 0.433 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.778 vs 0.467 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.778 vs 0.696 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.778 vs 0.977 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.778 vs 1.089 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.778 vs 0.953 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.778 vs 0.915 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 10 | 0.640 vs 0.433 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.640 vs 0.467 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.640 vs 0.696 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.640 vs 0.977 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.640 vs 1.089 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.640 vs 0.953 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.640 vs 0.915 | 4/10 | 0.7539 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.433 vs 0.467 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 10 | 0.433 vs 0.696 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | CausVid | 10 | 0.433 vs 0.977 | 2/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | Wan2.1-I2V-14B-480P | 10 | 0.433 vs 1.089 | 2/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | Wan2.2-I2V-A14B | 10 | 0.433 vs 0.953 | 2/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.433 vs 0.915 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 10 | 0.467 vs 0.696 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 10 | 0.467 vs 0.977 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.1-I2V-14B-480P | 10 | 0.467 vs 1.089 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.2-I2V-A14B | 10 | 0.467 vs 0.953 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.467 vs 0.915 | 2/10 | 0.1094 | no |
| Self-Forcing | CausVid | 10 | 0.696 vs 0.977 | 4/10 | 0.7539 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 0.696 vs 1.089 | 3/10 | 0.3438 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 0.696 vs 0.953 | 5/10 | 1.0000 | no |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 0.696 vs 0.915 | 5/10 | 1.0000 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | 0.977 vs 1.089 | 4/10 | 0.7539 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | 0.977 vs 0.953 | 5/10 | 1.0000 | no |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | 0.977 vs 0.915 | 5/10 | 1.0000 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 1.089 vs 0.953 | 6/10 | 0.7539 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 1.089 vs 0.915 | 6/10 | 0.7539 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 0.953 vs 0.915 | 5/10 | 1.0000 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 0.811 vs 0.662 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 10 | 0.811 vs 3.564 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.811 vs 0.885 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.811 vs 0.346 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.811 vs 0.887 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.811 vs 5.707 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.811 vs 9.819 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.811 vs 3.945 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 10 | 0.662 vs 3.564 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.662 vs 0.885 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.662 vs 0.346 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.662 vs 0.887 | 8/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.662 vs 5.707 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.662 vs 9.819 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.662 vs 3.945 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 10 | 3.564 vs 0.885 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (frame-wise) | Self-Forcing | 10 | 3.564 vs 0.346 | 10/10 | 0.0020 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 10 | 3.564 vs 0.887 | 9/10 | 0.0215 | **yes** |
| Causal-Forcing (frame-wise) | Wan2.1-I2V-14B-480P | 10 | 3.564 vs 5.707 | 8/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | Wan2.2-I2V-A14B | 10 | 3.564 vs 9.819 | 7/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 3.564 vs 3.945 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 10 | 0.885 vs 0.346 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 10 | 0.885 vs 0.887 | 7/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.1-I2V-14B-480P | 10 | 0.885 vs 5.707 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.2-I2V-A14B | 10 | 0.885 vs 9.819 | 0/10 | 0.0020 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.885 vs 3.945 | 2/10 | 0.1094 | no |
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
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 10 | 0.672 vs 0.678 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.672 vs 0.681 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.672 vs 0.737 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.672 vs 1.042 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.672 vs 0.524 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.672 vs 0.496 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.672 vs 0.388 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 10 | 0.661 vs 0.678 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.661 vs 0.681 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.661 vs 0.737 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.661 vs 1.042 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.661 vs 0.524 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.661 vs 0.496 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.661 vs 0.388 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.678 vs 0.681 | 6/10 | 0.7539 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 10 | 0.678 vs 0.737 | 4/10 | 0.7539 | no |
| Causal-Forcing (frame-wise) | CausVid | 10 | 0.678 vs 1.042 | 7/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | Wan2.1-I2V-14B-480P | 10 | 0.678 vs 0.524 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | Wan2.2-I2V-A14B | 10 | 0.678 vs 0.496 | 2/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.678 vs 0.388 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 10 | 0.681 vs 0.737 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 10 | 0.681 vs 1.042 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.1-I2V-14B-480P | 10 | 0.681 vs 0.524 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.2-I2V-A14B | 10 | 0.681 vs 0.496 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.681 vs 0.388 | 4/10 | 0.7539 | no |
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
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 10 | 0.302 vs 0.293 | 5/10 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 10 | 0.302 vs 0.294 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.302 vs 0.171 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 10 | 0.302 vs 0.214 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step) | CausVid | 10 | 0.302 vs -0.137 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (2-step) | Wan2.1-I2V-14B-480P | 10 | 0.302 vs 0.154 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | Wan2.2-I2V-A14B | 10 | 0.302 vs 0.241 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.302 vs 0.238 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 10 | 0.293 vs 0.294 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.293 vs 0.171 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 10 | 0.293 vs 0.214 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | CausVid | 10 | 0.293 vs -0.137 | 1/10 | 0.0215 | **yes** |
| Causal-Forcing++ (1-step) | Wan2.1-I2V-14B-480P | 10 | 0.293 vs 0.154 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (1-step) | Wan2.2-I2V-A14B | 10 | 0.293 vs 0.241 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (1-step) | LTX-Video 13B-0.9.8-distilled | 10 | 0.293 vs 0.238 | 2/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 10 | 0.294 vs 0.171 | 4/10 | 0.7539 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 10 | 0.294 vs 0.214 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | CausVid | 10 | 0.294 vs -0.137 | 2/10 | 0.1094 | no |
| Causal-Forcing (frame-wise) | Wan2.1-I2V-14B-480P | 10 | 0.294 vs 0.154 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | Wan2.2-I2V-A14B | 10 | 0.294 vs 0.241 | 3/10 | 0.3438 | no |
| Causal-Forcing (frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.294 vs 0.238 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 10 | 0.171 vs 0.214 | 6/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 10 | 0.171 vs -0.137 | 2/10 | 0.1094 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.1-I2V-14B-480P | 10 | 0.171 vs 0.154 | 3/10 | 0.3438 | no |
| Causal-Forcing++ (2-step, frame-wise) | Wan2.2-I2V-A14B | 10 | 0.171 vs 0.241 | 4/10 | 0.7539 | no |
| Causal-Forcing++ (2-step, frame-wise) | LTX-Video 13B-0.9.8-distilled | 10 | 0.171 vs 0.238 | 3/10 | 0.3438 | no |
| Self-Forcing | CausVid | 10 | 0.214 vs -0.137 | 2/10 | 0.1094 | no |
| Self-Forcing | Wan2.1-I2V-14B-480P | 10 | 0.214 vs 0.154 | 3/10 | 0.3438 | no |
| Self-Forcing | Wan2.2-I2V-A14B | 10 | 0.214 vs 0.241 | 3/10 | 0.3438 | no |
| Self-Forcing | LTX-Video 13B-0.9.8-distilled | 10 | 0.214 vs 0.238 | 4/10 | 0.7539 | no |
| CausVid | Wan2.1-I2V-14B-480P | 10 | -0.137 vs 0.154 | 6/10 | 0.7539 | no |
| CausVid | Wan2.2-I2V-A14B | 10 | -0.137 vs 0.241 | 7/10 | 0.3438 | no |
| CausVid | LTX-Video 13B-0.9.8-distilled | 10 | -0.137 vs 0.238 | 5/10 | 1.0000 | no |
| Wan2.1-I2V-14B-480P | Wan2.2-I2V-A14B | 10 | 0.154 vs 0.241 | 6/10 | 0.7539 | no |
| Wan2.1-I2V-14B-480P | LTX-Video 13B-0.9.8-distilled | 10 | 0.154 vs 0.238 | 6/10 | 0.7539 | no |
| Wan2.2-I2V-A14B | LTX-Video 13B-0.9.8-distilled | 10 | 0.241 vs 0.238 | 5/10 | 1.0000 | no |

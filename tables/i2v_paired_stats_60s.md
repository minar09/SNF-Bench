# Paired significance — I2V @ 60s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 29 | 8.816 vs 5.338 | 9/29 | 0.0614 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 30 | 9.177 vs 21.147 | 26/30 | 0.0001 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 9.177 vs 9.935 | 11/30 | 0.2005 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 9.177 vs 17.339 | 24/30 | 0.0014 | **yes** |
| Causal-Forcing++ (2-step) | CausVid | 29 | 8.816 vs 19.894 | 27/29 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 9.177 vs 10.388 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 29 | 5.338 vs 20.952 | 28/29 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 29 | 5.338 vs 9.276 | 14/29 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 29 | 5.338 vs 17.021 | 27/29 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | CausVid | 29 | 5.338 vs 19.894 | 28/29 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 29 | 5.338 vs 9.821 | 14/29 | 1.0000 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 21.147 vs 9.935 | 7/30 | 0.0052 | **yes** |
| Causal-Forcing (framewise) | Self-Forcing | 30 | 21.147 vs 17.339 | 9/30 | 0.0428 | **yes** |
| Causal-Forcing (framewise) | CausVid | 29 | 20.952 vs 19.894 | 12/29 | 0.4583 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (1-step, native) | 30 | 21.147 vs 10.388 | 9/30 | 0.0428 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 9.935 vs 17.339 | 24/30 | 0.0014 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 29 | 9.276 vs 19.894 | 25/29 | 0.0001 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 9.935 vs 10.388 | 16/30 | 0.8555 | no |
| Self-Forcing | CausVid | 29 | 17.021 vs 19.894 | 17/29 | 0.4583 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 17.339 vs 10.388 | 10/30 | 0.0987 | no |
| CausVid | Causal-Forcing++ (1-step, native) | 29 | 19.894 vs 9.821 | 6/29 | 0.0023 | **yes** |

## NBF (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 5.967 vs 7.051 | 22/30 | 0.0161 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 30 | 5.967 vs 36.391 | 30/30 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 5.967 vs 6.913 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 5.967 vs 5.520 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (2-step) | CausVid | 30 | 5.967 vs 3.307 | 3/30 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 5.967 vs 5.247 | 10/30 | 0.0987 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 30 | 7.051 vs 36.391 | 30/30 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 7.051 vs 6.913 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 7.051 vs 5.520 | 9/30 | 0.0428 | **yes** |
| Causal-Forcing++ (1-step) | CausVid | 30 | 7.051 vs 3.307 | 2/30 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 7.051 vs 5.247 | 11/30 | 0.2005 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 36.391 vs 6.913 | 3/30 | 0.0000 | **yes** |
| Causal-Forcing (framewise) | Self-Forcing | 30 | 36.391 vs 5.520 | 0/30 | 0.0000 | **yes** |
| Causal-Forcing (framewise) | CausVid | 30 | 36.391 vs 3.307 | 0/30 | 0.0000 | **yes** |
| Causal-Forcing (framewise) | Causal-Forcing++ (1-step, native) | 30 | 36.391 vs 5.247 | 0/30 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 6.913 vs 5.520 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 30 | 6.913 vs 3.307 | 6/30 | 0.0014 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 6.913 vs 5.247 | 13/30 | 0.5847 | no |
| Self-Forcing | CausVid | 30 | 5.520 vs 3.307 | 4/30 | 0.0001 | **yes** |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 5.520 vs 5.247 | 12/30 | 0.3616 | no |
| CausVid | Causal-Forcing++ (1-step, native) | 30 | 3.307 vs 5.247 | 21/30 | 0.0428 | **yes** |

## MCFF-E (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 30 | 0.855 vs 2.799 | 2/30 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | CausVid | 30 | 0.855 vs 0.578 | 23/30 | 0.0052 | **yes** |
| Causal-Forcing (framewise) | CausVid | 30 | 2.799 vs 0.578 | 25/30 | 0.0003 | **yes** |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.665 vs 0.574 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 30 | 0.665 vs 2.686 | 3/30 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.665 vs 0.814 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.665 vs 0.735 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step) | CausVid | 30 | 0.665 vs 0.408 | 24/30 | 0.0014 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.665 vs 0.525 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 30 | 0.574 vs 2.686 | 5/30 | 0.0003 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.574 vs 0.814 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.574 vs 0.735 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (1-step) | CausVid | 30 | 0.574 vs 0.408 | 23/30 | 0.0052 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.574 vs 0.525 | 15/30 | 1.0000 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 2.686 vs 0.814 | 24/30 | 0.0014 | **yes** |
| Causal-Forcing (framewise) | Self-Forcing | 30 | 2.686 vs 0.735 | 22/30 | 0.0161 | **yes** |
| Causal-Forcing (framewise) | CausVid | 30 | 2.686 vs 0.408 | 25/30 | 0.0003 | **yes** |
| Causal-Forcing (framewise) | Causal-Forcing++ (1-step, native) | 30 | 2.686 vs 0.525 | 25/30 | 0.0003 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.814 vs 0.735 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 30 | 0.814 vs 0.408 | 21/30 | 0.0428 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 0.814 vs 0.525 | 12/30 | 0.3616 | no |
| Self-Forcing | CausVid | 30 | 0.735 vs 0.408 | 21/30 | 0.0428 | **yes** |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.735 vs 0.525 | 15/30 | 1.0000 | no |
| CausVid | Causal-Forcing++ (1-step, native) | 30 | 0.408 vs 0.525 | 7/30 | 0.0052 | **yes** |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.858 vs 0.768 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 30 | 0.858 vs 0.893 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.858 vs 0.976 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.858 vs 0.879 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | CausVid | 30 | 0.858 vs 0.808 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.858 vs 0.970 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 30 | 0.768 vs 0.893 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.768 vs 0.976 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.768 vs 0.879 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | CausVid | 30 | 0.768 vs 0.808 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.768 vs 0.970 | 13/30 | 0.5847 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 29 | 0.893 vs 0.976 | 13/29 | 0.7111 | no |
| Causal-Forcing (framewise) | Self-Forcing | 30 | 0.893 vs 0.879 | 17/30 | 0.5847 | no |
| Causal-Forcing (framewise) | CausVid | 30 | 0.893 vs 0.808 | 16/30 | 0.8555 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (1-step, native) | 30 | 0.893 vs 0.970 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.976 vs 0.879 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 30 | 0.976 vs 0.808 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 28 | 0.976 vs 0.970 | 14/28 | 1.0000 | no |
| Self-Forcing | CausVid | 30 | 0.879 vs 0.808 | 13/30 | 0.5847 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.879 vs 0.970 | 14/30 | 0.8555 | no |
| CausVid | Causal-Forcing++ (1-step, native) | 30 | 0.808 vs 0.970 | 13/30 | 0.5847 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.740 vs 0.769 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 30 | 0.740 vs 3.612 | 2/30 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.740 vs 0.894 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.740 vs 0.772 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | CausVid | 30 | 0.740 vs 0.480 | 23/30 | 0.0052 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.740 vs 0.605 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 30 | 0.769 vs 3.612 | 3/30 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.769 vs 0.894 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.769 vs 0.772 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | CausVid | 30 | 0.769 vs 0.480 | 23/30 | 0.0052 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.769 vs 0.605 | 18/30 | 0.3616 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 3.612 vs 0.894 | 27/30 | 0.0000 | **yes** |
| Causal-Forcing (framewise) | Self-Forcing | 30 | 3.612 vs 0.772 | 26/30 | 0.0001 | **yes** |
| Causal-Forcing (framewise) | CausVid | 30 | 3.612 vs 0.480 | 27/30 | 0.0000 | **yes** |
| Causal-Forcing (framewise) | Causal-Forcing++ (1-step, native) | 30 | 3.612 vs 0.605 | 28/30 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.894 vs 0.772 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 30 | 0.894 vs 0.480 | 21/30 | 0.0428 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 0.894 vs 0.605 | 14/30 | 0.8555 | no |
| Self-Forcing | CausVid | 30 | 0.772 vs 0.480 | 23/30 | 0.0052 | **yes** |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.772 vs 0.605 | 15/30 | 1.0000 | no |
| CausVid | Causal-Forcing++ (1-step, native) | 30 | 0.480 vs 0.605 | 8/30 | 0.0161 | **yes** |

## DLR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.668 vs 0.637 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 30 | 0.668 vs 0.800 | 18/30 | 0.3616 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.668 vs 0.749 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.668 vs 0.674 | 18/30 | 0.3616 | no |
| Causal-Forcing++ (2-step) | CausVid | 30 | 0.668 vs 0.568 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.668 vs 0.833 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 30 | 0.637 vs 0.800 | 19/30 | 0.2005 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.637 vs 0.749 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.637 vs 0.674 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | CausVid | 30 | 0.637 vs 0.568 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.637 vs 0.833 | 15/30 | 1.0000 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.800 vs 0.749 | 14/30 | 0.8555 | no |
| Causal-Forcing (framewise) | Self-Forcing | 30 | 0.800 vs 0.674 | 10/30 | 0.0987 | no |
| Causal-Forcing (framewise) | CausVid | 30 | 0.800 vs 0.568 | 11/30 | 0.2005 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (1-step, native) | 30 | 0.800 vs 0.833 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.749 vs 0.674 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 30 | 0.749 vs 0.568 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 0.749 vs 0.833 | 15/30 | 1.0000 | no |
| Self-Forcing | CausVid | 30 | 0.674 vs 0.568 | 12/30 | 0.3616 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.674 vs 0.833 | 15/30 | 1.0000 | no |
| CausVid | Causal-Forcing++ (1-step, native) | 30 | 0.568 vs 0.833 | 18/30 | 0.3616 | no |

## DAR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.148 vs 0.279 | 26/30 | 0.0001 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 30 | 0.148 vs 0.354 | 25/30 | 0.0003 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.148 vs 0.110 | 9/30 | 0.0428 | **yes** |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.148 vs 0.104 | 9/30 | 0.0428 | **yes** |
| Causal-Forcing++ (2-step) | CausVid | 30 | 0.148 vs 0.137 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.148 vs 0.113 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (framewise) | 30 | 0.279 vs 0.354 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.279 vs 0.110 | 5/30 | 0.0003 | **yes** |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.279 vs 0.104 | 6/30 | 0.0014 | **yes** |
| Causal-Forcing++ (1-step) | CausVid | 30 | 0.279 vs 0.137 | 7/30 | 0.0052 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.279 vs 0.113 | 6/30 | 0.0014 | **yes** |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.354 vs 0.110 | 5/30 | 0.0003 | **yes** |
| Causal-Forcing (framewise) | Self-Forcing | 30 | 0.354 vs 0.104 | 5/30 | 0.0003 | **yes** |
| Causal-Forcing (framewise) | CausVid | 30 | 0.354 vs 0.137 | 7/30 | 0.0052 | **yes** |
| Causal-Forcing (framewise) | Causal-Forcing++ (1-step, native) | 30 | 0.354 vs 0.113 | 6/30 | 0.0014 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.110 vs 0.104 | 11/30 | 0.2005 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 30 | 0.110 vs 0.137 | 20/30 | 0.0987 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 0.110 vs 0.113 | 17/30 | 0.5847 | no |
| Self-Forcing | CausVid | 30 | 0.104 vs 0.137 | 20/30 | 0.0987 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.104 vs 0.113 | 18/30 | 0.3616 | no |
| CausVid | Causal-Forcing++ (1-step, native) | 30 | 0.137 vs 0.113 | 13/30 | 0.5847 | no |

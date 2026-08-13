# Paired significance — I2V @ 60s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 29 | 8.816 vs 5.338 | 9/29 | 0.0614 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 9.177 vs 9.935 | 11/30 | 0.2005 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 9.177 vs 17.339 | 24/30 | 0.0014 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 9.177 vs 10.388 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 29 | 5.338 vs 9.276 | 14/29 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 29 | 5.338 vs 17.021 | 27/29 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 29 | 5.338 vs 9.821 | 14/29 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 9.935 vs 17.339 | 24/30 | 0.0014 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 9.935 vs 10.388 | 16/30 | 0.8555 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 17.339 vs 10.388 | 10/30 | 0.0987 | no |

## NBF (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 5.967 vs 7.051 | 22/30 | 0.0161 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 5.967 vs 6.913 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 5.967 vs 5.520 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 5.967 vs 5.247 | 10/30 | 0.0987 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 7.051 vs 6.913 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 7.051 vs 5.520 | 9/30 | 0.0428 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 7.051 vs 5.247 | 11/30 | 0.2005 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 6.913 vs 5.520 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 6.913 vs 5.247 | 13/30 | 0.5847 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 5.520 vs 5.247 | 12/30 | 0.3616 | no |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.858 vs 0.771 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.858 vs 0.976 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.858 vs 0.879 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.858 vs 0.970 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.771 vs 0.976 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.771 vs 0.879 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.771 vs 0.970 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.976 vs 0.879 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 28 | 0.976 vs 0.970 | 14/28 | 1.0000 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.879 vs 0.970 | 14/30 | 0.8555 | no |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.665 vs 0.651 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.665 vs 0.814 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.665 vs 0.735 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.665 vs 0.525 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.651 vs 0.814 | 19/30 | 0.2005 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.651 vs 0.735 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.651 vs 0.525 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.814 vs 0.735 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 0.814 vs 0.525 | 12/30 | 0.3616 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.735 vs 0.525 | 15/30 | 1.0000 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.740 vs 0.769 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.740 vs 0.894 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.740 vs 0.772 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.740 vs 0.605 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.769 vs 0.894 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.769 vs 0.772 | 16/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.769 vs 0.605 | 18/30 | 0.3616 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.894 vs 0.772 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 0.894 vs 0.605 | 14/30 | 0.8555 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.772 vs 0.605 | 15/30 | 1.0000 | no |

## DLR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.668 vs 0.637 | 12/30 | 0.3616 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.668 vs 0.749 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.668 vs 0.674 | 18/30 | 0.3616 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.668 vs 0.833 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.637 vs 0.749 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.637 vs 0.674 | 13/30 | 0.5847 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.637 vs 0.833 | 15/30 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.749 vs 0.674 | 17/30 | 0.5847 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 0.749 vs 0.833 | 15/30 | 1.0000 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.674 vs 0.833 | 15/30 | 1.0000 | no |

## DAR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 30 | 0.148 vs 0.158 | 18/30 | 0.3616 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.148 vs 0.110 | 9/30 | 0.0428 | **yes** |
| Causal-Forcing++ (2-step) | Self-Forcing | 30 | 0.148 vs 0.104 | 9/30 | 0.0428 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 30 | 0.148 vs 0.113 | 14/30 | 0.8555 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 30 | 0.158 vs 0.110 | 7/30 | 0.0052 | **yes** |
| Causal-Forcing++ (1-step) | Self-Forcing | 30 | 0.158 vs 0.104 | 11/30 | 0.2005 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 30 | 0.158 vs 0.113 | 11/30 | 0.2005 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 30 | 0.110 vs 0.104 | 11/30 | 0.2005 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 30 | 0.110 vs 0.113 | 17/30 | 0.5847 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 30 | 0.104 vs 0.113 | 18/30 | 0.3616 | no |

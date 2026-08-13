# Paired significance — I2V @ 120s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 9.654 vs 7.260 | 6/20 | 0.1153 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 9.654 vs 11.369 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 9.654 vs 22.997 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 20 | 9.654 vs 13.598 | 17/20 | 0.0026 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 7.260 vs 11.369 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 7.260 vs 22.997 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 20 | 7.260 vs 13.598 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 20 | 11.369 vs 22.997 | 16/20 | 0.0118 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 20 | 11.369 vs 13.598 | 13/20 | 0.2632 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 20 | 22.997 vs 13.598 | 5/20 | 0.0414 | **yes** |

## BFR/NBF (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 1.102 vs 1.174 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 1.102 vs 2.159 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 1.102 vs 1.293 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 20 | 1.102 vs 0.923 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 1.174 vs 2.159 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 1.174 vs 1.293 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 20 | 1.174 vs 0.923 | 8/20 | 0.5034 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 20 | 2.159 vs 1.293 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 20 | 2.159 vs 0.923 | 8/20 | 0.5034 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 20 | 1.293 vs 0.923 | 9/20 | 0.8238 | no |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 0.909 vs 0.835 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 0.909 vs 0.962 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 0.909 vs 0.436 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 20 | 0.909 vs 0.685 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 0.835 vs 0.962 | 8/20 | 0.5034 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.835 vs 0.436 | 17/20 | 0.0026 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 20 | 0.835 vs 0.685 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 20 | 0.962 vs 0.436 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 20 | 0.962 vs 0.685 | 14/20 | 0.1153 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 20 | 0.436 vs 0.685 | 6/20 | 0.1153 | no |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 0.932 vs 0.833 | 8/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 0.932 vs 1.542 | 8/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 0.932 vs 0.777 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 20 | 0.932 vs 0.426 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 0.833 vs 1.542 | 8/20 | 0.5034 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.833 vs 0.777 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 20 | 0.833 vs 0.426 | 16/20 | 0.0118 | **yes** |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 20 | 1.542 vs 0.777 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 20 | 1.542 vs 0.426 | 13/20 | 0.2632 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 20 | 0.777 vs 0.426 | 14/20 | 0.1153 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 1.035 vs 0.972 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 1.035 vs 1.518 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 1.035 vs 0.935 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 20 | 1.035 vs 0.523 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 0.972 vs 1.518 | 7/20 | 0.2632 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.972 vs 0.935 | 11/20 | 0.8238 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 20 | 0.972 vs 0.523 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 20 | 1.518 vs 0.935 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 20 | 1.518 vs 0.523 | 12/20 | 0.5034 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 20 | 0.935 vs 0.523 | 15/20 | 0.0414 | **yes** |

## DriftFrac (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 0.575 vs 0.622 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 0.575 vs 0.747 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 0.575 vs 0.661 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, native) | 20 | 0.575 vs 0.767 | 15/20 | 0.0414 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, native nfpb=1) | 20 | 0.622 vs 0.747 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.622 vs 0.661 | 11/20 | 0.8238 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, native) | 20 | 0.622 vs 0.767 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 20 | 0.747 vs 0.661 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Causal-Forcing++ (1-step, native) | 20 | 0.747 vs 0.767 | 10/20 | 1.0000 | no |
| Self-Forcing | Causal-Forcing++ (1-step, native) | 20 | 0.661 vs 0.767 | 14/20 | 0.1153 | no |

# Paired significance — T2V @ 60s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 8.076 vs 11.370 | 19/23 | 0.0026 | **yes** |
| CausVid | Infinite-Forcing | 23 | 8.076 vs 7.748 | 14/23 | 0.4049 | no |
| CausVid | Rolling-Forcing | 23 | 8.076 vs 16.769 | 16/23 | 0.0931 | no |
| CausVid | Reward-Forcing | 23 | 8.076 vs 14.847 | 16/23 | 0.0931 | no |
| CausVid | LongLive | 23 | 8.076 vs 15.939 | 18/23 | 0.0106 | **yes** |
| CausVid | Causal-Forcing | 23 | 8.076 vs 22.437 | 22/23 | 0.0000 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 11.370 vs 7.748 | 5/23 | 0.0106 | **yes** |
| Self-Forcing | Rolling-Forcing | 23 | 11.370 vs 16.769 | 17/23 | 0.0347 | **yes** |
| Self-Forcing | Reward-Forcing | 23 | 11.370 vs 14.847 | 11/23 | 1.0000 | no |
| Self-Forcing | LongLive | 23 | 11.370 vs 15.939 | 13/23 | 0.6776 | no |
| Self-Forcing | Causal-Forcing | 23 | 11.370 vs 22.437 | 20/23 | 0.0005 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 7.748 vs 16.769 | 18/23 | 0.0106 | **yes** |
| Infinite-Forcing | Reward-Forcing | 23 | 7.748 vs 14.847 | 15/23 | 0.2100 | no |
| Infinite-Forcing | LongLive | 23 | 7.748 vs 15.939 | 18/23 | 0.0106 | **yes** |
| Infinite-Forcing | Causal-Forcing | 23 | 7.748 vs 22.437 | 20/23 | 0.0005 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 16.769 vs 14.847 | 10/23 | 0.6776 | no |
| Rolling-Forcing | LongLive | 23 | 16.769 vs 15.939 | 12/23 | 1.0000 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 16.769 vs 22.437 | 17/23 | 0.0347 | **yes** |
| Reward-Forcing | LongLive | 23 | 14.847 vs 15.939 | 14/23 | 0.4049 | no |
| Reward-Forcing | Causal-Forcing | 23 | 14.847 vs 22.437 | 17/23 | 0.0347 | **yes** |
| LongLive | Causal-Forcing | 23 | 15.939 vs 22.437 | 18/23 | 0.0106 | **yes** |

## NBF (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 9.272 vs 12.724 | 16/23 | 0.0931 | no |
| CausVid | Infinite-Forcing | 23 | 9.272 vs 3.649 | 11/23 | 1.0000 | no |
| CausVid | Rolling-Forcing | 23 | 9.272 vs 11.231 | 15/23 | 0.2100 | no |
| CausVid | Reward-Forcing | 23 | 9.272 vs 8.510 | 12/23 | 1.0000 | no |
| CausVid | LongLive | 23 | 9.272 vs 13.865 | 17/23 | 0.0347 | **yes** |
| CausVid | Causal-Forcing | 23 | 9.272 vs 87.624 | 23/23 | 0.0000 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 12.724 vs 3.649 | 0/23 | 0.0000 | **yes** |
| Self-Forcing | Rolling-Forcing | 23 | 12.724 vs 11.231 | 10/23 | 0.6776 | no |
| Self-Forcing | Reward-Forcing | 23 | 12.724 vs 8.510 | 6/23 | 0.0347 | **yes** |
| Self-Forcing | LongLive | 23 | 12.724 vs 13.865 | 12/23 | 1.0000 | no |
| Self-Forcing | Causal-Forcing | 23 | 12.724 vs 87.624 | 23/23 | 0.0000 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 3.649 vs 11.231 | 21/23 | 0.0001 | **yes** |
| Infinite-Forcing | Reward-Forcing | 23 | 3.649 vs 8.510 | 20/23 | 0.0005 | **yes** |
| Infinite-Forcing | LongLive | 23 | 3.649 vs 13.865 | 22/23 | 0.0000 | **yes** |
| Infinite-Forcing | Causal-Forcing | 23 | 3.649 vs 87.624 | 23/23 | 0.0000 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 11.231 vs 8.510 | 9/23 | 0.4049 | no |
| Rolling-Forcing | LongLive | 23 | 11.231 vs 13.865 | 12/23 | 1.0000 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 11.231 vs 87.624 | 22/23 | 0.0000 | **yes** |
| Reward-Forcing | LongLive | 23 | 8.510 vs 13.865 | 19/23 | 0.0026 | **yes** |
| Reward-Forcing | Causal-Forcing | 23 | 8.510 vs 87.624 | 22/23 | 0.0000 | **yes** |
| LongLive | Causal-Forcing | 23 | 13.865 vs 87.624 | 22/23 | 0.0000 | **yes** |

## MCFF-E (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 2.873 vs 10.359 | 6/23 | 0.0347 | **yes** |
| CausVid | Infinite-Forcing | 23 | 2.873 vs 1.174 | 16/23 | 0.0931 | no |
| CausVid | Rolling-Forcing | 23 | 2.873 vs 3.180 | 9/23 | 0.4049 | no |
| CausVid | Reward-Forcing | 23 | 2.873 vs 3.806 | 8/23 | 0.2100 | no |
| CausVid | LongLive | 23 | 2.873 vs 6.462 | 8/23 | 0.2100 | no |
| CausVid | Causal-Forcing | 23 | 2.873 vs 9.838 | 1/23 | 0.0000 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 10.359 vs 1.174 | 23/23 | 0.0000 | **yes** |
| Self-Forcing | Rolling-Forcing | 23 | 10.359 vs 3.180 | 20/23 | 0.0005 | **yes** |
| Self-Forcing | Reward-Forcing | 23 | 10.359 vs 3.806 | 19/23 | 0.0026 | **yes** |
| Self-Forcing | LongLive | 23 | 10.359 vs 6.462 | 16/23 | 0.0931 | no |
| Self-Forcing | Causal-Forcing | 23 | 10.359 vs 9.838 | 10/23 | 0.6776 | no |
| Infinite-Forcing | Rolling-Forcing | 23 | 1.174 vs 3.180 | 3/23 | 0.0005 | **yes** |
| Infinite-Forcing | Reward-Forcing | 23 | 1.174 vs 3.806 | 4/23 | 0.0026 | **yes** |
| Infinite-Forcing | LongLive | 23 | 1.174 vs 6.462 | 3/23 | 0.0005 | **yes** |
| Infinite-Forcing | Causal-Forcing | 23 | 1.174 vs 9.838 | 0/23 | 0.0000 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 3.180 vs 3.806 | 12/23 | 1.0000 | no |
| Rolling-Forcing | LongLive | 23 | 3.180 vs 6.462 | 9/23 | 0.4049 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 3.180 vs 9.838 | 6/23 | 0.0347 | **yes** |
| Reward-Forcing | LongLive | 23 | 3.806 vs 6.462 | 10/23 | 0.6776 | no |
| Reward-Forcing | Causal-Forcing | 23 | 3.806 vs 9.838 | 2/23 | 0.0001 | **yes** |
| LongLive | Causal-Forcing | 23 | 6.462 vs 9.838 | 5/23 | 0.0106 | **yes** |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 1.960 vs 2.538 | 9/23 | 0.4049 | no |
| CausVid | Infinite-Forcing | 23 | 1.960 vs 0.285 | 15/23 | 0.2100 | no |
| CausVid | Rolling-Forcing | 23 | 1.960 vs 1.574 | 7/23 | 0.0931 | no |
| CausVid | Reward-Forcing | 23 | 1.960 vs 0.796 | 9/23 | 0.4049 | no |
| CausVid | LongLive | 23 | 1.960 vs 2.407 | 8/23 | 0.2100 | no |
| CausVid | Causal-Forcing | 23 | 1.960 vs 7.213 | 4/23 | 0.0026 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 2.538 vs 0.285 | 19/23 | 0.0026 | **yes** |
| Self-Forcing | Rolling-Forcing | 23 | 2.538 vs 1.574 | 12/23 | 1.0000 | no |
| Self-Forcing | Reward-Forcing | 23 | 2.538 vs 0.796 | 15/23 | 0.2100 | no |
| Self-Forcing | LongLive | 23 | 2.538 vs 2.407 | 12/23 | 1.0000 | no |
| Self-Forcing | Causal-Forcing | 23 | 2.538 vs 7.213 | 6/23 | 0.0347 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.285 vs 1.574 | 1/23 | 0.0000 | **yes** |
| Infinite-Forcing | Reward-Forcing | 23 | 0.285 vs 0.796 | 4/23 | 0.0026 | **yes** |
| Infinite-Forcing | LongLive | 23 | 0.285 vs 2.407 | 2/23 | 0.0001 | **yes** |
| Infinite-Forcing | Causal-Forcing | 23 | 0.285 vs 7.213 | 0/23 | 0.0000 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 1.574 vs 0.796 | 13/23 | 0.6776 | no |
| Rolling-Forcing | LongLive | 23 | 1.574 vs 2.407 | 13/23 | 0.6776 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 1.574 vs 7.213 | 3/23 | 0.0005 | **yes** |
| Reward-Forcing | LongLive | 23 | 0.796 vs 2.407 | 6/23 | 0.0347 | **yes** |
| Reward-Forcing | Causal-Forcing | 23 | 0.796 vs 7.213 | 4/23 | 0.0026 | **yes** |
| LongLive | Causal-Forcing | 23 | 2.407 vs 7.213 | 6/23 | 0.0347 | **yes** |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 0.672 vs 0.443 | 14/23 | 0.4049 | no |
| CausVid | Infinite-Forcing | 23 | 0.672 vs 0.634 | 13/23 | 0.6776 | no |
| CausVid | Rolling-Forcing | 23 | 0.672 vs 0.749 | 15/23 | 0.2100 | no |
| CausVid | Reward-Forcing | 23 | 0.672 vs 0.491 | 15/23 | 0.2100 | no |
| CausVid | LongLive | 23 | 0.672 vs 0.754 | 12/23 | 1.0000 | no |
| CausVid | Causal-Forcing | 23 | 0.672 vs 0.834 | 12/23 | 1.0000 | no |
| Self-Forcing | Infinite-Forcing | 22 | 0.443 vs 0.634 | 8/22 | 0.2863 | no |
| Self-Forcing | Rolling-Forcing | 23 | 0.443 vs 0.749 | 8/23 | 0.2100 | no |
| Self-Forcing | Reward-Forcing | 23 | 0.443 vs 0.491 | 10/23 | 0.6776 | no |
| Self-Forcing | LongLive | 22 | 0.443 vs 0.754 | 7/22 | 0.1338 | no |
| Self-Forcing | Causal-Forcing | 23 | 0.443 vs 0.834 | 8/23 | 0.2100 | no |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.634 vs 0.749 | 10/23 | 0.6776 | no |
| Infinite-Forcing | Reward-Forcing | 23 | 0.634 vs 0.491 | 13/23 | 0.6776 | no |
| Infinite-Forcing | LongLive | 22 | 0.634 vs 0.754 | 8/22 | 0.2863 | no |
| Infinite-Forcing | Causal-Forcing | 22 | 0.634 vs 0.834 | 11/22 | 1.0000 | no |
| Rolling-Forcing | Reward-Forcing | 23 | 0.749 vs 0.491 | 13/23 | 0.6776 | no |
| Rolling-Forcing | LongLive | 22 | 0.749 vs 0.754 | 13/22 | 0.5235 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 0.749 vs 0.834 | 10/23 | 0.6776 | no |
| Reward-Forcing | LongLive | 23 | 0.491 vs 0.754 | 9/23 | 0.4049 | no |
| Reward-Forcing | Causal-Forcing | 23 | 0.491 vs 0.834 | 9/23 | 0.4049 | no |
| LongLive | Causal-Forcing | 23 | 0.754 vs 0.834 | 12/23 | 1.0000 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 2.285 vs 2.564 | 8/23 | 0.2100 | no |
| CausVid | Infinite-Forcing | 23 | 2.285 vs 0.304 | 16/23 | 0.0931 | no |
| CausVid | Rolling-Forcing | 23 | 2.285 vs 1.754 | 6/23 | 0.0347 | **yes** |
| CausVid | Reward-Forcing | 23 | 2.285 vs 0.913 | 10/23 | 0.6776 | no |
| CausVid | LongLive | 23 | 2.285 vs 2.501 | 7/23 | 0.0931 | no |
| CausVid | Causal-Forcing | 23 | 2.285 vs 10.757 | 4/23 | 0.0026 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 2.564 vs 0.304 | 22/23 | 0.0000 | **yes** |
| Self-Forcing | Rolling-Forcing | 23 | 2.564 vs 1.754 | 11/23 | 1.0000 | no |
| Self-Forcing | Reward-Forcing | 23 | 2.564 vs 0.913 | 15/23 | 0.2100 | no |
| Self-Forcing | LongLive | 23 | 2.564 vs 2.501 | 11/23 | 1.0000 | no |
| Self-Forcing | Causal-Forcing | 23 | 2.564 vs 10.757 | 5/23 | 0.0106 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.304 vs 1.754 | 1/23 | 0.0000 | **yes** |
| Infinite-Forcing | Reward-Forcing | 23 | 0.304 vs 0.913 | 4/23 | 0.0026 | **yes** |
| Infinite-Forcing | LongLive | 23 | 0.304 vs 2.501 | 1/23 | 0.0000 | **yes** |
| Infinite-Forcing | Causal-Forcing | 23 | 0.304 vs 10.757 | 0/23 | 0.0000 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 1.754 vs 0.913 | 13/23 | 0.6776 | no |
| Rolling-Forcing | LongLive | 23 | 1.754 vs 2.501 | 13/23 | 0.6776 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 1.754 vs 10.757 | 2/23 | 0.0001 | **yes** |
| Reward-Forcing | LongLive | 23 | 0.913 vs 2.501 | 6/23 | 0.0347 | **yes** |
| Reward-Forcing | Causal-Forcing | 23 | 0.913 vs 10.757 | 2/23 | 0.0001 | **yes** |
| LongLive | Causal-Forcing | 23 | 2.501 vs 10.757 | 5/23 | 0.0106 | **yes** |

## DLR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 0.454 vs 0.504 | 11/23 | 1.0000 | no |
| CausVid | Infinite-Forcing | 23 | 0.454 vs 0.551 | 14/23 | 0.4049 | no |
| CausVid | Rolling-Forcing | 23 | 0.454 vs 0.540 | 14/23 | 0.4049 | no |
| CausVid | Reward-Forcing | 23 | 0.454 vs 0.599 | 18/23 | 0.0106 | **yes** |
| CausVid | LongLive | 23 | 0.454 vs 0.590 | 17/23 | 0.0347 | **yes** |
| CausVid | Causal-Forcing | 23 | 0.454 vs 0.940 | 20/23 | 0.0005 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 0.504 vs 0.551 | 15/23 | 0.2100 | no |
| Self-Forcing | Rolling-Forcing | 23 | 0.504 vs 0.540 | 16/23 | 0.0931 | no |
| Self-Forcing | Reward-Forcing | 23 | 0.504 vs 0.599 | 17/23 | 0.0347 | **yes** |
| Self-Forcing | LongLive | 23 | 0.504 vs 0.590 | 15/23 | 0.2100 | no |
| Self-Forcing | Causal-Forcing | 23 | 0.504 vs 0.940 | 18/23 | 0.0106 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.551 vs 0.540 | 13/23 | 0.6776 | no |
| Infinite-Forcing | Reward-Forcing | 23 | 0.551 vs 0.599 | 11/23 | 1.0000 | no |
| Infinite-Forcing | LongLive | 23 | 0.551 vs 0.590 | 11/23 | 1.0000 | no |
| Infinite-Forcing | Causal-Forcing | 23 | 0.551 vs 0.940 | 18/23 | 0.0106 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 0.540 vs 0.599 | 12/23 | 1.0000 | no |
| Rolling-Forcing | LongLive | 23 | 0.540 vs 0.590 | 11/23 | 1.0000 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 0.540 vs 0.940 | 18/23 | 0.0106 | **yes** |
| Reward-Forcing | LongLive | 23 | 0.599 vs 0.590 | 9/23 | 0.4049 | no |
| Reward-Forcing | Causal-Forcing | 23 | 0.599 vs 0.940 | 16/23 | 0.0931 | no |
| LongLive | Causal-Forcing | 23 | 0.590 vs 0.940 | 18/23 | 0.0106 | **yes** |

## DAR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 0.142 vs 0.081 | 9/23 | 0.4049 | no |
| CausVid | Infinite-Forcing | 23 | 0.142 vs 0.123 | 14/23 | 0.4049 | no |
| CausVid | Rolling-Forcing | 23 | 0.142 vs 0.180 | 11/23 | 1.0000 | no |
| CausVid | Reward-Forcing | 23 | 0.142 vs 0.156 | 14/23 | 0.4049 | no |
| CausVid | LongLive | 23 | 0.142 vs 0.169 | 13/23 | 0.6776 | no |
| CausVid | Causal-Forcing | 23 | 0.142 vs 0.396 | 16/23 | 0.0931 | no |
| Self-Forcing | Infinite-Forcing | 23 | 0.081 vs 0.123 | 14/23 | 0.4049 | no |
| Self-Forcing | Rolling-Forcing | 23 | 0.081 vs 0.180 | 16/23 | 0.0931 | no |
| Self-Forcing | Reward-Forcing | 23 | 0.081 vs 0.156 | 15/23 | 0.2100 | no |
| Self-Forcing | LongLive | 23 | 0.081 vs 0.169 | 15/23 | 0.2100 | no |
| Self-Forcing | Causal-Forcing | 23 | 0.081 vs 0.396 | 15/23 | 0.2100 | no |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.123 vs 0.180 | 13/23 | 0.6776 | no |
| Infinite-Forcing | Reward-Forcing | 23 | 0.123 vs 0.156 | 14/23 | 0.4049 | no |
| Infinite-Forcing | LongLive | 23 | 0.123 vs 0.169 | 12/23 | 1.0000 | no |
| Infinite-Forcing | Causal-Forcing | 23 | 0.123 vs 0.396 | 17/23 | 0.0347 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 0.180 vs 0.156 | 8/23 | 0.2100 | no |
| Rolling-Forcing | LongLive | 23 | 0.180 vs 0.169 | 9/23 | 0.4049 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 0.180 vs 0.396 | 15/23 | 0.2100 | no |
| Reward-Forcing | LongLive | 23 | 0.156 vs 0.169 | 10/23 | 0.6776 | no |
| Reward-Forcing | Causal-Forcing | 23 | 0.156 vs 0.396 | 16/23 | 0.0931 | no |
| LongLive | Causal-Forcing | 23 | 0.169 vs 0.396 | 17/23 | 0.0347 | **yes** |

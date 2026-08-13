# Paired significance — T2V @ 60s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 8.136 vs 11.516 | 18/23 | 0.0106 | **yes** |
| CausVid | Infinite-Forcing | 23 | 8.136 vs 7.720 | 14/23 | 0.4049 | no |
| CausVid | Rolling-Forcing | 23 | 8.136 vs 16.907 | 16/23 | 0.0931 | no |
| CausVid | Reward-Forcing | 23 | 8.136 vs 14.974 | 16/23 | 0.0931 | no |
| CausVid | LongLive | 23 | 8.136 vs 15.723 | 19/23 | 0.0026 | **yes** |
| CausVid | Causal-Forcing | 23 | 8.136 vs 22.805 | 22/23 | 0.0000 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 11.516 vs 7.720 | 5/23 | 0.0106 | **yes** |
| Self-Forcing | Rolling-Forcing | 23 | 11.516 vs 16.907 | 16/23 | 0.0931 | no |
| Self-Forcing | Reward-Forcing | 23 | 11.516 vs 14.974 | 11/23 | 1.0000 | no |
| Self-Forcing | LongLive | 23 | 11.516 vs 15.723 | 13/23 | 0.6776 | no |
| Self-Forcing | Causal-Forcing | 23 | 11.516 vs 22.805 | 20/23 | 0.0005 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 7.720 vs 16.907 | 18/23 | 0.0106 | **yes** |
| Infinite-Forcing | Reward-Forcing | 23 | 7.720 vs 14.974 | 15/23 | 0.2100 | no |
| Infinite-Forcing | LongLive | 23 | 7.720 vs 15.723 | 19/23 | 0.0026 | **yes** |
| Infinite-Forcing | Causal-Forcing | 23 | 7.720 vs 22.805 | 21/23 | 0.0001 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 16.907 vs 14.974 | 11/23 | 1.0000 | no |
| Rolling-Forcing | LongLive | 23 | 16.907 vs 15.723 | 12/23 | 1.0000 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 16.907 vs 22.805 | 16/23 | 0.0931 | no |
| Reward-Forcing | LongLive | 23 | 14.974 vs 15.723 | 13/23 | 0.6776 | no |
| Reward-Forcing | Causal-Forcing | 23 | 14.974 vs 22.805 | 17/23 | 0.0347 | **yes** |
| LongLive | Causal-Forcing | 23 | 15.723 vs 22.805 | 20/23 | 0.0005 | **yes** |

## BFR/NBF (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 1.161 vs 1.587 | 16/23 | 0.0931 | no |
| CausVid | Infinite-Forcing | 23 | 1.161 vs 0.456 | 11/23 | 1.0000 | no |
| CausVid | Rolling-Forcing | 23 | 1.161 vs 1.405 | 15/23 | 0.2100 | no |
| CausVid | Reward-Forcing | 23 | 1.161 vs 1.066 | 12/23 | 1.0000 | no |
| CausVid | LongLive | 23 | 1.161 vs 1.734 | 17/23 | 0.0347 | **yes** |
| CausVid | Causal-Forcing | 23 | 1.161 vs 10.955 | 23/23 | 0.0000 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 1.587 vs 0.456 | 0/23 | 0.0000 | **yes** |
| Self-Forcing | Rolling-Forcing | 23 | 1.587 vs 1.405 | 10/23 | 0.6776 | no |
| Self-Forcing | Reward-Forcing | 23 | 1.587 vs 1.066 | 6/23 | 0.0347 | **yes** |
| Self-Forcing | LongLive | 23 | 1.587 vs 1.734 | 12/23 | 1.0000 | no |
| Self-Forcing | Causal-Forcing | 23 | 1.587 vs 10.955 | 23/23 | 0.0000 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.456 vs 1.405 | 21/23 | 0.0001 | **yes** |
| Infinite-Forcing | Reward-Forcing | 23 | 0.456 vs 1.066 | 20/23 | 0.0005 | **yes** |
| Infinite-Forcing | LongLive | 23 | 0.456 vs 1.734 | 22/23 | 0.0000 | **yes** |
| Infinite-Forcing | Causal-Forcing | 23 | 0.456 vs 10.955 | 23/23 | 0.0000 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 1.405 vs 1.066 | 9/23 | 0.4049 | no |
| Rolling-Forcing | LongLive | 23 | 1.405 vs 1.734 | 12/23 | 1.0000 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 1.405 vs 10.955 | 22/23 | 0.0000 | **yes** |
| Reward-Forcing | LongLive | 23 | 1.066 vs 1.734 | 19/23 | 0.0026 | **yes** |
| Reward-Forcing | Causal-Forcing | 23 | 1.066 vs 10.955 | 22/23 | 0.0000 | **yes** |
| LongLive | Causal-Forcing | 23 | 1.734 vs 10.955 | 22/23 | 0.0000 | **yes** |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 22 | 0.670 vs 0.439 | 13/22 | 0.5235 | no |
| CausVid | Infinite-Forcing | 22 | 0.670 vs 0.624 | 15/22 | 0.1338 | no |
| CausVid | Rolling-Forcing | 23 | 0.670 vs 0.740 | 15/23 | 0.2100 | no |
| CausVid | Reward-Forcing | 23 | 0.670 vs 0.502 | 17/23 | 0.0347 | **yes** |
| CausVid | LongLive | 22 | 0.670 vs 0.766 | 12/22 | 0.8318 | no |
| CausVid | Causal-Forcing | 23 | 0.670 vs 0.782 | 11/23 | 1.0000 | no |
| Self-Forcing | Infinite-Forcing | 22 | 0.439 vs 0.624 | 8/22 | 0.2863 | no |
| Self-Forcing | Rolling-Forcing | 23 | 0.439 vs 0.740 | 9/23 | 0.4049 | no |
| Self-Forcing | Reward-Forcing | 23 | 0.439 vs 0.502 | 9/23 | 0.4049 | no |
| Self-Forcing | LongLive | 22 | 0.439 vs 0.766 | 7/22 | 0.1338 | no |
| Self-Forcing | Causal-Forcing | 23 | 0.439 vs 0.782 | 9/23 | 0.4049 | no |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.624 vs 0.740 | 10/23 | 0.6776 | no |
| Infinite-Forcing | Reward-Forcing | 23 | 0.624 vs 0.502 | 10/23 | 0.6776 | no |
| Infinite-Forcing | LongLive | 22 | 0.624 vs 0.766 | 8/22 | 0.2863 | no |
| Infinite-Forcing | Causal-Forcing | 22 | 0.624 vs 0.782 | 10/22 | 0.8318 | no |
| Rolling-Forcing | Reward-Forcing | 23 | 0.740 vs 0.502 | 12/23 | 1.0000 | no |
| Rolling-Forcing | LongLive | 22 | 0.740 vs 0.766 | 13/22 | 0.5235 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 0.740 vs 0.782 | 10/23 | 0.6776 | no |
| Reward-Forcing | LongLive | 23 | 0.502 vs 0.766 | 10/23 | 0.6776 | no |
| Reward-Forcing | Causal-Forcing | 23 | 0.502 vs 0.782 | 9/23 | 0.4049 | no |
| LongLive | Causal-Forcing | 23 | 0.766 vs 0.782 | 12/23 | 1.0000 | no |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 2.279 vs 2.524 | 9/23 | 0.4049 | no |
| CausVid | Infinite-Forcing | 23 | 2.279 vs 0.286 | 17/23 | 0.0347 | **yes** |
| CausVid | Rolling-Forcing | 23 | 2.279 vs 1.538 | 7/23 | 0.0931 | no |
| CausVid | Reward-Forcing | 23 | 2.279 vs 0.875 | 10/23 | 0.6776 | no |
| CausVid | LongLive | 23 | 2.279 vs 2.440 | 8/23 | 0.2100 | no |
| CausVid | Causal-Forcing | 23 | 2.279 vs 6.893 | 4/23 | 0.0026 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 2.524 vs 0.286 | 21/23 | 0.0001 | **yes** |
| Self-Forcing | Rolling-Forcing | 23 | 2.524 vs 1.538 | 10/23 | 0.6776 | no |
| Self-Forcing | Reward-Forcing | 23 | 2.524 vs 0.875 | 14/23 | 0.4049 | no |
| Self-Forcing | LongLive | 23 | 2.524 vs 2.440 | 10/23 | 0.6776 | no |
| Self-Forcing | Causal-Forcing | 23 | 2.524 vs 6.893 | 6/23 | 0.0347 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.286 vs 1.538 | 1/23 | 0.0000 | **yes** |
| Infinite-Forcing | Reward-Forcing | 23 | 0.286 vs 0.875 | 4/23 | 0.0026 | **yes** |
| Infinite-Forcing | LongLive | 23 | 0.286 vs 2.440 | 2/23 | 0.0001 | **yes** |
| Infinite-Forcing | Causal-Forcing | 23 | 0.286 vs 6.893 | 0/23 | 0.0000 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 1.538 vs 0.875 | 13/23 | 0.6776 | no |
| Rolling-Forcing | LongLive | 23 | 1.538 vs 2.440 | 13/23 | 0.6776 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 1.538 vs 6.893 | 4/23 | 0.0026 | **yes** |
| Reward-Forcing | LongLive | 23 | 0.875 vs 2.440 | 6/23 | 0.0347 | **yes** |
| Reward-Forcing | Causal-Forcing | 23 | 0.875 vs 6.893 | 5/23 | 0.0106 | **yes** |
| LongLive | Causal-Forcing | 23 | 2.440 vs 6.893 | 7/23 | 0.0931 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 2.285 vs 2.560 | 8/23 | 0.2100 | no |
| CausVid | Infinite-Forcing | 23 | 2.285 vs 0.304 | 16/23 | 0.0931 | no |
| CausVid | Rolling-Forcing | 23 | 2.285 vs 1.752 | 6/23 | 0.0347 | **yes** |
| CausVid | Reward-Forcing | 23 | 2.285 vs 0.913 | 10/23 | 0.6776 | no |
| CausVid | LongLive | 23 | 2.285 vs 2.500 | 7/23 | 0.0931 | no |
| CausVid | Causal-Forcing | 23 | 2.285 vs 10.753 | 4/23 | 0.0026 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 2.560 vs 0.304 | 22/23 | 0.0000 | **yes** |
| Self-Forcing | Rolling-Forcing | 23 | 2.560 vs 1.752 | 11/23 | 1.0000 | no |
| Self-Forcing | Reward-Forcing | 23 | 2.560 vs 0.913 | 15/23 | 0.2100 | no |
| Self-Forcing | LongLive | 23 | 2.560 vs 2.500 | 11/23 | 1.0000 | no |
| Self-Forcing | Causal-Forcing | 23 | 2.560 vs 10.753 | 5/23 | 0.0106 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.304 vs 1.752 | 1/23 | 0.0000 | **yes** |
| Infinite-Forcing | Reward-Forcing | 23 | 0.304 vs 0.913 | 4/23 | 0.0026 | **yes** |
| Infinite-Forcing | LongLive | 23 | 0.304 vs 2.500 | 1/23 | 0.0000 | **yes** |
| Infinite-Forcing | Causal-Forcing | 23 | 0.304 vs 10.753 | 0/23 | 0.0000 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 1.752 vs 0.913 | 13/23 | 0.6776 | no |
| Rolling-Forcing | LongLive | 23 | 1.752 vs 2.500 | 13/23 | 0.6776 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 1.752 vs 10.753 | 2/23 | 0.0001 | **yes** |
| Reward-Forcing | LongLive | 23 | 0.913 vs 2.500 | 6/23 | 0.0347 | **yes** |
| Reward-Forcing | Causal-Forcing | 23 | 0.913 vs 10.753 | 2/23 | 0.0001 | **yes** |
| LongLive | Causal-Forcing | 23 | 2.500 vs 10.753 | 5/23 | 0.0106 | **yes** |

## DriftFrac (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| CausVid | Self-Forcing | 23 | 0.454 vs 0.504 | 11/23 | 1.0000 | no |
| CausVid | Infinite-Forcing | 23 | 0.454 vs 0.550 | 14/23 | 0.4049 | no |
| CausVid | Rolling-Forcing | 23 | 0.454 vs 0.540 | 14/23 | 0.4049 | no |
| CausVid | Reward-Forcing | 23 | 0.454 vs 0.598 | 18/23 | 0.0106 | **yes** |
| CausVid | LongLive | 23 | 0.454 vs 0.589 | 17/23 | 0.0347 | **yes** |
| CausVid | Causal-Forcing | 23 | 0.454 vs 0.939 | 20/23 | 0.0005 | **yes** |
| Self-Forcing | Infinite-Forcing | 23 | 0.504 vs 0.550 | 15/23 | 0.2100 | no |
| Self-Forcing | Rolling-Forcing | 23 | 0.504 vs 0.540 | 16/23 | 0.0931 | no |
| Self-Forcing | Reward-Forcing | 23 | 0.504 vs 0.598 | 17/23 | 0.0347 | **yes** |
| Self-Forcing | LongLive | 23 | 0.504 vs 0.589 | 15/23 | 0.2100 | no |
| Self-Forcing | Causal-Forcing | 23 | 0.504 vs 0.939 | 18/23 | 0.0106 | **yes** |
| Infinite-Forcing | Rolling-Forcing | 23 | 0.550 vs 0.540 | 13/23 | 0.6776 | no |
| Infinite-Forcing | Reward-Forcing | 23 | 0.550 vs 0.598 | 11/23 | 1.0000 | no |
| Infinite-Forcing | LongLive | 23 | 0.550 vs 0.589 | 11/23 | 1.0000 | no |
| Infinite-Forcing | Causal-Forcing | 23 | 0.550 vs 0.939 | 18/23 | 0.0106 | **yes** |
| Rolling-Forcing | Reward-Forcing | 23 | 0.540 vs 0.598 | 12/23 | 1.0000 | no |
| Rolling-Forcing | LongLive | 23 | 0.540 vs 0.589 | 11/23 | 1.0000 | no |
| Rolling-Forcing | Causal-Forcing | 23 | 0.540 vs 0.939 | 18/23 | 0.0106 | **yes** |
| Reward-Forcing | LongLive | 23 | 0.598 vs 0.589 | 9/23 | 0.4049 | no |
| Reward-Forcing | Causal-Forcing | 23 | 0.598 vs 0.939 | 16/23 | 0.0931 | no |
| LongLive | Causal-Forcing | 23 | 0.589 vs 0.939 | 18/23 | 0.0106 | **yes** |

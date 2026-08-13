# Paired significance — I2V @ 240s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 5 | 10.388 vs 19.833 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 10.388 vs 6.323 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 10.388 vs 22.280 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 10.388 vs 18.397 | 3/5 | 1.0000 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 19.833 vs 6.323 | 0/5 | 0.0625 | no |
| Causal-Forcing (framewise) | Self-Forcing | 5 | 19.833 vs 22.280 | 4/5 | 0.3750 | no |
| Causal-Forcing (framewise) | CausVid | 5 | 19.833 vs 18.397 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 5 | 6.323 vs 22.280 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 5 | 6.323 vs 18.397 | 5/5 | 0.0625 | no |
| Self-Forcing | CausVid | 5 | 22.280 vs 18.397 | 1/5 | 0.3750 | no |

## NBF (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 5 | 4.826 vs 31.451 | 5/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 4.826 vs 3.946 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 4.826 vs 5.735 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 4.826 vs 2.081 | 0/5 | 0.0625 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 31.451 vs 3.946 | 0/5 | 0.0625 | no |
| Causal-Forcing (framewise) | Self-Forcing | 5 | 31.451 vs 5.735 | 0/5 | 0.0625 | no |
| Causal-Forcing (framewise) | CausVid | 5 | 31.451 vs 2.081 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 5 | 3.946 vs 5.735 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 5 | 3.946 vs 2.081 | 1/5 | 0.3750 | no |
| Self-Forcing | CausVid | 5 | 5.735 vs 2.081 | 0/5 | 0.0625 | no |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 5 | 0.631 vs 2.862 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 0.631 vs 0.688 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 0.631 vs 1.655 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 0.631 vs 0.825 | 3/5 | 1.0000 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 2.862 vs 0.688 | 4/5 | 0.3750 | no |
| Causal-Forcing (framewise) | Self-Forcing | 5 | 2.862 vs 1.655 | 4/5 | 0.3750 | no |
| Causal-Forcing (framewise) | CausVid | 5 | 2.862 vs 0.825 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 5 | 0.688 vs 1.655 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 5 | 0.688 vs 0.825 | 3/5 | 1.0000 | no |
| Self-Forcing | CausVid | 5 | 1.655 vs 0.825 | 5/5 | 0.0625 | no |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 5 | 1.028 vs 0.757 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 1.028 vs 0.665 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 1.028 vs 0.794 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 1.028 vs 0.831 | 4/5 | 0.3750 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 0.757 vs 0.665 | 4/5 | 0.3750 | no |
| Causal-Forcing (framewise) | Self-Forcing | 5 | 0.757 vs 0.794 | 3/5 | 1.0000 | no |
| Causal-Forcing (framewise) | CausVid | 5 | 0.757 vs 0.831 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 5 | 0.665 vs 0.794 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 5 | 0.665 vs 0.831 | 1/5 | 0.3750 | no |
| Self-Forcing | CausVid | 5 | 0.794 vs 0.831 | 2/5 | 1.0000 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 5 | 0.680 vs 3.457 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 0.680 vs 0.681 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 0.680 vs 1.671 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 0.680 vs 0.838 | 3/5 | 1.0000 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 3.457 vs 0.681 | 4/5 | 0.3750 | no |
| Causal-Forcing (framewise) | Self-Forcing | 5 | 3.457 vs 1.671 | 4/5 | 0.3750 | no |
| Causal-Forcing (framewise) | CausVid | 5 | 3.457 vs 0.838 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 5 | 0.681 vs 1.671 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 5 | 0.681 vs 0.838 | 3/5 | 1.0000 | no |
| Self-Forcing | CausVid | 5 | 1.671 vs 0.838 | 5/5 | 0.0625 | no |

## DLR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 5 | 0.551 vs 0.686 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 0.551 vs 0.834 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 0.551 vs 0.712 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 0.551 vs 0.435 | 1/5 | 0.3750 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 0.686 vs 0.834 | 2/5 | 1.0000 | no |
| Causal-Forcing (framewise) | Self-Forcing | 5 | 0.686 vs 0.712 | 2/5 | 1.0000 | no |
| Causal-Forcing (framewise) | CausVid | 5 | 0.686 vs 0.435 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 5 | 0.834 vs 0.712 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 5 | 0.834 vs 0.435 | 2/5 | 1.0000 | no |
| Self-Forcing | CausVid | 5 | 0.712 vs 0.435 | 1/5 | 0.3750 | no |

## DAR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing (framewise) | 5 | 0.087 vs 0.328 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 0.087 vs -0.024 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 0.087 vs 0.046 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 0.087 vs 0.073 | 3/5 | 1.0000 | no |
| Causal-Forcing (framewise) | Causal-Forcing++ (2-step, native nfpb=1) | 5 | 0.328 vs -0.024 | 0/5 | 0.0625 | no |
| Causal-Forcing (framewise) | Self-Forcing | 5 | 0.328 vs 0.046 | 1/5 | 0.3750 | no |
| Causal-Forcing (framewise) | CausVid | 5 | 0.328 vs 0.073 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | Self-Forcing | 5 | -0.024 vs 0.046 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, native nfpb=1) | CausVid | 5 | -0.024 vs 0.073 | 5/5 | 0.0625 | no |
| Self-Forcing | CausVid | 5 | 0.046 vs 0.073 | 3/5 | 1.0000 | no |

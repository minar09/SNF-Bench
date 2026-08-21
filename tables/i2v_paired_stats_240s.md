# Paired significance — I2V @ 240s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 5 | 10.388 vs 6.417 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 5 | 10.388 vs 19.833 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 10.388 vs 6.323 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 10.388 vs 22.280 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 10.388 vs 18.397 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 5 | 6.417 vs 19.833 | 5/5 | 0.0625 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 6.417 vs 6.323 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 5 | 6.417 vs 22.280 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | CausVid | 5 | 6.417 vs 18.397 | 5/5 | 0.0625 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 5 | 19.833 vs 6.323 | 0/5 | 0.0625 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 5 | 19.833 vs 22.280 | 4/5 | 0.3750 | no |
| Causal-Forcing (frame-wise) | CausVid | 5 | 19.833 vs 18.397 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 5 | 6.323 vs 22.280 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 5 | 6.323 vs 18.397 | 5/5 | 0.0625 | no |
| Self-Forcing | CausVid | 5 | 22.280 vs 18.397 | 1/5 | 0.3750 | no |

## NBF (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 5 | 4.826 vs 6.658 | 5/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 5 | 4.826 vs 31.451 | 5/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 4.826 vs 3.946 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 4.826 vs 5.735 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 4.826 vs 2.081 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 5 | 6.658 vs 31.451 | 5/5 | 0.0625 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 6.658 vs 3.946 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 5 | 6.658 vs 5.735 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | CausVid | 5 | 6.658 vs 2.081 | 0/5 | 0.0625 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 5 | 31.451 vs 3.946 | 0/5 | 0.0625 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 5 | 31.451 vs 5.735 | 0/5 | 0.0625 | no |
| Causal-Forcing (frame-wise) | CausVid | 5 | 31.451 vs 2.081 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 5 | 3.946 vs 5.735 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 5 | 3.946 vs 2.081 | 1/5 | 0.3750 | no |
| Self-Forcing | CausVid | 5 | 5.735 vs 2.081 | 0/5 | 0.0625 | no |

## MCFF-E (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 5 | 0.529 vs 0.563 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 5 | 0.529 vs 3.081 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.529 vs 1.228 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 0.529 vs 1.483 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 0.529 vs 0.807 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 5 | 0.563 vs 3.081 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.563 vs 1.228 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 5 | 0.563 vs 1.483 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (1-step) | CausVid | 5 | 0.563 vs 0.807 | 3/5 | 1.0000 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 5 | 3.081 vs 1.228 | 3/5 | 1.0000 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 5 | 3.081 vs 1.483 | 3/5 | 1.0000 | no |
| Causal-Forcing (frame-wise) | CausVid | 5 | 3.081 vs 0.807 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 5 | 1.228 vs 1.483 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 5 | 1.228 vs 0.807 | 4/5 | 0.3750 | no |
| Self-Forcing | CausVid | 5 | 1.483 vs 0.807 | 5/5 | 0.0625 | no |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 5 | 0.593 vs 0.511 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 5 | 0.593 vs 2.277 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.593 vs 0.683 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 0.593 vs 1.590 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 0.593 vs 0.790 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 5 | 0.511 vs 2.277 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.511 vs 0.683 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 5 | 0.511 vs 1.590 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | CausVid | 5 | 0.511 vs 0.790 | 2/5 | 1.0000 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 5 | 2.277 vs 0.683 | 4/5 | 0.3750 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 5 | 2.277 vs 1.590 | 4/5 | 0.3750 | no |
| Causal-Forcing (frame-wise) | CausVid | 5 | 2.277 vs 0.790 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 5 | 0.683 vs 1.590 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 5 | 0.683 vs 0.790 | 3/5 | 1.0000 | no |
| Self-Forcing | CausVid | 5 | 1.590 vs 0.790 | 5/5 | 0.0625 | no |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 5 | 1.052 vs 0.830 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 5 | 1.052 vs 0.737 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 1.052 vs 0.673 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 1.052 vs 0.809 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 1.052 vs 0.863 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 5 | 0.830 vs 0.737 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.830 vs 0.673 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 5 | 0.830 vs 0.809 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | CausVid | 5 | 0.830 vs 0.863 | 2/5 | 1.0000 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.737 vs 0.673 | 4/5 | 0.3750 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 5 | 0.737 vs 0.809 | 3/5 | 1.0000 | no |
| Causal-Forcing (frame-wise) | CausVid | 5 | 0.737 vs 0.863 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 5 | 0.673 vs 0.809 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 5 | 0.673 vs 0.863 | 1/5 | 0.3750 | no |
| Self-Forcing | CausVid | 5 | 0.809 vs 0.863 | 2/5 | 1.0000 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 5 | 0.680 vs 0.676 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 5 | 0.680 vs 3.457 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.680 vs 0.681 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 0.680 vs 1.671 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 0.680 vs 0.838 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 5 | 0.676 vs 3.457 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.676 vs 0.681 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 5 | 0.676 vs 1.671 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | CausVid | 5 | 0.676 vs 0.838 | 3/5 | 1.0000 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 5 | 3.457 vs 0.681 | 4/5 | 0.3750 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 5 | 3.457 vs 1.671 | 4/5 | 0.3750 | no |
| Causal-Forcing (frame-wise) | CausVid | 5 | 3.457 vs 0.838 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 5 | 0.681 vs 1.671 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 5 | 0.681 vs 0.838 | 3/5 | 1.0000 | no |
| Self-Forcing | CausVid | 5 | 1.671 vs 0.838 | 5/5 | 0.0625 | no |

## DLR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 5 | 0.551 vs 0.674 | 5/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 5 | 0.551 vs 0.686 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.551 vs 0.834 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 0.551 vs 0.712 | 3/5 | 1.0000 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 0.551 vs 0.435 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 5 | 0.674 vs 0.686 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.674 vs 0.834 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 5 | 0.674 vs 0.712 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | CausVid | 5 | 0.674 vs 0.435 | 0/5 | 0.0625 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.686 vs 0.834 | 2/5 | 1.0000 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 5 | 0.686 vs 0.712 | 2/5 | 1.0000 | no |
| Causal-Forcing (frame-wise) | CausVid | 5 | 0.686 vs 0.435 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 5 | 0.834 vs 0.712 | 2/5 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 5 | 0.834 vs 0.435 | 2/5 | 1.0000 | no |
| Self-Forcing | CausVid | 5 | 0.712 vs 0.435 | 1/5 | 0.3750 | no |

## DAR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 5 | 0.154 vs 0.302 | 5/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 5 | 0.154 vs 0.451 | 5/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.154 vs -0.110 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 5 | 0.154 vs 0.056 | 1/5 | 0.3750 | no |
| Causal-Forcing++ (2-step) | CausVid | 5 | 0.154 vs 0.106 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 5 | 0.302 vs 0.451 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.302 vs -0.110 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 5 | 0.302 vs 0.056 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (1-step) | CausVid | 5 | 0.302 vs 0.106 | 0/5 | 0.0625 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 5 | 0.451 vs -0.110 | 0/5 | 0.0625 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 5 | 0.451 vs 0.056 | 0/5 | 0.0625 | no |
| Causal-Forcing (frame-wise) | CausVid | 5 | 0.451 vs 0.106 | 0/5 | 0.0625 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 5 | -0.110 vs 0.056 | 4/5 | 0.3750 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 5 | -0.110 vs 0.106 | 5/5 | 0.0625 | no |
| Self-Forcing | CausVid | 5 | 0.056 vs 0.106 | 3/5 | 1.0000 | no |

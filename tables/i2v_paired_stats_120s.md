# Paired significance — I2V @ 120s

Exact two-sided sign test over prompts evaluated by **both** methods.
`wins` = number of prompts where the row method has the *better* value.

## fBD (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 9.654 vs 7.260 | 6/20 | 0.1153 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 20 | 9.654 vs 19.947 | 15/20 | 0.0414 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 9.654 vs 11.369 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 9.654 vs 22.997 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing++ (2-step) | CausVid | 20 | 9.654 vs 19.652 | 15/20 | 0.0414 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 9.654 vs 13.598 | 17/20 | 0.0026 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 20 | 7.260 vs 19.947 | 17/20 | 0.0026 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 7.260 vs 11.369 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 7.260 vs 22.997 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing++ (1-step) | CausVid | 20 | 7.260 vs 19.652 | 19/20 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 7.260 vs 13.598 | 14/20 | 0.1153 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 20 | 19.947 vs 11.369 | 6/20 | 0.1153 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 20 | 19.947 vs 22.997 | 16/20 | 0.0118 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 20 | 19.947 vs 19.652 | 11/20 | 0.8238 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 19.947 vs 13.598 | 8/20 | 0.5034 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 20 | 11.369 vs 22.997 | 16/20 | 0.0118 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 20 | 11.369 vs 19.652 | 17/20 | 0.0026 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 11.369 vs 13.598 | 13/20 | 0.2632 | no |
| Self-Forcing | CausVid | 20 | 22.997 vs 19.652 | 7/20 | 0.2632 | no |
| Self-Forcing | Causal-Forcing++ (1-step, frame-wise) | 20 | 22.997 vs 13.598 | 5/20 | 0.0414 | **yes** |
| CausVid | Causal-Forcing++ (1-step, frame-wise) | 20 | 19.652 vs 13.598 | 7/20 | 0.2632 | no |

## NBF (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 8.815 vs 9.390 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 20 | 8.815 vs 52.668 | 20/20 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 8.815 vs 17.270 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 8.815 vs 10.346 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step) | CausVid | 20 | 8.815 vs 6.037 | 4/20 | 0.0118 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 8.815 vs 7.387 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 20 | 9.390 vs 52.668 | 20/20 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 9.390 vs 17.270 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 9.390 vs 10.346 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | CausVid | 20 | 9.390 vs 6.037 | 4/20 | 0.0118 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 9.390 vs 7.387 | 8/20 | 0.5034 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 20 | 52.668 vs 17.270 | 0/20 | 0.0000 | **yes** |
| Causal-Forcing (frame-wise) | Self-Forcing | 20 | 52.668 vs 10.346 | 0/20 | 0.0000 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 20 | 52.668 vs 6.037 | 0/20 | 0.0000 | **yes** |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 52.668 vs 7.387 | 0/20 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 20 | 17.270 vs 10.346 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 20 | 17.270 vs 6.037 | 5/20 | 0.0414 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 17.270 vs 7.387 | 8/20 | 0.5034 | no |
| Self-Forcing | CausVid | 20 | 10.346 vs 6.037 | 2/20 | 0.0004 | **yes** |
| Self-Forcing | Causal-Forcing++ (1-step, frame-wise) | 20 | 10.346 vs 7.387 | 9/20 | 0.8238 | no |
| CausVid | Causal-Forcing++ (1-step, frame-wise) | 20 | 6.037 vs 7.387 | 14/20 | 0.1153 | no |

## MCFF-E (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 0.891 vs 0.839 | 7/20 | 0.2632 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 20 | 0.891 vs 4.821 | 0/20 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.891 vs 1.890 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 0.891 vs 2.410 | 4/20 | 0.0118 | **yes** |
| Causal-Forcing++ (2-step) | CausVid | 20 | 0.891 vs 1.155 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.891 vs 1.011 | 11/20 | 0.8238 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 20 | 0.839 vs 4.821 | 3/20 | 0.0026 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.839 vs 1.890 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.839 vs 2.410 | 3/20 | 0.0026 | **yes** |
| Causal-Forcing++ (1-step) | CausVid | 20 | 0.839 vs 1.155 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.839 vs 1.011 | 12/20 | 0.5034 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 20 | 4.821 vs 1.890 | 17/20 | 0.0026 | **yes** |
| Causal-Forcing (frame-wise) | Self-Forcing | 20 | 4.821 vs 2.410 | 15/20 | 0.0414 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 20 | 4.821 vs 1.155 | 20/20 | 0.0000 | **yes** |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 4.821 vs 1.011 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 20 | 1.890 vs 2.410 | 5/20 | 0.0414 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 20 | 1.890 vs 1.155 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step, frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 1.890 vs 1.011 | 12/20 | 0.5034 | no |
| Self-Forcing | CausVid | 20 | 2.410 vs 1.155 | 16/20 | 0.0118 | **yes** |
| Self-Forcing | Causal-Forcing++ (1-step, frame-wise) | 20 | 2.410 vs 1.011 | 15/20 | 0.0414 | **yes** |
| CausVid | Causal-Forcing++ (1-step, frame-wise) | 20 | 1.155 vs 1.011 | 8/20 | 0.5034 | no |

## MCFF (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 0.819 vs 0.660 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 20 | 0.819 vs 5.057 | 0/20 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.819 vs 1.545 | 8/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 0.819 vs 0.762 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | CausVid | 20 | 0.819 vs 0.834 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.819 vs 0.349 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 20 | 0.660 vs 5.057 | 1/20 | 0.0000 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.660 vs 1.545 | 7/20 | 0.2632 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.660 vs 0.762 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | CausVid | 20 | 0.660 vs 0.834 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.660 vs 0.349 | 16/20 | 0.0118 | **yes** |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 20 | 5.057 vs 1.545 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing (frame-wise) | Self-Forcing | 20 | 5.057 vs 0.762 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 20 | 5.057 vs 0.834 | 20/20 | 0.0000 | **yes** |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 5.057 vs 0.349 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 20 | 1.545 vs 0.762 | 11/20 | 0.8238 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 20 | 1.545 vs 0.834 | 13/20 | 0.2632 | no |
| Causal-Forcing++ (2-step, frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 1.545 vs 0.349 | 13/20 | 0.2632 | no |
| Self-Forcing | CausVid | 20 | 0.762 vs 0.834 | 13/20 | 0.2632 | no |
| Self-Forcing | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.762 vs 0.349 | 14/20 | 0.1153 | no |
| CausVid | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.834 vs 0.349 | 10/20 | 1.0000 | no |

## FP (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 0.931 vs 0.861 | 11/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 20 | 0.931 vs 1.082 | 6/20 | 0.1153 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.931 vs 1.011 | 7/20 | 0.2632 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 0.931 vs 0.454 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing++ (2-step) | CausVid | 20 | 0.931 vs 0.668 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.931 vs 0.636 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 20 | 0.861 vs 1.082 | 6/20 | 0.1153 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.861 vs 1.011 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.861 vs 0.454 | 17/20 | 0.0026 | **yes** |
| Causal-Forcing++ (1-step) | CausVid | 20 | 0.861 vs 0.668 | 13/20 | 0.2632 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.861 vs 0.636 | 13/20 | 0.2632 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 19 | 1.082 vs 1.011 | 13/19 | 0.1671 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 20 | 1.082 vs 0.454 | 19/20 | 0.0000 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 20 | 1.082 vs 0.668 | 14/20 | 0.1153 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 1.082 vs 0.636 | 13/20 | 0.2632 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 20 | 1.011 vs 0.454 | 16/20 | 0.0118 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 20 | 1.011 vs 0.668 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step, frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 1.011 vs 0.636 | 14/20 | 0.1153 | no |
| Self-Forcing | CausVid | 20 | 0.454 vs 0.668 | 6/20 | 0.1153 | no |
| Self-Forcing | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.454 vs 0.636 | 8/20 | 0.5034 | no |
| CausVid | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.668 vs 0.636 | 13/20 | 0.2632 | no |

## DD_raw (higher is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 1.035 vs 0.972 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 20 | 1.035 vs 6.289 | 1/20 | 0.0000 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 1.035 vs 1.518 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 1.035 vs 0.935 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | CausVid | 20 | 1.035 vs 0.962 | 15/20 | 0.0414 | **yes** |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 1.035 vs 0.523 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 20 | 0.972 vs 6.289 | 2/20 | 0.0004 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.972 vs 1.518 | 7/20 | 0.2632 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.972 vs 0.935 | 11/20 | 0.8238 | no |
| Causal-Forcing++ (1-step) | CausVid | 20 | 0.972 vs 0.962 | 16/20 | 0.0118 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.972 vs 0.523 | 14/20 | 0.1153 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 20 | 6.289 vs 1.518 | 20/20 | 0.0000 | **yes** |
| Causal-Forcing (frame-wise) | Self-Forcing | 20 | 6.289 vs 0.935 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing (frame-wise) | CausVid | 20 | 6.289 vs 0.962 | 20/20 | 0.0000 | **yes** |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 6.289 vs 0.523 | 18/20 | 0.0004 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 20 | 1.518 vs 0.935 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 20 | 1.518 vs 0.962 | 13/20 | 0.2632 | no |
| Causal-Forcing++ (2-step, frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 1.518 vs 0.523 | 12/20 | 0.5034 | no |
| Self-Forcing | CausVid | 20 | 0.935 vs 0.962 | 16/20 | 0.0118 | **yes** |
| Self-Forcing | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.935 vs 0.523 | 15/20 | 0.0414 | **yes** |
| CausVid | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.962 vs 0.523 | 7/20 | 0.2632 | no |

## DLR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 0.575 vs 0.622 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 20 | 0.575 vs 0.674 | 11/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.575 vs 0.747 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 0.575 vs 0.661 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | CausVid | 20 | 0.575 vs 0.484 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.575 vs 0.767 | 15/20 | 0.0414 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 20 | 0.622 vs 0.674 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.622 vs 0.747 | 12/20 | 0.5034 | no |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.622 vs 0.661 | 11/20 | 0.8238 | no |
| Causal-Forcing++ (1-step) | CausVid | 20 | 0.622 vs 0.484 | 6/20 | 0.1153 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.622 vs 0.767 | 14/20 | 0.1153 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.674 vs 0.747 | 12/20 | 0.5034 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 20 | 0.674 vs 0.661 | 10/20 | 1.0000 | no |
| Causal-Forcing (frame-wise) | CausVid | 20 | 0.674 vs 0.484 | 8/20 | 0.5034 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.674 vs 0.767 | 14/20 | 0.1153 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 20 | 0.747 vs 0.661 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 20 | 0.747 vs 0.484 | 4/20 | 0.0118 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.747 vs 0.767 | 10/20 | 1.0000 | no |
| Self-Forcing | CausVid | 20 | 0.661 vs 0.484 | 5/20 | 0.0414 | **yes** |
| Self-Forcing | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.661 vs 0.767 | 14/20 | 0.1153 | no |
| CausVid | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.484 vs 0.767 | 15/20 | 0.0414 | **yes** |

## DAR (lower is better)

| A | B | n paired | mean A vs B | A wins | p (sign test) | sig |
|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step) | 20 | 0.276 vs 0.304 | 11/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing (frame-wise) | 20 | 0.276 vs 0.232 | 8/20 | 0.5034 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.276 vs 0.064 | 3/20 | 0.0026 | **yes** |
| Causal-Forcing++ (2-step) | Self-Forcing | 20 | 0.276 vs 0.257 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (2-step) | CausVid | 20 | 0.276 vs 0.138 | 6/20 | 0.1153 | no |
| Causal-Forcing++ (2-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.276 vs 0.327 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing (frame-wise) | 20 | 0.304 vs 0.232 | 10/20 | 1.0000 | no |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.304 vs 0.064 | 5/20 | 0.0414 | **yes** |
| Causal-Forcing++ (1-step) | Self-Forcing | 20 | 0.304 vs 0.257 | 9/20 | 0.8238 | no |
| Causal-Forcing++ (1-step) | CausVid | 20 | 0.304 vs 0.138 | 4/20 | 0.0118 | **yes** |
| Causal-Forcing++ (1-step) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.304 vs 0.327 | 10/20 | 1.0000 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (2-step, frame-wise) | 20 | 0.232 vs 0.064 | 6/20 | 0.1153 | no |
| Causal-Forcing (frame-wise) | Self-Forcing | 20 | 0.232 vs 0.257 | 10/20 | 1.0000 | no |
| Causal-Forcing (frame-wise) | CausVid | 20 | 0.232 vs 0.138 | 8/20 | 0.5034 | no |
| Causal-Forcing (frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.232 vs 0.327 | 13/20 | 0.2632 | no |
| Causal-Forcing++ (2-step, frame-wise) | Self-Forcing | 20 | 0.064 vs 0.257 | 16/20 | 0.0118 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | CausVid | 20 | 0.064 vs 0.138 | 15/20 | 0.0414 | **yes** |
| Causal-Forcing++ (2-step, frame-wise) | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.064 vs 0.327 | 15/20 | 0.0414 | **yes** |
| Self-Forcing | CausVid | 20 | 0.257 vs 0.138 | 8/20 | 0.5034 | no |
| Self-Forcing | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.257 vs 0.327 | 11/20 | 0.8238 | no |
| CausVid | Causal-Forcing++ (1-step, frame-wise) | 20 | 0.138 vs 0.327 | 14/20 | 0.1153 | no |

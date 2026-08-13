# Ranking disagreement — T2V @ 60s  (n=7 public methods)

Spearman rank correlation between each **generic** video metric and each **SNF-Bench** metric,
computed over method-level means. Values near 0 or of the *wrong sign* mean the generic metric
does not carry the information SNF-Bench measures.

| generic metric | fBD | NBF | MCFF | FP | DD_raw | DLR | DAR |
|---|---|---|---|---|---|---|---|
| VB-DD | 0.75 | 0.93 | 0.89 | 0.36 | 0.89 | 0.36 | 0.50 |
| VB-bg | -0.64 | -0.71 | -0.75 | -0.11 | -0.75 | -0.50 | -0.29 |
| VB-smooth | -0.96 | -0.82 | -0.61 | -0.71 | -0.61 | -0.64 | -0.61 |
| VB-flick | -0.96 | -0.82 | -0.61 | -0.71 | -0.61 | -0.64 | -0.61 |

## Per-method ranks

Directed metrics (↓/↑) are ranked 1 = best. Context metrics marked `(1=most)` have no intrinsic
"better" and are ranked 1 = most motion — the conventional reading SNF-Bench audits.

| Method | VB-DD(1=most) | VB-bg↑ | VB-smooth↑ | VB-flick↑ | fBD↓ | NBF↓ | MCFF(1=most) | FP↑ | DD_raw(1=most) | DLR↓ | DAR↓ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CausVid | 6 | 2 | 2 | 2 | 2 | 3 | 4 | 4 | 4 | 1 | 1 |
| Self-Forcing | 2 | 6 | 3 | 3 | 3 | 5 | 2 | 7 | 2 | 2 | 3 |
| Infinite-Forcing | 7 | 1 | 1 | 1 | 1 | 1 | 7 | 5 | 7 | 4 | 5 |
| Rolling-Forcing | 4 | 3 | 5 | 5 | 6 | 4 | 5 | 3 | 5 | 3 | 4 |
| Reward-Forcing | 5 | 5 | 4 | 4 | 4 | 2 | 6 | 6 | 6 | 6 | 2 |
| LongLive | 3 | 4 | 6 | 6 | 5 | 6 | 3 | 2 | 3 | 5 | 6 |
| Causal-Forcing | 1 | 7 | 7 | 7 | 7 | 7 | 1 | 1 | 1 | 7 | 7 |

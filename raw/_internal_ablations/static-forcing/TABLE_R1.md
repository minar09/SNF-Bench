
### task_results/r1_60s  (n videos per row shown)
| Method                   | n | fBD↓ | BFR↓ | FP↑ | MCFF_late↑ | DriftFrac↓ |
|---|---|---|---|---|---|---|
| CausVid                  | 23 | 8.14 | 1.161 | 0.670 | 2.279 | 0.45 |
| Self-Forcing             | 23 | 11.52 | 1.587 | 0.439 | 2.524 | 0.50 |
| Reward-Forcing           | 23 | 14.97 | 1.066 | 0.502 | 0.875 | 0.60 |
| Rolling-Forcing          | 24 | 16.27 | 1.371 | 0.729 | 1.536 | 0.53 |
| Infinite-Forcing         | 23 | 7.72 | 0.456 | 0.624 | 0.286 | 0.55 |
| LongLive                 | 23 | 15.72 | 1.734 | 0.766 | 2.440 | 0.59 |
| Causal-Forcing           | 23 | 22.81 | 10.955 | 0.782 | 6.893 | 0.94 |
| Steady-Forcing (Ours)    | 23 | 6.40 | 0.494 | 0.745 | 1.484 | 0.28 |

% ---- LaTeX (headline 3 cols) ----
\begin{tabular}{lccc}
\toprule
Method (60s) & fBD$\downarrow$ & BFR$\downarrow$ & FP$\uparrow$ \\
\midrule
CausVid & 8.14 & 1.161 & 0.670 \\
Self-Forcing & 11.52 & 1.587 & 0.439 \\
Reward-Forcing & 14.97 & 1.066 & 0.502 \\
Rolling-Forcing & 16.27 & 1.371 & 0.729 \\
Infinite-Forcing & 7.72 & 0.456 & 0.624 \\
LongLive & 15.72 & 1.734 & 0.766 \\
Causal-Forcing & 22.81 & 10.955 & 0.782 \\
Steady-Forcing (Ours) & \textbf{6.40} & \textbf{0.494} & \textbf{0.745} \\
\bottomrule
\end{tabular}

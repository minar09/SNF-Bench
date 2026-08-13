
### task_results/r2_60s  (n videos per row shown)
| Method                   | n | fBD↓ | BFR↓ | FP↑ | MCFF_late↑ | DriftFrac↓ |
|---|---|---|---|---|---|---|
| Base (no sink)           | 6 | 10.30 | 0.685 | 0.569 | 0.419 | 0.82 |
| V-Sink only              | 6 | 3.02 | 0.619 | 0.622 | 0.519 | 0.43 |
| EMA-Sink only            | 6 | 7.63 | 0.574 | 0.454 | 0.337 | 0.64 |
| Dual-Sink                | 6 | 1.92 | 0.537 | 0.464 | 0.393 | 0.59 |
| Dual-Sink + Flush (Full) | 6 | 4.32 | 0.500 | 0.355 | 0.278 | 0.62 |

% ---- LaTeX (headline 3 cols) ----
\begin{tabular}{lccc}
\toprule
Method (60s) & fBD$\downarrow$ & BFR$\downarrow$ & FP$\uparrow$ \\
\midrule
Base (no sink) & 10.30 & 0.685 & 0.569 \\
V-Sink only & 3.02 & 0.619 & 0.622 \\
EMA-Sink only & 7.63 & 0.574 & 0.454 \\
Dual-Sink & 1.92 & 0.537 & 0.464 \\
Dual-Sink + Flush (Full) & 4.32 & 0.500 & 0.355 \\
\bottomrule
\end{tabular}

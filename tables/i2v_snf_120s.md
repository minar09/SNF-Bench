# SNF-Bench core metrics — I2V @ 120s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | NBF↓ | MCFF-E | MCFF | FP↑ | DD_raw | DLR↓ | DAR↓ |
|---|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 20 | 9.654 <sub>[6.148, 13.218]</sub> | 8.815 <sub>[5.528, 12.760]</sub> | 0.891 <sub>[0.479, 1.435]</sub> | 0.819 <sub>[0.428, 1.307]</sub> | 0.931 <sub>[0.807, 1.079]</sub> | 1.035 <sub>[0.593, 1.580]</sub> | 0.575 <sub>[0.482, 0.668]</sub> | 0.276 <sub>[0.198, 0.357]</sub> |
| Causal-Forcing++ (1-step) | matched | 20 | 7.260 <sub>[4.447, 10.268]</sub> | 9.390 <sub>[6.130, 13.282]</sub> | 0.839 <sub>[0.540, 1.212]</sub> | 0.660 <sub>[0.412, 0.941]</sub> | 0.861 <sub>[0.703, 1.023]</sub> | 0.972 <sub>[0.626, 1.369]</sub> | 0.622 <sub>[0.530, 0.709]</sub> | 0.306 <sub>[0.218, 0.393]</sub> |
| Causal-Forcing (frame-wise) | matched | 20 | 19.947 <sub>[18.162, 21.639]</sub> | 52.668 <sub>[34.209, 73.948]</sub> | 4.821 <sub>[3.223, 6.529]</sub> | 5.057 <sub>[3.328, 6.964]</sub> | 1.082 <sub>[0.901, 1.280]</sub> | 6.289 <sub>[4.197, 8.678]</sub> | 0.674 <sub>[0.489, 0.889]</sub> | 0.241 <sub>[0.157, 0.329]</sub> |
| Causal-Forcing++ (2-step, frame-wise) | native | 20 | 11.369 <sub>[6.432, 16.803]</sub> | 17.270 <sub>[6.751, 30.383]</sub> | 1.890 <sub>[0.743, 3.454]</sub> | 1.545 <sub>[0.673, 2.643]</sub> | 1.011 <sub>[0.739, 1.295]</sub> | 1.518 <sub>[0.704, 2.561]</sub> | 0.747 <sub>[0.598, 0.914]</sub> | 0.090 <sub>[0.042, 0.147]</sub> |
| Self-Forcing | matched | 20 | 22.997 <sub>[20.805, 25.391]</sub> | 10.346 <sub>[6.186, 15.943]</sub> | 2.410 <sub>[1.356, 3.995]</sub> | 0.762 <sub>[0.409, 1.221]</sub> | 0.454 <sub>[0.294, 0.646]</sub> | 0.935 <sub>[0.535, 1.493]</sub> | 0.661 <sub>[0.555, 0.779]</sub> | 0.260 <sub>[0.173, 0.350]</sub> |
| CausVid | matched | 20 | 19.652 <sub>[17.436, 21.851]</sub> | 6.037 <sub>[2.620, 11.028]</sub> | 1.155 <sub>[0.454, 2.172]</sub> | 0.834 <sub>[0.259, 1.674]</sub> | 0.668 <sub>[0.551, 0.777]</sub> | 0.962 <sub>[0.307, 1.928]</sub> | 0.484 <sub>[0.394, 0.576]</sub> | 0.141 <sub>[0.097, 0.191]</sub> |
| Causal-Forcing++ (1-step, frame-wise) | native | 20 | 13.598 <sub>[9.170, 18.080]</sub> | 7.387 <sub>[5.012, 10.261]</sub> | 1.011 <sub>[0.495, 1.744]</sub> | 0.349 <sub>[0.204, 0.563]</sub> | 0.636 <sub>[0.420, 0.876]</sub> | 0.523 <sub>[0.339, 0.775]</sub> | 0.767 <sub>[0.649, 0.881]</sub> | 0.327 <sub>[0.235, 0.423]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & NBF$\downarrow$ & MCFF-E & MCFF & FP$\uparrow$ & DD\_raw & DLR$\downarrow$ & DAR$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 20 & 9.654 & 8.815 & 0.891 & 0.819 & 0.931 & 1.035 & 0.575 & 0.276 \\
Causal-Forcing++ (1-step) & matched & 20 & 7.260 & 9.390 & 0.839 & 0.660 & 0.861 & 0.972 & 0.622 & 0.306 \\
Causal-Forcing (frame-wise) & matched & 20 & 19.947 & 52.668 & 4.821 & 5.057 & 1.082 & 6.289 & 0.674 & 0.241 \\
Causal-Forcing++ (2-step, frame-wise) & native & 20 & 11.369 & 17.270 & 1.890 & 1.545 & 1.011 & 1.518 & 0.747 & 0.090 \\
Self-Forcing & matched & 20 & 22.997 & 10.346 & 2.410 & 0.762 & 0.454 & 0.935 & 0.661 & 0.260 \\
CausVid & matched & 20 & 19.652 & 6.037 & 1.155 & 0.834 & 0.668 & 0.962 & 0.484 & 0.141 \\
Causal-Forcing++ (1-step, frame-wise) & native & 20 & 13.598 & 7.387 & 1.011 & 0.349 & 0.636 & 0.523 & 0.767 & 0.327 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 120s}
\label{tab:i2v_snf_120s}
\end{table}
```
</details>

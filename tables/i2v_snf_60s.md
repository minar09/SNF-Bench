# SNF-Bench core metrics — I2V @ 60s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | BFR/NBF↓ | FP↑ | MCFF | DD_raw | DriftFrac↓ |
|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 30 | 9.177 <sub>[5.843, 12.764]</sub> | 0.746 <sub>[0.603, 0.906]</sub> | 0.858 <sub>[0.737, 0.989]</sub> | 0.665 <sub>[0.443, 0.939]</sub> | 0.740 <sub>[0.516, 1.011]</sub> | 0.668 <sub>[0.557, 0.799]</sub> |
| Causal-Forcing++ (1-step) | matched | 30 | 5.338 <sub>[3.097, 7.912]</sub> | 0.881 <sub>[0.701, 1.096]</sub> | 0.771 <sub>[0.665, 0.878]</sub> | 0.651 <sub>[0.453, 0.881]</sub> | 0.769 <sub>[0.545, 1.028]</sub> | 0.637 <sub>[0.555, 0.725]</sub> |
| Causal-Forcing (framewise) | matched | 1 | 23.395 <sub>[--, --]</sub> | 6.313 <sub>[--, --]</sub> | 0.652 <sub>[--, --]</sub> | 1.573 <sub>[--, --]</sub> | 2.239 <sub>[--, --]</sub> | 0.871 <sub>[--, --]</sub> |
| Causal-Forcing++ (2-step, native nfpb=1) | native | 30 | 9.935 <sub>[6.427, 13.572]</sub> | 0.864 <sub>[0.603, 1.191]</sub> | 0.976 <sub>[0.726, 1.238]</sub> | 0.814 <sub>[0.505, 1.179]</sub> | 0.894 <sub>[0.586, 1.254]</sub> | 0.749 <sub>[0.557, 0.974]</sub> |
| Self-Forcing | matched | 30 | 17.339 <sub>[14.636, 19.866]</sub> | 0.690 <sub>[0.564, 0.822]</sub> | 0.879 <sub>[0.681, 1.090]</sub> | 0.735 <sub>[0.486, 1.034]</sub> | 0.772 <sub>[0.529, 1.073]</sub> | 0.674 <sub>[0.525, 0.841]</sub> |
| CausVid | matched | 1 | 24.918 <sub>[--, --]</sub> | 0.181 <sub>[--, --]</sub> | 0.665 <sub>[--, --]</sub> | 0.109 <sub>[--, --]</sub> | 0.112 <sub>[--, --]</sub> | 0.590 <sub>[--, --]</sub> |
| Causal-Forcing++ (1-step, native) | native | 30 | 10.388 <sub>[6.484, 14.364]</sub> | 0.656 <sub>[0.503, 0.846]</sub> | 0.970 <sub>[0.764, 1.194]</sub> | 0.525 <sub>[0.370, 0.710]</sub> | 0.605 <sub>[0.428, 0.810]</sub> | 0.833 <sub>[0.602, 1.165]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & BFR/NBF$\downarrow$ & FP$\uparrow$ & MCFF & DD\_raw & DriftFrac$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 30 & 9.177 & 0.746 & 0.858 & 0.665 & 0.740 & 0.668 \\
Causal-Forcing++ (1-step) & matched & 30 & 5.338 & 0.881 & 0.771 & 0.651 & 0.769 & 0.637 \\
Causal-Forcing (framewise) & matched & 1 & 23.395 & 6.313 & 0.652 & 1.573 & 2.239 & 0.871 \\
Causal-Forcing++ (2-step, native nfpb=1) & native & 30 & 9.935 & 0.864 & 0.976 & 0.814 & 0.894 & 0.749 \\
Self-Forcing & matched & 30 & 17.339 & 0.690 & 0.879 & 0.735 & 0.772 & 0.674 \\
CausVid & matched & 1 & 24.918 & 0.181 & 0.665 & 0.109 & 0.112 & 0.590 \\
Causal-Forcing++ (1-step, native) & native & 30 & 10.388 & 0.656 & 0.970 & 0.525 & 0.605 & 0.833 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 60s}
\label{tab:i2v_snf_60s}
\end{table}
```
</details>

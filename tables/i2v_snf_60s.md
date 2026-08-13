# SNF-Bench core metrics — I2V @ 60s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | NBF↓ | FP↑ | MCFF | DD_raw | DLR↓ | DAR↓ |
|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 30 | 9.177 <sub>[5.843, 12.764]</sub> | 11.935 <sub>[9.656, 14.502]</sub> | 0.858 <sub>[0.737, 0.989]</sub> | 0.665 <sub>[0.443, 0.939]</sub> | 0.740 <sub>[0.516, 1.011]</sub> | 0.668 <sub>[0.557, 0.799]</sub> | 0.148 <sub>[0.109, 0.191]</sub> |
| Causal-Forcing++ (1-step) | matched | 30 | 5.338 <sub>[3.097, 7.912]</sub> | 14.103 <sub>[11.212, 17.542]</sub> | 0.771 <sub>[0.665, 0.878]</sub> | 0.651 <sub>[0.453, 0.881]</sub> | 0.769 <sub>[0.545, 1.028]</sub> | 0.637 <sub>[0.555, 0.725]</sub> | 0.158 <sub>[0.122, 0.200]</sub> |
| Causal-Forcing (framewise) | matched | 1 | 23.395 <sub>[--, --]</sub> | 101.0 <sub>[--, --]</sub> | 0.652 <sub>[--, --]</sub> | 1.573 <sub>[--, --]</sub> | 2.239 <sub>[--, --]</sub> | 0.871 <sub>[--, --]</sub> | 0.297 <sub>[--, --]</sub> |
| Causal-Forcing++ (2-step, native nfpb=1) | native | 30 | 9.935 <sub>[6.427, 13.572]</sub> | 13.826 <sub>[9.641, 19.062]</sub> | 0.976 <sub>[0.726, 1.238]</sub> | 0.814 <sub>[0.505, 1.179]</sub> | 0.894 <sub>[0.586, 1.254]</sub> | 0.749 <sub>[0.557, 0.974]</sub> | 0.110 <sub>[0.055, 0.181]</sub> |
| Self-Forcing | matched | 30 | 17.339 <sub>[14.636, 19.866]</sub> | 11.041 <sub>[9.028, 13.150]</sub> | 0.879 <sub>[0.681, 1.090]</sub> | 0.735 <sub>[0.486, 1.034]</sub> | 0.772 <sub>[0.529, 1.073]</sub> | 0.674 <sub>[0.525, 0.841]</sub> | 0.143 <sub>[0.074, 0.222]</sub> |
| CausVid | matched | 1 | 24.918 <sub>[--, --]</sub> | 2.894 <sub>[--, --]</sub> | 0.665 <sub>[--, --]</sub> | 0.109 <sub>[--, --]</sub> | 0.112 <sub>[--, --]</sub> | 0.590 <sub>[--, --]</sub> | 0.028 <sub>[--, --]</sub> |
| Causal-Forcing++ (1-step, native) | native | 30 | 10.388 <sub>[6.484, 14.364]</sub> | 10.493 <sub>[8.044, 13.531]</sub> | 0.970 <sub>[0.764, 1.194]</sub> | 0.525 <sub>[0.370, 0.710]</sub> | 0.605 <sub>[0.428, 0.810]</sub> | 0.833 <sub>[0.602, 1.165]</sub> | 0.139 <sub>[0.092, 0.191]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lccccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & NBF$\downarrow$ & FP$\uparrow$ & MCFF & DD\_raw & DLR$\downarrow$ & DAR$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 30 & 9.177 & 11.935 & 0.858 & 0.665 & 0.740 & 0.668 & 0.148 \\
Causal-Forcing++ (1-step) & matched & 30 & 5.338 & 14.103 & 0.771 & 0.651 & 0.769 & 0.637 & 0.158 \\
Causal-Forcing (framewise) & matched & 1 & 23.395 & 101.0 & 0.652 & 1.573 & 2.239 & 0.871 & 0.297 \\
Causal-Forcing++ (2-step, native nfpb=1) & native & 30 & 9.935 & 13.826 & 0.976 & 0.814 & 0.894 & 0.749 & 0.110 \\
Self-Forcing & matched & 30 & 17.339 & 11.041 & 0.879 & 0.735 & 0.772 & 0.674 & 0.143 \\
CausVid & matched & 1 & 24.918 & 2.894 & 0.665 & 0.109 & 0.112 & 0.590 & 0.028 \\
Causal-Forcing++ (1-step, native) & native & 30 & 10.388 & 10.493 & 0.970 & 0.525 & 0.605 & 0.833 & 0.139 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 60s}
\label{tab:i2v_snf_60s}
\end{table}
```
</details>

# SNF-Bench core metrics — I2V @ 120s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | BFR/NBF↓ | FP↑ | MCFF | DD_raw | DriftFrac↓ |
|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 20 | 9.654 <sub>[6.148, 13.218]</sub> | 1.102 <sub>[0.691, 1.595]</sub> | 0.909 <sub>[0.796, 1.033]</sub> | 0.932 <sub>[0.518, 1.440]</sub> | 1.035 <sub>[0.593, 1.580]</sub> | 0.575 <sub>[0.482, 0.668]</sub> |
| Causal-Forcing++ (1-step) | matched | 20 | 7.260 <sub>[4.447, 10.268]</sub> | 1.174 <sub>[0.766, 1.660]</sub> | 0.835 <sub>[0.695, 0.975]</sub> | 0.833 <sub>[0.516, 1.202]</sub> | 0.972 <sub>[0.626, 1.369]</sub> | 0.622 <sub>[0.530, 0.709]</sub> |
| Causal-Forcing (framewise) | matched | 1 | 19.403 <sub>[--, --]</sub> | 2.092 <sub>[--, --]</sub> | 1.588 <sub>[--, --]</sub> | 0.994 <sub>[--, --]</sub> | 1.441 <sub>[--, --]</sub> | 0.855 <sub>[--, --]</sub> |
| Causal-Forcing++ (2-step, native nfpb=1) | native | 20 | 11.369 <sub>[6.432, 16.803]</sub> | 2.159 <sub>[0.844, 3.798]</sub> | 0.962 <sub>[0.695, 1.242]</sub> | 1.542 <sub>[0.681, 2.631]</sub> | 1.518 <sub>[0.704, 2.561]</sub> | 0.747 <sub>[0.598, 0.914]</sub> |
| Self-Forcing | matched | 20 | 22.997 <sub>[20.805, 25.391]</sub> | 1.293 <sub>[0.773, 1.993]</sub> | 0.436 <sub>[0.298, 0.586]</sub> | 0.777 <sub>[0.453, 1.171]</sub> | 0.935 <sub>[0.535, 1.493]</sub> | 0.661 <sub>[0.555, 0.779]</sub> |
| CausVid | matched | 1 | 20.743 <sub>[--, --]</sub> | 0.321 <sub>[--, --]</sub> | 0.888 <sub>[--, --]</sub> | 0.201 <sub>[--, --]</sub> | 0.186 <sub>[--, --]</sub> | 0.605 <sub>[--, --]</sub> |
| Causal-Forcing++ (1-step, native) | native | 20 | 13.598 <sub>[9.170, 18.080]</sub> | 0.923 <sub>[0.626, 1.283]</sub> | 0.685 <sub>[0.449, 0.947]</sub> | 0.426 <sub>[0.257, 0.652]</sub> | 0.523 <sub>[0.339, 0.775]</sub> | 0.767 <sub>[0.649, 0.881]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & BFR/NBF$\downarrow$ & FP$\uparrow$ & MCFF & DD\_raw & DriftFrac$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 20 & 9.654 & 1.102 & 0.909 & 0.932 & 1.035 & 0.575 \\
Causal-Forcing++ (1-step) & matched & 20 & 7.260 & 1.174 & 0.835 & 0.833 & 0.972 & 0.622 \\
Causal-Forcing (framewise) & matched & 1 & 19.403 & 2.092 & 1.588 & 0.994 & 1.441 & 0.855 \\
Causal-Forcing++ (2-step, native nfpb=1) & native & 20 & 11.369 & 2.159 & 0.962 & 1.542 & 1.518 & 0.747 \\
Self-Forcing & matched & 20 & 22.997 & 1.293 & 0.436 & 0.777 & 0.935 & 0.661 \\
CausVid & matched & 1 & 20.743 & 0.321 & 0.888 & 0.201 & 0.186 & 0.605 \\
Causal-Forcing++ (1-step, native) & native & 20 & 13.598 & 0.923 & 0.685 & 0.426 & 0.523 & 0.767 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 120s}
\label{tab:i2v_snf_120s}
\end{table}
```
</details>

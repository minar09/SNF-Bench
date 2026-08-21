# SNF-Bench core metrics — I2V @ 60s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | NBF↓ | MCFF-E | MCFF | FP↑ | DD_raw | DLR↓ | DAR↓ |
|---|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 30 | 9.177 <sub>[5.843, 12.764]</sub> | 5.967 <sub>[4.828, 7.251]</sub> | 0.851 <sub>[0.476, 1.339]</sub> | 0.604 <sub>[0.382, 0.882]</sub> | 0.860 <sub>[0.740, 0.993]</sub> | 0.740 <sub>[0.516, 1.011]</sub> | 0.668 <sub>[0.557, 0.799]</sub> | 0.255 <sub>[0.198, 0.317]</sub> |
| Causal-Forcing++ (1-step) | matched | 30 | 5.338 <sub>[3.097, 7.912]</sub> | 7.051 <sub>[5.606, 8.771]</sub> | 0.855 <sub>[0.560, 1.207]</sub> | 0.574 <sub>[0.383, 0.801]</sub> | 0.768 <sub>[0.656, 0.881]</sub> | 0.769 <sub>[0.545, 1.028]</sub> | 0.637 <sub>[0.555, 0.725]</sub> | 0.279 <sub>[0.229, 0.334]</sub> |
| Causal-Forcing (frame-wise) | matched | 30 | 21.147 <sub>[18.837, 23.331]</sub> | 36.391 <sub>[28.349, 45.565]</sub> | 2.799 <sub>[1.876, 3.896]</sub> | 2.686 <sub>[1.744, 3.879]</sub> | 0.893 <sub>[0.734, 1.071]</sub> | 3.612 <sub>[2.585, 4.843]</sub> | 0.800 <sub>[0.633, 1.012]</sub> | 0.354 <sub>[0.271, 0.440]</sub> |
| Causal-Forcing++ (2-step, frame-wise) | native | 30 | 9.935 <sub>[6.427, 13.572]</sub> | 6.913 <sub>[4.820, 9.531]</sub> | 1.303 <sub>[0.600, 2.250]</sub> | 0.778 <sub>[0.473, 1.144]</sub> | 1.024 <sub>[0.766, 1.295]</sub> | 0.894 <sub>[0.586, 1.254]</sub> | 0.749 <sub>[0.557, 0.974]</sub> | 0.169 <sub>[0.108, 0.242]</sub> |
| Self-Forcing | matched | 30 | 17.339 <sub>[14.636, 19.866]</sub> | 5.520 <sub>[4.514, 6.575]</sub> | 1.498 <sub>[0.782, 2.367]</sub> | 0.694 <sub>[0.455, 0.986]</sub> | 0.891 <sub>[0.693, 1.105]</sub> | 0.772 <sub>[0.529, 1.073]</sub> | 0.674 <sub>[0.525, 0.841]</sub> | 0.183 <sub>[0.112, 0.259]</sub> |
| CausVid | matched | 30 | 19.894 <sub>[16.751, 23.116]</sub> | 3.307 <sub>[2.368, 4.436]</sub> | 0.578 <sub>[0.312, 0.950]</sub> | 0.408 <sub>[0.217, 0.663]</sub> | 0.808 <sub>[0.695, 0.929]</sub> | 0.480 <sub>[0.265, 0.753]</sub> | 0.568 <sub>[0.471, 0.673]</sub> | 0.141 <sub>[0.103, 0.188]</sub> |
| Causal-Forcing++ (1-step, frame-wise) | native | 30 | 10.388 <sub>[6.484, 14.364]</sub> | 5.247 <sub>[4.022, 6.766]</sub> | 0.526 <sub>[0.392, 0.692]</sub> | 0.525 <sub>[0.357, 0.725]</sub> | 1.007 <sub>[0.795, 1.235]</sub> | 0.605 <sub>[0.428, 0.810]</sub> | 0.833 <sub>[0.602, 1.165]</sub> | 0.219 <sub>[0.159, 0.282]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & NBF$\downarrow$ & MCFF-E & MCFF & FP$\uparrow$ & DD\_raw & DLR$\downarrow$ & DAR$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 30 & 9.177 & 5.967 & 0.851 & 0.604 & 0.860 & 0.740 & 0.668 & 0.255 \\
Causal-Forcing++ (1-step) & matched & 30 & 5.338 & 7.051 & 0.855 & 0.574 & 0.768 & 0.769 & 0.637 & 0.279 \\
Causal-Forcing (frame-wise) & matched & 30 & 21.147 & 36.391 & 2.799 & 2.686 & 0.893 & 3.612 & 0.800 & 0.354 \\
Causal-Forcing++ (2-step, frame-wise) & native & 30 & 9.935 & 6.913 & 1.303 & 0.778 & 1.024 & 0.894 & 0.749 & 0.169 \\
Self-Forcing & matched & 30 & 17.339 & 5.520 & 1.498 & 0.694 & 0.891 & 0.772 & 0.674 & 0.183 \\
CausVid & matched & 30 & 19.894 & 3.307 & 0.578 & 0.408 & 0.808 & 0.480 & 0.568 & 0.141 \\
Causal-Forcing++ (1-step, frame-wise) & native & 30 & 10.388 & 5.247 & 0.526 & 0.525 & 1.007 & 0.605 & 0.833 & 0.219 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 60s}
\label{tab:i2v_snf_60s}
\end{table}
```
</details>

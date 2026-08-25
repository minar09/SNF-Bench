# Appearance / stagnation metrics — I2V @ 240s

cv2-only metrics (blur growth, colour drift, background identity, stagnation onset).

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | sharp_ratio↑ | sharp_mean | dE_static↓ | dL_static | idPSNR↑ | FDP↑ | stag_onset↑ |
|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | wrapper | 5 | 0.965 <sub>[0.902, 1.007]</sub> | 353.9 <sub>[175.4, 552.1]</sub> | 6.100 <sub>[2.424, 9.936]</sub> | -1.456 <sub>[-3.658, 0.746]</sub> | 14.022 <sub>[12.504, 15.978]</sub> | 0.699 <sub>[0.646, 0.754]</sub> | 0.821 <sub>[0.526, 0.996]</sub> |
| Causal-Forcing++ (1-step) | wrapper | 5 | 1.206 <sub>[0.933, 1.693]</sub> | 356.3 <sub>[226.5, 524.9]</sub> | 3.268 <sub>[1.678, 5.132]</sub> | -0.076 <sub>[-1.408, 1.084]</sub> | 15.234 <sub>[14.434, 16.214]</sub> | 0.680 <sub>[0.596, 0.763]</sub> | 0.765 <sub>[0.460, 1.000]</sub> |
| Causal-Forcing (frame-wise) | wrapper | 5 | 0.931 <sub>[0.825, 1.022]</sub> | 414.3 <sub>[171.2, 729.1]</sub> | 5.228 <sub>[2.418, 8.038]</sub> | 0.240 <sub>[-1.860, 2.130]</sub> | 12.986 <sub>[12.270, 13.522]</sub> | 0.778 <sub>[0.738, 0.818]</sub> | 0.277 <sub>[0.175, 0.428]</sub> |
| Causal-Forcing++ (2-step, frame-wise) | released | 5 | 0.971 <sub>[0.681, 1.289]</sub> | 1115.2 <sub>[485.9, 1744.5]</sub> | 34.908 <sub>[17.460, 55.332]</sub> | -12.178 <sub>[-19.968, -4.874]</sub> | 12.908 <sub>[10.040, 15.488]</sub> | 0.443 <sub>[0.250, 0.626]</sub> | 0.334 <sub>[0.224, 0.502]</sub> |
| Self-Forcing | wrapper | 5 | 1.623 <sub>[0.822, 2.424]</sub> | 538.4 <sub>[309.3, 819.0]</sub> | 19.702 <sub>[12.784, 26.366]</sub> | -3.896 <sub>[-8.872, 1.174]</sub> | 11.190 <sub>[9.386, 13.450]</sub> | 0.529 <sub>[0.338, 0.767]</sub> | 0.488 <sub>[0.317, 0.751]</sub> |
| CausVid | wrapper | 5 | 1.190 <sub>[0.896, 1.591]</sub> | 1671.9 <sub>[512.7, 3139.3]</sub> | 14.838 <sub>[8.058, 23.292]</sub> | 1.228 <sub>[-4.088, 6.458]</sub> | 10.810 <sub>[8.736, 12.922]</sub> | 0.521 <sub>[0.395, 0.648]</sub> | 0.538 <sub>[0.220, 0.857]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lccccccccc}
\toprule
Method & setting & n & sharp\_ratio$\uparrow$ & sharp\_mean & dE\_static$\downarrow$ & dL\_static & idPSNR$\uparrow$ & FDP$\uparrow$ & stag\_onset$\uparrow$ \\
\midrule
Causal-Forcing++ (2-step) & wrapper & 5 & 0.965 & 353.9 & 6.100 & -1.456 & 14.022 & 0.699 & 0.821 \\
Causal-Forcing++ (1-step) & wrapper & 5 & 1.206 & 356.3 & 3.268 & -0.076 & 15.234 & 0.680 & 0.765 \\
Causal-Forcing (frame-wise) & wrapper & 5 & 0.931 & 414.3 & 5.228 & 0.240 & 12.986 & 0.778 & 0.277 \\
Causal-Forcing++ (2-step, frame-wise) & released & 5 & 0.971 & 1115.2 & 34.908 & -12.178 & 12.908 & 0.443 & 0.334 \\
Self-Forcing & wrapper & 5 & 1.623 & 538.4 & 19.702 & -3.896 & 11.190 & 0.529 & 0.488 \\
CausVid & wrapper & 5 & 1.190 & 1671.9 & 14.838 & 1.228 & 10.810 & 0.521 & 0.538 \\
\bottomrule
\end{tabular}
\caption{Appearance / stagnation metrics — I2V @ 240s}
\label{tab:i2v_snf_240s}
\end{table}
```
</details>

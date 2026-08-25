# Appearance / stagnation metrics — I2V @ 60s

cv2-only metrics (blur growth, colour drift, background identity, stagnation onset).

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | sharp_ratio↑ | sharp_mean | dE_static↓ | dL_static | idPSNR↑ | FDP↑ | stag_onset↑ |
|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | wrapper | 30 | 0.992 <sub>[0.911, 1.078]</sub> | 270.4 <sub>[222.8, 323.1]</sub> | 7.172 <sub>[5.861, 8.500]</sub> | -0.950 <sub>[-1.971, 0.133]</sub> | 15.178 <sub>[14.159, 16.225]</sub> | 0.579 <sub>[0.516, 0.640]</sub> | 0.533 <sub>[0.399, 0.669]</sub> |
| Causal-Forcing++ (1-step) | wrapper | 30 | 1.098 <sub>[0.935, 1.291]</sub> | 286.3 <sub>[235.2, 341.2]</sub> | 5.781 <sub>[4.612, 7.021]</sub> | -0.469 <sub>[-1.345, 0.426]</sub> | 15.240 <sub>[14.399, 16.092]</sub> | 0.601 <sub>[0.540, 0.663]</sub> | 0.581 <sub>[0.451, 0.711]</sub> |
| Causal-Forcing (frame-wise) | wrapper | 30 | 1.108 <sub>[0.931, 1.307]</sub> | 338.2 <sub>[279.3, 400.3]</sub> | 11.790 <sub>[9.566, 14.080]</sub> | 0.138 <sub>[-1.645, 1.914]</sub> | 12.719 <sub>[12.024, 13.403]</sub> | 0.636 <sub>[0.585, 0.688]</sub> | 0.324 <sub>[0.241, 0.419]</sub> |
| Causal-Forcing++ (2-step, frame-wise) | released | 30 | 1.577 <sub>[1.132, 2.204]</sub> | 770.6 <sub>[560.5, 998.8]</sub> | 26.157 <sub>[20.521, 32.136]</sub> | -5.127 <sub>[-8.354, -1.710]</sub> | 13.900 <sub>[12.800, 15.017]</sub> | 0.572 <sub>[0.446, 0.718]</sub> | 0.373 <sub>[0.267, 0.487]</sub> |
| Self-Forcing | wrapper | 30 | 1.519 <sub>[0.975, 2.294]</sub> | 514.9 <sub>[388.8, 642.2]</sub> | 19.994 <sub>[16.501, 23.845]</sub> | -4.551 <sub>[-6.994, -1.988]</sub> | 13.184 <sub>[12.306, 14.089]</sub> | 0.611 <sub>[0.536, 0.691]</sub> | 0.493 <sub>[0.365, 0.626]</sub> |
| CausVid | wrapper | 30 | 1.093 <sub>[0.980, 1.227]</sub> | 1068.0 <sub>[776.4, 1406.5]</sub> | 9.369 <sub>[7.323, 11.599]</sub> | 1.579 <sub>[0.417, 2.802]</sub> | 12.282 <sub>[11.447, 13.158]</sub> | 0.431 <sub>[0.379, 0.485]</sub> | 0.359 <sub>[0.259, 0.474]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lccccccccc}
\toprule
Method & setting & n & sharp\_ratio$\uparrow$ & sharp\_mean & dE\_static$\downarrow$ & dL\_static & idPSNR$\uparrow$ & FDP$\uparrow$ & stag\_onset$\uparrow$ \\
\midrule
Causal-Forcing++ (2-step) & wrapper & 30 & 0.992 & 270.4 & 7.172 & -0.950 & 15.178 & 0.579 & 0.533 \\
Causal-Forcing++ (1-step) & wrapper & 30 & 1.098 & 286.3 & 5.781 & -0.469 & 15.240 & 0.601 & 0.581 \\
Causal-Forcing (frame-wise) & wrapper & 30 & 1.108 & 338.2 & 11.790 & 0.138 & 12.719 & 0.636 & 0.324 \\
Causal-Forcing++ (2-step, frame-wise) & released & 30 & 1.577 & 770.6 & 26.157 & -5.127 & 13.900 & 0.572 & 0.373 \\
Self-Forcing & wrapper & 30 & 1.519 & 514.9 & 19.994 & -4.551 & 13.184 & 0.611 & 0.493 \\
CausVid & wrapper & 30 & 1.093 & 1068.0 & 9.369 & 1.579 & 12.282 & 0.431 & 0.359 \\
\bottomrule
\end{tabular}
\caption{Appearance / stagnation metrics — I2V @ 60s}
\label{tab:i2v_snf_60s}
\end{table}
```
</details>

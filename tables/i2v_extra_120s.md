# Appearance / stagnation metrics — I2V @ 120s

cv2-only metrics (blur growth, colour drift, background identity, stagnation onset).

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | sharp_ratio↑ | sharp_mean | dE_static↓ | dL_static | idPSNR↑ | FDP↑ | stag_onset↑ |
|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 20 | 0.871 <sub>[0.799, 0.946]</sub> | 212.7 <sub>[163.5, 262.9]</sub> | 5.557 <sub>[4.091, 7.225]</sub> | -0.394 <sub>[-1.493, 0.658]</sub> | 14.552 <sub>[13.439, 15.663]</sub> | 0.640 <sub>[0.590, 0.689]</sub> | 0.538 <sub>[0.388, 0.694]</sub> |
| Causal-Forcing++ (1-step) | matched | 20 | 0.933 <sub>[0.823, 1.091]</sub> | 197.4 <sub>[153.9, 243.7]</sub> | 4.966 <sub>[3.502, 6.671]</sub> | -0.274 <sub>[-1.300, 0.746]</sub> | 14.934 <sub>[14.012, 15.855]</sub> | 0.671 <sub>[0.617, 0.725]</sub> | 0.633 <sub>[0.474, 0.784]</sub> |
| Causal-Forcing (framewise) | matched | 20 | 1.061 <sub>[0.820, 1.430]</sub> | 257.8 <sub>[174.5, 350.4]</sub> | 9.675 <sub>[7.756, 11.848]</sub> | 0.784 <sub>[-0.902, 2.568]</sub> | 13.185 <sub>[12.286, 14.150]</sub> | 0.718 <sub>[0.661, 0.778]</sub> | 0.287 <sub>[0.190, 0.398]</sub> |
| Causal-Forcing++ (2-step, native nfpb=1) | native | 20 | 2.276 <sub>[1.322, 3.647]</sub> | 602.6 <sub>[410.3, 808.7]</sub> | 36.499 <sub>[28.787, 45.130]</sub> | -6.823 <sub>[-12.508, -1.085]</sub> | 12.675 <sub>[11.261, 14.206]</sub> | 0.526 <sub>[0.405, 0.685]</sub> | 0.246 <sub>[0.190, 0.308]</sub> |
| Self-Forcing | matched | 20 | 1.679 <sub>[1.169, 2.281]</sub> | 361.2 <sub>[262.0, 471.1]</sub> | 21.556 <sub>[15.190, 28.887]</sub> | -5.868 <sub>[-9.359, -2.514]</sub> | 12.314 <sub>[11.213, 13.432]</sub> | 0.636 <sub>[0.517, 0.773]</sub> | 0.222 <sub>[0.141, 0.312]</sub> |
| CausVid | matched | 20 | 1.048 <sub>[0.905, 1.187]</sub> | 965.4 <sub>[664.2, 1291.0]</sub> | 8.511 <sub>[6.222, 10.966]</sub> | 0.515 <sub>[-1.017, 1.949]</sub> | 12.893 <sub>[11.834, 14.010]</sub> | 0.362 <sub>[0.298, 0.427]</sub> | 0.237 <sub>[0.201, 0.281]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lccccccccc}
\toprule
Method & setting & n & sharp\_ratio$\uparrow$ & sharp\_mean & dE\_static$\downarrow$ & dL\_static & idPSNR$\uparrow$ & FDP$\uparrow$ & stag\_onset$\uparrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 20 & 0.871 & 212.7 & 5.557 & -0.394 & 14.552 & 0.640 & 0.538 \\
Causal-Forcing++ (1-step) & matched & 20 & 0.933 & 197.4 & 4.966 & -0.274 & 14.934 & 0.671 & 0.633 \\
Causal-Forcing (framewise) & matched & 20 & 1.061 & 257.8 & 9.675 & 0.784 & 13.185 & 0.718 & 0.287 \\
Causal-Forcing++ (2-step, native nfpb=1) & native & 20 & 2.276 & 602.6 & 36.499 & -6.823 & 12.675 & 0.526 & 0.246 \\
Self-Forcing & matched & 20 & 1.679 & 361.2 & 21.556 & -5.868 & 12.314 & 0.636 & 0.222 \\
CausVid & matched & 20 & 1.048 & 965.4 & 8.511 & 0.515 & 12.893 & 0.362 & 0.237 \\
\bottomrule
\end{tabular}
\caption{Appearance / stagnation metrics — I2V @ 120s}
\label{tab:i2v_snf_120s}
\end{table}
```
</details>

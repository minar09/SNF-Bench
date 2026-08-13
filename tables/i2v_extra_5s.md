# Appearance / stagnation metrics — I2V @ 5s

cv2-only metrics (blur growth, colour drift, background identity, stagnation onset).

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | sharp_ratio↑ | sharp_mean | dE_static↓ | dL_static | idPSNR↑ | FDP↑ | stag_onset↑ |
|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 10 | 1.420 <sub>[1.192, 1.659]</sub> | 275.1 <sub>[158.6, 418.5]</sub> | 10.976 <sub>[6.529, 16.095]</sub> | -2.589 <sub>[-5.364, -0.034]</sub> | 16.355 <sub>[14.768, 18.007]</sub> | 0.523 <sub>[0.393, 0.649]</sub> | 0.241 <sub>[0.091, 0.441]</sub> |
| Causal-Forcing++ (1-step) | matched | 10 | 1.398 <sub>[1.122, 1.677]</sub> | 263.4 <sub>[159.8, 395.8]</sub> | 10.293 <sub>[6.764, 14.254]</sub> | -1.030 <sub>[-3.683, 1.466]</sub> | 16.328 <sub>[15.010, 17.745]</sub> | 0.495 <sub>[0.388, 0.592]</sub> | 0.230 <sub>[0.083, 0.427]</sub> |
| Causal-Forcing (framewise) | matched | 10 | 1.407 <sub>[1.073, 1.744]</sub> | 315.3 <sub>[173.6, 483.9]</sub> | 15.113 <sub>[11.469, 18.593]</sub> | 0.709 <sub>[-2.432, 4.058]</sub> | 13.807 <sub>[12.389, 15.199]</sub> | 0.567 <sub>[0.494, 0.634]</sub> | 0.024 <sub>[0.021, 0.030]</sub> |
| Causal-Forcing++ (2-step, native nfpb=1) | native | 10 | 1.266 <sub>[1.140, 1.383]</sub> | 602.5 <sub>[237.8, 1112.3]</sub> | 9.087 <sub>[4.868, 14.386]</sub> | 1.359 <sub>[-0.466, 3.572]</sub> | 17.895 <sub>[16.722, 19.154]</sub> | 0.397 <sub>[0.252, 0.563]</sub> | 0.245 <sub>[0.109, 0.440]</sub> |
| Self-Forcing | matched | 10 | 1.685 <sub>[1.396, 2.062]</sub> | 520.0 <sub>[228.3, 924.0]</sub> | 7.753 <sub>[4.964, 10.768]</sub> | -2.456 <sub>[-3.901, -1.030]</sub> | 17.664 <sub>[16.269, 19.209]</sub> | 0.438 <sub>[0.310, 0.609]</sub> | 0.027 <sub>[0.021, 0.036]</sub> |
| CausVid | matched | 10 | 1.798 <sub>[1.433, 2.107]</sub> | 1017.7 <sub>[474.3, 1791.5]</sub> | 18.464 <sub>[12.222, 25.315]</sub> | 1.946 <sub>[-1.499, 5.721]</sub> | 13.868 <sub>[12.118, 15.539]</sub> | 0.398 <sub>[0.332, 0.465]</sub> | 0.022 <sub>[0.015, 0.030]</sub> |
| Wan2.1-I2V-14B-480P | native | 10 | 0.975 <sub>[0.859, 1.102]</sub> | 713.2 <sub>[291.2, 1371.4]</sub> | 7.316 <sub>[3.085, 11.992]</sub> | -0.911 <sub>[-2.505, 0.682]</sub> | 18.979 <sub>[16.627, 21.521]</sub> | 0.750 <sub>[0.583, 0.892]</sub> | 0.814 <sub>[0.609, 1.000]</sub> |
| Wan2.2-I2V-A14B | native | 10 | 1.001 <sub>[0.832, 1.121]</sub> | 706.7 <sub>[263.0, 1359.7]</sub> | 14.592 <sub>[5.251, 26.957]</sub> | -3.518 <sub>[-8.259, 0.184]</sub> | 16.451 <sub>[13.843, 18.989]</sub> | 0.705 <sub>[0.547, 0.881]</sub> | 0.694 <sub>[0.456, 0.910]</sub> |
| LTX-Video 13B-0.9.8-distilled | native | 10 | 1.645 <sub>[1.335, 1.994]</sub> | 121.8 <sub>[72.420, 176.9]</sub> | 7.548 <sub>[4.888, 10.385]</sub> | 1.782 <sub>[0.084, 3.469]</sub> | 18.930 <sub>[16.133, 21.706]</sub> | 0.490 <sub>[0.296, 0.684]</sub> | 0.641 <sub>[0.398, 0.861]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lccccccccc}
\toprule
Method & setting & n & sharp\_ratio$\uparrow$ & sharp\_mean & dE\_static$\downarrow$ & dL\_static & idPSNR$\uparrow$ & FDP$\uparrow$ & stag\_onset$\uparrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 10 & 1.420 & 275.1 & 10.976 & -2.589 & 16.355 & 0.523 & 0.241 \\
Causal-Forcing++ (1-step) & matched & 10 & 1.398 & 263.4 & 10.293 & -1.030 & 16.328 & 0.495 & 0.230 \\
Causal-Forcing (framewise) & matched & 10 & 1.407 & 315.3 & 15.113 & 0.709 & 13.807 & 0.567 & 0.024 \\
Causal-Forcing++ (2-step, native nfpb=1) & native & 10 & 1.266 & 602.5 & 9.087 & 1.359 & 17.895 & 0.397 & 0.245 \\
Self-Forcing & matched & 10 & 1.685 & 520.0 & 7.753 & -2.456 & 17.664 & 0.438 & 0.027 \\
CausVid & matched & 10 & 1.798 & 1017.7 & 18.464 & 1.946 & 13.868 & 0.398 & 0.022 \\
Wan2.1-I2V-14B-480P & native & 10 & 0.975 & 713.2 & 7.316 & -0.911 & 18.979 & 0.750 & 0.814 \\
Wan2.2-I2V-A14B & native & 10 & 1.001 & 706.7 & 14.592 & -3.518 & 16.451 & 0.705 & 0.694 \\
LTX-Video 13B-0.9.8-distilled & native & 10 & 1.645 & 121.8 & 7.548 & 1.782 & 18.930 & 0.490 & 0.641 \\
\bottomrule
\end{tabular}
\caption{Appearance / stagnation metrics — I2V @ 5s}
\label{tab:i2v_snf_5s}
\end{table}
```
</details>

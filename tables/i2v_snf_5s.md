# SNF-Bench core metrics — I2V @ 5s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | NBF↓ | FP↑ | MCFF | DD_raw | DLR↓ | DAR↓ |
|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 10 | 3.688 <sub>[0.989, 7.558]</sub> | 20.010 <sub>[12.255, 28.658]</sub> | 0.884 <sub>[0.552, 1.247]</sub> | 0.651 <sub>[0.312, 1.114]</sub> | 0.811 <sub>[0.430, 1.286]</sub> | 0.672 <sub>[0.505, 0.838]</sub> | 0.222 <sub>[0.119, 0.329]</sub> |
| Causal-Forcing++ (1-step) | matched | 10 | 5.279 <sub>[1.451, 10.454]</sub> | 22.863 <sub>[14.727, 32.144]</sub> | 0.663 <sub>[0.503, 0.833]</sub> | 0.508 <sub>[0.286, 0.750]</sub> | 0.662 <sub>[0.388, 0.964]</sub> | 0.661 <sub>[0.521, 0.793]</sub> | 0.243 <sub>[0.153, 0.331]</sub> |
| Causal-Forcing (framewise) | matched | 10 | 16.075 <sub>[10.248, 22.518]</sub> | 90.659 <sub>[71.417, 110.1]</sub> | 0.395 <sub>[0.243, 0.580]</sub> | 3.281 <sub>[1.791, 4.981]</sub> | 3.564 <sub>[2.056, 5.296]</sub> | 0.678 <sub>[0.474, 0.892]</sub> | 0.124 <sub>[0.030, 0.262]</sub> |
| Causal-Forcing++ (2-step, native nfpb=1) | native | 10 | 1.218 <sub>[0.710, 1.794]</sub> | 21.227 <sub>[9.389, 36.521]</sub> | 0.488 <sub>[0.268, 0.758]</sub> | 0.830 <sub>[0.348, 1.582]</sub> | 0.885 <sub>[0.396, 1.638]</sub> | 0.681 <sub>[0.520, 0.844]</sub> | 0.106 <sub>[0.042, 0.186]</sub> |
| Self-Forcing | matched | 10 | 9.665 <sub>[4.677, 14.978]</sub> | 11.484 <sub>[8.085, 15.448]</sub> | 0.649 <sub>[0.390, 0.941]</sub> | 0.330 <sub>[0.156, 0.536]</sub> | 0.346 <sub>[0.170, 0.556]</sub> | 0.737 <sub>[0.504, 0.998]</sub> | 0.073 <sub>[0.032, 0.119]</sub> |
| CausVid | matched | 10 | 15.230 <sub>[12.328, 17.661]</sub> | 21.502 <sub>[10.922, 35.090]</sub> | 0.946 <sub>[0.715, 1.189]</sub> | 0.902 <sub>[0.138, 2.190]</sub> | 0.887 <sub>[0.135, 2.171]</sub> | 1.042 <sub>[0.599, 1.625]</sub> | 0.059 <sub>[0.007, 0.136]</sub> |
| Wan2.1-I2V-14B-480P | native | 10 | 5.014 <sub>[0.870, 10.577]</sub> | 42.577 <sub>[7.358, 104.0]</sub> | 1.035 <sub>[0.772, 1.327]</sub> | 4.845 <sub>[0.348, 12.115]</sub> | 5.707 <sub>[0.429, 14.371]</sub> | 0.524 <sub>[0.380, 0.680]</sub> | 0.157 <sub>[0.057, 0.304]</sub> |
| Wan2.2-I2V-A14B | native | 10 | 6.308 <sub>[2.431, 11.364]</sub> | 50.584 <sub>[18.175, 104.7]</sub> | 0.948 <sub>[0.646, 1.290]</sub> | 9.079 <sub>[1.189, 23.797]</sub> | 9.819 <sub>[1.570, 25.314]</sub> | 0.496 <sub>[0.296, 0.723]</sub> | 0.262 <sub>[0.068, 0.484]</sub> |
| LTX-Video 13B-0.9.8-distilled | native | 10 | 6.646 <sub>[3.264, 10.438]</sub> | 53.448 <sub>[29.038, 80.013]</sub> | 0.899 <sub>[0.556, 1.299]</sub> | 3.677 <sub>[1.065, 7.773]</sub> | 3.945 <sub>[1.461, 7.928]</sub> | 0.388 <sub>[0.215, 0.592]</sub> | 0.185 <sub>[0.009, 0.434]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lccccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & NBF$\downarrow$ & FP$\uparrow$ & MCFF & DD\_raw & DLR$\downarrow$ & DAR$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 10 & 3.688 & 20.010 & 0.884 & 0.651 & 0.811 & 0.672 & 0.222 \\
Causal-Forcing++ (1-step) & matched & 10 & 5.279 & 22.863 & 0.663 & 0.508 & 0.662 & 0.661 & 0.243 \\
Causal-Forcing (framewise) & matched & 10 & 16.075 & 90.659 & 0.395 & 3.281 & 3.564 & 0.678 & 0.124 \\
Causal-Forcing++ (2-step, native nfpb=1) & native & 10 & 1.218 & 21.227 & 0.488 & 0.830 & 0.885 & 0.681 & 0.106 \\
Self-Forcing & matched & 10 & 9.665 & 11.484 & 0.649 & 0.330 & 0.346 & 0.737 & 0.073 \\
CausVid & matched & 10 & 15.230 & 21.502 & 0.946 & 0.902 & 0.887 & 1.042 & 0.059 \\
Wan2.1-I2V-14B-480P & native & 10 & 5.014 & 42.577 & 1.035 & 4.845 & 5.707 & 0.524 & 0.157 \\
Wan2.2-I2V-A14B & native & 10 & 6.308 & 50.584 & 0.948 & 9.079 & 9.819 & 0.496 & 0.262 \\
LTX-Video 13B-0.9.8-distilled & native & 10 & 6.646 & 53.448 & 0.899 & 3.677 & 3.945 & 0.388 & 0.185 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 5s}
\label{tab:i2v_snf_5s}
\end{table}
```
</details>

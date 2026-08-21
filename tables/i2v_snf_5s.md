# SNF-Bench core metrics — I2V @ 5s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | NBF↓ | MCFF-E | MCFF | FP↑ | DD_raw | DLR↓ | DAR↓ |
|---|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 10 | 3.688 <sub>[0.989, 7.558]</sub> | 10.005 <sub>[6.128, 14.329]</sub> | 1.057 <sub>[0.448, 1.888]</sub> | 0.607 <sub>[0.263, 1.085]</sub> | 0.778 <sub>[0.512, 1.049]</sub> | 0.811 <sub>[0.430, 1.286]</sub> | 0.672 <sub>[0.505, 0.838]</sub> | 0.319 <sub>[0.185, 0.446]</sub> |
| Causal-Forcing++ (1-step) | matched | 10 | 5.279 <sub>[1.451, 10.454]</sub> | 11.432 <sub>[7.363, 16.072]</sub> | 1.048 <sub>[0.418, 1.976]</sub> | 0.468 <sub>[0.264, 0.694]</sub> | 0.640 <sub>[0.479, 0.809]</sub> | 0.662 <sub>[0.388, 0.964]</sub> | 0.661 <sub>[0.521, 0.793]</sub> | 0.293 <sub>[0.221, 0.356]</sub> |
| Causal-Forcing (frame-wise) | matched | 10 | 16.075 <sub>[10.248, 22.518]</sub> | 45.329 <sub>[35.709, 55.047]</sub> | 8.475 <sub>[4.696, 13.593]</sub> | 2.793 <sub>[1.444, 4.397]</sub> | 0.433 <sub>[0.247, 0.639]</sub> | 3.564 <sub>[2.056, 5.296]</sub> | 0.678 <sub>[0.474, 0.892]</sub> | 0.294 <sub>[0.182, 0.430]</sub> |
| Causal-Forcing++ (2-step, frame-wise) | native | 10 | 1.218 <sub>[0.710, 1.794]</sub> | 10.614 <sub>[4.695, 18.260]</sub> | 2.228 <sub>[0.804, 4.289]</sub> | 0.781 <sub>[0.308, 1.533]</sub> | 0.467 <sub>[0.275, 0.709]</sub> | 0.885 <sub>[0.396, 1.638]</sub> | 0.681 <sub>[0.520, 0.844]</sub> | 0.200 <sub>[0.112, 0.300]</sub> |
| Self-Forcing | matched | 10 | 9.665 <sub>[4.677, 14.978]</sub> | 5.742 <sub>[4.042, 7.724]</sub> | 0.686 <sub>[0.304, 1.163]</sub> | 0.263 <sub>[0.128, 0.422]</sub> | 0.696 <sub>[0.404, 1.043]</sub> | 0.346 <sub>[0.170, 0.556]</sub> | 0.737 <sub>[0.504, 0.998]</sub> | 0.214 <sub>[0.155, 0.279]</sub> |
| CausVid | matched | 10 | 15.230 <sub>[12.328, 17.661]</sub> | 10.751 <sub>[5.461, 17.545]</sub> | 0.761 <sub>[0.165, 1.642]</sub> | 0.871 <sub>[0.149, 2.145]</sub> | 0.977 <sub>[0.747, 1.241]</sub> | 0.887 <sub>[0.135, 2.171]</sub> | 1.042 <sub>[0.599, 1.625]</sub> | 0.096 <sub>[0.019, 0.185]</sub> |
| Wan2.1-I2V-14B-480P | native | 10 | 5.014 <sub>[0.870, 10.577]</sub> | 21.289 <sub>[3.679, 52.009]</sub> | 6.666 <sub>[0.357, 18.364]</sub> | 5.575 <sub>[0.312, 14.175]</sub> | 1.089 <sub>[0.808, 1.398]</sub> | 5.707 <sub>[0.429, 14.371]</sub> | 0.524 <sub>[0.380, 0.680]</sub> | 0.179 <sub>[0.051, 0.337]</sub> |
| Wan2.2-I2V-A14B | native | 10 | 6.308 <sub>[2.431, 11.364]</sub> | 25.292 <sub>[9.088, 52.371]</sub> | 4.326 <sub>[1.470, 8.815]</sub> | 9.092 <sub>[1.134, 23.979]</sub> | 0.953 <sub>[0.641, 1.303]</sub> | 9.819 <sub>[1.570, 25.314]</sub> | 0.496 <sub>[0.296, 0.723]</sub> | 0.275 <sub>[0.086, 0.489]</sub> |
| LTX-Video 13B-0.9.8-distilled | native | 10 | 6.646 <sub>[3.264, 10.438]</sub> | 17.816 <sub>[9.679, 26.671]</sub> | 3.595 <sub>[0.999, 7.446]</sub> | 3.477 <sub>[0.986, 7.543]</sub> | 0.915 <sub>[0.578, 1.308]</sub> | 3.945 <sub>[1.461, 7.928]</sub> | 0.388 <sub>[0.215, 0.592]</sub> | 0.240 <sub>[0.063, 0.463]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & NBF$\downarrow$ & MCFF-E & MCFF & FP$\uparrow$ & DD\_raw & DLR$\downarrow$ & DAR$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 10 & 3.688 & 10.005 & 1.057 & 0.607 & 0.778 & 0.811 & 0.672 & 0.319 \\
Causal-Forcing++ (1-step) & matched & 10 & 5.279 & 11.432 & 1.048 & 0.468 & 0.640 & 0.662 & 0.661 & 0.293 \\
Causal-Forcing (frame-wise) & matched & 10 & 16.075 & 45.329 & 8.475 & 2.793 & 0.433 & 3.564 & 0.678 & 0.294 \\
Causal-Forcing++ (2-step, frame-wise) & native & 10 & 1.218 & 10.614 & 2.228 & 0.781 & 0.467 & 0.885 & 0.681 & 0.200 \\
Self-Forcing & matched & 10 & 9.665 & 5.742 & 0.686 & 0.263 & 0.696 & 0.346 & 0.737 & 0.214 \\
CausVid & matched & 10 & 15.230 & 10.751 & 0.761 & 0.871 & 0.977 & 0.887 & 1.042 & 0.096 \\
Wan2.1-I2V-14B-480P & native & 10 & 5.014 & 21.289 & 6.666 & 5.575 & 1.089 & 5.707 & 0.524 & 0.179 \\
Wan2.2-I2V-A14B & native & 10 & 6.308 & 25.292 & 4.326 & 9.092 & 0.953 & 9.819 & 0.496 & 0.275 \\
LTX-Video 13B-0.9.8-distilled & native & 10 & 6.646 & 17.816 & 3.595 & 3.477 & 0.915 & 3.945 & 0.388 & 0.240 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 5s}
\label{tab:i2v_snf_5s}
\end{table}
```
</details>

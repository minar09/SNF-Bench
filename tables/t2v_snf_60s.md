# SNF-Bench core metrics — T2V @ 60s

All seven systems are **public external models run under their own native configuration** (Setting A). Our own systems are excluded by construction — see `docs/EXCLUSIONS.md`.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | NBF↓ | MCFF-E | MCFF | FP↑ | DD_raw | DLR↓ | DAR↓ |
|---|---|---|---|---|---|---|---|---|---|---|
| CausVid | native | 23 | 8.076 <sub>[5.099, 11.402]</sub> | 9.272 <sub>[5.433, 13.711]</sub> | 2.873 <sub>[1.378, 4.670]</sub> | 1.960 <sub>[0.776, 3.444]</sub> | 0.672 <sub>[0.496, 0.858]</sub> | 2.285 <sub>[0.944, 3.986]</sub> | 0.454 <sub>[0.343, 0.608]</sub> | 0.142 <sub>[0.094, 0.204]</sub> |
| Self-Forcing | native | 23 | 11.370 <sub>[7.903, 15.161]</sub> | 12.724 <sub>[9.089, 17.023]</sub> | 10.359 <sub>[6.411, 15.048]</sub> | 2.538 <sub>[1.325, 4.124]</sub> | 0.443 <sub>[0.242, 0.691]</sub> | 2.564 <sub>[1.362, 4.157]</sub> | 0.504 <sub>[0.325, 0.711]</sub> | 0.136 <sub>[0.053, 0.236]</sub> |
| Infinite-Forcing | native | 23 | 7.748 <sub>[4.158, 11.833]</sub> | 3.649 <sub>[2.794, 4.561]</sub> | 1.174 <sub>[0.562, 2.103]</sub> | 0.285 <sub>[0.198, 0.381]</sub> | 0.634 <sub>[0.426, 0.872]</sub> | 0.304 <sub>[0.221, 0.395]</sub> | 0.551 <sub>[0.445, 0.661]</sub> | 0.139 <sub>[0.086, 0.196]</sub> |
| Rolling-Forcing | native | 23 | 16.769 <sub>[13.135, 20.508]</sub> | 11.231 <sub>[8.733, 14.137]</sub> | 3.180 <sub>[1.671, 5.215]</sub> | 1.574 <sub>[0.789, 2.558]</sub> | 0.749 <sub>[0.472, 1.048]</sub> | 1.754 <sub>[0.918, 2.833]</sub> | 0.540 <sub>[0.425, 0.659]</sub> | 0.183 <sub>[0.112, 0.261]</sub> |
| Reward-Forcing | native | 23 | 14.847 <sub>[11.036, 18.451]</sub> | 8.510 <sub>[6.001, 11.576]</sub> | 3.806 <sub>[1.971, 6.355]</sub> | 0.796 <sub>[0.531, 1.135]</sub> | 0.491 <sub>[0.328, 0.683]</sub> | 0.913 <sub>[0.636, 1.242]</sub> | 0.599 <sub>[0.470, 0.729]</sub> | 0.173 <sub>[0.109, 0.244]</sub> |
| LongLive | native | 23 | 15.939 <sub>[12.976, 18.762]</sub> | 13.865 <sub>[9.533, 19.049]</sub> | 6.462 <sub>[3.240, 10.457]</sub> | 2.407 <sub>[0.885, 4.851]</sub> | 0.754 <sub>[0.476, 1.041]</sub> | 2.501 <sub>[0.986, 4.920]</sub> | 0.590 <sub>[0.463, 0.720]</sub> | 0.171 <sub>[0.099, 0.250]</sub> |
| Causal-Forcing | native | 23 | 22.437 <sub>[20.007, 24.529]</sub> | 87.624 <sub>[68.827, 106.0]</sub> | 9.838 <sub>[6.793, 13.059]</sub> | 7.213 <sub>[3.684, 12.020]</sub> | 0.834 <sub>[0.533, 1.156]</sub> | 10.757 <sub>[7.136, 15.417]</sub> | 0.940 <sub>[0.755, 1.161]</sub> | 0.427 <sub>[0.292, 0.559]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & NBF$\downarrow$ & MCFF-E & MCFF & FP$\uparrow$ & DD\_raw & DLR$\downarrow$ & DAR$\downarrow$ \\
\midrule
CausVid & native & 23 & 8.076 & 9.272 & 2.873 & 1.960 & 0.672 & 2.285 & 0.454 & 0.142 \\
Self-Forcing & native & 23 & 11.370 & 12.724 & 10.359 & 2.538 & 0.443 & 2.564 & 0.504 & 0.136 \\
Infinite-Forcing & native & 23 & 7.748 & 3.649 & 1.174 & 0.285 & 0.634 & 0.304 & 0.551 & 0.139 \\
Rolling-Forcing & native & 23 & 16.769 & 11.231 & 3.180 & 1.574 & 0.749 & 1.754 & 0.540 & 0.183 \\
Reward-Forcing & native & 23 & 14.847 & 8.510 & 3.806 & 0.796 & 0.491 & 0.913 & 0.599 & 0.173 \\
LongLive & native & 23 & 15.939 & 13.865 & 6.462 & 2.407 & 0.754 & 2.501 & 0.590 & 0.171 \\
Causal-Forcing & native & 23 & 22.437 & 87.624 & 9.838 & 7.213 & 0.834 & 10.757 & 0.940 & 0.427 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — T2V @ 60s}
\label{tab:t2v_snf_60s}
\end{table}
```
</details>

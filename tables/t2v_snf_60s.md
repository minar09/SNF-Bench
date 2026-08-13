# SNF-Bench core metrics — T2V @ 60s

All seven systems are **public external models run under their own native configuration** (Setting A). Our own systems are excluded by construction — see `docs/EXCLUSIONS.md`.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | BFR/NBF↓ | FP↑ | MCFF | DD_raw | DriftFrac↓ |
|---|---|---|---|---|---|---|---|---|
| CausVid | native | 23 | 8.136 <sub>[5.136, 11.489]</sub> | 1.161 <sub>[0.681, 1.715]</sub> | 0.670 <sub>[0.489, 0.867]</sub> | 2.279 <sub>[0.943, 3.972]</sub> | 2.285 <sub>[0.944, 3.986]</sub> | 0.454 <sub>[0.343, 0.608]</sub> |
| Self-Forcing | native | 23 | 11.516 <sub>[8.020, 15.331]</sub> | 1.587 <sub>[1.133, 2.124]</sub> | 0.439 <sub>[0.239, 0.687]</sub> | 2.524 <sub>[1.317, 4.121]</sub> | 2.560 <sub>[1.361, 4.152]</sub> | 0.504 <sub>[0.325, 0.711]</sub> |
| Infinite-Forcing | native | 23 | 7.720 <sub>[4.145, 11.800]</sub> | 0.456 <sub>[0.349, 0.569]</sub> | 0.624 <sub>[0.410, 0.867]</sub> | 0.286 <sub>[0.202, 0.379]</sub> | 0.304 <sub>[0.221, 0.395]</sub> | 0.550 <sub>[0.445, 0.660]</sub> |
| Rolling-Forcing | native | 23 | 16.907 <sub>[13.155, 20.712]</sub> | 1.405 <sub>[1.092, 1.769]</sub> | 0.740 <sub>[0.469, 1.034]</sub> | 1.538 <sub>[0.847, 2.387]</sub> | 1.752 <sub>[0.917, 2.831]</sub> | 0.540 <sub>[0.426, 0.660]</sub> |
| Reward-Forcing | native | 23 | 14.974 <sub>[11.178, 18.599]</sub> | 1.066 <sub>[0.750, 1.455]</sub> | 0.502 <sub>[0.331, 0.698]</sub> | 0.875 <sub>[0.590, 1.216]</sub> | 0.913 <sub>[0.636, 1.243]</sub> | 0.598 <sub>[0.469, 0.727]</sub> |
| LongLive | native | 23 | 15.723 <sub>[12.803, 18.560]</sub> | 1.734 <sub>[1.191, 2.383]</sub> | 0.766 <sub>[0.485, 1.055]</sub> | 2.440 <sub>[0.914, 4.883]</sub> | 2.500 <sub>[0.986, 4.915]</sub> | 0.589 <sub>[0.463, 0.720]</sub> |
| Causal-Forcing | native | 23 | 22.805 <sub>[20.254, 25.050]</sub> | 10.955 <sub>[8.605, 13.256]</sub> | 0.782 <sub>[0.495, 1.084]</sub> | 6.893 <sub>[3.557, 11.460]</sub> | 10.753 <sub>[7.130, 15.412]</sub> | 0.939 <sub>[0.755, 1.160]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & BFR/NBF$\downarrow$ & FP$\uparrow$ & MCFF & DD\_raw & DriftFrac$\downarrow$ \\
\midrule
CausVid & native & 23 & 8.136 & 1.161 & 0.670 & 2.279 & 2.285 & 0.454 \\
Self-Forcing & native & 23 & 11.516 & 1.587 & 0.439 & 2.524 & 2.560 & 0.504 \\
Infinite-Forcing & native & 23 & 7.720 & 0.456 & 0.624 & 0.286 & 0.304 & 0.550 \\
Rolling-Forcing & native & 23 & 16.907 & 1.405 & 0.740 & 1.538 & 1.752 & 0.540 \\
Reward-Forcing & native & 23 & 14.974 & 1.066 & 0.502 & 0.875 & 0.913 & 0.598 \\
LongLive & native & 23 & 15.723 & 1.734 & 0.766 & 2.440 & 2.500 & 0.589 \\
Causal-Forcing & native & 23 & 22.805 & 10.955 & 0.782 & 6.893 & 10.753 & 0.939 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — T2V @ 60s}
\label{tab:t2v_snf_60s}
\end{table}
```
</details>

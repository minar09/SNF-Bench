# SNF-Bench core metrics — I2V @ 240s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | BFR/NBF↓ | FP↑ | MCFF | DD_raw | DriftFrac↓ |
|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 5 | 10.388 <sub>[3.765, 17.438]</sub> | 0.603 <sub>[0.423, 0.874]</sub> | 1.028 <sub>[0.728, 1.328]</sub> | 0.631 <sub>[0.243, 1.211]</sub> | 0.680 <sub>[0.269, 1.298]</sub> | 0.551 <sub>[0.367, 0.734]</sub> |
| Causal-Forcing++ (1-step) | matched | 1 | 0.976 <sub>[--, --]</sub> | 0.448 <sub>[--, --]</sub> | 0.389 <sub>[--, --]</sub> | 0.115 <sub>[--, --]</sub> | 0.193 <sub>[--, --]</sub> | 0.856 <sub>[--, --]</sub> |
| Causal-Forcing (framewise) | matched | 5 | 19.833 <sub>[16.364, 23.456]</sub> | 3.931 <sub>[1.850, 6.235]</sub> | 0.757 <sub>[0.695, 0.804]</sub> | 2.862 <sub>[0.462, 5.682]</sub> | 3.457 <sub>[0.999, 6.499]</sub> | 0.686 <sub>[0.490, 0.886]</sub> |
| Causal-Forcing++ (2-step, native nfpb=1) | native | 5 | 6.323 <sub>[1.385, 12.933]</sub> | 0.493 <sub>[0.221, 0.805]</sub> | 0.665 <sub>[0.180, 1.346]</sub> | 0.688 <sub>[0.093, 1.331]</sub> | 0.681 <sub>[0.092, 1.311]</sub> | 0.834 <sub>[0.340, 1.602]</sub> |
| Self-Forcing | matched | 5 | 22.280 <sub>[16.805, 26.226]</sub> | 0.717 <sub>[0.471, 0.967]</sub> | 0.794 <sub>[0.394, 1.302]</sub> | 1.655 <sub>[0.260, 3.415]</sub> | 1.671 <sub>[0.278, 3.395]</sub> | 0.712 <sub>[0.259, 1.305]</sub> |
| CausVid | matched | 5 | 18.397 <sub>[12.850, 23.238]</sub> | 0.260 <sub>[0.168, 0.359]</sub> | 0.831 <sub>[0.656, 0.975]</sub> | 0.825 <sub>[0.100, 1.725]</sub> | 0.838 <sub>[0.112, 1.733]</sub> | 0.435 <sub>[0.160, 0.710]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & BFR/NBF$\downarrow$ & FP$\uparrow$ & MCFF & DD\_raw & DriftFrac$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 5 & 10.388 & 0.603 & 1.028 & 0.631 & 0.680 & 0.551 \\
Causal-Forcing++ (1-step) & matched & 1 & 0.976 & 0.448 & 0.389 & 0.115 & 0.193 & 0.856 \\
Causal-Forcing (framewise) & matched & 5 & 19.833 & 3.931 & 0.757 & 2.862 & 3.457 & 0.686 \\
Causal-Forcing++ (2-step, native nfpb=1) & native & 5 & 6.323 & 0.493 & 0.665 & 0.688 & 0.681 & 0.834 \\
Self-Forcing & matched & 5 & 22.280 & 0.717 & 0.794 & 1.655 & 1.671 & 0.712 \\
CausVid & matched & 5 & 18.397 & 0.260 & 0.831 & 0.825 & 0.838 & 0.435 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 240s}
\label{tab:i2v_snf_240s}
\end{table}
```
</details>

# SNF-Bench core metrics — I2V @ 240s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | NBF↓ | MCFF-E | MCFF | FP↑ | DD_raw | DLR↓ | DAR↓ |
|---|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 5 | 10.388 <sub>[3.765, 17.438]</sub> | 4.826 <sub>[3.388, 6.990]</sub> | -- | 0.631 <sub>[0.243, 1.211]</sub> | 1.028 <sub>[0.728, 1.328]</sub> | 0.680 <sub>[0.269, 1.298]</sub> | 0.551 <sub>[0.367, 0.734]</sub> | 0.087 <sub>[0.062, 0.118]</sub> |
| Causal-Forcing++ (1-step) | matched | 5 | 6.417 <sub>[1.860, 11.982]</sub> | 6.658 <sub>[4.380, 9.704]</sub> | 0.563 <sub>[0.282, 0.936]</sub> | 0.511 <sub>[0.197, 0.927]</sub> | 0.830 <sub>[0.601, 1.014]</sub> | 0.676 <sub>[0.309, 1.176]</sub> | 0.674 <sub>[0.492, 0.857]</sub> | 0.302 <sub>[0.212, 0.405]</sub> |
| Causal-Forcing (frame-wise) | matched | 5 | 19.833 <sub>[16.364, 23.456]</sub> | 31.451 <sub>[14.797, 49.884]</sub> | -- | 2.862 <sub>[0.462, 5.682]</sub> | 0.757 <sub>[0.695, 0.804]</sub> | 3.457 <sub>[0.999, 6.499]</sub> | 0.686 <sub>[0.490, 0.886]</sub> | 0.328 <sub>[0.107, 0.549]</sub> |
| Causal-Forcing++ (2-step, frame-wise) | native | 5 | 6.323 <sub>[1.385, 12.933]</sub> | 3.946 <sub>[1.770, 6.442]</sub> | -- | 0.688 <sub>[0.093, 1.331]</sub> | 0.665 <sub>[0.180, 1.346]</sub> | 0.681 <sub>[0.092, 1.311]</sub> | 0.834 <sub>[0.340, 1.602]</sub> | 0.013 <sub>[0.000, 0.027]</sub> |
| Self-Forcing | matched | 5 | 22.280 <sub>[16.805, 26.226]</sub> | 5.735 <sub>[3.768, 7.739]</sub> | -- | 1.655 <sub>[0.260, 3.415]</sub> | 0.794 <sub>[0.394, 1.302]</sub> | 1.671 <sub>[0.278, 3.395]</sub> | 0.712 <sub>[0.259, 1.305]</sub> | 0.050 <sub>[0.004, 0.102]</sub> |
| CausVid | matched | 5 | 18.397 <sub>[12.850, 23.238]</sub> | 2.081 <sub>[1.344, 2.869]</sub> | -- | 0.825 <sub>[0.100, 1.725]</sub> | 0.831 <sub>[0.656, 0.975]</sub> | 0.838 <sub>[0.112, 1.733]</sub> | 0.435 <sub>[0.160, 0.710]</sub> | 0.073 <sub>[0.018, 0.128]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & NBF$\downarrow$ & MCFF-E & MCFF & FP$\uparrow$ & DD\_raw & DLR$\downarrow$ & DAR$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 5 & 10.388 & 4.826 & -- & 0.631 & 1.028 & 0.680 & 0.551 & 0.087 \\
Causal-Forcing++ (1-step) & matched & 5 & 6.417 & 6.658 & 0.563 & 0.511 & 0.830 & 0.676 & 0.674 & 0.302 \\
Causal-Forcing (frame-wise) & matched & 5 & 19.833 & 31.451 & -- & 2.862 & 0.757 & 3.457 & 0.686 & 0.328 \\
Causal-Forcing++ (2-step, frame-wise) & native & 5 & 6.323 & 3.946 & -- & 0.688 & 0.665 & 0.681 & 0.834 & 0.013 \\
Self-Forcing & matched & 5 & 22.280 & 5.735 & -- & 1.655 & 0.794 & 1.671 & 0.712 & 0.050 \\
CausVid & matched & 5 & 18.397 & 2.081 & -- & 0.825 & 0.831 & 0.838 & 0.435 & 0.073 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 240s}
\label{tab:i2v_snf_240s}
\end{table}
```
</details>

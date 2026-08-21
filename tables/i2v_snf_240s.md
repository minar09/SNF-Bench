# SNF-Bench core metrics — I2V @ 240s

**Read the `setting` column.** Entries marked `matched` were run in a common long-horizon I2V wrapper, *not* their authors' configuration; they are a stress-test result, not a native-capability ranking.

Cell format: `mean [bootstrap 95% CI]`, prompt-level, 10k resamples, seed 0.

| Method | setting | n | fBD↓ | NBF↓ | MCFF-E | MCFF | FP↑ | DD_raw | DLR↓ | DAR↓ |
|---|---|---|---|---|---|---|---|---|---|---|
| Causal-Forcing++ (2-step) | matched | 5 | 10.388 <sub>[3.765, 17.438]</sub> | 4.826 <sub>[3.388, 6.990]</sub> | 0.529 <sub>[0.248, 0.888]</sub> | 0.593 <sub>[0.219, 1.145]</sub> | 1.052 <sub>[0.747, 1.358]</sub> | 0.680 <sub>[0.269, 1.298]</sub> | 0.551 <sub>[0.367, 0.734]</sub> | 0.154 <sub>[0.112, 0.201]</sub> |
| Causal-Forcing++ (1-step) | matched | 5 | 6.417 <sub>[1.860, 11.982]</sub> | 6.658 <sub>[4.380, 9.704]</sub> | 0.563 <sub>[0.282, 0.936]</sub> | 0.511 <sub>[0.197, 0.927]</sub> | 0.830 <sub>[0.601, 1.014]</sub> | 0.676 <sub>[0.309, 1.176]</sub> | 0.674 <sub>[0.492, 0.857]</sub> | 0.302 <sub>[0.212, 0.405]</sub> |
| Causal-Forcing (frame-wise) | matched | 5 | 19.833 <sub>[16.364, 23.456]</sub> | 31.451 <sub>[14.797, 49.884]</sub> | 3.081 <sub>[0.550, 6.434]</sub> | 2.277 <sub>[0.399, 4.807]</sub> | 0.737 <sub>[0.700, 0.777]</sub> | 3.457 <sub>[0.999, 6.499]</sub> | 0.686 <sub>[0.490, 0.886]</sub> | 0.451 <sub>[0.266, 0.635]</sub> |
| Causal-Forcing++ (2-step, frame-wise) | native | 5 | 6.323 <sub>[1.385, 12.933]</sub> | 3.946 <sub>[1.770, 6.442]</sub> | 1.228 <sub>[0.433, 2.375]</sub> | 0.683 <sub>[0.103, 1.301]</sub> | 0.673 <sub>[0.201, 1.346]</sub> | 0.681 <sub>[0.092, 1.311]</sub> | 0.834 <sub>[0.340, 1.602]</sub> | 0.020 <sub>[0.002, 0.043]</sub> |
| Self-Forcing | matched | 5 | 22.280 <sub>[16.805, 26.226]</sub> | 5.735 <sub>[3.768, 7.739]</sub> | 1.483 <sub>[0.664, 2.302]</sub> | 1.590 <sub>[0.269, 3.272]</sub> | 0.809 <sub>[0.421, 1.290]</sub> | 1.671 <sub>[0.278, 3.395]</sub> | 0.712 <sub>[0.259, 1.305]</sub> | 0.084 <sub>[0.026, 0.141]</sub> |
| CausVid | matched | 5 | 18.397 <sub>[12.850, 23.238]</sub> | 2.081 <sub>[1.344, 2.869]</sub> | 0.807 <sub>[0.123, 1.569]</sub> | 0.790 <sub>[0.096, 1.652]</sub> | 0.863 <sub>[0.691, 1.016]</sub> | 0.838 <sub>[0.112, 1.733]</sub> | 0.435 <sub>[0.160, 0.710]</sub> | 0.106 <sub>[0.061, 0.159]</sub> |

<details><summary>LaTeX (point estimates)</summary>

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccccccccc}
\toprule
Method & setting & n & fBD$\downarrow$ & NBF$\downarrow$ & MCFF-E & MCFF & FP$\uparrow$ & DD\_raw & DLR$\downarrow$ & DAR$\downarrow$ \\
\midrule
Causal-Forcing++ (2-step) & matched & 5 & 10.388 & 4.826 & 0.529 & 0.593 & 1.052 & 0.680 & 0.551 & 0.154 \\
Causal-Forcing++ (1-step) & matched & 5 & 6.417 & 6.658 & 0.563 & 0.511 & 0.830 & 0.676 & 0.674 & 0.302 \\
Causal-Forcing (frame-wise) & matched & 5 & 19.833 & 31.451 & 3.081 & 2.277 & 0.737 & 3.457 & 0.686 & 0.451 \\
Causal-Forcing++ (2-step, frame-wise) & native & 5 & 6.323 & 3.946 & 1.228 & 0.683 & 0.673 & 0.681 & 0.834 & 0.020 \\
Self-Forcing & matched & 5 & 22.280 & 5.735 & 1.483 & 1.590 & 0.809 & 1.671 & 0.712 & 0.084 \\
CausVid & matched & 5 & 18.397 & 2.081 & 0.807 & 0.790 & 0.863 & 0.838 & 0.435 & 0.106 \\
\bottomrule
\end{tabular}
\caption{SNF-Bench core metrics — I2V @ 240s}
\label{tab:i2v_snf_240s}
\end{table}
```
</details>

# SNF-Bench v2 intervention matrix

Status: pre-run design for later v2 diagnostics, 2026-09-28. It records expected
*responses* separately from task *desirability*. It does not assert that a
metric currently passes. Existing v1.1 metrics retain their frozen definitions.
The 24-frame/five-medium VBench pilot in `manifest/` is exploratory and must
not set thresholds for the final study.

## Reading the matrix

- `↑` / `↓`: expected measurement response as corruption strength grows.
- `≈`: target invariance; report a measured tolerance, never assume exact zero.
- `?`: no defensible monotone expectation; report without an admission claim.
- `n/a`: the diagnostic is not defined for that prompt class.
- **Task penalty** means a fixed-camera natural-flow evaluator should mark the
  clip worse. A metric may respond but move in its own *rewarding* direction.

Every test is paired to an untouched parent clip. Report baseline, each
severity, paired effect size, uncertainty, and failure/abstention count.

| Intervention | Task judgment | Existing-factor response to test | New diagnostic response to test | Incumbent response / interpretation |
| --- | --- | --- | --- | --- |
| Progressive whole-frame translation, rotation, scale | Penalty: fixed support moves | fBD ↑; NBF ↑; MCFF after compensation ≈; DLR may ↑; DAR estimator-dependent | Long-baseline support displacement ↑; signed transport measured only after support check | VBench DD may ↑, which rewards motion; VBench BC should ideally ↓, but must be measured |
| Late dynamic-only attenuation or freeze | Penalty: flow stops | MCFF-L ↓ and FP ↓; fBD ideally ≈; DLR may ↑ from a shrinking denominator | Flow coverage and late transport ↓ | DD ↓; BC may ↑ because frames become similar; response and desirability differ |
| Wrong-way dynamic motion with support untouched | Penalty only on direction-eligible prompts | Magnitude metrics may remain ≈; no existing SNF direction claim | Signed transport ↓ or wrong-way fraction ↑ | General motion and consistency may remain strong |
| Ping-pong dynamic motion with sustained magnitude | Penalty on one-way transport prompts; n/a for surf and other permitted cycles | MCFF/FP may remain ≈ | Net/absolute transport ratio ↓; reversal count ↑ | DD and BC may still score well |
| Exact dynamic-region short loop; optional reset seam | Penalty even if per-frame motion remains strong | MCFF/FP may remain ≈ | Long-lag replay ↑; seam detector ↑ when a seam exists | Smoothness can remain strong; BC may reward repetition |
| Natural waves, eddies, flame flicker | No penalty for permitted periodic/turbulent motion | No expected monotone change | Replay false-positive rate must stay low; one-way ratio n/a | Controls the loop detector's specificity |
| Foreground expansion from incoming material, support fixed | Reward if prompt requests incoming flow | Existing magnitude metrics are contextual only | Source-to-near-boundary crossing ↑, foreground expansion with stable support | Whole-frame motion alone cannot establish approach |
| Whole-frame zoom imitating incoming flow | Penalty: camera moves | fBD/NBF ↑ | Support check fails, so incoming-flow credit is withheld | DD may rise; BC response empirical |
| Moving fog substituted for river or rain | Penalty: wrong medium | Some spatial/flow metrics may pass | Semantic medium check fails; plausibility judged separately | Prompt-alignment comparator should detect the mismatch |
| Brightness/color ramp without geometry change | Nuisance, not a motion failure | Geometric/flow factors ideally ≈, but estimator sensitivity is measured | Transport/replay ideally ≈ | BC may move; report operating limit |
| Mask erosion, dilation, label swap; video unchanged | Nuisance to the evaluator | Report score/rank sensitivity, particularly NBF/DAR | Report coverage and abstention changes | Incumbents without masks are a useful control |
| Inward versus outward boundary crossing with matched magnitude | Correct versus wrong source/destination behavior | Magnitude factors may remain ≈ | Incoming flux changes sign | Whole-frame motion can remain matched |
| Texture swelling without a boundary crossing | Local appearance confound for incoming flow | Support should remain ≈ | Boundary flux should remain near zero | Source-image/background similarity may change |
| Recolored exact loop | Replay with weakened pixel identity | Persistence/magnitude may remain ≈ | Feature/flow recurrence should still respond; pixel-only recurrence may fail | Tests representation dependence |
| One catastrophic late interval versus mild distributed errors, matched mean | Same mean, different long-horizon reliability | Final mean deliberately matched | Worst window and time-to-failure separate cases | VBench-Long aggregate is the direct comparator |

## Admission and reporting

No new diagnostic enters the headline set because it performs well on one
synthetic family. Before threshold selection, designate scene-family and model
holdouts. Set the decision threshold using development corruptions and real
fixed-camera footage, then report held-out detection at a fixed real-footage
false-positive rate, category spread, and unscorable fraction. Validate the
axis against blind human judgments on real generations and adversarial
examples. A diagnostic that cannot beat a simple task-specific baseline, or
that mislabels legitimate periodic flow, remains exploratory.

For existing factors, test selectivity against **all** off-target families,
including photometric and partition changes. Report response sign and reward
sign in separate columns in the paper. Do not compare unstandardized
multipliers across metrics. Keep the full family-by-factor response table and
small-sample confidence intervals available as artifacts.

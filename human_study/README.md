# SNF-Bench axis-specific human study

A deliberately small, deliberately narrow study. It is **not** a preference
study, and it does not ask which video is better. The whole point of the
benchmark is that "better" conflates two opposite failures, so a preference
study would reintroduce the confound the benchmark exists to remove.

## What it measures

Two forced-choice questions, one per failure axis:

| axis | question put to the rater | compared against |
|---|---|---|
| `drift` | Which video's **background** moves more? | fBD, NBF |
| `decay` | In which video does the **moving content** slow down or stop more? | MCFF-L, FP |

The result is a single agreement rate per axis: how often a human's ordering of
a pair matches the factor's ordering of the same pair. That is the evidence the
factors track something a person also perceives. It is not a claim that the
factors are perceptual quality measures, and the paper does not make one.

## Size

- **24 trials** (12 per axis), about 8 minutes per rater
- **3 raters**, so each trial gets three independent judgements
- Ties are allowed and expected. Forcing a choice on an indistinguishable pair
  manufactures noise and depresses the agreement rate for the wrong reason.

## Why these pairs

`scripts/make_human_study.py` selects them by rule, not by eye. For each axis it
bins candidate pairs by the *relative gap* in the relevant factor and samples
across three bands (0.05–0.20, 0.20–0.50, 0.50–1.00). Agreement is therefore
measured across the whole operating range rather than only on obvious extremes,
where any metric would look good.

Each trial records the factor's own verdict (`metric_says`) but never shows it
to the rater.

## Controls

- Trial order is randomised per rater.
- Left/right presentation is randomised per trial, and the recorded choice is
  resolved back to a system key server-side. A rater who starts answering by
  position rather than by content cannot bias the result systematically.
- System names are never shown.
- Raters see the final-window excerpt (last 10–15 s of each rollout), because
  both failures are defined on the late window.

## Running it

1. `~/miniconda3/envs/snfeval/bin/python scripts/make_human_study.py`
   → writes `pairs.json` and `TRIALS.gs`.
2. Cut the final-window excerpts for every clip referenced in `pairs.json` and
   upload them; fill the `videoA`/`videoB` URLs in `TRIALS.gs`.
3. Create an Apps Script project, add `code.gs` and `index.html`, paste
   `TRIALS.gs` into `code.gs` where marked, set `SPREADSHEET_ID`.
4. Deploy as a web app and send the link to the raters.
5. Export the `responses` sheet and score it with
   `scripts/score_human_study.py`.

## Reporting

Report per axis: agreement rate with its binomial confidence interval,
inter-rater agreement, and the tie rate. Report agreement **as a function of
metric gap** as well as pooled — a factor that agrees with people only on large
gaps is a different, and weaker, result than one that agrees throughout, and
pooling hides the difference.

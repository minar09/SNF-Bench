# SNF-Bench axis-specific human study

A deliberately small, deliberately narrow study. It is **not** a preference
study and it never asks which clip is better. The benchmark exists because
"better" conflates two opposite failures, so a preference study would
reintroduce the very confound the benchmark removes.

## What it measures

One question per trial, about one failure axis:

| axis | question put to the rater | compared against |
|---|---|---|
| `drift` | Which clip's **background** moves more? | NBF, fBD |
| `decay` | In which clip does the **moving content** slow or stop more? | MCFF-L, FP |

The result is an agreement rate per axis: how often a rater's ordering of a
pair matches the factor's ordering of the same pair. That is evidence the
factors track something a person also perceives. It is not a claim that they
are perceptual quality measures, and the paper makes no such claim.

## Media: existing assets, reused as-is

Clips are the image-conditioned 60 s rollouts already hosted on Drive for an
earlier study. `scenes_public.json` holds those URLs **verbatim**; nothing in
this pipeline rewrites them, and `make_human_study.py` only reads the file.
There is nothing to upload.

Because every clip in a pair starts from the **same source image**, which the
app shows above the players, divergence is attributable to the system rather
than to a differently imagined scene. That is why this study runs on the
image-conditioned track.

Eight scenes × three systems = 24 clips. Only the three publicly released
systems from that asset set are used; the internal ablations that shared the
same scenes are excluded by the benchmark's roster rule, and
`make_human_study.py` filters them out by construction.

## Size

- **20 trials**: 9 per axis plus 2 sentinels, about 8 minutes per rater
- **3 raters**, so each trial gets three independent judgements
- Ties are allowed and expected. Forcing a choice on an indistinguishable pair
  manufactures noise and depresses the agreement rate for the wrong reason.

## Controls

- **Sentinels.** Two trials show one clip against *itself*, where the only
  correct answer is "about the same". A rater who picks a side is not
  attending; the row is flagged (`failedSentinel`) rather than dropped
  silently.
- Trial order is randomised per rater; left/right side is randomised per trial
  and resolved back to a system key server-side, so a rater who starts
  answering by position cannot bias the result systematically.
- System names are never sent to the client — the app labels clips only
  "Video 1" and "Video 2".
- Each trial records dwell time and an optional playback-problem report, so a
  clip that failed to load is distinguishable from a genuine judgement.

## Why these pairs

`scripts/make_human_study.py` selects them by rule, not by eye: for each axis it
bins candidate pairs by the *relative gap* in the relevant factor and samples
across the range. Agreement is therefore measured across the whole operating
range rather than only on obvious extremes, where any metric would look good.
Each trial records the factor's own verdict in `pairs.json`, which stays
server-side and is never shown to a rater.

## Running it

1. `~/miniconda3/envs/snfeval/bin/python scripts/make_human_study.py`
   → writes `pairs.json` and `SCENES.gs`.
2. Create an Apps Script project and add three files: `code.gs`, `SCENES.gs`,
   and `index.html` (as an HTML file named `index`).
3. Set `CONFIG.SPREADSHEET_ID` if you want a different workbook. The default
   writes to its own tabs (`snf_responses`, `snf_summary`), so it never mixes
   with another study's sheet.
4. Run `validateStudyConfig()` once. It checks that every trial resolves to a
   scene with both clips present and reports problems by trial id — find a
   broken URL now, not from a rater.
5. Deploy as a web app (execute as yourself, access to anyone with the link)
   and send the link to the raters.
6. Export the `snf_responses` sheet and score it against `pairs.json`.

`generateSummary()` writes response counts, tie rates and sentinel failures to
the summary tab. Agreement against each factor is scored offline, because the
factor verdicts live in `pairs.json` and are deliberately not deployed with the
app.

## A note on Drive playback

Drive share links (`/file/d/<id>/view`) do **not** play in a `<video>` tag. The
app rewrites them to `/preview` and embeds them as iframes, and rewrites source
images to `drive.google.com/thumbnail`. Non-Drive URLs pass through unchanged.
A consequence of the iframe player is that the two clips cannot be started
programmatically in lockstep, which is why the instructions ask raters to play
both and watch each at least once.

## Reporting

Report per axis: agreement rate with its binomial confidence interval,
inter-rater agreement, and the tie rate. Report agreement **as a function of
metric gap** as well as pooled — a factor that agrees with people only on large
gaps is a different, and weaker, result than one that agrees throughout, and
pooling hides the difference. Report the sentinel failure rate alongside; an
agreement number computed over inattentive sessions is not interpretable.

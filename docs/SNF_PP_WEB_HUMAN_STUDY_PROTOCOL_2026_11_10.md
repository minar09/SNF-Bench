# Web human study and role-map annotation (2026-11-10)

**Page:** https://claude.ai/artifact/XxzQAEEzqoJ57dEFxoZFoa (private until the owner shares it)

**Source:** `human_eval_web_2026_11_10/site/snf_human_study.html`

**Stimuli:** built by `scripts/build_human_eval_stimuli.py`.

**Blinding key:** `human_eval_web_2026_11_10/private/key.json`. It is git-ignored and never published.

`human_study/` (the other engineer's study) is untouched. This page is separate, and it does not replace any existing study until its owner adopts it.

## Who can save, and how to share

The page stores answers in its own database. Under the platform's rules, saving is allowed only for:
- the owner;
- people invited **by email as Editors** while the page has **no public link**;
- on a Team/Enterprise plan, organization members at Contributor or above.

Anyone else, including visitors from a public link outside the organization, can open and use the page. Their work stays in their browser, and they get a **Download my answers** file to send back.

**Recommended setup:**
1. Use Share to invite the two annotators, the adjudicator and the raters by email as Editors.
2. Do not turn on a public link while collecting.
3. Give each person a code in advance:
   - annotators: `A1`, `B1`, `ADJ1`;
   - raters: `R01`, `R02`, and so on.

**Privacy:** each person writes only under their own id (`resp/<id>/…` or `ann/<id>/…`). Only the owner reads everyone's records, so annotators cannot see each other's maps. The owner releases a scene to the adjudicator (`adj/<scene>`, readable by Editors) only after both maps exist.

## Rating study (`#rate`)

**Items.** One item per (render, horizon).
- **Beginning clip:** seconds 2–8 of the render.
- **End clip:** the last 6 s before 60, 120 or 240 s.
- **Encoding:** 96 frames at 16 fps, H.264 CRF 23, 832×480.
- **Blinding:** item ids are random; model, scene and horizon live only in the private key. Order is a fixed shuffle per rater.

**Built-in known-answer controls**, made from Steady-Forcing cf01 at 60 s:
- frozen end, expected *motion* = 1–2;
- reversed end, expected *direction* = no;
- ping-pong end, expected *loop* = yes.

**Questions and the measurement each one validates:**

| question | answer scale | paper measurement |
|---|---|---|
| Still parts moved / warped / changed | 1–5 | background displacement (fBD), background motion (NBF) |
| Amount of motion, end vs beginning | 1 stopped … 3 same … 5 much more | motion retention (FP), late material motion (MCFF-L) |
| Moves the way it should | yes / no / cannot tell | candidate direction checks (channel alignment, gravity sign) |
| Repeating loop or backward | no / yes / not sure | replay signature candidate |
| Naturalness | 1–5 | plausibility (no automatic measure claimed) |
| Same scene | yes / partly / no | scene-identity drift (VBench subject/background consistency) |

**Current set.** Version 1 holds 12 items: 3 complete T2V renders × 3 horizons, plus 3 controls.
- I2V items are added by re-running the builder as the matched I2V renders finish, then republishing the same page.
- Item ids and earlier answers are kept.
- **Collect the main data only once both tracks are present in equal numbers.** Version 1 is a pilot.

**Analysis plan,** fixed before data collection:
- Exclude a rater who fails more than one of the three controls.
- Report agreement with Krippendorff's α (ordinal for the 1–5 scales, nominal for the categorical ones).
- Per construct, compute the Spearman correlation between the median rating and the matching SNF measurement and VBench dimension. Use 95% bootstrap intervals that resample both renders and raters, per track.
- Abstentions and exclusions are reported, not dropped silently.

## Role-map annotation (`#annotate`)

**Scope:** the 12 public I2V conditioning images.

**Starting map:** the automatic CLIPSeg map, unreviewed.

**Labels,** as in `docs/SNF_V2_MASK_PROTOCOL.md`:
- 1 support;
- 2 moving material;
- 3 overlay / mixed;
- 0 ignore.

**Tools:** brush, region fill, undo and reset. Annotators also draw a direction arrow, or tick "No single direction". Each map records a confidence and notes.

**Saved record:** a row-major run-length map plus the per-label share.

**Workflow:**
1. A and B annotate independently.
2. The owner releases each scene from `#owner`.
3. The adjudicator loads A, B, or their agreement-only map, decides the disagreements, and saves.

**Reported:** IoU between A and B for support and for material, per scene and per medium. Only adjudicated maps become a versioned mask set (`mask_review_scope: human-independent`). The 48 held I2V source-fixed SNF jobs are released only after that.

## What this cannot do

- **No ethics approval assumed:** the consent text is a minimal plain-language statement. The study owner must confirm it, the age and eligibility rule, and any approval their institution requires before inviting raters.
- **T2V region annotation is not included:** T2V has no conditioning image, and its masks are rebuilt from flow at each horizon.
- **Rater counts are a decision for the owner,** not set by this page. A typical target is at least 3 raters per item, with both tracks balanced.

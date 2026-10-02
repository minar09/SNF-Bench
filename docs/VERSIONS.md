# SNF-Bench versions: what each one is, where it lives, how to go back

Two independent version axes. Every result carries both labels.

| axis | values | what changes | where it is declared |
|---|---|---|---|
| **prompt set** | `v1`, `v2` | what a model is asked to generate | `scripts/prompt_sets.py`, `manifest/prompt_set_hashes.json` |
| **metric spec** | `1.0`, `1.1` | how a video is scored (compensation model) | `docs/METRIC_SPEC_v1.1.md`; `metric_spec_version` in each record |

They are orthogonal: v1 videos have been scored under both specs, and v2 videos
will be scored under 1.1. "v1.1" always means the metric spec, never a prompt set.

---

## Prompt set v1 — the WACV 2027 submission set

* T2V: 23 prompts at 60 s, **different prompts at each horizon** (5/60/120/240 s),
  61% channel water.
* I2V: 10 / 30 / 20 / 5 images at 5 / 60 / 120 / 240 s, captions with evaluator-
  style camera boilerplate.

| | path |
|---|---|
| T2V prompts | `prompts/t2v/prompts{5s,60s,120s,240s}.txt` (+ `prompts240s0[1-4].txt`, `prompts_ext.txt`) |
| I2V | `prompts/i2v/<H>/target_crop_info_16-9.json`, images in `prompts/i2v/<H>/images/` (`16-9 -> images` alias for the loader) |
| results | `raw/<track>/<key>/<H>/snf_task_metrics.json` |
| videos | `videos/<track>/<key>/<H>/` (local symlinks, untracked) |
| staging / flow | `.metric_staging/`, `.flow_fields/` |

**v1 is frozen and must never change.** Its 78 input files are hashed in
`manifest/prompt_set_hashes.json`; its 130 metric records are value-identical to
the last pre-v2 commit `729219b` (the large diffs in later commits are JSON
indentation and the repo-relative `videos_dir` field only).

**Known v1 properties, found on 2026-10-02, not in the submitted paper:**

* Until 2026-10-02 the I2V images were **not in git** — `images` was a tracked
  symlink into a sibling working repository. A fresh clone could not reproduce
  v1 I2V, and an upstream edit would have changed v1 silently. They are now
  vendored (28 MB) and their bytes verified against the files the renders used.
* Provenance of the vendored set: the generating repository's
  `prompts/eval/<H>/16-9` folders and their `target_crop_info_16-9.json`. Every
  caption in them was rendered, and no rendered v1 I2V video carries a caption
  outside them, so this is exactly the set behind every v1 record. A
  `target_crop_info_16-9.json.orig` beside the 60 s file is an earlier draft
  (one image swapped, two filenames normalised) that was never rendered; that
  repository's `supp/` and later 100-prompt T2V set are not part of SNF-Bench v1.
* The I2V pipelines resize the whole image to 832x480 and **do not apply
  `target_bbox`**, and the `16-9` folders are not 16:9 (aspect 0.56 to 1.83). On
  the 60 s primary tier, 16 of 30 conditioning images were stretched by more than
  5%, 7 by more than 25%, and 3 by more than 2x (worst 3.08x, a 720x1280 portrait
  squeezed to landscape). Every system received the same stretched image, so v1
  comparisons remain internally fair, but the conditioning was distorted.

## Prompt set v2 — the rebuilt set

* T2V: 96 scenes over nine transport regimes; **the same scenes at every horizon**.
* I2V: 48 image-text pairs, same strata at half size, every image pre-cut to
  exactly 832x480 so the pipeline resize is an identity.

| | path |
|---|---|
| authoritative manifests | `manifest/prompts_v2.json`, `manifest/i2v_pairs_v2.json` |
| frozen images | `prompts/v2/i2v/images/<id>.jpg` (48) |
| T2V consumer files | `prompts/v2/t2v/prompts{5s,60s,120s,240s}.txt` |
| I2V consumer dirs | `prompts/v2/i2v/snf_v2_<H>/target_crop_info_v2.json` + `v2/<id>.jpg` links |
| results | `raw_v2/<track>/<key>/<H>/snf_task_metrics.json` (records carry `"prompt_set": "v2"`) |
| videos | `videos_v2/<track>/<key>/<H>/` |
| staging / flow / failures | `.metric_staging_v2/`, `.flow_fields_v2/`, `failures_v2/` |

Consumer files are **exported, never hand-written**:
`python scripts/export_prompt_set.py` (write) / `--check` (gate). The first v2
I2V render crashed because its metadata was hand-converted with `target_crop`
as a list; the export writes the format the loader indexes, in v1's conventions
(I2V caption `...text.[240s]`, T2V line `...text. [240s]`). Generators strip the
marker before encoding, so the model sees the manifest text exactly.

**Known v2 properties:**

* Each crop is a 16:9 window resized to 832x480 (26:15), a uniform **2.6%
  horizontal squeeze**. Small, identical across systems, and far below v1's
  distortion; fixing it means re-cutting all 48 images, which is a new version
  (v2.1), not an edit, because renders are already consuming v2.
* Licence is recorded for 2 of 48 I2V images. Blocks release, not evaluation.
* The scene contract (`configs/snf_v2_scene_contract.json`) uses a six-medium
  taxonomy under which both tracks exceed its 35% water cap; v2 uses nine
  transport regimes. Open decision, see `NEXT_VENUE_PLAN.md`.
* The contract prefers scoring 60/120 s as **prefixes of one 240 s rollout**.
  The SNF scorer has no prefix mode yet, so horizons are separate rollouts of
  the same scenes. That is matched by scene but not by trajectory.

---

## Rules that keep the versions apart

1. **Score v2 only with `--prompt-set v2`.**
   `python scripts/rerun_metrics.py --prompt-set v2 --entry i2v/<key>/240s`
   reads `videos_v2/`, writes `raw_v2/`. The default is v1, so every existing
   command keeps its meaning.
2. The scorer **refuses** to score a video whose filename belongs to the other
   set, and **refuses** to merge into a record labelled with the other set.
   Both refusals are exercised by `tests/test_prompt_sets.py`.
3. The gate checks it end to end: `Prompt-set separation` classifies every
   per-video record in both trees; `v2 consumer files current` fails if an
   export is stale.
4. **Never re-freeze v1.** A change to any v2 input is a new version (`v2.1`):
   add it to `prompt_sets.py` with its own roots, freeze it, tag it. Do not edit
   v2 in place while renders are consuming it.
5. `python scripts/freeze_prompt_sets.py` verifies every input file of both sets
   against its hash; it runs in the test suite.
6. **Record the fingerprint in every run.** Each frozen set has a one-string
   content fingerprint (`--fingerprint v2`):

   | set | files | fingerprint |
   |---|---|---|
   | v1 | 78 | `sha256:99799499d912d4ca` |
   | v2 | 61 | `sha256:92bd38f05bd49b39` |

   A run record that stores it can always be matched to the exact inputs it
   consumed, even if a later version reuses the same paths.

## Going back to a version

Both sets live side by side in the working tree, in disjoint paths, so "going
back" to *run* or *score* a version needs no checkout — pick the paths above.
To recover the exact repository state:

    git checkout prompts-v1      # or prompts-v2
    python scripts/freeze_prompt_sets.py   # proves the inputs are intact

The tags are created on the first commit where each set is complete and frozen
(see the bottom of this file once they exist).

## Feeding a v2 render into scoring

Renders write `results/snf_v2/videos/<variant>/<H>s/` in the generating repo.
To score one:

    mkdir -p videos_v2/i2v/<key>
    ln -s <generating repo>/results/snf_v2/videos/<variant>/240s videos_v2/i2v/<key>/240s
    python scripts/rerun_metrics.py --prompt-set v2 --entry i2v/<key>/240s --gpu <g>

`<key>` must be registered in `scripts/registry.py`. A configuration that is not
a published baseline must be registered with `status="internal"` so it stays out
of every public table.

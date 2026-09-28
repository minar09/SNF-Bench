# M1 reviewed mask pilot protocol

Status: implementation input contract, 2026-09-28. No reviewed mask assets have
yet been supplied; the runner must refuse a score without them. The existing
automatic v1.1 masks and metrics are left intact.

## Why source alignment is checked first

The I2V source directory name alone does not establish the crop transform:
16 of 30 source files at 60 seconds differ from the generated frame's aspect
ratio by more than 5%. `scripts/audit_i2v_alignment.py` compared each source
to each generated first frame after direct resize. For three settings
(`self_forcing`, `chunk6`, `f2s_framewise`), all 90 pairs had at least 20 ORB
homography inliers and fitted mean corner displacement below 1% of the frame
diagonal. This supports *direct resize as a pilot transfer rule for these
specific settings*, subject to human mask inspection. It says nothing yet
about other systems or durations.

## Annotation input

Paint one single-channel, 8-bit PNG at the **exact source-image dimensions**:

| Pixel value | Meaning | Used by metric |
| --- | --- | --- |
| 0 | Ignore / cannot assign | No |
| 1 | Rigid support that should remain anchored | fBD, NBF, global fit |
| 2 | Intended moving material | MCFF, FP, DLR, DAR |
| 3 | Overlay or ambiguous support plus motion | Excluded from both |

Label rock, shore, building, or fixed railing as support; label only the
specified flowing medium as intended motion. Put transitions, reflection,
rain over buildings, thin smoke over background, and uncertain pixels into 3
or 0. This is one source-image mask shared across I2V systems, not a mask
estimated from each generated video. A second annotator should independently
label a stratified subset; report IoU and disagreements by role and medium.

The JSON manifest has this shape (values below are illustrative, not an
existing annotation):

```json
{
  "schema_version": 1,
  "entries": [{
    "track": "i2v",
    "duration": "60s",
    "prompt_id": "first 100 characters of the conditioning caption",
    "source_image": "prompts/i2v/60s/images/example.jpg",
    "source_sha256": "sha256 of the exact source file",
    "label_png": "prompts/i2v/reviewed_masks/60s/example.png",
    "geometry": "direct_resize",
    "reviewed": true,
    "reviewed_by": "annotator identifier"
  }]
}
```

The loader rejects missing review, source hash changes, wrong mask dimensions,
unknown labels, insufficient support/flow coverage, or a label PNG outside
the repository. The pilot runner also checks the source against the prompt
metadata and the selected system's recorded first-frame alignment.

## Execution

1. Produce reviewed label PNGs and a manifest; keep these separate from the
   old Otsu partitions. Annotators must not view later generated frames.
2. Run the alignment audit for each selected model and duration. Inspect its
   low-match or high-displacement cases visually; do not force a transfer.
3. Run `scripts/score_i2v_mask_pilot.py --check-only` with the reviewed manifest
   and matching alignment report. Resolve all failures before using a GPU.
4. Score a small, medium-diverse subset first. Pilot records go under
   `manifest/mask_pilot/`, never `raw/`. Compare prompt-paired v1.1 versus
   reviewed-mask metrics and document changes/abstentions.
5. Expand only after the small comparison and independent annotation review.

No score from this path is a v1.1 result. It carries
`metric_spec_version=2-mask-pilot`, role coverage, reviewer, source/mask hashes,
and alignment evidence. A T2V mask path needs a separate first-frame annotation
policy; reusing one pixel mask across different T2V layouts is invalid.

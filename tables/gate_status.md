# Pre-freeze gate status

The pipeline's refusal mechanism. Every defect found on 2026-08-13 shared one property: nothing was capable of noticing it. `FINAL_SWEEP_ALLOWED` turns TRUE only when every required gate passes.

```
SNF PRE-FREEZE GATE
===========================================================
Metric spec v1.1 parity ........ PASS     v1.1, six metrics defined
Banned terms purged (paper) .... PASS     paper clean of DriftFrac/BFR
FPS/size metadata .............. FAIL     1881/2817 videos have metadata
Artifact schema scan ........... FAIL     7 entries blocking (0 error records, 7 missing-key records)
Valid-record coverage .......... FAIL     7 entries incomplete; worst: i2v/phase7_000200/60s 29/30, i2v/causvid/60s 29/30, i2v/cf++_1step/60s 29/30
I2V >=3 published models @60s .. PASS     4 families >= 27 valid (CausVid:29, Causal-Forcing:30, Causal-Forcing++:30, Self-Forcing:30)
Similarity compensation ........ PASS     v1.1 fits similarity; v1.0 record unchanged
Compensation unit tests ........ PASS     translation/rotation/scale recovered
Records newer than videos ...... PASS     every record newer than its videos
Generated assets current ....... FAIL     22 generated file(s) older than i2v_metric_review_2026_10_08.json; re-run paper_assets.py
Prompt-set separation .......... PASS     2561 per-video records, each in its own set's tree
Single measurement per cell .... PASS     8 public table cells, each a single measurement
v2 consumer files current ...... PASS     v2 consumer files current (8 files, 192 links)
Mask schema frozen ............. PENDING  MASK_SPEC_v1.0.md not written (gate Aug 14)
Overlay masks built ............ PENDING  no overlay masks built (Aug 14)
Zero-motion floor .............. PENDING  not run (P0#5)
Validation suite ............... PENDING  not run (Aug 18)
Figure provenance footers ...... PASS     12 figures; footer enforced by figures.save()  (advisory)
===========================================================
FINAL_SWEEP_ALLOWED = FALSE

blocked by 8: FPS/size metadata; Artifact schema scan; Valid-record coverage; Generated assets current; Mask schema frozen; Overlay masks built; Zero-motion floor; Validation suite
```

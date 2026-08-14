# Pre-freeze gate status

The pipeline's refusal mechanism. Every defect found on 2026-08-13 shared one property: nothing was capable of noticing it. `FINAL_SWEEP_ALLOWED` turns TRUE only when every required gate passes.

```
SNF PRE-FREEZE GATE
===========================================================
Metric spec v1.1 parity ........ PASS     v1.1, six metrics defined
Banned terms purged (paper) .... PASS     paper clean of DriftFrac/BFR
FPS/size metadata .............. PASS     1881 videos, fps+size present
Artifact schema scan ........... FAIL     13 entries blocking (115 error records, 6 missing-key records)
Valid-record coverage .......... FAIL     13 entries incomplete; worst: i2v/cf_framewise/60s 1/30, i2v/causvid/60s 1/30, i2v/cf_framewise/120s 1/20
I2V >=3 published models @60s .. FAIL     2/3 families >= 27 valid (CausVid:1, Causal-Forcing:1, Causal-Forcing++:30, Self-Forcing:30)
Similarity compensation ........ FAIL     still translation-only (median of static flow)
Compensation unit tests ........ PASS     translation/rotation/scale recovered
Mask schema frozen ............. PENDING  MASK_SPEC_v1.0.md not written (gate Aug 14)
Overlay masks built ............ PENDING  no overlay masks built (Aug 14)
Zero-motion floor .............. PENDING  not run (P0#5)
Validation suite ............... PENDING  not run (Aug 18)
Figure provenance footers ...... PASS     5 figures; footer enforced by figures.save()  (advisory)
===========================================================
FINAL_SWEEP_ALLOWED = FALSE

blocked by 8: Artifact schema scan; Valid-record coverage; I2V >=3 published models @60s; Similarity compensation; Mask schema frozen; Overlay masks built; Zero-motion floor; Validation suite
```

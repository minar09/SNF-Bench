# SNF-Bench v2 metric work log

Execution record for the order in `I2V_METRIC_REVIEW_2026_10_08.md` §6.
Newest entries first. Nothing here changes a frozen measurement; each result
names the artifact that holds it.

---

## 2026-10-08 — step 1 (port) and step 2 (CPU floors)

### Step 1: source-referenced scorer ported, parity exact

`scripts/snf_sourceref.py` ports the method project's `sourcefixed-1.0`
scorer. The six scoring functions are copied verbatim by the Python parser
from upstream commit `592747a3e2` (file sha256 `f4782bc6…`), and their body
hashes are pinned. `tests/test_sourceref.py` fails if a copy is edited locally
or if upstream changes, and a deliberate re-port is required either way. Each
record declares the full measurement policy: source reference, mask set and
review scope, 12% windows, sampling rate, registered-only failure handling.
`scripts/measurement.py` therefore refuses to pool these records with v1.1.

**Parity on a real clip, CPU, one process, same RAFT weights**
(`manifest/sourceref_parity.json`, scene `ial01`, 5 s prefix):
46 of 46 output keys identical between port and upstream (|d| = 0), and the
8 v1.1-equivalent keys identical to `snf_metrics_v11.process_video`.

**Full-length GPU parity is prepared but not run.**
`scripts/check_sourceref_records.py` will re-score 9 already-scored 60 s
videos, one per regime and covering every abstention path, and compare them
with the stored records. It waits for ≥ 12 GB free and obeys the method
project's STOP/PAUSE flags. At the time of writing GPU 2 was saturated, and
GPU 3 was at 100% with `STOP_gpu3` and `PAUSE_gpu3` raised, so it has not run.

**Regression found and fixed on the way.** On 2026-09-30 the RAFT cache path
was moved behind `scripts/_paths.py`. The default became `~/.cache/vbench`,
which is empty on this machine, so SNF-Bench's own RAFT entry points (metric
worker, validation suite, v1.1 scorer) would have failed. The method project
sets `VBENCH_CACHE_DIR` itself and was unaffected. The real location is now in
`configs/local_paths.json`, and `vbench_cache()` raises when the checkpoint is
missing instead of creating an empty directory.

### Step 2: candidate kernels and their floors

`scripts/snf_candidates.py` holds four candidates, none admitted: pixelwise
CIEDE2000 on the eroded support, interior-tile detail retention, interior-tile
activity, and multi-frame recurrence. Colour uses an explicit D65 conversion.
CIEDE2000 matches all 35 rows of Sharma, Wu & Dalal's test data to < 1e-4
(`tests/data/ciede2000_sharma.txt`). Synthetic controls in
`tests/test_candidates.py`:

* an equal-mean texture swap is invisible to region-mean colour and clear to
  pixelwise ΔE00;
* glassy smoothing drops detail, while a frozen sharp clip keeps it (so detail
  is read only beside activity);
* an exact loop scores recurrence > 0.99 at the right lag; fresh motion < 0.5.

**Floors** (`manifest/candidate_floors.json`). Each of the 48 sources was
encoded as a 10 s static clip with the generators' own writer, inside the
generation image on CPU: `torchvision.io.write_video(fps=16)`, libx264
defaults, the same stream type as the renders. Nothing moves and nothing drifts:

| measure | median | p95 | reading |
|---|---:|---:|---|
| pixelwise ΔE00, support mean | 1.04 | 1.35 | codec floor ≈ one just-noticeable difference |
| pixelwise ΔE00, support p90 | 2.32 | 3.12 | tail floor |
| mask-edge effect (no erosion − 6 px) | 0.006 | max 0.29 | small; erosion kept |
| detail ratio vs source | 1.00 | 1.20 | encoding can *add* up to 20% high-frequency energy (ringing) |
| activity, grey levels | 0.019 | 0.038 | zero-motion floor; per-frame max 0.29–0.63 at keyframes, so use a robust window statistic |
| recurrence | 1.000 | 1.000 | a frozen region is a perfect loop: only meaningful where activity clears its floor |
| `sourcefixed-1.0` source PSNR | 44.9 dB | 47.2 dB | ceiling, not floor |
| `sourcefixed-1.0` dE_static | 1.43 | 4.53 | **see below** — mostly arithmetic error |

Seven scenes have no interior dynamic tile: all six precipitation scenes
(overlay medium) and `icb04`. This matches the method project's own endpoint
eligibility.

### Defect: float32 accumulation in `dE_static`

`metric_code/snf_extra_metrics.py` (v1 extras, lines 96–99) and the ported
`extras_sourcefixed` average support Lab colour with
`np.stack(...).reshape(-1, 3).mean(0)` on **float32**. With about 300k support
pixels × 24 late frames, the per-channel sum outgrows float32 precision.

On the static `icb04` clip, the late-window a* mean is 130.76 in float32 and
135.53 in float64. `dE_static` reads **6.84 where the true shift is 1.35**:
every frame is shifted by the same 1.35, a small, uniform darkening (ΔL* ≈
−0.5) from the H.264/yuv420p path.

* **The v1 SNF-Bench paper is unaffected:** no table, figure or macro uses
  `dE_static`. The 83 v1 extras records carry the error in that field.
* **`sourcefixed-1.0` keeps the defect deliberately**, because it must reproduce
  upstream. A corrected measure needs a new identity. Pixelwise ΔE00 in
  `snf_candidates.py` is float64 throughout and is not affected.
* **The method project's colour results are measured with it.** The size of
  the effect on their contrasts is the audit below.

**Audit result** (`scripts/audit_de_precision.py`,
`manifest/de_precision_audit_seed{42,1042}.json`). The method project's 60 s
records for Echo and the static sink at k = 1 and k = 3, all 48 scenes, were
recomputed both ways. The float32 recomputation reproduces every stored
`dE_static` exactly (0 mismatches on either seed), so the comparison is
trustworthy.

| | seed 42 | seed 1042 |
|---|---|---|
| per-video |float32 − float64| | median 0.09, p95 1.44, max 3.73 | median 0.11, p95 1.35, max 4.33 |
| D(1) | −3.51 → −3.53 | −4.83 → −5.00 |
| D(3) | +1.22 → +1.17 | +3.68 → +3.55 |
| **Γ(3,1)** | **+4.73 → +4.70** | **+8.51 → +8.56** |

The error is real per video, but it is nearly common to the two arms of a
pair, which share a scene, a support and similar colours, so it cancels in the
contrasts. **The method project's colour-drift interaction stands.** It
matters where values are read absolutely: a per-video error up to ~4 units
exceeds their ±0.5 "tied" margin, and on static or near-static content the
mean-colour distance is dominated by it. Recommendation: any future
mean-colour measure accumulates in float64 under a new identity. Pixelwise
ΔE00 (candidate) is already float64.

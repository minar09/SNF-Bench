"""Render a concise read-only report from saved, provenance-checked summaries."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PANEL = ROOT / 'manifest/existing_snf_vbench_panel_60s_2026_10_30_v2.json'
T2V = ROOT / 'manifest/existing_t2v_matched_60s_2026_10_30.json'
INV = ROOT / 'manifest/existing_scores_inventory_2026_10_30.json'
HORIZON = ROOT / 'manifest/existing_snf_vbench_horizons_2026_10_30_v2.json'
OUT = ROOT / 'docs/EXISTING_SCORE_COMPARISONS_2026_10_30.md'
COLUMNS = ['snf.idPSNR_late_src', 'snf.MCFF_late', 'i2v.subject', 'i2v.background', 'long.background', 'long.dynamic_degree']
T2V_COLUMNS = ['fBD_mean', 'NBF_mean', 'background_consistency', 'motion_smoothness', 'dynamic_degree']


def main():
    panel = json.loads(PANEL.read_text())
    t2v = json.loads(T2V.read_text())
    inventory = json.loads(INV.read_text())
    horizon_data = json.loads(HORIZON.read_text())
    comparisons = panel['comparisons']
    for key in COLUMNS:
        scenes = {tuple(row['scene_id'] for row in c['rows'] if row['scores'][key]['paired']) for c in comparisons.values()}
        if len(scenes) != 1:
            raise ValueError(f'{key}: panel rows do not share exactly the same paired scenes')
    lines = ['# Existing SNF and VBench results: reuse-first comparison', '',
        'Snapshot: 2026-10-30. This report reads saved records only; no video was generated or rescored. '
        'The [score inventory](../manifest/existing_scores_inventory_2026_10_30.json) indexes '
        f"{sum(g['type']=='sourcefixed_staging' for g in inventory['groups'])} source-fixed staging groups "
        f"({sum(g['n_records'] for g in inventory['groups'] if g['type']=='sourcefixed_staging')} records), "
        f"{sum(g['type']=='vbench_summary' for g in inventory['groups'])} VBench summary groups, "
        f"and {inventory['legacy_rows']} legacy SNF CSV rows. It is a bounded snapshot of the method project's "
        'factorial score tree and the legacy CSV, not an exhaustive scan of all disks or proof of release eligibility. '
        'Active project jobs may add records after this snapshot.', '',
        '## I2V: same-source 60-second results', '',
        'The following means use existing source-fixed SNF, VBench-I2V and VBench-Long results on the '
        'same fixed-nature source cohort. Each method is paired to SceneTether with matching source-image '
        'and mask hashes, actual per-scene seed, scorer identity, recorded VBench entrypoint, flags, sampling and environment-file hashes, and input-video '
        'hashes. Recorded hashes were cross-checked; the video files themselves were not rehashed. '
        'For every column below, the included scene IDs are identical across all rows. '
        'The VBench suites are evaluations on the same inputs, not independent datasets. '
        'Ports are CF++ adaptations, not their authors’ native model pipelines.', '',
        '| Method | SNF source PSNR (dB), n=48 | SNF late MCFF, n=41 | I2V subject, n=48 | I2V background, n=48 | Long background, n=48 | Long dynamic degree, n=48 |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for label, c in comparisons.items():
        vals = [c['summary'][k]['baseline_mean'] for k in COLUMNS]
        lines.append('| ' + label + ' | ' + ' | '.join(f'{v:.3f}' for v in vals) + ' |')
    first = next(iter(comparisons.values()))
    vals = [first['summary'][k]['candidate_mean'] for k in COLUMNS]
    lines += ['| SceneTether (author method) | ' + ' | '.join(f'{v:.3f}' for v in vals) + ' |', '',
        'The 41-scene MCFF subset excludes motion-abstaining cases. fBD is omitted from this overview '
        'because paired eligibility differs across comparisons; the full [panel record]'
        '(../manifest/existing_snf_vbench_panel_60s_2026_10_30_v2.json) contains fBD and per-scene scores '
        'with counts. VBench-Long here uses the saved custom-input/dev configuration and its own clip '
        'aggregation; numbers should not be labeled official leaderboard scores. Dynamic degree and '
        'MCFF measure activity-related signals, not whether motion is physically correct. Historical '
        '`dE_static_src` is omitted because of the documented float32 accumulation defect. These '
        'are exposed development sources; paired descriptive means are not evidence of statistical '
        'significance or human-aligned naturalness. Stored SceneTether-paper summary tables may use '
        'different estimator paths or populations; do not mix cells without a separate provenance audit.', '',
        '## Historical T2V: shared legacy prompt identifiers', '',
        'The following means come from the existing legacy per-video CSV and use the intersection of '
        '22 unambiguous stored prompt identifiers for each shown metric across all eight models. '
        'One duplicate Rolling-Forcing identifier is excluded. Identifiers are truncated strings, not '
        'independently verified prompt/video hashes; these are provisional matching results. '
        'The author method is shown separately by name. Legacy automatic masks and metric definitions '
        'are not comparable in absolute scale to the I2V source-fixed rows.', '',
        '| Model | SNF fBD_mean | SNF NBF_mean | VBench background | VBench motion smoothness | VBench dynamic degree |',
        '|---|---:|---:|---:|---:|---:|']
    # Add a compact endpoint-window comparison, validating common scene sets.
    endpoint_lines = ['## Existing 120/240-second endpoint windows', '',
        'These rows score the final 60-second window of separately requested 120- and '
        '240-second generations. They are not prefixes of one common rollout and '
        'must not be interpreted as within-rollout accumulation. For each endpoint, '
        'the two rows below use identical paired scenes per metric. The '
        '[horizon panel](../manifest/existing_snf_vbench_horizons_2026_10_30_v2.json) '
        'contains nine matched configurations per endpoint and records the missing '
        'TetherCache VBench-I2V provenance explicitly.', '',
        '| Endpoint / method | SNF source PSNR (dB), n=48 | SNF late MCFF, n=41 | I2V subject, n=48 | I2V background, n=48 | Long background, n=48 | Long dynamic degree, n=48 |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for horizon in ('120', '240'):
        c = horizon_data['horizons'][horizon]['comparisons']['Framewise Echo k=1']
        for label, side in [('Framewise Echo k=1', 'baseline_mean'), ('SceneTether', 'candidate_mean')]:
            vals = [c['summary'][k][side] for k in COLUMNS]
            counts = [c['summary'][k]['n_paired'] for k in COLUMNS]
            if counts != [48, 41, 48, 48, 48, 48]:
                raise ValueError(f'{horizon} endpoint coverage changed: {counts}')
            endpoint_lines.append('| ' + horizon + ' s / ' + label + ' | ' + ' | '.join(f'{v:.3f}' for v in vals) + ' |')
    endpoint_lines += ['', 'VBench-Long here operates on the extracted 60-second '
        'endpoint window, not the entire 120- or 240-second video. The scoring '
        'window, codec and sampling remain part of each metric definition.', '']
    insert_at = lines.index('## Historical T2V: shared legacy prompt identifiers')
    lines[insert_at:insert_at] = endpoint_lines
    for m in t2v['models']:
        vals = [t2v['metrics'][k]['mean_per_model'][m] for k in T2V_COLUMNS]
        label = m + (' (author method)' if m == t2v['author_method'] else '')
        lines.append('| ' + label + ' | ' + ' | '.join(f'{v:.3f}' for v in vals) + ' |')
    lines += ['', 'The [T2V record](../manifest/existing_t2v_matched_60s_2026_10_30.json) '
        'includes excluded duplicate rows, prompt IDs and additional scores. These are historical '
        'SNF-Bench v1 results; the automatically inferred masks, prompt-set size and prior metric '
        'selectivity limitations remain. High scores or motion magnitude alone do not establish '
        'natural flow.', '', '## Reuse and future scheduling', '',
        'Before any generation, check model/adapter and checkpoint, source-image or full prompt, '
        'preprocessing, actual seed, requested and realized duration, fps and codec against existing '
        'records. Before scoring, additionally check video-content hash, suite/version, weights, '
        'metric configuration, mask and time windows. Reuse an exact eligible result; a missing '
        'hash or ambiguous legacy identifier requires investigation, not a presumed match or an '
        'automatic rerun. Under the current reuse instruction, do not rescore existing videos; '
        'score only new model/image/prompt outputs. Preserve prior failures and partial records. The inventory '
        'does not authorize a new run merely because an item is absent from this bounded snapshot.', '',
        'Rebuild the inventory and reports with new output names before a new scheduling decision; '
        'avoid overwriting existing snapshots. The executable comparison and inventory scripts are '
        '`scripts/compare_existing_snf_vbench.py`, `scripts/compare_existing_panel.py`, '
        '`scripts/summarize_existing_t2v.py` and `scripts/inventory_existing_scores.py`. '
        'Use `scripts/lookup_existing_video.py --inventory manifest/existing_scores_inventory_2026_10_30.json '
        '--video-sha256 <full-lowercase-sha256>` to find indexed evidence before scheduling; '
        'it checks whether VBench provenance changed since the snapshot. A hit still requires '
        'a matching metric configuration and input policy. The exploratory pair report with '
        'suffix `_v2` adds provenance checks to the earlier preliminary pair report.']
    OUT.write_text('\n'.join(lines) + '\n')
    print('wrote', OUT)


if __name__ == '__main__':
    main()

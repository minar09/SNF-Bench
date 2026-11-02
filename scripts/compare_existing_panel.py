"""Pair each existing CF++-family cell against SceneTether, retaining failures."""
import json
from pathlib import Path
from compare_existing_snf_vbench import compare

ROOT = Path('/home/minar/ar-image-animation/results/factorial/scores/cfpp')
OUT = Path('manifest/existing_snf_vbench_panel_60s_2026_10_30_v2.json')
CANDIDATE = 'echo_nfpb1_h1_fm_tether100_lr'
BASELINES = {
    'Framewise Echo k=1': 'echo_nfpb1_default_lr',
    'Spatial Echo k=3': 'echo_spatial_nfpb3_default_lr',
    'Static sink k=3': 'static_sink_nfpb3_default_lr',
    'Age-decay read': 'echo_nfpb1_fg_rho03_lr',
    'ALG-inspired port': 'echo_nfpb1_c2_lr',
    'DyMoS port': 'echo_nfpb1_dymos_lr',
    'UnStep port': 'static_sink_nfpb3_unstep_lr',
    'PackCache-style': 'echo_nfpb1_packcache_decay_lr',
    'FramePack-style': 'echo_nfpb1_fp_pool_lr',
    'TetherCache port': 'static_sink_nfpb1_tether_lr',
}

if __name__ == '__main__':
    if OUT.exists(): raise SystemExit('output exists')
    comparisons, errors = {}, []
    for label, cell in BASELINES.items():
        try:
            comparisons[label] = compare(ROOT, cell, CANDIDATE)
        except (ValueError, OSError, KeyError) as exc:
            errors.append({'label': label, 'cell': cell, 'error': str(exc)})
    result = {'status': 'complete' if not errors else 'complete_with_errors',
              'scope': 'existing matched CF++-family 60s seed42 cells; adapted ports are not native baselines',
              'comparisons': comparisons, 'errors': errors}
    OUT.write_text(json.dumps(result, indent=1, allow_nan=False) + '\n')
    print('comparisons', len(comparisons), 'errors', errors)

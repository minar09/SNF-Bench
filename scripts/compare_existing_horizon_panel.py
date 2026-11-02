"""Reuse saved endpoint-window records; expose unavailable comparisons."""
import json
from pathlib import Path
from compare_existing_panel import ROOT, CANDIDATE, BASELINES
from compare_existing_snf_vbench import compare

OUT = Path('manifest/existing_snf_vbench_horizons_2026_10_30_v2.json')
if __name__ == '__main__':
    if OUT.exists(): raise SystemExit('output exists')
    output = {'status': 'complete', 'scope': 'separately requested duration endpoints; last 60s windows, not same-rollout prefixes', 'horizons': {}}
    for horizon in (120, 240):
        comparisons, errors = {}, []
        for label, cell in BASELINES.items():
            try:
                comparisons[label] = compare(ROOT, cell, CANDIDATE, horizon)
            except (ValueError, OSError, KeyError) as exc:
                errors.append({'label': label, 'cell': cell, 'error': str(exc)})
        output['horizons'][str(horizon)] = {'comparisons': comparisons, 'errors': errors}
        if errors: output['status'] = 'complete_with_errors'
    OUT.write_text(json.dumps(output, indent=1, allow_nan=False) + '\n')
    print([(h, len(v['comparisons']), len(v['errors'])) for h, v in output['horizons'].items()])

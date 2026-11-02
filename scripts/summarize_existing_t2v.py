"""Conservative historical T2V score summary; ambiguous identifiers are excluded."""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
import statistics

CSV = Path('manifest/per_video_scores.csv')
OUTPUT = Path('manifest/existing_t2v_matched_60s_2026_10_30.json')
MODELS = ['CausVid', 'self_forcing', 'infinite_forcing', 'rolling_forcing',
          'reward_forcing', 'longlive', 'causal_forcing', 'steady_forcing_bt']
METRICS = ['fBD_mean', 'NBF_mean', 'FP_mean', 'MCFF_late_mean', 'background_consistency',
           'motion_smoothness', 'temporal_flickering', 'dynamic_degree']


def build(path):
    groups = defaultdict(list)
    with path.open(newline='') as f:
        for r in csv.DictReader(f):
            if r['track'] == 't2v' and r['duration'] == '60s' and r['model'] in MODELS and r['metric'] in METRICS:
                try:
                    v = float(r['value'])
                except ValueError:
                    continue
                if math.isfinite(v):
                    groups[(r['model'], r['prompt_id'], r['metric'])].append(v)
    summaries = {}
    for metric in METRICS:
        by_model = {model: {p: values[0] for (m,p,k),values in groups.items() if m == model and k == metric and len(values) == 1} for model in MODELS}
        shared = sorted(set.intersection(*(set(by_model[m]) for m in MODELS)))
        ambiguous = [{'model': m, 'prompt_id': p, 'row_count': len(values), 'values': values}
                     for (m,p,k),values in groups.items() if k == metric and len(values) > 1]
        summaries[metric] = {'n_shared_unambiguous_prompt_ids': len(shared), 'prompt_ids': shared,
                             'ambiguous_excluded': ambiguous,
                             'mean_per_model': {m: statistics.mean(by_model[m][p] for p in shared) if shared else None for m in MODELS}}
    return {'status': 'complete', 'csv_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'scope': 'historical T2V 60s scores, intersection of unambiguous stored prompt identifiers, 8 models',
            'models': MODELS, 'author_method': 'steady_forcing_bt', 'metrics': summaries,
            'limitations': ['identifiers are truncated legacy strings; prompt/video identity is not independently hash-verified',
                            'duplicates excluded even if values agree', 'historical source sets exposed and not journal confirmation',
                            'legacy automatic partitions and metric identities cannot be pooled with sourcefixed I2V',
                            'per-metric shared prompt set may differ', 'no confidence intervals or preference claims']}


if __name__ == '__main__':
    if OUTPUT.exists(): raise SystemExit('output exists')
    result = build(CSV)
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print('wrote', OUTPUT)

"""Compare two completed same-source parity reports without ranking naturalness."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(base_path, method_path):
    a, b = (json.loads(p.read_text()) for p in (base_path, method_path))
    if a['status'] != 'PASS' or b['status'] != 'PASS':
        raise ValueError('both input parity runs must be complete and pass')
    for key in ('measurement', 'port_sha256', 'upstream_scorer_sha256', 'mask_manifest_sha256'):
        if a[key] != b[key]:
            raise ValueError(f'{key} differs between reports')
    if a['cell'].split('/')[-1] != b['cell'].split('/')[-1]:
        raise ValueError('seed differs between reports')
    aa = {x['scene_id']: x for x in a['rows']}
    bb = {x['scene_id']: x for x in b['rows']}
    if set(aa) != set(bb):
        raise ValueError('paired scene sets differ')
    rows = []
    for sid in a['requested_scenes']:
        x, y = aa[sid], bb[sid]
        if x['source_sha256'] != y['source_sha256'] or x['mask_sha256'] != y['mask_sha256']:
            raise ValueError(f'{sid}: source or mask hashes differ')
        if x['category'] != y['category']:
            raise ValueError(f'{sid}: category mismatch')
        metrics = {}
        for name in x['scores']:
            v1, v2 = x['scores'][name]['rescore'], y['scores'][name]['rescore']
            if isinstance(v1, (float, int)) and isinstance(v2, (float, int)) and math.isfinite(v1) and math.isfinite(v2):
                metrics[name] = {'baseline': v1, 'scenetether': v2, 'difference_scenetether_minus_baseline': v2 - v1}
            else:
                metrics[name] = {'baseline': v1, 'scenetether': v2, 'difference_scenetether_minus_baseline': None}
        rows.append({'scene_id': sid, 'category': x['category'], 'source_sha256': x['source_sha256'],
                     'mask_sha256': x['mask_sha256'], 'scores': metrics,
                     'baseline_abstentions': x['abstentions'], 'scenetether_abstentions': y['abstentions']})
    summary = {}
    for name in rows[0]['scores']:
        ds = [r['scores'][name]['difference_scenetether_minus_baseline'] for r in rows]
        ds = [d for d in ds if d is not None]
        summary[name] = {'n_paired': len(ds), 'median_difference': statistics.median(ds) if ds else None}
    return {'status': 'complete', 'scope': 'exploratory paired nine-scene 60-second seed-42 port comparison; not naturalness validation or model ranking',
            'measurement': a['measurement'], 'baseline_cell': a['cell'], 'scenetether_cell': b['cell'],
            'baseline_report_sha256': digest(base_path), 'scenetether_report_sha256': digest(method_path),
            'summary': summary, 'rows': rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--scenetether', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error('output exists')
    report = build(args.baseline, args.scenetether)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print('wrote', args.output)


if __name__ == '__main__':
    main()

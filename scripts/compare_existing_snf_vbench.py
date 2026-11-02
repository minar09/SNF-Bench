"""Pair already-computed SNF and VBench scores on exact recorded provenance."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

METRICS = {
    'snf.fBD_src': ('snf', 'fBD_src'),
    'snf.MCFF_late': ('snf', 'MCFF_late'),
    'snf.idPSNR_late_src': ('snf', 'idPSNR_late_src'),
    'i2v.subject': ('i2v', 'i2v_subject'),
    'i2v.background': ('i2v', 'i2v_background'),
    'long.subject': ('long', 'subject_consistency'),
    'long.background': ('long', 'background_consistency'),
    'long.motion_smoothness': ('long', 'motion_smoothness'),
    'long.dynamic_degree': ('long', 'dynamic_degree'),
    'long.aesthetic': ('long', 'aesthetic_quality'),
    'long.imaging': ('long', 'imaging_quality'),
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def finite(x):
    try:
        value = float(x)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def load_cell(root, cell, horizon=60):
    c = root / cell / 'seed42'
    records = {}
    stage = c / ('sourcefixed_60s/staging' if horizon == 60 else f'sourcefixed_{horizon}s/w{horizon:03d}/staging')
    for p in sorted(stage.glob('*.json')):
        d = json.loads(p.read_text())
        if d.get('scene_id') and d.get('horizon_s') == 60:
            records[d['scene_id']] = (d, sha(p))
    suites = {}
    suffix = '60s' if horizon == 60 else f'{horizon}s_w{horizon:03d}'
    long_rel = 'vbench_long/60s/long' if horizon == 60 else f'horizon_vbench/{suffix}/vbench_long/60s/long'
    for name, rel in [('i2v', f'vbench_i2v/{suffix}/i2v'), ('long', long_rel)]:
        folder = c / rel
        prov = json.loads((folder / 'provenance.json').read_text())
        summary = json.loads((folder / 'summary.json').read_text())
        rows = {}
        with (folder / 'per_video.csv').open(newline='') as f:
            for row in csv.DictReader(f):
                key = (row['scene_id'], row['dim'])
                if key in rows:
                    raise ValueError(f'duplicate VBench row: {cell} {name} {key}')
                rows[key] = row
        signature = {k: prov.get(k) for k in ('repository_revision', 'entry_file_sha256', 'official_args', 'dev_flag', 'frame_sampling', 'env_files_sha256')}
        suites[name] = {'rows': rows, 'signature': signature, 'provenance': prov, 'summary_status': summary.get('status'),
                        'provenance_sha256': sha(folder / 'provenance.json'),
                        'csv_sha256': sha(folder / 'per_video.csv')}
    return records, suites


def compare(root, a, b, horizon=60):
    if horizon not in (60, 120, 240):
        raise ValueError("unsupported endpoint")
    ra, sa = load_cell(root, a, horizon)
    rb, sb = load_cell(root, b, horizon)
    for name in ('i2v', 'long'):
        if sa[name]['signature'] != sb[name]['signature']:
            raise ValueError(f'{name}: VBench configurations differ')
    rows = []
    for sid in sorted(set(ra) & set(rb)):
        x, xsha = ra[sid]
        y, ysha = rb[sid]
        for rec in (x, y):
            for value in (rec.get('source_sha256'), rec.get('video_sha256'), (rec.get('mask_sha256') or {}).get('labels'), rec.get('scorer_sha256')):
                if not isinstance(value, str) or len(value) != 64:
                    raise ValueError(f'{sid}: missing or invalid SHA256 identity')
        if x.get('source_sha256') != y.get('source_sha256') or x.get('mask_sha256', {}).get('labels') != y.get('mask_sha256', {}).get('labels'):
            raise ValueError(f'{sid}: source or mask differs')
        if x.get('seed') != y.get('seed') or x.get('scorer_sha256') != y.get('scorer_sha256'):
            raise ValueError(f'{sid}: actual seed or scorer differs')
        scores = {}
        for key, (suite, dim) in METRICS.items():
            if suite == 'snf':
                av, bv = finite(x.get(dim)), finite(y.get(dim))
                if dim == 'fBD_src' and (x.get('fBD_abstained') or y.get('fBD_abstained')):
                    av = bv = None
                if dim == 'MCFF_late' and (x.get('motion_abstained') or y.get('motion_abstained')):
                    av = bv = None
            else:
                one, two = sa[suite]['rows'].get((sid, dim)), sb[suite]['rows'].get((sid, dim))
                for row, rec, scored in ((one, x, sa[suite]), (two, y, sb[suite])):
                    prov = scored['provenance']
                    if row and prov.get('input_video_sha256', {}).get(sid) != rec.get('video_sha256'):
                        raise ValueError(f'{sid} {key}: VBench provenance video hash mismatch')
                    if row and suite == 'i2v' and prov.get('source_image_sha256', {}).get(sid) != rec.get('source_sha256'):
                        raise ValueError(f'{sid} {key}: VBench source image mismatch')
                    if row and (row['src_sha256'] != rec.get('video_sha256') or str(row['seed']) != str(rec.get('seed'))):
                        raise ValueError(f'{sid} {key}: scored video hash or actual seed mismatch')
                av = finite(one['value']) if one and one['status'] == 'ok' else None
                bv = finite(two['value']) if two and two['status'] == 'ok' else None
            scores[key] = {'baseline': av, 'candidate': bv, 'paired': av is not None and bv is not None}
        rows.append({'scene_id': sid, 'category': x.get('category'), 'actual_seed': x.get('seed'),
                     'source_sha256': x.get('source_sha256'), 'mask_sha256': x.get('mask_sha256', {}).get('labels'),
                     'baseline_video_sha256': x.get('video_sha256'), 'candidate_video_sha256': y.get('video_sha256'),
                     'baseline_snf_record_sha256': xsha, 'candidate_snf_record_sha256': ysha, 'scores': scores})
    summary = {}
    for key in METRICS:
        pairs = [(r['scores'][key]['baseline'], r['scores'][key]['candidate']) for r in rows if r['scores'][key]['paired']]
        summary[key] = {'n_paired': len(pairs),
                        'baseline_mean': statistics.mean(x for x, _ in pairs) if pairs else None,
                        'candidate_mean': statistics.mean(y for _, y in pairs) if pairs else None,
                        'mean_paired_difference': statistics.mean(y - x for x, y in pairs) if pairs else None}
    return {'status': 'complete', 'scope': f'existing endpoint {horizon}s, last 60-second window, same-source, same-mask, actual-seed-paired scores; exploratory exposed development data', 'endpoint_seconds': horizon,
            'baseline': a, 'candidate': b, 'n_common_sourcefixed_records': len(rows),
            'suite_provenance': {n: {'configuration': sa[n]['signature'], 'baseline_csv_sha256': sa[n]['csv_sha256'],
                                      'candidate_csv_sha256': sb[n]['csv_sha256'],
                                      'baseline_status': sa[n]['summary_status'], 'candidate_status': sb[n]['summary_status']} for n in sa},
            'limitations': ['input hashes checked against stored records, not rehashed video bytes',
                            'distinct metric populations retained per metric', 'same benchmark sources, not independent datasets',
                            'no human validity, independent confirmation, or claims of causal significance'],
            'summary': summary, 'rows': rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--baseline', required=True)
    p.add_argument('--candidate', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--horizon', type=int, choices=(60, 120, 240), default=60)
    args = p.parse_args()
    if args.output.exists():
        p.error('output exists')
    result = compare(args.root, args.baseline, args.candidate, args.horizon)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print('paired', result['n_common_sourcefixed_records'], 'scenes:', args.output)


if __name__ == '__main__':
    main()

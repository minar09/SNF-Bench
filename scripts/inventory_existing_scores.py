"""Read-only inventory of existing benchmark scores; never generates or scores media."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory(root, legacy):
    groups = []
    errors = []
    base = root / 'results/factorial/scores'
    # Limit recursive scans to actual suite names to avoid stage output, thumbnails and model files.
    for suite in ('vbench_i2v', 'vbench_long', 'horizon_vbench'):
        for summary in sorted(base.glob(f'*/*/seed*/{suite}/**/summary.json')):
            try:
                raw = summary.read_bytes()
                d = json.loads(raw)
                folder = summary.parent
                pv = folder / 'per_video.csv'
                prov = folder / 'provenance.json'
                groups.append({'type': 'vbench_summary', 'suite_path': suite,
                    'path': str(summary.relative_to(root)), 'sha256': sha(raw), 'status': d.get('status'),
                    'cell': d.get('cell'), 'horizon': d.get('horizon'), 'suite': d.get('score_suite'),
                    'n_videos': d.get('n_videos'), 'counts': d.get('counts'), 'per_dim': d.get('per_dim'),
                    'per_video_csv': str(pv.relative_to(root)) if pv.is_file() else None,
                    'per_video_sha256': sha(pv.read_bytes()) if pv.is_file() else None,
                    'provenance_path': str(prov.relative_to(root)) if prov.is_file() else None,
                    'provenance_sha256': sha(prov.read_bytes()) if prov.is_file() else None})
            except (OSError, ValueError, KeyError) as exc:
                errors.append({'path': str(summary.relative_to(root)), 'error': str(exc)})
    # These staging files represent distinct versions/horizons/windows; do not deduplicate by scene.
    for stage in sorted(base.glob('*/*/seed*/sourcefixed_*/**/staging')):
        records = []
        for path in sorted(stage.glob('*.json')):
            try:
                raw = path.read_bytes()
                d = json.loads(raw)
                records.append({'scene_id': d.get('scene_id'), 'status': 'record_present',
                    'path': str(path.relative_to(root)), 'record_sha256': sha(raw),
                    'video_sha256': d.get('video_sha256'), 'source_sha256': d.get('source_sha256'),
                    'mask_sha256': (d.get('mask_sha256') or {}).get('labels') if isinstance(d.get('mask_sha256'), dict) else None,
                    'scorer_sha256': d.get('scorer_sha256'), 'actual_seed': d.get('seed'),
                    'horizon_s': d.get('horizon_s'), 'motion_abstained': d.get('motion_abstained'),
                    'fBD_abstained': d.get('fBD_abstained')})
            except (OSError, ValueError) as exc:
                errors.append({'path': str(path.relative_to(root)), 'error': str(exc)})
        if records:
            groups.append({'type': 'sourcefixed_staging', 'path': str(stage.relative_to(root)),
                           'n_records': len(records), 'records': records})
    with legacy.open(newline='') as f:
        rows = list(csv.DictReader(f))
    legacy_groups = Counter((r['track'], r['model'], r['duration'], r['metric']) for r in rows)
    return {'status': 'complete_with_errors' if errors else 'complete',
        'scope': 'read-only index of sourcefixed staging and VBench per-video summaries in factorial scores; legacy SNF CSV groups; not a global disk search',
        'source_root': str(root), 'legacy_csv': str(legacy), 'legacy_csv_sha256': sha(legacy.read_bytes()),
        'legacy_rows': len(rows), 'legacy_groups': [{'track': t, 'model': m, 'duration': d, 'metric': k, 'n_rows': n} for (t,m,d,k),n in sorted(legacy_groups.items())],
        'groups': groups, 'errors': errors,
        'warnings': ['record presence is not proof of completeness or validity', 'sourcefixed windows and horizon types are separate',
                     'legacy filenames/partial fingerprints are not sufficient to establish exact video identity',
                     'active external jobs can change files after this snapshot', 'CSV src_sha256 denotes input video, not conditioning image']}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--method-root', type=Path, required=True)
    p.add_argument('--legacy-csv', type=Path, default=Path('manifest/per_video_scores.csv'))
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): p.error('output exists')
    report = inventory(args.method_root, args.legacy_csv)
    tmp = args.output.with_suffix(args.output.suffix + '.tmp')
    tmp.write_text(json.dumps(report, indent=1, allow_nan=False) + '\n')
    tmp.replace(args.output)
    print('groups', len(report['groups']), 'errors', len(report['errors']), 'legacy rows', report['legacy_rows'])
    return 0 if report['status'] == 'complete' else 1


if __name__ == '__main__':
    raise SystemExit(main())

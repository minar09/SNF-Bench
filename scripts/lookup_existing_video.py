"""Find known video-hash evidence in a bounded score inventory, without scoring."""
import argparse
import json
from pathlib import Path
import re


def lookup(inventory, video_sha256):
    if not re.fullmatch(r'[0-9a-f]{64}', video_sha256):
        raise ValueError('video hash must be lowercase SHA256')
    root = Path(inventory['source_root'])
    hits, errors = [], []
    for group in inventory['groups']:
        if group['type'] == 'sourcefixed_staging':
            for rec in group['records']:
                if rec.get('video_sha256') == video_sha256:
                    hits.append({'type': 'sourcefixed_record', 'path': rec['path'], 'scene_id': rec['scene_id'],
                                 'record_sha256': rec['record_sha256'], 'scorer_sha256': rec['scorer_sha256']})
        elif group['type'] == 'vbench_summary' and group.get('provenance_path'):
            try:
                path = root / group['provenance_path']
                raw = path.read_bytes()
                import hashlib
                if hashlib.sha256(raw).hexdigest() != group['provenance_sha256']:
                    raise ValueError('provenance changed since inventory snapshot')
                prov = json.loads(raw)
                for sid, value in (prov.get('input_video_sha256') or {}).items():
                    if value == video_sha256:
                        hits.append({'type': 'vbench_summary', 'path': group['path'], 'scene_id': sid,
                                     'suite': group['suite'], 'status': group['status'],
                                     'provenance_sha256': group['provenance_sha256'], 'per_video_csv': group['per_video_csv']})
            except (OSError, ValueError) as exc:
                errors.append({'path': group['provenance_path'], 'error': str(exc)})
    return {'video_sha256': video_sha256, 'matches': hits, 'errors': errors,
            'limitations': ['bounded inventory only; absence does not prove no score exists',
                            'a video hash hit does not establish matching metric, version, mask or eligibility',
                            'legacy score rows without full video hashes are not searched']}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--inventory', type=Path, required=True)
    p.add_argument('--video-sha256', required=True)
    a = p.parse_args()
    print(json.dumps(lookup(json.loads(a.inventory.read_text()), a.video_sha256), indent=2))


if __name__ == '__main__':
    main()

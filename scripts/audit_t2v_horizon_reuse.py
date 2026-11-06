#!/usr/bin/env python3
"""Inventory existing v1.1 long-horizon scores without decoding or rescoring video."""
import argparse
import glob
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import registry  # noqa: E402


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        raise SystemExit(f'refusing to overwrite {out}')
    rows = []
    for model in registry.contestants('t2v'):
        for horizon in ('120s', '240s'):
            key = model['key']
            folder = ROOT / 'videos' / 't2v' / key / horizon
            videos = sorted(Path(p).name for p in glob.glob(str(folder / '*.mp4')))
            path = ROOT / 'raw' / 't2v' / key / horizon / 'snf_task_metrics.json'
            if not path.exists():
                rows.append(dict(model=key, horizon=horizon, videos=len(videos), score_file=None))
                continue
            record = json.loads(path.read_text())
            per_video = record.get('per_video', [])
            scored = [r.get('video') for r in per_video]
            rows.append(dict(model=key, horizon=horizon, videos=len(videos), records=len(scored),
                             missing_basenames=sorted(set(videos) - set(scored)),
                             extra_basenames=sorted(str(x) for x in set(scored) - set(videos)),
                             duplicate_score_basenames=sorted({x for x in scored if scored.count(x) > 1}),
                             spec=record.get('metric_spec_version'), score_file=str(path.relative_to(ROOT)),
                             score_sha256=file_hash(path),
                             records_with_video_hash=sum(bool(r.get('video_sha256') or r.get('sha256')) for r in per_video)))
    report = dict(scope='Historical T2V 120s and 240s; inventory only; no video was decoded or scored',
                  caveat='Basename and score-file hash are not proof that video bytes match the original scored input. '
                         'Independent video-hash provenance must be verified before exact reuse is asserted.', rows=rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x') as f:
        json.dump(report, f, indent=2)
    print(f'{out}: {len(rows)} model/horizon cells inventoried')


if __name__ == '__main__':
    main()

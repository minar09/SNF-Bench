"""Check locally indexed Helios checkpoint shards without loading weights."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/home/minar/ckpt/Helios')
OUT = Path('manifest/helios_local_index_audit_2026_10_30.json')
rows = []
for model in sorted(ROOT.iterdir()):
    for index in sorted(model.glob('*/*.index.json')):
        raw = index.read_bytes()
        files = sorted(set(json.loads(raw).get('weight_map', {}).values()))
        rows.append({'model_directory': model.name, 'component': index.parent.name,
                     'index_filename': index.name, 'index_sha256': hashlib.sha256(raw).hexdigest(),
                     'shards': [{'filename': name, 'exists': (index.parent / name).is_file(),
                                 'size_bytes': (index.parent / name).stat().st_size if (index.parent / name).is_file() else None}
                                for name in files]})
report = {'status': 'complete', 'scope': 'index and file existence only; no weight hashes, content integrity, version identity, or inference validation',
          'root_symlink_target': str(ROOT.resolve()), 'rows': rows}
if OUT.exists():
    raise SystemExit('output exists')
OUT.write_text(json.dumps(report, indent=2) + '\n')
print('checked', len(rows), 'indexes;', sum(not s['exists'] for r in rows for s in r['shards']), 'missing shards')

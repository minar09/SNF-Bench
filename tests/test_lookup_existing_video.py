import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lookup_existing_video import lookup


def test_lookup_distinguishes_stale_provenance_and_hash_hits(tmp_path):
    h = 'a' * 64
    provenance = tmp_path / 'prov.json'
    provenance.write_text(json.dumps({'input_video_sha256': {'s1': h}}))
    digest = hashlib.sha256(provenance.read_bytes()).hexdigest()
    inventory = {'source_root': str(tmp_path), 'groups': [
        {'type': 'sourcefixed_staging', 'records': [{'video_sha256': h, 'path': 'record', 'scene_id': 's1',
                                                     'record_sha256': 'r', 'scorer_sha256': 's'}]},
        {'type': 'vbench_summary', 'provenance_path': 'prov.json', 'provenance_sha256': digest,
         'path': 'summary', 'suite': 'vbench_i2v', 'status': 'complete', 'per_video_csv': 'rows.csv'}]}
    assert len(lookup(inventory, h)['matches']) == 2
    provenance.write_text('{}')
    out = lookup(inventory, h)
    assert len(out['matches']) == 1
    assert 'changed' in out['errors'][0]['error']
    with pytest.raises(ValueError):
        lookup(inventory, 'not a hash')

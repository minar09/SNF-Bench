import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from compare_parity_cells import build


def make_report(path, source='x', mask='m', score=1.0, status='PASS'):
    row = {'scene_id': 'a', 'category': 'channel', 'source_sha256': source, 'mask_sha256': mask,
           'scores': {'fBD_src': {'rescore': score}}, 'abstentions': {}}
    path.write_text(json.dumps({'status': status, 'measurement': 'v', 'cell': 'cfpp/a/seed42',
                                'rows': [row], 'requested_scenes': ['a'], 'port_sha256': 'p',
                                'upstream_scorer_sha256': 'u', 'mask_manifest_sha256': 'm'}))


def test_pair_uses_only_matching_source_and_mask(tmp_path):
    a, b = tmp_path / 'a', tmp_path / 'b'
    make_report(a)
    make_report(b, score=2.0)
    result = build(a, b)
    assert result['summary']['fBD_src'] == {'n_paired': 1, 'median_difference': 1.0}
    make_report(b, mask='other')
    with pytest.raises(ValueError, match='hashes differ'):
        build(a, b)


def test_incomplete_run_rejected(tmp_path):
    a, b = tmp_path / 'a', tmp_path / 'b'
    make_report(a)
    make_report(b, status='running')
    with pytest.raises(ValueError, match='complete'):
        build(a, b)

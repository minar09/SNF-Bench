import csv
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from compare_existing_snf_vbench import compare


def fixture_cell(root, cell, video, source='a' * 64, score=0.9):
    p = root / cell / 'seed42'
    stage = p / 'sourcefixed_60s/staging'
    stage.mkdir(parents=True)
    rec = {'scene_id': 'scene', 'horizon_s': 60, 'source_sha256': source, 'video_sha256': video,
           'mask_sha256': {'labels': 'b' * 64}, 'scorer_sha256': 'c' * 64, 'seed': 44,
           'category': 'test', 'fBD_src': 1.0, 'MCFF_late': 2.0, 'idPSNR_late_src': 3.0,
           'motion_abstained': False, 'fBD_abstained': False}
    (stage / 'scene.json').write_text(json.dumps(rec))
    for suite, rel, dim in [('i2v', 'vbench_i2v/60s/i2v', 'i2v_subject'),
                             ('long', 'vbench_long/60s/long', 'dynamic_degree')]:
        d = p / rel
        d.mkdir(parents=True)
        prov = {'repository_revision': 'revision', 'entry_file_sha256': 'entry', 'official_args': ['x'],
                'dev_flag': None, 'input_video_sha256': {'scene': video},
                'source_image_sha256': {'scene': source}}
        (d / 'provenance.json').write_text(json.dumps(prov))
        (d / 'summary.json').write_text(json.dumps({'status': 'complete'}))
        with (d / 'per_video.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['scene_id', 'dim', 'src_sha256', 'seed', 'value', 'status'])
            w.writeheader()
            w.writerow({'scene_id': 'scene', 'dim': dim, 'src_sha256': video, 'seed': 44,
                        'value': score, 'status': 'ok'})


def test_pairs_same_source_and_video_provenance(tmp_path):
    fixture_cell(tmp_path, 'a', 'd' * 64, score=0.5)
    fixture_cell(tmp_path, 'b', 'e' * 64, score=0.7)
    out = compare(tmp_path, 'a', 'b')
    assert out['summary']['i2v.subject']['n_paired'] == 1
    assert out['summary']['i2v.subject']['mean_paired_difference'] == pytest.approx(0.2)
    assert out['summary']['i2v.background']['n_paired'] == 0


def test_mismatched_image_and_input_video_fail_closed(tmp_path):
    fixture_cell(tmp_path, 'a', 'd' * 64)
    fixture_cell(tmp_path, 'b', 'e' * 64, source='f' * 64)
    with pytest.raises(ValueError, match='source or mask'):
        compare(tmp_path, 'a', 'b')
    path = tmp_path / 'b/seed42/sourcefixed_60s/staging/scene.json'
    rec = json.loads(path.read_text())
    rec['source_sha256'] = 'a' * 64
    path.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match='source image mismatch'):
        compare(tmp_path, 'a', 'b')

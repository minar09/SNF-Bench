"""argv / docker-command construction of scripts/run_i2v_matched.py (no GPU, no docker run)."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('run_i2v_matched', ROOT / 'scripts/run_i2v_matched.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
OUT = R.OUT / 'x' / 'pq0092' / '240s'
DATA = R.STAGE / 'x' / 'pq0092'


def lock():
    return json.loads(R.LOCK.read_text())


def val(argv, k):
    return argv[argv.index(k) + 1]


def test_scenetether_changes_only_allowed_args():
    lk = lock()
    a = R.argv_for('scenetether', DATA, OUT, lk)
    b = lk['run']['argv']
    assert len(a) == len(b)
    changed = {b[i] if b[i].startswith('eval_first_n') else b[i - 1] for i in range(len(a)) if a[i] != b[i]}
    assert changed <= {'--output_folder', '--data_path', '--force_num_frames', '--num_output_frames', 'eval_first_n=7'}
    assert val(a, '--force_num_frames') == '960' and val(a, '--num_output_frames') == '961'
    assert val(a, '--seed') == '42' and 'eval_first_n=1' in a and '--use_ema' in a and '--i2v' in a
    assert val(a, '--output_folder') == '/workspace/snf-bench/' + str(OUT.relative_to(ROOT))
    assert R.SYSTEMS['scenetether']['frames'] == 3841


@pytest.mark.parametrize('system,cfg,ckpt,ema,frames', [
    ('cfpp_f2s', 'configs/causal_forcing_dmd_f2s_steady.yaml', '../ckpt/causal-forcing++/framewise-2step.pt', True, 3837),
    ('causvid_i2v', 'configs/causal_forcing_dmd_f2s_steady_chunk6.yaml', '../ckpt/CausVid/autoregressive_checkpoint/model.pt', False, 3841),
    ('self_forcing_i2v', 'configs/causal_forcing_dmd_f2s_steady_chunk6.yaml', '../ckpt/Self-Forcing/checkpoints/self_forcing_dmd.pt', False, 3841),
])
def test_rf_argv_matches_run_eval_ours(system, cfg, ckpt, ema, frames):
    a = R.argv_for(system, DATA, OUT)
    assert a[:2] == ['python', 'inference.py']
    assert val(a, '--config_path') == cfg and val(a, '--checkpoint_path') == ckpt
    assert ('--use_ema' in a) is ema and '--i2v' in a and val(a, '--seed') == '0'
    assert '--force_num_frames' not in a and '--num_output_frames' not in a     # length from the [240s] marker
    assert R.SYSTEMS[system]['frames'] == frames
    sh = (R.RF / 'scripts/eval/run_eval_ours.sh').read_text()
    assert f"{R.SYSTEMS[system]['method']})" in sh and ckpt in sh


def test_docker_mounts_home_read_only_and_snf_writable():
    c = R.docker_cmd('cfpp_f2s', 'pq0092', 3, ['python'])
    assert '/home/minar:/workspace:ro' in c and f'{R.ROOT}:/workspace/snf-bench' in c
    assert val(c, '--gpus') == 'device=3' and val(c, '-w') == '/workspace/region-forcing'
    assert c[c.index(R.IMAGE) + 1:] == ['python']
    s = R.docker_cmd('scenetether', 'pq0092', 2, ['python'], Path('/snap'))
    assert '/snap/pipeline:/workspace/ar-image-animation/pipeline:ro' in s and 'SNF_PER_PROMPT_SEED=1' in s


def test_caption_is_manifest_text_plus_marker():
    sc = R.scenes()['pq0092']
    info = R.crop_info('cfpp_f2s', sc)[0]
    assert info['caption'] == sc['text'] + '[240s]' and info['target_crop']['target_ratio'] == '16-9'
    assert R.crop_info('scenetether', sc)[0]['target_crop']['target_ratio'] == '26-15'

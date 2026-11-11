#!/usr/bin/env python3
"""One 240 s T2V render of a v2 prompt by a published checkpoint, in the historical common wrapper.

The matched journal set (2026-11-10): the first prompt of each of the nine v2 categories
(manifest/prompts_v2.json; screened against the Steady-Forcing, SceneTether and Region-Forcing
trees on 2026-11-10 with no text or filename hit) x the eight published T2V checkpoints.
Horizons 60/120/240 s are prefixes of this one rollout, so the trajectory is within-rollout.

Setting, disclosed: every checkpoint runs through Steady-Forcing's `inference.py` with
`configs/steady_forcing_infer.yaml` (EMA sink 3 + local attention 18), exactly as the historical
SNF-Bench T2V panel (static-forcing/inference_*_t2v.sh). That is a common long-video wrapper, not
each method's released native long rollout. `wan/modules/causal_model.py` is replaced read-only by
the isolated copy whose only change removes a shadowing local `import os` (the 2026-11-09 CausVid
retry); both hashes are recorded. Seed 0. Outputs are new and never overwritten.

    python scripts/run_t2v_matched.py --model self_forcing --scene fp01 --gpu 2
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('/home/minar/static-forcing')
CONFIG = REPO / 'configs/steady_forcing_infer.yaml'
PROMPTS = ROOT / 'manifest/prompts_v2.json'
PATCHED_MODEL = ROOT / '.metric_staging/t2v_unbound_os_fix_2026_11_09/causal_model.py'
OUT = ROOT / 'videos/journal_matched_2026_11_10/t2v'
MIN_BYTES = 110_000_000_000
SCENES = ('cf01', 'fp01', 'ow01', 'al01', 'bp01', 'cb01', 'wb01', 'gt01', 'fw01')
# checkpoint (relative to /home/minar/ckpt) and --use_ema, as in static-forcing/inference_*_t2v.sh
MODELS = {
    'causvid': ('CausVid/autoregressive_checkpoint/model.pt', False),
    'self_forcing': ('Self-Forcing/checkpoints/self_forcing_dmd.pt', True),
    'infinite_forcing': ('SOTAMak1r/Infinite-Forcing/ema_model.pt', True),
    'rolling_forcing': ('RollingForcing/checkpoints/rolling_forcing_dmd.pt', True),
    'reward_forcing': ('rewardforcing.pt', True),
    'longlive': ('longlive_models/models/longlive_base.pt', True),
    'causal_forcing': ('causal-forcing/chunkwise/causal_forcing.pt', False),
    'steady_forcing': ('Steady-Forcing/steady_forcing_t2v.pt', True),
}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(4 << 20), b''):
            h.update(b)
    return h.hexdigest()


def gpu_free(gpu):
    rows = [r.split(', ') for r in subprocess.check_output(
        ['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader'], text=True, timeout=15).splitlines()]
    uuid = next(u for i, u in rows if int(i) == gpu)
    apps = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid', '--format=csv,noheader'],
                                   text=True, timeout=15).split()
    return uuid not in apps


def disk_ok():
    st = os.statvfs('/')
    return st.f_bavail * st.f_frsize >= MIN_BYTES


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--model', required=True, choices=sorted(MODELS))
    a.add_argument('--scene', required=True, choices=SCENES)
    a.add_argument('--gpu', required=True, type=int, choices=(2, 3))
    args = a.parse_args()
    scene = next(s for s in json.loads(PROMPTS.read_text())['scenes'] if s['id'] == args.scene)
    ckpt_rel, ema = MODELS[args.model]
    ckpt = Path('/home/minar/ckpt') / ckpt_rel
    out = OUT / args.model / args.scene / '240s'
    if out.exists():
        raise SystemExit(f'{out} exists; refusing to overwrite or duplicate')
    if not disk_ok() or not gpu_free(args.gpu):
        raise SystemExit(f'GPU {args.gpu} busy or / below the 110 GB guard; nothing started')
    if not PATCHED_MODEL.is_file():
        raise SystemExit('isolated causal_model.py fix is missing')
    out.mkdir(parents=True)
    prompt = out / 'prompt.txt'
    prompt.write_text(scene['text'] + ' [240s]\n')
    image = subprocess.check_output(['docker', 'image', 'inspect', 'regfor:cuda12.1', '--format', '{{.Id}}'],
                                    text=True, timeout=30).strip()
    info = dict(status='running', role='journal matched T2V render; development data, not confirmation',
                scene=args.scene, category=scene['category'], prompt=scene['text'],
                prompt_sha256=hashlib.sha256(scene['text'].encode()).hexdigest(), prompt_file_sha256=sha(prompt),
                requested_s=240, model=args.model, checkpoint=str(ckpt), checkpoint_sha256=sha(ckpt), use_ema=ema,
                setting='historical common inference wrapper (Steady-Forcing inference.py + steady_forcing_infer.yaml), '
                        'not the released native long rollout',
                seed=0, config_sha256=sha(CONFIG), image_id=image,
                code_commit=subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip(),
                inference_sha256=sha(REPO / 'inference.py'),
                original_model_sha256=sha(REPO / 'wan/modules/causal_model.py'), patched_model_sha256=sha(PATCHED_MODEL),
                adaptation='remove shadowing local os import; module-level os import is used', gpu=args.gpu)
    if not disk_ok() or not gpu_free(args.gpu):
        info.update(status='not_started', reason='GPU or disk changed during provenance hashing')
        (out / 'RUN.final.json').write_text(json.dumps(info, indent=2) + '\n')
        raise SystemExit(info['reason'])
    cout = '/workspace/snf-bench/' + str(out.relative_to(ROOT))
    cmd = ['docker', 'run', '--rm', '--gpus', f'device={args.gpu}', '--shm-size=16g',
           '-v', f'{REPO}:/workspace/static-forcing:ro',
           '-v', f'{PATCHED_MODEL}:/workspace/static-forcing/wan/modules/causal_model.py:ro',
           '-v', '/home/minar/ckpt:/workspace/ckpt:ro', '-v', f'{ROOT}:/workspace/snf-bench',
           '-w', '/workspace/static-forcing', '-e', 'HF_HUB_OFFLINE=1', '-e', 'PYTHONDONTWRITEBYTECODE=1',
           'regfor:cuda12.1', 'python', 'inference.py', '--config_path', 'configs/steady_forcing_infer.yaml',
           '--checkpoint_path', '../ckpt/' + ckpt_rel, '--output_folder', cout,
           '--data_path', cout + '/prompt.txt', '--seed', '0'] + (['--use_ema'] if ema else [])
    info['command'] = cmd
    (out / 'RUN.json').write_text(json.dumps(info, indent=2) + '\n')
    t0 = time.monotonic()
    with (out / 'inference.log').open('x') as log:
        res = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    vids = sorted(out.glob('*.mp4'))
    info.update(status='complete' if res.returncode == 0 and len(vids) == 1 else 'failed', exit_code=res.returncode,
                elapsed_s=time.monotonic() - t0,
                outputs=[dict(name=p.name, sha256=sha(p), bytes=p.stat().st_size) for p in vids])
    (out / 'RUN.final.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps(dict(model=args.model, scene=args.scene, status=info['status'],
                          elapsed_s=round(info['elapsed_s']))), flush=True)
    if info['status'] != 'complete':
        raise SystemExit('generation failed; see inference.log')


if __name__ == '__main__':
    main()

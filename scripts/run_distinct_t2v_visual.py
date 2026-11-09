#!/usr/bin/env python3
"""Generate one new 240 s T2V visual using the historical common configuration.

Runs only one explicitly specified scene at a time. Outputs and logs are new;
existing videos/scores are untouched. The run is development visual material,
not an official native-pipeline result or an independent confirmation set.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('/home/minar/static-forcing')
CKPT = Path('/home/minar/ckpt/CausVid/autoregressive_checkpoint/model.pt')
CONFIG = REPO / 'configs/steady_forcing_infer.yaml'
PLAN = ROOT / 'manifest/journal_distinct_track_visual_plan_2026_11_08.json'
PATCHED_MODEL = ROOT / '.metric_staging/t2v_unbound_os_fix_2026_11_09/causal_model.py'
MIN_BYTES = 110_000_000_000


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def gpu_free(gpu):
    devs = subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,memory.used',
                                    '--format=csv,noheader,nounits'], text=True, timeout=15)
    entries = [[s.strip() for s in line.split(',')] for line in devs.splitlines()]
    found = [r for r in entries if int(r[0]) == gpu]
    if len(found) != 1:
        raise RuntimeError('GPU identity not found uniquely')
    apps = subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid',
                                    '--format=csv,noheader'], text=True, timeout=15)
    return int(found[0][2]) < 100 and found[0][1] not in apps.splitlines()


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--scene', required=True, choices=('cf01','cb01'))
    a.add_argument('--gpu', required=True, type=int, choices=(2,3))
    args = a.parse_args()
    plan = json.loads(PLAN.read_text())
    scene = next(x for x in plan['t2v']['scenes'] if x['scene_id'] == args.scene)
    if hashlib.sha256(scene['prompt'].encode()).hexdigest() != scene['prompt_sha256']:
        raise SystemExit('prompt hash mismatch')
    out = ROOT / f'videos/journal_distinct_visual_2026_11_09/t2v/causvid_common/{args.scene}/240s_retry1'
    if out.exists():
        raise SystemExit(f'{out} exists; refusing to overwrite or duplicate')
    if os.statvfs('/').f_bavail * os.statvfs('/').f_frsize < MIN_BYTES:
        raise SystemExit('root disk below 110 GB guard')
    if not gpu_free(args.gpu):
        raise SystemExit(f'GPU {args.gpu} has another compute process')
    image = subprocess.check_output(['docker','image','inspect','regfor:cuda12.1','--format','{{.Id}}'],
                                    text=True, timeout=30).strip()
    out.mkdir(parents=True)
    prompt = out / 'prompt.txt'
    prompt.write_text(scene['prompt'] + ' [240s]\n')
    cfg_hash, checkpoint_hash = sha(CONFIG), sha(CKPT)
    if not PATCHED_MODEL.is_file():
        raise SystemExit('isolated inference fix is missing')
    if not gpu_free(args.gpu) or os.statvfs('/').f_bavail * os.statvfs('/').f_frsize < MIN_BYTES:
        raise SystemExit('GPU or disk changed during provenance hashing; no generation started')
    container_out = '/workspace/snf-bench/' + str(out.relative_to(ROOT))
    cmd = ['docker','run','--rm','--gpus',f'device={args.gpu}','--shm-size=16g',
           '-v','/home/minar/static-forcing:/workspace/static-forcing:ro',
           '-v',f'{PATCHED_MODEL}:/workspace/static-forcing/wan/modules/causal_model.py:ro',
           '-v','/home/minar/ckpt:/workspace/ckpt:ro',
           '-v','/home/minar/snf-bench:/workspace/snf-bench',
           '-w','/workspace/static-forcing','-e','HF_HUB_OFFLINE=1','-e','PYTHONDONTWRITEBYTECODE=1',
           'regfor:cuda12.1','python','inference.py','--config_path','configs/steady_forcing_infer.yaml',
           '--checkpoint_path','../ckpt/CausVid/autoregressive_checkpoint/model.pt',
           '--output_folder',container_out,'--data_path',container_out+'/prompt.txt','--seed','0']
    info = dict(status='running', role='development visual; not confirmation', scene=args.scene,
                prompt_sha256=scene['prompt_sha256'], prompt_file_sha256=sha(prompt), requested_s=240,
                model='CausVid', setting='historical common inference wrapper, not released native pipeline',
                seed=0, config_sha256=cfg_hash, checkpoint_sha256=checkpoint_hash, image_id=image,
                code_commit=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),
                inference_sha256=sha(REPO/'inference.py'),
                original_model_sha256=sha(REPO/'wan/modules/causal_model.py'),
                patched_model_sha256=sha(PATCHED_MODEL),
                adaptation='remove shadowing local os import; module-level os import is used',
                command=cmd, gpu=args.gpu)
    record = out / 'RUN.json'
    record.write_text(json.dumps(info,indent=2)+'\n')
    started = time.monotonic()
    with (out / 'inference.log').open('x') as log:
        result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    videos = list(out.glob('*.mp4'))
    info.update(status='complete' if result.returncode == 0 and len(videos) == 1 else 'failed',
                exit_code=result.returncode, elapsed_s=time.monotonic()-started,
                outputs=[dict(name=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in videos])
    (out/'RUN.final.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(dict(scene=args.scene,status=info['status'],outputs=info['outputs'])),flush=True)
    if info['status'] != 'complete':
        raise SystemExit('generation failed; inspect inference.log and preserve outputs')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""One new SVI Pro 60s development visual, on GPU 3 when safely idle.

The input is an exposed public-figure source, not a held-out test scene. This
pilot uses the method-project runner and records its deviation from upstream.
It never overwrites a run, retries a failed run or changes the other project.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from wait_fp_freeze_gpu import available

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('/home/minar/Stable-Video-Infinity-wan22')
AIA = Path('/home/minar/ar-image-animation')
CKPT = Path('/home/minar/ckpt')
OUT = ROOT / 'videos/journal_distinct_visual_2026_11_09/i2v/svi_pro/vb161950/60s'
SCENE = 'vb161950'
MIN_BYTES = 110_000_000_000


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    if OUT.exists():
        raise SystemExit('output exists; inspect it rather than duplicate it')
    spec = json.loads((ROOT/'manifest/public_figure_set_2026_11_05.json').read_text())
    scene = next(s for s in spec['scenes'] if s['id'] == SCENE)
    source = ROOT / scene['image']
    if sha(source) != scene['image_sha256']:
        raise SystemExit('source hash mismatch')
    runner = AIA/'tools/run_svi_pro_native.py'
    pipeline = REPO/'diffsynth/pipelines/wan_video_svi_pro.py'
    lora = CKPT/'Stable-Video-Infinity/version-2.0'
    weights = CKPT/'wan_models/Wan2.2-I2V-A14B'
    files = sorted((weights/'high_noise_model').glob('diffusion_pytorch_model*.safetensors'))
    files += sorted((weights/'low_noise_model').glob('diffusion_pytorch_model*.safetensors'))
    files += [weights/'models_t5_umt5-xxl-enc-bf16.pth', weights/'Wan2.1_VAE.pth',
              lora/'SVI_Wan2.2-I2V-A14B_high_noise_lora_v2.0_pro.safetensors',
              lora/'SVI_Wan2.2-I2V-A14B_low_noise_lora_v2.0_pro.safetensors']
    if len(files) < 6 or not all(p.is_file() for p in files):
        raise SystemExit('incomplete SVI weights')
    print('Hashing SVI input files before GPU scheduling', flush=True)
    hashes = {str(p): sha(p) for p in files}
    image = subprocess.check_output(['docker','image','inspect','wan22:cuda12.1',
                                     '--format','{{.Id}}'],text=True).strip()
    while True:
        if OUT.exists():
            raise SystemExit('output appeared while waiting; refusing duplication')
        if 3 in available():
            time.sleep(60)
            if 3 in available():
                break
        print('Waiting for GPU 3 and disk guards', flush=True)
        time.sleep(60)
    OUT.mkdir(parents=True)
    target = '/workspace/snf-bench/' + str(OUT.relative_to(ROOT)) + '/video.mp4'
    source_in = '/workspace/snf-bench/' + str(source.relative_to(ROOT))
    cmd = ['docker','run','--rm','--gpus','device=3','--shm-size=16g',
           '-v',f'{REPO}:/workspace/svi_wan22:ro',
           '-v',f'{AIA}:/workspace/ar-image-animation:ro',
           '-v',f'{CKPT}:/workspace/ckpt:ro',
           '-v',f'{ROOT}:/workspace/snf-bench',
           '-w','/workspace/svi_wan22','-e','HF_HUB_OFFLINE=1',
           '-e','PYTHONDONTWRITEBYTECODE=1','-e','PYTHONUNBUFFERED=1',
           'wan22:cuda12.1','python','/workspace/ar-image-animation/tools/run_svi_pro_native.py',
           '--image',source_in,'--prompt',scene['text'],'--out',target,'--num_clips','12']
    info = {'status':'running','role':'exposed development visual; not confirmation',
            'scene_id':SCENE,'source_sha256':scene['image_sha256'],
            'prompt_sha256':hashlib.sha256(scene['text'].encode()).hexdigest(),
            'requested_s':60,'gpu':3,'image_id':image,'command':cmd,
            'runner_sha256':sha(runner),'pipeline_sha256':sha(pipeline),
            'weight_sha256':hashes,
            'repo_commit':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),
            'repo_status':subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True).splitlines(),
            'deviation':'method-project wrapper uses seed + 123*k; 917 frames at 15 fps',
            'licence':scene['licence'],'licence_url':scene['licence_url']}
    (OUT/'RUN.json').write_text(json.dumps(info,indent=2)+'\n')
    if 3 not in available() or os.statvfs('/').f_bavail * os.statvfs('/').f_frsize < MIN_BYTES:
        (OUT/'RUN.final.json').write_text(json.dumps({**info,'status':'aborted_before_launch'},indent=2)+'\n')
        raise SystemExit('GPU or disk changed; no generation started')
    start = time.monotonic()
    with (OUT/'inference.log').open('x') as log:
        r = subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
    video = OUT/'video.mp4'
    metadata = OUT/'video.mp4.json'
    details = json.loads(metadata.read_text()) if metadata.is_file() else None
    valid = bool(r.returncode == 0 and video.is_file() and details and
                 details.get('frames') == 917 and details.get('fps') == 15)
    info.update(status='complete' if valid else 'failed',exit_code=r.returncode,
                elapsed_s=time.monotonic()-start, realized=details,
                output_sha256=sha(video) if video.is_file() else None)
    (OUT/'RUN.final.json').write_text(json.dumps(info,indent=2)+'\n')
    if not valid:
        raise SystemExit('SVI failed or output is incomplete; inspect the log')
    print('SVI development visual completed', flush=True)


if __name__ == '__main__':
    main()

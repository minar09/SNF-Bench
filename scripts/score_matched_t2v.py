#!/usr/bin/env python3
"""Frozen SNF v1.1 scores of one matched 240 s T2V rollout at the 60, 120 and 240 s horizons.

The horizons are prefixes of the same rollout (window policy `prefix`), not separate endpoint
generations, so they form a within-rollout trajectory and must never be pooled with the historical
whole-file 60/120/240 s records (different prompts, separate generations). Prefixes are lossless cuts
(libx264 -qp 0, yuv420p, passthrough timing) of the first 16*H + 1 frames, verified frame by frame by
framemd5 against the source; the 240 s horizon is the original file itself. Each file is then scored
unchanged by scripts/metric_worker.py --spec 1.1 (the frozen T2V path: Otsu masks on early flow,
WIN_FRAC 0.12 of the scored file), so a 60 s prefix is measured exactly as a 60 s video would be.

    python scripts/score_matched_t2v.py --model steady_forcing --scene cf01 --gpu 3
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
VIDEOS = ROOT / 'videos/journal_matched_2026_11_10/t2v'
SCORES = ROOT / 'raw_matched_2026_11_10/t2v'
FFMPEG = '/home/minar/miniconda3/envs/helios/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'  # the method project's verified-cut build (has libx264)
PY = '/home/minar/miniconda3/envs/snfeval/bin/python'
FPS = 16
HORIZONS = (60, 120, 240)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(4 << 20), b''):
            h.update(b)
    return h.hexdigest()


def framemd5(path, n):
    out = subprocess.run([FFMPEG, '-nostdin', '-v', 'error', '-i', str(path), '-map', '0:v:0', '-frames:v', str(n),
                          '-f', 'framemd5', '-'], capture_output=True, text=True, check=True).stdout
    return [line.split(',')[-1].strip() for line in out.splitlines() if line and not line.startswith('#')]


def cut_prefix(src, n, dst):
    """Lossless prefix of the first n frames, verified by framemd5; returns its record."""
    if not dst.exists():
        tmp = dst.with_suffix('.part.mp4')
        subprocess.run([FFMPEG, '-nostdin', '-hide_banner', '-v', 'error', '-y', '-i', str(src), '-map', '0:v:0',
                        '-frames:v', str(n), '-an', '-sn', '-dn', '-c:v', 'libx264', '-preset', 'veryfast', '-qp', '0',
                        '-pix_fmt', 'yuv420p', '-fps_mode', 'passthrough', str(tmp)], check=True)
        a, b = framemd5(src, n), framemd5(tmp, n)
        if len(b) != n or a != b:
            tmp.unlink()
            raise SystemExit(f'{dst}: prefix is not frame-identical to the source ({len(b)} of {n} frames)')
        tmp.rename(dst)
    return dict(path=str(dst.relative_to(ROOT)), frames=n, sha256=sha(dst), verified='framemd5 identical to source')


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--model', required=True)
    a.add_argument('--scene', required=True)
    a.add_argument('--gpu', required=True, type=int, choices=(2, 3))
    args = a.parse_args()
    run_dir = VIDEOS / args.model / args.scene / '240s'
    run = json.loads((run_dir / 'RUN.final.json').read_text())
    if run.get('status') != 'complete':
        raise SystemExit('render is not complete')
    src = run_dir / run['outputs'][0]['name']
    if sha(src) != run['outputs'][0]['sha256']:
        raise SystemExit('render hash differs from its RUN.final.json')
    out = SCORES / args.model / args.scene / 'snf'
    done = out / 'SCORE.json'
    if done.exists():
        raise SystemExit(f'{done} exists; scores are never overwritten')
    out.mkdir(parents=True, exist_ok=True)
    total = int(subprocess.run([FFMPEG, '-nostdin', '-v', 'error', '-i', str(src), '-map', '0:v:0', '-f', 'framemd5',
                                '-'], capture_output=True, text=True, check=True).stdout.count('\n0,'))
    pre = out / 'prefixes'
    pre.mkdir(exist_ok=True)
    inputs = {}
    for h in HORIZONS:
        n = FPS * h + 1
        if h == 240 or n >= total:
            inputs[h] = dict(path=str(src.relative_to(ROOT)), frames=total, sha256=run['outputs'][0]['sha256'],
                             verified='original render file')
        else:
            inputs[h] = cut_prefix(src, n, pre / f'p{h:03d}.mp4')
    listing = out / 'videos.txt'
    listing.write_text('\n'.join(str(ROOT / inputs[h]['path']) for h in HORIZONS) + '\n')
    t0 = time.monotonic()
    rc = subprocess.run([PY, str(ROOT / 'scripts/metric_worker.py'), '--videos', str(listing),
                         '--staging', str(out / 'staging'), '--gpu', str(args.gpu), '--spec', '1.1'], cwd=ROOT).returncode
    recs = {}
    for h in HORIZONS:
        name = Path(inputs[h]['path']).name
        f = out / 'staging' / (name + '.json')
        recs[h] = json.loads(f.read_text()) if f.exists() else None
    ok = rc == 0 and all(recs.values())
    rep = dict(status='complete' if ok else 'failed', track='t2v', model=args.model, scene=args.scene,
               category=run.get('category'), prompt_sha256=run.get('prompt_sha256'), render=str(run_dir.relative_to(ROOT)),
               render_setting=run.get('setting'), metric_spec='1.1', scorer='scripts/metric_worker.py',
               scorer_sha256=sha(ROOT / 'scripts/metric_worker.py'),
               window_policy='prefix: first 16*H+1 frames of one 240 s rollout; 240 s = whole file',
               role='journal matched-horizon development scores; never pool with historical whole-file records',
               inputs={str(h): inputs[h] for h in HORIZONS}, records={str(h): recs[h] for h in HORIZONS},
               worker_rc=rc, wall_s=round(time.monotonic() - t0), gpu=args.gpu)
    done.write_text(json.dumps(rep, indent=1) + '\n')
    print(json.dumps(dict(model=args.model, scene=args.scene, status=rep['status'], wall_s=rep['wall_s'])))
    if not ok:
        raise SystemExit('scoring failed; see staging/*.error.json')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Stimuli and annotation inputs for the web human-evaluation page (2026-11-10).

Writes the files published beside the page (human_eval_web_2026_11_10/site/) and a private key that
is never published (human_eval_web_2026_11_10/private/key.json):

* Rating items: one per (complete matched render, horizon 60/120/240 s). Each item shows a
  "beginning" excerpt (2-8 s, shared by the render's three items) and an "end" excerpt (the last
  6 s before the horizon). 96 frames at 16 fps, H.264 CRF 23, 832x480, no audio. Item ids are random
  tokens; the model, scene and horizon are only in the private key, so raters are blind to them.
* Known-answer controls built from one render at 60 s: frozen end, reversed end, ping-pong end.
  They test rater attention and the scale anchors, and are flagged in the key, not on the page.
* Annotation scenes: the 12 public conditioning images and their automatic CLIPSeg role maps
  (masks/public_role_maps_2026_11_10, unreviewed) as row-major run-length strings "v:n,v:n,...".

Re-running adds new renders and keeps every existing item id and file (never overwritten).

    /home/minar/miniconda3/envs/snfeval/bin/python scripts/build_human_eval_stimuli.py
"""
import glob
import hashlib
import json
import os
import secrets
import shutil
import subprocess

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'human_eval_web_2026_11_10')
SITE, PRIV = os.path.join(OUT, 'site'), os.path.join(OUT, 'private')
FFMPEG = '/home/minar/miniconda3/envs/helios/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
FPS, N = 16, 96
BEGIN = 32                      # the beginning excerpt is 2-8 s (skips the conditioning frame and warm-up)
HORIZONS = (60, 120, 240)
LABELS = {'t2v': 'manifest/prompts_v2.json', 'i2v': 'manifest/public_figure_set_2026_11_05.json'}
CONTROL_SRC = ('t2v', 'steady_forcing', 'cf01', 60)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def read_frames(path, idx):
    """Frames at the given sorted indices (sequential decode)."""
    cap, want, out, i = cv2.VideoCapture(path), set(idx), {}, 0
    last = max(idx)
    while i <= last:
        ok, f = cap.read()
        if not ok:
            break
        if i in want:
            out[i] = f
        i += 1
    return [out[k] for k in idx]


def encode(frames, dst):
    if os.path.exists(dst):
        return
    h, w = frames[0].shape[:2]
    p = subprocess.Popen([FFMPEG, '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                          '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'slow',
                          '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst + '.part.mp4'],
                         stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit(f'encode failed: {dst}')
    os.replace(dst + '.part.mp4', dst)


def rle(lab):
    flat = lab.reshape(-1)
    cut = np.flatnonzero(np.diff(flat)) + 1
    starts = np.concatenate([[0], cut])
    lens = np.diff(np.concatenate([starts, [flat.size]]))
    return ','.join(f'{int(flat[s])}:{int(n)}' for s, n in zip(starts, lens))


def scene_meta(track, sid):
    d = json.load(open(os.path.join(ROOT, LABELS[track])))
    return next(s for s in d['scenes'] if s['id'] == sid)


def medium_phrase(s):
    return s['dynamic_medium'].split(',')[0].rstrip('.').strip()


def main():
    for d in ('videos', 'images'):
        os.makedirs(os.path.join(SITE, d), exist_ok=True)
    os.makedirs(PRIV, exist_ok=True)
    key_path = os.path.join(PRIV, 'key.json')
    key = json.load(open(key_path)) if os.path.exists(key_path) else {'items': {}, 'renders': {}}
    have = {(v['track'], v['model'], v['scene'], v['horizon'], v.get('control')): k for k, v in key['items'].items()}

    def new_id():
        while True:
            t = secrets.token_hex(3)
            if t not in key['items'] and t not in key['renders']:
                return t

    runs = sorted(glob.glob(os.path.join(ROOT, 'videos/journal_matched_2026_11_10/*/*/*/240s/RUN.final.json')))
    for run_path in runs:
        run = json.load(open(run_path))
        if run.get('status') != 'complete':
            continue
        track, model, scene = run_path.split(os.sep)[-5:-2]
        src = os.path.join(os.path.dirname(run_path), run['outputs'][0]['name'])
        n_frames = int(cv2.VideoCapture(src).get(cv2.CAP_PROP_FRAME_COUNT))
        rkey = f'{track}/{model}/{scene}'
        rid = next((k for k, v in key['renders'].items() if v['render'] == rkey), None) or new_id()
        meta = scene_meta(track, scene)
        key['renders'][rid] = dict(render=rkey, video_sha256=run['outputs'][0]['sha256'], frames=n_frames)
        begin = f'videos/{rid}_b.mp4'
        jobs = [(begin, list(range(BEGIN, BEGIN + N)))]
        items = []
        for h in HORIZONS:
            last = min(FPS * h, n_frames - 1)
            iid = have.get((track, model, scene, h, None)) or new_id()
            jobs.append((f'videos/{iid}_e.mp4', list(range(last - N + 1, last + 1))))
            items.append((iid, h, last))
        need = sorted({i for _, idx in jobs for i in idx})
        frames = dict(zip(need, read_frames(src, need))) if not all(
            os.path.exists(os.path.join(SITE, p)) for p, _ in jobs) else None
        for p, idx in jobs:
            if frames is not None:
                encode([frames[i] for i in idx], os.path.join(SITE, p))
        for iid, h, last in items:
            key['items'][iid] = dict(track=track, model=model, scene=scene, horizon=h, control=None, render_id=rid,
                                     begin=begin, end=f'videos/{iid}_e.mp4', end_frames=[last - N + 1, last],
                                     medium=medium_phrase(meta), direction=meta.get('direction'),
                                     category=meta.get('category'))
        if (track, model, scene) == CONTROL_SRC[:3]:
            last = FPS * CONTROL_SRC[3]
            seg = list(range(last - N + 1, last + 1))
            fr = dict(zip(seg, read_frames(src, seg)))
            ctl = {'freeze': [fr[seg[0]]] * N, 'reverse': [fr[i] for i in reversed(seg)],
                   'pingpong': ([fr[i] for i in seg[-24:]] + [fr[i] for i in reversed(seg[-24:])]) * 2}
            for name, frs in ctl.items():
                iid = have.get((track, model, scene, CONTROL_SRC[3], name)) or new_id()
                encode(frs, os.path.join(SITE, f'videos/{iid}_e.mp4'))
                key['items'][iid] = dict(track=track, model=model, scene=scene, horizon=CONTROL_SRC[3], control=name,
                                         render_id=rid, begin=begin, end=f'videos/{iid}_e.mp4', end_frames=[seg[0], seg[-1]],
                                         medium=medium_phrase(meta), direction=meta.get('direction'),
                                         category=meta.get('category'),
                                         expected={'freeze': {'motion': [1, 2]}, 'reverse': {'direction': 'no'},
                                                   'pingpong': {'loop': 'yes'}}[name])
    # annotation scenes (I2V conditioning images)
    pub = json.load(open(os.path.join(ROOT, LABELS['i2v'])))['scenes']
    scenes = []
    for s in pub:
        img_dst = os.path.join(SITE, 'images', s['id'] + '.jpg')
        if not os.path.exists(img_dst):
            shutil.copyfile(os.path.join(ROOT, s['image']), img_dst)
        lab = cv2.imread(os.path.join(ROOT, 'masks/public_role_maps_2026_11_10', s['id'], 'labels.png'), cv2.IMREAD_GRAYSCALE)
        scenes.append(dict(id=s['id'], category=s['category'], medium=medium_phrase(s), direction=s.get('direction'),
                           support=s['static_support'], credit=s['credit'], licence=s['licence'],
                           image=f'images/{s["id"]}.jpg', w=int(lab.shape[1]), h=int(lab.shape[0]), auto_rle=rle(lab)))
    # public stimulus list: no model, scene or horizon; T2V and I2V items both use the same fields
    public = [dict(id=k, begin=v['begin'], end=v['end'], medium=v['medium'], direction=v['direction'])
              for k, v in sorted(key['items'].items())]
    json.dump(dict(version=len(public), items=public), open(os.path.join(SITE, 'stimuli.json'), 'w'))
    json.dump(dict(scenes=scenes), open(os.path.join(SITE, 'annotation_scenes.json'), 'w'))
    json.dump(key, open(key_path, 'w'), indent=1)
    print(len(public), 'rating items;', sum(1 for v in key['items'].values() if v['control']), 'controls;',
          len(scenes), 'annotation scenes')


if __name__ == '__main__':
    main()

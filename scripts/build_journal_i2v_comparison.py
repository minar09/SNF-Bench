#!/usr/bin/env python3
"""Build short I2V comparison frames from existing, hash-verified renders.

Selection: waterfall and campfire from the documented public figure set; four
released-pipeline rows with outputs on both sources. This is visual evidence,
not a leaderboard or a long-horizon result. No video is generated or scored.
"""
import hashlib
import json
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'JOURNAL_TCSVT/figures/i2v_comparison_2026_11_08'
MANIFEST = ROOT / 'manifest/public_figure_set_2026_11_05.json'
SCENES = ('vb161950', 'vb10462563')
MODELS = ('causal_forcing', 'ltx_video', 'wan21', 'wan22')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    if OUT.exists():
        raise SystemExit(f'{OUT} already exists; refusing to overwrite')
    scenes = {s['id']: s for s in json.loads(MANIFEST.read_text())['scenes']}
    inputs = []
    for sid in SCENES:
        scene = scenes[sid]
        image = ROOT / scene['image']
        if sha(image) != scene['image_sha256']:
            raise SystemExit(f'{sid}: source image hash mismatch')
        for model in MODELS:
            folder = ROOT / f'videos/public_bench/renders/{model}/5s'
            run = json.loads((folder / 'RUN.json').read_text())
            video = folder / f'{sid}.mp4'
            if sha(video) != run['videos'][sid]['sha256']:
                raise SystemExit(f'{model}/{sid}: video hash mismatch')
            inputs.append((sid, model, video, run, scene))
    OUT.mkdir(parents=True)
    report = dict(role='exposure-logged qualitative development evidence, not confirmation',
                  selection='Two public-benchmark sources selected for distinct natural materials: '
                            'waterfall and campfire; four systems with existing 5s outputs on both.',
                  limitations='Short-window visualization; no long-horizon or model-ranking claim. '
                              'Visual cross-paper overlap audit is documented separately.',
                  scenes={})
    for sid in SCENES:
        scene = scenes[sid]
        src = cv2.imread(str(ROOT / scene['image']))
        if src is None or not cv2.imwrite(str(OUT / f'{sid}_source.png'), src):
            raise RuntimeError(f'{sid}: source image decode/write failed')
        report['scenes'][sid] = dict(source_sha256=scene['image_sha256'], source_url=scene['pexels_url'],
                                      setting=scene['setting'], text=scene['text'], models={})
    for sid, model, video, run, _ in inputs:
        cap = cv2.VideoCapture(str(video))
        fps, n = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if not cap.isOpened() or fps <= 0 or n < 2:
            raise RuntimeError(f'{video}: invalid decoded metadata')
        indices = {'mid': min(n - 1, int(round(2.5 * fps))), 'end': n - 1}
        for label, idx in indices.items():
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if not ok or not cv2.imwrite(str(OUT / f'{sid}_{model}_{label}.png'), frame):
                raise RuntimeError(f'{video}: could not decode frame {idx}')
        cap.release()
        report['scenes'][sid]['models'][model] = dict(video_sha256=sha(video), run_sha256=sha(video.parent/'RUN.json'),
                                                        fps=fps, frames=n, frame_indices=indices,
                                                        frame_times_s={k: v/fps for k,v in indices.items()},
                                                        configuration=run['identity'], deviations=run['deviations'])
    (OUT / 'PROVENANCE.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Built two-source, four-system I2V figure assets:', OUT)


if __name__ == '__main__':
    main()

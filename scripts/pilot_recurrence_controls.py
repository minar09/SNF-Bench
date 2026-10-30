"""Exploratory recurrence controls on short generated-video windows, not validation."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _paths
from run_sourceref_gpu_parity import sha, write_atomic
from snf_candidates import recurrence


def controls(frames, dynamic, loop_frames):
    """Keep the non-dynamic region intact while looping/freezing the dynamic pixels."""
    loop, frozen = [], []
    for i, frame in enumerate(frames):
        a, b = frame.copy(), frame.copy()
        a[dynamic] = frames[i % loop_frames][dynamic]
        b[dynamic] = frames[0][dynamic]
        loop.append(a)
        frozen.append(b)
    return loop, frozen


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error('output exists; choose a new path')
    cv2.setNumThreads(1)
    root = Path(_paths.resolve('method_repo'))
    records = root / 'results/factorial/scores/cfpp/echo_nfpb1_default_lr/seed42/sourcefixed_60s/staging'
    masks = root / 'results/factorial/source_masks'
    scenes = ['icf04', 'iow02', 'ifw03', 'ibp03', 'iwb03', 'icb04']
    report = dict(status='running', scope='exploratory generated-video 12-second windows; no natural-video or human validation',
                  runner_sha256=sha(__file__), candidate_sha256=sha(HERE / 'snf_candidates.py'),
                  requested_scenes=scenes, requested_fps=4, seconds=12, loop_period_seconds=3,
                  control='replace dynamic-region pixels only; support remains unchanged', rows=[])
    write_atomic(args.output, report)
    for sid in scenes:
        start = time.monotonic()
        row = dict(scene_id=sid)
        try:
            rec = json.loads((records / (sid + '.json')).read_text())
            video = Path(str(rec['video_path']).replace('/workspace/', '/home/minar/'))
            if not video.is_absolute():
                video = root / video
            mask_path = masks / sid / 'labels.png'
            if sha(video) != rec['video_sha256'] or sha(mask_path) != rec['mask_sha256']['labels']:
                raise ValueError('input hash mismatch')
            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
            dynamic = mask == 2
            cap = cv2.VideoCapture(str(video))
            native = cap.get(cv2.CAP_PROP_FPS)
            step = round(native / 4)
            if not cap.isOpened() or not native or step < 1:
                raise ValueError('video could not be decoded at requested rate')
            fps = native / step
            frames = []
            for i in range(int(round(12 * native))):
                ok, frame = cap.read()
                if not ok:
                    break
                if i % step == 0:
                    frames.append(frame)
            cap.release()
            if len(frames) < round(12 * fps):
                raise ValueError('video shorter than 12 seconds')
            loop, frozen = controls(frames, dynamic, round(3 * fps))
            row.update(status='PASS', category=rec.get('category'), video_sha256=rec['video_sha256'],
                       mask_sha256=rec['mask_sha256']['labels'], dynamic_pixels=int(dynamic.sum()),
                       sampled_fps=fps, frame_count=len(frames),
                       baseline=recurrence(frames, dynamic, fps_sampled=fps),
                       dynamic_loop=recurrence(loop, dynamic, fps_sampled=fps),
                       dynamic_freeze=recurrence(frozen, dynamic, fps_sampled=fps))
        except Exception as exc:
            row.update(status='ERROR', error=f'{type(exc).__name__}: {exc}')
        row['elapsed_s'] = round(time.monotonic() - start, 2)
        report['rows'].append(row)
        write_atomic(args.output, report)
        print(sid, row['status'], flush=True)
        if row['status'] == 'ERROR':
            break
    report['status'] = 'COMPLETE' if len(report['rows']) == len(scenes) and all(r['status'] == 'PASS' for r in report['rows']) else 'INCOMPLETE_OR_FAILED'
    write_atomic(args.output, report)
    return 0 if report['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    sys.exit(main())

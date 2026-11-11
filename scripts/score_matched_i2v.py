#!/usr/bin/env python3
"""Source-fixed SNF scores (`sourcefixed-1.0`) of one matched 240 s I2V rollout at 60, 120 and 240 s.

Same horizon policy as scripts/score_matched_t2v.py: 60 and 120 s are lossless framemd5-verified
prefixes (first 16*H + 1 frames) of the one rollout, 240 s is the original file. Each is scored by
scripts/snf_sourceref.py::score_video against the conditioning image and the automatic CLIPSeg role
map of masks/public_role_maps_2026_11_10/<id>/ (mask_review_scope "none": unreviewed; the maps of
vb1236906, vb10462563 and pq0140 are known to be poor, and pq0092/pq0065/pq0089/vb2385898 have
almost no dynamic region, so their motion metrics abstain).

    python scripts/score_matched_i2v.py --system scenetether --scene vb161950 --gpu 2
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import score_matched_t2v as T  # noqa: E402  (cut_prefix, sha, framemd5)

VIDEOS = ROOT / 'videos/journal_matched_2026_11_10/i2v'
SCORES = ROOT / 'raw_matched_2026_11_10/i2v'
MASKS = ROOT / 'masks/public_role_maps_2026_11_10'
MANIFEST = ROOT / 'manifest/public_figure_set_2026_11_05.json'
HORIZONS = (60, 120, 240)


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--system', required=True)
    a.add_argument('--scene', required=True)
    a.add_argument('--gpu', required=True, type=int, choices=(2, 3))
    args = a.parse_args()
    os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu)
    run_dir = VIDEOS / args.system / args.scene / '240s'
    run = json.loads((run_dir / 'RUN.final.json').read_text())
    if run.get('status') != 'complete':
        raise SystemExit('render is not complete')
    out_rec = run['outputs'][0] if run.get('outputs') else run['output']
    src = run_dir / out_rec['name']
    if T.sha(src) != out_rec['sha256']:
        raise SystemExit('render hash differs from its RUN.final.json')
    scene = next(s for s in json.loads(MANIFEST.read_text())['scenes'] if s['id'] == args.scene)
    image = ROOT / scene['image']
    if T.sha(image) != scene['image_sha256']:
        raise SystemExit('conditioning image hash differs from the manifest')
    labels = MASKS / args.scene / 'labels.png'
    mask_set = 'sha256:' + T.sha(MASKS / 'PROVENANCE.json')[:12]
    out = SCORES / args.system / args.scene / 'snf'
    done = out / 'SCORE.json'
    if done.exists():
        raise SystemExit(f'{done} exists; scores are never overwritten')
    out.mkdir(parents=True, exist_ok=True)
    total = len(T.framemd5(src, 10 ** 6))
    inputs = {}
    for h in HORIZONS:
        n = T.FPS * h + 1
        if h == 240 or n >= total:
            inputs[h] = dict(path=str(src.relative_to(ROOT)), frames=total, sha256=out_rec['sha256'],
                             verified='original render file')
        else:
            (out / 'prefixes').mkdir(exist_ok=True)
            inputs[h] = T.cut_prefix(src, n, out / 'prefixes' / f'p{h:03d}.mp4')
    import snf_sourceref as scorer
    S, _, _ = scorer.snf_modules()
    t0 = time.monotonic()
    model, recs, errs = S.load_raft('cuda'), {}, {}
    for h in HORIZONS:
        try:
            recs[h] = scorer.score_video(model, str(ROOT / inputs[h]['path']), str(labels), str(image), 'cuda',
                                         native_fps=16.0, mask_set=mask_set, mask_version='public-clipseg-2026-11-10',
                                         mask_review_scope='none')
        except Exception as exc:  # recorded, not retried
            errs[h] = f'{type(exc).__name__}: {exc}'
    ok = not errs
    rep = dict(status='complete' if ok else 'failed', track='i2v', system=args.system, scene=args.scene,
               category=scene['category'], render=str(run_dir.relative_to(ROOT)), render_setting=run.get('setting'),
               metric='sourcefixed-1.0 (scripts/snf_sourceref.py)', scorer_sha256=T.sha(ROOT / 'scripts/snf_sourceref.py'),
               upstream_scorer_sha256=scorer.UPSTREAM_SHA256, mask=str(labels.relative_to(ROOT)),
               mask_sha256=T.sha(labels), mask_set=mask_set, mask_review_scope='none',
               conditioning_image=scene['image'], conditioning_image_sha256=scene['image_sha256'],
               window_policy='prefix: first 16*H+1 frames of one 240 s rollout; 240 s = whole file',
               role='journal matched-horizon development scores; never pool with historical endpoint records',
               inputs={str(h): inputs[h] for h in HORIZONS}, records={str(h): recs.get(h) for h in HORIZONS},
               errors={str(h): e for h, e in errs.items()}, wall_s=round(time.monotonic() - t0), gpu=args.gpu)
    done.write_text(json.dumps(rep, indent=1, default=str) + '\n')
    print(json.dumps(dict(system=args.system, scene=args.scene, status=rep['status'], wall_s=rep['wall_s'])))
    if not ok:
        raise SystemExit(f'scoring failed: {errs}')


if __name__ == '__main__':
    main()

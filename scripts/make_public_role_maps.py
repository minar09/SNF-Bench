#!/usr/bin/env python3
"""SNF role maps (832x480 labels.png: 0 ignore, 1 support, 2 dynamic, 3 overlay) for the 12 licence-cleared public
I2V sources of manifest/public_figure_set_2026_11_05.json.

Adapter only: the per-scene method is AIA tools/factorial_scoring/source_masks.py, imported read-only (its
process_scene: CLIPSeg CIDAS/clipseg-rd64-refined on the 832x480 source, queries from the scene's own
`dynamic_medium` + category terms, `static_support` + its nouns, and the generic overlay terms; Otsu/floor thresholds,
confidence band, 7x7 cleanup, 4 % border, falling_precip as an overlay medium). Its main() checks scene ids against the
AIA frozen test split, which these public ids are not in; the adapter calls process_scene directly with the public
manifest's own image_sha256 as the frozen hash. Nothing under AIA is edited or written (bytecode writing is off).

AUTOMATIC, UNREVIEWED masks. Run on CPU in the vbench env, offline. source_masks.py's docstring names
/home/minar/ckpt/hf_cache, which holds no CLIPSeg copy; the cache whose model.safetensors sha256 equals the one recorded
by the AIA source-mask build (d00ca85d...) is /home/minar/.cache/hf_minar, so that is the default and the weights hash
is checked against the AIA value before any mask is written:

    OMP_NUM_THREADS=16 /home/minar/miniconda3/envs/vbench/bin/python scripts/make_public_role_maps.py

Output: masks/public_role_maps_2026_11_10/<id>/{labels.png, region pngs, p_*.png, meta.json (source_masks.py's)},
<id>/provenance.json, masks/public_role_maps_2026_11_10/PROVENANCE.json, and a contact sheet at
.metric_staging/i2v_matched_2026_11_10/role_maps_sheet.png. An existing scene directory is never overwritten.
"""
import sys

sys.dont_write_bytecode = True               # never leave __pycache__ in the AIA tree

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
from pathlib import Path  # noqa: E402
import time  # noqa: E402

os.environ.setdefault('HF_HOME', '/home/minar/.cache/hf_minar')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

ROOT = Path(__file__).resolve().parents[1]
AIA_TOOLS = Path('/home/minar/ar-image-animation/tools/factorial_scoring')
MANIFEST = ROOT / 'manifest/public_figure_set_2026_11_05.json'
OUT = ROOT / 'masks/public_role_maps_2026_11_10'
AIA_WEIGHTS_SHA256 = 'd00ca85d6b859f9d07b7cfb8ef26fe9771cb275b34c9368f2ecf603139307f55'   # AIA source_masks meta.json
SHEET = ROOT / '.metric_staging/i2v_matched_2026_11_10/role_maps_sheet.png'

sys.path.insert(0, str(AIA_TOOLS))
import source_masks as sm  # noqa: E402


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(4 << 20), b''):
            h.update(b)
    return h.hexdigest()


def scenes():
    d = json.loads(MANIFEST.read_text())
    out = []
    for s in d['scenes']:
        missing = [k for k in ('id', 'category', 'text', 'dynamic_medium', 'static_support', 'image', 'image_sha256')
                   if not s.get(k)]
        if missing:
            raise SystemExit(f"{s.get('id')}: manifest lacks {missing}; not invented")
        out.append(s)
    return out


def sheet(metas, by_id):
    import cv2
    import numpy as np
    cols, tw, th, cap = 3, 416, 240, 34
    rows = -(-len(metas) // cols)
    S = np.full((rows * (th + cap), cols * 2 * tw, 3), 255, np.uint8)
    for i, m in enumerate(metas):
        sid = m['scene_id']
        img = cv2.resize(cv2.imread(str(ROOT / by_id[sid]['image'])), (tw, th), interpolation=cv2.INTER_AREA)
        reg = sm.load_regions(str(OUT), sid, (tw, th))
        r, c = divmod(i, cols)
        y, x = r * (th + cap), c * 2 * tw
        S[y:y + th, x:x + tw] = img
        S[y:y + th, x + tw:x + 2 * tw] = sm.overlay_img(img, reg, ['support', 'dynamic', 'overlay'])
        cc = m['coverage']
        t1 = (f"{sid} {m['category']}  sup {cc['support_frac']:.2f} dyn {cc['dynamic_frac']:.2f} "
              f"ovl {cc['overlay_frac']:.2f} unc {cc['uncertain_frac']:.2f}" + ('  ABSTAIN' if m['abstain_reasons'] else ''))
        cv2.putText(S, t1, (x + 4, y + th + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(S, 'dyn: ' + m['prompt']['dynamic_medium'][:95], (x + 4, y + th + 28), cv2.FONT_HERSHEY_SIMPLEX,
                    0.38, (60, 60, 60), 1, cv2.LINE_AA)
    cv2.putText(S, 'green support | red dynamic | blue overlay | untinted ignore  (automatic, unreviewed)',
                (4, S.shape[0] - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(SHEET), S)


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--only', default='', help='comma list of scene ids')
    args = a.parse_args()
    sc = scenes()
    by_id = {s['id']: s for s in sc}
    ids = [x for x in args.only.split(',') if x] or [s['id'] for s in sc]
    OUT.mkdir(parents=True, exist_ok=True)
    cs, metas, built = None, [], []
    for sid in ids:
        s = by_id[sid]
        od = OUT / sid
        if od.exists():                       # never overwrite; reuse only a complete build
            if not (od / 'meta.json').is_file():
                raise SystemExit(f'{od} exists without meta.json; refusing to touch it')
            metas.append(json.loads((od / 'meta.json').read_text()))
            continue
        if cs is None:
            cs = sm.ClipSeg('cpu')
            if cs.weights_sha256 != AIA_WEIGHTS_SHA256:
                raise SystemExit(f'CLIPSeg weights {cs.weights_sha256} != the AIA build {AIA_WEIGHTS_SHA256}')
        pair = dict(id=sid, category=s['category'], text=s['text'], dynamic_medium=s['dynamic_medium'],
                    static_support=s['static_support'], direction=s.get('direction'))
        m = sm.process_scene(cs, pair, str(ROOT / s['image']), str(od), s['image_sha256'])
        prov = dict(scene_id=sid, labels='0 ignore/uncertain, 1 support, 2 dynamic, 3 overlay', size=[sm.W, sm.H],
                    review='automatic, unreviewed', mask_version=sm.MASK_VERSION, model=sm.MODEL_ID,
                    model_weights_sha256=m['model_weights_sha256'], hf_home=os.environ['HF_HOME'], device='cpu',
                    method='AIA tools/factorial_scoring/source_masks.py process_scene (imported read-only)',
                    method_sha256=sha(sm.__file__), adapter=str(Path(__file__).relative_to(ROOT)),
                    adapter_sha256=sha(__file__), manifest=str(MANIFEST.relative_to(ROOT)), manifest_sha256=sha(MANIFEST),
                    image=s['image'], image_sha256=s['image_sha256'],
                    prompt_fields=dict(source='manifest/public_figure_set_2026_11_05.json (verbatim)',
                                       dynamic_medium=s['dynamic_medium'], static_support=s['static_support'],
                                       category=s['category']),
                    queries=m['queries'], thresholds=m['thresholds'], coverage=m['coverage'],
                    abstain_reasons=m['abstain_reasons'], labels_sha256=m['files_sha256']['labels.png'],
                    written=time.strftime('%Y-%m-%dT%H:%M:%S%z'))
        (od / 'provenance.json').write_text(json.dumps(prov, indent=1) + '\n')
        metas.append(m)
        built.append(sid)
        c = m['coverage']
        print(f"{sid} {s['category']}: sup {c['support_frac']:.3f} dyn {c['dynamic_frac']:.3f} "
              f"ovl {c['overlay_frac']:.3f} unc {c['uncertain_frac']:.3f} {'; '.join(m['abstain_reasons'])}", flush=True)
    if not args.only:
        top = OUT / 'PROVENANCE.json'
        if not top.exists():
            top.write_text(json.dumps(dict(
                review='automatic, unreviewed', model=sm.MODEL_ID, mask_version=sm.MASK_VERSION,
                method_sha256=sha(sm.__file__), adapter_sha256=sha(__file__), manifest_sha256=sha(MANIFEST),
                scenes={m['scene_id']: dict(labels_sha256=m['files_sha256']['labels.png'],
                                            image_sha256=m['source_sha256'], abstain_reasons=m['abstain_reasons'])
                        for m in metas},
                written=time.strftime('%Y-%m-%dT%H:%M:%S%z')), indent=1) + '\n')
    sheet(metas, by_id)
    print(f'built {len(built)}, reused {len(metas) - len(built)}; sheet {SHEET}')


if __name__ == '__main__':
    main()

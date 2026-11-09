#!/usr/bin/env python3
"""Screen selected I2V sources against SceneTether's raster figure assets.

Perceptual hashes help find duplicates but cannot prove absence of reuse. The
audit is read-only on both sibling projects and never changes source images.
"""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OTHER = Path('/home/minar/ar-image-animation/CVPR_2027_AR_I2V')
TOMM = Path('/home/minar/static-forcing/ACM_TOMM_SF/acmmanuscript.pdf')
OUT = ROOT / 'manifest/cross_paper_figure_audit_2026_11_08_v2.json'
SCENES = ('vb161950', 'vb10462563')
ASSET_ROOTS = {
    'scenetether': OTHER / 'figures',
    'steady_forcing': TOMM.parent / 'figs',
    'region_forcing': Path('/home/minar/region-forcing'),
}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def phash(path):
    im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if im is None:
        return None
    dct = cv2.dct(cv2.resize(im, (32, 32)).astype(np.float32))[:8, :8]
    return dct > np.median(dct)


def main():
    if OUT.exists():
        raise SystemExit(f'{OUT} exists; do not overwrite historical audit')
    src = {s['id']: s for s in json.loads((ROOT / 'manifest/public_figure_set_2026_11_05.json').read_text())['scenes']}
    refs = []
    unreadable = []
    for group, root in ASSET_ROOTS.items():
        files = sorted(p for p in root.rglob('*') if p.suffix.lower() in ('.png', '.jpg', '.jpeg'))
        for p in files:
            h = phash(p)
            name = f'{group}/{p.relative_to(root)}'
            if h is None:
                unreadable.append(name)
            else:
                refs.append((name, h))
    rows = []
    for sid in SCENES:
        scene = src[sid]
        p = ROOT / scene['image']
        if sha(p) != scene['image_sha256']:
            raise SystemExit(f'{sid}: image hash mismatch')
        q = phash(p)
        near = sorted((int(np.count_nonzero(h != q)), name) for name,h in refs)
        rows.append(dict(scene=sid, image_sha256=sha(p), nearest=near[:5]))
    report = dict(scope='Selected I2V conditioning images versus SceneTether and Steady-Forcing figure rasters and region-forcing raster files',
                  method='64-bit DCT perceptual hash on grayscale whole images, Hamming distance',
                  caution='No low-distance match is not proof of no reuse; crops, PDF vector assets, '
                          'videos, and other simultaneous manuscript versions require further review.',
                  scenetether_main_pdf_sha256=sha(OTHER/'main.pdf'), steady_forcing_pdf_sha256=sha(TOMM),
                  raster_candidates=len(refs), unreadable=unreadable, rows=rows)
    with OUT.open('x') as f:
        json.dump(report, f, indent=2)
    print(f'{OUT}: {len(refs)} raster images screened')


if __name__ == '__main__':
    main()

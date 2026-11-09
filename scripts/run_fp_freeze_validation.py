#!/usr/bin/env python3
"""Resume new fp-cell freeze controls and their GPU flow audit without overwriting.

Uses the fp cell, which was not used to set v2's static-bias threshold. This
is a held-out control *cell*, not a held-out source or model family.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import native_controls as NC
import snf_sourceref as P
from pilot_support_realism import verify_chain

PY = sys.executable
LIST = ROOT / 'manifest/realism_dev_2026_11_05/lists/list_fp.tsv'
CONTROLS = ROOT / 'videos/realism_controls_2026_11_05/echo_nfpb1_fp_pool_lr'
LABEL = 'cfpp/echo_nfpb1_fp_pool_lr'
REPORT = ROOT / 'manifest/realism_dev_2026_11_05/geometry_v2_fp_freeze_2026_11_08.json'
MIN_BYTES = 110_000_000_000


def main():
    if REPORT.exists():
        raise SystemExit(f'{REPORT} exists; refusing to overwrite')
    rows = [line.split('\t', 1) for line in LIST.read_text().splitlines()]
    eligible = []
    for sid, parent in rows:
        mask = Path(NC.MASKS) / sid / 'labels.png'
        dyn, _, _, _ = P.load_role_masks(str(mask))
        if int(dyn.sum()) < 50:
            print(f'{sid}: excluded, material mask < 50 pixels', flush=True)
            continue
        if os.statvfs('/').f_bavail * os.statvfs('/').f_frsize < MIN_BYTES:
            raise SystemExit('insufficient root disk space; controls remain resumable')
        video = CONTROLS / 'freeze' / f'{sid}.mp4'
        sidecar = video.with_suffix('.json')
        if video.exists() != sidecar.exists():
            raise SystemExit(f'{sid}: incomplete control pair; investigate without overwriting')
        if video.exists():
            verify_chain(str(video), NC.chain(sid, NC.sha256(parent)))
            print(f'{sid}: reuse verified freeze control', flush=True)
        else:
            with tempfile.NamedTemporaryFile(mode='w', prefix='snf_fp_freeze_', suffix='.tsv') as t:
                t.write(f'{sid}\t{parent}\n')
                t.flush()
                subprocess.run([PY, str(ROOT / 'scripts/native_controls.py'), 'temporal', t.name,
                                str(CONTROLS), 'freeze'], cwd=ROOT, check=True)
        eligible.append((sid, parent))
    stage = ROOT / '.metric_staging'
    stage.mkdir(exist_ok=True)
    # Deterministic listing, created only if absent or already identical.
    listing = stage / 'fp_freeze_eligible_2026_11_08.tsv'
    content = ''.join(f'{sid}\t{parent}\n' for sid, parent in eligible)
    if listing.exists() and listing.read_text() != content:
        raise SystemExit(f'{listing}: different listing already exists')
    if not listing.exists():
        listing.write_text(content)
    print(f'{len(eligible)} eligible freeze controls; launching GPU 3 flow audit', flush=True)
    subprocess.run([PY, str(ROOT / 'scripts/realism_geometry_run.py'), '--gpu', '3',
                    '--videos', str(listing), '--controls', str(CONTROLS),
                    '--modes', 'passthrough_crf18,freeze', '--label', LABEL,
                    '--out', str(REPORT)], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()

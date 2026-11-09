#!/usr/bin/env python3
"""Run prepared fp freeze flow validation on the first safely idle GPU 2 or 3."""
from pathlib import Path
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'manifest/realism_dev_2026_11_05/geometry_v2_fp_freeze_2026_11_08.json'
LISTING = ROOT / '.metric_staging/fp_freeze_eligible_2026_11_08.tsv'
CONTROLS = ROOT / 'videos/realism_controls_2026_11_05/echo_nfpb1_fp_pool_lr'
CACHE = ROOT / 'videos/realism_cache/geometry_flows'
MIN_BYTES = 110_000_000_000


def available():
    if any(os.statvfs(p).f_bavail * os.statvfs(p).f_frsize < MIN_BYTES
           for p in ('/', os.path.realpath(CACHE))):
        return set()
    q = subprocess.run(['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader'],
                       capture_output=True, text=True, check=True, timeout=15)
    uuids = {}
    for line in q.stdout.splitlines():
        i, uuid = [x.strip() for x in line.split(',', 1)]
        uuids[int(i)] = uuid
    if 2 not in uuids or 3 not in uuids:
        raise RuntimeError('GPU inventory lacks device 2 or 3')
    apps = subprocess.run(['nvidia-smi', '--query-compute-apps=gpu_uuid', '--format=csv,noheader'],
                          capture_output=True, text=True, check=True, timeout=15)
    busy = set(apps.stdout.splitlines())
    return {g for g in (2, 3) if uuids[g] not in busy}


def main():
    if not LISTING.is_file():
        raise SystemExit('eligible listing absent; prepare controls first')
    while True:
        if REPORT.exists():
            raise SystemExit('report already exists; refusing to duplicate scoring')
        try:
            first = available()
            if first:
                time.sleep(60)
                free = first & available()
                if free:
                    gpu = min(free)
                    print(f'GPU {gpu} idle on both checks; starting flow validation', flush=True)
                    subprocess.run([sys.executable, str(ROOT / 'scripts/realism_geometry_run.py'),
                                    '--gpu', str(gpu), '--videos', str(LISTING),
                                    '--controls', str(CONTROLS), '--modes', 'passthrough_crf18,freeze',
                                    '--label', 'cfpp/echo_nfpb1_fp_pool_lr', '--out', str(REPORT)],
                                   cwd=ROOT, check=True)
                    return
        except (OSError, RuntimeError, subprocess.SubprocessError) as e:
            print(f'GPU/disk check failed or scorer stopped: {e}; inspect before retry', flush=True)
            raise
        print('GPUs 2 and 3 busy or disk guard unmet; waiting', flush=True)
        time.sleep(60)


if __name__ == '__main__':
    main()

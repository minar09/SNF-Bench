#!/usr/bin/env python3
"""Queue one new T2V visual when GPU 2 or 3 is idle and disk guards pass."""
import subprocess
import sys
import time
from pathlib import Path

from wait_fp_freeze_gpu import available

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'videos/journal_distinct_visual_2026_11_09/t2v/causvid_common/cf01/240s_retry1'


def main():
    while True:
        if OUT.exists():
            raise SystemExit(f'{OUT} exists; not starting another run')
        first = available()
        if first:
            time.sleep(60)
            free = first & available()
            if free:
                gpu = min(free)
                print(f'GPU {gpu} idle on both checks; starting cf01', flush=True)
                subprocess.run([sys.executable, str(ROOT/'scripts/run_distinct_t2v_visual.py'),
                                '--scene','cf01','--gpu',str(gpu)], cwd=ROOT, check=True)
                return
        print('Waiting for GPU 2 or 3 and the 110 GB disk guards', flush=True)
        time.sleep(60)


if __name__ == '__main__':
    main()

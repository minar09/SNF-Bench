#!/usr/bin/env python3
"""Queue second prespecified T2V scene only after the first retry succeeds."""
import json
from pathlib import Path
import subprocess
import sys
import time

from wait_fp_freeze_gpu import available

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'videos/journal_distinct_visual_2026_11_09/t2v/causvid_common'
FIRST = BASE/'cf01/240s_retry1/RUN.final.json'
SECOND = BASE/'cb01/240s_retry1'


def main():
    while not FIRST.exists():
        if SECOND.exists():
            raise SystemExit('second output already exists')
        print('Waiting for cf01 final record', flush=True)
        time.sleep(60)
    if json.loads(FIRST.read_text()).get('status') != 'complete':
        raise SystemExit('first run did not complete; inspect it before continuing')
    while True:
        if SECOND.exists():
            raise SystemExit('second output already exists')
        if 2 in available():
            time.sleep(60)
            if 2 in available():
                subprocess.run([sys.executable,str(ROOT/'scripts/run_distinct_t2v_visual.py'),
                                '--scene','cb01','--gpu','2'],cwd=ROOT,check=True)
                return
        print('Waiting for idle GPU 2 and disk guards', flush=True)
        time.sleep(60)


if __name__ == '__main__':
    main()

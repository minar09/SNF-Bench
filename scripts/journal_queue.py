#!/usr/bin/env python3
"""Self-running job queue for the journal renders and scores on GPUs 2 and 3.

One worker per GPU (`--gpu 2`, `--gpu 3`). Each worker re-reads the job list before every pick,
so jobs may be appended while it runs. A job is a JSON line in QUEUE/jobs.jsonl:

    {"id": "t2v/self_forcing/fp01", "argv": ["python", "scripts/run_t2v_matched.py", ..., "--gpu", "{gpu}"],
     "done": "videos/.../RUN.final.json", "deps": ["..."], "gpus": [2, 3]}

A job is runnable when its `done` file is absent, every dep's `done` file exists with a JSON
`status` of "complete" (or any content, for a non-JSON marker), it is not claimed, and the worker's
GPU is in `gpus`. Claims are atomic directories QUEUE/claims/<id>; a claim with result.json is
finished (passed or failed) and is never retried automatically: delete the claim to retry.

Guards before every job: no compute process on the GPU at two checks 60 s apart, at least
MIN_BYTES free on / and on /data1, and no QUEUE/STOP or QUEUE/STOP_gpu<N> file. A worker stops after
two consecutive failures, so a systemic fault does not burn the queue.

    nohup python scripts/journal_queue.py --gpu 2 >> manifest/journal_queue_2026_11_10/worker_gpu2.log 2>&1 &
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / 'manifest/journal_queue_2026_11_10'
MIN_BYTES = 110_000_000_000
PY = '/home/minar/miniconda3/envs/snfeval/bin/python'


def now():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def log(gpu, msg):
    print(f'{now()} gpu{gpu} {msg}', flush=True)


def gpu_idle(gpu):
    rows = [r.split(', ') for r in subprocess.check_output(
        ['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader'], text=True, timeout=15).splitlines()]
    uuid = next(u for i, u in rows if int(i) == gpu)
    apps = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid', '--format=csv,noheader'],
                                   text=True, timeout=15).split()
    return uuid not in apps


def disk_ok():
    return all(os.statvfs(p).f_bavail * os.statvfs(p).f_frsize >= MIN_BYTES for p in ('/', '/data1'))


def stopped(gpu):
    return (QUEUE / 'STOP').exists() or (QUEUE / f'STOP_gpu{gpu}').exists()


def finished(path):
    p = ROOT / path
    if not p.exists():
        return False
    try:
        return json.loads(p.read_text()).get('status', 'complete') == 'complete'
    except (ValueError, AttributeError):
        return True


def jobs():
    out = []
    for line in (QUEUE / 'jobs.jsonl').read_text().splitlines():
        if line.strip() and not line.startswith('#'):
            out.append(json.loads(line))
    return out


def pick(gpu):
    js = jobs()
    by_id = {j['id']: j for j in js}
    for j in js:
        if gpu not in j.get('gpus', [2, 3]) or (ROOT / j['done']).exists():
            continue
        if (QUEUE / 'claims' / j['id'].replace('/', '__')).exists():
            continue
        if all(finished(by_id[d]['done']) for d in j.get('deps', [])):
            return j
    return None


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--gpu', type=int, required=True, choices=(2, 3))
    gpu = a.parse_args().gpu
    (QUEUE / 'claims').mkdir(parents=True, exist_ok=True)
    (QUEUE / 'logs').mkdir(exist_ok=True)
    fails = 0
    while True:
        if stopped(gpu):
            log(gpu, 'STOP file present; exiting')
            return
        j = pick(gpu)
        if j is None:
            time.sleep(120)
            continue
        if not (disk_ok() and gpu_idle(gpu)):
            time.sleep(60)
            continue
        time.sleep(60)
        if stopped(gpu) or not (disk_ok() and gpu_idle(gpu)):
            continue
        claim = QUEUE / 'claims' / j['id'].replace('/', '__')
        try:
            claim.mkdir()
        except FileExistsError:
            continue
        argv = [PY if x == 'python' else x.replace('{gpu}', str(gpu)) for x in j['argv']]
        (claim / 'claim.json').write_text(json.dumps(dict(job=j, gpu=gpu, argv=argv, started=now()), indent=1))
        log(gpu, f'start {j["id"]}')
        t0 = time.monotonic()
        with (QUEUE / 'logs' / (claim.name + '.log')).open('a') as f:
            rc = subprocess.run(argv, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
        ok = rc == 0 and finished(j['done'])
        if not ok and not (ROOT / j['done']).parent.exists():
            # the job refused before creating its output (GPU taken or disk low at launch): release, not a failure
            log(gpu, f'released {j["id"]} rc={rc}: nothing was written')
            for p in claim.iterdir():
                p.unlink()
            claim.rmdir()
            time.sleep(300)
            continue
        (claim / 'result.json').write_text(json.dumps(dict(rc=rc, ok=ok, wall_s=round(time.monotonic() - t0),
                                                           ended=now()), indent=1))
        log(gpu, f'{"done" if ok else "FAILED"} {j["id"]} rc={rc} {round(time.monotonic() - t0)}s')
        fails = 0 if ok else fails + 1
        if fails >= 2:
            log(gpu, 'two consecutive failures; worker stops (inspect, then restart)')
            return


if __name__ == '__main__':
    main()

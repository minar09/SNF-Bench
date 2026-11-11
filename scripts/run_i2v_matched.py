#!/usr/bin/env python3
"""One 240 s I2V render of a licence-cleared public source by a published / adapted long-I2V system.

The matched journal I2V set (2026-11-10): the 12 sources of manifest/public_figure_set_2026_11_05.json (832x480
conditioning JPEGs, sha256-checked; manifest `text` verbatim as the caption) x four systems, one render each, fixed
seed. Outputs are new and never overwritten; the same guards as run_t2v_matched.py (refuse if the output directory
exists, if the GPU has any compute process, or if / has < 110 GB free; image id, code commits, config / checkpoint
sha256 and the full command are recorded). A refusal before launch writes nothing under videos/.

  scenetether       SceneTether, the locked cell echo_nfpb1_h1_fm_tether100_lr (AIA docs/locked_final_scenetether_oct16.json):
                    the lock argv with only --output_folder, --data_path, --force_num_frames 4H, --num_output_frames 4H+1,
                    eval_first_n changed (as AIA tools/oos/run_oos_samples_oct28.py), locked pipeline/ and wan21/
                    snapshot mounted read-only, CF++ framewise-2step EMA, seed 42 + prompt index (index 0),
                    SNF_PER_PROMPT_SEED=1. 961 latents -> 3841 frames at 16 fps (240.06 s).
  cfpp_f2s          CF++ checkpoint with Steady-Forcing-derived long-video adaptation (adapted, not native): the
                    region-forcing Phase-A runner (scripts/eval/run_eval_ours.sh METHOD=f2s_framewise), nfpb=1
                    steady config, EMA, seed 0, length from the caption's [240s] marker -> 959 noise latents
                    -> 3837 frames (239.81 s; the runner's int(240*16) frame rule, as in its historical 240s outputs).
  causvid_i2v       CausVid checkpoint in the same adapted runner (METHOD=causvid): chunk6 steady config, no EMA,
                    seed 0, [240s] -> 960 noise latents -> 3841 frames.
  self_forcing_i2v  Self-Forcing DMD checkpoint in the same adapted runner (METHOD=self_forcing): chunk6, no EMA, seed 0.

The region-forcing python command line is replicated (the shell script writes into region-forcing/output); the data
folder (crop-info json + image) is staged under .metric_staging/i2v_matched_2026_11_10/data/<system>/<scene>/ and the
output goes straight to videos/journal_matched_2026_11_10/i2v/<system>/<scene>/240s/. /home/minar is mounted read-only
in the container; only the snf-bench tree is writable. No crop or resize is needed: the sources are already 832x480
(the runners' Resize((480, 832)) is the identity).

    python scripts/run_i2v_matched.py --system scenetether --scene pq0092 --gpu 2 [--dry-run]
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
HOME = Path('/home/minar')
AIA = HOME / 'ar-image-animation'
RF = HOME / 'region-forcing'
MANIFEST = ROOT / 'manifest/public_figure_set_2026_11_05.json'
OUT = ROOT / 'videos/journal_matched_2026_11_10/i2v'
STAGE = ROOT / '.metric_staging/i2v_matched_2026_11_10/data'
IMAGE = 'regfor:cuda12.1'
MIN_BYTES = 110_000_000_000
HORIZON = 240
FPS = 16
LOCK = AIA / 'docs/locked_final_scenetether_oct16.json'
LOCK_SHA256 = '90cc9d5932f4865d1d555a0c4101211e8a40f488ecf657153d06b751d3a62a13'
STRICT_LOAD = '[load] matched 825/825 keys (missing=0, unexpected=0)'
SYSTEMS = {
    'scenetether': dict(
        repo=AIA, ratio='26-15', ckpt='causal-forcing++/framewise-2step.pt', ema=True, seed=42, frames=4 * 4 * HORIZON + 1,
        code=('inference.py', 'utils', 'model', 'configs/cfpp_phase1_60s.yaml', 'configs/phase1/echo_forcing.yaml',
              'configs/default_config.yaml'),
        label='SceneTether (locked final cell echo_nfpb1_h1_fm_tether100_lr)', native=True,
        setting='locked SceneTether argv; only output folder, data path, horizon (force_num_frames 960, '
                'num_output_frames 961) and eval_first_n=1 changed, as AIA tools/oos/run_oos_samples_oct28.py'),
    'cfpp_f2s': dict(
        repo=RF, ratio='16-9', ckpt='causal-forcing++/framewise-2step.pt', ema=True, seed=0, frames=4 * 959 + 1,
        config='configs/causal_forcing_dmd_f2s_steady.yaml', method='f2s_framewise',
        label='CF++ checkpoint with Steady-Forcing-derived long-video adaptation', native=False,
        setting='region-forcing run_eval_ours.sh METHOD=f2s_framewise python command replicated; adapted, not native'),
    'causvid_i2v': dict(
        repo=RF, ratio='16-9', ckpt='CausVid/autoregressive_checkpoint/model.pt', ema=False, seed=0, frames=4 * 960 + 1,
        config='configs/causal_forcing_dmd_f2s_steady_chunk6.yaml', method='causvid',
        label='CausVid checkpoint in the adapted I2V long-video wrapper (chunk6 steady)', native=False,
        setting='region-forcing run_eval_ours.sh METHOD=causvid python command replicated; adapted wrapper, not native'),
    'self_forcing_i2v': dict(
        repo=RF, ratio='16-9', ckpt='Self-Forcing/checkpoints/self_forcing_dmd.pt', ema=False, seed=0, frames=4 * 960 + 1,
        config='configs/causal_forcing_dmd_f2s_steady_chunk6.yaml', method='self_forcing',
        label='Self-Forcing DMD checkpoint in the adapted I2V long-video wrapper (chunk6 steady)', native=False,
        setting='region-forcing run_eval_ours.sh METHOD=self_forcing python command replicated; adapted wrapper, not native'),
}
RF_CODE = ('inference.py', 'pipeline', 'utils', 'wan', 'model', 'configs/default_config.yaml')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(4 << 20), b''):
            h.update(b)
    return h.hexdigest()


def gpu_free(gpu):
    rows = [r.split(', ') for r in subprocess.check_output(
        ['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader'], text=True, timeout=15).splitlines()]
    uuid = next(u for i, u in rows if int(i) == gpu)
    apps = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid', '--format=csv,noheader'],
                                   text=True, timeout=15).split()
    return uuid not in apps


def disk_ok():
    st = os.statvfs('/')
    return st.f_bavail * st.f_frsize >= MIN_BYTES


def git(repo, *a):
    return subprocess.check_output(['git', '-C', str(repo), *a], text=True).strip()


def scenes():
    return {s['id']: s for s in json.loads(MANIFEST.read_text())['scenes']}


def ws(p):
    """host path under /home/minar -> container path under /workspace"""
    return '/workspace/' + str(Path(p).relative_to(HOME))


def caption(scene):
    # the manifest text verbatim; the [240s] marker is stripped by both runners before encoding
    return scene['text'] + f'[{HORIZON}s]'


def crop_info(system, scene):
    s = SYSTEMS[system]
    return [dict(file_name=f"{scene['id']}.jpg", caption=caption(scene),
                 target_crop=dict(target_bbox=[0, 0, 832, 480], target_ratio=s['ratio']), type=scene['category'],
                 origin_width=832, origin_height=480, id=scene['id'], source_image=scene['image'],
                 source_sha256=scene['image_sha256'])]


def stage(system, scene, write):
    """Data folder <STAGE>/<system>/<scene>/{target_crop_info_<ratio>.json, <ratio>/<scene>.jpg}; created once, then
    only verified (never rewritten)."""
    ratio = SYSTEMS[system]['ratio']
    d = STAGE / system / scene['id']
    meta = (json.dumps(crop_info(system, scene), indent=1) + '\n').encode()
    img = (ROOT / scene['image']).read_bytes()
    want = {d / f'target_crop_info_{ratio}.json': meta, d / ratio / f"{scene['id']}.jpg": img}
    if d.exists():
        have = sorted(p for p in d.rglob('*') if p.is_file())
        if have != sorted(want) or any(p.read_bytes() != b for p, b in want.items()):
            raise SystemExit(f'staged data folder {d} differs from what this script would write; refusing')
    elif write:
        (d / ratio).mkdir(parents=True)
        for p, b in want.items():
            p.write_bytes(b)
    return d, {str(p.relative_to(ROOT)): hashlib.sha256(b).hexdigest() for p, b in want.items()}


def argv_for(system, data_dir, out_dir, lock=None):
    """The python command run inside the container (cwd = the system's repo)."""
    s = SYSTEMS[system]
    if system == 'scenetether':
        argv = list(lock['run']['argv'])
        for k, v in {'--output_folder': ws(out_dir), '--data_path': ws(data_dir),
                     '--force_num_frames': str(4 * HORIZON), '--num_output_frames': str(4 * HORIZON + 1),
                     '--seed': str(s['seed'])}.items():
            argv[argv.index(k) + 1] = v
        argv[argv.index('eval_first_n=7')] = 'eval_first_n=1'
        return argv
    return (['python', 'inference.py', '--config_path', s['config'], '--output_folder', ws(out_dir),
             '--checkpoint_path', '../ckpt/' + s['ckpt'], '--data_path', ws(data_dir), '--i2v']
            + (['--use_ema'] if s['ema'] else []) + ['--seed', str(s['seed'])])


def docker_cmd(system, scene_id, gpu, argv, snapshot=None):
    s = SYSTEMS[system]
    cmd = ['docker', 'run', '--rm', '--name', f'snf_i2v_{system}_{scene_id}', '--gpus', f'device={gpu}',
           '--shm-size=32g', '-v', f'{HOME}:/workspace:ro', '-v', f'{ROOT}:{ws(ROOT)}', '-w', ws(s['repo'])]
    if system == 'scenetether':
        cmd += ['-v', f"{snapshot / 'pipeline'}:{ws(AIA)}/pipeline:ro", '-v', f"{snapshot / 'wan21'}:{ws(AIA)}/wan21:ro",
                '-e', 'SNF_PER_PROMPT_SEED=1', '-e', 'PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True']
    cmd += ['-e', 'HF_HUB_OFFLINE=1', '-e', 'PYTHONDONTWRITEBYTECODE=1', IMAGE]
    return cmd + argv


def check_scenetether():
    lock = json.loads(LOCK.read_text())
    if sha(LOCK) != LOCK_SHA256:
        raise SystemExit('SceneTether lock file changed')
    snap = Path(lock['code_snapshot'])
    for p, digest in lock['run']['code_sha256'].items():
        if p.startswith(('pipeline/', 'wan21/')) and sha(snap / p) != digest:
            raise SystemExit(f'locked computational snapshot changed: {p}')
    return lock, snap


def frames_of(path):
    try:
        import cv2
    except ImportError:
        return None, None
    c = cv2.VideoCapture(str(path))
    n = 0
    while c.grab():
        n += 1
    fps = c.get(cv2.CAP_PROP_FPS)
    c.release()
    return n, fps


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--system', required=True, choices=list(SYSTEMS))
    a.add_argument('--scene', required=True, choices=sorted(scenes()))
    a.add_argument('--gpu', required=True, type=int, choices=(2, 3))
    a.add_argument('--dry-run', action='store_true', help='all checks and staging; print the command and RUN.json; '
                                                          'write nothing under videos/')
    args = a.parse_args()
    s = SYSTEMS[args.system]
    scene = scenes()[args.scene]
    out = OUT / args.system / args.scene / f'{HORIZON}s'
    if out.exists():
        raise SystemExit(f'{out} exists; refusing to overwrite or duplicate')
    img = ROOT / scene['image']
    if sha(img) != scene['image_sha256']:
        raise SystemExit(f'{img} sha256 differs from the manifest')
    guards = dict(gpu_free=gpu_free(args.gpu), disk_ok=disk_ok())
    if not args.dry_run and not all(guards.values()):
        raise SystemExit(f'GPU {args.gpu} busy or / below the 110 GB guard; nothing started')
    lock = snap = None
    if args.system == 'scenetether':
        lock, snap = check_scenetether()
    repo = s['repo']
    code = list(s.get('code', RF_CODE)) + ([s['config']] if 'config' in s else [])
    dirty = git(repo, 'status', '--porcelain', '--', *code)
    if dirty:
        raise SystemExit(f'{repo} has uncommitted changes in the code it runs:\n{dirty}')
    if subprocess.run(['docker', 'container', 'inspect', f'snf_i2v_{args.system}_{args.scene}'],
                      capture_output=True).returncode == 0:
        raise SystemExit(f'a container named snf_i2v_{args.system}_{args.scene} already exists')
    data, staged = stage(args.system, scene, write=True)
    ckpt = HOME / 'ckpt' / s['ckpt']
    ckpt_sha = sha(ckpt)
    if lock and ckpt_sha != lock['checkpoint_sha256']:
        raise SystemExit('SceneTether checkpoint sha256 differs from the lock')
    argv = argv_for(args.system, data, out, lock)
    cmd = docker_cmd(args.system, args.scene, args.gpu, argv, snap)
    config = repo / argv[argv.index('--config_path') + 1]
    image = subprocess.check_output(['docker', 'image', 'inspect', IMAGE, '--format', '{{.Id}}'], text=True,
                                    timeout=30).strip()
    info = dict(status='running', role='journal matched I2V render; development data, not confirmation',
                system=args.system, label=s['label'], native=s['native'], setting=s['setting'],
                scene=args.scene, category=scene['category'], source=scene['source'], licence=scene['licence'],
                prompt=scene['text'], prompt_sha256=hashlib.sha256(scene['text'].encode()).hexdigest(),
                caption_in_data=caption(scene), image=scene['image'], image_sha256=scene['image_sha256'],
                preprocessing='none: source is the manifest 832x480 JPEG, copied byte-identical; the runner '
                              'Resize((480, 832)) is the identity',
                staged_data=staged, requested_s=HORIZON, fps=FPS, expected_frames=s['frames'],
                checkpoint=str(ckpt), checkpoint_sha256=ckpt_sha, use_ema=s['ema'], seed=s['seed'],
                seed_rule=('42 + prompt index (single prompt, index 0), SNF_PER_PROMPT_SEED=1' if lock else
                           'set_seed(--seed 0) once; --seed 0 is the runner default (run_eval_ours.sh passes none)'),
                config=str(config), config_sha256=sha(config), image_id=image, repo=str(repo),
                code_commit=git(repo, 'rev-parse', 'HEAD'), code_clean=True, inference_sha256=sha(repo / 'inference.py'),
                gpu=args.gpu, command=cmd)
    if lock:
        info.update(lock=str(LOCK), lock_sha256=LOCK_SHA256, lock_code_commit=lock['code_git_commit'],
                    code_snapshot=str(snap), phase1_config_sha256=sha(AIA / 'configs/phase1/echo_forcing.yaml'),
                    inference_unchanged_since_lock=git(AIA, 'diff', '--stat', lock['code_git_commit'], 'HEAD', '--',
                                                       *s['code']) == '',
                    note='AIA inference.py adds a non-contract context_summary key to RUN.json in the output folder '
                         '(factorial.context_accounting=true); RUN.final.json records the RUN.json sha256 at launch')
    else:
        info.update(method=s['method'], runner='region-forcing scripts/eval/run_eval_ours.sh (python line replicated)',
                    runner_sha256=sha(RF / 'scripts/eval/run_eval_ours.sh'))
    if args.dry_run:
        print(json.dumps(dict(dry_run=True, guards_now=guards, out=str(out), data=str(data),
                              shell=' '.join(map(lambda x: f"'{x}'" if ' ' in x or '[' in x else x, cmd)),
                              RUN_json=info), indent=2))
        return
    if not disk_ok() or not gpu_free(args.gpu):
        raise SystemExit('GPU or disk changed during provenance hashing; nothing started')
    out.mkdir(parents=True)
    run_json = json.dumps(info, indent=2) + '\n'
    (out / 'RUN.json').write_text(run_json)
    t0 = time.monotonic()
    with (out / 'inference.log').open('x') as log:
        res = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    elapsed = time.monotonic() - t0
    vids = sorted(out.glob('*.mp4'))
    text = (out / 'inference.log').read_text(errors='replace')
    outputs = []
    for p in vids:
        n, fps = frames_of(p)
        outputs.append(dict(name=p.name, sha256=sha(p), bytes=p.stat().st_size, frames=n, fps=fps,
                            seconds=(n - 1) / fps if n and fps else None))
    load_lines = [ln for ln in text.splitlines() if ln.startswith('[load]')]
    reasons = []
    if res.returncode != 0:
        reasons.append(f'exit code {res.returncode}')
    if len(vids) != 1:
        reasons.append(f'{len(vids)} mp4 files')
    elif outputs[0]['frames'] is not None and outputs[0]['frames'] != s['frames']:
        reasons.append(f"{outputs[0]['frames']} frames != expected {s['frames']}")
    if lock and STRICT_LOAD not in text:
        reasons.append('strict checkpoint-load evidence missing')
    info.update(status='failed' if reasons else 'complete', failure=reasons, exit_code=res.returncode,
                elapsed_s=elapsed, outputs=outputs, realized_frames=outputs[0]['frames'] if len(outputs) == 1 else None,
                realized_fps=outputs[0]['fps'] if len(outputs) == 1 else None, load_log=load_lines,
                strict_load_825=STRICT_LOAD in text, run_json_sha256_at_launch=hashlib.sha256(run_json.encode()).hexdigest())
    (out / 'RUN.final.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps(dict(system=args.system, scene=args.scene, status=info['status'], elapsed_s=round(elapsed),
                          frames=info['realized_frames'])), flush=True)
    if info['status'] != 'complete':
        raise SystemExit('generation failed: ' + '; '.join(reasons))


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()

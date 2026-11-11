#!/usr/bin/env python3
"""Official VBench (fd18b3d) on one matched 240 s journal rollout at the 60, 120 and 240 s horizons.

    python scripts/score_matched_vbench.py --track t2v --model causvid --scene cf01 --suite long --gpu 2 [--dry-run]
    python scripts/score_matched_vbench.py --track i2v --model <system> --scene pq0092 --suite i2v --gpu 3

Runs under any python with stdlib + psutil (the queue uses snfeval); the GPU work is a subprocess of the
OFFICIAL entrypoints in the pinned worktree /home/minar/VBench-fd18 with the vbench_fd18 interpreter. Nothing
here imports VBench or the method project's tools: their protocol is mirrored, not imported, so no byte is
written under /home/minar/ar-image-animation (source of the rules: AIA tools/snf_v2/{vbench_common,run_vbench}.py
and tools/factorial_scoring/{score_vbench_ext,score_horizon}.py).

Suites (protocol configs/vbench_incumbent_protocol.json):
  long  vbench2_beta_long/eval_long.py --mode long_custom_input --dev_flag --clip_length_config
        clip_length_mix.yaml --sb_clip2clip_feat_extractor dinov2 --bg_clip2clip_feat_extractor dreamsim,
        dims SC BC MS DD AQ IQ (SC before BC: DreamSim resets torch.hub's dir process-wide). Inputs = the
        horizon PREFIXES of the one rollout (window policy 'prefix'): p060 / p120 are the framemd5-verified
        lossless cuts of score_matched_t2v.cut_prefix at raw_matched_2026_11_10/<track>/<m>/<s>/snf/prefixes/
        (cut here with that same function if absent), 240 = the original render file. Staged '<scene>-0.mp4'.
  i2v   evaluate_i2v.py --mode custom_input --dimension i2v_subject i2v_background (I2V track only). The
        official i2v loader holds every frame in memory, so each horizon H is scored on the 961-frame 60 s
        WINDOW ENDING AT H: frames [16(H-60), 16H] (the 60 s window is the p060 prefix itself), cut losslessly
        (libx264 -qp 0, yuv420p, passthrough; AIA score_horizon.seg_cmd) into <scene>/vbench_i2v_windows/
        w120.mp4, w240.mp4 and framemd5-verified against the source. A render shorter than 16H+1 frames uses the last 961 frames (recorded). Staged
        '<scene> camera static-0.mp4' next to images/'<scene> camera static.jpg' -> the conditioning image of
        manifest/public_figure_set_2026_11_05.json (sha256 checked).

Every horizon is ONE official invocation on a FRESH stage dir u/h<HHH>/{stage,out,logs}; the official Long code
silently reuses split_clip/, *_cat_firstframes_videos/ and temporal_filtered_cilps/ when present. Staged names
carry no '_' (Long groups clips by basename.split('_')[0]) and no stage path contains split_clip,
filtered_clips, temporal_filtered or cat_firstframes (the official code splits paths on these).

Output: raw_matched_2026_11_10/<track>/<model>/<scene>/vbench_<suite>/SCORE.json (status complete|failed),
never overwritten (refuses if it exists). Guards before anything is written: no compute process on the GPU
and >= 110 GB free on / (checked again right before the first launch). A refusal creates nothing under
vbench_<suite>/, so the journal queue releases its claim. --dry-run stages everything under
.metric_staging/vbench_matched_2026_11_10/dryrun/ and prints the exact commands; it launches nothing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from score_matched_t2v import FFMPEG, cut_prefix, framemd5  # noqa: E402  (the verified prefix cut)

VB = '/home/minar/VBench-fd18'
VB_REV = 'fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490'
VB_PY = '/home/minar/miniconda3/envs/vbench_fd18/bin/python'
VB_CACHE = '/home/minar/.cache/vbench'          # AIA tools/snf_v2/vbench_common.VB_CACHE
TORCH_HUB = '/home/minar/.cache/torch/hub'
SLOW_FAST = f'{VB}/vbench2_beta_long/configs/slow_fast_params.yaml'
MAP_TABLES = [f'{VB}/vbench2_beta_long/configs/subject_mapping_table.yaml',
              f'{VB}/vbench2_beta_long/configs/background_mapping_table.yaml']
# read-only environment records of the AIA vbench_fd18 install (hashed into provenance, never written)
ENV_FILES = ['/home/minar/ar-image-animation/results/snf_v2/scores/_env/vbench_fd18_freeze.txt',
             '/home/minar/ar-image-animation/results/snf_v2/scores/_env/checkpoints.sha256',
             '/home/minar/ar-image-animation/results/snf_v2/scores/_env/vbench_env.json']
PROTOCOL = ROOT / 'configs/vbench_incumbent_protocol.json'
VIDEOS = ROOT / 'videos/journal_matched_2026_11_10'
SCORES = ROOT / 'raw_matched_2026_11_10'
STAGING = ROOT / '.metric_staging/vbench_matched_2026_11_10'
FIGSET = ROOT / 'manifest/public_figure_set_2026_11_05.json'
MIN_FREE = 110_000_000_000
FPS = 16
HORIZONS = (60, 120, 240)
WIN_S = 60
WIN_N = FPS * WIN_S + 1                         # 961 frames
TOOL = 'snf-bench score_matched_vbench 1.0'

LONG_DIMS = ['subject_consistency', 'background_consistency', 'motion_smoothness', 'dynamic_degree',
             'aesthetic_quality', 'imaging_quality']
I2V_DIMS = ['i2v_subject', 'i2v_background']
LONG_ARGS = ['--mode', 'long_custom_input', '--dev_flag', '--clip_length_config', 'clip_length_mix.yaml',
             '--sb_clip2clip_feat_extractor', 'dinov2', '--bg_clip2clip_feat_extractor', 'dreamsim']
I2V_ARGS = ['--mode', 'custom_input']
SUITES = {'long': dict(entry='vbench2_beta_long/eval_long.py', args=LONG_ARGS, dims=LONG_DIMS),
          'i2v': dict(entry='evaluate_i2v.py', args=I2V_ARGS, dims=I2V_DIMS)}
FORBIDDEN_PATH_PARTS = ('split_clip', 'filtered_clips', 'temporal_filtered', 'cat_firstframes')
OOM = re.compile(r'CUDA out of memory|OutOfMemoryError|CUBLAS_STATUS_ALLOC_FAILED|'
                 r'CUDNN_STATUS_NOT_ENOUGH_WORKSPACE|std::bad_alloc', re.I)
IQ_NOTE = ('imaging_quality: official per-clip MUSIQ values are on 0-100 and the official aggregate divides by '
           '100; every value here is on 0-1')
DEVIATIONS = [
    'horizons are PREFIXES (long) or the 60 s window ending at H (i2v) of ONE 240 s rollout, not separate '
    'generations; never pool with the historical whole-file records',
    'VBench-Long temporal_flickering (protocol dimension) is not in this suite: like AIA run_vbench "long" it '
    'needs separate static-filter / no-filter runs',
    'VBench-I2V camera_motion (protocol dimension) is not run; one sample per image-prompt (protocol: 5)',
    'i2v dims at 120/240 s are on the final 961-frame window, not the whole video (official loader holds all '
    'frames in memory); the 240 s window ends at the last rendered frame when the render has < 3841 frames',
    'VBench-Long per-video value = mean of the official per-clip values (fd18b3d reorganize quirk makes the '
    'official per-video list per clip; for SC/BC the fused 0.5/0.5 per-clip values); official aggregate kept',
    'one video per official invocation (AIA batched 8): adds the model-load overhead per horizon',
    'prompts are read from the staged file names (no --prompt_file); none of these dims uses the prompt text',
]


# ------------------------------------------------------------------------------------------------ utils
def now():
    return time.strftime('%Y-%m-%dT%H:%M:%S%z')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(4 << 20), b''):
            h.update(b)
    return h.hexdigest()


def num(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if x != x or x in (float('inf'), float('-inf')) else x


def clean(o):
    if isinstance(o, float):
        return None if (o != o or o in (float('inf'), float('-inf'))) else o
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    return o


def write_json_new(path, obj):
    """Write path atomically; refuses (FileExistsError) if it already exists: never overwrites."""
    path = Path(path)
    tmp = path.with_name(f'.{path.name}.tmp.{os.getpid()}')
    tmp.write_text(json.dumps(clean(obj), indent=1, default=str) + '\n')
    try:
        os.link(tmp, path)
    finally:
        tmp.unlink()


def rel(p):
    p = Path(p)
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


# ------------------------------------------------------------------------------------- naming (official)
def staged_stem(suite, scene):
    """'<scene>-0' (long) or '<scene> camera static-0' (i2v). get_prompt_from_filename strips '-<digits>';
    camera_motion's get_type needs 'camera static' in the name; Long groups clips by basename.split('_')[0]."""
    if not scene or '_' in scene or '/' in scene or scene != scene.strip() or re.search(r'-\d+$', scene):
        raise ValueError(f'scene id {scene!r} would break VBench naming')
    return f'{scene}-0' if suite == 'long' else f'{scene} camera static-0'


def image_stem(scene):
    return staged_stem('i2v', scene)[:-2]


def check_stage_path(path):
    """Refuse a staged file whose basename has '_' or whose path has a part the official code splits on."""
    p = Path(path)
    bad = [x for x in FORBIDDEN_PATH_PARTS if x in str(p)]
    if bad:
        raise ValueError(f'{p}: path contains {bad} (official VBench splits paths on these)')
    if '_' in p.name:
        raise ValueError(f'{p}: staged name contains "_" (VBench-Long groups clips by basename.split("_")[0])')
    return p


def long_clip_plan(n, fps=FPS):
    """Official split_video_into_clips(duration=2): L = int(fps)*2; [kL,(k+1)L); remainder -> one clip extended
    backwards to L frames."""
    L = int(fps) * 2
    if n < L:
        return [('full', 0, n)]
    total, rem = divmod(n, L)
    plan = [(i, i * L, (i + 1) * L) for i in range(total)]
    if rem:
        plan.append((total, total * L - (L - rem), n))
    return plan


def window_frames(h, total, n=WIN_N, fps=FPS):
    """[first, last] (inclusive) of the n-frame window ending at h s, clamped to the last rendered frame."""
    last = min(int(round(h * fps)), total - 1)
    first = last - (n - 1)
    if first < 0:
        raise ValueError(f'render has {total} frames: no {n}-frame window ends at {h} s')
    return first, last


# ------------------------------------------------------------------------------------------- guards
def gpu_busy(gpu):
    """Compute processes on GPU index `gpu` (read-only nvidia-smi, as scripts/journal_queue.gpu_idle)."""
    rows = [r.split(', ') for r in subprocess.check_output(
        ['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader'], text=True, timeout=30).splitlines()]
    uuid = next(u for i, u in rows if int(i) == gpu)
    apps = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid,used_memory',
                                    '--format=csv,noheader'], text=True, timeout=30).splitlines()
    return [a for a in apps if a.startswith(uuid)]


def free_bytes(path='/'):
    s = os.statvfs(path)
    return s.f_bavail * s.f_frsize


def guards(gpu):
    probs = []
    busy = gpu_busy(gpu)
    if busy:
        probs.append(f'GPU {gpu} has compute processes: {busy}')
    fb = free_bytes('/')
    if fb < MIN_FREE:
        probs.append(f'/ has {fb / 1e9:.0f} GB free (< {MIN_FREE / 1e9:.0f} GB)')
    return probs


def vbench_checks():
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    rev = subprocess.run(['git', '-C', VB, 'rev-parse', 'HEAD'], capture_output=True, text=True, env=env).stdout.strip()
    dirty = subprocess.run(['git', '-C', VB, 'status', '--porcelain', '--untracked-files=no'], capture_output=True,
                           text=True, env=env).stdout.strip()
    probs = []
    if rev != VB_REV:
        probs.append(f'{VB} at {rev}, expected {VB_REV}')
    if dirty:
        probs.append(f'{VB} has modified tracked files: {dirty[:300]}')
    if not os.access(VB_PY, os.X_OK):
        probs.append(f'{VB_PY} missing')
    if not os.path.isdir(VB_CACHE):
        probs.append(f'{VB_CACHE} missing')
    w = {}
    for ln in Path(SLOW_FAST).read_text().splitlines():
        m = re.match(r'^\s*(w_inclip_sb|w_clip2clip_sb|w_inclip_bg|w_clip2clip_bg)\s*:\s*([0-9.]+)', ln)
        if m:
            w[m.group(1)] = float(m.group(2))
    if w != dict(w_inclip_sb=0.5, w_clip2clip_sb=0.5, w_inclip_bg=0.5, w_clip2clip_bg=0.5):
        probs.append(f'dev_flag weights {w} are not the 0.5/0.5 protocol')
    return rev, w, probs


# ------------------------------------------------------------------------------------------- inputs
def load_render(track, model, scene):
    run_dir = VIDEOS / track / model / scene / '240s'
    run = json.loads((run_dir / 'RUN.final.json').read_text())
    if run.get('status') != 'complete':
        raise SystemExit(f'{run_dir}: render is not complete')
    out0 = run['outputs'][0]
    src = run_dir / out0['name']
    s = sha(src)
    if s != out0['sha256']:
        raise SystemExit(f'{src}: sha256 {s[:12]} differs from RUN.final.json {out0["sha256"][:12]}')
    prompt = run.get('prompt')
    if prompt is None and (run_dir / 'prompt.txt').exists():
        prompt = (run_dir / 'prompt.txt').read_text().strip()
    run['_probe'] = probe(src)
    if run['_probe'].get('fps') != FPS:
        raise SystemExit(f'{src}: stream is {run["_probe"]} but the horizon/window frame rule assumes {FPS} fps')
    return run_dir, run, src, prompt


def probe(path):
    """fps / size from the ffmpeg stream line (no ffprobe in this environment)."""
    txt = subprocess.run([FFMPEG, '-hide_banner', '-nostdin', '-i', str(path)], capture_output=True, text=True).stderr
    m = re.search(r'Video: .*?, (\d+)x(\d+).*?, ([\d.]+) fps', txt)
    if not m:
        return dict(error='no video stream line', stream=txt[-300:])
    fps = float(m.group(3))
    return dict(width=int(m.group(1)), height=int(m.group(2)), fps=int(fps) if fps.is_integer() else fps)


def conditioning_image(scene, run):
    scenes = {x['id']: x for x in json.loads(FIGSET.read_text())['scenes']}
    if scene not in scenes:
        raise SystemExit(f'{scene} is not in {rel(FIGSET)}')
    e = scenes[scene]
    img = ROOT / e['image']
    s = sha(img)
    if s != e['image_sha256']:
        raise SystemExit(f'{img}: sha256 {s[:12]} != manifest {e["image_sha256"][:12]}')
    for k in ('image_sha256', 'conditioning_image_sha256', 'source_image_sha256', 'conditioning_sha256'):
        if run.get(k) and run[k] != s:
            raise SystemExit(f'RUN.final.json {k} {run[k][:12]} != conditioning image {s[:12]}')
    return dict(path=rel(img), abspath=str(img), sha256=s, manifest=rel(FIGSET), manifest_sha256=sha(FIGSET),
                licence=e.get('licence'), benchmark=e.get('benchmark'))


def horizon_prefixes(src, md5s, pre_dir, real_pre_dir):
    """{H: record} for the 'long' inputs. Existing real prefixes are used read-only and re-verified by framemd5;
    a missing one is cut with score_matched_t2v.cut_prefix into pre_dir (the real snf/prefixes dir, or the
    dry-run dir)."""
    total = len(md5s)
    out = {}
    for h in HORIZONS:
        n = FPS * h + 1
        if h == 240 or n >= total:
            out[h] = dict(path=rel(src), frames=total, first=0, last=total - 1, sha256=sha(src),
                          verified='original render file')
            continue
        real = real_pre_dir / f'p{h:03d}.mp4'
        dst = real if real.exists() else pre_dir / f'p{h:03d}.mp4'
        existed = dst.exists()
        dst.parent.mkdir(parents=True, exist_ok=True)
        rec = cut_prefix(src, n, dst)
        if existed:
            got = framemd5(dst, n + 1)
            if got != md5s[:n]:
                raise SystemExit(f'{dst}: existing prefix is not frame-identical to the source')
            rec['verified'] = 'existing prefix; framemd5 re-verified identical to source'
        else:
            rec['verified'] = 'cut here by score_matched_t2v.cut_prefix; framemd5 identical to source'
        out[h] = dict(rec, first=0, last=n - 1)
    return out


def seg_cmd(src, first, n, out):
    """AIA score_horizon.seg_cmd for first > 0: accurate input seek + the prefix encoder settings."""
    return [FFMPEG, '-nostdin', '-hide_banner', '-v', 'error', '-y', '-ss', f'{first / FPS:.6f}', '-i', str(src),
            '-map', '0:v:0', '-frames:v', str(n), '-an', '-sn', '-dn', '-c:v', 'libx264', '-preset', 'veryfast',
            '-qp', '0', '-pix_fmt', 'yuv420p', '-fps_mode', 'passthrough', '-threads', '8', str(out)]


def horizon_windows(src, md5s, prefixes, win_dir):
    """{H: record} for the i2v inputs: the 961-frame window ending at H (the 60 s one is the p060 prefix)."""
    total = len(md5s)
    out = {}
    for h in HORIZONS:
        first, last = window_frames(h, total)
        if first == 0 and prefixes[60]['frames'] == WIN_N:
            out[h] = dict(prefixes[60], first=0, last=WIN_N - 1, window_end_s=last / FPS,
                          verified=prefixes[60]['verified'] + ' (60 s window = p060 prefix)')
            continue
        dst = win_dir / f'w{h:03d}.mp4'
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            tmp = dst.with_suffix('.part.mp4')
            cmd = seg_cmd(src, first, WIN_N, tmp)
            subprocess.run(cmd, check=True)
            got = framemd5(tmp, WIN_N + 1)
            if got != md5s[first:first + WIN_N]:
                tmp.unlink()
                raise SystemExit(f'{dst}: window [{first},{last}] is not frame-identical ({len(got)} frames)')
            tmp.rename(dst)
            how = 'cut here (AIA score_horizon.seg_cmd); framemd5 identical to source frames [first,last]'
        else:
            if framemd5(dst, WIN_N + 1) != md5s[first:first + WIN_N]:
                raise SystemExit(f'{dst}: existing window is not frame-identical to source [{first},{last}]')
            how = 'existing window; framemd5 re-verified identical to source frames [first,last]'
        out[h] = dict(path=rel(dst), frames=WIN_N, first=first, last=last, window_end_s=last / FPS,
                      sha256=sha(dst), verified=how,
                      cmd=shlex.join(seg_cmd(rel(src), first, WIN_N, dst.name)))
    return out


# ------------------------------------------------------------------------------------- staging / run
def stage_unit(udir, suite, scene, inp, image=None):
    """Fresh u/h<HHH>/{stage,out,logs}; returns (videos_path, image_folder, staged_name)."""
    if os.path.lexists(udir):
        raise SystemExit(f'{udir} exists: every official invocation needs a fresh stage dir')
    stem = staged_stem(suite, scene)
    st = udir / 'stage'
    for d in ('out', 'logs'):
        (udir / d).mkdir(parents=True)
    src = Path(os.path.abspath(ROOT / inp['path']))     # absolute, symlinks not resolved (as AIA)
    if suite == 'long':
        st.mkdir()
        link = check_stage_path(st / f'{stem}.mp4')
        os.symlink(src, link)
        return st, None, link.name
    (st / 'videos').mkdir(parents=True)
    (st / 'images').mkdir()
    link = check_stage_path(st / 'videos' / f'{stem}.mp4')
    os.symlink(src, link)
    il = check_stage_path(st / 'images' / f'{image_stem(scene)}.jpg')
    os.symlink(image['abspath'], il)
    return st / 'videos', st / 'images', link.name


def build_cmd(suite, videos_path, image_folder, out_dir):
    c = SUITES[suite]
    cmd = [VB_PY, c['entry']] + c['args'] + ['--videos_path', str(videos_path)]
    if image_folder is not None:
        cmd += ['--custom_image_folder', str(image_folder)]
    return cmd + ['--output_path', str(out_dir), '--dimension'] + c['dims']


def child_env(gpu):
    env = dict(os.environ)
    for k in ('VBENCH_MAX_FRAMES', 'LOCAL_RANK', 'RANK', 'WORLD_SIZE', 'MASTER_ADDR', 'MASTER_PORT'):
        env.pop(k, None)
    env.update(CUDA_VISIBLE_DEVICES=str(gpu), PYTHONPATH=VB, VBENCH_CACHE_DIR=VB_CACHE, PYTHONUNBUFFERED='1',
               VBENCH_ROOT=VB)
    return env


def env_prefix(gpu):
    return (f'cd {VB} && CUDA_VISIBLE_DEVICES={gpu} PYTHONPATH={VB} VBENCH_CACHE_DIR={VB_CACHE} '
            f'PYTHONUNBUFFERED=1 VBENCH_ROOT={VB} ')


class GpuPoll(threading.Thread):
    """nvidia-smi every dt s (read-only): peak used_memory of the child's process tree (AIA run_vbench.GpuPoll)."""

    def __init__(self, root_pid, gpu, log_path, dt=2.0):
        super().__init__(daemon=True)
        self.root, self.gpu, self.log_path, self.dt = root_pid, str(gpu), log_path, dt
        self.peak, self.dev_peak, self.samples = 0, None, 0
        self.ev = threading.Event()

    def pids(self):
        try:
            import psutil
            p = psutil.Process(self.root)
            return {self.root} | {c.pid for c in p.children(recursive=True)}
        except Exception:
            return {self.root}

    def run(self):
        with open(self.log_path, 'a') as lf:
            while not self.ev.is_set():
                try:
                    a = subprocess.run(['nvidia-smi', '--query-compute-apps=pid,used_memory',
                                        '--format=csv,noheader,nounits', '-i', self.gpu],
                                       capture_output=True, text=True, timeout=30).stdout
                    d = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits',
                                        '-i', self.gpu], capture_output=True, text=True, timeout=30).stdout
                    mine, use = self.pids(), 0
                    for ln in a.strip().splitlines():
                        parts = [x.strip() for x in ln.split(',')]
                        if len(parts) == 2 and parts[0].isdigit() and int(parts[0]) in mine and parts[1].isdigit():
                            use += int(parts[1])
                    dev = int(d.strip().splitlines()[0]) if d.strip() else None
                    self.peak = max(self.peak, use)
                    if dev is not None:
                        self.dev_peak = max(self.dev_peak or 0, dev)
                    self.samples += 1
                    lf.write(f'{time.time():.1f},{use},{dev}\n')
                    lf.flush()
                except Exception as e:  # monitoring never kills the run
                    lf.write(f'# poll error {e}\n')
                self.ev.wait(self.dt)


def parse_time_v(path):
    d = {}
    try:
        for ln in Path(path).read_text(errors='replace').splitlines():
            ln = ln.strip()
            if ln.startswith('Elapsed (wall clock) time'):
                s = 0.0
                for x in ln.split('):', 1)[-1].strip().split(':'):
                    s = s * 60 + float(x)
                d['wall_s'] = s
            elif ln.startswith('Maximum resident set size'):
                d['max_rss_kb'] = int(ln.rsplit(':', 1)[-1])
    except OSError:
        pass
    return d


def run_unit(key, cmd, gpu, logs):
    log, tfile, gfile = logs / f'{key}.log', logs / f'{key}.time.txt', logs / f'{key}.gpu_mem.csv'
    env = child_env(gpu)
    full = ['/usr/bin/time', '-v', '-o', str(tfile)] + cmd
    t0 = time.time()
    with open(log, 'w') as lf:
        lf.write(f'# cwd={VB}\n# CUDA_VISIBLE_DEVICES={gpu} PYTHONPATH={VB} VBENCH_CACHE_DIR={VB_CACHE}\n'
                 f'# {shlex.join(full)}\n')
        lf.flush()
        p = subprocess.Popen(full, cwd=VB, env=env, stdout=lf, stderr=subprocess.STDOUT)
        poll = GpuPoll(p.pid, gpu, gfile)
        poll.start()
        rc = p.wait()
        poll.ev.set()
        poll.join(timeout=60)
    tv = parse_time_v(tfile)
    return dict(cmd=shlex.join(full), cwd=VB, rc=rc, log=rel(log), wall_s=tv.get('wall_s', round(time.time() - t0, 2)),
                max_rss_kb=tv.get('max_rss_kb'), gpu_peak_mib_child=poll.peak if poll.samples else None,
                gpu_device_used_mib_peak=poll.dev_peak, gpu_samples=poll.samples, finished=now())


def failure_reason(log, rc):
    txt = Path(log).read_text(errors='replace') if Path(log).exists() else ''
    m = OOM.search(txt)
    if m:
        return f'OOM ({m.group(0)}); exit {rc}'
    err = [ln for ln in txt.splitlines() if re.match(r'^\w*(Error|Exception)\b', ln.strip())]
    tail = [ln for ln in txt.splitlines() if ln.strip()][-1:] or ['']
    return f'exit {rc}: {(err[-1] if err else tail[-1]).strip()[:300]}'


def results_json(out_dir):
    c = sorted(Path(out_dir).glob('*_eval_results.json'), key=os.path.getmtime)
    return c[-1] if c else None


# ------------------------------------------------------------------------------------------- flatten
def flatten_long(res, stem, n_frames):
    """Per dim: mean of the official per-clip values of this video (SC/BC: fused list entry[1]; others: the
    per-clip list entry[1]); IQ / 100. Returns (values, details, per_clip, notes)."""
    vals, det, clips, notes = {}, {}, {}, []
    n_plan = len(long_clip_plan(n_frames))
    for dim in LONG_DIMS:
        e = res.get(dim)
        if not isinstance(e, list) or len(e) < 2 or not isinstance(e[1], list):
            notes.append(f'{dim}: no per-clip list in the official output')
            continue
        items = [it for it in e[1] if isinstance(it, dict) and f'/split_clip/{stem}/' in it.get('video_path', '')]
        if len(items) != len(e[1]):
            notes.append(f'{dim}: {len(e[1]) - len(items)} official items do not map to {stem}')
        pc = []
        for it in items:
            v = num(it.get('video_results'))
            if dim == 'imaging_quality' and v is not None:
                v /= 100.0
            m = re.search(r'_(\d+|full)\.mp4', it['video_path'])
            pc.append(dict(clip=m.group(1) if m else it['video_path'], value=v,
                           **{k: it[k] for k in ('inclip_score', 'clip2clip_score', 'mapped_clip2clip_score')
                              if k in it}))
        ok = [x['value'] for x in pc if x['value'] is not None]
        vals[dim] = sum(ok) / len(ok) if ok else None
        det[dim] = dict(official_aggregate=num(e[0]), n_clips=len(pc), n_clips_official_plan=n_plan)
        if dim in ('subject_consistency', 'background_consistency') and pc:
            c2c = {x.get('clip2clip_score') for x in pc}
            if len(c2c) > 1:
                notes.append(f'{dim}: clip2clip not constant within the video')
            det[dim].update(inclip_mean=sum(x['inclip_score'] for x in pc) / len(pc),
                            clip2clip=next(iter(c2c)), mapped_clip2clip=pc[0].get('mapped_clip2clip_score'))
        if len(pc) != n_plan:
            notes.append(f'{dim}: {len(pc)} clip values for {n_plan} planned clips')
        clips[dim] = pc
    return vals, det, clips, notes


def flatten_i2v(res, stem):
    vals, det, notes = {}, {}, []
    for dim in I2V_DIMS:
        e = res.get(dim)
        items = [it for it in (e[1] if isinstance(e, list) and len(e) > 1 and isinstance(e[1], list) else [])
                 if isinstance(it, dict) and Path(it.get('video_path', '')).name == f'{stem}.mp4']
        if len(items) != 1:
            notes.append(f'{dim}: {len(items)} official items for {stem}.mp4')
            continue
        vals[dim] = num(items[0].get('video_results'))
        det[dim] = dict(official_aggregate=num(e[0]), image_path=items[0].get('image_path'))
    return vals, det, notes


def split_clip_report(stage, stem, n_frames):
    d = Path(stage) / 'split_clip' / stem
    files = sorted(os.listdir(d)) if d.is_dir() else []
    plan = long_clip_plan(n_frames)
    exp = [f'{stem}_{i:03d}.mp4' if i != 'full' else f'{stem}_full.mp4' for i, _, _ in plan]
    return dict(rule='official split_video_into_clips(duration=2); clips re-encoded by torchvision.io.write_video',
                n_clips=len(plan), matches_plan=files == exp,
                clips=[dict(file=f, start=s, end_exclusive=e,
                            sha256=sha(d / f) if (d / f).is_file() else None) for (_, s, e), f in zip(plan, exp)])


# ----------------------------------------------------------------------------------------------- main
def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('--track', required=True, choices=('t2v', 'i2v'))
    a.add_argument('--model', required=True)
    a.add_argument('--scene', required=True)
    a.add_argument('--suite', required=True, choices=('long', 'i2v'))
    a.add_argument('--gpu', required=True, type=int, choices=(2, 3))
    a.add_argument('--dry-run', action='store_true', help='stage + check + print commands under .metric_staging')
    args = a.parse_args(argv)
    if args.suite == 'i2v' and args.track != 'i2v':
        raise SystemExit('--suite i2v needs --track i2v (it scores against the conditioning image)')
    for x in (args.model, args.scene):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', x):
            raise SystemExit(f'bad id {x!r}')
    staged_stem(args.suite, args.scene)                     # naming rules before anything else
    cfg = SUITES[args.suite]
    t_start = time.monotonic()

    out = SCORES / args.track / args.model / args.scene / f'vbench_{args.suite}'
    done = out / 'SCORE.json'
    if done.exists():
        raise SystemExit(f'{done} exists; scores are never overwritten')
    run_dir, run, src, prompt = load_render(args.track, args.model, args.scene)
    image = conditioning_image(args.scene, run) if args.track == 'i2v' else None
    vb_rev, weights, vprobs = vbench_checks()
    gprobs = guards(args.gpu)
    if args.dry_run:
        for p in vprobs + gprobs:
            print(f'[dry-run] WARNING: a real run would refuse: {p}')
    elif vprobs or gprobs:
        raise SystemExit('refused: ' + '; '.join(vprobs + gprobs))

    # inputs (CPU): verified prefixes / windows
    real_pre = SCORES / args.track / args.model / args.scene / 'snf' / 'prefixes'
    if args.dry_run:
        dry = STAGING / 'dryrun' / args.track / args.model / args.scene
        pre_dir, win_dir = dry / 'prefixes', dry / 'windows'
        work = dry / f'vbench_{args.suite}-{time.strftime("%Y%m%d-%H%M%S")}'
    else:
        # windows live beside, not inside, vbench_i2v/: a refusal must leave the queue's done-parent absent
        pre_dir, win_dir, work = real_pre, out.parent / 'vbench_i2v_windows', out
    md5s = framemd5(src, 10 ** 6)
    prefixes = horizon_prefixes(src, md5s, pre_dir, real_pre)
    if args.suite == 'i2v':
        inputs = horizon_windows(src, md5s, prefixes, win_dir)
        window_policy = 'window ending at H, 60 s'
    else:
        inputs = prefixes
        window_policy = 'prefix'

    if not args.dry_run:
        gprobs = guards(args.gpu)                           # again, right before the first launch
        if gprobs:
            raise SystemExit('refused: ' + '; '.join(gprobs))
        if out.exists():                                    # an interrupted attempt (no SCORE.json): keep it
            arch = out.with_name(f'{out.name}.prev-{time.strftime("%Y%m%d-%H%M%S")}')
            out.rename(arch)
            print(f'archived incomplete {rel(out)} -> {arch.name}', flush=True)
    for x in FORBIDDEN_PATH_PARTS:
        if x in str(work):
            raise SystemExit(f'{work} contains {x}')
    work.mkdir(parents=True, exist_ok=True)

    horizons, notes = {}, []
    for h in HORIZONS:
        key = f'h{h:03d}'
        udir = work / 'u' / key
        vp, imgf, staged = stage_unit(udir, args.suite, args.scene, inputs[h], image)
        cmd = build_cmd(args.suite, vp, imgf, udir / 'out')
        rec = dict(input=inputs[h], staged_name=staged, stage=rel(udir / 'stage'),
                   video_s=round((inputs[h]['frames'] - 1) / FPS, 4))
        if args.dry_run:
            print(f'[dry-run] {key}: {env_prefix(args.gpu)}{shlex.join(cmd)}', flush=True)
            rec.update(status='dry-run', cmd=env_prefix(args.gpu) + shlex.join(cmd))
            horizons[str(h)] = rec
            continue
        print(f'[vbench] {args.track} {args.model} {args.scene} {args.suite} {key}: running on GPU {args.gpu}',
              flush=True)
        u = run_unit(key, cmd, args.gpu, udir / 'logs')
        rj = results_json(udir / 'out')
        rec['unit'] = u
        if u['rc'] != 0 or rj is None:
            rec.update(status='failed', reason=failure_reason(ROOT / u['log'], u['rc']) if u['rc'] else
                       'exit 0 but no *_eval_results.json', values={d: None for d in cfg['dims']})
        else:
            res = json.loads(rj.read_text())
            stem = staged[:-4]
            if args.suite == 'long':
                vals, det, clips, nt = flatten_long(res, stem, inputs[h]['frames'])
                (udir / 'per_clip.json').write_text(json.dumps(clean(clips), indent=1) + '\n')
                rec['split_clips'] = split_clip_report(udir / 'stage', stem, inputs[h]['frames'])
                rec['per_clip'] = rel(udir / 'per_clip.json')
                if not rec['split_clips']['matches_plan']:
                    nt.append('split_clip files differ from the official plan')
            else:
                vals, det, nt = flatten_i2v(res, stem)
            missing = [d for d in cfg['dims'] if vals.get(d) is None]
            rec.update(status='complete' if not missing else 'failed',
                       reason=f'no value for {missing}' if missing else '', values={d: vals.get(d) for d in cfg['dims']},
                       official=det, results_json=rel(rj), notes=nt)
            notes += [f'{h}s {n}' for n in nt]
        print(f'[vbench]   -> {rec["status"]} wall={u["wall_s"]}s gpu_peak={u["gpu_peak_mib_child"]}MiB '
              f'{rec.get("reason", "")}', flush=True)
        horizons[str(h)] = rec

    report = dict(
        status=('dry-run' if args.dry_run else
                'complete' if all(r['status'] == 'complete' for r in horizons.values()) else 'failed'),
        track=args.track, model=args.model, scene=args.scene, suite=args.suite,
        role='journal matched-horizon development scores',
        role_note='within-rollout trajectory of one 240 s render; never pool with historical whole-file records',
        window_policy=window_policy,
        window_rule=('first 16*H+1 frames of the rollout; 240 s = the whole file' if args.suite == 'long' else
                     f'{WIN_N} frames [16(H-60), 16H], clamped to end at the last rendered frame'),
        render=dict(dir=rel(run_dir), file=run['outputs'][0]['name'], sha256=run['outputs'][0]['sha256'],
                    frames=len(md5s), fps=FPS, width=run['_probe'].get('width'), height=run['_probe'].get('height'),
                    setting=run.get('setting'), category=run.get('category'),
                    seed=run.get('seed'), checkpoint_sha256=run.get('checkpoint_sha256')),
        prompt=prompt, prompt_sha256=run.get('prompt_sha256'), conditioning_image=image,
        dims=cfg['dims'], values={h: r.get('values') for h, r in horizons.items()}, horizons=horizons,
        input_sha256={h: r['input']['sha256'] for h, r in horizons.items()},
        official=dict(repository='https://github.com/Vchitect/VBench', revision=vb_rev, path=VB,
                      entrypoint=cfg['entry'], entry_sha256=sha(f'{VB}/{cfg["entry"]}'), args=cfg['args'],
                      dimension=cfg['dims'], python=VB_PY, cwd=VB,
                      env=dict(CUDA_VISIBLE_DEVICES=str(args.gpu), PYTHONPATH=VB, VBENCH_CACHE_DIR=VB_CACHE,
                               TORCH_HUB=TORCH_HUB),
                      dev_flag=(dict(weights=weights, slow_fast_params_sha256=sha(SLOW_FAST),
                                     mapping_tables={Path(p).name: sha(p) for p in MAP_TABLES})
                                if args.suite == 'long' else None),
                      env_records={p: (sha(p) if os.path.exists(p) else None) for p in ENV_FILES}),
        protocol=dict(path=rel(PROTOCOL), sha256=sha(PROTOCOL)),
        deviations_from_protocol=DEVIATIONS, imaging_quality_scale=IQ_NOTE if args.suite == 'long' else None,
        notes=notes, wall_s=round(time.monotonic() - t_start, 1),
        gpu_wall_s=sum((r.get('unit') or {}).get('wall_s') or 0 for r in horizons.values()),
        gpu_peak_mib_child=max([(r.get('unit') or {}).get('gpu_peak_mib_child') or 0 for r in horizons.values()]),
        gpu=args.gpu, tool=TOOL, tool_sha256={Path(__file__).name: sha(__file__),
                                              'score_matched_t2v.py': sha(ROOT / 'scripts/score_matched_t2v.py')},
        command=shlex.join([sys.executable] + sys.argv), host=os.uname().nodename, written=now())
    if args.dry_run:
        write_json_new(work / 'DRYRUN.json', report)
        print(f'[dry-run] staged {rel(work)}; plan {rel(work / "DRYRUN.json")}; a real run writes {rel(done)}; '
              f'nothing launched', flush=True)
        return 0
    write_json_new(done, report)
    print(json.dumps(dict(track=args.track, model=args.model, scene=args.scene, suite=args.suite,
                          status=report['status'], wall_s=report['wall_s'])), flush=True)
    if report['status'] != 'complete':
        raise SystemExit('scoring failed; see SCORE.json horizons[*].reason and u/*/logs')
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Render the public-benchmark I2V figure set with published systems' released recipes.

Conditioning set: manifest/public_figure_set_2026_11_05.json (Physics-IQ CC BY 4.0,
VBench-I2V Pexels). Renders are exposure-logged visual material for figures,
not confirmation data (manifest/realism_dev_split_2026_11_05_amendment_1.json).

Systems are run only with their released inference recipe; anything else is a
labelled deviation in the sidecar. Each run writes:

    videos/public_bench/renders/<system>/<horizon>/<scene>.mp4   (gitignored)
    videos/public_bench/renders/<system>/<horizon>/<scene>.json  (sidecar)
    videos/public_bench/renders/<system>/<horizon>/RUN.json

and refuses to overwrite. GPU policy: GPUs 2 and 3 only, one generation per GPU,
never beside RAFT or VBench scorers (method-project AGENTS.md; the 2026-10 cuDNN
corruption). The co-tenant snapshot is recorded; timings under contention are
not publishable cost measurements.

    python scripts/render_public_figure_set.py causal_forcing --gpu 2
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOME = "/home/minar"
MAN = os.path.join(ROOT, "manifest/public_figure_set_2026_11_05.json")
OUT = os.path.join(ROOT, "videos/public_bench/renders")
DISK_MIN = 110e9       # bytes free on / (AIA's 100 GiB guard, plus margin)

SYSTEMS = {
    # Released I2V command from the upstream README ("Our frame-wise setting natively
    # supports I2V"): frame-wise checkpoint, 21 latent frames = 81 frames = 5 s, seed 0.
    # The local checkout differs from upstream 8e1ef8f only in checkpoint paths.
    "causal_forcing": dict(
        name="Causal-Forcing (frame-wise)", horizon="5s", repo=f"{HOME}/Causal-Forcing",
        image="regfor:cuda12.1", config="configs/causal_forcing_dmd_framewise.yaml",
        ckpt=f"{HOME}/ckpt/causal-forcing/framewise/causal_forcing.pt", seed=0,
        identity="upstream released I2V command (README, 'NEW: I2V')",
        deviations=["checkpoint paths edited to ../ckpt (no behavioural change)"],
        cmd=lambda inp, out, s: ["python", "inference.py", "--config_path", "configs/causal_forcing_dmd_framewise.yaml",
                                 "--output_folder", out, "--checkpoint_path",
                                 "../ckpt/causal-forcing/framewise/causal_forcing.pt",
                                 "--data_path", inp, "--i2v", "--use_ema", "--seed", str(s)]),
    # LTX-Video's official inference.py with the released distilled multi-scale config, 121 frames at
    # 24 fps (~5 s), driven per clip by region-forcing's run_ltx_i2v_baseline.py. The released config
    # enhances prompts under 120 words with Florence-2 + Llama-3.2-3B; our prompts are 37-50 words, so a
    # copy with prompt_enhancement_words_threshold 0 is used to keep every system on the same text.
    "ltx_video": dict(
        name="LTX-Video 13B 0.9.8 distilled", horizon="5s", repo=f"{HOME}/baseline_repos/LTX-Video",
        workdir=f"{HOME}/region-forcing", image="regfor:cuda12.1",
        config="configs/ltxv-13b-0.9.8-distilled.yaml",
        ckpt=f"{HOME}/baseline_repos/LTX-Video/models/ltxv-13b-0.9.8-distilled.safetensors", seed=0,
        identity="official inference.py, released distilled multi-scale config",
        deviations=["prompt_enhancement_words_threshold 120 -> 0 (enhancement off, same text for every system)",
                    "config checkpoint paths made absolute (no behavioural change)",
                    "text encoder PixArt-XL-2-1024-MS from a local cache copied out of the regfor_eval container"],
        env={"HF_HOME": f"{HOME}/ckpt/hf_cache_ltx"},
        prepare=lambda work, spec: ltx_config(work, spec),
        cmd=lambda inp, out, s, cfg=None: ["python", "scripts/eval/run_ltx_i2v_baseline.py",
                                           "--json", f"{inp}/target_crop_info_26-15.json", "--img_dir", f"{inp}/26-15",
                                           "--out_dir", out, "--config", cfg, "--seed", str(s)]),
    # Official Wan2.1 README single-GPU I2V command (generate.py, --task i2v-14B --size 832*480):
    # its own defaults give shift 3.0 at 832x480, guidance 5.0, 40 steps, 81 frames at 16 fps, offload on.
    "wan21": dict(
        name="Wan2.1-I2V-14B-480P", horizon="5s", repo=f"{HOME}/Wan2.1", image="wan22:cuda12.1",
        config="wan/configs/wan_i2v_14B.py", ckpt=f"{HOME}/ckpt/wan_models/Wan2.1-I2V-14B-480P", seed=0,
        identity="official README single-GPU I2V command, generate.py defaults",
        deviations=["--base_seed 0 (README leaves it random)",
                    "one generate.py call per scene via scripts/wan_official_loop.py (no behavioural change)"],
        cmd=lambda inp, out, s: ["python", "/workspace/snf-bench/scripts/wan_official_loop.py",
                                 "--json", f"{inp}/target_crop_info_26-15.json", "--img_dir", f"{inp}/26-15",
                                 "--out", out, "--", "--task", "i2v-14B", "--size", "832*480",
                                 "--ckpt_dir", "/workspace/ckpt/wan_models/Wan2.1-I2V-14B-480P",
                                 "--base_seed", str(s)]),
    # Official Wan2.2 README single-GPU I2V command (--offload_model True --convert_model_dtype); config
    # defaults: guidance (3.5, 3.5), 40 steps, shift 5.0, boundary 0.9, 81 frames at 16 fps. 832*480 is a
    # supported i2v-A14B size; the README example uses 1280*720.
    "wan22": dict(
        name="Wan2.2-I2V-A14B", horizon="5s", repo=f"{HOME}/Wan2.2", image="wan22:cuda12.1",
        config="wan/configs/wan_i2v_A14B.py", ckpt=f"{HOME}/ckpt/wan_models/Wan2.2-I2V-A14B", seed=0,
        identity="official README single-GPU I2V command, config defaults",
        deviations=["--size 832*480 instead of the README example 1280*720 (a supported size; matches the panel)",
                    "--base_seed 0 (README leaves it random)",
                    "one generate.py call per scene via scripts/wan_official_loop.py (no behavioural change)"],
        cmd=lambda inp, out, s: ["python", "/workspace/snf-bench/scripts/wan_official_loop.py",
                                 "--json", f"{inp}/target_crop_info_26-15.json", "--img_dir", f"{inp}/26-15",
                                 "--out", out, "--", "--task", "i2v-A14B", "--size", "832*480",
                                 "--ckpt_dir", "/workspace/ckpt/wan_models/Wan2.2-I2V-A14B",
                                 "--offload_model", "True", "--convert_model_dtype", "--base_seed", str(s)]),
}


def ltx_config(work, spec):
    src = os.path.join(spec["repo"], spec["config"])
    dst = f"{work}/ltxv-13b-0.9.8-distilled.no-enhance.yaml"
    text = open(src).read()
    if "prompt_enhancement_words_threshold: 120" not in text:
        raise SystemExit(f"{src}: enhancement threshold is not the released 120; refusing to guess")
    open(dst, "w").write(text.replace("prompt_enhancement_words_threshold: 120",
                                      "prompt_enhancement_words_threshold: 0"))
    return dst


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tree_sha256(d):
    """SHA-256 over (relative path, file SHA-256) of every file in a checkpoint directory; a symlink
    contributes its target string instead (Wan's transformer/ links point at container paths)."""
    h = hashlib.sha256()
    for root, _, files in sorted(os.walk(d)):
        for f in sorted(files):
            p = os.path.join(root, f)
            v = "-> " + os.readlink(p) if os.path.islink(p) else sha256(p)
            h.update(f"{os.path.relpath(p, d)}\t{v}\n".encode())
    return h.hexdigest()


def ws(path):
    """Host path under /home/minar -> container path under /workspace."""
    return path.replace(HOME, "/workspace", 1)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True).stdout.strip()


def gpu_snapshot(gpu):
    q = subprocess.run(["nvidia-smi", "-i", str(gpu), "--query-gpu=utilization.gpu,memory.used,name",
                        "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
    apps = subprocess.run(["nvidia-smi", "-i", str(gpu), "--query-compute-apps=pid,used_memory",
                           "--format=csv,noheader"], capture_output=True, text=True).stdout.strip().splitlines()
    procs = []
    for line in apps:
        pid = line.split(",")[0].strip()
        cmd = subprocess.run(["ps", "-o", "user=,cmd=", "-p", pid], capture_output=True, text=True).stdout.strip()
        procs.append(f"{line} | {cmd[:160]}")
    return dict(gpu=gpu, state=q, processes=procs)


def probe(path):
    cap = cv2.VideoCapture(path)
    got = dict(frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), fps=cap.get(cv2.CAP_PROP_FPS),
               width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    cap.release()
    return got


def stage_inputs(scenes, d):
    """Upstream TextImagePairDataset layout: target_crop_info_<ar>.json + <ar>/ images."""
    os.makedirs(f"{d}/26-15", exist_ok=True)
    meta = []
    for r in scenes:
        png = f"{d}/26-15/{r['id']}.png"
        cv2.imwrite(png, cv2.imread(os.path.join(ROOT, r["image"])))
        # target_crop/type/origin_* are metadata the dataset passes through; inference does not use them
        meta.append(dict(file_name=f"{r['id']}.png", caption=r["text"],
                         target_crop=dict(target_bbox=[0, 0, 832, 480], target_ratio="26-15"),
                         type=r["category"], origin_width=832, origin_height=480))
    json.dump(meta, open(f"{d}/target_crop_info_26-15.json", "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("system", choices=sorted(SYSTEMS))
    ap.add_argument("--gpu", type=int, required=True, choices=(2, 3))
    ap.add_argument("--scenes", default="", help="comma-separated ids; default all")
    ap.add_argument("--tag", default="", help="suffix of the output folder, e.g. _smoke")
    a = ap.parse_args()
    st = os.statvfs("/")
    if st.f_bavail * st.f_frsize < DISK_MIN:
        raise SystemExit(f"less than {DISK_MIN / 1e9:.0f} GB free on /; AIA's 100 GiB guard")
    spec = SYSTEMS[a.system]
    man = json.load(open(MAN))
    scenes = [r for r in man["scenes"] if not a.scenes or r["id"] in a.scenes.split(",")]
    prefixes = [r["text"][:100] for r in scenes]
    if len(set(prefixes)) != len(prefixes):
        raise SystemExit("two prompts share their first 100 characters; upstream names outputs by them")
    out = os.path.join(OUT, a.system, spec["horizon"] + a.tag)
    if os.path.exists(out):
        raise SystemExit(f"{out} exists; renders are never overwritten")
    work = os.path.join(OUT, "_work", a.system + a.tag)
    if os.path.exists(work):
        shutil.rmtree(work)
    stage_inputs(scenes, f"{work}/inputs")
    os.makedirs(f"{work}/raw")
    before = gpu_snapshot(a.gpu)
    extra = {}
    if "prepare" in spec:
        extra["cfg"] = ws(spec["prepare"](work, spec))
    envs = [x for k, v in {"HF_HUB_OFFLINE": "1", **{k: ws(v) for k, v in spec.get("env", {}).items()}}.items()
            for x in ("-e", f"{k}={v}")]
    cmd = ["docker", "run", "--rm", "--gpus", f'"device={a.gpu}"', "--shm-size=16g",
           "-v", f"{HOME}:/workspace", "-w", ws(spec.get("workdir", spec["repo"])), *envs, spec["image"],
           *spec["cmd"](ws(f"{work}/inputs"), ws(f"{work}/raw"), spec["seed"], **extra)]
    t0 = time.time()
    proc = subprocess.run(" ".join(c if c.startswith('"') else f"'{c}'" for c in cmd), shell=True,
                          capture_output=True, text=True)
    wall = time.time() - t0
    open(f"{work}/log.txt", "w").write(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    if proc.returncode != 0:
        raise SystemExit(f"render failed ({proc.returncode}); see {work}/log.txt")
    os.makedirs(out)
    image_id = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", spec["image"]],
                              capture_output=True, text=True).stdout.strip()
    common = dict(system=a.system, name=spec["name"], identity=spec["identity"], deviations=spec["deviations"],
                  repo=spec["repo"], commit=git(spec["repo"], "rev-parse", "HEAD"),
                  local_diff_files=git(spec["repo"], "diff", "--name-only").splitlines(),
                  config_sha256=sha256(os.path.join(spec["repo"], spec["config"])),
                  config_used=extra.get("cfg"), config_used_sha256=(sha256(spec["prepare"](work, spec))
                                                                    if "prepare" in spec else None),
                  driver_sha256=(sha256(f"{HOME}/region-forcing/scripts/eval/run_ltx_i2v_baseline.py")
                                 if a.system == "ltx_video" else None),
                  checkpoint=spec["ckpt"], checkpoint_sha256=(sha256(spec["ckpt"]) if os.path.isfile(spec["ckpt"])
                                                              else tree_sha256(spec["ckpt"])),
                  container=spec["image"], container_id=image_id, command=cmd, seed=spec["seed"],
                  seed_rule="one global seed, scenes in manifest order", gpu_before=before,
                  gpu_after=gpu_snapshot(a.gpu), wall_s_all=wall, concurrent=bool(before["processes"]),
                  manifest=os.path.relpath(MAN, ROOT), manifest_sha256=sha256(MAN),
                  role="exposure-logged visual material, not confirmation data",
                  created=datetime.datetime.utcnow().isoformat() + "Z")
    rows = {}
    for r in scenes:
        raw = f"{work}/raw/{r['text'][:100]}.mp4"
        if not os.path.exists(raw):
            raise SystemExit(f"{r['id']}: no output {raw}")
        dst = f"{out}/{r['id']}.mp4"
        shutil.move(raw, dst)
        side = dict(scene=r["id"], source=r["source"], origin_id=r["origin_id"], licence=r["licence"],
                    credit=r["credit"], image_sha256=r["image_sha256"], prompt=r["text"],
                    prompt_sha256=hashlib.sha256(r["text"].encode()).hexdigest(),
                    output_sha256=sha256(dst), output=probe(dst), system=a.system)
        json.dump(side, open(f"{out}/{r['id']}.json", "w"), indent=1)
        rows[r["id"]] = dict(sha256=side["output_sha256"], **side["output"])
    json.dump(dict(common, videos=rows), open(f"{out}/RUN.json", "w"), indent=1)
    shutil.copy(f"{work}/log.txt", f"{out}/log.txt")
    shutil.rmtree(work)
    print(json.dumps(dict(out=out, n=len(rows), wall_s=round(wall), concurrent=common["concurrent"]), indent=1))


if __name__ == "__main__":
    sys.exit(main())

#!/bin/bash
# Isolated environment for the VLM judge.
#
# The metric pipeline lives in `snfeval`, pinned to torch 2.0.1 because RAFT and
# the VBench code depend on it. transformers 5.x cannot see that torch, so the
# judge gets its own environment rather than upgrading a working measurement
# stack -- a benchmark whose numbers move because a judge needed a newer torch
# would not be worth publishing.
set -u
cd /home/minar/snf-bench
ENV=/home/minar/miniconda3/envs/vlmjudge
export HF_HOME=/home/minar/snf-bench/.hf_cache

if [ ! -x "$ENV/bin/python" ]; then
  echo "[$(date +%H:%M:%S)] creating env"
  /home/minar/miniconda3/bin/conda create -y -p "$ENV" python=3.11 || exit 1
  "$ENV/bin/pip" install -q --index-url https://download.pytorch.org/whl/cu121 \
      torch torchvision || exit 1
  "$ENV/bin/pip" install -q "transformers>=4.57" accelerate pillow opencv-python-headless || exit 1
fi
echo "[$(date +%H:%M:%S)] torch: $("$ENV/bin/python" -c 'import torch;print(torch.__version__, torch.cuda.is_available())')"
CUDA_VISIBLE_DEVICES=0,1 "$ENV/bin/python" scripts/vlm_judge.py \
    --model Qwen/Qwen3-VL-8B-Instruct --limit 24 \
    --out /home/minar/snf-bench/manifest/vlm_judge.json
echo "[$(date +%H:%M:%S)] done rc=$?"

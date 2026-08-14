"""Open-weight VLM judge for the SNF-Bench axes.

Purpose and scope. This is a *complement* to the mechanistic validation, not a
replacement and not a new metric. It answers one question: does an independent
judge, given no access to our factors, order the same clip pairs the same way
our factors do? Agreement is evidence the factors track something a competent
observer also perceives; disagreement localises where they do not.

Design follows current practice in VLM-judged video evaluation, and three
choices matter:

  1. **Axis-specific forced choice, never "which is better".** The benchmark
     exists because overall quality conflates background drift with motion
     decay. Asking a judge for preference would reintroduce exactly that
     confound. The judge answers the same two questions the human raters do.
  2. **Identical pair list to the human study.** The VLM and the humans see the
     same trials, so the two agreement numbers are directly comparable and the
     VLM can be checked against the humans on the subset they share.
  3. **Presentation-order randomisation with a paired re-query.** Each pair is
     asked twice with the clips swapped. A judge that answers by position
     rather than by content disagrees with itself, and that self-consistency
     rate is reported alongside the agreement rate -- an inconsistent judge's
     agreement is not interpretable.

Model: Qwen3-VL (Apache-2.0, 2B-235B). The 8B instruct variant is the default
here because it is the smallest that reports competitive video understanding,
which keeps the check reproducible on one GPU.

    ~/miniconda3/envs/snfeval/bin/python scripts/vlm_judge.py --dry-run
    ~/miniconda3/envs/snfeval/bin/python scripts/vlm_judge.py --model Qwen/Qwen3-VL-8B-Instruct
"""

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN, STUDY = f"{ROOT}/manifest", f"{ROOT}/human_study"

# The judge sees exactly what a human rater sees. Wording is deliberately the
# same as human_study/code.gs so the two agreement numbers measure the same
# construct.
QUESTIONS = {
    "drift": (
        "You are shown two short clips of the same scene, recorded by a camera "
        "that never moves.\n"
        "Question: in which clip does the BACKGROUND move more? The background "
        "is everything that should stay perfectly still: buildings, banks, "
        "rocks, the ground, the horizon. Ignore the water, fire, rain or smoke. "
        "Ignore sharpness, colour and overall quality.\n"
        "Answer with exactly one word: FIRST, SECOND, or SAME."),
    "decay": (
        "You are shown two short clips of the same scene, recorded by a camera "
        "that never moves.\n"
        "Question: in which clip does the MOVING CONTENT slow down or stop more "
        "by the end? The moving content is the water, fire, rain or smoke. "
        "Ignore whether the background is stable. Ignore sharpness, colour and "
        "overall quality.\n"
        "Answer with exactly one word: FIRST, SECOND, or SAME."),
}

SAMPLE_FRAMES = 8          # uniformly spaced; enough for a drift/decay judgement


def video_for(key, prompt_id, dur="60s"):
    for p in sorted(glob.glob(f"{ROOT}/videos/t2v/{key}/{dur}/*.mp4")):
        if prompt_id[:80] in os.path.basename(p):
            return p
    return None


def load_frames(path, n=SAMPLE_FRAMES, max_h=336):
    import cv2
    from PIL import Image
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    idxs = [int(round(i * (total - 1) / max(1, n - 1))) for i in range(n)]
    out = []
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, f = cap.read()
        if not ok:
            continue
        h, w = f.shape[:2]
        f = cv2.resize(f, (int(w * max_h / h), max_h), interpolation=cv2.INTER_AREA)
        out.append(Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)))
    cap.release()
    return out


def parse_verdict(text):
    t = (text or "").strip().upper()
    m = re.search(r"\b(FIRST|SECOND|SAME)\b", t)
    return m.group(1).lower() if m else None


class QwenJudge:
    def __init__(self, model_id):
        from transformers import AutoModelForImageTextToText, AutoProcessor
        import torch
        self.proc = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, device_map="auto")
        self.model.eval()

    def ask(self, frames_a, frames_b, question):
        import torch
        content = [{"type": "text", "text": question},
                   {"type": "text", "text": "\nFIRST clip:"}]
        content += [{"type": "image"} for _ in frames_a]
        content += [{"type": "text", "text": "\nSECOND clip:"}]
        content += [{"type": "image"} for _ in frames_b]
        msgs = [{"role": "user", "content": content}]
        prompt = self.proc.apply_chat_template(msgs, add_generation_prompt=True,
                                               tokenize=False)
        inputs = self.proc(text=[prompt], images=frames_a + frames_b,
                           return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=8, do_sample=False)
        gen = out[0][inputs["input_ids"].shape[1]:]
        return self.proc.decode(gen, skip_special_tokens=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-VL-8B-Instruct")
    ap.add_argument("--pairs", default=f"{STUDY}/pairs.json")
    ap.add_argument("--out", default=f"{MAN}/vlm_judge.json")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve videos and print the plan without loading the model")
    args = ap.parse_args()

    study = json.load(open(args.pairs))
    trials = []
    for ax in study["axes"]:
        for p in ax["pairs"]:
            va, vb = video_for(p["a"], p["prompt"]), video_for(p["b"], p["prompt"])
            if va and vb:
                trials.append(dict(axis=ax["axis"], metric=ax["metric"], **p,
                                   video_a=va, video_b=vb))
    if args.limit:
        trials = trials[:args.limit]

    print(f"{len(trials)} trials resolved "
          f"({sum(1 for t in trials if t['axis']=='drift')} drift, "
          f"{sum(1 for t in trials if t['axis']=='decay')} decay)")
    if args.dry_run:
        for t in trials[:3]:
            print(f"  [{t['axis']}] {t['a_name']} vs {t['b_name']}  "
                  f"gap={t['gap']}  metric_says={t['metric_says']}")
        print("dry run: model not loaded")
        return 0

    judge = QwenJudge(args.model)
    records = []
    for i, t in enumerate(trials):
        fa, fb = load_frames(t["video_a"]), load_frames(t["video_b"])
        q = QUESTIONS[t["axis"]]
        # Ask both orders; a position-answering judge disagrees with itself.
        v1 = parse_verdict(judge.ask(fa, fb, q))
        v2 = parse_verdict(judge.ask(fb, fa, q))
        # map to system keys
        pick1 = {"first": t["a"], "second": t["b"], "same": "same"}.get(v1)
        pick2 = {"first": t["b"], "second": t["a"], "same": "same"}.get(v2)
        records.append(dict(axis=t["axis"], prompt=t["prompt"], a=t["a"], b=t["b"],
                            gap=t["gap"], metric_says=t["metric_says"],
                            vlm_order1=pick1, vlm_order2=pick2,
                            consistent=(pick1 == pick2)))
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(trials)}", flush=True)
            with open(args.out, "w") as f:
                json.dump({"model": args.model, "records": records}, f, indent=2)

    with open(args.out, "w") as f:
        json.dump({"model": args.model, "records": records}, f, indent=2)

    # Agreement is computed only on self-consistent trials: a judge that
    # contradicts itself on a pair has expressed no opinion about it.
    by = defaultdict(lambda: [0, 0, 0])
    for r in records:
        s = by[r["axis"]]
        s[2] += 1
        if not r["consistent"]:
            continue
        s[1] += 1
        if r["vlm_order1"] == r["metric_says"]:
            s[0] += 1
    print("\naxis   agree/consistent  consistency")
    for ax, (agree, cons, tot) in by.items():
        print(f"  {ax:6s} {agree}/{cons}  ({agree/max(1,cons)*100:.0f}%)   "
              f"{cons}/{tot} ({cons/max(1,tot)*100:.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

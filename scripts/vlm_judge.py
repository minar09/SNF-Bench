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
        "Ignore sharpness, colour and overall quality."),
    "decay": (
        "You are shown two short clips of the same scene, recorded by a camera "
        "that never moves.\n"
        "Question: in which clip does the MOVING CONTENT slow down or stop more "
        "by the end? The moving content is the water, fire, rain or smoke. "
        "Ignore whether the background is stable. Ignore sharpness, colour and "
        "overall quality."),
}

SAMPLE_FRAMES = 8          # uniformly spaced; enough for a drift/decay judgement

# Forcing an immediate one-word verdict makes this judge answer by slot: an
# earlier version chose SECOND on 43 of 48 queries and was self-consistent on
# none, while still correctly answering SAME when shown one clip against
# itself. Describing each clip before committing separates what the judge
# observes from which slot it prefers, and 'SAME' is stated as a legitimate
# answer so an indistinguishable pair need not be broken arbitrarily.
RUBRIC = (
    "Describe what you actually observe in ONE short sentence per clip, then "
    "give your verdict. If the two clips are indistinguishable on this "
    "question, SAME is the correct answer -- do not guess. Use exactly this "
    "format:\n"
    "FIRST clip: <observation>\n"
    "SECOND clip: <observation>\n"
    "ANSWER: FIRST or SECOND or SAME")


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
    """Take the LAST verdict token, not the first.

    The judge is asked to describe each clip before committing, and those
    descriptions routinely contain the words 'first' and 'second' as ordinals.
    Reading the first match would score the preamble instead of the answer.
    """
    t = (text or "").strip().upper()
    m = re.search(r"ANSWER\s*:?\s*\**\s*(FIRST|SECOND|SAME)", t)
    if m:
        return m.group(1).lower()
    ms = re.findall(r"\b(FIRST|SECOND|SAME)\b", t)
    return ms[-1].lower() if ms else None


class QwenJudge:
    def __init__(self, model_id):
        from transformers import AutoModelForImageTextToText, AutoProcessor
        import torch
        self.proc = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, device_map="auto")
        self.model.eval()

    def ask(self, frames_a, frames_b, question):
        """Each clip is passed as a *video*, not as loose frames.

        Interleaving both clips as a flat image sequence separated only by text
        gives the model nothing that binds a frame to "FIRST" or "SECOND", and
        it answers by position instead of by content: an early version of this
        harness returned SECOND on 36 of 48 queries and was self-consistent on
        7 of 24 pairs, i.e. below chance for a three-way choice. Two video
        blocks give each clip its own vision span, which is what the model was
        trained on.
        """
        import torch
        content = [{"type": "text", "text": "\nFIRST clip:"},
                   {"type": "video"},
                   {"type": "text", "text": "\nSECOND clip:"},
                   {"type": "video"},
                   {"type": "text", "text": question + "\n" + RUBRIC}]
        msgs = [{"role": "user", "content": content}]
        prompt = self.proc.apply_chat_template(msgs, add_generation_prompt=True,
                                               tokenize=False)
        inputs = self.proc(text=[prompt], videos=[frames_a, frames_b],
                           return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=160,
                                      do_sample=False)
        gen = out[0][inputs["input_ids"].shape[1]:]
        return self.proc.decode(gen, skip_special_tokens=True)


def run_controls(judge, trials, n=6):
    """Two sanity controls the judge must pass before its numbers mean anything.

    A. The same clip on both sides. The only correct answer is SAME; anything
       else is the judge answering by slot rather than by content.
    B. A frozen first frame against the real clip. A still image cannot have
       background motion, so the real clip must be chosen -- and the choice has
       to follow the clip when the two are swapped, not stay in one slot.

    These are cheap and they are the difference between an agreement rate that
    means something and one that merely looks healthy.
    """
    q = QUESTIONS["drift"]
    ident = []
    for t in trials[:n]:
        f = load_frames(t["video_a"])
        ident.append(parse_verdict(judge.ask(f, f, q)))
    n_same = sum(1 for v in ident if v == "same")

    swap_ok = 0
    for t in trials[:n]:
        f = load_frames(t["video_a"])
        still = [f[0]] * len(f)
        a = parse_verdict(judge.ask(still, f, q))
        b = parse_verdict(judge.ask(f, still, q))
        if a == "second" and b == "first":
            swap_ok += 1

    print(f"\ncontrol A (same clip twice -> SAME): {n_same}/{len(ident)}")
    print(f"control B (still vs real, verdict follows the swap): {swap_ok}/{n}")
    return {"identity_same": n_same, "identity_n": len(ident),
            "swap_correct": swap_ok, "swap_n": n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-VL-8B-Instruct")
    ap.add_argument("--pairs", default=f"{STUDY}/pairs.json")
    ap.add_argument("--out", default=f"{MAN}/vlm_judge.json")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve videos and print the plan without loading the model")
    ap.add_argument("--controls", action="store_true",
                    help="run the identity and swap controls as well")
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
    controls = run_controls(judge, trials) if args.controls else None
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
                            # positional answers are kept so a judge answering
                            # by slot rather than by content stays visible
                            pos1=v1, pos2=v2,
                            consistent=(pick1 == pick2)))
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(trials)}", flush=True)
            with open(args.out, "w") as f:
                json.dump({"model": args.model, "controls": controls,
                           "records": records}, f, indent=2)

    with open(args.out, "w") as f:
        json.dump({"model": args.model, "controls": controls,
                           "records": records}, f, indent=2)

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

    # Positional summary. If one slot dominates, the judge is reading layout
    # rather than video and no agreement number computed from it is meaningful,
    # however healthy that number happens to look.
    slots = defaultdict(int)
    for r in records:
        for v in (r["pos1"], r["pos2"]):
            slots[v or "unparsed"] += 1
    n_q = 2 * len(records)
    top, top_n = max(slots.items(), key=lambda kv: kv[1])
    print(f"\nposition check over {n_q} queries: "
          + ", ".join(f"{k}={v}" for k, v in sorted(slots.items())))
    if top != "same" and top_n > 0.60 * n_q:
        print(f"  WARNING: '{top.upper()}' chosen in {top_n}/{n_q} "
              f"({top_n/n_q*100:.0f}%) -- judge is answering by position; "
              f"agreement above is not interpretable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

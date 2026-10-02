"""The two SNF-Bench prompt sets, and where everything belonging to each lives.

SNF-Bench has two independent version axes that are easy to conflate:

* **Prompt set** -- what was generated. ``v1`` is the WACV-submitted set
  (23 T2V prompts at 60 s, disjoint prompts per horizon, 30 I2V images).
  ``v2`` is the rebuilt set (96 T2V scenes and 48 I2V pairs over nine transport
  regimes, the *same* scenes at every horizon). This module.
* **Metric spec** -- how a video is scored. ``1.0`` (median-translation
  compensation) and ``1.1`` (RANSAC similarity). See ``METRIC_SPEC_v1.1.md``.
  Either spec can score either prompt set; a record carries both labels.

Until this module existed nothing recorded the prompt set at all. Every
analysis script globs ``raw/*/*/*/snf_task_metrics.json`` keyed only by
``<track>/<key>/<dur>``, and ``rerun_metrics.assemble`` merges into whatever
record is already at that path -- so v2 scores written under a model key that
v1 also used would have blended into the v1 record and every v1 table, with no
error. The two sets therefore get **disjoint roots** for everything derived
from generation, and v1 keeps exactly the paths it always had, so no v1 script,
table or record changes meaning.

    raw/            raw_v2/             per-entry metric records
    videos/         videos_v2/          symlinks to generated videos
    .metric_staging .metric_staging_v2  per-video staging
    .flow_fields    .flow_fields_v2     persisted flow samples
"""

import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SETS = {
    "v1": {
        "description": "WACV 2027 submission set: disjoint prompts per horizon",
        "raw": "raw",
        "videos": "videos",
        "staging": ".metric_staging",
        "flow": ".flow_fields",
        # frozen inputs, relative to ROOT
        "t2v_prompt_files": {
            "5s": "prompts/t2v/prompts5s.txt",
            "60s": "prompts/t2v/prompts60s.txt",
            "120s": "prompts/t2v/prompts120s.txt",
            "240s": "prompts/t2v/prompts240s.txt",
            # the 240 s tier was also run in four batches, and an extension set
            # exists beside the per-horizon files; all are v1 model-visible text
            "240s_01": "prompts/t2v/prompts240s01.txt",
            "240s_02": "prompts/t2v/prompts240s02.txt",
            "240s_03": "prompts/t2v/prompts240s03.txt",
            "240s_04": "prompts/t2v/prompts240s04.txt",
            "ext": "prompts/t2v/prompts_ext.txt",
        },
        "i2v_dirs": {d: f"prompts/i2v/{d}" for d in ("5s", "60s", "120s", "240s")},
        "i2v_meta_name": "target_crop_info_16-9.json",
    },
    "v2": {
        "description": "rebuilt set: 96 T2V scenes / 48 I2V pairs, matched across horizons",
        "raw": "raw_v2",
        "videos": "videos_v2",
        "staging": ".metric_staging_v2",
        "flow": ".flow_fields_v2",
        "t2v_prompt_files": {d: f"prompts/v2/t2v/prompts{d}.txt"
                             for d in ("5s", "60s", "120s", "240s")},
        "i2v_dirs": {d: f"prompts/v2/i2v/snf_v2_{d}"
                     for d in ("5s", "60s", "120s", "240s")},
        "i2v_meta_name": "target_crop_info_v2.json",
        # authoritative sources the consumer files are exported from
        "t2v_manifest": "manifest/prompts_v2.json",
        "i2v_manifest": "manifest/i2v_pairs_v2.json",
    },
}

DEFAULT = "v1"          # every pre-existing script keeps v1 behaviour unchanged

_MARKER = re.compile(r"\s*\[\d+(?:\.\d+)?s\]\s*$")


def get(name):
    if name not in SETS:
        raise SystemExit(f"unknown prompt set {name!r}; known: {sorted(SETS)}")
    return SETS[name]


def root(name, kind):
    """Absolute path of a derived-data root ('raw', 'videos', 'staging', 'flow')."""
    return os.path.join(ROOT, get(name)[kind])


def _norm(text):
    """Comparable form of a prompt or a video filename stem."""
    text = _MARKER.sub("", text)
    text = text.replace("_", " ")
    return re.sub(r"\s+", " ", text).strip().lower()


def prompt_texts(name):
    """Every model-visible prompt in a set (duration markers removed)."""
    s, out = get(name), []
    for rel in s["t2v_prompt_files"].values():
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            out += [l for l in open(p).read().splitlines() if l.strip()]
    for rel in s["i2v_dirs"].values():
        p = os.path.join(ROOT, rel, s["i2v_meta_name"])
        if os.path.exists(p):
            out += [r["caption"] for r in json.load(open(p))]
    if name == "v2":                      # also the authoritative manifests
        for key, field, sub in (("t2v_manifest", "text", "scenes"),
                                ("i2v_manifest", "text", "pairs")):
            p = os.path.join(ROOT, s[key])
            if os.path.exists(p):
                out += [r[field] for r in json.load(open(p))[sub]]
    return sorted({_MARKER.sub("", t).strip() for t in out})


_PREFIX = 48            # long enough to be distinctive, short enough to survive
                        # every truncation the generators apply to filenames


def classify(video_name, _cache={}):
    """'v1', 'v2', 'both' or None for a generated video's filename.

    Generators name outputs after the (truncated) prompt, sometimes with spaces
    replaced by underscores and a seed/timestamp suffix, so this matches on a
    normalised prefix. v1 and v2 prompts share no opening words, so a 48-char
    prefix cannot be ambiguous in practice; 'both' is returned rather than
    guessed if it ever is.
    """
    if not _cache:
        for n in SETS:
            _cache[n] = {_norm(t)[:_PREFIX] for t in prompt_texts(n)}
    stem = _norm(os.path.splitext(os.path.basename(video_name))[0])[:_PREFIX]
    hits = [n for n in SETS if stem in _cache[n]]
    if len(hits) > 1:
        return "both"
    return hits[0] if hits else None

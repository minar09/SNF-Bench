"""SNF-Bench scene-category assignment and balance audit.

SNF-Bench reports are macro-averaged by scene category so that a track is not
dominated by whichever flow medium happens to be over-sampled. This module is
the single source of truth for that category axis, and it is deliberately
auditable: every prompt's assignment is written out with the rule that fired
and the text span that triggered it, so a reviewer can check all 100 of them by
hand rather than trusting a regex.

Category axis = **flow medium**, i.e. what the dynamic region physically is.
That is the right axis for this benchmark because the metrics (NBF, MCFF, FP,
DAR) all measure optical flow inside the dynamic mask, and different
media have structurally different flow signatures: channel water is coherent
and directional, precipitation is sparse and high-frequency, smoke and lava are
slow and non-rigid, windborne particles are chaotic and low-density. Grouping
by biome or by location instead would mix these signatures inside one cell.

Provenance of the label differs by track and is recorded per row:
  source='meta'     I2V. The eval set ships a curated `type` field per prompt
                    (53 distinct fine types over 65 prompts). We map fine type
                    -> coarse category; the fine type is preserved in the CSV.
  source='keyword'  T2V. No type field exists, so the category is derived from
                    the scene descriptor (the clause before the fixed-camera
                    boilerplate) via the ordered rules below.
  source='override' Either track, hand-assigned. Used only where the automatic
                    rule is defensibly wrong; each carries a written reason.

Outputs
  manifest/prompt_categories.csv   one row per (track, duration, prompt_id)
  manifest/category_balance.json   machine-readable counts + thin-cell flags
  tables/category_balance.md       the audit table for the paper appendix

Also exports load_categories() and macro_average() for build_tables.py.
"""

import csv
import glob
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN, TAB = f"{ROOT}/manifest", f"{ROOT}/tables"
DURATIONS = ["5s", "60s", "120s", "240s"]

# Minimum prompts in a (track, duration, category) cell for its macro-average
# contribution to be reported rather than flagged as unstable.
MIN_CELL = 3

# --------------------------------------------------------------------------
# Coarse taxonomy
# --------------------------------------------------------------------------
CATEGORIES = {
    "river_stream":  "channel water: rivers, streams, creeks, canals, waterfalls, rapids, floods",
    "ocean_waves":   "open water with wave action: surf, tides, coastal swell, seascapes",
    "precipitation": "falling water or ice: rain, snowfall, and the surfaces they wet",
    "fire_smoke":    "combustion plumes: wildfire, campfire, hearth, urban fire, grill smoke",
    "lava_volcanic": "volcanic flow and ejecta: lava channels, ash columns, eruption smoke",
    "windborne":     "air-carried particulates and wind-driven vegetation: dust, sand, blossom, leaves, thrashing trees, drifting cloud",
}
CAT_ORDER = list(CATEGORIES)

# Ordered rules. FIRST MATCH WINS, so ordering encodes the disambiguation
# policy for prompts that mention more than one medium:
#   lava before ocean      -> "volcanic_lava_ocean_entry" is lava, not surf
#   fire before windborne  -> "wildfire_hillside_smoke" is smoke, not wind
#   channel before ocean   -> "fjord approach ... forest creek" is the creek
#   channel before wind    -> "urban storm drain canal" is the canal, not a storm
#   wind before precip     -> "storm_wind_rain_palms" is thrashing palms
RULES = [
    ("lava_volcanic", r"volcan|lava|magma|ash column|eruption|pyroclast"),
    ("fire_smoke",    r"wildfire|campfire|fireplace|fire pit|firefight|bonfire|hearth"
                      r"|\bfire\b|\bsmoke|\bgrill|\bembers?\b|\bflames?\b"),
    ("river_stream",  r"\briver|\bstream|\bcreek|\bcanal|waterfall|cascad|\brapids?\b"
                      r"|\bbrook\b|\bflood|\btorrent|waterway|storm drain|\bweir\b"
                      # NB: 'runoff' is deliberately absent -- roof/street runoff is
                      # rain leaving a surface, not channel flow (rainfall_roof_runoff).
                      r"|\bfountain\b|\bpond\b|\bchannel\b|\bcurrent\b"),
    ("ocean_waves",   r"\bocean|\bsea\b|seascape|\bsurf\b|\bwaves?\b|\bbeach|coastal|shoreline"
                      r"|\btide|\bfjord|\bswell\b|\bbreakers?\b|\bcliffs? in\b"),
    ("windborne",     r"wind[_ ]particle|sandstorm|sand storm|dust storm|dust[_ ]storm"
                      r"|windstorm|\bwind\b|cherry blossom|cherry[_ ]blossom|\bsakura\b"
                      r"|autumn[_ ]leaves|\bcloud[_ ]drift|drifting clouds?|\bgust"),
    ("precipitation", r"rainfall|\brain\b|\brains\b|\brainy\b|rainstorm|rain[_ ]streak|raindrop"
                      r"|\bsnow\b|snowfall|\bsnowy\b|\bsleet\b|\bhail\b|\bdownpour\b|\bdrizzle\b"
                      r"|\bprecipitation\b|\bpuddle"),
]

# --------------------------------------------------------------------------
# Hand overrides. Each is a case where first-match-wins is defensibly wrong.
# Keyed by (track, duration, prompt_id-prefix). Kept small and each justified;
# these are the rows a reviewer should scrutinise first.
# --------------------------------------------------------------------------
OVERRIDES = {
    ("t2v", "60s", "A_completely_fixed,_tripod-mounted_camera_captures_a_flooded_urban_street"): (
        "precipitation",
        "'flooded' fires the channel-water rule, but the dynamic content is falling "
        "rain plus a slowly rising waterline -- there is no channel flow in frame."),
}


# Negation boilerplate that would otherwise leak a medium token into a match.
# "with no waves, wobble, flicker, jumps, resets" appears in most prompts and is
# the only phrase in the corpus that names a medium it does not contain.
NEGATIONS = re.compile(r"\bno waves?\b|\bwithout waves?\b")


def _norm(s):
    """Lowercase, and treat '_' as a space so \\b works on I2V type slugs."""
    return re.sub(r"\s+", " ", s.lower().replace("_", " "))


def classify(text):
    """-> (category, rule_pattern, matched_span). Falls back to ('unassigned', ...)."""
    t = NEGATIONS.sub(" ", _norm(text))
    for cat, pat in RULES:
        m = re.search(pat, t)
        if m:
            return cat, pat, m.group(0)
    return "unassigned", "", ""


def scene_descriptor(prompt):
    """Strip the fixed-camera boilerplate so the classifier reads the scene.

    Every T2V prompt is '<scene>, recorded by a completely fixed ... camera. <rules>'
    or '<camera clause> captures <scene>. <rules>'. The trailing rule text names
    static objects ('vegetation remains motionless') and would otherwise leak
    tokens from the wrong medium into the match.
    """
    p = prompt.strip()
    m = re.search(r",?\s*(recorded by|captured by|filmed by)\b", p, re.I)
    if m:
        head = p[:m.start()]
        if len(head) >= 20:
            return head
    m = re.search(r"\bcaptures\b|\brecords\b", p, re.I)
    if m:
        return p[m.end():].split(".")[0]
    return p.split(".")[0]


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------
def t2v_prompts():
    """-> {slug: full prompt text}. slug matches build_tables.prompt_id()."""
    out = {}
    for f in sorted(glob.glob(f"{ROOT}/prompts/t2v/*.txt")):
        for line in open(f):
            line = line.strip()
            if line:
                out[line[:100].replace(" ", "_")] = line
    return out


def i2v_prompts():
    """-> {(duration, caption-prefix): (type, caption, file_name)}."""
    out = {}
    for d in DURATIONS:
        p = f"{ROOT}/prompts/i2v/{d}/target_crop_info_16-9.json"
        if not os.path.exists(p):
            continue
        for x in json.load(open(p)):
            out[(d, x["caption"][:100])] = (x["type"], x["caption"], x["file_name"])
    return out


def evaluated_prompt_ids():
    """-> {(track, duration): {prompt_id}} actually present in the score table."""
    out = defaultdict(set)
    p = f"{MAN}/per_video_scores.csv"
    for r in csv.DictReader(open(p)):
        out[(r["track"], r["duration"])].add(r["prompt_id"])
    return out


# --------------------------------------------------------------------------
# Assignment
# --------------------------------------------------------------------------
def assign():
    rows, unmatched = [], []
    evald = evaluated_prompt_ids()
    t2v, i2v = t2v_prompts(), i2v_prompts()

    for (track, dur), pids in sorted(evald.items(),
                                     key=lambda kv: (kv[0][0], DURATIONS.index(kv[0][1]))):
        for pid in sorted(pids):
            if track == "t2v":
                text = t2v.get(pid)
                if text is None:
                    unmatched.append(dict(track=track, duration=dur, prompt_id=pid))
                    continue
                fine, basis, source = "", scene_descriptor(text), "keyword"
                # Some T2V scenes name their medium only in the body ("A dangerous
                # hillside storm ... trees thrash in fierce wind"). Widen to the
                # full prompt only when the descriptor alone decides nothing.
                if classify(basis)[0] == "unassigned":
                    basis, source = text, "keyword-body"
            else:
                rec = i2v.get((dur, pid))
                if rec is None:
                    unmatched.append(dict(track=track, duration=dur, prompt_id=pid))
                    continue
                fine, basis, source = rec[0], rec[0], "meta"

            cat, rule, span = classify(basis)
            for (ot, od, opfx), (ocat, oreason) in OVERRIDES.items():
                if ot == track and od == dur and pid.startswith(opfx):
                    cat, rule, span, source = ocat, "OVERRIDE", oreason, "override"
                    break

            rows.append(dict(track=track, duration=dur, prompt_id=pid, fine_type=fine,
                             category=cat, source=source, rule=rule, evidence=span,
                             basis=basis[:200]))
    return rows, unmatched


# --------------------------------------------------------------------------
# Balance report
# --------------------------------------------------------------------------
def balance(rows):
    counts = defaultdict(Counter)
    for r in rows:
        counts[(r["track"], r["duration"])][r["category"]] += 1

    report = {"min_cell": MIN_CELL, "categories": CATEGORIES, "cells": {}, "thin": [],
              "absent": [], "unassigned": []}
    for (track, dur), c in sorted(counts.items(), key=lambda kv: (kv[0][0], DURATIONS.index(kv[0][1]))):
        n = sum(c.values())
        cell = {cat: c.get(cat, 0) for cat in CAT_ORDER}
        cell["_n"] = n
        cell["_n_categories"] = sum(1 for cat in CAT_ORDER if c.get(cat, 0))
        # Largest share held by any one category -- the concentration a reviewer asks about.
        cell["_max_share"] = round(max(c.values()) / n, 3) if n else 0.0
        report["cells"][f"{track}/{dur}"] = cell
        for cat in CAT_ORDER:
            k = c.get(cat, 0)
            if k == 0:
                report["absent"].append(f"{track}/{dur}/{cat}")
            elif k < MIN_CELL:
                report["thin"].append(f"{track}/{dur}/{cat} (n={k})")
        if c.get("unassigned"):
            report["unassigned"].append(f"{track}/{dur} (n={c['unassigned']})")
    return report


def _md_table(header, body):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in body]
    return out


def write_report(rows, report, unmatched):
    L = ["# Scene-category balance audit", "",
         "SNF-Bench macro-averages by **flow medium** — what the dynamic region physically is —",
         "because every task metric (NBF, MCFF, FP, DAR) measures optical flow inside the",
         "dynamic mask, and media differ structurally in flow signature. Per-prompt assignments,",
         "with the rule that fired and the text that triggered it, are in",
         "`manifest/prompt_categories.csv` (all rows, hand-checkable).", "",
         "## Taxonomy", ""]
    L += _md_table(["category", "definition"], [[c, d] for c, d in CATEGORIES.items()])

    L += ["", "## Prompts per category", "",
          f"`n` = prompts in the eval set. `max share` = fraction held by the single largest",
          f"category. Cells with `0 < n < {MIN_CELL}` are too thin to macro-average stably.", ""]
    hdr = ["track/duration", "n"] + CAT_ORDER + ["cats", "max share"]
    body = []
    for k, c in report["cells"].items():
        body.append([k, c["_n"]] + [c[cat] or "·" for cat in CAT_ORDER]
                    + [c["_n_categories"], f'{c["_max_share"]:.2f}'])
    L += _md_table(hdr, body)

    L += ["", "## Label provenance", ""]
    src = Counter((r["track"], r["source"]) for r in rows)
    L += _md_table(["track", "source", "prompts"],
                   [[t, s, n] for (t, s), n in sorted(src.items())])
    L += ["",
          "- `meta` — the I2V eval set's curated `type` field (53 fine types over 65 prompts),",
          "  mapped to the coarse axis. The fine type is retained in the CSV.",
          "- `keyword` — T2V has no type field; the category is derived from the scene descriptor",
          "  (the clause before the fixed-camera boilerplate) by ordered first-match rules.",
          "- `override` — hand-assigned where first-match-wins is defensibly wrong; each is listed below."]

    if OVERRIDES:
        L += ["", "## Overrides", ""]
        L += _md_table(["track", "duration", "prompt (prefix)", "category", "reason"],
                       [[t, d, p[:48] + "…", cat, why]
                        for (t, d, p), (cat, why) in OVERRIDES.items()])

    L += ["", "## Findings", ""]
    if report["unassigned"]:
        L += [f"- **UNASSIGNED prompts remain**: {', '.join(report['unassigned'])} — "
              "the rule set does not cover the whole eval set and must be extended."]
    else:
        L += ["- Every evaluated prompt received a category; no `unassigned` rows."]
    if unmatched:
        L += [f"- **{len(unmatched)} scored prompt_ids could not be traced to a source prompt** "
              "— see `manifest/category_balance.json`."]
    else:
        L += ["- Every scored `prompt_id` traced back to a source prompt/caption (exact 100-char join)."]
    if report["thin"]:
        L += [f"- Thin cells (n < {MIN_CELL}), macro-average unstable: " + "; ".join(report["thin"])]
    if report["absent"]:
        L += [f"- Categories absent entirely from a cell: {len(report['absent'])} "
              f"of {len(report['cells']) * len(CAT_ORDER)} (track,duration,category) slots — "
              + "; ".join(report["absent"])]
    L += ["",
          "Read the two together: a category absent from a duration means that duration's",
          "macro-average is taken over a *different* medium mix than its neighbours, so",
          "cross-duration comparison of a macro-average is only sound within a fixed category.",
          ""]

    os.makedirs(TAB, exist_ok=True)
    with open(f"{TAB}/category_balance.md", "w") as f:
        f.write("\n".join(L))


# --------------------------------------------------------------------------
# Public helpers for build_tables.py
# --------------------------------------------------------------------------
def load_categories():
    """-> {(track, duration, prompt_id): category}. Run this module first."""
    p = f"{MAN}/prompt_categories.csv"
    if not os.path.exists(p):
        raise FileNotFoundError(f"{p} missing — run scripts/categories.py first")
    return {(r["track"], r["duration"], r["prompt_id"]): r["category"]
            for r in csv.DictReader(open(p))}


def macro_average(per_prompt, track, dur, cats=None, min_cell=MIN_CELL):
    """Category-macro-average of {prompt_id: value}.

    Each category contributes its own prompt-mean once, so an over-sampled
    medium cannot dominate. Categories with fewer than `min_cell` prompts
    *present for this model* are still included but reported, because dropping
    them would silently change the estimand between models.

    -> (macro_mean, {category: (mean, n)}, [thin categories])
    """
    cats = cats or load_categories()
    groups = defaultdict(list)
    for pid, v in per_prompt.items():
        c = cats.get((track, dur, pid))
        if c:
            groups[c].append(v)
    per_cat = {c: (sum(v) / len(v), len(v)) for c, v in groups.items()}
    thin = sorted(c for c, (_, n) in per_cat.items() if n < min_cell)
    if not per_cat:
        return None, {}, thin
    return sum(m for m, _ in per_cat.values()) / len(per_cat), per_cat, thin


def main():
    rows, unmatched = assign()
    os.makedirs(MAN, exist_ok=True)
    with open(f"{MAN}/prompt_categories.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["track", "duration", "prompt_id", "fine_type",
                                          "category", "source", "rule", "evidence", "basis"])
        w.writeheader()
        w.writerows(rows)

    report = balance(rows)
    report["unmatched_prompt_ids"] = unmatched
    with open(f"{MAN}/category_balance.json", "w") as f:
        json.dump(report, f, indent=2)

    write_report(rows, report, unmatched)

    print(f"{len(rows)} prompt-duration assignments -> manifest/prompt_categories.csv")
    tot = Counter(r["category"] for r in rows)
    for c in CAT_ORDER + ["unassigned"]:
        if tot.get(c):
            print(f"   {tot[c]:3d}  {c}")
    if unmatched:
        print(f"!! {len(unmatched)} scored prompt_ids unmatched to a source prompt")
    if report["thin"]:
        print(f"!! thin cells (n<{MIN_CELL}): {len(report['thin'])}")


if __name__ == "__main__":
    main()

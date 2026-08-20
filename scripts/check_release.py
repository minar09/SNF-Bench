"""Fail the build if anything that ships names unpublished internal work.

A reviewer who opens the reproducibility package and finds a checkpoint path,
config filename or model key named after an unpublished method has both
deanonymised the submission and previewed that method in one click. The LaTeX
was already swept; this sweeps the part that actually ships as code and data.

Two kinds of file are treated differently:

  * `SOURCE_OF_TRUTH` files are allowed to name internal entries, because their
    job is to declare what is excluded. `scripts/registry.py` cannot mark an
    entry internal without naming it. They are still reported, so the list of
    places a name legitimately appears stays short and reviewed.
  * Everything else that is tracked must be clean.

    ~/miniconda3/envs/snfeval/bin/python scripts/check_release.py
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Names of unpublished work, and internal deployment vocabulary that identifies
# it. Word-boundaried so ordinary words are not swept up.
PATTERNS = [
    r"steady[-_ ]?forcing", r"\bra[-_]i2v\b", r"\bphase7", r"\bnfpb\b",
    r"\brt500\b", r"\babl_[a-z0-9]+", r"region[-_]forcing",
    r"OUR method", r"OUR prior work", r"\bredmd\b", r"\bgated_v2\b",
]
RX = re.compile("|".join(PATTERNS), re.I)

# Allowed to name internal entries: declaring an exclusion requires naming it.
SOURCE_OF_TRUTH = {"scripts/registry.py", "scripts/check_release.py",
                   "docs/EXCLUSIONS.md"}

# Never ships: internal ablation artifacts.
MUST_NOT_SHIP = ("raw/_internal_ablations/",)

SKIP_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".mp4", ".pt", ".pth", ".npz"}


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if l]


def main():
    hits, shipped_internal, allowed = {}, [], {}
    for rel in tracked():
        if any(rel.startswith(p) for p in MUST_NOT_SHIP):
            shipped_internal.append(rel)
            continue
        if os.path.splitext(rel)[1].lower() in SKIP_EXT:
            continue
        path = os.path.join(ROOT, rel)
        try:
            with open(path, "r", errors="ignore") as fh:
                n = sum(1 for line in fh if RX.search(line))
        except OSError:
            continue
        if not n:
            continue
        (allowed if rel in SOURCE_OF_TRUTH else hits)[rel] = n

    if allowed:
        print("declared source-of-truth files (allowed to name exclusions):")
        for r, n in sorted(allowed.items()):
            print(f"   {n:6d}  {r}")

    ok = True
    if shipped_internal:
        ok = False
        print(f"\nFAIL: {len(shipped_internal)} tracked file(s) under internal-only "
              f"paths would ship, e.g.:")
        for r in shipped_internal[:5]:
            print(f"          {r}")
        print("       git rm -r --cached raw/_internal_ablations/  (keeps them on disk)")
    if hits:
        ok = False
        print(f"\nFAIL: internal names in {len(hits)} tracked file(s):")
        for r, n in sorted(hits.items(), key=lambda kv: -kv[1]):
            print(f"   {n:6d}  {r}")

    print("\nRELEASE CLEAN" if ok else "\nRELEASE NOT CLEAN")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

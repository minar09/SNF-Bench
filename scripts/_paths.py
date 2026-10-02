"""Resolve paths to things outside this repository.

Six tracked scripts used to carry absolute paths into two private repositories
(`/home/minar/region-forcing/snf_eval`, `/home/minar/static-forcing`). That is
two defects at once:

* **Reproducibility.** Nobody outside this machine can run the metric worker,
  the gate, the validation suite or the collector, because the paths do not
  exist for them. A downstream driver in one of those repos hit exactly this and
  had to reconstruct the import environment by hand.
* **Disclosure.** The release scan refuses internal *names* in tracked files;
  it never looked at source-level constants, so the private repository names
  shipped in the released source regardless.

Paths now come from the environment, then from an untracked local file, and
nothing is hardcoded. Missing configuration raises with the variable to set
rather than failing later with an obscure ImportError.

Local configuration lives in `configs/local_paths.json` (git-ignored):

    {"vbench_home": "...", "t2v_source_repo": "...", "i2v_source_repo": "..."}

Keys
----
`vbench_home`
    A VBench checkout supplying `vbench/third_party/RAFT`. SNF-Bench does not
    vendor it: RAFT and VBench are third-party code with their own licences, and
    a public benchmark should depend on the upstream release rather than
    relicense a copy. Env: ``SNF_VBENCH_HOME``.
`i2v_ablation_repo`
    Optional. A further upstream repository the collector cross-checks as a
    superset; absent configuration simply skips that check.
`t2v_source_repo` / `i2v_source_repo`
    Upstream generation repositories the collector reads from. Only
    `scripts/collect.py` needs these, and only when ingesting new runs; every
    analysis script works from `raw/` alone. Env: ``SNF_T2V_SOURCE_REPO``,
    ``SNF_I2V_SOURCE_REPO``.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL = os.path.join(ROOT, "configs", "local_paths.json")
METRIC_CODE = os.path.join(ROOT, "metric_code")

ENV = {
    "vbench_home": "SNF_VBENCH_HOME",
    "t2v_source_repo": "SNF_T2V_SOURCE_REPO",
    "i2v_source_repo": "SNF_I2V_SOURCE_REPO",
    "i2v_ablation_repo": "SNF_I2V_ABLATION_REPO",
    "vbench_cache": "VBENCH_CACHE_DIR",
    "vbench_repo": "SNF_VBENCH_ROOT",
}

# VBench resolves its RAFT checkpoint under VBENCH_CACHE_DIR and defaults to
# ~/.cache/vbench. Three scripts pinned an absolute path instead so the worker
# would not depend on the caller's environment -- right instinct, wrong fix,
# because the pinned path exists on exactly one machine.
CACHE_DEFAULT = os.path.expanduser("~/.cache/vbench")

_local_cache = None


def _local():
    global _local_cache
    if _local_cache is None:
        try:
            with open(LOCAL) as fh:
                _local_cache = json.load(fh)
        except (OSError, ValueError):
            _local_cache = {}
    return _local_cache


def resolve(key, required=True):
    """Path for `key`, from the environment or the untracked local file."""
    if key not in ENV:
        raise KeyError(f"unknown path key {key!r}; known: {sorted(ENV)}")
    value = os.environ.get(ENV[key]) or _local().get(key)
    if value and os.path.exists(value):
        return value
    if not required:
        return None
    raise SystemExit(
        f"path {key!r} is not configured or does not exist"
        f"{f' ({value})' if value else ''}.\n"
        f"  set ${ENV[key]}, or add {key!r} to "
        f"{os.path.relpath(LOCAL, ROOT)} (git-ignored).\n"
        f"  see scripts/_paths.py for what each key must point at.")


def vbench_cache():
    """Directory holding VBench's RAFT checkpoint; created if absent."""
    p = (os.environ.get("VBENCH_CACHE_DIR") or _local().get("vbench_cache")
         or CACHE_DEFAULT)
    os.makedirs(p, exist_ok=True)
    return p


def metric_source():
    """The v1.0 metric implementation this repository actually scores with.

    The tracked `metric_code/snf_task_metrics.py` is the provenance record, and
    until now `import snf_task_metrics` resolved to an identical copy inside a
    private repo instead -- byte-identical today, so no measurement was wrong,
    but nothing kept them that way. This returns the tracked path so the file
    under version control is the file that runs.
    """
    return os.path.join(METRIC_CODE, "snf_task_metrics.py")


def bootstrap_metric_imports():
    """Make `import snf_task_metrics` work, using the tracked copy.

    `metric_code/snf_task_metrics.py` prepends its own sibling
    `vbench/third_party/RAFT` to `sys.path` before importing `core.raft`. That
    directory does not exist here, and a non-existent entry is simply skipped,
    so putting the real RAFT directory on the path first satisfies the import
    without editing a file whose whole purpose is to stay byte-identical.
    """
    raft = os.path.join(resolve("vbench_home"), "vbench", "third_party", "RAFT")
    if not os.path.isdir(raft):
        raise SystemExit(
            f"vbench_home does not contain vbench/third_party/RAFT: {raft}")
    for p in (raft, METRIC_CODE):
        if p not in sys.path:
            sys.path.insert(0, p)
    return METRIC_CODE

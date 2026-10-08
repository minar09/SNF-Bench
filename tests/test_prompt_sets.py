"""v1 and v2 must stay separable: by filename, by storage root, and on write.

Nothing on disk is currently mis-filed, so the separation gate has never had
anything to catch. These tests construct the failure deliberately -- a v2 video
offered to the v1 scorer, a v2 result written over a v1 record -- because a
guard that has never fired cannot be told apart from one that does not work.

    ~/miniconda3/envs/snfeval/bin/python -m pytest tests/test_prompt_sets.py
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))

import prompt_sets as P  # noqa: E402


def _v1_text():
    return next(t for t in P.prompt_texts("v1") if len(t) > 80)


def _v2_text():
    return json.load(open(os.path.join(P.ROOT, "manifest/i2v_pairs_v2.json")))[
        "pairs"][0]["text"]


def test_sets_have_disjoint_roots():
    for kind in ("raw", "videos", "staging", "flow"):
        assert P.root("v1", kind) != P.root("v2", kind)
    assert P.root("v1", "raw").endswith("/raw")        # v1 paths unchanged


def test_classify_i2v_style_names():
    # I2V generators name outputs prompt[:100] + ".mp4", spaces kept
    assert P.classify(_v1_text()[:100] + ".mp4") == "v1"
    assert P.classify(_v2_text()[:100] + ".mp4") == "v2"


def test_classify_t2v_style_names():
    # T2V generators replace spaces with underscores and append seed-timestamp
    name = _v1_text()[:100].replace(" ", "_") + "-0-1778471300.18.mp4"
    assert P.classify(name) == "v1"
    name = _v2_text()[:100].replace(" ", "_") + "-0-1790000000.0.mp4"
    assert P.classify(name) == "v2"


def test_classify_ignores_duration_marker_and_unknowns():
    assert P.classify(_v2_text() + "[240s].mp4") == "v2"
    assert P.classify("completely_unrelated_clip_0001.mp4") is None


def test_no_v1_prompt_collides_with_a_v2_prompt():
    v1 = {P._norm(t)[:P._PREFIX] for t in P.prompt_texts("v1")}
    v2 = {P._norm(t)[:P._PREFIX] for t in P.prompt_texts("v2")}
    assert not (v1 & v2)


@pytest.fixture
def rm(tmp_path, monkeypatch):
    import rerun_metrics as R
    monkeypatch.setattr(R, "ROOT", str(tmp_path))
    yield R, tmp_path
    R.select_prompt_set(P.DEFAULT)


def test_v1_scorer_refuses_v2_videos(rm):
    R, tmp = rm
    R.select_prompt_set("v1")
    vids = [str(tmp / (_v2_text()[:100] + ".mp4")),
            str(tmp / (_v1_text()[:100] + ".mp4"))]
    wrong = R.foreign_videos(vids, "v1")
    assert len(wrong) == 1 and wrong[0][1] == "v2"


def test_select_v2_moves_every_root(rm):
    R, _ = rm
    R.select_prompt_set("v2")
    for attr in ("RAW", "STAGE", "VIDEOS", "FLOW", "FAIL"):
        assert getattr(R, attr).rstrip("/").split("/")[-1].endswith("_v2"), attr


def test_assemble_stamps_set_and_relative_dir(rm, monkeypatch):
    R, tmp = rm
    R.select_prompt_set("v2")
    monkeypatch.setattr(R, "RAW", str(tmp / "raw_v2"))
    monkeypatch.setattr(R, "VIDEOS", str(tmp / "videos_v2"))
    monkeypatch.setattr(R, "FAIL", str(tmp / "failures_v2"))
    R.assemble("i2v/m/60s", [{"video": "x.mp4", "fBD": 1.0}], [])
    d = json.load(open(tmp / "raw_v2/i2v/m/60s/snf_task_metrics.json"))
    assert d["prompt_set"] == "v2"
    assert d["videos_dir"] == "videos_v2/i2v/m/60s"


def test_assemble_refuses_to_merge_across_sets(rm, monkeypatch):
    R, tmp = rm
    rec = tmp / "raw/i2v/m/60s/snf_task_metrics.json"
    rec.parent.mkdir(parents=True)
    rec.write_text(json.dumps({"per_video": [], "fBD_mean": 3.0}))   # a v1 record
    R.select_prompt_set("v2")
    monkeypatch.setattr(R, "RAW", str(tmp / "raw"))                  # misfiled write
    monkeypatch.setattr(R, "FAIL", str(tmp / "failures_v2"))
    with pytest.raises(SystemExit):
        R.assemble("i2v/m/60s", [{"video": "x.mp4", "fBD": 1.0}], [])
    assert json.load(open(rec))["fBD_mean"] == 3.0                    # untouched


def _run(script, *args):
    import subprocess
    return subprocess.run([sys.executable, os.path.join(P.ROOT, "scripts", script),
                           *args], capture_output=True, text=True)


def test_both_prompt_sets_match_their_freeze():
    r = _run("freeze_prompt_sets.py")
    assert r.returncode == 0, r.stdout + r.stderr


def test_v2_consumer_files_match_the_manifests():
    r = _run("export_prompt_set.py", "--check")
    assert r.returncode == 0, r.stdout + r.stderr


def test_v1_loader_layout_present():
    # the I2V loader wants target_crop_info_<X>.json with images under <X>/
    for h, rel in P.get("v1")["i2v_dirs"].items():
        d = os.path.join(P.ROOT, rel)
        assert os.path.isdir(os.path.join(d, "16-9")), h
        assert not os.path.islink(os.path.join(d, "images")), \
            f"{h}: v1 images must be vendored, not a link into another repo"


def test_v2_splits_match_the_audit():
    r = _run("assign_v2_splits.py", "--check")
    assert r.returncode == 0, r.stdout + r.stderr

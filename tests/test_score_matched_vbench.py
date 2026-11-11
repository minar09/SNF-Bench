"""Staging-name rules and pure helpers of scripts/score_matched_vbench.py (CPU only, no VBench import)."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import score_matched_vbench as V  # noqa: E402

T2V_SCENES = ["cf01", "fp01", "ow01", "al01", "bp01", "cb01", "wb01", "gt01", "fw01"]


def figure_set_ids():
    with open(V.FIGSET) as f:
        return [s["id"] for s in json.load(f)["scenes"]]


@pytest.mark.parametrize("scene", T2V_SCENES + figure_set_ids())
def test_every_planned_scene_stages_legally(scene):
    for suite in ("long", "i2v"):
        stem = V.staged_stem(suite, scene)
        assert "_" not in stem and "/" not in stem and stem.endswith("-0")
    assert V.staged_stem("long", scene) == f"{scene}-0"
    assert V.staged_stem("i2v", scene) == f"{scene} camera static-0"
    assert V.image_stem(scene) == f"{scene} camera static"


@pytest.mark.parametrize("bad", ["cf_01", "a/b", "cf01-3", " cf01", ""])
def test_scene_ids_that_break_vbench_naming_are_refused(bad):
    with pytest.raises(ValueError):
        V.staged_stem("long", bad)


def test_get_prompt_from_filename_rule_recovers_the_image_stem():
    # vbench.utils.get_prompt_from_filename strips a trailing '-<digits>' from the stem
    import re
    stem = V.staged_stem("i2v", "pq0092")
    assert re.sub(r"-\d+$", "", stem) == V.image_stem("pq0092")


@pytest.mark.parametrize("part", V.FORBIDDEN_PATH_PARTS)
def test_forbidden_path_parts_are_refused(part, tmp_path):
    with pytest.raises(ValueError):
        V.check_stage_path(tmp_path / f"x{part}y" / "cf01-0.mp4")


def test_underscore_in_staged_basename_is_refused_but_not_in_parent_dirs(tmp_path):
    with pytest.raises(ValueError):
        V.check_stage_path(tmp_path / "stage" / "cf01_0.mp4")
    ok = tmp_path / "raw_matched_2026_11_10" / "steady_forcing" / "stage" / "cf01-0.mp4"
    assert V.check_stage_path(ok) == ok


def test_long_clip_plan_matches_the_official_rule():
    plan = V.long_clip_plan(961)                      # 30 full 32-frame clips + 1 back-extended remainder
    assert len(plan) == 31 and plan[-1] == (30, 929, 961)
    plan = V.long_clip_plan(3837)
    assert len(plan) == 120 and plan[-1] == (119, 3805, 3837)
    assert all(e - s == 32 for _, s, e in plan)
    assert V.long_clip_plan(20) == [("full", 0, 20)]


def test_windows_end_at_the_horizon_and_clamp_to_the_last_frame():
    assert V.window_frames(60, 3841) == (0, 960)
    assert V.window_frames(120, 3841) == (960, 1920)
    assert V.window_frames(240, 3841) == (2880, 3840)
    assert V.window_frames(240, 3837) == (2876, 3836)  # render 4 frames short: last 961 frames
    with pytest.raises(ValueError):
        V.window_frames(60, 900)


def test_staging_is_fresh_and_named_per_rules(tmp_path, monkeypatch):
    monkeypatch.setattr(V, "ROOT", tmp_path)
    vid = tmp_path / "in" / "p060.mp4"
    vid.parent.mkdir()
    vid.write_bytes(b"x")
    img = tmp_path / "in" / "pq0092.jpg"
    img.write_bytes(b"y")
    inp = dict(path="in/p060.mp4")
    vp, imgf, name = V.stage_unit(tmp_path / "u" / "h060", "long", "cf01", inp)
    assert imgf is None and name == "cf01-0.mp4" and os.readlink(vp / name) == str(vid)
    vp, imgf, name = V.stage_unit(tmp_path / "v" / "h060", "i2v", "pq0092", inp, dict(abspath=str(img)))
    assert name == "pq0092 camera static-0.mp4"
    assert os.readlink(imgf / "pq0092 camera static.jpg") == str(img)
    with pytest.raises(SystemExit):                   # never reuse a stage dir
        V.stage_unit(tmp_path / "u" / "h060", "long", "cf01", inp)


def test_long_command_is_the_aia_protocol():
    cmd = V.build_cmd("long", "/s", None, "/o")
    assert cmd[:2] == [V.VB_PY, "vbench2_beta_long/eval_long.py"]
    for flag in ("--dev_flag", "long_custom_input", "clip_length_mix.yaml", "dinov2", "dreamsim"):
        assert flag in cmd
    dims = cmd[cmd.index("--dimension") + 1:]
    assert dims == V.LONG_DIMS and dims.index("subject_consistency") < dims.index("background_consistency")
    cmd = V.build_cmd("i2v", "/s/videos", "/s/images", "/o")
    assert cmd[cmd.index("--custom_image_folder") + 1] == "/s/images"
    assert cmd[cmd.index("--dimension") + 1:] == ["i2v_subject", "i2v_background"]


def test_child_env_pins_the_gpu_and_cache():
    env = V.child_env(3)
    assert env["CUDA_VISIBLE_DEVICES"] == "3" and env["PYTHONPATH"] == V.VB
    assert env["VBENCH_CACHE_DIR"] == "/home/minar/.cache/vbench" and "VBENCH_MAX_FRAMES" not in env


def test_flatten_long_averages_this_videos_clips_and_rescales_iq():
    base = "/x/u/h060/stage/split_clip/cf01-0/cf01-0_{:03d}.mp4"
    res = {}
    for d in V.LONG_DIMS:
        if d in ("subject_consistency", "background_consistency"):
            items = [dict(video_path=base.format(i) + "/cf01-0.mp4", inclip_score=0.9, clip2clip_score=0.8,
                          mapped_clip2clip_score=0.95, video_results=0.5 + i / 100) for i in range(31)]
            res[d] = [0.6, items]
        else:
            v = (lambda i: 50.0) if d == "imaging_quality" else (lambda i: i % 2 == 0) if d == "dynamic_degree" \
                else (lambda i: 0.4)
            items = [dict(video_path=base.format(i), video_results=v(i)) for i in range(31)]
            res[d] = [0.1, items, items]
    vals, det, clips, notes = V.flatten_long(res, "cf01-0", 961)
    assert notes == []
    assert vals["imaging_quality"] == pytest.approx(0.5)
    assert vals["dynamic_degree"] == pytest.approx(16 / 31)
    assert vals["subject_consistency"] == pytest.approx(0.65)
    assert det["subject_consistency"]["n_clips"] == det["subject_consistency"]["n_clips_official_plan"] == 31

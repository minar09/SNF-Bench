"""`rerun_metrics.outdated_entries` must fire when a record predates its videos.

The check exists because a sibling repository scored an arm in 2m21s against
three-week-old metric JSONs left from a discarded run, and every downstream
table used them without complaint. A guard that never fires is indistinguishable
from a guard that does not work, and on this machine nothing is stale by a
margin of 1400+ hours, so the only way to know the comparison is wired up is to
construct staleness deliberately.

The real videos are read-only symlinks into upstream repositories, so the test
builds its own tree rather than touching them.

    ~/miniconda3/envs/snfeval/bin/python -m pytest tests/test_outdated_entries.py
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))


@pytest.fixture
def fake_tree(tmp_path, monkeypatch):
    """A minimal raw/ + videos/ pair for one public entry."""
    import registry
    import rerun_metrics as R

    pub = next(m for m in registry.ALL if m["status"] == "public")
    track, key, dur = pub["track"], pub["key"], "60s"

    raw = tmp_path / "raw" / track / key / dur
    vids = tmp_path / "videos" / track / key / dur
    raw.mkdir(parents=True)
    vids.mkdir(parents=True)
    rec = raw / "snf_task_metrics.json"
    rec.write_text('{"per_video": []}')
    video = vids / "clip.mp4"
    video.write_bytes(b"\0")

    monkeypatch.setattr(R, "RAW", str(tmp_path / "raw"))
    monkeypatch.setattr(R, "VIDEOS", str(tmp_path / "videos"))
    monkeypatch.setattr(R, "ROOT", str(tmp_path))
    return R, f"{track}/{key}/{dur}", rec, video


def test_fresh_record_is_not_flagged(fake_tree):
    R, entry, rec, video = fake_tree
    t = os.path.getmtime(str(rec))
    os.utime(str(video), (t - 3600, t - 3600))      # video older than record
    assert [e for e, _ in R.outdated_entries()] == []


def test_record_older_than_its_video_is_flagged(fake_tree):
    R, entry, rec, video = fake_tree
    t = os.path.getmtime(str(rec))
    os.utime(str(video), (t + 7200, t + 7200))      # video newer by 2 h
    hits = R.outdated_entries()
    assert [e for e, _ in hits] == [entry]
    assert "1/1 videos newer" in hits[0][1]
    assert "2.0 h" in hits[0][1]


def test_slack_suppresses_coarse_timestamp_noise(fake_tree):
    R, entry, rec, video = fake_tree
    t = os.path.getmtime(str(rec))
    os.utime(str(video), (t + 1, t + 1))            # 1 s newer
    assert [e for e, _ in R.outdated_entries()] == [entry]
    assert R.outdated_entries(slack_s=5) == []


def test_entry_without_videos_is_skipped(fake_tree):
    R, entry, rec, video = fake_tree
    t = os.path.getmtime(str(rec))
    os.utime(str(video), (t + 7200, t + 7200))
    os.remove(str(video))
    assert R.outdated_entries() == []

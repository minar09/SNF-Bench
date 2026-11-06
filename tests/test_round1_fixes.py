"""Round-1 review fixes: fail-closed adoption, codec-floor abstentions, reference and static checks."""
import json
import os
import sys

import cv2
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import native_controls as NC        # noqa: E402
import pilot_support_realism as PS  # noqa: E402
import realism_replay as RR         # noqa: E402


# ---------------------------------------------------------------- adoption fails closed

def adoption_fixture(tmp_path, monkeypatch, record):
    cell = "control_pasteback_nfpb1_copy_lr"
    run_dir = tmp_path / "results/factorial/cfpp" / cell / "seed42/60s"
    run_dir.mkdir(parents=True)
    video, parent = tmp_path / "control.mp4", tmp_path / "parent.mp4"
    video.write_bytes(b"control")
    parent.write_bytes(b"parent")
    rec = {"video": str(video), **record(NC.sha256(video), NC.sha256(parent))}
    (run_dir / "RUN.json").write_text(json.dumps({"videos": {"s1": rec}, "encoder": "x"}))
    listing = tmp_path / "list.tsv"
    listing.write_text(f"s1\t{parent}\n")
    monkeypatch.setattr(NC, "METHOD", str(tmp_path))
    monkeypatch.setattr(NC, "chain", lambda sid, sha: {"parent_sha256": sha})
    monkeypatch.setattr(NC, "probe", lambda path: {})
    return cell, str(listing), str(tmp_path / "out")


def test_adoption_refuses_a_record_without_the_parent_hash(tmp_path, monkeypatch):
    cell, listing, out = adoption_fixture(tmp_path, monkeypatch, lambda o, p: {"sha256": o})
    with pytest.raises(SystemExit, match="lacks"):
        NC.adopt(cell, listing, out)
    assert not os.path.lexists(f"{out}/s1.mp4")


def test_adoption_refuses_a_wrong_parent_hash(tmp_path, monkeypatch):
    cell, listing, out = adoption_fixture(tmp_path, monkeypatch,
                                          lambda o, p: {"sha256": o, "echo_sha256": "0" * 64})
    with pytest.raises(SystemExit, match="differ"):
        NC.adopt(cell, listing, out)


def test_adoption_accepts_a_complete_matching_record(tmp_path, monkeypatch):
    cell, listing, out = adoption_fixture(tmp_path, monkeypatch, lambda o, p: {"sha256": o, "echo_sha256": p})
    NC.adopt(cell, listing, out)
    side = json.load(open(f"{out}/s1.json"))
    assert side["parent_evidence"].endswith("[echo_sha256]")


def test_adoption_refuses_an_undeclared_cell(tmp_path):
    with pytest.raises(SystemExit, match="no declared parent key"):
        NC.adopt("control_unknown", str(tmp_path / "x.tsv"), str(tmp_path / "out"))


# ---------------------------------------------------------------- codec-floor abstentions

def masks():
    dyn = np.zeros((120, 200), bool)
    dyn[40:80, 60:140] = True
    sup = ~(np.pad(dyn[1:-1, 1:-1], 1) | dyn)
    sup[30:90, 50:150] = False          # ignore band around the dynamic region
    return dyn, sup


def test_edge_profile_2_abstains_on_a_frozen_support():
    dyn, sup = masks()
    act = np.where(dyn, 8.0, 0.0).astype(np.float32)        # pasted support: codec-silent
    out = PS.stats(act, dyn, sup)
    assert "edge_spill" in out                               # -1 still reports its inflated ratio
    assert "edge_spill_2" not in out and "codec floor" in out["abstain"]["edge_spill_2"]


def test_edge_profile_2_matches_profile_1_above_the_floor():
    dyn, sup = masks()
    act = np.where(dyn, 8.0, 2.0).astype(np.float32)
    out = PS.stats(act, dyn, sup)
    assert out["edge_spill_2"] == pytest.approx(out["edge_spill"])
    assert out["boundary_step_2"] == pytest.approx(out["boundary_step"])


def replay_measure(monkeypatch, frames):
    monkeypatch.setattr(RR, "window", lambda path: (frames, 8.0))
    dyn = np.zeros(frames[0].shape[:2], bool)
    dyn[10:90, 10:150] = True
    return RR.measure("unused.mp4", dyn)


def test_seam_1_abstains_on_a_frozen_region(monkeypatch):
    still = np.full((100, 160, 3), 128, np.uint8)
    frames = [still.copy() for _ in range(200)]
    frames[100] = frames[100] + 3                            # codec-like refresh step
    out = replay_measure(monkeypatch, frames)
    assert out["seam"] > 1e5                                 # -0 explodes
    assert "seam_1" not in out and "codec floor" in out["abstain"]["seam_1"]


def test_seam_1_reports_a_cut_in_moving_material(monkeypatch):
    rng = np.random.default_rng(0)
    frames = [rng.integers(0, 255, (100, 160, 3), np.uint8) for _ in range(200)]
    out = replay_measure(monkeypatch, frames)
    assert out["seam_1"] == pytest.approx(out["seam"], rel=1e-6)


# ---------------------------------------------------------------- reference and static checks

def test_reference_must_be_a_passthrough(tmp_path):
    for mode, ok in (("passthrough_crf18", True), ("loop_exact", False)):
        path = tmp_path / f"{mode}.mp4"
        path.write_bytes(b"")
        (tmp_path / f"{mode}.json").write_text(json.dumps({"mode": mode}))
        if ok:
            PS.verify_reference(str(path))
        else:
            with pytest.raises(SystemExit, match="not a pass-through"):
                PS.verify_reference(str(path))


def write_clip(path, frames):
    out = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 16, frames[0].shape[1::-1])
    for f in frames:
        out.write(f)
    out.release()


def test_static_check_accepts_the_source_and_rejects_another_image(tmp_path):
    rng = np.random.default_rng(3)
    src = cv2.GaussianBlur(rng.integers(0, 255, (96, 160, 3), np.uint8), (0, 0), 3)
    other = cv2.GaussianBlur(rng.integers(0, 255, (96, 160, 3), np.uint8), (0, 0), 3)
    cv2.imwrite(str(tmp_path / "src.png"), src)
    write_clip(tmp_path / "good.mp4", [src] * 16)
    write_clip(tmp_path / "bad.mp4", [other] * 16)
    write_clip(tmp_path / "drifts.mp4", [src] * 8 + [other] * 8)
    assert PS.verify_static(str(tmp_path / "good.mp4"), str(tmp_path / "src.png"))["psnr_last_db"] >= 30
    for bad in ("bad.mp4", "drifts.mp4"):
        with pytest.raises(SystemExit, match="not a still"):
            PS.verify_static(str(tmp_path / bad), str(tmp_path / "src.png"))

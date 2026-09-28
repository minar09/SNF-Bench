"""Guard the shared-source mask path against silent geometry or label errors."""

import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import external_masks as M  # noqa: E402
import snf_metrics_v11 as V11  # noqa: E402


def source_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "ROOT", tmp_path)
    src = np.zeros((80, 120, 3), np.uint8)
    src[:, :60] = (40, 70, 100)
    labels = np.zeros((80, 120), np.uint8)
    labels[:, :60] = 1
    labels[:, 60:] = 2
    cv2.imwrite(str(tmp_path / "source.png"), src)
    cv2.imwrite(str(tmp_path / "labels.png"), labels)
    return {"track": "i2v", "duration": "60s", "prompt_id": "example",
            "source_image": "source.png", "source_sha256": M.sha256(tmp_path / "source.png"),
            "label_png": "labels.png", "geometry": "direct_resize",
            "reviewed": True, "reviewed_by": "independent-annotator-1"}


def test_reviewed_mask_resizes_labels_and_keeps_roles_disjoint(tmp_path, monkeypatch):
    entry = source_entry(tmp_path, monkeypatch)
    dynamic, static, provenance = M.load_reviewed_mask(entry, (60, 40))
    assert dynamic.shape == static.shape == (40, 60)
    assert not np.any(dynamic & static)
    assert dynamic.mean() == static.mean() == 0.5
    assert provenance["mask_source_sha256"] == entry["source_sha256"]


def test_mask_rejects_unreviewed_or_changed_source(tmp_path, monkeypatch):
    entry = source_entry(tmp_path, monkeypatch)
    entry["reviewed"] = False
    with pytest.raises(ValueError, match="review"):
        M.load_reviewed_mask(entry, (60, 40))
    entry["reviewed"] = True
    cv2.imwrite(str(tmp_path / "source.png"), np.ones((80, 120, 3), np.uint8))
    with pytest.raises(ValueError, match="hash"):
        M.load_reviewed_mask(entry, (60, 40))


def test_alignment_check_requires_matching_video_and_good_geometry(tmp_path):
    report = tmp_path / "alignment.json"
    video = "videos/i2v/example/60s/example.mp4"
    report.write_text(json.dumps({"rows": [{"video": video, "ransac_inliers": 100,
                                            "corner_shift_fraction": 0.004}]}))
    assert M.verify_alignment(report, video)["alignment_inliers"] == 100
    with pytest.raises(ValueError, match="lacks"):
        M.verify_alignment(report, "another.mp4")


def test_external_mask_control_preserves_default_scoring_when_masks_agree(monkeypatch):
    shape = (80, 120)
    static = np.zeros(shape, bool)
    static[:, :60] = True
    dynamic = ~static
    flow = np.zeros((*shape, 2), np.float32)
    flow[dynamic, 0] = 1.0
    monkeypatch.setattr(V11.S, "read_frames", lambda path, device: ([None] * 12,
                         [np.zeros(shape, np.uint8) for _ in range(12)]))
    monkeypatch.setattr(V11.S, "flow_mag", lambda *args: np.ones(shape, np.float32))
    monkeypatch.setattr(V11.S, "build_masks", lambda early: (dynamic, static))
    monkeypatch.setattr(V11.S, "flow_vec", lambda *args: flow)
    monkeypatch.setattr(V11.S, "orb_drift", lambda *args: 0.25)
    default = V11.process_video(None, "example.mp4", "cpu")
    pilot = V11.process_video(None, "example.mp4", "cpu",
                              external_masks=(dynamic, static),
                              mask_provenance={"mask_source": "test"})
    for key in ("fBD", "BFR", "FP", "MCFF_early", "MCFF_late", "DAR_signed"):
        assert default[key] == pytest.approx(pilot[key])
    assert default["metric_spec_version"] == "1.1"
    assert pilot["metric_spec_version"] == "2-mask-pilot"

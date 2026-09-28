"""The reliability trace must preserve frozen fBD behavior."""

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_fbd_reliability import compact_trace, trace_orb_drift  # noqa: E402


def textured_frames():
    rng = np.random.default_rng(7)
    base = rng.integers(0, 256, size=(180, 240), dtype=np.uint8)
    cv2.rectangle(base, (20, 20), (210, 150), 255, 3)
    frames = [base]
    for shift in (1, 2, 3, 4):
        matrix = np.float32([[1, 0, shift], [0, 1, 0]])
        frames.append(cv2.warpAffine(base, matrix, (240, 180),
                                     borderMode=cv2.BORDER_REFLECT))
    return frames


def test_trace_reproduces_frozen_orb_drift():
    sys.path.insert(0, "/home/minar/region-forcing/snf_eval")
    import snf_task_metrics as frozen

    frames = textured_frames()
    static = np.ones(frames[0].shape, dtype=bool)
    indices = [1, 2, 3, 4]
    reference = frozen.orb_drift(frames, static, indices)
    trace = compact_trace(trace_orb_drift(frames, static, indices))
    assert trace["fBD"] == reference
    assert trace["usable_late_frames"] == 4
    assert trace["late_frames_requested"] == 4
    assert trace["base_keypoints"] >= 12


def test_blank_frame_records_explicit_abstention():
    frames = [np.zeros((120, 160), dtype=np.uint8) for _ in range(3)]
    static = np.ones(frames[0].shape, dtype=bool)
    trace = compact_trace(trace_orb_drift(frames, static, [1, 2]))
    assert trace["fBD"] is None
    assert trace["abstention_reason"] == "base_descriptors_or_keypoints_below_12"
    assert trace["usable_late_frames"] == 0

"""Fast checks for the ported source-referenced scorer (no RAFT, no GPU).

The expensive check -- both implementations on the same real clip, every
output identical -- is `scripts/check_sourceref_parity.py`.
"""
import ast
import hashlib
import inspect
import os
import sys

import cv2
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))
import snf_sourceref as P  # noqa: E402
import measurement  # noqa: E402

W, H = P.SIZE


def test_copied_bodies_are_unedited():
    src = open(P.__file__).read()
    tree = ast.parse(src)
    have = {n.name: hashlib.sha256(ast.get_source_segment(src, n).encode()).hexdigest()
            for n in tree.body if isinstance(n, ast.FunctionDef)
            and n.name in P.UPSTREAM_FUNCTION_SHA256}
    assert have == P.UPSTREAM_FUNCTION_SHA256


def test_upstream_has_not_drifted_if_present():
    up = "/home/minar/ar-image-animation/tools/factorial_scoring/sourcefixed_metrics.py"
    if not os.path.exists(up):
        pytest.skip("upstream not on this machine")
    src = open(up).read()
    tree = ast.parse(src)
    now = {n.name: hashlib.sha256(ast.get_source_segment(src, n).encode()).hexdigest()
           for n in tree.body if isinstance(n, ast.FunctionDef)
           and n.name in P.UPSTREAM_FUNCTION_SHA256}
    changed = [k for k in P.UPSTREAM_FUNCTION_SHA256 if now.get(k) != P.UPSTREAM_FUNCTION_SHA256[k]]
    assert not changed, f"upstream changed {changed}: re-port deliberately, under a new identity"


def _write_labels(path, rows):
    lab = np.zeros((H, W), np.uint8)
    for (y0, y1, v) in rows:
        lab[y0:y1] = v
    cv2.imwrite(str(path), lab)
    return lab


def test_role_masks_load(tmp_path):
    p = tmp_path / "labels.png"
    _write_labels(p, [(0, 200, 1), (200, 400, 2), (400, 440, 3)])
    dyn, sup, sha, reg = P.load_role_masks(str(p))
    assert dyn.sum() == 200 * W and sup.sum() == 200 * W
    assert not (dyn & sup).any()
    assert abs(reg["overlay"] - 40 / H) < 1e-9 and len(sha) == 64


def test_role_masks_refuse_bad_labels(tmp_path):
    p = tmp_path / "labels.png"
    _write_labels(p, [(0, 10, 7)])
    with pytest.raises(ValueError):
        P.load_role_masks(str(p))


def _video(path, frames, fps=16):
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
    for f in frames:
        vw.write(f)
    vw.release()


def _scene(seed=0):
    rng = np.random.default_rng(seed)
    base = cv2.GaussianBlur(rng.integers(0, 255, (H, W, 3), dtype=np.uint8), (5, 5), 0)
    return base


def test_extras_detect_colour_drift_against_source(tmp_path):
    base = _scene()
    stable = [base.copy() for _ in range(48)]
    drift = [np.clip(base.astype(int) + int(i * 1.2), 0, 255).astype(np.uint8) for i in range(48)]
    _video(tmp_path / "stable.mp4", stable)
    _video(tmp_path / "drift.mp4", drift)
    dyn = np.zeros((H, W), bool); dyn[300:400] = True
    sup = np.zeros((H, W), bool); sup[:250] = True
    a = P.extras_sourcefixed(str(tmp_path / "stable.mp4"), dyn, sup, base)
    b = P.extras_sourcefixed(str(tmp_path / "drift.mp4"), dyn, sup, base)
    assert b["dE_static_src"] > a["dE_static_src"] + 5
    assert b["idPSNR_late_src"] < a["idPSNR_late_src"] - 5


def test_record_policy_never_pools_with_v11():
    v11 = {"per_video": [{"metric_spec_version": "1.1", "mask_version": "pre-overlay-v0",
                          "flow_backbone": "RAFT", "feature_backbone": "ORB"}]}
    port = {"prompt_set": "v1", "per_video": [dict(P.POLICY, mask_version="source-clipseg-auto-v0",
                                                   mask_set="sha256:x", mask_review_scope="ai",
                                                   flow_backbone="RAFT", feature_backbone="ORB")]}
    with pytest.raises(ValueError):
        measurement.assert_poolable([("a", v11), ("b", port)])

"""Tables must not pool different measurements (mask, spec, prompt set, backbone)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))
import measurement as M  # noqa: E402

V11 = {"metric_spec_version": "1.1", "mask_version": "pre-overlay-v0",
       "flow_backbone": "RAFT", "feature_backbone": "ORB"}


def rec(prompt_set=None, **over):
    s = {"per_video": [dict(V11, **over)]}
    if prompt_set:
        s["prompt_set"] = prompt_set
    return s


def test_same_measurement_pools():
    assert M.assert_poolable([("a", rec()), ("b", rec())])[0] == "v1"


@pytest.mark.parametrize("over", [
    {"mask_version": "shared-source-v1"},     # output-derived vs shared mask
    {"metric_spec_version": "1.0"},            # translation vs similarity
    {"flow_backbone": "SEA-RAFT"},
])
def test_different_measurement_refused(over):
    with pytest.raises(ValueError):
        M.assert_poolable([("a", rec()), ("b", rec(**over))])


def test_prompt_sets_never_pool():
    with pytest.raises(ValueError):
        M.assert_poolable([("a", rec()), ("b", rec(prompt_set="v2"))])


def test_unlabelled_records_are_not_assumed_compatible():
    bare = {"per_video": [{"fBD": 1.0}]}
    with pytest.raises(ValueError):
        M.assert_poolable([("a", rec()), ("b", bare)])


@pytest.mark.parametrize("over", [
    {"reference_policy": "source_image"},           # frame 0 vs source image
    {"mask_set": "sha256:a46afad8333e"},             # output-derived vs shared masks
    {"mask_review_scope": "ai"},
    {"window_policy": "fixed:51-60s"},
    {"failure_policy": "registered_only"},
])
def test_source_fixed_policies_never_pool_with_v11(over):
    with pytest.raises(ValueError):
        M.assert_poolable([("a", rec()), ("b", rec(**over))])


def test_v11_records_get_their_known_policies():
    sig = dict(zip(M.FIELDS, M.signature({}, dict(V11))))
    assert sig["reference_policy"] == "output_frame0"
    assert sig["mask_set"] == "output-derived"


def test_explicit_field_beats_legacy_default():
    sig = dict(zip(M.FIELDS, M.signature({}, dict(V11, reference_policy="source_image"))))
    assert sig["reference_policy"] == "source_image"

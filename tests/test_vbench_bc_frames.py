"""Check the incumbent formula without loading CLIP or a GPU."""

import sys
from pathlib import Path

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from vbench_bc_frames import score_features  # noqa: E402


def test_adjacent_and_first_frame_are_both_used():
    features = torch.tensor([[1., 0.], [0., 1.], [1., 0.]])
    # Frame 1: 0; frame 2: (0 adjacent + 1 first) / 2.
    assert score_features(features) == pytest.approx(0.25)


def test_negative_similarity_is_clipped_as_in_vbench():
    features = torch.tensor([[1., 0.], [-1., 0.]])
    assert score_features(features) == 0.0

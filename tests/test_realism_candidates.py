"""Known answers for the R3 direction and R4 replay candidates (no RAFT, no video files)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import realism_direction as RD  # noqa: E402
import realism_replay as RR     # noqa: E402

FPS = 8


def test_residual_recurrence_finds_an_exact_loop_and_not_noise():
    rng = np.random.default_rng(1)
    period = 3 * FPS
    loop = rng.standard_normal((period, 300))
    looped = np.concatenate([loop] * 8)
    fresh = rng.standard_normal((len(looped), 300))
    score_loop, lag = RR.sustained_match(looped, FPS)
    score_fresh, _ = RR.sustained_match(fresh, FPS)
    assert score_loop == pytest.approx(1.0, abs=1e-9)
    assert lag % 3 == pytest.approx(0, abs=1e-9)
    assert score_fresh < 0.3


def test_sustained_match_ignores_lags_below_the_minimum():
    rng = np.random.default_rng(2)
    short = rng.standard_normal((FPS, 300))          # 1 s period, below MIN_LAG_S
    score, lag = RR.sustained_match(np.concatenate([short] * 12), FPS)
    assert lag >= RR.MIN_LAG_S


class StubFlow:
    """Stands in for RAFT: every pair has the same uniform flow (dx, dy)."""

    def __init__(self, dx, dy):
        self.v = (dx, dy)


def run_stub(monkeypatch, dx, dy, direction, n=40):
    h, w = 32, 48
    monkeypatch.setattr(RD, "late_frames", lambda path, device: [np.zeros((1, 3, h, w))] * n)
    monkeypatch.setattr(RD.S, "flow_vec", lambda model, a, b: np.broadcast_to(np.float32(model.v), (h, w, 2)))
    dyn = np.zeros((480, 832), bool)
    dyn[100:400, 200:700] = True
    return RD.measure(StubFlow(dx, dy), "unused.mp4", dyn, direction, "cpu")


def test_flux_sign_follows_the_declared_direction(monkeypatch):
    assert run_stub(monkeypatch, 1.0, 0.0, "left to right")["flux"] == pytest.approx(1.0)
    assert run_stub(monkeypatch, 1.0, 0.0, "right to left")["flux"] == pytest.approx(-1.0)
    assert run_stub(monkeypatch, 0.0, -1.0, "upward")["flux"] == pytest.approx(1.0)
    assert run_stub(monkeypatch, 0.0, 1.0, "left to right")["flux"] == pytest.approx(0.0, abs=1e-9)
    diag = run_stub(monkeypatch, 1.0, 1.0, "upper left to lower right")
    assert diag["flux"] == pytest.approx(1.0) and diag["agreement"] == 1.0


def test_direction_abstains_without_label_or_motion(monkeypatch):
    assert "abstain" in run_stub(monkeypatch, 1.0, 0.0, None)
    assert "abstain" in run_stub(monkeypatch, 1.0, 0.0, "swirling")
    still = run_stub(monkeypatch, 0.01, 0.0, "left to right")
    assert "abstain" in still and "flux" not in still


def test_replay_abstains_on_an_empty_dynamic_region(monkeypatch):
    frames = [np.zeros((480, 832, 3), np.uint8)] * (RR.WINDOW_S * FPS)
    monkeypatch.setattr(RR.C, "read_sampled", lambda path: (frames, float(FPS)))
    out = RR.measure("unused.mp4", np.zeros((480, 832), bool))
    assert "eroded dynamic region" in out["abstain"]

"""Known answers for the material-drift port."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import realism_drift as D  # noqa: E402


def means(n=960, mat_ramp=0.0, sup_ramp=0.0):
    t = np.linspace(0, 1, n)[:, None]
    base = np.array([[120.0, 128.0, 128.0]])
    return dict(material=base + mat_ramp * t * np.array([[1, 0, 0]]),
                support=base + sup_ramp * t * np.array([[1, 0, 0]]))


def test_stable_colour_has_no_drift():
    out = D.drift(means(), 16.0)
    assert out["drift_material"] == pytest.approx(0) and out["delta"] == pytest.approx(0)


def test_material_ramp_is_material_specific():
    out = D.drift(means(mat_ramp=30.0), 16.0)
    assert out["drift_material"] > 15 and out["delta"] > 15


def test_global_exposure_change_cancels_in_the_contrast():
    out = D.drift(means(mat_ramp=30.0, sup_ramp=30.0), 16.0)
    assert out["drift_material"] > 15 and abs(out["delta"]) < 1e-6


def test_windows_are_in_seconds():
    assert D.drift(means(n=1440), 24.0)["early"] == [36, 72]
    assert D.drift(means(n=960), 16.0)["early"] == [24, 48]
    assert "abstain" in D.drift(means(n=40), 16.0)

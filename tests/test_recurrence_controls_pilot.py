"""The pilot's interventions preserve support and impose the requested motion."""
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from pilot_recurrence_controls import controls


def test_controls_only_replace_dynamic_region():
    frames = [np.full((3, 4, 3), i, dtype=np.uint8) for i in range(6)]
    dynamic = np.zeros((3, 4), dtype=bool)
    dynamic[1, 1:3] = True
    loop, freeze = controls(frames, dynamic, 3)
    for i, frame in enumerate(frames):
        np.testing.assert_array_equal(loop[i][~dynamic], frame[~dynamic])
        np.testing.assert_array_equal(freeze[i][~dynamic], frame[~dynamic])
        np.testing.assert_array_equal(loop[i][dynamic], frames[i % 3][dynamic])
        np.testing.assert_array_equal(freeze[i][dynamic], frames[0][dynamic])

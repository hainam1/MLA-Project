from __future__ import annotations

import numpy as np
from sklearn.tree import DecisionTreeClassifier

from src.models.calibration import TemperatureScaledClassifier


def test_temperature_scaling_preserves_predictions_and_normalizes_probabilities():
    features = np.array([[0.0], [0.5], [1.0], [1.5], [2.0], [2.5]])
    labels = np.array([0, 0, 1, 1, 2, 2])
    base = DecisionTreeClassifier(max_depth=2, random_state=42).fit(features, labels)
    calibrated = TemperatureScaledClassifier(base, temperature=1.7)

    assert np.array_equal(base.predict(features), calibrated.predict(features))
    assert np.allclose(calibrated.predict_proba(features).sum(axis=1), 1.0)

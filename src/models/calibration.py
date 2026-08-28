"""Serializable probability-calibration wrappers."""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin


class TemperatureScaledClassifier(ClassifierMixin, BaseEstimator):
    """Calibrate probabilities while preserving the fitted estimator's decisions."""

    def __init__(self, estimator, temperature: float = 1.0):
        self.estimator = estimator
        self.temperature = float(temperature)

    @property
    def classes_(self):
        return self.estimator.classes_

    @property
    def feature_names_in_(self):
        return self.estimator.feature_names_in_

    @property
    def n_features_in_(self):
        return self.estimator.n_features_in_

    def predict(self, features):
        return self.estimator.predict(features)

    def predict_proba(self, features):
        probabilities = np.clip(self.estimator.predict_proba(features), 1e-12, 1.0)
        logits = np.log(probabilities) / self.temperature
        logits -= logits.max(axis=1, keepdims=True)
        scaled = np.exp(logits)
        return scaled / scaled.sum(axis=1, keepdims=True)

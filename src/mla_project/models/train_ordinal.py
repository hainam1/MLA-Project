"""A lightweight cumulative-logit ordinal regressor for half-point rubric scores."""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


class CumulativeLogitRegressor(RegressorMixin, BaseEstimator):
    """Fit one binary logistic model per ordered threshold and return expected score."""

    def __init__(self, *, c: float = 1.0, max_iter: int = 2_000, random_state: int = 42):
        self.c = c
        self.max_iter = max_iter
        self.random_state = random_state

    def fit(self, x, y, sample_weight=None):
        scores = np.asarray(y, dtype=float)
        self.minimum_score_ = 1.0
        self.step_ = 0.5
        self.thresholds_ = np.arange(1.0, 5.0, self.step_)
        self.imputer_ = SimpleImputer(strategy="median")
        self.scaler_ = StandardScaler()
        transformed = self.scaler_.fit_transform(self.imputer_.fit_transform(x))
        self.models_: list[LogisticRegression | float] = []
        for threshold in self.thresholds_:
            binary = (scores > threshold).astype(int)
            if np.unique(binary).size == 1:
                self.models_.append(float(binary[0]))
                continue
            model = LogisticRegression(
                C=self.c,
                max_iter=self.max_iter,
                random_state=self.random_state,
            )
            model.fit(transformed, binary, sample_weight=sample_weight)
            self.models_.append(model)
        return self

    def predict(self, x):
        transformed = self.scaler_.transform(self.imputer_.transform(x))
        probabilities = []
        for model in self.models_:
            if isinstance(model, float):
                probabilities.append(np.full(len(transformed), model))
            else:
                probabilities.append(model.predict_proba(transformed)[:, 1])
        cumulative = np.column_stack(probabilities)
        cumulative = np.minimum.accumulate(cumulative, axis=1)
        return self.minimum_score_ + self.step_ * cumulative.sum(axis=1)

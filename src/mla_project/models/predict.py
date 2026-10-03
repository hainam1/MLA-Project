"""Prediction helpers for named model artifacts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd


def predict_model_set(models: Mapping[str, Any], features: pd.DataFrame) -> dict[str, float]:
    """Predict one feature row with all four required named models."""
    expected = {
        "ridge_vocabulary",
        "ridge_grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
    }
    missing = sorted(expected.difference(models))
    if missing:
        raise ValueError(f"Missing required model artifacts: {missing}")
    if len(features) != 1:
        raise ValueError("Inference expects exactly one feature row.")
    return {
        name: float(model.predict(features)[0])
        for name, model in models.items()
        if name in expected
    }

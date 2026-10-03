"""Random Forest regression pipeline factory."""

from __future__ import annotations

from typing import Any

from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


def build_random_forest(**parameters: Any) -> Pipeline:
    """Build a median-imputed Random Forest with explicit reproducibility settings."""
    defaults = {
        "n_estimators": 300,
        "max_depth": None,
        "min_samples_leaf": 2,
        "max_features": "sqrt",
        "random_state": 42,
        "n_jobs": -1,
    }
    defaults.update(parameters)
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestRegressor(**defaults)),
        ]
    )

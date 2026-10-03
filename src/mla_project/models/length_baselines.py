"""Deterministic reconstruction of the frozen Phase 5 length-only estimators."""

from __future__ import annotations

from typing import Any

import pandas as pd

from mla_project.models.train_random_forest import build_random_forest
from mla_project.models.train_ridge import build_ridge

LENGTH_FEATURES = ("word_count", "sentence_count", "mean_sentence_length")
TARGETS = ("Vocabulary", "Grammar")
FROZEN_RIDGE_ALPHA = 1.0
FROZEN_FOREST_PARAMETERS = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_leaf": 2,
    "max_features": "sqrt",
    "random_state": 42,
    "n_jobs": 1,
}


def reconstruct_length_models(train: pd.DataFrame) -> dict[str, Any]:
    """Fit only the authorized frozen baselines on eligible model-train rows."""
    required = {"essay_id", *LENGTH_FEATURES, *TARGETS}
    missing = sorted(required.difference(train.columns))
    if missing:
        raise ValueError(f"Length-baseline training data are missing columns: {missing}")
    if len(train) != 3_050:
        raise ValueError("Length baselines must use exactly 3,050 eligible model-train essays.")
    if "split" in train.columns and set(train["split"].astype(str)) != {"model_train"}:
        raise ValueError("Length-baseline reconstruction accepts model_train rows only.")
    x_train = train.loc[:, list(LENGTH_FEATURES)]
    models: dict[str, Any] = {}
    for target in TARGETS:
        ridge = build_ridge(alpha=FROZEN_RIDGE_ALPHA)
        forest = build_random_forest(**FROZEN_FOREST_PARAMETERS)
        ridge.fit(x_train, train[target].to_numpy(dtype=float))
        forest.fit(x_train, train[target].to_numpy(dtype=float))
        models[f"length_ridge_{target.lower()}"] = ridge
        models[f"length_random_forest_{target.lower()}"] = forest
    return models


def predict_length_models(models: dict[str, Any], frame: pd.DataFrame) -> pd.DataFrame:
    """Generate named predictions with the frozen length-only estimators."""
    x = frame.loc[:, list(LENGTH_FEATURES)]
    result = pd.DataFrame({"essay_id": frame["essay_id"].astype("string").to_numpy()})
    for target in TARGETS:
        for family in ("ridge", "random_forest"):
            name = f"length_{family}_{target.lower()}"
            if name not in models:
                raise ValueError(f"Missing reconstructed baseline model: {name}")
            result[name] = models[name].predict(x)
    return result

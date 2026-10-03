"""Factories for the four required target/model combinations."""

from __future__ import annotations

from typing import Any

from sklearn.pipeline import Pipeline

from mla_project.models.train_random_forest import build_random_forest
from mla_project.models.train_ridge import build_ridge

TARGETS = ("Vocabulary", "Grammar")


def build_model_set(
    ridge_config: dict[str, Any] | None = None,
    random_forest_config: dict[str, Any] | None = None,
) -> dict[str, Pipeline]:
    """Return unfitted Ridge and Random Forest pipelines for both targets."""
    ridge = dict(ridge_config or {})
    forest = dict(random_forest_config or {})
    ridge_alpha = float(ridge.get("alpha", 1.0))
    forest_parameters = {
        "n_estimators": forest.get("n_estimators", 300),
        "max_depth": forest.get("max_depth"),
        "min_samples_leaf": forest.get("min_samples_leaf", 2),
        "max_features": forest.get("max_features", "sqrt"),
        "random_state": forest.get("random_seed", 42),
        "n_jobs": forest.get("n_jobs", 1),
    }
    return {f"ridge_{target.lower()}": build_ridge(alpha=ridge_alpha) for target in TARGETS} | {
        f"random_forest_{target.lower()}": build_random_forest(**forest_parameters)
        for target in TARGETS
    }

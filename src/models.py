"""Compatibility shim; use :mod:`mla_project.models`."""

from mla_project.models.model_selection import build_model_set


def build_models(random_seed: int = 42):
    """Return the current four-model set for older imports."""
    return build_model_set(random_forest_config={"random_seed": random_seed})


__all__ = ["build_models", "build_model_set"]

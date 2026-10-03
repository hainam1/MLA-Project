"""Frozen validation-only helpers for Phase 8 review prioritization."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from mla_project.evaluation.review_metrics import review_queue_metrics

REQUIRED_COLUMNS = (
    "essay_id",
    "split",
    "word_count",
    "Vocabulary",
    "Grammar",
    "ridge_vocabulary",
    "ridge_grammar",
    "random_forest_vocabulary",
    "random_forest_grammar",
)


def validate_phase8_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate that a Phase 8 frame is a unique validation-only population."""
    missing = sorted(set(REQUIRED_COLUMNS).difference(frame.columns))
    if missing:
        raise ValueError(f"Phase 8 data are missing columns: {missing}")
    result = frame.loc[:, list(REQUIRED_COLUMNS)].copy()
    result["essay_id"] = result["essay_id"].astype("string")
    if result["essay_id"].isna().any() or result["essay_id"].duplicated().any():
        raise ValueError("Phase 8 essay IDs must be unique and non-null.")
    observed_splits = set(result["split"].dropna().astype(str))
    if observed_splits != {"validation"}:
        raise ValueError(
            "Phase 8 is validation only; official_test and other splits are forbidden."
        )
    numeric_columns = [column for column in REQUIRED_COLUMNS if column not in {"essay_id", "split"}]
    numeric = result[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any() or not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError(
            "Phase 8 labels, predictions, and word counts must be finite numeric values."
        )
    result.loc[:, numeric_columns] = numeric
    return result


def review_count(population_size: int, budget: float) -> int:
    """Return the frozen ceiling-sized review queue."""
    if population_size < 1 or not 0 < budget <= 1:
        raise ValueError("population_size must be positive and budget must be in (0, 1].")
    return math.ceil(population_size * budget)


def add_review_signals(frame: pd.DataFrame, *, error_threshold: float = 1.0) -> pd.DataFrame:
    """Add RF reference errors and label-free Ridge/RF disagreement scores."""
    result = validate_phase8_frame(frame)
    result["error_vocabulary"] = (result["random_forest_vocabulary"] - result["Vocabulary"]).abs()
    result["error_grammar"] = (result["random_forest_grammar"] - result["Grammar"]).abs()
    result["max_rf_absolute_error"] = result[["error_vocabulary", "error_grammar"]].max(axis=1)
    result["large_error"] = result["max_rf_absolute_error"].ge(float(error_threshold))
    result["disagreement_vocabulary"] = (
        result["ridge_vocabulary"] - result["random_forest_vocabulary"]
    ).abs()
    result["disagreement_grammar"] = (
        result["ridge_grammar"] - result["random_forest_grammar"]
    ).abs()
    result["disagreement"] = result[["disagreement_vocabulary", "disagreement_grammar"]].max(axis=1)
    return result


def disagreement_ranking(frame: pd.DataFrame, *, selected_count: int) -> pd.DataFrame:
    """Rank descending by maximum target disagreement, then ascending essay ID."""
    if "disagreement" not in frame.columns:
        raise ValueError("disagreement ranking requires a precomputed disagreement column.")
    if not 0 < selected_count <= len(frame):
        raise ValueError("selected_count must be between 1 and the number of essays.")
    ranked = frame.loc[:, ["essay_id", "disagreement"]].copy()
    ranked["essay_id"] = ranked["essay_id"].astype("string")
    ranked = ranked.sort_values(
        ["disagreement", "essay_id"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    ranked.insert(0, "rank", np.arange(1, len(ranked) + 1))
    ranked["selected"] = ranked["rank"].le(selected_count)
    return ranked


def metrics_for_selected_ids(
    frame: pd.DataFrame, selected_ids: set[str], *, strategy: str
) -> dict[str, float | int | str]:
    """Evaluate one fixed-size selection against the shared large-error labels."""
    selected = frame["essay_id"].astype("string").isin(selected_ids).to_numpy()
    metrics = review_queue_metrics(frame["large_error"].to_numpy(dtype=bool), selected)
    return {"strategy": strategy, **metrics}


def random_reference_draws(
    large_errors: np.ndarray,
    *,
    selected_count: int,
    repetitions: int = 1_000,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Return every uniform-without-replacement random reference draw."""
    error_mask = np.asarray(large_errors, dtype=bool)
    if not 0 < selected_count <= len(error_mask):
        raise ValueError("selected_count must be between 1 and the number of essays.")
    if repetitions < 1:
        raise ValueError("repetitions must be positive.")
    rng = np.random.default_rng(random_seed)
    rows: list[dict[str, float | int]] = []
    for repetition in range(1, repetitions + 1):
        indices = rng.choice(len(error_mask), size=selected_count, replace=False)
        if len(np.unique(indices)) != selected_count:
            raise RuntimeError("Random review selection unexpectedly sampled with replacement.")
        selected = np.zeros(len(error_mask), dtype=bool)
        selected[indices] = True
        rows.append({"repetition": repetition, **review_queue_metrics(error_mask, selected)})
    return pd.DataFrame(rows)

"""Label-free baseline rankings for teacher-review prioritization."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _validate_ranking_frame(frame: pd.DataFrame, required: set[str]) -> pd.DataFrame:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Ranking data are missing columns: {missing}")
    if frame["essay_id"].isna().any() or frame["essay_id"].astype("string").duplicated().any():
        raise ValueError("Ranking requires unique, non-null essay IDs.")
    result = frame.copy()
    result["essay_id"] = result["essay_id"].astype("string")
    return result


def shortest_first(frame: pd.DataFrame, *, selected_count: int) -> pd.DataFrame:
    """Rank essays by ascending word count and then ascending string essay ID."""
    ranked = _validate_ranking_frame(frame, {"essay_id", "word_count"})
    if not 0 < selected_count <= len(ranked):
        raise ValueError("selected_count must be between 1 and the number of essays.")
    words = pd.to_numeric(ranked["word_count"], errors="coerce")
    if words.isna().any() or not np.isfinite(words.to_numpy(dtype=float)).all():
        raise ValueError("word_count must contain finite numeric values.")
    ranked["word_count"] = words
    ranked = ranked.sort_values(
        ["word_count", "essay_id"], ascending=[True, True], kind="stable"
    ).reset_index(drop=True)
    ranked.insert(0, "rank", np.arange(1, len(ranked) + 1))
    ranked["selected"] = ranked["rank"].le(selected_count)
    return ranked


def ridge_extremity(
    frame: pd.DataFrame,
    *,
    median_ridge_vocabulary: float,
    median_ridge_grammar: float,
    selected_count: int,
) -> pd.DataFrame:
    """Rank by raw maximum distance from eligible-train Ridge prediction medians."""
    columns = {"essay_id", "ridge_vocabulary", "ridge_grammar"}
    ranked = _validate_ranking_frame(frame, columns)
    if not 0 < selected_count <= len(ranked):
        raise ValueError("selected_count must be between 1 and the number of essays.")
    prediction_columns = ["ridge_vocabulary", "ridge_grammar"]
    numeric = ranked[prediction_columns].apply(pd.to_numeric, errors="coerce")
    centers = np.asarray([median_ridge_vocabulary, median_ridge_grammar], dtype=float)
    if (
        numeric.isna().any().any()
        or not np.isfinite(numeric.to_numpy(dtype=float)).all()
        or not np.isfinite(centers).all()
    ):
        raise ValueError("Ridge predictions and centers must be finite numeric values.")
    ranked.loc[:, prediction_columns] = numeric
    ranked["ridge_extremity_vocabulary"] = (
        ranked["ridge_vocabulary"] - float(median_ridge_vocabulary)
    ).abs()
    ranked["ridge_extremity_grammar"] = (
        ranked["ridge_grammar"] - float(median_ridge_grammar)
    ).abs()
    ranked["ridge_extremity"] = ranked[
        ["ridge_extremity_vocabulary", "ridge_extremity_grammar"]
    ].max(axis=1)
    ranked = ranked.sort_values(
        ["ridge_extremity", "essay_id"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    ranked.insert(0, "rank", np.arange(1, len(ranked) + 1))
    ranked["selected"] = ranked["rank"].le(selected_count)
    return ranked

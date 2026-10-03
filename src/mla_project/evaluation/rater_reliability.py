"""Human-rater reliability helpers with explicit development-ID allowlisting."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

RATER_COLUMNS = (
    "text_id_kaggle",
    "Vocabulary_1",
    "Vocabulary_2",
    "Grammar_1",
    "Grammar_2",
)


def load_allowlisted_rater_scores(
    path: str | Path,
    allowed_ids: Iterable[str],
    *,
    forbidden_ids: Iterable[str] = (),
    chunksize: int = 1_000,
) -> pd.DataFrame:
    """Retain raw ratings only for an allowlist that is disjoint from forbidden IDs."""
    allowed = {str(value) for value in allowed_ids}
    forbidden = {str(value) for value in forbidden_ids}
    if not allowed:
        raise ValueError("The raw-rater allowlist must not be empty.")
    if allowed.intersection(forbidden):
        raise ValueError("Raw-rater allowlist overlaps forbidden official-test IDs.")

    retained: list[pd.DataFrame] = []
    for chunk in pd.read_csv(
        path,
        usecols=list(RATER_COLUMNS),
        dtype={"text_id_kaggle": "string"},
        chunksize=chunksize,
    ):
        selected = chunk.loc[chunk["text_id_kaggle"].isin(allowed)].copy()
        if not selected.empty:
            retained.append(selected)
    if not retained:
        raise ValueError("No allowlisted development IDs were found in the raw-rater file.")

    result = pd.concat(retained, ignore_index=True).rename(columns={"text_id_kaggle": "essay_id"})
    if result["essay_id"].duplicated().any():
        raise ValueError("Allowlisted raw-rater scores contain duplicate essay IDs.")
    if set(result["essay_id"]).intersection(forbidden):
        raise ValueError("A forbidden official-test ID was retained from the raw-rater file.")
    numeric_columns = list(RATER_COLUMNS[1:])
    numeric = result[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any() or not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("Allowlisted raw-rater scores must be finite numeric values.")
    if not numeric.apply(lambda column: column.between(1, 5)).all().all():
        raise ValueError("Allowlisted Vocabulary and Grammar rater scores must be in [1, 5].")
    result.loc[:, numeric_columns] = numeric
    return result


def absolute_agreement_icc(rater_1: np.ndarray, rater_2: np.ndarray) -> float:
    """Compute ICC(A,1): two-way random-effects, absolute agreement, single rating."""
    ratings = np.column_stack((rater_1, rater_2)).astype(float)
    n_subjects, n_raters = ratings.shape
    if n_subjects < 2:
        return float("nan")
    grand_mean = float(ratings.mean())
    subject_means = ratings.mean(axis=1)
    rater_means = ratings.mean(axis=0)
    ss_subject = n_raters * float(np.square(subject_means - grand_mean).sum())
    ss_rater = n_subjects * float(np.square(rater_means - grand_mean).sum())
    residual = ratings - subject_means[:, None] - rater_means[None, :] + grand_mean
    ss_error = float(np.square(residual).sum())
    ms_subject = ss_subject / (n_subjects - 1)
    ms_rater = ss_rater / (n_raters - 1)
    ms_error = ss_error / ((n_subjects - 1) * (n_raters - 1))
    denominator = (
        ms_subject + (n_raters - 1) * ms_error + n_raters * (ms_rater - ms_error) / n_subjects
    )
    return float((ms_subject - ms_error) / denominator) if denominator else float("nan")


def rater_reliability_metrics(
    frame: pd.DataFrame,
    *,
    rater_1_column: str,
    rater_2_column: str,
) -> dict[str, float | int]:
    """Compute agreement metrics for a pair of complete human ratings."""
    rater_1 = frame[rater_1_column].to_numpy(dtype=float)
    rater_2 = frame[rater_2_column].to_numpy(dtype=float)
    if len(rater_1) == 0:
        raise ValueError("Rater reliability requires at least one paired rating.")
    difference = np.abs(rater_1 - rater_2)
    return {
        "n_samples": len(frame),
        "human_human_mae": float(difference.mean()),
        "exact_agreement_rate": float(np.mean(difference == 0.0)),
        "within_0_5_points_rate": float(np.mean(difference <= 0.5)),
        "within_1_0_point_rate": float(np.mean(difference <= 1.0)),
        "quadratic_weighted_kappa": float(
            cohen_kappa_score(rater_1, rater_2, labels=[1, 2, 3, 4, 5], weights="quadratic")
        ),
        "icc_a_1": absolute_agreement_icc(rater_1, rater_2),
    }


def model_and_rater_comparison(
    frame: pd.DataFrame,
    *,
    target: str,
    prediction_column: str,
) -> dict[str, float | int | str]:
    """Compare a selected model with aggregate and individual human ratings."""
    reliability = rater_reliability_metrics(
        frame,
        rater_1_column=f"{target}_1",
        rater_2_column=f"{target}_2",
    )
    aggregate = frame[target].to_numpy(dtype=float)
    prediction = frame[prediction_column].to_numpy(dtype=float)
    rater_1 = frame[f"{target}_1"].to_numpy(dtype=float)
    rater_2 = frame[f"{target}_2"].to_numpy(dtype=float)
    return {
        "trait": target,
        **reliability,
        "selected_model": "Random Forest",
        "model_aggregate_human_mae": float(np.mean(np.abs(prediction - aggregate))),
        "model_individual_human_mae": float(
            (np.mean(np.abs(prediction - rater_1)) + np.mean(np.abs(prediction - rater_2))) / 2
        ),
        "aggregate_matches_rater_mean_rate": float(
            np.mean(np.isclose(aggregate, (rater_1 + rater_2) / 2, rtol=0.0, atol=1e-12))
        ),
    }

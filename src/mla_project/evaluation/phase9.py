"""Frozen helpers for the one-time official-test evaluation."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from mla_project.features.build_features import FEATURE_NAMES

EXPECTED_TOTAL_ROWS = 2_571
EXPECTED_ELIGIBLE_ROWS = 2_518
PRIMARY_ERROR_THRESHOLD = 1.0
PRIMARY_REVIEW_BUDGET = 0.20
REVIEW_BUDGETS = (0.10, 0.20, 0.30)
ERROR_THRESHOLDS = (0.5, 1.0, 1.5)
RANDOM_SEED = 42
RANDOM_REPETITIONS = 1_000
VALIDATION_DISAGREEMENT_THRESHOLD = 0.133989655155
RIDGE_CENTERS = {
    "median_ridge_vocabulary": 3.26941940240918,
    "median_ridge_grammar": 3.124225726952784,
}
REFERENCE_PREDICTORS = {
    "Vocabulary": "random_forest_vocabulary",
    "Grammar": "random_forest_grammar",
}


def prepare_official_population(
    features: pd.DataFrame, labels: pd.DataFrame, manifest: pd.DataFrame
) -> pd.DataFrame:
    """Validate and return the frozen privacy-eligible official-test population."""
    feature_required = {"essay_id", *FEATURE_NAMES}
    label_required = {"essay_id", "Vocabulary", "Grammar", "gender", "race_ethnicity", "SES"}
    manifest_required = {"essay_id", "split", "privacy_review_status"}
    for table, required, name in (
        (features, feature_required, "official-test features"),
        (labels, label_required, "official-test labels"),
        (manifest, manifest_required, "split manifest"),
    ):
        missing = sorted(required.difference(table.columns))
        if missing:
            raise ValueError(f"{name} are missing columns: {missing}")
        if table["essay_id"].isna().any() or table["essay_id"].astype("string").duplicated().any():
            raise ValueError(f"{name} must have unique, non-null essay IDs.")

    feature_ids = set(features["essay_id"].astype(str))
    label_ids = set(labels["essay_id"].astype(str))
    official_manifest = manifest.loc[manifest["split"].eq("official_test")].copy()
    manifest_ids = set(official_manifest["essay_id"].astype(str))
    if not (
        len(features) == len(labels) == len(official_manifest) == EXPECTED_TOTAL_ROWS
        and feature_ids == label_ids == manifest_ids
    ):
        raise ValueError("Official-test sources do not match the frozen 2,571-ID population.")
    eligible_manifest = official_manifest.loc[
        official_manifest["privacy_review_status"].eq("not_flagged"), ["essay_id"]
    ]
    if len(eligible_manifest) != EXPECTED_ELIGIBLE_ROWS:
        raise ValueError("Official-test privacy gate did not produce exactly 2,518 essays.")

    selected_features = features.loc[:, ["essay_id", *FEATURE_NAMES]].copy()
    selected_features["essay_id"] = selected_features["essay_id"].astype("string")
    selected_labels = labels.loc[:, list(label_required)].copy()
    selected_labels["essay_id"] = selected_labels["essay_id"].astype("string")
    eligible_manifest["essay_id"] = eligible_manifest["essay_id"].astype("string")
    frame = eligible_manifest.merge(
        selected_features, on="essay_id", how="left", validate="one_to_one"
    ).merge(selected_labels, on="essay_id", how="left", validate="one_to_one")
    numeric_columns = [*FEATURE_NAMES, "Vocabulary", "Grammar"]
    numeric = frame[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any() or not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("Official-test features and labels must be complete finite values.")
    if (
        not numeric[["Vocabulary", "Grammar"]]
        .apply(lambda column: column.between(1.0, 5.0))
        .all()
        .all()
    ):
        raise ValueError("Official-test labels must remain in [1.0, 5.0].")
    frame.loc[:, numeric_columns] = numeric
    return frame


def add_frozen_test_signals(
    frame: pd.DataFrame, *, error_threshold: float = PRIMARY_ERROR_THRESHOLD
) -> pd.DataFrame:
    """Add RF-reference errors and label-free disagreement under frozen definitions."""
    result = frame.copy()
    result["error_vocabulary"] = (result["random_forest_vocabulary"] - result["Vocabulary"]).abs()
    result["error_grammar"] = (result["random_forest_grammar"] - result["Grammar"]).abs()
    result["max_rf_absolute_error"] = result[["error_vocabulary", "error_grammar"]].max(axis=1)
    result["large_error"] = result["max_rf_absolute_error"].ge(error_threshold)
    result["disagreement_vocabulary"] = (
        result["ridge_vocabulary"] - result["random_forest_vocabulary"]
    ).abs()
    result["disagreement_grammar"] = (
        result["ridge_grammar"] - result["random_forest_grammar"]
    ).abs()
    result["disagreement"] = result[["disagreement_vocabulary", "disagreement_grammar"]].max(axis=1)
    return result


def primary_review_count(population_size: int = EXPECTED_ELIGIBLE_ROWS) -> int:
    """Return the frozen ceiling-sized 20% queue."""
    return math.ceil(PRIMARY_REVIEW_BUDGET * population_size)


def classify_confirmatory_evidence(
    *, disagreement: float, random_mean: float, shortest: float, ridge_extremity: float
) -> str:
    """Apply a predeclared qualitative classification to capture-rate evidence."""
    if disagreement > max(random_mean, shortest, ridge_extremity):
        return "A. Supports added value of disagreement"
    if disagreement < min(random_mean, shortest, ridge_extremity):
        return "C. Worse than simpler baselines"
    if disagreement >= random_mean and min(shortest, ridge_extremity) <= disagreement <= max(
        shortest, ridge_extremity
    ):
        return "B. Comparable to simpler baselines"
    return "D. Mixed / inconclusive"

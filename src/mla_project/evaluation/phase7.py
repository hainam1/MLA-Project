"""Pure validation-evaluation helpers for Phase 7."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from mla_project.evaluation.regression_metrics import regression_metrics

TARGETS = ("Vocabulary", "Grammar")
MODEL_COLUMNS = {
    "Vocabulary": {
        "Ridge": "ridge_vocabulary",
        "Random Forest": "random_forest_vocabulary",
    },
    "Grammar": {
        "Ridge": "ridge_grammar",
        "Random Forest": "random_forest_grammar",
    },
}
PREDICTION_COLUMNS = (
    "essay_id",
    "Vocabulary",
    "Grammar",
    "ridge_vocabulary",
    "ridge_grammar",
    "random_forest_vocabulary",
    "random_forest_grammar",
)
PHASE6_PREDICTION_COLUMNS = (
    "essay_id",
    "ridge_vocabulary",
    "ridge_grammar",
    "random_forest_vocabulary",
    "random_forest_grammar",
)
POINT_TIE_ATOL = 1e-12
BASELINE_COMPARISONS = (
    ("mean", "train_mean"),
    ("length_ridge", "length_only_ridge"),
    ("length_random_forest", "length_only_random_forest"),
    ("length_consensus", "length_only_consensus"),
)


def validate_and_join_predictions(
    validation_labels: pd.DataFrame,
    phase6_predictions: pd.DataFrame,
    *,
    expected_ids: Iterable[str],
) -> pd.DataFrame:
    """Join text-free predictions to labels after strict ID/schema checks."""
    required_labels = {"essay_id", *TARGETS}
    missing_labels = sorted(required_labels.difference(validation_labels.columns))
    if missing_labels:
        raise ValueError(f"Validation labels are missing columns: {missing_labels}")
    missing_predictions = sorted(
        set(PHASE6_PREDICTION_COLUMNS).difference(phase6_predictions.columns)
    )
    if missing_predictions:
        raise ValueError(f"Phase 6 predictions are missing columns: {missing_predictions}")
    predictions = phase6_predictions.loc[:, list(PHASE6_PREDICTION_COLUMNS)].copy()
    labels = validation_labels.loc[:, ["essay_id", *TARGETS]].copy()
    predictions["essay_id"] = predictions["essay_id"].astype("string")
    labels["essay_id"] = labels["essay_id"].astype("string")
    expected = {str(essay_id) for essay_id in expected_ids}
    prediction_ids = set(predictions["essay_id"])
    label_ids = set(labels["essay_id"])
    if predictions["essay_id"].duplicated().any():
        raise ValueError("Phase 6 validation predictions contain duplicate essay IDs.")
    if labels["essay_id"].duplicated().any():
        raise ValueError("Validation labels contain duplicate essay IDs.")
    if prediction_ids != expected:
        raise ValueError("Phase 6 prediction IDs do not exactly match eligible validation IDs.")
    if label_ids != expected:
        raise ValueError("Validation label IDs do not exactly match eligible validation IDs.")
    joined = labels.merge(predictions, on="essay_id", how="inner", validate="one_to_one")
    if len(joined) != len(expected):
        raise ValueError("Validation label/prediction join changed the eligible population.")
    numeric_columns = [*TARGETS, *PHASE6_PREDICTION_COLUMNS[1:]]
    numeric = joined[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any() or not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("Validation labels and predictions must be finite numeric values.")
    joined.loc[:, numeric_columns] = numeric
    return joined


def regression_metrics_table(joined: pd.DataFrame) -> pd.DataFrame:
    """Compute MAE, RMSE, and R-squared separately for every model and target."""
    rows: list[dict[str, object]] = []
    for target, model_columns in MODEL_COLUMNS.items():
        y_true = joined[target].to_numpy(dtype=float)
        for family, column in model_columns.items():
            metrics = regression_metrics(y_true, joined[column].to_numpy(dtype=float))
            rows.append(
                {
                    "model": family,
                    "target": target,
                    "prediction_column": column,
                    "n_samples": len(joined),
                    **metrics,
                }
            )
    return pd.DataFrame(rows)


def scorer_distribution_table(joined: pd.DataFrame) -> pd.DataFrame:
    """Summarize human scores and both machine scorers on the same population."""
    rows: list[dict[str, object]] = []
    for target, model_columns in MODEL_COLUMNS.items():
        scorers = {"Human": target, **model_columns}
        for scorer, column in scorers.items():
            values = joined[column].to_numpy(dtype=float)
            rows.append(
                {
                    "target": target,
                    "scorer": scorer,
                    "score_type": "reference" if scorer == "Human" else "prediction",
                    "n_samples": len(values),
                    "mean": float(np.mean(values)),
                    "standard_deviation": float(np.std(values, ddof=1)),
                    "minimum": float(np.min(values)),
                    "q25": float(np.quantile(values, 0.25)),
                    "median": float(np.median(values)),
                    "q75": float(np.quantile(values, 0.75)),
                    "maximum": float(np.max(values)),
                }
            )
    return pd.DataFrame(rows)


def machine_by_human_score_table(joined: pd.DataFrame) -> pd.DataFrame:
    """Compare each machine scorer with the human reference at every observed score."""
    rows: list[dict[str, object]] = []
    for target, model_columns in MODEL_COLUMNS.items():
        for model, column in model_columns.items():
            actual = joined[target].to_numpy(dtype=float)
            prediction = joined[column].to_numpy(dtype=float)
            for human_score in np.sort(np.unique(actual)):
                mask = actual == human_score
                group_predictions = prediction[mask]
                residuals = group_predictions - human_score
                absolute_errors = np.abs(residuals)
                rows.append(
                    {
                        "target": target,
                        "model": model,
                        "human_score": float(human_score),
                        "n_samples": int(mask.sum()),
                        "mean_machine_score": float(np.mean(group_predictions)),
                        "standard_deviation_machine_score": (
                            float(np.std(group_predictions, ddof=1))
                            if len(group_predictions) > 1
                            else np.nan
                        ),
                        "mean_difference_machine_minus_human": float(np.mean(residuals)),
                        "mae": float(np.mean(absolute_errors)),
                        "within_0_5_points_rate": float(np.mean(absolute_errors <= 0.5)),
                        "within_1_0_point_rate": float(np.mean(absolute_errors <= 1.0)),
                    }
                )
    return pd.DataFrame(rows)


def choose_point_predictors(
    metrics: pd.DataFrame, *, tie_atol: float = POINT_TIE_ATOL
) -> pd.DataFrame:
    """Select one validation point predictor per target, preferring Ridge on a tie."""
    rows: list[dict[str, object]] = []
    for target in TARGETS:
        subset = metrics.loc[metrics["target"].eq(target)].set_index("model")
        ridge_mae = float(subset.loc["Ridge", "mae"])
        forest_mae = float(subset.loc["Random Forest", "mae"])
        tie = bool(np.isclose(ridge_mae, forest_mae, rtol=0.0, atol=tie_atol))
        selected = "Ridge" if tie or ridge_mae < forest_mae else "Random Forest"
        rows.append(
            {
                "target": target,
                "ridge_mae": ridge_mae,
                "random_forest_mae": forest_mae,
                "mae_difference_ridge_minus_random_forest": ridge_mae - forest_mae,
                "selected_model": selected,
                "selected_prediction_column": MODEL_COLUMNS[target][selected],
                "tie_within_atol": tie,
                "tie_atol": tie_atol,
                "selection_rule": "Lower validation MAE; Ridge on tie.",
            }
        )
    return pd.DataFrame(rows)


def baseline_comparison_table(
    full_feature_metrics: pd.DataFrame, baseline_metrics: pd.DataFrame
) -> pd.DataFrame:
    """Compare each full-feature model with all available frozen Phase 5 baselines."""
    baseline_lookup = baseline_metrics.set_index(["baseline", "target"])
    rows: list[dict[str, object]] = []
    for row in full_feature_metrics.to_dict(orient="records"):
        for baseline_name, label in BASELINE_COMPARISONS:
            key = (baseline_name, row["target"])
            if key not in baseline_lookup.index:
                raise ValueError(f"Missing Phase 5 baseline: {baseline_name}/{row['target']}")
            baseline_mae = float(baseline_lookup.loc[key, "mae"])
            model_mae = float(row["mae"])
            rows.append(
                {
                    "model": row["model"],
                    "target": row["target"],
                    "n_samples": row["n_samples"],
                    "baseline": label,
                    "baseline_mae": baseline_mae,
                    "full_feature_mae": model_mae,
                    "mae_difference_baseline_minus_full": baseline_mae - model_mae,
                    "mae_improvement_pct": (baseline_mae - model_mae) / baseline_mae * 100.0,
                }
            )
    return pd.DataFrame(rows)


def error_table(joined: pd.DataFrame) -> pd.DataFrame:
    """Return one text-free residual row per essay/model/target."""
    rows: list[dict[str, object]] = []
    for target, model_columns in MODEL_COLUMNS.items():
        for model, column in model_columns.items():
            residual = joined[column].to_numpy(dtype=float) - joined[target].to_numpy(dtype=float)
            rows.extend(
                {
                    "essay_id": essay_id,
                    "model": model,
                    "target": target,
                    "actual": float(actual),
                    "prediction": float(prediction),
                    "residual": float(error),
                    "absolute_error": float(abs(error)),
                }
                for essay_id, actual, prediction, error in zip(
                    joined["essay_id"],
                    joined[target],
                    joined[column],
                    residual,
                    strict=True,
                )
            )
    return pd.DataFrame(rows)

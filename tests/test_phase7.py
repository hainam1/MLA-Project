from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mla_project.evaluation.phase7 import (
    PREDICTION_COLUMNS,
    baseline_comparison_table,
    choose_point_predictors,
    error_table,
    machine_by_human_score_table,
    regression_metrics_table,
    scorer_distribution_table,
    validate_and_join_predictions,
)


def toy_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    labels = pd.DataFrame(
        {
            "essay_id": ["e1", "e2", "e3"],
            "Vocabulary": [2.0, 3.0, 4.0],
            "Grammar": [2.5, 3.5, 4.5],
        }
    )
    predictions = pd.DataFrame(
        {
            "essay_id": ["e1", "e2", "e3"],
            "ridge_vocabulary": [2.0, 3.5, 3.5],
            "ridge_grammar": [2.5, 3.0, 4.0],
            "random_forest_vocabulary": [2.5, 3.0, 4.0],
            "random_forest_grammar": [2.0, 3.5, 4.5],
        }
    )
    return labels, predictions


def test_phase7_join_and_metrics_are_target_separate():
    labels, predictions = toy_frames()
    joined = validate_and_join_predictions(labels, predictions, expected_ids=labels["essay_id"])
    assert list(predictions.columns) == list(PREDICTION_COLUMNS[:1]) + list(PREDICTION_COLUMNS[3:])
    metrics = regression_metrics_table(joined)
    assert set(metrics["target"]) == {"Vocabulary", "Grammar"}
    assert set(metrics["model"]) == {"Ridge", "Random Forest"}
    ridge_vocabulary = metrics.loc[metrics["prediction_column"].eq("ridge_vocabulary"), "mae"].iloc[
        0
    ]
    assert ridge_vocabulary == pytest.approx(1 / 3)


def test_phase7_point_predictor_prefers_ridge_on_tie():
    metrics = pd.DataFrame(
        {
            "model": ["Ridge", "Random Forest", "Ridge", "Random Forest"],
            "target": ["Vocabulary", "Vocabulary", "Grammar", "Grammar"],
            "mae": [0.4, 0.4 + 5e-13, 0.3, 0.2],
        }
    )
    selected = choose_point_predictors(metrics)
    assert dict(zip(selected["target"], selected["selected_model"], strict=True)) == {
        "Vocabulary": "Ridge",
        "Grammar": "Random Forest",
    }
    assert bool(selected.loc[selected["target"].eq("Vocabulary"), "tie_within_atol"].iloc[0])


def test_phase7_baseline_comparison_reports_signed_improvement():
    full = pd.DataFrame(
        {
            "model": ["Ridge", "Random Forest"],
            "target": ["Vocabulary", "Grammar"],
            "n_samples": [3, 3],
            "mae": [0.3, 0.6],
        }
    )
    baselines = pd.DataFrame(
        {
            "baseline": [
                "mean",
                "length_ridge",
                "length_random_forest",
                "length_consensus",
                "mean",
                "length_ridge",
                "length_random_forest",
                "length_consensus",
            ],
            "target": ["Vocabulary"] * 4 + ["Grammar"] * 4,
            "mae": [0.5, 0.4, 0.45, 0.42, 0.5, 0.55, 0.65, 0.57],
        }
    )
    comparison = baseline_comparison_table(full, baselines)
    assert set(comparison["baseline"]) == {
        "train_mean",
        "length_only_ridge",
        "length_only_random_forest",
        "length_only_consensus",
    }
    ridge_mean = comparison.loc[
        comparison["baseline"].eq("train_mean") & comparison["target"].eq("Vocabulary")
    ].iloc[0]
    assert ridge_mean["mae_improvement_pct"] == pytest.approx(40.0)
    forest_mean = comparison.loc[
        comparison["baseline"].eq("train_mean") & comparison["target"].eq("Grammar")
    ].iloc[0]
    assert forest_mean["mae_improvement_pct"] == pytest.approx(-20.0)


def test_phase7_rejects_missing_or_duplicate_ids():
    labels, predictions = toy_frames()
    predictions.loc[1, "essay_id"] = "e1"
    with pytest.raises(ValueError, match="duplicate essay IDs"):
        validate_and_join_predictions(labels, predictions, expected_ids=labels["essay_id"])


def test_phase7_error_table_has_four_rows_per_essay():
    labels, predictions = toy_frames()
    joined = validate_and_join_predictions(labels, predictions, expected_ids=labels["essay_id"])
    errors = error_table(joined)
    assert len(errors) == 12
    assert set(errors["target"]) == {"Vocabulary", "Grammar"}
    assert np.isfinite(errors["absolute_error"]).all()


def test_phase7_scorer_distribution_compares_human_and_both_models():
    labels, predictions = toy_frames()
    joined = validate_and_join_predictions(labels, predictions, expected_ids=labels["essay_id"])
    summary = scorer_distribution_table(joined)
    assert len(summary) == 6
    assert set(summary["scorer"]) == {"Human", "Ridge", "Random Forest"}
    human_vocabulary = summary.loc[
        summary["target"].eq("Vocabulary") & summary["scorer"].eq("Human")
    ].iloc[0]
    assert human_vocabulary["mean"] == pytest.approx(3.0)
    assert human_vocabulary["minimum"] == pytest.approx(2.0)
    assert human_vocabulary["maximum"] == pytest.approx(4.0)


def test_phase7_machine_by_human_score_reports_bias_and_tolerance_rates():
    labels, predictions = toy_frames()
    joined = validate_and_join_predictions(labels, predictions, expected_ids=labels["essay_id"])
    comparison = machine_by_human_score_table(joined)
    row = comparison.loc[
        comparison["target"].eq("Vocabulary")
        & comparison["model"].eq("Random Forest")
        & comparison["human_score"].eq(2.0)
    ].iloc[0]
    assert row["n_samples"] == 1
    assert row["mean_machine_score"] == pytest.approx(2.5)
    assert row["mean_difference_machine_minus_human"] == pytest.approx(0.5)
    assert row["mae"] == pytest.approx(0.5)
    assert row["within_0_5_points_rate"] == pytest.approx(1.0)
    assert row["within_1_0_point_rate"] == pytest.approx(1.0)
    assert np.isnan(row["standard_deviation_machine_score"])

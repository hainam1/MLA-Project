import numpy as np

from mla_project.evaluation.regression_metrics import model_qwk, qwk_scores, regression_metrics
from mla_project.evaluation.review_metrics import (
    random_review_distribution,
    review_queue_metrics,
)


def test_regression_metrics_use_mae_rmse_and_r2():
    metrics = regression_metrics(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 4.0]))
    assert set(metrics) == {"mae", "rmse", "r2", "qwk"}
    assert metrics["mae"] == 1 / 3
    assert metrics["rmse"] > metrics["mae"]


def test_qwk_uses_half_up_rounding_clipping_and_fixed_half_point_grid():
    predictions = np.array([0.0, 1.24, 1.25, 1.74, 1.75, 4.74, 4.75, 5.8])
    assert qwk_scores(predictions).tolist() == [1.0, 1.0, 1.5, 1.5, 2.0, 4.5, 5.0, 5.0]
    levels = np.arange(1.0, 5.01, 0.5)
    assert model_qwk(levels, levels) == 1.0


def test_review_queue_metrics_and_seeded_random_baseline():
    large_errors = np.array([True, False, True, False, False])
    selected = np.array([True, True, False, False, False])

    metrics = review_queue_metrics(large_errors, selected)
    assert metrics["captured_count"] == 1
    assert metrics["capture_rate"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["lift"] == 1.25

    first = random_review_distribution(
        large_errors, selected_count=2, repetitions=20, random_seed=42
    )
    second = random_review_distribution(
        large_errors, selected_count=2, repetitions=20, random_seed=42
    )
    assert first == second
    assert first["repetitions"] == 20


def test_random_review_handles_no_large_errors_without_runtime_warning():
    result = random_review_distribution(
        np.zeros(5, dtype=bool), selected_count=2, repetitions=5, random_seed=42
    )
    assert np.isnan(result["capture_rate_mean"])
    assert np.isnan(result["lift_mean"])
    assert result["precision_mean"] == 0.0

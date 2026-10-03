from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mla_project.evaluation.rater_reliability import (
    absolute_agreement_icc,
    model_and_rater_comparison,
    rater_reliability_metrics,
)


def test_perfect_rater_agreement_has_unit_reliability():
    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    frame = pd.DataFrame({"a": values, "b": values})
    metrics = rater_reliability_metrics(frame, rater_1_column="a", rater_2_column="b")
    assert metrics["human_human_mae"] == 0.0
    assert metrics["exact_agreement_rate"] == 1.0
    assert metrics["quadratic_weighted_kappa"] == pytest.approx(1.0)
    assert metrics["icc_a_1"] == pytest.approx(1.0)


def test_absolute_agreement_icc_penalizes_a_systematic_rater_shift():
    left = np.array([1.0, 2.0, 3.0, 4.0])
    right = left + 1.0
    assert absolute_agreement_icc(left, right) < 1.0


def test_model_comparison_distinguishes_aggregate_and_individual_humans():
    frame = pd.DataFrame(
        {
            "Vocabulary": [2.5, 3.5],
            "Vocabulary_1": [2.0, 3.0],
            "Vocabulary_2": [3.0, 4.0],
            "prediction": [2.5, 3.5],
        }
    )
    result = model_and_rater_comparison(frame, target="Vocabulary", prediction_column="prediction")
    assert result["human_human_mae"] == pytest.approx(1.0)
    assert result["model_aggregate_human_mae"] == pytest.approx(0.0)
    assert result["model_individual_human_mae"] == pytest.approx(0.5)
    assert result["aggregate_matches_rater_mean_rate"] == pytest.approx(1.0)

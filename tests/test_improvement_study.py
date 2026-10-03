from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mla_project.evaluation.improvement_study import (
    acceptance_table,
    band_metrics,
    inverse_sqrt_band_weights,
    overall_metrics,
    score_bands,
)


def test_score_bands_follow_predeclared_boundaries():
    scores = np.array([1.0, 2.5, 3.0, 3.5, 4.0, 5.0])
    assert score_bands(scores).tolist() == ["low", "low", "middle", "middle", "high", "high"]


def test_inverse_sqrt_weights_are_mean_one_and_upweight_rare_bands():
    scores = np.array([2.0, 3.0, 3.0, 3.5, 3.5, 4.0])
    weights = inverse_sqrt_band_weights(scores)
    assert weights.mean() == pytest.approx(1.0)
    assert weights[0] > weights[1]


def test_metrics_expose_tail_bias_and_calibration():
    actual = np.array([2.0, 2.5, 3.0, 3.5, 4.0, 4.5])
    predicted = np.array([2.5, 2.8, 3.0, 3.4, 3.7, 4.0])
    overall = overall_metrics(actual, predicted)
    groups = band_metrics(actual, predicted).set_index("score_band")
    assert overall["mae"] > 0
    assert groups.loc["low", "signed_bias"] > 0
    assert groups.loc["high", "signed_bias"] < 0


def test_acceptance_requires_every_rule():
    overall = pd.DataFrame(
        {
            "target": ["Vocabulary", "Vocabulary"],
            "variant": ["rf_baseline", "challenger"],
            "mae": [0.40, 0.39],
        }
    )
    bands = pd.DataFrame(
        [
            {
                "target": "Vocabulary",
                "variant": variant,
                "score_band": band,
                "mae": mae,
                "signed_bias": bias,
            }
            for variant, values in {
                "rf_baseline": [("low", 0.6, 0.5), ("middle", 0.2, 0.0), ("high", 0.7, -0.6)],
                "challenger": [("low", 0.5, 0.4), ("middle", 0.2, 0.0), ("high", 0.55, -0.45)],
            }.items()
            for band, mae, bias in values
        ]
    )
    folds = pd.DataFrame(
        [
            {"target": "Vocabulary", "variant": variant, "fold": fold, "mae": value}
            for variant, value in (("rf_baseline", 0.40), ("challenger", 0.39))
            for fold in range(5)
        ]
    )
    result = acceptance_table(overall, bands, folds).iloc[0]
    assert bool(result["all_acceptance_rules_pass"])

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from mla_project.evaluation.phase8b import (
    assign_error_quadrants,
    fairness_table,
    summarize_by_human_score,
    summarize_error_groups,
)


def analysis_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "essay_id": ["a", "b", "c", "d"],
            "disagreement": [0.1, 0.2, 0.3, 0.4],
            "large_error": [True, False, True, False],
            "max_rf_absolute_error": [1.2, 0.4, 1.1, 0.2],
            "word_count": [100, 200, 300, 400],
            "Vocabulary": [2.0, 2.0, 4.0, 4.0],
            "Grammar": [2.5, 3.0, 3.5, 4.0],
            "random_forest_vocabulary": [3.2, 2.2, 3.0, 4.1],
            "random_forest_grammar": [2.7, 2.6, 3.6, 3.8],
            "error_vocabulary": [1.2, 0.2, 1.0, 0.1],
            "error_grammar": [0.2, 0.4, 0.1, 0.2],
            "gender": ["F", "F", "M", "M"],
            "race_ethnicity": ["A", "A", "B", "B"],
            "SES": ["low", "high", "low", "high"],
            "disagreement_selected": [False, False, True, True],
            "shortest_selected": [True, True, False, False],
        }
    )


def test_quadrants_use_inclusive_validation_median_threshold():
    result, threshold = assign_error_quadrants(analysis_frame())
    assert threshold == pytest.approx(0.25)
    assert result["error_quadrant"].tolist() == [
        "Low disagreement + Large error",
        "Low disagreement + No large error",
        "High disagreement + Large error",
        "High disagreement + No large error",
    ]


def test_quadrant_summary_has_counts_percentages_directions_and_score_distributions():
    result, _ = assign_error_quadrants(analysis_frame())
    summary = summarize_error_groups(result, ["error_quadrant"], include_score_distributions=True)
    assert summary["n"].sum() == 4
    assert summary["percentage"].sum() == pytest.approx(100.0)
    shared = summary.loc[summary["error_quadrant"].eq("Low disagreement + Large error")].iloc[0]
    assert shared["large_error_count"] == 1
    assert json.loads(shared["vocabulary_human_score_distribution"]) == {"2": 1}
    assert shared["vocabulary_overprediction_rate"] == 1.0


def test_score_summary_preserves_overprediction_and_underprediction_direction():
    summary = summarize_by_human_score(analysis_frame())
    vocabulary_two = summary.loc[
        summary["target"].eq("Vocabulary") & summary["human_score"].eq(2.0)
    ].iloc[0]
    assert vocabulary_two["n"] == 2
    assert vocabulary_two["overprediction_rate"] == 1.0
    vocabulary_four = summary.loc[
        summary["target"].eq("Vocabulary") & summary["human_score"].eq(4.0)
    ].iloc[0]
    assert vocabulary_four["overprediction_rate"] == 0.5
    assert vocabulary_four["underprediction_rate"] == 0.5


def test_fairness_metrics_use_within_group_denominators_and_flag_small_groups():
    table = fairness_table(analysis_frame(), selected_count=2)
    female = table.loc[table["attribute"].eq("gender") & table["group"].eq("F")].iloc[0]
    assert female["n"] == 2
    assert female["large_error_prevalence"] == 0.5
    assert female["disagreement_selection_rate"] == 0.0
    assert female["within_group_capture_rate"] == 0.0
    assert female["shortest_first_selection_rate"] == 1.0
    assert female["random_expected_selection_rate"] == 0.5
    assert bool(female["small_n_flag"])


def test_fairness_capture_is_na_when_a_group_has_no_large_errors():
    frame = analysis_frame()
    frame.loc[frame["gender"].eq("F"), "large_error"] = False
    table = fairness_table(frame, selected_count=2)
    female = table.loc[table["attribute"].eq("gender") & table["group"].eq("F")].iloc[0]
    assert np.isnan(female["within_group_capture_rate"])

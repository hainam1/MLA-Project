from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mla_project.evaluation.phase8 import (
    add_review_signals,
    disagreement_ranking,
    metrics_for_selected_ids,
    random_reference_draws,
    review_count,
    validate_phase8_frame,
)
from mla_project.review.baselines import ridge_extremity, shortest_first


def phase8_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "essay_id": ["b", "a", "c", "d", "e"],
            "split": ["validation"] * 5,
            "word_count": [10, 10, 5, 20, 15],
            "Vocabulary": [3.0, 3.0, 3.0, 3.0, 3.0],
            "Grammar": [3.0, 3.0, 3.0, 3.0, 3.0],
            "ridge_vocabulary": [3.5, 2.5, 4.0, 3.0, 3.0],
            "ridge_grammar": [3.0, 3.5, 3.0, 2.0, 3.0],
            "random_forest_vocabulary": [4.0, 3.0, 3.0, 3.0, 3.0],
            "random_forest_grammar": [3.0, 3.0, 3.0, 2.0, 3.0],
        }
    )


def test_shortest_first_direction_tie_break_and_no_target_requirement():
    label_free = phase8_frame()[["essay_id", "word_count"]]
    ranked = shortest_first(label_free, selected_count=3)
    assert ranked["essay_id"].tolist()[:3] == ["c", "a", "b"]
    assert ranked.loc[ranked["selected"], "essay_id"].tolist() == ["c", "a", "b"]


def test_ridge_extremity_direction_tie_break_and_no_target_requirement():
    label_free = phase8_frame()[["essay_id", "ridge_vocabulary", "ridge_grammar"]]
    ranked = ridge_extremity(
        label_free,
        median_ridge_vocabulary=3.0,
        median_ridge_grammar=3.0,
        selected_count=2,
    )
    assert ranked["essay_id"].tolist()[:2] == ["c", "d"]
    assert ranked["ridge_extremity"].tolist()[:2] == [1.0, 1.0]


def test_disagreement_direction_and_deterministic_tie_break():
    signals = add_review_signals(phase8_frame())
    label_free = signals[["essay_id", "disagreement"]]
    ranked = disagreement_ranking(label_free, selected_count=2)
    assert ranked["essay_id"].tolist()[:2] == ["c", "a"]
    assert ranked["disagreement"].tolist()[:2] == [1.0, 0.5]


def test_review_count_uses_ceiling_for_frozen_validation_population():
    assert review_count(762, 0.20) == 153


def test_large_error_includes_exactly_one_point_and_uses_rf_only():
    signals = add_review_signals(phase8_frame(), error_threshold=1.0).set_index("essay_id")
    assert bool(signals.loc["b", "large_error"])
    assert bool(signals.loc["d", "large_error"])
    assert not bool(signals.loc["c", "large_error"])


def test_review_metric_denominators_are_total_errors_queue_size_and_prevalence():
    signals = add_review_signals(phase8_frame(), error_threshold=1.0)
    metrics = metrics_for_selected_ids(signals, {"b", "a"}, strategy="test")
    assert metrics["large_error_count"] == 2
    assert metrics["captured_count"] == 1
    assert metrics["capture_rate"] == pytest.approx(1 / 2)
    assert metrics["precision"] == pytest.approx(1 / 2)
    assert metrics["large_error_prevalence"] == pytest.approx(2 / 5)
    assert metrics["lift"] == pytest.approx(1.25)


def test_random_reference_is_seeded_fixed_size_and_without_replacement():
    errors = np.array([True, True, False, False, False])
    first = random_reference_draws(errors, selected_count=3, repetitions=25, random_seed=42)
    second = random_reference_draws(errors, selected_count=3, repetitions=25, random_seed=42)
    pd.testing.assert_frame_equal(first, second)
    assert first["selected_count"].eq(3).all()
    assert first["captured_count"].le(2).all()
    assert first["captured_count"].le(first["selected_count"]).all()


def test_phase8_forbids_official_test_rows():
    frame = phase8_frame()
    frame.loc[0, "split"] = "official_test"
    with pytest.raises(ValueError, match="validation only"):
        validate_phase8_frame(frame)

"""Guard the new supplementary population boundary and max/mean comparison."""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location(
    "post_midterm_teacher_analysis",
    Path(__file__).resolve().parents[1] / "scripts/post_midterm_teacher_analysis.py",
)
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def population():
    return pd.DataFrame(
        {
            "essay_id": ["a", "b"],
            "split": ["validation"] * 2,
            "privacy_review_status": ["not_flagged"] * 2,
            "Vocabulary": [3.0, 3.0],
            "Grammar": [3.0, 3.0],
            "random_forest_vocabulary": [4.0, 3.0],
            "random_forest_grammar": [3.0, 3.0],
            "ridge_vocabulary": [4.8, 3.6],
            "ridge_grammar": [3.0, 3.6],
        }
    )


def test_max_mean_use_same_rf_error_labels_but_can_select_different_essays():
    signals = analysis.validation_signals(population())
    assert signals.large_error.tolist() == [True, False]  # RF threshold is inclusive
    assert analysis.top_ids(signals, "D_max") == {"a"}
    assert analysis.top_ids(signals, "D_mean") == {"b"}
    assert signals.D_max.tolist() == pytest.approx([0.8, 0.6])
    assert signals.D_mean.tolist() == pytest.approx([0.4, 0.6])


@pytest.mark.parametrize("split", ["official_test", "model_train"])
def test_supplementary_error_analysis_rejects_other_splits(split):
    frame = population()
    frame.loc[0, "split"] = split
    with pytest.raises(ValueError, match="Validation only"):
        analysis.validation_signals(frame)


def test_supplementary_error_analysis_rejects_privacy_flagged_rows():
    frame = population()
    frame.loc[0, "privacy_review_status"] = "flagged_by_rater"
    with pytest.raises(ValueError, match="privacy-eligible"):
        analysis.validation_signals(frame)


def test_supplementary_ties_and_ceiling_do_not_use_input_order():
    frame = pd.DataFrame({"essay_id": ["2", "10", "a"], "score": [1.0, 1.0, 0.0]})
    assert analysis.top_ids(frame, "score") == {"10"}
    assert analysis.top_ids(frame.iloc[::-1], "score") == {"10"}

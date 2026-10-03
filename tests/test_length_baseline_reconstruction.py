from __future__ import annotations

import pandas as pd
import pytest

from mla_project.models.length_baselines import (
    FROZEN_FOREST_PARAMETERS,
    FROZEN_RIDGE_ALPHA,
    LENGTH_FEATURES,
    reconstruct_length_models,
)


def test_reconstruction_specification_is_frozen():
    assert LENGTH_FEATURES == ("word_count", "sentence_count", "mean_sentence_length")
    assert FROZEN_RIDGE_ALPHA == 1.0
    assert FROZEN_FOREST_PARAMETERS == {
        "n_estimators": 300,
        "max_depth": None,
        "min_samples_leaf": 2,
        "max_features": "sqrt",
        "random_state": 42,
        "n_jobs": 1,
    }


def test_reconstruction_rejects_any_population_other_than_3050_model_train_rows():
    frame = pd.DataFrame(
        {
            "essay_id": ["x"],
            "split": ["validation"],
            "word_count": [100],
            "sentence_count": [5],
            "mean_sentence_length": [20.0],
            "Vocabulary": [3.0],
            "Grammar": [3.0],
        }
    )
    with pytest.raises(ValueError, match="exactly 3,050"):
        reconstruct_length_models(frame)

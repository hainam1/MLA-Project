import json

import joblib
import pandas as pd
import pytest

from src.features import SENTENCE_FEATURE_COLUMNS, WORD_FEATURE_COLUMNS

pytestmark = pytest.mark.integration


def test_calibration_preserves_base_predictions():
    specs = [
        (
            "src/models/cefr_word_classifier",
            "data/processed/model2a_word_cefr_test.csv",
            WORD_FEATURE_COLUMNS,
        ),
        (
            "src/models/cefr_sentence_classifier",
            "data/processed/model2b_sentence_cefr_test.csv",
            SENTENCE_FEATURE_COLUMNS,
        ),
    ]
    for model_dir, test_path, features in specs:
        calibrated = joblib.load(f"{model_dir}/model.pkl")
        base = joblib.load(f"{model_dir}/model_uncalibrated.pkl")
        test = pd.read_csv(test_path).head(100)
        assert (calibrated.predict(test[features]) == base.predict(test[features])).all()


def test_calibration_metadata_has_review_policy():
    for model_dir in [
        "src/models/cefr_word_classifier",
        "src/models/cefr_sentence_classifier",
    ]:
        metadata = json.loads(open(f"{model_dir}/metadata.json", encoding="utf-8").read())
        calibration = metadata["calibration"]
        assert calibration["method"] == "temperature_scaling"
        assert calibration["needs_review_threshold"] > 0
        assert 0 <= calibration["test_selective_metrics"]["coverage"] <= 1

from __future__ import annotations

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.features import SENTENCE_FEATURE_COLUMNS, WORD_FEATURE_COLUMNS
from src.features.word import extract_word_features

pytestmark = pytest.mark.integration


def test_word_feature_schema_matches_saved_training_data():
    saved = pd.read_csv("data/processed/cefr_word_features.csv").head(25)
    online = pd.concat([extract_word_features(word) for word in saved["word"]], ignore_index=True)
    assert list(online.columns) == WORD_FEATURE_COLUMNS
    assert_frame_equal(
        saved[WORD_FEATURE_COLUMNS].reset_index(drop=True),
        online,
        check_dtype=False,
        atol=1e-12,
        rtol=1e-12,
    )


def test_sentence_features_match_saved_training_data(cefr_engine):
    saved = pd.read_csv("data/processed/cefr_sentence_features.csv").head(10)
    online = pd.concat(
        [cefr_engine.extract_sentence_features(text) for text in saved["text"]],
        ignore_index=True,
    )
    assert list(online.columns) == SENTENCE_FEATURE_COLUMNS
    assert_frame_equal(
        saved[SENTENCE_FEATURE_COLUMNS].reset_index(drop=True),
        online,
        check_dtype=False,
        atol=1e-12,
        rtol=1e-12,
    )

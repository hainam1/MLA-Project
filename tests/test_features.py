from __future__ import annotations

import spacy

from src.features import SENTENCE_FEATURE_COLUMNS, SentenceFeatureExtractor


def test_sentence_feature_schema_is_finite_and_stable():
    extractor = SentenceFeatureExtractor({}, nlp=spacy.blank("en"))
    frame = extractor.extract("Although it rained, the expedition continued safely.")

    assert list(frame.columns) == SENTENCE_FEATURE_COLUMNS
    assert frame.shape == (1, len(SENTENCE_FEATURE_COLUMNS))
    assert frame.notna().all().all()
    assert frame["num_words"].iloc[0] == 7


def test_extract_many_preserves_row_count():
    extractor = SentenceFeatureExtractor({}, nlp=spacy.blank("en"))
    frame = extractor.extract_many(["This is easy.", "This construction is somewhat harder."])

    assert len(frame) == 2
    assert list(frame.columns) == SENTENCE_FEATURE_COLUMNS

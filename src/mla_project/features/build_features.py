"""One reusable feature extractor for train, validation, test, and new essays."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import pandas as pd

from mla_project.features.extract_grammar import GrammarChecker, extract_grammar_features
from mla_project.features.extract_length import extract_length_features
from mla_project.features.extract_syntax import extract_syntax_features
from mla_project.features.extract_vocabulary import extract_vocabulary_features
from mla_project.features.preprocessing import clean_text

FEATURE_NAMES = (
    "word_count",
    "sentence_count",
    "mean_sentence_length",
    "mtld",
    "mattr",
    "mean_word_frequency",
    "mean_word_length",
    "lexical_density",
    "noun_diversity",
    "detected_grammar_errors_per_100_words",
    "detected_error_free_sentence_ratio",
    "complex_sentence_ratio",
    "estimated_clauses_per_sentence",
    "subordinate_clause_ratio",
)


@dataclass
class FeatureExtractor:
    """Stateful holder for expensive spaCy and LanguageTool resources."""

    nlp: Any
    grammar_checker: GrammarChecker
    mtld_threshold: float = 0.72
    mtld_min_tokens: int = 10
    mattr_window: int = 50

    def transform_text(self, text: str) -> dict[str, float]:
        """Transform one essay using exactly the configured feature set."""
        cleaned = clean_text(text)
        doc = self.nlp(cleaned)
        return self.transform_prepared(cleaned, doc)

    def transform_prepared(
        self, cleaned_text: str, doc: Any, *, grammar_matches: list[object] | None = None
    ) -> dict[str, float]:
        """Compose features from a cleaned text/doc, optionally using batched grammar results."""
        features = extract_length_features(doc)
        features.update(
            extract_vocabulary_features(
                doc,
                mtld_threshold=self.mtld_threshold,
                mtld_min_tokens=self.mtld_min_tokens,
                mattr_window=self.mattr_window,
            )
        )
        features.update(
            extract_grammar_features(
                cleaned_text,
                doc,
                self.grammar_checker,
                matches=grammar_matches,
            )
        )
        features.update(extract_syntax_features(doc))
        if tuple(features) != FEATURE_NAMES:
            raise RuntimeError(f"Feature schema mismatch: {tuple(features)}")
        if not all(math.isfinite(value) for value in features.values()):
            raise RuntimeError("Feature extraction produced a non-finite value.")
        return {name: float(features[name]) for name in FEATURE_NAMES}

    def transform(self, texts: pd.Series) -> pd.DataFrame:
        """Transform a series while preserving its index."""
        rows = [self.transform_text(text) for text in texts]
        return pd.DataFrame(rows, index=texts.index)


def load_default_extractor(
    *,
    spacy_model: str = "en_core_web_sm",
    language: str = "en-US",
    language_tool_version: str = "6.6",
) -> FeatureExtractor:
    """Load configured NLP resources explicitly; may download nothing."""
    import language_tool_python
    import spacy

    return FeatureExtractor(
        nlp=spacy.load(spacy_model),
        grammar_checker=language_tool_python.LanguageTool(
            language, language_tool_download_version=language_tool_version
        ),
    )


def extract_features(essay: str, *, extractor: FeatureExtractor | None = None) -> dict[str, float]:
    """Public single-essay API returning exactly 14 ordered values."""
    active_extractor = extractor or load_default_extractor()
    try:
        return active_extractor.transform_text(essay)
    finally:
        if extractor is None and hasattr(active_extractor.grammar_checker, "close"):
            active_extractor.grammar_checker.close()

from __future__ import annotations

from dataclasses import dataclass

import pytest
import yaml
import spacy
from spacy.tokens import Doc

from mla_project.features import FEATURE_NAMES, FeatureExtractor
from mla_project.features.extract_syntax import extract_syntax_features
from mla_project.features.preprocessing import clean_text


@dataclass
class FakeMatch:
    ruleIssueType: str
    offset: int
    errorLength: int


class FakeChecker:
    def __init__(self, matches: list[FakeMatch] | None = None):
        self.matches = matches or []

    def check(self, text: str) -> list[FakeMatch]:
        return self.matches


def sentencizer():
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    return nlp


def test_feature_extraction_returns_exact_ordered_schema():
    extractor = FeatureExtractor(nlp=sentencizer(), grammar_checker=FakeChecker())
    features = extractor.transform_text("Learners use precise vocabulary. It helps.")

    assert tuple(features) == FEATURE_NAMES
    assert len(features) == 14
    assert features["word_count"] == 6
    assert features["sentence_count"] == 2
    assert features["mean_sentence_length"] == 3
    assert features["detected_error_free_sentence_ratio"] == 1


def test_yaml_schema_matches_public_feature_order():
    with open("configs/features.yaml", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    configured = tuple(
        feature
        for group in ("length", "vocabulary", "grammar", "syntax")
        for feature in config["groups"][group]
    )
    assert configured == FEATURE_NAMES


def test_detected_grammar_features_ignore_non_grammar_matches():
    checker = FakeChecker(
        [
            FakeMatch("grammar", offset=4, errorLength=2),
            FakeMatch("misspelling", offset=28, errorLength=7),
        ]
    )
    extractor = FeatureExtractor(nlp=sentencizer(), grammar_checker=checker)
    features = extractor.transform_text("She go to school yesterday. The teacher smiles.")

    assert features["detected_grammar_errors_per_100_words"] == 12.5
    assert features["detected_error_free_sentence_ratio"] == 0.5


def test_syntax_features_on_simple_and_subordinate_clauses():
    vocab = spacy.blank("en").vocab
    simple = Doc(
        vocab,
        words=["Students", "write", "."],
        heads=[1, 1, 1],
        deps=["nsubj", "ROOT", "punct"],
        pos=["NOUN", "VERB", "PUNCT"],
        sent_starts=[True, False, False],
    )
    complex_doc = Doc(
        vocab,
        words=["Although", "students", "study", ",", "they", "improve", "."],
        heads=[2, 2, 5, 2, 5, 5, 5],
        deps=["mark", "nsubj", "advcl", "punct", "nsubj", "ROOT", "punct"],
        pos=["SCONJ", "NOUN", "VERB", "PUNCT", "PRON", "VERB", "PUNCT"],
        sent_starts=[True, False, False, False, False, False, False],
    )

    assert extract_syntax_features(simple) == {
        "complex_sentence_ratio": 0.0,
        "estimated_clauses_per_sentence": 1.0,
        "subordinate_clause_ratio": 0.0,
    }
    assert extract_syntax_features(complex_doc) == {
        "complex_sentence_ratio": 1.0,
        "estimated_clauses_per_sentence": 2.0,
        "subordinate_clause_ratio": 0.5,
    }


def test_short_text_policy_and_cleaning():
    extractor = FeatureExtractor(nlp=sentencizer(), grammar_checker=FakeChecker())
    features = extractor.transform_text("  Word\n\tword  ")

    assert clean_text("  Word\n\tword  ") == "Word word"
    assert features["mtld"] == 0.0
    assert features["mattr"] == 0.5
    assert features["noun_diversity"] == 0.0


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_empty_essay_is_rejected(text):
    extractor = FeatureExtractor(nlp=sentencizer(), grammar_checker=FakeChecker())
    with pytest.raises(ValueError, match="non-empty"):
        extractor.transform_text(text)

from dataclasses import dataclass

import pytest
import spacy
from spacy.tokens import Doc

from mla_project.features.feature_v2 import V2_FEATURE_NAMES, extract_v2_features


@dataclass
class Match:
    ruleIssueType: str
    ruleId: str


def test_v2_features_have_stable_schema_and_count_rule_repetition():
    nlp = spacy.blank("en")
    doc = Doc(
        nlp.vocab,
        words=["Students", "write", "essays", "."],
        heads=[1, 1, 1, 1],
        deps=["nsubj", "ROOT", "dobj", "punct"],
        pos=["NOUN", "VERB", "NOUN", "PUNCT"],
        sent_starts=[True, False, False, False],
    )
    matches = [
        Match("grammar", "AGR"),
        Match("grammar", "AGR"),
        Match("grammar", "VERB"),
        Match("misspelling", "TYPO"),
    ]
    result = extract_v2_features(doc, matches)
    assert tuple(result) == V2_FEATURE_NAMES
    assert result["detected_misspellings_per_100_words"] == pytest.approx(100 / 3)
    assert result["detected_grammar_rule_diversity"] == pytest.approx(2 / 3)
    assert result["detected_repeated_grammar_rule_ratio"] == pytest.approx(1 / 3)
    assert result["mean_dependency_distance"] == pytest.approx(1.0)
    assert result["mean_sentence_tree_depth"] == pytest.approx(1.0)


def test_v2_empty_match_features_are_finite():
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    result = extract_v2_features(nlp("Short text."), [])
    assert result["detected_grammar_rule_diversity"] == 0.0
    assert result["detected_repeated_grammar_rule_ratio"] == 0.0

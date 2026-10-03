"""The three parser-based approximate syntax features."""

from __future__ import annotations

from typing import Any

from mla_project.features.preprocessing import sentence_spans

SUBORDINATE_DEPENDENCIES = frozenset(
    {"advcl", "ccomp", "xcomp", "acl", "relcl", "csubj", "csubjpass"}
)
MAIN_CLAUSE_DEPENDENCIES = frozenset({"ROOT", "conj"})


def extract_syntax_features(doc: Any) -> dict[str, float]:
    """Estimate clause counts from verbal heads and subordinate dependencies."""
    sentences = sentence_spans(doc)
    clause_pos = {"VERB", "AUX"}
    total_clauses = 0
    subordinate_clauses = 0
    complex_sentences = 0
    for sentence in sentences:
        clause_heads = [
            token
            for token in sentence
            if token.pos_ in clause_pos
            and token.dep_ in MAIN_CLAUSE_DEPENDENCIES | SUBORDINATE_DEPENDENCIES
        ]
        subordinate = [token for token in clause_heads if token.dep_ in SUBORDINATE_DEPENDENCIES]
        total_clauses += len(clause_heads)
        subordinate_clauses += len(subordinate)
        complex_sentences += bool(subordinate)
    return {
        "complex_sentence_ratio": float(complex_sentences / len(sentences)),
        "estimated_clauses_per_sentence": float(total_clauses / len(sentences)),
        "subordinate_clause_ratio": float(
            subordinate_clauses / total_clauses if total_clauses else 0.0
        ),
    }

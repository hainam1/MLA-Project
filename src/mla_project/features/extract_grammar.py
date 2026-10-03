"""The two LanguageTool-based detected-grammar features."""

from __future__ import annotations

from typing import Any, Protocol

from mla_project.features.preprocessing import sentence_spans, word_tokens


class GrammarChecker(Protocol):
    def check(self, text: str) -> list[object]: ...


def extract_grammar_features(
    text: str,
    doc: Any,
    checker: GrammarChecker | None = None,
    *,
    matches: list[object] | None = None,
) -> dict[str, float]:
    """Count only matches classified as grammar; detections are not human labels."""
    if matches is None:
        if checker is None:
            raise ValueError("Provide either a grammar checker or precomputed matches.")
        matches = checker.check(text)
    grammar_matches = [
        match for match in matches if getattr(match, "ruleIssueType", "").casefold() == "grammar"
    ]
    sentences = sentence_spans(doc)
    sentence_has_error = []
    for sentence in sentences:
        sentence_has_error.append(
            any(
                match.offset < sentence.end_char
                and match.offset + max(match.errorLength, 1) > sentence.start_char
                for match in grammar_matches
            )
        )
    word_count = len(word_tokens(doc))
    return {
        "detected_grammar_errors_per_100_words": float(
            100 * len(grammar_matches) / max(word_count, 1)
        ),
        "detected_error_free_sentence_ratio": float(
            sum(not value for value in sentence_has_error) / len(sentences)
        ),
    }

from pathlib import Path

import pytest

from src.pipeline.lexical_retriever import VietnameseEnglishLexicon
from src.pipeline.semantic_reranker import SemanticReranker

pytestmark = pytest.mark.integration


def test_semantic_artifacts_are_local_and_pinned():
    reranker = SemanticReranker(device="cpu")
    assert reranker.available is True
    assert Path("src/models/semantic_reranker/SOURCE.md").exists()


def test_dictionary_retrieval_filters_obvious_wrong_meanings():
    lexicon = VietnameseEnglishLexicon(device="cpu")
    dog = lexicon.retrieve("con chó", limit=5)
    help_items = lexicon.retrieve("giúp đỡ", limit=10)
    assert dog[0].lemma == "dog"
    assert "help" in {item.lemma for item in help_items}
    assert "resolve" not in {item.lemma for item in help_items}
    assert all(item.sense_id and item.vietnamese_gloss for item in dog + help_items)

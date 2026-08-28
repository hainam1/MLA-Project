import pytest

from src.models.sentence_rewriter.service import SentenceRewriterService, build_prompt


def test_rewrite_prompt_contains_sentence_and_target():
    prompt = build_prompt("The experiment produced significant results.", "A2")
    assert "A2" in prompt
    assert "significant results" in prompt


def test_rewriter_rejects_upgrade_before_model_generation():
    service = SentenceRewriterService.__new__(SentenceRewriterService)
    with pytest.raises(ValueError, match="does not support upgrade"):
        service.rewrite("This sentence is simple.", "A2", "B1")

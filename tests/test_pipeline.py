from src.pipeline.run_pipeline import (
    CapyVocabPipeline,
    build_controlled_examples,
    is_complete_example,
)
from src.pipeline.lexical_retriever import LexicalCandidate


class FakeTranslator:
    def translate_candidates(self, text):
        return ["excellent", "resolve", "delusion"]


class FakeCEFR:
    word_levels = {"good": "A1", "excellent": "B2", "beneficial": "C1"}

    def predict(self, text, route_override=None):
        if route_override == "sentence_mode":
            level = "B2" if "excellent" in text.lower() else "A1"
        else:
            level = self.word_levels.get(text.lower(), "A1")
        probabilities = {item: 2.0 for item in ["A1", "A2", "B1", "B2", "C1"]}
        probabilities[level] = 92.0
        return {
            "status": "success",
            "route": route_override,
            "model": (
                "Model 2b (CEFR Sentence Classifier)"
                if route_override == "sentence_mode"
                else "CEFR Wordlist Exact Lookup"
            ),
            "predicted_level": level,
            "confidence": 92.0,
            "probabilities": probabilities,
            "needs_review": False,
        }


class FakeExampleGenerator:
    def generate_candidates(self, target_word, target_level):
        return [
            {
                "status": "success",
                "target_word": target_word,
                "target_level": target_level,
                "sentence": f"The result was {target_word}.",
                "lexical_constraint_satisfied": True,
            }
        ]


def candidate(word, pos, score=0.9, sense="test:1"):
    return LexicalCandidate(
        lemma=word,
        part_of_speech=pos,
        sense_id=sense,
        vietnamese_gloss="tốt",
        source="test lexicon",
        lexical_score=score,
        semantic_score=score,
        relevance_score=score,
    )


class FakeLexicon:
    def retrieve(self, text):
        return [
            candidate("good", "ADJ", 0.95, "test:good"),
            candidate("excellent", "ADJ", 0.93, "test:excellent"),
            candidate("beneficial", "ADJ", 0.91, "test:beneficial"),
        ]

    def validate_english_candidates(self, text, candidates):
        return []


def pipeline():
    return CapyVocabPipeline(
        FakeTranslator(),
        FakeCEFR(),
        FakeExampleGenerator(),
        lexical_retriever=FakeLexicon(),
    )


def test_selects_candidate_matching_requested_level_and_verifies_example():
    result = pipeline().process("tốt", "B2")
    assert result["status"] == "success"
    assert result["requested_level"] == "B2"
    assert result["translation_en"] == "excellent"
    assert result["selected_vocabulary"]["target_match"] is True
    assert result["generated_example"]["level_match"] is True
    assert result["generated_example"]["target_word"] == "excellent"
    assert result["capabilities"]["sentence_rewriting"] is False


def test_rejects_complete_sentence():
    result = pipeline().process("Tôi học tiếng Anh mỗi ngày.", "A1")
    assert result["status"] == "error"
    assert "sentences" in result["message"]


def test_requires_valid_target_level():
    assert pipeline().process("tốt", None)["status"] == "error"
    assert pipeline().process("tốt", "C2")["status"] == "error"


def test_marks_closest_candidate_when_exact_level_is_unavailable():
    result = pipeline().process("tốt", "A2")
    assert result["status"] == "success"
    assert result["selected_vocabulary"]["selection_status"] == "no_exact_level_match"
    assert result["selected_vocabulary"]["target_match"] is False
    assert result["selected_vocabulary"]["needs_review"] is True


def test_controlled_examples_are_complete_and_span_all_levels():
    examples = build_controlled_examples("superb", "ADJ")
    assert [example["target_level"] for example in examples] == ["A1", "A2", "B1", "B2", "C1"]
    assert all(is_complete_example(example["sentence"]) for example in examples)


def test_incomplete_or_repetitive_generation_is_rejected():
    assert is_complete_example("superb, amazing, amazing.") is False
    assert is_complete_example("This result is superb.") is True


class DisabilityTranslator:
    def translate_candidates(self, text):
        return ["Disabilities", "Disabled", "Delusion", "Resolve", "Despot"]


class DisabilityCEFR:
    levels = {
        "disability": ("B2", "CEFR Wordlist Exact Lookup", "NOUN", False),
        "handicap": ("B1", "CEFR Wordlist Exact Lookup", "NOUN", False),
        "impairment": ("C1", "Model 2a (CEFR Word Classifier)", "NOUN", True),
        "disablement": ("C1", "Model 2a (CEFR Word Classifier)", "NOUN", True),
        "resolve": ("B2", "CEFR Wordlist Exact Lookup", "VERB", False),
    }

    def predict_vocabulary(self, text):
        level, model, pos, needs_review = self.levels.get(
            text.lower(), ("B1", "Model 2a (CEFR Word Classifier)", None, True)
        )
        probabilities = {item: 0.0 for item in ["A1", "A2", "B1", "B2", "C1"]}
        probabilities[level] = 100.0 if not needs_review else 45.0
        return {
            "status": "success",
            "model": model,
            "predicted_level": level,
            "part_of_speech": pos,
            "probabilities": probabilities,
            "needs_review": needs_review,
        }

    def predict(self, text, route_override=None):
        probabilities = {item: 0.0 for item in ["A1", "A2", "B1", "B2", "C1"]}
        probabilities["C1"] = 70.0
        return {
            "status": "success",
            "model": "Model 2b (CEFR Sentence Classifier)",
            "predicted_level": "C1",
            "probabilities": probabilities,
            "needs_review": False,
        }


class DisabilityLexicon:
    def retrieve(self, text):
        return [
            LexicalCandidate(
                lemma="disability",
                part_of_speech="NOUN",
                sense_id="test:disability",
                vietnamese_gloss="tật nguyền",
                source="test lexicon",
                lexical_score=1.0,
                semantic_score=0.95,
                relevance_score=0.95,
            ),
            LexicalCandidate(
                lemma="impairment",
                part_of_speech="NOUN",
                sense_id="test:impairment",
                vietnamese_gloss="tật nguyền",
                source="test lexicon",
                lexical_score=0.96,
                semantic_score=0.92,
                relevance_score=0.92,
            ),
        ]

    def validate_english_candidates(self, text, candidates):
        return []


def test_semantics_are_filtered_before_cefr_selection_for_disability():
    subject = CapyVocabPipeline(
        DisabilityTranslator(),
        DisabilityCEFR(),
        FakeExampleGenerator(),
        lexical_retriever=DisabilityLexicon(),
    )
    candidates, _ = subject._translation_candidates("tật nguyền")
    assert candidates[0].lemma == "disability"
    assert "impairment" in [item.lemma for item in candidates]
    assert "resolve" not in [item.lemma for item in candidates]
    result = subject.process("tật nguyền", "C1")
    assert result["translation_en"] == "disability"
    assert result["selected_vocabulary"]["selection_status"] == "no_exact_level_match"
    assert result["selected_vocabulary"]["target_match"] is False
    assert result["selected_vocabulary"]["needs_review"] is True

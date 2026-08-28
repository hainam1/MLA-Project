import os
import subprocess
import sys

import pytest

from src.features import SENTENCE_FEATURE_COLUMNS, WORD_FEATURE_COLUMNS

pytestmark = pytest.mark.integration


def test_model_feature_contracts(cefr_engine):
    assert list(cefr_engine.model2a.feature_names_in_) == WORD_FEATURE_COLUMNS
    assert list(cefr_engine.model2b.feature_names_in_) == SENTENCE_FEATURE_COLUMNS
    assert list(cefr_engine.model2a.classes_) == [0, 1, 2, 3, 4]
    assert list(cefr_engine.model2b.classes_) == [0, 1, 2, 3, 4]


def test_word_and_sentence_predictions(cefr_engine):
    word = cefr_engine.predict("ubiquitous")
    sentence = cefr_engine.predict("The student reads a book every day.")
    assert word["status"] == "success"
    assert word["route"] == "word_mode"
    assert sentence["status"] == "success"
    assert sentence["route"] == "sentence_mode"
    assert word["predicted_level"] in {"A1", "A2", "B1", "B2", "C1"}
    assert sentence["predicted_level"] in {"A1", "A2", "B1", "B2", "C1"}
    for result in (word, sentence):
        assert isinstance(result["needs_review"], bool)
        assert result["confidence_status"] in {"accepted", "low_confidence"}
        assert result["review_threshold"] > 0
        assert result["probability_calibration"] == "temperature_scaling"


def test_exact_wordlist_lookup_precedes_statistical_word_model(cefr_engine):
    result = cefr_engine.predict_vocabulary("superb")
    assert result["predicted_level"] == "B2"
    assert result["model"] == "CEFR Wordlist Exact Lookup"
    assert result["needs_review"] is False


def test_exact_lookup_keeps_level_and_part_of_speech_on_same_row(cefr_engine):
    adjective = cefr_engine.predict_vocabulary("above", part_of_speech="ADJ")
    preposition = cefr_engine.predict_vocabulary("above", part_of_speech="ADP")
    ambiguous = cefr_engine.predict_vocabulary("above")
    assert (adjective["predicted_level"], adjective["part_of_speech"]) == ("A1", "ADJ")
    assert (preposition["predicted_level"], preposition["part_of_speech"]) == ("B1", "ADP")
    assert ambiguous["model"] == "Model 2a (CEFR Word Classifier)"
    assert ambiguous["needs_review"] is True
    assert ambiguous["confidence_status"] == "ambiguous_lemma_without_pos"


def test_example_generator_checkpoint_loads_and_enforces_word():
    code = (
        "from src.models.example_generator import ExampleGeneratorService; "
        "r=ExampleGeneratorService(device='cpu').generate('apple','A1'); "
        "assert r['status']=='success' and r['lexical_constraint_satisfied']; "
        "print('MODEL3A_LOAD_OK')"
    )
    environment = os.environ.copy()
    environment["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        env=environment,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "MODEL3A_LOAD_OK" in completed.stdout


def test_sentence_rewriter_checkpoint_loads():
    code = (
        "from src.models.sentence_rewriter import SentenceRewriterService; "
        "s=SentenceRewriterService(device='cpu'); "
        "r=s.rewrite('The experiment produced significant results.','B2','A2'); "
        "assert r['status']=='success' and r['direction']=='simplify'; "
        "print('MODEL3B_LOAD_OK')"
    )
    environment = os.environ.copy()
    environment["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        env=environment,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "MODEL3B_LOAD_OK" in completed.stdout

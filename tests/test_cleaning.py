from __future__ import annotations

import pandas as pd

from src.data.clean_cefr_sentences import clean_corpus, combine_corpora, normalize_text


def test_normalize_text_collapses_space_and_uses_nfc():
    assert normalize_text("  This\t is   a sentence. ") == "This is a sentence."


def test_clean_corpus_excludes_invalid_and_conflicting_rows():
    raw = pd.DataFrame(
        {
            "text": ["Hello world.", "hello world.", "Bad label.", "C2 row.", ""],
            "cefr_level": ["A1", "B1", "Z9", "C2", "A1"],
        }
    )
    cleaned, audit = clean_corpus(raw, "sample")

    assert cleaned.empty
    assert audit["conflicting_text_groups"] == 1
    assert audit["conflicting_label_rows"] == 2
    assert audit["excluded_c2_rows"] == 1
    assert audit["invalid_label_rows"] == 1
    assert audit["empty_rows"] == 1


def test_combine_corpora_keeps_valid_independent_rows():
    left, _ = clean_corpus(pd.DataFrame({"text": ["One sentence."], "cefr_level": ["A1"]}), "left")
    right, _ = clean_corpus(
        pd.DataFrame({"text": ["Another sentence."], "cefr_level": ["B1"]}), "right"
    )
    combined, audit = combine_corpora([left, right])

    assert len(combined) == 2
    assert audit["retained_rows"] == 2


def test_clean_wordlist_maps_levels():
    from src.data.clean_cefr_wordlist import clean_auxiliary_lexicon

    raw = pd.DataFrame(
        {
            "Word": ["cat", "dog", "unknown_word", "c2_word"],
            "PoS": ["NOUN", "NOUN", "VERB", "ADJ"],
            "Teachers Avg": [1.0, 3.0, 2.0, 6.0],
            "Level.Teachers.Average": ["A1", "B1", "Unknown", "C2"],
        }
    )
    cleaned = clean_auxiliary_lexicon(raw)
    assert len(cleaned) == 2
    assert set(cleaned["cefr_level"]) == {"A1", "B1"}


def test_eda_properties_compute_correct_ranges():
    from src.data.generate_eda import compute_basic_properties

    sample = pd.DataFrame(
        {"text": ["This is a simple test sentence."], "cefr_level": ["A1"], "source": ["test"]}
    )
    props = compute_basic_properties(sample)
    assert props["num_words"].iloc[0] == 6
    assert props["num_chars"].iloc[0] == len("This is a simple test sentence.")
    assert 1.0 <= props["avg_word_zipf"].iloc[0] <= 8.0

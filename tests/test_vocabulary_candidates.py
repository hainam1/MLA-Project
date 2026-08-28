from src.pipeline.vocabulary_candidates import expand_with_wordnet, normalize_to_lemma


def test_translation_candidates_remain_ranked_first():
    expanded = expand_with_wordnet(["Good", "Fine"], max_candidates=20)
    assert expanded[0] == "good"
    assert "fine" not in expanded


def test_wordnet_expands_common_translation_when_installed():
    expanded = [candidate.casefold() for candidate in expand_with_wordnet(["good"], 80, "ADJ")]
    assert "superb" in expanded
    assert "commodity" not in expanded


def test_plural_translation_is_normalized_before_expansion():
    assert normalize_to_lemma("Disabilities") == "disability"


def test_noisy_translation_beams_are_removed_by_semantic_whitelist():
    expanded = expand_with_wordnet(
        ["Disabilities", "Resolve", "Delusion", "Despot"],
        max_candidates=20,
        part_of_speech="NOUN",
    )
    assert expanded[0] == "disability"
    assert "impairment" in expanded
    assert "resolve" not in expanded
    assert "delusion" not in expanded

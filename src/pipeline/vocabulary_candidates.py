"""Semantic candidate expansion for target-level vocabulary selection."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORDNET_DATA = PROJECT_ROOT / "data/external/nltk_data"
ENGLISH_TERM = re.compile(r"^[A-Za-z][A-Za-z '\-]*$")


def _clean_term(value: str) -> str:
    term = str(value).strip().strip(".,:;!?")
    if term.lower().startswith("to "):
        term = term[3:].strip()
    if term.istitle():
        term = term.lower()
    return term


def normalize_to_lemma(value: str, part_of_speech: str | None = None) -> str:
    """Normalize an inflected translation before semantic expansion."""
    term = _clean_term(value)
    if not term or len(term.split()) != 1:
        return term
    try:
        import nltk
        from nltk.corpus import wordnet as wn

        if str(WORDNET_DATA) not in nltk.data.path:
            nltk.data.path.insert(0, str(WORDNET_DATA))
        pos_map = {"ADJ": wn.ADJ, "NOUN": wn.NOUN, "VERB": wn.VERB, "ADV": wn.ADV}
        preferred = pos_map.get(str(part_of_speech or "").upper())
        lemma = (
            wn.morphy(term.casefold(), pos=preferred) if preferred else wn.morphy(term.casefold())
        )
        return lemma or term
    except (ImportError, LookupError, OSError):
        return term


def infer_part_of_speech(value: str) -> str | None:
    """Infer the most frequent WordNet part of speech for a lemma."""
    term = normalize_to_lemma(value)
    try:
        import nltk
        from nltk.corpus import wordnet as wn

        if str(WORDNET_DATA) not in nltk.data.path:
            nltk.data.path.insert(0, str(WORDNET_DATA))
        synsets = wn.synsets(term.replace(" ", "_"))
        if not synsets:
            return None
        return {
            wn.ADJ: "ADJ",
            wn.ADJ_SAT: "ADJ",
            wn.NOUN: "NOUN",
            wn.VERB: "VERB",
            wn.ADV: "ADV",
        }.get(synsets[0].pos())
    except (ImportError, LookupError, OSError):
        return None


def wordnet_related(left: str, right: str, minimum_wup: float = 0.82) -> bool:
    """Check whether two English lemmas share a defensible lexical relation."""
    left_term = normalize_to_lemma(left).casefold().replace(" ", "_")
    right_term = normalize_to_lemma(right).casefold().replace(" ", "_")
    if left_term == right_term:
        return True
    try:
        import nltk
        from nltk.corpus import wordnet as wn

        if str(WORDNET_DATA) not in nltk.data.path:
            nltk.data.path.insert(0, str(WORDNET_DATA))
        left_synsets = wn.synsets(left_term)
        right_synsets = wn.synsets(right_term)
        if not left_synsets or not right_synsets:
            return False
        if any(
            left_synset == right_synset
            for left_synset in left_synsets
            for right_synset in right_synsets
        ):
            return True
        derived = {
            related.name().casefold()
            for synset in left_synsets
            for lemma in synset.lemmas()
            for related in lemma.derivationally_related_forms()
        }
        if right_term in derived:
            return True
        similarities = [
            left_synset.wup_similarity(right_synset) or 0.0
            for left_synset in left_synsets
            for right_synset in right_synsets
            if left_synset.pos() == right_synset.pos()
        ]
        return max(similarities, default=0.0) >= minimum_wup
    except (ImportError, LookupError, OSError):
        return False


def expand_with_wordnet(
    candidates: list[str], max_candidates: int = 80, part_of_speech: str | None = None
) -> list[str]:
    """Expand ranked translations with auditable English WordNet synonyms.

    Only the normalized top translation acts as the semantic anchor. Lower
    translation beams are intentionally discarded because beam rank does not
    guarantee semantic equivalence. If WordNet is unavailable, serving
    degrades to the normalized top translation only.
    """
    ranked = []
    seen = set()
    if not candidates:
        return ranked
    anchor = normalize_to_lemma(candidates[0], part_of_speech)
    anchor_key = anchor.casefold()
    if anchor and ENGLISH_TERM.fullmatch(anchor) and len(anchor.split()) <= 3:
        seen.add(anchor_key)
        ranked.append(anchor)

    try:
        import nltk
        from nltk.corpus import wordnet as wn

        if str(WORDNET_DATA) not in nltk.data.path:
            nltk.data.path.insert(0, str(WORDNET_DATA))
        semantic_rank: dict[str, tuple[int, int, int, int, str]] = {}
        display: dict[str, str] = {}
        pos_map = {"ADJ": wn.ADJ, "NOUN": wn.NOUN, "VERB": wn.VERB, "ADV": wn.ADV}
        wordnet_pos = pos_map.get(str(part_of_speech or "").upper())
        lookup = anchor.casefold().replace(" ", "_")
        primary_synsets = wn.synsets(lookup, pos=wordnet_pos)
        if primary_synsets:
            # Vocabulary-only input has no context for sense disambiguation.
            # Use the most frequent WordNet sense instead of mixing all senses.
            for sense_index, synset in enumerate(primary_synsets[:1]):
                # Adjective "similar to" links capture graded alternatives
                # such as good -> superb without crossing into antonyms.
                related_groups = (
                    [(synset, 0)],
                    [(item, 1) for item in synset.similar_tos()],
                    [(item, 2) for item in synset.also_sees()],
                )
                for group in related_groups:
                    for related, relation_rank in group:
                        for lemma in related.lemmas():
                            term = _clean_term(lemma.name().replace("_", " "))
                            key = term.casefold()
                            if (
                                term
                                and ENGLISH_TERM.fullmatch(term)
                                and len(term.split()) <= 3
                                and key not in seen
                            ):
                                display[key] = term
                                rank = (
                                    sense_index,
                                    relation_rank,
                                    -int(lemma.count()),
                                    len(key),
                                    key,
                                )
                                semantic_rank[key] = min(rank, semantic_rank.get(key, rank))
        synonyms = sorted(display, key=semantic_rank.__getitem__)
        for key in synonyms:
            seen.add(key)
            ranked.append(display[key])
            if len(ranked) >= max_candidates:
                break
    except (ImportError, LookupError, OSError):
        pass
    return ranked

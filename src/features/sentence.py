"""Shared sentence features for the CEFR sentence classifier."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd
import pyphen
import spacy
import textstat
import wordfreq

SENTENCE_FEATURE_COLUMNS = [
    "num_words",
    "num_chars",
    "avg_word_len",
    "num_syllables_total",
    "avg_syllables_per_word",
    "avg_word_zipf",
    "min_word_zipf",
    "rare_word_ratio",
    "avg_word_cefr",
    "max_word_cefr",
    "word_oov_ratio",
    "dep_tree_depth",
    "subclause_count",
    "subclause_ratio",
    "passive_count",
    "pos_noun_ratio",
    "pos_verb_ratio",
    "pos_adj_ratio",
    "pos_adv_ratio",
    "pos_adp_ratio",
    "flesch_reading_ease",
    "flesch_kincaid_grade",
    "gunning_fog",
    "automated_readability_index",
    "dale_chall_score",
]

SUBCLAUSE_DEPS = frozenset({"advcl", "relcl", "ccomp", "xcomp", "csubj", "csubjpass", "acl"})
PASSIVE_DEPS = frozenset({"nsubjpass", "auxpass"})


def zipf_to_cefr(zipf_score: float) -> float:
    if zipf_score >= 6.0:
        return 0.0
    if zipf_score >= 5.0:
        return 1.0
    if zipf_score >= 4.0:
        return 2.0
    if zipf_score >= 3.0:
        return 3.0
    return 4.0


class SentenceFeatureExtractor:
    """Extract the same deterministic feature frame everywhere."""

    def __init__(self, word_cefr_lookup: Mapping[str, float], nlp=None):
        self.word_cefr_lookup = {
            str(word).lower(): float(level) for word, level in word_cefr_lookup.items()
        }
        self.nlp = nlp or spacy.load("en_core_web_sm", disable=["ner"])
        self.hyphenator = pyphen.Pyphen(lang="en_US")

    @classmethod
    def from_wordlist(cls, wordlist_path, nlp=None):
        words = pd.read_csv(wordlist_path)
        lookup = words.groupby(words["word"].str.lower())["cefr_label"].mean()
        return cls(lookup.to_dict(), nlp=nlp)

    def _syllables(self, word: str) -> int:
        hyphenated = self.hyphenator.inserted(word.lower())
        return max(1, len(hyphenated.split("-"))) if hyphenated else 1

    def _tree_depth(self, node) -> int:
        children = list(node.children)
        if not children:
            return 1
        return 1 + max(self._tree_depth(child) for child in children)

    def extract(self, sentence: str) -> pd.DataFrame:
        text = str(sentence).strip()
        doc = self.nlp(text)
        words = [token for token in doc if token.is_alpha]
        num_words = max(1, len(words))
        word_lengths = [len(token.text) for token in words] or [len(text)]
        syllables = [self._syllables(token.text) for token in words] or [1]
        zipf_scores = [wordfreq.zipf_frequency(token.text.lower(), "en") for token in words] or [
            4.0
        ]

        levels = []
        oov_count = 0
        for token in words:
            surface = token.text.lower()
            lemma = token.lemma_.lower()
            if surface in self.word_cefr_lookup:
                levels.append(self.word_cefr_lookup[surface])
            elif lemma in self.word_cefr_lookup:
                levels.append(self.word_cefr_lookup[lemma])
            else:
                oov_count += 1
                levels.append(zipf_to_cefr(wordfreq.zipf_frequency(surface, "en")))
        levels = levels or [1.0]

        roots = [token for token in doc if token.head == token]
        tree_depth = max((self._tree_depth(root) for root in roots), default=1)
        subclause_count = sum(token.dep_ in SUBCLAUSE_DEPS for token in words)
        passive_count = sum(token.dep_ in PASSIVE_DEPS or "pass" in token.dep_ for token in words)
        pos_tags = [token.pos_ for token in words]

        values = {
            "num_words": num_words,
            "num_chars": len(text),
            "avg_word_len": round(float(np.mean(word_lengths)), 4),
            "num_syllables_total": int(sum(syllables)),
            "avg_syllables_per_word": round(sum(syllables) / num_words, 4),
            "avg_word_zipf": round(float(np.mean(zipf_scores)), 4),
            "min_word_zipf": round(float(np.min(zipf_scores)), 4),
            "rare_word_ratio": round(sum(z < 4.0 for z in zipf_scores) / num_words, 4),
            "avg_word_cefr": round(float(np.mean(levels)), 4),
            "max_word_cefr": round(float(np.max(levels)), 4),
            "word_oov_ratio": round(oov_count / num_words, 4),
            "dep_tree_depth": tree_depth,
            "subclause_count": subclause_count,
            "subclause_ratio": round(subclause_count / num_words, 4),
            "passive_count": passive_count,
            "pos_noun_ratio": round(
                sum(pos in {"NOUN", "PROPN"} for pos in pos_tags) / num_words, 4
            ),
            "pos_verb_ratio": round(sum(pos in {"VERB", "AUX"} for pos in pos_tags) / num_words, 4),
            "pos_adj_ratio": round(sum(pos == "ADJ" for pos in pos_tags) / num_words, 4),
            "pos_adv_ratio": round(sum(pos == "ADV" for pos in pos_tags) / num_words, 4),
            "pos_adp_ratio": round(sum(pos == "ADP" for pos in pos_tags) / num_words, 4),
            "flesch_reading_ease": round(float(textstat.flesch_reading_ease(text)), 2),
            "flesch_kincaid_grade": round(float(textstat.flesch_kincaid_grade(text)), 2),
            "gunning_fog": round(float(textstat.gunning_fog(text)), 2),
            "automated_readability_index": round(
                float(textstat.automated_readability_index(text)), 2
            ),
            "dale_chall_score": round(float(textstat.dale_chall_readability_score(text)), 2),
        }
        frame = pd.DataFrame([values], columns=SENTENCE_FEATURE_COLUMNS)
        return frame.replace([np.inf, -np.inf], 0.0).fillna(0.0)

    def extract_many(self, sentences) -> pd.DataFrame:
        rows = [self.extract(sentence).iloc[0].to_dict() for sentence in sentences]
        return pd.DataFrame(rows, columns=SENTENCE_FEATURE_COLUMNS)

"""Create explicit word-conditioned training pairs for Model 3a."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

TOKEN_PATTERN = re.compile(r"\b[a-zA-Z]+(?:[-'][a-zA-Z]+)*\b")


def select_target_word(text: str, level: int, lookup: dict[str, float]) -> str | None:
    candidates = [
        token.lower()
        for token in TOKEN_PATTERN.findall(str(text))
        if len(token) >= 3 and token.lower() not in ENGLISH_STOP_WORDS
    ]
    if not candidates:
        return None
    known = [word for word in candidates if word in lookup]
    if known:
        # Prefer a word matching the sentence level, then a more informative
        # (longer) lexical item. Selection is deterministic and reproducible.
        return min(known, key=lambda word: (abs(lookup[word] - level), -len(word), word))
    return min(candidates, key=lambda word: (-len(word), word))


def build_pairs(sentences: pd.DataFrame, wordlist: pd.DataFrame) -> pd.DataFrame:
    lookup = wordlist.groupby(wordlist["word"].str.lower())["cefr_label"].mean().to_dict()
    records = []
    for row in sentences.itertuples(index=False):
        target_word = select_target_word(row.text, int(row.cefr_label), lookup)
        if not target_word:
            continue
        records.append(
            {
                "target_word": target_word,
                "target_level": row.cefr_level,
                "target_label": int(row.cefr_label),
                "prompt": f"generate: word={target_word} level={row.cefr_level}",
                "target_sentence": row.text,
                "source": row.source,
                "group_key": str(row.text).strip().lower(),
            }
        )
    result = pd.DataFrame(records)
    return result.drop_duplicates(["target_word", "target_sentence"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="data/processed/example_generation_pairs.csv")
    args = parser.parse_args()
    sentences = pd.read_csv("data/processed/example_sentences_with_readability.csv")
    wordlist = pd.read_csv("data/processed/cefr_wordlist_clean.csv")
    pairs = build_pairs(sentences, wordlist)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    pairs.to_csv(output, index=False, encoding="utf-8")
    coverage = len(pairs) / max(1, len(sentences))
    print(
        f"Wrote {len(pairs):,} word-conditioned pairs ({coverage:.1%} sentence coverage) "
        f"to {output}"
    )


if __name__ == "__main__":
    main()

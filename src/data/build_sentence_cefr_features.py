"""Build the shared linguistic feature table for sentence CEFR classification."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from src.features import SENTENCE_FEATURE_COLUMNS, SentenceFeatureExtractor


def build_sentence_feature_table(
    sentences: pd.DataFrame, extractor: SentenceFeatureExtractor
) -> pd.DataFrame:
    required = {"sentence_id", "text", "source", "cefr_level", "cefr_label"}
    missing = required.difference(sentences.columns)
    if missing:
        raise ValueError(f"Cleaned sentence data is missing columns: {sorted(missing)}")
    started = time.perf_counter()
    features = extractor.extract_many(sentences["text"].astype(str))
    metadata = sentences[["sentence_id", "text", "source", "cefr_level", "cefr_label"]].reset_index(
        drop=True
    )
    result = pd.concat(
        [
            metadata[["sentence_id", "text", "source"]],
            features[SENTENCE_FEATURE_COLUMNS],
            metadata[["cefr_level", "cefr_label"]],
        ],
        axis=1,
    )
    print(f"Extracted {len(result):,} rows in {time.perf_counter() - started:.1f}s")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="Process the complete cleaned corpus")
    parser.add_argument("--limit", type=int, default=100, help="Preview row count without --full")
    args = parser.parse_args()

    sentence_path = Path("data/processed/cefr_sentences_clean.csv")
    wordlist_path = Path("data/processed/cefr_wordlist_clean.csv")
    if not sentence_path.exists():
        raise FileNotFoundError(f"Missing {sentence_path}; clean sentence data first")
    if not wordlist_path.exists():
        raise FileNotFoundError(
            f"Missing auxiliary lexicon {wordlist_path}; prepare it or revise the feature schema"
        )

    sentences = pd.read_csv(sentence_path)
    selected = sentences if args.full else sentences.head(args.limit)
    extractor = SentenceFeatureExtractor.from_wordlist(wordlist_path)
    result = build_sentence_feature_table(selected, extractor)
    destination = Path(
        "data/processed/cefr_sentence_features.csv"
        if args.full
        else "data/processed/cefr_sentence_features_preview.csv"
    )
    result.to_csv(destination, index=False, encoding="utf-8")
    print(f"Wrote {destination}")


if __name__ == "__main__":
    main()

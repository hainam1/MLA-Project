"""Build Model 2b features with the shared serving extractor."""

from __future__ import annotations

import argparse
from pathlib import Path
import time

import pandas as pd

from src.features import SENTENCE_FEATURE_COLUMNS, SentenceFeatureExtractor

LABEL_MAPPING = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4}


def build_sentence_feature_table(
    sentences: pd.DataFrame, extractor: SentenceFeatureExtractor
) -> pd.DataFrame:
    started = time.time()
    features = extractor.extract_many(sentences["text"].astype(str))
    metadata = sentences[["text", "source", "cefr_level"]].reset_index(drop=True)
    metadata["cefr_label"] = metadata["cefr_level"].map(LABEL_MAPPING).astype(int)
    result = pd.concat(
        [
            metadata[["text", "source"]],
            features[SENTENCE_FEATURE_COLUMNS],
            metadata[["cefr_level", "cefr_label"]],
        ],
        axis=1,
    )
    print(f"Extracted {len(result):,} sentences in {time.time() - started:.1f}s")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="Process all rows")
    args = parser.parse_args()

    sentence_path = Path("data/processed/cefr_sentences_clean.csv")
    wordlist_path = Path("data/processed/cefr_wordlist_clean.csv")
    output_path = Path("data/processed/cefr_sentence_features.csv")
    preview_path = Path("data/processed/cefr_sentence_features_preview.csv")
    if not sentence_path.exists() or not wordlist_path.exists():
        raise FileNotFoundError("Run the cleaning stages before feature extraction")

    sentences = pd.read_csv(sentence_path)
    selected = sentences if args.full else sentences.head(100)
    extractor = SentenceFeatureExtractor.from_wordlist(wordlist_path)
    result = build_sentence_feature_table(selected, extractor)
    destination = output_path if args.full else preview_path
    result.to_csv(destination, index=False, encoding="utf-8")
    print(f"Wrote {destination}")


if __name__ == "__main__":
    main()

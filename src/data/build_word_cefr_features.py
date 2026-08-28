"""Build the leakage-safe feature table for Model 2a."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.features import WORD_FEATURE_COLUMNS
from src.features.word import extract_word_feature_table, normalize_word

LEVELS = ["A1", "A2", "B1", "B2", "C1"]


def build_word_feature_table(clean_words: pd.DataFrame) -> pd.DataFrame:
    """Collapse POS variants to one target per context-free word."""
    data = clean_words.copy()
    data["word"] = data["word"].map(normalize_word)
    data = data[data["word"].str.fullmatch(r"[a-z]+(?:[-'][a-z]+)*", na=False)]

    grouped = data.groupby("word", as_index=False).agg(
        teachers_avg=("teachers_avg", "mean"),
        cefr_label_mean=("cefr_label", "mean"),
        source_pos_count=("pos", "nunique"),
    )
    grouped["cefr_label"] = np.floor(grouped["cefr_label_mean"] + 0.5).astype(int)
    grouped["cefr_label"] = grouped["cefr_label"].clip(0, 4)
    grouped["cefr_level"] = grouped["cefr_label"].map(dict(enumerate(LEVELS)))

    features = extract_word_feature_table(grouped["word"])
    output = pd.concat(
        [
            grouped[["word"]].reset_index(drop=True),
            features,
            grouped[["teachers_avg", "source_pos_count", "cefr_level", "cefr_label"]].reset_index(
                drop=True
            ),
        ],
        axis=1,
    )
    expected = [
        "word",
        *WORD_FEATURE_COLUMNS,
        "teachers_avg",
        "source_pos_count",
        "cefr_level",
        "cefr_label",
    ]
    return output[expected]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="Write the full table")
    args = parser.parse_args()

    input_path = Path("data/processed/cefr_wordlist_clean.csv")
    output_path = Path("data/processed/cefr_word_features.csv")
    preview_path = Path("data/processed/cefr_word_features_preview.csv")
    if not input_path.exists():
        raise FileNotFoundError(f"Missing clean word list: {input_path}")

    result = build_word_feature_table(pd.read_csv(input_path))
    result.head(100).to_csv(preview_path, index=False, encoding="utf-8")
    if args.full:
        result.to_csv(output_path, index=False, encoding="utf-8")
    print(
        f"Built {len(result):,} unique words with {len(WORD_FEATURE_COLUMNS)} "
        "serving-safe features."
    )


if __name__ == "__main__":
    main()

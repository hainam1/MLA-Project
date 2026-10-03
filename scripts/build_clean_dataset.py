"""Clean and standardize ELLIPSE dataset CSVs into easy-to-use, canonical tables.

This script reads the original ELLIPSE corpus and the frozen split manifest,
normalizes columns to standard snake_case, cleans text with Unicode NFKC,
and produces four clearly named, ready-to-use datasets:
  - data/03_clean_ready_to_use/model_train_3128.csv
  - data/03_clean_ready_to_use/validation_783.csv
  - data/03_clean_ready_to_use/official_test_2571.csv
  - data/03_clean_ready_to_use/full_clean_corpus_6482.csv
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

import pandas as pd

from mla_project.features.preprocessing import clean_text
from mla_project.utils.paths import PROJECT_ROOT

logger = logging.getLogger("build_clean_dataset")

RAW_COLUMN_MAP = {
    "text_id_kaggle": "essay_id",
    "prompt": "prompt",
    "full_text": "essay_text",
    "Vocabulary": "vocabulary",
    "Grammar": "grammar",
    "Overall": "overall",
    "Cohesion": "cohesion",
    "Syntax": "syntax",
    "Phraseology": "phraseology",
    "Conventions": "conventions",
    "SES": "ses",
    "gender": "gender",
    "grade": "grade",
    "race_ethnicity": "race_ethnicity",
}

CANONICAL_COLUMNS = [
    "essay_id",
    "prompt",
    "essay_text",
    "clean_text",
    "vocabulary",
    "grammar",
    "overall",
    "cohesion",
    "syntax",
    "phraseology",
    "conventions",
    "grade",
    "gender",
    "race_ethnicity",
    "ses",
    "split",
    "cv_fold",
    "source_partition",
    "privacy_review_status",
]

SUBSET_COLUMNS = [
    "essay_id",
    "prompt",
    "essay_text",
    "clean_text",
    "vocabulary",
    "grammar",
    "overall",
    "cohesion",
    "syntax",
    "phraseology",
    "conventions",
    "grade",
    "gender",
    "race_ethnicity",
    "ses",
]


def build_clean_datasets(
    raw_dir: Path | None = None,
    splits_file: Path | None = None,
    clean_dir: Path | None = None,
) -> dict[str, Path]:
    """Load raw ELLIPSE datasets, standardize schema, clean text, and export clean CSVs."""
    raw_dir = raw_dir or PROJECT_ROOT / "data" / "01_original_source" / "official_corpus"
    splits_file = (
        splits_file
        or PROJECT_ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
    )
    clean_dir = clean_dir or PROJECT_ROOT / "data" / "03_clean_ready_to_use"

    train_raw_path = raw_dir / "ELLIPSE_Final_github_train.csv"
    test_raw_path = raw_dir / "ELLIPSE_Final_github_test.csv"

    if not train_raw_path.exists():
        raise FileNotFoundError(f"Raw train file not found: {train_raw_path}")
    if not test_raw_path.exists():
        raise FileNotFoundError(f"Raw test file not found: {test_raw_path}")
    if not splits_file.exists():
        raise FileNotFoundError(f"Split manifest not found: {splits_file}")

    logger.info("Loading raw ELLIPSE snapshots and split manifest...")
    train_raw = pd.read_csv(train_raw_path, dtype={"text_id_kaggle": str})
    test_raw = pd.read_csv(test_raw_path, dtype={"text_id_kaggle": str})
    split_manifest = pd.read_csv(splits_file, dtype={"essay_id": str})

    raw_combined = pd.concat([train_raw, test_raw], ignore_index=True)
    raw_combined = raw_combined.rename(columns=RAW_COLUMN_MAP)

    logger.info("Merging with frozen split manifest...")
    merged = raw_combined.merge(
        split_manifest[["essay_id", "split", "cv_fold", "source_partition", "privacy_review_status"]],
        on="essay_id",
        how="inner",
    )

    if len(merged) != len(split_manifest):
        raise ValueError(
            f"Row count mismatch after merge: got {len(merged)}, expected {len(split_manifest)}"
        )

    logger.info("Cleaning essay text (Unicode NFKC + whitespace normalization)...")
    merged["essay_text"] = merged["essay_text"].astype(str).str.strip()
    merged["clean_text"] = merged["essay_text"].apply(clean_text)
    merged["cv_fold"] = merged["cv_fold"].astype("Int64")
    merged["grade"] = merged["grade"].astype(int)

    # Ensure float for score columns
    score_cols = ["vocabulary", "grammar", "overall", "cohesion", "syntax", "phraseology", "conventions"]
    for col in score_cols:
        merged[col] = merged[col].astype(float)

    clean_all = merged[CANONICAL_COLUMNS].copy()

    # Create destination directories
    clean_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}

    # 1. Full clean corpus
    all_path = clean_dir / "full_clean_corpus_6482.csv"
    clean_all.to_csv(all_path, index=False, encoding="utf-8")
    outputs["all"] = all_path
    logger.info("Saved all clean essays to %s (%d rows)", all_path, len(clean_all))

    # 2. Model train partition (with cv_fold)
    train_df = clean_all[clean_all["split"] == "model_train"].copy()
    train_cols = SUBSET_COLUMNS + ["cv_fold"]
    train_path = clean_dir / "model_train_3128.csv"
    train_df[train_cols].to_csv(train_path, index=False, encoding="utf-8")
    outputs["train"] = train_path
    logger.info("Saved clean train dataset to %s (%d rows)", train_path, len(train_df))

    # 3. Validation partition
    val_df = clean_all[clean_all["split"] == "validation"].copy()
    val_path = clean_dir / "validation_783.csv"
    val_df[SUBSET_COLUMNS].to_csv(val_path, index=False, encoding="utf-8")
    outputs["val"] = val_path
    logger.info("Saved clean val dataset to %s (%d rows)", val_path, len(val_df))

    # 4. Official test partition
    test_df = clean_all[clean_all["split"] == "official_test"].copy()
    test_path = clean_dir / "official_test_2571.csv"
    test_df[SUBSET_COLUMNS].to_csv(test_path, index=False, encoding="utf-8")
    outputs["test"] = test_path
    logger.info("Saved clean test dataset to %s (%d rows)", test_path, len(test_df))

    return outputs


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Build clean, standardized ELLIPSE datasets.")
    parser.add_argument("--raw-dir", type=Path, default=None, help="Directory containing source CSVs")
    parser.add_argument(
        "--splits-file", type=Path, default=None, help="Path to essay_split_manifest.csv"
    )
    parser.add_argument("--clean-dir", type=Path, default=None, help="Output directory for clean CSVs")

    args = parser.parse_args()
    build_clean_datasets(
        raw_dir=args.raw_dir,
        splits_file=args.splits_file,
        clean_dir=args.clean_dir,
    )
    logger.info("Dataset cleaning and organization complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

from pathlib import Path
import pytest
import pandas as pd

from mla_project.data.load_data import load_clean_data
from mla_project.features.preprocessing import clean_text
from mla_project.utils.paths import PROJECT_ROOT

CLEAN_DIR = PROJECT_ROOT / "data" / "03_clean_ready_to_use"

EXPECTED_COUNTS = {
    "train": 3128,
    "val": 783,
    "test": 2571,
    "all": 6482,
}

CORE_COLUMNS = [
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


def test_clean_files_exist():
    assert (CLEAN_DIR / "model_train_3128.csv").is_file()
    assert (CLEAN_DIR / "validation_783.csv").is_file()
    assert (CLEAN_DIR / "official_test_2571.csv").is_file()
    assert (CLEAN_DIR / "full_clean_corpus_6482.csv").is_file()


def test_clean_row_counts_match_splits():
    train_df = load_clean_data("train")
    val_df = load_clean_data("val")
    test_df = load_clean_data("test")
    all_df = load_clean_data("all")

    assert len(train_df) == EXPECTED_COUNTS["train"]
    assert len(val_df) == EXPECTED_COUNTS["val"]
    assert len(test_df) == EXPECTED_COUNTS["test"]
    assert len(all_df) == EXPECTED_COUNTS["all"]
    assert len(train_df) + len(val_df) + len(test_df) == EXPECTED_COUNTS["all"]


def test_schema_and_column_integrity():
    train_df = load_clean_data("train")
    assert set(CORE_COLUMNS).issubset(train_df.columns)
    assert "cv_fold" in train_df.columns

    # essay_id uniqueness
    assert train_df["essay_id"].is_unique
    assert not train_df["essay_id"].isna().any()

    # Targets in [1.0, 5.0]
    for target in ["vocabulary", "grammar", "overall"]:
        assert train_df[target].dtype.kind == "f"
        assert (train_df[target] >= 1.0).all()
        assert (train_df[target] <= 5.0).all()

    # Text non-empty
    assert (train_df["essay_text"].str.strip() != "").all()
    assert (train_df["clean_text"].str.strip() != "").all()


def test_clean_train_folds_are_balanced():
    train_df = load_clean_data("train")
    fold_counts = train_df["cv_fold"].value_counts()
    assert set(fold_counts.index) == {0, 1, 2, 3, 4}
    for count in fold_counts.values:
        assert 620 <= count <= 630


def test_load_clean_data_rejects_unknown_split():
    with pytest.raises(ValueError, match="Unknown split"):
        load_clean_data("non_existent_split")

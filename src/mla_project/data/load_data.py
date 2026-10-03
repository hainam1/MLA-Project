"""Load untouched ELLIPSE source files into the canonical schema."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from mla_project.data.validate_data import validate_ellipse_schema

ELLIPSE_COLUMN_MAP = {
    "text_id_kaggle": "essay_id",
    "full_text": "essay_text",
    "prompt": "prompt_id",
}


def load_ellipse(path: str | Path, *, require_targets: bool = True) -> pd.DataFrame:
    """Read an ELLIPSE CSV without altering the source file."""
    data_path = Path(path)
    if not data_path.is_file():
        raise FileNotFoundError(f"ELLIPSE file not found: {data_path}")
    if data_path.suffix.lower() != ".csv":
        raise ValueError("ELLIPSE input must be a CSV file.")
    frame = pd.read_csv(data_path).rename(columns=ELLIPSE_COLUMN_MAP)
    return validate_ellipse_schema(frame, require_targets=require_targets)


def load_clean_data(
    split: str = "train",
    *,
    base_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Load a standardized clean dataset partition ('train', 'val', 'test', 'all')."""
    from mla_project.utils.paths import PROJECT_ROOT

    clean_dir = Path(base_dir) if base_dir else PROJECT_ROOT / "data" / "03_clean_ready_to_use"
    filename_map = {
        "train": "model_train_3128.csv",
        "val": "validation_783.csv",
        "validation": "validation_783.csv",
        "test": "official_test_2571.csv",
        "official_test": "official_test_2571.csv",
        "all": "full_clean_corpus_6482.csv",
    }
    split_key = split.lower().strip()
    if split_key not in filename_map:
        raise ValueError(
            f"Unknown split: {split!r}. Available: {list(filename_map.keys())}"
        )

    file_path = clean_dir / filename_map[split_key]
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Clean dataset file not found at {file_path}. Run `scripts/build_clean_dataset.py` first."
        )

    return pd.read_csv(file_path, dtype={"essay_id": str})

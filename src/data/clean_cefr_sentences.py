"""Clean UniversalCEFR English sentence data and emit a reproducible audit."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

LABEL_MAPPING = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4}
VALID_LEVELS = tuple(LABEL_MAPPING)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 checksum without loading a whole file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFC", value)
    return re.sub(r"\s+", " ", normalized).strip()


def normalized_text_key(value: object) -> str:
    return normalize_text(value).casefold()


def clean_corpus(frame: pd.DataFrame, source_name: str) -> tuple[pd.DataFrame, dict]:
    required = {"text", "cefr_level"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{source_name} is missing columns: {sorted(missing)}")

    working = frame[["text", "cefr_level"]].copy()
    working["text"] = working["text"].map(normalize_text)
    working["text_key"] = working["text"].map(normalized_text_key)
    working["cefr_level"] = working["cefr_level"].astype(str).str.strip().str.upper()

    empty = int((working["text"] == "").sum())
    c2 = int((working["cefr_level"] == "C2").sum())
    invalid = int((~working["cefr_level"].isin((*VALID_LEVELS, "C2"))).sum())
    eligible = working[(working["text"] != "") & working["cefr_level"].isin(VALID_LEVELS)]

    kept: list[dict] = []
    duplicate_rows = 0
    conflicts = 0
    conflicting_rows = 0
    for text_key, group in eligible.groupby("text_key", sort=True):
        levels = sorted(group["cefr_level"].unique())
        if len(levels) != 1:
            conflicts += 1
            conflicting_rows += len(group)
            continue
        duplicate_rows += len(group) - 1
        text = group.iloc[0]["text"]
        level = levels[0]
        sentence_id = hashlib.sha256(f"{source_name}\0{text_key}".encode("utf-8")).hexdigest()[:16]
        kept.append(
            {
                "sentence_id": sentence_id,
                "text": text,
                "source": source_name,
                "cefr_level": level,
                "cefr_label": LABEL_MAPPING[level],
            }
        )

    cleaned = pd.DataFrame(kept)
    audit = {
        "source": source_name,
        "raw_rows": int(len(frame)),
        "empty_rows": empty,
        "excluded_c2_rows": c2,
        "invalid_label_rows": invalid,
        "merged_duplicate_rows": int(duplicate_rows),
        "conflicting_text_groups": int(conflicts),
        "conflicting_label_rows": int(conflicting_rows),
        "retained_rows": int(len(cleaned)),
    }
    return cleaned, audit


def combine_corpora(corpora: list[pd.DataFrame]) -> tuple[pd.DataFrame, dict]:
    combined = pd.concat(corpora, ignore_index=True)
    combined["text_key"] = combined["text"].map(normalized_text_key)
    conflicts = combined.groupby("text_key")["cefr_level"].nunique()
    conflict_keys = set(conflicts[conflicts > 1].index)
    cross_source_conflicts = int(len(conflict_keys))
    cross_source_conflict_rows = int(combined["text_key"].isin(conflict_keys).sum())
    if conflict_keys:
        combined = combined[~combined["text_key"].isin(conflict_keys)].copy()

    cross_source_duplicate_rows = int(combined.duplicated(subset=["text_key"]).sum())
    combined = combined.sort_values(["text_key", "source"]).drop_duplicates(subset=["text_key"])
    combined["sentence_id"] = combined["text_key"].map(
        lambda key: hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    )
    combined = combined.drop(columns="text_key").reset_index(drop=True)
    audit = {
        "cross_source_conflicting_text_groups": cross_source_conflicts,
        "cross_source_conflicting_label_rows": cross_source_conflict_rows,
        "merged_cross_source_duplicate_rows": cross_source_duplicate_rows,
        "retained_rows": int(len(combined)),
        "label_counts": {
            level: int((combined["cefr_level"] == level).sum()) for level in VALID_LEVELS
        },
        "source_counts": {
            str(source): int(count)
            for source, count in combined["source"].value_counts().sort_index().items()
        },
    }
    return combined, audit


def plot_distribution(frame: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    counts = frame["cefr_level"].value_counts().reindex(VALID_LEVELS, fill_value=0)
    sns.set_theme(style="whitegrid")
    figure, axis = plt.subplots(figsize=(9, 5.5), dpi=200)
    sns.barplot(x=list(counts.index), y=list(counts.values), ax=axis, color="#4C78A8")
    axis.set(title="English sentence CEFR distribution", xlabel="CEFR level", ylabel="Sentences")
    for index, count in enumerate(counts.values):
        axis.text(index, count, f"{count:,}", ha="center", va="bottom")
    figure.tight_layout()
    figure.savefig(destination)
    plt.close(figure)


def main() -> None:
    sources = {
        "cefr_sp_en": Path("data/raw/cefr_sentence/cefr_sp_en_train.csv"),
        "readme_en": Path("data/raw/cefr_sentence/readme_en_train.csv"),
    }
    cleaned_frames: list[pd.DataFrame] = []
    source_audits: list[dict] = []
    for source_name, path in sources.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}; run src.data.download_datasets first")
        cleaned, audit = clean_corpus(pd.read_csv(path), source_name)
        audit["raw_file"] = path.as_posix()
        audit["raw_file_sha256"] = sha256_file(path)
        cleaned_frames.append(cleaned)
        source_audits.append(audit)

    combined, combined_audit = combine_corpora(cleaned_frames)
    output = Path("data/processed/cefr_sentences_clean.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output, index=False, encoding="utf-8")
    combined_audit["cleaned_file"] = output.as_posix()
    combined_audit["cleaned_file_sha256"] = sha256_file(output)

    audit = {"sources": source_audits, "combined": combined_audit}
    Path("data/processed/data_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    plot_distribution(combined, Path("reports/figures/cefr_sentence_distribution.png"))
    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

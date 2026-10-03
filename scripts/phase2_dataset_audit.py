"""Reproducible Phase 2 audit of the local ELLIPSE source snapshot.

This script reads raw files without modifying them and writes only aggregate evidence.
It deliberately does not train or fit a prediction model.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_CORPUS = ROOT / "data" / "01_original_source" / "official_corpus"
RATER_SCORES = ROOT / "data" / "01_original_source" / "rater_scores"
TABLES = ROOT / "docs" / "data" / "phase2_tables"
FIGURES = ROOT / "docs" / "assets"

FINAL_FILES = {
    "official_train": OFFICIAL_CORPUS / "ELLIPSE_Final_github_train.csv",
    "official_test": OFFICIAL_CORPUS / "ELLIPSE_Final_github_test.csv",
}
RAW_RATER_FILE = RATER_SCORES / "ellipsis_raw_rater_scores_anon_all_essay.csv"
ALL_FILES = FINAL_FILES | {"raw_rater": RAW_RATER_FILE}

WORD_RE = re.compile(r"\b\w+(?:['\u2019-]\w+)*\b", flags=re.UNICODE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def normalize_text(text: object) -> str:
    return re.sub(r"\s+", " ", str(text).strip().casefold())


def word_count(text: object) -> int:
    return len(WORD_RE.findall(str(text)))


def load_sources() -> dict[str, pd.DataFrame]:
    return {name: pd.read_csv(path, low_memory=False) for name, path in ALL_FILES.items()}


def build_file_inventory(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for name, path in ALL_FILES.items():
        frame = frames[name]
        text_column = "full_text" if name != "raw_rater" else "Text"
        id_column = "text_id_kaggle"
        canonical_complete: int | None = None
        both_raters_complete: int | None = None
        if name != "raw_rater":
            canonical_complete = int(
                (
                    frame[text_column].notna()
                    & frame[text_column].astype(str).str.strip().ne("")
                    & frame["Vocabulary"].notna()
                    & frame["Grammar"].notna()
                ).sum()
            )
        else:
            both_raters_complete = int(
                (
                    frame[text_column].notna()
                    & frame[text_column].astype(str).str.strip().ne("")
                    & frame[["Vocabulary_1", "Vocabulary_2", "Grammar_1", "Grammar_2"]]
                    .notna()
                    .all(axis=1)
                ).sum()
            )
        rows.append(
            {
                "file_role": name,
                "file": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "rows": len(frame),
                "columns": len(frame.columns),
                "id_column": id_column,
                "text_column": text_column,
                "rows_with_nonblank_text": int(
                    (
                        frame[text_column].notna()
                        & frame[text_column].astype(str).str.strip().ne("")
                    ).sum()
                ),
                "rows_complete_text_vocabulary_grammar": canonical_complete,
                "rows_complete_both_rater_vocab_grammar": both_raters_complete,
            }
        )
    return pd.DataFrame(rows)


def build_column_profile(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for name, frame in frames.items():
        for column in frame.columns:
            series = frame[column]
            rows.append(
                {
                    "file_role": name,
                    "column": column,
                    "dtype": str(series.dtype),
                    "non_null": int(series.notna().sum()),
                    "missing": int(series.isna().sum()),
                    "unique_non_null": int(series.nunique(dropna=True)),
                }
            )
    return pd.DataFrame(rows)


def build_score_distribution(final: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for split, split_frame in final.groupby("source_split", sort=False):
        for target in ("Vocabulary", "Grammar"):
            counts = split_frame[target].value_counts(dropna=False).sort_index()
            for score, count in counts.items():
                rows.append(
                    {
                        "source_split": split,
                        "target": target,
                        "score": score,
                        "count": int(count),
                        "percent": round(100 * int(count) / len(split_frame), 4),
                    }
                )
    return pd.DataFrame(rows)


def best_near_duplicate_pairs(final: pd.DataFrame) -> pd.DataFrame:
    normalized = final["normalized_text"]
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(5, 5),
        lowercase=False,
        min_df=2,
        sublinear_tf=True,
        dtype=np.float32,
    )
    matrix = vectorizer.fit_transform(normalized)
    neighbors = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=3, n_jobs=-1)
    neighbors.fit(matrix)
    distances, indices = neighbors.kneighbors(matrix)

    pairs: dict[tuple[int, int], float] = {}
    for row_index, (row_distances, row_indices) in enumerate(zip(distances, indices, strict=True)):
        for distance, neighbor_index in zip(row_distances, row_indices, strict=True):
            if neighbor_index == row_index:
                continue
            left, right = sorted((row_index, int(neighbor_index)))
            similarity = float(1.0 - distance)
            if similarity >= 0.95:
                pairs[(left, right)] = max(similarity, pairs.get((left, right), 0.0))
            break

    columns = [
        "left_id",
        "right_id",
        "left_split",
        "right_split",
        "cosine_similarity_char_5gram_tfidf",
        "left_words",
        "right_words",
    ]
    rows: list[dict[str, object]] = []
    for (left, right), similarity in sorted(pairs.items(), key=lambda item: -item[1]):
        left_row = final.iloc[left]
        right_row = final.iloc[right]
        rows.append(
            {
                "left_id": left_row["text_id_kaggle"],
                "right_id": right_row["text_id_kaggle"],
                "left_split": left_row["source_split"],
                "right_split": right_row["source_split"],
                "cosine_similarity_char_5gram_tfidf": round(similarity, 6),
                "left_words": int(left_row["computed_word_count"]),
                "right_words": int(right_row["computed_word_count"]),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def build_target_summary(final: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for split, split_frame in final.groupby("source_split", sort=False):
        for target in ("Vocabulary", "Grammar"):
            values = split_frame[target]
            rows.append(
                {
                    "source_split": split,
                    "target": target,
                    "rows": len(values),
                    "missing": int(values.isna().sum()),
                    "minimum": float(values.min()),
                    "q1": float(values.quantile(0.25)),
                    "median": float(values.median()),
                    "mean": round(float(values.mean()), 6),
                    "q3": float(values.quantile(0.75)),
                    "maximum": float(values.max()),
                    "distinct_values": int(values.nunique(dropna=True)),
                }
            )
    return pd.DataFrame(rows)


def build_text_quality_by_split(final: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for split, split_frame in final.groupby("source_split", sort=False):
        words = split_frame["computed_word_count"]
        rows.append(
            {
                "source_split": split,
                "rows": len(split_frame),
                "blank_text": int(split_frame["normalized_text"].eq("").sum()),
                "under_50_words": int(words.lt(50).sum()),
                "under_100_words": int(words.lt(100).sum()),
                "minimum_words": int(words.min()),
                "q1_words": float(words.quantile(0.25)),
                "median_words": float(words.median()),
                "q3_words": float(words.quantile(0.75)),
                "maximum_words": int(words.max()),
            }
        )
    return pd.DataFrame(rows)


def build_raw_rater_score_summary(raw_rater: pd.DataFrame) -> pd.DataFrame:
    score_columns = [
        column
        for column in raw_rater.columns
        if re.fullmatch(
            r"(Overall|Cohesion|Syntax|Vocabulary|Phraseology|Grammar|Conventions)_[12]",
            column,
        )
    ]
    rows: list[dict[str, object]] = []
    for column in score_columns:
        values = raw_rater[column]
        rows.append(
            {
                "column": column,
                "rows": len(values),
                "missing": int(values.isna().sum()),
                "minimum": float(values.min()),
                "maximum": float(values.max()),
                "zero_count": int(values.eq(0).sum()),
                "distinct_values": int(values.nunique(dropna=True)),
            }
        )
    return pd.DataFrame(rows)


def build_column_usage_catalog() -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    rows.extend(
        [
            {
                "column": "full_text",
                "class": "raw model input",
                "model_use": "allowed",
                "rule": "Only source field used to derive model features.",
            },
            {
                "column": "text_id_kaggle",
                "class": "identifier",
                "model_use": "not a feature",
                "rule": "Tracking, joins, deterministic tie-break, and split manifests only.",
            },
        ]
    )
    for column in (
        "num_words",
        "num_words2",
        "num_words3",
        "num_sent",
        "num_para",
        "num_word_div_para",
        "MTLD",
        "TTR",
        "Type",
        "Token",
    ):
        rows.append(
            {
                "column": column,
                "class": "source-precomputed text feature",
                "model_use": "audit-only by default",
                "rule": "May validate the local extractor, but is not fed to models; train/inference features are recomputed from full_text.",
            }
        )
    for column in ("task", "prompt", "set"):
        rows.append(
            {
                "column": column,
                "class": "context/split metadata",
                "model_use": "not a feature",
                "rule": "Dataset audit, split verification, and slice analysis only.",
            }
        )
    for column in ("gender", "grade", "race_ethnicity", "SES"):
        rows.append(
            {
                "column": column,
                "class": "demographic",
                "model_use": "prohibited",
                "rule": "Fairness/subgroup audit only with responsible-use safeguards.",
            }
        )
    for column in (
        "Overall",
        "Cohesion",
        "Syntax",
        "Vocabulary",
        "Phraseology",
        "Grammar",
        "Conventions",
    ):
        target_note = "target only" if column in {"Vocabulary", "Grammar"} else "prohibited"
        rows.append(
            {
                "column": column,
                "class": "human score/label",
                "model_use": target_note,
                "rule": "Never an input feature. Vocabulary and Grammar are labels; all other scores are excluded.",
            }
        )
    return pd.DataFrame(rows)


def save_score_plot(distribution: pd.DataFrame) -> None:
    scores = np.arange(1.0, 5.01, 0.5)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    colors = {"official_train": "#2563EB", "official_test": "#F97316"}
    for axis, target in zip(axes, ("Vocabulary", "Grammar"), strict=True):
        target_data = distribution[distribution["target"] == target]
        x = np.arange(len(scores))
        width = 0.38
        for offset, split in zip((-width / 2, width / 2), FINAL_FILES, strict=True):
            values = (
                target_data[target_data["source_split"] == split]
                .set_index("score")["percent"]
                .reindex(scores, fill_value=0)
            )
            axis.bar(x + offset, values, width=width, label=split, color=colors[split])
        axis.set_title(target)
        axis.set_xticks(x, [f"{score:g}" for score in scores])
        axis.set_xlabel("Human score")
        axis.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Essays within source split (%)")
    axes[1].legend(frameon=False)
    fig.suptitle("ELLIPSE Vocabulary and Grammar score distributions")
    fig.tight_layout()
    fig.savefig(FIGURES / "phase2_score_distributions.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_length_plot(final: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    colors = {"official_train": "#2563EB", "official_test": "#F97316"}
    for split in FINAL_FILES:
        subset = final.loc[final["source_split"] == split, "computed_word_count"]
        axes[0].hist(subset, bins=50, alpha=0.55, label=split, color=colors[split])
    axes[0].set_title("Computed word-count distribution")
    axes[0].set_xlabel("Words")
    axes[0].set_ylabel("Essays")
    axes[0].legend(frameon=False)
    axes[0].grid(axis="y", alpha=0.2)

    grouped = [
        final.loc[final["source_split"] == split, "computed_word_count"].to_numpy()
        for split in FINAL_FILES
    ]
    axes[1].boxplot(grouped, tick_labels=list(FINAL_FILES), showfliers=False)
    axes[1].set_title("Word counts without outlier markers")
    axes[1].set_ylabel("Words")
    axes[1].grid(axis="y", alpha=0.2)
    fig.suptitle("ELLIPSE text-length audit")
    fig.tight_layout()
    fig.savefig(FIGURES / "phase2_text_lengths.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    frames = load_sources()

    final_parts = []
    for split, frame in ((name, frames[name].copy()) for name in FINAL_FILES):
        frame.insert(0, "source_split", split)
        final_parts.append(frame)
    final = pd.concat(final_parts, ignore_index=True)
    final["normalized_text"] = final["full_text"].map(normalize_text)
    final["computed_word_count"] = final["full_text"].map(word_count)

    inventory = build_file_inventory(frames)
    columns = build_column_profile(frames)
    scores = build_score_distribution(final)
    target_summary = build_target_summary(final)
    text_quality = build_text_quality_by_split(final)
    raw_rater_scores = build_raw_rater_score_summary(frames["raw_rater"])
    near_duplicates = best_near_duplicate_pairs(final)
    usage = build_column_usage_catalog()

    normalized_group_sizes = final.groupby("normalized_text", dropna=False).size()
    id_group_sizes = final.groupby("text_id_kaggle", dropna=False).size()
    raw_ids = set(frames["raw_rater"]["text_id_kaggle"].dropna().astype(str))
    final_ids = set(final["text_id_kaggle"].dropna().astype(str))
    raw_rater = frames["raw_rater"]
    raw_scientific_ids = (
        raw_rater["text_id_kaggle"]
        .astype(str)
        .str.contains(r"^[0-9.]+E\+[0-9]+$", case=False, regex=True, na=False)
    )
    linked_privacy = final[["text_id_kaggle"]].merge(
        raw_rater[["text_id_kaggle", "Identifying_Info_1", "Identifying_Info_2"]],
        on="text_id_kaggle",
        how="left",
    )
    linked_identifying_flag = linked_privacy["Identifying_Info_1"].eq(1) | linked_privacy[
        "Identifying_Info_2"
    ].eq(1)
    summary = {
        "audit_date": "2026-09-23",
        "final_rows": int(len(final)),
        "official_train_rows": int(len(frames["official_train"])),
        "official_test_rows": int(len(frames["official_test"])),
        "raw_rater_rows": int(len(frames["raw_rater"])),
        "blank_text_rows": int(final["normalized_text"].eq("").sum()),
        "missing_vocabulary_rows": int(final["Vocabulary"].isna().sum()),
        "missing_grammar_rows": int(final["Grammar"].isna().sum()),
        "under_50_word_rows": int(final["computed_word_count"].lt(50).sum()),
        "under_100_word_rows": int(final["computed_word_count"].lt(100).sum()),
        "minimum_words": int(final["computed_word_count"].min()),
        "median_words": float(final["computed_word_count"].median()),
        "maximum_words": int(final["computed_word_count"].max()),
        "duplicate_id_groups": int(id_group_sizes.gt(1).sum()),
        "exact_duplicate_text_groups": int(normalized_group_sizes.gt(1).sum()),
        "rows_in_exact_duplicate_text_groups": int(
            normalized_group_sizes[normalized_group_sizes.gt(1)].sum()
        ),
        "near_duplicate_pairs_at_0_95": int(len(near_duplicates)),
        "cross_split_near_duplicate_pairs_at_0_95": int(
            (
                near_duplicates.get("left_split", pd.Series(dtype=str))
                != near_duplicates.get("right_split", pd.Series(dtype=str))
            ).sum()
        ),
        "distinct_prompt_strings": int(final["prompt"].nunique(dropna=True)),
        "missing_prompt_rows": int(final["prompt"].isna().sum()),
        "writer_id_available": False,
        "final_ids_found_in_raw_rater_file": int(len(final_ids & raw_ids)),
        "final_ids_not_found_in_raw_rater_file": int(len(final_ids - raw_ids)),
        "raw_rater_ids_in_scientific_notation": int(raw_scientific_ids.sum()),
        "raw_rater_identifying_info_1_flagged": int(raw_rater["Identifying_Info_1"].eq(1).sum()),
        "raw_rater_identifying_info_2_flagged": int(raw_rater["Identifying_Info_2"].eq(1).sum()),
        "linkable_final_rows_flagged_by_either_rater": int(linked_identifying_flag.sum()),
        "vocabulary_values": sorted(final["Vocabulary"].dropna().unique().tolist()),
        "grammar_values": sorted(final["Grammar"].dropna().unique().tolist()),
    }

    quality_rows = [
        {"metric": key, "value": value}
        for key, value in summary.items()
        if key not in {"vocabulary_values", "grammar_values"}
    ]

    inventory.to_csv(TABLES / "file_inventory.csv", index=False)
    columns.to_csv(TABLES / "column_profile.csv", index=False)
    scores.to_csv(TABLES / "score_distribution.csv", index=False)
    target_summary.to_csv(TABLES / "target_summary.csv", index=False)
    text_quality.to_csv(TABLES / "text_quality_by_split.csv", index=False)
    raw_rater_scores.to_csv(TABLES / "raw_rater_score_summary.csv", index=False)
    pd.DataFrame(quality_rows).to_csv(TABLES / "quality_summary.csv", index=False)
    usage.to_csv(TABLES / "column_usage_catalog.csv", index=False)
    near_duplicates.to_csv(TABLES / "near_duplicate_pairs.csv", index=False)
    final.loc[
        final["computed_word_count"].lt(100),
        ["source_split", "text_id_kaggle", "computed_word_count"],
    ].sort_values(["computed_word_count", "source_split", "text_id_kaggle"]).to_csv(
        TABLES / "short_text_ids_under_100_words.csv", index=False
    )
    (TABLES / "audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    save_score_plot(scores)
    save_length_plot(final)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

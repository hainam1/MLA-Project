"""Build the frozen Phase 3 split manifest and leakage audit.

The script uses target values only from the official training file. The official test file is
loaded without score columns and is never repartitioned. No prediction model is trained.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedGroupKFold, train_test_split
from sklearn.neighbors import NearestNeighbors

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_CORPUS = ROOT / "data" / "01_original_source" / "official_corpus"
RATER_SCORES = ROOT / "data" / "01_original_source" / "rater_scores"
SPLITS = ROOT / "data" / "02_split_manifest"
TABLES = ROOT / "docs" / "data" / "phase3_tables"

TRAIN_PATH = OFFICIAL_CORPUS / "ELLIPSE_Final_github_train.csv"
TEST_PATH = OFFICIAL_CORPUS / "ELLIPSE_Final_github_test.csv"
RAW_RATER_PATH = RATER_SCORES / "ellipsis_raw_rater_scores_anon_all_essay.csv"

SEED = 42
VALIDATION_SIZE = 0.20
CV_FOLDS = 5
NEAR_DUPLICATE_THRESHOLD = 0.95
TARGETS = ("Vocabulary", "Grammar")


def normalize_text(text: object) -> str:
    return re.sub(r"\s+", " ", str(text).strip().casefold())


def text_hash(text: object) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_columns = ["text_id_kaggle", "full_text", "prompt", *TARGETS, "set"]
    test_columns = ["text_id_kaggle", "full_text", "prompt", "set"]
    raw_rater_columns = ["text_id_kaggle", "Identifying_Info_1", "Identifying_Info_2"]
    train = pd.read_csv(TRAIN_PATH, usecols=train_columns)
    # Deliberately excludes all official-test score columns.
    test = pd.read_csv(TEST_PATH, usecols=test_columns)
    raw_rater = pd.read_csv(RAW_RATER_PATH, usecols=raw_rater_columns, low_memory=False)
    return train, test, raw_rater


def assign_development_split(train: pd.DataFrame) -> pd.DataFrame:
    result = train.copy()
    result["normalized_text_hash"] = result["full_text"].map(text_hash)
    group_rows: list[dict[str, object]] = []
    for hash_value, group in result.groupby("normalized_text_hash", sort=True):
        prompt_counts = group["prompt"].value_counts(dropna=False)
        group_rows.append(
            {
                "normalized_text_hash": hash_value,
                "stratify_prompt": str(prompt_counts.index[0]),
                "group_size": len(group),
                "prompt_values_in_group": int(group["prompt"].nunique(dropna=False)),
            }
        )
    groups = pd.DataFrame(group_rows)
    model_groups, validation_groups = train_test_split(
        groups["normalized_text_hash"],
        test_size=VALIDATION_SIZE,
        random_state=SEED,
        stratify=groups["stratify_prompt"],
    )
    validation_hashes = set(validation_groups)
    result["split"] = np.where(
        result["normalized_text_hash"].isin(validation_hashes),
        "validation",
        "model_train",
    )
    result.attrs["multi_prompt_duplicate_groups"] = int(
        groups["prompt_values_in_group"].gt(1).sum()
    )
    result.attrs["duplicate_text_groups"] = int(groups["group_size"].gt(1).sum())
    return result


def assign_cv_folds(development: pd.DataFrame) -> pd.DataFrame:
    result = development.copy()
    result["cv_fold"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    model_mask = result["split"].eq("model_train")
    model_rows = result.loc[model_mask]
    splitter = StratifiedGroupKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED)
    for fold, (_, holdout_positions) in enumerate(
        splitter.split(
            model_rows,
            y=model_rows["prompt"],
            groups=model_rows["normalized_text_hash"],
        )
    ):
        holdout_indices = model_rows.iloc[holdout_positions].index
        result.loc[holdout_indices, "cv_fold"] = fold
    if result.loc[model_mask, "cv_fold"].isna().any():
        raise RuntimeError("Every model-train row must receive exactly one CV holdout fold.")
    return result


def privacy_status(ids: pd.Series, raw_rater: pd.DataFrame) -> pd.Series:
    exact = raw_rater.dropna(subset=["text_id_kaggle"]).copy()
    exact["privacy_review_status"] = np.where(
        exact["Identifying_Info_1"].eq(1) | exact["Identifying_Info_2"].eq(1),
        "flagged_by_rater",
        "not_flagged",
    )
    status_map = exact.set_index("text_id_kaggle")["privacy_review_status"]
    return ids.map(status_map).fillna("unresolved_raw_id_link")


def build_manifest(
    development: pd.DataFrame, test: pd.DataFrame, raw_rater: pd.DataFrame
) -> pd.DataFrame:
    development_manifest = pd.DataFrame(
        {
            "essay_id": development["text_id_kaggle"],
            "source_partition": "official_train",
            "split": development["split"],
            "cv_fold": development["cv_fold"],
            "prompt_id": development["prompt"],
            "normalized_text_hash": development["normalized_text_hash"],
            "privacy_review_status": privacy_status(development["text_id_kaggle"], raw_rater),
        }
    )
    test_manifest = pd.DataFrame(
        {
            "essay_id": test["text_id_kaggle"],
            "source_partition": "official_test",
            "split": "official_test",
            "cv_fold": pd.Series(pd.NA, index=test.index, dtype="Int64"),
            "prompt_id": test["prompt"],
            "normalized_text_hash": test["full_text"].map(text_hash),
            "privacy_review_status": privacy_status(test["text_id_kaggle"], raw_rater),
        }
    )
    manifest = pd.concat([development_manifest, test_manifest], ignore_index=True)
    manifest["cv_fold"] = manifest["cv_fold"].astype("Int64")
    return manifest.sort_values(
        ["source_partition", "split", "essay_id"], kind="stable"
    ).reset_index(drop=True)


def find_near_duplicates(
    development: pd.DataFrame, test: pd.DataFrame, manifest: pd.DataFrame
) -> pd.DataFrame:
    combined = pd.concat(
        [
            development[["text_id_kaggle", "full_text"]],
            test[["text_id_kaggle", "full_text"]],
        ],
        ignore_index=True,
    )
    normalized = combined["full_text"].map(normalize_text)
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
    split_map = manifest.set_index("essay_id")["split"]

    columns = ["left_id", "right_id", "left_split", "right_split", "similarity"]
    pairs: dict[tuple[int, int], float] = {}
    for row_index, (row_distances, row_indices) in enumerate(zip(distances, indices, strict=True)):
        for distance, neighbor_index in zip(row_distances, row_indices, strict=True):
            if neighbor_index == row_index:
                continue
            similarity = float(1.0 - distance)
            if similarity >= NEAR_DUPLICATE_THRESHOLD:
                left, right = sorted((row_index, int(neighbor_index)))
                pairs[(left, right)] = max(similarity, pairs.get((left, right), 0.0))
            break

    rows: list[dict[str, object]] = []
    for (left, right), similarity in sorted(pairs.items(), key=lambda item: -item[1]):
        left_id = combined.iloc[left]["text_id_kaggle"]
        right_id = combined.iloc[right]["text_id_kaggle"]
        rows.append(
            {
                "left_id": left_id,
                "right_id": right_id,
                "left_split": split_map[left_id],
                "right_split": split_map[right_id],
                "similarity": round(similarity, 6),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def build_distribution_tables(
    development: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    model_train = development[development["split"].eq("model_train")]
    validation = development[development["split"].eq("validation")]

    target_rows: list[dict[str, object]] = []
    score_rows: list[dict[str, object]] = []
    for target in TARGETS:
        train_values = model_train[target]
        validation_values = validation[target]
        target_rows.append(
            {
                "target": target,
                "model_train_mean": round(float(train_values.mean()), 6),
                "validation_mean": round(float(validation_values.mean()), 6),
                "absolute_mean_difference": round(
                    abs(float(train_values.mean() - validation_values.mean())), 6
                ),
                "ks_statistic": round(
                    float(ks_2samp(train_values, validation_values).statistic), 6
                ),
            }
        )
        levels = sorted(set(train_values.unique()) | set(validation_values.unique()))
        for level in levels:
            train_percent = float(train_values.eq(level).mean() * 100)
            validation_percent = float(validation_values.eq(level).mean() * 100)
            score_rows.append(
                {
                    "target": target,
                    "score": level,
                    "model_train_count": int(train_values.eq(level).sum()),
                    "validation_count": int(validation_values.eq(level).sum()),
                    "model_train_percent": round(train_percent, 4),
                    "validation_percent": round(validation_percent, 4),
                    "absolute_percentage_point_difference": round(
                        abs(train_percent - validation_percent), 4
                    ),
                }
            )

    train_prompt = model_train["prompt"].value_counts(normalize=True)
    validation_prompt = validation["prompt"].value_counts(normalize=True)
    prompt_levels = sorted(set(train_prompt.index) | set(validation_prompt.index))
    prompt_rows = []
    for prompt in prompt_levels:
        train_count = int(model_train["prompt"].eq(prompt).sum())
        validation_count = int(validation["prompt"].eq(prompt).sum())
        train_percent = float(train_prompt.get(prompt, 0) * 100)
        validation_percent = float(validation_prompt.get(prompt, 0) * 100)
        prompt_rows.append(
            {
                "prompt": prompt,
                "model_train_count": train_count,
                "validation_count": validation_count,
                "model_train_percent": round(train_percent, 4),
                "validation_percent": round(validation_percent, 4),
                "absolute_percentage_point_difference": round(
                    abs(train_percent - validation_percent), 4
                ),
            }
        )
    return pd.DataFrame(target_rows), pd.DataFrame(score_rows), pd.DataFrame(prompt_rows)


def build_cv_summary(development: pd.DataFrame) -> pd.DataFrame:
    model_train = development[development["split"].eq("model_train")]
    rows: list[dict[str, object]] = []
    for fold in range(CV_FOLDS):
        holdout = model_train[model_train["cv_fold"].eq(fold)]
        fitting = model_train[model_train["cv_fold"].ne(fold)]
        rows.append(
            {
                "fold": fold,
                "fit_rows": len(fitting),
                "holdout_rows": len(holdout),
                "holdout_prompt_count": int(holdout["prompt"].nunique()),
                "vocabulary_fit_mean": round(float(fitting["Vocabulary"].mean()), 6),
                "vocabulary_holdout_mean": round(float(holdout["Vocabulary"].mean()), 6),
                "grammar_fit_mean": round(float(fitting["Grammar"].mean()), 6),
                "grammar_holdout_mean": round(float(holdout["Grammar"].mean()), 6),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    SPLITS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    train, test, raw_rater = load_inputs()
    development = assign_cv_folds(assign_development_split(train))
    manifest = build_manifest(development, test, raw_rater)
    near_duplicates = find_near_duplicates(development, test, manifest)
    target_balance, score_balance, prompt_balance = build_distribution_tables(development)
    cv_summary = build_cv_summary(development)

    split_counts = manifest["split"].value_counts()
    duplicate_ids = int(manifest["essay_id"].duplicated().sum())
    hash_partition_counts = manifest.groupby("normalized_text_hash")["split"].nunique()
    exact_hash_cross_split = int(hash_partition_counts.gt(1).sum())
    cross_split_near_duplicates = int(
        near_duplicates["left_split"].ne(near_duplicates["right_split"]).sum()
    )
    privacy = (
        manifest.groupby(["split", "privacy_review_status"], dropna=False)
        .size()
        .rename("rows")
        .reset_index()
    )

    summary = {
        "created_on": "2026-09-23",
        "random_seed": SEED,
        "validation_fraction_of_official_train": VALIDATION_SIZE,
        "cv_folds": CV_FOLDS,
        "official_train_rows": len(train),
        "model_train_rows": int(split_counts["model_train"]),
        "validation_rows": int(split_counts["validation"]),
        "official_test_rows": int(split_counts["official_test"]),
        "duplicate_ids_across_manifest": duplicate_ids,
        "exact_text_hash_groups_crossing_splits": exact_hash_cross_split,
        "near_duplicate_pairs_at_0_95": len(near_duplicates),
        "near_duplicate_pairs_crossing_splits_at_0_95": cross_split_near_duplicates,
        "writer_id_available": False,
        "prompts_in_model_train": int(
            manifest.loc[manifest["split"].eq("model_train"), "prompt_id"].nunique()
        ),
        "prompts_in_validation": int(
            manifest.loc[manifest["split"].eq("validation"), "prompt_id"].nunique()
        ),
        "prompts_in_official_test": int(
            manifest.loc[manifest["split"].eq("official_test"), "prompt_id"].nunique()
        ),
        "maximum_prompt_percentage_point_difference_train_validation": round(
            float(prompt_balance["absolute_percentage_point_difference"].max()), 4
        ),
        "maximum_score_percentage_point_difference_train_validation": round(
            float(score_balance["absolute_percentage_point_difference"].max()), 4
        ),
        "maximum_target_mean_difference_train_validation": round(
            float(target_balance["absolute_mean_difference"].max()), 6
        ),
        "multi_prompt_exact_duplicate_groups": development.attrs["multi_prompt_duplicate_groups"],
        "test_score_columns_loaded": False,
    }

    if duplicate_ids or exact_hash_cross_split or cross_split_near_duplicates:
        raise RuntimeError("Leakage audit failed; inspect Phase 3 tables before proceeding.")
    if set(split_counts.index) != {"model_train", "validation", "official_test"}:
        raise RuntimeError("Unexpected split labels in manifest.")
    if manifest.loc[manifest["split"].eq("model_train"), "cv_fold"].isna().any():
        raise RuntimeError("Missing CV fold assignment in model-train rows.")
    if manifest.loc[manifest["split"].ne("model_train"), "cv_fold"].notna().any():
        raise RuntimeError("Only model-train rows may have CV fold assignments.")

    manifest_path = SPLITS / "essay_split_manifest.csv"
    manifest.to_csv(manifest_path, index=False)
    summary["manifest_sha256"] = file_sha256(manifest_path)
    target_balance.to_csv(TABLES / "target_balance.csv", index=False)
    score_balance.to_csv(TABLES / "score_balance.csv", index=False)
    prompt_balance.to_csv(TABLES / "prompt_balance.csv", index=False)
    cv_summary.to_csv(TABLES / "cv_fold_summary.csv", index=False)
    near_duplicates.to_csv(TABLES / "near_duplicate_pairs.csv", index=False)
    privacy.to_csv(TABLES / "privacy_status_by_split.csv", index=False)
    (TABLES / "split_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

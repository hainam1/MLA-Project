"""Create leakage-safe train/validation/test splits for sentence CEFR classification."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

RANDOM_STATE = 42


class UnionFind:
    def __init__(self, size: int):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, index: int) -> int:
        if self.parent[index] != index:
            self.parent[index] = self.find(self.parent[index])
        return self.parent[index]

    def union(self, left: int, right: int) -> None:
        root_left, root_right = self.find(left), self.find(right)
        if root_left == root_right:
            return
        if self.rank[root_left] < self.rank[root_right]:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left
        if self.rank[root_left] == self.rank[root_right]:
            self.rank[root_left] += 1


def word_tokens(text: object) -> set[str]:
    return set(re.findall(r"\b[a-z]+\b", str(text).casefold()))


def compute_sentence_clusters(
    frame: pd.DataFrame,
    jaccard_threshold: float = 0.80,
    sequence_threshold: float = 0.75,
) -> pd.DataFrame:
    """Group likely template variants using conservative, transitive similarity links."""
    if "text" not in frame:
        raise ValueError("Expected a text column")
    sentences = frame["text"].astype(str).tolist()
    union_find = UnionFind(len(sentences))
    buckets: dict[str, list[int]] = defaultdict(list)
    for index, sentence in enumerate(sentences):
        tokens = re.findall(r"\b[a-z]+\b", sentence.casefold())
        if len(tokens) >= 3:
            buckets["_".join(tokens[:2])].append(index)

    for indices in buckets.values():
        if not 1 < len(indices) < 200:
            continue
        for position, left in enumerate(indices):
            left_tokens = word_tokens(sentences[left])
            for right in indices[position + 1 :]:
                right_tokens = word_tokens(sentences[right])
                union = left_tokens | right_tokens
                if not union:
                    continue
                jaccard = len(left_tokens & right_tokens) / len(union)
                sequence = SequenceMatcher(None, sentences[left], sentences[right]).ratio()
                if jaccard >= jaccard_threshold and sequence >= sequence_threshold:
                    union_find.union(left, right)

    clustered = frame.copy()
    roots = [union_find.find(index) for index in range(len(clustered))]
    root_to_id = {root: cluster_id for cluster_id, root in enumerate(sorted(set(roots)))}
    clustered["cluster_id"] = [root_to_id[root] for root in roots]
    return clustered


def split_by_cluster(
    frame: pd.DataFrame,
    n_splits: int = 20,
    train_folds: int = 14,
    validation_folds: int = 3,
    random_state: int = RANDOM_STATE,
) -> dict[str, pd.DataFrame]:
    required = {"cefr_label", "cluster_id"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing split columns: {sorted(missing)}")
    if train_folds + validation_folds >= n_splits:
        raise ValueError("At least one fold must remain for test")

    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    fold_ids = np.zeros(len(frame), dtype=int)
    for fold, (_, held_out) in enumerate(
        splitter.split(frame, frame["cefr_label"], frame["cluster_id"])
    ):
        fold_ids[held_out] = fold

    assigned = frame.copy()
    assigned["fold"] = fold_ids
    validation_end = train_folds + validation_folds
    splits = {
        "train": assigned[assigned["fold"] < train_folds].drop(columns="fold"),
        "validation": assigned[
            (assigned["fold"] >= train_folds) & (assigned["fold"] < validation_end)
        ].drop(columns="fold"),
        "test": assigned[assigned["fold"] >= validation_end].drop(columns="fold"),
    }
    return {name: split.reset_index(drop=True) for name, split in splits.items()}


def assert_no_group_leakage(splits: dict[str, pd.DataFrame]) -> None:
    names = list(splits)
    for index, left_name in enumerate(names):
        left_groups = set(splits[left_name]["cluster_id"])
        left_text = set(splits[left_name]["text"].astype(str).str.casefold())
        for right_name in names[index + 1 :]:
            right_groups = set(splits[right_name]["cluster_id"])
            right_text = set(splits[right_name]["text"].astype(str).str.casefold())
            if left_groups & right_groups:
                raise AssertionError(f"cluster leakage: {left_name} vs {right_name}")
            if left_text & right_text:
                raise AssertionError(f"exact-text leakage: {left_name} vs {right_name}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(splits: dict[str, pd.DataFrame], paths: dict[str, Path]) -> dict:
    manifest = {"random_state": RANDOM_STATE, "splits": {}}
    for name, frame in splits.items():
        manifest["splits"][name] = {
            "path": paths[name].as_posix(),
            "sha256": file_sha256(paths[name]),
            "rows": int(len(frame)),
            "clusters": int(frame["cluster_id"].nunique()),
            "labels": {
                str(label): int(count)
                for label, count in frame["cefr_level"].value_counts().sort_index().items()
            },
            "sources": {
                str(source): int(count)
                for source, count in frame["source"].value_counts().sort_index().items()
            },
        }
    return manifest


def main() -> None:
    input_path = Path("data/processed/cefr_sentence_features.csv")
    if not input_path.exists():
        raise FileNotFoundError(f"Missing {input_path}; build sentence features first")
    frame = pd.read_csv(input_path)
    if "cluster_id" not in frame:
        frame = compute_sentence_clusters(frame)
    splits = split_by_cluster(frame)
    assert_no_group_leakage(splits)

    output_dir = Path("data/processed")
    paths = {
        "train": output_dir / "sentence_cefr_train.csv",
        "validation": output_dir / "sentence_cefr_validation.csv",
        "test": output_dir / "sentence_cefr_test.csv",
    }
    for name, split in splits.items():
        split.to_csv(paths[name], index=False, encoding="utf-8")
    manifest = build_manifest(splits, paths)
    (output_dir / "split_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

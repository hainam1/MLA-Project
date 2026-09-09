from __future__ import annotations

import pandas as pd

from src.data.split_datasets import assert_no_group_leakage, split_by_cluster


def test_stratified_group_split_keeps_clusters_disjoint():
    rows = []
    levels = ["A1", "A2", "B1", "B2", "C1"]
    for label, level in enumerate(levels):
        for group_offset in range(3):
            cluster = label * 10 + group_offset
            for variant in range(2):
                rows.append(
                    {
                        "text": f"Sentence {label} {group_offset} variant {variant}",
                        "source": "sample",
                        "cefr_level": level,
                        "cefr_label": label,
                        "cluster_id": cluster,
                    }
                )
    frame = pd.DataFrame(rows)
    splits = split_by_cluster(frame, n_splits=3, train_folds=1, validation_folds=1)

    assert_no_group_leakage(splits)
    assert sum(len(split) for split in splits.values()) == len(frame)

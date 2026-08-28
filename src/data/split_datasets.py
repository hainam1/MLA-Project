"""
Script phân chia tập dữ liệu Train / Validation / Test (70% / 15% / 15%)
cho toàn bộ 5 mô hình trong hệ thống CapyVocab ML (Mục 2.8).

Áp dụng chiến lược chống rò rỉ dữ liệu (Anti-Data Leakage) nghiêm ngặt:
1. Model 1 (Translator): Split theo unique câu tiếng Việt ('vi').
2. Model 2a (Word CEFR): Stratified split theo 'cefr_label' (0-4).
3. Model 2b (Sentence CEFR): StratifiedGroupKFold theo 'cluster_id' (Union-Find Jaccard >= 0.80).
4. Model 3a (Example Generator): Stratified split theo 'cefr_level' (A1-C1).
5. Model 3b (Sentence Rewriter): Group split theo 'original' (10 bản rewrite luôn cùng tập).

Output: 15 tệp CSV tại data/processed/ theo định dạng:
  - model1_translator_{train,val,test}.csv
  - model2a_word_cefr_{train,val,test}.csv
  - model2b_sentence_cefr_{train,val,test}.csv
  - model3a_example_gen_{train,val,test}.csv
  - model3b_rewrite_{train,val,test}.csv
"""

import sys
import os
import re
from difflib import SequenceMatcher
from collections import defaultdict
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

RANDOM_STATE = 42


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            return True
        return False


def compute_sentence_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """Tạo cột cluster_id cho câu dựa trên Union-Find Jaccard >= 0.80."""
    sentences = df["text"].tolist()
    N = len(sentences)
    uf = UnionFind(N)

    def get_tokens(text):
        return set(re.findall(r"\b[a-zA-Z]+\b", str(text).lower()))

    buckets = defaultdict(list)
    for i, text in enumerate(sentences):
        words = str(text).lower().split()
        if len(words) >= 3:
            bucket_key = words[0] + "_" + words[1]
            buckets[bucket_key].append(i)

    for b_key, indices in buckets.items():
        if 1 < len(indices) < 200:
            for idx1 in range(len(indices)):
                for idx2 in range(idx1 + 1, len(indices)):
                    i1, i2 = indices[idx1], indices[idx2]
                    s1, s2 = sentences[i1], sentences[i2]
                    t1, t2 = get_tokens(s1), get_tokens(s2)
                    if t1 and t2:
                        jaccard = len(t1.intersection(t2)) / len(t1.union(t2))
                        if jaccard >= 0.80 and s1 != s2:
                            if SequenceMatcher(None, s1, s2).ratio() >= 0.75:
                                uf.union(i1, i2)

    df_res = df.copy()
    df_res["cluster_id"] = [uf.find(i) for i in range(N)]
    return df_res


def print_distribution(df_train, df_val, df_test, label_col):
    """In phân bố tỷ lệ nhãn trên 3 tập để kiểm tra stratification."""
    labels = sorted(df_train[label_col].unique())
    print(f"\n  Phân bố nhãn '{label_col}' qua các tập:")
    print(f"  {'Nhãn':<8} | {'Train (70%)':<16} | {'Val (15%)':<16} | {'Test (15%)':<16}")
    print("  " + "-" * 56)
    for lbl in labels:
        tr_cnt = sum(df_train[label_col] == lbl)
        tr_pct = tr_cnt / len(df_train) * 100
        val_cnt = sum(df_val[label_col] == lbl)
        val_pct = val_cnt / len(df_val) * 100
        te_cnt = sum(df_test[label_col] == lbl)
        te_pct = te_cnt / len(df_test) * 100
        print(
            f"  {str(lbl):<8} | {tr_cnt:>6,} ({tr_pct:>5.2f}%) | {val_cnt:>6,} ({val_pct:>5.2f}%) | {te_cnt:>6,} ({te_pct:>5.2f}%)"
        )


def save_splits(train_df, val_df, test_df, prefix):
    out_dir = "data/processed"
    os.makedirs(out_dir, exist_ok=True)
    p_train = os.path.join(out_dir, f"{prefix}_train.csv")
    p_val = os.path.join(out_dir, f"{prefix}_val.csv")
    p_test = os.path.join(out_dir, f"{prefix}_test.csv")

    train_df.to_csv(p_train, index=False, encoding="utf-8")
    val_df.to_csv(p_val, index=False, encoding="utf-8")
    test_df.to_csv(p_test, index=False, encoding="utf-8")
    return p_train, p_val, p_test


def main():
    print("=" * 75)
    print("CAPYVOCAB ML - PHÂN CHIA TẬP TRAIN / VAL / TEST (70/15/15) - MỤC 2.8")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # 1. MODEL 1: TRANSLATOR (VI -> EN)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("1. MODEL 1: TRANSLATOR VI -> EN")
    print("=" * 75)
    m1_path = "data/processed/parallel_vi_en_clean.csv"
    df_m1 = pd.read_csv(m1_path)
    print(f"Đọc dữ liệu: {m1_path} ({len(df_m1):,} dòng)")

    # Group split theo unique câu tiếng Việt
    unique_vi = df_m1["vi"].unique()
    np.random.seed(RANDOM_STATE)
    shuffled_vi = np.random.permutation(unique_vi)

    n_total_vi = len(shuffled_vi)
    n_train_vi = int(0.70 * n_total_vi)
    n_val_vi = int(0.15 * n_total_vi)

    train_vi_set = set(shuffled_vi[:n_train_vi])
    val_vi_set = set(shuffled_vi[n_train_vi : n_train_vi + n_val_vi])
    test_vi_set = set(shuffled_vi[n_train_vi + n_val_vi :])

    m1_train = df_m1[df_m1["vi"].isin(train_vi_set)].copy().reset_index(drop=True)
    m1_val = df_m1[df_m1["vi"].isin(val_vi_set)].copy().reset_index(drop=True)
    m1_test = df_m1[df_m1["vi"].isin(test_vi_set)].copy().reset_index(drop=True)

    # Assert Anti-Leakage
    assert len(set(m1_train["vi"]) & set(m1_val["vi"])) == 0, "Lỗi: Rò rỉ câu VI giữa Train và Val!"
    assert (
        len(set(m1_train["vi"]) & set(m1_test["vi"])) == 0
    ), "Lỗi: Rò rỉ câu VI giữa Train và Test!"
    assert len(set(m1_val["vi"]) & set(m1_test["vi"])) == 0, "Lỗi: Rò rỉ câu VI giữa Val và Test!"

    save_splits(m1_train, m1_val, m1_test, "model1_translator")
    tot_m1 = len(df_m1)
    print(f"✓ Train: {len(m1_train):>7,} dòng ({len(m1_train)/tot_m1*100:>5.2f}%)")
    print(f"✓ Val  : {len(m1_val):>7,} dòng ({len(m1_val)/tot_m1*100:>5.2f}%)")
    print(f"✓ Test : {len(m1_test):>7,} dòng ({len(m1_test)/tot_m1*100:>5.2f}%)")
    print("✓ Assert Anti-Leakage: KHÔNG có câu tiếng Việt nào xuất hiện ở nhiều hơn 1 tập!")

    # -------------------------------------------------------------------------
    # 2. MODEL 2A: CEFR WORD CLASSIFIER
    # -------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("2. MODEL 2a: CEFR WORD CLASSIFIER (TABULAR)")
    print("=" * 75)
    m2a_path = "data/processed/cefr_word_features.csv"
    df_m2a = pd.read_csv(m2a_path)
    print(f"Đọc dữ liệu: {m2a_path} ({len(df_m2a):,} dòng)")

    # Grouped stratification: every spelling belongs to exactly one split.
    # This remains safe if future feature tables contain multiple POS variants.
    sgkf_word = StratifiedGroupKFold(n_splits=20, shuffle=True, random_state=RANDOM_STATE)
    word_folds = np.zeros(len(df_m2a), dtype=int)
    for fold, (_, held_out) in enumerate(
        sgkf_word.split(df_m2a, df_m2a["cefr_label"], df_m2a["word"])
    ):
        word_folds[held_out] = fold
    df_m2a["fold"] = word_folds
    m2a_train = df_m2a[df_m2a["fold"] < 14].drop(columns=["fold"]).copy().reset_index(drop=True)
    m2a_val = (
        df_m2a[(df_m2a["fold"] >= 14) & (df_m2a["fold"] < 17)]
        .drop(columns=["fold"])
        .copy()
        .reset_index(drop=True)
    )
    m2a_test = df_m2a[df_m2a["fold"] >= 17].drop(columns=["fold"]).copy().reset_index(drop=True)

    train_words = set(m2a_train["word"])
    val_words = set(m2a_val["word"])
    test_words = set(m2a_test["word"])
    assert not train_words & val_words
    assert not train_words & test_words
    assert not val_words & test_words

    save_splits(m2a_train, m2a_val, m2a_test, "model2a_word_cefr")
    tot_m2a = len(df_m2a)
    print(f"✓ Train: {len(m2a_train):>5,} dòng ({len(m2a_train)/tot_m2a*100:>5.2f}%)")
    print(f"✓ Val  : {len(m2a_val):>5,} dòng ({len(m2a_val)/tot_m2a*100:>5.2f}%)")
    print(f"✓ Test : {len(m2a_test):>5,} dòng ({len(m2a_test)/tot_m2a*100:>5.2f}%)")
    print_distribution(m2a_train, m2a_val, m2a_test, "cefr_level")
    print("✓ Assert Anti-Leakage: không có word nào xuất hiện ở nhiều split.")

    # -------------------------------------------------------------------------
    # 3. MODEL 2B: CEFR SENTENCE CLASSIFIER
    # -------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("3. MODEL 2b: CEFR SENTENCE CLASSIFIER (STRATIFIED GROUP K-FOLD)")
    print("=" * 75)
    m2b_path = "data/processed/cefr_sentence_features.csv"
    df_m2b = pd.read_csv(m2b_path)
    print(f"Đọc dữ liệu: {m2b_path} ({len(df_m2b):,} dòng)")

    # Compute Union-Find clusters if not existing
    if "cluster_id" not in df_m2b.columns:
        print("  -> Đang tính toán Union-Find clusters (Jaccard >= 0.80)...")
        df_m2b = compute_sentence_clusters(df_m2b)

    print(f"  -> Tổng số cụm liên thông (cluster_id): {df_m2b['cluster_id'].nunique():,} clusters")

    # StratifiedGroupKFold với 20 folds (14 folds train = 70%, 3 folds val = 15%, 3 folds test = 15%)
    sgkf = StratifiedGroupKFold(n_splits=20, shuffle=True, random_state=RANDOM_STATE)
    folds = np.zeros(len(df_m2b), dtype=int)
    for fold, (_, test_idx) in enumerate(
        sgkf.split(df_m2b, df_m2b["cefr_label"], df_m2b["cluster_id"])
    ):
        folds[test_idx] = fold

    df_m2b["fold"] = folds
    m2b_train = df_m2b[df_m2b["fold"] < 14].drop(columns=["fold"]).copy().reset_index(drop=True)
    m2b_val = (
        df_m2b[(df_m2b["fold"] >= 14) & (df_m2b["fold"] < 17)]
        .drop(columns=["fold"])
        .copy()
        .reset_index(drop=True)
    )
    m2b_test = df_m2b[df_m2b["fold"] >= 17].drop(columns=["fold"]).copy().reset_index(drop=True)

    # Assert Anti-Leakage
    assert (
        len(set(m2b_train["cluster_id"]) & set(m2b_val["cluster_id"])) == 0
    ), "Lỗi: Rò rỉ cluster giữa Train và Val!"
    assert (
        len(set(m2b_train["cluster_id"]) & set(m2b_test["cluster_id"])) == 0
    ), "Lỗi: Rò rỉ cluster giữa Train và Test!"
    assert (
        len(set(m2b_val["cluster_id"]) & set(m2b_test["cluster_id"])) == 0
    ), "Lỗi: Rò rỉ cluster giữa Val và Test!"

    save_splits(m2b_train, m2b_val, m2b_test, "model2b_sentence_cefr")
    tot_m2b = len(df_m2b)
    print(f"✓ Train: {len(m2b_train):>5,} dòng ({len(m2b_train)/tot_m2b*100:>5.2f}%)")
    print(f"✓ Val  : {len(m2b_val):>5,} dòng ({len(m2b_val)/tot_m2b*100:>5.2f}%)")
    print(f"✓ Test : {len(m2b_test):>5,} dòng ({len(m2b_test)/tot_m2b*100:>5.2f}%)")
    print("✓ Assert Anti-Leakage: KHÔNG có cluster_id nào bị chia cắt giữa các tập!")
    print_distribution(m2b_train, m2b_val, m2b_test, "cefr_level")

    # -------------------------------------------------------------------------
    # 4. MODEL 3A: EXAMPLE GENERATOR
    # -------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("4. MODEL 3a: EXAMPLE GENERATOR (MULTI-LEVEL)")
    print("=" * 75)
    m3a_path = "data/processed/example_generation_pairs.csv"
    df_m3a = pd.read_csv(m3a_path)
    print(f"Đọc dữ liệu: {m3a_path} ({len(df_m3a):,} dòng)")

    sgkf_examples = StratifiedGroupKFold(n_splits=20, shuffle=True, random_state=RANDOM_STATE)
    example_folds = np.zeros(len(df_m3a), dtype=int)
    for fold, (_, held_out) in enumerate(
        sgkf_examples.split(df_m3a, df_m3a["target_label"], df_m3a["target_word"])
    ):
        example_folds[held_out] = fold
    df_m3a["fold"] = example_folds
    m3a_train = df_m3a[df_m3a["fold"] < 14].drop(columns="fold").reset_index(drop=True)
    m3a_val = (
        df_m3a[(df_m3a["fold"] >= 14) & (df_m3a["fold"] < 17)]
        .drop(columns="fold")
        .reset_index(drop=True)
    )
    m3a_test = df_m3a[df_m3a["fold"] >= 17].drop(columns="fold").reset_index(drop=True)
    assert not set(m3a_train["target_word"]) & set(m3a_val["target_word"])
    assert not set(m3a_train["target_word"]) & set(m3a_test["target_word"])

    save_splits(m3a_train, m3a_val, m3a_test, "model3a_example_gen")
    tot_m3a = len(df_m3a)
    print(f"✓ Train: {len(m3a_train):>6,} dòng ({len(m3a_train)/tot_m3a*100:>5.2f}%)")
    print(f"✓ Val  : {len(m3a_val):>6,} dòng ({len(m3a_val)/tot_m3a*100:>5.2f}%)")
    print(f"✓ Test : {len(m3a_test):>6,} dòng ({len(m3a_test)/tot_m3a*100:>5.2f}%)")
    print_distribution(m3a_train, m3a_val, m3a_test, "target_level")

    # -------------------------------------------------------------------------
    # 5. MODEL 3B: SENTENCE REWRITER
    # -------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("5. MODEL 3b: SENTENCE REWRITER (GROUP SPLIT BY ORIGINAL)")
    print("=" * 75)
    m3b_path = "data/processed/sentence_rewrite_simplification_pairs.csv"
    df_m3b = pd.read_csv(m3b_path)
    print(f"Đọc dữ liệu: {m3b_path} ({len(df_m3b):,} dòng)")

    unique_orig = df_m3b["original"].unique()
    np.random.seed(RANDOM_STATE)
    shuffled_orig = np.random.permutation(unique_orig)

    n_tot_orig = len(shuffled_orig)
    n_tr_orig = int(0.70 * n_tot_orig)
    n_va_orig = int(0.15 * n_tot_orig)

    train_orig_set = set(shuffled_orig[:n_tr_orig])
    val_orig_set = set(shuffled_orig[n_tr_orig : n_tr_orig + n_va_orig])
    test_orig_set = set(shuffled_orig[n_tr_orig + n_va_orig :])

    m3b_train = df_m3b[df_m3b["original"].isin(train_orig_set)].copy().reset_index(drop=True)
    m3b_val = df_m3b[df_m3b["original"].isin(val_orig_set)].copy().reset_index(drop=True)
    m3b_test = df_m3b[df_m3b["original"].isin(test_orig_set)].copy().reset_index(drop=True)

    # Assert Anti-Leakage
    assert (
        len(set(m3b_train["original"]) & set(m3b_val["original"])) == 0
    ), "Lỗi: Rò rỉ original giữa Train và Val!"
    assert (
        len(set(m3b_train["original"]) & set(m3b_test["original"])) == 0
    ), "Lỗi: Rò rỉ original giữa Train và Test!"
    assert (
        len(set(m3b_val["original"]) & set(m3b_test["original"])) == 0
    ), "Lỗi: Rò rỉ original giữa Val và Test!"

    save_splits(m3b_train, m3b_val, m3b_test, "model3b_rewrite")
    tot_m3b = len(df_m3b)
    print(
        f"✓ Train: {len(m3b_train):>6,} dòng ({len(m3b_train)/tot_m3b*100:>5.2f}%) | {len(train_orig_set):,} câu gốc"
    )
    print(
        f"✓ Val  : {len(m3b_val):>6,} dòng ({len(m3b_val)/tot_m3b*100:>5.2f}%) | {len(val_orig_set):,} câu gốc"
    )
    print(
        f"✓ Test : {len(m3b_test):>6,} dòng ({len(m3b_test)/tot_m3b*100:>5.2f}%) | {len(test_orig_set):,} câu gốc"
    )
    print("✓ Assert Anti-Leakage: mọi rewrite của cùng câu gốc nằm trong một split.")

    print("\n" + "=" * 75)
    print("✅ TOÀN BỘ 15 TỆP TRAIN/VAL/TEST ĐÃ ĐƯỢC XUẤT THÀNH CÔNG VÀO data/processed/!")
    print("=" * 75)


if __name__ == "__main__":
    main()

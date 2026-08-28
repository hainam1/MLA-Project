"""
Script huấn luyện và đánh giá Model 2b: CEFR Sentence Classifier (Mục 3.2).

Nhiệm vụ:
  - Phân loại cấp độ CEFR của một câu tiếng Anh (A1 -> C1, 5 lớp: 0 - 4).
  - Thuộc họ Classical Machine Learning trên 25 đặc trưng cú pháp, từ vựng và độ đọc hiểu.
  - Tuyệt đối loại trừ 'text', 'source', 'cluster_id' khỏi không gian đặc trưng X.

Quy trình:
  1. Đọc dữ liệu train/val/test từ data/processed/model2b_sentence_cefr_{train,val,test}.csv.
  2. Huấn luyện Baseline Logistic Regression (class_weight='balanced').
  3. Huấn luyện Random Forest, Gradient Boosting và XGBoost trên tập Validation.
  4. Đánh giá mô hình tốt nhất trên Test set (Accuracy, Macro F1, Confusion Matrix, Classification Report).
  5. Trích xuất Feature Importance nhóm theo 5 danh mục ngôn ngữ học.
  6. Lưu mô hình tốt nhất vào src/models/cefr_sentence_classifier/model.pkl và metadata.json.
"""

import sys
import os
import json
import joblib
import pandas as pd
from datetime import datetime

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_sample_weight

from src.features import SENTENCE_FEATURE_COLUMNS

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

RANDOM_STATE = 42

FEATURE_CATEGORIES = {
    "Độ dài & Bề mặt (Surface / Length)": [
        "num_words",
        "num_chars",
        "avg_word_len",
        "num_syllables_total",
        "avg_syllables_per_word",
    ],
    "Tần suất từ vựng & Độ hiếm (Lexical Rarity)": [
        "avg_word_zipf",
        "min_word_zipf",
        "rare_word_ratio",
    ],
    "Cấp độ CEFR từ vựng (Word-Level CEFR)": ["avg_word_cefr", "max_word_cefr", "word_oov_ratio"],
    "Độ phức tạp cú pháp & POS (Syntax Complexity)": [
        "dep_tree_depth",
        "subclause_count",
        "subclause_ratio",
        "passive_count",
        "pos_noun_ratio",
        "pos_verb_ratio",
        "pos_adj_ratio",
        "pos_adv_ratio",
        "pos_adp_ratio",
    ],
    "Chỉ số độ đọc hiểu (Readability Indices)": [
        "flesch_reading_ease",
        "flesch_kincaid_grade",
        "gunning_fog",
        "automated_readability_index",
        "dale_chall_score",
    ],
}


def main():
    model_dir = "src/models/cefr_sentence_classifier"
    os.makedirs(model_dir, exist_ok=True)

    train_path = "data/processed/model2b_sentence_cefr_train.csv"
    val_path = "data/processed/model2b_sentence_cefr_val.csv"
    test_path = "data/processed/model2b_sentence_cefr_test.csv"

    model_save_path = os.path.join(model_dir, "model.pkl")
    meta_save_path = os.path.join(model_dir, "metadata.json")

    print("=" * 75)
    print("CAPYVOCAB ML - HUẤN LUYỆN MODEL 2b: CEFR SENTENCE CLASSIFIER (MỤC 3.2)")
    print("=" * 75)

    # 1. Đọc dữ liệu
    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)

    print(f"1. Đã nạp 3 tập dữ liệu (StratifiedGroupKFold theo cluster_id):")
    print(f"   - Train: {df_train.shape[0]:,} dòng x {df_train.shape[1]} cột")
    print(f"   - Val  : {df_val.shape[0]:,} dòng x {df_val.shape[1]} cột")
    print(f"   - Test : {df_test.shape[0]:,} dòng x {df_test.shape[1]} cột")

    # 2. Xác định danh sách đặc trưng & Khẳng định chống rò rỉ (Anti-Leakage)
    print("\n2. Xác định không gian đặc trưng và kiểm tra rò rỉ dữ liệu:")
    all_cols = list(df_train.columns)
    print(f"   - Toàn bộ cột trong file dữ liệu: {all_cols}")

    feature_cols = SENTENCE_FEATURE_COLUMNS
    target_col = "cefr_label"

    print(
        f"\n   - Danh sách 25 đặc trưng toán học/ngôn ngữ đầu vào X ({len(feature_cols)} features):"
    )
    for group_name, feats in FEATURE_CATEGORIES.items():
        print(f"     • {group_name}: {feats}")

    print(f"\n   - Cột nhãn mục tiêu y : '{target_col}' (0: A1 -> 4: C1)")

    # Assert Anti-Leakage
    assert "cluster_id" not in feature_cols, "LỖI: 'cluster_id' bị lẫn vào tập đặc trưng X!"
    assert "text" not in feature_cols, "LỖI: 'text' bị lẫn vào tập đặc trưng X!"
    assert "source" not in feature_cols, "LỖI: 'source' bị lẫn vào tập đặc trưng X!"
    assert "cefr_level" not in feature_cols, "LỖI: 'cefr_level' bị lẫn vào tập đặc trưng X!"
    print("   ✓ XÁC NHẬN: Cột 'text', 'source', 'cluster_id' đã được cô lập tuyệt đối khỏi tập X!")

    X_train, y_train = df_train[feature_cols], df_train[target_col]
    X_val, y_val = df_val[feature_cols], df_val[target_col]
    X_test, y_test = df_test[feature_cols], df_test[target_col]

    # Sample weights for imbalanced classes
    sample_weights_train = compute_sample_weight("balanced", y_train)

    # 3. Định nghĩa các mô hình ứng viên
    models = {
        "Logistic Regression (Baseline)": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        class_weight="balanced", max_iter=1000, random_state=RANDOM_STATE
                    ),
                ),
            ]
        ),
        "Random Forest (Default)": RandomForestClassifier(
            n_estimators=100, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "Random Forest (Tuned)": RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "XGBoost (Default)": XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=RANDOM_STATE,
            eval_metric="mlogloss",
        ),
        "XGBoost (Tuned - Weighted)": XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=RANDOM_STATE,
            eval_metric="mlogloss",
        ),
        "Gradient Boosting (Default)": GradientBoostingClassifier(
            n_estimators=150, max_depth=4, learning_rate=0.05, random_state=RANDOM_STATE
        ),
    }

    # 4. Huấn luyện và so sánh trên tập Validation
    print("\n3. Đang huấn luyện và đánh giá trên tập Validation:")
    val_results = []
    trained_models = {}

    for name, model in models.items():
        if "XGBoost" in name:
            model.fit(X_train, y_train, sample_weight=sample_weights_train)
        else:
            model.fit(X_train, y_train)

        trained_models[name] = model
        y_pred_val = model.predict(X_val)
        acc = accuracy_score(y_val, y_pred_val)
        macro_f1 = f1_score(y_val, y_pred_val, average="macro")
        weighted_f1 = f1_score(y_val, y_pred_val, average="weighted")

        val_results.append(
            {
                "Model": name,
                "Val Accuracy": round(acc, 4),
                "Val Macro F1": round(macro_f1, 4),
                "Val Weighted F1": round(weighted_f1, 4),
            }
        )

    df_results = (
        pd.DataFrame(val_results)
        .sort_values(by="Val Macro F1", ascending=False)
        .reset_index(drop=True)
    )
    print("\n--- BẢNG SO SÁNH CÁC MÔ HÌNH TRÊN TẬP VALIDATION ---")
    print(df_results.to_string(index=False))

    best_model_name = df_results.iloc[0]["Model"]
    best_model = trained_models[best_model_name]
    print(f"\n👉 MÔ HÌNH TỐT NHẤT ĐƯỢC CHỌN (DỰA TRÊN VAL MACRO F1): {best_model_name}")

    # 5. Đánh giá cuối cùng trên Test Set (Chỉ chạy 1 lần)
    print("\n" + "=" * 75)
    print(f"4. ĐÁNH GIÁ CUỐI CÙNG TRÊN TẬP TEST SET ({best_model_name})")
    print("=" * 75)

    y_test_pred = best_model.predict(X_test)
    test_acc = accuracy_score(y_test, y_test_pred)
    test_macro_f1 = f1_score(y_test, y_test_pred, average="macro")
    test_weighted_f1 = f1_score(y_test, y_test_pred, average="weighted")

    print(f"✓ Accuracy tổng thể : {test_acc:.4f} ({test_acc*100:.2f}%)")
    print(f"✓ Macro F1-Score    : {test_macro_f1:.4f}")
    print(f"✓ Weighted F1-Score : {test_weighted_f1:.4f}")

    target_names = ["A1", "A2", "B1", "B2", "C1"]
    print("\n--- BÁO CÁO PHÂN LOẠI CHI TIẾT TỪNG LỚP (CLASSIFICATION REPORT) ---")
    cls_report = classification_report(y_test, y_test_pred, target_names=target_names, digits=4)
    print(cls_report)

    cm = confusion_matrix(y_test, y_test_pred)
    df_cm = pd.DataFrame(
        cm,
        index=[f"Thực tế {n}" for n in target_names],
        columns=[f"Dự đoán {n}" for n in target_names],
    )
    print("--- MA TRẬN NHẦM LẪN (5x5 CONFUSION MATRIX) ---")
    print(df_cm.to_string())

    # 6. Trích xuất Feature Importance theo Nhóm
    print("\n--- XẾP HẠNG TẦM QUAN TRỌNG CỦA ĐẶC TRƯNG (FEATURE IMPORTANCE THEO NHÓM) ---")
    clf = best_model.named_steps["clf"] if hasattr(best_model, "named_steps") else best_model

    feature_importance_dict = {}
    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
        feat_imp_df = (
            pd.DataFrame({"Feature": feature_cols, "Importance": importances})
            .sort_values(by="Importance", ascending=False)
            .reset_index(drop=True)
        )
        feat_imp_df["Importance (%)"] = (feat_imp_df["Importance"] * 100).round(2)
        print(feat_imp_df.to_string(index=False))
        feature_importance_dict = dict(
            zip(feat_imp_df["Feature"], feat_imp_df["Importance"].round(4))
        )

        # Thống kê theo danh mục
        print("\n--- TỔNG HỢP FEATURE IMPORTANCE THEO 5 NHÓM NGÔN NGỮ HỌC ---")
        cat_importances = []
        for cat_name, feats in FEATURE_CATEGORIES.items():
            cat_sum = sum(feature_importance_dict.get(f, 0.0) for f in feats)
            cat_importances.append(
                {
                    "Nhóm đặc trưng": cat_name,
                    "Số lượng features": len(feats),
                    "Tổng đóng góp (%)": round(cat_sum * 100, 2),
                }
            )
        df_cat_imp = (
            pd.DataFrame(cat_importances)
            .sort_values(by="Tổng đóng góp (%)", ascending=False)
            .reset_index(drop=True)
        )
        print(df_cat_imp.to_string(index=False))

    # 7. Lưu Model và Metadata
    print("\n5. Lưu trữ Artifacts:")
    joblib.dump(best_model, model_save_path)
    print(f"✅ Đã lưu model tại: {model_save_path}")

    metadata = {
        "model_name": best_model_name,
        "model_type": str(type(clf).__name__),
        "task": "CEFR Sentence Classification (5 classes: A1-C1)",
        "features": feature_cols,
        "train_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics_test": {
            "accuracy": round(float(test_acc), 4),
            "macro_f1": round(float(test_macro_f1), 4),
            "weighted_f1": round(float(test_weighted_f1), 4),
        },
        "metrics_val": {
            row["Model"]: {
                "val_accuracy": row["Val Accuracy"],
                "val_macro_f1": row["Val Macro F1"],
                "val_weighted_f1": row["Val Weighted F1"],
            }
            for row in val_results
        },
        "feature_importances": feature_importance_dict,
    }

    with open(meta_save_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✅ Đã lưu metadata tại: {meta_save_path}")
    print("=" * 75)


if __name__ == "__main__":
    main()

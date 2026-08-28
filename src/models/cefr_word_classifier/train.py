"""
Script huấn luyện và đánh giá Model 2a: CEFR Word Classifier (Mục 3.1).

Nhiệm vụ:
  - Phân loại cấp độ CEFR của một từ tiếng Anh (A1 -> C1, 5 lớp: 0 - 4).
  - Thuộc họ Classical Machine Learning.
  - Tuyệt đối loại trừ 'teachers_avg' và 'word' khỏi không gian đặc trưng X.

Quy trình:
  1. Đọc dữ liệu train/val/test từ data/processed/model2a_word_cefr_{train,val,test}.csv.
  2. Huấn luyện Baseline Logistic Regression (class_weight='balanced').
  3. Huấn luyện Random Forest và XGBoost với các bộ siêu tham số trên Validation set.
  4. Đánh giá mô hình tốt nhất trên Test set (Accuracy, Macro F1, Confusion Matrix, Classification Report).
  5. Trích xuất Feature Importance cho 9 đặc trưng đầu vào.
  6. Lưu mô hình tốt nhất vào src/models/cefr_word_classifier/model.pkl và metadata.json.
"""

import sys
import os
import json
import joblib
import pandas as pd
from datetime import datetime

from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_sample_weight

from src.features import WORD_FEATURE_COLUMNS

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

RANDOM_STATE = 42


def main():
    model_dir = "src/models/cefr_word_classifier"
    os.makedirs(model_dir, exist_ok=True)

    train_path = "data/processed/model2a_word_cefr_train.csv"
    val_path = "data/processed/model2a_word_cefr_val.csv"
    test_path = "data/processed/model2a_word_cefr_test.csv"

    model_save_path = os.path.join(model_dir, "model.pkl")
    meta_save_path = os.path.join(model_dir, "metadata.json")

    print("=" * 75)
    print("CAPYVOCAB ML - HUẤN LUYỆN MODEL 2a: CEFR WORD CLASSIFIER (MỤC 3.1)")
    print("=" * 75)

    # 1. Đọc dữ liệu
    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)

    print(f"1. Đã nạp 3 tập dữ liệu:")
    print(f"   - Train: {df_train.shape[0]:,} dòng x {df_train.shape[1]} cột")
    print(f"   - Val  : {df_val.shape[0]:,} dòng x {df_val.shape[1]} cột")
    print(f"   - Test : {df_test.shape[0]:,} dòng x {df_test.shape[1]} cột")

    # 2. Xác định danh sách đặc trưng & Khẳng định chống rò rỉ (Anti-Leakage)
    print("\n2. Xác định không gian đặc trưng và kiểm tra rò rỉ dữ liệu:")
    all_cols = list(df_train.columns)
    print(f"   - Toàn bộ cột trong file dữ liệu: {all_cols}")

    feature_cols = WORD_FEATURE_COLUMNS
    target_col = "cefr_label"

    print(f"   - Danh sách đặc trưng đầu vào X ({len(feature_cols)} features):")
    for idx, f in enumerate(feature_cols, 1):
        print(f"     {idx}. {f:<18} (Dtype: {str(df_train[f].dtype)})")

    print(f"   - Cột nhãn mục tiêu y : '{target_col}' (0: A1 -> 4: C1)")

    # Assert Anti-Leakage
    assert "teachers_avg" not in feature_cols, "LỖI: 'teachers_avg' bị lẫn vào tập đặc trưng X!"
    assert "word" not in feature_cols, "LỖI: 'word' bị lẫn vào tập đặc trưng X!"
    assert "cefr_level" not in feature_cols, "LỖI: 'cefr_level' bị lẫn vào tập đặc trưng X!"
    print("   ✓ XÁC NHẬN: Cột 'teachers_avg' và 'word' đã được cô lập tuyệt đối khỏi tập X!")

    X_train, y_train = df_train[feature_cols], df_train[target_col]
    X_val, y_val = df_val[feature_cols], df_val[target_col]
    X_test, y_test = df_test[feature_cols], df_test[target_col]

    num_cols = feature_cols

    preprocessor_scaled = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
        ]
    )

    preprocessor_tree = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_cols),
        ]
    )

    # 3. Định nghĩa các mô hình ứng viên
    models = {
        "Logistic Regression (Baseline)": Pipeline(
            [
                ("prep", preprocessor_scaled),
                (
                    "clf",
                    LogisticRegression(
                        class_weight="balanced", max_iter=1000, random_state=RANDOM_STATE
                    ),
                ),
            ]
        ),
        "Random Forest (Default)": Pipeline(
            [
                ("prep", preprocessor_tree),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=100, class_weight="balanced", random_state=RANDOM_STATE
                    ),
                ),
            ]
        ),
        "Random Forest (Tuned)": Pipeline(
            [
                ("prep", preprocessor_tree),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=300,
                        max_depth=10,
                        min_samples_split=4,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "XGBoost (Default)": Pipeline(
            [
                ("prep", preprocessor_tree),
                (
                    "clf",
                    XGBClassifier(
                        n_estimators=100,
                        max_depth=4,
                        learning_rate=0.1,
                        random_state=RANDOM_STATE,
                        eval_metric="mlogloss",
                    ),
                ),
            ]
        ),
        "XGBoost (Tuned)": Pipeline(
            [
                ("prep", preprocessor_tree),
                (
                    "clf",
                    XGBClassifier(
                        n_estimators=250,
                        max_depth=5,
                        learning_rate=0.05,
                        subsample=0.8,
                        colsample_bytree=0.8,
                        random_state=RANDOM_STATE,
                        eval_metric="mlogloss",
                    ),
                ),
            ]
        ),
    }

    sample_weights_train = compute_sample_weight("balanced", y_train)

    # 4. Huấn luyện và so sánh trên tập Validation
    print("\n3. Đang huấn luyện và đánh giá trên tập Validation:")
    val_results = []
    trained_pipelines = {}

    for name, pipe in models.items():
        if "XGBoost" in name:
            # Preprocess and fit XGBoost with balanced sample weights
            X_tr_proc = pipe.named_steps["prep"].fit_transform(X_train)
            pipe.named_steps["clf"].fit(X_tr_proc, y_train, sample_weight=sample_weights_train)
            X_val_proc = pipe.named_steps["prep"].transform(X_val)
            y_pred = pipe.named_steps["clf"].predict(X_val_proc)
        else:
            pipe.fit(X_train, y_train)
            y_pred = pipe.predict(X_val)

        trained_pipelines[name] = pipe
        acc = accuracy_score(y_val, y_pred)
        macro_f1 = f1_score(y_val, y_pred, average="macro")
        weighted_f1 = f1_score(y_val, y_pred, average="weighted")

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
    best_pipe = trained_pipelines[best_model_name]
    print(f"\n👉 MÔ HÌNH TỐT NHẤT ĐƯỢC CHỌN (DỰA TRÊN VAL MACRO F1): {best_model_name}")

    # 5. Đánh giá cuối cùng trên Test Set (Chỉ chạy 1 lần)
    print("\n" + "=" * 75)
    print(f"4. ĐÁNH GIÁ CUỐI CÙNG TRÊN TẬP TEST SET ({best_model_name})")
    print("=" * 75)

    if "XGBoost" in best_model_name:
        X_test_proc = best_pipe.named_steps["prep"].transform(X_test)
        y_test_pred = best_pipe.named_steps["clf"].predict(X_test_proc)
        clf = best_pipe.named_steps["clf"]
    else:
        y_test_pred = best_pipe.predict(X_test)
        clf = best_pipe.named_steps["clf"]

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

    # 6. Trích xuất Feature Importance
    print("\n--- XẾP HẠNG TẦM QUAN TRỌNG CỦA ĐẶC TRƯNG (FEATURE IMPORTANCE) ---")
    all_feature_names = num_cols

    feature_importance_dict = {}
    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
        feat_imp_df = (
            pd.DataFrame({"Feature": all_feature_names, "Importance": importances})
            .sort_values(by="Importance", ascending=False)
            .reset_index(drop=True)
        )
        feat_imp_df["Importance (%)"] = (feat_imp_df["Importance"] * 100).round(2)
        print(feat_imp_df.to_string(index=False))
        feature_importance_dict = dict(
            zip(feat_imp_df["Feature"], feat_imp_df["Importance"].round(4))
        )

    # 7. Lưu Model và Metadata
    print("\n5. Lưu trữ Artifacts:")
    joblib.dump(best_pipe, model_save_path)
    print(f"✅ Đã lưu model tại: {model_save_path}")

    metadata = {
        "model_name": best_model_name,
        "model_type": str(type(clf).__name__),
        "task": "CEFR Word Classification (5 classes: A1-C1)",
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

"""
Script chuẩn bị cặp câu leveled cho Sentence Rewriter / Simplifier (Model 3b - Mục 2.7).

Input:
  - data/raw/sentence_simplification/asset_validation.csv (2.000 câu gốc)
  - data/raw/sentence_simplification/asset_test.csv (359 câu gốc)
  -> Tổng 2.359 câu gốc, mỗi câu có 10 bản simplification reference.

Xử lý:
  - Explode thành 23.590 cặp (original, rewrite).
  - Tính điểm FKGL và gán nhãn CEFR Proxy cho câu gốc (source_level) và câu viết lại (target_level):
      * FKGL <= 3.0       -> A1 (label 0)
      * 3.0 < FKGL <= 6.0  -> A2 (label 1)
      * 6.0 < FKGL <= 9.0  -> B1 (label 2)
      * 9.0 < FKGL <= 12.0 -> B2 (label 3)
      * FKGL > 12.0        -> C1 (label 4)
  - Giữ nguyên cột 'original' làm khóa group-split cho Mục 2.8.

Output: data/processed/sentence_rewrite_pairs.csv
"""

import sys
import os
import ast
import json
import unicodedata
import pandas as pd
import numpy as np
import textstat

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def map_fkgl_to_cefr(fkgl: float) -> tuple:
    """Ánh xạ điểm FKGL sang nhãn chuỗi CEFR và nhãn số nguyên (0-4)."""
    if fkgl <= 3.0:
        return "A1", 0
    elif fkgl <= 6.0:
        return "A2", 1
    elif fkgl <= 9.0:
        return "B1", 2
    elif fkgl <= 12.0:
        return "B2", 3
    else:
        return "C1", 4


def parse_simplifications(raw_val) -> list:
    """Phân giải chuỗi danh sách 10 bản simplification."""
    if isinstance(raw_val, list):
        return raw_val
    try:
        return ast.literal_eval(raw_val)
    except Exception:
        try:
            return json.loads(raw_val)
        except Exception:
            return []


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFC", text).strip()
    return " ".join(text.split())


def main():
    val_path = "data/raw/sentence_simplification/asset_validation.csv"
    test_path = "data/raw/sentence_simplification/asset_test.csv"
    output_csv = "data/processed/sentence_rewrite_pairs.csv"
    simplification_output_csv = "data/processed/sentence_rewrite_simplification_pairs.csv"

    if not os.path.exists(val_path) or not os.path.exists(test_path):
        print(f"❌ Error: Không tìm thấy tệp đầu vào ASSET tại {val_path} hoặc {test_path}")
        sys.exit(1)

    print("=" * 70)
    print("CAPYVOCAB ML - CHUẨN BỊ CẶP CÂU LEVELED MODEL 3b (MỤC 2.7)")
    print("=" * 70)

    # 1. Đọc dữ liệu ASSET
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)
    df_raw = pd.concat([df_val, df_test], ignore_index=True)
    print(f"1. Đọc ASSET dataset:")
    print(f"   - Validation: {len(df_val):,} câu gốc")
    print(f"   - Test      : {len(df_test):,} câu gốc")
    print(f"   -> Tổng số câu gốc: {len(df_raw):,}")

    # 2. Explode thành các cặp (original, rewrite)
    print("\n2. Đang explode 2.359 câu gốc x 10 references thành 23.590 cặp câu...")
    records = []

    for idx, row in df_raw.iterrows():
        orig_text = clean_text(row["original"])
        simps = parse_simplifications(row["simplifications"])

        # Tính FKGL và CEFR Proxy cho câu gốc (chỉ tính 1 lần / original)
        src_fkgl = round(float(textstat.flesch_kincaid_grade(orig_text)), 2)
        src_level, src_label = map_fkgl_to_cefr(src_fkgl)
        src_words = len(orig_text.split())

        for ref_idx, simp_text in enumerate(simps):
            rewrite_text = clean_text(simp_text)
            tgt_fkgl = round(float(textstat.flesch_kincaid_grade(rewrite_text)), 2)
            tgt_level, tgt_label = map_fkgl_to_cefr(tgt_fkgl)
            tgt_words = len(rewrite_text.split())

            compression_ratio = round(len(rewrite_text) / max(1, len(orig_text)), 4)

            records.append(
                {
                    "original": orig_text,
                    "rewrite": rewrite_text,
                    "ref_index": ref_idx,
                    "source_level": src_level,
                    "source_label": src_label,
                    "source_fkgl": src_fkgl,
                    "source_words": src_words,
                    "target_level": tgt_level,
                    "target_label": tgt_label,
                    "target_fkgl": tgt_fkgl,
                    "target_words": tgt_words,
                    "compression_ratio": compression_ratio,
                }
            )

    df_output = pd.DataFrame(records)
    df_output["task_direction"] = np.select(
        [
            df_output["target_label"] < df_output["source_label"],
            df_output["target_label"] == df_output["source_label"],
        ],
        ["simplify", "preserve"],
        default="upgrade_proxy_only",
    )

    # 3. Kiểm tra tiêu chuẩn nghiệm thu (Acceptance Criteria)
    print("\n" + "=" * 70)
    print("KIỂM TRA TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA):")
    print("=" * 70)

    total_pairs = len(df_output)
    print(f"✓ Tổng số dòng đầu ra: {total_pairs:,} (Kỳ vọng: 23,590)")
    assert total_pairs == 23590, f"Lỗi: Số dòng {total_pairs} != 23590"

    # Kiểm tra mỗi câu original xuất hiện đúng 10 lần
    counts_per_orig = df_output["original"].value_counts()
    exact_10_check = (counts_per_orig == 10).all()
    print(f"✓ Kiểm tra mỗi 'original' xuất hiện đúng 10 lần: {exact_10_check}")
    print(f"  - Số câu gốc duy nhất (Unique original): {len(counts_per_orig):,} câu")
    print(f"  - Min số reference/câu: {counts_per_orig.min()} | Max: {counts_per_orig.max()}")
    assert exact_10_check, "Lỗi: Có câu gốc không có đúng 10 references!"

    # Kiểm tra NaN
    nan_src = df_output["source_level"].isnull().sum()
    nan_tgt = df_output["target_level"].isnull().sum()
    print(f"✓ Kiểm tra giá trị NaN:")
    print(f"  - NaN ở cột 'source_level': {nan_src}")
    print(f"  - NaN ở cột 'target_level': {nan_tgt}")
    assert nan_src == 0 and nan_tgt == 0, "Lỗi: Phát hiện giá trị NaN!"
    print("  -> Đạt chuẩn 100% không có giá trị NaN!")

    # 4. Ma trận chuyển dịch cấp độ (Transition Matrix 5x5: source_level -> target_level)
    levels = ["A1", "A2", "B1", "B2", "C1"]
    trans_matrix = pd.crosstab(
        df_output["source_level"],
        df_output["target_level"],
        rownames=["Source Level (Original)"],
        colnames=["Target Level (Rewrite)"],
    ).reindex(index=levels, columns=levels, fill_value=0)

    print("\n--- MA TRẬN CHUYỂN DỊCH CẤP ĐỘ CEFR PROXY (5x5 TRANSITION MATRIX) ---")
    print(trans_matrix.to_string())

    # Thống kê xu hướng đơn giản hóa
    simpler_count = sum(df_output["target_label"] < df_output["source_label"])
    same_count = sum(df_output["target_label"] == df_output["source_label"])
    harder_count = sum(df_output["target_label"] > df_output["source_label"])

    print("\n--- THỐNG KÊ XU HƯỚNG ĐƠN GIẢN HÓA (SIMPLIFICATION TREND) ---")
    print(
        f"  - Giảm cấp độ khó (target_level < source_level): {simpler_count:>6,} cặp ({simpler_count/total_pairs*100:>5.2f}%)"
    )
    print(
        f"  - Giữ nguyên cấp độ (target_level == source_level): {same_count:>6,} cặp ({same_count/total_pairs*100:>5.2f}%)"
    )
    print(
        f"  - Tăng cấp độ nhẹ (target_level > source_level): {harder_count:>6,} cặp ({harder_count/total_pairs*100:>5.2f}%)"
    )
    print(
        f"  -> Tổng cặp giữ nguyên hoặc giảm độ khó: {simpler_count + same_count:,} ({(simpler_count + same_count)/total_pairs*100:.2f}%)"
    )

    # 5. Lưu file output
    os.makedirs("data/processed", exist_ok=True)
    df_output.to_csv(output_csv, index=False, encoding="utf-8")
    supported = df_output[df_output["task_direction"] != "upgrade_proxy_only"].copy()
    supported.to_csv(simplification_output_csv, index=False, encoding="utf-8")
    print(
        f"✅ Đã xuất {len(supported):,} cặp simplify/preserve được hỗ trợ vào: "
        f"{simplification_output_csv}"
    )
    print(f"\n✅ Đã lưu tệp kết quả vào: {output_csv}")

    # 6. In 5 dòng preview
    print("\n--- 5 DÒNG DỮ LIỆU XEM TRƯỚC (PREVIEW) ---")
    cols_preview = [
        "original",
        "rewrite",
        "source_level",
        "target_level",
        "source_fkgl",
        "target_fkgl",
        "compression_ratio",
    ]
    print(df_output[cols_preview].head(5).to_string(index=False))
    print("=" * 70)


if __name__ == "__main__":
    main()

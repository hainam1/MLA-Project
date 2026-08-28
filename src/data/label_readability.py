"""
Script gán nhãn độ đọc hiểu Readability (FKGL) sang CEFR Level cho câu ví dụ
(Model 3a: Example Generator - Mục 2.6).

Quy tắc phân khoảng ngưỡng Flesch-Kincaid Grade Level (FKGL -> CEFR Proxy):
  - FKGL <= 3.0       -> A1 (cefr_label = 0)
  - 3.0 < FKGL <= 6.0  -> A2 (cefr_label = 1)
  - 6.0 < FKGL <= 9.0  -> B1 (cefr_label = 2)
  - 9.0 < FKGL <= 12.0 -> B2 (cefr_label = 3)
  - FKGL > 12.0        -> C1 (cefr_label = 4)

Input: data/interim/english_examples_readability_filtered.csv (116.408 câu)
Output: data/processed/example_sentences_with_readability.csv
"""

import sys
import os
import pandas as pd
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


def main():
    input_interim_csv = "data/interim/english_examples_readability_filtered.csv"
    output_processed_csv = "data/processed/example_sentences_with_readability.csv"

    if not os.path.exists(input_interim_csv):
        print(f"❌ Error: Không tìm thấy tệp đầu vào tại {input_interim_csv}")
        sys.exit(1)

    print("=" * 70)
    print("CAPYVOCAB ML - GÁN NHÃN READABILITY CEFR CHO CÂU VÍ DỤ (MỤC 2.6)")
    print("=" * 70)

    # 1. Đọc dữ liệu interim
    print(f"1. Đang đọc tệp đầu vào: {input_interim_csv}...")
    df = pd.read_csv(input_interim_csv)
    initial_rows = len(df)
    print(f"   -> Tổng số câu ban đầu: {initial_rows:,}")

    # 2. Tính toán / Chuẩn hóa cột fkgl_score
    print("\n2. Đang kiểm tra và gán điểm FKGL (Flesch-Kincaid Grade Level)...")
    if "flesch_kincaid_grade" in df.columns:
        df["fkgl_score"] = df["flesch_kincaid_grade"].astype(float).round(2)
    else:
        df["fkgl_score"] = df["text"].apply(
            lambda x: round(float(textstat.flesch_kincaid_grade(str(x))), 2)
        )

    # 3. Ánh xạ sang CEFR Level (A1 - C1)
    print("3. Đang ánh xạ FKGL sang cấp độ CEFR Proxy (A1 - C1)...")
    cefr_mapping = df["fkgl_score"].apply(map_fkgl_to_cefr)
    df["cefr_level"] = [m[0] for m in cefr_mapping]
    df["cefr_label"] = [m[1] for m in cefr_mapping]

    # Sắp xếp thứ tự cột chuẩn
    cols_order = [
        "text",
        "source",
        "num_words",
        "num_chars",
        "fkgl_score",
        "flesch_reading_ease",
        "cefr_level",
        "cefr_label",
    ]
    df_output = df[cols_order].copy()

    # 4. Kiểm tra tiêu chuẩn nghiệm thu
    print("\n" + "=" * 70)
    print("KIỂM TRA TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA):")
    print("=" * 70)

    total_output_rows = len(df_output)
    nan_fkgl = df_output["fkgl_score"].isnull().sum()
    nan_cefr = df_output["cefr_level"].isnull().sum()

    print(f"✓ Tổng số dòng đầu ra: {total_output_rows:,} (Ban đầu: {initial_rows:,})")
    if total_output_rows == initial_rows:
        print("  -> Khớp 100% số lượng dòng, không có câu nào bị loại bỏ!")
    else:
        print(f"  -> Cảnh báo: Lệch {initial_rows - total_output_rows} dòng.")

    print(f"✓ Kiểm tra giá trị NaN:")
    print(f"  - NaN ở cột 'fkgl_score': {nan_fkgl}")
    print(f"  - NaN ở cột 'cefr_level' : {nan_cefr}")
    if nan_fkgl == 0 and nan_cefr == 0:
        print("  -> Đạt chuẩn 100% không có giá trị NaN!")

    # 5. Phân bố cấp độ CEFR
    print("\n--- PHÂN BỐ CÂU THEO CẤP ĐỘ CEFR PROXY (A1 -> C1) ---")
    dist = df_output["cefr_level"].value_counts()[["A1", "A2", "B1", "B2", "C1"]]
    for level, count in dist.items():
        pct = count / total_output_rows * 100
        bar = "█" * int(pct // 2)
        print(
            f"  Level {level:<2} ({map_fkgl_to_cefr({'A1': 0, 'A2': 4, 'B1': 7, 'B2': 10, 'C1': 13}[level])[1]}): {count:>7,} câu ({pct:>5.2f}%) | {bar}"
        )

    # 6. Lưu file output
    os.makedirs("data/processed", exist_ok=True)
    df_output.to_csv(output_processed_csv, index=False, encoding="utf-8")
    print(f"\n✅ Đã lưu tệp kết quả vào: {output_processed_csv}")

    # 7. In 5 dòng preview
    print("\n--- 5 DÒNG DỮ LIỆU XEM TRƯỚC (PREVIEW) ---")
    print(df_output.head(5).to_string(index=False))
    print("=" * 70)


if __name__ == "__main__":
    main()

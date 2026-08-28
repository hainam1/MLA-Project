"""
Script làm sạch và chuẩn hóa dữ liệu CEFR Wordlist (Mục 2.2).

Nhiệm vụ:
1. Đọc dữ liệu từ: data/raw/cefr_wordlist/WordsTeachersLevelsGoogleFrequenciesPredictions.csv
2. Loại bỏ nhãn 'Unknown' và cấp độ 'C2' (giữ lại 5 lớp A1-C1).
3. Chuẩn hóa chuỗi từ vựng (lowercase, strip khoảng trắng).
4. Xử lý các bản ghi trùng lặp (word, pos):
   - Tính trung bình điểm đánh giá giáo viên (teachers_avg) trên tất cả các lượt khảo sát.
   - Tái gán nhãn CEFR đồng thuận dựa trên công thức phân khoảng chính xác 100% của tác giả Guzey et al. (2014):
     + s < 1.5       -> A1 (0)
     + 1.5 <= s <= 2.5 -> A2 (1)
     + 2.5 < s < 3.5   -> B1 (2)
     + 3.5 <= s <= 4.5 -> B2 (3)
     + 4.5 < s <= 5.5  -> C1 (4)
     + s > 5.5         -> C2 (loại bỏ nếu có)
   - Lấy giá trị tần suất Google N-gram lớn nhất (max frequency) giữa các bản ghi hoa/thường để tránh rơi vào giá trị 0.
5. Xuất tệp dữ liệu sạch: data/processed/cefr_wordlist_clean.csv
6. Vẽ và lưu biểu đồ phân bố cấp độ: reports/figures/cefr_word_distribution.png
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def score_to_cefr_guzey(score: float) -> str:
    """
    Ánh xạ điểm đánh giá trung bình liên tục của giáo viên sang nhãn CEFR
    theo đúng phân khoảng chuẩn 100% của tác giả Guzey et al. (Zenodo 12501, 2014).
    """
    if score < 1.5:
        return "A1"
    elif score <= 2.5:
        return "A2"
    elif score < 3.5:
        return "B1"
    elif score <= 4.5:
        return "B2"
    elif score <= 5.5:
        return "C1"
    else:
        return "C2"


LABEL_MAPPING = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4}


def clean_and_deduplicate(raw_csv_path: str) -> pd.DataFrame:
    df_raw = pd.read_csv(raw_csv_path)
    total_raw = len(df_raw)
    print(f"1. Tổng số dòng dữ liệu thô ban đầu: {total_raw}")

    # Chuẩn hóa từ và PoS
    df_raw["word_clean"] = df_raw["Word"].astype(str).str.strip().str.lower()
    df_raw["pos_clean"] = df_raw["PoS"].astype(str).str.strip().str.upper()

    # Loại bỏ các từ rỗng / không hợp lệ
    df_raw = df_raw[df_raw["word_clean"].str.len() > 0].copy()

    # Lọc bỏ nhãn Unknown và C2
    c2_count = (df_raw["Level.Teachers.Average"] == "C2").sum()
    unknown_count = (df_raw["Level.Teachers.Average"] == "Unknown").sum()
    print(f"2. Loại bỏ:")
    print(f"   - Nhãn 'Unknown' : {unknown_count} dòng")
    print(f"   - Nhãn 'C2'      : {c2_count} dòng")

    valid_mask = ~df_raw["Level.Teachers.Average"].isin(["Unknown", "C2", np.nan])
    df_valid = df_raw[valid_mask].copy().reset_index(drop=True)
    print(f"3. Số dòng A1-C1 hợp lệ trước khi gộp trùng lặp: {len(df_valid)}")

    # Nhóm và gộp trùng lặp theo (word_clean, pos_clean)
    grouped_rows = []
    conflict_count = 0

    for (word, pos), group in df_valid.groupby(["word_clean", "pos_clean"]):
        # Tính trung bình điểm giáo viên
        mean_score = group["Teachers Avg"].mean()
        derived_level = score_to_cefr_guzey(mean_score)

        if len(group) > 1:
            unique_orig_levels = group["Level.Teachers.Average"].unique()
            if len(unique_orig_levels) > 1:
                conflict_count += 1

        # Lấy tần suất Google N-gram lớn nhất (để không bị 0 khi gộp chữ hoa/thường)
        max_freq = group["AvrgOfYears"].max() if pd.notna(group["AvrgOfYears"].max()) else 0.0

        if derived_level in LABEL_MAPPING:
            grouped_rows.append(
                {
                    "word": word,
                    "pos": pos,
                    "teachers_avg": round(float(mean_score), 4),
                    "cefr_level": derived_level,
                    "cefr_label": LABEL_MAPPING[derived_level],
                    "google_freq": float(max_freq),
                }
            )

    df_clean = pd.DataFrame(grouped_rows)
    # Sắp xếp lại theo word và pos
    df_clean = df_clean.sort_values(by=["word", "pos"]).reset_index(drop=True)

    print(f"4. Xử lý trùng lặp:")
    print(f"   - Số nhóm (word, pos) có nhãn xung đột đã được tái gán nhãn chuẩn: {conflict_count}")
    print(f"   - Số dòng sau khi loại bỏ trùng lặp và làm sạch hoàn chỉnh: {len(df_clean)}")
    print(f"   - Số dòng trùng lặp đã được gộp: {len(df_valid) - len(df_clean)}")

    return df_clean


def plot_distribution(df: pd.DataFrame, output_image_path: str):
    """Vẽ biểu đồ phân bố số lượng từ theo từng level (A1-C1)."""
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

    level_order = ["A1", "A2", "B1", "B2", "C1"]
    counts = df["cefr_level"].value_counts().reindex(level_order, fill_value=0)
    percentages = (counts / len(df) * 100).round(1)

    plt.figure(figsize=(9, 5.5), dpi=300)
    sns.set_theme(style="whitegrid")

    colors = ["#2ecc71", "#3498db", "#f1c40f", "#e67e22", "#e74c3c"]
    ax = sns.barplot(
        x=counts.index,
        y=counts.values,
        hue=counts.index,
        palette=colors,
        legend=False,
        edgecolor="black",
        linewidth=1.2,
    )

    # Ghi nhãn số lượng và phần trăm trên mỗi cột
    for i, (count, pct) in enumerate(zip(counts.values, percentages.values)):
        ax.text(
            i,
            count + 30,
            f"{count:,}\n({pct}%)",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    plt.title(
        "Phân Bố Cấp Độ Từ Vựng CEFR (A1 - C1)\nDataset: Zenodo 12501 (Istanbul Sehir University)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Cấp Độ CEFR (Target Level)", fontsize=11, fontweight="bold")
    plt.ylabel("Số Lượng Từ Vựng (Word Count)", fontsize=11, fontweight="bold")
    plt.ylim(0, max(counts.values) * 1.18)
    plt.tight_layout()

    plt.savefig(output_image_path, dpi=300)
    plt.close()
    print(f"5. Đã xuất biểu đồ phân bố vào: {output_image_path}")


def main():
    input_path = "data/raw/cefr_wordlist/WordsTeachersLevelsGoogleFrequenciesPredictions.csv"
    output_clean_csv = "data/processed/cefr_wordlist_clean.csv"
    output_chart_path = "reports/figures/cefr_word_distribution.png"

    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("reports/figures", exist_ok=True)

    print("=" * 70)
    print("CAPYVOCAB ML - TIỀN XỬ LÝ & LÀM SẠCH WORDLIST CEFR (MỤC 2.2)")
    print("=" * 70)

    df_clean = clean_and_deduplicate(input_path)
    df_clean.to_csv(output_clean_csv, index=False, encoding="utf-8")
    print(f"Đã lưu tệp dữ liệu sạch: {output_clean_csv}")

    plot_distribution(df_clean, output_chart_path)

    print("\n--- THỐNG KÊ PHÂN BỐ LEVEL TRÊN TẬP DỮ LIỆU SẠCH ---")
    print(df_clean["cefr_level"].value_counts()[["A1", "A2", "B1", "B2", "C1"]].to_string())
    print("=" * 70)


if __name__ == "__main__":
    main()

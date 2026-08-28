"""
Script làm sạch và chuẩn hóa dữ liệu câu CEFR Sentence Classification (Mục 2.3).

Nhiệm vụ:
1. Đọc dữ liệu từ 2 nguồn:
   - data/raw/cefr_sentence/cefr_sp_en_train.csv (CEFR-SP: 10.004 câu)
   - data/raw/cefr_sentence/readme_en_train.csv (README-EN: 2.822 câu)
2. Chuẩn hóa unicode (NFC), strip khoảng trắng thừa.
3. Loại bỏ nhãn C2 (230 câu ở CEFR-SP, 71 câu ở README-EN).
4. Khử trùng lặp nội bộ trong từng file và kiểm tra trùng lặp liên nguồn:
   - Trùng lặp nội bộ khớp nhãn: giữ 1 bản duy nhất.
   - Trùng lặp nội bộ xung đột nhãn (1 ca trong README-EN giữa A2 và B1): loại bỏ mẫu mơ hồ.
   - Trùng lặp liên nguồn giữa CEFR-SP và README-EN: 0 câu (2 tập hoàn toàn độc lập).
5. Gộp và xuất tệp dữ liệu sạch: data/processed/cefr_sentences_clean.csv (kèm cột 'source').
6. Vẽ biểu đồ phân bố cấp độ: reports/figures/cefr_sentence_distribution.png
"""

import sys
import os
import unicodedata
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

LABEL_MAPPING = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4}
VALID_LEVELS = list(LABEL_MAPPING.keys())


def normalize_text(text: str) -> str:
    """Chuẩn hóa Unicode NFC và chuẩn hóa khoảng trắng."""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFC", text)
    return " ".join(text.strip().split())


def clean_single_corpus(csv_path: str, source_name: str) -> pd.DataFrame:
    df_raw = pd.read_csv(csv_path)
    total_raw = len(df_raw)
    print(f"\n--- Đang xử lý nguồn: {source_name.upper()} ({csv_path}) ---")
    print(f"  1. Tổng số câu thô ban đầu: {total_raw:,}")

    # Chuẩn hóa text và level
    df_raw["text_clean"] = df_raw["text"].apply(normalize_text)
    df_raw["cefr_level_clean"] = df_raw["cefr_level"].astype(str).str.strip().str.upper()

    # Loại bỏ câu rỗng
    df_raw = df_raw[df_raw["text_clean"].str.len() > 0].copy()

    # Thống kê & lọc bỏ C2
    c2_count = (df_raw["cefr_level_clean"] == "C2").sum()
    invalid_count = (~df_raw["cefr_level_clean"].isin(VALID_LEVELS + ["C2"])).sum()
    print(f"  2. Loại bỏ nhãn C2: {c2_count:,} câu | Nhãn không hợp lệ: {invalid_count:,} câu")

    df_valid = df_raw[df_raw["cefr_level_clean"].isin(VALID_LEVELS)].copy().reset_index(drop=True)
    print(f"  3. Số câu A1-C1 hợp lệ trước khi khử trùng lặp: {len(df_valid):,}")

    # Khử trùng lặp nội bộ
    cleaned_rows = []
    conflict_count = 0
    duplicate_rows_merged = 0

    for text, group in df_valid.groupby("text_clean"):
        unique_levels = group["cefr_level_clean"].unique()
        if len(unique_levels) == 1:
            # Khớp nhãn hoặc chỉ có 1 bản ghi
            lvl = unique_levels[0]
            cleaned_rows.append(
                {
                    "text": text,
                    "cefr_level": lvl,
                    "cefr_label": LABEL_MAPPING[lvl],
                    "source": source_name,
                }
            )
            if len(group) > 1:
                duplicate_rows_merged += len(group) - 1
        else:
            # Xung đột nhãn nội bộ: loại bỏ mẫu gây nhiễu
            conflict_count += 1
            print(
                f"     ⚠️ Phát hiện xung đột nhãn nội bộ cho câu: '{text[:60]}...' -> Nhãn: {list(unique_levels)} (Đã loại bỏ để tránh nhiễu)"
            )

    df_clean = pd.DataFrame(cleaned_rows)
    print(f"  4. Kết quả sau làm sạch nội bộ:")
    print(f"     - Số dòng trùng lặp khớp nhãn đã gộp: {duplicate_rows_merged}")
    print(f"     - Số câu xung đột nhãn bị loại bỏ: {conflict_count}")
    print(f"     - Số câu sạch giữ lại: {len(df_clean):,}")

    return df_clean


def check_cross_source_duplicates(df_sp: pd.DataFrame, df_readme: pd.DataFrame):
    """Kiểm tra và báo cáo trùng lặp liên nguồn."""
    sp_texts = set(df_sp["text"])
    readme_texts = set(df_readme["text"])
    common = sp_texts.intersection(readme_texts)
    print("\n" + "=" * 70)
    print(f"KIỂM TRA TRÙNG LẶP LIÊN NGUỒN (CEFR-SP vs README-EN):")
    print(f"  - Số câu xuất hiện ở cả 2 nguồn: {len(common)}")
    if len(common) == 0:
        print(
            "  -> Hai nguồn dữ liệu HOÀN TOÀN ĐỘC LẬP (0 câu trùng nhau), không có xung đột liên nguồn."
        )
    else:
        print(f"  -> Cần xử lý {len(common)} câu trùng lặp giữa 2 nguồn.")
    print("=" * 70)


def plot_sentence_distribution(df: pd.DataFrame, output_image_path: str):
    """Vẽ biểu đồ phân bố số lượng câu theo từng level (A1-C1)."""
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

    for i, (count, pct) in enumerate(zip(counts.values, percentages.values)):
        ax.text(
            i,
            count + 80,
            f"{count:,}\n({pct}%)",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    plt.title(
        "Phân Bố Cấp Độ Câu CEFR (A1 - C1)\nDatasets: UniversalCEFR (cefr_sp_en + readme_en)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Cấp Độ CEFR (Sentence Level)", fontsize=11, fontweight="bold")
    plt.ylabel("Số Lượng Câu (Sentence Count)", fontsize=11, fontweight="bold")
    plt.ylim(0, max(counts.values) * 1.18)
    plt.tight_layout()

    plt.savefig(output_image_path, dpi=300)
    plt.close()
    print(f"\nĐã xuất biểu đồ phân bố câu vào: {output_image_path}")


def main():
    sp_path = "data/raw/cefr_sentence/cefr_sp_en_train.csv"
    readme_path = "data/raw/cefr_sentence/readme_en_train.csv"
    output_clean_csv = "data/processed/cefr_sentences_clean.csv"
    output_chart_path = "reports/figures/cefr_sentence_distribution.png"

    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("reports/figures", exist_ok=True)

    print("=" * 70)
    print("CAPYVOCAB ML - TIỀN XỬ LÝ & LÀM SẠCH CEFR SENTENCES (MỤC 2.3)")
    print("=" * 70)

    df_sp_clean = clean_single_corpus(sp_path, "cefr_sp")
    df_readme_clean = clean_single_corpus(readme_path, "readme_en")

    # Kiểm tra trùng lặp liên nguồn
    check_cross_source_duplicates(df_sp_clean, df_readme_clean)

    # Gộp 2 nguồn
    df_combined = pd.concat([df_sp_clean, df_readme_clean], ignore_index=True)
    df_combined.to_csv(output_clean_csv, index=False, encoding="utf-8")
    print(f"Đã lưu tệp câu sạch tổng hợp ({len(df_combined):,} câu) vào: {output_clean_csv}")

    # Vẽ biểu đồ
    plot_sentence_distribution(df_combined, output_chart_path)

    print("\n--- THỐNG KÊ PHÂN BỐ LEVEL TRÊN TẬP CÂU SẠCH (A1 - C1) ---")
    counts_table = df_combined["cefr_level"].value_counts()[["A1", "A2", "B1", "B2", "C1"]]
    for lvl, cnt in counts_table.items():
        pct = cnt / len(df_combined) * 100
        print(f"  - Cấp {lvl}: {cnt:,} câu ({pct:.2f}%)")
    print(f"  -> TỔNG CỘNG: {len(df_combined):,} câu")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
Script thu thập và lọc sơ bộ câu ví dụ tiếng Anh từ tập ngữ liệu song ngữ
(IWSLT 2015 + MTET) phục vụ huấn luyện Model 3a (Mục 1.7).

Quy trình lọc sơ bộ:
1. Đọc cột tiếng Anh ('en') từ 2 nguồn:
   - data/raw/translator_corpus/iwslt2015_en_vi_train.csv (133.317 câu)
   - data/raw/translator_corpus/mtet_sample5k.csv (5.000 câu)
2. Chuẩn hóa Unicode NFC, strip khoảng trắng và làm sạch dấu câu.
3. Lọc câu phù hợp làm câu ví dụ học từ vựng:
   - Độ dài: từ 4 đến 35 từ (không quá ngắn như cụm từ cộc lốc, không quá dài như đoạn văn).
   - Số ký tự: từ 15 đến 250 ký tự.
   - Kết thúc bằng dấu câu hợp lệ (. ? ! ").
   - Không chứa ký tự lạ / HTML tags / URL.
4. Tính toán sơ bộ chỉ số độ đọc hiểu Flesch-Kincaid Grade Level (FKGL) qua textstat.
5. Khử trùng lặp exact sentences.
6. Xuất dữ liệu tạm thời: data/interim/english_examples_readability_filtered.csv
"""

import sys
import os
import re
import html
import unicodedata
import pandas as pd
import textstat

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def clean_english_sentence(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Giải mã HTML entities (&apos; -> ', &quot; -> ", &amp; -> &)
    text = html.unescape(text)
    text = unicodedata.normalize("NFC", text).strip()
    # Loại bỏ khoảng trắng thừa
    text = " ".join(text.split())
    # Loại bỏ các tag HTML hoặc URL nếu có
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"http\S+|www\.\S+", "", text)
    return text.strip()


def is_valid_example_sentence(text: str) -> bool:
    if not text:
        return False
    # Kiểm tra độ dài ký tự
    if len(text) < 15 or len(text) > 250:
        return False
    # Đếm số từ
    words = text.split()
    if len(words) < 4 or len(words) > 35:
        return False
    # Kiểm tra có chứa chữ cái tiếng Anh không
    if not re.search(r"[a-zA-Z]", text):
        return False
    # Kiểm tra dấu câu kết thúc
    if not text.endswith((".", "?", "!", '"', "'", "”")):
        return False
    return True


def main():
    iwslt_path = "data/raw/translator_corpus/iwslt2015_en_vi_train.csv"
    mtet_path = "data/raw/translator_corpus/mtet_sample5k.csv"
    output_interim_csv = "data/interim/english_examples_readability_filtered.csv"

    os.makedirs("data/interim", exist_ok=True)

    print("=" * 70)
    print("CAPYVOCAB ML - THU THẬP & LỌC CÂU VÍ DỤ TIẾNG ANH CHO MODEL 3a (MỤC 1.7)")
    print("=" * 70)

    sentences = []

    # 1. Đọc IWSLT 2015 Train
    if os.path.exists(iwslt_path):
        df_iwslt = pd.read_csv(iwslt_path)
        print(f"1. Đọc IWSLT 2015 Train: {len(df_iwslt):,} câu...")
        for t in df_iwslt["en"]:
            cleaned = clean_english_sentence(t)
            if is_valid_example_sentence(cleaned):
                sentences.append({"text": cleaned, "source": "iwslt2015"})
    else:
        print(f"⚠️ Cảnh báo: Không tìm thấy {iwslt_path}")

    # 2. Đọc MTET Sample
    if os.path.exists(mtet_path):
        df_mtet = pd.read_csv(mtet_path)
        print(f"2. Đọc MTET Sample: {len(df_mtet):,} câu...")
        for t in df_mtet["en"]:
            cleaned = clean_english_sentence(t)
            if is_valid_example_sentence(cleaned):
                sentences.append({"text": cleaned, "source": "mtet"})
    else:
        print(f"⚠️ Cảnh báo: Không tìm thấy {mtet_path}")

    df_raw = pd.DataFrame(sentences)
    total_extracted = len(df_raw)
    print(f"\n3. Tổng số câu vượt qua bộ lọc độ dài/ký tự ban đầu: {total_extracted:,}")

    # 3. Khử trùng lặp câu
    df_dedup = df_raw.drop_duplicates(subset=["text"]).copy().reset_index(drop=True)
    print(
        f"4. Số câu sau khi khử trùng lặp: {len(df_dedup):,} (loại {total_extracted - len(df_dedup):,} câu trùng)"
    )

    # 4. Tính toán các chỉ số độ dài và độ đọc hiểu (FKGL)
    print("\n5. Đang tính toán độ dài từ và điểm Flesch-Kincaid Grade Level...")
    df_dedup["num_words"] = df_dedup["text"].apply(lambda x: len(x.split()))
    df_dedup["num_chars"] = df_dedup["text"].apply(len)
    df_dedup["flesch_kincaid_grade"] = df_dedup["text"].apply(
        lambda x: round(float(textstat.flesch_kincaid_grade(x)), 2)
    )
    df_dedup["flesch_reading_ease"] = df_dedup["text"].apply(
        lambda x: round(float(textstat.flesch_reading_ease(x)), 2)
    )

    # Xuất file interim
    df_dedup.to_csv(output_interim_csv, index=False, encoding="utf-8")
    print(f"\n✅ Đã lưu tập câu ví dụ interim ({len(df_dedup):,} câu) vào: {output_interim_csv}")

    # Thống kê phân bố độ dài
    print("\n--- THỐNG KÊ PHÂN BỐ ĐỘ DÀI CÂU VÍ DỤ ---")
    print(
        f"  - Độ dài từ trung bình: {df_dedup['num_words'].mean():.2f} từ (Min: {df_dedup['num_words'].min()}, Max: {df_dedup['num_words'].max()})"
    )
    print(
        f"  - Phân vị độ dài từ (25%, 50%, 75%): {df_dedup['num_words'].quantile(0.25):.0f} / {df_dedup['num_words'].quantile(0.50):.0f} / {df_dedup['num_words'].quantile(0.75):.0f} từ"
    )
    print(
        f"  - Điểm FKGL trung bình: {df_dedup['flesch_kincaid_grade'].mean():.2f} (Min: {df_dedup['flesch_kincaid_grade'].min()}, Max: {df_dedup['flesch_kincaid_grade'].max()})"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
Script làm sạch ngữ liệu song ngữ Việt - Anh (VI - EN) cho Model 1 (Translator).
(Mục 2.1 - Tiền xử lý dữ liệu dịch máy).

Đặc tả xử lý:
1. Đọc toàn bộ các tệp thô trong data/raw/translator_corpus/:
   - iwslt2015_en_vi_train.csv
   - iwslt2015_en_vi_validation.csv
   - iwslt2015_en_vi_test.csv
   - mtet_sample5k.csv
2. Giải mã HTML entities (html.unescape: &apos; -> ', &quot; -> ", &amp; -> &)
3. Chuẩn hóa Unicode NFC cho cả 2 phía tiếng Việt và tiếng Anh.
4. Lọc độ dài: cả 2 câu phải có từ 3 đến 64 từ (tokens).
   (Sử dụng whitespace/regex tokenization, tương thích trực tiếp với SentencePiece BPE của Opus-MT).
5. Loại bỏ dòng rỗng, lỗi encoding (mojibake), câu không chứa chữ cái, tỷ lệ độ dài bất thường.
6. Khử trùng lặp exact duplicate theo cặp (vi, en).

Output: data/processed/parallel_vi_en_clean.csv
"""

import sys
import os
import re
import html
import unicodedata
import pandas as pd
import numpy as np

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def clean_sentence_str(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Giải mã HTML entities
    text = html.unescape(text)
    # Chuẩn hóa Unicode NFC
    text = unicodedata.normalize("NFC", text).strip()
    # Loại bỏ khoảng trắng thừa
    text = " ".join(text.split())
    # Loại bỏ các tag HTML hoặc URL nếu có
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"http\S+|www\.\S+", "", text)
    return text.strip()


def count_words(text: str) -> int:
    return len(text.split())


def has_alphabetic(text: str) -> bool:
    return bool(
        re.search(
            r"[a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệđìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]",
            text,
            re.IGNORECASE,
        )
    )


def has_mojibake(text: str) -> bool:
    return "\ufffd" in text or "Ã" in text or "â€™" in text or "â€œ" in text


def main():
    raw_dir = "data/raw/translator_corpus"
    output_clean_csv = "data/processed/parallel_vi_en_clean.csv"

    file_sources = [
        ("iwslt2015_en_vi_train.csv", "iwslt_train"),
        ("iwslt2015_en_vi_validation.csv", "iwslt_val"),
        ("iwslt2015_en_vi_test.csv", "iwslt_test"),
        ("mtet_sample5k.csv", "mtet_sample"),
    ]

    print("=" * 70)
    print("CAPYVOCAB ML - LÀM SẠCH DỮ LIỆU SONG NGỮ VI-EN (MODEL 1 - MỤC 2.1)")
    print("=" * 70)

    raw_dfs = []
    print("1. Đọc và thống kê số dòng thực tế từ các tệp thô trong data/raw/translator_corpus/:")
    for fname, src in file_sources:
        fpath = os.path.join(raw_dir, fname)
        if os.path.exists(fpath):
            df = pd.read_csv(fpath)
            df["source"] = src
            print(f"   - {fname:<30} | {len(df):>8,} dòng")
            raw_dfs.append(df)
        else:
            print(f"   ⚠️ Không tìm thấy tệp: {fpath}")

    if not raw_dfs:
        print("❌ Lỗi: Không có dữ liệu đầu vào.")
        sys.exit(1)

    df_combined = pd.concat(raw_dfs, ignore_index=True)
    initial_total = len(df_combined)
    print(f"   -> TỔNG SỐ DÒNG THÔ BAN ĐẦU: {initial_total:,} cặp câu song ngữ.")

    # 2. Xử lý làm sạch và kiểm tra từng dòng
    print("\n2. Đang tiến hành làm sạch, chuẩn hóa Unicode NFC, giải mã HTML và lọc chất lượng...")

    clean_records = []
    drop_counts = {
        "empty_or_null": 0,
        "encoding_mojibake": 0,
        "no_alphabet": 0,
        "too_short (<3 words)": 0,
        "too_long (>64 words)": 0,
        "abnormal_length_ratio": 0,
    }

    for idx, row in df_combined.iterrows():
        vi_raw = row.get("vi", "")
        en_raw = row.get("en", "")
        src = row.get("source", "unknown")

        # Clean strings
        vi_clean = clean_sentence_str(vi_raw)
        en_clean = clean_sentence_str(en_raw)

        # Check empty
        if not vi_clean or not en_clean:
            drop_counts["empty_or_null"] += 1
            continue

        # Check mojibake
        if has_mojibake(vi_clean) or has_mojibake(en_clean):
            drop_counts["encoding_mojibake"] += 1
            continue

        # Check alphabet
        if not has_alphabetic(vi_clean) or not has_alphabetic(en_clean):
            drop_counts["no_alphabet"] += 1
            continue

        # Token count
        vi_len = count_words(vi_clean)
        en_len = count_words(en_clean)

        # Length bounds: 3 to 64 tokens
        if vi_len < 3 or en_len < 3:
            drop_counts["too_short (<3 words)"] += 1
            continue

        if vi_len > 64 or en_len > 64:
            drop_counts["too_long (>64 words)"] += 1
            continue

        # Length ratio check (0.25 to 4.0)
        len_ratio = vi_len / max(1, en_len)
        if len_ratio < 0.25 or len_ratio > 4.0:
            drop_counts["abnormal_length_ratio"] += 1
            continue

        clean_records.append(
            {"vi": vi_clean, "en": en_clean, "source": src, "vi_words": vi_len, "en_words": en_len}
        )

    df_cleaned_raw = pd.DataFrame(clean_records)
    after_filter_count = len(df_cleaned_raw)

    # 3. Khử trùng lặp
    print("\n3. Đang khử trùng lặp các cặp câu (vi, en)...")
    df_dedup = df_cleaned_raw.drop_duplicates(subset=["vi", "en"]).copy().reset_index(drop=True)
    exact_duplicates_count = after_filter_count - len(df_dedup)
    drop_counts["exact_duplicates"] = exact_duplicates_count

    final_total = len(df_dedup)
    total_dropped = initial_total - final_total

    # 4. Báo cáo tiêu chuẩn nghiệm thu
    print("\n" + "=" * 70)
    print("BÁO CÁO THỐNG KÊ TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA):")
    print("=" * 70)
    print(f"✓ Tổng số dòng ban đầu       : {initial_total:>8,} dòng (100.00%)")
    print(
        f"✓ Tổng số dòng sau khi lọc   : {final_total:>8,} dòng ({final_total/initial_total*100:>5.2f}%)"
    )
    print(
        f"✓ Tổng số dòng bị loại bỏ    : {total_dropped:>8,} dòng ({total_dropped/initial_total*100:>5.2f}%)"
    )

    print("\n--- CHI TIẾT SỐ LƯỢNG VÀ TỶ LỆ DÒNG BỊ LOẠI THEO TỪNG LÝ DO ---")
    for reason, count in drop_counts.items():
        pct = count / initial_total * 100
        print(f"  - {reason:<25}: {count:>6,} dòng ({pct:>5.2f}%)")

    # Kiểm tra null / rỗng
    null_vi = df_dedup["vi"].isnull().sum()
    null_en = df_dedup["en"].isnull().sum()
    empty_vi = sum(df_dedup["vi"].str.strip() == "")
    empty_en = sum(df_dedup["en"].str.strip() == "")
    duplicate_check = df_dedup.duplicated(subset=["vi", "en"]).sum()

    print(f"\n✓ Kiểm tra tính toàn vẹn của tệp đầu ra:")
    print(f"  - Giá trị Null (vi / en)       : {null_vi} / {null_en}")
    print(f"  - Giá trị Rỗng (vi / en)       : {empty_vi} / {empty_en}")
    print(f"  - Cặp câu trùng lặp còn sót    : {duplicate_check}")
    assert (
        null_vi == 0 and null_en == 0 and empty_vi == 0 and empty_en == 0
    ), "Lỗi: Còn giá trị rỗng/null!"
    assert duplicate_check == 0, "Lỗi: Còn cặp câu trùng lặp!"
    print("  -> Đạt chuẩn 100% không có dữ liệu rỗng, null hoặc trùng lặp!")

    # 5. Lưu file output
    os.makedirs("data/processed", exist_ok=True)
    df_dedup.to_csv(output_clean_csv, index=False, encoding="utf-8")
    print(f"\n✅ Đã xuất dữ liệu song ngữ sạch vào: {output_clean_csv}")

    # 6. Random sample 10 cặp câu để review
    print("\n--- 10 CẶP CÂU MẪU NGẪU NHIÊN REVIEW THỦ CÔNG (RANDOM SEED 42) ---")
    np.random.seed(42)
    sample_indices = np.random.choice(len(df_dedup), size=10, replace=False)
    for i, idx in enumerate(sample_indices, 1):
        row = df_dedup.iloc[idx]
        print(
            f"\n[Mẫu #{i} | Nguồn: {row['source']} | VI: {row['vi_words']} từ, EN: {row['en_words']} từ]"
        )
        print(f"  VI : {row['vi']}")
        print(f"  EN : {row['en']}")
    print("=" * 70)


if __name__ == "__main__":
    main()

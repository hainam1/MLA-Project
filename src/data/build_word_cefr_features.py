"""
Script trích xuất đặc trưng ngôn ngữ học (Linguistic Feature Extraction)
cho bài toán phân loại cấp độ từ vựng CEFR (Model 2a: CEFR Word Classifier).

Input:
  data/raw/cefr_wordlist/WordsTeachersLevelsGoogleFrequenciesPredictions.csv

Features extracted:
  - char_length: Độ dài từ theo số lượng ký tự.
  - syllable_count: Số lượng âm tiết tính bằng thư viện Pyphen (en_US).
  - vowel_count: Số nguyên âm trong từ.
  - vowel_ratio: Tỷ lệ nguyên âm trên tổng số ký tự.
  - google_freq: Tần suất từ Google N-gram trung bình (AvrgOfYears).
  - google_log_freq: Log10 của tần suất Google N-gram.
  - wordfreq_zipf: Điểm Zipf frequency tính từ wordfreq (thang điểm 0 - 8).
  - wordfreq_freq: Tần suất xuất hiện chuẩn hóa từ wordfreq.
  - pos: Từ loại (PoS) của từ.
  - teachers_avg: Điểm đánh giá trung bình từ 30 giáo viên (thang 1 - 6).
  - cefr_level: Nhãn chuỗi cấp độ CEFR (A1, A2, B1, B2, C1).
  - cefr_label: Nhãn số nguyên mục tiêu (0: A1, 1: A2, 2: B1, 3: B2, 4: C1).

Lọc dữ liệu:
  - Loại bỏ các mẫu nhãn 'Unknown' hoặc 'C2' để đảm bảo phạm vi 5 lớp A1-C1.
"""

import sys
import os
import argparse
import numpy as np
import pandas as pd
import pyphen
import wordfreq

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Khởi tạo bộ đếm âm tiết Pyphen tiếng Anh
dic_en = pyphen.Pyphen(lang='en_US')
VOWELS = set("aeiouyAEIOUY")

LABEL_MAPPING = {
    "A1": 0,
    "A2": 1,
    "B1": 2,
    "B2": 3,
    "C1": 4
}

def count_syllables(word: str) -> int:
    """Đếm số âm tiết của từ bằng Pyphen, fallback về ước lượng nguyên âm."""
    if not isinstance(word, str) or not word.strip():
        return 1
    w = word.strip().lower()
    hyphenated = dic_en.inserted(w)
    syllable_count = len(hyphenated.split('-')) if hyphenated else 1
    return max(1, syllable_count)

def extract_word_features(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Trích xuất toàn bộ feature matrix từ dataframe gốc."""
    # 1. Lọc nhãn: chỉ giữ A1, A2, B1, B2, C1
    mask_valid = df_raw['Level.Teachers.Average'].isin(LABEL_MAPPING.keys())
    df = df_raw[mask_valid].copy().reset_index(drop=True)

    features = []
    for _, row in df.iterrows():
        raw_word = str(row['Word']).strip() if pd.notna(row['Word']) else ""
        word_lower = raw_word.lower()
        
        char_len = len(word_lower)
        syl_cnt = count_syllables(word_lower)
        vowel_cnt = sum(1 for ch in word_lower if ch in VOWELS)
        vowel_rat = round(vowel_cnt / max(1, char_len), 4)

        # Google N-gram frequency từ dataset gốc
        google_f = float(row['AvrgOfYears']) if pd.notna(row.get('AvrgOfYears')) else 0.0
        google_log_f = round(float(np.log10(google_f + 1e-10)), 4)

        # Thư viện wordfreq (Zipf scale & raw frequency)
        wf_zipf = round(wordfreq.zipf_frequency(word_lower, 'en'), 4)
        wf_freq = float(wordfreq.word_frequency(word_lower, 'en'))

        pos_tag = str(row['PoS']).strip() if pd.notna(row['PoS']) else "UNKNOWN"
        t_avg = round(float(row['Teachers Avg']), 4) if pd.notna(row['Teachers Avg']) else 0.0

        level_str = str(row['Level.Teachers.Average']).strip()
        level_int = LABEL_MAPPING[level_str]

        features.append({
            "word": raw_word,
            "pos": pos_tag,
            "char_length": char_len,
            "syllable_count": syl_cnt,
            "vowel_count": vowel_cnt,
            "vowel_ratio": vowel_rat,
            "google_freq": google_f,
            "google_log_freq": google_log_f,
            "wordfreq_zipf": wf_zipf,
            "wordfreq_freq": wf_freq,
            "teachers_avg": t_avg,
            "cefr_level": level_str,
            "cefr_label": level_int
        })

    return pd.DataFrame(features)

def main():
    parser = argparse.ArgumentParser(description="Build CEFR Word Features Matrix")
    parser.add_argument("--preview_only", action="store_true", default=True, help="Xuất 100 dòng đầu preview")
    parser.add_argument("--full", action="store_true", help="Chạy toàn bộ dataset và xuất processed data")
    args = parser.parse_args()

    input_path = "data/raw/cefr_wordlist/WordsTeachersLevelsGoogleFrequenciesPredictions.csv"
    preview_output_path = "data/processed/cefr_word_features_preview.csv"
    full_output_path = "data/processed/cefr_word_features.csv"

    os.makedirs("data/processed", exist_ok=True)

    if not os.path.exists(input_path):
        print(f"❌ Error: Không tìm thấy file đầu vào: {input_path}")
        sys.exit(1)

    print("=" * 70)
    print("CAPYVOCAB ML - TRÍCH XUẤT ĐẶC TRƯNG CEFR WORDLIST (PHASE 1 PART B.2)")
    print("=" * 70)
    print(f"Đọc dữ liệu thô: {input_path}")
    df_raw = pd.read_csv(input_path)
    print(f"Tổng số dòng ban đầu: {len(df_raw)}")
    
    # Thống kê mẫu bị loại
    c2_count = (df_raw['Level.Teachers.Average'] == 'C2').sum()
    unknown_count = (df_raw['Level.Teachers.Average'] == 'Unknown').sum()
    print(f"  - Số mẫu C2 bị loại       : {c2_count}")
    print(f"  - Số mẫu Unknown bị loại  : {unknown_count}")
    print(f"  - Số mẫu A1-C1 hợp lệ     : {len(df_raw) - c2_count - unknown_count}")

    print("\nĐang tiến hành trích xuất đặc trưng ngôn ngữ học...")
    df_features = extract_word_features(df_raw)
    print(f"Trích xuất thành công: {len(df_features)} dòng x {len(df_features.columns)} cột")

    # Xuất file preview 100 dòng đầu
    df_preview = df_features.head(100)
    df_preview.to_csv(preview_output_path, index=False, encoding="utf-8")
    print(f"\n✅ Đã xuất 100 dòng preview vào: {preview_output_path}")

    if args.full:
        df_features.to_csv(full_output_path, index=False, encoding="utf-8")
        print(f"✅ Đã xuất toàn bộ dataset vào: {full_output_path}")

    print("\n--- XEM TRƯỚC 5 DÒNG ĐẦU TIÊN CỦA BẢNG ĐẶC TRƯNG ---")
    print(df_preview[['word', 'pos', 'char_length', 'syllable_count', 'wordfreq_zipf', 'google_log_freq', 'cefr_level', 'cefr_label']].head(5).to_string(index=False))
    print("=" * 70)

if __name__ == "__main__":
    main()

# Nhật Ký Tiến Độ Dự Án (Project Progress Log)

Tài liệu ghi lại toàn bộ quá trình phát triển, các quyết định kỹ thuật, thử nghiệm và kết quả theo từng buổi làm việc nhằm phục vụ báo cáo và bảo vệ đề tài CapyVocab ML.

---

## [2026-08-27]
- **Việc đã làm:**
  - **[Phase 0] Khởi tạo dự án & Thiết lập môi trường:**
    + Tạo cây thư mục chuẩn ML Pipeline: `data/` (`raw`, `interim`, `processed`), `notebooks/`, `src/` (`data`, `models/`, `eval`, `pipeline`), `reports/figures/`, `configs/`, `logs/`, `tests/`.
    + Cập nhật cấu trúc phân nhánh xử lý từ và câu (Word & Sentence Branching):
      * `src/models/translator/`: Model 1 (Dịch nghĩa ngữ cảnh Việt -> Anh: VI -> EN, base model: `Helsinki-NLP/opus-mt-vi-en`)
      * `src/models/cefr_word_classifier/`: Model 2a (Phân loại CEFR cho từ vựng, A1-C1)
      * `src/models/cefr_sentence_classifier/`: Model 2b (Phân loại CEFR cho câu, A1-C1)
      * `src/models/example_generator/`: Model 3a (Sinh câu ví dụ theo từ & cấp độ A1-C1)
      * `src/models/sentence_rewriter/`: Model 3b (Viết lại câu theo cấp độ CEFR mục tiêu A1-C1)
      * `src/models/second_pair_of_eyes/`: Model 4 (Kiểm duyệt chất lượng & độ chính xác)
    + Thiết lập Git repository (`git init`) và `.gitignore`.
    + Viết tài liệu `README.md` mô tả 2 chế độ input (`word_mode` & `sentence_mode`), chiều dịch VI -> EN và hướng dẫn cài đặt.
    + Tạo môi trường ảo `.venv` (Python 3.12.13), cài đặt 201 packages qua `requirements.txt` kèm `spaCy` và model `en_core_web_sm`.
    + Viết và chạy `src/_env_check.py` đạt 11/11 [OK], nhận diện GPU NVIDIA GeForce RTX 5060 Laptop GPU (CUDA 12.4).
  - **[Phase 1 - Part A] Đặc tả bài toán & Bộ định tuyến Input:**
    + Viết tài liệu đặc tả hệ thống chuẩn học thuật tiếng Anh: `reports/01_task_formulation.md` (Motivation CapyVocabApp, Dual-Branching Architecture, phân tích tính phi tuyến cú pháp của Sentence CEFR vs Word CEFR).
    + Xác nhận phạm vi cấp độ chính thức cho toàn bộ pipeline là **A1 đến C1 (5 classes: A1, A2, B1, B2, C1)**; phân bổ cấp độ **C2 vào Future Work** do hạn chế dữ liệu gán nhãn đáng tin cậy trong các tập dữ liệu mở.
    + Làm rõ thiết kế Model 2b: Thuộc hoàn toàn họ **Classical ML** (XGBoost/Random Forest); baseline chính sử dụng bộ đặc trưng ngôn ngữ học thủ công (Readability, spaCy syntactic tree, word frequency); DeBERTa (nếu dùng) chỉ đóng vai trò bộ trích xuất embedding tĩnh (frozen, không fine-tune).
    + Nâng cấp `src/pipeline/input_type_detector.py`: Thêm trạng thái `"invalid_input"` cho chuỗi rỗng / khoảng trắng; vượt qua 100% (14/14) test cases kiểm thử tự động.
  - **[Phase 1 - Part B.1] Thu thập dữ liệu từ HuggingFace & Zenodo:**
    + **Model 1 (Translator VI-EN)**: Tải bộ dữ liệu `phongmt184172/mtet` (4.2M câu) làm nguồn chính và `thainq107/iwslt2015-en-vi` (133k câu, nghiên cứu học thuật) làm tập đánh giá chuẩn; lập `data/raw/translator_corpus/SOURCE.md`.
    + **Model 2a (CEFR Word Classifier)**: Tải và giải nén bộ dữ liệu chuẩn Zenodo Record 12501 (Istanbul Sehir University 2014, CC-BY-4.0) gồm 7.000 từ thẩm định bởi 30 giáo viên và 51.352 từ mở rộng; lập `data/raw/cefr_wordlist/SOURCE.md`.
    + **Model 2b (CEFR Sentence Classifier)**: Tải thành công `UniversalCEFR/cefr_sp_en` (10.004 câu, CC-BY-NC-SA-4.0) và `UniversalCEFR/readme_en` (2.822 câu, CC-BY-NC-SA-4.0); lập `data/raw/cefr_sentence/SOURCE.md`.
    + **Model 3b (Sentence Rewriter)**: Tải thành công `facebook/asset` (2.000 validation + 359 test sentences, CC-BY-NC-4.0) gồm các cặp câu gốc và 10 bản viết lại đơn giản hóa; lập `data/raw/sentence_simplification/SOURCE.md`.
    + Viết script tự động hóa tải dữ liệu tập trung `src/data/download_datasets.py`.
  - **[Phase 1 - Part B.2] Xác thực Giấy phép, Thống kê C2 & Bắt đầu Trích xuất Đặc trưng Từ vựng:**
    + Kiểm tra trực tiếp license của `phongmt184172/mtet`: Metadata card trên HuggingFace không khai báo license tag; upstream repository chính thức `vietai/mTet` được phát hành theo giấy phép **CC-BY-NC-SA-4.0** (phi thương mại, phục vụ nghiên cứu & học thuật).
    + Thống kê số lượng mẫu C2 sẽ được loại bỏ trong bước làm sạch:
      * `cefr_wordlist`: 191 mẫu C2 (2,73%) bị loại, cùng 1.056 mẫu Unknown, giữ lại 5.753 mẫu chuẩn A1-C1.
      * `cefr_sp_en`: 230 mẫu C2 (2,30%) bị loại, giữ lại 9.774 câu A1-C1.
      * `readme_en`: 71 mẫu C2 (2,52%) bị loại, giữ lại 2.751 câu A1-C1.
    + Làm rõ giải pháp gán nhãn CEFR Proxy cho ASSET trong `SOURCE.md`: Sử dụng chỉ số đọc hiểu Flesch-Kincaid Grade Level kết hợp Dale-Chall Score qua `textstat` để ước lượng cấp độ cho câu gốc và bản viết lại ở Phase 2.7.
    + Viết script `src/data/build_word_cefr_features.py`: Trích xuất 10+ đặc trưng ngôn ngữ học (độ dài, số âm tiết Pyphen, tỷ lệ nguyên âm, Google N-gram frequency, log frequency, Zipf score & frequency qua `wordfreq`, PoS tag, teachers average score) và xuất thành công `data/processed/cefr_word_features_preview.csv` (100 dòng đầu).

- **Vấn đề gặp phải & Giải pháp:**
  - Python mặc định không nằm trong PATH hệ thống; đã sử dụng `uv` với CPython 3.12 để tạo `.venv` và cài đặt các thư viện Deep Learning nhanh chóng.
  - Xảy ra xung đột phiên bản giữa `datasets`, `pyarrow` và `huggingface-hub` khi nâng cấp; đã giải quyết triệt để bằng cách cố định `datasets>=3.0.0,<3.5.0`, `pyarrow<19.0.0` và `huggingface-hub<1.0,>=0.34.0`.
  - Link gốc của `IWSLT/mt_eng_vietnamese` trỏ về server Stanford NLP (`nlp.stanford.edu`) bị nghẽn mạng/timeout; đã khắc phục bằng cách sử dụng mirror sạch tương thích hoàn toàn `thainq107/iwslt2015-en-vi` trên HuggingFace.

- **Việc tiếp theo:**
  - [Phase 1 - Part B.3] Xây dựng script trích xuất đặc trưng cú pháp và độ đọc hiểu cho câu `src/data/build_sentence_cefr_features.py` (spaCy dependency depth, POS ratios, Flesch-Kincaid, ARI, Dale-Chall).
  - [Phase 1 - Part B.4] Hoàn thiện toàn bộ pipeline làm sạch, gán nhãn và xuất các tập Train/Val/Test chuẩn hóa vào `data/processed/`.

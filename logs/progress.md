# Nhật Ký Tiến Độ Dự Án (Project Progress Log)

Tài liệu ghi lại toàn bộ quá trình phát triển, các quyết định kỹ thuật, thử nghiệm và kết quả theo từng buổi làm việc nhằm phục vụ báo cáo và bảo vệ đề tài CapyVocab ML.

---

## [2026-08-27]
- **Việc đã làm:**
  - **[Phase 0] Khởi tạo dự án & Thiết lập môi trường:**
    + Tạo cây thư mục chuẩn ML Pipeline: `data/` (`raw`, `interim`, `processed`), `notebooks/`, `src/` (`data`, `models/`, `eval`, `pipeline`), `reports/figures/`, `configs/`, `logs/`, `tests/`.
    + Cập nhật cấu trúc phân nhánh xử lý từ và câu (Word & Sentence Branching):
      * `src/models/translator/`: Model 1 (Dịch nghĩa ngữ cảnh Việt -> Anh: VI -> EN, base model: `Helsinki-NLP/opus-mt-vi-en`)
      * `src/models/cefr_word_classifier/`: Model 2a (Phân loại CEFR cho từ vựng)
      * `src/models/cefr_sentence_classifier/`: Model 2b (Phân loại CEFR cho câu)
      * `src/models/example_generator/`: Model 3a (Sinh câu ví dụ theo từ & cấp độ)
      * `src/models/sentence_rewriter/`: Model 3b (Viết lại câu theo cấp độ CEFR mục tiêu)
      * `src/models/second_pair_of_eyes/`: Model 4 (Kiểm duyệt chất lượng & độ chính xác)
    + Thiết lập Git repository (`git init`) và `.gitignore`.
    + Viết tài liệu `README.md` mô tả 2 chế độ input (`word_mode` & `sentence_mode`) và hướng dẫn cài đặt.
    + Tạo môi trường ảo `.venv` (Python 3.12.13), cài đặt 201 packages qua `requirements.txt` kèm `spaCy` và model `en_core_web_sm`.
    + Viết và chạy `src/_env_check.py` đạt 11/11 [OK], nhận diện GPU NVIDIA GeForce RTX 5060 Laptop GPU (CUDA 12.4).
  - **[Phase 1 - Part A] Đặc tả bài toán & Bộ định tuyến Input:**
    + Viết tài liệu đặc tả hệ thống chuẩn học thuật tiếng Anh: `reports/01_task_formulation.md` (Motivation, Dual-Branching Architecture, lý do cần Machine Learning cho Sentence vs Word CEFR, và bảng Input/Output/Features/Labels cho toàn bộ 6 models).
    + Viết và kiểm thử module `src/pipeline/input_type_detector.py` với rule phân loại <= 3 tokens & không có dấu câu kết thúc; vượt qua 100% (12/12) test cases gồm các edge cases (phrasal verbs, idioms, câu ngắn có dấu, câu dài không dấu).

- **Vấn đề gặp phải:**
  - Python mặc định không nằm trong PATH hệ thống; đã sử dụng `uv` với CPython 3.12 để tạo `.venv` và cài đặt các thư viện Deep Learning nhanh chóng.
  - Xảy ra xung đột phiên bản giữa `datasets`, `pyarrow` và `huggingface-hub` khi nâng cấp; đã giải quyết triệt để bằng cách cố định `datasets>=3.0.0,<3.5.0`, `pyarrow<19.0.0` và `huggingface-hub<1.0,>=0.34.0`.
  - Terminal Windows sử dụng bảng mã mặc định cp1252 gây lỗi Unicode khi in tiếng Việt; đã cấu hình tự động `sys.stdout.reconfigure(encoding='utf-8')` trong các script CLI.

- **Việc tiếp theo:**
  - [Phase 1 - Part B] Xây dựng module trích xuất đặc trưng ngôn ngữ học `src/data/features.py` (Zipf, syllable, readability, syntax).
  - Thu thập và tiền xử lý bộ dữ liệu CEFR Wordlist (Oxford/EVP) và CEFR Sentences.

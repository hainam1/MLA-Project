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

- **Vấn đề gặp phải:**
  - Python mặc định không nằm trong PATH hệ thống; đã sử dụng `uv` với CPython 3.12 để tạo `.venv` và cài đặt các thư viện Deep Learning nhanh chóng.
  - Xảy ra xung đột phiên bản giữa `datasets`, `pyarrow` và `huggingface-hub` khi nâng cấp; đã giải quyết triệt để bằng cách cố định `datasets>=3.0.0,<3.5.0`, `pyarrow<19.0.0` và `huggingface-hub<1.0,>=0.34.0`.
  - Terminal Windows sử dụng bảng mã mặc định cp1252 gây lỗi Unicode khi in tiếng Việt; đã cấu hình tự động `sys.stdout.reconfigure(encoding='utf-8')` trong các script CLI.

- **Việc tiếp theo:**
  - [Phase 1 - Part B] Xây dựng module trích xuất đặc trưng ngôn ngữ học `src/data/features.py` (Zipf frequency, syllable counts, readability indices, spaCy syntactic depth).
  - Thu thập và tiền xử lý bộ dữ liệu CEFR Wordlist (Oxford/EVP) và CEFR Sentences (A1–C1).

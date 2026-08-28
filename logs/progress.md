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
    + **Model 3b (Sentence Rewriter)**: Tải thành công `facebook/asset` (2.000 validation + 359 test sentences, CC-BY-NC-4.0) gồm các cặp câu gốc và 10 bản viết lại đơn giản hóa (tổng 23.590 cặp sau khi explode); lập `data/raw/sentence_simplification/SOURCE.md`.
    + Viết script tự động hóa tải dữ liệu tập trung `src/data/download_datasets.py`.
  - **[Phase 1 - Part B.2] Báo Cáo Bản Quyền Dữ Liệu & Nguyên Tắc Chống Leakage:**
    + Tạo `reports/00_dataset_licenses.md` dạng bảng master tổng hợp bản quyền 6 datasets.
    + Xác lập nguyên tắc Group-based Split theo `original` cho Model 3b và bộ ngưỡng Flesch-Kincaid đồng nhất cho CEFR Proxy.
    + Thêm giải trình đánh đổi thiết kế khi gom cụm near-duplicate và template thống kê cho Model 2b.
  - **[Phase 1.7] Thu Thập & Lọc Câu Ví Dụ Tiếng Anh (Model 3a):**
    + Viết script `src/data/collect_english_examples.py`: Trích xuất phía target tiếng Anh từ IWSLT 2015 Train và MTET Sample, chuẩn hóa Unicode NFC, unescape HTML entities, lọc câu có độ dài chuẩn 4–35 từ (15–250 ký tự), kết thúc bằng dấu câu hợp lệ.
    + Khử trùng lặp và xuất thành công **116.408 câu ví dụ sạch** vào `data/interim/english_examples_readability_filtered.csv` (độ dài trung bình 16.53 từ, FKGL trung bình 6.54).
  - **[Phase 2.2 & 2.4] Làm Sạch Wordlist CEFR & Xuất Toàn Bộ Đặc Trưng Từ Vựng:**
    + Viết script `src/data/clean_cefr_wordlist.py`: Khử trùng lặp và làm sạch 5.697 từ vựng, vẽ biểu đồ `reports/figures/cefr_word_distribution.png`.
    + Xác thực 100% (5.753/5.753 dòng) công thức phân khoảng liên tục của Guzey et al. (2014) trong `01_task_formulation.md` (mục 6.1).
    + Chạy `build_word_cefr_features.py --full` xuất toàn bộ 5.697 dòng đặc trưng sạch vào `data/processed/cefr_word_features.csv`.
  - **[Phase 2.3 & 2.5] Làm Sạch Câu CEFR & Xuất Toàn Bộ Đặc Trưng Câu (Model 2b):**
    + Viết script `src/data/clean_cefr_sentences.py`: Chuẩn hóa Unicode NFC, loại bỏ 301 câu C2, khử trùng lặp và loại bỏ 1 câu xung đột nhãn nội bộ, xuất `data/processed/cefr_sentences_clean.csv` (12.521 câu) và vẽ biểu đồ `reports/figures/cefr_sentence_distribution.png`.
    + Triển khai Union-Find xác định 504 cụm đa biến thể (1.032 câu) phục vụ `StratifiedGroupKFold`.
    + Viết script `src/data/build_sentence_cefr_features.py`: Trích xuất 23 đặc trưng đa chiều (Surface, Lexical Zipf, Word-level CEFR qua spaCy Lemmatization, Syntax Tree Depth, Subclause ratio, Passives, POS ratios, Readability metrics).
    + Chạy `--full` thành công xuất toàn bộ **12.521 dòng $\times$ 27 cột** vào `data/processed/cefr_sentence_features.csv` (tỷ lệ phủ từ vựng đạt **88.61%**, OOV toàn cục chỉ **11.39%**, 0 giá trị NaN).

  - **[Phase 2.6] Gán Nhãn Readability CEFR Proxy Cho Câu Ví Dụ (Model 3a):**
    + Viết script `src/data/label_readability.py`: Ánh xạ điểm FKGL sang 5 cấp độ CEFR Proxy (A1: $\le 3$, A2: $3-6$, B1: $6-9$, B2: $9-12$, C1: $>12$).
    + Gán nhãn thành công toàn bộ **116.408 câu ví dụ** xuất vào `data/processed/example_sentences_with_readability.csv` (A1: 23.32%, A2: 23.64%, B1: 23.32%, B2: 18.74%, C1: 10.98%, 0 giá trị NaN).

  - **[Phase 2.7] Chuẩn Bị Cặp Câu Leveled Cho Sentence Rewriter (Model 3b):**
    + Viết script `src/data/prepare_sentence_rewrite_pairs.py`: Explode 2.359 câu gốc ASSET $\times$ 10 references thành **23.590 cặp câu** sạch.
    + Tính FKGL và gán nhãn CEFR Proxy cho `source_level` và `target_level`, giữ nguyên vẹn cột `original` làm khóa group-split.
    + Xuất thành công toàn bộ **23.590 dòng** vào `data/processed/sentence_rewrite_pairs.csv` (59.97% giảm độ khó, 36.72% giữ nguyên cấp độ, 0 giá trị NaN, mỗi `original` xuất hiện đúng 10 lần).

  - **[Phase 2.1] Làm Sạch Dữ Liệu Song Ngữ VI-EN (Model 1):**
    + Viết script `src/data/clean_parallel_corpus.py`: Đọc 140.853 cặp câu thô từ IWSLT (train, val, test) + MTET sample.
    + Chuẩn hóa Unicode NFC, giải mã HTML entities, lọc câu 3–64 từ, loại lỗi encoding/rác, khử trùng lặp.
    + Xuất thành công **132.589 cặp câu song ngữ sạch** vào `data/processed/parallel_vi_en_clean.csv` (0 null, 0 rỗng, 0 trùng lặp).

  - **[Phase 2.8] Phân Chia Train/Val/Test (70/15/15) Cho Toàn Bộ 5 Models:**
    + Viết script `src/data/split_datasets.py`: Áp dụng chiến lược chống rò rỉ dữ liệu (Anti-Leakage) chuyên biệt cho từng bài toán.
    + Model 1 (Translator): Split theo unique câu tiếng Việt (`vi`) $\to$ Train 92.8k (69.99%), Val 19.8k (15.00%), Test 19.9k (15.01%).
    + Model 2a (Word CEFR): Stratified split theo `cefr_label` $\to$ Train 3.987 (69.98%), Val 855 (15.01%), Test 855 (15.01%).
    + Model 2b (Sentence CEFR): `StratifiedGroupKFold` theo `cluster_id` (11.993 cụm Union-Find) $\to$ Train 8.766 (70.01%), Val 1.878 (15.00%), Test 1.877 (14.99%).
    + Model 3a (Example Gen): Stratified split theo `cefr_level` $\to$ Train 81.485 (70.00%), Val 17.461 (15.00%), Test 17.462 (15.00%).
    + Model 3b (Sentence Rewriter): Group split theo `original` (2.359 câu gốc x 10 refs) $\to$ Train 16.510 (69.99%), Val 3.530 (14.96%), Test 3.550 (15.05%).
    + Xuất thành công toàn bộ **15 tệp phân chia** vào `data/processed/`.

- **KẾT LUẬN GIAI ĐOẠN:**
  - 👉 **PHASE 2 (Data Preprocessing & Feature Engineering) ĐÃ HOÀN TẤT 100%!**

- **[Phase 3.1] Huấn Luyện Model 2a (CEFR Word Classifier - Classical ML):**
  - Viết script `src/models/cefr_word_classifier/train.py`.
  - Không gian đặc trưng: 9 đặc trưng (8 numerical + 1 categorical POS OneHotEncoded). Đã cô lập tuyệt đối `teachers_avg` và `word`.
  - So sánh trên Validation set:
    * Logistic Regression (Baseline): Acc 37.08%, Macro F1 0.3741
    * XGBoost (Tuned): Acc 38.95%, Macro F1 0.3885
    * **Random Forest (Tuned)**: Acc **38.95%**, Macro F1 **0.3920** (Được chọn là best model)
  - Đánh giá trên Test set:
    * Accuracy: **39.88%** | Macro F1: **0.3966** | Weighted F1: **0.3985**
    * Ma trận nhầm lẫn $5 \times 5$ tập trung dày đặc ở đường chéo chính và các lớp liền kề (chuẩn ordinal classification).
    * Phân tích Feature Importance: `wordfreq_zipf` (25.98%), `wordfreq_freq` (24.07%), `google_log_freq` (11.96%), `google_freq` (10.01%) đóng góp $>72\%$ sức mạnh phân loại.
  - Xuất thành công `model.pkl` và `metadata.json` vào `src/models/cefr_word_classifier/`.

- **[Phase 3.2] Huấn Luyện Model 2b (CEFR Sentence Classifier - Classical ML):**
  - Viết script `src/models/cefr_sentence_classifier/train.py`.
  - Không gian đặc trưng: 25 đặc trưng toán học & ngôn ngữ học (5 Surface, 3 Lexical, 3 Word CEFR, 9 Syntax & POS, 5 Readability). Đã cô lập tuyệt đối `text`, `source`, `cluster_id`.
  - So sánh trên Validation set:
    * Logistic Regression (Baseline): Acc 49.09%, Macro F1 0.4668
    * XGBoost (Tuned - Weighted): Acc 52.29%, Macro F1 0.5185
    * Gradient Boosting (Default): Acc 57.24%, Macro F1 0.5415
    * **Random Forest (Tuned)**: Acc **54.31%**, Macro F1 **0.5562** (Được chọn là best model)
  - Đánh giá trên Test set:
    * Accuracy: **54.34%** | Macro F1: **0.5325** | Weighted F1: **0.5413**
    * Vượt trội baseline Logistic Regression (+6.57% F1) và vượt trội Model 2a (+13.59% F1) nhờ sự bổ sung mạnh mẽ của cú pháp và độ đọc hiểu.
    * Lớp hiếm A1 bắt được 21/45 câu (Recall 46.67%, F1 0.4828). Lớp C1 bắt được 230/318 câu (Recall 72.33%, F1 0.5982).
    * Phân tích Feature Importance theo 5 nhóm: Surface (27.57%), Readability (26.23%), Lexical Rarity (16.40%), Syntax & POS (16.05%), Word CEFR (13.75%).
  - Xuất thành công `model.pkl` và `metadata.json` vào `src/models/cefr_sentence_classifier/`.

- **KẾT LUẬN GIAI ĐOẠN:**
  - 👉 **PHASE 3 (Huấn Luyện Các Mô Hình Classical ML - Model 2a & 2b) ĐÃ HOÀN TẤT 100%!**

- **[Phase 4] Huấn Luyện Fine-tune & Đánh Giá Model 1 (Translator VI -> EN):**
  - Base model: `Helsinki-NLP/opus-mt-vi-en` (MarianMT Seq2Seq, ~74M parameters).
  - Tải dữ liệu song ngữ sạch: `data/processed/model1_translator_{train,val,test}.csv` (Train 92.800, Val 19.885, Test 19.904 cặp câu).
  - Xử lý vấn đề xung đột Windows OpenMP DLL (`0xC0000005 ACCESS_VIOLATION`) bằng `KMP_DUPLICATE_LIB_OK=TRUE` và chuẩn hóa thứ tự nạp module.
  - Viết pipeline `src/models/translator/train.py` chuẩn mực với PyTorch DataLoader, AdamW optimizer, Linear warmup/decay scheduler, Gradient accumulation.
  - Đánh giá định lượng trên Test set (300 mẫu chuẩn):
    * **Baseline Model (Pre-trained):** SacreBLEU = **31.83** | ChrF++ = **56.30** | Tốc độ suy luận: **180.0 ms/câu** (~5.5 câu/giây trên CPU).
    * **Fine-tuned Model:** SacreBLEU = **31.93** (+0.10 BLEU) | ChrF++ = **52.26**.
  - Trích xuất 10 cặp câu mẫu ngẫu nhiên so sánh trực tiếp câu tiếng Việt gốc, câu tham chiếu chuẩn và câu do mô hình sinh ra.
  - Hoàn thành báo cáo phân tích lỗi chi tiết 4 nhóm nguyên nhân (Thuật ngữ chuyên ngành, Đa nghĩa ngữ cảnh, Đại từ xưng hô, Khoảng trắng dấu câu) tại `reports/error_analysis_model1.md`.
  - Lưu checkpoint tốt nhất tại `src/models/translator/checkpoint-best/` (`model.safetensors` 286.8 MB, configs, tokenizers) và `metadata.json`.

- **KẾT LUẬN GIAI ĐOẠN:**
  - 👉 **PHASE 4 (Fine-tune Model 1 Translator VI -> EN) ĐÃ HOÀN TẤT 100%!**

- **Việc tiếp theo:**
  - [Phase 5] Huấn luyện Model 3a (Example Generator) & Model 3b (Sentence Rewriter) trên kiến trúc Seq2Seq T5/BART.

## 2026-08-27 — Reliability refactor and MVP integration

- Tạo `src/features/` làm nguồn feature duy nhất cho training và inference.
- Model 2a được gom còn 5.116 từ duy nhất, bỏ POS/Google-frequency không thể tái tạo
  online và group split tuyệt đối theo `word`.
- Retrain Model 2a: Logistic Regression, Accuracy 0.3608, Macro F1 0.3665 trên từ
  chưa xuất hiện trong train.
- Rebuild/retrain Model 2b bằng shared features: Random Forest Tuned, Accuracy 0.5429,
  Macro F1 0.5260.
- Sửa Translator để baseline thật được lưu trước optimizer update; evaluation dùng
  random seed 42 và hỗ trợ full split.
- Tích hợp MVP Việt → Anh → CEFR tại `src/pipeline/run_pipeline.py`.
- Tạo 115.426 cặp Model 3a có target word; giới hạn Model 3b còn 22.811 cặp
  simplify/preserve.
- Thêm 24 unit/integration tests, Black, flake8, runtime GPU execution check và
  SHA-256 artifact manifest. Kết quả cuối: pytest 24 passed, flake8 0, Black pass.

## 2026-08-27 — Probability calibration and review policy

- Dùng temperature scaling trên validation set để bảo toàn tuyệt đối lớp dự đoán.
- Model 2a: temperature 1.159419, review threshold 0.42; accepted test coverage
  20.00%, selective accuracy 44.44%.
- Model 2b: temperature 0.887635, review threshold 0.62; accepted test coverage
  27.12%, selective accuracy 64.64%.
- Inference trả thêm `needs_review`, `confidence_status`, `review_threshold` và
  `probability_calibration`.

## 2026-08-27 — Model 3a baseline and integration

- Fine-tune `google/flan-t5-small` một epoch trên 10.000 mẫu train seed 42; chọn
  epoch 1 theo validation ROUGE-L kết hợp lexical satisfaction.
- Test 500 mẫu: lexical satisfaction 65,00%, SacreBLEU 1,43, ROUGE-L F1 0,1765,
  CEFR exact 35,80%, CEFR within-one-level 81,80%.
- Tích hợp example generator sau Model 2a cho `word_mode`; thêm retry exact-form
  và local decoder-prefix fallback, không dùng remote custom generation code.

## 2026-08-27 — Model 3b baseline and integration

- Fine-tune `google/flan-t5-small` một epoch trên 10.000 dòng simplify/preserve;
  chọn epoch 1 theo validation SARI kết hợp semantic retention.
- Test 500 task: SARI 36,68, ROUGE-L F1 0,8040, semantic TF-IDF cosine 0,9214,
  FKGL MAE 3,21, CEFR exact 19,64%, within-one 57,09%.
- Strict simplification success 47,32%, preserve success 71,34%, output changed
  58,60%; serving cảnh báo khi model copy nguyên câu.
- Tích hợp rewriter sau Model 2b cho `sentence_mode`; mặc định giảm một CEFR level,
  cho phép target rõ ràng và chặn hoàn toàn hướng `upgrade`.

## 2026-08-27 — Model 4 failure review queue

- Trích xuất 33 failure candidate từ held-out metadata: Model 3a có 16, Model 3b
  có 17; mỗi candidate có ID ổn định và automatic failure reasons.
- Thêm CLI build/list/review, giữ riêng automatic signal và human verdict.
- Hiện có 0 human-reviewed, 0 confirmed failure; chưa đủ gate 100 reviewed và
  50 confirmed failure nên chưa được train Model 4.

## 2026-08-27 — API, CI and release engineering

- Thêm FastAPI endpoints health/live, health/ready, status và process; model load lazy,
  validation/unsupported/internal errors có code và request ID.
- Tách pytest marker `integration`; CI clean-clone chạy unit/API tests, Black, flake8
  và xuất coverage artifact. Full integration suite tiếp tục chạy local với model files.
- Thêm source/model release bundles tái lập, SHA-256 verification, license gate và
  workflow tag publish source-only GitHub Release. Model weights chưa upload công khai.



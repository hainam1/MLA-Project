# 🐾 CapyVocab ML

Hệ thống Machine Learning & NLP phục vụ nền tảng học từ vựng và câu tiếng Anh thông minh **CapyVocab**.

---

## 🔀 Kiến trúc 2 Chế độ Xử lý (Dual Input Modes)

Hệ thống CapyVocab ML hỗ trợ linh hoạt 2 chế độ đầu vào thông qua bộ điều hướng `input_type_detector`:

1. **`word_mode` (Chế độ Từ / Cụm từ vựng)**:
   - **Translator (Model 1)**: Dịch nghĩa chính xác EN-VI theo ngữ cảnh.
   - **CEFR Word Classifier (Model 2a)**: Phân loại cấp độ từ vựng theo khung CEFR (A1 - C2) dựa trên đặc trưng ngôn ngữ học (Zipf frequency, âm tiết, độ dài) và mô hình phân loại.
   - **Example Generator (Model 3a)**: Tự động sinh câu ví dụ ngữ cảnh tự nhiên chứa từ mục tiêu phù hợp với cấp độ người học.
   - **Second Pair of Eyes (Model 4)**: Kiểm duyệt chất lượng ngữ pháp, độ chính xác và mức độ phù hợp của câu ví dụ sinh ra.

2. **`sentence_mode` (Chế độ Câu hoàn chỉnh)**:
   - **Translator (Model 1)**: Dịch toàn bộ câu tiếng Anh sang tiếng Việt.
   - **CEFR Sentence Classifier (Model 2b)**: Đánh giá độ khó và xếp hạng cấp độ CEFR (A1 - C2) của câu dựa trên đặc trưng cú pháp (spaCy POS/Dep parsing), độ đọc hiểu (readability scores) và Transformer.
   - **Sentence Rewriter (Model 3b)**: Viết lại / đơn giản hóa hoặc nâng cấp câu theo cấp độ CEFR mục tiêu (ví dụ: chuyển từ C1 xuống B1 hoặc ngược lại).
   - **Second Pair of Eyes (Model 4)**: Đánh giá câu viết lại đảm bảo bảo toàn ngữ nghĩa gốc và chuẩn ngữ pháp.

---

## 📌 Cấu trúc thư mục dự án

```text
capyvocab-ml/
├── data/
│   ├── raw/                 # Dữ liệu thô ban đầu (ignored by git)
│   ├── interim/             # Dữ liệu trung gian sau tiền xử lý bước 1
│   └── processed/           # Dữ liệu sạch sẵn sàng để train/eval
├── notebooks/               # Jupyter notebooks phục vụ EDA & thí nghiệm nhanh
├── src/                     # Source code chính của dự án
│   ├── data/                # Data loaders, downloaders, preprocessors, feature extractors
│   ├── models/              # Các modules mô hình NLP
│   │   ├── translator/                  # [Model 1] Dịch nghĩa song ngữ Anh - Việt
│   │   ├── cefr_word_classifier/        # [Model 2a] Phân loại CEFR cho từ vựng (A1-C2)
│   │   ├── cefr_sentence_classifier/    # [Model 2b] Phân loại CEFR cho câu (A1-C2)
│   │   ├── example_generator/           # [Model 3a] Sinh câu ví dụ cho từ
│   │   ├── sentence_rewriter/           # [Model 3b] Viết lại câu theo cấp độ CEFR
│   │   └── second_pair_of_eyes/         # [Model 4] Bộ lọc kiểm duyệt và đánh giá chất lượng
│   ├── eval/                # Bộ công cụ đánh giá metrics (BLEU, ROUGE, Accuracy, F1...)
│   └── pipeline/            # Pipeline tích hợp end-to-end (Training & Inference)
│       └── input_type_detector.py # Bộ phát hiện & điều hướng word_mode / sentence_mode
├── reports/
│   └── figures/             # Biểu đồ phân tích, visualization, đồ thị training
├── configs/
│   └── config.yaml          # File cấu hình (YAML) tập trung cho toàn bộ models & pipeline
├── logs/
│   └── progress.md          # Nhật ký tiến độ từng ngày phục vụ báo cáo/bảo vệ đề tài
├── tests/                   # Unit test & Integration test
├── requirements.txt         # Khai báo các thư viện phụ thuộc
├── README.md                # Tài liệu hướng dẫn dự án
└── .gitignore               # Cấu hình bỏ qua các file không cần commit lên Git
```

---

## 🚀 Hướng dẫn cài đặt & Môi trường

### 1. Khởi tạo môi trường ảo (Virtual Environment)
```bash
# Tạo môi trường ảo (khuyến nghị Python 3.11 hoặc 3.12)
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
source .venv/bin/activate
```

### 2. Cài đặt các thư viện phụ thuộc & Mô hình ngôn ngữ
```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Kiểm tra môi trường & Phần cứng
Chạy script kiểm tra hệ thống:
```bash
python src/_env_check.py
```
> **Môi trường huấn luyện**:
> - **Local**: Máy có GPU NVIDIA hỗ trợ CUDA có thể huấn luyện trực tiếp các mô hình Tabular, Classifier hoặc fine-tuning mô hình dịch vừa/nhỏ.
> - **Cloud GPU (Google Colab / Kaggle)**: Khuyến nghị sử dụng GPU Cloud miễn phí (T4/A100) khi huấn luyện các mô hình Transformer Seq2Seq hoặc Decoder kích thước lớn, sau đó lưu weights về thư mục `models_cache/`.

---

## 🧪 Kiểm thử (Testing)
Chạy toàn bộ unit test với lệnh:
```bash
pytest tests/
```

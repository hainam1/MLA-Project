# 🐾 CapyVocab ML

Hệ thống Machine Learning & NLP phục vụ nền tảng học từ vựng tiếng Anh thông minh **CapyVocab**.

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
│   ├── data/                # Data loaders, downloaders, preprocessors
│   ├── models/              # Các modules mô hình NLP
│   │   ├── translator/          # Dịch nghĩa từ vựng / cụm từ / câu Anh-Việt
│   │   ├── cefr_classifier/     # Phân loại độ khó từ/câu theo chuẩn CEFR (A1-C2)
│   │   ├── example_generator/   # Sinh câu ví dụ ngữ cảnh tự nhiên
│   │   └── second_pair_of_eyes/ # Bộ lọc kiểm duyệt và đánh giá chất lượng đầu ra
│   ├── eval/                # Bộ công cụ đánh giá metrics (BLEU, ROUGE, Accuracy, F1...)
│   └── pipeline/            # Pipeline tích hợp end-to-end (Training & Inference)
├── reports/
│   └── figures/             # Biểu đồ phân tích, visualization, đồ thị training
├── configs/                 # File cấu hình (YAML, JSON) cho models & training
├── logs/                    # Log files trong quá trình chạy thực nghiệm
├── tests/                   # Unit test & Integration test
├── requirements.txt         # Khai báo các thư viện phụ thuộc
├── README.md                # Tài liệu hướng dẫn dự án
└── .gitignore               # Cấu hình bỏ qua các file không cần commit lên Git
```

---

## 🚀 Hướng dẫn cài đặt môi trường

### 1. Khởi tạo môi trường ảo (Virtual Environment)
```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
source .venv/bin/activate
```

### 2. Cài đặt các thư viện phụ thuộc
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🧠 Các Module Cốt Lõi (Architecture)

1. **Translator (`src/models/translator/`)**: Dịch nghĩa song ngữ EN-VI chính xác theo ngữ cảnh.
2. **CEFR Classifier (`src/models/cefr_classifier/`)**: Đánh giá và phân loại cấp độ từ vựng/câu (A1, A2, B1, B2, C1, C2).
3. **Example Generator (`src/models/example_generator/`)**: Tự động sinh câu ví dụ ngữ cảnh thực tế phù hợp với cấp độ người học.
4. **Second Pair of Eyes (`src/models/second_pair_of_eyes/`)**: Cơ chế giám sát, phát hiện lỗi ngữ pháp/ngữ nghĩa/sai lệch trước khi trả về kết quả.

---

## 🧪 Kiểm thử (Testing)
Chạy toàn bộ unit test với lệnh:
```bash
pytest tests/
```

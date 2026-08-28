# Translation Corpus Sources & Licensing (Model 1: VI -> EN)

Tài liệu ghi lại nguồn gốc, quy mô, giấy phép (license) và đánh giá chất lượng các bộ dữ liệu song ngữ cho module Translator.

---

## 1. Primary Dataset: MTET (Multi-domain Translation for English-Vietnamese)
- **HuggingFace Hub ID**: [`phongmt184172/mtet`](https://huggingface.co/datasets/phongmt184172/mtet)
- **Nguồn gốc upstream**: Cloned từ dự án mã nguồn mở [`vietai/mTet`](https://github.com/vietai/mTet) của VietAI Research.
- **Quy mô**: ~4.200.000 cặp câu song ngữ (4.2M sentence pairs).
- **Domain**: Đa miền rộng lớn (Daily conversation, Wikipedia, Giáo dục, Tin tức, Văn học, Pháp luật, Phụ đề phim ảnh).
- **License**:
  - *Trên HuggingFace card metadata*: Trường license **chưa được khai báo cụ thể (Not specified / omitted in frontmatter)**.
  - *Tại upstream repository chính thức (`vietai/mTet`)*: **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** — Hoàn toàn cho phép nghiên cứu học thuật, giáo dục và bài tập lớn môn học (coursework) phi thương mại.
- **Đánh giá chất lượng**: Cặp câu tự nhiên, đa dạng từ vựng đời sống và chuyên ngành, rất phù hợp làm nguồn huấn luyện chính (**Primary Source**) cho bài toán dịch ngữ cảnh từ và câu của CapyVocab.

---

## 2. Supplementary Dataset: IWSLT 2015 (TED Talks English-Vietnamese)
- **HuggingFace Hub ID**: [`thainq107/iwslt2015-en-vi`](https://huggingface.co/datasets/thainq107/iwslt2015-en-vi)
- **Dataset gốc theo TASKS.md**: [`IWSLT/mt_eng_vietnamese`](https://huggingface.co/datasets/IWSLT/mt_eng_vietnamese)
- **Tác giả gốc**: Luong & Manning (Stanford Neural Machine Translation Systems, IWSLT 2015), Cettolo et al. (TED Talks).
- **Quy mô**: 133.317 cặp câu Train, 1.268 cặp Validation, 1.268 cặp Test.
- **Bản chất của repo `thainq107/iwslt2015-en-vi`**:
  - Đây là bản **Parquet conversion/mirror** được một cá nhân (`thainq107`) chuyển đổi nguyên vẹn từ tập dữ liệu IWSLT 2015 gốc của Stanford NLP lên Hugging Face Hub.
  - **Lý do sử dụng repo thay thế**: Khi gọi `load_dataset('IWSLT/mt_eng_vietnamese')`, script remote của HuggingFace cố gắng tải trực tiếp các tệp thô từ server Stanford (`https://nlp.stanford.edu/projects/nmt/data/iwslt15.en-vi/`), nhưng server này thường xuyên bị timeout / HTTP 403 khi tải tự động từ Python. Repo của `thainq107` lưu sẵn định dạng Parquet trên HF Hub nên tải nhanh và ổn định 100%.
  - **Rủi ro & Tình trạng License**: Uploader cá nhân không điền thẻ `license` trong metadata. Bản thân dữ liệu TED Talks gốc thuộc bản quyền phi thương mại (**Non-Commercial / Research Use**). Dữ liệu này chỉ được dùng trong dự án làm tập đánh giá chuẩn (**Benchmark & Evaluation Set**) phi thương mại.

---

## 📌 Đề xuất sử dụng trong Pipeline:
- **Tập Train chính**: Trích xuất tập con cân bằng ~100.000 - 200.000 cặp câu chất lượng cao từ MTET (lọc câu sạch, độ dài 3-64 từ).
- **Tập Benchmark/Eval**: Sử dụng tập test chuẩn của IWSLT 2015 (1.268 câu) để đo lường điểm SacreBLEU và ROUGE-L khách quan.

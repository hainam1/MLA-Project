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
- **HuggingFace Hub ID**: [`IWSLT/mt_eng_vietnamese`](https://huggingface.co/datasets/IWSLT/mt_eng_vietnamese) / [`thainq107/iwslt2015-en-vi`](https://huggingface.co/datasets/thainq107/iwslt2015-en-vi)
- **Tác giả**: Cettolo et al. (IWSLT Evaluation Campaign), Stanford NLP.
- **Quy mô**: ~133.317 cặp câu Train, 1.268 cặp Validation, 1.268 cặp Test.
- **Domain**: Bài thuyết trình TED Talks (Diễn thuyết, giáo dục, khoa học xã hội).
- **License**: **Non-Commercial / Research Use** (Dựa trên bản quyền TED Talks CC-BY-NC-ND cho mục đích nghiên cứu & học thuật).
- **Đánh giá chất lượng**: Bản dịch chuẩn mực theo văn phong nói tự nhiên, câu có độ dài trung bình 15-25 từ. Đề xuất sử dụng làm tập đánh giá chuẩn (**Benchmark & Evaluation Set**) và nguồn bổ sung cho văn phong thuyết trình/giao tiếp.

---

## 📌 Đề xuất sử dụng trong Pipeline:
- **Tập Train chính**: Trích xuất tập con cân bằng ~100.000 - 200.000 cặp câu chất lượng cao từ MTET (lọc câu sạch, độ dài 3-64 từ).
- **Tập Benchmark/Eval**: Sử dụng tập test chuẩn của IWSLT 2015 (tst2012, tst2013) để đo lường điểm SacreBLEU và ROUGE-L khách quan.

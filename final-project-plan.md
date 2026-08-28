# Final Project — ML Pipeline for Vietnamese→English Vocabulary Learning Support
## (CapyVocab-Linked ML Coursework Project)

---

## 1. Yêu cầu chính của môn học (tổng hợp từ đề bài + slide)

### 1.1 Bản chất môn học
- Môn học là **Machine Learning Applications** — tập trung vào input/output, feature, label, model, loss, validation, evaluation, error analysis, và responsible use.
- **KHÔNG** phải là môn học công cụ AI nói chung, không phải môn "dùng tool cho nhanh", không phải môn chấm tự động, và **không được phép dùng ML như một hình thức để "né" việc thực sự xây model** ("not a shortcut around ML models").

### 1.2 Yêu cầu bắt buộc của Final Project
| # | Yêu cầu | Diễn giải |
|---|---|---|
| 1 | **Formulate an ML task** | Phải tự phát biểu rõ bài toán: input là gì, output là gì, feature/label là gì, vì sao cần ML (không giải được bằng rule đơn giản) |
| 2 | **Apply ≥ 2 model family đã học trong khóa** | Không được chỉ dùng 1 họ thuật toán; 2 model phải thuộc 2 family khác nhau đã dạy trong môn |
| 3 | **Evaluate results** | Có metric định lượng rõ ràng cho từng model, không chỉ nhận xét cảm tính |
| 4 | **Conduct error analysis** | Phân tích cụ thể các case sai, lý giải nguyên nhân — không được bỏ qua |
| 5 | **Defend orally** | Bảo vệ miệng — cần hiểu sâu, giải thích được từng quyết định kỹ thuật |

### 1.3 Cơ cấu điểm
| Thành phần | Trọng số |
|---|---|
| Active participation | 10% |
| Midterm/Internal | 30% |
| **Final Exam (Final project + Oral exam)** | **60%** |

### 1.4 Đề tài được chấp nhận
> "Build an ML pipeline for a **translation**, **multilingual NLP**, or **language-learning support** task. Then explain and defend it orally."

→ Dự án hiện tại của Nam (Việt→Anh translation + CEFR classification + language-learning support) **nằm đúng tâm đề bài**.

### 1.5 Quy định về sử dụng LLM — QUAN TRỌNG NHẤT, DỄ VI PHẠM NHẤT
> "LLMs may be used only as **disclosed support tools**. LLM-only work, including zero-shot prompting, does **not** satisfy the ML requirements of the course."

Diễn giải cụ thể:
- ✅ **Được phép**: dùng LLM để **tạo/tăng cường dữ liệu train** (silver data generation), miễn công khai rõ ràng trong báo cáo (prompt dùng, số lượng, cách lọc/kiểm duyệt).
- ❌ **Không được phép**: lúc **inference/demo/chạy thực tế**, gọi thẳng LLM (GPT/Gemini) để sinh output thay vì dùng model đã tự train/fine-tune. Đây được tính là "LLM-only work" — **KHÔNG đạt yêu cầu môn học** dù có làm phần training riêng trước đó.
- Nguyên tắc an toàn: mọi model chạy trong pipeline final (lúc demo/bảo vệ) phải là **model do Nam tự train hoặc fine-tune**, có source code training, có log quá trình train, có thể trình bày được cơ chế hoạt động.

### 1.6 Gợi ý mở rộng (optional, cho nhóm mạnh): "Second Pair of Eyes"
- Một **model phụ nhẹ**, dùng feature đơn giản (độ dài, độ trùng lặp, tag, rubric field...) để dự đoán xem output của model chính có **cần người duyệt lại hay không** (needs review / acceptable), hoặc tín hiệu độ khó / độ ưu tiên.
- Nguyên tắc bắt buộc đi kèm — **Human-in-the-loop rule**:
  > "A prediction is a review flag, not a final judgement. The teacher, translator, or reviewer makes the decision."
- Đây là điểm cộng tự nhiên nếu còn thời gian, vì thầy đã gợi ý sẵn trong slide và khớp hoàn hảo với tinh thần "error analysis + responsible use" của môn.

### 1.7 Nguồn dữ liệu HuggingFace đã chốt & nguyên tắc sử dụng

| Model | Dataset gợi ý | Ghi chú license |
|---|---|---|
| 1. Translator (VI→EN) | `IWSLT/mt_eng_vietnamese` (IWSLT'15, ~130k cặp câu), hoặc `phongmt184172/mtet` (MTet, lớn hơn, 1M–10M cặp) | Tự kiểm tra license ghi trên dataset card trước khi dùng |
| 1. Translator (bổ sung, domain rộng) | PhoMT (VinAI, 3.02M cặp câu, chất lượng cao) — GitHub `VinAIResearch/PhoMT`, kiểm tra xem có mirror trên HuggingFace không | Academic use, cần trích dẫn paper |
| 2a. CEFR Word Classifier | *Classification of word levels with usage frequency, expert opinions and ML* (Zenodo, Istanbul Sehir University) — có label CEFR + frequency + POS sẵn | Open dataset, phù hợp academic |
| 2b. CEFR Sentence Classifier | `UniversalCEFR` (tổ chức UniversalCEFR trên HuggingFace) — 505,807 văn bản gán CEFR ở nhiều mức granularity (có cả sentence-level), 13 ngôn ngữ trong đó có tiếng Anh | Mỗi sub-dataset có license riêng (cc-by-nc, mit...) — cần liệt kê license từng phần trước khi dùng |
| 3b. Sentence Rewriter | `facebook/asset` (ASSET — simplification, 10 bản rewrite/câu) | CC-BY-NC-4.0 — ổn cho coursework/academic, không dùng thương mại |
| 3b. Sentence Rewriter (bổ sung) | WikiLarge/WikiSmall (mirror trên HuggingFace, dạng `wiki_auto`) | Research use |

**Không dùng**: Newsela — dataset simplification chất lượng cao nhất nhưng yêu cầu xin phép truy cập riêng, không tải trực tiếp qua `datasets` được, tốn thời gian ngoài phạm vi 8 tuần → bỏ qua, dùng ASSET/WikiLarge thay thế.

**Nguyên tắc sử dụng**: các dataset trên dùng được, miễn **ghi rõ nguồn/license trong báo cáo** (mục 7 và `reports/00_dataset_licenses.md`); vẫn phải **tự fine-tune model trên dữ liệu này** — không phải chỉ tải về dùng thẳng. Trước khi dùng, phải tự đọc dataset card mới nhất để xác nhận license hiện tại (bảng trên chỉ là tóm tắt tham khảo).

---

## 2. Bài toán ML được Nam phát biểu (Task Formulation) — bản mở rộng

> **Bài toán**: Cho một **từ hoặc một câu** tiếng Việt do người dùng nhập (hoặc lấy từ CapyVocabApp), hệ thống sẽ:
> 1. Dịch sang tiếng Anh.
> 2. Xác định input thuộc loại **từ** hay **câu** (word mode / sentence mode).
> 3. Ước lượng **cấp độ CEFR (A1–C1)** của từ/câu tiếng Anh đó — dùng model phù hợp theo loại input (word-level hoặc sentence-level).
> 4. Sinh ra **các phiên bản / gợi ý ở những cấp độ khác** để người học luyện tập:
>    - Nếu input là **từ** → sinh câu ví dụ ở nhiều level khác nhau cho từ đó (ví dụ: câu A2, câu B1, câu C1 đều dùng từ này).
>    - Nếu input là **câu** → viết lại câu đó ở các level khác (giữ nguyên nghĩa, đơn giản hóa hoặc nâng cao độ khó), và/hoặc gợi ý các từ vựng đáng chú ý trong câu kèm level của chúng.
> 5. (Tùy chọn) Gắn cờ các output có độ tin cậy thấp cần người dùng/giáo viên xem lại.

Bài toán này **không thể giải bằng rule-based đơn giản** vì:
- Việc dịch từ đa nghĩa/theo ngữ cảnh cần khả năng tổng quát hóa từ dữ liệu, không có bảng tra cứu 1-1 hoàn hảo.
- Việc phân loại độ khó từ vựng phụ thuộc nhiều đặc trưng đồng thời (tần suất, độ dài, hình thái học...) — không thể liệt kê hết bằng if/else.
- **Việc đánh giá độ khó của cả một câu** còn phức tạp hơn: phụ thuộc đồng thời vào độ khó từng từ trong câu, độ dài câu, mật độ mệnh đề phụ, cấu trúc ngữ pháp — là một hàm tổng hợp phi tuyến của nhiều yếu tố, không thể quy về rule cố định.
- Việc sinh câu ví dụ hoặc viết lại câu ở đúng cấp độ mục tiêu, tự nhiên, đúng ngữ pháp, giữ đúng nghĩa gốc (với sentence rewriting) đòi hỏi mô hình ngôn ngữ có khả năng generalize và điều kiện hóa theo level.

---

## 3. Kiến trúc Pipeline tổng thể (có nhánh word / sentence)

```
Input: từ HOẶC câu tiếng Việt (người dùng nhập, hoặc lấy từ list từ vựng/
       câu CapyVocabApp đã detect từ ảnh)
        │
        ▼
┌─────────────────────────────────────────────┐
│ MODEL 1 — Translator (Việt → Anh)            │
│ Family: Neural Sequence-to-Sequence          │
│ (MarianMT fine-tuned, opus-mt-vi-en)         │
│ Xử lý được cả input là từ và câu             │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ INPUT TYPE DETECTOR (rule-based, KHÔNG phải  │
│ model ML — dựa trên số token / dấu câu / POS)│
│ → word_mode  hoặc  sentence_mode             │
└─────────────────────────────────────────────┘
        │
   ┌────┴─────────────────────┐
   ▼ word_mode                 ▼ sentence_mode
┌───────────────────────┐   ┌───────────────────────────────────┐
│ MODEL 2a — CEFR Word   │   │ MODEL 2b — CEFR Sentence           │
│ Level Classifier       │   │ Level Classifier                    │
│ Family: Classical ML   │   │ Family: Classical ML                │
│ (RF/XGBoost trên       │   │ (RF/XGBoost trên feature tổng hợp:  │
│  feature từ vựng)      │   │  avg word-CEFR, độ dài câu, độ phức │
│                        │   │  tạp cú pháp, readability score)    │
└───────────────────────┘   └───────────────────────────────────┘
        │                              │
        ▼                              ▼
┌───────────────────────┐   ┌───────────────────────────────────┐
│ MODEL 3a — Multi-level │   │ MODEL 3b — Multi-level Sentence     │
│ Example Generator      │   │ Rewriter                             │
│ Family: Neural seq2seq │   │ Family: Neural seq2seq               │
│ (T5-small/BART, sinh   │   │ (T5-small/BART, viết lại câu ở level│
│  câu ví dụ ở NHIỀU     │   │  khác — dễ hơn/khó hơn — giữ nghĩa, │
│  level khác nhau cho   │   │  + gợi ý từ vựng đáng chú ý kèm     │
│  cùng 1 từ)            │   │  level của từng từ)                  │
└───────────────────────┘   └───────────────────────────────────┘
        │                              │
        └──────────────┬───────────────┘
                        ▼
        ┌───────────────────────────────────────┐
        │ MODEL 4 (OPTIONAL) — "Second Pair of   │
        │ Eyes" — needs_review / acceptable       │
        │ Family: Classical ML (lightweight)      │
        └───────────────────────────────────────┘
                        ▼
Output: (từ/câu tiếng Anh) + CEFR level + các phiên bản/gợi ý ở level khác
        (+ cờ cảnh báo nếu cần người duyệt)
```

→ Với kiến trúc này, dự án vẫn dùng **2 model family rõ ràng và khác biệt** (Neural seq2seq: Model 1, 3a, 3b — vs. Classical ML: Model 2a, 2b, 4), đáp ứng đúng yêu cầu tối thiểu của môn, đồng thời có **6 thành phần model** (thay vì 4) — nội dung phong phú hơn cho phần error analysis và bảo vệ miệng.

> ⚠️ **Lưu ý về phạm vi**: việc mở rộng thêm sentence-level classifier (2b) và sentence rewriter (3b) làm tăng đáng kể khối lượng công việc so với bản gốc (đặc biệt là 3b — text simplification/complexification là bài toán khó, cần dữ liệu leveled-sentence pairs). Nếu tới giữa lộ trình thấy thiếu thời gian, có thể ưu tiên hoàn thiện **word_mode** (Model 2a + 3a) cho thật chắc trước, rồi làm **sentence_mode** (2b + 3b) như phần mở rộng — tương tự cách Model 4 đã là optional.

---

## 4. Quy trình thực hiện chi tiết theo tuần

### Tuần 1 — Formulate task + chuẩn bị dữ liệu khung
- [ ] Viết văn bản formulate task hoàn chỉnh (mục 2) bằng tiếng Anh, nộp/trình bày với thầy nếu cần duyệt đề tài trước.
- [ ] Xác định rõ input/output/feature/label cho **từng model** riêng biệt, bao gồm cả 2a/2b và 3a/3b (bảng chi tiết ở mục 5).
- [ ] Thiết kế rule cho **Input Type Detector** (word vs sentence): ví dụ số token ≤ 2-3 và không có dấu câu kết thúc → word_mode; ngược lại → sentence_mode. Ghi rõ case biên (cụm từ 2-3 từ) sẽ xử lý thế nào.
- [ ] Thu thập nguồn dữ liệu (danh sách dataset đã chốt — xem bảng chi tiết ở mục 1.7, mỗi dataset đều cần kiểm tra license trên dataset card trước khi tải):
  - Cặp câu Việt–Anh (Model 1): `IWSLT/mt_eng_vietnamese` (chính), `phongmt184172/mtet` (bổ sung, tập lớn hơn), PhoMT (bổ sung domain rộng, cần trích dẫn paper).
  - Wordlist CEFR (Model 2a): dataset *"Classification of word levels with usage frequency, expert opinions and ML"* trên Zenodo (Istanbul Sehir University) — đã có sẵn CEFR level + frequency + POS.
  - Câu ví dụ có gán độ khó (Model 3a): lọc từ phía tiếng Anh của các cặp dịch (IWSLT/MTet) theo readability, bổ sung bằng LLM (silver data — có disclose).
  - **Dữ liệu câu đã gán CEFR level** (cho Model 2b): `UniversalCEFR` trên HuggingFace (505,807 văn bản, nhiều granularity, 13 ngôn ngữ) — lọc subset tiếng Anh + sentence-level; mỗi sub-dataset con có license riêng nên phải liệt kê rõ từng phần đã dùng. Nếu không đủ, dùng readability formula (Flesch-Kincaid) làm proxy label bổ sung — ghi rõ giới hạn của proxy này trong báo cáo.
  - **Dữ liệu cặp câu cùng nghĩa khác level** (cho Model 3b — sentence rewriting/simplification): `facebook/asset` (ASSET, CC-BY-NC-4.0, không thương mại) làm nguồn chính, WikiLarge/WikiSmall (dạng `wiki_auto` trên HuggingFace) làm nguồn bổ sung, kết hợp silver data từ LLM (có disclose) để tạo thêm cặp (câu gốc, câu ở level khác) cho từ vựng/chủ đề đời sống mà CapyVocabApp cần. **Không dùng Newsela** (yêu cầu xin quyền truy cập riêng, tốn thời gian ngoài phạm vi 8 tuần).
- [ ] Setup môi trường: Google Colab / Kaggle Notebook (GPU free), cài `transformers`, `datasets`, `scikit-learn`, `xgboost`, `wordfreq`, `textstat`, `sacrebleu`, `spacy` (để trích đặc trưng cú pháp cho Model 2b).

### Tuần 2 — Làm sạch & xử lý dữ liệu
- [ ] Làm sạch dữ liệu song ngữ (loại câu quá ngắn/quá dài, loại trùng lặp).
- [ ] Làm sạch wordlist CEFR (chuẩn hóa chữ thường, loại từ nhãn không rõ ràng).
- [ ] Trích xuất feature cho Model 2a (word-level): word frequency (`wordfreq`), độ dài từ, số âm tiết (`pyphen`), embedding (GloVe/BERT).
- [ ] Trích xuất feature cho Model 2b (sentence-level): độ dài câu (số từ), avg word-CEFR/avg word frequency của các từ trong câu, độ phức tạp cú pháp (độ sâu dependency parse hoặc số mệnh đề phụ — dùng `spacy`), readability score (`textstat`), tỉ lệ từ hiếm trong câu.
- [ ] Gán nhãn readability cho câu ví dụ (`textstat`, Flesch-Kincaid) làm proxy hỗ trợ CEFR level (dùng chung cho cả Model 2b và Model 3).
- [ ] Chuẩn bị dữ liệu dạng cặp (câu gốc, câu level khác) cho Model 3b — làm sạch, loại cặp không giữ nghĩa (kiểm tra sơ bộ bằng similarity score).
- [ ] Chia train/validation/test (70/15/15) cho **từng** model (2a, 2b, 3a, 3b...) — đảm bảo không rò rỉ dữ liệu giữa các tập.

### Tuần 3 — Xây & train Model 2a + 2b (CEFR Classifiers) — làm trước vì an toàn nhất
- [ ] Train baseline: Logistic Regression (đo nhanh, để so sánh) cho cả 2a và 2b.
- [ ] Train model chính: Random Forest / XGBoost cho Model 2a (feature từ vựng) và Model 2b (feature câu).
- [ ] Xử lý mất cân bằng lớp (class weighting hoặc oversampling cho C1/C2) — áp dụng riêng cho từng model.
- [ ] Đánh giá: accuracy, macro-F1, confusion matrix — riêng cho 2a và 2b.
- [ ] Error analysis sơ bộ: liệt kê các cặp level hay bị nhầm lẫn (thường B1↔B2) — riêng cho word-level và sentence-level, so sánh xem loại nào khó phân loại hơn và vì sao.

### Tuần 4 — Xây & train Model 1 (Translator)
- [ ] Tải `Helsinki-NLP/opus-mt-vi-en` làm base model.
- [ ] Fine-tune trên tập dữ liệu Việt–Anh domain hẹp (từ vựng đời sống, đúng loại từ CapyVocabApp cần), đảm bảo dataset có cả câu ngắn (từ/cụm từ) và câu dài để model xử lý tốt cả 2 mode.
- [ ] Đánh giá: BLEU, chrF (dùng `sacrebleu`) — tách riêng đánh giá trên tập chỉ-từ và tập câu để xem chất lượng dịch có khác nhau không.
- [ ] Error analysis: liệt kê case dịch sai điển hình, phân loại nguyên nhân (từ đa nghĩa, thiếu ngữ cảnh, dữ liệu train ít).

### Tuần 5 — Xây & train Model 3a (Example Generator) và Model 3b (Sentence Rewriter)
- [ ] Model 3a: chuẩn hóa dữ liệu dạng `input: "generate: word=<W> level=<L>"` → `target: "<câu ví dụ>"`, fine-tune T5-small/BART-base, có thể sinh nhiều level cùng lúc bằng cách gọi lại model với nhiều `<L>` khác nhau cho cùng 1 từ.
- [ ] Model 3b: chuẩn hóa dữ liệu dạng `input: "rewrite: sentence=<S> target_level=<L>"` → `target: "<câu đã viết lại ở level L>"`, fine-tune riêng (hoặc multi-task cùng checkpoint với 3a nếu muốn tiết kiệm — ghi rõ lựa chọn và lý do).
- [ ] Áp dụng constrained decoding (`force_words_ids`) cho Model 3a để đảm bảo từ mục tiêu xuất hiện đúng dạng trong câu sinh ra.
- [ ] Đánh giá Model 3a: lexical constraint satisfaction rate, readability score theo level, BLEU/ROUGE nếu có câu tham chiếu.
- [ ] Đánh giá Model 3b: (1) mức độ giữ nghĩa so với câu gốc (semantic similarity, ví dụ cosine similarity embedding), (2) readability score có đúng lệch về target level không, (3) BLEU/ROUGE nếu có câu tham chiếu.
- [ ] Error analysis: câu không chứa đúng từ (3a), câu lệch level, câu lặp/nhàm chán, câu rewrite bị lệch nghĩa so với gốc (3b).

### Tuần 6 — (Nếu còn thời gian) Model 4 — Second Pair of Eyes
- [ ] Tự gán nhãn "needs_review / acceptable" cho một tập nhỏ (50–100 mẫu) output của Model 1, 3a và/hoặc 3b.
- [ ] Trích feature đơn giản: độ dài, độ trùng lặp với input, BLEU/readability thấp bất thường, có chứa từ hiếm không, (với 3b) độ lệch semantic similarity bất thường.
- [ ] Train classifier nhẹ (Logistic Regression / Decision Tree).
- [ ] Đánh giá đặc biệt chú trọng **Recall** (không được bỏ sót case cần duyệt).
- [ ] Viết rõ nguyên tắc human-in-the-loop trong báo cáo: model chỉ gắn cờ, không tự quyết định.

### Tuần 7 — Ghép pipeline end-to-end (có nhánh word/sentence) + phân tích lỗi cộng dồn
- [ ] Viết script/notebook demo hoàn chỉnh: input tiếng Việt (từ hoặc câu) → Model 1 → Input Type Detector → nhánh (2a→3a) hoặc (2b→3b) → (4) → output cuối.
- [ ] Đánh giá **end-to-end** riêng cho từng nhánh (word_mode và sentence_mode): so sánh chất lượng khi chạy pipeline đầy đủ với khi đánh giá từng model độc lập, để đo mức độ lỗi lan truyền (error propagation) giữa các tầng.
- [ ] Ghi nhận cụ thể: lỗi ở Model 1 ảnh hưởng thế nào đến Model 2a/2b và Model 3a/3b (ví dụ: dịch sai từ → chọn nhầm level → sinh/viết lại câu sai ngữ cảnh).
- [ ] Kiểm tra riêng độ chính xác của Input Type Detector trên các case biên (cụm từ ngắn, câu không dấu chấm...).

### Tuần 8 — Viết báo cáo + chuẩn bị bảo vệ miệng
- [ ] Viết báo cáo đầy đủ theo cấu trúc ở mục 6.
- [ ] Viết riêng mục "Responsible Use & LLM Disclosure" (mục 7) — không được bỏ qua, có nhắc rõ phần LLM dùng cho cả silver data Model 3a lẫn Model 3b.
- [ ] Chuẩn bị trả lời các câu hỏi bảo vệ dự kiến (mục 8).
- [ ] Thử chạy demo trực tiếp nhiều lần, test cả input là từ và input là câu, đảm bảo không lỗi khi trình bày.

---

## 5. Bảng chi tiết Input/Output/Feature/Label cho từng model

| Model | Input | Output | Feature | Label (nguồn) |
|---|---|---|---|---|
| **1. Translator** | Từ/cụm/câu tiếng Việt | Từ/cụm/câu tiếng Anh | Token embedding (nội bộ trong kiến trúc seq2seq) | Câu Anh tham chiếu (`IWSLT/mt_eng_vietnamese`, `phongmt184172/mtet`, PhoMT) |
| **2a. CEFR Word Classifier** | Từ tiếng Anh | Nhãn A1/A2/B1/B2/C1(/C2) | Word frequency, độ dài, số âm tiết, embedding, morphology | CEFR level (dataset Zenodo — Istanbul Sehir University, kèm frequency + POS) |
| **2b. CEFR Sentence Classifier** | Câu tiếng Anh | Nhãn A1/A2/B1/B2/C1(/C2) | Độ dài câu, avg word-CEFR/frequency, độ phức tạp cú pháp, readability score | CEFR level câu (`UniversalCEFR` — subset tiếng Anh/sentence-level, hoặc proxy readability nếu thiếu) |
| **3a. Multi-level Example Generator** | (Từ tiếng Anh, CEFR level đích) | Câu ví dụ tiếng Anh ở level đích | Token embedding + level token điều kiện | Câu ví dụ tham chiếu (lọc từ `IWSLT/mt_eng_vietnamese`/`mtet` + silver data) |
| **3b. Multi-level Sentence Rewriter** | (Câu tiếng Anh, CEFR level đích) | Câu viết lại ở level đích, giữ nghĩa | Token embedding + level token điều kiện | Cặp (câu gốc, câu level khác) — `facebook/asset` + WikiLarge/WikiSmall (`wiki_auto`) + silver data |
| **4. Second Pair of Eyes** (optional) | Output Model 1/3a/3b + input gốc | needs_review / acceptable | Độ dài, độ trùng lặp, readability, BLEU/semantic-similarity nội bộ | Gán nhãn thủ công trên tập nhỏ |

---

## 6. Cấu trúc báo cáo đề xuất

1. **Introduction & Motivation** — bối cảnh, liên hệ tới CapyVocabApp (ứng dụng thực tế).
2. **Task Formulation** — bài toán ML, input/output/feature/label rõ ràng, bao gồm nhánh word/sentence.
3. **Data** — nguồn dữ liệu, quy trình làm sạch, thống kê mô tả (số lượng mẫu, phân bố nhãn) cho cả 2 loại dữ liệu (word-level và sentence-level).
4. **Methodology** — mô tả từng model (bao gồm 2a/2b, 3a/3b), lý do chọn model family, kiến trúc, hyperparameter, loss function, quy trình train/validate.
5. **Results** — bảng số liệu đánh giá cho từng model + toàn pipeline, tách riêng theo nhánh word/sentence.
6. **Error Analysis** — case study cụ thể, phân loại nguyên nhân lỗi, phân tích lỗi lan truyền qua pipeline, so sánh độ khó giữa word-level và sentence-level.
7. **Responsible Use & LLM Disclosure** — minh bạch việc dùng LLM ở đâu, dùng để làm gì, khẳng định inference không gọi LLM trực tiếp.
8. **Limitations & Future Work** — hạn chế hiện tại, hướng cải thiện (ví dụ: mở rộng cấp độ C2, tăng dữ liệu, cải thiện constrained decoding, cải thiện sentence rewriter).
9. **Conclusion**.

---

## 7. Mục Responsible Use & LLM Disclosure (bắt buộc, viết mẫu tham khảo)

> *"Large Language Models (Gemini) were used exclusively during the data preparation phase to augment training data for the Example Generator (3a) and Sentence Rewriter (3b) models, generating candidate example sentences and leveled sentence pairs for underrepresented (word/sentence, CEFR level) combinations. All LLM-generated content was filtered using automatic readability scoring (Flesch-Kincaid) and semantic similarity checks, and manually reviewed for factual/grammatical correctness before being included in the fine-tuning dataset. All pretrained datasets used (IWSLT/mt_eng_vietnamese, MTet, PhoMT, the Zenodo CEFR word-level dataset, UniversalCEFR, ASSET, and WikiLarge/WikiSmall) were sourced under their respective licenses, which are disclosed in full in `reports/00_dataset_licenses.md`; each dataset was used only to fine-tune the author's own models, never as a drop-in inference component. At inference time, the deployed pipeline does not call any external LLM API — all outputs (translation, CEFR classification for both words and sentences, example generation, sentence rewriting) are produced exclusively by models trained/fine-tuned by the author as part of this project."*

---

## 8. Câu hỏi bảo vệ miệng dự kiến — chuẩn bị sẵn câu trả lời

- Vì sao chọn model family X cho tầng này mà không phải family khác?
- Nếu Model 1 (Translator) dự đoán sai, điều đó ảnh hưởng thế nào đến Model 2 và Model 3?
- Làm sao đo được mức độ lỗi lan truyền (error propagation) qua toàn pipeline?
- Vì sao chọn feature cụ thể đó cho Model 2a (CEFR Word Classifier)? Feature nào quan trọng nhất (feature importance)?
- **Feature cho Model 2b (sentence-level) khác gì so với 2a? Vì sao đánh giá độ khó câu lại khó hơn đánh giá độ khó từ?**
- **Input Type Detector hoạt động theo nguyên tắc nào? Có case biên nào (cụm từ ngắn, câu không dấu câu) gây nhầm lẫn không, xử lý ra sao?**
- **Model 3b (Sentence Rewriter) đảm bảo giữ đúng nghĩa gốc bằng cách nào? Đo lường "giữ nghĩa" bằng metric gì?**
- Model 4 (nếu có) đảm bảo không bỏ sót case cần duyệt bằng cách nào? Vì sao ưu tiên Recall hơn Precision ở đây?
- Dữ liệu train có bị thiên lệch (bias) theo hướng nào không? (VD: wordlist CEFR có thể thiên về từ vựng học thuật, ít từ vựng đời sống)
- Ranh giới giữa việc dùng LLM để tạo dữ liệu và "LLM-only work" nằm ở đâu, và làm sao đảm bảo dự án không vi phạm quy định này?
- Các dataset có sẵn (UniversalCEFR, ASSET, PhoMT, MTet...) có license gì, vì sao vẫn được phép dùng trong project dù không tự thu thập, và giới hạn sử dụng (ví dụ CC-BY-NC) ảnh hưởng gì đến phạm vi dự án?

---

## 9. Checklist cuối cùng trước khi nộp

- [ ] Đã có ≥ 2 model thuộc 2 family khác nhau đã học trong khóa (xác nhận lại đúng family theo syllabus của thầy).
- [ ] Có đầy đủ metric đánh giá định lượng cho từng model, bao gồm cả 2a/2b và 3a/3b.
- [ ] Có phần error analysis cụ thể, không chung chung — có so sánh word-level vs sentence-level.
- [ ] Có mục Responsible Use & LLM Disclosure minh bạch, bao gồm license của từng dataset có sẵn đã dùng (`reports/00_dataset_licenses.md` đầy đủ).
- [ ] Lúc demo/inference **không gọi LLM trực tiếp** — chỉ dùng model tự train.
- [ ] Đã test pipeline với cả input là từ và input là câu, không lỗi.
- [ ] Đã luyện tập trả lời các câu hỏi bảo vệ miệng dự kiến.
- [ ] Code, notebook, log training được lưu trữ đầy đủ, có thể trình bày khi thầy hỏi.

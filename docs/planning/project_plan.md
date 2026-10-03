# Dự đoán Điểm Đánh giá Bài viết Tiếng Anh của Người học: So sánh các Đặc trưng Ngôn ngữ Dễ giải thích và Mô hình Pretrained Transformer
## (Predicting Human-Rated English Learner Writing Scores: Interpretable Linguistic Features versus a Pretrained Transformer)

> **ARCHIVED — KHÔNG PHẢI PHẠM VI HIỆN HÀNH (2026-09-23).** Tài liệu này lưu
> phương án cũ gồm 6 target, DeBERTa, Decision Tree và MCRMSE. Không dùng các quyết
> định trong tài liệu này để triển khai hoặc nghiệm thu. Phạm vi có hiệu lực nằm
> trong `docs/phase1_problem_definition.md`, `docs/project_scope.md` và
> `configs/experiment.yaml`.

## Kế hoạch Dự án Hoàn chỉnh (Final Project Plan)

> **Lĩnh vực:** Hỗ trợ học ngôn ngữ / Xử lý ngôn ngữ tự nhiên (NLP)  
> **Nhiệm vụ cốt lõi:** Hồi quy đa đầu ra có giám sát (Supervised Multi-output Regression)  
> **Đầu vào (Input):** Toàn bộ bài luận tiếng Anh của người học (`full_text`)  
> **Đầu ra (Output):** Vector 6 điểm đánh giá năng lực viết do con người chấm  
> **Đóng góp chính:** So sánh công bằng giữa các mô hình hồi quy dựa trên đặc trưng ngôn ngữ có thể giải thích được và mô hình Pretrained Transformer (DeBERTa-v3-small), kèm phân tích đóng góp nhóm đặc trưng, phân tích lối tắt độ dài (shortcut analysis), khả năng tổng quát hóa và phân tích lỗi chi tiết.

---

## Bảng Tóm tắt Cấu hình Chốt của Dự án (Executive Summary)

| Thành phần | Lựa chọn chốt | Chi tiết kỹ thuật |
|---|---|---|
| **Tên đề tài** | Dự đoán Điểm Bài viết Tiếng Anh: Đặc trưng Ngôn ngữ vs. Pretrained Transformer | So sánh trực diện mô hình dễ giải thích (Interpretable) và Transformer |
| **Dataset** | ELLIPSE / Feedback Prize – English Language Learning | Nguồn chính thức Kaggle, bản xem nhanh Hugging Face mirror |
| **Quy mô dữ liệu** | Khoảng 3.911 bài viết của người học tiếng Anh | Đầy đủ metadata bài viết và 6 cột nhãn do chuyên gia chấm |
| **Dữ liệu đầu vào** | `text_id`, `full_text` | Toàn văn bài luận tiếng Anh nguyên bản |
| **6 Target dự đoán** | `cohesion`, `syntax`, `vocabulary`, `phraseology`, `grammar`, `conventions` | Thang điểm 1.0 – 5.0, bước nhảy 0.5 (Dự đoán đồng thời 6 đầu ra) |
| **Cột loại bỏ chống rò rỉ**| `mss`, `response_fluency`, `non_fluency_reason` | `non_fluency_reason` chứa nhận xét trực tiếp chất lượng bài viết |
| **Pretrained Model** | `microsoft/deberta-v3-small` (Hugging Face) | 6 transformer layers, hidden size 768, 44M backbone params, MIT License |
| **Kiến trúc Transformer Head**| DeBERTa Backbone (768) $\to$ Dropout $\to$ Linear Layer $\to$ 6 scores | Thay thế head phân loại mặc định bằng regression head 6 chiều |
| **Chuẩn hóa Target** | $y_{\text{normalized}} = (y - 1.0) / 4.0$ (về khoảng $[0, 1]$) | Khôi phục $y = y_{\text{norm}} \times 4.0 + 1.0$, cắt biên `clip(1.0, 5.0)` |
| **Xử lý bài luận dài** | Truncation (nếu $\le 512$) hoặc Sliding Window Chunking (512/128) | Mean pooling các chunk trước khi đưa qua regression head |
| **Hàm Loss** | MSE Loss (hoặc Smooth L1 Loss) | Tối ưu hóa sai số khoảng cách liên tục trên 6 tiêu chí |
| **Metric chính** | **MCRMSE** (Mean Columnwise Root Mean Squared Error) | Đo lường độ lệch căn bậc hai trung bình trên từng cột target |
| **Metric bổ sung** | MAE từng tiêu chí, Mean MAE, RMSE từng tiêu chí, $R^2$ từng tiêu chí | Phân tích chi tiết từng khía cạnh ngữ pháp, từ vựng, tính liên kết |
| **Phân chia dữ liệu** | 70% Train / 15% Validation / 15% Test (seed: 42) | Stratified xấp xỉ theo phân vị điểm trung bình (`mean_score` 10 bins) |
| **Các mô hình so sánh** | Baseline (Mean), Ridge Regression, Decision Tree, DeBERTa-v3-small | (KNN Regression là tùy chọn bổ sung nếu thời gian cho phép) |
| **Thiết kế thực nghiệm** | E0 (Baseline), E1–E3 (Ridge theo nhóm đặc trưng), E4 (Cây), E5 (DeBERTa) | E6 tùy chọn: Mô hình lai (DeBERTa representation + Linguistic features) |

---

## 1. Tóm tắt Dự án (Project Summary)

Dự án nghiên cứu khả năng dự đoán điểm đánh giá bài viết tiếng Anh của người học ngôn ngữ (English Language Learners) do con người chấm điểm, thông qua việc so sánh đối đầu giữa:
1. **Các mô hình máy học truyền thống dễ giải thích (Interpretable Machine Learning):** Trích xuất từ 24 đến 30 đặc trưng ngôn ngữ định lượng (hình thức/độ dài, độ phong phú từ vựng, độ phức tạp cú pháp, chỉ số độ dễ đọc) và huấn luyện trên các mô hình hồi quy (Ridge Regression, Decision Tree Regression, và KNN Regression).
2. **Mô hình Pretrained Transformer hiện đại:** Tận dụng biểu diễn ngữ cảnh sâu từ mô hình `microsoft/deberta-v3-small`, gắn regression head 6 đầu ra và fine-tune trực tiếp trên tập dữ liệu bài luận nguyên bản.

Dự án **không tuyên bố** đo lường toàn diện năng lực tiếng Anh tổng quát của một người học. Mục tiêu cụ thể là **dự đoán điểm số được con người gán cho một bài viết cụ thể theo một khung tiêu chuẩn (rubric) chấm điểm xác định**. Sự phân biệt này mang tính then chốt vì điểm bài viết còn phản ánh độ khó của đề bài, mức độ hoàn thành yêu cầu, sự nhất quán của người chấm và điều kiện phòng thi.

### Các nguyên tắc ưu tiên hàng đầu của dự án:
- Mục tiêu dự đoán rõ ràng, có căn cứ và được ghi chép minh bạch.
- Chiến lược phân chia dữ liệu nghiêm ngặt, triệt tiêu nguy cơ rò rỉ thông tin (leakage-safe split).
- Trích xuất đặc trưng ngôn ngữ tường minh, không sử dụng "hộp đen" cho nhánh classical model.
- So sánh khách quan, công bằng trên cùng một phân vùng dữ liệu và điều kiện đánh giá.
- Phân tích cẩn trọng xem các mô hình có dựa dẫm vào độ dài bài luận như một "lối tắt" (shortcut learning) hay không.
- Chú trọng phân tích lỗi định tính và định lượng thay vì chỉ báo cáo một con số đo lường đơn thuần.

### Định nghĩa dự án trong một câu (One-sentence project definition)
> Cho một bài luận tiếng Anh của người học, dự đoán đồng thời 6 tiêu chí điểm do con người chấm bằng cách so sánh các đặc trưng ngôn ngữ dễ giải thích với mô hình Pretrained Transformer DeBERTa, từ đó phân tích mô hình và nhóm đặc trưng nào mang lại độ tin cậy cao nhất.

---

## 2. Phạm vi Dự án (Project Scope)

### 2.1 Các nội dung NẰM TRONG phạm vi (Included)
- Dữ liệu văn bản tiếng Anh do người học viết từ bộ dữ liệu chính thức ELLIPSE / Feedback Prize ELL.
- Điểm đánh giá gồm 6 tiêu chí định lượng do giám khảo con người chấm trên thang 1.0–5.0 bước điểm 0.5.
- Trích xuất tất định 24–30 đặc trưng ngôn ngữ dễ giải thích thuộc 4 nhóm: Bề mặt, Từ vựng, Cú pháp, Độ dễ đọc.
- Nhiệm vụ hồi quy đa biến có giám sát (Supervised Multi-output Regression).
- Huấn luyện và tinh chỉnh 4 họ mô hình: Baseline trung bình, Ridge Regression, Decision Tree Regression, và Pretrained Transformer (`microsoft/deberta-v3-small`).
- Lựa chọn mô hình và tối ưu siêu tham số chỉ thực hiện trên tập Training và Validation.
- Đánh giá chốt duy nhất một lần trên tập Test độc lập (Held-out Test Set).
- Phân tích đóng góp của từng nhóm đặc trưng và kiểm tra hiện tượng lối tắt độ dài văn bản.
- Phân tích lỗi định lượng theo phân đoạn dữ liệu (data slices) và kiểm tra định tính các ca lỗi lớn nhất.

### 2.2 Các nội dung NẰM NGOÀI phạm vi (Excluded)
- Tự động sửa lỗi ngữ pháp hoặc chính tả (Grammar error correction).
- Tự động sinh bài văn hoặc viết lại bài luận (Essay generation / rewriting).
- Tạo lời nhận xét sư phạm cá nhân hóa (Personalized pedagogical feedback generation).
- Phát hiện đạo văn hoặc gian lận thi cử.
- Chấm điểm bằng LLM dạng Zero-shot hoặc chỉ dùng Prompt Engineering đóng vai trò chấm điểm.
- **Sử dụng các checkpoint essay-scoring đã fine-tune sẵn bởi người dùng ngẫu nhiên trên mạng** (nhằm đảm bảo tính liêm chính học thuật, tránh rò rỉ tập test và giữ vững tính tái lập).
- Khẳng định đo lường năng lực ngôn ngữ toàn diện của học viên ngoài bài luận này.
- Triển khai thành hệ thống chấm điểm tự động có tính chất quyết định cao (High-stakes automated grading system).

### 2.3 Mục đích sử dụng dự kiến (Intended Use)
Hệ thống là một nguyên mẫu nghiên cứu (research prototype) phục vụ mục đích học thuật: phân tích mối tương quan giữa các đặc trưng ngôn ngữ học với nhận định của người chấm, đồng thời làm rõ sự đánh đổi giữa hiệu năng vượt trội của mô hình học sâu và tính minh bạch, dễ giải thích của các mô hình truyền thống. Mô hình tuyệt đối không được dùng để thay thế giáo viên hay ra quyết định điểm số chính thức.

---

## 3. Bài toán Nghiên cứu và Câu hỏi Nghiên cứu (Research Questions)

### 3.1 Câu hỏi nghiên cứu chính (Main Research Question)
> **Mức độ chính xác của các đặc trưng ngôn ngữ dễ giải thích so với mô hình Pretrained Transformer (DeBERTa-v3-small) khi dự đoán đồng thời 6 tiêu chí điểm viết bài của người học tiếng Anh ra sao, và mô hình nào cân bằng tốt nhất giữa hiệu năng và khả năng giải thích?**

### 3.2 Các câu hỏi nghiên cứu cụ thể (Sub-questions)

- **RQ1 — So sánh họ mô hình (Model Comparison):**  
  Trong số Ridge Regression, Decision Tree Regression và `microsoft/deberta-v3-small`, mô hình nào đạt sai số MCRMSE thấp nhất trên cùng một giao thức phân chia dữ liệu? Khoảng cách hiệu năng giữa mô hình học sâu và mô hình tuyến tính có đủ lớn để bù đắp sự mất mát tính diễn giải không?
  
- **RQ2 — Đóng góp của các nhóm đặc trưng (Feature Information & Ablation):**  
  Các đặc trưng bề mặt (độ dài), đặc trưng ngôn ngữ phi bề mặt (từ vựng, cú pháp, độ dễ đọc), và sự kết hợp của chúng mang lại bao nhiêu thông tin dự đoán?
  
- **RQ3 — Hiện tượng lối tắt và điều kiện phát sinh lỗi (Shortcut & Error Conditions):**  
  Các mô hình có xu hướng dựa vào chiều dài bài viết như một chỉ dấu đánh lừa không? Sai số lớn nhất thường xuất hiện ở dải điểm nào (cực cao, cực thấp), ở độ dài văn bản nào, hay ở các bài luận có phong cách viết dị biệt?
  
- **RQ4 — Tính tổng quát hóa và khả năng kết hợp (Generalization & Hybridization):**  
  Mô hình fine-tuned Transformer có thể hiện sự vượt trội đồng đều trên cả 6 tiêu chí điểm không? Việc kết hợp biểu diễn sâu của DeBERTa với các đặc trưng ngôn ngữ học (Hybrid Model) có giúp cải thiện sai số dự đoán không?

### 3.3 Các giả thuyết kỳ vọng cần kiểm chứng bằng thực nghiệm
- Mọi mô hình huấn luyện đều vượt qua Baseline trung bình (Mean Baseline).
- Việc kết hợp toàn bộ các nhóm đặc trưng ngôn ngữ sẽ cho kết quả tốt hơn là chỉ dùng các đặc trưng độ dài bề mặt.
- `microsoft/deberta-v3-small` sẽ đạt MCRMSE thấp hơn đáng kể so với các mô hình cổ điển nhờ khả năng nắm bắt ngữ cảnh, cấu trúc diễn ngôn và sắc thái ngữ nghĩa toàn cục.
- Cả hai họ mô hình đều có nguy cơ suy giảm độ chính xác ở dải điểm biên (1.0–2.0 và 4.5–5.0) do hiện tượng mất cân bằng dữ liệu (đa số bài tập trung ở dải 2.5–3.5).

---

## 4. Định nghĩa Nhiệm vụ Học máy (Machine Learning Task Definition)

### 4.1 Đầu vào cấp ứng dụng (Application-level Input)
Một bài luận tiếng Anh hoàn chỉnh do người học viết:
```text
I believe learning English is important because it helps people communicate across different cultures.
However, many students struggle with vocabulary and syntax when writing long essays...
```

### 4.2 Định dạng đầu vào mô hình (Model Input)
- **Đối với Classical Models (Ridge, Decision Tree):**  
  Văn bản được ánh xạ tất định thành vector đặc trưng số học:
  $$
  X_i = [x_{i1}, x_{i2}, \ldots, x_{ip}] \in \mathbb{R}^p \quad (p \approx 24 - 30)
  $$
- **Đối với Pretrained Transformer (DeBERTa-v3-small):**  
  Chuỗi token văn bản thô $T_i = (t_1, t_2, \ldots, t_L)$ được mã hóa bởi DeBERTa Tokenizer với độ dài tối đa 512 tokens (hoặc xử lý chunking).

### 4.3 Mục tiêu dự đoán (Target)
Dự đoán đồng thời vector 6 chiều tương ứng với 6 tiêu chí chấm điểm:
$$
\mathbf{y}_i = [y_{i1}, y_{i2}, y_{i3}, y_{i4}, y_{i5}, y_{i6}]^T
$$
Trong đó:
1. `cohesion`: Tính liên kết và mạch lạc giữa các câu, đoạn.
2. `syntax`: Cấu trúc câu và độ phức tạp cú pháp.
3. `vocabulary`: Vốn từ, sự phong phú và độ chính xác dùng từ.
4. `phraseology`: Sử dụng cụm từ tự nhiên, chuẩn thành ngữ bản ngữ.
5. `grammar`: Sự chuẩn xác về ngữ pháp, chia thì, hòa hợp chủ vị.
6. `conventions`: Quy ước chính tả, viết hoa, chấm câu, định dạng.

Giá trị nhãn gốc: $y_{ij} \in [1.0, 5.0]$ với bước nhảy rời rạc $0.5$.

### 4.4 Tại sao dự đoán đồng thời 6 target tốt hơn một điểm trung bình?
1. **Bảo toàn thông tin nhãn gốc:** Không tự tiện làm phẳng dữ liệu hoặc làm mất đi sự chênh lệch giữa các kỹ năng của người học.
2. **Tránh áp đặt trọng số bằng nhau:** Một bài viết có thể rất tốt về từ vựng (4.5) nhưng yếu về quy ước chính tả (2.0); việc gộp điểm sẽ xóa nhòa sự khác biệt sư phạm này.
3. **Phù hợp với tên đề tài:** Tên đề tài sử dụng số nhiều *"Scores"*, nhấn mạnh vào hồ sơ điểm đa chiều.
4. **Tính linh hoạt:** Hoàn toàn có thể suy ra điểm tổng hợp sau dự đoán nếu cần:
   $$
   \text{overall\_score}_i = \frac{1}{6} \sum_{j=1}^{6} \hat{y}_{ij}
   $$

### 4.5 Sơ đồ luồng xử lý đầu-cuối (End-to-end Flow)
```text
Bài luận của học viên (full_text)
            │
            ├──────────────────────────────────────────────────────┐
            ▼                                                      ▼
[Nhánh Mô hình Dễ giải thích]                              [Nhánh Pretrained Transformer]
            │                                                      │
Trích xuất đặc trưng ngôn ngữ                               Kiểm tra độ dài token
(Độ dài, Từ vựng, Cú pháp, Độ dễ đọc)                     (Phân tích phân phối percentiles)
            │                                                      │
Vector đặc trưng số học (24-30 chiều)                       Tokenization & Padding (max 512)
            │                                               (Hoặc Chunking 512/128 + Mean Pooling)
Tiền xử lý trong Pipeline                                          │
(Median Imputation, StandardScaler)                         Backbone DeBERTa-v3-small
            │                                               (Representation 768 chiều)
Mô hình Hồi quy Đa đầu ra                                          │
(Ridge / Decision Tree Regression)                          Dropout (0.1) & Linear Layer (768 -> 6)
            │                                                      │
            ├──────────────────────────────────────────────────────┘
            ▼
Khôi phục thang điểm & Cắt biên clip(1.0, 5.0)
            │
Vector 6 điểm dự đoán: [cohesion, syntax, vocabulary, phraseology, grammar, conventions]
            │
Đánh giá sai số MCRMSE, MAE, RMSE, R² & Phân tích lỗi / Phân tích lối tắt
```

---

## 5. Lựa chọn Dataset & Tiêu chí Chấp nhận

Dự án chốt sử dụng tập dữ liệu chuẩn mực quốc tế: **ELLIPSE / Feedback Prize – English Language Learning**.

### 5.1 Nguồn dữ liệu chính thức
- **Nguồn chính thức Kaggle:** [Kaggle – Feedback Prize: English Language Learning](https://www.kaggle.com/competitions/feedback-prize-english-language-learning/data)
- **Bản xem nhanh trên Hugging Face:** [Hugging Face Mirror](https://huggingface.co/datasets/tcapelle/feedback-prize-english-language-learning-fluency)
- **Quy mô:** Khoảng 3.911 bài viết của học sinh từ lớp 8 đến lớp 12 thuộc diện English Language Learners (ELL) với nguồn gốc ngôn ngữ bản địa đa dạng.

### 5.2 Các cột đầu vào và target chính thức
- **Mã định danh & văn bản:**
  - `text_id`: Mã duy nhất cho từng bài luận.
  - `full_text`: Nội dung toàn văn bài luận tiếng Anh thô.
- **Sáu cột target bắt buộc:**
  - `cohesion`, `syntax`, `vocabulary`, `phraseology`, `grammar`, `conventions`.
  - Khoảng giá trị: $1.0$ đến $5.0$ với bước điểm $0.5$.

### 5.3 Loại bỏ triệt để các cột gây rò rỉ thông tin (Data Leakage Prevention)
Bản Hugging Face mirror có chứa thêm một số cột siêu dữ liệu đánh giá:
- `mss` (Mã phiên chấm / nguồn).
- `response_fluency` (Đánh giá mức độ trôi chảy).
- `non_fluency_reason` (Lý do không trôi chảy).

> [!CAUTION]
> **Quy định bắt buộc:** Cột `non_fluency_reason` chứa nhận xét trực tiếp của chuyên gia chấm điểm về các lỗi hành văn, chất lượng bài viết. Việc giữ lại cột này hoặc sử dụng nó sẽ gây **rò rỉ mục tiêu nghiêm trọng (Target Leakage)**. Tất cả các cột này phải bị loại bỏ ngay khi nạp dữ liệu:
> ```python
> DROP_COLUMNS = ["mss", "response_fluency", "non_fluency_reason"]
> df = df.drop(columns=[c for c in DROP_COLUMNS if c in df.columns])
> ```

### 5.4 Căn cứ khoa học: Tại sao KHÔNG dùng checkpoint essay-scoring đã fine-tune sẵn?
Không sử dụng các mô hình essay-scoring do người dùng ngẫu nhiên chia sẻ trên Hugging Face vì các lý do học thuật nghiêm ngặt:
1. **Rủi ro rò rỉ dữ liệu (Data Leakage):** Không thể xác minh mô hình đó đã huấn luyện trên những bài luận nào trong ELLIPSE, nguy cơ tập Test của dự án đã nằm trong tập Train của mô hình đó là rất lớn.
2. **Không đồng nhất về phân chia tập dữ liệu:** Không thể kiểm soát được cách chia train/test cũ.
3. **Lệch thang điểm và rubric:** Các mô hình chia sẻ tự do có thể dùng thang điểm khác, hàm loss khác hoặc trọng số khác.
4. **Model Card thiếu minh bạch:** Đa số các checkpoint này thiếu thông tin chi tiết về phiên bản thư viện, cách tiền xử lý và nguồn dữ liệu làm sạch.
5. **Đảm bảo tính trung thực khoa học:** Việc tải pretrained language model gốc `microsoft/deberta-v3-small`, tự dựng regression head và tự thực hiện huấn luyện từ đầu trên phân chia 70/15/15 của chính dự án là cách tiếp cận minh bạch, chuẩn mực và chứng minh được đóng góp kỹ thuật thực chất của tác giả.

---

## 6. Kiểm toán Dữ liệu và Phân tích Khám phá (Data Audit & EDA)

### 6.1 Các phép kiểm toán tính toàn vẹn
- Kiểm tra tính duy nhất của `text_id`.
- Phát hiện bài viết trùng lặp hoàn toàn (exact duplicate) hoặc gần trùng lặp (near duplicate).
- Kiểm tra văn bản rỗng, chỉ có khoảng trắng hoặc quá ngắn ($< 15$ từ).
- Kiểm tra dữ liệu khuyết thiếu (missing values) trên cả văn bản và 6 cột target.
- Xác thực giá trị điểm số có nằm nghiêm ngặt trong đoạn $[1.0, 5.0]$ hay không.
- Giữ nguyên văn bản gốc của học viên: Không tự động sửa lỗi ngữ pháp/chính tả trong quá trình làm sạch vì chính các lỗi này là tín hiệu quan trọng để dự đoán điểm năng lực.

### 6.2 Phân tích phân phối điểm số
- Tính toán thống kê mô tả: Mean, Std, Median, Min, Max, Skewness, Kurtosis cho cả 6 tiêu chí.
- Trực quan hóa biểu đồ phân phối (histogram / KDE) của 6 tiêu chí và ma trận tương quan giữa 6 điểm số (thường có tương quan dương mạnh từ 0.65 đến 0.85).
- Kiểm tra hiện tượng mất cân bằng phân phối: Điểm số tập trung dày đặc ở dải trung bình ($2.5 - 3.5$), rất ít mẫu ở dải điểm cực đoan ($1.0 - 1.5$ hoặc $4.5 - 5.0$).

### 6.3 Kiểm tra phân phối độ dài token DeBERTa
Trước khi quyết định cắt ngắn văn bản, dự án thực hiện kiểm toán độ dài token DeBERTa bằng mã nguồn:
```python
token_lengths = df["full_text"].apply(
    lambda text: len(tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"])
)
token_stats = token_lengths.describe(percentiles=[0.5, 0.75, 0.9, 0.95, 0.99])
```
- **Kịch bản A:** Nếu trên 95% số bài viết có độ dài $\le 512$ tokens, việc áp dụng truncation đơn thuần ở ngưỡng 512 không gây mất mát thông tin nghiêm trọng.
- **Kịch bản B:** Nếu một lượng đáng kể bài viết vượt quá 512 tokens, dự án kích hoạt cơ chế Chunking dạng cửa sổ trượt (Sliding Window Chunking) để không bỏ sót nội dung cuối bài.

---

## 7. Thiết kế Đặc trưng Ngôn ngữ Dễ giải thích (Linguistic Features)

Dự án xây dựng bộ đặc trưng gồm **24 đến 30 biến định lượng** được chia thành 4 nhóm ngôn ngữ học có cơ sở lý thuyết vững chắc:

### 7.1 Nhóm S — Đặc trưng Bề mặt và Độ dài (Surface & Length Features)
Đo lường dung lượng và cấu trúc hình thức bài viết (chỉ số phản ánh nguy cơ lối tắt độ dài):
1. `word_count`: Tổng số từ trong bài luận.
2. `sentence_count`: Tổng số câu phát hiện được.
3. `paragraph_count`: Tổng số đoạn văn.
4. `character_count`: Tổng số ký tự (không tính khoảng trắng).
5. `mean_word_length`: Độ dài từ trung bình (số ký tự / số từ).
6. `mean_sentence_length`: Độ dài câu trung bình (số từ / số câu).

### 7.2 Nhóm L — Đặc trưng Độ phong phú Từ vựng (Lexical Diversity & Sophistication)
Đo lường năng lực sử dụng từ vựng đa dạng và trình độ từ ngữ nâng cao:
7. `ttr`: Type-Token Ratio (số từ phân biệt / tổng số từ).
8. `root_ttr`: Root TTR ($\text{types} / \sqrt{\text{tokens}}$) nhằm giảm phụ thuộc vào độ dài.
9. `mtld`: Measure of Textual Lexical Diversity (thước đo độ phong phú từ vựng ổn định).
10. `lexical_density`: Tỷ lệ từ nội dung (content words: danh từ, động từ, tính từ, trạng từ) trên tổng số từ.
11. `content_word_ratio`: Tỷ lệ từ thực từ trong toàn bài.
12. `mean_log_word_frequency`: Tần suất logarit trung bình của từ theo kho ngữ liệu chuẩn (external frequency corpus).
13. `rare_word_ratio`: Tỷ lệ các từ hiếm xuất hiện (nằm ngoài top từ phổ biến).

### 7.3 Nhóm Y — Đặc trưng Cú pháp và Ngữ pháp (Syntactic Complexity)
Đo lường mức độ phức tạp và độ chính xác của cấu trúc câu (sử dụng thư viện spaCy):
14. `noun_ratio`: Tỷ lệ danh từ trên tổng số từ.
15. `verb_ratio`: Tỷ lệ động từ trên tổng số từ.
16. `adjective_ratio`: Tỷ lệ tính từ trên tổng số từ.
17. `adverb_ratio`: Tỷ lệ trạng từ trên tổng số từ.
18. `subordination_ratio`: Tỷ lệ mệnh đề phụ thuộc trên tổng số câu (đo độ phức tạp liên câu).
19. `mean_dependency_depth`: Độ sâu trung bình của cây phụ thuộc cú pháp.
20. `mean_dependency_distance`: Khoảng cách tuyến tính trung bình giữa từ đứng đầu (head) và từ phụ thuộc (dependent).

### 7.4 Nhóm R — Đặc trưng Độ dễ đọc (Readability Formulas)
Các chỉ số kinh điển ước lượng độ khó văn bản dựa trên âm tiết, từ vựng và câu:
21. `flesch_reading_ease`: Chỉ số dễ đọc Flesch (điểm càng cao càng dễ đọc).
22. `flesch_kincaid_grade`: Ước lượng trình độ lớp học theo chuẩn Mỹ.
23. `gunning_fog`: Chỉ số Gunning Fog đo lường từ phức tạp ($\ge 3$ âm tiết).
24. `automated_readability_index`: Chỉ số ARI dựa trên tỷ lệ ký tự/từ và từ/câu.

---

## 8. Các Điều kiện Đặc trưng Phân tích Chính (Feature Conditions)

Để trả lời câu hỏi RQ2 mà không làm phân tán kết quả, dự án kiểm nghiệm 3 điều kiện đặc trưng tiền định:

| Điều kiện | Các nhóm đặc trưng bao gồm | Mục tiêu phân tích |
|---|---|---|
| **S: Surface-only** | Nhóm S (6 đặc trưng bề mặt/độ dài) | Đo lường mức độ đóng góp của riêng tín hiệu độ dài (lối tắt bài viết dài = điểm cao). |
| **Linguistic-only** | Nhóm L + Y + R (Từ vựng, Cú pháp, Độ dễ đọc) | Đánh giá năng lực dự đoán khi không có thông tin trực tiếp về dung lượng văn bản. |
| **All Features** | Nhóm S + L + Y + R (Toàn bộ 24–30 đặc trưng) | Đánh giá hiệu năng cao nhất của hướng tiếp cận trích xuất đặc trưng truyền thống. |

---

## 9. Phân chia Dữ liệu và Chống Rò rỉ (Data Splitting & Leakage Prevention)

### 9.1 Phân tích ràng buộc thực tế của Dataset
- Tập dữ liệu Feedback Prize ELL **không cung cấp** trường `learner_id` định danh duy nhất người học (các bài luận được thu thập ẩn danh). Do đó, không thể phân chia dạng `GroupKFold` theo cá nhân người học.
- Đề bài (prompts) cũng không có nhãn phân loại rõ ràng trong tập train chính thức.

### 9.2 Chiến lược phân chia chốt: 70 / 15 / 15 Stratified Split
Dự án chọn chiến lược phân chia 3 tập độc lập nhằm phục vụ tối ưu cho việc huấn luyện và dừng sớm (early stopping) mô hình Deep Learning:
- **70% Training set (~2.737 bài):** Dùng để học trọng số mô hình (fit feature scaler, train Ridge, Decision Tree và fine-tune DeBERTa).
- **15% Validation set (~587 bài):** Dùng để theo dõi hàm loss, tính metric MCRMSE theo từng epoch, thực hiện Early Stopping và lựa chọn checkpoint tốt nhất.
- **15% Held-out Test set (~587 bài):** Giữ tuyệt đối độc lập, chỉ nạp vào đánh giá đúng 1 lần duy nhất sau khi toàn bộ quy trình đã đóng băng (freeze).

### 9.3 Cơ chế phân tầng xấp xỉ theo phân vị điểm số (Binned Stratification)
Vì đây là bài toán hồi quy đa đầu ra liên tục, phân chia ngẫu nhiên thuần túy có thể dẫn đến phân bố điểm không đều giữa 3 tập. Dự án giải quyết bằng cách tạo 10 phân vị (quantiles) dựa trên điểm trung bình của 6 tiêu chí:
```python
df["mean_score"] = df[TARGET_COLUMNS].mean(axis=1)
df["score_bin"] = pd.qcut(df["mean_score"], q=10, labels=False, duplicates="drop")
```
Phép chia sẽ phân tầng theo cột `score_bin` với `random_state=42`, bảo đảm tập Train, Validation và Test có phân phối điểm tương đồng tuyệt đối.

### 9.4 Quy tắc nghiêm ngặt chống rò rỉ (Data Leakage Rules)
1. Mọi phép học thống kê (ví dụ: `StandardScaler.fit()`, tính trung vị thay thế khuyết thiếu) chỉ được thực hiện trên tập Training. Tập Validation và Test chỉ được gọi hàm `transform()`.
2. Toàn bộ quá trình tuning siêu tham số chỉ được sử dụng dữ liệu Training và Validation.
3. Không thực hiện bất kỳ phép chuẩn hóa hay trích chọn đặc trưng nào trên toàn bộ tập dữ liệu trước khi phân chia.

---

## 10. Tiền xử lý Dữ liệu & Xử lý Kỹ thuật

### 10.1 Chuẩn hóa Target về khoảng $[0, 1]$
Nhằm giúp quá trình tối ưu hóa trọng số (đặc biệt là gradient descent của DeBERTa) diễn ra ổn định và nhanh hội tụ, các giá trị điểm số gốc (từ 1.0 đến 5.0) được chuẩn hóa tuyến tính về đoạn $[0.0, 1.0]$:
$$
y_{\text{normalized}} = \frac{y - 1.0}{4.0}
$$
Quy trình khôi phục điểm gốc (Denormalization) khi xuất kết quả dự đoán:
$$
\hat{y} = \hat{y}_{\text{normalized}} \times 4.0 + 1.0
$$
Áp dụng cắt biên để đảm bảo điểm dự đoán luôn nằm trong phạm vi rubric hợp lệ:
$$
\hat{y}_{\text{clipped}} = \text{clip}(\hat{y}, 1.0, 5.0)
$$
Mã nguồn triển khai:
```python
def normalize_scores(scores):
    return (scores - 1.0) / 4.0

def denormalize_scores(scores):
    return scores * 4.0 + 1.0

# Sau khi mô hình đưa ra dự đoán:
predictions = denormalize_scores(predictions_normalized)
predictions = np.clip(predictions, 1.0, 5.0)
```
> [!IMPORTANT]
> **Quy tắc tính metric:** Tuyệt đối không làm tròn điểm số dự đoán về bước nhảy $0.5$ trước khi tính toán MCRMSE/MAE. Việc làm tròn làm biến dạng sai số liên tục của mô hình và chỉ được dùng khi hiển thị kết quả cho người dùng cuối.

### 10.2 Giải pháp Xử lý Bài luận Dài (Long Essay Handling)
Mô hình DeBERTa xử lý chuỗi tối đa 512 tokens. Để tránh việc cắt cụt tùy tiện phần kết luận của bài viết:
1. **Kiểm tra độ dài token:** Nếu đa phần bài viết trong khoảng $\le 512$ tokens:
   ```python
   tokenizer(text, max_length=512, truncation=True, padding="max_length")
   ```
2. **Cơ chế Chunking khi có nhiều bài dài:**
   - Cắt bài viết thành các đoạn chồng lấn (overlapping chunks) với `chunk_length = 512`, `stride = 128`.
   - Mỗi chunk được DeBERTa backbone mã hóa thành vector biểu diễn 768 chiều.
   - Thực hiện **Mean Pooling** trên các vector chunk để tổng hợp thành một biểu diễn duy nhất cho toàn bài luận trước khi đưa vào Regression Head.
   - *Không coi mỗi chunk là một mẫu độc lập*, vì nhãn điểm số phản ánh năng lực của toàn bộ bài viết chứ không thuộc về từng đoạn nhỏ riêng rẽ.

### 10.3 Pipeline xử lý cho Classical Models
Sử dụng `sklearn.pipeline.Pipeline` nhằm đóng gói chặt chẽ:
- **Ridge Regression Pipeline:** `Numerical Features` $\to` `SimpleImputer(strategy='median')` $\to` `StandardScaler()` $\to` `Ridge(alpha=...)`.
- **Decision Tree Pipeline:** `Numerical Features` $\to` `SimpleImputer(strategy='median')` $\to` `DecisionTreeRegressor(...)` (không cần chuẩn hóa thang đo cho mô hình cây).

---

## 11. Các Mô hình Huấn luyện và Cấu hình Chi tiết

### 11.1 Mô hình Cơ sở: Baseline Trung bình (Mean Baseline)
Mô hình không học, luôn dự đoán vector điểm trung bình của tập Train cho mọi mẫu trong tập Validation và Test:
$$
\hat{\mathbf{y}}_i = \bar{\mathbf{y}}_{\text{train}} \in \mathbb{R}^6
$$
Đây là cột mốc tối thiểu mà bất kỳ mô hình học máy nào cũng phải vượt qua.

### 11.2 Mô hình A: Ridge Regression (Mô hình Tuyến tính có Chính quy hóa)
- **Đầu vào:** 24–30 đặc trưng ngôn ngữ được chuẩn hóa z-score.
- **Bản chất:** Hồi quy tuyến tính đa biến với chính quy hóa L2 ($\alpha \|w\|_2^2$), hỗ trợ trực tiếp multi-output regression.
- **Mục tiêu:** Kiểm tra xem mối quan hệ giữa đặc trưng ngôn ngữ và điểm số có thể xấp xỉ tuyến tính hay không; cung cấp trọng số chuẩn hóa để giải thích tầm quan trọng của từng đặc trưng.

### 11.3 Mô hình B: K-Nearest Neighbors Regression (KNN - Tùy chọn)
- **Đầu vào:** 24–30 đặc trưng ngôn ngữ được chuẩn hóa z-score.
- **Bản chất:** Hồi quy dựa trên khoảng cách (Euclidean / Manhattan), dự đoán điểm bằng trung bình trọng số của $k$ bài viết gần nhất trong không gian đặc trưng.
- **Mục tiêu:** Kiểm chứng giả thuyết: những bài luận có hồ sơ ngôn ngữ tương tự nhau thì nhận điểm tương tự nhau.

### 11.4 Mô hình C: Decision Tree Regression (Cây Quyết định Đa đầu ra)
- **Đầu vào:** 24–30 đặc trưng ngôn ngữ gốc.
- **Bản chất:** Cây quyết định phân nhánh dựa trên giảm thiểu phương sai (MSE reduction) đồng thời trên cả 6 đầu ra.
- **Mục tiêu:** Nắm bắt các ngưỡng phi tuyến và tương tác giữa các đặc trưng (ví dụ: bài viết dài nhưng tỷ lệ từ hiếm thấp thì bị khống chế điểm). Kiểm soát bằng `max_depth` và `min_samples_leaf`.

### 11.5 Mô hình D: Pretrained Transformer (`microsoft/deberta-v3-small`)
- **Nền tảng:** Mô hình DeBERTa-v3-small tải từ Hugging Face Hub (MIT License).
  - 6 transformer layers, hidden size 768, 44 triệu tham số backbone.
  - Sử dụng cơ chế Disentangled Attention và Enhanced Masked Language Modeling, có kích thước nhẹ, phù hợp tối ưu với tập dữ liệu ~3.900 bài luận và tài nguyên GPU tầm trung (Google Colab / Kaggle T4).
- **Kiến trúc Regression Head:**
  ```text
  DeBERTa-v3-small Backbone (Contextual Embedding: 768 dimensions)
                         │
                      Dropout (p = 0.1)
                         │
             Linear Layer (768 -> 6 outputs)
                         │
         6 Điểm số dự đoán liên tục [0, 1]
  ```
- **Mã khởi tạo mô hình chuẩn Hugging Face:**
  ```python
  from transformers import AutoTokenizer, AutoModelForSequenceClassification

  MODEL_NAME = "microsoft/deberta-v3-small"
  tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
  model = AutoModelForSequenceClassification.from_pretrained(
      MODEL_NAME,
      num_labels=6,
      problem_type="regression"
  )
  ```

### 11.6 Cấu hình Huấn luyện DeBERTa Khuyến nghị
Bảng siêu tham số được tối ưu hóa cho môi trường GPU thông dụng (Kaggle / Colab T4):

| Siêu tham số | Giá trị cấu hình | Ý nghĩa & Lý do |
|---|---|---|
| `model_name` | `microsoft/deberta-v3-small` | Backbone ngôn ngữ đã tiền huấn luyện |
| `max_length` | `512` | Chiều dài token tối đa |
| `learning_rate` | `2.0e-5` | Tốc độ học chuẩn cho fine-tuning DeBERTa |
| `num_train_epochs` | `5` | Số lượt duyệt toàn bộ tập huấn luyện |
| `per_device_train_batch_size` | `4` | Batch size cục bộ trên mỗi GPU |
| `gradient_accumulation_steps` | `4` | Tích lũy gradient để đạt **Effective Batch Size = 16** |
| `per_device_eval_batch_size` | `8` | Batch size đánh giá trên tập Validation |
| `weight_decay` | `0.01` | Tránh hiện tượng overfitting trọng số |
| `warmup_ratio` | `0.10` | 10% số bước đầu tăng dần learning rate |
| `lr_scheduler_type` | `linear` | Giảm tốc độ học tuyến tính sau warmup |
| `fp16` | `True` | Huấn luyện độ chính xác nửa (Mixed Precision) tăng tốc độ |
| `evaluation_strategy` | `epoch` | Đánh giá sai số sau mỗi epoch hoàn thành |
| `save_strategy` | `epoch` | Lưu checkpoint sau mỗi epoch |
| `load_best_model_at_end` | `True` | Tự động nạp lại trọng số tốt nhất khi kết thúc |
| `metric_for_best_model` | `mcrmse` | Chọn checkpoint có MCRMSE nhỏ nhất trên Validation |
| `greater_is_better` | `False` | Chỉ số lỗi càng nhỏ càng tốt |
| `early_stopping_patience` | `2` | Dừng sớm nếu sau 2 epoch MCRMSE không cải thiện |
| `seed` | `42` | Cố định hạt giống ngẫu nhiên đảm bảo tính tái lập |

---

## 12. Thiết kế Thực nghiệm (Experimental Design)

Dự án thiết lập chuỗi thực nghiệm E0 đến E5 (và E6 tùy chọn) nhằm phân tích có hệ thống:

| Mã thực nghiệm | Tên thực nghiệm | Đầu vào (Features) | Mô hình (Model) | Câu hỏi trả lời |
|---|---|---|---|---|
| **E0** | Baseline tham chiếu | Không dùng feature | Mean Baseline | Mức sai số tối thiểu mà mô hình học máy phải vượt qua là bao nhiêu? |
| **E1** | Lối tắt độ dài (Length shortcut) | Nhóm S (Surface-only) | Ridge Regression | Riêng thông tin về độ dài văn bản có thể dự đoán điểm tốt đến mức nào? |
| **E2** | Đặc trưng ngôn ngữ phi độ dài | Nhóm L + Y + R (Linguistic-only) | Ridge Regression | Từ vựng, cú pháp và độ dễ đọc giải thích được bao nhiêu phương sai điểm số? |
| **E3** | Mô hình Tuyến tính toàn diện | Nhóm S + L + Y + R (All) | Ridge Regression | Hiệu năng tối đa của mô hình hồi quy tuyến tính dễ giải thích là bao nhiêu? |
| **E4** | Mô hình Cây quyết định phi tuyến | Nhóm S + L + Y + R (All) | Decision Tree Regression | Các tương tác phi tuyến giữa các đặc trưng có giúp giảm sai số so với Ridge không? |
| **E5** | Mô hình Deep Learning Transformer | Chuỗi văn bản thô (`full_text`) | `microsoft/deberta-v3-small` | Mô hình ngôn ngữ tiền huấn luyện sâu có vượt trội hơn hẳn đặc trưng thủ công không? |
| **E6** *(Tùy chọn)* | Mô hình Lai (Hybrid Model) | DeBERTa representation + All linguistic features | Ridge / MLP Head | Việc kết hợp đặc trưng ngôn ngữ học vào Transformer có tạo ra hiệu ứng cộng hưởng không? |

---

## 13. Tiêu chí Đánh giá (Evaluation Metrics)

### 13.1 Metric chính: MCRMSE (Mean Columnwise Root Mean Squared Error)
Do bài toán dự đoán đồng thời 6 biến mục tiêu liên tục, dự án sử dụng **MCRMSE** làm chỉ số tối ưu hóa và đánh giá chính thức (đồng bộ với thước đo của cuộc thi Kaggle Feedback Prize ELL):

$$
MCRMSE = \frac{1}{6} \sum_{j=1}^{6} \sqrt{ \frac{1}{n} \sum_{i=1}^{n} (y_{ij} - \hat{y}_{ij})^2 }
$$

Trong đó:
- $n$: Số lượng mẫu trong tập đánh giá.
- $j$: Chỉ số cột tương ứng với 6 tiêu chí chấm điểm ($j \in \{1, 2, \ldots, 6\}$).
- $y_{ij}$: Điểm số thực tế của mẫu $i$ tại tiêu chí $j$.
- $\hat{y}_{ij}$: Điểm số mô hình dự đoán cho mẫu $i$ tại tiêu chí $j$.

Mã nguồn Python chuẩn hóa để đánh giá:
```python
import numpy as np
from sklearn.metrics import mean_squared_error

def mcrmse(y_true, y_pred):
    column_rmse = []
    for column in range(y_true.shape[1]):
        rmse = np.sqrt(mean_squared_error(y_true[:, column], y_pred[:, column]))
        column_rmse.append(rmse)
    return float(np.mean(column_rmse))
```

### 13.2 Các Metric bổ sung (Secondary Metrics)
Nhằm phân tích sâu năng lực của mô hình trên từng khía cạnh kỹ năng cụ thể, dự án ghi nhận và báo cáo:
- **MAE từng tiêu chí:** $MAE_j = \frac{1}{n} \sum_{i=1}^n |y_{ij} - \hat{y}_{ij}|$ (đơn vị trực tiếp là thang điểm, dễ giải thích cho người dạy ngôn ngữ).
- **Mean MAE:** Trung bình cộng MAE trên 6 cột: $\frac{1}{6}\sum_{j=1}^6 MAE_j$.
- **RMSE từng tiêu chí:** $RMSE_j = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_{ij} - \hat{y}_{ij})^2}$ (phạt nặng các ca dự đoán sai lệch lớn).
- **Hệ số xác định $R^2$ từng tiêu chí:** $R_j^2 = 1 - \frac{\sum_i (y_{ij} - \hat{y}_{ij})^2}{\sum_i (y_{ij} - \bar{y}_j)^2}$ (đo tỷ lệ phương sai mà mô hình giải thích được).

> [!NOTE]
> **Không sử dụng Accuracy:** Các chỉ số như Accuracy, Precision, Recall, Macro F1 không được sử dụng cho bài toán hồi quy đa đầu ra này vì đây là bài toán biến liên tục, không phải bài toán phân loại rời rạc.

---

## 14. Khung Bảng Kết quả Thực nghiệm Dự kiến (Results Tables)

Toàn bộ các số liệu sẽ được điền tự động từ pipeline thực nghiệm có thể tái lập, không ghi số liệu minh họa khi chưa chạy code.

### 14.1 Bảng so sánh các mô hình chính (Main Model Comparison Table)

| Mô hình | Đầu vào (Input) | Val MCRMSE ↓ | Test MCRMSE ↓ | Test Mean MAE ↓ | Test Mean $R^2$ ↑ |
|---|---|---:|---:|---:|---:|
| **Mean Baseline** | Vector trung bình | TBD | TBD | TBD | TBD |
| **Ridge Regression** | 24–30 linguistic features | TBD | TBD | TBD | TBD |
| **Decision Tree** | 24–30 linguistic features | TBD | TBD | TBD | TBD |
| **DeBERTa-v3-small** | Raw essay (`full_text`) | TBD | TBD | TBD | TBD |
| **Hybrid (Tùy chọn)** | DeBERTa + Linguistic features | TBD | TBD | TBD | TBD |

### 14.2 Bảng chi tiết từng tiêu chí trên tập Test (Per-Target Test Metrics)

| Tiêu chí | Mean Baseline RMSE | Ridge RMSE | Decision Tree RMSE | DeBERTa-v3-small RMSE | DeBERTa MAE | DeBERTa $R^2$ |
|---|---:|---:|---:|---:|---:|---:|
| `cohesion` | TBD | TBD | TBD | TBD | TBD | TBD |
| `syntax` | TBD | TBD | TBD | TBD | TBD | TBD |
| `vocabulary` | TBD | TBD | TBD | TBD | TBD | TBD |
| `phraseology` | TBD | TBD | TBD | TBD | TBD | TBD |
| `grammar` | TBD | TBD | TBD | TBD | TBD | TBD |
| `conventions`| TBD | TBD | TBD | TBD | TBD | TBD |
| **MCRMSE / Mean** | **TBD** | **TBD** | **TBD** | **TBD** | **TBD** | **TBD** |

### 14.3 Bảng kiểm chứng các điều kiện đặc trưng (Feature Conditions Comparison)

| Mô hình | Surface-only MCRMSE (E1) | Linguistic-only MCRMSE (E2) | All Features MCRMSE (E3) | Mức chênh lệch ($\Delta$) |
|---|---:|---:|---:|---|
| **Ridge Regression** | TBD | TBD | TBD | TBD |

---

## 15. Phương pháp Giải thích Mô hình (Model Interpretability)

Tính minh bạch và khả năng giải thích là giá trị cốt lõi của nghiên cứu này.

### 15.1 Giải thích Mô hình Tuyến tính Ridge
- Trích xuất ma trận hệ số chuẩn hóa $\mathbf{W} \in \mathbb{R}^{6 \times p}$.
- Trực quan hóa Top 5 đặc trưng có trọng số dương lớn nhất và Top 5 đặc trưng có trọng số âm lớn nhất cho từng tiêu chí trong số 6 tiêu chí (ví dụ: `word_count` tác động mạnh tới `cohesion`, `mtld` tác động mạnh tới `vocabulary`, `subordination_ratio` tác động mạnh tới `syntax`).
- Khẳng định rõ: Hệ số thể hiện mức độ liên đới thống kê có điều kiện trong tập dữ liệu, không chứng minh mối quan hệ nhân quả.

### 15.2 Giải thích Cây quyết định
- Trích xuất độ quan trọng đặc trưng (Feature Importance) dựa trên mức giảm phương sai (MSE impurity reduction) và Permutation Importance.
- Vẽ sơ đồ các phân nhánh cấp cao nhất (top 3 tầng đầu) của cây để làm rõ ngưỡng quyết định (ví dụ: nếu `word_count` $\le 210$ thì điểm tối đa bị giới hạn ở mức nào).

### 15.3 Khả năng diễn giải của Pretrained Transformer (DeBERTa)
- Mặc dù DeBERTa là mô hình hộp đen phức tạp, dự án sẽ phân tích cơ chế chú ý (Self-Attention Weights) hoặc tính gradient saliency maps trên một số ca điển hình để xem mô hình chú ý vào các cấu trúc câu, từ ngữ liên kết hay chỉ nhìn vào độ dài văn bản.

---

## 16. Kế hoạch Phân tích Lỗi (Error Analysis Plan)

Phân tích lỗi là phần trọng tâm khoa học, chiếm dung lượng lớn trong báo cáo:

### 16.1 Định nghĩa phần dư (Residuals)
$$
e_{ij} = y_{ij} - \hat{y}_{ij}
$$
- $e_{ij} > 0$: Mô hình dự đoán thấp hơn điểm thực tế của người chấm (Underprediction).
- $e_{ij} < 0$: Mô hình dự đoán cao hơn điểm thực tế của người chấm (Overprediction).

### 16.2 Phân đoạn định lượng (Quantitative Data Slices)
Tính toán sai số MCRMSE và MAE phân tách theo:
1. **Dải điểm thực tế:** Phân nhóm điểm thấp ($[1.0, 2.5)$), trung bình ($[2.5, 3.5]$), và cao ($(3.5, 5.0]$).
2. **Nhóm độ dài bài viết:** Bài ngắn ($< 200$ từ), trung bình ($200 - 400$ từ), dài ($> 400$ từ).
3. **Độ phân tán giữa các tiêu chí:** Những bài viết có sự chênh lệch lớn giữa các điểm thành phần (ví dụ: Grammar 2.0 nhưng Vocabulary 4.0).

### 16.3 Lựa chọn và kiểm tra ca bệnh điển hình (Qualitative Case Studies)
Trích xuất tối thiểu 5 ca lỗi nghiêm trọng nhất trên tập Test:
- Bài viết dài nhưng điểm thực tế thấp: Mô hình có bị "lừa" cho điểm cao không?
- Bài viết ngắn nhưng hành văn cô đọng, ngữ pháp chuẩn: Mô hình có bị phạt oan vì thiếu dung lượng không?
- Bài viết có lỗi chính tả/ngữ pháp đặc thù mà parser ngôn ngữ trích xuất sai.

---

## 17. Phân tích Lối tắt và Thiên vị Độ dài (Shortcut & Length Bias Analysis)

Câu hỏi trọng tâm:
> **Mô hình thực sự học được năng lực ngôn ngữ, hay chỉ đơn giản học lối tắt rằng bài càng dài thì điểm càng cao?**

Các bằng chứng thực nghiệm đối chất:
1. So sánh trực tiếp MCRMSE giữa **E1 (Surface-only)** và **E3 (All Features)**:
   - Nếu $MCRMSE_{E1} \approx MCRMSE_{E3}$, độ dài bài viết là tín hiệu áp đảo hoàn toàn.
   - Nếu $MCRMSE_{E3}$ tốt hơn rõ rệt so với $MCRMSE_{E1}$, các đặc trưng cú pháp và từ vựng cung cấp giá trị dự đoán độc lập thực chất.
2. Đánh giá **E2 (Linguistic-only)**: Xem khi loại bỏ hoàn toàn các đặc trưng đếm độ dài thì mô hình đạt độ chính xác ra sao.
3. So sánh tương quan phần dư với độ dài bài luận giữa Ridge Regression và DeBERTa-v3-small.

---

## 18. Thí nghiệm Khả năng Tổng quát hóa (Generalization Experiment)

- Đánh giá khả năng tổng quát hóa của DeBERTa-v3-small và Ridge trên các bài viết có cấu trúc đặc biệt hoặc từ vựng ngoài kho ngữ liệu thông thường.
- Thảo luận rõ giới hạn về mặt dữ liệu: Do tập dữ liệu Feedback Prize ELL không cung cấp nhãn người học (`learner_id`) hoặc nhãn đề tài (`prompt_id`) một cách tường minh trong metadata gốc, các thử nghiệm về unseen-learner và unseen-prompt sẽ được thảo luận dưới dạng phân tích suy rộng và khuyến nghị hướng nghiên cứu tiếp nối thay vì tuyên bố vô căn cứ.

---

## 19. Cấu trúc Triển khai và Tính Tái lập (Reproducibility)

### 19.1 Cấu trúc mã nguồn đề xuất
```text
project/
├── configs/
│   └── experiment.yaml          # Cấu hình đường dẫn, siêu tham số, split, seed
├── data/
│   ├── 01_original_source/      # Corpus, điểm rater và tài liệu gốc
│   ├── 02_split_manifest/       # Manifest train/validation/official-test
│   ├── 03_clean_ready_to_use/   # Bảng bài luận sạch theo từng phân vùng
│   ├── 04_intermediate_work/    # Checkpoint và dữ liệu kiểm toán tạm
│   └── 05_model_features/       # Ma trận đặc trưng ngôn ngữ hoàn chỉnh
├── notebooks/
│   ├── 01_data_audit_eda.ipynb  # Khám phá dữ liệu, phân phối token percentiles
│   ├── 02_feature_extraction.ipynb # Trích xuất và kiểm định 24-30 đặc trưng
│   ├── 03_classical_models.ipynb   # Baseline, Ridge, Decision Tree (E0 - E4)
│   ├── 04_deberta_finetuning.ipynb # Huấn luyện DeBERTa-v3-small (E5)
│   └── 05_error_shortcut_analysis.ipynb # Phân tích lỗi, shortcut, đối chiếu
├── src/
│   ├── config.py                # Đọc cấu hình tập trung
│   ├── data.py                  # Tải dữ liệu, lọc bỏ non_fluency_reason, nắn chỉnh
│   ├── features.py              # Trích xuất 4 nhóm đặc trưng ngôn ngữ
│   ├── split.py                 # Chia dữ liệu 70/15/15 stratify theo score_bin
│   ├── models.py                # Xây dựng Ridge, Tree, DeBERTa Regression Head
│   ├── evaluate.py              # Hàm tính MCRMSE, MAE, RMSE, R²
│   └── analysis.py              # Phân tích phần dư và trực quan hóa
├── tests/
│   ├── test_features.py         # Kiểm thử tính đúng đắn trích xuất đặc trưng
│   ├── test_splits.py           # Kiểm tra không trùng lặp và tỷ lệ split
│   └── test_metrics.py          # Kiểm thử tính toán MCRMSE
├── outputs/
│   ├── models/                  # Checkpoint DeBERTa tốt nhất, file .joblib cho Ridge
│   ├── predictions/             # predictions_test.csv ghi nhận 6 nhãn dự đoán
│   └── figures/                 # Biểu đồ phân phối, feature importance, residuals
├── requirements.txt             # Danh sách thư viện cố định phiên bản
└── README.md                    # Hướng dẫn tái lập toàn bộ quy trình bằng 1 dòng lệnh
```

### 19.2 Yêu cầu nghiêm ngặt về tính tái lập
- Cố định toàn bộ hạt giống ngẫu nhiên: `random_seed = 42` (trong Python, NumPy, PyTorch, Transformers).
- Lưu `essay_split_manifest.csv` của tập Train, Validation và official Test để mọi thử nghiệm dùng chung một phân vùng cố định.
- Lưu trữ file dự đoán `predictions_test.csv` gồm: `text_id`, 6 điểm thực tế, 6 điểm dự đoán của từng mô hình và 6 giá trị phần dư tương ứng.

---

## 20. Đạo đức, Quyền riêng tư và Sử dụng Có trách nhiệm

1. **Bảo mật và Quyền sở hữu dữ liệu:** Dữ liệu ELLIPSE được phát hành theo giấy phép nghiên cứu mở của Kaggle; không chứa thông tin nhận dạng cá nhân (PII) của học sinh.
2. **Nhận thức về bản chất điểm số:** Điểm số là nhận định chủ quan của giám khảo theo rubric, không phải là chân lý tuyệt đối về trí tuệ hay năng lực học tập của một con người.
3. **Tuyệt đối không thay thế giáo viên:** Mô hình nghiên cứu này không được phép dùng để quyết định điểm số thực tế, cấp chứng chỉ hoặc phân loại học sinh trong môi trường giáo dục thật.
4. **Cảnh báo về thiên kiến văn hóa và phong cách viết:** Các bài luận có cấu trúc diễn đạt mang âm hưởng ngôn ngữ mẹ đẻ (L1 transfer) có thể bị mô hình chấm điểm thấp do không khớp với mẫu hình văn bản phổ biến trong tập train.

---

## 21. Minh bạch về việc Sử dụng LLM & AI Tạo sinh (LLM Disclosure)

Dự án có sử dụng các công cụ Trí tuệ nhân tạo tạo sinh (như Antigravity / Gemini / ChatGPT) trong vai trò trợ lý hỗ trợ kỹ thuật:
- Tra cứu cú pháp thư viện, viết khung mã nguồn ban đầu (boilerplate code).
- Hỗ trợ định dạng tài liệu, kiểm tra lỗi chính tả và gợi ý cấu trúc báo cáo.
- **Cam kết tác giả:** Toàn bộ ý tưởng thiết kế thực nghiệm, lựa chọn mô hình, cơ chế kiểm soát rò rỉ dữ liệu, việc thực thi mã nguồn trên GPU, phân tích kết quả và kết luận cuối cùng đều do tác giả trực tiếp thực hiện, kiểm tra và chịu trách nhiệm học thuật. Không sử dụng LLM để chấm điểm giả lập hay tạo dữ liệu giả.

---

## 22. Các Giới hạn của Nghiên cứu (Limitations)

1. **Hiệu lực khái niệm (Construct Validity):** Một bài viết duy nhất không đại diện cho toàn bộ năng lực viết hay trình độ tiếng Anh của người học.
2. **Độ bất định của người chấm (Rater Inconsistency):** Con người có thể mệt mỏi, có định kiến vô thức hoặc hiểu rubric khác nhau, dẫn đến nhãn ground-truth chứa nhiễu.
3. **Giới hạn bộ tách từ và phân tích cú pháp (Parser Reliability):** Các công cụ NLP chuẩn (như spaCy) thường được huấn luyện trên văn báo chí chuẩn mực, do đó có thể phân tích sai cú pháp khi gặp bài viết nhiều lỗi của người học.
4. **Độ dài cửa sổ Transformer:** Mô hình DeBERTa bị giới hạn ở 512 tokens; dù đã có phương án chunking nhưng vẫn có thể làm suy giảm sự gắn kết ngữ cảnh toàn bài so với các kiến trúc long-context chuyên dụng.
5. **Thiên lệch phân phối điểm:** Điểm tập trung nhiều ở dải trung bình khiến mô hình có xu hướng dự đoán co cụm về giá trị kỳ vọng (regression to the mean), dẫn đến sai số lớn ở nhóm bài xuất sắc hoặc nhóm bài quá yếu.

---

## 23. Tuyên bố Hợp lệ và Tuyên bố Cần Tránh

### 23.1 Tuyên bố HỢP LỆ (Được minh chứng bởi thực nghiệm)
- Mô hình DeBERTa-v3-small đạt MCRMSE thấp hơn so với Ridge Regression trên tập kiểm thử của dữ liệu ELLIPSE.
- Các đặc trưng từ vựng và cú pháp mang lại thông tin dự đoán bổ sung có ý nghĩa so với việc chỉ dựa vào đặc trưng độ dài bề mặt.
- Mô hình có xu hướng dự đoán thiên lệch ở dải điểm cực đoan do hiện tượng mất cân bằng số lượng mẫu.

### 23.2 Tuyên bố BẤT HỢP LỆ (Tuyệt đối không được nêu trong báo cáo)
- "Mô hình có khả năng đo lường chính xác trình độ tiếng Anh tuyệt đối của học sinh."
- "Đặc trưng độ dài từ hay câu là nguyên nhân trực tiếp làm tăng điểm số bài viết." (Nhầm lẫn giữa tương quan và nhân quả).
- "Hệ thống có thể thay thế hoàn toàn giám khảo con người trong các kỳ thi chuẩn hóa."
- "Kết quả này tự động khái quát hóa cho tất cả các kỳ thi tiếng Anh khác như IELTS hay TOEFL."

---

## 24. Cấu trúc Báo cáo Cuối kỳ (Final Report Structure)

Báo cáo chính thức sẽ tuân theo cấu trúc 14 chương chuẩn mực học thuật:
1. **Mở đầu (Introduction):** Bối cảnh, tính cấp thiết, định nghĩa bài toán, câu hỏi nghiên cứu và đóng góp cốt lõi.
2. **Kiến thức Nền tảng (Background & Related Work):** Đánh giá bài viết người học, các nhóm đặc trưng ngôn ngữ, học máy truyền thống vs. Pretrained Transformer.
3. **Tập dữ liệu ELLIPSE (Dataset Description):** Nguồn gốc Kaggle, rubric 6 tiêu chí, thống kê mô tả, đạo đức dữ liệu.
4. **Kiểm toán Dữ liệu và Tiền xử lý (Data Audit & Preprocessing):** Loại bỏ cột rò rỉ `non_fluency_reason`, làm sạch văn bản, phân tầng 70/15/15, chuẩn hóa target $[0, 1]$.
5. **Kỹ nghệ Đặc trưng Ngôn ngữ (Linguistic Feature Engineering):** Chi tiết 4 nhóm S, L, Y, R và phương pháp trích xuất bằng spaCy / textstat.
6. **Mô hình và Pipeline Học máy (Models & Architectures):** Mean Baseline, Ridge, Decision Tree, và kiến trúc DeBERTa-v3-small regression head.
7. **Thiết lập Thực nghiệm (Experimental Setup):** Môi trường huấn luyện, siêu tham số, cơ chế chunking bài dài, tính tái lập.
8. **Chỉ số Đánh giá (Evaluation Metrics):** MCRMSE, MAE, RMSE, $R^2$.
9. **Kết quả Thực nghiệm (Experimental Results):** Các bảng so sánh mô hình, so sánh điều kiện đặc trưng E0–E5.
10. **Phân tích và Diễn giải Mô hình (Interpretation & Discussion):** Tầm quan trọng của đặc trưng, kiểm tra lối tắt độ dài văn bản.
11. **Phân tích Lỗi Toàn diện (Error Analysis):** Phân tích lát cắt định lượng và nghiên cứu trường hợp sai lệch lớn nhất.
12. **Giới hạn và Sử dụng Có trách nhiệm (Limitations & Ethical Considerations).**
13. **Minh bạch Sử dụng AI (Generative AI Disclosure).**
14. **Kết luận và Hướng phát triển (Conclusion & Future Work).**

---

## 25. Chuẩn bị Vấn đáp Bảo vệ Đề tài (Oral Defense Q&A Preparation)

Các câu hỏi phản biện trọng tâm hội đồng có thể đặt ra và định hướng trả lời:

### Câu 1: Tại sao chọn dự đoán cả 6 tiêu chí thay vì lấy điểm trung bình?
- **Trả lời:** Điểm trung bình làm phẳng thông tin và xóa nhòa sự chênh lệch tự nhiên giữa các kỹ năng của người học (ví dụ: người có vốn từ phong phú nhưng yếu ngữ pháp). Dự đoán vector 6 chiều phản ánh đúng rubric sư phạm và giữ nguyên nhãn gốc của đề tài. Điểm tổng hợp hoàn toàn có thể tính lại bằng trung bình cộng các đầu ra sau khi dự đoán.

### Câu 2: Tại sao chọn `microsoft/deberta-v3-small` mà không dùng BERT hay RoBERTa-large?
- **Trả lời:** DeBERTa-v3 sử dụng cơ chế Disentangled Attention giúp phân tách biểu diễn nội dung và vị trí tương đối của từ, vượt trội hơn BERT/RoBERTa trên các tác vụ ngôn ngữ tự nhiên. Phiên bản `small` (44M backbone params) có dung lượng nhỏ gọn, ít nguy cơ overfit trên tập dữ liệu ~3.900 mẫu, đồng thời chạy mượt mà trên GPU tầm trung trong thời gian cho phép.

### Câu 3: Tại sao không tải một checkpoint essay-scoring đã fine-tune sẵn trên Hugging Face để đạt điểm cao hơn?
- **Trả lời:** Việc dùng model fine-tuned sẵn tiềm ẩn rủi ro rò rỉ dữ liệu (model có thể đã nhìn thấy tập test của dự án), không rõ phân vùng huấn luyện cũ, và có thể khác biệt về thang điểm/rubric. Về mặt học thuật, việc tự dựng regression head trên pretrained language model gốc và tự fine-tune từ đầu là phương pháp luận chuẩn xác, trung thực và chứng minh được năng lực làm chủ quy trình khoa học dữ liệu của sinh viên.

### Câu 4: Làm thế nào để chứng minh mô hình không chỉ đơn giản đếm số lượng từ để cho điểm?
- **Trả lời:** Dự án đã thiết kế thực nghiệm kiểm chứng trực diện: so sánh mô hình chỉ dùng đặc trưng bề mặt (E1) với mô hình chỉ dùng đặc trưng ngôn ngữ phi độ dài (E2) và mô hình toàn diện (E3). Đồng thời, đồ thị tương quan giữa phần dư dự đoán với độ dài bài luận sẽ làm sáng tỏ mức độ thiên lệch của từng mô hình.

---

## 26. Lộ trình Thực hiện Dự án (Project Execution Roadmap)

Lộ trình được chia thành 8 giai đoạn tuần tự, tuân thủ nguyên tắc "đóng băng" (freeze) từng bước:
- **Phase 1: Chốt Cổng Dữ liệu (Dataset Gate):** Tải dữ liệu ELLIPSE từ Kaggle, loại bỏ ngay các cột `non_fluency_reason`, `mss`, `response_fluency`, xác thực cấu trúc 6 target.
- **Phase 2: Kiểm toán Dữ liệu và EDA:** Khám phá phân phối điểm, thống kê độ dài token (percentiles), xác nhận chiến lược chunking / truncation.
- **Phase 3: Cố định Phân vùng Dữ liệu (Splitting Freeze):** Giữ nguyên official test, chia official train 80/20 và xuất `essay_split_manifest.csv` cố định.
- **Phase 4: Triển khai Đặc trưng Ngôn ngữ:** Cài đặt bộ trích xuất 24–30 đặc trưng cho các nhóm S, L, Y, R; kiểm tra tính đúng đắn và lưu ma trận đặc trưng.
- **Phase 5: Huấn luyện Mô hình Truyền thống (E0 – E4):** Xây dựng pipeline scikit-learn cho Baseline, Ridge Regression, Decision Tree; tối ưu tham số trên tập Train/Val.
- **Phase 6: Fine-tuning DeBERTa-v3-small (E5):** Tinh chỉnh mô hình Deep Learning trên GPU, giám sát MCRMSE trên tập Validation, lưu lại checkpoint tốt nhất.
- **Phase 7: Đánh giá Chốt trên Tập Test & Phân tích:** Đánh giá đúng 1 lần duy nhất toàn bộ các mô hình trên tập Test; tiến hành phân tích lối tắt và phân tích lỗi.
- **Phase 8: Viết Báo cáo & Luyện tập Vấn đáp:** Hoàn thiện báo cáo 14 chương, vẽ biểu đồ xuất bản, chuẩn bị slide và tập dượt trả lời phản biện.

---

## 27. Dự án Khả thi Tối thiểu (MVP) và Biên giới Mở rộng

### 27.1 Phần Cốt lõi Bắt buộc (Must-have Core)
- Nạp và tiền xử lý sạch tập dữ liệu Kaggle ELLIPSE.
- Dự đoán đồng thời 6 đầu ra điểm số.
- Huấn luyện đầy đủ 4 mô hình: Mean Baseline, Ridge Regression, Decision Tree Regression, và Pretrained DeBERTa-v3-small.
- Chuẩn hóa target về $[0, 1]$ và khôi phục hợp lệ $[1.0, 5.0]$.
- Đánh giá bằng metric MCRMSE và các metric phụ (MAE, RMSE, $R^2$).
- Hoàn thành đầy đủ các thực nghiệm so sánh E0, E1, E2, E3, E4, E5.
- Thực hiện phân tích lối tắt độ dài và phân tích lỗi định lượng/định tính.
- Toàn bộ quy trình có thể tái lập với `random_seed = 42`.

### 27.2 Phần Mở rộng Tùy chọn (Nice-to-have Extensions - Chỉ làm khi cốt lõi đã hoàn tất)
- Bổ sung mô hình KNN Regression (E-KNN).
- Thử nghiệm mô hình Lai (E6 Hybrid): Kết hợp vector đặc trưng 768 chiều của DeBERTa với 24 đặc trưng ngôn ngữ qua một MLP Regression Head.
- Xây dựng giao diện web demo nhỏ (bằng Streamlit / Gradio) cho phép nhập một đoạn văn bản và hiển thị 6 điểm dự đoán kèm cảnh báo phi thương mại.

---

## 28. Tiêu chí Hoàn thành Dự án (Completion Criteria)

Dự án được nghiệm thu đạt chuẩn khi đáp ứng trọn vẹn các tiêu chuẩn sau:
1. Tập dữ liệu không bị rò rỉ bất kỳ thông tin nào từ các cột phụ (`non_fluency_reason`).
2. Mọi phép xử lý thống kê đều nằm trong Pipeline, chỉ fit trên tập Train.
3. Tập Test chỉ được nạp vào tính toán sau khi các mô hình đã huấn luyện xong.
4. Cả mô hình truyền thống và mô hình Transformer đều được so sánh trên cùng một tập Test với độ đo MCRMSE chuẩn xác.
5. Câu hỏi về lối tắt độ dài văn bản được trả lời tường minh bằng số liệu thực nghiệm.
6. Các ca lỗi lớn nhất được giải thích thấu đáo, có căn cứ ngôn ngữ học.
7. Báo cáo bằng tiếng Việt mạch lạc, văn phong khoa học, lập luận logic và trung thực.

---

## 29. Sơ đồ Logic Cốt lõi của Dự án (Final Project Logic Flow)

```text
Vấn đề nghiên cứu: Dự đoán điểm bài viết học viên tiếng Anh
                           │
                           ▼
Cổng dữ liệu: Dataset Kaggle ELLIPSE (Loại bỏ cột rò rỉ non_fluency_reason)
                           │
                           ▼
Kiểm toán dữ liệu & Phân tích phân phối token (Phân vị percentiles)
                           │
                           ▼
Phân chia dữ liệu chuẩn 70% Train / 15% Val / 15% Test (Stratified bằng score_bin)
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
Trích xuất đặc trưng ngôn ngữ     Tokenization & Chunking (512/128)
(24-30 đặc trưng: S, L, Y, R)     (DeBERTa-v3-small Backbone)
             │                           │
Pipeline: StandardScaler & Impute Dropout & Linear Regression Head (768 -> 6)
             │                           │
Huấn luyện Ridge & Decision Tree  Fine-tune DeBERTa (MCRMSE monitoring, early stop)
             │                           │
             └─────────────┬─────────────┘
                           ▼
Chuẩn hóa target y_norm = (y-1)/4 -> Khôi phục y_pred & Clip [1.0, 5.0]
                           │
                           ▼
Đánh giá duy nhất trên Held-out Test Set (Metric chính: MCRMSE)
                           │
                           ▼
Thực nghiệm đối chứng E0 -> E5 (So sánh mô hình & Bóc tách nhóm đặc trưng)
                           │
                           ▼
Phân tích lối tắt độ dài văn bản (Shortcut Analysis) & Phân tích lỗi (Error Analysis)
                           │
                           ▼
Báo cáo học thuật toàn diện & Bảo vệ vấn đáp phản biện
```

### Công thức ngắn gọn ghi nhớ triết lý dự án:
> **Dữ liệu sạch không rò rỉ $\to$ 6 Target nguyên bản $\to$ Phân tầng 70/15/15 $\to$ So sánh Ridge/Tree vs. DeBERTa $\to$ Tối ưu bằng MCRMSE $\to$ Đánh giá Test 1 lần $\to$ Phân tích lối tắt và lỗi sâu sắc.**

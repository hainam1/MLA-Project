# Danh sách Nhiệm vụ Dự án (Project Task List)

## Dự đoán Điểm Đánh giá Bài viết Tiếng Anh của Người học: So sánh các Đặc trưng Ngôn ngữ Dễ giải thích và Mô hình Pretrained Transformer
### (Predicting Human-Rated English Learner Writing Scores: Interpretable Linguistic Features versus a Pretrained Transformer)

> **ARCHIVED — KHÔNG PHẢI BACKLOG HIỆN HÀNH (2026-09-23).** Danh sách này thuộc
> phương án 6 target/DeBERTa/MCRMSE cũ. Không tiếp tục thực hiện các task bên dưới.
> Backlog mới phải được sinh từ protocol hai target Ridge/Random Forest trong
> `docs/phase1_problem_definition.md`.

Tài liệu này chuyển hóa toàn bộ kế hoạch dự án đã được phê duyệt thành cấu trúc phân rã công việc (Work Breakdown Structure - WBS) có thể thực thi chi tiết từ giai đoạn khởi tạo cho đến khi nộp báo cáo và bảo vệ vấn đáp trước hội đồng.

---

## 1. Hướng dẫn Sử dụng Danh sách Nhiệm vụ

### Quy ước Trạng thái (Status notation)
- `[ ]` Chưa bắt đầu (Not started)
- `[-]` Đang thực hiện (In progress)
- `[x]` Đã hoàn thành (Completed)
- `[!]` Bị nghẽn / Cần tháo gỡ (Blocked)
- `[~]` Đưa ra khỏi phạm vi kèm lý do minh bạch (Removed from scope)

### Quy ước Mức độ Ưu tiên (Priority notation)
- **P0 — Bắt buộc (Required):** Điều kiện tiên quyết để dự án được công nhận hợp lệ và đạt chuẩn.
- **P1 — Khuyến nghị (Recommended):** Nâng cao đáng kể chất lượng phân tích khoa học và chất lượng bảo vệ.
- **P2 — Tùy chọn (Optional):** Chỉ thực hiện sau khi tất cả các nhiệm vụ P0 đã hoàn thành hoàn hảo và còn dư thời gian.

### Quy ước Sự phụ thuộc (Dependency notation)
- `—`: Không yêu cầu nhiệm vụ trước đó, có thể làm ngay.
- `Txxx`: Bắt buộc phải hoàn thành nhiệm vụ mã hiệu `Txxx` trước.
- `Phase n`: Phải vượt qua cổng đánh giá (Gate) của Giai đoạn `n` trước khi bắt đầu.
- `Conditional`: Nhiệm vụ có điều kiện, chỉ thực hiện khi dữ liệu đáp ứng đầy đủ siêu dữ liệu.

### Định nghĩa Hoàn thành một Nhiệm vụ (Definition of Complete)
Một nhiệm vụ chỉ được đánh dấu là hoàn thành (`[x]`) khi thỏa mãn đồng thời:
1. Sản phẩm đầu ra (output) của nhiệm vụ đã tồn tại thực tế (file mã nguồn, dữ liệu, bảng biểu, biểu đồ).
2. Kết quả đầu ra đã được kiểm thử, xác minh tính đúng đắn.
3. Mọi quyết định kỹ thuật liên quan đã được ghi chép vào nhật ký quyết định (decision log).
4. Mã nguồn hoặc quy trình phân tích hoàn toàn có thể tái lập được.
5. Không có lỗi kỹ thuật hoặc vấn đề P0 nào bị che giấu.

---

## 2. Đường Găng Dự án (Critical Path)

Quy trình dự án tuân thủ nghiêm ngặt chuỗi mắt xích phụ thuộc không thể nhảy cóc hoặc đảo lộn sau:

```text
Đóng băng định nghĩa bài toán, 6 Target và Phạm vi
                     ↓
Tiếp nhận chính thức Dataset ELLIPSE (Kaggle) & Loại bỏ cột rò rỉ
                     ↓
Kiểm toán dữ liệu, phân phối điểm và độ dài token DeBERTa
                     ↓
Thiết lập phân vùng 70/15/15 Stratified an toàn chống rò rỉ
                     ↓
Cài đặt & Thẩm định 24-30 đặc trưng ngôn ngữ dễ giải thích
                     ↓
Xây dựng pipeline Baseline, Ridge, Cây quyết định & DeBERTa-v3-small
                     ↓
Tối ưu siêu tham số trên tập Train/Val (Giám sát MCRMSE, Early Stopping)
                     ↓
Đóng băng toàn bộ mã nguồn, trọng số và quyết định thực nghiệm
                     ↓
Đánh giá duy nhất 1 lần trên Held-out Test Set (Tính MCRMSE và MAE)
                     ↓
Phân tích lối tắt độ dài (Shortcut), phân tích mô hình và phân tích lỗi
                     ↓
Viết báo cáo học thuật hoàn chỉnh và luyện tập bảo vệ vấn đáp
                     ↓
Kiểm toán tính tái lập kỹ thuật cuối cùng trước khi nộp
```

---

# Giai đoạn 0 — Khởi tạo Dự án và Đóng băng Phạm vi (Phase 0)

## Mục tiêu
Xác lập chính xác những gì dự án sẽ làm và không làm trước khi nạp dữ liệu hoặc viết mã mô hình.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T001 | P0 | Tạo thư mục gốc dự án và khởi tạo hệ thống quản lý phiên bản Git. | — |
| T002 | P0 | Cập nhật tiêu đề dự án chính thức (song ngữ Việt - Anh) vào `README.md`. | T001 |
| T003 | P0 | Viết định nghĩa bài toán trong 1 câu: Bài luận $\to$ So sánh Đặc trưng Ngôn ngữ & DeBERTa $\to$ Vector 6 điểm số do con người chấm. | T002 |
| T004 | P0 | Ghi nhận lĩnh vực ứng dụng: Hỗ trợ học ngôn ngữ / Xử lý ngôn ngữ tự nhiên (NLP). | T002 |
| T005 | P0 | Xác định nhiệm vụ học máy là Hồi quy đa đầu ra có giám sát (Multi-output Regression). | T003 |
| T006 | P0 | Ghi nhận 4 câu hỏi nghiên cứu cốt lõi (RQ1: So sánh mô hình; RQ2: Đóng góp đặc trưng; RQ3: Lỗi & Lối tắt; RQ4: Khả năng kết hợp/tổng quát hóa). | T003 |
| T007 | P0 | Tuyên bố rõ ràng: Target là điểm bài luận cụ thể theo rubric, không đại diện cho năng lực tiếng Anh tổng quát. | T003 |
| T008 | P0 | Chốt 4 họ mô hình chính: Mean Baseline, Ridge Regression, Decision Tree Regression, và Pretrained Transformer (`microsoft/deberta-v3-small`). | T005 |
| T009 | P0 | Chốt 3 điều kiện đặc trưng: Surface-only, Linguistic-only, và All Features. | T006 |
| T010 | P0 | Ghi rõ các nội dung loại trừ: Không sửa lỗi ngữ pháp, không sinh văn bản, không chấm điểm zero-shot LLM, không dùng model pre-fine-tuned trôi nổi. | T003 |
| T011 | P0 | Định nghĩa Metric chính là **MCRMSE**; Metric bổ sung là MAE từng target, Mean MAE, RMSE từng target, $R^2$ từng target. | T005 |
| T012 | P1 | Tạo biểu mẫu nhật ký quyết định (`docs/decision_log.md`) ghi nhận ngày, quyết định, phương án thay thế, lý do và hệ quả. | T001 |
| T013 | P1 | Tạo sổ đăng ký rủi ro (`docs/risk_register.md`) cho rủi ro rò rỉ dữ liệu, lỗi parser ngôn ngữ, giới hạn GPU và tài nguyên tính toán. | T001 |
| T014 | P0 | Cập nhật danh sách nhiệm vụ và duy trì trạng thái sau mỗi phiên làm việc. | T001 |

### Sản phẩm đầu ra Giai đoạn 0
- Cấu trúc khung repository Git sạch sẽ.
- Tệp `README.md` khởi tạo với phát biểu bài toán rõ ràng.
- Bảng câu hỏi nghiên cứu và phạm vi đã đóng băng.
- Danh mục metric và quyết định các họ mô hình.
- Sổ nhật ký quyết định và sổ đăng ký rủi ro.

### Cổng đánh giá Giai đoạn 0 (Gate 0)
Chỉ chuyển sang Giai đoạn 1 khi có thể trình bày lưu loát đầu vào, 6 đầu ra, bài toán học máy, phạm vi và thiết kế thực nghiệm trong vòng 2 phút mà không có điểm mâu thuẫn nào.

---

# Giai đoạn 1 — Thẩm định và Tiếp nhận Dataset ELLIPSE (Phase 1)

## Mục tiêu
Tiếp nhận chính thức bộ dữ liệu chuẩn mực ELLIPSE từ Kaggle, xác thực 6 target và thiết lập rào chắn loại bỏ hoàn toàn các cột rò rỉ nhãn.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T015 | P0 | Thiết lập bảng kiểm định tiếp nhận dữ liệu (Dataset acceptance checklist) trước khi tải. | Phase 0 |
| T016 | P0 | Xác nhận các trường bắt buộc: `text_id`, `full_text` và 6 target: `cohesion`, `syntax`, `vocabulary`, `phraseology`, `grammar`, `conventions`. | T015 |
| T017 | P0 | Nhận diện các trường phụ gây nguy cơ rò rỉ target trong mirror: `mss`, `response_fluency`, `non_fluency_reason`. | T015 |
| T018 | P0 | Thiết lập quy định loại bỏ vĩnh viễn `non_fluency_reason` và các cột phụ ngay tại bước nạp dữ liệu ban đầu. | T017 |
| T019 | P0 | Ghi nhận URL chính thức trên Kaggle và bản mirror trên Hugging Face kèm trích dẫn khoa học chuẩn. | T016 |
| T020 | P0 | Ghi nhận giấy phép sử dụng dữ liệu mở cho mục đích nghiên cứu học thuật của cuộc thi Feedback Prize ELL. | T019 |
| T021 | P0 | Xác thực văn bản là bài viết xác thực của người học tiếng Anh (lớp 8–12), không phải văn bản nhân tạo. | T016 |
| T022 | P0 | Xác thực điểm số được chấm bởi hội đồng chuyên gia khảo thí con người theo khung rubric chuẩn. | T016 |
| T023 | P0 | Lưu trữ và đọc kỹ bản mô tả tiêu chí rubric của 6 kỹ năng (thang 1.0 đến 5.0, bước 0.5). | T022 |
| T024 | P0 | Xác nhận ý nghĩa của khoảng cách 0.5 và 1.0 điểm trên thang điểm đo lường liên tục. | T023 |
| T025 | P0 | Kiểm tra để bảo đảm 6 điểm số không bị tính toán một cách nhân tạo từ bất kỳ biến đặc trưng nào sắp trích xuất. | T022 |
| T026 | P0 | Thống kê sơ bộ tổng số mẫu: khoảng 3.911 bài viết. | T016 |
| T027 | P0 | Kiểm tra xem có trường `learner_id` trong dữ liệu không; xác nhận ẩn danh và không có nhãn người học. | T026 |
| T028 | P0 | Kiểm tra sự hiện diện của nhãn đề tài (`prompt_id`); xác nhận dữ liệu train không phân tách prompt rõ ràng. | T026 |
| T029 | P0 | Kiểm tra điểm số của từng giám khảo độc lập (chỉ có điểm tổng hợp cuối cùng sau hòa giải). | T026 |
| T030 | P0 | Kiểm tra sơ bộ độ bao phủ điểm số ở dải thấp (1.0–2.0), trung bình (2.5–3.5) và cao (4.0–5.0). | T026 |
| T031 | P0 | Xác nhận dữ liệu đã được ẩn danh hóa toàn bộ, không chứa thông tin định danh cá nhân (PII). | T016 |
| T032 | P0 | Lập luận khoa học vì sao KHÔNG dùng model essay-scoring fine-tuned sẵn của bên thứ ba trên Hugging Face. | T020 |
| T033 | P0 | Phê duyệt chính thức lựa chọn dataset ELLIPSE / Feedback Prize ELL. | T015–T032 |
| T034 | P0 | Khẳng định tính hợp lệ của bài toán Hồi quy đa biến trên thang điểm 1.0–5.0 bước 0.5. | T024, T033 |
| T035 | P0 | Tiếp nhận file `ELLIPSE_Final_github_train.csv` và lưu trong `data/01_original_source/official_corpus/`. | T033 |
| T036 | P0 | Tạo bản sao thô bất biến (read-only raw copy) và ghi lại mã băm kiểm tra (SHA256 checksum). | T035 |
| T037 | P0 | Viết `data/README.md` mô tả nguồn gốc, trích dẫn, giấy phép và điều kiện bảo mật dữ liệu. | T036 |
| T038 | P0 | Lập từ điển dữ liệu (`docs/data_card.md`) mô tả chi tiết từng cột trong file nguồn chính thức. | T036 |
| T039 | P1 | Ghi nhận quyết định lựa chọn dữ liệu và loại bỏ cột rò rỉ vào `docs/decision_log.md`. | T033 |
| T040 | P0 | Bổ sung quy tắc loại bỏ cột rò rỉ vào hàm nạp dữ liệu tự động. | T018, T038 |

### Sản phẩm đầu ra Giai đoạn 1
- Dữ liệu thô an toàn trong `data/01_original_source/` kèm mã băm SHA256.
- Tài liệu Data Card (`docs/data_card.md`) và `data/README.md`.
- Báo cáo thẩm định dữ liệu và quyết định loại bỏ cột gây rò rỉ target.
- Cơ sở học thuật bảo vệ quyết định fine-tune từ model gốc `microsoft/deberta-v3-small`.

### Cổng đánh giá Giai đoạn 1 (Gate 1)
Tuyệt đối không bước sang giai đoạn tiếp theo nếu chưa loại bỏ hoàn toàn `non_fluency_reason` và chưa nắm rõ ý nghĩa định lượng của 6 tiêu chí điểm.

---

# Giai đoạn 2 — Thiết lập Môi trường và Tính Tái lập (Phase 2)

## Mục tiêu
Xây dựng nền tảng kỹ thuật chuẩn mực, hỗ trợ cả scikit-learn, spaCy và Hugging Face Transformers trên môi trường tính toán GPU.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T041 | P0 | Khởi tạo cấu trúc dữ liệu đánh số `01_original_source` đến `05_model_features`, cùng `src`, `notebooks`, `tests`, `configs`, `outputs`, `report`. | Phase 1 |
| T042 | P0 | Cấu hình `.gitignore` loại trừ dữ liệu thô lớn, checkpoint mô hình PyTorch (`*.bin`, `*.safetensors`), tệp tạm thời và virtualenv. | T041 |
| T043 | P0 | Tạo và kích hoạt môi trường ảo Python 3.10+ chuyên dụng. | T041 |
| T044 | P0 | Cài đặt các thư viện cốt lõi: `torch`, `transformers`, `accelerate`, `scikit-learn`, `spacy`, `textstat`, `pandas`, `numpy`, `matplotlib`, `seaborn`. | T043 |
| T045 | P0 | Tải mô hình ngôn ngữ tiếng Anh chuẩn của spaCy: `python -m spacy download en_core_web_sm`. | T044 |
| T046 | P0 | Khóa phiên bản phụ thuộc chính xác trong `requirements.txt` và kiểm tra tương thích CUDA. | T044 |
| T047 | P0 | Thiết lập biến cấu hình hạt giống ngẫu nhiên toàn cục `random_seed = 42`. | T041 |
| T048 | P0 | Cập nhật `configs/experiment.yaml` chứa đường dẫn, seed, danh sách 6 target, cấu hình DeBERTa và siêu tham số mô hình. | T046, T047 |
| T049 | P0 | Viết module nạp dữ liệu `src/data.py` tự động loại bỏ các cột rò rỉ `DROP_COLUMNS = ["mss", "response_fluency", "non_fluency_reason"]`. | T048 |
| T050 | P0 | Cài đặt kiểm tra schema dữ liệu: đủ 6 cột target, đúng kiểu dữ liệu, không có giá trị vô lý. | T049 |
| T051 | P1 | Cấu hình công cụ kiểm tra chất lượng mã nguồn (flake8 / black). | T043 |
| T052 | P1 | Viết bài kiểm thử khói (smoke test) kiểm tra nạp dữ liệu và kiểm tra GPU trong `tests/`. | T049 |
| T053 | P0 | Cập nhật hướng dẫn cài đặt môi trường và chạy thử nghiệm vào `README.md`. | T046, T052 |
| T054 | P0 | Tạo commit Git đầu tiên đánh dấu môi trường đã sẵn sàng hoạt động. | T041–T053 |

### Sản phẩm đầu ra Giai đoạn 2
- Môi trường thực thi đầy đủ scikit-learn và Hugging Face Transformers.
- Cấu hình tập trung `configs/experiment.yaml`.
- Module `src/data.py` nạp dữ liệu sạch và bài kiểm thử khói passed.
- Tệp `requirements.txt` cố định phiên bản.

### Cổng đánh giá Giai đoạn 2 (Gate 2)
Một thành viên khác có thể clone repository, tạo môi trường, chạy `pytest tests/` và nạp thành công dữ liệu mà không phát sinh bất kỳ lỗi nào.

---

# Giai đoạn 3 — Kiểm toán Dữ liệu và Làm sạch Văn bản (Phase 3)

## Mục tiêu
Phát hiện các bất thường về dữ liệu, bảo toàn văn bản lỗi tự nhiên của học sinh và tạo tệp dữ liệu trung gian chuẩn xác.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T055 | P0 | Nạp toàn bộ dữ liệu thô qua hàm nạp `src/data.py`. | Phase 2 |
| T056 | P0 | Đối chiếu số lượng hàng (khoảng 3.911 bài) và các cột với tài liệu chính thức Kaggle. | T055 |
| T057 | P0 | Kiểm tra tính duy nhất của trường định danh `text_id`. | T055 |
| T058 | P0 | Kiểm tra giá trị khuyết thiếu (NaN/Null) trên cả cột văn bản `full_text` và 6 cột target. | T055 |
| T059 | P0 | Xác thực miền giá trị của 6 target: mọi điểm phải nằm trong $[1.0, 5.0]$ và là bội số của 0.5. | T055 |
| T060 | P0 | Phát hiện văn bản rỗng, văn bản chỉ có ký tự trắng hoặc quá ngắn ($< 15$ từ). | T055 |
| T061 | P0 | Phát hiện bài viết trùng lặp hoàn toàn nội dung văn bản (Exact duplicates). | T055 |
| T062 | P1 | Kiểm tra các bài viết gần trùng lặp (Near duplicates) bằng phương pháp độ tương đồng n-gram/TF-IDF. | T061 |
| T063 | P0 | Xử lý các bài viết trùng lặp: loại bỏ bản sao thừa, giữ lại một bản duy nhất trước khi phân chia tập dữ liệu. | T061, T062 |
| T064 | P0 | Kiểm tra các ký tự điều khiển lạ, mã HTML rác, lỗi mã hóa UTF-8 trong văn bản. | T055 |
| T065 | P0 | Khảo sát độ dài văn bản ngắn nhất và dài nhất (tính theo số từ và số ký tự). | T055 |
| T066 | P0 | Thiết lập nguyên tắc bất biến: Giữ nguyên lỗi ngữ pháp, chính tả, lỗi chấm câu của người học; không sửa lỗi bằng phần mềm. | T055 |
| T067 | P0 | Xây dựng quy trình làm sạch kỹ thuật: loại bỏ ký tự trắng thừa, chuẩn hóa ngắt dòng, lưu vào `src/data.py`. | T064, T066 |
| T068 | P0 | Lưu nhật ký các mẫu bị loại trừ kèm mã lý do (exclusion log). | T063, T067 |
| T069 | P0 | Xuất tệp dữ liệu sạch trung gian `data/03_clean_ready_to_use/full_clean_corpus_6482.csv`. | T067 |
| T070 | P0 | Kiểm tra lại schema và miền giá trị trên file `data/03_clean_ready_to_use/full_clean_corpus_6482.csv`. | T069 |
| T071 | P0 | Lập bảng kiểm toán dữ liệu (Data audit table) hiển thị số lượng mẫu trước và sau khi làm sạch. | T068, T070 |
| T072 | P1 | Kiểm tra ngẫu nhiên bằng mắt 20 bài viết giữ lại và các bài bị loại để bảo đảm tính hợp lý. | T069 |
| T073 | P0 | Ghi nhận các hạn chế về chất lượng dữ liệu vào `docs/risk_register.md`. | T071 |
| T074 | P0 | Thêm bài kiểm thử tự động kiểm tra tính toàn vẹn của dữ liệu interim vào `tests/test_data.py`. | T069 |

### Sản phẩm đầu ra Giai đoạn 3
- Tệp dữ liệu trung gian sạch `data/03_clean_ready_to_use/full_clean_corpus_6482.csv`.
- Bảng thống kê kiểm toán dữ liệu trước và sau làm sạch.
- Quy tắc làm sạch bảo toàn lỗi ngôn ngữ nguyên bản của học sinh.

### Cổng đánh giá Giai đoạn 3 (Gate 3)
Mọi mẫu bị loại bỏ đều có lý do kỹ thuật rõ ràng; văn bản bài luận của học sinh được giữ nguyên vẹn để phản ánh chân thực năng lực viết.

---

# Giai đoạn 4 — Phân tích Dữ liệu Khám phá và Kiểm toán Token (Phase 4)

## Mục tiêu
Khám phá phân phối điểm số 6 tiêu chí, khảo sát tương quan và kiểm toán phân phối độ dài token DeBERTa để đưa ra quyết định xử lý văn bản dài.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T075 | P0 | Tạo notebook `notebooks/01_data_audit_eda.ipynb`. | Phase 3 |
| T076 | P0 | Tính toán thống kê mô tả (Mean, Std, Median, Min, Max, Skewness) cho cả 6 tiêu chí điểm. | T075 |
| T077 | P0 | Vẽ biểu đồ phân phối điểm số (Histogram & KDE) cho từng tiêu chí trong 6 tiêu chí. | T076 |
| T078 | P0 | Tính toán và trực quan hóa ma trận tương quan Pearson giữa 6 tiêu chí chấm điểm. | T076 |
| T079 | P0 | Nhận diện hiện tượng phân phối tập trung dày đặc ở dải trung bình ($2.5 - 3.5$) và thưa thớt ở 2 đầu ($< 2.0$ và $> 4.5$). | T077 |
| T080 | P0 | Khởi tạo tokenizer của `microsoft/deberta-v3-small` để đo độ dài token trên toàn bộ tập dữ liệu. | T075 |
| T081 | P0 | Tính toán độ dài token DeBERTa cho từng bài viết: `len(tokenizer(text)["input_ids"])`. | T080 |
| T082 | P0 | Báo cáo các phân vị độ dài token: percentiles 50%, 75%, 90%, 95%, 99% và Max. | T081 |
| T083 | P0 | Quyết định chiến lược văn bản dài: Nếu $\le 512$ chiếm đa số thì dùng Truncation; nếu nhiều bài $> 512$ thì áp dụng Chunking 512/128 + Mean pooling. | T082 |
| T084 | P0 | Vẽ biểu đồ tương quan giữa độ dài bài viết (số từ / số token) với từng tiêu chí điểm. | T076, T081 |
| T085 | P0 | Đánh giá sơ bộ nguy cơ lối tắt độ dài (đo lường hệ số tương quan giữa word count và điểm số). | T084 |
| T086 | P1 | Kiểm tra các trường hợp bài viết ngắn nhưng điểm cao và bài viết dài nhưng điểm thấp. | T084 |
| T087 | P0 | Lưu các biểu đồ phân phối và tương quan chuẩn xuất bản vào `outputs/figures/`. | T077, T078, T084 |
| T088 | P0 | Viết tóm tắt báo cáo phân tích EDA và quyết định cấu hình token DeBERTa vào `notebooks/01_data_audit_eda.ipynb`. | T082, T085 |

### Sản phẩm đầu ra Giai đoạn 4
- Báo cáo phân vị độ dài token DeBERTa (50%, 75%, 90%, 95%, 99%).
- Quyết định xử lý văn bản dài (Truncation hoặc Chunking 512/128 + Mean pooling).
- Hệ thống đồ thị phân phối điểm 6 tiêu chí và ma trận tương quan giữa các nhãn.
- Đánh giá sơ bộ về tương quan độ dài văn bản với điểm số.

### Cổng đánh giá Giai đoạn 4 (Gate 4)
Đã nắm chắc phân bố điểm 6 tiêu chí và phân vị độ dài token để thiết lập đúng đắn chiến lược phân tầng dữ liệu và cấu hình tokenizer cho DeBERTa.

---

# Giai đoạn 5 — Thiết kế Phân tầng 70/15/15 và Chống Rò rỉ (Phase 5)

## Mục tiêu
Tạo phân vùng dữ liệu Train 70%, Validation 15%, Test 15% phân tầng xấp xỉ theo phân vị điểm số, đảm bảo tuyệt đối không rò rỉ thông tin.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T089 | P0 | Xác nhận không có `learner_id` trong dữ liệu; loại trừ phương án phân chia GroupKFold theo người học. | Phase 4 |
| T090 | P0 | Chốt tỷ lệ phân chia: **70% Train (~2.737 bài), 15% Validation (~587 bài), 15% Test (~587 bài)**. | T089 |
| T091 | P0 | Tính điểm trung bình 6 tiêu chí: `df["mean_score"] = df[TARGET_COLUMNS].mean(axis=1)`. | T090 |
| T092 | P0 | Tạo 10 phân vị điểm: `df["score_bin"] = pd.qcut(df["mean_score"], q=10, labels=False, duplicates="drop")`. | T091 |
| T093 | P0 | Thực hiện Stratified Split dựa trên cột `score_bin` với `random_state = 42` thành tập Train/Val/Test. | T092 |
| T094 | P0 | Viết logic phân chia vào module `src/split.py`. | T093 |
| T095 | P0 | Kiểm tra không có sự trùng lặp mẫu giữa 3 tập (`len(set(train_ids) & set(test_ids)) == 0`). | T094 |
| T096 | P0 | Đối chiếu phân phối điểm số và độ lệch chuẩn giữa tập Train, Validation và Test để đảm bảo tương đồng. | T095 |
| T097 | P0 | Xuất `data/02_split_manifest/essay_split_manifest.csv` chứa `essay_id` và nhãn phân vùng. | T095 |
| T098 | P0 | Thiết lập 5-fold cross-validation trên tập Train (hoặc Train+Val khi cần so sánh classical CV) phân tầng theo `score_bin`. | T097 |
| T099 | P0 | Viết bài kiểm thử tự động kiểm tra tính không giao nhau của các tập phân chia trong `tests/test_splits.py`. | T097 |
| T100 | P0 | Khóa cứng tập Test: Tuyệt đối không sử dụng tập Test cho việc chọn đặc trưng, fit scaler hay tối ưu siêu tham số. | T097 |
| T101 | P0 | Lập báo cáo phân chia dữ liệu (`outputs/tables/split_summary.csv`) ghi rõ số lượng, tỷ lệ và phân phối điểm. | T096, T097 |

### Sản phẩm đầu ra Giai đoạn 5
- Tệp định danh cố định `data/02_split_manifest/essay_split_manifest.csv`.
- Module phân chia dữ liệu tái lập `src/split.py`.
- Bài kiểm thử không giao thoa dữ liệu `tests/test_splits.py` passed.
- Cơ chế rào chắn tập Test được xác lập và kích hoạt.

### Cổng đánh giá Giai đoạn 5 (Gate 5)
Tập Test được đóng băng hoàn toàn; phân phối điểm trên 3 tập tương đồng nhau qua kiểm định phân tầng `score_bin`.

---

# Giai đoạn 6 — Triển khai Trích xuất Đặc trưng Ngôn ngữ (Phase 6)

## Mục tiêu
Xây dựng và kiểm định chất lượng bộ 24–30 đặc trưng ngôn ngữ dễ giải thích thuộc 4 nhóm (Bề mặt, Từ vựng, Cú pháp, Độ dễ đọc).

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T102 | P0 | Lập danh mục chi tiết 24–30 đặc trưng ngôn ngữ vào `src/features.py` kèm định nghĩa và công thức tính. | Phase 5 |
| T103 | P0 | Cài đặt Nhóm S (Bề mặt): `word_count`, `sentence_count`, `paragraph_count`, `character_count`, `mean_word_length`, `mean_sentence_length`. | T102 |
| T104 | P0 | Cài đặt Nhóm L (Từ vựng): `ttr`, `root_ttr`, `mtld` (Lexical Diversity), `lexical_density`, `content_word_ratio`. | T102 |
| T105 | P1 | Cài đặt bổ sung Nhóm L: `mean_log_word_frequency` và `rare_word_ratio` dựa trên kho từ vựng tần suất chuẩn. | T104 |
| T106 | P0 | Cài đặt Nhóm Y (Cú pháp qua spaCy): `noun_ratio`, `verb_ratio`, `adjective_ratio`, `adverb_ratio`. | T102 |
| T107 | P1 | Cài đặt bổ sung Nhóm Y: `subordination_ratio`, `mean_dependency_depth`, `mean_dependency_distance`. | T106 |
| T108 | P0 | Cài đặt Nhóm R (Độ dễ đọc qua textstat): `flesch_reading_ease`, `flesch_kincaid_grade`, `gunning_fog`, `automated_readability_index`. | T102 |
| T109 | P0 | Cài đặt cơ chế xử lý ngoại lệ an toàn: nếu văn bản không phân tích cú pháp được, trả về giá trị mặc định hợp lệ. | T103–T108 |
| T110 | P0 | Viết các ca kiểm thử đơn vị (unit tests) trên các câu ngắn kiểm tra thủ công được trong `tests/test_features.py`. | T109 |
| T111 | P0 | Kiểm tra tính tất định: Cùng một bài viết chạy 2 lần phải cho ra vector đặc trưng giống hệt nhau 100%. | T110 |
| T112 | P0 | Kiểm tra thủ công kết quả trích xuất trên 10 bài luận đại diện các mức điểm khác nhau. | T111 |
| T113 | P0 | Đóng băng danh sách đặc trưng chính thức và định nghĩa 3 điều kiện: Surface-only, Linguistic-only, và All Features. | T112 |
| T114 | P0 | Xuất bảng từ điển đặc trưng (`docs/feature_dictionary.md`) ghi rõ tên, nhóm, công thức, công cụ trích xuất và ý nghĩa sư phạm. | T113 |

### Sản phẩm đầu ra Giai đoạn 6
- Module trích xuất đặc trưng `src/features.py` tất định, không lỗi.
- Bộ kiểm thử `tests/test_features.py` bao phủ toàn bộ 4 nhóm đặc trưng.
- Tài liệu từ điển đặc trưng `docs/feature_dictionary.md`.

### Cổng đánh giá Giai đoạn 6 (Gate 6)
Mọi đặc trưng đều được tính toán tất định, kiểm thử độc lập thành công và gán nhãn rõ ràng vào các nhóm S, L, Y, R.

---

# Giai đoạn 7 — Xây dựng Ma trận Đặc trưng và Tiền xử lý (Phase 7)

## Mục tiêu
Trích xuất đặc trưng trên toàn bộ tập dữ liệu, chuẩn hóa target về $[0, 1]$, kiểm tra đa cộng tuyến và lưu trữ ma trận dữ liệu đã xử lý.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T115 | P0 | Tạo notebook `notebooks/02_feature_extraction.ipynb` để chạy trích xuất trên toàn bộ 3.911 bài viết. | Phase 6 |
| T116 | P0 | Lưu trữ `text_id` và 6 cột target bên ngoài ma trận đặc trưng $X$, không để nhãn lọt vào predictors. | T115 |
| T117 | P0 | Kiểm tra giá trị khuyết thiếu (NaN) và vô cực (Inf) trong ma trận đặc trưng $X$. | T116 |
| T118 | P0 | Kiểm tra các đặc trưng có phương sai bằng 0 hoặc gần như hằng số trên tập Train. | T117 |
| T119 | P0 | Tính toán ma trận tương quan giữa các đặc trưng trên tập Train để phát hiện đa cộng tuyến mạnh ($r > 0.90$). | T118 |
| T120 | P0 | Cài đặt hàm chuẩn hóa target về $[0, 1]$: $y_{\text{normalized}} = (y - 1.0) / 4.0$. | T116 |
| T121 | P0 | Cài đặt hàm khôi phục target: $y = y_{\text{normalized}} \times 4.0 + 1.0$ kèm `np.clip(y, 1.0, 5.0)`. | T120 |
| T122 | P0 | Viết kiểm thử bảo đảm việc chuẩn hóa và khôi phục target là phép biến đổi đảo ngược hoàn hảo (`tests/test_data.py`). | T121 |
| T123 | P0 | Xuất tệp ma trận đặc trưng hoàn chỉnh `data/05_model_features/essay_features.csv` kèm thông tin phiên bản. | T119, T120 |
| T124 | P0 | Đồng bộ hóa ID giữa `essay_features.csv`, `essay_split_manifest.csv` và `full_clean_corpus_6482.csv`. | T123 |
| T125 | P0 | Lập báo cáo kiểm định chất lượng đặc trưng (Feature QA summary) lưu vào `outputs/tables/feature_qa.csv`. | T124 |

### Sản phẩm đầu ra Giai đoạn 7
- Ma trận đặc trưng số học `data/05_model_features/essay_features.csv`.
- Các hàm chuẩn hóa và khôi phục target đã được kiểm định.
- Báo cáo kiểm định phương sai và tương quan giữa các đặc trưng.

### Cổng đánh giá Giai đoạn 7 (Gate 7)
Ma trận đặc trưng sạch hoàn toàn (không NaN/Inf, không rò rỉ target), khớp dòng hoàn hảo với file phân chia split.

---

# Giai đoạn 8 — Xây dựng Pipeline Mô hình và Metric MCRMSE (Phase 8)

## Mục tiêu
Cài đặt hàm tính metric MCRMSE, xây dựng scikit-learn Pipeline cho các mô hình truyền thống và thiết lập mã nguồn fine-tuning DeBERTa.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T126 | P0 | Cài đặt hàm tính metric chính **MCRMSE** trong `src/evaluate.py` theo công thức chuẩn của Kaggle. | Phase 7 |
| T127 | P0 | Cài đặt các metric bổ sung trong `src/evaluate.py`: MAE từng cột, Mean MAE, RMSE từng cột, $R^2$ từng cột. | T126 |
| T128 | P0 | Viết unit test cho hàm `mcrmse(y_true, y_pred)` với các vector giả định biết trước kết quả (`tests/test_metrics.py`). | T126 |
| T129 | P0 | Xây dựng mô hình Mean Baseline (luôn dự đoán vector trung bình 6 target của tập Train). | T127 |
| T130 | P0 | Xây dựng Ridge Regression Pipeline trong `src/models.py`: `SimpleImputer(median)` $\to$ `StandardScaler()` $\to$ `Ridge()`. | T127 |
| T131 | P0 | Xây dựng Decision Tree Regression Pipeline trong `src/models.py`: `SimpleImputer(median)` $\to$ `DecisionTreeRegressor()`. | T127 |
| T132 | P1 | Xây dựng KNN Regression Pipeline: `SimpleImputer(median)` $\to$ `StandardScaler()` $\to$ `KNeighborsRegressor()`. | T127 |
| T133 | P0 | Đảm bảo `StandardScaler` và `SimpleImputer` chỉ được `fit()` trên tập Train của từng fold, không fit trên dữ liệu đánh giá. | T130–T132 |
| T134 | P0 | Xây dựng kiến trúc mô hình Deep Learning trong `src/models.py`: `AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-v3-small", num_labels=6, problem_type="regression")`. | T126 |
| T135 | P0 | Cài đặt hàm tính metric MCRMSE tương thích với Hugging Face `Trainer` (`compute_metrics`). | T126, T134 |
| T136 | P0 | Cài đặt cơ chế xử lý độ dài token trong Dataset class PyTorch: Tokenizer padding/truncation ở 512 hoặc Chunking 512/128 + Mean pooling. | T134 |
| T137 | P0 | Chạy thử nghiệm khói (Smoke test run) trên tập Train nhỏ (50 mẫu) cho cả Ridge, Decision Tree và DeBERTa. | T129–T136 |
| T138 | P0 | Sửa toàn bộ lỗi phát sinh từ thử nghiệm khói, đảm bảo luồng tính toán gradient và xuất vector dự đoán 6 chiều trơn tru. | T137 |

### Sản phẩm đầu ra Giai đoạn 8
- Module đánh giá `src/evaluate.py` chứa hàm tính MCRMSE chuẩn xác kèm unit test passed.
- Module `src/models.py` chứa đầy đủ pipeline của Baseline, Ridge, Decision Tree và DeBERTa-v3-small.
- Kết quả chạy thử nghiệm khói thành công trên dữ liệu mẫu.

### Cổng đánh giá Giai đoạn 8 (Gate 8)
Tất cả 4 họ mô hình đều nhận đầu vào hợp lệ và trả về dự đoán 6 chiều, tương thích với hàm tính MCRMSE mà không truy cập vào tập Test.

---

# Giai đoạn 9 — Thực nghiệm Huấn luyện và Tối ưu Mô hình (Phase 9)

## Mục tiêu
Thực hiện các thực nghiệm E0 đến E5 trên tập Train và Validation, tối ưu hóa siêu tham số và đóng băng các mô hình trước khi mở tập Test.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T139 | P0 | Tạo notebook `notebooks/03_classical_models.ipynb` cho các mô hình truyền thống (E0 – E4). | Phase 8 |
| T140 | P0 | **Thực nghiệm E0:** Chạy Mean Baseline trên tập Validation, ghi nhận baseline MCRMSE, MAE, RMSE, $R^2$. | T139 |
| T141 | P0 | **Thực nghiệm E1 (Surface-only):** Huấn luyện Ridge Regression chỉ với nhóm đặc trưng S; ghi nhận Val MCRMSE. | T139 |
| T142 | P0 | **Thực nghiệm E2 (Linguistic-only):** Huấn luyện Ridge Regression chỉ với nhóm đặc trưng L+Y+R; ghi nhận Val MCRMSE. | T139 |
| T143 | P0 | **Thực nghiệm E3 (All Features):** Huấn luyện và tối ưu siêu tham số $\alpha$ của Ridge Regression trên toàn bộ đặc trưng; ghi nhận Val MCRMSE. | T139 |
| T144 | P0 | **Thực nghiệm E4 (Cây quyết định):** Huấn luyện và tinh chỉnh Decision Tree (`max_depth`, `min_samples_leaf`) trên toàn bộ đặc trưng; ghi nhận Val MCRMSE. | T139 |
| T145 | P1 | Chạy thử nghiệm KNN Regression (nếu chọn thực hiện) trên tập All Features, tìm $k$ tối ưu. | T139 |
| T146 | P0 | Lưu bảng so sánh kết quả thực nghiệm trên tập Validation của các mô hình truyền thống. | T140–T145 |
| T147 | P0 | Tạo notebook `notebooks/04_deberta_finetuning.ipynb` dành riêng cho fine-tuning DeBERTa-v3-small trên GPU. | Phase 8 |
| T148 | P0 | Thiết lập `TrainingArguments` cho DeBERTa: lr=2e-5, epochs=5, batch_size=4, grad_accum=4 (effective 16), eval_bs=8, fp16=True, weight_decay=0.01, warmup=0.10. | T147 |
| T149 | P0 | Cấu hình Early Stopping: `early_stopping_patience = 2`, chọn checkpoint có Val MCRMSE nhỏ nhất. | T148 |
| T150 | P0 | **Thực nghiệm E5 (DeBERTa-v3-small):** Tiến hành huấn luyện fine-tuning trên tập Train (70%), đánh giá sau mỗi epoch trên tập Val (15%). | T148, T149 |
| T151 | P0 | Theo dõi đồ thị Training Loss và Validation MCRMSE qua từng epoch để kiểm soát overfitting. | T150 |
| T152 | P0 | Nạp lại checkpoint tốt nhất của DeBERTa sau khi kết thúc huấn luyện. | T150 |
| T153 | P1 | **Thực nghiệm E6 (Tùy chọn - Hybrid Model):** Trích xuất biểu diễn 768 chiều từ DeBERTa kết hợp đặc trưng ngôn ngữ đưa vào Ridge/MLP. | T152 |
| T154 | P0 | Lập bảng so sánh tổng hợp Validation MCRMSE giữa Baseline, Ridge, Decision Tree và DeBERTa. | T146, T152 |
| T155 | P0 | Ghi nhận chi tiết các cấu hình siêu tham số tối ưu vào nhật ký quyết định `docs/decision_log.md`. | T154 |
| T156 | P0 | **ĐÓNG BĂNG (FREEZE):** Đóng băng toàn bộ mã nguồn, checkpoint mô hình, siêu tham số và pipeline trước khi đánh giá tập Test. | T155 |
| T157 | P0 | Tạo checkpoint commit Git đánh dấu trạng thái tiền kiểm thử (Pre-test frozen state). | T156 |

### Sản phẩm đầu ra Giai đoạn 9
- Checkpoint DeBERTa-v3-small tốt nhất lưu tại `outputs/models/deberta_best/`.
- File mô hình Ridge và Decision Tree tối ưu lưu tại `outputs/models/`.
- Bảng kết quả thực nghiệm E0 đến E5 trên tập Validation.
- Commit Git đóng băng toàn bộ cấu hình trước khi mở tập Test.

### Cổng đánh giá Giai đoạn 9 (Gate 9)
Tất cả các mô hình đã được huấn luyện xong, siêu tham số đã được cố định hoàn toàn; tuyệt đối không thay đổi mã nguồn sau khi xem kết quả tập Test.

---

# Giai đoạn 10 — Đánh giá Chốt trên Held-out Test Set (Phase 10)

## Mục tiêu
Đánh giá duy nhất một lần toàn bộ các mô hình trên tập Test độc lập (15%), xuất bảng kết quả thực tế không thiên lệch.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T158 | P0 | Nạp tệp cấu hình và mã nguồn đã đóng băng tại Gate 9. | Phase 9 |
| T159 | P0 | Nạp ID tập test độc lập từ `data/02_split_manifest/essay_split_manifest.csv`. | T158 |
| T160 | P0 | Chạy Mean Baseline trên tập Test; tính MCRMSE, MAE, RMSE, $R^2$. | T159 |
| T161 | P0 | Chạy Ridge Regression trên tập Test; tính MCRMSE, MAE, RMSE, $R^2$ cho cả 6 tiêu chí. | T159 |
| T162 | P0 | Chạy Decision Tree Regression trên tập Test; tính MCRMSE, MAE, RMSE, $R^2$ cho cả 6 tiêu chí. | T159 |
| T163 | P0 | Chạy Pretrained DeBERTa-v3-small trên tập Test; tính MCRMSE, MAE, RMSE, $R^2$ cho cả 6 tiêu chí. | T159 |
| T164 | P1 | Chạy mô hình Hybrid E6 (nếu có) trên tập Test. | T159, T153 |
| T165 | P0 | Xuất file dự đoán chi tiết `outputs/predictions/predictions_test.csv` gồm: `text_id`, 6 giá trị nhãn thực tế, 6 giá trị dự đoán của từng mô hình và các phần dư tương ứng. | T160–T164 |
| T166 | P0 | Kiểm tra bảo đảm mọi bài viết trong tập Test đều có đúng một bộ dự đoán hợp lệ, không có giá trị khuyết. | T165 |
| T167 | P0 | Lập Bảng Kết quả Chính thức (Main Results Table) so sánh các mô hình trên tập Test và lưu vào `outputs/tables/test_results_main.csv`. | T165 |
| T168 | P0 | Lập Bảng Chi tiết từng Tiêu chí (Per-target Metrics Table) trên tập Test và lưu vào `outputs/tables/test_results_per_target.csv`. | T165 |
| T169 | P1 | Tính khoảng tin cậy Bootstrap 95% cho MCRMSE và MAE của mô hình tốt nhất nếu điều kiện thống kê cho phép. | T165 |
| T170 | P0 | So sánh thứ hạng mô hình trên tập Test với thứ hạng trên tập Validation để đánh giá mức độ ổn định. | T167 |
| T171 | P0 | Khóa cứng và lưu trữ vĩnh viễn tệp dự đoán `predictions_test.csv` và các bảng kết quả. | T165, T167 |

### Sản phẩm đầu ra Giai đoạn 10
- Tệp dự đoán chi tiết `outputs/predictions/predictions_test.csv`.
- Bảng kết quả chính thức trên tập Test (`test_results_main.csv` và `test_results_per_target.csv`).
- Minh chứng thực nghiệm trả lời câu hỏi RQ1.

### Cổng đánh giá Giai đoạn 10 (Gate 10)
Kết quả kiểm thử tập Test được lưu lại nguyên bản; tuyệt đối không điều chỉnh lại mô hình hay sửa đổi tham số để làm đẹp số liệu.

---

# Giai đoạn 11 — Diễn giải Mô hình, Lối tắt và Phân tích Lỗi (Phase 11)

## Mục tiêu
Phân tích cơ chế hoạt động của mô hình, giải quyết triệt để nghi vấn về lối tắt độ dài và đào sâu phân tích nguyên nhân các ca dự đoán sai lệch lớn.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T172 | P0 | Tạo notebook `notebooks/05_error_shortcut_analysis.ipynb`. | Phase 10 |
| T173 | P0 | **Phân tích RQ2 & Shortcut:** So sánh Test MCRMSE giữa E1 (Surface-only), E2 (Linguistic-only) và E3 (All Features). | T172 |
| T174 | P0 | Đánh giá mức độ phụ thuộc vào độ dài: Xác định xem đặc trưng từ vựng, cú pháp có thực sự mang lại giá trị độc lập hay độ dài chiếm ưu thế. | T173 |
| T175 | P0 | Vẽ biểu đồ tương quan giữa phần dư dự đoán ($y - \hat{y}$) với độ dài văn bản của Ridge và DeBERTa. | T172 |
| T176 | P0 | **Diễn giải Ridge:** Trích xuất trọng số chuẩn hóa của Ridge; vẽ biểu đồ Top 5 đặc trưng tác động mạnh nhất lên từng tiêu chí điểm. | T172 |
| T177 | P0 | **Diễn giải Cây quyết định:** Trích xuất độ quan trọng đặc trưng (Permutation Importance) và vẽ các phân nhánh cấp cao của cây. | T172 |
| T178 | P0 | **Phân đoạn sai số định lượng (Quantitative slices):** Tính Test MCRMSE và MAE theo 3 dải điểm thực tế: Thấp ($< 2.5$), Trung bình ($2.5 - 3.5$), Cao ($> 3.5$). | T172 |
| T179 | P0 | Tính Test MCRMSE theo 3 nhóm độ dài bài viết: Ngắn ($< 200$ từ), Trung bình ($200 - 400$ từ), Dài ($> 400$ từ). | T172 |
| T180 | P0 | Xác nhận xem mô hình có xu hướng dự đoán co cụm về trung bình (Overpredict ở điểm thấp, Underpredict ở điểm cao) hay không. | T178 |
| T181 | P0 | **Phân tích định tính ca bệnh (Qualitative Case Studies):** Trích xuất 5 ca dự đoán quá cao (Overprediction) lớn nhất. | T172 |
| T182 | P0 | Trích xuất 5 ca dự đoán quá thấp (Underprediction) lớn nhất. | T172 |
| T183 | P0 | Trích xuất các ca điển hình mà Ridge và DeBERTa bất đồng quan điểm sâu sắc. | T172 |
| T184 | P0 | Đọc trực tiếp nội dung bài luận của các ca lỗi lớn, phân tích dưới góc độ ngôn ngữ học (lỗi diễn đạt, câu cụt, từ vựng hiếm, sự lạc đề). | T181–T183 |
| T185 | P0 | Phân loại lỗi theo bảng phân loại (Taxonomy): Lối tắt độ dài, lỗi parser cú pháp, điểm số người chấm bất thường, từ vựng dị biệt. | T184 |
| T186 | P0 | Lưu các biểu đồ phân tích lỗi, feature importance và residual plots vào `outputs/figures/`. | T175–T180 |
| T187 | P0 | Tổng hợp các phát hiện trả lời dứt khoát RQ1, RQ2 và RQ3 vào báo cáo phân tích. | T173, T174, T185 |

### Sản phẩm đầu ra Giai đoạn 11
- Biểu đồ phân tích độ quan trọng đặc trưng và biểu đồ phân tích lối tắt độ dài.
- Bảng thống kê sai số phân tách theo dải điểm và phân đoạn độ dài văn bản.
- Hồ sơ phân tích định tính 10 ca lỗi sai lệch lớn nhất kèm giải thích ngôn ngữ học.
- Câu trả lời hoàn chỉnh dựa trên bằng chứng cho RQ1, RQ2, RQ3.

### Cổng đánh giá Giai đoạn 11 (Gate 11)
Báo cáo phân tích phân biệt rõ giữa tương quan thống kê và quan hệ nhân quả; các giải thích lỗi dựa trên bằng chứng dữ liệu xác thực, không võ đoán.

---

# Giai đoạn 12 — Thử nghiệm Khả năng Mở rộng (Phase 12 - Tùy chọn)

## Mục tiêu
Thực hiện các thử nghiệm phân tích sâu bổ sung (như mô hình Lai Hybrid hoặc phân tích suy rộng) nếu Giai đoạn 11 đã hoàn tất mỹ mãn.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T188 | P0 | Xác nhận tất cả các nhiệm vụ P0 từ Giai đoạn 0 đến Giai đoạn 11 đã hoàn tất 100%. | Phase 11 |
| T189 | P1 | Đánh giá chi tiết mô hình Lai E6 (DeBERTa + Linguistic features) nếu đã triển khai ở Phase 9 và 10. | T188 |
| T190 | P1 | So sánh xem việc bổ sung đặc trưng ngôn ngữ học vào DeBERTa có cải thiện thêm MCRMSE hay không. | T189 |
| T191 | P1 | Thảo luận về khả năng tổng quát hóa trên người học mới hoặc đề bài mới dựa trên các đặc điểm văn phong. | T188 |
| T192 | P2 | Thử nghiệm loại trừ từng nhóm đặc trưng (Leave-one-group-out ablation) trên mô hình Ridge nếu cần làm sâu thêm RQ2. | T188 |
| T193 | P2 | Xây dựng giao diện web demo nhỏ (Gradio / Streamlit) nhận diện bài văn và xuất 6 điểm dự đoán kèm cảnh báo phi thương mại. | T188 |
| T194 | P0 | Ghi rõ trong báo cáo phần nào là kết quả thực nghiệm chính thức, phần nào là phân tích mở rộng sau thử nghiệm (post-hoc). | T189–T193 |

### Sản phẩm đầu ra Giai đoạn 12
- Kết quả đánh giá mô hình Lai hoặc thử nghiệm ablation bổ sung (nếu có).
- Giao diện demo trực quan (tùy chọn).
- Phân định rạch ròi giữa kết quả kiểm định tiền định và phân tích mở rộng.

### Cổng đánh giá Giai đoạn 12 (Gate 12)
Không để các thử nghiệm mở rộng làm lu mờ hoặc trì hoãn việc hoàn thành báo cáo khoa học chính thức.

---

# Giai đoạn 13 — Viết Báo cáo Học thuật Hoàn chỉnh (Phase 13)

## Mục tiêu
Chuyển hóa toàn bộ quy trình, mã nguồn và kết quả thực nghiệm thành Báo cáo nghiên cứu học thuật chuẩn mực gồm 14 chương bằng Tiếng Việt.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T195 | P0 | Thiết lập khung cấu trúc báo cáo 14 chương chuẩn mực trong thư mục `report/`. | Phase 11 |
| T196 | P0 | Viết Chương 1 (Mở đầu): Bối cảnh hỗ trợ học tiếng Anh, bài toán, phạm vi, 4 câu hỏi nghiên cứu và đóng góp cốt lõi. | T195 |
| T197 | P0 | Viết Chương 2 (Kiến thức Nền tảng): Khảo sát đánh giá bài viết người học, các nhóm đặc trưng ngôn ngữ, cơ chế DeBERTa-v3. | T195 |
| T198 | P0 | Viết Chương 3 (Tập dữ liệu ELLIPSE): Nguồn gốc Kaggle, rubric 6 tiêu chí, phân tích thống kê mô tả, đạo đức dữ liệu. | T195 |
| T199 | P0 | Viết Chương 4 (Kiểm toán Dữ liệu và Tiền xử lý): Quy tắc drop `non_fluency_reason`, phân tầng 70/15/15, chuẩn hóa target $[0, 1]$. | T195 |
| T200 | P0 | Viết Chương 5 (Kỹ nghệ Đặc trưng Ngôn ngữ): Định nghĩa, công thức và công cụ trích xuất 4 nhóm đặc trưng S, L, Y, R. | T195 |
| T201 | P0 | Viết Chương 6 (Mô hình và Pipeline Học máy): Kiến trúc Baseline, Ridge, Decision Tree và DeBERTa-v3-small 6-output head. | T195 |
| T202 | P0 | Viết Chương 7 (Thiết lập Thực nghiệm): Môi trường huấn luyện GPU, siêu tham số, cơ chế chunking bài dài, tính tái lập seed 42. | T195 |
| T203 | P0 | Viết Chương 8 (Chỉ số Đánh giá): Định nghĩa toán học và ý nghĩa của MCRMSE, MAE, RMSE, $R^2$. | T195 |
| T204 | P0 | Viết Chương 9 (Kết quả Thực nghiệm): Chèn các bảng số liệu thực tế từ tập Test (E0 đến E5), không để số ảo hay placeholder. | T195, Phase 10 |
| T205 | P0 | Viết Chương 10 (Phân tích và Diễn giải): Trình bày kết quả RQ1 (so sánh mô hình) và RQ2 (đóng góp đặc trưng & phân tích lối tắt). | T204, Phase 11 |
| T206 | P0 | Viết Chương 11 (Phân tích Lỗi Toàn diện): Trình bày kết quả RQ3, các phân đoạn định lượng và 10 ca bệnh định tính điển hình. | T204, Phase 11 |
| T207 | P0 | Viết Chương 12 (Giới hạn và Đạo đức): Nêu rõ 5 giới hạn nghiên cứu và tuyên bố sử dụng có trách nhiệm, không thay thế giáo viên. | T195 |
| T208 | P0 | Viết Chương 13 (Minh bạch Sử dụng AI): Ghi nhận trung thực vai trò hỗ trợ của trợ lý AI và cam kết chịu trách nhiệm của tác giả. | T195 |
| T209 | P0 | Viết Chương 14 (Kết luận và Hướng phát triển): Tóm lược các phát hiện dựa trên bằng chứng xác thực. | T205–T208 |
| T210 | P0 | Rà soát toàn bộ báo cáo: Đảm bảo 100% bằng Tiếng Việt, câu từ học thuật mạch lạc, công thức toán hiển thị đẹp. | T196–T209 |
| T211 | P0 | Kiểm tra tất cả các hình ảnh, biểu đồ, bảng biểu đều có tiêu đề, số thứ tự và được viện dẫn chính xác trong văn bản. | T210 |
| T212 | P0 | Kiểm tra trích dẫn tài liệu tham khảo đầy đủ theo chuẩn IEEE hoặc APA. | T210 |
| T213 | P0 | Loại bỏ triệt để mọi tuyên bố quá đà (như "mô hình đo lường năng lực tiếng Anh tuyệt đối"). | T210 |
| T214 | P1 | Nhờ bạn học hoặc người hướng dẫn đọc phản biện và góp ý bản thảo. | T210 |
| T215 | P0 | Chỉnh sửa và hoàn thiện báo cáo theo các góp ý xác đáng. | T214 |
| T216 | P0 | Xuất tệp báo cáo định dạng PDF hoàn chỉnh và kiểm tra định dạng trang in. | T215 |

### Sản phẩm đầu ra Giai đoạn 13
- Báo cáo nghiên cứu học thuật hoàn chỉnh 14 chương định dạng PDF và Markdown.
- Hệ thống bảng biểu, biểu đồ chất lượng cao được gắn kết hoàn hảo vào nội dung.
- Bản tuyên bố minh bạch sử dụng AI và cam kết học thuật.

### Cổng đánh giá Giai đoạn 13 (Gate 13)
Mọi kết luận trong báo cáo đều có căn cứ trực tiếp từ số liệu thực nghiệm; không có lỗi chính tả, sai lệch bảng biểu hay số liệu giả tạo.

---

# Giai đoạn 14 — Chuẩn bị Slide và Luyện tập Bảo vệ Vấn đáp (Phase 14)

## Mục tiêu
Xây dựng slide báo cáo súc tích, ấn tượng và luyện tập trả lời sắc bén các câu hỏi chất vấn phản biện của hội đồng chấm điểm.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T217 | P0 | Xác nhận thời gian và định dạng thuyết trình chính thức (ví dụ: 15 phút trình bày + 10 phút vấn đáp). | Phase 13 |
| T218 | P0 | Lập dàn ý bài trình bày: Đặt vấn đề $\to$ Dữ liệu ELLIPSE $\to$ Đặc trưng & DeBERTa $\to$ Phân tầng 70/15/15 $\to$ Kết quả Test $\to$ Lối tắt & Lỗi $\to$ Kết luận. | T217 |
| T219 | P0 | Thiết kế slide bài toán và pipeline tổng thể trực quan, làm nổi bật sự so sánh giữa mô hình diễn giải và Transformer. | T218 |
| T220 | P0 | Thiết kế slide thẩm định dữ liệu: Nguồn gốc Kaggle, 6 target, rào chắn loại bỏ `non_fluency_reason`. | T218 |
| T221 | P0 | Thiết kế slide kỹ nghệ đặc trưng: Tóm lược 4 nhóm S, L, Y, R và tính tất định. | T218 |
| T222 | P0 | Thiết kế slide kiến trúc DeBERTa-v3-small và cấu hình fine-tuning. | T218 |
| T223 | P0 | Thiết kế slide kết quả thực nghiệm: Bảng so sánh MCRMSE chính thức và phân tích theo từng tiêu chí. | T218 |
| T224 | P0 | Thiết kế slide phân tích lối tắt độ dài văn bản và kết quả ablation E1 vs E3. | T218 |
| T225 | P0 | Thiết kế slide phân tích lỗi: Trực quan hóa các phân đoạn và ví dụ ca bệnh thực tế. | T218 |
| T226 | P0 | Thiết kế slide giới hạn nghiên cứu, đạo đức và sử dụng có trách nhiệm. | T218 |
| T227 | P0 | Thiết kế slide kết luận trả lời ngắn gọn 4 câu hỏi nghiên cứu. | T218 |
| T228 | P0 | Soạn bộ câu hỏi vấn đáp phản biện trọng tâm (Oral Defense Question Bank):
- Tại sao dự đoán 6 target thay vì điểm trung bình?
- Tại sao chọn `microsoft/deberta-v3-small`?
- Tại sao không dùng model essay-scoring fine-tuned sẵn?
- Làm sao chứng minh mô hình không chỉ đếm số từ để cho điểm?
- Ý nghĩa của chỉ số MCRMSE so với MAE?
- Xử lý bài luận dài vượt 512 token như thế nào? | T218–T226 |
| T229 | P0 | Chuẩn bị câu trả lời ngắn gọn, khúc chiết, có số liệu và lý lẽ chứng minh cho từng câu hỏi. | T228 |
| T230 | P0 | Luyện tập thuyết trình thử nghiệm canh chuẩn thời gian (bấm giờ thực tế). | T219–T229 |
| T231 | P1 | Tổ chức buổi bảo vệ thử (Mock Defense) với người phản biện đặt câu hỏi hóc búa. | T230 |
| T232 | P0 | Điều chỉnh nội dung slide và câu trả lời dựa trên phản hồi của buổi bảo vệ thử. | T231 |
| T233 | P0 | Kiểm tra kỹ thuật: chạy thử slide trên máy chiếu/thiết bị trình chiếu thực tế. | T232 |

### Sản phẩm đầu ra Giai đoạn 14
- Bộ slide báo cáo hoàn chỉnh (định dạng PPTX / PDF).
- Tài liệu ngân hàng câu hỏi vấn đáp và định hướng trả lời.
- Bản ghi nhận kết quả luyện tập thuyết trình đúng khung thời gian.

### Cổng đánh giá Giai đoạn 14 (Gate 14)
Người trình bày tự tin giải thích được mọi quyết định thiết kế kỹ thuật và trả lời thuyết phục các câu hỏi phản biện của hội đồng.

---

# Giai đoạn 15 — Kiểm toán Kỹ thuật Cuối cùng và Đóng gói Nộp bài (Phase 15)

## Mục tiêu
Chạy kiểm toán tính tái lập toàn diện trên môi trường sạch, đối chiếu khớp số liệu 100% và đóng gói hồ sơ nộp bài hoàn hảo.

| Mã hiệu | Mức ưu tiên | Nhiệm vụ chi tiết | Sự phụ thuộc |
|---|---|---|---|
| T234 | P0 | Chạy kiểm thử toàn bộ dự án từ đầu trong một môi trường sạch để bảo đảm tính tái lập độc lập. | Phase 13, Phase 14 |
| T235 | P0 | Xác nhận quy trình chạy lại tái hiện chính xác 100% các bảng kết quả và biểu đồ trong báo cáo. | T234 |
| T236 | P0 | Chạy toàn bộ các bài kiểm tra tự động (`pytest tests/`) và bảo đảm 100% tests passed. | T234 |
| T237 | P0 | Rà soát toàn bộ kho mã nguồn: Tuyệt đối không commit dữ liệu thô bị giới hạn bản quyền hay khóa API cá nhân. | T234 |
| T238 | P0 | Kiểm tra xác nhận tập Test chỉ được nạp vào đúng một lần ở Phase 10, không lọt vào tuning. | T234 |
| T239 | P0 | Đối chiếu từng con số trong báo cáo, slide và file kết quả `outputs/predictions/predictions_test.csv` khớp nhau từng chữ số thập phân. | T235 |
| T240 | P0 | Rà soát toàn bộ dự án để loại bỏ triệt để các chuỗi `TBD`, placeholder hay số liệu minh họa giả định. | T239 |
| T241 | P0 | Đối chiếu từng tiêu chí trong khung chấm điểm (Rubric) của giảng viên và ghi chú vị trí đáp ứng trong hồ sơ nộp. | T239 |
| T242 | P0 | Đóng gói mã nguồn sạch kèm tệp `README.md` hướng dẫn chạy tái lập bằng 1 dòng lệnh. | T236, T240 |
| T243 | P0 | Tạo thẻ phiên bản Git chính thức (Git Tag v1.0.0 - Final Submission). | T242 |
| T244 | P0 | Sao lưu toàn bộ mã nguồn, dữ liệu chế biến, checkpoint, báo cáo và slide lên bộ nhớ an toàn. | T243 |
| T245 | P0 | Nộp bài qua cổng nộp bài chính thức của môn học theo đúng cú pháp đặt tên quy định. | T241, T244 |
| T246 | P0 | Tải lại tệp đã nộp từ cổng thông tin trường và mở kiểm tra xác thực tệp nguyên vẹn, không lỗi. | T245 |
| T247 | P0 | Lưu ảnh chụp màn hình xác nhận nộp bài thành công. | T246 |
| T248 | P1 | Viết tóm tắt tổng kết dự án, ghi nhận các bài học kinh nghiệm và định hướng nâng cấp trong tương lai. | T247 |

### Sản phẩm đầu ra Giai đoạn 15
- Repository mã nguồn tái lập hoàn hảo đã gắn thẻ Release v1.0.0.
- Trọn bộ hồ sơ nộp bài: Báo cáo PDF, Slide thuyết trình, Mã nguồn, Bảng kết quả.
- Minh chứng nộp bài thành công và bản tổng kết bài học kinh nghiệm.

### Cổng đánh giá Giai đoạn 15 (Gate 15)
Dự án hoàn thành trọn vẹn; tệp nộp đã được tải lại và mở kiểm tra thành công, sẵn sàng bước vào buổi bảo vệ chính thức.

---

## 3. Các Cột mốc Trọng yếu (Milestones)

| Cột mốc | Điều kiện hoàn thành | Khoảng nhiệm vụ |
|---|---|---|
| **M1 — Phạm vi được phê duyệt** | Đóng băng định nghĩa bài toán, 6 target, 4 họ mô hình, metric MCRMSE và danh sách loại trừ. | T001–T014 |
| **M2 — Dữ liệu được tiếp nhận** | Tiếp nhận ELLIPSE, loại bỏ `non_fluency_reason`, hoàn thành Data Card và quyết định hồi quy. | T015–T040 |
| **M3 — Môi trường sẵn sàng** | Môi trường GPU hoạt động, dependencies cố định, kiểm toán dữ liệu và phân tích token hoàn tất. | T041–T088 |
| **M4 — Phân chia được đóng băng** | Giữ official test; chia official train 80/20 và khóa `essay_split_manifest.csv`. | T089–T101 |
| **M5 — Đặc trưng được thẩm định** | 24–30 đặc trưng ngôn ngữ S, L, Y, R được trích xuất tất định, ma trận đặc trưng qua QA. | T102–T125 |
| **M6 — Pipeline sẵn sàng** | Pipeline Baseline, Ridge, Cây quyết định và DeBERTa regression head qua bài test khói. | T126–T138 |
| **M7 — Tối ưu phát triển hoàn tất** | Hoàn thành thực nghiệm E0–E5 trên Train/Val, lưu checkpoint DeBERTa tốt nhất, đóng băng mô hình. | T139–T157 |
| **M8 — Đánh giá Test hoàn thành** | Đánh giá 1 lần duy nhất trên tập Test, lưu tệp dự đoán và xuất bảng kết quả chính thức. | T158–T171 |
| **M9 — Phân tích hoàn tất** | Hoàn thành phân tích lối tắt độ dài, giải thích mô hình và giải mã 10 ca lỗi lớn nhất (RQ1–RQ3). | T172–T194 |
| **M10 — Báo cáo hoàn chỉnh** | Báo cáo 14 chương tiếng Việt chuẩn mực được xuất bản PDF và kiểm tra định dạng trang. | T195–T216 |
| **M11 — Bảo vệ sẵn sàng** | Hoàn thành bộ slide, thuộc ngân hàng câu hỏi vấn đáp và hoàn thành diễn tập bấm giờ. | T217–T233 |
| **M12 — Nghiệm thu nộp bài** | Kiểm toán tái lập thành công, nộp bài đúng hạn và xác nhận tệp nộp nguyên vẹn. | T234–T248 |

---

## 4. Thứ tự Thực hiện Khuyến nghị theo Phiên làm việc (Work Sessions)

### Phiên làm việc Nhóm A — Bắt đầu ngay lập tức
1. Hoàn thành T001–T014 (Khởi tạo repo, đóng băng phạm vi bài toán).
2. Tải dữ liệu ELLIPSE và thực hiện ngay T017–T018 (Loại bỏ cột rò rỉ `non_fluency_reason`).
3. Chưa viết mã mô hình khi chưa kiểm toán dữ liệu.

### Phiên làm việc Nhóm B — Cổng dữ liệu và Môi trường
1. Hoàn thành T041–T054 (Cài đặt môi trường GPU, cố định requirements).
2. Hoàn thành T055–T074 (Kiểm toán tính toàn vẹn, bảo toàn lỗi ngôn ngữ gốc).
3. Hoàn thành T075–T088 (EDA, đo phân vị token DeBERTa để chốt chiến lược chunking/truncation).

### Phiên làm việc Nhóm C — Phân tầng và Trích xuất Đặc trưng
1. Hoàn thành T089–T101 (giữ official test, chia official train 80/20 và xuất `essay_split_manifest.csv`).
2. Hoàn thành T102–T114 (Cài đặt 24–30 đặc trưng ngôn ngữ qua spaCy và textstat).
3. Hoàn thành T115–T125 (Trích xuất ma trận đặc trưng, cài đặt hàm chuẩn hóa target $[0, 1]$).

### Phiên làm việc Nhóm D — Xây dựng Pipeline và Thử nghiệm Khói
1. Cài đặt metric MCRMSE và các metric phụ trong `src/evaluate.py`.
2. Dựng Pipeline cho Baseline, Ridge, Decision Tree trong `src/models.py`.
3. Dựng kiến trúc `microsoft/deberta-v3-small` regression head.
4. Chạy smoke test thành công cho tất cả các mô hình.

### Phiên làm việc Nhóm E — Huấn luyện và Tối ưu Mô hình
1. Chạy thực nghiệm E0 đến E4 cho các mô hình truyền thống trên tập Train/Val.
2. Fine-tune DeBERTa-v3-small (E5) trên GPU, theo dõi Early Stopping qua Val MCRMSE.
3. Đóng băng toàn bộ mã nguồn và checkpoint mô hình (T156–T157).

### Phiên làm việc Nhóm F — Mở Tập Test và Đào sâu Phân tích
1. Đánh giá 1 lần duy nhất trên tập Test, lưu file `predictions_test.csv`.
2. Tiến hành phân tích lối tắt độ dài văn bản (E1 vs E3).
3. Phân tích định lượng các phân đoạn điểm số và phân tích định tính 10 ca lỗi lớn nhất.

### Phiên làm việc Nhóm G — Soạn thảo Báo cáo, Slide và Nộp bài
1. Viết báo cáo học thuật 14 chương bằng tiếng Việt dựa trên các bảng biểu đã lưu.
2. Soạn slide báo cáo và luyện tập trả lời ngân hàng câu hỏi vấn đáp.
3. Chạy kiểm toán tái lập trong môi trường sạch, đóng gói và nộp bài chính thức.

---

## 5. Các Quy tắc Kiểm soát Phạm vi Dự án (Scope-Control Rules)

Nhằm giữ cho nghiên cứu đi vào chiều sâu khoa học thay vì mở rộng dàn trải, thiếu căn cứ:
1. **Không thêm mô hình mới** ngoài 4 họ mô hình đã phê duyệt (Mean Baseline, Ridge, Decision Tree, DeBERTa-v3-small).
2. **Không xây dựng ứng dụng web phức tạp** trước khi các thực nghiệm cốt lõi, bảng kết quả và báo cáo được hoàn thành chuẩn chỉnh.
3. **Không thay đổi bài toán hay hàm loss** chỉ vì điểm số ban đầu chưa đạt như kỳ vọng.
4. **Không xóa bỏ các mẫu khó hoặc ca dự đoán sai** để làm đẹp số liệu báo cáo một cách giả tạo; các ca sai lệch chính là trọng tâm của phân tích lỗi.
5. **Tuyệt đối không tinh chỉnh đặc trưng hay siêu tham số dựa trên kết quả tập Test.**
6. **Ưu tiên phân tích sâu sắc bản chất ngôn ngữ và lỗi của mô hình** hơn là chạy đua thêm nhiều mô hình mà không giải thích được cơ chế hoạt động.
7. **Coi kết quả bất ngờ hoặc kết quả phủ định là một phát hiện khoa học có giá trị** nếu quy trình thực nghiệm được tiến hành chuẩn mực.

---

## 6. Định nghĩa Hoàn thành Toàn diện (Final Definition of Done)

Toàn bộ dự án được chính thức công nhận hoàn thành mỹ mãn khi tất cả nhiệm vụ P0 được tích chọn (`[x]`) và thỏa mãn đầy đủ các tiêu chuẩn sau:
- Tập dữ liệu ELLIPSE chính thức từ Kaggle được tiếp nhận hợp lệ và loại bỏ hoàn toàn các cột rò rỉ (`non_fluency_reason`).
- Dự đoán đồng thời 6 đầu ra điểm số liên tục $[1.0, 5.0]$ theo đúng rubric của bài toán.
- Tập Test 15% được bảo vệ tuyệt đối an toàn, phân tầng chuẩn mực theo phân vị điểm số `score_bin`.
- 24–30 đặc trưng ngôn ngữ dễ giải thích được trích xuất tất định, kiểm thử độc lập và tài liệu hóa đầy đủ.
- Chuẩn hóa target về đoạn $[0, 1]$ và khôi phục điểm số nguyên bản kèm cắt biên $[1.0, 5.0]$ chính xác.
- Pipeline DeBERTa-v3-small và các mô hình Ridge, Decision Tree được so sánh công bằng trên cùng một phân vùng dữ liệu.
- MCRMSE là thước đo chính thức; MAE, RMSE, $R^2$ được báo cáo chi tiết cho từng tiêu chí.
- Đánh giá trên tập Test được thực hiện duy nhất một lần sau khi mọi quyết định đã đóng băng.
- Nghi vấn về lối tắt độ dài văn bản được giải đáp thỏa đáng bằng số liệu thực nghiệm đối chứng.
- Tối thiểu 10 ca dự đoán sai lệch lớn nhất được phân tích thấu đáo về mặt ngôn ngữ học.
- Báo cáo khoa học 14 chương bằng tiếng Việt mạch lạc, văn phong chuẩn mực, số liệu thống nhất 100%.
- Slide trình bày ấn tượng, tác giả tự tin bảo vệ lý do đưa ra từng quyết định thiết kế kỹ thuật trước hội đồng.
- Kho mã nguồn có thể tái lập trọn vẹn bằng một dòng lệnh trong môi trường mới.
- Toàn bộ hồ sơ nộp bài đã được tải lại từ hệ thống và kiểm tra xác nhận hoàn hảo.

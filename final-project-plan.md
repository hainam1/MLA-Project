# Kế hoạch tổng thể Final Project

## Phân loại độ khó CEFR của câu tiếng Anh bằng KNN và Decision Tree

**Tên tiếng Anh:** *English Sentence CEFR Classification: Comparing K-Nearest Neighbors and Decision Trees with Interpretable Linguistic Features*

Đây là tài liệu định hướng trung tâm của project. Project chỉ giải quyết **một bài toán Machine Learning**: dự đoán mức CEFR của một câu tiếng Anh.

---

## 1. Quyết định đã chốt

### 1.1. Bài toán ML

- **Input (`X`):** một câu tiếng Anh.
- **Output (`y`):** một trong năm nhãn `{A1, A2, B1, B2, C1}`.
- **Mã hóa khi train:** `A1=0`, `A2=1`, `B1=2`, `B2=3`, `C1=4`.
- **Loại bài toán:** supervised ordinal multi-class classification.
- **Ứng dụng:** hỗ trợ người học/giáo viên chọn câu phù hợp với trình độ.
- **Không phải mục tiêu:** đánh giá trình độ của một người học hoặc cấp chứng chỉ CEFR.

### 1.2. Hai model families chính thức

1. **K-Nearest Neighbors (KNN):** họ mô hình dựa trên khoảng cách/instance-based learning.
2. **Decision Tree:** họ mô hình cây quyết định/tree-based learning.

Hai mô hình đều là classifier, đều được thầy dạy và đều xuất được xác suất cho năm lớp. `DummyClassifier(strategy="most_frequent")` chỉ là sanity baseline, không được tính là model family thứ ba.

KNN và Decision Tree phải dùng:

- cùng phiên bản dataset;
- cùng train/validation/test split;
- cùng nhãn và cùng tập linguistic features trong thí nghiệm so sánh chính;
- cùng metric và quy tắc chọn hyperparameter;
- test set chỉ được mở sau khi khóa cấu hình.

### 1.3. Câu hỏi nghiên cứu

- **RQ1:** Với cùng bộ linguistic/readability features, KNN và Decision Tree khác nhau thế nào về Macro F1, QWK và loại lỗi CEFR?
- **RQ2:** Những nhóm đặc trưng nào đóng góp nhiều nhất, và việc bỏ nguồn word-level CEFR phụ trợ ảnh hưởng đến hai mô hình ra sao?
- **RQ3:** Hai mô hình thường thất bại ở loại câu nào, đặc biệt theo level, độ dài, từ hiếm, cú pháp và nguồn dữ liệu?

**Câu hỏi mở rộng tùy chọn:** contextual embeddings từ frozen DeBERTa + PCA có tạo ra cải thiện đủ lớn để bù chi phí tính toán hay không? Câu hỏi này chỉ thực hiện sau khi ba RQ chính đã hoàn tất.

### 1.4. Giả thuyết cần kiểm chứng

- **H1:** Decision Tree có thể đạt Macro F1 cao hơn KNN vì các ngưỡng và tương tác phi tuyến giữa linguistic features, nhưng cũng dễ overfit hơn.
- **H2:** StandardScaler và distance weighting sẽ ảnh hưởng đáng kể đến KNN; pruning parameters sẽ ảnh hưởng đáng kể đến Decision Tree.
- **H3:** Cả hai mô hình sẽ mắc nhiều lỗi liền kề hơn lỗi cách từ hai cấp trở lên, nhưng có thể thiên lệch theo độ dài và lớp B1/B2.
- **H4:** Bỏ ba aggregate word-CEFR features có thể làm giảm kết quả; mức giảm phải được đo thay vì giả định.

Mọi giả thuyết đều có thể bị bác bỏ. Kết luận phải dựa trên kết quả thực nghiệm đã lưu.

### 1.5. Phạm vi bị loại bỏ

- Dịch Việt–Anh.
- Phân loại CEFR ở mức từ như một task riêng.
- Chọn từ đồng nghĩa hoặc vocabulary retrieval.
- Sinh câu ví dụ.
- Viết lại/đơn giản hóa câu.
- “Second Pair of Eyes”.
- Fine-tune LLM/Transformer như mô hình chính.
- REST API production, web UI, release pipeline và triển khai công khai.

Word-level CEFR survey chỉ được dùng để tạo ba đặc trưng tổng hợp cho câu. Nó không tạo thành bài toán ML thứ hai và bắt buộc có ablation không dùng nguồn này.

---

## 2. Dữ liệu và protocol cố định

### 2.1. Dataset

**Nguồn chính:**

- `UniversalCEFR/cefr_sp_en`: 10.004 dòng thô đã ghi nhận.
- `UniversalCEFR/readme_en`: 2.822 dòng thô đã ghi nhận.
- Chỉ giữ A1–C1; loại C2, nhãn sai, câu rỗng, exact duplicate và nhóm cùng câu nhưng mâu thuẫn nhãn.
- Pipeline cũ tạo 12.521 câu; số cuối cùng phải được sinh lại tự động trong Phase 1.

**Nguồn phụ trợ:**

- Word-level CEFR survey của Guzey et al. chỉ dùng cho aggregate lexical features.

Trước khi nộp phải xác minh lại license, citation, revision, access date và checksum. Project không dùng dữ liệu sinh viên thật.

### 2.2. Chia dữ liệu chống leakage

- Tạo cluster cho exact/near duplicates trước khi split.
- Chia xấp xỉ 70% train, 15% validation, 15% test theo `cluster_id`, có stratification và seed cố định.
- Không có normalized text hoặc `cluster_id` xuất hiện ở nhiều split.
- Imputer, scaler, PCA và mọi biến đổi học từ dữ liệu chỉ được fit trên train.
- Validation dùng để chọn hyperparameter; test không được dùng để điều chỉnh mô hình.

### 2.3. Đặc trưng chính

- **Surface:** số từ, số ký tự, độ dài từ trung bình, số âm tiết.
- **Lexical rarity:** Zipf frequency trung bình/thấp nhất, tỷ lệ từ hiếm.
- **Auxiliary word-CEFR:** CEFR trung bình/cao nhất của từ và OOV ratio.
- **Syntax/POS:** dependency depth, mệnh đề phụ, bị động, POS ratios.
- **Readability:** Flesch Reading Ease, FKGL, Gunning Fog, ARI, Dale–Chall.

`source`, `cluster_id`, split ID, text label và target tuyệt đối không được đưa vào feature matrix.

### 2.4. Metric

- **Metric chọn mô hình:** Macro F1 trên validation.
- **Metric ordinal bắt buộc:** Quadratic Weighted Kappa (QWK).
- **Metric phụ:** accuracy, weighted F1, adjacent accuracy, mean absolute level error, precision/recall/F1 từng lớp.
- **Chẩn đoán:** confusion matrix, xác suất dự đoán, runtime và kết quả theo các error slices định nghĩa trước.
- **So sánh độ bất định:** paired bootstrap 95% confidence interval cho chênh lệch KNN–Decision Tree nếu thời gian cho phép.

---

## 3. Thiết kế mô hình

### 3.1. Sanity baseline

`DummyClassifier(strategy="most_frequent")` kiểm tra rằng mô hình học được tốt hơn việc luôn đoán lớp phổ biến nhất. Baseline này không đáp ứng yêu cầu hai families và không tham gia tranh luận KNN–Decision Tree.

### 3.2. KNN

Pipeline bắt buộc:

```text
linguistic features
→ median imputer fit trên train
→ StandardScaler fit trên train
→ KNeighborsClassifier
→ A1/A2/B1/B2/C1
```

Search space nhỏ, công bố trước:

- `n_neighbors`: `{3, 5, 7, 11, 15}`;
- `weights`: `{uniform, distance}`;
- `p`: `{1, 2}` tương ứng Manhattan/Euclidean;
- giữ các lựa chọn khác cố định trừ khi validation cho thấy lý do rõ ràng phải thay đổi.

Điểm cần phân tích: KNN nhạy với scaling, lựa chọn `k`, class imbalance và số chiều. Xác suất của KNN là tỷ lệ/trọng số phiếu từ các hàng xóm, không nên gọi là độ chắc chắn tuyệt đối.

### 3.3. Decision Tree

Pipeline bắt buộc:

```text
linguistic features
→ median imputer fit trên train
→ DecisionTreeClassifier
→ A1/A2/B1/B2/C1
```

Search space nhỏ, công bố trước:

- `criterion`: `{gini, entropy}`;
- `max_depth`: `{4, 6, 8, 12, None}`;
- `min_samples_split`: `{2, 4, 10}`;
- `min_samples_leaf`: `{1, 2, 5, 10}`;
- `class_weight`: `balanced` và, nếu đủ thời gian, so sánh với `None` trên validation.

Điểm cần phân tích: cây sâu dễ ghi nhớ train data; pruning phải được chọn bằng validation. Feature importance và đường đi trong cây chỉ thể hiện association/quy tắc của model, không chứng minh quan hệ nhân quả.

### 3.4. Ma trận thí nghiệm tối thiểu

| ID | Model | Feature set | Vai trò |
|---|---|---|---|
| E0 | Majority Dummy | Linguistic | Sanity baseline |
| E1 | KNN | Toàn bộ linguistic features | Model family 1 |
| E2 | Decision Tree | Toàn bộ linguistic features | Model family 2 |
| E3a | KNN | Không có auxiliary word-CEFR | Ablation bắt buộc |
| E3b | Decision Tree | Không có auxiliary word-CEFR | Ablation bắt buộc |

**Extension tùy chọn, không được làm trước E0–E3:** frozen DeBERTa embeddings → train-only PCA → thử với KNN và/hoặc ghép với linguistic features. Không dùng extension này để thay thế hai families chính thức.

---

## 4. Kế hoạch chi tiết theo phase

### Phase 0 — Khóa scope và rubric

**Mục tiêu:** mọi phần việc đều phục vụ trực tiếp một bài toán CEFR classification.

**Cần làm:**

- Chốt input, output, label space, application và phần ngoài phạm vi.
- Ghi rõ KNN và Decision Tree là hai model families chính thức đã học.
- Ghi rõ majority classifier chỉ là sanity baseline.
- Đối chiếu từng tiêu chí của thầy với file/bằng chứng cụ thể.
- Không dùng tên module cũ như Model 1/2a/2b/3/4 trong bài final.

**Deliverables:** plan, task formulation và rubric matrix đồng nhất.

**Điều kiện hoàn thành:** giải thích project trong một phút mà không nhắc translation/generation và gọi đúng hai classifier.

### Phase 1 — Data provenance, cleaning và EDA

**Mục tiêu:** tạo corpus có nhãn, sạch, có license và tái lập được.

**Cần làm:**

- Pin dataset ID/revision; ghi URL, citation, license, access date và checksum.
- Chuẩn hóa Unicode NFC, whitespace và nhãn nhưng không viết lại câu.
- Chỉ giữ A1–C1; log số C2/invalid/empty bị loại.
- Loại exact duplicates và toàn bộ nhóm có cùng normalized text nhưng mâu thuẫn nhãn.
- Giữ `source` chỉ để audit/domain analysis.
- Sinh `data_audit.json`: raw count, retained count, label/source distribution và lý do loại.
- Tạo EDA về class imbalance, độ dài, lexical rarity và khác biệt giữa hai nguồn.
- Hoàn thiện data card và giới hạn sử dụng.

**Deliverables:** cleaned CSV, `data_audit.json`, data card, license table và EDA figures.

**Điều kiện hoàn thành:** mỗi dòng có sentence ID ổn định, text không rỗng, một nhãn hợp lệ và provenance rõ ràng.

### Phase 2 — Leakage-safe split

**Mục tiêu:** câu trùng/gần trùng không đi qua nhiều split.

**Cần làm:**

- Chuẩn hóa riêng text dùng cho duplicate matching.
- Tạo near-duplicate clusters có tính bắc cầu bằng token Jaccard và SequenceMatcher.
- Review thủ công sample quanh threshold trước khi khóa ngưỡng.
- Tạo train/validation/test split theo group và kiểm tra phân bố nhãn/source.
- Assert không có normalized text hoặc cluster giao nhau.
- Lưu row IDs, cluster IDs, seed, ratios và checksum vào `split_manifest.json`.

**Deliverables:** ba split CSV và `split_manifest.json`.

**Điều kiện hoàn thành:** toàn bộ leakage tests pass và hai model sử dụng đúng cùng manifest.

### Phase 3 — Linguistic feature pipeline

**Mục tiêu:** có feature matrix ổn định, giải thích được và dùng chung giữa train/inference.

**Cần làm:**

- Kiểm tra ý nghĩa, kiểu dữ liệu và range của từng feature.
- Test extractor trên câu ngắn, dài, đơn giản và cú pháp phức.
- Xử lý missing/infinite values trong sklearn pipeline.
- Khóa feature schema và checksum/version của auxiliary lexicon.
- Chứng minh metadata và label không lọt vào `X`.
- Dùng cùng `SentenceFeatureExtractor` cho train và demo.

**Deliverables:** feature CSV, feature schema, unit tests và feature-group documentation.

**Điều kiện hoàn thành:** cùng một câu tạo đúng cùng vector đặc trưng trong training và inference.

### Phase 4 — Majority baseline và KNN

**Mục tiêu:** hoàn thành family thứ nhất và xác minh vai trò của scaling/khoảng cách.

**Cần làm:**

- Train majority baseline để kiểm tra sanity.
- Fit imputer và StandardScaler chỉ trên train.
- Tune grid KNN đã khai báo bằng validation Macro F1.
- Lưu kết quả mọi cấu hình, không chỉ cấu hình thắng.
- Báo cáo Macro F1, QWK, adjacent accuracy, level MAE, train/inference time.
- Kiểm tra train–validation gap và sensitivity theo `k`.
- Chạy ablation không có auxiliary word-CEFR features.

**Deliverables:** KNN pipeline, tuning log, ablation table và validation predictions.

**Điều kiện hoàn thành:** khóa một KNN config trước khi xem test.

### Phase 5 — Decision Tree

**Mục tiêu:** hoàn thành family thứ hai và kiểm soát overfitting.

**Cần làm:**

- Train cây mặc định chỉ để chẩn đoán overfitting, không mặc định chọn nó.
- Tune grid pruning đã khai báo bằng validation Macro F1.
- Lưu train score, validation score, node count, leaf count và depth.
- Báo cáo cùng metric/runtime như KNN.
- Chạy ablation không có auxiliary word-CEFR features.
- Xuất cây rút gọn hoặc các đường quyết định mẫu để phục vụ giải thích.

**Deliverables:** Decision Tree pipeline, tuning log, tree diagnostics, ablation table và validation predictions.

**Điều kiện hoàn thành:** khóa một Decision Tree config trước khi xem test.

### Phase 6 — Controlled comparison và khóa thí nghiệm

**Mục tiêu:** bảo đảm so sánh công bằng trước final evaluation.

**Cần làm:**

- Đặt E0–E3 vào một bảng validation duy nhất.
- Xác nhận cùng split, features, label mapping và metric implementation.
- So sánh KNN với Decision Tree về chất lượng, tốc độ, kích thước model và khả năng giải thích.
- Quyết định trước protocol cuối: retrain trên train hay train+validation; áp dụng giống nhau cho cả hai.
- Ghi config cuối, package versions, seed và feature list.
- Đóng băng code/config và đánh dấu test set chưa dùng.

**Deliverables:** validation comparison, experiment manifest và hai cấu hình đã khóa.

**Điều kiện hoàn thành:** không còn quyết định nào phụ thuộc vào kết quả test.

### Phase 7 — Final test evaluation

**Mục tiêu:** tạo một bộ kết quả chính thức duy nhất.

**Cần làm:**

- Retrain KNN và Decision Tree theo protocol đã khóa.
- Mở untouched test đúng một lần.
- Tính Macro F1, QWK, accuracy, weighted F1, adjacent accuracy, level MAE và per-class metrics.
- Sinh confusion matrix cho cả hai mô hình theo cùng thứ tự A1–C1.
- Lưu prediction từng câu cùng stable ID, true label và predicted label.
- Tính paired bootstrap interval nếu đủ thời gian.
- Không thay hyperparameter sau khi xem kết quả test.

**Deliverables:** `final_metrics.json`, `model_comparison.csv`, predictions và figures.

**Điều kiện hoàn thành:** mọi số trong report truy ngược được về config và prediction đã lưu.

### Phase 8 — Error analysis và limitations

**Mục tiêu:** giải thích hai mô hình sai ở đâu và vì sao.

**Slices định nghĩa trước:**

- true CEFR level;
- đúng, lệch một cấp, lệch từ hai cấp trở lên;
- sentence-length bins;
- lexical rarity/OOV bins;
- dependency depth/subordinate clauses;
- câu ngắn nhưng cú pháp phức;
- `cefr_sp_en` so với `readme_en`;
- high-probability wrong predictions.

**Cần làm:**

- So sánh slice metrics của KNN và Decision Tree.
- Review deterministic, stratified sample gồm cả dự đoán đúng và sai.
- Gán taxonomy: length bias, rare vocabulary, rare grammar, label ambiguity/noise, domain cue, parser failure và CEFR-boundary disagreement.
- Phân tích KNN qua hàng xóm gần nhất; phân tích Decision Tree qua decision path/feature importance.
- Nêu rõ probability chưa chắc đã được calibration tốt.
- Không tuyên bố mô hình tương đương giáo viên hoặc đánh giá được người học thật.

**Deliverables:** quantitative slice table, qualitative error table và limitations section.

**Điều kiện hoàn thành:** mỗi kết luận chính có metric hoặc error sample làm bằng chứng.

### Phase 9 — Contextual embedding extension, tùy chọn

**Mục tiêu:** chỉ sau khi core evaluation và error analysis đã hoàn tất, đo giá trị tăng thêm của contextual representation nếu còn thời gian.

**Cần làm nếu còn thời gian:**

- Pin revision/tokenizer của `microsoft/deberta-v3-small` và giữ encoder frozen.
- Cache embedding theo dataset checksum.
- Fit PCA chỉ trên train; chọn `{16, 32, 64}` bằng validation.
- KNN bắt buộc scale các PCA components trong pipeline.
- So sánh improvement với chi phí tính toán và trình bày đây là feature extension.

**Deliverables:** embedding metadata, PCA artifact và bảng extension riêng.

**Điều kiện dừng:** bỏ hoàn toàn phase này nếu Phase 0–8 chưa vững hoặc thời gian không đủ.

### Phase 10 — Reproducibility, demo, report và oral defense

**Mục tiêu:** chạy lại được, trình bày được và map đủ rubric.

**Cần làm:**

- Xác minh README commands từ download đến inference trong môi trường sạch.
- Chạy test/lint; lưu Python, package, hardware và runtime.
- Demo tối giản: câu tiếng Anh → nhãn CEFR → estimated probabilities → một vài feature values/explanations.
- Chuẩn bị saved predictions làm phương án demo dự phòng.
- Viết report theo RQ1–RQ3 và chỉ dùng final authoritative results.
- Công khai LLM chỉ hỗ trợ planning, code review, debugging và language editing; không tạo labels hoặc runtime predictions.
- Tập trả lời câu hỏi về KNN, scaling, chọn `k`, Decision Tree, pruning, leakage, Macro F1, QWK và limitations.

**Deliverables:** README hoàn chỉnh, test report, demo CLI, final report, slides, LLM disclosure và oral question bank.

**Điều kiện hoàn thành:** tất cả thành phần trong công thức Pass xuất hiện rõ và người làm giải thích được từng quyết định.

---

## 5. Ma trận đối chiếu tiêu chí của thầy

Chi tiết đối chiếu đầy đủ từng tiêu chí của đề bài với file, code, config và kiểm thử xem tại [`docs/rubric_mapping.md`](docs/rubric_mapping.md).

| Tiêu chí | Bằng chứng trong project |
|---|---|
| Language-related task | Dự đoán CEFR cho câu tiếng Anh phục vụ language learning (`reports/01_task_formulation.md`) |
| Dataset | UniversalCEFR sentence subsets, data card, license/citation/checksum (`reports/00_dataset_licenses.md`, `docs/data_card.md`) |
| ML pipeline | Download → clean → group split → features → train → evaluate → infer (`src/`, `tests/`) |
| Ít nhất 2 model families | KNN (distance-based) và Decision Tree (tree-based) (`src/models/sentence_cefr/train.py`) |
| Evaluation | Macro F1, QWK, accuracy, adjacent accuracy, MAE, per-class metrics (`configs/config.yaml`) |
| Comparison | Cùng split/features/protocol; validation và final test table chung (`reports/model_comparison.md`) |
| Error analysis | Level, distance, length, rarity, syntax, source và model-specific explanation (`reports/error_analysis.md`) |
| LLM disclosure | Supporting-only; không tạo label hoặc thay thế trained classifier (`docs/llm_disclosure.md`) |
| Oral defense | Question bank, experiment evidence và demo tái lập được (`docs/oral_defense.md`, `src/inference.py`) |

---

## 6. Thứ tự bắt đầu thực hiện

Không bắt đầu bằng tuning model. Thứ tự bắt buộc là:

1. Chạy và xác minh Phase 1: dataset/license/cleaning.
2. Khóa Phase 2: split manifest không leakage.
3. Khóa Phase 3: feature schema và tests.
4. Train/tune KNN trong Phase 4.
5. Train/tune Decision Tree trong Phase 5.
6. Khóa comparison ở Phase 6 rồi mới mở test ở Phase 7.
7. Hoàn thành error analysis ở Phase 8 trước khi cân nhắc extension Phase 9.

---

## 7. Checklist chấp nhận trước khi nộp

- [x] Đã chốt KNN và Decision Tree là hai model families chính thức.
- [ ] License/revision/citation dataset đã xác minh.
- [ ] Data audit và leakage assertions pass.
- [ ] KNN và Decision Tree dùng chính xác cùng split và feature set chính.
- [ ] KNN có imputer + scaler chỉ fit trên train.
- [ ] Decision Tree được pruning/tune chỉ bằng train/validation.
- [ ] Hyperparameter và final protocol đã khóa trước khi mở test.
- [ ] Bảng cuối có Macro F1, QWK, accuracy, adjacent accuracy và per-class metrics.
- [ ] Có confusion matrix và error analysis cho cả hai mô hình.
- [ ] Historical metrics được gắn nhãn rõ, không trộn vào kết quả chính thức.
- [ ] LLM use được công khai và chỉ ở vai trò hỗ trợ.
- [ ] README commands, test và demo chạy được trong môi trường sạch.
- [ ] Oral defense giải thích được task, data, pipeline, hai model, evaluation, results và limitations.

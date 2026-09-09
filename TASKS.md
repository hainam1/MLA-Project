# Danh sách công việc Final Project

File này dùng để theo dõi việc thực thi hằng ngày. Lý do, thiết kế thí nghiệm, deliverables và điều kiện qua phase được giải thích trong `final-project-plan.md`.

## Quy tắc làm việc

- Chỉ làm một bài toán: phân loại CEFR A1–C1 cho câu tiếng Anh.
- Hai mô hình chính thức: `KNeighborsClassifier` và `DecisionTreeClassifier`.
- Không mở test set trước khi hoàn thành và khóa Phase 6.
- Không bắt đầu extension DeBERTa khi core experiment hoặc error analysis chưa hoàn tất.
- Mọi con số trong báo cáo phải được sinh từ code và truy ngược được về config/prediction.

## Phase 0 — Chốt scope và rubric

- [x] Chốt input là một câu tiếng Anh và output là A1/A2/B1/B2/C1.
- [x] Chốt KNN là family dựa trên khoảng cách.
- [x] Chốt Decision Tree là family dựa trên cây.
- [x] Chỉ giữ majority classifier như sanity baseline.
- [x] Loại translation, word classification, generation, rewriting, auditor, API và UI khỏi scope.
- [x] Cập nhật plan, task formulation, README, config và oral-defense notes theo hai mô hình mới.
- [x] Đối chiếu lần cuối câu chữ rubric với đề bài chính thức của thầy (hoàn thành tại `docs/rubric_mapping.md`).

## Phase 1 — Dataset, license, cleaning và EDA

- [x] Pin revision của `UniversalCEFR/cefr_sp_en` và `UniversalCEFR/readme_en`.
- [x] Ghi access date, tác giả, citation, license URL và checksum raw files.
- [x] Kiểm tra download script chỉ tải hai sentence datasets và auxiliary lexicon khi được yêu cầu.
- [x] Chạy cleaning và sinh `data_audit.json`.
- [x] Xác nhận cách xử lý C2, invalid label, empty text, exact duplicate và conflicting labels.
- [x] Sinh lại retained row count thay vì dùng con số 12.521 viết tay.
- [x] Sinh bảng phân bố label theo source.
- [x] Sinh EDA về class imbalance, sentence length và lexical rarity.
- [x] Hoàn thiện `docs/data_card.md` bằng số liệu thực tế.

**Gate:** chưa làm Phase 2 nếu data audit chưa truy ngược được về raw data.

## Phase 2 — Chia tập chống leakage

- [ ] Review thủ công sample quanh near-duplicate threshold.
- [ ] Khóa seed và threshold clustering trong config.
- [ ] Sinh `cluster_id` có tính bắc cầu.
- [ ] Chia train/validation/test xấp xỉ 70/15/15 theo group và label.
- [ ] Assert normalized exact text không đi qua nhiều split.
- [ ] Assert một `cluster_id` không đi qua nhiều split.
- [ ] Kiểm tra phân bố label/source/cluster của từng split.
- [ ] Lưu row IDs, seed, ratios và checksums trong `split_manifest.json`.
- [ ] Xác nhận cả KNN và Decision Tree đọc đúng cùng ba split.

**Gate:** chưa trích xuất/tune model nếu leakage tests chưa pass.

## Phase 3 — Đặc trưng ngôn ngữ

- [ ] Kiểm tra schema của toàn bộ linguistic/readability features.
- [ ] Test feature extractor trên câu ngắn, dài, đơn giản và cú pháp phức.
- [ ] Xác nhận feature values không có `NaN`/`inf` sau pipeline.
- [ ] Xác nhận `source`, IDs, split, label và text label không lọt vào `X`.
- [ ] Dùng cùng extractor trong training và inference.
- [ ] Version/checksum auxiliary word-level CEFR lexicon.
- [ ] Định nghĩa sẵn feature groups cho ablation.
- [ ] Sinh feature matrix và lưu feature schema.

**Gate:** một câu phải tạo cùng vector trong training và demo.

## Phase 4 — Majority baseline và KNN

- [ ] Train majority-class sanity baseline.
- [ ] Tạo pipeline KNN: median imputer → StandardScaler → KNN.
- [ ] Chỉ fit imputer/scaler trên train.
- [ ] Tune `n_neighbors = {3,5,7,11,15}` trên validation.
- [ ] Tune `weights = {uniform,distance}` trên validation.
- [ ] Tune `p = {1,2}` trên validation.
- [ ] Chọn KNN bằng validation Macro F1; dùng QWK làm chẩn đoán ordinal.
- [ ] Lưu tất cả tuning trials, runtime và validation predictions.
- [ ] Chạy KNN ablation không dùng auxiliary word-CEFR features.
- [ ] Khóa một KNN config trước final test.

## Phase 5 — Decision Tree

- [ ] Train cây mặc định để quan sát train–validation overfitting.
- [ ] Tạo pipeline Decision Tree: median imputer → Decision Tree.
- [ ] Tune `criterion = {gini,entropy}` trên validation.
- [ ] Tune `max_depth = {4,6,8,12,None}` trên validation.
- [ ] Tune `min_samples_split = {2,4,10}` trên validation.
- [ ] Tune `min_samples_leaf = {1,2,5,10}` trên validation.
- [ ] Dùng `class_weight=balanced`; chỉ so sánh với `None` nếu đã ghi trước trong experiment log.
- [ ] Lưu train/validation score, depth, node count, leaf count và runtime.
- [ ] Chạy Decision Tree ablation không dùng auxiliary word-CEFR features.
- [ ] Xuất feature importance và một cây/decision path có thể giải thích.
- [ ] Khóa một Decision Tree config trước final test.

## Phase 6 — So sánh validation và khóa thí nghiệm

- [ ] Tạo một bảng chung: majority, KNN, Decision Tree và hai ablations.
- [ ] Kiểm tra cùng split, labels, main feature set và metric code.
- [ ] So sánh validation Macro F1, QWK, accuracy, adjacent accuracy và MAE.
- [ ] So sánh runtime, artifact size và khả năng giải thích.
- [ ] Chọn protocol retrain cuối và áp dụng giống nhau cho cả hai model.
- [ ] Lưu experiment manifest: config, seed, versions, features và checksums.
- [ ] Đóng băng code/config trước khi mở test.
- [ ] Ghi xác nhận rằng test chưa được dùng để chọn model/hyperparameter.

**Gate:** chỉ sau khi tất cả mục trên hoàn thành mới chuyển sang final test.

## Phase 7 — Final test evaluation

- [ ] Retrain KNN và Decision Tree bằng config/protocol đã khóa.
- [ ] Mở held-out test đúng một lần.
- [ ] Tính Macro F1, QWK, accuracy, weighted F1, adjacent accuracy và level MAE.
- [ ] Tính precision/recall/F1 theo A1–C1.
- [ ] Sinh confusion matrix cùng một label order cho cả hai model.
- [ ] Tính paired bootstrap 95% CI nếu đủ thời gian.
- [ ] Lưu `final_metrics.json`, `model_comparison.csv` và row-level predictions.
- [ ] Không retune sau khi xem test.

## Phase 8 — Error analysis và limitations

- [ ] Phân tích lỗi theo true level và error distance.
- [ ] Phân tích theo sentence length, rarity/OOV và syntax.
- [ ] Phân tích câu ngắn nhưng cú pháp phức.
- [ ] So sánh `cefr_sp_en` với `readme_en`.
- [ ] Review high-probability wrong predictions.
- [ ] Kiểm tra hàng xóm gần nhất để giải thích lỗi KNN.
- [ ] Kiểm tra decision path để giải thích lỗi Decision Tree.
- [ ] Review deterministic stratified sample gồm cả dự đoán đúng và sai.
- [ ] Viết limitations về class imbalance, label noise, source bias và probability calibration.
- [ ] Không overclaim rằng model đánh giá được trình độ người học.

## Phase 9 — Contextual embedding, tùy chọn

- [ ] Chỉ kích hoạt nếu Phase 0–8 đã hoàn tất và thời gian còn đủ.
- [ ] Pin revision/tokenizer/pooling của frozen DeBERTa.
- [ ] Cache embedding theo dataset checksum.
- [ ] Fit PCA chỉ trên train; chọn 16/32/64 chiều qua validation.
- [ ] Scale PCA features trước KNN.
- [ ] Báo cáo improvement, runtime và artifact size trong bảng extension riêng.
- [ ] Không tính DeBERTa feature extractor là một trong hai family chính thức.

## Phase 10 — Reproducibility, demo, report và bảo vệ

- [ ] Hoàn thiện các lệnh download → clean → split → features → train → evaluate → infer.
- [ ] Chạy lint/test trong môi trường Python 3.12 sạch.
- [ ] Lưu package versions, seed, hardware và runtime.
- [ ] Demo: English sentence → predicted CEFR → estimated probabilities → explanation ngắn.
- [ ] Chuẩn bị saved predictions làm demo fallback.
- [ ] Viết report trả lời trực tiếp RQ1–RQ3.
- [ ] Chỉ dùng final authoritative results trong kết luận.
- [ ] Hoàn thiện LLM disclosure bằng lịch sử sử dụng thực tế.
- [ ] Chuẩn bị slides và oral question bank.
- [ ] Tập giải thích KNN/scaling/k, Decision Tree/pruning, leakage, Macro F1, QWK và ba lỗi cụ thể.
- [ ] Chạy lại toàn bộ README commands từ môi trường sạch.

## Việc cần bắt đầu ngay

1. Đã hoàn thành 100% Phase 0 (chốt scope & rubric mapping).
2. Đã hoàn thành 100% Phase 1 (dataset provenance, license, cleaning audit, và EDA).
3. Bắt đầu Phase 2: tạo near-duplicate clusters và khóa `split_manifest.json` chống leakage.
4. Sau đó chuyển sang Phase 3 (feature extraction) và tuning KNN & Decision Tree.

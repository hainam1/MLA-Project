# Master Documentation Index (`docs/`)

Mới mở dự án? Đọc [bản đồ dự án bằng tiếng Việt](../START_HERE.md) trước để tìm
data, code clean, model và điểm chạy train. Các CSV trong `docs/data/` là bảng
kiểm toán/đánh giá phục vụ tài liệu; dữ liệu train nằm trong `data/` ở gốc repo.

Tài liệu dự án được tổ chức thành các nhóm chuyên đề dưới đây để tiện tra cứu và đối chiếu:

---

## 1. Yêu cầu môn học, Rubric & Vấn đáp
Các tài liệu định hướng mục tiêu, đối chiếu tiêu chí chấm điểm và chuẩn bị bảo vệ:

- [instructor_requirements.md](instructor_requirements.md) — Tổng hợp diễn giải nội bộ về yêu cầu và phản hồi của giảng viên.
- [rubric_mapping.md](rubric_mapping.md) — Bảng đối chiếu chi tiết từng tiêu chí trong Rubric chấm điểm với code/báo cáo tương ứng.
- [oral_defense.md](oral_defense.md) — Kịch bản câu hỏi vấn đáp tiềm năng, lập luận bảo vệ phương pháp và xử lý chất vấn.
- [project_scope.md](project_scope.md) — Phạm vi bài toán, mục tiêu hỗ trợ giáo viên và ranh giới hệ thống.
- [project_freeze_status.md](project_freeze_status.md) — Tuyên bố và trạng thái đóng băng dữ liệu/mô hình chính thức.
- [setup.md](setup.md) — Hướng dẫn cài đặt môi trường phát triển (Python 3.14, uv, spacy, languagetool).

---

## 2. Dữ liệu & Giao thức phân chia (Data & Splits)
Các tài liệu quy định tập dữ liệu, bảo mật thông tin và phòng chống rò rỉ:

- [dataset.md](dataset.md) — Mô tả tổng quan về tập dữ liệu ELLIPSE và quy trình tiền xử lý.
- [data_card.md](data_card.md) — Thẻ dữ liệu chuẩn ML (Data Card) mô tả thuộc tính, nhân khẩu học và nguồn gốc.
- [data_inventory.md](data_inventory.md) — Kiểm kê số lượng mẫu, phân bố độ dài và phân loại đề bài (prompts).
- [split_and_leakage_protocol.md](split_and_leakage_protocol.md) — Giao thức phân chia Prompt-stratified Train/Val/Test và nguyên tắc chống rò rỉ (leakage).
- [evaluation_protocol_freeze.md](evaluation_protocol_freeze.md) — Giao thức đánh giá chính thức đã được đóng băng trước khi truy cập tập Test.

---

## 3. Báo cáo thực nghiệm theo 9 Phase (Core Pipeline)
Tiến trình 9 giai đoạn xây dựng hệ thống từ bài toán đến đánh giá trên tập Test:

1. [phase1_problem_definition.md](phase1_problem_definition.md) — Định nghĩa bài toán hồi quy điểm Vocabulary & Grammar.
2. `phase2` & `phase3`: Xem chi tiết trong code [scripts/phase2_dataset_audit.py](../scripts/phase2_dataset_audit.py) và [scripts/phase3_build_split.py](../scripts/phase3_build_split.py).
3. [phase4_feature_extraction_report.md](phase4_feature_extraction_report.md) — Trích xuất 14 đặc trưng ngôn ngữ (lexical, syntactic, textstat, grammar errors).
4. [phase5_feature_audit_and_baselines.md](phase5_feature_audit_and_baselines.md) — Kiểm toán đặc trưng và xây dựng mô hình cơ sở (Mean, Median, Length-only).
5. [phase6_training_readiness.md](phase6_training_readiness.md) — Kiểm tra độ sẵn sàng và huấn luyện 4 mô hình chính thức (Ridge & Random Forest).
6. [phase7_regression_evaluation.md](phase7_regression_evaluation.md) — Đánh giá hiệu năng hồi quy trên tập Validation (MAE, RMSE, R²).
7. [phase8_review_prioritization.md](phase8_review_prioritization.md) — Đánh giá chiến lược ưu tiên giáo viên chấm lại bằng độ bất đồng ($D$).
8. [phase8_error_fairness_analysis.md](phase8_error_fairness_analysis.md) — Phân tích sai số và tính công bằng (fairness) theo giới tính, sắc tộc, điều kiện kinh tế.
9. [phase9_official_test_evaluation.md](phase9_official_test_evaluation.md) — Kết quả đánh giá cuối cùng trên tập Official Test (2,518 bài).

---

## 4. Đặc tả Tính năng & Phương pháp (Specs & Methodology)
Mô tả chi tiết kỹ thuật thuật toán và đặc trưng:

- [methodology.md](methodology.md) — Phương pháp luận toàn diện của nghiên cứu.
- [features.md](features.md) — Danh mục và diễn giải 14 đặc trưng ngôn ngữ cốt lõi.
- [feature_specification.md](feature_specification.md) — Đặc tả kỹ thuật toán học và thư viện trích xuất của từng feature.
- [length_baseline_reconstruction_addendum.md](length_baseline_reconstruction_addendum.md) — Phụ lục tái hiện và kiểm chứng baseline độ dài từ.
- [signal_lock_tree_spread.md](signal_lock_tree_spread.md) — Phân tích tính ổn định tín hiệu xếp hạng giữa các cây quyết định.

---

## 5. Nghiên cứu Cải tiến & Nghiên cứu mở rộng (Exploratory / Improvements)
Các thực nghiệm thăm dò sau giữa kỳ (không thay thế mô hình chính thức):

- [model_improvement_protocol.md](model_improvement_protocol.md) — Giao thức kiểm thử cải tiến mô hình.
- [model_improvement_audit.md](model_improvement_audit.md) — Kiểm toán các phương án cải tiến mô hình.
- [train_only_improvement_results.md](train_only_improvement_results.md) — Kết quả thử nghiệm các kiến trúc mới trên tập train-only.
- [feature_v2_gate.md](feature_v2_gate.md) — Tiêu chí kiểm duyệt bộ đặc trưng mở rộng (Feature v2).
- [feature_v2_train_only_results.md](feature_v2_train_only_results.md) — Kết quả đánh giá bộ đặc trưng v2 trên tập train.

---

## 6. Đạo đức, Quản trị rủi ro & Nhật ký dự án (Governance & Ethics)
Tài liệu đảm bảo tính minh bạch, trách nhiệm đạo đức và tính trung thực học thuật:

- [responsible_use.md](responsible_use.md) — Hướng dẫn sử dụng AI có trách nhiệm trong môi trường giáo dục (Human-in-the-loop).
- [risk_register.md](risk_register.md) — Sổ theo dõi và biện pháp giảm thiểu rủi ro kỹ thuật và đạo đức.
- [llm_disclosure.md](llm_disclosure.md) — Bản công bố minh bạch việc sử dụng công cụ AI hỗ trợ trong quá trình làm đồ án.
- [decision_log.md](decision_log.md) — Nhật ký các quyết định kiến trúc và kỹ thuật xuyên suốt dự án.
- [finalization_changelog.md](finalization_changelog.md) — Lịch sử các thay đổi trong giai đoạn hoàn thiện dự án.
- [finalization_evidence.md](finalization_evidence.md) — Tổng hợp các bằng chứng kiểm chứng tính toàn vẹn của kết quả.

---

## 7. Các thư mục con trực thuộc `docs/`
- [assets/](assets/) — Hình ảnh, biểu đồ minh họa phục vụ báo cáo.
- [data/](data/) — Các bảng dữ liệu trung gian, bảng đánh giá lỗi thủ công ([manual_error_review.csv](data/error_analysis/manual_error_review.csv)).
- [planning/](planning/) — Các bản thảo lập kế hoạch sơ khởi ban đầu.
- [post_midterm/](post_midterm/) — Các phân tích và số liệu phản hồi sau buổi nhận xét giữa kỳ của giảng viên.
- [weekly_reports/](weekly_reports/) — Bản lưu báo cáo tiến độ các tuần.


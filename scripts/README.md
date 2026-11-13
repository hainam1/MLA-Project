# Scripts: chọn điểm chạy theo công việc

[Bản đồ dự án](../START_HERE.md) · [Code chính](../src/mla_project/README.md)

Chạy từ thư mục gốc bằng `.venv\Scripts\python.exe scripts/<tên_file>.py`.
Các script có thể ghi lại kết quả ở đường dẫn cố định. Đây là mục lục điểm chạy,
không phải yêu cầu chạy lại toàn bộ pipeline đã đóng băng.

| Công việc | Điểm chạy | Kết quả chính |
|---|---|---|
| Kiểm toán data gốc | [phase2_dataset_audit.py](phase2_dataset_audit.py) | `docs/data/phase2_tables/` |
| Tạo manifest chia tập / fold | [phase3_build_split.py](phase3_build_split.py) | `data/02_split_manifest/` |
| Tạo các CSV clean dễ sử dụng | [build_clean_dataset.py](build_clean_dataset.py) | `data/03_clean_ready_to_use/` |
| Trích xuất 14 features | [phase4_extract_features.py](phase4_extract_features.py) | `data/05_model_features/`, checkpoint trong `data/04_intermediate_work/` |
| Kiểm toán features, chạy baselines | [phase5_feature_audit_and_baselines.py](phase5_feature_audit_and_baselines.py) | `docs/data/phase5_tables/` |
| Chọn tham số và train 4 model | [phase6_train_models.py](phase6_train_models.py) | `outputs/phase6/` mặc định; có `--output-dir` |
| Đánh giá hồi quy validation | [phase7_evaluate_regression_models.py](phase7_evaluate_regression_models.py) | `docs/data/phase7_tables/`, `outputs/predictions/` |
| Đánh giá ưu tiên review | [phase8_evaluate_review_prioritization.py](phase8_evaluate_review_prioritization.py) | `docs/data/phase8_tables/` |
| Phân tích lỗi / fairness | [phase8b_error_fairness_analysis.py](phase8b_error_fairness_analysis.py) | Báo cáo Phase 8b |
| Đánh giá Official Test | [phase9_official_test_evaluation.py](phase9_official_test_evaluation.py) | `docs/data/phase9_tables/`, `outputs/predictions/official_test_predictions.csv` |

Nhánh CSV clean phục vụ đọc/EDA; Phase 4 trích xuất trực tiếp từ data gốc + manifest.
Train dùng bảng features development + manifest, không dùng Official Test.

## Thực nghiệm và báo cáo bổ sung

| Nhóm | Tìm ở đâu |
|---|---|
| Kiểm toán/cải tiến model | `improvement_*.py`, `train_only_improvement_experiments.py` |
| Features v2 | `feature_v2_*.py` |
| Phân tích sau giữa kỳ | `post_midterm_teacher_analysis.py`, `progress_report_checks.py`, `show_teacher_evidence.py` |
| Hoàn thiện và kiểm tra kết quả | `finalization_*.py`, `reconstruct_phase5_length_baselines.py` |
| Biểu đồ so sánh | `plot_*.py` |
| Công việc tuần 9 / tree spread | [week9/](week9/), [week9b/](week9b/), `tree_spread_official_test_second_use.py` |
| Công việc tuần 10 / đọc bài / GEC | [week10/](week10/) |
| Chuẩn bị nguồn cho bộ vấn đáp | `build_interview_sources.py` |

Các nhánh này có mục tiêu và đầu ra riêng; không thay thế pipeline model chính.

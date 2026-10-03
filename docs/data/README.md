# Bảng Báo Cáo & Kiểm Toán Thực Nghiệm (`docs/data/`)

> **LƯU Ý QUAN TRỌNG:** Thư mục này **KHÔNG PHẢI** là dataset dùng để huấn luyện mô hình.
> - Dataset sạch và phân chia chuẩn để nạp vào mô hình nằm tại: [`data/03_clean_ready_to_use/`](../../data/03_clean_ready_to_use/).
> - Toàn bộ từ điển dữ liệu xem tại: [`data/DATA_DICTIONARY.md`](../../data/DATA_DICTIONARY.md).

---

## Mục Đích Của Thư Mục Này

Thư mục `docs/data/` chứa các bảng số liệu, báo cáo kiểm toán (Audit tables), số liệu thống kê phân phối và kết quả định lượng được sinh ra từ các Phase nghiên cứu của môn học **Machine Learning & Applications**:

| Thư Mục Con | Giai Đoạn Dự Án | Nội Dung Chính | File Tiêu Biểu |
|---|---|---|---|
| **`phase2_tables/`** | Phase 2: Khám phá & Kiểm toán dữ liệu thô | Hồ sơ phân phối cột, kiểm tra PII, độ dài bài viết, trùng lặp | `column_profile.csv`, `quality_summary.csv`, `score_distribution.csv` |
| **`phase3_tables/`** | Phase 3: Phân chia tập dữ liệu (Splits) | Đánh giá cân bằng điểm số, đề bài, phân bố 5 folds, chống rò rỉ dữ liệu | `prompt_balance.csv`, `score_balance.csv`, `cv_fold_summary.csv` |
| **`phase4_tables/`** | Phase 4: Trích xuất đặc trưng ngôn ngữ | Thống kê phân phối 14 features theo từng split, rà soát thủ công | `feature_summary_by_split.csv`, `manual_feature_review.csv` |
| **`phase5_tables/`** | Phase 5: Thẩm định đặc trưng & Baseline | Tương quan Pearson/Spearman của đặc trưng với target, kết quả baseline | `feature_correlations.csv`, `baseline_regression_metrics.csv` |
| **`phase7_tables/`** | Phase 7: Đánh giá mô hình hồi quy | Bảng so sánh MAE/RMSE/R², phân tích sai số theo nhóm, ca lỗi lớn nhất | `regression_metrics.csv`, `baseline_comparisons.csv`, `largest_errors.csv` |
| **`improvement_tables/`** | Nghiên cứu cải tiến & Độ tin cậy rater | Thẩm định Out-of-Fold (OOF), độ tin cậy giữa hai người chấm và máy | `train_oof_overall_metrics.csv`, `human_machine_reliability.csv` |

Các file CSV trong thư mục này được nhúng trực tiếp vào các tài liệu báo cáo Markdown trong thư mục `docs/` để phục vụ chấm điểm và bảo vệ đồ án (oral defense).

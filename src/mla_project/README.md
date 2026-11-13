# Code chính của dự án

[Bản đồ dự án](../../START_HERE.md) · [Các điểm chạy](../../scripts/README.md)

| Thư mục | Trách nhiệm | File nên đọc trước |
|---|---|---|
| [data/](data/) | Nạp, kiểm tra schema và xử lý chia tập | `load_data.py`, `validate_data.py`, `make_splits.py` |
| [features/](features/) | Chuẩn hóa text, trích xuất features | `preprocessing.py`, `build_features.py` |
| [models/](models/) | Tạo estimator và helpers dự đoán | `train_ridge.py`, `train_random_forest.py`, `predict.py` |
| [pipelines/](pipelines/) | Ghép các bước thành luồng train / inference | `training_pipeline.py`, `inference_pipeline.py` |
| [review/](review/) | Tính disagreement, ưu tiên teacher review và baselines | `disagreement.py`, `baselines.py` |
| [evaluation/](evaluation/) | Metrics, đánh giá hồi quy / review, phân tích lỗi | `regression_metrics.py`, `phase7.py`, `phase8.py` |
| [utils/](utils/) | Paths, cấu hình, logging và reproducibility | `paths.py`, `config.py` |

`train_ridge.py` và `train_random_forest.py` định nghĩa cách tạo model. Luồng
chọn tham số, fit, lưu và nạp artifacts nằm ở `pipelines/training_pipeline.py`:
`prepare_training_data()`, `train_models()`, `save_training_result()`,
`load_model_artifacts()`.

Script tạo CSV clean nằm ở [scripts/build_clean_dataset.py](../../scripts/build_clean_dataset.py).
Hàm chuẩn hóa text dùng chung nằm ở `features/preprocessing.py`.

Các module nằm trực tiếp dưới `src/` như `data.py`, `models.py`, `features.py`
là lớp tương thích cho code cũ. Với code mới, import từ `mla_project`.

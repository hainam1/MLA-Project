# Outputs: model đã train và kết quả chạy

[Bản đồ dự án](../START_HERE.md)

| Đường dẫn | Nội dung |
|---|---|
| [phase6/](phase6/) | Bộ 4 model chính đã train, schema, tham số, CV và metadata |
| [predictions/](predictions/) | CSV dự đoán validation, Official Test và các baselines |
| [figures/](figures/) | Hình vẽ từ các lượt đánh giá/phân tích |
| [metrics/](metrics/) | Vị trí dành cho metrics; bảng đánh giá chính hiện nằm ở `docs/data/phase*_tables/` |
| [tables/](tables/) | Vị trí dành cho bảng xuất; xem đường dẫn cụ thể trong từng script |
| [models/](models/) | Thư mục giữ chỗ; bộ model chính hiện nằm ở `phase6/` |
| `experiments/<tên_lượt>/` | Quy ước lưu lượt train mới qua `--output-dir`; tạo khi chạy thực nghiệm |

## Bộ model chính trong `phase6/`

```text
ridge_vocabulary.joblib
ridge_grammar.joblib
random_forest_vocabulary.joblib
random_forest_grammar.joblib
feature_schema.json
selected_parameters.json
cv_results.csv
validation_predictions.csv
training_summary.json
artifact_manifest.json
```

Định nghĩa kiến trúc nằm trong `src/mla_project/models/`; các file `.joblib`
ở đây là estimator đã được fit. Nạp bộ artifacts bằng
`mla_project.pipelines.training_pipeline.load_model_artifacts()`.

Đường dẫn train chính được khai báo trong `configs/phase6_training.yaml`
(`artifacts.output_dir: outputs/phase6`) và `configs/paths.yaml`.
`configs/experiment.yaml` vẫn có giá trị tổng quát `outputs/models`; đó không
phải nơi Phase 6 hiện lưu bộ model chính. Một số script đánh giá còn dùng
trực tiếp đường dẫn `outputs/phase6/`.

Các artifacts phần lớn bị Git bỏ qua. README này được lưu trong Git để hướng
dẫn cả khi clone repo sang máy chưa có model local.

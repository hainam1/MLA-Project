# Bắt đầu ở đây: bản đồ dự án

Muốn tìm data, code clean, model hoặc chỗ train: dùng bảng này trước.
Đường dẫn tính từ thư mục gốc dự án.

| Bạn cần gì? | Mở ở đâu? |
|---|---|
| Data gốc ELLIPSE | [data/01_original_source/official_corpus/](data/01_original_source/official_corpus/) |
| Điểm của từng giám khảo | [data/01_original_source/rater_scores/](data/01_original_source/rater_scores/) |
| ID chia train / validation / test và 5 fold | [data/02_split_manifest/](data/02_split_manifest/) → `essay_split_manifest.csv` |
| Data đã clean, có nội dung bài viết | [data/03_clean_ready_to_use/](data/03_clean_ready_to_use/) |
| Script tạo các CSV clean | [scripts/build_clean_dataset.py](scripts/build_clean_dataset.py) → `build_clean_datasets()` |
| Hàm làm sạch văn bản dùng chung | [src/mla_project/features/preprocessing.py](src/mla_project/features/preprocessing.py) → `clean_text()` |
| Data số đưa vào model | [data/05_model_features/](data/05_model_features/) → `development_features_with_targets.csv` |
| Code trích xuất 14 features | [src/mla_project/features/](src/mla_project/features/) |
| Script chạy trích xuất features | [scripts/phase4_extract_features.py](scripts/phase4_extract_features.py) |
| Code định nghĩa Ridge / Random Forest | [src/mla_project/models/](src/mla_project/models/) → `train_ridge.py`, `train_random_forest.py` |
| Code chọn tham số, fit và lưu model | [src/mla_project/pipelines/training_pipeline.py](src/mla_project/pipelines/training_pipeline.py) |
| Script chạy train | [scripts/phase6_train_models.py](scripts/phase6_train_models.py) |
| Tham số train và grid search | [configs/phase6_training.yaml](configs/phase6_training.yaml), [ridge.yaml](configs/ridge.yaml), [random_forest.yaml](configs/random_forest.yaml) |
| Model đã train, dùng cho kết quả chính | [outputs/phase6/](outputs/phase6/) → 4 file `.joblib` |
| Code dự đoán bài mới | [src/mla_project/pipelines/inference_pipeline.py](src/mla_project/pipelines/inference_pipeline.py) |
| Code tính độ bất đồng / ưu tiên review | [src/mla_project/review/](src/mla_project/review/) |
| Predictions và kết quả đánh giá | [outputs/README.md](outputs/README.md) |
| Báo cáo nộp | xem thư mục `submission/` |
| Báo cáo tuần 9 / 10 | [reports/](reports/) |
| Tài liệu chi tiết | [docs/README.md](docs/README.md) |

## Luồng dữ liệu thực tế

```text
data/01_original_source/official_corpus/   (CSV gốc)
                  +
data/02_split_manifest/essay_split_manifest.csv
                  |
                  +-- scripts/build_clean_dataset.py
                  |      + clean_text(): Unicode NFKC, chuẩn hóa khoảng trắng
                  |      `--> data/03_clean_ready_to_use/ (CSV để đọc / EDA)
                  |
                  `-- scripts/phase4_extract_features.py
                         + clean_text() + bộ trích xuất features
                         + checkpoint: data/04_intermediate_work/
                         `--> data/05_model_features/
                                  |
                     development_features_with_targets.csv + manifest
                                  |
                     scripts/phase6_train_models.py
                                  |
                     pipelines/training_pipeline.py
                         + lọc privacy_review_status == not_flagged
                         + chọn tham số bằng 5-fold CV trên model_train
                         + fit 4 model, xuất dự đoán validation
                                  |
                             outputs/phase6/
                                  |
                       đánh giá / ưu tiên teacher review
                                  |
                 outputs/predictions/ + docs/data/phase*_tables/
```

**CSV clean và bảng features là hai nhánh xuất dữ liệu.** Pipeline train hiện tại
đọc bảng features, không đọc trực tiếp `03_clean_ready_to_use/`. Phase 4 đọc text
từ CSV gốc và dùng cùng hàm `clean_text()`. Việc có thư mục `03` và `05` không có
nghĩa Phase 4 đang đọc từ `03`.

Clean chỉ chuẩn hóa Unicode và khoảng trắng, không sửa ngữ pháp/chính tả của học
sinh. Lỗi ngôn ngữ là thông tin cần giữ để trích xuất features.

## Chọn đúng file dữ liệu

| Mục đích | File | Số dòng trước lọc privacy | Sau lọc `not_flagged` |
|---|---|---:|---:|
| Train / CV | `data/03_clean_ready_to_use/model_train_3128.csv` | 3.128 | 3.050 |
| Validation | `data/03_clean_ready_to_use/validation_783.csv` | 783 | 762 |
| Official Test | `data/03_clean_ready_to_use/official_test_2571.csv` | 2.571 | 2.518 |
| Toàn corpus để tra cứu | `data/03_clean_ready_to_use/full_clean_corpus_6482.csv` | 6.482 | — |

Các CSV clean chưa loại các dòng bị gắn cờ privacy. Trạng thái nằm trong manifest
và file full clean; khi dùng các CSV con phải đối chiếu manifest nếu cần lọc.
Hàm `prepare_training_data()` thực hiện bước lọc khi train.

`development_features_with_targets.csv` gồm 3.911 dòng train + validation, có
targets `Vocabulary`, `Grammar`. `official_test_features.csv` gồm features của
2.571 bài test, không chứa targets. `essay_features.csv` gồm features của toàn
6.482 bài. `feature_v2_model_train_3050.csv` là thử nghiệm mở rộng, không phải
bộ 14 features của model chính.

## Chạy từ đâu?

Chạy lệnh ở **thư mục gốc dự án**, dùng môi trường đã cài theo [docs/setup.md](docs/setup.md).

Kiểm tra đầu vào train mà không fit hay ghi đè kết quả:

```powershell
.venv\Scripts\python.exe scripts/phase6_train_models.py --preflight-only
```

Train một lượt mới vào thư mục riêng khi cần thực nghiệm:

```powershell
.venv\Scripts\python.exe scripts/phase6_train_models.py --output-dir outputs/experiments/retrain_01
```

Lệnh trên chỉ train và xuất artifacts vào thư mục chỉ định. Các script đánh giá
chính vẫn đọc `outputs/phase6/`; chúng không tự chuyển sang lượt train mới.

Các bước tạo lại dữ liệu, nếu thật sự cần tái tạo:

```powershell
.venv\Scripts\python.exe scripts/build_clean_dataset.py
.venv\Scripts\python.exe scripts/phase4_extract_features.py
```

Hai lệnh này ghi lại CSV ở các đường dẫn cố định; Phase 4 cần spaCy, LanguageTool
và Java theo hướng dẫn setup. Dự án hiện đã có dữ liệu và model local nên không
cần chạy lại chỉ để tìm hiểu cấu trúc. Manifest và model chính đã đóng băng;
chi tiết tại [project_freeze_status.md](docs/project_freeze_status.md).

## Quy ước đặt file

- `src/mla_project/`: code Python dùng lại. Thêm logic mới vào đúng module chức năng.
- `scripts/`: điểm chạy tác vụ; xem [mục lục scripts](scripts/README.md).
- `configs/`: cấu hình; một số script lịch sử vẫn khai báo đường dẫn trực tiếp trong code.
- `data/`: input, CSV clean, features và checkpoint dữ liệu.
- `outputs/`: model, predictions và artifacts phát sinh khi chạy.
- `docs/data/`: bảng số liệu kiểm toán/đánh giá hỗ trợ tài liệu, không phải data train.
- `report/`: bản Markdown nháp; `submission/`: báo cáo nộp; `reports/`: báo cáo và kết quả theo tuần.
- `interview_pack/`: bộ tài liệu thuyết trình/vấn đáp đã đóng gói.
- `scratch/`: file làm việc tạm; `.venv/`, `.venv_gec/`: môi trường local.

Các file `src/data.py`, `src/models.py`, `src/features.py`, ... là lớp tương thích
cho import cũ. Code chính nằm trong `src/mla_project/`.

Data riêng tư, features và model phần lớn bị Git bỏ qua. Có trên máy hiện tại
không đồng nghĩa chúng có sẵn khi clone repo; xem [data/README.md](data/README.md).

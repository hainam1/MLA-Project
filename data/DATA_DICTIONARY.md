# ELLIPSE Dataset — Data Dictionary & Catalog

Tài liệu này cung cấp danh mục chi tiết, từ điển dữ liệu (data dictionary), và hướng dẫn cấu trúc toàn bộ các file CSV trong thư mục `data/`.

---

## 1. Bản Đồ Phân Bổ Thư Mục & Vai Trò (`data/`)

```
data/
├── 01_original_source/                   # Dữ liệu nguồn bất biến
│   ├── official_corpus/                  # Hai bảng bài luận chính thức
│   ├── rater_scores/                     # Điểm riêng của hai giám khảo
│   └── documentation/                    # Rubric, nguồn, checksum, README gốc
├── 02_split_manifest/                    # Manifest chia tập chống rò rỉ
│   └── essay_split_manifest.csv          # 6,482 ID thuộc train / validation / test
├── 03_clean_ready_to_use/                # ★ KHUYÊN DÙNG: dữ liệu sạch
│   ├── model_train_3128.csv              # Tập train kèm 5 folds
│   ├── validation_783.csv                # Tập validation
│   ├── official_test_2571.csv            # Tập test chính thức
│   └── full_clean_corpus_6482.csv        # Toàn bộ corpus sạch
├── 04_intermediate_work/                 # Checkpoint và kiểm toán tạm thời
│   ├── phase4_feature_checkpoint.csv     # Checkpoint 14 đặc trưng ngôn ngữ
│   └── improvement_audit/                # Dữ liệu kiểm toán lỗi chuyên sâu
└── 05_model_features/                    # Ma trận đặc trưng số học hoàn chỉnh
    ├── development_features_with_targets.csv # 3,911 dòng: 14 features + targets (Vocabulary, Grammar)
    ├── essay_features.csv                # 6,482 dòng: Toàn bộ ma trận đặc trưng
    └── official_test_features.csv        # 2,571 dòng: Features của tập test chính thức
```

---

## 2. Từ Điển Dữ Liệu Bảng Sạch (`data/03_clean_ready_to_use/*.csv`)

Tất cả các bảng trong `data/03_clean_ready_to_use/` đã được chuẩn hóa tên cột theo chuẩn `snake_case`, làm sạch văn bản (Unicode NFKC, xóa khoảng trắng thừa), và loại bỏ các cột rác tính toán dư thừa từ file gốc.

### Bảng Định Nghĩa Chi Tiết Các Cột

| Tên Cột | Kiểu Dữ Liệu | Giá Trị Cho Phép / Dải Giá Trị | Ví Dụ | Giải Thích Chi Tiết |
|---|---|---|---|---|
| `essay_id` | `string` | Chuỗi 10-12 ký tự hex/số | `"5661280443"` | Mã định danh duy nhất của mỗi bài viết. |
| `prompt` | `string` | Tên đề bài văn | `"Benefits of a problem"` | Đề bài văn học sinh được yêu cầu viết. |
| `essay_text` | `string` | Văn bản tiếng Anh | `"Imagine if you..."` | Toàn văn bài viết gốc (đã trim khoảng trắng đầu/cuối). |
| `clean_text` | `string` | Văn bản chuẩn hóa | `"Imagine if you..."` | Văn bản sau khi chuẩn hóa Unicode NFKC & thu gọn space. |
| **`vocabulary`** | `float` | `1.0` – `5.0` (bước 0.5) | `3.5` | **Target cốt lõi 1:** Điểm Từ vựng (do người chấm gán). |
| **`grammar`** | `float` | `1.0` – `5.0` (bước 0.5) | `4.0` | **Target cốt lõi 2:** Điểm Ngữ pháp (do người chấm gán). |
| `overall` | `float` | `1.0` – `5.0` (bước 0.5) | `4.0` | Điểm đánh giá tổng thể (Holistic score). |
| `cohesion` | `float` | `1.0` – `5.0` (bước 0.5) | `3.5` | Điểm tính liên kết và mạch lạc. |
| `syntax` | `float` | `1.0` – `5.0` (bước 0.5) | `4.0` | Điểm cấu trúc cú pháp câu. |
| `phraseology` | `float` | `1.0` – `5.0` (bước 0.5) | `3.5` | Điểm cách diễn đạt cụm từ / ngữ pháp nâng cao. |
| `conventions` | `float` | `1.0` – `5.0` (bước 0.5) | `4.0` | Điểm quy ước viết (chính tả, viết hoa, chấm câu). |
| `grade` | `integer` | `8`, `9`, `10`, `11`, `12` | `8` | Khối lớp học sinh đang theo học tại trường. |
| `gender` | `string` | `"Male"`, `"Female"` | `"Male"` | Giới tính của người viết. |
| `race_ethnicity` | `string` | Tên nhóm sắc tộc | `"Hispanic/Latino"` | Sắc tộc của người viết. |
| `ses` | `string` | Phân loại kinh tế xã hội | `"Economically disadvantaged"` | Tình trạng kinh tế xã hội của học sinh. |
| `cv_fold` | `Int64` *(chỉ có ở model_train_3128.csv)* | `0`, `1`, `2`, `3`, `4` | `0` | Fold phân chia Cross-Validation (5 folds cân bằng). |

### Các Cột Bổ Sung Trong `full_clean_corpus_6482.csv`:
- `split`: Tên phân vùng dữ liệu (`"model_train"`, `"validation"`, `"official_test"`).
- `source_partition`: Nguồn gốc ban đầu từ tác giả (`"official_train"`, `"official_test"`).
- `privacy_review_status`: Trạng thái rà soát PII (`"not_flagged"`, `"flagged_by_rater"`).

---

## 3. Bảng Ánh Xạ Giữa Raw và Clean (Data Mapping)

Để đảm bảo tính minh bạch khoa học, dưới đây là bảng đối chiếu cách chuyển đổi từ dữ liệu thô sang dữ liệu sạch:

| Cột Gốc (`data/01_original_source/`) | Cột Chuẩn (`data/03_clean_ready_to_use/`) | Xử Lý Làm Sạch | Lý Do / Ghi Chú |
|---|---|---|---|
| `text_id_kaggle` | `essay_id` | Chuẩn hóa string | Tên cột chuẩn, tránh nhầm lẫn nền tảng Kaggle |
| `full_text` | `essay_text` & `clean_text` | Strip whitespace, Unicode NFKC | Cung cấp cả bản gốc và bản đã chuẩn hóa space |
| `prompt` | `prompt` | Giữ nguyên string | Tên đề bài viết |
| `Vocabulary` | `vocabulary` | Chuyển `float` | Target cốt lõi (lower_case) |
| `Grammar` | `grammar` | Chuyển `float` | Target cốt lõi (lower_case) |
| `Overall`, `Cohesion`, ... | `overall`, `cohesion`, ... | Chuyển `float` | Thang điểm phụ theo rubric |
| `grade`, `gender`, `SES` | `grade`, `gender`, `ses` | Chuẩn hóa kiểu dữ liệu | Dữ liệu nhân khẩu học phục vụ phân tích fairness |
| `num_words`, `num_words2`, `num_words3` | *(Loại bỏ khỏi clean)* | Không dùng | Các cột thô do tác giả tính sơ bộ, không nhất quán |
| `num_sent`, `num_para`, `num_word_div_para` | *(Loại bỏ khỏi clean)* | Không dùng | Được thay thế bằng bộ 14 feature chính xác ở Phase 4 |
| `MTLD`, `TTR`, `Type`, `Token` | *(Loại bỏ khỏi clean)* | Không dùng | Tính toán sơ lược cũ; project đã có feature extractor riêng |
| `task`, `set` | *(Loại bỏ khỏi clean)* | Thay bằng cột `split` | Không mang thông tin hữu ích |

---

## 4. Thống Kê Phân Vùng Dữ Liệu (Split Balance)

Phân vùng được thực hiện bằng phương pháp phân tầng theo đề bài (Prompt-Stratified) và nhóm các bài viết trùng lặp chính xác (Exact-text Grouping), đảm bảo **tuyệt đối không rò rỉ dữ liệu (No Data Leakage)**:

| Phân Vùng (`split`) | File CSV Tương Ứng | Số Lượng Bài Viết | Tỷ Lệ | Vai Trò Trong Dự Án |
|---|---|---|---|---|
| `model_train` | `data/03_clean_ready_to_use/model_train_3128.csv` | **3,128** | ~48.3% | Huấn luyện mô hình Ridge & Random Forest (kèm 5-fold CV) |
| `validation` | `data/03_clean_ready_to_use/validation_783.csv` | **783** | ~12.1% | Thẩm định, điều chỉnh ngưỡng, phân tích lỗi |
| `official_test` | `data/03_clean_ready_to_use/official_test_2571.csv` | **2,571** | ~39.6% | Đánh giá tổng kết cuối cùng (Held-out Test) |
| **Tổng Cộng** | `data/03_clean_ready_to_use/full_clean_corpus_6482.csv` | **6,482** | **100%** | Toàn bộ tập dữ liệu ELLIPSE sạch |

Phân bố 5 Folds trong tập huấn luyện `data/03_clean_ready_to_use/model_train_3128.csv`:
- Fold 0: 626 bài
- Fold 1: 626 bài
- Fold 2: 625 bài
- Fold 3: 626 bài
- Fold 4: 625 bài

---

## 5. Hướng Dẫn Sử Dụng Trong Python

Để đọc dữ liệu một cách nhanh chóng và an toàn trong mã nguồn hoặc Jupyter Notebook:

```python
from mla_project.data import load_clean_data

# 1. Đọc tập train đã gán fold
train_df = load_clean_data("train")
print(f"Train shape: {train_df.shape}")  # (3128, 16)
print(train_df[["essay_id", "prompt", "vocabulary", "grammar", "cv_fold"]].head())

# 2. Đọc tập validation
val_df = load_clean_data("val")
print(f"Validation shape: {val_df.shape}")  # (783, 15)

# 3. Đọc tập test chính thức
test_df = load_clean_data("test")
print(f"Test shape: {test_df.shape}")  # (2571, 15)

# 4. Đọc toàn bộ kho dữ liệu
all_df = load_clean_data("all")
print(f"Total shape: {all_df.shape}")  # (6482, 19)
```

---

## 6. Lệnh Tái Lập (Reproducibility)

Tất cả các file sạch trong `data/03_clean_ready_to_use/` có thể được tái tạo lại 100% bất kỳ lúc nào bằng lệnh:

```powershell
python scripts/build_clean_dataset.py
```

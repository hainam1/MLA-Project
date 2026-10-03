# Bản đồ dữ liệu của dự án

## Kết luận ngắn gọn để trình bày

Dự án chỉ sử dụng **một corpus chính: ELLIPSE** (English Language Learner
Insight, Proficiency and Skills Evaluation). Corpus gồm **6.482 bài luận tiếng
Anh của người học**, có điểm chấm theo rubric từ 1 đến 5. Mô hình trong dự án dự
đoán riêng hai tiêu chí **Vocabulary** và **Grammar**.

Các file trong `data/` không phải là nhiều dataset độc lập. Chúng là các phiên
bản của cùng corpus ở từng bước xử lý: dữ liệu gốc, quy tắc chia tập, dữ liệu
sạch, checkpoint trung gian và ma trận đặc trưng.

Nguồn: <https://github.com/scrosseye/ELLIPSE-Corpus>  
Giấy phép: CC BY-NC-SA 4.0.

## Cấu trúc thư mục đã sắp xếp

```text
data/
├── 01_original_source/          # Dữ liệu và tài liệu gốc, chỉ đọc
│   ├── official_corpus/         # 2 bảng bài luận chính thức
│   ├── rater_scores/            # Điểm riêng của hai giám khảo, chỉ để kiểm toán
│   └── documentation/           # Rubric, nguồn, checksum và README của tác giả
├── 02_split_manifest/           # Danh sách ID quyết định train/validation/test
├── 03_clean_ready_to_use/       # Dữ liệu sạch, dễ dùng và dễ trình bày
├── 04_intermediate_work/        # Checkpoint/kết quả kiểm tra tạm thời
└── 05_model_features/           # 14 đặc trưng số dùng trực tiếp cho mô hình
```

Các số `01` đến `05` thể hiện đúng thứ tự của pipeline dữ liệu.

## Mỗi file là gì?

### 01 — Dữ liệu nguồn gốc

| File | Dòng | Vai trò |
|---|---:|---|
| `01_original_source/official_corpus/ELLIPSE_Final_github_train.csv` | 3.911 | Phần development do tác giả công bố; dự án chia tiếp thành model-train và validation. |
| `01_original_source/official_corpus/ELLIPSE_Final_github_test.csv` | 2.571 | Tập test chính thức, giữ độc lập đến bước đánh giá cuối. |
| `01_original_source/rater_scores/ellipsis_raw_rater_scores_anon_all_essay.csv` | 8.890 | Điểm riêng của hai giám khảo; chỉ dùng phân tích độ tin cậy, không dùng làm đầu vào mô hình. |
| `01_original_source/documentation/ELL_Rubrics.docx` | — | Rubric định nghĩa Overall và 6 tiêu chí chấm. |

Lưu ý: file raw-rater có 6.482 dòng mang `text_id_kaggle` và 2.408 dòng thiếu
ID. Trong 6.482 ID đó, 14 giá trị bị mã hóa dạng scientific notation nên manifest
đánh dấu `unresolved_raw_id_link`. Pipeline chỉ giữ các ID khớp chính xác và
thuộc allowlist development hợp lệ; phần thiếu/không khớp ID và official test
không đi vào phân tích cải tiến mô hình.

### 02 — Quy tắc chia tập

`02_split_manifest/essay_split_manifest.csv` có 6.482 dòng, mỗi bài luận đúng
một dòng. File này lưu `split`, `cv_fold`, nguồn ban đầu, hash văn bản và trạng
thái rà soát riêng tư. Đây là **manifest**, không phải một dataset nội dung mới.

### 03 — Dữ liệu sạch nên dùng

| Nhu cầu | File | Dòng |
|---|---|---:|
| Huấn luyện và 5-fold CV | `03_clean_ready_to_use/model_train_3128.csv` | 3.128 |
| Chọn mô hình/tham số | `03_clean_ready_to_use/validation_783.csv` | 783 |
| Đánh giá cuối cùng | `03_clean_ready_to_use/official_test_2571.csv` | 2.571 |
| EDA/toàn bộ corpus | `03_clean_ready_to_use/full_clean_corpus_6482.csv` | 6.482 |

Tên cột đã được chuẩn hóa về `snake_case`; văn bản được chuẩn hóa Unicode NFKC
và khoảng trắng. Ba tập con cộng lại đúng 6.482 bài, không trùng `essay_id`.

### 04 — File trung gian

`04_intermediate_work/phase4_feature_checkpoint.csv` là checkpoint để có thể tiếp
tục quá trình trích xuất đặc trưng. Thư mục `improvement_audit/` chứa mẫu kiểm
tra lỗi có nội dung bài luận và bị Git bỏ qua. Không dùng các file này để giới
thiệu như dataset huấn luyện chính.

### 05 — Dữ liệu đặc trưng cho mô hình

| File | Dòng | Nội dung |
|---|---:|---|
| `05_model_features/essay_features.csv` | 6.482 | 14 đặc trưng ngôn ngữ của toàn corpus, không kèm target. |
| `05_model_features/development_features_with_targets.csv` | 3.911 | Đặc trưng development + Vocabulary/Grammar để huấn luyện và thẩm định. |
| `05_model_features/official_test_features.csv` | 2.571 | Đặc trưng test chính thức, không nạp target trong bước trích xuất. |

## Những gì đã được lọc và làm rõ

- Giữ nguyên mọi file nguồn và checksum; không sửa nội dung dữ liệu gốc.
- Tách corpus chính, điểm giám khảo và tài liệu rubric thành ba thư mục riêng.
- Đổi tên file dữ liệu sạch để nhìn tên là biết mục đích và số dòng.
- Loại bản sao `04_intermediate_work/essays_clean.csv` cũ vì checksum trùng hoàn
  toàn với `full_clean_corpus_6482.csv`; script không còn tạo bản sao này.
- Giữ checkpoint và bảng kiểm toán ở khu vực trung gian, tách khỏi dataset dùng
  để huấn luyện.

## Lệnh tái tạo và cách nạp

```powershell
python scripts/build_clean_dataset.py
```

```python
from mla_project.data import load_clean_data

train_df = load_clean_data("train")
validation_df = load_clean_data("validation")
test_df = load_clean_data("official_test")
all_df = load_clean_data("all")
```

Chi tiết từng cột xem tại [DATA_DICTIONARY.md](DATA_DICTIONARY.md). Nguồn và
checksum xem tại
[`01_original_source/documentation/SOURCE.md`](01_original_source/documentation/SOURCE.md).

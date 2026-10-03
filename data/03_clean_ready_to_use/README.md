# Dữ liệu sạch, sẵn sàng sử dụng

Đây là thư mục nên mở khi cần trình bày hoặc nạp dữ liệu bài luận vào Python.
Tất cả file được tạo lại từ dữ liệu nguồn và manifest bằng:

```powershell
python scripts/build_clean_dataset.py
```

| File | Dòng | Cột | Mục đích |
|---|---:|---:|---|
| `model_train_3128.csv` | 3.128 | 16 | Huấn luyện mô hình; có `cv_fold` từ 0 đến 4. |
| `validation_783.csv` | 783 | 15 | Chọn mô hình, siêu tham số và phân tích lỗi. |
| `official_test_2571.csv` | 2.571 | 15 | Đánh giá cuối cùng; không dùng để tuning. |
| `full_clean_corpus_6482.csv` | 6.482 | 19 | EDA và truy vết toàn corpus; có nhãn split và metadata. |

Ba file train, validation và test là các tập không giao nhau, tổng cộng đúng
6.482 `essay_id` duy nhất. `full_clean_corpus_6482.csv` là bản hợp nhất của ba
tập đó, không phải một nguồn dữ liệu khác.

Hai target chính của dự án là `vocabulary` và `grammar`, đều theo thang 1–5.
Chi tiết schema xem [../DATA_DICTIONARY.md](../DATA_DICTIONARY.md).

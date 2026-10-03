# Thử nghiệm feature v2 để giảm lệch điểm Vocabulary và Grammar

## Phạm vi và kết luận

Đã trích xuất 9 đặc trưng thử nghiệm từ **3.050 bài model-train hợp lệ** và so sánh
Ridge/Random Forest bằng 5 fold đã cố định. Không có nhãn validation hoặc official
test đi vào việc huấn luyện, chọn đặc trưng hay tính bảng kết quả bên dưới.

Thêm đủ 9 đặc trưng làm MAE giảm cho cả bốn cặp mô hình–tiêu chí. Tuy nhiên,
**không ứng viên nào đạt đủ các điều kiện chấp nhận đã chốt trước** trong
[`model_improvement_protocol.md`](model_improvement_protocol.md). Đặc biệt, độ
lệch có hướng lớn nhất ở hai đầu thang điểm giảm dưới 6%, trong khi yêu cầu là
ít nhất 20%. Vì vậy baseline v1 vẫn là bản được duyệt; feature v2 chưa được dùng
để chấm bài mới hay đánh giá test.

## Kết quả 5-fold OOF trên model-train

Giá trị trong bảng là **MAE** (thấp hơn là tốt hơn). `v1` dùng 14 đặc trưng cũ;
`v1 + v2` dùng 14 đặc trưng cũ và 9 đặc trưng mới. Cả hai dùng cùng tham số đã
chọn trước để cô lập ảnh hưởng của đặc trưng.

| Tiêu chí | Ridge v1 | Ridge v1 + v2 | RF v1 | RF v1 + v2 |
|---|---:|---:|---:|---:|
| Vocabulary | 0.3724 | **0.3639** | 0.3726 | **0.3629** |
| Grammar | 0.4636 | **0.4555** | 0.4577 | **0.4489** |

RF v1 + v2 cải thiện MAE ở cả 5 fold cho cả hai tiêu chí. Ridge v1 + v2 cải thiện
4/5 fold Vocabulary và 3/5 fold Grammar. Những thay đổi này là kết quả sàng lọc
trên train, chưa phải ước lượng hiệu năng độc lập.

Thử thêm trọng số nghịch căn bậc hai tần suất ba vùng điểm trên toàn bộ feature
v2. Với RF, sai lệch lớn nhất ở hai đầu giảm **11.80% Vocabulary** và **11.91%
Grammar**, nhưng MAE vùng giữa tăng tương ứng **0.0230** và **0.0144** so với
RF v1. MAE chung của bản có trọng số là **0.3635 Vocabulary** và **0.4497
Grammar**. Cả hai vẫn dưới yêu cầu giảm sai lệch 20%, nên chưa được chấp nhận.
Ridge có trọng số cũng không đạt cổng và cải thiện qua ít fold hơn.

### Sai lệch ở hai vùng điểm ngoài

`bias = dự đoán − điểm người chấm`. Giá trị dương ở nhóm điểm thấp nghĩa là chấm
dư; giá trị âm ở nhóm điểm cao nghĩa là chấm thiếu.

| Tiêu chí / mô hình | Điểm thấp v1 → v2 | Điểm cao v1 → v2 |
|---|---:|---:|
| Vocabulary / Ridge | +0.539 → +0.510 | −0.621 → −0.593 |
| Vocabulary / RF | +0.592 → +0.570 | −0.628 → −0.607 |
| Grammar / Ridge | +0.473 → +0.454 | −0.813 → −0.781 |
| Grammar / RF | +0.495 → +0.481 | −0.779 → −0.754 |

Cải thiện là có thật trên train OOF nhưng còn nhỏ. Với RF v1 + v2, MAE trung
bình ba vùng điểm giảm **3.15% Vocabulary** và **2.40% Grammar**, dưới mức tối
thiểu 10% trong giao thức. Độ lệch hai đầu giảm lần lượt **3.41%** và **3.23%**,
dưới mức tối thiểu 20%.

## 9 đặc trưng đã thử

- Từ vựng: tỷ lệ từ nội dung tần suất thấp, phân vị 25% tần suất từ nội dung,
  độ đa dạng lemma theo cửa sổ 50 từ.
- Chính tả: số phát hiện `misspelling` trên 100 từ và độ đa dạng quy tắc phát
  hiện. Theo rubric, chính tả thuộc *Conventions*, nên đây là nhóm ablation riêng;
  nó không được coi là phép đo Vocabulary trực tiếp.
- Ngữ pháp: độ đa dạng và mức lặp của `ruleId` trong các phát hiện grammar.
- Cú pháp: khoảng cách phụ thuộc trung bình và độ sâu cây phụ thuộc trung bình.

Các phép tính được định nghĩa trong
[`feature_v2.py`](../src/mla_project/features/feature_v2.py). Chúng là chỉ số
tự động, không xác nhận một phát hiện LanguageTool là lỗi thật. Trong mẫu kiểm
tra 30 bài, nhóm Vocabulary bị dự đoán quá cao có cả tỷ lệ từ “hiếm” và số phát
hiện chính tả cao; từ viết sai có thể là một yếu tố gây nhiễu chỉ số tần suất,
nhưng mẫu này quá nhỏ để kết luận nhân quả. Bảng pilot chỉ dùng kiểm tra schema,
không dùng chọn đặc trưng. Phiếu rà rubric riêng tư đã được tạo tại
`data/04_intermediate_work/improvement_audit/feature_v2_rubric_review_private.csv`;
các ô nhận xét để trống và cần người có chuyên môn chấm xác nhận trước khi rút
ra kết luận về lỗi thật/lỗi giả của LanguageTool.

## Kết quả ablation

Thử riêng nhóm chính tả cho RF cho MAE Vocabulary **0.3650** và Grammar
**0.4492**; đây là nhóm đơn lẻ có tác động lớn nhất. Thử riêng hai chỉ số quy
tắc grammar gần như không thay đổi kết quả. Gộp tất cả đạt MAE tốt hơn nhóm đơn
lẻ, nhưng vẫn không đạt cổng về sai lệch hai đầu. Xem bảng đầy đủ:

- [`feature_v2_oof_overall.csv`](data/improvement_tables/feature_v2_oof_overall.csv)
- [`feature_v2_oof_bands.csv`](data/improvement_tables/feature_v2_oof_bands.csv)
- [`feature_v2_acceptance.csv`](data/improvement_tables/feature_v2_acceptance.csv)
- [`feature_v2_pilot_group_means.csv`](data/improvement_tables/feature_v2_pilot_group_means.csv)

## Tái lập và bước nghiên cứu kế tiếp

```powershell
uv run python scripts/feature_v2_extract_train.py
uv run python scripts/feature_v2_pilot.py
uv run python scripts/feature_v2_train_only_ablation.py
```

Checkpoint trích xuất nằm trong `data/04_intermediate_work/`; bảng numeric
train-only nằm trong `data/05_model_features/`. Cả hai được Git bỏ qua. Script
ablation ghi dự đoán OOF text-free vào `outputs/improvement_study/`; các bảng
tổng hợp ở `docs/data/improvement_tables/`.

Hướng tiếp theo có cơ sở hơn là đối chiếu một số bài sai nặng với rubric bằng
người chấm, đặc biệt **độ chính xác của từ trong ngữ cảnh**, dạng từ và các lỗi
ngữ pháp mà LanguageTool bỏ sót hoặc báo nhầm. Định nghĩa đặc trưng mới phải
được cố định trước khi chạy thêm ablation train-only. Chỉ sau khi một phương án
đạt cổng mới xem xét đánh giá xác nhận độc lập; không chọn phương án dựa trên
762 bài validation đã dùng ở Phase 7.

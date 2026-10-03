# Ảnh so sánh kết quả feature v2

Ba biểu đồ này dùng cho báo cáo hoặc slide. Mỗi ảnh có bản PNG độ phân giải cao và bản SVG để phóng to không vỡ nét.

1. `01_mae_truoc_sau`: MAE của Ridge và Random Forest, v1 so với v1 + 9 đặc trưng v2. MAE thấp hơn nghĩa là sai số trung bình nhỏ hơn.
2. `02_lech_diem_thap_cao`: độ lệch có hướng của hai mô hình ở nhóm điểm thấp và điểm cao. Giá trị dương là chấm dư; âm là chấm thiếu. Bản v2 giảm độ lệch nhưng chưa xử lý triệt để.
3. `03_danh_doi_trong_so_rf`: MAE của Random Forest theo ba nhóm điểm. Tăng trọng số giúp rõ hơn ở nhóm điểm cao, nhưng làm sai số nhóm giữa tăng.

Nguồn số liệu: [`feature_v2_oof_overall.csv`](../../data/improvement_tables/feature_v2_oof_overall.csv) và [`feature_v2_oof_bands.csv`](../../data/improvement_tables/feature_v2_oof_bands.csv). Đây là kết quả **5-fold OOF trên 3.050 bài model-train**, không phải đánh giá độc lập trên validation/test. Không ứng viên nào đạt toàn bộ ngưỡng chấp nhận đã định trước, nên chưa thể nói v2 đã sửa xong vấn đề chấm lệch điểm.

Tạo lại ảnh từ bảng số liệu:

```powershell
.\.venv\Scripts\python.exe scripts/plot_feature_v2_comparison.py
```

# Lịch sử dùng Test: chỉ trích hồ sơ đã lưu
Kết quả sau nhiều lần chọn là thăm dò.

| Mốc UTC | Sự kiện | Bằng chứng |
|---|---|---|
| Lần 1, báo cáo tuần 9; ngày chạy đầu chưa xác định | D = 47/208, N=2518, k=504; exact p=0,1883246714 | reports/week9/RESULTS_week9.md, Task 0; chronology không xác định được ngày truy cập đầu |
| 19/10/2026 05:41:08 UTC | Commit khóa 4e381150edf08d49a134505e669058f1e0d27b48 | git show -s --format=%cI 4e38115 ghi 12:41:08 +07:00; đổi sang UTC |
| 26/10/2026 07:14:53 UTC | Dừng khớp dự đoán Vocabulary: 2015 dòng, max lệch 4,995115432393504e-12 > atol 1e-12; chưa tính tín hiệu | log STOPPED; commit b32ad4e35d0fc9546dc07d090526a59518641536 |
| Sau lần dừng, chưa có giờ riêng được xác nhận | Chẩn đoán chỉ trên development; định dạng lưu %.12g giải thích sai số; sửa atol=1e-11, rtol=0 | RESULTS_tree_spread_second_use.md, Sự cố lần chạy đầu |
| Sau sửa dung sai, trước 07:27 UTC; chưa có giờ riêng | Chốt chặn từ chối vì log tồn tại; không mở Test ở lần gọi này | RESULTS_tree_spread_second_use.md, Sự cố chốt chặn; script hash trung gian 15bd8ee6c5d2611fd09bba32202e86cdb8398e3d433845bd55f89a1537e75ec6 |
| 26/10/2026 07:27:32 UTC | Hoàn thành: cây 55/208, kỳ vọng 41,6330421; p=0,01158570685 so ngẫu nhiên | log _attempt2 COMPLETED, pre_signal_checks PASS; run commit cdc0a6a871d1f7ae9458f920157853159d6f9318; result commit 97159a6b9a10e46b881b8e1a66cd278171dff4f6 |

File khóa docs/signal_lock_tree_spread.md SHA256:
`d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca`.
Script cuối scripts/tree_spread_official_test_second_use.py SHA256:
`cc7bdd6efd8c0cf23a4f6dbd5673e17a5c8501aaf72e77fb0b99e96090b31e05`.
Hai hash đã kiểm lại trực tiếp khi dựng gói; không chạy script đánh giá Test.
Sự cố đầu dùng script hash df70177723d5fdeee72e1dc65a55fc242e19fbcc9b6ad2a1052cd1fda839240b.
Nguồn toàn dòng thời gian: reports/week9/RESULTS_tree_spread_second_use.md và hai log JSON; các trích số an toàn nằm trong 08_tai_lap/nguon.
Chênh 55-47=8 là số đếm Test, chưa có kiểm định ghép cặp so với D. Khoảng +8 [-11,27] là của development, không gán cho Test.

# RESULTS — Official Test lần dùng thứ hai: DỪNG trước tính tín hiệu

Official Test lần dùng thứ hai, cho tín hiệu đã khóa, dùng lại RF đã lưu từ tuần 9; không phải xác nhận độc lập sạch; không có tín hiệu nào khác được thử

## Cho phép và nhận diện bản chạy

- Ngày thầy cho phép: **26/10/2026**. Nguồn: **nhận xét tuần 10 của thầy Khánh**, theo xác nhận của người phụ trách trong cuộc trao đổi.
- Commit điền ngày, chỉ chứa file nháp: `b32ad4e35d0fc9546dc07d090526a59518641536`.
- Nháp: `reports/week9/RESULTS_tree_spread_second_use_DRAFT.md`; SHA256 trước chạy: `f70341b9787982396eabb267a62b18a3fe8875c086bfffedae555fec77222189`.
- Script: `scripts/tree_spread_official_test_second_use.py`; SHA256 khớp trước chạy và do script ghi: `df70177723d5fdeee72e1dc65a55fc242e19fbcc9b6ad2a1052cd1fda839240b`.
- Commit khóa: `4e381150edf08d49a134505e669058f1e0d27b48`; SHA256 file khóa: `d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca`.
- Commit lúc chạy: `b32ad4e35d0fc9546dc07d090526a59518641536`; thời điểm bắt đầu do script ghi: `2026-10-26T07:14:53.007659+00:00`, tức **14:14:53 ngày 26/10/2026, UTC+07:00**.

Đã gọi đúng **một lần**, mã thoát **2**, không chạy lại:

```text
.venv/Scripts/python.exe scripts/tree_spread_official_test_second_use.py --i-have-permission
```

## Kiểm tra dừng và kết quả thực tế

| Kiểm tra / trường | Trạng thái |
|---|---|
| Hash file khóa, hai RF và bốn nguồn số đã lưu | Khớp |
| Cấu hình pipeline RF đã lưu | Qua kiểm tra, không huấn luyện lại |
| Tập đủ điều kiện | Qua kiểm tra 2.518 bài và khớp tập ID với nhãn/dự đoán đã lưu |
| Dự đoán RF Vocabulary khớp bảng cũ | **Không đạt**: 2.015 dòng lệch quá atol=1e-12, rtol=0 |
| Sai lệch tuyệt đối lớn nhất ở Vocabulary | **4,995115432393504e-12** |
| Kiểm tra dự đoán RF Grammar | Chưa thực hiện, vì đã dừng ở Vocabulary |
| Kiểm tra tập sai lớn và số lượng 208 | Chưa thực hiện; không suy ra đã đạt |
| Ngân sách thực tính | Chưa tính; kế hoạch là ceil(20% × N), tương ứng 504 nếu N=2.518 |
| Độ lệch chuẩn giữa các cây / tín hiệu đã khóa | **Chưa tính** |
| Số bắt được / kỳ vọng ngẫu nhiên / p chính xác một phía | **Không có kết quả**, vì dừng trước tính tín hiệu |

Thông báo của script:

```text
STOP: RF prediction mismatch: vocabulary; mismatched_rows=2015; max_absolute_difference=4.995115432393504e-12; atol=1e-12; rtol=0; no signal result released.
```

Không đổi dung sai, không suy đoán nguyên nhân sai lệch, không tính tín hiệu khác và không chạy lại. Đây là hồ sơ của một lần truy cập Test bị dừng, không phải kết quả đánh giá độ phân tán cây.

## Log và lịch sử Test

Nguồn trực tiếp: [tree_spread_official_test_second_use_log.json](tree_spread_official_test_second_use_log.json), `status=STOPPED`, trường `failure`; không có trường `result` hoặc `pre_signal_checks=PASS`.

Sau khi script dừng, chỉ bổ sung metadata cho phép, nguồn xác nhận, hash nháp và số lần gọi vào log. Trường `operator_annotation` ghi rõ việc bổ sung sau chạy và SHA256 của log gốc trước bổ sung; các trường thực thi do script ghi được giữ nguyên, ngoại trừ điền ô `teacher_permission_date` vốn trống. Không chạy lại script hoặc đọc lại nguồn Test khi bổ sung metadata và viết RESULTS.

Lần dùng đầu là đánh giá chính Phase 9 được báo cáo và kiểm tra lại từ dự đoán lưu sẵn ở tuần 9; ngày truy cập đầu tiên không xác định được từ lịch sử hiện có. Nguồn: [t0_provenance.md](t0_provenance.md). Các phân tích mở rộng sau đánh giá chính dùng development/Validation. Lần dùng thứ hai được phép ở đây đã truy cập đặc trưng, nhãn số và dự đoán Test cho kiểm tra tính toàn vẹn, rồi dừng trước tính tín hiệu. Không mở CSV bài luận gốc hoặc corpus gộp; không in nội dung bài luận.

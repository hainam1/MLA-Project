# RESULTS — Official Test lần dùng thứ hai: hoàn thành tín hiệu đã khóa

Official Test lần dùng thứ hai, cho tín hiệu đã khóa, dùng lại RF đã lưu từ tuần 9; không phải xác nhận độc lập sạch; không có tín hiệu nào khác được thử

## Kết quả hoàn thành sau sửa chốt chặn log

Ngày thầy cho phép: **26/10/2026**, nguồn **nhận xét tuần 10 của thầy Khánh**, theo xác nhận của người phụ trách. Trước chạy, hash script và cả hai RF khớp các giá trị đã chốt; nháp có ngày cho phép, còn mục Sự cố nằm trong RESULTS thật này. Log `_attempt2` chưa tồn tại; log STOPPED cũ được giữ nguyên.

Đã gọi script **đúng một lần trong lần cho phép chạy hiện tại**, mã thoát **0**; thời điểm bắt đầu do script ghi là `2026-10-26T07:27:32.910903+00:00`, tức **14:27:32 ngày 26/10/2026, UTC+07:00**. Không gọi lại hoặc tính thêm tín hiệu, không huấn luyện lại.

```text
.venv/Scripts/python.exe scripts/tree_spread_official_test_second_use.py --i-have-permission
```

| Trường | Kết quả do script ghi |
|---|---:|
| Số bài đủ điều kiện N | **2.518** |
| Số bài RF sai lớn K | **208** |
| Ngân sách ceil(20% × N) | **504** |
| Số bài tín hiệu cây bắt được C | **55** |
| Kỳ vọng ngẫu nhiên kK/N | **41,6330420969023 ≈ 41,63** |
| p chính xác một phía, hypergeom.sf(C−1,N,K,k) | **0,011585706847145556** |

Tín hiệu duy nhất là max(std của 300 cây Vocabulary, std của 300 cây Grammar), ddof=0; xếp giảm dần, hòa thì essay_id dạng chuỗi tăng dần. Dung sai khớp dự đoán là `atol=1e-11, rtol=0` cho cả hai RF. Log xác nhận `pre_signal_checks=PASS`: hash mô hình khớp, dự đoán hai đích khớp bảng cũ theo dung sai, tập ID sai lớn khớp, N=2.518 và K=208 trước khi tính tín hiệu.

So với **D đã có 47/208** tại cùng ngân sách 504, tín hiệu cây bắt **55/208**, cao hơn **8 bài**. Mốc D chỉ trích từ hồ sơ tuần 9; không tính lại D trên Test. Đây là so sánh số đếm, không có kiểm định trực tiếp sự hơn kém với D trong lần chạy này. p trên là kiểm định một phía so với hàng đợi ngẫu nhiên cùng ngân sách, không phải p so với D. Nguồn D: [RESULTS_week9.md, Task 0](RESULTS_week9.md).

Nguồn kết quả mới: [tree_spread_official_test_second_use_log_attempt2.json](tree_spread_official_test_second_use_log_attempt2.json), `status=COMPLETED`, `pre_signal_checks` và `result`.

- Commit lúc chạy: `cdc0a6a871d1f7ae9458f920157853159d6f9318`.
- SHA256 script: `cc7bdd6efd8c0cf23a4f6dbd5673e17a5c8501aaf72e77fb0b99e96090b31e05`.
- SHA256 file khóa: `d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca`; commit khóa `4e381150edf08d49a134505e669058f1e0d27b48`.
- SHA256 nháp ngày cho phép: `f70341b9787982396eabb267a62b18a3fe8875c086bfffedae555fec77222189`.
- Log cũ không sửa, xóa hoặc đổi tên: SHA256 `132a4ca1a6ab15943d6cbb16bf3043978c233332bcd0a6f460ba1d9c93e0c624`.

Sau hoàn thành chỉ điền ngày cho phép, nguồn và hash nháp vào log `_attempt2`; `operator_annotation` ghi SHA256 log do script tạo trước bổ sung. Các trường thực thi và kết quả giữ nguyên. Chỉ đọc log tổng hợp để viết báo cáo; không đọc lại nguồn Test, không mở CSV bài luận gốc hoặc corpus gộp, không in nội dung bài luận. Các mục dưới giữ lịch sử các lần dừng trước kết quả hoàn thành này.

## Hồ sơ lần dừng đầu — cho phép và nhận diện bản chạy

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

Tại lần chạy này không đổi dung sai, không suy đoán nguyên nhân sai lệch, không tính tín hiệu khác và không chạy lại. Đây là hồ sơ của một lần truy cập Test bị dừng, không phải kết quả đánh giá độ phân tán cây. Hiệu chỉnh dung sai sau đó chỉ dựa trên development, được ghi riêng dưới đây.

## Log và lịch sử Test

Nguồn trực tiếp: [tree_spread_official_test_second_use_log.json](tree_spread_official_test_second_use_log.json), `status=STOPPED`, trường `failure`; không có trường `result` hoặc `pre_signal_checks=PASS`.

Sau khi script dừng, chỉ bổ sung metadata cho phép, nguồn xác nhận, hash nháp và số lần gọi vào log. Trường `operator_annotation` ghi rõ việc bổ sung sau chạy và SHA256 của log gốc trước bổ sung; các trường thực thi do script ghi được giữ nguyên, ngoại trừ điền ô `teacher_permission_date` vốn trống. Không chạy lại script hoặc đọc lại nguồn Test khi bổ sung metadata và viết RESULTS.

Lần dùng đầu là đánh giá chính Phase 9 được báo cáo và kiểm tra lại từ dự đoán lưu sẵn ở tuần 9; ngày truy cập đầu tiên không xác định được từ lịch sử hiện có. Nguồn: [t0_provenance.md](t0_provenance.md). Các phân tích mở rộng sau đánh giá chính dùng development/Validation. Lần dùng thứ hai được phép ở đây đã truy cập đặc trưng, nhãn số và dự đoán Test cho kiểm tra tính toàn vẹn, rồi dừng trước tính tín hiệu. Không mở CSV bài luận gốc hoặc corpus gộp; không in nội dung bài luận.

## Sự cố lần chạy đầu

**Ngày 26/10/2026:** lần gọi được phép đầu tiên của script lần dùng Test thứ hai dừng ở kiểm tra khớp dự đoán RF Vocabulary: **2.015 dòng** vượt dung sai tuyệt đối cũ `1e-12`, sai lệch lớn nhất **4,995115432393504e-12** (xấp xỉ **4,995115e-12**). Đây là thông tin đã ghi trước đó ở log, không phải phép tính lại trên Test. Kiểm tra RF Grammar và số bài sai lớn 208 chưa được thực hiện; tín hiệu chưa tính.

### Bước 1: kiểm tra chỉ trên development

Chỉ dùng **762 bài Validation thuộc development** có dự đoán lưu; đối chiếu theo `essay_id`, xác nhận `split=validation`, `source_partition=official_train`. Đọc đúng 14 cột đặc trưng số, không đọc văn bản bài luận. Tải hai RF đã lưu, xác nhận hash dưới đây, rồi gọi `predict` **hai lần cho mỗi RF trên cùng bảng đầu vào**; không huấn luyện lại, không tính độ phân tán cây hoặc tín hiệu nào.

| RF đã lưu | SHA256 khớp trước và sau kiểm tra development |
|---|---|
| `outputs/phase6/random_forest_vocabulary.joblib` | `899e9283e2eb01b4df6913eadd6cf8a4a823df0298ddfe820d14ba5912ffe7be` |
| `outputs/phase6/random_forest_grammar.joblib` | `bc285a202de126247240982696ca94c16dbee82bf15906d8e75ebdf4405a8f91` |

Định nghĩa độ lệch tương đối báo cáo: `max_i(abs(a_i-b_i)/abs(b_i))`, trong đó b là lần 2 hoặc bản lưu tương ứng; các giá trị tham chiếu đều khác 0. Hai cột cực đại được tính riêng, không nhất thiết thuộc cùng bài.

| Đích | Phép so trên 762 bài | Lệch tuyệt đối lớn nhất | Lệch tương đối lớn nhất |
|---|---|---:|---:|
| Vocabulary | Lần 1 so lần 2 | 0 | 0 |
| Grammar | Lần 1 so lần 2 | 0 | 0 |
| Vocabulary | Lần 1 so bản lưu tuần 9 | 4,988454094245753e-12 | 1,958839043150567e-12 |
| Grammar | Lần 1 so bản lưu tuần 9 | 4,999112235282155e-12 | 2,243807202392152e-12 |
| Vocabulary | Lần 2 so bản lưu tuần 9 | 4,988454094245753e-12 | 1,958839043150567e-12 |
| Grammar | Lần 2 so bản lưu tuần 9 | 4,999112235282155e-12 | 2,243807202392152e-12 |

Hai cột RF trong `reports/week9/t1_essay_level.csv` khớp tuyệt đối bảng gốc `outputs/phase6/validation_predictions.csv` (cả độ lệch tuyệt đối và tương đối đều 0). Vì vậy các phép so với bảng gốc cũng có đúng kết quả trên. Tại dung sai cũ, 601 bài Vocabulary và 608 bài Grammar vượt `1e-12` ngay trên development.

**Kiểm tra nguyên nhân khách quan:** định dạng từng dự đoán mới bằng `%.12g` rồi chuyển lại thành số khớp **762/762** giá trị đã lưu cho **mỗi đích**; sai lệch còn lại bằng 0. Mã lưu dự đoán development tại `src/mla_project/pipelines/training_pipeline.py`, dòng 377–378, dùng `float_format="%.12g"`. Đây là sai số làm tròn do lưu 12 chữ số có nghĩa, được xác nhận trên development; hai lần tính hiện tại lặp lại tuyệt đối nên không có bằng chứng sai lệch do thứ tự cộng thay đổi giữa hai lần.

Đối chiếu thêm **chỉ mã nguồn** `scripts/phase9_official_test_evaluation.py`, dòng 466, cho thấy bảng dự đoán cũ cũng được ghi bằng `%.12g`. Điều này giải thích cơ chế có thể gây sự cố đã ghi; không khẳng định đã kiểm chứng lại từng dòng Test, vì không mở hoặc dự đoán lại Test trong bước chẩn đoán này.

| Phiên bản | Hiện tại | Ghi lúc huấn luyện cả hai RF |
|---|---|---|
| Python | 3.14.5 | 3.14.5 |
| scikit-learn | 1.9.1 | 1.9.1 |
| NumPy | 2.4.6 | 2.4.6 |
| joblib | 1.6.0 | 1.6.0 |
| pandas | 2.3.3 | 2.3.3 |

Nguồn phiên bản huấn luyện: `outputs/phase6/training_summary.json`, `model_metadata.random_forest_{vocabulary,grammar}.package_versions` và `python_version`; môi trường kiểm tra là `.venv/Scripts/python.exe`. Các phiên bản được ghi đều khớp; không có cơ sở quy nguyên nhân cho khác phiên bản thư viện.

Nguồn development, đã xác nhận không đổi trong kiểm tra:

| File | SHA256 |
|---|---|
| `data/05_model_features/development_features_with_targets.csv` | `cafb1bca27423e0a8b6fb2d282fb7bd87fb703fc637a3a15778855caf0817a5b` |
| `outputs/phase6/validation_predictions.csv` | `6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab` |
| `reports/week9/t1_essay_level.csv` | `525c5fdaef3f36d40201d79fc75dc61629254c1f1513d0c38784d4abc892f966` |

### Bước 2: dung sai chỉ dựa trên development

Chọn **atol = 1e-11, rtol = 0**, dùng chung cho bảo vệ (b) của **RF Vocabulary và RF Grammar**. Lý do: sai lệch development lớn nhất là `4.999112235282155e-12`, được tái tạo hoàn toàn bằng làm tròn `%.12g`; trong vùng điểm 1–5, lưu 12 chữ số có nghĩa gây sai số tối đa xấp xỉ `5e-12`. Dung sai mới khoảng gấp đôi giới hạn làm tròn đó, có phần dư cho biểu diễn số dấu phẩy động, đồng thời chỉ bằng **2e-11 lần bước điểm 0,5**, tức nhỏ hơn bước đó **50 tỷ lần**. Không dùng số sai lệch Test hoặc số dòng Test để chọn dung sai; không đổi ngưỡng sai lớn 1 điểm hoặc cho phép tập ID sai lớn khác nhau.

### Bước 3: bản script sau chẩn đoán — chưa chạy trên Test

- SHA256 script cũ: `df70177723d5fdeee72e1dc65a55fc242e19fbcc9b6ad2a1052cd1fda839240b`.
- SHA256 script mới: `15bd8ee6c5d2611fd09bba32202e86cdb8398e3d433845bd55f89a1537e75ec6`.
- Chỉ đổi hằng số dung sai chung và chú thích nguồn development. Giữ nguyên công thức tín hiệu, hash mô hình/file khóa/đầu vào, nhãn sai lớn, ngân sách, phá hòa, kiểm định và cờ bảo vệ.
- **Giữ nguyên log STOPPED**, không sửa, không xóa: SHA256 `132a4ca1a6ab15943d6cbb16bf3043978c233332bcd0a6f460ba1d9c93e0c624`. Log vẫn ghi dung sai cũ và hash script cũ để phản ánh đúng lần dừng.
- Tại bước hiệu chỉnh dung sai này, không gọi script với cờ cho phép, không chạy lại trên Test, không mở lại đặc trưng/nhãn/dự đoán Test hoặc corpus. Khi đó cơ chế từ chối khi log đã tồn tại vẫn được giữ nguyên; sự cố tiếp theo và cách sửa được ghi dưới đây.

### Sự cố chốt chặn ở lần gọi thứ hai và sửa quản lý log

Sau khi đổi dung sai, script được gọi thêm đúng một lần theo chỉ dẫn người phụ trách, nhưng chốt chặn từ chối ngay vì log STOPPED của lần đầu còn tồn tại. Mã thoát 2; thông báo nguyên văn:

```text
STOP: second-use log already exists; no Test files opened.
```

Lần gọi thứ hai này không mở dữ liệu Test, không chạy các kiểm tra dự đoán trên Test, không tính tín hiệu và không tạo log mới. Đây là lần gọi bị từ chối bởi bảo vệ file, không phải một lượt đánh giá tín hiệu.

Theo chỉ dẫn tiếp theo, chỉ sửa phần chọn file log:

- Đọc metadata của log gốc và các file cùng tên có hậu tố `_attempt*`. Nếu bất kỳ log nào có `status=COMPLETED` hoặc có trường `result`, từ chối trước truy cập Test, giữ thông báo chặn hoàn thành như trước.
- Nếu các log đã có đều là `STOPPED` và không có trường `result`, cho phép thử tiếp, ghi vào file chưa tồn tại: `_attempt2.json`, rồi `_attempt3.json`, v.v. Không xóa, đổi tên hoặc ghi đè bất kỳ log cũ nào.
- Log không đọc được, không hợp lệ, đang chạy hoặc trạng thái không rõ vẫn bị chặn. Tạo file mới bằng chế độ độc quyền `x` để hai tiến trình không cùng chiếm một file log. Dòng thông báo đường dẫn cuối cùng dùng đúng tên log vừa tạo.
- Không sửa các phép kiểm tra còn lại, dung sai chung `atol=1e-11, rtol=0`, hash mô hình/đầu vào/file khóa, định nghĩa tín hiệu, ngân sách, nhãn sai lớn, phá hòa hoặc kiểm định.

SHA256 script trước sửa log: `15bd8ee6c5d2611fd09bba32202e86cdb8398e3d433845bd55f89a1537e75ec6`.

SHA256 script sau sửa log: `cc7bdd6efd8c0cf23a4f6dbd5673e17a5c8501aaf72e77fb0b99e96090b31e05`.

Kiểm tra chỉ bằng dữ liệu giả trong thư mục tạm, thay hàm đánh giá thật bằng hàm giả:

| Trường hợp giả | Kết quả |
|---|---|
| Có log STOPPED chưa có kết quả | Hàm đánh giá giả được gọi, ghi `_attempt2`; byte của log gốc không đổi |
| Có thêm log COMPLETED tại `_attempt3` | Từ chối; không gọi hàm đánh giá, không tạo/sửa file log |
| File mô hình giả có hash sai | Kiểm tra hash cũ vẫn dừng |
| Dự đoán giả lệch 5e-12 / 2e-11 | Chấp nhận / dừng tương ứng, cho cả Vocabulary và Grammar |
| Số bài giả sai N hoặc sai K | Kiểm tra 2.518/208 cũ vẫn dừng |
| Không có cờ cho phép | Thoát, kiểm tra xác nhận không mở file |

Log thật `tree_spread_official_test_second_use_log.json` giữ nguyên SHA256 `132a4ca1a6ab15943d6cbb16bf3043978c233332bcd0a6f460ba1d9c93e0c624`. Bước sửa quản lý log này chưa chạy trên Test, chưa mở lại dữ liệu Test hoặc corpus; chưa tạo file log thử tiếp trong repo và chưa có kết quả tín hiệu thật.

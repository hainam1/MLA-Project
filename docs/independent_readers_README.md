# Hai bản đọc độc lập — năm bài đã chốt

Nhóm: **điểm từ 4,0 trở lên ở đích bị sai**. Người phụ trách đã xác nhận dùng đúng năm mã dưới trong cuộc trao đổi ngày 26/10/2026; không tự chọn từ toàn bộ các bài thỏa tiêu chí.

| Mã thật (chỉ điều phối viên giữ) | Đích bị sai | Điểm thật | RF đã lưu |
|---|---|---:|---:|
| 51DA4BA94C7C | Grammar | 4,0 | 2,56698319644 |
| D1D770AF6855 | Vocabulary | 5,0 | 3,5343874469 |
| 4032ED0063E4 | Grammar | 4,0 | 2,84191058701 |
| 0FFB44B5D0C2 | Vocabulary | 4,0 | 2,97138470677 |
| 277A95AC0190 | Grammar | 4,0 | 2,60996335329 |

Nguồn nhận diện: `reports/week9/t4_reading_summary.csv`; mục “Week 10 five unexplained cases source clarification” trong `reports/week10/RESULTS_week10.md` ghi danh sách ứng viên Prompt C. Quyết định dùng đúng năm ứng viên là xác nhận mới của người phụ trách; trạng thái “chưa chốt” trong báo cáo lịch sử không bị sửa. Tiêu chí hiện tại là điểm thật **≥4,0** ở đích bị sai và RF thấp hơn ít nhất 1,0; không dùng vùng điểm trung bình >4,0. Tham chiếu tiêu chí ≥4,0: `scripts/improvement_audit.py`, dòng 174; script đó không được chạy.

## File và phạm vi Git

- `outputs/independent_readers_20261026/doc_reader_A.xlsx`
- `outputs/independent_readers_20261026/doc_reader_B.xlsx`
- `outputs/independent_readers_20261026/reader_id_map.json` — chứa ánh xạ R1–R5 riêng của từng người, đích bị sai, điểm thật, hash nguồn và hash hai phiếu gốc.
- `docs/templates/independent_reader_blank.xlsx` — mẫu rỗng để commit, không có mã thật, bài luận, đề, điểm hoặc số liệu mô hình. Chỉ chứa nhãn, hướng dẫn, mã tạm và ô nhập trống.

Hai phiếu thật, ánh xạ, bản điền và kết quả so sánh đặt trong thư mục `outputs/...` đã được `.gitignore` của repo bỏ qua. Script tạo phiếu kiểm tra `git check-ignore` trước khi đọc bài. Không cần thay `.gitignore`. Chỉ commit ba script, mẫu rỗng và README này; không dùng `git add -f` cho file riêng tư.

Nguồn dữ liệu duy nhất được script tạo đọc: `data/03_clean_ready_to_use/validation_783.csv`, `data/05_model_features/development_features_with_targets.csv`, `outputs/phase6/validation_predictions.csv`, `reports/week9/t4_reading_summary.csv`. Không đọc Test, raw-rater hay corpus gộp, không fit/predict mô hình. Văn bản bài chỉ ghi vào hai file phiếu xlsx; không lưu payload JSON văn bản, không in bài vào terminal. Trường prompt là nhãn đề hiện có, không suy đoán nguyên văn đề.

## Tạo phiếu

Từ gốc repo, dùng Python của dự án và Node có `@oai/artifact-tool` của runtime:

```powershell
.venv/Scripts/python.exe scripts/week10/create_reader_packets.py
```

Script dùng `reader_packets.mjs` để tạo xlsx. Có thể đặt `READER_NODE` và `READER_NODE_MODULES` nếu đường dẫn runtime khác máy này; mặc định tìm Node và bộ thư viện runtime trong thư mục người dùng. Không dùng node_modules của repo. Script từ chối ghi đè phiếu, ánh xạ hoặc mẫu đã có. Không chạy lại chỉ để tạo bản gửi người đọc; sao chép phiếu gốc thành bản làm việc trong cùng thư mục riêng tư và giữ hash gốc trong ánh xạ.

Xáo thứ tự: `random.Random(42)`, bắt đầu từ danh sách mã thật đã sắp xếp; gọi shuffle lần lượt cho A rồi B. Hai thứ tự khác nhau, ánh xạ R1–R5 theo vị trí ở mỗi file. Chỉ điều phối viên giữ ánh xạ và README có mã thật; gửi mỗi người đúng phiếu của họ.

## Cách đọc và nộp

Sáu sheet theo thứ tự: `Hướng dẫn`, `Bài và điểm`, `Phần A`, `Thông tin mô hình`, `Phần B`, `Xác nhận`. Tên tab rút gọn vì Excel giới hạn 31 ký tự; tiêu đề trong sheet ghi đầy đủ trình tự.

1. Người đọc tự ghi tên và thời gian bắt đầu. Đọc bài và hai điểm thật, chưa mở sheet 4. Không trao đổi hoặc xem bản người kia trước khi cả hai nộp.
2. Tự điền hết Phần A. Gửi bản sao Phần A cho điều phối viên, tự ghi giờ nộp A. Sau đó mới xem sheet 4 và điền Phần B; không sửa Phần A.
3. Tự ghi giờ nộp B, tick `☑` xác nhận độc lập và ký tên. Thời gian nhập dạng `YYYY-MM-DD HH:MM`, giờ Việt Nam (UTC+07:00).

Các ô vàng đều để trống, kể cả số đếm, nguyên nhân, tự tin, họ tên, thời gian, tick và chữ ký. Người đọc tự ghi “không có” khi không có nhận xét; 0 là số lỗi hợp lệ. Nhận xét/lý do tối đa 3 câu, người đọc tự tuân thủ. Nguyên nhân nhập mã 1–8 như hướng dẫn, nhiều mã ngăn bằng `;` (ví dụ `1;3`); không dùng macro hoặc chọn mặc định. Chọn mã 8 thì nhận xét tự do phải bắt đầu `Khác:` và ghi rõ.

Sheet 4 có RF/Ridge, 14 đặc trưng và số LanguageTool **ước lượng** cho 150 từ đầu: tỷ lệ toàn bài × min(150, word_count)/100. Không gọi đây là số đếm trực tiếp trên đoạn. Bài được chia thành các ô văn bản liên tiếp để đọc đủ, không cắt bớt; ghép nguyên các ô tái tạo đúng văn bản nguồn. Không đặt dự đoán hoặc số lỗi công cụ ở sheet 2. Quy tắc xem sheet dựa trên việc nộp và tự xác nhận; file Excel không chứng minh lịch sử người đọc đã mở sheet nào.

## So hai bản đã điền

```powershell
.venv/Scripts/python.exe scripts/week10/compare_readers.py --a outputs/independent_readers_20261026/doc_reader_A_da_dien.xlsx --b outputs/independent_readers_20261026/doc_reader_B_da_dien.xlsx
```

Mặc định dùng ánh xạ cùng thư mục; có thể chỉ định `--map` và `--out` (tiền tố đầu ra nằm trong đường dẫn được Git bỏ qua). Xuất `reader_comparison.md` và `reader_comparison.xlsx`, không in nhận xét ra terminal. Không ghi đè kết quả cũ. Không chạy so sánh phiếu thật trước khi hai thành viên nộp.

Script kiểm tra tất cả ô nhập, mã tạm, danh tính file A/B, các lựa chọn, số lỗi nguyên không âm, mã nguyên nhân, tên hai người khác nhau, thời gian theo thứ tự, tick độc lập và chữ ký. Thiếu/không hợp lệ thì dừng, liệt kê `người:sheet!ô`; không tạo kết quả. Không xác nhận sự thật thay người đọc. Phân loại nguyên nhân chỉ so **tập mã**: giống hệt → “giống nhau hoàn toàn”; có giao nhưng không giống hệt → “một phần”; không giao → “khác”. Với mã 8, nội dung giải thích được giữ bên cạnh để người đọc đối chiếu, không tự suy diễn bằng ngôn ngữ. Không tính kappa hoặc suy luận nguyên nhân.

## Kiểm tra bằng dữ liệu giả

```powershell
.venv/Scripts/python.exe scripts/week10/compare_readers.py --self-test
```

Chỉ tạo dữ liệu **FAKE** trong thư mục tạm: hai thứ tự khác nhau, ba trường hợp so tập nguyên nhân, số lỗi bằng 0, file thiếu ô và thiếu tick độc lập; tạo cả markdown/xlsx so sánh giả. Tất cả fixture và kết quả giả được xóa tự động khi kết thúc, không ghi vào thư mục phiếu thật. Không điền thử vào phiếu thật. Kiểm tra trình bày chỉ render mẫu không có bài luận; kiểm tra đủ văn bản thật bằng so sánh nội bộ, không xuất nội dung bài.

Đã chạy kiểm tra giả ngày 26/10/2026: **đạt** các trường hợp trên; đã dọn toàn bộ file giả. Đã kiểm tra sáu sheet trên mẫu không có văn bản bài, thứ tự sheet đúng, 46 ô người đọc trong mỗi phiếu đều trống, văn bản đủ và không có mã thật trong phiếu. Việc kiểm tra không xác nhận thay người đọc rằng họ đã đọc độc lập; cần họ tự nộp và xác nhận.

## SHA256 hai phiếu gốc sau khi tạo và kiểm tra

| Phiếu | SHA256 |
|---|---|
| `doc_reader_A.xlsx` | `799d2479f611cb2190e63507d00886b32573afe2f17ae0e58ab4b4c0aeac03d4` |
| `doc_reader_B.xlsx` | `a7bc27300fbfb19eff8c8cf95f471696c84e3b4f341d70ba8cd6cedc5d631545` |

Hash này cũng lưu trong ánh xạ riêng tư. Hash bản đã điền sẽ khác; không yêu cầu bản nộp khớp hash phiếu gốc. Giữ phiếu gốc để đối chiếu, gửi/điền trên bản sao. Chưa so sánh bản điền thật vì chưa có người đọc nộp.

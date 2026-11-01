# Nguồn: docs/du_lieu_interview.md
SHA256 toàn file: ddef7a3748fcb1e6edf84a2ed6ffa6a4bb1f4d359f3c69dfabd0e759cb542379

Trích chọn metadata/số liệu; không chứa bài luận.

85: ## 3. Bảng đọc năm bài — dừng, chưa đủ điều kiện so sánh
86: 
87: Kiểm tra đúng hai file được chỉ định trong `outputs/independent_readers_20261026/`, chỉ đọc các ô trả lời và xác nhận; không giải mã hoặc in các ô văn bản bài. Không thay đổi file.
88: 
89: | Phiếu | SHA256 hiện tại, cũng khớp SHA256 phiếu gốc | Kết luận trong phạm vi file đã kiểm tra |
90: |---|---|---|
91: | `doc_reader_A.xlsx` | `799d2479f611cb2190e63507d00886b32573afe2f17ae0e58ab4b4c0aeac03d4` | Còn nguyên phiếu gốc; ô trả lời và xác nhận trống |
92: | `doc_reader_B.xlsx` | `a7bc27300fbfb19eff8c8cf95f471696c84e3b4f341d70ba8cd6cedc5d631545` | Còn nguyên phiếu gốc; ô trả lời và xác nhận trống |
93: 
94: Nguồn hash gốc: `outputs/independent_readers_20261026/reader_id_map.json`, trường `original_workbook_sha256`, và README bộ phiếu (nguồn gốc trong repository: `independent_readers_README.md`), commit **`aa13e834e654debcb547f5aa21f38f85bd85434d`**. Hash hiện tại tính trực tiếp từ hai file được chỉ định, chỉ dùng để biết file có thay đổi hay không; không sửa phiếu.
95: 
96: Thông báo dừng nguyên văn của bước kiểm tra:
97: 
98: ```text
99: STOP: chưa đủ điều kiện so sánh — còn ô trống hoặc thiếu xác nhận độc lập.
100: ```
101: 
102: **Các ô thiếu, áp dụng giống nhau cho cả file A và file B:**
103: 
104: | Sheet | Danh sách đầy đủ các ô còn trống trong mỗi file | Ý nghĩa |
105: |---|---|---|
106: | `Phần A` | `B6:B9`, `B13:B16`, `B20:B23`, `B27:B30`, `B34:B37` | Đánh giá điểm thật, lý do, số lỗi và ghi chú từ vựng của các bài |
107: | `Phần B` | `B6:B9`, `B13:B16`, `B20:B23`, `B27:B30`, `B34:B37` | Máy sai ở đâu, nguyên nhân, tự tin và nhận xét của các bài |
109: 
110: Mỗi file thiếu **46 ô**, tổng hai file **92 ô**; cả hai ô `Xác nhận!B9` chưa xác nhận độc lập. Nguồn: đọc có chọn lọc các địa chỉ trên từ hai file phiếu, theo `input_layout()` trong `scripts/week10/compare_readers.py`. Không in giá trị các ô đã điền. Việc hai file này chưa được điền không chứng minh có hay không một bản nộp khác ở nơi khác; chưa có bản nộp đủ điều kiện trong hai đường dẫn được yêu cầu kiểm tra.
111: 
112: **Không chạy `compare_readers.py` để so bản thật và không xuất bảng nhận xét/nguyên nhân.** Chưa xác định được bài nào cả hai chọn “không giải thích được”; không coi ô trống là lựa chọn đó và không suy luận thay người đọc.
113: 
114: Danh sách nhóm đã chốt để biết các bài đang chờ đọc (đây không phải kết quả đọc):
115: 
116: | Mã bài | Đích bị sai | Điểm thật ở đích đó | Trạng thái so sánh |
117: |---|---|---:|---|
118: | `51DA4BA94C7C` | Ngữ pháp | **4,0** | Chưa đủ điều kiện |
119: | `D1D770AF6855` | Từ vựng | **5,0** | Chưa đủ điều kiện |
120: | `4032ED0063E4` | Ngữ pháp | **4,0** | Chưa đủ điều kiện |
121: | `0FFB44B5D0C2` | Từ vựng | **4,0** | Chưa đủ điều kiện |
122: | `277A95AC0190` | Ngữ pháp | **4,0** | Chưa đủ điều kiện |
123: 
124: Nguồn mã, đích và điểm: README bộ phiếu (nguồn gốc trong repository: `independent_readers_README.md`), danh sách đã được người phụ trách xác nhận; nguồn số ban đầu `reports/week9/t4_reading_summary.csv`. Không điền nhận xét, nguyên nhân, tự tin hoặc thông tin cá nhân vào báo cáo thay người đọc.
125: 
126: Phần này dừng không làm mất kết quả đã hoàn tất ở hai phần trước. Sau khi dừng chỉ tạo tài liệu tổng hợp mới này, không sửa đầu vào, script, dung sai, log hoặc RESULTS đã có; không chạy lại bất kỳ bước bị dừng nào.

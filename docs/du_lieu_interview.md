# Dữ liệu để điền sổ tay interview

Ngày tổng hợp: 26/10/2026. Làm tuần tự ba phần; chỉ đọc hồ sơ đã lưu và các ô trả lời được chỉ định. Không chạy mô hình hoặc script đánh giá Test, không đọc lại đặc trưng/nhãn/dự đoán Test, không mở corpus và không in hay đưa nội dung bài luận vào tài liệu. Không sửa phiếu hoặc điền thay người đọc.

## 1. Test lần hai — xong từ kết quả đã có, không chạy lại

Đã có [log `_attempt2`](../reports/week9/tree_spread_official_test_second_use_log_attempt2.json) với `status=COMPLETED` và `pre_signal_checks=PASS`. Vì vậy không gọi script hoặc mở dữ liệu Test trong lần tổng hợp này. Kết quả đã commit tại **`97159a6b9a10e46b881b8e1a66cd278171dff4f6`**; commit lúc chạy là **`cdc0a6a871d1f7ae9458f920157853159d6f9318`**. Nguồn: các trường `status`, `pre_signal_checks`, `run_commit` trong log; lịch sử Git của log; [RESULTS thật](../reports/week9/RESULTS_tree_spread_second_use.md).

| Chỉ số | Số đã lưu | Nguồn |
|---|---:|---|
| Bài đủ điều kiện | **2.518** | Log `_attempt2`, `result.eligible_count` |
| Bài RF sai lớn | **208** | Cùng log, `result.large_error_count` |
| Ngân sách đọc, làm tròn lên | **504** | Cùng log, `result.budget_ceil_20pct` |
| Tín hiệu cây bắt được | **55/208** | Cùng log, `result.caught` và `large_error_count` |
| Kỳ vọng ngẫu nhiên | **41,6330420969023 ≈ 41,63** | Cùng log, `result.expected_random` |
| p chính xác một phía | **0,011585706847145556** | Cùng log, `result.exact_one_sided_p` |
| D đã có, không tính lại | **47/208** | [RESULTS tuần 9, Task 0](../reports/week9/RESULTS_week9.md); đối chiếu RESULTS thật |
| Chênh số bắt được so với D | **8 bài** | So hai số đã lưu 55−47, cũng ghi trong RESULTS thật |

Nói bằng lời thường: với cùng số bài cần đọc và cùng nhãn sai lớn đã cố định, tín hiệu cây tìm được nhiều bài sai hơn mức trung bình khi bốc ngẫu nhiên. Giá trị p trên cho thấy việc bốc ngẫu nhiên bắt được ít nhất số bài như vậy là ít gặp theo phép so đã chốt. Tuy nhiên, đây là **Test dùng lại, không phải xác nhận độc lập sạch**. Hơn D về số đếm không đồng nghĩa đã kiểm định trực tiếp và chứng minh tốt hơn D; p trong bảng là so với ngẫu nhiên, không phải p so với D. Nguồn cách hiểu và giới hạn: RESULTS thật, mục Kết quả hoàn thành.

Kiểm tra trước khi tổng hợp, chỉ đọc file script/mô hình và hồ sơ, không dự đoán:

| File / thiết lập | Kết quả kiểm tra | Nguồn đối chiếu |
|---|---|---|
| `scripts/tree_spread_official_test_second_use.py` | SHA256 `cc7bdd6efd8c0cf23a4f6dbd5673e17a5c8501aaf72e77fb0b99e96090b31e05` — khớp | Log `_attempt2`, `script_sha256`; commit `cdc0a6a8` |
| `outputs/phase6/random_forest_vocabulary.joblib` | SHA256 `899e9283e2eb01b4df6913eadd6cf8a4a823df0298ddfe820d14ba5912ffe7be` — khớp | Cùng log, `model_sha256` |
| `outputs/phase6/random_forest_grammar.joblib` | SHA256 `bc285a202de126247240982696ca94c16dbee82bf15906d8e75ebdf4405a8f91` — khớp | Cùng log, `model_sha256` |
| Dung sai khớp dự đoán | `atol=1e-11, rtol=0` | Cùng log; hằng số trong script |
| Ngày thầy cho phép | **26/10/2026**, nguồn nhận xét tuần 10 của thầy Khánh theo xác nhận người phụ trách | [Nháp RESULTS](../reports/week9/RESULTS_tree_spread_second_use_DRAFT.md) và RESULTS thật |

**Lưu ý vị trí mục Sự cố:** ngày cho phép nằm trong nháp, nhưng mục “Sự cố lần chạy đầu” và “Sự cố chốt chặn ở lần gọi thứ hai” nằm trong **RESULTS thật**, không nằm trong nháp. Nháp còn dòng “CHƯA CHẠY” là bản chuẩn bị lịch sử; trạng thái hiện tại lấy theo log COMPLETED và RESULTS thật. Không sửa các file đó trong nhiệm vụ này.

## 2. Dữ liệu hai bài luyện — xong

### Bài 684166ED2438

| Điểm / mô hình | Từ vựng | Ngữ pháp | Nguồn |
|---|---:|---:|---|
| Điểm thật | **1,5** | **1,5** | [Phiếu 684166ED2438](phieu_luyen_684166ED2438_development.md), bảng Điểm và dự đoán; nguồn gốc `reports/week9/t3_heldout_predictions.csv`, `prompt_disjoint` |
| RF | **2,9557419105** | **3,0314580630** | Cùng phiếu và bảng dự đoán gốc, `RF_V/RF_G` |
| Ridge | **2,8934052120** | **3,0758794159** | Cùng phiếu và bảng dự đoán gốc, `Ridge_V/Ridge_G` |
| MiniLM + Ridge (B2) | **3,054166078567505** | **3,095129728317261** | [b2_oof.csv](../reports/week10/b2_oof.csv), đúng mã bài, `B2_V/B2_G`; phiếu ghi số làm tròn |

| D và danh sách đọc lại | Giá trị | Nguồn |
|---|---:|---|
| Fold chia theo đề | **5** | Phiếu 684166ED2438, mục D, thứ hạng và ngưỡng; nguồn gốc `t3_heldout_predictions.csv`, `prompt_disjoint` |
| D của bài | **0,06233669853577917** | Cùng nguồn, max bất đồng tuyệt đối RF–Ridge giữa hai đích |
| Thứ hạng D trong fold | **671/769** | Cùng nguồn, D giảm dần, hòa thì essay_id dạng chuỗi tăng dần |
| Ngưỡng ngân sách 20% | **154 bài đầu** | Cùng nguồn, ceil(20%×769) |
| D tại vị trí cuối danh sách đọc | **0,2178198494584902** | Cùng nguồn, bài hạng 154 |
| Có được D chọn đọc lại không? | **Không** | Hạng 671 nằm ngoài 154 bài đầu, từ cùng phiếu |

Bài có Từ vựng thật dưới 2,5 và thuộc nhóm 276 bài RF/Ridge cùng sai lớn. Hai dự đoán Từ vựng đều gần 2,9 theo cách hiểu cách mốc này không quá 0,1 điểm trong phiếu. Nguồn các số và tiêu chí chọn: phiếu 684166ED2438, mục Lý do chọn và Điểm và dự đoán. Các dự đoán là dự đoán trên fold giữ lại của thử nghiệm chia theo đề; trường chia ban đầu của bài là `model_train`, không lấy dự đoán trên chính phần vừa học.

**Năm đặc trưng nổi bật nhất so với development:** chọn theo trị tuyệt đối của `z=(giá trị−trung bình)/độ lệch chuẩn`, với độ lệch chuẩn tổng thể (`ddof=0`), trong bộ 14 đặc trưng. Mốc trung bình và độ lệch chuẩn tính trên **3.812 bài** của [t3_eligible_development.csv](../reports/week9/t3_eligible_development.csv). Đây là tính thống kê từ đặc trưng lưu sẵn, không chạy mô hình; “nổi bật” không có nghĩa đã tìm ra nguyên nhân máy sai.

| Đặc trưng | Bài này | Trung bình development | z xấp xỉ | Nguồn mọi số trong hàng |
|---|---:|---:|---:|---|
| Chỉ số tần suất từ (`mean_word_frequency`) | **5,616364** | **6,073201** | **−3,2127** | `reports/week9/t3_eligible_development.csv`, đúng mã bài; trung bình và z tính từ cùng bảng |
| Số từ (`word_count`) | **55** | **428,280693** | **−1,9649** | Cùng file và cách tính |
| Số câu (`sentence_count`) | **2** | **19,088143** | **−1,6517** | Cùng file và cách tính |
| Đa dạng danh từ (`noun_diversity`) | **0,647059** | **0,460300** | **+1,4884** | Cùng file và cách tính |
| Tỷ lệ câu phức (`complex_sentence_ratio`) | **1,000000** | **0,858556** | **+1,1444** | Cùng file và cách tính |

Nói đơn giản: bài này ngắn hơn mức chung, chỉ số tần suất từ thấp hơn, còn hai tỷ lệ ở cuối bảng cao hơn mức chung. Những con số mô tả này chưa phải nhận xét hoặc nguyên nhân do người đọc xác nhận.

**Người đếm lỗi: “chưa có người đếm”.** Đối chiếu ID trong [gec_part_a_68.csv](../reports/week10/gec_part_a_68.csv), bài này **không thuộc mẫu 68 bài** đã có số đếm người đọc. Vì vậy số đếm người đọc và GECToR của mẫu đó là **chưa có dữ liệu**, không điền 0 thay cho thiếu.

Công cụ cũ có tỷ lệ đã lưu **0 cảnh báo/100 từ**, tương ứng ước lượng trên tối đa 150 từ đầu là **0** theo công thức `0×min(150,55)/100`. Nguồn tỷ lệ và độ dài: `t3_eligible_development.csv`; đối chiếu phiếu 684166ED2438, mục Số đếm lỗi. Đây chỉ là ước lượng từ đặc trưng toàn bài, không phải một lần công cụ đếm trực tiếp đoạn đầu và không chứng minh bài không có lỗi.

### Bài 0514D25768A0

| Dữ liệu cần xác nhận | Giá trị | Nguồn |
|---|---:|---|
| Điểm thật Từ vựng / Ngữ pháp | **2 / 2** | [phieu_luyen_mot_bai_development.md](phieu_luyen_mot_bai_development.md), mục 3 |
| Fold / thứ hạng D | **5 / 174 trên 769** | Cùng phiếu, Quyết định đọc lại; nguồn gốc `t3_heldout_predictions.csv`, `prompt_disjoint` |
| Ngưỡng 20% | **154 bài đầu** | Cùng nguồn |
| D của bài | **0,20849338320386002 ≈ 0,21** | Cùng nguồn |
| D cuối danh sách đọc | **0,2178198494584902** | Cùng nguồn |
| Có được D chọn đọc lại không? | **Không** | Hạng 174 vượt ngân sách 154, từ cùng phiếu |

“D lớn nhất khoảng 0,21” chỉ đúng nếu hiểu là lấy số lớn hơn giữa bất đồng của hai đích trong **bài này**. Không gọi đó là D lớn nhất cả fold. Nguồn định nghĩa và số: phiếu 0514D25768A0.

## 3. Bảng đọc năm bài — dừng, chưa đủ điều kiện so sánh

Kiểm tra đúng hai file được chỉ định trong `outputs/independent_readers_20261026/`, chỉ đọc các ô trả lời và xác nhận; không giải mã hoặc in các ô văn bản bài. Không thay đổi file.

| Phiếu | SHA256 hiện tại, cũng khớp SHA256 phiếu gốc | Kết luận trong phạm vi file đã kiểm tra |
|---|---|---|
| `doc_reader_A.xlsx` | `799d2479f611cb2190e63507d00886b32573afe2f17ae0e58ab4b4c0aeac03d4` | Còn nguyên phiếu gốc; ô trả lời và xác nhận trống |
| `doc_reader_B.xlsx` | `a7bc27300fbfb19eff8c8cf95f471696c84e3b4f341d70ba8cd6cedc5d631545` | Còn nguyên phiếu gốc; ô trả lời và xác nhận trống |

Nguồn hash gốc: `outputs/independent_readers_20261026/reader_id_map.json`, trường `original_workbook_sha256`, và [README bộ phiếu](independent_readers_README.md), commit **`aa13e834e654debcb547f5aa21f38f85bd85434d`**. Hash hiện tại tính trực tiếp từ hai file được chỉ định, chỉ dùng để biết file có thay đổi hay không; không sửa phiếu.

Thông báo dừng nguyên văn của bước kiểm tra:

```text
STOP: chưa đủ điều kiện so sánh — còn ô trống hoặc thiếu xác nhận độc lập.
```

**Các ô thiếu, áp dụng giống nhau cho cả file A và file B:**

| Sheet | Danh sách đầy đủ các ô còn trống trong mỗi file | Ý nghĩa |
|---|---|---|
| `Phần A` | `B6:B9`, `B13:B16`, `B20:B23`, `B27:B30`, `B34:B37` | Đánh giá điểm thật, lý do, số lỗi và ghi chú từ vựng của các bài |
| `Phần B` | `B6:B9`, `B13:B16`, `B20:B23`, `B27:B30`, `B34:B37` | Máy sai ở đâu, nguyên nhân, tự tin và nhận xét của các bài |
| `Xác nhận` | `B5:B10` | Họ tên, ba thời gian, tick độc lập ở B9 và chữ ký |

Mỗi file thiếu **46 ô**, tổng hai file **92 ô**; cả hai ô `Xác nhận!B9` chưa xác nhận độc lập. Nguồn: đọc có chọn lọc các địa chỉ trên từ hai file phiếu, theo `input_layout()` trong `scripts/week10/compare_readers.py`. Không in giá trị các ô đã điền. Việc hai file này chưa được điền không chứng minh có hay không một bản nộp khác ở nơi khác; chưa có bản nộp đủ điều kiện trong hai đường dẫn được yêu cầu kiểm tra.

**Không chạy `compare_readers.py` để so bản thật và không xuất bảng nhận xét/nguyên nhân.** Chưa xác định được bài nào cả hai chọn “không giải thích được”; không coi ô trống là lựa chọn đó và không suy luận thay người đọc.

Danh sách nhóm đã chốt để biết các bài đang chờ đọc (đây không phải kết quả đọc):

| Mã bài | Đích bị sai | Điểm thật ở đích đó | Trạng thái so sánh |
|---|---|---:|---|
| `51DA4BA94C7C` | Ngữ pháp | **4,0** | Chưa đủ điều kiện |
| `D1D770AF6855` | Từ vựng | **5,0** | Chưa đủ điều kiện |
| `4032ED0063E4` | Ngữ pháp | **4,0** | Chưa đủ điều kiện |
| `0FFB44B5D0C2` | Từ vựng | **4,0** | Chưa đủ điều kiện |
| `277A95AC0190` | Ngữ pháp | **4,0** | Chưa đủ điều kiện |

Nguồn mã, đích và điểm: [README bộ phiếu](independent_readers_README.md), danh sách đã được người phụ trách xác nhận; nguồn số ban đầu `reports/week9/t4_reading_summary.csv`. Không điền nhận xét, nguyên nhân, tự tin hoặc thông tin cá nhân vào báo cáo thay người đọc.

Phần này dừng không làm mất kết quả đã hoàn tất ở hai phần trước. Sau khi dừng chỉ tạo tài liệu tổng hợp mới này, không sửa đầu vào, script, dung sai, log hoặc RESULTS đã có; không chạy lại bất kỳ bước bị dừng nào.

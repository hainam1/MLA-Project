# Sổ tay hiểu dự án ELLIPSE — MLA-Project, Nhóm 03

Tài liệu dành cho người mới: máy chấm điểm bài viết có thể giúp giáo viên chọn bài cần đọc lại hay không?
Đây là bản giải thích các kết quả đã lưu, không phải một lần chạy thí nghiệm mới.
Không có nội dung bài luận nào được đưa vào sổ tay.

## Mục lục

- [Phần A. Bức tranh tổng thể](#phan-a)
- [Phần B. Dữ liệu và cách chia](#phan-b)
- [Phần C. Mô hình chấm điểm](#phan-c)
- [Phần D. Lỗi ngữ pháp và công cụ](#phan-d)
- [Phần E. Kết quả chính và vì sao](#phan-e)
- [Phần F. Trung thực và kiểm soát](#phan-f)
- [Phần G. Tổng kết và hướng đi](#phan-g)
- [Từ khó → nghĩa dễ hiểu](#tu-kho)
- [Số liệu và nguồn](#so-lieu)
- [Chuẩn bị interview](#chuan-bi-interview)

**Cách đọc nguồn:** [W9](../reports/week9/RESULTS_week9.md) là báo cáo tuần chín; [W10](../reports/week10/RESULTS_week10.md) là báo cáo tuần mười; [Khóa](signal_lock_tree_spread.md) là bản chốt cách chọn bài.
Các nhãn này được ghi ngay sau số liệu, kèm tên mục để tra cứu.
`e88d82c:tên_file` nghĩa là đọc file tại commit `e88d82c`, tức một bản lưu trong lịch sử Git; giống như tra đúng bản sách đã xuất bản.
Các nguồn lịch sử được dùng ở đây là `e88d82c:docs/data_card.md`, `e88d82c:docs/feature_specification.md` và `e88d82c:docs/split_and_leakage_protocol.md`.
Lần hiệu chỉnh còn đối chiếu trực tiếp `docs/split_and_leakage_protocol.md` và bảng đếm không chứa văn bản bài luận `reports/week10/gec_part_a_68.csv` theo yêu cầu người dùng.
**Cập nhật ngày 26/10/2026:** bổ sung [kết quả tín hiệu cây trên Test dùng lại](../reports/week9/RESULTS_tree_spread_second_use.md) và [bộ phiếu hai người đọc độc lập](independent_readers_README.md), chỉ từ hồ sơ đã lưu; không chạy lại hoặc đọc lại dữ liệu Test khi sửa sổ tay.
Số thập phân được làm tròn; số thứ tự câu, tên tuần, mã file và mã commit là nhãn tra cứu, không phải kết quả đo.

<a id="phan-a"></a>
## Phần A. Bức tranh tổng thể

Nói gọn là: nhóm muốn giúp giáo viên tìm bài máy có thể chấm sai để đọc lại trước.

### 1. Dự án giải quyết việc gì trong đời thực?

Giáo viên có ít thời gian nên cần biết bài nào đáng kiểm tra lại trước.
Mô hình, tức chương trình học cách đoán từ ví dụ, chấm bài rồi tạo danh sách ưu tiên đọc lại.
Hãy hình dung một người phụ giúp xếp chồng bài cần kiểm tra lên đầu bàn.
Mục tiêu là hỗ trợ giáo viên, không tự quyết định điểm cuối cùng thay giáo viên.
Nguồn: [W9, Task 0](../reports/week9/RESULTS_week9.md); `e88d82c:docs/data_card.md`, mục Intended and prohibited use.

### 2. ELLIPSE là dữ liệu gì?

ELLIPSE là bộ bài viết tiếng Anh của học sinh đang học tiếng Anh tại trường ở Mỹ, từ lớp 8 đến lớp 12.
Bộ bài đáng tin cậy có 6.482 bài: phần huấn luyện chính thức có 3.911 bài, phần kiểm tra chính thức có 2.571 bài.
Mỗi bài được hai người chấm độc lập; điểm dùng trong dự án là điểm tổng hợp/trung bình đã cung cấp.
Thang điểm từ 1 đến 5, có các mức cách nhau 0,5 điểm, như những nấc trên một chiếc thang.
Bộ gốc có điểm Tổng thể và sáu mặt: Liên kết ý, Cấu trúc câu, Từ vựng, Cách dùng cụm từ, Ngữ pháp, Quy ước viết; dự án chỉ dự đoán Từ vựng và Ngữ pháp.
Nguồn cho toàn bộ thông tin và số lượng ở câu này: `e88d82c:docs/data_card.md`, mục Population, unit, and target và Data quality and size.

### 3. Máy đoán gì, và sai lớn nghĩa là gì?

Máy đoán điểm Từ vựng và điểm Ngữ pháp của từng bài.
Điểm người chấm là mốc để đối chiếu, giống đáp án dùng khi kiểm tra bài tập.
Theo cách đánh giá chính, một bài sai lớn khi RF lệch điểm người chấm ít nhất 1 điểm ở bất kỳ mặt nào trong hai mặt trên.
RF là tên ngắn của rừng cây quyết định, một nhóm bộ đoán điểm sẽ được giải thích ở câu 9.
Đây là lỗi của máy so với điểm tham chiếu, không phải nói học sinh viết sai một lỗi ngữ pháp; các phân tích phụ còn kiểm tra lỗi của Ridge hoặc lỗi của cả hai máy.
Nguồn: [Khóa, Signal definition](signal_lock_tree_spread.md); [W9, Task 2](../reports/week9/RESULTS_week9.md).

### 4. Ý tưởng “hai máy bất đồng” là gì?

Ridge là một bộ đoán điểm khác RF; nhóm so xem điểm hai bộ đoán có cách xa nhau không.
“Bất đồng” nghĩa là hai máy cho điểm khác nhau, giống hai người cân cùng một vật nhưng báo cân nặng khác nhau.
Nhóm lấy khoảng cách lớn hơn giữa Từ vựng và Ngữ pháp để xếp bài cần đọc lại.
Giả thuyết ban đầu là khoảng cách càng lớn thì bài càng dễ bị máy chấm sai.
Nghe hợp lý vì hai ý kiến trái nhau thường khiến ta cần kiểm tra, nhưng chúng cũng có thể cùng đồng ý mà cùng sai.
Nguồn cách tính: [Khóa, Future confirmation protocol](signal_lock_tree_spread.md); phần lý do là giải thích trực giác, chưa phải bằng chứng rằng giả thuyết đúng.

### 5. Đo “tốt hơn ngẫu nhiên” như thế nào?

Giáo viên chỉ đọc lại khoảng 20% bài, tức khoảng một phần năm chồng bài; số bài được làm tròn lên.
Ta đếm bao nhiêu bài sai lớn lọt vào danh sách đó rồi so với bốc ngẫu nhiên cùng số bài.
Trên Validation, tức tập bài tập dượt để chọn cách làm, có 762 bài đủ điều kiện và 69 bài máy sai lớn: đọc 153 bài theo bất đồng tìm được 15 bài sai.
Kỳ vọng ngẫu nhiên là 69 × 153 / 762 = 13,854330… ≈ 13,85 bài; chưa có bằng chứng đáng tin rằng cách bất đồng tốt hơn.
Số 13,946 là trung bình của 1.000 lượt bốc mô phỏng đã lưu, còn 13,85 là kỳ vọng theo công thức; cả hai có phần lẻ vì diễn tả mức trung bình, không phải số bài của một lượt.
Nguồn: [W9, Task 0, dòng 23 và 32, Random mean và Expected random caught](../reports/week9/RESULTS_week9.md).

<a id="phan-b"></a>
## Phần B. Dữ liệu và cách chia

Nói gọn là: phải tách bài để học, bài để thử cách làm và bài kiểm tra cuối, giống học bài rồi mới thi.

### 6. Các phần dữ liệu dùng để làm gì?

Development là vùng phát triển cách làm, gồm model-train để máy học và Validation để kiểm tra lựa chọn trước lần đánh giá cuối.
Ban đầu development có 3.911 bài, chia thành 3.128 bài học và 783 bài Validation; sau khi loại bài không đủ điều kiện riêng tư, còn 3.050 và 762 bài, tổng 3.812 bài.
Official Test là phần kiểm tra cuối được giữ riêng: có 2.571 bài ban đầu, trong đó 2.518 bài đủ điều kiện đánh giá.
Giữ kín nó giống giữ đề thi cuối kỳ để điểm thi còn cho biết học sinh làm được bài mới ra sao.
Lịch sử dự án đã có kết quả Test; các mở rộng về sau phải mang nhãn thăm dò, chứ không được coi dữ liệu cũ là đề thi mới chưa xem.
Nguồn: [W9, t3_eligibility_counts.csv](../reports/week9/t3_eligibility_counts.csv); [W9, Task 0 và Task 3](../reports/week9/RESULTS_week9.md); `e88d82c:docs/split_and_leakage_protocol.md`, Outcome và Privacy status.

### 7. Chia theo đề bài và chia năm phần nghĩa là gì?

Prompt là đề bài học sinh nhận được, giống cả lớp cùng viết về một chủ đề.
Fold là một phần dữ liệu được giữ lại để thử máy; trong cách chia 5 phần, lần lượt giữ một phần để thử và cho máy học từ các phần còn lại.
Kết quả gọi là dự đoán ngoài phần học: mỗi bài được đoán khi máy chưa học bài đó.
Chia theo đề bài còn giữ toàn bộ bài cùng đề về cùng phía, nên đề trong phần thử không xuất hiện trong phần học.
Như vậy ta hỏi “máy gặp đề mới thì sao”; cách chia ban đầu của repo chia theo tỷ lệ trong từng đề, giữ các đề ở cả hai phía và nhóm theo mã băm văn bản trùng, nên không tách riêng đề bài để thử đề mới.
Nguồn xác nhận cách chia ban đầu: [docs/split_and_leakage_protocol.md, Reproducible split procedure, bước 5–6; Distribution checks, Prompt coverage và Cross-validation folds](split_and_leakage_protocol.md), ghi phân tầng theo đề, nhóm theo mã băm văn bản, mỗi đề có ở cả hai phần và mỗi fold thử đều có đủ 44 đề; vì vậy đây không phải chia tách theo đề. Nguồn cách thử đề mới: [W9, Task 3](../reports/week9/RESULTS_week9.md) và [Khóa](signal_lock_tree_spread.md).

<a id="phan-c"></a>
## Phần C. Mô hình chấm điểm — mốc so sánh ban đầu

Nói gọn là: máy ban đầu nhìn một phiếu mô tả bài viết bằng số, rồi học liên hệ giữa phiếu ấy và điểm người chấm.

### 8. Các đặc trưng thủ công là gì?

Đặc trưng là một con số mô tả bài, giống phiếu mô tả món ăn có độ ngọt và độ mặn; “thủ công” nghĩa là người thiết kế chọn trước cách đo.
Bộ ban đầu có 14 đặc trưng trong bảng dưới, chứ không đọc toàn bộ ý nghĩa bài như giáo viên.
Các phép đo về từ và câu dùng spaCy, công cụ tách câu và nhận diện vai trò của từ, giống người chia một đoàn tàu thành từng toa để xem cấu trúc.
Nguồn số lượng, tên và định nghĩa của toàn bộ bảng: `e88d82c:docs/feature_specification.md`, Feature table và Shared preprocessing.
Các ví dụ trong bảng là ví dụ minh họa tự viết, không trích bài học sinh.

| Nhóm | Đặc trưng trong repo | Nghĩa dễ hiểu và ví dụ |
|---|---|---|
| Độ dài | `word_count` | Số từ chữ cái mà bộ tách từ nhận ra; xem chồng bài dài hay ngắn. |
| Độ dài | `sentence_count` | Số câu; xem bài có nhiều câu ngắn hay ít câu dài. |
| Độ dài | `mean_sentence_length` | Độ dài câu trung bình; giống chia đều số từ vào các câu. |
| Từ vựng | `mtld` | Độ đa dạng từ khi đọc dọc bài; liên tục lặp “đẹp” sẽ kém đa dạng hơn dùng nhiều từ khác nhau. |
| Từ vựng | `mattr` | Độ đa dạng trong các đoạn nhỏ trượt dọc bài; giống đưa một khung cửa sổ qua trang giấy. |
| Từ vựng | `mean_word_frequency` | Từ thường gặp đến đâu; từ quen thuộc trong đời sống khác từ hiếm gặp. |
| Từ vựng | `mean_word_length` | Độ dài từ trung bình; từ dài chưa chắc dùng đúng. |
| Từ vựng | `lexical_density` | Phần từ mang nội dung như danh từ, động từ, tính từ, trạng từ; giống phần nhân trong chiếc bánh. |
| Từ vựng | `noun_diversity` | Danh từ có phong phú không; dùng nhiều tên sự vật khác nhau thay vì lặp cùng một tên. |
| Ngữ pháp | `detected_grammar_errors_per_100_words` | Số cảnh báo ngữ pháp quy về mỗi 100 từ, giống so tiền trên cùng một đơn vị hàng. |
| Ngữ pháp | `detected_error_free_sentence_ratio` | Phần câu không bị công cụ báo lỗi; không bị báo chưa có nghĩa chắc chắn đúng. |
| Cấu trúc câu | `complex_sentence_ratio` | Phần câu có mệnh đề phụ, tức ý nhỏ nằm trong câu lớn, như câu có “vì… nên…”. |
| Cấu trúc câu | `estimated_clauses_per_sentence` | Số mệnh đề ước tính trong một câu; một câu có thể ghép nhiều ý có động từ. |
| Cấu trúc câu | `subordinate_clause_ratio` | Phần mệnh đề phụ trong tổng mệnh đề; xem các ý phụ chiếm bao nhiêu. |

### 9. Ridge và RF là gì, vì sao dùng cả hai?

Ridge giống người cộng điểm từ một bảng tiêu chí, nhưng có dây giữ để không đặt quá nhiều sức nặng vào một tiêu chí riêng lẻ.
RF là rừng cây quyết định: mỗi cây là một chuỗi câu hỏi rẽ nhánh về đặc trưng, giống trò đoán đồ vật bằng các câu hỏi nối tiếp.
Rừng gộp điểm của nhiều cây để ra dự đoán chung.
Hai cách nhìn cùng một phiếu đặc trưng nhưng dùng quy tắc học khác nhau, nên có thể đem mức bất đồng ra thử làm dấu hiệu cần đọc lại.
Đây là cách giải thích cơ chế; dùng cả hai không tự tạo ra hai nguồn hiểu bài độc lập.
Nguồn thiết kế: `e88d82c:docs/split_and_leakage_protocol.md`, Fit and transform rules; [Khóa, Signal definition và Future confirmation protocol](signal_lock_tree_spread.md).

### 10. Mỗi máy lệch trung bình bao nhiêu điểm?

Sai lệch tuyệt đối trung bình nghĩa là lấy độ cách xa điểm người chấm trên từng bài rồi tính trung bình, nên sai lên và sai xuống không xóa nhau.
Bảng dùng cùng 3.812 bài development đủ điều kiện, chia 5 phần theo đề bài; đây là kết quả thăm dò trên dữ liệu đã được dùng phát triển.
TF-IDF là cách mô tả từ/cụm từ theo mức nổi bật, giống đánh dấu từ đặc trưng của bài; MiniLM là bộ mã hóa văn bản, giống biến đoạn viết thành một phiếu dấu hiệu bằng số, rồi cả hai dùng Ridge để đoán điểm.
Chẳng hạn RF lệch khoảng 0,372 điểm Từ vựng, nghĩa là trung bình cách điểm người chấm gần bốn phần mười điểm, không có nghĩa mọi bài đều chỉ sai ngần ấy.
Nhỏ hơn là tốt hơn ở phép đo này; các nguồn đọc văn bản mới chưa chấm chính xác hơn các máy dùng đặc trưng ban đầu.
Nguồn tất cả số trong bảng: [W10, B2 concise result tables](../reports/week10/RESULTS_week10.md); đối chiếu Ridge/RF tại [W9, Task 3](../reports/week9/RESULTS_week9.md).

| Cách đoán điểm | Từ vựng: lệch trung bình | Ngữ pháp: lệch trung bình |
|---|---:|---:|
| Ridge với đặc trưng ban đầu | 0,373424 | 0,463037 |
| RF với đặc trưng ban đầu | 0,372165 | 0,455404 |
| TF-IDF + Ridge, tên trong báo cáo là B1 | 0,406626 | 0,506841 |
| MiniLM + Ridge, tên trong báo cáo là B2 | 0,404448 | 0,507 |

Điểm Ngữ pháp MiniLM được làm tròn trực tiếp đến ba chữ số thập phân từ 0,50749980021123497 thành **0,507**, thống nhất trong sổ tay; không làm tròn qua số trung gian 0,5075. Nguồn số gốc: [W10, dòng 1564, B2,G,3812](../reports/week10/RESULTS_week10.md).

<a id="phan-d"></a>
## Phần D. Lỗi ngữ pháp và công cụ

Nói gọn là: công cụ đếm lỗi cũng có thể sai, nên cần đối chiếu với người đọc trước khi tin con số của nó.

### 11. Công cụ cũ đếm lỗi bằng gì?

Dự án dùng `language-tool-python` để gọi LanguageTool chạy tại máy, giống một người dò bài bằng danh sách quy tắc ngôn ngữ.
Nó đánh dấu những chỗ có vẻ sai và cho biết loại cảnh báo.
Dự án chỉ đếm cảnh báo thuộc loại ngữ pháp, bỏ các loại chính tả, kiểu trình bày và phong cách.
Vì vậy “không có cảnh báo” chỉ là công cụ không phát hiện, giống chuông không reo chưa đủ chứng minh nhà không có người.
Nguồn: `e88d82c:docs/feature_specification.md`, Shared preprocessing và Interpretation limits.

### 12. Trên mẫu ngẫu nhiên, công cụ đếm thiếu bao nhiêu?

Mẫu có 36 bài, được bốc ngẫu nhiên trong từng vùng điểm: mỗi vùng thấp, giữa, cao có 12 bài, nên không phải mẫu ngẫu nhiên đều của toàn bộ tập.
Người đọc đếm lỗi trong tối đa 150 từ đầu; LanguageTool ở phép so này được ước lượng bằng tỷ lệ lỗi toàn bài nhân độ dài đoạn đọc, không được đếm trực tiếp lại trên đoạn đó.
Trung bình người đọc đếm 7,33 lỗi, công cụ ước lượng 1,24 lỗi, chênh khoảng 6,10 lỗi mỗi đoạn.
Trong vùng điểm thấp, hai bên là 10,75 và 2,59; ở vùng giữa là 7,00 và 0,89; ở vùng cao là 4,25 và 0,23 lỗi.
Các số cho thấy công cụ bỏ sót so với người đọc trong phép đối chiếu này, nhưng không phải tỷ lệ thiếu chắc chắn cho mọi bài ELLIPSE.
Nguồn: [W10, Week 10 filled random reading audit, TOOL_FORMULA và RANDOM_SAMPLE_PER_BAND/OVERALL](../reports/week10/RESULTS_week10.md).

### 13. GECToR + ERRANT khác gì và có tốt hơn không?

GECToR đề xuất sửa câu; ERRANT so câu trước và sau để phân loại chỗ sửa, giống người sửa bản nháp rồi người khác kiểm những vết bút đỏ.
Cách đếm mới chỉ giữ nhóm sửa được quy định là ngữ pháp, loại các nhóm chính tả, dấu câu và kiểu chữ; một đề xuất sửa vẫn có thể không phải lỗi thật.
Trên 68 đoạn đã có người đếm, trung bình người đọc là 8,32 lỗi, LanguageTool ước lượng 1,32, còn cách mới đếm 14,32: cách mới đếm dư khoảng 6,00, cách cũ đếm thiếu khoảng 7,00 lỗi.
Trên riêng 36 bài ngẫu nhiên, cách mới là 14,33 so với người đọc 7,33, chênh 7,00 lỗi và kém hơn khoảng cách 6,10 của công cụ cũ; trên mẫu 32 bài chọn có chủ đích, cách mới là 14,31 so với người đọc 9,44, chênh 4,875 lỗi và gần hơn khoảng cách 8,016 của cách cũ.
Ví dụ từng bài trong bảng dưới cho thấy cách mới có lúc khớp người đọc, có lúc đếm dư nhiều; trong riêng 36 bài ngẫu nhiên, mỗi vùng có 12 bài, vùng thấp có người đọc 10,75, cách cũ 2,59, cách mới 26,50, còn vùng cao tương ứng 4,25, 0,23 và 5,58 lỗi.
Nguồn: [W10, Exploratory Part A, bảng Sample/Tool và interpretation; dòng 1420 và 1422 cho vùng thấp/cao](../reports/week10/RESULTS_week10.md), cùng bảng đếm từng bài dẫn dưới; kết quả gộp đạt tiêu chí thăm dò đã đặt nhưng không chứng minh tốt hơn trên mọi mẫu hay mọi bài.

| Mã bài | Người đọc | LanguageTool ước lượng | GECToR + ERRANT đếm ngữ pháp | Nguồn |
|---|---:|---:|---:|---|
| `0AFC8CE27321` | 5 | 0 | 5 | [gec_part_a_68.csv, dòng 38](../reports/week10/gec_part_a_68.csv) |
| `0514D25768A0` | 9 | 3,20 | 12 | [gec_part_a_68.csv, dòng 2](../reports/week10/gec_part_a_68.csv) |
| `A4DA4201903F` | 15 | 3,57 | 48 | [gec_part_a_68.csv, dòng 19](../reports/week10/gec_part_a_68.csv) |

Đã đối chiếu ba mã bài với các cột `reader`, `LT_estimate`, `edits_grammar` của bảng đã lưu; cách cũ là ước lượng trên tối đa 150 từ đầu, không phải số đếm trực tiếp trên đoạn đó. Hai số theo vùng có nguồn `RANDOM_BAND`: 318/12 = 26,50 và 67/12 = 5,583333… ≈ 5,58, tại [W10, dòng 1420 và 1422](../reports/week10/RESULTS_week10.md).

### 14. Đã dùng GECToR để thử dự đoán điểm chưa?

**Chưa**, theo kết quả đã lưu được phép dùng cho sổ tay.
Báo cáo mới có đối chiếu cách đếm lỗi trên mẫu nhỏ, chưa chạy phần thay đặc trưng rồi huấn luyện và đo điểm.
Phần đếm trên toàn bộ development cũng chưa thực hiện; lần thử thời gian ban đầu đã chạm điều kiện phải dừng, sau đó mới hoàn thành phần đối chiếu mẫu nhỏ.
Giống mua được thước mới và thử đo vài vật chưa có nghĩa đã dùng thước đó xây xong căn nhà.
Nguồn: [W10, Exploratory GECToR, bảng Requested result; Exploratory Part A, interpretation](../reports/week10/RESULTS_week10.md).

<a id="phan-e"></a>
## Phần E. Kết quả chính và vì sao

Nói gọn là: hai máy cùng sai là điểm yếu lớn của cách chọn bài theo bất đồng.

### 15. Cách bất đồng tìm được bao nhiêu bài sai?

Trên Validation có 69 bài sai lớn: chọn đọc 153 bài tìm được 15 bài sai, so với kỳ vọng ngẫu nhiên 13,85 bài, tính từ 69 × 153 / 762; nguồn là [W9, dòng 23 và 32](../reports/week9/RESULTS_week9.md).
Báo cáo Test đã lưu ghi 208 bài sai lớn: đọc 504 bài tìm được 47, so với kỳ vọng ngẫu nhiên 41,63 bài, tính từ 208 × 504 / 2.518; nguồn chính xác là [W9, dòng 24 và 33](../reports/week9/RESULTS_week9.md).
Trong thử nghiệm thăm dò chia theo đề bài trên development, có 386 bài RF sai lớn: đọc tổng 764 bài tìm được 88, so với kỳ vọng ngẫu nhiên 77,362908 bài.
Trung bình mô phỏng 1.000 lượt là 41,427 trên Test và 13,946 trên Validation, khác kỳ vọng theo công thức tương ứng 41,633042… ≈ 41,63 và 13,854330… ≈ 13,85 do chỉ lấy hữu hạn lượt bốc; các số mô phỏng được giữ đúng nhãn, không dùng thay kỳ vọng. Nguồn: [W9, Task 0, dòng 23–24 và 32–33](../reports/week9/RESULTS_week9.md).
Cách bất đồng tìm nhiều hơn về số đếm trong các ví dụ này, nhưng kết quả chưa đủ để kết luận nó đáng tin cậy hơn ngẫu nhiên.
Nguồn: [W9, Task 0; Task 3; Week 9b, CAPTURE_METRICS](../reports/week9/RESULTS_week9.md).

### 16. Lỗi chung là gì, và vì sao khó phát hiện?

Lỗi chung là một bài mà cả RF và Ridge đều sai lớn, giống hai đồng hồ cùng chạy chậm nên vẫn chỉ giờ gần nhau.
Trong development chia theo đề bài, 276 trên 386 bài RF sai lớn cũng là bài Ridge sai lớn, tức khoảng 71,5% tính từ hai số đã lưu.
Ở phép đếm này, hai máy có thể sai lớn ở hai mặt chấm khác nhau; đừng hiểu tất cả đều sai cùng chiều ở cùng một mặt.
Khi hai dự đoán gần nhau mà đều xa điểm người chấm, mức bất đồng nhỏ sẽ không kéo bài lên đầu danh sách.
Riêng danh sách 276 bài lỗi chung, bất đồng tìm được 44 bài, trong khi ngẫu nhiên kỳ vọng khoảng 55,32 bài.
Nguồn: [W9, Task 3, bảng Prompt-disjoint và A3 Both wrong](../reports/week9/RESULTS_week9.md); 71,5% là phép tính làm tròn từ 276 chia 386, không phải lần đo mới.

### 17. “Nén về giữa thang” nghĩa là gì?

Nó nghĩa là điểm máy tập trung ở vùng giữa hơn điểm người chấm, giống người hay trả lời “khá” cho cả món rất ngon lẫn món rất dở.
Trên Validation, nhóm 29 bài có điểm Từ vựng dưới 2,5 được người chấm trung bình 1,93, nhưng RF cho khoảng 2,92 và Ridge cho 2,85.
Ở nhóm 25 bài có điểm Từ vựng trên 4,0, người chấm trung bình 4,64, còn RF cho 3,66 và Ridge cho 3,65.
Máy vì thế có thể cùng nâng bài yếu và cùng hạ bài giỏi, làm bất đồng không nổi bật dù lỗi lớn.
Đây là bằng chứng mô tả phù hợp với hiện tượng nén về giữa; nó chưa chứng minh đầy đủ nguyên nhân gây ra hiện tượng.
Nguồn: [W10, Part B, Validation TRUTH_BAND_MEANS](../reports/week10/RESULTS_week10.md).

### 18. TF-IDF và MiniLM đọc khác ở đâu, có giúp chọn bài không?

TF-IDF nhìn dấu hiệu từ/cụm từ nổi bật, MiniLM biến đoạn văn thành dấu hiệu có ngữ cảnh, còn các máy ban đầu chỉ nhìn phiếu đặc trưng đã thiết kế.
Trong 276 bài RF/Ridge cùng sai, TF-IDF vẫn sai lớn ở 203 bài và có cả hai điểm dưới ngưỡng sai lớn ở 73 bài; MiniLM tương ứng là 191 và 85 bài, nhưng RF vẫn sai trên các bài cũ đó.
Với cùng 386 bài RF sai lớn và ngân sách đọc tổng 764 bài, bất đồng cũ tìm 88, bất đồng RF–TF-IDF tìm 81, bất đồng RF–MiniLM tìm 93, so với kỳ vọng ngẫu nhiên khoảng 77,36.
TF-IDF chưa cải thiện chọn bài; MiniLM có dấu hiệu khả quan so với mốc ngẫu nhiên theo phép so có điều kiện trong báo cáo, nhưng chưa chứng minh tốt hơn cách cũ hay xác nhận trên dữ liệu mới.
Khi chỉ xét 217 bài RF và MiniLM cùng sai, bất đồng RF–MiniLM tìm 36 so với ngẫu nhiên kỳ vọng 43,50, nên vấn đề lỗi chung vẫn còn.
Nguồn: [W10, B2 concise result tables và Evidence-only interpretation](../reports/week10/RESULTS_week10.md); số bài “hết sai lớn” chỉ nói về nguồn thay thế, không có nghĩa đã sửa điểm RF.

### 19. MiniLM chỉ đọc đoạn đầu thì phải hiểu kết quả thế nào?

MiniLM dùng tối đa 256 token đầu; token là mảnh văn bản máy đọc, giống các mảnh ghép của từ, nên không được coi là đúng 256 từ.
Nếu bài dài hơn giới hạn, đoạn cuối không vào phiếu mã hóa của MiniLM.
Vì thế kết quả này nói về cách đọc đoạn đầu đã chốt, không đại diện mọi cách dùng MiniLM để đọc toàn bài.
Khả năng máy bỏ qua lỗi hoặc ý quan trọng ở cuối bài là **đây là suy đoán** hợp lý về giới hạn đầu vào; chưa có phép đo riêng mức ảnh hưởng trong nguồn được dùng.
Nguồn giới hạn: [W10, B2 Evidence-only interpretation, native truncation](../reports/week10/RESULTS_week10.md).

### 20. Độ phân tán giữa các cây là gì, kết quả ra sao?

RF có 300 cây, và độ lệch chuẩn là số đo mức các cây đoán xa nhau, giống xem ý kiến trong một hội đồng tụ lại hay tản ra.
Tín hiệu lấy mức phân tán lớn hơn giữa Từ vựng và Ngữ pháp; lớn hơn thì được ưu tiên đọc lại.
Trên Validation, nó tìm được 25 trong 69 bài sai lớn, nhưng đã được chọn sau khi xem kết quả tập này.
Trên development chia theo đề bài, cùng ngân sách tổng 764 bài, nó tìm 96 trong 386 bài sai lớn, so với bất đồng cũ 88 và kỳ vọng ngẫu nhiên khoảng 77,36.
Chưa thể coi là xác nhận vì development đã được dùng trước; kết quả đáng quan tâm không biến một bộ dữ liệu cũ thành bài thi mới.
Nguồn: [Khóa, Signal definition và Status](signal_lock_tree_spread.md); [W9, Week 9b, RF tree spread, CAPTURE_METRICS](../reports/week9/RESULTS_week9.md).

**Kết quả mới đã lưu ngày 26/10/2026:** trên Official Test dùng lại, tín hiệu cây đã khóa chọn đọc 504 trong 2.518 bài, bắt được **55/208** bài RF sai lớn; kỳ vọng ngẫu nhiên **41,633042 ≈ 41,63**, p chính xác một phía **0,01158570685**. Hai RF đã lưu được dùng nguyên trạng, không huấn luyện lại; nhãn sai lớn và tập ID 208 bài khớp hồ sơ cũ trước khi tính tín hiệu.
So với D đã có **47/208**, số bắt được cao hơn **8 bài**, nhưng p trên là so với ngẫu nhiên, **không phải kiểm định tín hiệu cây tốt hơn D**. Không tính lại D hoặc thử tín hiệu khác trong lần chạy này. Đây là **Test lần dùng thứ hai, không phải xác nhận độc lập sạch**, vì Test đã được xem trong đánh giá chính.
Nguồn: [RESULTS_tree_spread_second_use.md, Kết quả hoàn thành sau sửa chốt chặn log](../reports/week9/RESULTS_tree_spread_second_use.md), cùng log `_attempt2` được dẫn trong báo cáo; commit lưu kết quả **`97159a6`**.

<a id="phan-f"></a>
## Phần F. Trung thực và kiểm soát

Nói gọn là: phải ghi rõ cái gì đã chốt, cái gì mới thử và bằng chứng còn thiếu ở đâu.

### 21. Khóa tín hiệu để làm gì?

Tín hiệu là con số dùng xếp bài cần đọc, giống đèn báo nhắc kiểm tra.
File khóa ghi cách tính, cách phá hòa khi bằng điểm, ngân sách đọc và quy trình đánh giá tương lai.
Hash là dấu vân tay của file để phát hiện nội dung thay đổi; ngày giờ giúp xác định bản chốt được ghi lúc nào.
Giống viết dự đoán vào phong bì niêm phong trước khi xem đáp án, nó giúp ngăn đổi luật sau khi biết kết quả.
Bản khóa ghi thời điểm 19/10/2026 lúc 05:41:03 theo giờ UTC, tức giờ chuẩn quốc tế, nhưng chính bản khóa cũng nói tín hiệu được chọn sau khi xem Validation nên không biến kết quả cũ thành xác nhận.
Nguồn: [Khóa, Future confirmation protocol, Status và Provenance](signal_lock_tree_spread.md).

### 22. Thăm dò khác xác nhận thế nào?

Thăm dò là tìm ý tưởng trên dữ liệu đã biết, giống làm nháp rồi đổi cách giải.
Xác nhận là chốt cách làm trước và thử trên dữ liệu độc lập chưa dùng để chọn cách, giống làm đề thi mới sau khi đã nộp bản nháp.
Official Test đã được dùng một lần cho đánh giá chính được báo cáo ở tuần chín; tuần chín còn kiểm tra lại các số đánh giá đã chốt từ dự đoán lưu sẵn.
Các phân tích mở rộng trước lần dùng Test thứ hai chạy trên development và Validation, gắn nhãn thăm dò: chia theo đề bài, chẩn đoán lỗi, độ phân tán cây, độ nén điểm, đọc mẫu, TF-IDF, MiniLM và so đếm GECToR.
**Ngày thầy cho phép lần hai: 26/10/2026**, nguồn nhận xét tuần 10 của thầy Khánh, theo xác nhận của người phụ trách đã ghi trong nháp và RESULTS. Ngày chạy Test đầu tiên và toàn bộ thứ tự thay đổi trước đó vẫn chưa được xác minh độc lập trong hồ sơ hiện có.
Lần dùng Test thứ hai đã hoàn thành cho đúng một tín hiệu độ lệch chuẩn giữa 300 cây RF khóa tại commit **`4e38115`**, dùng lại RF đã lưu tuần 9. Kết quả **55/208**, ngân sách **504**, được lưu tại commit **`97159a6`**; đây không phải xác nhận độc lập sạch. Việc sửa sổ tay hiện tại chỉ trích hồ sơ này, không truy cập lại dữ liệu Test.

Lịch sử các lần gọi script cần phân biệt với lần đánh giá tín hiệu:

1. Lần gọi đầu ngày 26/10/2026 dừng ở kiểm tra khớp dự đoán Vocabulary: 2.015 dòng vượt dung sai cũ `1e-12`, lệch lớn nhất `4,995115432393504e-12`; chưa tính tín hiệu, chưa kiểm tra số sai lớn 208.
2. Chẩn đoán chỉ trên 762 bài Validation cho thấy hai lần dự đoán RF khớp tuyệt đối; làm tròn `%.12g` tái tạo đúng bản lưu. Dung sai được đổi thành `atol=1e-11, rtol=0` cho cả hai đích, dựa trên development, không dựa trên số liệu Test.
3. Lần gọi tiếp theo bị chặn vì log STOPPED cũ tồn tại; không mở Test. Sau đó chỉ sửa quản lý log: giữ log cũ, cho ghi file thử tiếp mới khi chưa có kết quả; vẫn chặn khi đã hoàn thành.
4. Sau chỉ dẫn chạy tiếp, script được gọi đúng một lần trong lượt cho phép đó và hoàn thành lúc **14:27:32 ngày 26/10/2026 (UTC+07:00)**, ghi log `_attempt2` với `status=COMPLETED`. Không có tín hiệu nào khác được thử. Log STOPPED cũ được giữ nguyên.

Nguồn: [W9, Task 0 và giới hạn lịch sử](../reports/week9/RESULTS_week9.md); [W10, các mục Exploratory](../reports/week10/RESULTS_week10.md); [RESULTS lần dùng Test thứ hai, Kết quả hoàn thành và Sự cố lần chạy đầu](../reports/week9/RESULTS_tree_spread_second_use.md). Nháp chuẩn bị ban đầu ở commit `c7c42b9` là hồ sơ lịch sử, không còn là trạng thái chạy hiện tại.

### 23. Nhóm còn thiếu hoặc chưa chắc những gì?

- **Mới có một người đếm lỗi cho phép đối chiếu chính;** bộ chuẩn bị cho người thứ hai còn chờ điền, nên chưa biết người khác có đếm giống vậy không. Nguồn: [W10, second-reader agreement preparation](../reports/week10/RESULTS_week10.md).
- **Chưa xác nhận thứ tự đọc trước hay sau khi xem đáp án;** bảng tính hiện tại không chứng minh lịch sử nhìn từng ô, nên chưa thể khẳng định lượt đầu là đọc mù, tức đọc khi chưa biết điểm và dự đoán. Nguồn: [W10, Provenance of blind reading](../reports/week10/RESULTS_week10.md).
- **Năm bài đã được chốt, nhưng chưa có kết quả đọc độc lập mới;** người phụ trách đã xác nhận năm mã ở bảng dưới. Tên nhóm là **“điểm từ 4,0 trở lên ở đích bị sai”**: điểm thật ≥4,0 tại đích đó và RF dự đoán thấp hơn ít nhất 1,0. Không dùng điều kiện điểm trung bình >4,0 để gọi tên nhóm. Hồ sơ tuần 10 ban đầu ghi chưa chốt; quyết định xác nhận và bộ phiếu mới lưu tại commit **`aa13e83`**. Nguồn: [README bộ phiếu](independent_readers_README.md), đối chiếu danh sách ứng viên trong [W10, five unexplained cases source clarification](../reports/week10/RESULTS_week10.md).
- **GECToR chưa chạy toàn development hay thử chấm điểm;** kết quả đếm trên mẫu nhỏ chưa cho biết đặc trưng mới có giúp chấm hoặc chọn bài toàn tập không. Nguồn: [W10, Exploratory Part A, interpretation](../reports/week10/RESULTS_week10.md).
- **Repo này chưa phải bằng chứng tái lập độc lập;** kiểm tra lại số và chạy lặp trong cùng dự án giống tự kiểm bài của mình, còn bằng chứng một bên khác dựng lại trọn quy trình từ đầu thì **chưa có nguồn** trong phạm vi đã tra. Nguồn về phạm vi kiểm tra hiện có: [W9, Task 0, Task 3 Artifact verification](../reports/week9/RESULTS_week9.md).

**Bộ phiếu A/B đang ở bước chờ hai thành viên đọc và nộp:**

| Mã bài đã chốt | Đích bị sai | Điểm thật ở đích đó |
|---|---|---:|
| `51DA4BA94C7C` | Ngữ pháp | 4,0 |
| `D1D770AF6855` | Từ vựng | 5,0 |
| `4032ED0063E4` | Ngữ pháp | 4,0 |
| `0FFB44B5D0C2` | Từ vựng | 4,0 |
| `277A95AC0190` | Ngữ pháp | 4,0 |

Hai phiếu tại `outputs/independent_readers_20261026/doc_reader_A.xlsx` và `doc_reader_B.xlsx` có thứ tự khác nhau, seed 42, dùng mã tạm R1–R5 riêng theo từng người; ánh xạ nằm ở `reader_id_map.json` trong cùng thư mục. Mỗi phiếu có 46 ô người đọc để trống khi tạo. Phiếu có văn bản và file ánh xạ đều được Git bỏ qua, không commit; mẫu không có bài luận và các công cụ được commit.
Người đọc phải nộp Phần A trước khi xem thông tin mô hình, sau đó tự điền Phần B, thời gian, xác nhận độc lập và chữ ký; không trao đổi trước khi cả hai nộp. `scripts/week10/compare_readers.py` chỉ ghép hai bản theo ánh xạ và so tập mã nguyên nhân thành “giống nhau hoàn toàn / một phần / khác”; thiếu ô hoặc thiếu xác nhận thì dừng. Kiểm tra công cụ bằng dữ liệu giả đã đạt và file giả đã được dọn. **Chưa có kết quả so sánh hai bản đọc thật trong hồ sơ đã lưu**, không gán nguyên nhân hoặc mức tự tin thay người đọc.
Nguồn cho bảng, đường dẫn và trạng thái tạo phiếu: [docs/independent_readers_README.md](independent_readers_README.md), commit `aa13e83`; nguồn số ban đầu là `reports/week9/t4_reading_summary.csv`. Các phiếu hiện điểm thật nên không gọi quy trình này là chấm mù hoàn toàn; thứ tự xem sheet dựa trên nộp bài và người đọc tự xác nhận.

<a id="phan-g"></a>
## Phần G. Tổng kết và hướng đi

Nói gọn là: kết quả âm giúp nhóm nhận ra điểm mù, còn các dấu hiệu mới cần được thử thật công bằng.

### 24. Dự án tìm ra điều gì?

Dự án chưa chứng minh được rằng hai máy bất đồng là cách đáng tin để tìm bài chấm sai hơn chọn ngẫu nhiên.
Một điểm yếu được quan sát là hai máy thường cùng sai và cùng cho điểm về phía giữa thang.
Đổi sang nguồn đọc văn bản khác làm thay đổi một phần lỗi, nhưng không tự bảo đảm tìm được bài sai tốt hơn.
MiniLM và độ phân tán cây có kết quả thăm dò đáng theo dõi; công cụ đếm lỗi mới cũng có mặt được và mặt chưa được.
Tín hiệu cây đã có thêm kết quả **55/208** trên Test dùng lại, so với **47/208** của D đã lưu và kỳ vọng ngẫu nhiên khoảng **41,63**; p so với ngẫu nhiên là **0,0115857**, nhưng chưa có kiểm định trực tiếp hơn D và đây không phải xác nhận độc lập sạch.
Kết quả âm của giả thuyết bất đồng vẫn có ích: nó chỉ ra “hai người đồng ý” chưa phải “hai người đúng”, và giúp tránh khẳng định quá sớm.
Nguồn tổng hợp: [W9](../reports/week9/RESULTS_week9.md), [W10](../reports/week10/RESULTS_week10.md), [Khóa](signal_lock_tree_spread.md) và [RESULTS lần dùng Test thứ hai](../reports/week9/RESULTS_tree_spread_second_use.md).

### 25. Kịch bản giải thích cho thầy trong khoảng một phút

“Thưa thầy, nhóm em muốn giúp giáo viên chọn bài máy có thể chấm sai để đọc lại trước, khi chỉ đủ thời gian xem khoảng 20% số bài.
Ban đầu nhóm so điểm của Ridge và rừng cây quyết định, nghĩ hai máy càng khác nhau thì bài càng đáng nghi.
Trên Validation, cách này tìm 15 trong 69 bài sai lớn, trong khi chọn ngẫu nhiên trung bình tìm gần 14 bài, nên chưa chứng minh được lợi ích.
Nhóm thấy hai máy thường cùng sai, giống hai đồng hồ cùng chạy chậm, nên nhìn mức khác nhau giữa chúng chưa đủ.
Nguồn đọc văn bản và độ phân tán giữa các cây có vài dấu hiệu mới, còn công cụ đếm lỗi ngữ pháp cũng có thể đếm thiếu hoặc đếm dư.
Tín hiệu cây vừa tìm 55 trong 208 bài sai lớn trên Test dùng lại, cao hơn số 47 của bất đồng, nhưng chưa kiểm định trực tiếp hơn bất đồng và không phải xác nhận độc lập sạch.
Nhóm muốn chốt cách đánh giá, kiểm tra người đếm và thử trên dữ liệu mới trước khi nói đã có cách hỗ trợ giáo viên đáng tin.”

Nguồn số trong lời thoại: [W9, Task 0](../reports/week9/RESULTS_week9.md) và [RESULTS lần dùng Test thứ hai](../reports/week9/RESULTS_tree_spread_second_use.md); các nhận xét tổng hợp từ [W9](../reports/week9/RESULTS_week9.md), [W10](../reports/week10/RESULTS_week10.md) và [Khóa](signal_lock_tree_spread.md); thời lượng là mục tiêu trình bày do người dùng yêu cầu, chưa đo bằng đọc thành tiếng.

### 26. Nên làm gì tiếp, và hỏi thầy điều gì?

**Đề xuất của người viết, chưa kiểm chứng hiệu quả:** trước hết để hai thành viên hoàn thành phiếu A/B của năm bài đã chốt, giữ bản nộp Phần A rồi mới xem thông tin mô hình, và chỉ chạy công cụ so sau khi cả hai nộp đủ. Đồng thời hoàn tất đối chiếu người đếm thứ hai của mẫu đếm lỗi trước đây; đây là hai việc khác nhau.
Tiếp theo, giữ nguyên khóa độ phân tán cây và xin một bộ bài mới độc lập, đủ điều kiện riêng tư, để kiểm tra lời hứa hỗ trợ giáo viên.
Sau đó mới cân nhắc chạy GECToR toàn development và thử tác dụng của đặc trưng mới lên điểm số, vì đếm lỗi gần người hơn chưa chắc chấm điểm tốt hơn.
Với MiniLM, có thể thiết kế riêng thử nghiệm đọc thêm phần cuối bài; **đây là suy đoán** về một hướng cải tiến, chưa phải kết quả đã có.
Nên hỏi thầy: mục tiêu chính là chấm chính xác hay chọn bài cần đọc lại; điều kiện nào đủ gọi là xác nhận; có dữ liệu mới phù hợp không; và tiêu chí đếm lỗi giữa người đọc cần thống nhất thế nào?
Căn cứ đề xuất: các giới hạn trong [W10, second-reader preparation, Provenance, Part A và B2](../reports/week10/RESULTS_week10.md), [README bộ phiếu](independent_readers_README.md), [RESULTS Test dùng lại](../reports/week9/RESULTS_tree_spread_second_use.md), cùng [Khóa, Future confirmation protocol](signal_lock_tree_spread.md).

### 27. Sơ đồ từ đầu đến cuối

Sơ đồ dưới ghi nơi triển khai từng bước để tra cứu, không phải lệnh cần chạy trong lần viết sổ tay này.
Tuyến chính dùng đặc trưng ban đầu; các tuyến TF-IDF, MiniLM và độ phân tán cây là thử nghiệm mở rộng.
Nguồn quy trình và ngân sách: `e88d82c:docs/split_and_leakage_protocol.md`, [W9, Task 0 và Task 3](../reports/week9/RESULTS_week9.md), [W10, OOF comparison và B2](../reports/week10/RESULTS_week10.md), [Khóa](signal_lock_tree_spread.md).

```text
DỮ LIỆU: các phần học/thử được chia và lọc đủ điều kiện
  [scripts/phase3_build_split.py;
   src/mla_project/data/make_splits.py;
   docs/split_and_leakage_protocol.md]
  → ĐẶC TRƯNG: phiếu mô tả độ dài, từ vựng, ngữ pháp, cấu trúc câu
    [scripts/phase4_extract_features.py;
     src/mla_project/features/build_features.py;
     docs/feature_specification.md]
  → MÔ HÌNH: Ridge và RF học từ điểm người chấm trong phần được phép học
    [scripts/phase6_train_models.py;
     src/mla_project/models/train_ridge.py;
     src/mla_project/models/train_random_forest.py]
  → DỰ ĐOÁN: điểm Từ vựng/Ngữ pháp trên phần giữ lại
    [src/mla_project/models/predict.py;
     scripts/week9/t3_evaluate.py cho thử nghiệm chia theo đề bài]
  → CHỌN KHOẢNG 20% BÀI: xếp theo mức bất đồng, làm tròn ngân sách lên
    [src/mla_project/review/disagreement.py;
     src/mla_project/evaluation/review_metrics.py;
     scripts/week9/t3_evaluate.py cho từng hàng đợi theo phần]
  → SO VỚI NGẪU NHIÊN: đối chiếu số bài RF sai lớn tìm được
    [scripts/week9/t0_provenance.py cho kiểm tra lại số đã lưu;
     scripts/week9/t3_evaluate.py cho thử nghiệm mở rộng;
     reports/week9/RESULTS_week9.md cho kết quả]

Nhánh đọc văn bản:
  scripts/week10/information_sources_oof.py → TF-IDF + Ridge
  scripts/week10/gec_b2.py → MiniLM + Ridge
  → reports/week10/RESULTS_week10.md

Nhánh độ phân tán cây:
  scripts/week9b/tree_spread_oof.py
  → scripts/week9b/paired_tree_spread.py
  → reports/week9/RESULTS_week9.md
  → docs/signal_lock_tree_spread.md cho quy trình xác nhận tương lai

Kết quả Test dùng lại đã lưu (không phải lệnh chạy tiếp):
  scripts/tree_spread_official_test_second_use.py
  → reports/week9/RESULTS_tree_spread_second_use.md

Nhánh đọc độc lập năm bài development/Validation:
  scripts/week10/create_reader_packets.py + reader_packets.mjs
  → phiếu A/B và ánh xạ riêng tư (git-ignored), chờ người đọc tự điền
  → scripts/week10/compare_readers.py (chỉ dùng sau khi cả hai nộp đủ)
  → docs/independent_readers_README.md
```

<a id="tu-kho"></a>
## Từ khó → nghĩa dễ hiểu

| Từ khó | Nghĩa dễ hiểu |
|---|---|
| ELLIPSE | Tên bộ bài viết tiếng Anh có điểm người chấm. |
| Mô hình | Chương trình học cách đoán từ các ví dụ, như học chấm qua bài mẫu. |
| Huấn luyện | Cho máy học từ các bài và điểm có sẵn. |
| Điểm tham chiếu | Điểm người chấm dùng làm mốc đối chiếu, như đáp án kiểm tra. |
| Từ vựng | Cách chọn và dùng từ trong bài. |
| Ngữ pháp | Cách ghép từ thành câu theo quy tắc. |
| Development | Vùng dữ liệu để xây dựng cách làm, như tập bài luyện. |
| Model-train | Phần bài cho máy học quy luật. |
| Validation | Phần tập dượt để kiểm tra các lựa chọn trước bài thi cuối. |
| Official Test | Phần kiểm tra cuối được giữ riêng. |
| Prompt | Đề bài học sinh nhận được. |
| Fold | Một phần được giữ lại để thử khi máy học từ các phần khác. |
| Dự đoán ngoài phần học | Điểm đoán cho bài không nằm trong phần máy vừa học. |
| Đặc trưng | Một số mô tả bài, như số từ hoặc mức lặp từ. |
| Mốc so sánh ban đầu | Cách đơn giản dùng để xem cách mới có ích hơn không. |
| Ridge | Máy cộng ảnh hưởng của đặc trưng, có lực giữ ảnh hưởng quá lớn. |
| RF | Rừng các chuỗi câu hỏi rẽ nhánh, cùng góp điểm đoán. |
| Bất đồng | Khoảng cách giữa điểm hai máy cho cùng bài. |
| Sai lớn | Điểm máy cách điểm người chấm đến ngưỡng đã định. |
| Sai lệch tuyệt đối trung bình | Trung bình khoảng cách giữa điểm máy và người chấm. |
| Lỗi chung | Một bài mà các máy đang xét đều chấm sai lớn. |
| Nén về giữa | Máy hay đoán quanh vùng điểm giữa, kể cả bài rất yếu hoặc rất giỏi. |
| LanguageTool | Công cụ dò chỗ đáng nghi bằng các quy tắc ngôn ngữ. |
| spaCy | Công cụ chia câu, tách từ và nhận diện cấu trúc câu. |
| GECToR | Máy đề xuất sửa câu. |
| ERRANT | Công cụ đối chiếu câu gốc và câu sửa để phân loại chỗ sửa. |
| TF-IDF | Cách làm nổi bật từ/cụm từ đặc trưng, như bút đánh dấu. |
| MiniLM | Máy biến đoạn văn thành dấu hiệu bằng số có xét ngữ cảnh. |
| Token | Mảnh văn bản máy xử lý, có thể chỉ là một phần của từ. |
| Độ lệch chuẩn | Mức các con số tản xa nhau, như hội đồng có ý kiến chênh nhau nhiều hay ít. |
| Tín hiệu | Con số giúp xếp bài đáng kiểm tra lên trước. |
| Ngân sách đọc | Số bài giáo viên có thời gian đọc lại. |
| Kỳ vọng ngẫu nhiên | Mức trung bình tính theo cách bốc, không phải số chắc chắn của một lượt. |
| Thăm dò | Tìm ý tưởng trên dữ liệu đã biết, giống làm nháp. |
| Xác nhận | Thử cách đã chốt trên dữ liệu mới chưa dùng để chọn cách. |
| Khóa tín hiệu | Ghi luật trước khi thử tiếp, như niêm phong dự đoán. |
| Hash | Dấu vân tay của nội dung file, giúp nhận ra file đã đổi. |
| Commit | Một bản lưu có mã trong lịch sử Git. |
| Đọc mù | Đọc và đánh giá trước khi biết điểm, dự đoán và kết quả công cụ. |
| Tái lập độc lập | Một bên khác dựng lại quy trình và kiểm tra kết quả, như nhờ người khác làm lại bài toán. |

<a id="so-lieu"></a>
## Số liệu và nguồn

Các dòng dưới liệt kê số lượng, ngưỡng, điểm số, tỷ lệ và thời điểm dùng trong nội dung; những số lặp lại dùng chung dòng nguồn.
Số làm tròn được tính trực tiếp từ kết quả đã lưu, không chạy lại mô hình hay đo lại dữ liệu.
Số thứ tự câu và nhãn kỹ thuật trong đường dẫn không mang nghĩa kết quả đo.

| Số liệu đã dùng | Ý nghĩa / nơi dùng | Nguồn được phép |
|---|---|---|
| Nhóm 03; khoảng một phút | Nhãn nhóm và mục tiêu thời lượng của câu 25; thời lượng chưa đo | Yêu cầu người dùng; không phải số liệu thí nghiệm |
| Lớp 8–12; 6.482; 3.911; 2.571 | Đối tượng và quy mô bộ bài đáng tin cậy | `e88d82c:docs/data_card.md`, Population và Data quality |
| Hai người chấm; sáu mặt phân tích và điểm Tổng thể | Cách chấm bộ gốc | `e88d82c:docs/data_card.md`, Human-rating process và Rubric |
| 1–5; bước 0,5 | Thang điểm | `e88d82c:docs/data_card.md`, Valid score range |
| Hai điểm: Từ vựng và Ngữ pháp; lệch ít nhất 1 điểm | Đầu ra dự đoán và ngưỡng bài sai lớn | [Khóa, Signal definition](signal_lock_tree_spread.md) |
| 20%; một phần năm; làm tròn lên | Ngân sách đọc | [Khóa, Signal definition](signal_lock_tree_spread.md); [W9, Task 0](../reports/week9/RESULTS_week9.md) |
| 3.128 → 3.050; 783 → 762; 3.911 → 3.812 | Số bài trước/sau lọc đủ điều kiện riêng tư | [t3_eligibility_counts.csv](../reports/week9/t3_eligibility_counts.csv) |
| 2.571 → 2.518 | Số bài kiểm tra cuối trước/sau lọc | `e88d82c:docs/split_and_leakage_protocol.md`, Outcome và Privacy status |
| 5 phần | Cách chia thử nghiệm theo đề bài | [W9, Task 3](../reports/week9/RESULTS_week9.md); [Khóa](signal_lock_tree_spread.md) |
| 14 đặc trưng; quy về 100 từ | Bộ đầu vào và đơn vị của đặc trưng cảnh báo lỗi | `e88d82c:docs/feature_specification.md`, Feature table |
| 0,373424 / 0,463037 | Ridge: Từ vựng / Ngữ pháp | [W10, B2 concise result tables](../reports/week10/RESULTS_week10.md) |
| 0,372165 / 0,455404; khoảng 0,372, gần bốn phần mười | RF: Từ vựng / Ngữ pháp và lời diễn giải làm tròn | [W10, B2 concise result tables](../reports/week10/RESULTS_week10.md) |
| 0,406626 / 0,506841 | TF-IDF + Ridge: Từ vựng / Ngữ pháp | [W10, B2 concise result tables](../reports/week10/RESULTS_week10.md) |
| 0,404448 / 0,507 | MiniLM + Ridge: Từ vựng / Ngữ pháp; Ngữ pháp làm tròn trực tiếp số gốc 0,50749980021123497 đến ba chữ số thập phân | [W10, dòng 1564, B2,G,3812](../reports/week10/RESULTS_week10.md) |
| 36; 12 mỗi vùng; tối đa 150 từ đầu | Thiết kế mẫu đọc ngẫu nhiên trong từng vùng điểm | [W10, filled random reading audit, RANDOM_SAMPLE_PER_BAND và TOOL_FORMULA](../reports/week10/RESULTS_week10.md) |
| 7,33 / 1,24 / 6,10 | Người đọc / LanguageTool ước lượng / chênh lệch trung bình trên mẫu ngẫu nhiên; gốc 7,333333 / 1,236789 / 6,096544 | [W10, RANDOM_SAMPLE_OVERALL](../reports/week10/RESULTS_week10.md) |
| 10,75 / 2,59; 7,00 / 0,89; 4,25 / 0,23 | Người đọc / công cụ cũ ở vùng thấp, giữa, cao | [W10, RANDOM_SAMPLE_PER_BAND](../reports/week10/RESULTS_week10.md) |
| 68 = 36 + 32 | Mẫu gộp đối chiếu công cụ mới, từ mẫu ngẫu nhiên và mẫu có chủ đích | [W10, Exploratory Part A, Verification](../reports/week10/RESULTS_week10.md) |
| 8,32 / 1,32 / 14,32; 6,00 / khoảng 7,00 | Người đọc / công cụ cũ / công cụ mới trên mẫu gộp; khoảng cách mới / cũ | [W10, Exploratory Part A, pooled68 table và interpretation](../reports/week10/RESULTS_week10.md) |
| 14,33 / 7,33; chênh 7,00 | Công cụ mới / người đọc trên mẫu ngẫu nhiên | [W10, Exploratory Part A, random36 table](../reports/week10/RESULTS_week10.md) |
| 14,31 / 9,44; chênh 4,875 / 8,016 | Công cụ mới / người đọc trên mẫu có chủ đích; khoảng cách mới / cũ | [W10, Exploratory Part A, week9_32 table](../reports/week10/RESULTS_week10.md) |
| 26,50; 5,58 | Công cụ mới ở vùng thấp / cao; đối chiếu số người và công cụ cũ ở dòng trên | [W10, dòng 1420 và 1422, RANDOM_BAND](../reports/week10/RESULTS_week10.md) |
| 5 / 0 / 5; 9 / 3,20 / 12; 15 / 3,57 / 48 | Người đọc / công cụ cũ ước lượng / công cụ mới cho ba mã bài trong câu 13 | [gec_part_a_68.csv, dòng 38, 2 và 19 tương ứng](../reports/week10/gec_part_a_68.csv) |
| 762; 69; 153; 15; 13,854330… ≈ 13,85; 13,946 ≈ 14 | Validation: số bài, số sai lớn, số đọc, số tìm được; kỳ vọng theo công thức; trung bình mô phỏng đã lưu | [W9, Task 0, dòng 23 và 32](../reports/week9/RESULTS_week9.md); kỳ vọng bằng 69 × 153 / 762 |
| 208; 504; 47; 2.518; 41,633042… ≈ 41,63; 41,427 | Test: số sai lớn, số đọc, số tìm được, tổng số đủ điều kiện; kỳ vọng theo công thức; trung bình mô phỏng đã lưu | [W9, dòng 24 và 33](../reports/week9/RESULTS_week9.md), chỉ trích báo cáo; kỳ vọng bằng 208 × 504 / 2.518 |
| 386; 764; 88; 77,362908 ≈ 77,36 | Development chia theo đề: số RF sai lớn, tổng số đọc, bất đồng tìm được, kỳ vọng ngẫu nhiên | [W9, Week 9b, CAPTURE_METRICS pooled](../reports/week9/RESULTS_week9.md); [W10, B2 concise result tables](../reports/week10/RESULTS_week10.md) |
| 276/386 ≈ 71,5%; 44; 55,32 | Lỗi chung RF/Ridge; số tìm bằng bất đồng / kỳ vọng ngẫu nhiên trên lỗi chung | [W9, Task 3, Prompt-disjoint A1 và A3](../reports/week9/RESULTS_week9.md); phần trăm là phép chia làm tròn |
| 29; dưới 2,5; 1,93 / 2,92 / 2,85 | Validation Từ vựng thấp: số bài, ngưỡng, điểm người / RF / Ridge | [W10, Part B, Validation TRUTH_BAND_MEANS](../reports/week10/RESULTS_week10.md) |
| 25; trên 4,0; 4,64 / 3,66 / 3,65 | Validation Từ vựng cao: số bài, ngưỡng, điểm người / RF / Ridge | [W10, Part B, Validation TRUTH_BAND_MEANS](../reports/week10/RESULTS_week10.md) |
| 203 + 73; 191 + 85; tập gốc 276 | Lỗi cũ còn / hết sai lớn đối với TF-IDF, rồi MiniLM | [W10, B2 Source/Old shared-error set table](../reports/week10/RESULTS_week10.md) |
| 81; 93 | Bất đồng RF–TF-IDF / RF–MiniLM tìm được trên cùng tập RF sai lớn | [W10, B2 Anchor/Signal table](../reports/week10/RESULTS_week10.md) |
| 217; 36; 43,50 | Số lỗi chung RF/MiniLM, số tìm được, kỳ vọng ngẫu nhiên làm tròn | [W10, B2 A3_RF_B2 và interpretation](../reports/week10/RESULTS_week10.md) |
| 256 token, không phải 256 từ | Giới hạn đoạn đầu vào MiniLM | [W10, B2 Evidence-only interpretation](../reports/week10/RESULTS_week10.md) |
| 300 cây; 25/69; 96/386 | Số cây, kết quả Validation và development của độ phân tán cây | [Khóa, Signal definition và Status](signal_lock_tree_spread.md); [W9, Week 9b tree spread](../reports/week9/RESULTS_week9.md) |
| 2.518; 208; 504; 55/208; 41,633042 ≈ 41,63; p=0,01158570685; 47/208; hơn 8 bài | Tín hiệu cây trên Test dùng lại; p so với ngẫu nhiên, chỉ so số đếm với D đã lưu | [RESULTS lần dùng Test thứ hai, Kết quả hoàn thành](../reports/week9/RESULTS_tree_spread_second_use.md), commit 97159a6 |
| 26/10/2026; 14:27:32 UTC+07:00 | Ngày cho phép theo nguồn người phụ trách cung cấp; thời điểm bắt đầu lượt hoàn thành | [RESULTS lần dùng Test thứ hai](../reports/week9/RESULTS_tree_spread_second_use.md), ngày cho phép và started_utc trong log được dẫn |
| 2.015 dòng; 4,995115432393504e-12; dung sai 1e-12 → 1e-11; 762 bài Validation | Sự cố kiểm tra dự đoán và chẩn đoán CSV chỉ trên development; không có tín hiệu ở lần dừng | [RESULTS, Sự cố lần chạy đầu và Bước 1–2](../reports/week9/RESULTS_tree_spread_second_use.md) |
| 19/10/2026, 05:41:03 UTC | Thời điểm ghi trong bản khóa | [Khóa, Provenance](signal_lock_tree_spread.md) |
| Một người đếm; người thứ hai chờ điền | Trạng thái đối chiếu mẫu đếm lỗi trước đây, tách biệt với bộ phiếu A/B năm bài mới | [W10, second-reader agreement preparation](../reports/week10/RESULTS_week10.md) |
| 5 bài đã chốt; điểm thật ≥4,0 ở đích sai; RF dự đoán thấp hơn ≥1,0 | Nhóm đọc độc lập ở câu 23; một bài có điểm trung bình >4,0 không phải tiêu chí chọn hiện tại | [README bộ phiếu, danh sách và nguồn nhận diện](independent_readers_README.md), xác nhận người phụ trách; hồ sơ ứng viên tại [W10](../reports/week10/RESULTS_week10.md) |
| 2 phiếu; seed 42; R1–R5; 46 ô mỗi phiếu để trống; commit aa13e83 | Bộ phiếu A/B đã tạo, chưa có kết quả so sánh bản đọc thật trong hồ sơ | [README bộ phiếu, Cách đọc và nộp; Kiểm tra bằng dữ liệu giả](independent_readers_README.md) |
| Một đánh giá chính; lần dùng Test thứ hai đã hoàn thành; commit 97159a6 | Lịch sử dùng Test tại câu 22; không coi lần dùng lại là xác nhận độc lập sạch | [RESULTS lần dùng Test thứ hai](../reports/week9/RESULTS_tree_spread_second_use.md); [W9, Task 0](../reports/week9/RESULTS_week9.md) |
| 174/769; ngưỡng 154; 9 / 3,20; 88/386 | Bài thực hành và phép tính đã lưu dùng cho interview | [Phiếu luyện development](phieu_luyen_mot_bai_development.md), mục 2–3 |

**Những chỗ chưa đủ bằng chứng:** câu 19 chưa đo riêng ảnh hưởng bỏ đoạn cuối; câu 20 chưa có kiểm định trực tiếp hơn D và Test dùng lại không phải xác nhận độc lập sạch; câu 22 thiếu mốc chạy Test đầu tiên có xác minh độc lập; câu 23 chưa có kết quả hai bản đọc thật, chưa xác nhận lịch sử xem đáp án của mẫu cũ và chưa có bằng chứng tái lập độc lập. Danh sách năm bài mới đã chốt, không còn là mục chưa rõ danh tính.
**Những chỗ là suy luận hoặc đề xuất:** trực giác ở câu 4; diễn giải cơ chế ở câu 9; tác động có thể có của đoạn cuối ở câu 19; thứ tự ưu tiên và hướng thử tiếp ở câu 26.
**Phạm vi lần hiệu chỉnh này:** chỉ sửa file sổ tay; không sửa code, không chạy lại phân tích hoặc mô hình, không mở hay tìm trong file Official Test, file corpus gộp hoặc `full_clean_corpus_6482.csv`, không in nội dung bài luận.
**Về commit:** lần hiệu chỉnh này được người dùng yêu cầu rõ tạo một commit riêng chỉ chứa file sổ tay.

<a id="chuan-bi-interview"></a>
## Chuẩn bị interview

- **Một bài cụ thể:** `0514D25768A0` có hạng D **174/769** trong fold 5, trong khi ngân sách chỉ lấy **154** bài đầu, nên không được chọn đọc lại; người đọc đếm **9 lỗi**, công cụ cũ ước lượng **3,20 lỗi** trên 150 từ đầu. Cần nói rõ số công cụ cũ là ước lượng từ tỷ lệ toàn bài.
- **Con số đã kiểm tra:** D bắt được **88/386** bài RF sai lớn trên development chia theo đề; đây là kết quả đã tính lại và lưu trong phiếu, không phải lần chạy mới ở lần sửa sổ tay này.

Nguồn cho cả hai ý: [docs/phieu_luyen_mot_bai_development.md, mục 2 và 3](phieu_luyen_mot_bai_development.md).

- **Kết quả mới cần nói đúng phạm vi:** tín hiệu cây bắt **55/208** trên Test dùng lại, ngân sách **504**, kỳ vọng **41,63**, p so với ngẫu nhiên **0,0115857**. D đã có **47/208**; hơn **8 bài** về số đếm chưa chứng minh hơn D bằng kiểm định trực tiếp. Nguồn: [RESULTS lần dùng Test thứ hai](../reports/week9/RESULTS_tree_spread_second_use.md).
- **Việc nhóm cần tự làm:** hai thành viên đọc độc lập năm bài đã chốt bằng phiếu A/B, nộp A trước khi xem mô hình, rồi nộp B và xác nhận. Phiếu đã tạo; chưa có kết quả đọc thật trong hồ sơ, nên không được trình bày nguyên nhân do người đọc chưa điền như một phát hiện. Nguồn: [README bộ phiếu](independent_readers_README.md).

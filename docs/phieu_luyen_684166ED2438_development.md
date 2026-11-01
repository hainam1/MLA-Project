# Phiếu luyện development: 684166ED2438

Ngày lập: 26/10/2026. Chỉ dùng điểm, dự đoán và đặc trưng đã lưu; không đọc hoặc đưa nội dung bài luận vào phiếu, không chạy lại mô hình.

## Lý do chọn thay bài 0514D25768A0

Bài cũ `0514D25768A0` có Từ vựng thật 2, thuộc nhóm 276 bài RF/Ridge cùng sai lớn, nhưng dự đoán Từ vựng là RF 3,2013385365 và Ridge 3,4068243406; chưa sát mô tả hai máy cùng đoán khoảng 2,9. Nguồn: [phieu_luyen_mot_bai_development.md](phieu_luyen_mot_bai_development.md), mục 3.

Ở đây hiểu “khoảng 2,9” là dự đoán **Từ vựng** của mỗi máy trong khoảng 2,8–3,0, tức cách 2,9 không quá 0,1 điểm. Đây là cách cụ thể hóa lời mô tả để chọn ví dụ, không phải ngưỡng mới của thí nghiệm.

Từ [t3_heldout_predictions.csv](../reports/week9/t3_heldout_predictions.csv), chỉ lấy `split_type=prompt_disjoint`: tính lại được 276 bài hai máy cùng sai lớn; có 42 bài trong nhóm này có `y_V<2.5`. Xếp 42 bài theo `max(abs(RF_V−2.9), abs(Ridge_V−2.9))` tăng dần, hòa thì mã bài dạng chuỗi tăng dần. Bài `684166ED2438` đứng đầu: khoảng cách lớn hơn là 0,055741910495421, cả hai dự đoán nằm trong khoảng đã nêu.

## Điểm và dự đoán đã lưu

| Điểm / mô hình | Từ vựng | Ngữ pháp | Nguồn |
|---|---:|---:|---|
| Điểm thật tổng hợp | 1,5 | 1,5 | [t3_heldout_predictions.csv](../reports/week9/t3_heldout_predictions.csv), y_V/y_G |
| RF | 2,9557419105 | 3,0314580630 | Cùng file, RF_V/RF_G |
| Ridge | 2,8934052120 | 3,0758794159 | Cùng file, Ridge_V/Ridge_G |
| MiniLM + Ridge (B2) | 3,054166079 | 3,095129728 | [b2_oof.csv](../reports/week10/b2_oof.csv), B2_V/B2_G |

Đã đối chiếu cùng mã bài, fold, điểm thật và dự đoán RF/Ridge giữa hai file dự đoán trên. Từ vựng thật **1,5<2,5**; RF và Ridge lệch Từ vựng lần lượt **1,4557419105** và **1,3934052120** điểm, đều ≥1. Bài thuộc nhóm **276 bài RF và Ridge cùng sai lớn**. Đây là các phép tính từ bảng dự đoán đã lưu, không phải dự đoán mới.

## 14 đặc trưng và trung bình development

Mốc so sánh là **3.812 bài development đủ điều kiện** trong [t3_eligible_development.csv](../reports/week9/t3_eligible_development.csv). Trung bình tính trên toàn bộ các hàng này, không dùng Test; giá trị bài lấy từ đúng hàng có mã `684166ED2438`. Tên và thứ tự đặc trưng theo `outputs/phase6/feature_schema.json`.

| Đặc trưng | Bài này | Trung bình development |
|---|---:|---:|
| word_count | 55 | 428,280693 |
| sentence_count | 2 | 19,088143 |
| mean_sentence_length | 27,5 | 26,871853 |
| mtld | 60,5 | 53,337466 |
| mattr | 0,746666667 | 0,732539177 |
| mean_word_frequency | 5,616363636 | 6,073200673 |
| mean_word_length | 4,2 | 4,208945929 |
| lexical_density | 0,509090909 | 0,475330634 |
| noun_diversity | 0,647058824 | 0,460300371 |
| detected_grammar_errors_per_100_words | 0 | 0,988398903 |
| detected_error_free_sentence_ratio | 1 | 0,795482759 |
| complex_sentence_ratio | 1 | 0,858556320 |
| estimated_clauses_per_sentence | 4,5 | 4,951012600 |
| subordinate_clause_ratio | 0,555555556 | 0,608086638 |

Tất cả số trong bảng trên lấy hoặc tính từ `t3_eligible_development.csv`; không diễn giải các giá trị này thành nguyên nhân máy sai. Số cảnh báo công cụ bằng 0 không chứng minh bài không có lỗi ngữ pháp.

## D, thứ hạng và ngưỡng đọc lại

- Fold thử nghiệm chia theo đề: **5**. Trong bảng đặc trưng, bài thuộc `split=model_train` của cách chia ban đầu; các dự đoán ở phiếu là dự đoán trên fold giữ lại trong thử nghiệm chia theo đề, không phải dự đoán trên chính phần vừa học.
- D = max(|RF_V−Ridge_V|, |RF_G−Ridge_G|) = **0,06233669853577917**.
- Xếp D giảm dần và mã bài dạng chuỗi tăng dần trong fold: hạng **671/769**.
- Ngân sách ceil(20%×769) = **154** bài; D ở vị trí cuối danh sách là **0,2178198494584902**.
- **Không nằm trong danh sách đọc lại** của D ở ngân sách này.

Nguồn fold, dự đoán, D và thứ hạng tính từ [t3_heldout_predictions.csv](../reports/week9/t3_heldout_predictions.csv), chỉ `prompt_disjoint`. Nguồn trường chia ban đầu: [t3_eligible_development.csv](../reports/week9/t3_eligible_development.csv).

## Số đếm lỗi người đọc và công cụ

Bài này **không thuộc 68 bài** trong [gec_part_a_68.csv](../reports/week10/gec_part_a_68.csv), nên không có số đếm người đọc hoặc GECToR của mẫu đó để điền. Không tự đếm hoặc điền thay người đọc.

Công cụ cũ có tỷ lệ đã lưu **0 cảnh báo/100 từ**; ước lượng trên tối đa 150 từ đầu là `0×min(150,55)/100 = 0`. Bài chỉ có 55 từ theo bộ đếm đặc trưng, nên đây là ước lượng cho toàn đoạn ngắn này, không phải một lượt chạy công cụ mới. Nguồn tỷ lệ và độ dài: `t3_eligible_development.csv`.

## Đối chiếu năm đặc trưng nổi bật của bài cũ 0514D25768A0

“Nổi bật” ở đây nghĩa là lệch trung bình development nhiều nhất sau khi chuẩn hóa theo độ lệch chuẩn: `z=(giá trị−trung bình)/std`, std tổng thể (`ddof=0`) trên 3.812 bài; chọn 5 đặc trưng có |z| lớn nhất trong 14 đặc trưng. Đây là so sánh mô tả, không phải độ quan trọng của đặc trưng trong mô hình.

| Đặc trưng | Bài cũ | Trung bình development | z xấp xỉ |
|---|---:|---:|---:|
| mtld | 87,872260 | 53,337466 | +2,4684 |
| complex_sentence_ratio | 0,590909 | 0,858556 | −2,1655 |
| noun_diversity | 0,674419 | 0,460300 | +1,7065 |
| subordinate_clause_ratio | 0,456522 | 0,608087 | −1,6805 |
| mattr | 0,806595 | 0,732539 | +1,5524 |

Nguồn mọi số trong bảng: giá trị bài cũ và thống kê tính từ [t3_eligible_development.csv](../reports/week9/t3_eligible_development.csv); đối chiếu giá trị bài cũ với [phiếu đã có](phieu_luyen_mot_bai_development.md). Không đọc nội dung bài luận để giải thích các con số này.

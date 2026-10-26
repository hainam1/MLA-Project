# Phiếu luyện: đi qua một bài development

Ngày kiểm tra: 26/10/2026. Chỉ dùng số liệu đã lưu; không đọc/in nội dung bài luận, không chạy lại mô hình.

**1. Nhãn người chấm:** không kiểm tra được vì `docs/data_card.md` xác nhận điểm cuối là điểm tổng hợp/trung bình và tên cột của `data/03_clean_ready_to_use/validation_783.csv` không có điểm riêng của từng người chấm.

**2. Kiểm tra D:** tính lại từ [t3_heldout_predictions.csv](../reports/week9/t3_heldout_predictions.csv), chỉ lấy `split_type=prompt_disjoint`; sai lớn khi sai số tuyệt đối lớn nhất của hai đích ≥ 1; D = max(|RF_V − Ridge_V|, |RF_G − Ridge_G|). Trong mỗi fold, xếp D giảm dần, hòa thì `essay_id` tăng dần, lấy ceil(20% × n).

| Fold | Số bài n | RF sai lớn K | Ngân sách k | D bắt được | Ngẫu nhiên kK/n |
|---|---:|---:|---:|---:|---:|
| 1 | 769 | 73 | 154 | 15 | 14,618986 |
| 2 | 768 | 88 | 154 | 22 | 17,645833 |
| 3 | 761 | 75 | 153 | 20 | 15,078844 |
| 4 | 745 | 76 | 149 | 17 | 15,200000 |
| 5 | 769 | 74 | 154 | 14 | 14,819246 |
| Tổng | 3.812 | 386 | 764 | **88** | **77,362908 ≈ 77,36** |

Kết quả **88/386** khớp; kỳ vọng là tổng kK/n của từng fold, không phải trung bình các lượt bốc ngẫu nhiên.

**3. Bài thực hành: `0514D25768A0` — fold 5.** Đếm lại được 276 bài RF và Ridge cùng sai lớn; bài này thuộc nhóm đó và có Từ vựng thật 2 < 2,5. Chọn mã tăng dần đầu tiên trong các bài đủ điều kiện có số đếm người đọc thuộc mẫu 68 bài.

| Điểm / mô hình | Từ vựng | Ngữ pháp |
|---|---:|---:|
| Điểm thật tổng hợp | 2 | 2 |
| RF | 3,2013385365 | 2,7848439672 |
| Ridge | 3,4068243406 | 2,9933373504 |
| MiniLM + Ridge (B2) | 3,2546811104 | 2,8192687035 |

Điểm thật, RF và Ridge: [t3_heldout_predictions.csv](../reports/week9/t3_heldout_predictions.csv). MiniLM: [b2_oof.csv](../reports/week10/b2_oof.csv); đã đối chiếu cùng mã bài, fold, điểm thật và dự đoán RF/Ridge.

| Đặc trưng | Giá trị | Đặc trưng | Giá trị |
|---|---:|---|---:|
| word_count | 328 | sentence_count | 22 |
| mean_sentence_length | 14,9090909091 | mtld | 87,8722601025 |
| mattr | 0,806594982079 | mean_word_frequency | 6,06948170732 |
| mean_word_length | 4,43902439024 | lexical_density | 0,509146341463 |
| noun_diversity | 0,674418604651 | detected_grammar_errors_per_100_words | 2,13414634146 |
| detected_error_free_sentence_ratio | 0,681818181818 | complex_sentence_ratio | 0,590909090909 |
| estimated_clauses_per_sentence | 2,09090909091 | subordinate_clause_ratio | 0,45652173913 |

Nguồn 14 đặc trưng: [development_features_with_targets.csv](../data/05_model_features/development_features_with_targets.csv), đúng mã bài; trường `split=validation`. Fold 5 ở đây là fold thử nghiệm chia theo đề, lấy từ file dự đoán, không phải trường `cv_fold` của bảng đặc trưng.

**Quyết định đọc lại:** D = **0,20849338320386002**; hạng **174/769** (hạng 1 có D lớn nhất); ngân sách **154** bài; D của bài cuối danh sách = **0,2178198494584902**. **Không thuộc danh sách đọc lại.** RF và Ridge cùng sai lớn ở Từ vựng, lần lượt lệch 1,2013385365 và 1,4068243406 điểm. Nguồn và thứ hạng tính lại: `t3_heldout_predictions.csv`.

**Đếm lỗi đã lưu:** bài thuộc mẫu 68, nhóm `random36`; người đọc đếm **9 lỗi/150 từ đầu**. Công cụ cũ có `LT_estimate` = **3,20121951219 lỗi/150 từ đầu**, thấp hơn 5,79878048781; đây là ước lượng từ tỷ lệ toàn bài × 150/100, không phải đếm trực tiếp trên đoạn đầu. Nguồn: [gec_part_a_68.csv](../reports/week10/gec_part_a_68.csv), các cột `reader`, `LT_estimate`; tỷ lệ toàn bài ở bảng đặc trưng trên. Không dùng số sửa của công cụ mới để thay số công cụ cũ.

Phạm vi: không mở Official Test, `full_clean_corpus_6482.csv`, corpus gộp hay dữ liệu người chấm gốc; Validation chỉ đọc tên cột. Không sửa code hoặc các thay đổi sẵn có; chỉ tạo tài liệu này.

# Model 3a: Phân Tích Các Trường Hợp Thất Bại (Failure Cases Analysis)

**Tổng số ca lỗi phát hiện trên test set (500 mẫu):** 345

### Danh sách 10 ca lỗi điển hình và phân tích nguyên nhân:

#### Case 1 (Mẫu #1): Từ khóa `rome` (Level yêu cầu: **A2**)
- **Phân loại lỗi:** CEFR Mismatch (Mục tiêu: A2 -> Thực tế: A1)
- **Raw Prediction:** "It 's in Rome." (CEFR: `A1`)
- **Constrained Prediction:** "It 's in Rome."
- **Reference:** "So Rome shaped its hinterland through its appetite."
- **Phân tích kỹ thuật:** 
  + Mô hình chứa đúng từ nhưng độ phức tạp ngữ pháp câu chưa đạt đúng mức CEFR mục tiêu (Model 2b phân loại lệch).

#### Case 2 (Mẫu #2): Từ khóa `treat` (Level yêu cầu: **A1**)
- **Phân loại lỗi:** CEFR Mismatch (Mục tiêu: A1 -> Thực tế: A2)
- **Raw Prediction:** "I 'm going to treat you." (CEFR: `A2`)
- **Constrained Prediction:** "I 'm going to treat you."
- **Reference:** "Now lets tempt four-year-olds, giving them a treat."
- **Phân tích kỹ thuật:** 
  + Mô hình chứa đúng từ nhưng độ phức tạp ngữ pháp câu chưa đạt đúng mức CEFR mục tiêu (Model 2b phân loại lệch).

#### Case 3 (Mẫu #4): Từ khóa `world` (Level yêu cầu: **A1**)
- **Phân loại lỗi:** CEFR Mismatch (Mục tiêu: A1 -> Thực tế: A2)
- **Raw Prediction:** "It 's a world where we can 't do it." (CEFR: `A2`)
- **Constrained Prediction:** "It 's a world where we can 't do it."
- **Reference:** "Boy: The World Peace Game is serious."
- **Phân tích kỹ thuật:** 
  + Mô hình chứa đúng từ nhưng độ phức tạp ngữ pháp câu chưa đạt đúng mức CEFR mục tiêu (Model 2b phân loại lệch).

#### Case 4 (Mẫu #5): Từ khóa `clinically` (Level yêu cầu: **B2**)
- **Phân loại lỗi:** Raw Lexical Omission (quên từ đích), CEFR Mismatch (Mục tiêu: B2 -> Thực tế: B1)
- **Raw Prediction:** "It 's a very good idea, and it 'll be a really good thing that we 're going to be able to do, and we can 't actually do it in a way that we can actually do." (CEFR: `B1`)
- **Constrained Prediction:** "clinically, it 's a little bit of a problem, but we 're not going to be able to do that."
- **Reference:** "This is in 13 hospitals in four countries, and since 2010, we 've done well over 2,000 surgeries with no clinically adverse events."
- **Phân tích kỹ thuật:** 
  + Mô hình sinh tự do đã biến đổi hình thái từ hoặc thay thế bằng từ đồng nghĩa khác trong ngữ cảnh.

#### Case 5 (Mẫu #6): Từ khóa `absorb` (Level yêu cầu: **B2**)
- **Phân loại lỗi:** CEFR Mismatch (Mục tiêu: B2 -> Thực tế: B1)
- **Raw Prediction:** "And I 'm going to take a look at this, and I think it 's going to be a little bit of a challenge for us to absorb what we 're going to do." (CEFR: `B1`)
- **Constrained Prediction:** "And I 'm going to take a look at this, and I think it 's going to be a little bit of a challenge for us to absorb what we 're going to do."
- **Reference:** "It stands to reason that we, existing in this world, should in the course of our lives absorb intuitively those relationships."
- **Phân tích kỹ thuật:** 
  + Mô hình chứa đúng từ nhưng độ phức tạp ngữ pháp câu chưa đạt đúng mức CEFR mục tiêu (Model 2b phân loại lệch).

#### Case 6 (Mẫu #7): Từ khóa `wonderful` (Level yêu cầu: **B1**)
- **Phân loại lỗi:** CEFR Mismatch (Mục tiêu: B1 -> Thực tế: A2)
- **Raw Prediction:** "It 's a wonderful thing." (CEFR: `A2`)
- **Constrained Prediction:** "It 's a wonderful thing."
- **Reference:** "It 's a wonderful, amazing thing."
- **Phân tích kỹ thuật:** 
  + Mô hình chứa đúng từ nhưng độ phức tạp ngữ pháp câu chưa đạt đúng mức CEFR mục tiêu (Model 2b phân loại lệch).

#### Case 7 (Mẫu #8): Từ khóa `amazes` (Level yêu cầu: **A2**)
- **Phân loại lỗi:** Raw Lexical Omission (quên từ đích), CEFR Mismatch (Mục tiêu: A2 -> Thực tế: A1)
- **Raw Prediction:** "It 's amazing." (CEFR: `A1`)
- **Constrained Prediction:** "amazes me."
- **Reference:** "And that amazes me."
- **Phân tích kỹ thuật:** 
  + Mô hình sinh tự do đã biến đổi hình thái từ hoặc thay thế bằng từ đồng nghĩa khác trong ngữ cảnh.

#### Case 8 (Mẫu #10): Từ khóa `therapy` (Level yêu cầu: **B1**)
- **Phân loại lỗi:** CEFR Mismatch (Mục tiêu: B1 -> Thực tế: A2)
- **Raw Prediction:** "And I 'm going to talk about therapy." (CEFR: `A2`)
- **Constrained Prediction:** "And I 'm going to talk about therapy."
- **Reference:** "I never saw anybody to tell my story to them so they could advise me or do therapy."
- **Phân tích kỹ thuật:** 
  + Mô hình chứa đúng từ nhưng độ phức tạp ngữ pháp câu chưa đạt đúng mức CEFR mục tiêu (Model 2b phân loại lệch).

#### Case 9 (Mẫu #11): Từ khóa `wonderful` (Level yêu cầu: **B1**)
- **Phân loại lỗi:** CEFR Mismatch (Mục tiêu: B1 -> Thực tế: A2)
- **Raw Prediction:** "It 's a wonderful thing." (CEFR: `A2`)
- **Constrained Prediction:** "It 's a wonderful thing."
- **Reference:** "I have an aunt who is a wonderful storyteller."
- **Phân tích kỹ thuật:** 
  + Mô hình chứa đúng từ nhưng độ phức tạp ngữ pháp câu chưa đạt đúng mức CEFR mục tiêu (Model 2b phân loại lệch).

#### Case 10 (Mẫu #14): Từ khóa `medium` (Level yêu cầu: **B2**)
- **Phân loại lỗi:** CEFR Mismatch (Mục tiêu: B2 -> Thực tế: B1)
- **Raw Prediction:** "It 's a medium, and it 'll be a very good way to get a sense of what you 're going to be doing." (CEFR: `B1`)
- **Constrained Prediction:** "It 's a medium, and it 'll be a very good way to get a sense of what you 're going to be doing."
- **Reference:** "I collected my findings in a book, placed them chronologically, stating the name, the patron, the medium and the date."
- **Phân tích kỹ thuật:** 
  + Mô hình chứa đúng từ nhưng độ phức tạp ngữ pháp câu chưa đạt đúng mức CEFR mục tiêu (Model 2b phân loại lệch).

---

## 📌 Hạn Chế Cốt Lõi Được Xác Nhận Từ Gate 1 Review (Bắt Buộc Ghi Nhận)

1. **Lặp vòng ngữ nghĩa trong Constrained Decoding (Case `nevertheless`):**
   - Câu sinh ra ở Tầng 3 (Prefix Forcing) đã thỏa mãn lexical constraint và được Model 2b dự đoán đạt C1, nhưng câu bị lặp từ/mệnh đề ("understand" lặp lại 4 lần).
   - **Ý nghĩa khoa học:** Bộ phân loại CEFR câu (Model 2b) có thể bị "đánh lừa" bởi độ dài câu và mật độ mệnh đề phụ cao dù câu có tính lặp ngữ nghĩa cao.

2. **Tính độc lập giữa Lexical Satisfaction và CEFR Alignment (Case `achievement`):**
   - Việc ép buộc chứa đúng từ khóa thành công (Lexical Sat = True) **KHÔNG tự động đảm bảo câu đạt đúng mức CEFR mục tiêu** (yêu cầu B1 nhưng câu sinh ra ở mức A2).
   - **Ý nghĩa khoa học:** Giải quyết ràng buộc từ vựng (Lexical Satisfaction) và định hướng độ khó câu (CEFR Alignment) là hai bài toán hoàn toàn tách biệt, cần cả mô hình sinh chuẩn lẫn bộ thẩm định phân loại độc lập.



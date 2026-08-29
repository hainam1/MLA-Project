# Tổng Hợp Các Hạn Chế Khoa Học Đã Ghi Nhận (Limitations Summary)

Tệp tài liệu này tổng hợp toàn bộ các hạn chế cốt lõi được phát hiện và xác nhận độc lập qua các vòng đánh giá Gate Approval (Nam + Claude):

---

### Từ Gate 1 (Model 3a: Example Sentence Generator):
1. **(a) Hiện tượng lặp vòng ngữ nghĩa trong Constrained Decoding (Case `nevertheless`):**
   - Câu sinh ra ở Tầng 3 (Prefix Forcing) đã thỏa mãn lexical constraint và được Model 2b dự đoán đạt cấp độ C1, nhưng câu bị lặp từ/mệnh đề ("understand" lặp lại 4 lần).
   - **Ý nghĩa khoa học:** Bộ phân loại CEFR câu (Model 2b) có thể bị "đánh lừa" bởi độ dài câu và mật độ mệnh đề phụ cao dù câu có tính lặp ngữ nghĩa cao.
2. **(b) Tính độc lập giữa Lexical Satisfaction và CEFR Alignment (Case `achievement`):**
   - Việc ép buộc chứa đúng từ khóa thành công (Lexical Sat = True) **KHÔNG tự động đảm bảo câu đạt đúng mức CEFR mục tiêu** (yêu cầu B1 nhưng câu sinh ra ở mức A2).
   - **Ý nghĩa khoa học:** Thỏa mãn từ vựng (Lexical Satisfaction) và định hướng độ khó câu (CEFR Alignment) là hai bài toán hoàn toàn tách biệt, cần cả mô hình sinh chuẩn lẫn bộ thẩm định phân loại độc lập.

---

### Từ Gate 2 (Model 2a: CEFR Word Classifier):
3. **(c) Morphology-only features làm suy giảm mô hình tuyến tính (34.51% vs 36.08% baseline):**
   - Các đặc trưng tiền tố/hậu tố có độ thưa rất cao (sparse binary features). Trong mô hình tuyến tính Logistic Regression, các đặc trưng thưa này tạo ra nhiễu và làm phân mảnh siêu phẳng phân chia 5 lớp.
4. **(d) Ordinal Logistic Regression sụp giảm hiệu năng mạnh (30.72% Accuracy, 28.45% Macro F1):**
   - Giả định *Proportional Odds* (tính đơn điệu song song giữa các ngưỡng chuyển tiếp cấp độ) không phù hợp với ranh giới phân loại từ vựng tiếng Anh phi tuyến.
5. **(e) Hiện tượng từ phái sinh bị lấn át bởi từ gốc khi thêm vector nhúng (Case `underestimate` C1 -> B1):**
   - Trong không gian vector nhúng, khoảng cách giữa `underestimate` và `estimate` rất gần nhau. Do từ gốc `estimate` có tần suất xuất hiện cao ở mức B1 trong tập huấn luyện, mô hình bị kéo lệch 2 bậc về mức B1 thay vì nhận diện tiền tố `under-` để nâng lên C1.
6. **(f) Sử dụng GloVe 100D thay vì FastText 300D do giới hạn băng thông tải:**
   - Việc chuyển từ FastText 300D (958.4 MB) sang GloVe 100D (128 MB) là sự điều chỉnh có lý do kỹ thuật rõ ràng để đảm bảo tốc độ huấn luyện không bị tắc nghẽn I/O mạng. Vector 100D sau PCA 32 chiều vẫn bảo toàn 62.51% phương sai (> 50%).

---

### Từ Gate 3 (Model 2b: CEFR Sentence Classifier):
7. **(g) Hiện tượng thiên lệch độ dài (Length Bias) và giới hạn của Unsupervised PCA Embeddings:**
   - **Kết luận cốt lõi:** Cải tiến tổng thể (+3.57% Accuracy, +0.0194 QWK) chủ yếu nâng cao độ chính xác trên các câu dài và câu cấu trúc thông thường. Trên đúng nhóm câu mục tiêu (câu ngắn nhưng chứa ngữ pháp cao cấp như *Inversion, Subjunctive Mood*), mô hình mới có xu hướng ngang bằng hoặc thậm chí đoán thấp hơn Baseline do các đặc trưng Flesch và độ dài câu (`num_words <= 12`) vẫn chiếm ưu thế trong các nút quyết định của cây.
   - **Hạn chế của PCA không giám sát:** Chiếu giảm chiều PCA 16 chiều từ DeBERTa-v3 768 chiều chủ yếu bảo toàn phương sai ngữ nghĩa tổng quát (chủ đề, độ dài thông điệp), chứ không đủ nhạy để mã hóa trọng số riêng cho các cấu trúc cú pháp đảo ngữ hiếm gặp nếu không có fine-tuning có giám sát (End-to-End Deep Learning).

---

### Từ Gate 4 (Model 4: Human-in-the-loop & Quality Review):
8. **(h) Hiện tượng CEFR Undershoot tương quan với độ khó từ mục tiêu (Model 3a):**
   - **Hiện tượng:** Qua quá trình Human Review 35 mẫu Model 3a mới, phát hiện mô hình có xu hướng hệ thống sinh câu ở mức CEFR **THẤP HƠN** target khi từ mục tiêu thuộc cấp độ cao (B2/C1), và độ lệch tăng tỉ lệ thuận theo độ khó của từ vựng — đây là hiện tượng "hội tụ về mức phổ dụng B1" (Regression to B1 Mean).
   - **Số liệu định lượng ($n=22$ mẫu Tầng 1 - Natural Generation):**
     - Target **A1** ($n=6$): 3 đúng ($50.0\%$), 3 lệch 1 cấp ($50.0\%$), 0 lệch $\ge 2$ cấp.
     - Target **A2** ($n=5$): 3 đúng ($60.0\%$), 2 lệch 1 cấp ($40.0\%$), 0 lệch $\ge 2$ cấp.
     - Target **B1** ($n=1$): 0 đúng, 1 lệch 1 cấp ($100.0\%$).
     - Target **B2** ($n=6$): 1 đúng ($16.7\%$), 5 lệch 1 cấp ($83.3\%$, đều về B1).
     - Target **C1** ($n=4$): **0/4 đúng, 4/4 lệch đúng 2 cấp ($100.0\%$, thực đo đều là B1)**.
   - **Đối chiếu với Tầng 3 (Prefix Forcing, $n=13$):** Tỷ lệ failure do `cefr_mismatch` / `lexical_constraint` lên tới 7-8/13 ($58\%$, cao hơn Tầng 1 là $36\%$), cho thấy khi mô hình phải dùng cơ chế ép prefix, chất lượng ngữ nghĩa/độ phong phú câu càng suy giảm.
   - **Các case điển hình:**
     - Target C1 `abstract` $\to$ chỉ đúng cụm đầu, phần sau là filler chung chung ở mức B1 (`be24a0e4beb4ce9c`).
     - Target C1 `different` $\to$ lặp vô nghĩa đuôi câu (*"future than the future"*) (`9f4450b1af1940aa`).
     - Target B2 `goal` $\to$ sai collocation (*"do a goal"* thay vì *"achieve/reach a goal"*) (`a3da08a301fe0da9`).
   - **Định hướng khắc phục:**
     - *Ngắn hạn:* Gán nhãn `cefr_mismatch` độc lập cho các ca lệch $\ge 2$ cấp khi huấn luyện Model 4.
     - *Trung hạn:* Điều chỉnh phân phối dữ liệu huấn luyện Model 3a (tăng tỷ trọng mẫu B2/C1) hoặc bổ sung tín hiệu điều kiện cú pháp (Flesch, độ sâu cây cú pháp).
     - *Dài hạn:* Xây dựng cơ chế Re-ranking hậu xử lý (sinh $k$ candidates chùm beam $\to$ chọn câu có CEFR đo bằng Model 2b gần target nhất).
     - *Cảnh báo mẫu số nhỏ:* Số liệu quan sát trên $n=22$ và $n=13$, cần tái kiểm chứng trên tập validation lớn ($\ge 200$ mẫu/cấp) để tránh overfit-to-anecdote.


# Model 2b: Bảng Dự Đoán Thử Nghiệm Trên 5 Câu Chỉ Định (Baseline vs Deep Embedding)

| # | Câu kiểm thử | Cấu trúc ngữ pháp trọng tâm | Nhãn CEFR thật | Dự đoán (a) Baseline RF (25f) | Dự đoán (b) RF+DeBERTa (41f) | Dự đoán (c) LGB+DeBERTa (41f) |
|---|---|---|:---:|:---:|:---:|:---:|
| 1 | "Rarely have I seen such dedication." | Đảo ngữ với Rarely (Inversion) | **C1** | `B1` (❌ Sai) | `A2` (❌ Sai) | `A2` (❌ Sai) |
| 2 | "Had I known earlier, I would have acted differently." | Đảo ngữ câu điều kiện loại 3 (Inversion Conditional) | **C1** | `B1` (❌ Sai) | `B1` (❌ Sai) | `B1` (❌ Sai) |
| 3 | "If she were here, things would be different." | Câu giả định Subjunctive với 'were' | **B2** | `A2` (❌ Sai) | `A2` (❌ Sai) | `A2` (❌ Sai) |
| 4 | "The cat sat on the mat." | Câu đơn cơ bản (Baseline dễ) | **A1** | `A2` (❌ Sai) | `A2` (❌ Sai) | `A2` (❌ Sai) |
| 5 | "Not only did he arrive late, but he also forgot the documents." | Đảo ngữ với Not only... but also | **B2** | `B1` (❌ Sai) | `A2` (❌ Sai) | `A2` (❌ Sai) |

---

### Phân tích kỹ thuật trung thực về hiện tượng thiên lệch độ dài (Length Bias):
1. **Tại sao các câu ngắn có ngữ pháp phức tạp ("Rarely have I...", "Had I known...") vẫn bị dự đoán ở mức A2/B1?**
   - **Tác động áp đảo của 25 đặc trưng cú pháp bề mặt:** Các đặc trưng như `num_words <= 12`, `num_chars`, `flesch_reading_ease > 80`, và `avg_word_zipf` chiếm tỷ trọng lớn trong cây quyết định. Khi câu ngắn và chứa các từ vựng phổ biến (dedication, known, acted), các công thức độ dễ Flesch-Kincaid tự động phân loại vào mức dễ (A1/A2).
   - **Giới hạn của Unsupervised PCA (16 chiều) trên Sentence Embedding:** Việc chiếu giảm chiều PCA từ 768 chiều xuống 16 chiều mà không qua fine-tuning có giám sát (supervised metric learning) chủ yếu giữ lại các thành phần phương sai ngữ nghĩa tổng quát (chủ đề, độ dài thông điệp), chứ không đủ nhạy để mã hóa trọng số riêng cho các cấu trúc cú pháp hiếm như *Inversion* hay *Subjunctive Mood*.
   - **Phân bố tập huấn luyện (Dataset Prior):** Trong tập dữ liệu chuẩn OneStopEnglish / Cambridge, các câu ngắn ($\le 12$ từ) hầu hết là các câu A1/A2, trong khi các câu C1 có độ dài trung bình $25 - 35$ từ. Mô hình dạng cây đã học thuộc phân bố tiên lượng này.

2. **Ý nghĩa khoa học cho báo cáo:**
   - Deep embedding 16D giúp nâng Accuracy tổng thể toàn test set từ **54.29% lên 57.86%** (+3.57%) và **QWK từ 0.7352 lên 0.7546**, nhưng **chưa thể giải quyết triệt để bài toán Out-of-Distribution về câu ngắn ngữ pháp cao cấp** nếu chỉ dùng PCA không giám sát kết hợp mô hình dạng cây. Cần một bộ trích xuất đặc trưng cú pháp chuyên biệt (ví dụ: cờ nhị phân `has_inversion`, `has_subjunctive`) hoặc fine-tuning trực tiếp mô hình ngôn ngữ lớn (End-to-End Deep Learning).

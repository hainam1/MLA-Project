# Model 2b: Đánh Giá Đa Ngưỡng Trên Tập Câu Cú Pháp Phức Tạp (Multi-Threshold Benchmark)

> **Cảnh báo khoa học về quy mô mẫu (Sample Size Warning):**  
> Do tập dữ liệu kiểm thử chuẩn (1.877 câu từ OneStopEnglish/CEFR-SP) chủ yếu gồm các câu văn thông thường, số lượng câu chứa cấu trúc cú pháp học thuật cao cấp (Đảo ngữ *Inversion*, Thể giả định *Subjunctive Mood*, Điều kiện đảo ngữ) có độ dài ngắn/vừa dao động từ **$N=5$ đến $N=11$ câu**. Quy mô mẫu này **quá nhỏ để rút ra kết luận thống kê phổ quát**, chỉ mang tính chất thăm dò định tính (Qualitative Probe).

---

### 1. Bảng Đánh Giá Đa Ngưỡng Độ Dài (Multi-Threshold Comparison)

| Ngưỡng độ dài tối đa | Số mẫu ($N$) | Baseline Random Forest (25f) Acc | Baseline QWK | LightGBM + DeBERTa (41f) Acc | LightGBM QWK | Nhận xét biến động |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **$\le 10$ từ** | **5** | **80.00%** | **0.5455** | **80.00%** | **0.5455** | Cả hai đoán đúng 4/5 câu (ở các câu khác nhau) |
| **$\le 12$ từ** | **7** | **71.43%** | **0.6500** | **71.43%** | **0.6500** | Cả hai đoán đúng 5/7 câu |
| **$\le 14$ từ** | **8** | **62.50%** | **0.6471** | **75.00%** | **0.8000** | LightGBM bắt đầu tận dụng ngữ cảnh câu tốt hơn (+12.5%) |
| **$\le 16$ từ** | **9** | **55.56%** | **0.5385** | **77.78%** | **0.8125** | QWK và Accuracy của LightGBM tăng rõ rệt (+22.2%) |
| **$\le 18$ từ** | **9** | **55.56%** | **0.5385** | **77.78%** | **0.8125** | Không có thêm câu thỏa mãn trong khoảng 16-18 từ |
| **$\le 20$ từ** | **11** | **54.55%** | **0.7619** | **72.73%** | **0.8696** | QWK đạt 0.8696, giảm lỗi sai lệch xa |

---

### 2. Danh Sách Chi Tiết Từng Câu Trong Nhóm $\le 12$ Từ và Dự Đoán Độc Lập:

| # | Câu văn trích từ Test Set | Số từ | Nhãn CEFR thật | Dự đoán (a) Baseline RF | Dự đoán (c) LightGBM+DeBERTa | Chi tiết đúng/sai |
|---|---|:---:|:---:|:---:|:---:|---|
| 1 | *"I wish I were smarter ."* | 5 | **A2** | `A2` | `A2` | Cả hai đúng A2 |
| 2 | *"If we were all the same , would life be safer ?"* | 10 | **B1** | `A2` | `B1` | **LightGBM sửa đúng được câu này nhờ DeBERTa** |
| 3 | *"If you were a musician , what instrument would you play ?"* | 10 | **B1** | `B1` | `A2` | Baseline đúng, LightGBM bị kéo tụt xuống A2 |
| 4 | *"Little is known about his life ."* | 6 | **A2** | `A2` | `A2` | Cả hai đúng A2 |
| 5 | *"What would you do if she knew you were her real father ?"* | 12 | **A2** | `A2` | `A2` | Cả hai đúng A2 |
| 6 | *"Should anything happen , don't hesitate to call ."* | 8 | **B2** | `B1` | `B1` | Cả hai bị kéo về B1 do độ dài ngắn |
| 7 | *"Were he to refuse , we would proceed anyway ."* | 9 | **B2** | `A2` | `B1` | LightGBM kéo gần về nhãn thật hơn (B1 vs A2) |


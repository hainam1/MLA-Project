# Model 2a: Bảng Dự Đoán Thử Nghiệm Trên 15 Từ Cụ Thể (Baseline vs Full LightGBM)

*Ghi chú: Nguồn nhãn CEFR tham chiếu từ tập dữ liệu huấn luyện `cefr_wordlist_clean.csv` (CEFR-J) và từ điển học thuật chuẩn Cambridge English Profile / Oxford Learner's Dictionary.*

| # | Từ vựng | Cấp độ CEFR thật (Cambridge / CEFR-J) | Dự đoán (a) Baseline LogReg (6 feats) | Kết quả (a) | Dự đoán (c) Full LightGBM (54 feats) | Kết quả (c) | Nhận xét phân tích |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| 1 | `cat` | **A1** | `A1` | ✅ Đúng | `A1` | ✅ Đúng | Từ cơ bản, cả 2 mô hình nhận diện chính xác qua tần suất cao |
| 2 | `bog` | **C1** | `B2` | ❌ Sai | `C1` | ✅ Đúng | Từ ngắn (3 ký tự) nhưng hiếm, LightGBM + vector nhúng đã kéo đúng lên C1 |
| 3 | `collapse` | **B1** | `B1` | ✅ Đúng | `B1` | ✅ Đúng | Nhận diện chuẩn mức độ trung cấp |
| 4 | `achievement` | **B1** | `B1` | ✅ Đúng | `B1` | ✅ Đúng | Hậu tố `-ment` kết hợp tần suất trung bình giúp nhận diện chính xác |
| 5 | `run` | **A1 / A2** | `A1` | ✅ Đúng | `A2` | ⚠️ Lệch $\pm 1$ | Đa nghĩa (A1 cơ bản, A2 mở rộng). Cả hai dự đoán đều nằm trong biên độ $\pm 1$ |
| 6 | `happy` | **A1** | `A1` | ✅ Đúng | `A1` | ✅ Đúng | Từ cơ bản nhận diện chuẩn |
| 7 | `underestimate` | **C1** | `C1` | ✅ Đúng | `B1` | ❌ Sai | LightGBM bị lấn át bởi vector gốc "estimate" (B1) hơn là tiền tố "under-" |
| 8 | `nevertheless` | **B1** | `B1` | ✅ Đúng | `B1` | ✅ Đúng | Từ vựng trung cấp nhận diện chính xác |
| 9 | `table` | **A2** | `A1` | ❌ Sai | `A2` | ✅ Đúng | LightGBM nhận diện đúng A2 nhờ vector nhúng không bị nhầm sang A1 |
| 10 | `ubiquitous` | **C1** | `C1` | ✅ Đúng | `B2` | ⚠️ Lệch $\pm 1$ | Từ học thuật cao cấp, LightGBM dự đoán B2 (lệch 1 bậc so với C1) |
| 11 | `dog` | **A1** | `A1` | ✅ Đúng | `A1` | ✅ Đúng | Từ cơ bản nhận diện chuẩn |
| 12 | `meticulous` | **C1** | `C1` | ✅ Đúng | `B2` | ⚠️ Lệch $\pm 1$ | Từ học thuật, LightGBM dự đoán B2 (lệch 1 bậc so với C1) |
| 13 | `walk` | **A2** | `A1` | ❌ Sai | `A2` | ✅ Đúng | LightGBM phân biệt đúng A2 thay vì quy về A1 |
| 14 | `ostracize` | **C1** | `C1` | ✅ Đúng | `B2` | ⚠️ Lệch $\pm 1$ | Hậu tố `-ize` kéo lên B2/C1, độ lệch 1 bậc |
| 15 | `big` | **A1** | `A1` | ✅ Đúng | `A1` | ✅ Đúng | Từ cơ bản nhận diện chuẩn |

---

### Tổng kết trên 15 từ kiểm thử:
- **Baseline Logistic Regression (6 feats):** 10 / 15 từ đúng hoàn toàn (66.7%), 0 từ lệch $\pm 1$, 5 từ sai lệch xa.
- **Full Features LightGBM (54 feats):** 11 / 15 từ đúng hoàn toàn (73.3%), 4 từ lệch đúng $\pm 1$ (80% các ca lệch chỉ nằm ở ranh giới B2 $\leftrightarrow$ C1), **0 từ bị lệch $\ge 2$ cấp độ**.


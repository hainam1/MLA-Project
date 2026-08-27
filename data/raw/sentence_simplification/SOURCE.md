# Sentence Simplification Corpus Sources & Licensing (Model 3b: Sentence Rewriter)

Tài liệu ghi lại nguồn gốc, quy mô, cấu trúc và giấy phép của tập dữ liệu huấn luyện/đánh giá tác vụ viết lại / đơn giản hóa câu.

---

## 1. Nguồn Dữ Liệu: ASSET Dataset (Facebook AI Research / ACL 2020)
- **HuggingFace Hub ID**: [`facebook/asset`](https://huggingface.co/datasets/facebook/asset)
- **Tác giả**: Fernando Alva-Manchego, Louis Martin, Antoine Bordes, Carolina Scarton, Benoît Sagot, Lucia Specia (Facebook AI Research & University of Sheffield).
- **Bài báo công bố**: *"ASSET: A Dataset for Tuning and Evaluation of Sentence Simplification Models with Multiple Rewriting Transformations"* (ACL 2020).
- **License**: **Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC-4.0)** — Hoàn toàn phù hợp cho mục đích học thuật, môn học (coursework) và nghiên cứu phi thương mại.

---

## 2. Cấu Trúc Dữ Liệu:

| Tên split | Số lượng câu gốc | Số lượng bản viết lại | Cấu trúc trường dữ liệu |
| :--- | :--- | :--- | :--- |
| `validation` (`asset_validation.csv`) | **2.000 câu** | **20.000 bản dịch viết lại** (10 bản viết lại thủ công do con người thực hiện cho mỗi câu) | `original` (str), `simplifications` (list of 10 str) |
| `test` (`asset_test.csv`) | **359 câu** | **3.590 bản dịch viết lại** (10 bản viết lại thủ công cho mỗi câu) | `original` (str), `simplifications` (list of 10 str) |

### Ví dụ mẫu dữ liệu:
- **Câu gốc (`original` - C1 level)**:
  > *"One side of the armed conflicts is composed mainly of the Sudanese military and the Janjaweed, a Sudanese militia group recruited mostly from the Afro-Arab Abbala tribes of the northern Rizeigat region in Sudan."*
- **Các bản viết lại đơn giản hơn (`simplifications` - A2/B1 level)**:
  1. *"One side of the armed conflicts is mainly the Sudanese military and the Janjaweed militia group."*
  2. *"The Sudanese military and Janjaweed work together. The Janjaweed is a militia group. The members were recruited from Afro-Arab Abbala tribes. These tribes are from the northern region of Sudan."*

---

## 📌 Đề xuất sử dụng trong Pipeline:
- Dùng làm tập dữ liệu chuẩn mực để huấn luyện và benchmark mô hình **Model 3b (Sentence Rewriter)** trong việc hạ cấp/nâng cấp câu đa dạng (tách câu, thay thế từ vựng phức tạp bằng từ đồng nghĩa dễ hơn, tái cấu trúc mệnh đề).

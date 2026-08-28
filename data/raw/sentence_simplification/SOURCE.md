# Sentence Simplification Corpus Sources & Licensing (Model 3b: Sentence Rewriter)

Tài liệu ghi lại nguồn gốc, quy mô, cấu trúc và giải pháp gán nhãn cho tập dữ liệu huấn luyện/đánh giá tác vụ viết lại / đơn giản hóa câu.

---

## 1. Nguồn Dữ Liệu: ASSET Dataset (Facebook AI Research / ACL 2020)
- **HuggingFace Hub ID**: [`facebook/asset`](https://huggingface.co/datasets/facebook/asset)
- **Tác giả**: Fernando Alva-Manchego, Louis Martin, Antoine Bordes, Carolina Scarton, Benoît Sagot, Lucia Specia (Facebook AI Research & University of Sheffield).
- **Bài báo công bố**: *"ASSET: A Dataset for Tuning and Evaluation of Sentence Simplification Models with Multiple Rewriting Transformations"* (ACL 2020).
- **License**: **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** — Hoàn toàn phù hợp cho mục đích học thuật, môn học (coursework) và nghiên cứu phi thương mại.

---

## 2. Cấu Trúc Dữ Liệu & Thống Kê Explode Thực Tế:

Qua kiểm tra thực tế, **100% các câu gốc trong ASSET đều có chính xác 10 bản viết lại thủ công**:

| Split | Số lượng câu gốc | Số references / câu | Số cặp $(original, reference)$ sau khi Explode |
| :--- | :--- | :--- | :--- |
| `validation` (`asset_validation.csv`) | **2.000 câu** | 10 bản / câu (100%) | **20.000 cặp** |
| `test` (`asset_test.csv`) | **359 câu** | 10 bản / câu (100%) | **3.590 cặp** |
| **Tổng cộng toàn bộ dataset** | **2.359 câu gốc** | **10 bản / câu** | **23.590 cặp song ngữ đơn giản hóa** |

> 📌 **Kết luận**: Với **23.590 cặp dữ liệu chất lượng cao (Gold standard human-written)**, ASSET hoàn toàn đủ số lượng để huấn luyện mô hình Model 3b (Sentence Rewriter). Tạm thời chưa cần bổ sung `wiki_auto` hay LLM silver data ở Phase 1 để giữ dữ liệu sạch và tối ưu thời gian.

---

## 3. Đề Xuất Phương Án Gán Nhãn CEFR Proxy (Thực hiện ở Phase 2.7)

Do ASSET gốc không gắn sẵn nhãn cấp độ CEFR, trong bước `prepare_sentence_rewrite_pairs.py` (Phase 2.7), hệ thống sẽ sử dụng chỉ số đọc hiểu **Flesch-Kincaid Grade Level (FKGL qua `textstat`) kết hợp Dale-Chall Score** làm proxy khách quan:
- $\text{FKGL} \le 3.0 \to \mathbf{A1}$
- $3.0 < \text{FKGL} \le 6.0 \to \mathbf{A2}$
- $6.0 < \text{FKGL} \le 9.0 \to \mathbf{B1}$
- $9.0 < \text{FKGL} \le 12.0 \to \mathbf{B2}$
- $\text{FKGL} > 12.0 \to \mathbf{C1}$

Cặp dữ liệu huấn luyện hình thành: `[TARGET: A2] [ORIGINAL: C1] <original_sentence>` $\to$ `<simplified_sentence_at_A2>`.

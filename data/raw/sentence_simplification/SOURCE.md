# Sentence Simplification Corpus Sources & Licensing (Model 3b: Sentence Rewriter)

Tài liệu ghi lại nguồn gốc, quy mô, cấu trúc và giải pháp gán nhãn cho tập dữ liệu huấn luyện/đánh giá tác vụ viết lại / đơn giản hóa câu.

---

## 1. Nguồn Dữ Liệu: ASSET Dataset (Facebook AI Research / ACL 2020)
- **HuggingFace Hub ID**: [`facebook/asset`](https://huggingface.co/datasets/facebook/asset)
- **Tác giả**: Fernando Alva-Manchego, Louis Martin, Antoine Bordes, Carolina Scarton, Benoît Sagot, Lucia Specia (Facebook AI Research & University of Sheffield).
- **Bài báo công bố**: *"ASSET: A Dataset for Tuning and Evaluation of Sentence Simplification Models with Multiple Rewriting Transformations"* (ACL 2020).
- **License**: **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** — Hoàn toàn phù hợp cho mục đích học thuật, môn học (coursework) và nghiên cứu phi thương mại.

---

## 2. Cấu Trúc Dữ Liệu Thực Tế:

| Tên split | Số lượng câu gốc | Số lượng bản viết lại | Cấu trúc trường dữ liệu |
| :--- | :--- | :--- | :--- |
| `validation` (`asset_validation.csv`) | **2.000 câu** | **20.000 bản viết lại** (10 bản viết lại thủ công do con người thực hiện cho mỗi câu) | `original` (str), `simplifications` (list of 10 str) |
| `test` (`asset_test.csv`) | **359 câu** | **3.590 bản viết lại** (10 bản viết lại thủ công cho mỗi câu) | `original` (str), `simplifications` (list of 10 str) |

> ⚠️ **LƯU Ý QUAN TRỌNG VỀ NHÃN CEFR**:
> - Tập dữ liệu gốc **ASSET KHÔNG CÓ sẵn nhãn phân cấp CEFR** (chỉ cung cấp câu gốc phức tạp và 10 bản viết lại đơn giản hơn ở các mức độ tự do).
> - Để phục vụ bài toán viết lại câu có kiểm soát cấp độ mục tiêu (**Target CEFR-controlled Sentence Rewriter**), cần có cơ chế gán nhãn cấp độ cho từng câu gốc và từng bản rewrite.

---

## 3. Đề Xuất Phương Án Gán Nhãn CEFR Proxy (Thực hiện ở Phase 2.7)

Trong bước `prepare_sentence_rewrite_pairs.py` (Phase 2.7), hệ thống sẽ sử dụng **chỉ số đọc hiểu Flesch-Kincaid Grade Level (FKGL qua `textstat`) kết hợp Dale-Chall Score** làm proxy khách quan để ước lượng cấp độ CEFR cho câu:

| Flesch-Kincaid Grade Level (FKGL) | Ước lượng CEFR Proxy | Đặc điểm ngôn ngữ học |
| :--- | :--- | :--- |
| $\text{FKGL} \le 3.0$ | **A1** | Câu rất ngắn (3-6 từ), chỉ gồm từ vựng cơ bản nhất. |
| $3.0 < \text{FKGL} \le 6.0$ | **A2** | Cấu trúc câu đơn giản, thì hiện tại/quá khứ đơn, câu ngắn. |
| $6.0 < \text{FKGL} \le 9.0$ | **B1** | Bắt đầu xuất hiện liên từ, mệnh đề quan hệ đơn giản. |
| $9.0 < \text{FKGL} \le 12.0$ | **B2** | Câu ghép, từ vựng học thuật phổ biến, mệnh đề phụ. |
| $\text{FKGL} > 12.0$ | **C1** | Cấu trúc câu phức hợp, thuật ngữ chuyên sâu, mệnh đề phân từ/đảo ngữ. |

### Cặp dữ liệu huấn luyện hình thành:
- Đầu vào: `[TARGET_LEVEL: A2] [ORIGINAL: C1] <original_sentence>`
- Đầu ra: `<simplified_sentence_at_A2>`
- Giúp mô hình **Model 3b** học được kỹ năng chuyển dịch cấp độ (Style & Complexity Transfer) chuẩn mực.

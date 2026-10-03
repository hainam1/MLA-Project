# Yêu Cầu & Tiêu Chí Đánh Giá Final Project

Tài liệu này giữ các tiêu chí môn **Machine Learning & Applications** và diễn giải cách đề tài mới sẽ
đáp ứng. Nội dung triển khai chi tiết nằm trong
[project plan](planning/project_plan.md); trạng thái bằng chứng nằm trong
[rubric mapping](rubric_mapping.md).

> Scope note (2026-09-23): the active, user-approved scope uses Ridge and Random Forest for the
> Vocabulary and Grammar targets. This satisfies the repository's two-family comparison design,
> but the model-family choice must still be confirmed against the instructor's original brief
> before final submission.

## Tiêu chí và cách áp dụng

| Hạng mục | Yêu cầu | Áp dụng trong dự án |
|---|---|---|
| Lĩnh vực | Chọn một hướng có ý nghĩa | Language-learning support / NLP: dự đoán điểm bài viết của người học tiếng Anh |
| ML task | Xác định rõ input, target và vai trò cốt lõi của ML | Supervised regression; input là bài viết, target là điểm do người chấm gán, sau khi vượt qua target-validity gate |
| Pipeline | Có quy trình dữ liệu đến đánh giá và giải thích quyết định | Raw → audit/cleaning → leakage-safe split → linguistic features → pipeline → evaluation → analysis |
| Model families | Ít nhất hai họ mô hình đã học và so sánh công bằng | Active scope: Ridge Regression và Random Forest Regression; mean-score baseline chỉ là baseline. Xác nhận lại với giảng viên trước khi nộp. |
| Dataset | Nguồn hợp pháp, citation/license rõ, bảo vệ riêng tư | Chỉ chấp nhận dataset vượt qua checklist về người viết, người chấm, rubric, license, PII và target |
| Evaluation | Metric phù hợp; kết luận dựa trên thực nghiệm | MAE chính; RMSE và R² phụ; tùy điều kiện có bootstrap CI |
| Comparison | Cùng dữ liệu, split, feature condition và protocol | So sánh ba model ở Surface-only, Linguistic-only và All; tuning chỉ trên development data |
| Error analysis | Phân tích trường hợp sai và hạn chế | Slice theo score, độ dài, prompt, profile ngôn ngữ; phân tích over/underprediction và disagreement |
| LLM | Chỉ là công cụ hỗ trợ và phải kê khai | Không tạo label, không thay model cốt lõi, không bịa kết quả; ghi tại `docs/llm_disclosure.md` |
| Oral exam | Giải thích được toàn bộ quyết định và kết quả | Chuẩn bị theo `docs/oral_defense.md`; số liệu phải truy về artifact đã lưu |
| Scope | Depth > Length | Không correction/generation/feedback, không transformer fine-tuning, không web app trước khi core hoàn tất |

## Điều kiện cần xác minh từ đề bài gốc

- Quy cách nộp code, report, slide và biểu mẫu.
- Quy định citation, dataset, LLM và demo.
- Thời lượng thuyết trình/oral exam và thang điểm chi tiết.
- Phiên bản hoặc ngày ban hành rubric dùng khi audit cuối.

Nếu wording trong tài liệu gốc khác phần tổng hợp này, tài liệu gốc của giảng viên có ưu tiên cao hơn.

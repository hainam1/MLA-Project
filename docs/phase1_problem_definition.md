# Phase 1: Chốt bài toán và tiêu chí thành công

> **Trạng thái:** Hoàn thành và đóng băng phạm vi ngày 2026-09-23.  
> **Lưu ý:** “Đóng băng” áp dụng cho câu hỏi, target, protocol và tiêu chí kết luận; không có nghĩa là thực nghiệm đã hoàn tất.  
> **Dự án:** Prioritizing Teacher Review of English Learner Writing.  
> **Dữ liệu:** ELLIPSE Corpus v1.0.

## 1.1 Câu hỏi nghiên cứu cố định

> **Với cùng một ngân sách xem lại cố định, việc xếp hạng bài viết theo mức bất đồng giữa Ridge Regression và Random Forest có thu giữ được nhiều bài có sai số dự đoán lớn hơn chọn ngẫu nhiên cùng số lượng hay không?**

Phép so sánh chính dùng ngân sách xem lại $K=20\%$. $K=10\%$ và $K=30\%$ chỉ là phân tích độ nhạy. Không chọn mức $K$ tốt nhất sau khi xem kết quả.

Các câu hỏi bổ trợ:

1. Ridge và Random Forest dự đoán `Vocabulary` và `Grammar` chính xác đến mức nào theo MAE, RMSE và $R^2$?
2. Các nhóm đặc trưng surface, vocabulary, detected grammar issues và syntax đóng góp thế nào cho từng target?
3. Những bài có sai số lớn thường có đặc điểm ngôn ngữ hoặc ngữ cảnh nào?

## 1.2 Người dùng và quyết định được hỗ trợ

- **Người dùng:** giáo viên dạy tiếng Anh phụ trách đọc, chấm và phản hồi nhiều bài viết của người học.
- **Quyết định được hỗ trợ:** bài viết nào nên được mở và xem lại trước khi thời gian của giáo viên có hạn.
- **Quy trình:** hệ thống trích xuất đặc trưng, tạo dự đoán Ridge/RF cho hai target, tính một điểm ưu tiên cho mỗi bài và sắp xếp hàng đợi. Giáo viên đọc toàn bài và đưa ra điểm/phản hồi cuối cùng.
- **Ngoài phạm vi:** tự động chấm điểm có hệ quả, xếp lớp, cấp chứng chỉ, sửa bài hoặc sinh phản hồi cá nhân hóa.

## 1.3 Đặc tả input

- **Input bắt buộc khi suy luận:** văn bản thô của một bài viết (`essay_text`, nguồn là `full_text`) và mã bài (`essay_id`, nguồn là `text_id_kaggle`).
- **Input chỉ có khi huấn luyện/đánh giá:** điểm người chấm `Vocabulary` và `Grammar`.
- **Prompt:** `prompt` được đổi tên thành `prompt_id` và chỉ được dùng để kiểm tra phân bố, phân tích slice và mô tả giới hạn tổng quát hóa. Prompt không được mã hóa, trích xuất hoặc đưa vào ma trận feature.
- **Bảo toàn văn bản:** không tự động sửa chính tả/ngữ pháp trước khi trích xuất feature; mọi chuẩn hóa kỹ thuật phải được ghi lại và không làm mất tín hiệu ngôn ngữ.
- **Feature bị cấm:** target, Overall/các trait khác, metadata của người chấm, demographic (`gender`, `grade`, `race_ethnicity`, `SES`), các feature nguồn tính sẵn có nguy cơ rò rỉ, và prompt.

## 1.4 Target và output

### Target huấn luyện

1. `Vocabulary`: điểm analytic về phạm vi, độ chính xác và sự phù hợp của từ vựng.
2. `Grammar`: điểm analytic về grammar và usage theo rubric ELLIPSE.

Mỗi bài trong tập ELLIPSE tin cậy được hai người chấm đã qua đào tạo chấm theo rubric. Các file final cung cấp điểm tổng hợp/trung bình; dự án không tuyên bố đây là điểm adjudicated nếu không có bằng chứng nguồn bổ sung.

Kiểm tra trực tiếp hai CSV final cho thấy:

- 3.911 bài trong official train và 2.571 bài trong official test;
- không thiếu `full_text`, `Vocabulary` hoặc `Grammar`;
- miền giá trị quan sát trên toàn bộ hai file là 1,0–5,0, theo bước 0,5.

Rubric gốc mô tả các mức có thứ tự 1–5. Dự án xử lý điểm tổng hợp như một biến gần liên tục để hồi quy; đây là **giả định mô hình hóa**, không phải tuyên bố rằng khoảng cách năng lực giữa mọi mức là bằng nhau.

### Output cho một bài

- dự đoán Ridge và RF cho `Vocabulary` và `Grammar`;
- dự đoán đồng thuận cho mỗi target, là trung bình của hai dự đoán;
- bất đồng theo từng target;
- một `review_priority_score` cấp bài và lý do target nào tạo ra mức bất đồng cao nhất;
- thông báo rằng đây là tín hiệu triage, không phải confidence hoặc xác suất sai.

## 1.5 Sử dụng có trách nhiệm

1. Dự đoán là ước lượng tham chiếu cho một bài viết, không phải điểm chính thức hay thước đo toàn bộ năng lực tiếng Anh.
2. Bất đồng chỉ là tín hiệu cần kiểm tra. Hai mô hình có thể cùng sai theo một hướng, nên bất đồng thấp không bảo đảm dự đoán đúng.
3. Giáo viên giữ quyền quyết định và phải đọc bài trước khi chấm/phản hồi.
4. Demographic và prompt không được dùng làm feature. Phân tích subgroup chỉ dùng để kiểm tra sai lệch, phải báo cáo cỡ mẫu và độ không chắc chắn, và không được diễn giải theo hướng quy kết thiếu hụt cho người học.
5. Cờ LanguageTool có thể là false positive, gợi ý phong cách hoặc không phù hợp với biến thể phương ngữ; chúng không phải nhãn lỗi.
6. Mọi kết luận chỉ áp dụng cho phạm vi dữ liệu ELLIPSE và cần thẩm định bên ngoài trước khi dùng trong lớp học thực.

## 1.6 Protocol đánh giá đã đóng băng

### A. Đơn vị và các định nghĩa cho RQ1

Với bài $i$ và target $t \in \{V,G\}$:

\[
d_{it}=|\hat y^{Ridge}_{it}-\hat y^{RF}_{it}|,
\qquad
D_i=\max_t d_{it}.
\]

$D_i$ là `review_priority_score` duy nhất của bài. Hàng đợi được sắp theo $D_i$ giảm dần; nếu hòa thì sắp `essay_id` tăng dần để kết quả tất định.

Dự đoán đồng thuận dùng để định nghĩa sai số:

\[
\hat y^{consensus}_{it}=\frac{\hat y^{Ridge}_{it}+\hat y^{RF}_{it}}{2},
\qquad
e_{it}=|y_{it}-\hat y^{consensus}_{it}|.
\]

Bài $i$ là **large-error case** nếu $\max_t e_{it}\ge1.0$ điểm. Ngưỡng 1,0 được chốt trước khi xem kết quả test.

Với $N$ bài test và ngân sách $K$, số bài được xem là $m_K=\lceil K N\rceil$. Các metric:

- **Large Error Capture Rate@K:** số large-error case trong top $m_K$ chia cho tổng large-error case trong test.
- **Precision@K:** số large-error case trong top $m_K$ chia cho $m_K$.
- **Lift@K:** Precision@K chia cho tỷ lệ large-error case trong toàn test.

Nếu test không có large-error case, Capture Rate và Lift được ghi `NA` và RQ1 được kết luận là không đủ bằng chứng, không phải thành công.

### B. Baseline ngẫu nhiên và tiêu chí thành công

- Với mỗi $K$, baseline chọn đồng đều $m_K$ bài không hoàn lại.
- Lặp 1.000 lần với random seed 42; báo cáo trung bình và percentile interval 95% của các metric ngẫu nhiên.
- Dùng 1.000 bootstrap resamples cấp bài trên test để lập CI 95% cho chênh lệch Capture Rate và Lift của chiến lược bất đồng so với baseline. Mỗi resample tính lại top-K và random baseline với seed phát sinh từ seed gốc 42.
- **Tiêu chí thành công primary:** tại $K=20\%$, cận dưới CI 95% của chênh lệch Capture Rate lớn hơn 0. Lift@20 phải lớn hơn 1 và được báo cáo như bằng chứng hỗ trợ.
- Kết quả tại 10% và 30% là secondary/sensitivity, không được dùng để đảo ngược kết luận primary.

Top-K là cơ chế đánh giá RQ1. Ngưỡng triage ứng dụng τ, nếu cần, chỉ được chọn trên validation và không thay thế phép so sánh top-K.

### C. So sánh mô hình và feature

- Mean baseline, Ridge Regression và Random Forest được đánh giá trên cùng split.
- Ridge và RF được fit riêng cho `Vocabulary` và `Grammar`.
- Điều kiện feature đã chốt: Surface-only, Linguistic-only và All Features.
- Metric dự đoán chính là MAE theo từng target; RMSE và $R^2$ là metric phụ. Báo cáo CI bootstrap 95% khi có đủ mẫu hợp lệ.
- Không làm tròn dự đoán về bước 0,5 trước khi tính metric.

### D. Dữ liệu, tuning và test freeze

1. `ELLIPSE_Final_github_train.csv` là development source. File này được chia thành **model-train 80%** và **validation 20%**, seed 42.
2. Các bài trùng nhau theo hash của text đã casefold, trim và gộp whitespace phải nằm cùng partition. Split được phân tầng xấp xỉ theo 10 quantile của trung bình hai target. Phân phối từng target và prompt phải được kiểm tra sau split; prompt không phải feature.
3. Hyperparameter được chọn bằng 5-fold CV chỉ trên model-train. Validation chỉ dùng để chọn feature condition, quy tắc/ngưỡng triage và kiểm tra pipeline trước khi freeze.
4. `ELLIPSE_Final_github_test.csv` là **final held-out test**. Không chia lại file này, không tuning trên nó, và chỉ chạy đánh giá xác nhận sau khi code, feature schema, hyperparameter và protocol đã freeze.
5. Imputation và scaling phải nằm trong pipeline và chỉ `fit` trên fold/model-train tương ứng.
6. Trước khi huấn luyện, phải kiểm tra trùng ID/text giữa development và official test. Mọi overlap phải được giải quyết và ghi lại trước khi mở nhãn test cho đánh giá.

## Bài giải thích 30 giây

> Một hàng dữ liệu là một bài viết tiếng Anh của người học, kèm ID và, trong dữ liệu huấn luyện, hai điểm Vocabulary và Grammar do người chấm cung cấp. Ridge và Random Forest học ước lượng hai điểm từ các đặc trưng ngôn ngữ có thể giải thích, không dùng prompt hay demographic làm feature. Giáo viên nhận một hàng đợi bài viết theo mức bất đồng cao nhất giữa hai mô hình để biết bài nào nên xem trước; giáo viên vẫn là người quyết định cuối cùng.

## Checklist sign-off Phase 1

- [x] RQ1, người dùng và quyết định hỗ trợ đã chốt.
- [x] Input, feature bị cấm, hai target và thang điểm đã kiểm tra.
- [x] Một priority score cấp bài, large-error event và tie-break đã định nghĩa.
- [x] Primary budget, baseline, metric, CI và success criterion đã chốt.
- [x] Development/validation/final-test protocol đã chốt.
- [x] Responsible-use boundary và bài giải thích 30 giây đã chốt.

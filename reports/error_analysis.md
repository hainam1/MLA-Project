# Protocol phân tích lỗi KNN và Decision Tree

File này là template. Không điền kết luận trước khi có final predictions từ cùng một test split.

## Error slices định nghĩa trước

- True CEFR level.
- Prediction distance: đúng, lệch một cấp, lệch từ hai cấp trở lên.
- Sentence-length bins được khóa trước khi xem final errors.
- Lexical rarity/OOV bins.
- Dependency depth và subordinate-clause bins.
- Câu ngắn nhưng có syntactic complexity cao.
- `cefr_sp_en` so với `readme_en`.
- High-probability wrong predictions.

## Manual review protocol

- Chọn mẫu xác định, có stratification theo model, true class và error distance.
- Bao gồm cả dự đoán đúng để tránh chỉ chọn các lỗi nổi bật.
- Gán một hoặc nhiều nhóm: length bias, lexical rarity, rare grammar, ambiguous/noisy label,
  domain/topic cue, parser failure hoặc CEFR-boundary disagreement.
- Với KNN, lưu các nearest neighbors đại diện và nhãn của chúng.
- Với Decision Tree, lưu decision path và các split features liên quan.
- Không diễn giải neighbor/path/feature importance như bằng chứng nhân quả.

## Bảng kết quả cần điền sau Phase 7

| Slice | Model | Số mẫu | Macro F1/Accuracy phù hợp | Lỗi ≥2 cấp | Nhận xét có bằng chứng |
|---|---|---:|---:|---:|---|
| Chưa chạy | KNN | — | — | — | — |
| Chưa chạy | Decision Tree | — | — | — | — |

## Limitations bắt buộc thảo luận

- Class imbalance và ranh giới nhãn CEFR không tuyệt đối.
- Label noise và khác biệt domain giữa hai nguồn.
- KNN nhạy với scaling, `k` và biểu diễn khoảng cách.
- Decision Tree nhạy với pruning và có thể overfit.
- Estimated probabilities có thể chưa được calibration tốt.
- Kết quả dự đoán độ khó câu, không đánh giá trình độ của một người học.

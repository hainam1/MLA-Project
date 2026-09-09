# Chuẩn bị bảo vệ trực tiếp

## Mở đầu trong một phút

Giải thích bài toán hỗ trợ người học, input là một câu tiếng Anh, output A1–C1, dữ liệu có nhãn,
hai family KNN/Decision Tree và Macro F1. Không nhắc các module translation/generation đã loại.

## Câu hỏi bắt buộc tự trả lời được

1. Vì sao đây là bài toán ML thay vì chỉ đặt ngưỡng readability?
2. Vì sao Macro F1 là metric chính dù accuracy dễ hiểu hơn?
3. QWK xử lý lỗi có thứ tự A1 < A2 < B1 < B2 < C1 như thế nào?
4. Vì sao KNN và Decision Tree là hai model families khác nhau?
5. KNN dự đoán bằng hàng xóm gần nhất như thế nào và `k` ảnh hưởng ra sao?
6. Vì sao KNN bắt buộc cần scaling, còn Decision Tree thì không?
7. Decision Tree học các ngưỡng ra sao và vì sao cây sâu dễ overfit?
8. `max_depth`, `min_samples_split` và `min_samples_leaf` giúp pruning thế nào?
9. Duplicate và near-duplicate đã được ngăn đi qua nhiều split như thế nào?
10. Vì sao imputer/scaler/PCA chỉ được fit trên training data?
11. Các nhóm linguistic features biểu diễn thông tin gì?
12. Mô hình nào thắng, hơn bao nhiêu và chênh lệch có ổn định không?
13. Ba lỗi đại diện là gì và nguyên nhân có thể là gì?
14. Class imbalance, label noise và domain bias giới hạn kết luận ra sao?
15. LLM được dùng thế nào và vì sao hệ thống cuối không phải LLM-only?
16. Frozen DeBERTa, nếu có, đóng góp gì và không chứng minh điều gì?

## Hợp đồng demo

- Nhập một câu tiếng Anh.
- Hiển thị CEFR dự đoán và estimated probability của năm lớp.
- Hiển thị một số feature values; với KNN có thể xem hàng xóm, với cây có decision path.
- Nêu rõ output là ước lượng độ khó câu, không phải đánh giá người học.
- Chuẩn bị saved predictions nếu model assets gặp lỗi khi demo.

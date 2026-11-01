# Kết quả rà soát interview_pack

## 1. Manifest và FILE_LIST
Trước lần chốt hiện tại (so với manifest của lượt kiểm tra trước): 78/106 mục khớp; 9 lệch; 19 mất file. Chi tiết ở manifest_before.json; script audit vừa sửa cũng thuộc danh sách được băm, nên hash cũ của chính script có thể khác.
Sau audit: mọi file trừ MANIFEST.sha256 được ghi hash. FILE_LIST.md liệt kê đúng tập mục trong manifest, không liệt kê chính manifest như một mục tự băm. Manifest được ghi sau tất cả nội dung; bước cuối xác minh toàn bộ hash, tập đường dẫn và mtime nghiêm ngặt. Hash manifest được in ra console và báo trong chat, không ghi vào file bên trong để tránh vòng tự tham chiếu.

## 2. Thư mục kiểm định hiển thị
_kiem_tra/hien_thi có 17 PNG (13 render trang PDF + 4 ảnh ghép), pdf_pages.csv và VERIFICATION.md. Đã gom 19 file vào đây và xác minh toàn bộ nội dung giữ nguyên theo hash trước/sau; không cần cho phần trình chiếu phỏng vấn.

## 3. Trang mở đầu
Đã đọc và phân tích toàn bộ HTML: 26 liên kết tương đối, 0 hỏng, 0 liên kết mạng; fragment page của PDF hợp lệ; đủ mục 11–15. Không script, CDN, @import hoặc url CSS; không cần máy chủ khi mở file trực tiếp. links.json có danh sách đầy đủ.
Mở bằng trình duyệt UI: CHƯA XÁC NHẬN. Công cụ CUA tự chặn vì không xác định đủ tin cậy URL hiện tại trên Windows; không tiếp tục thao tác UI. Kết quả trên là xác minh tĩnh đích file, không phải tuyên bố đã mở trang thành công.

## 4. Cây và mẫu
TREE.txt liệt kê toàn bộ cây, kích thước byte, file rỗng và mẫu trống. File rỗng vật lý: 0. Mẫu CSV/hướng dẫn trống: 9; thêm hai file dữ liệu có ô cố ý để trống được đánh dấu riêng. Không điền thay thành viên.

## 5. Quét riêng tư
Quét 74 file text/PDF; giải mã 25 PNG, 8 PNG khớp manifest trước audit. Không OCR PNG; ảnh dựa trên QA trực quan và tính toàn vẹn.
Số chuỗi 10 chữ số theo regex, phân loại ngữ cảnh: {'decimal_value': 36, 'essay_id_hex': 28, 'essay_id_numeric_10': 1, 'hash_or_commit': 15}. Không in giá trị/đoạn bài luận. Xem privacy_scan.json để lấy vị trí từng match; các số thập phân và hash không được tự gọi là mã sinh viên.
Một ID bài toàn số 10 chữ số: 07_kiem_tra_offline/development_predictions.csv, dòng 1751, cột essay_id. Đã đối chiếu với reports/week9/t3_eligible_development.csv / essay_id: xuất hiện đúng một lần. Trong 3812 ID duy nhất: 3809 ID dài 12 ký tự hex có chữ; 2 ID toàn số dài 11 chữ số; 1 ID toàn số dài 10 chữ số. Nguồn và hash nguồn trong doi_chieu_id_va_di_chuyen.json. Không thay ID để tránh thay phép xếp hạng. Các literal định nghĩa quy tắc của chính audit_pack.py không được xem là payload bài luận; đã kiểm tra các false positive đó theo vị trí, không in nội dung bài.
Trường chứa payload hoặc cột dữ liệu riêng tư: 0; mẫu họ tên đầy đủ thành viên: 0; đoạn English dài cần xem xét: 0; định dạng chưa xử lý: 0.
Không phát hiện payload bài luận theo các kiểm tra trên. Không thể chứng minh tuyệt đối không có bài luận bằng đối chiếu corpus vì không được mở corpus; cũng không có danh sách họ tên đầy đủ chuẩn để so khớp toàn bộ tên bất kỳ. Nhãn thư mục Nam/Giang/Linh là ba nhãn đã được yêu cầu.

## 6. Chạy offline
Hai tiến trình Python -I có audit hook chặn socket/network và mọi đọc repository ngoài gói. Cả hai return code 0, dưới 10 giây. Thời gian là toàn tiến trình, không chỉ đồng hồ nội bộ script.
- check_d_88_of_386.py: 0.085871 giây
- check_synthetic_ranking.py: 0.052556 giây
D in 88/386; expected_random=77.362908 (77.36), tổng budget=764. Script synthetic có N=10, K=3, k=2, caught=1, E=0,6; không phải script synthetic cũng in 88/386. Stdout được lưu riêng, không sửa ảnh đầu ra đã có.

## 7. Những phần còn thiếu nguồn/xác nhận
- 55/208, 47/208: khớp log/RESULTS; p 0,0116 so ngẫu nhiên, không phải so D. Ngày dùng Test đầu tiên: chưa xác định; tuần 9 là mốc báo cáo/tái kiểm.
- MAE mean baseline trong cùng GroupKFold: chưa có nguồn trong t3_regression; không lấy một bảng chia khác để thế vào.
- “5 bài đọc hai bản”: nguồn hiện tại chỉ chứng minh ghi nhận cũ và hai phiếu mới còn trống. 0 cặp đủ điều kiện độc lập. Bản B cũ điền sẵn: chưa có nguồn được xác nhận. Không tạo so sánh giả.
- Ghi nhận cũ: 32 ca, 22 RF sai lớn. Không tự xác nhận đủ rubric mới chỉ từ số đếm; mẫu 10 ca và danh sách ứng viên cần thành viên thực hiện.
- Rubric gốc MLA Final Project Requirements and Rubric ngày 26/10/2026: chưa có nguồn gốc đã xác nhận trong nguồn được đọc. Gói dựng theo yêu cầu đính kèm; docs/instructor_requirements.md là tổng hợp có ghi cần xác minh đề gốc.
- Điều kiện ELLIPSE theo data card: CC BY-NC-SA 4.0 và cho phép tái phân phối có điều kiện. Quyền trình chiếu văn bản từng bài chưa rõ; không kèm bài luận.
- Phân rã đúng dự đoán OOF: thiếu mô hình riêng từng fold được xác nhận. Đã cung cấp phân rã từ bốn model Phase 6 có hash, ghi riêng scope; không coi là cùng mô hình.
- Nhật ký quyết định/đóng góp/AI: mẫu trống; lịch sử chi tiết chưa đầy đủ, cần thành viên xác nhận.

15,0% và 16,6% đã có nguồn 35/233 và 36/217 ở tuần 10; không còn là số thiếu nguồn. File khóa được đối chiếu bằng hai bản trong gói, không mở nguồn ngoài gói.

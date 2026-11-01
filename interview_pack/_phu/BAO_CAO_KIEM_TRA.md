# Kiểm tra cuối gói một file mỗi mục
Gói chỉ đọc hồ sơ đã có; không mở Official Test/corpus, không in nội dung bài luận, không huấn luyện lại. Không xóa file có nội dung. Nhật ký di chuyển và hash trước/sau ở _kiem_tra/di_chuyen_toi_uu.json; chỉ rmdir sau khi kiểm tra thật sự rỗng.

## 1 Cấp cao nhất
Đúng 16 file từ 00 đến 15 và một thư mục _phu. Bộ 01 (8 trang), 03 và 10 giữ nguyên SHA-256 so với trước tối ưu.

| Tên | Kích thước byte | Giờ sửa Việt Nam |
|---|---:|---|
| 00_START_HERE.html | 2669 | 2026-11-01 17:27:14.480918 +07:00 |
| 01_trinh_chieu.pdf | 61473 | 2026-11-01 15:18:01.576197 +07:00 |
| 02_mau_truy_vet.pdf | 54565 | 2026-11-01 16:40:23.229525 +07:00 |
| 03_so_do_chia.pdf | 48097 | 2026-11-01 15:18:01.605462 +07:00 |
| 04_bang_ket_qua.pdf | 50598 | 2026-11-01 16:11:33.125657 +07:00 |
| 05_ca_loi.xlsx | 6993 | 2026-11-01 17:03:26.538275 +07:00 |
| 06_lich_su_dung_test.pdf | 48981 | 2026-11-01 16:11:33.133593 +07:00 |
| 07_kiem_tra_offline.bat | 364 | 2026-11-01 16:06:58.622019 +07:00 |
| 08_tai_lap.pdf | 51845 | 2026-11-01 16:11:33.142205 +07:00 |
| 09_dong_gop_va_ai.xlsx | 5887 | 2026-11-01 16:06:35.851094 +07:00 |
| 10_so_tay_so_lieu.pdf | 47583 | 2026-11-01 15:18:01.613557 +07:00 |
| 11_ba_cau_giai_thich.pdf | 570489 | 2026-11-01 16:11:33.328852 +07:00 |
| 12_mang_theo.pdf | 299636 | 2026-11-01 16:11:33.421142 +07:00 |
| 13_cau_truc_bao_cao_cuoi.pdf | 49744 | 2026-11-01 16:11:33.431141 +07:00 |
| 14_luot_di_qua.pdf | 53497 | 2026-11-01 16:11:33.113760 +07:00 |
| 15_review_tuan10_mau.docx | 37711 | 2026-11-01 16:09:19.938946 +07:00 |
| _phu | thư mục | 2026-11-01 16:13:23.526952 +07:00 |

## 2 PDF và Office
- 01_trinh_chieu.pdf: 8 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 02_mau_truy_vet.pdf: 2 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 03_so_do_chia.pdf: 1 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 04_bang_ket_qua.pdf: 1 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 06_lich_su_dung_test.pdf: 1 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 08_tai_lap.pdf: 2 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 10_so_tay_so_lieu.pdf: 1 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 11_ba_cau_giai_thich.pdf: 3 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 12_mang_theo.pdf: 2 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 13_cau_truc_bao_cao_cuoi.pdf: 1 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.
- 14_luot_di_qua.pdf: 2 trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.

Tổng 24 trang PDF chính; file Word render kiểm tra bằng Word cài sẵn: 1 trang. Bộ render_docx.py đã thử nhưng máy không có LibreOffice; fallback Word native chỉ mở file DOCX mới ở chế độ read-only để xuất PDF. Cả 3 sheet Excel đã render bằng artifact-tool và xem lại. 05 có một sheet; 09 có đúng hai sheet. 05 đã nhận hai bản điền đầy đủ cho cùng 5 bài, mỗi người đủ 40 ô Phần A/B và 6 ô xác nhận; ghép ID bằng 6 số điểm thật/RF/Ridge do thứ tự bài khác nhau. Số đếm A/B được chép đúng nguồn mới; chỉ lưu alias/hash, không sao chép workbook chứa bài hay danh tính. Có nội dung tự xác nhận, chưa kiểm chứng quy trình. Ô giải thích/kết luận của 5 ca đã điền bằng tóm lược hai bản nộp theo yêu cầu mới, có tách ý A/B và tọa độ ô/hash nguồn ở 05_ca_loi/tom_luoc_nhan_xet_da_nop.json; không sao chép ví dụ trích bài. Năm dòng bổ sung và mọi ô trả lời đóng góp/AI vẫn trống. File Word chỉnh sửa được, các ô trả lời trống. Bản ghi nguồn mới ở 05_ca_loi/kiem_tra_hai_ban_da_nop.json; kết luận thiếu bản nộp trong hồ sơ cũ là trạng thái lịch sử, không phải trạng thái hiện tại.
Mục 02 đã sửa theo yêu cầu làm rõ: nghĩa tiếng Việt trong ngoặc và miền min–max theo định nghĩa của 14 đặc trưng thô, không dùng cực trị quan sát trong dữ liệu. Tỷ lệ có miền 0–1; số đếm và độ dài không có trần cố định; sentence_count tối thiểu 1 ở đầu vào hợp lệ. Zipf có sàn 0 và trần lý thuyết 9 theo log10(p)+9 với p<=1; thường gặp 0–8, không coi 8 là trần cứng. Nguồn và hash nguồn: 02_mau_truy_vet/nguon_mien_gia_tri.json; giai_nghia_va_mien_gia_tri.csv; docs/feature_specification.md và mã extractor/wordfreq. Hai trang 02 đã render và xem lại; không đổi số liệu bài, dự đoán, D hoặc thứ hạng. Các tệp max_development trước và PDF trước sửa được giữ làm lịch sử trong _phu, không phải miền giá trị hiện tại.

## 3 Liên kết
0 liên kết hỏng, 0 liên kết mạng trong mọi HTML và mọi annotation liên kết PDF. Các liên kết Markdown nguồn cũng được kiểm tra. Nguồn citation dạng tên file/commit là văn bản, không cần mạng. 00 có đường dẫn trực tiếp tới 01–15. Kết quả tĩnh ở _kiem_tra/toi_uu/links.json; không cần máy chủ.

## 4 Chạy BAT khi chặn mạng
07_kiem_tra_offline.bat chạy thực tế bằng cmd.exe, return code 0, toàn tiến trình 0.233 giây. Python audit hook từ chối socket/urllib/http và mọi đọc repository ngoài gói. Hai script cũ được giữ nguyên. D in 88/386; E=77.362908 (77.36), dòng nhắc 77,36; synthetic N=10, K=3, k=2, caught=1, E=0,6. BAT có pause; test cấp newline chỉ để đi qua pause. Stdout thực tế và PNG kết xuất stdout ở _kiem_tra/toi_uu/BAT_stdout.txt và BAT_stdout.png.

## 5 Riêng tư
Quét text/PDF/OOXML XLSX/DOCX, kiểm cột CSV và mẫu họ tên thành viên; không phát hiện payload bài luận, cột mã sinh viên hoặc họ tên đầy đủ. Essay_id số 10 chữ số đã được đối chiếu trực tiếp với development ở lượt trước; giữ nguyên. Không OCR PNG và không đối chiếu corpus; ảnh đã kiểm tra trực quan/nguồn tạo, không tuyên bố phương pháp regex chứng minh tuyệt đối mọi loại tên bất kỳ. Các nhãn Nam/Giang/Linh chỉ dùng nơi mẫu yêu cầu.

## 6 FILE_LIST và manifest
FILE_LIST được viết sau nội dung, MANIFEST được viết cuối cùng sau FILE_LIST. Mọi file trong cả gói được băm, trừ _phu/MANIFEST.sha256 không thể tự băm. FILE_LIST liệt kê đúng các mục manifest; TREE đầy đủ có kích thước. Hash manifest và số khớp/không khớp được in sau bước cuối, không ghi hash manifest vào file bên trong gây vòng tham chiếu.

## 7 Chưa có nguồn hoặc cần xác nhận
- MAE mean baseline cùng GroupKFold: chưa có nguồn.
- Mô hình từng fold OOF để phân rã chính xác từng dự đoán: chưa có nguồn được xác nhận; phân rã Phase 6 cũ được giữ riêng.
- Ngày truy cập Test đầu tiên: chưa xác định; tuần 9 là mốc báo cáo.
- Rubric gốc 26/10 và bản trả lời gốc của thầy, cách tính trang phụ lục: chưa có nguồn xác nhận.
- Đã nhận hai bản điền đủ và có lời tự xác nhận; còn chưa kiểm chứng trình tự đọc, lịch sử xem thông tin hay trao đổi. Không tiếp tục gọi hai bản mới là trống/chưa làm; bản B cũ là hồ sơ lịch sử riêng.
- Quyền hiển thị văn bản từng bài và nhật ký đóng góp/AI chi tiết: chưa rõ/chờ thành viên; gói không kèm văn bản bài.
- 15,0% và 16,6% đã có nguồn 35/233 và 36/217 trong báo cáo tuần 10, không còn là số thiếu nguồn.

Các script dựng cũ trong 08_tai_lap là hồ sơ lịch sử trước đổi bố cục. Cách chạy trực tiếp hiện tại là BAT; công cụ dựng/chốt bố cục mới ở _cong_cu. Không chạy các script lịch sử có fit hoặc đánh giá Test.

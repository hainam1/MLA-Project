"""Populate safe Vietnamese summaries of the two submitted annotation forms."""
from pathlib import Path
import json, shutil
P=Path(__file__).resolve().parents[2]
datafile=P/'_phu/_cong_cu/workbook_input.json'
data=json.loads(datafile.read_text(encoding='utf-8'))
summaries={
'51DA4BA94C7C':(
'A: Nhiều lỗi dạng động từ, cấu trúc và nối mệnh đề; có từ nâng cao nhưng dùng chưa tự nhiên. Chọn mã 4, 6.\nB: Lỗi động từ, hòa hợp chủ-vị, đại từ và nối câu; công cụ có thể đếm thiếu. Chọn mã 1, 4, 6.',
'Cả hai cho rằng điểm ngữ pháp 4,0 có vẻ cao, cùng chọn lỗi ngữ pháp chưa được tính và nghi điểm chấm lệch. A đề nghị đối chiếu tiêu chí chấm. Đây là nhận định người đọc, chưa xác nhận nhãn sai.'),
'D1D770AF6855':(
'A: Từ vựng phổ thông, lặp lại; có cụm phù hợp chủ đề nhưng dùng từ chưa chính xác. Chọn mã 3, 6.\nB: Có lập luận và từ đúng chủ đề, nhưng cách diễn đạt còn cơ bản, lặp lại và thiếu tự nhiên. Chọn mã 3, 6.',
'Cả hai cùng nêu đặc trưng có thể chưa phản ánh từ vựng phù hợp chủ đề và nghi điểm 5,0 cao. B lưu ý RF/Ridge gần nhau nên bất đồng không giúp phát hiện ca này. Cần kiểm chứng điểm và cách đo từ vựng.'),
'4032ED0063E4':(
'A: Thiếu trợ động từ, lỗi số ít/số nhiều, câu thiếu thành phần; từ vựng đơn giản và lặp. Chọn mã 4, 6.\nB: Bài ngắn, lỗi ngữ pháp cơ bản và nối câu; tín hiệu độ dài và ngữ pháp có thể góp phần vào sai số. Chọn mã 1, 2, 4, 6.',
'Hai người cùng cho rằng điểm ngữ pháp 4,0 chưa tương xứng, cùng chọn mã 4, 6. B bổ sung giả thuyết bài ngắn và công cụ đếm thiếu. Cần đối chiếu cách tính lỗi và tiêu chí chấm; chưa quy toàn bộ chênh lệch cho mô hình.'),
'0FFB44B5D0C2':(
'A: Từ lặp, lỗi dùng từ và chính tả; vốn từ hạn chế dù nội dung bám đề. Chọn mã 3, 6.\nB: Từ vựng phổ thông, lặp lại, có kết hợp từ thiếu tự nhiên; vẫn hiểu được ý tổng quát. Chọn mã 3, 6.',
'Cả hai cùng nghi điểm từ vựng 4,0 cao và đặc trưng chưa phản ánh đủ cách chấm. A đề nghị đối chiếu tiêu chí; B nhấn mạnh đánh giá độ phù hợp của điểm còn chủ quan. Chưa xác định nguyên nhân đã được kiểm chứng.'),
'277A95AC0190':(
'A: Câu dài thiếu dấu câu, lỗi hòa hợp chủ-vị và cấu trúc; từ phổ thông, lặp và sai chính tả. Chọn mã 4, 6.\nB: Lỗi chính tả, hòa hợp và cấu trúc lặp lại; công cụ có thể đếm thiếu. Chọn mã 1, 4, 6.',
'Cả hai cùng nghi điểm ngữ pháp 4,0 cao, chọn lỗi ngữ pháp chưa được tính và nghi điểm chấm lệch. A đề nghị kiểm tra lại điểm và cách tính lỗi; B nêu khả năng mô hình và người chấm dùng tín hiệu khác nhau. Chưa kết luận máy sai hoàn toàn.')}
mapping={'A':['51DA4BA94C7C','277A95AC0190','4032ED0063E4','D1D770AF6855','0FFB44B5D0C2'], 'B':['51DA4BA94C7C','4032ED0063E4','0FFB44B5D0C2','D1D770AF6855','277A95AC0190']}
evidence={'scope':'Tóm lược nhận xét đã nộp; bỏ toàn bộ ví dụ trích bài và danh tính. Không suy luận nguyên nhân mới. Không đọc sheet bài luận.', 'codes':{'1':'công cụ đếm lỗi thiếu','2':'bài ngắn','3':'từ vựng/ý hay nhưng đặc trưng không đo','4':'lỗi ngữ pháp không được tính','6':'nghi điểm người chấm lệch'}, 'cases':[]}
for r in data['cases']:
 eid=r['essay_id'];r['submitted_explanation'],r['submitted_conclusion']=summaries[eid]
 sources={}
 for alias,ids in mapping.items():
  i=ids.index(eid);start=6+7*i
  sources[alias]={'source_sha256':data['submitted_readers'][alias]['source_sha256'],'part_A_answer_cells':f'B{start}:B{start+3}','part_B_answer_cells':f'B{start}:B{start+3}','sheet_indexes_zero_based':[2,4]}
 evidence['cases'].append({'essay_id':eid,'explanation':summaries[eid][0],'conclusion':summaries[eid][1],'sources':sources})
backup=P/'_phu/_kiem_tra/toi_uu/05_ca_loi_truoc_dien_nhan_xet.xlsx'
if not backup.exists():shutil.copy2(P/'05_ca_loi.xlsx',backup)
datafile.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'_phu/05_ca_loi/tom_luoc_nhan_xet_da_nop.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
b=P/'_phu/_cong_cu/build_workbooks.mjs';s=b.read_text(encoding='utf-8')
s=s.replace('Giải thích và kết luận vẫn để TRỐNG','Giải thích/kết luận: tóm lược hai bản đã nộp, tách ý A/B')
s=s.replace("quy trình',null,null,", "quy trình',r.submitted_explanation,r.submitted_conclusion,")
s=s.replace("_phu/05_ca_loi/5_ca_hai_ban_da_nop.csv']);", "_phu/05_ca_loi/5_ca_hai_ban_da_nop.csv; _phu/05_ca_loi/tom_luoc_nhan_xet_da_nop.json (ô nguồn và SHA-256 A/B)']);")
s=s.replace("const widths=[155,75,90,105,105,90,90,135,250,220,220,340];","s.getRange('A6:L10').format.rowHeight=235;\nconst widths=[155,75,90,105,105,90,90,135,250,420,420,340];")
s=s.replace('Không tự viết thêm nguyên nhân hay kết luận.', 'Hai cột cuối tóm lược nhận xét đã nộp theo yêu cầu mới; không phải nguyên nhân được kiểm chứng. Năm dòng bổ sung vẫn trống.')
b.write_text(s,encoding='utf-8')
seal=P/'_phu/_cong_cu/seal_optimized.py';s=seal.read_text(encoding='utf-8')
s=s.replace("assert all(cells[0].get(f'{col}{row}','')=='' for row in range(6,16) for col in ['J','K'])", "# First five explanations/conclusions are authorized summaries of submitted forms.")
s=s.replace("for rownum,r in enumerate(submitted,6):", "for rownum,r in enumerate(submitted,6):\n assert cells[0][f'J{rownum}']==r['submitted_explanation']\n assert cells[0][f'K{rownum}']==r['submitted_conclusion']")
s=s.replace('Ô giải thích/kết luận, 5 dòng bổ sung và mọi ô trả lời đóng góp/AI đều trống.', 'Ô giải thích/kết luận của 5 ca đã điền bằng tóm lược hai bản nộp theo yêu cầu mới, có tách ý A/B và tọa độ ô/hash nguồn ở 05_ca_loi/tom_luoc_nhan_xet_da_nop.json; không sao chép ví dụ trích bài. Năm dòng bổ sung và mọi ô trả lời đóng góp/AI vẫn trống.')
seal.write_text(s,encoding='utf-8')
print('Prepared five paired summaries; preserved prior workbook.')

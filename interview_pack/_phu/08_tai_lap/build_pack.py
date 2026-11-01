"""Build offline interview artifacts from an explicit safe source allowlist.
No training, no Test input, no essay text. Run with Python + reportlab/Pillow/PyMuPDF.
"""
from pathlib import Path
import csv, json, hashlib, math, html, io, subprocess, sys, time, re
from collections import Counter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
import fitz
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parents[1]; R=P.parent
SOURCES={}
ALLOW={
 'reports/week9/t3_heldout_predictions.csv','reports/week9/t3_eligible_development.csv',
 'reports/week9/t3_fold_composition.csv','reports/week9/t3_regression.csv','reports/week9/t3_pooled.csv',
 'reports/week9/t4_reading_summary.csv','reports/week9/RESULTS_week9.md',
 'reports/week9/RESULTS_tree_spread_second_use.md',
 'reports/week9/tree_spread_official_test_second_use_log_attempt2.json',
 'reports/week9/tree_spread_official_test_second_use_log.json',
 'reports/week10/gec_part_a_68.csv','reports/week10/b2_oof.csv',
 'reports/week10/RESULTS_week10.md','docs/data_card.md','docs/signal_lock_tree_spread.md',
 'docs/du_lieu_interview.md','docs/phieu_luyen_mot_bai_development.md',
 'docs/phieu_luyen_684166ED2438_development.md','docs/split_and_leakage_protocol.md',
 'docs/llm_disclosure.md','docs/instructor_requirements.md','docs/independent_readers_README.md',
 'outputs/phase6/feature_schema.json','scripts/week9b/paired_tree_spread.py',
 'scripts/tree_spread_official_test_second_use.py'}
def read(rel):
 assert rel in ALLOW,rel
 b=(R/rel).read_bytes(); SOURCES[rel]=hashlib.sha256(b).hexdigest()
 return b.decode('utf-8-sig')
def rows(rel):return list(csv.DictReader(io.StringIO(read(rel))))
def write(rel,s):
 p=P/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def csvout(rel,data,fields=None):
 data=list(data);fields=fields or list(data[0])
 p=P/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(data)
def source_excerpt(rel,select):
 lines=read(rel).splitlines(); chosen=[f'{i+1}: {line}' for i,line in enumerate(lines) if select(i+1,line)]
 chosen=[re.sub(r'\[([^\]]*)\]\(([^)]+)\)',lambda m:m.group(0) if m.group(2).startswith(('https://','http://')) else m.group(1)+' (nguồn gốc trong repository: `'+m.group(2)+'`)',line) for line in chosen]
 write('08_tai_lap/nguon/'+Path(rel).stem+'.md',f'# Nguồn: {rel}\nSHA256 toàn file: {SOURCES[rel]}\n\nTrích chọn metadata/số liệu; không chứa bài luận.\n\n'+'\n'.join(chosen)+'\n')

for folder in ['02_mau_truy_vet','04_bang_ket_qua','05_ca_loi','07_kiem_tra_offline','08_tai_lap/nguon','09_dong_gop_va_ai','_kiem_tra/hien_thi']:(P/folder).mkdir(parents=True,exist_ok=True)
schema=json.loads(read('outputs/phase6/feature_schema.json'))
dev=rows('reports/week9/t3_eligible_development.csv');assert all(r['source_partition']=='official_train' for r in dev)
pred=[r for r in rows('reports/week9/t3_heldout_predictions.csv') if r['split_type']=='prompt_disjoint']
assert len(dev)==len(pred)==3812
for r in pred:
 r['_D']=max(abs(float(r['RF_V'])-float(r['Ridge_V'])),abs(float(r['RF_G'])-float(r['Ridge_G'])))
 r['_L']=max(abs(float(r['RF_V'])-float(r['y_V'])),abs(float(r['RF_G'])-float(r['y_G'])))>=1
 r['_B']=r['_L'] and max(abs(float(r['Ridge_V'])-float(r['y_V'])),abs(float(r['Ridge_G'])-float(r['y_G'])))>=1
for fold in sorted({r['fold'] for r in pred}):
 group=sorted([r for r in pred if r['fold']==fold],key=lambda r:(-r['_D'],r['essay_id']))
 for j,r in enumerate(group):r['_rank']=j+1;r['_n']=len(group);r['_k']=math.ceil(.2*len(group))
fields=['essay_id','split_type','fold','y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G']
csvout('07_kiem_tra_offline/development_predictions.csv',pred,fields)
csvout('08_tai_lap/nguon/t3_fold_composition.csv',rows('reports/week9/t3_fold_composition.csv'))
csvout('08_tai_lap/nguon/t3_regression.csv',[r for r in rows('reports/week9/t3_regression.csv') if r['split_type']=='prompt_disjoint' and r['fold']=='pooled'])
csvout('08_tai_lap/nguon/t3_pooled.csv',[r for r in rows('reports/week9/t3_pooled.csv') if r['split_type']=='prompt_disjoint'])
gec=rows('reports/week10/gec_part_a_68.csv');reading=rows('reports/week9/t4_reading_summary.csv')
csvout('08_tai_lap/nguon/gec_part_a_68.csv',gec)
safe_read_fields=['essay_id','sample_group','y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G','D','word_count','reader_error_count_first150','approx_tool_count','explained']
csvout('05_ca_loi/32_ca_da_co_ghi_nhan.csv',reading,safe_read_fields)
log=json.loads(read('reports/week9/tree_spread_official_test_second_use_log_attempt2.json'))
stopped=json.loads(read('reports/week9/tree_spread_official_test_second_use_log.json'))
assert log['status']=='COMPLETED' and log['result']['caught']==55
for rel,sel in [
 ('docs/data_card.md',lambda n,l: n<10 or any(k in l for k in ['License','Redistribution','Unit of','grade','score range','3,911','2,571','6,482','aggregate','approximately continuous','protected handling'])),
 ('docs/signal_lock_tree_spread.md',lambda n,l:True),
 ('reports/week9/RESULTS_week9.md',lambda n,l: n in [23,24,32,33] or 1403<=n<=1440 or 1490<=n<=1538),
 ('reports/week10/RESULTS_week10.md',lambda n,l: 1680<=n<=1713 or 1410<=n<=1430),
 ('docs/du_lieu_interview.md',lambda n,l: n>=85 and not any(k in l for k in ['họ tên','Họ tên','chữ ký','Chữ ký'])),
 ('docs/split_and_leakage_protocol.md',lambda n,l:n<=50),
 ('docs/llm_disclosure.md',lambda n,l:n>=34)]:source_excerpt(rel,sel)
for rel in ['docs/phieu_luyen_mot_bai_development.md','docs/phieu_luyen_684166ED2438_development.md','docs/instructor_requirements.md','docs/independent_readers_README.md','reports/week9/RESULTS_tree_spread_second_use.md','scripts/week9b/paired_tree_spread.py','scripts/tree_spread_official_test_second_use.py']:read(rel)
lockhash=hashlib.sha256((R/'docs/signal_lock_tree_spread.md').read_bytes()).hexdigest()
assert lockhash=='d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca'
assert SOURCES['scripts/tree_spread_official_test_second_use.py']=='cc7bdd6efd8c0cf23a4f6dbd5673e17a5c8501aaf72e77fb0b99e96090b31e05'
arith=json.loads((P/'02_mau_truy_vet/saved_model_arithmetic.json').read_text(encoding='utf-8'))
IDS=['0514D25768A0','684166ED2438'];b2=rows('reports/week10/b2_oof.csv')
samples={}
for essay in IDS:
 d=next(r for r in dev if r['essay_id']==essay);r=next(r for r in pred if r['essay_id']==essay);b=next(r for r in b2 if r['essay_id']==essay)
 record={'essay_id':essay,**{s:d[s] for s in schema},**{s:r[s] for s in ['fold','y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G']},'MiniLM_V':b['B2_V'],'MiniLM_G':b['B2_G'],'D':r['_D'],'D_rank':r['_rank'],'fold_n':r['_n'],'budget':r['_k'],'RF_large_error':r['_L'],'shared_large_error':r['_B'],'selected_by_D':r['_rank']<=r['_k'],'source_features':'reports/week9/t3_eligible_development.csv','source_predictions':'reports/week9/t3_heldout_predictions.csv; prompt_disjoint','source_MiniLM':'reports/week10/b2_oof.csv','scope':'Held-out fold predictions; NOT frozen-model arithmetic'}
 csvout(f'02_mau_truy_vet/{essay}.csv',[record]);samples[essay]=record
 terms=[];trees=[]
 for name,a in arith['rows'][essay].items():
  if name.startswith('ridge'):
   terms.extend([{'model':name,**t,'intercept':a['intercept'],'sum_plus_intercept':a['reconstructed'],'model_sha256':a['sha256'],'scope':arith['scope']} for t in a['terms']])
  else:trees.extend([{'model':name,'tree':j+1,'prediction':v,'tree_mean':a['reconstructed'],'model_sha256':a['sha256'],'scope':arith['scope']} for j,v in enumerate(a['tree_predictions'])])
 csvout(f'02_mau_truy_vet/{essay}_ridge_terms.csv',terms);csvout(f'02_mau_truy_vet/{essay}_300_trees.csv',trees)
write('02_mau_truy_vet/README.md','''# Truy vết hai bài development
CSV một dòng và PNG dùng dự đoán held-out GroupKFold theo đề từ hồ sơ đã lưu.
Ridge: y_hat = intercept + sum_j(coefficient_j * standardized_value_j).
Chuẩn hóa dùng trung bình/độ lệch chuẩn của tập đã fit, sau điền thiếu bằng trung vị tập fit.
RF: y_hat = sum(tree_prediction_t)/300, sau tiền xử lý của pipeline đã lưu.
Các file *_ridge_terms.csv, *_300_trees.csv và saved_model_arithmetic.json là phép tính từ mô hình Phase 6 đã lưu, đã kiểm SHA256; không phải mô hình OOF của bảng truy vết. Không ghép chúng để giải thích chính xác dự đoán OOF.
0514D25768A0 thuộc validation ban đầu; 684166ED2438 thuộc model_train ban đầu, nên phép tính từ mô hình Phase 6 của bài thứ hai là in-sample. Chỉ bảng OOF dùng để đánh giá held-out.
Không còn mô hình riêng của từng fold đã lưu được xác nhận trong nhiệm vụ này; vì vậy phân rã đúng các dự đoán OOF: để trống, lý do thiếu mô hình fold. Không fit lại để lấp khoảng trống.
Nguồn: docs/phieu_luyen_*.md; reports/week9/t3_eligible_development.csv; reports/week9/t3_heldout_predictions.csv; outputs/phase6/*.joblib; hash chi tiết trong JSON.
''')
main=[
 {'scope':'Dev - D','N':3812,'K':386,'budget':764,'caught':88,'random':77.362908429581,'base_rate':386/3812,'source':'S1: reports/week9/t3_pooled.csv; prompt_disjoint, A1_RF, Disagreement'},
 {'scope':'Dev - D, cùng sai','N':3812,'K':276,'budget':764,'caught':44,'random':55.32185687702314,'base_rate':276/3812,'source':'S1: reports/week9/t3_pooled.csv; prompt_disjoint, A3_Both_wrong, Disagreement'},
 {'scope':'Dev - độ lệch cây','N':3812,'K':386,'budget':764,'caught':96,'random':77.362908429581,'base_rate':386/3812,'source':'S2: reports/week9/RESULTS_week9.md; Week 9b CAPTURE_METRICS'},
 {'scope':'Test - D đã lưu','N':2518,'K':208,'budget':504,'caught':47,'random':41.6330420969023,'base_rate':208/2518,'source':'S3: reports/week9/RESULTS_week9.md; Task 0'},
 {'scope':'Test - cây, dùng lại','N':2518,'K':208,'budget':504,'caught':55,'random':41.6330420969023,'base_rate':208/2518,'source':'S4: reports/week9/tree_spread_official_test_second_use_log_attempt2.json; result'}]
csvout('04_bang_ket_qua/bang_chinh.csv',main)
reg=[r for r in rows('reports/week9/t3_regression.csv') if r['split_type']=='prompt_disjoint' and r['fold']=='pooled']
models=[]
for name,assumption,loss,why in [('Mean','Điểm trung bình tập fit','Bình phương sai số','Mốc hằng số để kiểm tra giá trị của ML'),('Ridge','Quan hệ tuyến tính gần đúng trên đặc trưng chuẩn hóa','SSE + alpha * ||beta||²','Giảm hệ số lớn, dễ phân rã'),('RF','Quan hệ phi tuyến; mẫu tương lai gần phân phối huấn luyện','Cây giảm bình phương sai số; lấy trung bình','Mô hình tương tác và ngưỡng đặc trưng')]:
 vals={r['target']:float(r['MAE']) for r in reg if r['model']==name}
 models.append({'model':name,'MAE_V':vals.get('V',''),'MAE_G':vals.get('G',''),'assumption':assumption,'training_loss':loss,'why':why,'source':'reports/week9/t3_regression.csv; prompt_disjoint, pooled' if vals else 'Chưa có nguồn cho MAE mean baseline cùng GroupKFold; không điền'})
csvout('04_bang_ket_qua/bang_mo_hinh.csv',models)
five=['51DA4BA94C7C','D1D770AF6855','4032ED0063E4','0FFB44B5D0C2','277A95AC0190'];case=[]
for essay in five:
 r=next(r for r in reading if r['essay_id']==essay)
 target='V' if float(r['y_V'])-float(r['RF_V'])>=1 else 'G'
 case.append({'essay_id':essay,'target':target,'truth':r['y_'+target],'RF':r['RF_'+target],'Ridge':r['Ridge_'+target],'reader_A_legacy_count':r['reader_error_count_first150'],'reader_B_count':'','old_tool_estimate':r['approx_tool_count'],'selection_reason':'Danh sách đã chốt; điểm đích >=4 và RF thấp hơn >=1','independence_B':'Không xác nhận độc lập. Hai phiếu mới còn trống theo docs/du_lieu_interview.md; tình trạng phiếu B cũ điền sẵn: chưa có nguồn được xác nhận','reader_explanation':'','source':'reports/week9/t4_reading_summary.csv; docs/independent_readers_README.md; docs/du_lieu_interview.md'})
csvout('05_ca_loi/5_ca_cho_hai_ban.csv',case)
qual_large=sum(max(abs(float(r['RF_V'])-float(r['y_V'])),abs(float(r['RF_G'])-float(r['y_G'])))>=1 for r in reading)
fields_blank=['essay_id','quy_tac_chon','dich_sai','nguoi_A_tom_y','nguoi_B_tom_y','nguyen_nhan_do_nguoi_doc_dien','xac_nhan_doc_lap','nguon']
csvout('05_ca_loi/mau_10_ca.csv',[dict.fromkeys(fields_blank,'') for _ in range(10)],fields_blank)
candidates=sorted([r for r in pred if r['_B'] and r['essay_id'] not in {x['essay_id'] for x in reading}],key=lambda r:(-r['_D'],r['essay_id']))[:5]
csvout('05_ca_loi/5_ung_vien_chua_doc.csv',[{'essay_id':r['essay_id'],'fold':r['fold'],'D':r['_D'],'D_rank_in_fold':r['_rank'],'status':'CHƯA ĐỌC; không phải phân tích lỗi hoàn tất','source':'reports/week9/t3_heldout_predictions.csv; prompt_disjoint; A3 tự tính; D giảm dần rồi essay_id tăng dần'} for r in candidates])
write('05_ca_loi/README.md',f'''# Phạm vi bằng chứng đọc
Đã có {len(reading)} ID duy nhất có ghi nhận đọc cũ, trong đó {qual_large} ca RF sai lớn (tính từ cột điểm thật và dự đoán của reports/week9/t4_reading_summary.csv). Bộ này là kết quả nhóm tiếp nhận với công cụ hỗ trợ, không phải hai lượt người đọc độc lập (docs/llm_disclosure.md, Week 9).
Mẫu đếm lỗi có {len(gec)} ID: 36 random36 + 32 week9; không cộng 68 với 32 vì có trùng (reports/week10/gec_part_a_68.csv). Số đếm lỗi không tự tạo ra phân tích nguyên nhân cho 10 ca.
Năm bài đã chốt có bằng chứng cũ, không phải năm bài có hai phiếu độc lập hợp lệ. Theo docs/du_lieu_interview.md, cả hai phiếu mới còn nguyên và 92 ô trả lời/xác nhận trống; 0/5 cặp đủ điều kiện so sánh. Không mở workbook có văn bản trong nhiệm vụ này.
Yêu cầu “bản B có điền sẵn”: chưa có nguồn xác nhận cho bản B cũ; không diễn giải thành đã đọc độc lập. Các ô B và nguyên nhân giữ trống.
Rubric tối thiểu 10 ca: theo yêu cầu người dùng; bản gốc rubric ngày 26/10/2026 chưa có nguồn trong các file đã xác nhận. Hiện có hơn 10 ghi nhận đọc cũ, nhưng tính độc lập và việc đáp ứng đúng bản rubric gốc vẫn cần kiểm chứng.
Quy tắc đề xuất bổ sung: từ 276 ca cùng sai OOF, loại toàn bộ ID trong bộ đọc cũ; xếp D giảm dần, hòa essay_id chuỗi tăng dần, lấy 5 đầu. File ứng viên chỉ là lịch đọc dự kiến. Thành viên tự đọc và tự điền mẫu 10 ca, không coi ứng viên là ca đã phân tích.
''')
timeline='''# Lịch sử dùng Test: chỉ trích hồ sơ đã lưu
Kết quả sau nhiều lần chọn là thăm dò.

| Mốc UTC | Sự kiện | Bằng chứng |
|---|---|---|
| Lần 1, báo cáo tuần 9; ngày chạy đầu chưa xác định | D = 47/208, N=2518, k=504; exact p=0,1883246714 | reports/week9/RESULTS_week9.md, Task 0; chronology không xác định được ngày truy cập đầu |
| 19/10/2026 05:41:08 UTC | Commit khóa 4e381150edf08d49a134505e669058f1e0d27b48 | git show -s --format=%cI 4e38115 ghi 12:41:08 +07:00; đổi sang UTC |
| 26/10/2026 07:14:53 UTC | Dừng khớp dự đoán Vocabulary: 2015 dòng, max lệch 4,995115432393504e-12 > atol 1e-12; chưa tính tín hiệu | log STOPPED; commit b32ad4e35d0fc9546dc07d090526a59518641536 |
| Sau lần dừng, chưa có giờ riêng được xác nhận | Chẩn đoán chỉ trên development; định dạng lưu %.12g giải thích sai số; sửa atol=1e-11, rtol=0 | RESULTS_tree_spread_second_use.md, Sự cố lần chạy đầu |
| Sau sửa dung sai, trước 07:27 UTC; chưa có giờ riêng | Chốt chặn từ chối vì log tồn tại; không mở Test ở lần gọi này | RESULTS_tree_spread_second_use.md, Sự cố chốt chặn; script hash trung gian 15bd8ee6c5d2611fd09bba32202e86cdb8398e3d433845bd55f89a1537e75ec6 |
| 26/10/2026 07:27:32 UTC | Hoàn thành: cây 55/208, kỳ vọng 41,6330421; p=0,01158570685 so ngẫu nhiên | log _attempt2 COMPLETED, pre_signal_checks PASS; run commit cdc0a6a871d1f7ae9458f920157853159d6f9318; result commit 97159a6b9a10e46b881b8e1a66cd278171dff4f6 |

File khóa docs/signal_lock_tree_spread.md SHA256:
`d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca`.
Script cuối scripts/tree_spread_official_test_second_use.py SHA256:
`cc7bdd6efd8c0cf23a4f6dbd5673e17a5c8501aaf72e77fb0b99e96090b31e05`.
Hai hash đã kiểm lại trực tiếp khi dựng gói; không chạy script đánh giá Test.
Sự cố đầu dùng script hash df70177723d5fdeee72e1dc65a55fc242e19fbcc9b6ad2a1052cd1fda839240b.
Nguồn toàn dòng thời gian: reports/week9/RESULTS_tree_spread_second_use.md và hai log JSON; các trích số an toàn nằm trong 08_tai_lap/nguon.
Chênh 55-47=8 là số đếm Test, chưa có kiểm định ghép cặp so với D. Khoảng +8 [-11,27] là của development, không gán cho Test.
'''
write('06_lich_su_dung_test.md',timeline)
write('08_tai_lap/nguon/test_log_summary.json',json.dumps({'completed':{k:log[k] for k in ['status','run_commit','result'] if k in log},'stopped':{k:stopped[k] for k in ['status','run_commit','failure'] if k in stopped},'source_completed':'reports/week9/tree_spread_official_test_second_use_log_attempt2.json','source_stopped':'reports/week9/tree_spread_official_test_second_use_log.json'},ensure_ascii=False,indent=2))
csvout('09_dong_gop_va_ai/mau_nhat_ky_dong_gop.csv',[],['ngày','câu hỏi','giả định trước khi chạy','kết quả','thay đổi'])
for member in ['Nam','Giang','Linh']:
 write(f'09_dong_gop_va_ai/{member}/README.md','# Mẫu trống - thành viên tự điền\n\nMột quyết định mình sở hữu: \n\nBằng chứng: \n\nCách kiểm tra khi dùng AI: \n')
write('09_dong_gop_va_ai/khai_bao_ai.md','''# NHÁP TRỐNG - cần từng thành viên xác nhận
Nhóm công cụ cần kiểm kê: agent mã; trợ lý viết. Tên công cụ/model: ___
Mục đích thực tế: ___
Artifact và phạm vi hỗ trợ: ___
Người kiểm chứng và cách kiểm chứng: ___
Khoảng trống lịch sử cần bổ sung: ___
Nguồn hiện có để đối chiếu: docs/llm_disclosure.md có Working Record và mục Week 9, nhưng không đủ nhật ký chi tiết mọi lần dùng. Đây không phải xác nhận lịch sử hay đóng góp của bất kỳ thành viên nào.
Không ký, không điền giờ hoặc quyết định thay thành viên.
''')

pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold')
NAVY=colors.HexColor('#17334b');TEAL=colors.HexColor('#087e8b');GREY=colors.HexColor('#edf0f2')
W,H=960,540
def para(c,text,x,y,width,size=20,color=NAVY):
 style=ParagraphStyle('p',fontName='Arial',fontSize=size,leading=size*1.32,textColor=color)
 p=Paragraph(text,style);_,height=p.wrap(width,1000);p.drawOn(c,x,y-height);return y-height
def base(c,title,num,sub='NHÓM 03 / ELLIPSE / GÓI PHỎNG VẤN OFFLINE'):
 c.setFillColor(colors.white);c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(TEAL);c.rect(0,H-12,W,12,fill=1,stroke=0)
 para(c,sub,40,H-32,880,11,TEAL);para(c,title,40,H-65,880,29)
 c.setFont('Arial',10);c.setFillColor(NAVY);c.drawRightString(W-40,20,str(num))
def footer(c,text):para(c,text,40,63,875,10)
def bullets(c,items,y=420,size=22):
 for item in items:y=para(c,'• '+item,48,y,862,size)-19
 assert y>75,(items,y)
def table(c,data,widths,x=40,y=410,size=15):
 style=ParagraphStyle('cell',fontName='Arial',fontSize=size,leading=size*1.3,textColor=NAVY)
 cells=[[Paragraph(html.escape(str(v)).replace('\n','<br/>'),style) for v in row] for row in data]
 t=Table(cells,colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GREY),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d7e1e7')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LEFTPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,0),1,colors.white),('INNERGRID',(0,0),(-1,-1),1,colors.white)]))
 _,h=t.wrap(sum(widths),1000);assert y-h>80,(y,h);t.drawOn(c,x,y-h);return y-h
main_data=[['Tập / tín hiệu','N','K sai','Đọc k','Bắt C/K','Ngẫu nhiên','Tỷ lệ nền','Nguồn']]+[[r['scope'],r['N'],r['K'],r['budget'],f"{r['caught']}/{r['K']}",f"{r['random']:.2f}",f"{100*r['base_rate']:.2f}%",f'S{[1,1,2,3,4][j]}'] for j,r in enumerate(main)]
main_foot='S1: reports/week9/t3_pooled.csv (prompt_disjoint). S2: RESULTS_week9.md / Week 9b. S3: cùng RESULTS / Task 0. S4: tree_spread_official_test_second_use_log_attempt2.json / result. Các nguồn nằm dưới reports/week9; trích số offline tại 08_tai_lap/nguon.'
model_data=[['Mô hình','MAE V / G','Giả định và loss','Vai trò']]+[[m['model'],f"{m['MAE_V']:.3f} / {m['MAE_G']:.3f}" if m['MAE_V']!='' else 'Chưa có nguồn',m['assumption']+'; '+m['training_loss'],m['why']] for m in models]
model_foot='Nguồn: reports/week9/t3_regression.csv, prompt_disjoint / pooled; cấu hình: docs/signal_lock_tree_spread.md và RESULTS_week9.md / Week 9b. MAE là sai số tuyệt đối trung bình; khác loss huấn luyện. Mean baseline cùng phép chia: chưa có nguồn cho MAE.'
slides=[
 ('Giáo viên đọc lại bài nào trước?',[
 'Sau khi bài viết hoàn tất, dự đoán hai điểm: Từ vựng và Ngữ pháp; ưu tiên giáo viên đọc lại 20% bài.',
 'Một dòng là một bài, nhận diện bằng essay_id. Đây là dự đoán điểm bài viết, không đo toàn bộ năng lực người học.',
 '“Sai lớn”: max(|RF_V − y_V|, |RF_G − y_G|) ≥ 1 điểm. D = max(|RF_V − Ridge_V|, |RF_G − Ridge_G|).',
 'Câu hỏi: bất đồng giữa hai máy có tìm được bài RF sai lớn tốt hơn đọc ngẫu nhiên cùng ngân sách?'],
 'Nguồn: docs/data_card.md; docs/signal_lock_tree_spread.md / Signal definition; reports/week9/RESULTS_week9.md / Task 3.'),
 ('Một bài đi từ đặc trưng đến nhãn',[
 'ELLIPSE v1.0: bài viết học sinh lớp 8–12; điểm tổng hợp từ người chấm, thang 1–5, bước 0,5. Dùng hai đích V/G.',
 'Theo data card: CC BY-NC-SA 4.0; cho phép phân phối kèm điều kiện. Quyền hiển thị văn bản từng bài và xử lý riêng tư: chưa rõ.',
 'Nguồn gốc: 3.911 train + 2.571 Test; development đủ điều kiện = 3.812. Các tổng lấy từ hồ sơ, không mở corpus/Test.',
 '0514D25768A0: 328 từ, 22 câu → RF V=3,201; Ridge V=3,407 → nhãn V=2; RF sai lớn. Xem PNG truy vết.'],
 'Nguồn: docs/data_card.md; reports/week9/t3_eligible_development.csv; docs/phieu_luyen_mot_bai_development.md; CSV và hash trong gói.'),
 ('Hai cách chia, hai vai trò đánh giá',[],
 'Nguồn: docs/split_and_leakage_protocol.md; reports/week9/t3_fold_composition.csv; RESULTS_week9.md / Week 9b. Xem sơ đồ riêng và ghi chú phạm vi.'),
 ('Baseline và hai họ mô hình',[],model_foot),
 ('Cùng ngân sách đọc 20%, cùng cách phá hòa',[],main_foot),
 ('Kiểm tra đã lưu cho thấy điều gì?',[
 'Nguồn thứ hai: TF-IDF bắt 81, MiniLM bắt 93 so D cũ 88 trên 386 lỗi. MiniLM chưa chứng minh hơn D: chênh +5, CI [−16,025; 27].',
 'Đếm lỗi trên 36 bài random: người đọc 7,33; công cụ cũ 1,24 (ước lượng). GECToR đếm 14,33, không gần người hơn ở mẫu này.',
 'Hệ quả diễn giải: chưa coi đồng thuận là đúng; chưa coi công cụ đếm là nhãn chuẩn. “Quyết định nhóm đổi”: để trống cho thành viên xác nhận.',
 'Cây so D: +8 [−11; 27] ở development. Bootstrap 44 cụm đề, 2.000 lượt, seed 42; giữ hàng đợi; chưa chứng minh hơn D.'],
 'Nguồn: reports/week10/RESULTS_week10.md / B2 concise tables, Exploratory Part A; reports/week9/RESULTS_week9.md / paired tree spread. Quyết định cá nhân: mẫu trống.'),
 ('Ca lỗi: hai máy gần nhau vẫn cùng sai',[
 '0514D25768A0: 328 từ; mtld=87,872; mattr=0,807; tỷ lệ câu phức=0,591. Chỉ mô tả đặc trưng, không gán nguyên nhân.',
 'V / G: nhãn 2 / 2; RF 3,201 / 2,785; Ridge 3,407 / 2,993; MiniLM 3,255 / 2,819.',
 'D=0,208493; hạng 174/769, ngoài 154 bài được đọc. RF và Ridge cùng sai lớn ở Từ vựng.',
 '150 từ đầu: người đọc 9 lỗi; công cụ cũ ước lượng 3,20; GECToR 12 chỉnh sửa ngữ pháp. Không coi chỉnh sửa là lỗi chuẩn.'],
 'Nguồn: docs/phieu_luyen_mot_bai_development.md; reports/week9/t3_heldout_predictions.csv; reports/week10/b2_oof.csv và gec_part_a_68.csv, đúng essay_id.'),
 ('Giới hạn và phần thành viên cần tự xác nhận',[
 'Test lần đầu được báo cáo ở tuần 9; ngày truy cập đầu chưa xác định. 26/10: dừng 07:14 UTC; chốt chặn từ chối; hoàn thành 07:27 UTC.',
 'Kết quả sau nhiều lần chọn là thăm dò. Test cây 55/208 có p=0,0116 so ngẫu nhiên; không phải p chứng minh hơn D.',
 'Thiếu: hai phiếu độc lập hợp lệ, phân rã đúng mô hình từng fold, MAE mean cùng phép chia, rubric gốc. Số 15/16,6 đã có nguồn ở bảng 3.4 bổ sung.',
 'Đóng góp, quyết định, giờ và khai báo AI: thành viên tự điền mẫu. Hồ sơ AI trước đây chưa đủ nhật ký chi tiết.'],
 'Nguồn: reports/week9/RESULTS_tree_spread_second_use.md; docs/du_lieu_interview.md; docs/llm_disclosure.md. Thiếu nguồn được liệt kê ở 08_tai_lap/THIEU_VA_DOI_CHIEU.md.')]
diagram_lines=[
 'Chia gốc: Official train 3.911 → model-train 3.128 + Validation 783. Sau cổng riêng tư: development 3.812; Validation đủ điều kiện 762.',
 'Model-train: fit trung vị điền thiếu; Ridge fit thêm StandardScaler; CV để chọn tham số. Validation chọn/cố định cấu hình trước đánh giá chính.',
 'Thăm dò mới trên development: GroupKFold(5) theo normalised_prompt; mỗi lượt fit chỉ bốn fold còn lại. Fold giữ lại không có đề trùng phần fit.',
 'Official Test gốc 2.571; đủ điều kiện 2.518. Chỉ dùng sau chốt lựa chọn; đã dùng lại nên kết quả là thăm dò. Gói này chỉ trích kết quả tổng hợp đã lưu.'
]
def draw_diagram(c):
 table(c,[['CHIA GỐC','THĂM DÒ DEVELOPMENT','TEST ĐÃ LƯU'],['Model-train 3.128\nFit + CV\n↓ chọn cấu hình','3.812 bài đủ điều kiện\nGroupKFold(5) theo đề','2.518 đủ điều kiện\n208 RF sai lớn'],['Validation 783\n762 đủ điều kiện\nChọn và chốt mô hình','4 fold → fit median/scaler/model\n1 fold → dự đoán giữ lại\nKhông dùng nhãn giữ lại để fit','Sau chốt lựa chọn → Test\nD 47/208; cây 55/208\nKhông mở Test khi dựng gói']],[280,310,290],y=430,size=17)
 para(c,'Thời điểm dự đoán: sau khi hoàn tất bài, trước giáo viên đọc lại. Điểm thật chỉ dùng để đánh giá khi đã có nhãn.',48,180,865,19)
 para(c,'Hai cách chia này khác nhau: fold OOF theo đề không phải cv_fold của bảng chia gốc. Mô hình Phase 6 đã lưu cũng khác mô hình OOF.',48,118,865,16)
c=canvas.Canvas(str(P/'01_trinh_chieu.pdf'),pagesize=(W,H))
for j,(title,items,src) in enumerate(slides,1):
 base(c,title,j)
 if j==3:draw_diagram(c)
 elif j==4:table(c,model_data,[110,150,365,255],y=420,size=16);para(c,'TF-IDF / MiniLM: nguồn đối chiếu thăm dò, không thay hai họ mô hình chính.',48,155,860,19)
 elif j==5:
  table(c,main_data,[208,70,70,80,105,110,137,100],y=420,size=15)
  para(c,'K = số lỗi của nhãn đang xét; k = ceil(0,2N) từng fold. Hòa: essay_id chuỗi tăng dần. +8 [−11; 27] là CI theo cụm đề trên development, không phải Test.',48,164,865,17)
 else:bullets(c,items,size=21 if j in [2,6,8] else 22)
 footer(c,src);c.showPage()
c.save()
write('01_trinh_chieu_nguon.md','\n\n'.join(f'## Slide {j}: {t}\n\n'+'\n'.join('- '+x for x in (diagram_lines if j==3 else items))+ ('\n\n'+json.dumps(models if j==4 else main,ensure_ascii=False,indent=2) if j in [4,5] else '')+'\n\n'+src for j,(t,items,src) in enumerate(slides,1)))
for rel,title,data,widths,foot in [('04_bang_ket_qua/bang_chinh.pdf','Bảng kết quả chính',main_data,[208,70,70,80,105,110,137,100],main_foot),('04_bang_ket_qua/bang_mo_hinh.pdf','Baseline và hai họ mô hình',model_data,[110,150,365,255],model_foot)]:
 c=canvas.Canvas(str(P/rel),pagesize=(W,H));base(c,title,1);table(c,data,widths,y=415,size=16 if 'mo_hinh' in rel else 15)
 para(c,'Ngân sách và cách phá hòa cố định; kết quả development/Test dùng lại đều cần đọc cùng giới hạn. Chi tiết nguồn từng hàng trong CSV cùng tên.',48,140,865,18);footer(c,foot);c.save()
c=canvas.Canvas(str(P/'03_so_do_chia.pdf'),pagesize=(W,H));base(c,'Sơ đồ chia và thời điểm dự đoán',1);draw_diagram(c);footer(c,slides[2][2]);c.save()
write('03_so_do_chia_ghi_chu.md','# Sơ đồ và phạm vi\n\n'+'\n\n'.join(diagram_lines)+'\n\nNguồn: docs/split_and_leakage_protocol.md; reports/week9/t3_fold_composition.csv; reports/week9/RESULTS_week9.md.\n')
random36=[r for r in gec if r['sample_group']=='random36']
assert len(random36)==36
mean_reader=sum(float(r['reader']) for r in random36)/36;mean_old=sum(float(r['LT_estimate']) for r in random36)/36
notebook=[['Số cần nhớ','Ý nghĩa và nguồn'],['55/208; E=41,63; p=0,0116','Test dùng lại, cây; log _attempt2 / result'],['47/208; p=0,1883','Test D đã lưu; RESULTS_week9.md / Task 0'],['88/386; E=77,36','Development D; t3_pooled.csv / prompt_disjoint'],['276/386 ≈ 71,5%','RF sai cũng Ridge sai; t3_pooled.csv / A1, A3'],[f'{mean_reader:.2f} so {mean_old:.2f} lỗi','36 random36; gec_part_a_68.csv; người / công cụ cũ ước lượng'],['15,0 / 16,6 trên 100 lỗi chung','35/233 và 36/217; RESULTS_week10.md / A3; bảng 3.4 bổ sung'],['Khóa SHA256: d2eabcb7…8eca','docs/signal_lock_tree_spread.md; hash đầy đủ ở 06_lich_su_dung_test.md']]
c=canvas.Canvas(str(P/'10_so_tay_so_lieu.pdf'),pagesize=(W,H));base(c,'Sổ tay số liệu - một trang',1);table(c,notebook,[330,550],y=420,size=15);footer(c,'Đường dẫn nguồn ở reports/week9, trừ gec_part_a_68.csv thuộc reports/week10. Bản trích offline ở 08_tai_lap/nguon. p là so ngẫu nhiên, không phải so D.');c.save()

FONT='C:/Windows/Fonts/arial.ttf';BOLD='C:/Windows/Fonts/arialbd.ttf'
def text_image(rel,title,lines):
 font=ImageFont.truetype(FONT,24);bold=ImageFont.truetype(BOLD,31)
 # Wrap by pixel width; preserve source and long hashes safely.
 wrapped=[]
 for line in lines:
  current=''
  for word in str(line).split(' '):
   trial=(current+' '+word).strip()
   if font.getlength(trial)>1420 and current:wrapped.append(current);current=word
   else:current=trial
  wrapped.append(current)
 im=Image.new('RGB',(1536,max(500,145+38*len(wrapped))),'#f3f5f7');d=ImageDraw.Draw(im)
 d.rectangle((0,0,1536,14),fill='#087e8b');d.text((48,40),title,font=bold,fill='#17334b')
 for j,line in enumerate(wrapped):d.text((48,110+j*38),line,font=font,fill='#17334b')
 im.save(P/rel)
for essay,r in samples.items():
 a=arith['rows'][essay]
 text_image(f'02_mau_truy_vet/{essay}.png',f'{essay} | Đặc trưng → dự đoán OOF → nhãn',[
  f"Đặc trưng: word_count={r['word_count']}; sentence_count={r['sentence_count']}; mattr={float(r['mattr']):.6f}",
  f"mtld={float(r['mtld']):.6f}; mean_word_frequency={float(r['mean_word_frequency']):.6f}; complex_sentence_ratio={float(r['complex_sentence_ratio']):.6f}",
  f"RF V/G: {float(r['RF_V']):.6f} / {float(r['RF_G']):.6f}; Ridge: {float(r['Ridge_V']):.6f} / {float(r['Ridge_G']):.6f}",
  f"MiniLM: {float(r['MiniLM_V']):.6f} / {float(r['MiniLM_G']):.6f} → Nhãn V/G: {r['y_V']} / {r['y_G']}",
  f"D={r['D']:.9f}; hạng={r['D_rank']}/{r['fold_n']}; ngân sách={r['budget']}; không được D chọn; cả hai máy sai lớn.",
  'Nguồn: t3_eligible_development.csv + t3_heldout_predictions.csv (reports/week9); b2_oof.csv (reports/week10).',
  'PHÉP TÍNH RIÊNG: mô hình Phase 6 đã lưu, không phải mô hình OOF ở trên:',
  f"Ridge V = intercept {a['ridge_vocabulary']['intercept']:.9f} + Σ(hệ số × z) = {a['ridge_vocabulary']['reconstructed']:.9f}",
  f"RF V = Σ dự đoán 300 cây / 300 = {a['random_forest_vocabulary']['reconstructed']:.9f}",
  'Nguồn hệ số/cây: outputs/phase6/*.joblib; bốn hash khớp; xem CSV terms, trees và saved_model_arithmetic.json.',
  'Phân rã đúng dự đoán OOF: để trống vì chưa có mô hình từng fold được xác nhận. Không huấn luyện lại.',
  'Bài thứ hai thuộc model_train gốc: phép tính Phase 6 là in-sample; bảng OOF vẫn là held-out.' if essay==IDS[1] else 'Bài này thuộc Validation gốc; hai pipeline Phase 6 và OOF có phần fit khác nhau.' ])
for script in ['check_d_88_of_386.py','check_synthetic_ranking.py']:
 start=time.perf_counter();res=subprocess.run([sys.executable,str(P/'07_kiem_tra_offline'/script)],capture_output=True,text=True,encoding='utf-8',check=True);assert time.perf_counter()-start<10
 write('07_kiem_tra_offline/'+script.replace('.py','_output.txt'),res.stdout)
 text_image('07_kiem_tra_offline/'+script.replace('.py','_output.png'),script+' | ảnh kết xuất stdout thực tế',res.stdout.splitlines())
 print(res.stdout)
doc=fitz.open(P/'03_so_do_chia.pdf');doc[0].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(P/'03_so_do_chia.png');doc.close()
write('08_tai_lap/REPRODUCE.md','''# Tái lập và phạm vi thực thi
Gói hiển thị hoàn toàn offline; xem HTML/PDF/PNG không cần môi trường Python.
Hai kiểm tra tính toán chỉ cần Python standard library:
```
python interview_pack/07_kiem_tra_offline/check_d_88_of_386.py
python interview_pack/07_kiem_tra_offline/check_synthetic_ranking.py
```
Có thể đối chiếu nguồn gốc bằng cách truyền đúng reports/week9/t3_heldout_predictions.csv cho script đầu; chỉ lọc prompt_disjoint.
Bản kèm development_predictions.csv chỉ chứa ID, fold, nhãn và dự đoán development; không có văn bản, prompt hoặc thông tin cá nhân.
K là số nhãn sai lớn; k là ngân sách, tính ceil(0,20N) từng fold. Kỳ vọng cộng k_f*K_f/N_f. Không gộp thành một phép lấy 20% toàn cục.

## Nguồn sinh bảng đã lưu (ghi để truy xuất, KHÔNG chạy lại trong nhiệm vụ này)
- Bảng D: `.venv/Scripts/python.exe scripts/week9/t3_evaluate.py --capture`; nguồn RESULTS_week9.md / Task 3, Producer. Dự đoán lưu do quy trình huấn luyện trước tạo; không gọi lại quy trình có fit trong nhiệm vụ này.
- Cây 96/386: `.venv/Scripts/python.exe -u scripts/week9b/tree_spread_oof.py --append` (nguồn RESULTS_week9.md). Có fit lại fold, ngoài phạm vi được phép hiện tại.
- Khoảng ghép cặp: `.venv/Scripts/python.exe -u scripts/week9b/paired_tree_spread.py --append` (nguồn cùng RESULTS). Bootstrap 44 normalised_prompt, 2000 lượt, seed 42; giữ hàng đợi, không rerank. CI có điều kiện trên mô hình OOF đã fit.
- Test: chỉ trích log/RESULTS đã lưu; không chạy lệnh đánh giá Test, không cần có đầu vào Test để dùng gói.

## Môi trường suy luận development đã kiểm tra
Python 3.14.5; scikit-learn 1.9.1; NumPy 2.4.6; joblib 1.6.0; seed cấu hình 42. Phiên bản khớp hồ sơ RESULTS_tree_spread_second_use.md và môi trường .venv tại lúc dựng gói.
`extract_saved_models.py` dùng joblib/NumPy; cần reports/week9/t3_eligible_development.csv, outputs/phase6/feature_schema.json và bốn model Ridge/RF ở outputs/phase6. Chỉ chọn hai ID source_partition=official_train; kiểm hash trước/sau; không gọi fit. Kết quả là phép tính Phase 6 riêng, không thay dự đoán OOF.
`build_pack.py` dùng reportlab, Pillow, PyMuPDF; đọc allowlist cố định trong script. Fonts Arial tại C:/Windows/Fonts. Mọi script mới nằm trong gói.

## File tối thiểu để kiểm tra và truy xuất
- 07_kiem_tra_offline/development_predictions.csv và hai script cùng thư mục.
- Nguồn dự đoán gốc reports/week9/t3_heldout_predictions.csv; ID/fold theo reports/week9/t3_fold_composition.csv, bản trích trong nguon/.
- reports/week9/t3_pooled.csv, t3_regression.csv, RESULTS_week9.md.
- reports/week9/RESULTS_tree_spread_second_use.md và hai log JSON (không phải dữ liệu Test).
- reports/week10/gec_part_a_68.csv, b2_oof.csv, RESULTS_week10.md; chỉ cần khi dựng lại gói.
- docs/data_card.md, signal_lock_tree_spread.md, split_and_leakage_protocol.md, phieu_luyen_*.md, du_lieu_interview.md, llm_disclosure.md.
Chi tiết hash nguồn đọc thực tế ở SOURCES.sha256. Không sao chép corpus, workbook có bài luận hoặc model vào gói.
''')
write('08_tai_lap/THIEU_VA_DOI_CHIEU.md',f'''# Thiếu và đối chiếu nguồn
- 88/386 và 77,362908: khớp phép tính từ dự đoán đã lưu; ngân sách tổng 764.
- 44/276 và kỳ vọng 55,321857: khớp t3_pooled; 276 là nhãn cùng sai trong toàn bộ 3812 bài, không xếp hạng chỉ trên 276 bài đã biết là dương tính.
- 96/386, +8 [-11,27]: đã có nguồn; CI lấy lại 44 cụm đề (2000 lượt seed 42), hàng đợi cố định, không refit/rerank. Không gán CI này cho Test.
- 55/208, 47/208: khớp log/RESULTS; p 0,0116 so ngẫu nhiên, không phải so D. Ngày dùng Test đầu tiên: chưa xác định; tuần 9 là mốc báo cáo/tái kiểm.
- 7,33 và 1,24: tái tính từ {len(random36)} dòng random36, kết quả {mean_reader:.9f} và {mean_old:.9f}. Công cụ cũ là ước lượng, không đếm đoạn trực tiếp.
- ĐÃ CÓ NGUỒN cho 15,0 và 16,6 trên 100 bài trong nhóm cùng sai: 100*35/233 và 100*36/217. Nguồn reports/week10/RESULTS_week10.md / B1 A3_new và B2 A3_RF_B2; xem 12_mang_theo/bang_3_4.csv. Không phải trên 100 bài được đọc.
- MAE mean baseline trong cùng GroupKFold: chưa có nguồn trong t3_regression; không lấy một bảng chia khác để thế vào.
- “5 bài đọc hai bản”: nguồn hiện tại chỉ chứng minh ghi nhận cũ và hai phiếu mới còn trống. 0 cặp đủ điều kiện độc lập. Bản B cũ điền sẵn: chưa có nguồn được xác nhận. Không tạo so sánh giả.
- Ghi nhận cũ: {len(reading)} ca, {qual_large} RF sai lớn. Không tự xác nhận đủ rubric mới chỉ từ số đếm; mẫu 10 ca và danh sách ứng viên cần thành viên thực hiện.
- Rubric gốc MLA Final Project Requirements and Rubric ngày 26/10/2026: chưa có nguồn gốc đã xác nhận trong nguồn được đọc. Gói dựng theo yêu cầu đính kèm; docs/instructor_requirements.md là tổng hợp có ghi cần xác minh đề gốc.
- Điều kiện ELLIPSE theo data card: CC BY-NC-SA 4.0 và cho phép tái phân phối có điều kiện. Quyền trình chiếu văn bản từng bài chưa rõ; không kèm bài luận.
- Phân rã đúng dự đoán OOF: thiếu mô hình riêng từng fold được xác nhận. Đã cung cấp phân rã từ bốn model Phase 6 có hash, ghi riêng scope; không coi là cùng mô hình.
- Nhật ký quyết định/đóng góp/AI: mẫu trống; lịch sử chi tiết chưa đầy đủ, cần thành viên xác nhận.
''')
qa=[]
for path in sorted(P.rglob('*.pdf')):
 doc=fitz.open(path)
 for n,page in enumerate(doc):
  rel=path.relative_to(P).as_posix();filename=rel.replace('/','__').replace('.pdf',f'_page{n+1:02}.png')
  pix=page.get_pixmap(matrix=fitz.Matrix(1.3,1.3));pix.save(P/'_kiem_tra/hien_thi'/filename)
  assert '\ufffd' not in page.get_text()
  qa.append({'file':rel,'page':n+1,'render':filename,'width':pix.width,'height':pix.height,'status':'rendered; requires visual inspection'})
 doc.close()
csvout('_kiem_tra/hien_thi/pdf_pages.csv',qa)
# Contact sheets: show every requested PDF page and PNG with its exact filename.
visuals=sorted([p for p in P.rglob('*.png') if not p.is_relative_to(P/'_kiem_tra')])+[P/'_kiem_tra/hien_thi'/r['render'] for r in qa]
for batch in range(0,len(visuals),6):
 paths=visuals[batch:batch+6];im=Image.new('RGB',(1800,3*590),'white');d=ImageDraw.Draw(im)
 for j,path in enumerate(paths):
  pic=Image.open(path).convert('RGB');pic.thumbnail((870,520));x=(j%2)*900;y=(j//2)*590
  d.text((x+12,y+8),path.relative_to(P).as_posix(),font=ImageFont.truetype(FONT,17),fill='black');im.paste(pic,(x+12,y+45))
 im.save(P/f'_kiem_tra/hien_thi/contact_{batch//6+1:02}.png')
write('08_tai_lap/SOURCES.sha256',''.join(f'{h}  {p}\n' for p,h in sorted(SOURCES.items())))
links=[('Hàng dữ liệu và nhãn','02_mau_truy_vet/0514D25768A0.png'),('Baseline và dự đoán','04_bang_ket_qua/bang_mo_hinh.pdf'),('Một giả định','01_trinh_chieu.pdf#page=4'),('Kết quả so baseline','04_bang_ket_qua/bang_chinh.pdf'),('Một ca lỗi','02_mau_truy_vet/0514D25768A0.png'),('Việc của chính bạn','09_dong_gop_va_ai/'),('Nhóm tự kiểm tra kết quả nào, quyết định nào đổi?','01_trinh_chieu.pdf#page=6'),('Chỉ giữ một bảng và một ca lỗi?','04_bang_ket_qua/bang_chinh.pdf')]
write('00_START_HERE.html','''<!doctype html><html lang="vi"><meta charset="utf-8"><title>Nhóm 03 - Interview pack</title><style>body{font:18px Arial,sans-serif;color:#17334b;max-width:1100px;margin:30px auto;padding:0 20px}h1{font-size:34px}table{border-collapse:collapse;width:100%}td,th{padding:10px 16px;background:#edf0f2;text-align:left;border:2px solid white}a{color:#087e8b}small{font-size:14px}.note{padding:14px;background:#fff0d6}p{line-height:1.5}</style><h1>Nhóm 03 · ELLIPSE</h1><p>Gói phỏng vấn offline · Mở trực tiếp file, không cần chạy mô hình.</p><p><a href="01_trinh_chieu.pdf">MỞ 8 SLIDE TRÌNH CHIẾU</a> · <a href="10_so_tay_so_lieu.pdf">Sổ tay một trang</a> · <a href="03_so_do_chia.png">Sơ đồ chia</a></p><table><tr><th>Thầy hỏi gì?</th><th>Mở file nào?</th></tr>'''+''.join(f'<tr><td>{html.escape(q)}</td><td><a href="{url}">{html.escape(url)}</a></td></tr>' for q,url in links)+'''</table><p>Nếu giữ một bảng và một ca: bảng chính cùng ngân sách và bài 0514D25768A0 cho thấy hai máy gần nhau vẫn cùng sai. Đây là gợi ý luyện tập; thành viên tự nhận quyết định của mình.</p><p class="note">Cần hoàn thiện: phiếu độc lập, mẫu 10 ca, đóng góp và AI. Số 15 / 16,6 đã có nguồn ở bảng 3.4 bổ sung; MAE mean cùng phép chia còn thiếu. <a href="08_tai_lap/THIEU_VA_DOI_CHIEU.md">Xem mọi khoảng trống</a>.</p><p><a href="06_lich_su_dung_test.md">Lịch sử Test</a> · <a href="07_kiem_tra_offline/check_d_88_of_386_output.png">Kiểm tra 88/386</a> · <a href="07_kiem_tra_offline/check_synthetic_ranking_output.png">Ví dụ tổng hợp</a> · <a href="08_tai_lap/REPRODUCE.md">Tái lập</a> · <a href="FILE_LIST.md">Toàn bộ file</a></p><small>Không có bài luận hoặc thông tin cá nhân trong gói. Kết quả sau nhiều lần chọn là thăm dò. Nguồn số liệu nằm ngay trong tài liệu và 08_tai_lap/nguon.</small></html>''')
print(f'BUILT: {P}; legacy read={len(reading)}, RF-large={qual_large}; PDFs=5; PDF pages={len(qa)}; visual assets={len(visuals)}')

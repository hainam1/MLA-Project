"""Add sections 11-15 from saved, text-free development records and reports.
No model loading, fitting, Test inputs or corpus access.
"""
from pathlib import Path
import csv, io, json, math, hashlib, html, subprocess, sys, re
from statistics import mean, pstdev
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
import fitz

sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parents[1];R=P.parent
EXPECTED='d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca'
lock=R/'docs/signal_lock_tree_spread.md'
assert hashlib.sha256(lock.read_bytes()).hexdigest()==EXPECTED,'STOP: lock hash mismatch'
# Correct stale missing-source notices in the base generator; no committed source is edited.
builder=P/'08_tai_lap/build_pack.py';s=builder.read_text(encoding='utf-8')
s=s.replace('MAE mean cùng phép chia, nguồn 15 và 16,6 trên 100 bài, rubric gốc.','MAE mean cùng phép chia, rubric gốc. Số 15/16,6 đã có nguồn ở bảng 3.4 bổ sung.')
s=s.replace("['15 và 16,6 trên 100 bài','Chưa có nguồn; không biết mẫu số/định nghĩa nên không sử dụng']","['15,0 / 16,6 trên 100 lỗi chung','35/233 và 36/217; RESULTS_week10.md / A3; bảng 3.4 bổ sung']")
s=s.replace('- 15 và 16,6 trên 100 bài: chưa có nguồn xác định được đơn vị, mẫu số và phép đo. Để trạng thái thiếu, không dùng làm kết quả.','- ĐÃ CÓ NGUỒN cho 15,0 và 16,6 trên 100 bài trong nhóm cùng sai: 100*35/233 và 100*36/217. Nguồn reports/week10/RESULTS_week10.md / B1 A3_new và B2 A3_RF_B2; xem 12_mang_theo/bang_3_4.csv. Không phải trên 100 bài được đọc.')
s=s.replace('Số 15 / 16,6 trên 100 bài và MAE mean cùng phép chia chưa có nguồn.','Số 15 / 16,6 đã có nguồn ở bảng 3.4 bổ sung; MAE mean cùng phép chia còn thiếu.')
builder.write_text(s,encoding='utf-8')
if '--skip-base' not in sys.argv:
 subprocess.run([sys.executable,str(builder)],check=True)
def write(rel,text):
 p=P/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def getcsv(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def outcsv(rel,rows,fields=None):
 path=P/rel;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fields or list(rows[0]));w.writeheader();w.writerows(rows)
src='reports/week10/RESULTS_week10.md';report=(R/src).read_text(encoding='utf-8');lines=report.splitlines()
def block(anchor,header):
 start=report.index(header,report.index(anchor));ls=report[start:].splitlines();body=[]
 for line in ls:
  if not line.strip() or len(next(csv.reader([line])))!=len(next(csv.reader([header]))):break
  body.append(line)
 return list(csv.DictReader(io.StringIO('\n'.join(body))))
head='target,model,n,SD_true,SD_pred,ratio,about_0_5,true_min,true_max,true_p05,true_p95,pred_min,pred_max,pred_p05,pred_p95,Pearson_r,OLS_truth_on_pred_slope'
stats=[]
for setname,anchor in [('Development','SET=Development_OOF'),('Validation','SET=Validation')]:
 for r in block(anchor,head):
  if r['model']=='RF':stats.append({'set':setname,**r})
assert [tuple(round(float(r[k]),3) for k in ['ratio','Pearson_r','OLS_truth_on_pred_slope']) for r in stats]==[(.533,.587,1.102),(.560,.586,1.046),(.540,.548,1.015),(.570,.582,1.021)]
bands=[r for r in block('SET=Development_OOF','target,model,truth_band,n,mean_true,mean_pred,arithmetic') if r['target']=='Vocabulary' and r['model']=='RF']
pred=getcsv(P/'07_kiem_tra_offline/development_predictions.csv')
truth=[float(r['y_V']) for r in pred];rf=[float(r['RF_V']) for r in pred]
q=pstdev(rf)/pstdev(truth)
mt,mr=mean(truth),mean(rf)
cov=mean([(a-mt)*(b-mr) for a,b in zip(truth,rf)])
r=cov/(pstdev(truth)*pstdev(rf));forward=cov/pstdev(truth)**2;reverse=cov/pstdev(rf)**2
assert abs(q-float(stats[0]['ratio']))<1e-10
assert abs(reverse-float(stats[0]['OLS_truth_on_pred_slope']))<1e-10
for b in bands:
 g=[(t,p) for t,p in zip(truth,rf) if (t<2.5 if b['truth_band']=='<2.5' else t>4 if b['truth_band']=='>4.0' else 2.5<=t<=4)]
 assert len(g)==int(b['n']) and abs(mean([z[1] for z in g])-float(b['mean_pred']))<1e-10
outcsv('11_ba_cau_giai_thich/so_lieu_nen.csv',[{'set':x['set'],'target':x['target'],'N':x['n'],'SD_pred_over_SD_true':x['ratio'],'Pearson':x['Pearson_r'],'OLS_truth_on_prediction':x['OLS_truth_on_pred_slope'],'source':src+' / Part B, SMALL_SUMMARY_TABLE; OLS includes intercept'} for x in stats])
# Standalone numeric evidence, with original line locators; no learner prose.
selected=[(n,l) for n,l in enumerate(lines,1) if n in [28,34,35,37,99,101,103,118,119,120,278,714,723,726,727,1629] or 1699<=n<=1713]
write('08_tai_lap/nguon/bo_sung_tuan10.md',f'# Nguồn: {src}\nSHA256: {hashlib.sha256((R/src).read_bytes()).hexdigest()}\n\n'+'\n'.join(f'{n}: {l}' for n,l in selected))
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold')
NAVY=colors.HexColor('#17334b');TEAL=colors.HexColor('#087e8b');GRAY=colors.HexColor('#edf0f2');ORANGE=colors.HexColor('#c96724')
W,H=1100,760
def text(c,s,x,y,w,size=17,color=NAVY):
 st=ParagraphStyle('p',fontName='Arial',fontSize=size,leading=size*1.3,textColor=color)
 p=Paragraph(s,st);_,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return y-h
def header(c,title,sub):
 c.setFillColor(colors.white);c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(TEAL);c.rect(0,H-12,W,12,fill=1,stroke=0)
 text(c,title,38,H-30,W-76,29);text(c,sub,38,H-78,W-76,15,TEAL)
def table(c,data,widths,x,y,size=15):
 st=ParagraphStyle('cell',fontName='Arial',fontSize=size,leading=size*1.27,textColor=NAVY)
 t=Table([[Paragraph(html.escape(str(v)).replace('\n','<br/>'),st) for v in row] for row in data],colWidths=widths)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GRAY),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d4e1e7')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('INNERGRID',(0,0),(-1,-1),1,colors.white)]))
 _,h=t.wrap(sum(widths),1000);t.drawOn(c,x,y-h);return y-h
def raster(rel,draw):
 buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(W,H));draw(c);c.save()
 with fitz.open(stream=buf.getvalue(),filetype='pdf') as d:
  p=P/rel;p.parent.mkdir(parents=True,exist_ok=True);d[0].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(p)
def image_a(c):
 header(c,'Độ phân tán và độ dốc: xem rõ chiều hồi quy','Gợi ý trực quan để thành viên tự giải thích; không phải đoạn trả lời học thuộc')
 x0,y0,side=90,240,410
 def xx(v):return x0+(v-1)*side/4
 def yy(v):return y0+(v-1)*side/4
 c.setStrokeColor(colors.HexColor('#dde3e7'));c.setLineWidth(.6)
 for v in [1,2,3,4,5]:
  c.line(xx(v),y0,xx(v),y0+side);c.line(x0,yy(v),x0+side,yy(v));text(c,str(v),xx(v)-5,y0-8,30,12);text(c,str(v),x0-24,yy(v)+7,25,12)
 c.setStrokeColor(NAVY);c.setLineWidth(1.4);c.line(x0,y0,x0+side,y0);c.line(x0,y0,x0,y0+side)
 c.setFillColor(colors.HexColor('#84b5bd'))
 for t,p in zip(truth,rf):c.circle(xx(t),yy(p),1.4,fill=1,stroke=0)
 c.setStrokeColor(colors.HexColor('#75808a'));c.setDash(5,4);c.line(xx(1),yy(1),xx(5),yy(5));c.setDash()
 intercept=mean(rf)-forward*mean(truth)
 c.setStrokeColor(ORANGE);c.setLineWidth(2.5);c.line(xx(1),yy(intercept+forward),xx(5),yy(intercept+5*forward))
 c.setFillColor(TEAL)
 for b in bands:c.circle(xx(float(b['mean_true'])),yy(float(b['mean_pred'])),5,fill=1,stroke=0)
 text(c,'Điểm thật Từ vựng',190,201,300,17)
 c.saveState();c.translate(40,410);c.rotate(90);c.setFont('Arial',17);c.setFillColor(NAVY);c.drawString(0,0,'RF dự đoán');c.restoreState()
 text(c,'Nét đứt: y = x  ·  Nét cam: OLS RF ~ thật',85,176,445,13)
 text(c,f'Độ dốc trên biểu đồ = r × q = {forward:.3f}',85,150,445,16,ORANGE)
 text(c,'q = SD(dự đoán) / SD(điểm thật)',560,666,495,20)
 dat=[['Tập / đích','q','r','β: thật ~ RF']]+[[x['set'].replace('Development','Dev').replace('Validation','Val')+' / '+('Từ vựng' if x['target']=='Vocabulary' else 'Ngữ pháp'),f"{float(x['ratio']):.3f}",f"{float(x['Pearson_r']):.3f}",f"{float(x['OLS_truth_on_pred_slope']):.3f}"] for x in stats]
 table(c,dat,[220,75,75,135],550,625,15)
 text(c,'β = r / q   (OLS thật ~ RF, có intercept)',560,405,495,20)
 text(c,'Trục hình: x = thật; y = RF. Bảng β dùng chiều ngược lại.',560,367,495,17)
 table(c,[['Vùng thật V (Dev)','Thật TB','RF TB']]+[[b['truth_band'],f"{float(b['mean_true']):.2f}",f"{float(b['mean_pred']):.2f}"] for b in bands if b['truth_band']!='2.5-4.0'],[265,120,120],550,305,16)
 text(c,'Tự giải thích: q nhỏ cho thấy gì? β gần 1 thuộc chiều nào?',560,145,495,18,TEAL)
 text(c,'Nguồn: reports/week10/RESULTS_week10.md, Part B: SMALL_SUMMARY_TABLE và TRUTH_BAND_MEANS (Dev/Val).',38,77,1020,12)
 text(c,'Điểm trên hình và đường cam tính trực tiếp từ reports/week9/t3_heldout_predictions.csv, prompt_disjoint, N=3.812; không fit lại mô hình. SD tổng thể (ddof=0).',38,53,1020,12)
def box(c,label,x,y,w,h):
 c.setFillColor(GRAY);c.roundRect(x,y-h,w,h,10,fill=1,stroke=0);text(c,label.replace('\n','<br/>'),x+15,y-15,w-30,21)
def arrow(c,x1,y1,x2,y2):
 c.setStrokeColor(TEAL);c.setLineWidth(3);c.line(x1,y1,x2,y2)
 a=math.atan2(y2-y1,x2-x1);d=12
 c.line(x2,y2,x2-d*math.cos(a-.45),y2-d*math.sin(a-.45));c.line(x2,y2,x2-d*math.cos(a+.45),y2-d*math.sin(a+.45))
def image_b(c):
 header(c,'Hai mô hình cùng nhìn một nguồn đặc trưng','Sơ đồ giả thuyết về thông tin đầu vào; số liệu tổng hợp không chứng minh cơ chế gây lỗi từng bài')
 box(c,'14 đặc trưng chung\nVí dụ: tỷ lệ cảnh báo lỗi do công cụ cũ',48,610,300,125)
 box(c,'Ridge\nTuyến tính + phạt hệ số',430,665,260,100)
 box(c,'Random Forest\nTrung bình các cây',430,515,260,100)
 box(c,'D = max |RF − Ridge|\nHai dự đoán gần nhau?\nCó thể cùng xa nhãn.',780,600,270,160)
 arrow(c,348,550,430,615);arrow(c,348,550,430,465);arrow(c,690,615,780,550);arrow(c,690,465,780,500)
 text(c,'Giả thuyết để tự giải thích: đặc trưng thiếu thông tin → cả hai có thể bỏ sót cùng dấu hiệu.',50,385,1000,21,TEAL)
 table(c,[['Bằng chứng đã lưu','Giá trị','Phạm vi / nguồn'],['RF và Ridge cùng sai lớn','276/386','Development OOF; week9/t3_pooled.csv'],['D bắt trong nhóm cùng sai','44; ngẫu nhiên 55,32','Cùng ngân sách 764; week9/t3_pooled.csv'],['Người đọc / công cụ cũ','7,33 / 1,24 lỗi','36 random36, tối đa 150 từ đầu; week10/gec_part_a_68.csv']],[370,220,430],40,335,18)
 text(c,'Công cụ cũ: số ước lượng từ tỷ lệ toàn bài × độ dài đoạn; không phải đếm lại trực tiếp. Tương quan/bất đồng không xác nhận nguyên nhân.',45,133,1010,16)
 text(c,'Câu hỏi tự nói: khi cùng thiếu một dấu hiệu, D đang đo điều gì? Cần nguồn thông tin nào để kiểm tra?',45,84,1010,18,TEAL)
 text(c,'Nguồn: reports/week9/t3_pooled.csv (prompt_disjoint, A1/A3); reports/week10/gec_part_a_68.csv và RESULTS_week10.md / RANDOM_SAMPLE_OVERALL; schema 14 đặc trưng: outputs/phase6/feature_schema.json.',40,47,1020,11)
raster('11_ba_cau_giai_thich/nen_ve_giua.png',image_a)
raster('11_ba_cau_giai_thich/dung_chung_dac_trung.png',image_b)
write('11_ba_cau_giai_thich/cau_lich_su_dung_test.md','''# Một câu nháp - thành viên viết lại bằng lời của mình

“Test đã được dùng ở lần đánh giá được báo cáo trong tuần 9 (47/208, kỳ vọng 41,63; ngày truy cập đầu chưa xác định); lần hai thầy cho phép ngày **__________**, chỉ cho tín hiệu đã khóa (commit 4e38115, SHA-256 d2eabcb7…8eca), dùng lại RF đã lưu từ tuần 9, không thử tín hiệu khác; kết quả 55/208, kỳ vọng 41,63, p 0,0116 so với ngẫu nhiên; đây là lần dùng thứ hai nên không phải xác nhận độc lập sạch.”

Ngày cố ý để trống để thành viên tự xác nhận và điền. Đây chỉ là nháp theo yêu cầu, không phải lời khai hay câu trả lời của thành viên.
Nguồn: reports/week9/RESULTS_week9.md / Task 0; reports/week9/RESULTS_tree_spread_second_use.md; reports/week9/tree_spread_official_test_second_use_log_attempt2.json / result; docs/signal_lock_tree_spread.md. Xem lịch sử các lần dừng ở ../06_lich_su_dung_test.md. Không xem khoảng CI development +8 [-11,27] là CI của Test.
''')
target=P/'12_mang_theo/signal_lock_tree_spread.md';target.parent.mkdir(exist_ok=True)
target.write_bytes(lock.read_bytes());assert target.read_bytes()==lock.read_bytes()
write('12_mang_theo/kiem_tra_ma_bam.txt',f'Nguồn: docs/signal_lock_tree_spread.md\nBản mang theo được sao chép nguyên byte.\nSHA-256 hiện tính: {hashlib.sha256(target.read_bytes()).hexdigest()}\nSHA-256 kỳ vọng: {EXPECTED}\nKết quả: KHỚP\nCommit khóa: 4e381150edf08d49a134505e669058f1e0d27b48 (nguồn: reports/week9/RESULTS_tree_spread_second_use.md).\nDòng trạng thái Test trong file khóa là nguyên bản lịch sử; lịch sử mới xem 06_lich_su_dung_test.md.\n')
assert 'B1_TFIDF,A3_new_RF_and_B,3812,233,764,35,46.698038123452477' in report
assert 'A3_RF_B2,D_B2,pooled,3812,217,764,36,43.495177942481519' in report
assert '| B1 | 276 | 203 | 73 |' in report and '| B2 | 276 | 191 | 85 |' in report
entries=[
 {'comparison':'RF – Ridge','shared_of_386':276,'caught_of_386':88,'random_of_386':77.362908429581,'shared_caught':44,'shared_K':276,'shared_per_100':100*44/276,'random_shared_per_100':100*55.32185687702314/276,'old276_remain':'','old276_fixed':'','source':src+'; B1 POOLED A1 (D_old); 276/44: week9/t3_pooled.csv A3'},
 {'comparison':'RF – TF-IDF','shared_of_386':233,'caught_of_386':81,'random_of_386':77.362908429581,'shared_caught':35,'shared_K':233,'shared_per_100':100*35/233,'random_shared_per_100':100*46.69803812345248/233,'old276_remain':203,'old276_fixed':73,'source':src+'; B1 POOLED_EVIDENCE A1/A3_new; OLD_SHARED_ERROR_SET_UNDER_NEW_SOURCE'},
 {'comparison':'RF – MiniLM','shared_of_386':217,'caught_of_386':93,'random_of_386':77.362908429581,'shared_caught':36,'shared_K':217,'shared_per_100':100*36/217,'random_shared_per_100':100*43.49517794248152/217,'old276_remain':191,'old276_fixed':85,'source':src+'; B2 concise result tables, A1_RF/A3_RF_B2; old shared-error set'}]
outcsv('12_mang_theo/bang_3_4.csv',entries)
def table34(c):
 header(c,'Bảng 3.4 · Đổi nguồn thông tin đối chiếu','Development OOF · cùng RF, cùng nhãn, cùng 3.812 bài và tổng ngân sách đọc 764')
 dat=[['Nguồn đối chiếu RF','Ridge / 14 đặc trưng','TF-IDF + Ridge','MiniLM + Ridge'],['Cùng sai trong 386 RF sai','276 / 386 [S1]','233 / 386 [S2]','217 / 386 [S3]'],['D tương ứng bắt / 386','88 / 386 [S2,S3]','81 / 386 [S2]','93 / 386 [S3]'],['Ngẫu nhiên cùng ngân sách','77,36 [S2,S3]','77,36 [S2]','77,36 [S3]'],['Bắt trong nhóm cùng sai','44 / 276 [S1]','35 / 233 [S2]','36 / 217 [S3]'],['Trên 100 bài cùng sai','15,94 [S1]','15,02 ≈ 15,0 [S2]','16,59 ≈ 16,6 [S3]'],['Ngẫu nhiên / 100 bài cùng sai','20,04 [S1]','20,04 [S2]','20,04 [S3]'],['Trong nhóm 276 cũ: còn sai / hết sai ở nguồn thay thế','—','203 / 73 [S2]','191 / 85 [S3]']]
 table(c,dat,[340,225,225,230],40,640,17)
 text(c,'“Được cứu”: cả hai sai số của nguồn thay thế < 1; RF vẫn sai ở các ca cũ. Đây không phải sửa điểm RF.',45,206,1010,17)
 text(c,'Mẫu số 233 / 217 là các nhóm lỗi chung khác nhau. Tỷ lệ trên 100 là capture trong nhóm lỗi chung, không phải precision trên số bài được đọc.',45,161,1010,17)
 text(c,'S1: reports/week9/t3_pooled.csv / prompt_disjoint A3; cùng lỗi 276 được tuần 10 nhắc lại. S2: reports/week10/RESULTS_week10.md / B1 POOLED_EVIDENCE và OLD_SHARED_ERROR_SET. S3: cùng báo cáo / B2 concise result tables, A1_RF và A3_RF_B2.',40,98,1020,12)
 text(c,'Tỷ lệ = 100 × C/K; ngẫu nhiên = 100 × tổng(k_f K_f/N_f)/K. Cột Ridge có nguồn gốc tuần 9, không gán nhầm cho một bảng mới tuần 10. Bản số và dòng nguồn kèm trong CSV và 08_tai_lap/nguon/bo_sung_tuan10.md.',40,51,1020,12)
c=canvas.Canvas(str(P/'12_mang_theo/bang_3_4.pdf'),pagesize=(W,H));table34(c);c.save()
with fitz.open(P/'12_mang_theo/bang_3_4.pdf') as d:d[0].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(P/'12_mang_theo/bang_3_4.png')
write('13_cau_truc_bao_cao_cuoi.md','''# Đề cương báo cáo cuối - khung 6–8 trang

Chỉ là đề cương. Nguồn định hướng: chỉ dẫn người dùng trong yêu cầu bổ sung, thuật lại trả lời câu 2 của thầy; chưa có bản trả lời gốc để xác minh. Phân bổ trang dưới đây là đề xuất biên tập, không phải quy định mới của thầy. Không fine-tune encoder; giữ MiniLM như nguồn đối chiếu đã lưu.

| Phần nội dung | Trọng tâm cần trình bày | Ánh xạ cấu trúc 6–8 trang | Bằng chứng dự kiến |
|---|---|---|---|
| (1) So cách ưu tiên đọc | Đối chiếu D với ngẫu nhiên, Ridge extremity (xa trung vị dự đoán, không dùng điểm thật để chọn), bài ngắn nhất; giữ cùng nhãn, ngân sách và phá hòa | Tóm tắt/Giới thiệu; Dữ liệu/Phương pháp; Thiết lập thí nghiệm; Kết quả | 04_bang_ket_qua; week9/t3_pooled.csv; biểu đồ nén về giữa |
| (2) Gộp nguồn thông tin | Một bảng so Ridge, TF-IDF, MiniLM: cùng sai, bắt lỗi, kỳ vọng, nhóm 276; không mở rộng thành phần fine-tune | Dữ liệu/Phương pháp; Thiết lập; một bảng trong Kết quả | 12_mang_theo/bang_3_4.pdf; reports/week10/RESULTS_week10.md |
| (3) Phân tích mọi mô hình cùng sai | Ưu tiên ca có RF/Ridge/TF-IDF/MiniLM đều sai; công khai quy tắc chọn, đích, thiếu dữ liệu và trạng thái đọc; chỉ tổng hợp nhận xét thành viên đã xác nhận | Kết quả/Phân tích lỗi là phần trọng tâm; giới hạn ở Thảo luận/Kết luận | 05_ca_loi; 14_luot_di_qua; bảng dự đoán development đã lưu; không tự coi 191 ca RF/Ridge/MiniLM là giao của cả bốn |
| (4) Nghiên cứu cùng dữ liệu | Một đoạn ngắn: bài liên quan, cùng ELLIPSE nhưng khác split/nhãn/nhiệm vụ thì giới hạn khả năng so | Giới thiệu hoặc Thảo luận; Tham khảo | Chỉ dùng tài liệu đã đọc và có trích dẫn; chưa điền số từ nghiên cứu khác |

Gợi ý bố cục tổng thể: Tóm tắt/Giới thiệu → Dữ liệu/Phương pháp → Thiết lập thí nghiệm → Kết quả/Phân tích lỗi → Thảo luận/Kết luận → Tham khảo/Phụ lục. Điều chỉnh để nằm trong 6–8 trang theo chỉ dẫn được cung cấp; chưa mặc định phụ lục có tính vào giới hạn.

Phụ lục: GECToR, bảng phụ theo fold/vùng điểm, CI và đơn vị bootstrap, lịch sử Test, hash và lệnh tái lập. Trong thân bài chỉ dẫn tới phụ lục khi cần. Thành viên tự viết nội dung, kết luận, quyết định và khai báo AI.
''')
schema=json.loads((R/'outputs/phase6/feature_schema.json').read_text())
gec=getcsv(P/'08_tai_lap/nguon/gec_part_a_68.csv')
for essay in ['0514D25768A0','684166ED2438']:
 z=getcsv(P/f'02_mau_truy_vet/{essay}.csv')[0]
 assert len(schema)==14 and float(z['y_V'])<2.5 and z['shared_large_error']=='True'
 human=next((x for x in gec if x['essay_id']==essay),None)
 counts=(f"Người đọc: {float(human['reader']):g} lỗi / tối đa 150 từ đầu; công cụ cũ ước lượng: {float(human['LT_estimate']):.9f}; GECToR: {human['edits_grammar']} chỉnh sửa ngữ pháp. Nguồn: reports/week10/gec_part_a_68.csv, đúng ID. Không coi chỉnh sửa là nhãn lỗi chuẩn." if human else 'Người đọc: **chưa có người đếm**; không có dòng trong reports/week10/gec_part_a_68.csv. Công cụ cũ = 0 cảnh báo/100 từ, ước lượng trên min(150,55) từ = 0; không có nghĩa bài không lỗi. Nguồn: docs/phieu_luyen_684166ED2438_development.md và t3_eligible_development.csv.')
 features='\n'.join(f'| {f} | {float(z[f]):.12g} |' for f in schema)
 write(f'14_luot_di_qua/{essay}.md',f'''# Lượt đi qua: {essay}

Tệp nhìn số để tự giải thích; không có bài luận, không có đoạn trả lời thay thành viên. Dự đoán đều là held-out GroupKFold theo đề; không thay bằng mô hình Phase 6 ở phần phân rã riêng.

## 1. Điểm thật và nhóm cùng sai
Nhãn V/G = {z['y_V']} / {z['y_G']}; Từ vựng < 2,5. RF và Ridge cùng sai lớn; thuộc 276 ca chung trong 386 ca RF sai lớn. “Sai lớn” là max sai số tuyệt đối hai đích ≥ 1.
Nguồn: reports/week9/t3_heldout_predictions.csv, prompt_disjoint, đúng ID; reports/week9/t3_pooled.csv / A3; docs/phieu_luyen_*.md; CSV truy vết trong 02_mau_truy_vet.

## 2. Đặc trưng và số đếm lỗi
| Đặc trưng | Giá trị |
|---|---:|
{features}

Nguồn tất cả 14 giá trị: reports/week9/t3_eligible_development.csv, đúng ID; tên/thứ tự theo outputs/phase6/feature_schema.json. {counts}

## 3. RF, Ridge, D và danh sách đọc lại
| Đại lượng | Từ vựng | Ngữ pháp |
|---|---:|---:|
| RF | {float(z['RF_V']):.10f} | {float(z['RF_G']):.10f} |
| Ridge | {float(z['Ridge_V']):.10f} | {float(z['Ridge_G']):.10f} |

D = max(|RF_V−Ridge_V|, |RF_G−Ridge_G|) = {float(z['D']):.14f}. Fold {z['fold']}; hạng {z['D_rank']}/{z['fold_n']}; ngưỡng đọc ceil(0,20×{z['fold_n']}) = {z['budget']}. **Không vào danh sách đọc lại.** Hòa theo essay_id chuỗi tăng dần. D cuối danh sách = 0,2178198494584902.
Nguồn: reports/week9/t3_heldout_predictions.csv, prompt_disjoint; phiếu docs/phieu_luyen_* tương ứng. {'RF và Ridge Từ vựng gần 2,9 theo khoảng 2,8–3,0 trong phiếu.' if essay=='684166ED2438' else 'Từ vựng 3,20 / 3,41; không gọi hai dự đoán này là cùng gần 2,9.'}

## 4. MiniLM trên cùng bài
MiniLM + Ridge: V = {float(z['MiniLM_V']):.10f}; G = {float(z['MiniLM_G']):.10f}. Nguồn: reports/week10/b2_oof.csv, cột B2_V/B2_G, đúng ID; được đối chiếu trong docs/phieu_luyen_*.

## 5. Kiểm tra trực tiếp phép đếm D
Chạy từ gốc repo: `python interview_pack/07_kiem_tra_offline/check_d_88_of_386.py`.
Script và [PNG đầu ra](../07_kiem_tra_offline/check_d_88_of_386_output.png): D bắt 88/386, đọc tổng 764; kỳ vọng 77,362908. Nguồn: bản dự đoán development đã lưu kèm script, gốc reports/week9/t3_heldout_predictions.csv / prompt_disjoint. Chỉ tính lại số đã lưu, không model, không mạng, không Test.
''')
fields=['hành động','người phụ trách','bằng chứng hoàn thành']
outcsv('15_review_tuan10_mau/ba_hanh_dong.csv',[dict.fromkeys(fields,'') for _ in range(3)],fields)
outcsv('15_review_tuan10_mau/moi_thanh_vien_mot_buoc.csv',[dict.fromkeys(['thành viên','bước pipeline tự chọn','giải thích hoặc phần tự viết','bằng chứng tự kiểm tra'],'') for _ in range(3)],['thành viên','bước pipeline tự chọn','giải thích hoặc phần tự viết','bằng chứng tự kiểm tra'])
write('15_review_tuan10_mau/README.md','''# MẪU TRỐNG - review tuần 10

Ba hành động chốt với thầy: tự điền ba dòng trong ba_hanh_dong.csv (hành động, người phụ trách, bằng chứng hoàn thành).

Một điểm nhóm chưa hiểu: ____________________

Một quyết định cần phản hồi: ____________________

Gợi ý để nhóm **tự chọn**, chưa có lựa chọn mặc định: đơn vị lấy mẫu lại CI; quy tắc chọn tối thiểu 10 ca lỗi; cách gọi kết quả Test lần hai là thăm dò.

Mỗi thành viên tự giải thích hoặc viết một bước pipeline trong moi_thanh_vien_mot_buoc.csv. Tất cả ô để trống. Không gán người phụ trách, nhận quyết định, giờ hoặc đóng góp thay thành viên.
Nguồn cấu trúc mẫu: yêu cầu bổ sung của người dùng; không phải biên bản đã chốt.
''')
extra=[('11 · Vì sao độ dốc gần 1 mà dự đoán vẫn nén?','11_ba_cau_giai_thich/nen_ve_giua.png'),('11 · Dùng chung đặc trưng có thể bỏ sót lỗi gì?','11_ba_cau_giai_thich/dung_chung_dac_trung.png'),('11 · Tự viết lại lịch sử Test lần hai','11_ba_cau_giai_thich/cau_lich_su_dung_test.md'),('12 · Mang theo khóa và bảng 3.4','12_mang_theo/bang_3_4.pdf'),('12 · Kiểm tra hash khóa','12_mang_theo/kiem_tra_ma_bam.txt'),('13 · Báo cáo cuối tổ chức thế nào?','13_cau_truc_bao_cao_cuoi.md'),('14 · Đi qua bài 0514D25768A0','14_luot_di_qua/0514D25768A0.md'),('14 · Đi qua bài 684166ED2438, gần 2,9','14_luot_di_qua/684166ED2438.md'),('15 · Nhóm tự điền review tuần 10','15_review_tuan10_mau/README.md')]
index=P/'00_START_HERE.html';v=index.read_text(encoding='utf-8')
for label,path in extra:
 v=re.sub(r'<tr><td>[^<]*</td><td><a href="'+re.escape(path)+r'">[^<]*</a></td></tr>','',v)
v=v.replace('</table>',''.join(f'<tr><td>{html.escape(label)}</td><td><a href="{path}">{path}</a></td></tr>' for label,path in extra)+'</table>',1);index.write_text(v,encoding='utf-8')
write('08_tai_lap/SUPPLEMENT_SOURCES.sha256',''.join(f'{hashlib.sha256((R/rel).read_bytes()).hexdigest()}  {rel}\n' for rel in [src,'docs/signal_lock_tree_spread.md','outputs/phase6/feature_schema.json']))
write('11_ba_cau_giai_thich/README.md','''# Hình gợi ý tự giải thích
Hai PNG có font nhúng khi kết xuất, xem offline không cần thư viện hoặc mạng. Chỉ gồm biểu đồ/sơ đồ, nhãn, công thức, số liệu và câu hỏi gợi mở; không có đoạn trả lời thay thành viên.
Lưu ý chiều hồi quy: beta≈1 trong báo cáo là OLS điểm thật ~ dự đoán (có intercept), beta=r/q. Biểu đồ trục x=điểm thật, y=RF dùng chiều RF ~ thật, độ dốc=r*q. Không lấy beta của chiều ngược đặt trực tiếp lên biểu đồ này.
Sơ đồ dùng chung đặc trưng mô tả một giả thuyết cơ chế, không chứng minh việc công cụ đếm thiếu gây sai cho mọi bài hoặc toàn bộ 276 ca.
Nguồn số liệu: so_lieu_nen.csv, reports/week10/RESULTS_week10.md / Part B; week9/t3_heldout_predictions.csv và t3_pooled.csv; week10/gec_part_a_68.csv. Bảng nguồn trích kèm ở 08_tai_lap/nguon/bo_sung_tuan10.md.
''')
repro=P/'08_tai_lap/REPRODUCE.md'
v=repro.read_text(encoding='utf-8').split('\n## Bổ sung 11–15')[0]
repro.write_text(v+'\n## Bổ sung 11–15\n`python interview_pack/08_tai_lap/supplement_pack.py` dựng lại cả gói nền và phần bổ sung, không mô hình/không fit/không Test. Sau kiểm tra hình, chạy finalize_pack.py để chốt manifest. Cần Python với reportlab, Pillow, PyMuPDF và font Arial. Nguồn được kiểm tra bằng SUPPLEMENT_SOURCES.sha256.\n',encoding='utf-8')
print(f'SUPPLEMENT PASS: lock={EXPECTED}; beta_reverse={reverse:.9f}; slope_forward={forward:.9f}; TF-IDF=35/233={100*35/233:.3f}%; MiniLM=36/217={100*36/217:.3f}%')

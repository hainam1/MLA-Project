"""Edit section 02 only: Vietnamese meanings and definition-based min/max ranges.
Reads saved sample rows and extractor definitions; no cohort statistics or model.
"""
from pathlib import Path
import csv,json,hashlib,html,sys
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
import fitz

sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parents[2];A=P/'_phu';R=P.parent;Q=A/'_kiem_tra/toi_uu'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
MEANINGS={
 'word_count':'Số từ',
 'sentence_count':'Số câu',
 'mean_sentence_length':'Số từ trung bình mỗi câu',
 'mtld':'Độ đa dạng từ vựng MTLD',
 'mattr':'Tỷ lệ từ khác nhau theo cửa sổ',
 'mean_word_frequency':'Tần suất từ trung bình theo thang Zipf',
 'mean_word_length':'Độ dài từ trung bình tính bằng ký tự',
 'lexical_density':'Tỷ lệ từ mang nội dung',
 'noun_diversity':'Tỷ lệ danh từ gốc khác nhau',
 'detected_grammar_errors_per_100_words':'Cảnh báo ngữ pháp trên 100 từ',
 'detected_error_free_sentence_ratio':'Tỷ lệ câu không có cảnh báo ngữ pháp',
 'complex_sentence_ratio':'Tỷ lệ câu có mệnh đề phụ',
 'estimated_clauses_per_sentence':'Số mệnh đề ước lượng trung bình mỗi câu',
 'subordinate_clause_ratio':'Tỷ lệ mệnh đề phụ'}
RATIOS={'mattr','lexical_density','noun_diversity','detected_error_free_sentence_ratio','complex_sentence_ratio','subordinate_clause_ratio'}
spec=R/'docs/feature_specification.md'
ids=['684166ED2438','0514D25768A0'];samples={i:rows(A/f'02_mau_truy_vet/{i}.csv')[0] for i in ids}
features=list(samples[ids[0]])[1:15];assert set(features)==set(MEANINGS)
LOWER={f:1 if f=='sentence_count' else 0 for f in features}
UPPER={f:1 if f in RATIOS else 9 if f=='mean_word_frequency' else None for f in features}
definition_sources=[spec,R/'src/mla_project/features/extract_length.py',R/'src/mla_project/features/extract_vocabulary.py',R/'.venv/Lib/site-packages/wordfreq/__init__.py']
assert all(p.exists() for p in definition_sources)
counts={r['essay_id']:r for r in rows(A/'08_tai_lap/nguon/gec_part_a_68.csv')}
target=P/'02_mau_truy_vet.pdf';backup=Q/'02_mau_truy_vet_truoc_mien_gia_tri.pdf'
if not backup.exists():backup.write_bytes(target.read_bytes())
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold')
W,H=1400,1000;NAVY=colors.HexColor('#17334b')
def text(c,s,x,y,w,size=20):
 p=Paragraph(s,ParagraphStyle('p',fontName='Arial',fontSize=size,leading=size*1.25,textColor=NAVY))
 _,h=p.wrap(w,1800);assert y-h>15,(s[:40],y-h);p.drawOn(c,x,y-h);return y-h
def table(c,data,widths,top,size=17):
 st=ParagraphStyle('cell',fontName='Arial',fontSize=size,leading=size*1.25,textColor=NAVY)
 t=Table([[Paragraph(html.escape(str(v)).replace('\n','<br/>'),st) for v in row] for row in data],colWidths=widths)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#edf0f2')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d4e1e7')),('INNERGRID',(0,0),(-1,-1),1,colors.white),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
 _,h=t.wrap(sum(widths),1800);assert top-h>80;t.drawOn(c,40,top-h);return top-h
def number(v):return f'{float(v):.6g}'.replace('.',',')
c=canvas.Canvas(str(target),pagesize=(W,H))
for essay in ids:
 z=samples[essay]
 c.setFillColor(colors.HexColor('#087e8b'));c.rect(0,H-10,W,10,fill=1,stroke=0)
 text(c,'NHÓM 03 · ELLIPSE · DỰ ĐOÁN GIỮ LẠI THEO ĐỀ',40,968,1320,13)
 text(c,'Đặc trưng → dự đoán → nhãn · '+essay,40,934,1320,31)
 text(c,f"Nhãn V/G = {z['y_V']} / {z['y_G']}; V &lt; 2,5; thuộc 276/386 ca RF–Ridge cùng sai lớn.",40,883,1320,23)
 text(c,'Nguồn nhãn/nhóm: reports/week9/t3_heldout_predictions.csv, prompt_disjoint; t3_pooled.csv / A3.',40,847,1320,12)
 text(c,'Đặc trưng (nghĩa tiếng Việt) và miền giá trị min–max theo định nghĩa',40,815,1320,23)
 data=[['Đặc trưng (nghĩa tiếng Việt)','Bài này','Miền min–max','Đặc trưng (nghĩa tiếng Việt)','Bài này','Miền min–max']]
 for j in range(7):
  row=[]
  for f in [features[j],features[j+7]]:
   domain=f"{LOWER[f]}–{UPPER[f]}"+('*' if f=='mean_word_frequency' else '') if UPPER[f] is not None else f"{LOWER[f]}–∞\n(không trần)"
   row.extend([f+'\n('+MEANINGS[f]+')',number(z[f]),domain])
  data.append(row)
 y=table(c,data,[425,85,150,425,85,150],778,size=16)
 text(c,'Miền của đặc trưng thô; ∞ = không có trần cố định, không phải giá trị lưu. Tỷ lệ 1 = 100%; cảnh báo trên 100 từ có thể vượt 100. Không có thang điểm chung.',40,y-12,1320,13)
 text(c,'*Zipf: 0–9 theo log10(tần suất)+9 và sàn 0; thường 0–8. Nguồn: docs/feature_specification.md; extract_length.py, extract_vocabulary.py; wordfreq/__init__.py.',40,y-33,1320,12)
 if essay in counts:
  h=counts[essay];s=f"Đếm lỗi / tối đa 150 từ đầu: người {float(h['reader']):g}; công cụ cũ ước lượng {float(h['LT_estimate']):.2f}; GECToR {h['edits_grammar']} chỉnh sửa."
 else:s='Đếm lỗi: chưa có người đếm; công cụ cũ 0 cảnh báo/100 từ; GECToR chưa có dữ liệu.'
 text(c,s,40,y-66,1320,20)
 text(c,'Nguồn đếm lỗi: reports/week10/gec_part_a_68.csv; docs/phieu_luyen_* tương ứng. Cảnh báo công cụ không phải lỗi do người chấm xác nhận.',40,y-97,1320,12)
 text(c,'Dự đoán OOF trên cùng bài',40,y-129,1320,23)
 dat=[['Mô hình','Từ vựng','Ngữ pháp','Nguồn'],['RF',f"{float(z['RF_V']):.10f}",f"{float(z['RF_G']):.10f}",'reports/week9/t3_heldout_predictions.csv'],['Ridge',f"{float(z['Ridge_V']):.10f}",f"{float(z['Ridge_G']):.10f}",'reports/week9/t3_heldout_predictions.csv'],['MiniLM + Ridge',f"{float(z['MiniLM_V']):.10f}",f"{float(z['MiniLM_G']):.10f}",'reports/week10/b2_oof.csv']]
 y=table(c,dat,[230,220,220,650],y-162,size=17)
 text(c,f"D = {float(z['D']):.9f}; hạng {z['D_rank']}/{z['fold_n']}; ngưỡng đọc {z['budget']} bài đầu (20%). Không được D chọn.",40,y-12,1320,22)
 text(c,'Nguồn D/hạng/ngưỡng: reports/week9/t3_heldout_predictions.csv; D giảm dần, hòa essay_id chuỗi tăng dần. Sai lớn: max sai số tuyệt đối V/G ≥ 1.',40,y-46,1320,12)
 text(c,'Số của bài và dự đoán giữ nguyên. Min–max là miền theo định nghĩa, không phải min/max quan sát trong dữ liệu. Không mở Test/corpus, không tính lại mô hình.',40,47,1320,12)
 c.showPage()
c.save()
with (A/'02_mau_truy_vet/giai_nghia_va_mien_gia_tri.csv').open('w',encoding='utf-8-sig',newline='') as f:
 out=csv.DictWriter(f,['feature','nghia_tieng_viet','minimum','maximum','note','source_definition']);out.writeheader()
 for name in features:out.writerow({'feature':name,'nghia_tieng_viet':MEANINGS[name],'minimum':LOWER[name],'maximum':UPPER[name] if UPPER[name] is not None else 'không có trần cố định','note':'Zipf: theoretical upper bound from proportion <=1; usual words 0-8; default floor 0' if name=='mean_word_frequency' else 'Valid non-empty input must yield at least one sentence' if name=='sentence_count' else 'Raw feature range, not observed sample extrema','source_definition':'docs/feature_specification.md; src/mla_project/features/extract_length.py; extract_vocabulary.py; wordfreq/__init__.py'})
(A/'02_mau_truy_vet/nguon_mien_gia_tri.json').write_text(json.dumps({'source_hashes':{p.relative_to(R).as_posix():sha(p) for p in definition_sources},'scope':'Mathematical ranges from extractor definitions, including zero-value fallback policies; no observed cohort maxima','lower':LOWER,'upper':UPPER,'Zipf_note':'0 floor by zipf_frequency default; theoretical 9 from log10(p)+9 with p<=1; typical 0-8 is not a hard maximum'},ensure_ascii=False,indent=2),encoding='utf-8')
with fitz.open(target) as doc:
 assert len(doc)==2
 for j,page in enumerate(doc):
  for block in page.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     x0,y0,x1,y1=span['bbox'];assert min(x0,y0)>=0 and x1<=W and y1<=H
  page.get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(Q/f'02_mau_truy_vet_page{j+1:02}.png')
print('Updated section 02 only: two pages, 14 Vietnamese meanings and definition-based min/max ranges; all text within page.')

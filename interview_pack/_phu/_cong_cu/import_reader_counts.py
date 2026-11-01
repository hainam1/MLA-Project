"""Extract submitted numeric answers without resolving learner-writing cells.
Pass the two user-specified XLSX paths as arguments; paths/names are not persisted.
"""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import csv,json,posixpath,re,sys,hashlib
P=Path(__file__).resolve().parents[2];A=P/'_phu'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def select(path,index,wanted):
 with ZipFile(path) as z:
  sheets=list(E.fromstring(z.read('xl/workbook.xml')).find('s:sheets',NS));assert len(sheets)==6
  s=sheets[index];rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
  t=rels[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
  t=t.lstrip('/') if t.startswith('/') else posixpath.normpath('xl/'+t)
  cells=[c for c in E.fromstring(z.read(t)).findall('.//s:sheetData/s:row/s:c',NS) if c.get('r') in wanted]
  refs={int(c.find('s:v',NS).text) for c in cells if c.get('t')=='s'};strings={}
  if refs:
   with z.open('xl/sharedStrings.xml') as stream:
    n=0
    for _,el in E.iterparse(stream,events=['end']):
     if el.tag.endswith('}si'):
      if n in refs:strings[n]=''.join(x.text or '' for x in el.iter() if x.tag.endswith('}t'))
      n+=1;el.clear()
      if len(strings)==len(refs):break
  out={k:None for k in wanted}
  for c in cells:
   assert c.find('s:f',NS) is None
   v=c.find('s:v',NS);raw=v.text if v is not None else None
   out[c.get('r')]=strings[int(raw)] if c.get('t')=='s' else ''.join(t.text or '' for t in c.findall('.//s:t',NS)) if c.get('t')=='inlineStr' else raw
  return out
def readcsv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
assert len(sys.argv)==3
paths=[Path(x) for x in sys.argv[1:]]
reference=readcsv(A/'05_ca_loi/32_ca_da_co_ghi_nhan.csv')
keys=['y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G']
refs=[f'B{6+7*i+j}' for i in range(5) for j in range(4)]
proof={'scope':'Only selected answer/confirmation and numeric model cells; no essay cells resolved or exported. Reader names, signatures and times omitted.','readers':{}}
counts={};confirmations=[]
for alias,path in zip(['A','B'],paths):
 answers=select(path,2,refs);answers_b=select(path,4,refs);confirm=select(path,5,[f'B{i}' for i in range(5,11)])
 nonempty=lambda v:v is not None and str(v).strip()!=''
 assert all(map(nonempty,answers.values())) and all(map(nonempty,answers_b.values())) and all(map(nonempty,confirm.values()))
 confirmations.append(confirm)
 model=select(path,3,[f'{col}{row}' for row in range(6,11) for col in 'BCDEFG'])
 extracted=[]
 for i in range(5):
  vals=[float(model[f'{col}{i+6}']) for col in 'BCDEFG']
  matches=[r for r in reference if all(abs(float(r[k])-v)<1e-8 for k,v in zip(keys,vals))];assert len(matches)==1
  eid=matches[0]['essay_id'];number=float(answers[f'B{8+7*i}']);assert number>=0 and number.is_integer()
  counts.setdefault(eid,{})[alias]=int(number)
  extracted.append({'essay_id':eid,'temporary_code':'R'+str(i+1),'reader_error_count':int(number)})
 proof['readers'][alias]={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'part_A_fields_filled':20,'part_B_fields_filled':20,'confirmation_fields_filled':6,'self_confirmation_present':True,'independence_status':'Có nội dung tự xác nhận; chưa kiểm chứng quy trình thực hiện','mapped_cases':extracted}
assert confirmations[0]['B5']!=confirmations[1]['B5']
assert len(counts)==5 and all(set(v)=={'A','B'} for v in counts.values())
proof['reader_identities_different']=True
proof['mapping_method']='Match all six saved truth/RF/Ridge numeric columns to the text-free 32-case export; never assume matching R1..R5 order between readers.'
proof['validation_limit']='Filled fields verified; original comparator requires exact checkbox and fixed role header, but submitted files use free-text confirmations/custom headers. Do not declare complete procedural validation or independence from file presence alone.'
(A/'05_ca_loi/kiem_tra_hai_ban_da_nop.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
inputfile=A/'_cong_cu/workbook_input.json';data=json.loads(inputfile.read_text(encoding='utf-8'))
for row in data['cases']:
 row['reader_A_submitted_count']=counts[row['essay_id']]['A'];row['reader_B_submitted_count']=counts[row['essay_id']]['B']
data['submitted_readers']=proof['readers'];inputfile.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
with (A/'05_ca_loi/5_ca_hai_ban_da_nop.csv').open('w',encoding='utf-8-sig',newline='') as f:
 out=csv.DictWriter(f,['essay_id','reader_A_count','reader_B_count','status','source_A_sha256','source_B_sha256']);out.writeheader()
 for eid,v in counts.items():out.writerow({'essay_id':eid,'reader_A_count':v['A'],'reader_B_count':v['B'],'status':'Hai bản đã điền; có nội dung tự xác nhận; chưa kiểm chứng quy trình','source_A_sha256':proof['readers']['A']['source_sha256'],'source_B_sha256':proof['readers']['B']['source_sha256']})
print(json.dumps({'readers':2,'cases':5,'filled_answer_fields_per_reader':40,'filled_confirmation_fields_per_reader':6,'matched_ids':sorted(counts),'private_text_or_names_exported':False},ensure_ascii=True))

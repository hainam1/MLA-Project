from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import fitz,json,subprocess,time,sys,hashlib
P=Path(__file__).resolve().parents[2];Q=P/'_phu/_kiem_tra/toi_uu';sys.stdout.reconfigure(encoding='utf-8')
for f in list(P.glob('*.inspect.ndjson')):
 target=Q/f.name
 if target.exists():
  previous=Q/(f.stem+'_previous'+f.suffix);assert not previous.exists();target.rename(previous)
 f.rename(target)
start=time.perf_counter()
res=subprocess.run(['cmd.exe','/d','/c',str(P/'07_kiem_tra_offline.bat')],input='\n',capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=10,cwd=P)
elapsed=time.perf_counter()-start
assert 'caught=88/386' in res.stdout and '77.362908 (77.36)' in res.stdout and '77,36' in res.stdout and 'N=10' in res.stdout,(res.stdout,res.stderr)
assert 'OFFLINE GUARD ACTIVE' in res.stdout and elapsed<10
(Q/'BAT_stdout.txt').write_text(res.stdout,encoding='utf-8')
(Q/'BAT_run.json').write_text(json.dumps({'wall_seconds':elapsed,'returncode':res.returncode,'network':'socket/urllib/http events denied in Python by audit hook','stdin':'newline supplied only to exercise pause under test; double-click waits for user key'},indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
out=Image.new('RGB',(1600,1080),'#f3f5f7');draw=ImageDraw.Draw(out);draw.text((30,20),'07_kiem_tra_offline.bat | stdout thuc te - network denied',font=font,fill='black')
for j,line in enumerate(res.stdout.splitlines()):draw.text((30,65+j*31),line,font=font,fill='#17334b')
out.save(Q/'BAT_stdout.png')
pages=[];bounds=[]
for f in sorted(P.glob('*.pdf'))+[Q/'15_review_word_render.pdf']:
 with fitz.open(f) as d:
  for i,page in enumerate(d):
   for block in page.get_text('dict')['blocks']:
    for line in block.get('lines',[]):
     for span in line['spans']:
      x0,y0,x1,y1=span['bbox']
      if x0<0 or y0<0 or x1>page.rect.width or y1>page.rect.height:bounds.append({'file':f.name,'page':i+1})
   target=Q/f'{f.stem}_page{i+1:02}.png';page.get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(target);pages.append(target)
for offset in range(0,len(pages),6):
 im=Image.new('RGB',(2400,2100),'white');draw=ImageDraw.Draw(im)
 for j,f in enumerate(pages[offset:offset+6]):
  pic=Image.open(f).convert('RGB');pic.thumbnail((1160,640));x=(j%2)*1200;y=(j//2)*700
  draw.text((x+15,y+10),f.name,font=font,fill='black');im.paste(pic,(x+15,y+48))
 im.save(Q/f'projection_contact_{offset//6+1:02}.png')
print(json.dumps({'bat_seconds':elapsed,'bat_rc':res.returncode,'rendered_pages_including_docx':len(pages),'text_outside_page':bounds},ensure_ascii=False,indent=2))

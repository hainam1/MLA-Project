"""Editable empty review form. Run with bundled Python/python-docx."""
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
P=Path(__file__).resolve().parents[2]
d=Document();sec=d.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=sec.bottom_margin=Inches(.6);sec.left_margin=sec.right_margin=Inches(.65)
for name in ['Normal','Title','Heading 1','Heading 2']:
 s=d.styles[name];s.font.name='Arial';s.font.color.rgb=RGBColor(0,0,0);s.font.size=Pt(11 if name=='Normal' else 14)
 s.paragraph_format.space_after=Pt(6)
d.styles['Title'].font.size=Pt(20)
d.add_paragraph('Mẫu review tuần 10',style='Title')
d.add_paragraph('Nhóm tự điền trước hoặc sau buổi trao đổi với thầy. Tất cả ô trả lời để trống; đây không phải biên bản đã chốt.')
def table(headers,n,widths):
 t=d.add_table(rows=1,cols=len(headers));t.autofit=False
 for c,h,w in zip(t.rows[0].cells,headers,widths):c.text=h;c.width=Inches(w)
 for _ in range(n):
  row=t.add_row();row.height=Inches(.43)
  for c,w in zip(row.cells,widths):c.width=Inches(w);c.text=''
 for j,row in enumerate(t.rows):
  for c in row.cells:
   pr=c._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'6');e.set(qn('w:color'),'D9D9D9');b.append(e)
   pr.append(b)
   if j==0:
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E4E8EC');pr.append(sh)
    for r in c.paragraphs[0].runs:r.bold=True
 return t
d.add_paragraph('Ba hành động chốt với thầy',style='Heading 1')
table(['Hành động','Người phụ trách','Bằng chứng hoàn thành'],3,[2.7,1.7,2.8])
d.add_paragraph('Một điểm nhóm chưa hiểu',style='Heading 1');d.add_paragraph('____________________________________________________________________________\n____________________________________________________________________________')
d.add_paragraph('Một quyết định cần phản hồi',style='Heading 1');d.add_paragraph('____________________________________________________________________________')
p=d.add_paragraph('Gợi ý để nhóm tự chọn: đơn vị lấy mẫu lại của CI; quy tắc chọn tối thiểu 10 ca lỗi; cách gọi kết quả Test lần hai là thăm dò. Không có lựa chọn mặc định.');p.paragraph_format.space_after=Pt(8)
d.add_paragraph('Mỗi thành viên tự giải thích hoặc viết một bước pipeline',style='Heading 1')
table(['Thành viên','Bước tự chọn','Giải thích hoặc phần tự viết','Bằng chứng tự kiểm tra'],3,[1.1,1.5,2.8,1.8])
d.add_paragraph('Nguồn cấu trúc mẫu: yêu cầu người dùng; _phu/15_review_tuan10_mau/. Không ký, ghi giờ, gán đóng góp hoặc kết luận thay thành viên.').runs[0].font.size=Pt(9)
d.core_properties.author='Nhóm 03';d.core_properties.last_modified_by='Nhóm 03'
for root in [d.element,d.styles.element]:
 for border in list(root.xpath('.//w:pBdr')):border.getparent().remove(border)
d.save(P/'15_review_tuan10_mau.docx')
print('Created blank editable review DOCX')

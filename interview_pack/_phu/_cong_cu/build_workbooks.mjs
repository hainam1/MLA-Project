import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
const require=createRequire(path.resolve(root,'../scratch/interview_build_deps/loader.mjs'));
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const input=JSON.parse(await fs.readFile(path.join(here,'workbook_input.json'),'utf8'));
const qa=path.join(root,'_phu/_kiem_tra/toi_uu');
function style(sheet,range){
 const r=sheet.getRange(range);r.format.font={name:'Arial',size:14,color:'#17334B'};
 r.format.wrapText=true;r.format.verticalAlignment='center';r.format.rowHeight=42;
 r.format.borders={preset:'all',style:'thin',color:'#D9D9D9'};r.format.fill='#F0F2F4';sheet.showGridLines=false;
}
function banner(sheet,range,text){const r=sheet.getRange(range);r.merge();r.values=[[text]];r.format.font={name:'Arial',size:18,bold:true,color:'#17334B'};r.format.rowHeight=42;}
function heading(sheet,range){sheet.getRange(range).format.fill='#D7E2E8';sheet.getRange(range).format.font={name:'Arial',size:14,bold:true,color:'#17334B'};}
async function save(wb,name,renders){
 wb.recalculate();const out=await SpreadsheetFile.exportXlsx(wb);await out.save(path.join(root,name));
 for(const [sheetName,range,label]of renders){const png=await wb.render({sheetName,range,scale:1.3,format:'png'});await fs.writeFile(path.join(qa,label+'.png'),new Uint8Array(await png.arrayBuffer()));}
 console.log(name, (await wb.inspect({kind:'sheet',include:'id,name',maxChars:700})).ndjson);
}
const cases=Workbook.create();const s=cases.worksheets.add('Ca lỗi');style(s,'A1:L20');
banner(s,'A1:L1','Năm ca có hai bản nhận xét đã nộp và năm dòng bổ sung');
banner(s,'A2:L2','Phần A/B đã điền đủ · Có nội dung tự xác nhận · Giải thích/kết luận: tóm lược hai bản đã nộp, tách ý A/B');
s.getRange('A3:L3').merge();s.getRange('A3').values=[['Điểm/RF/Ridge: reports/week9/t4_reading_summary.csv. Số đếm A/B: hai bản người dùng cung cấp, kiểm đủ ô và ghép bằng 6 cột điểm/dự đoán; nguồn an toàn, hash file ở _phu/05_ca_loi/5_ca_hai_ban_da_nop.csv và kiem_tra_hai_ban_da_nop.json. Không ghép theo thứ tự R1–R5.']];s.getRange('A3:L3').format.rowHeight=66;
const headers=['essay_id','Đích sai','Điểm\nthật','RF','Ridge','Người A','Người B','Công cụ cũ ước lượng','Tình trạng xác nhận','Giải thích','Kết luận','Nguồn dòng'];
s.getRange('A5:L5').values=[headers];heading(s,'A5:L5');s.getRange('A5:L5').format.rowHeight=52;
const vals=input.cases.map(r=>[r.essay_id,r.target,Number(r.truth),Number(r.RF),Number(r.Ridge),r.reader_A_submitted_count??null,r.reader_B_submitted_count??null,Number(r.old_tool_estimate),'Có nội dung tự xác nhận; chưa kiểm chứng quy trình',r.submitted_explanation,r.submitted_conclusion,'reports/week9/t4_reading_summary.csv; _phu/05_ca_loi/5_ca_hai_ban_da_nop.csv; _phu/05_ca_loi/tom_luoc_nhan_xet_da_nop.json (ô nguồn và SHA-256 A/B)']);
while(vals.length<10)vals.push(Array(12).fill(null));s.getRange('A6:L15').values=vals;
s.getRange('A6:L15').format.rowHeight=92;s.getRange('J6:K15').format.fill='#FFF6D9';
s.getRange('A6:L10').format.rowHeight=235;
const widths=[155,75,90,105,105,90,90,135,250,420,420,340];
widths.forEach((w,i)=>s.getRangeByIndexes(0,i,20,1).format.columnWidthPx=w);
s.getRange('C6:H15').setNumberFormat('0.0000');s.getRange('C6:C15').setNumberFormat('0.0');s.getRange('F6:G15').setNumberFormat('0');
s.getRange('A17:L17').merge();s.getRange('A17').values=[['Hai bản có đủ 40 ô Phần A/B và 6 ô xác nhận mỗi người. Nội dung tự xác nhận đã có; file không chứng minh lịch sử mở sheet, đọc mù hoặc không trao đổi. Hai cột cuối tóm lược nhận xét đã nộp theo yêu cầu mới; không phải nguyên nhân được kiểm chứng. Năm dòng bổ sung vẫn trống. Công cụ cũ vẫn là ước lượng.']];s.getRange('A17:L17').format.rowHeight=62;
s.getRange('A19:L19').merge();s.getRange('A19').values=[['Quy tắc gợi ý bổ sung: từ 276 ca cùng sai development, loại ID đã đọc, xếp D giảm dần và essay_id tăng dần, lấy 5 đầu; thành viên tự đọc. Nguồn: _phu/05_ca_loi/README.md.']];s.getRange('A19:L19').format.rowHeight=62;
s.freezePanes.freezeRows(5);
const priorCase=path.join(qa,'05_ca_loi_truoc_nhan_ban_nop.xlsx');
try{await fs.access(priorCase);}catch{await fs.copyFile(path.join(root,'05_ca_loi.xlsx'),priorCase);}
await save(cases,'05_ca_loi.xlsx',[['Ca lỗi','A1:L19','05_ca_loi']]);
if(process.argv.includes('--cases-only'))process.exit(0);
const contrib=Workbook.create();const log=contrib.worksheets.add('Nhật ký đóng góp');const ai=contrib.worksheets.add('Khai báo AI');
style(log,'A1:F22');banner(log,'A1:F1','Mẫu trống nhật ký đóng góp và phần từng thành viên');
log.getRange('A3:E3').values=[['Ngày','Câu hỏi','Giả định trước khi chạy','Kết quả','Thay đổi']];heading(log,'A3:E3');
log.getRange('A4:E9').values=Array.from({length:6},()=>Array(5).fill(null));log.getRange('A4:E9').format.rowHeight=55;log.getRange('A4:E9').format.fill='#FFF6D9';
banner(log,'A11:F11','Mỗi thành viên tự điền một quyết định và cách kiểm chứng');
log.getRange('A13:D13').values=[['Nhãn thành viên','Quyết định mình sở hữu','Bằng chứng','Cách kiểm tra khi dùng AI']];heading(log,'A13:D13');
log.getRange('A14:D16').values=[['Nam',null,null,null],['Giang',null,null,null],['Linh',null,null,null]];log.getRange('B14:D16').format.fill='#FFF6D9';log.getRange('A14:D16').format.rowHeight=88;
banner(log,'A18:F18','Không gán người phụ trách không ký không ghi giờ thay thành viên');
log.getRange('A20:F20').merge();log.getRange('A20').values=[['Nguồn: mẫu theo yêu cầu người dùng; _phu/09_dong_gop_va_ai/. Không phải nhật ký đã hoàn tất.']];
[130,290,340,340,290,120].forEach((w,i)=>log.getRangeByIndexes(0,i,22,1).format.columnWidthPx=w);
style(ai,'A1:C17');banner(ai,'A1:C1','NHÁP TRỐNG khai báo AI cần thành viên xác nhận');
ai.getRange('A3:C3').values=[['Trường cần tự xác nhận','Nội dung thành viên tự điền','Bằng chứng / cách kiểm tra']];heading(ai,'A3:C3');
ai.getRange('A4:C11').values=[['Agent mã',null,null],['Trợ lý viết',null,null],['Tên công cụ và model',null,null],['Mục đích thực tế',null,null],['Artifact chịu ảnh hưởng',null,null],['Người kiểm chứng và cách kiểm chứng',null,null],['Khoảng trống lịch sử cần bổ sung',null,null],['Xác nhận của thành viên',null,null]];
ai.getRange('B4:C11').format.fill='#FFF6D9';ai.getRange('A4:C11').format.rowHeight=72;
ai.getRange('A13:C13').merge();ai.getRange('A13').values=[['Nguồn đối chiếu: docs/llm_disclosure.md có Working Record và Week 9 nhưng thiếu nhật ký chi tiết mọi lần dùng. Không suy diễn lịch sử hay đóng góp thay thành viên.']];ai.getRange('A13:C13').format.rowHeight=80;
[330,540,540].forEach((w,i)=>ai.getRangeByIndexes(0,i,17,1).format.columnWidthPx=w);
await save(contrib,'09_dong_gop_va_ai.xlsx',[['Nhật ký đóng góp','A1:F20','09_dong_gop'],['Khai báo AI','A1:C13','09_ai']]);

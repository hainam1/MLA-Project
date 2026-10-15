import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'reports/week9');
const privateDir=path.join(out,'t4_private');
const data=JSON.parse(await fs.readFile(path.join(privateDir,'payload.json'),'utf8'));
const wb=Workbook.create();
function col(i) {let s=''; for (let n=i+1;n>0;n=Math.floor((n-1)/26)) s=String.fromCharCode(65+(n-1)%26)+s; return s;}
function table(name,columns,rows) {
  const s=wb.worksheets.add(name); const end=col(columns.length-1); const last=rows.length+1;
  const matrix=[columns,...rows.map(r=>columns.map(c=>r[c]??''))];
  s.getRange(`A1:${end}${last}`).values=matrix;
  const range=s.getRange(`A1:${end}${last}`);
  range.format.font={name:'Arial',size:10,color:'#243244'};
  range.format.rowHeight=36;
  range.format.columnWidth=17;
  range.format.verticalAlignment='top';
  range.format.wrapText=true;
  s.getRange(`A1:${end}1`).format={fill:'#283A55',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:76,horizontalAlignment:'center',verticalAlignment:'center'};
  s.showGridLines=false;
  for (let i=0;i<columns.length;i++) {
    const c=columns[i]; const letter=col(i); const r=s.getRange(`${letter}2:${letter}${last}`);
    if (['essay_id','sample_group','quadrant','prompt_text_status','selection_provenance'].includes(c)) s.getRange(`${letter}1:${letter}${last}`).format.columnWidth=29;
    if (c==='prompt_text') s.getRange(`${letter}1:${letter}${last}`).format.columnWidth=35;
    if (['y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G','e_RF_V','e_RF_G','e_Ridge_V','e_Ridge_G','D','rater1_V','rater2_V','rater1_G','rater2_G','mean_word_frequency','detected_grammar_errors_per_100_words'].includes(c)) r.setNumberFormat('0.000');
    if (c==='word_count') r.setNumberFormat('0');
    if (data.rubric.some(x=>x.criterion===c)) {r.format.fill='#FFF5CD';s.getRange(`${letter}1:${letter}${last}`).format.columnWidth=27;}
    if (c.startsWith('source_')) s.getRange(`${letter}1:${letter}${last}`).format.columnWidth=26;
    if (c==='confidence') r.dataValidation={rule:{type:'list',values:['low','med','high']}};
    if (c==='essay_text') {
      s.getRange(`${letter}1:${letter}${last}`).format.columnWidth=160;
      r.format.wrapText=true;
      // Full value retained; ordinary Excel rows cannot exceed 409 points. Read long
      // essays in the cell's formula bar / expanded editor rather than truncating values.
    }
  }
  rows.forEach((r,i)=>{ const lines=String(r.essay_text??'').split('\n').reduce((n,t)=>n+Math.max(1,Math.ceil(t.length/160)),0); s.getRange(`A${i+2}:${end}${i+2}`).format.rowHeight=Math.min(409,Math.max(84,(lines+3)*12)); });
  s.tables.add(`A1:${end}${last}`,true,name==='reading_sheet'?'ReadingRecords':'ProposedRecords');
  s.freezePanes.freezeRows(1); s.freezePanes.freezeColumns(2);
  return s;
}
table('reading_sheet',data.columns,data.rows);
const rubric=wb.worksheets.add('rubric');
rubric.getRange(`A1:C${data.rubric.length+1}`).values=[['criterion','definition','how_to_decide'],...data.rubric.map(r=>[r.criterion,r.definition,''])];
rubric.getRange(`A1:C${data.rubric.length+1}`).format={font:{name:'Arial',size:10,color:'#243244'},wrapText:true,rowHeight:58,verticalAlignment:'center'};
rubric.getRange('A1:C1').format={fill:'#283A55',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:30};
rubric.getRange(`A1:A${data.rubric.length+1}`).format.columnWidth=34;
rubric.getRange(`B1:B${data.rubric.length+1}`).format.columnWidth=84;
rubric.getRange(`C1:C${data.rubric.length+1}`).format.columnWidth=50;
rubric.getRange(`C2:C${data.rubric.length+1}`).format.fill='#FFF5CD';
rubric.showGridLines=false;
if (data.supplement.length) table('supplement_proposed',data.columns,data.supplement);
wb.recalculate();
// Inspect numeric/ID and human-input regions without printing private student text.
const inspect=await wb.inspect({kind:'table',range:'reading_sheet!A1:B3',include:'values',tableMaxRows:3,tableMaxCols:2,maxChars:1000});
console.log('WORKBOOK_INSPECT '+inspect.ndjson);
for (const name of ['reading_sheet','rubric',...(data.supplement.length?['supplement_proposed']:[])]) {
  const range=name==='rubric'?'A1:C6':'A1:C3';
  const preview=await wb.render({sheetName:name,range,scale:1.2,format:'png'});
  await fs.writeFile(path.join(privateDir,`${name}_preview.png`),new Uint8Array(await preview.arrayBuffer()));
}
const humanStart=col(data.columns.indexOf('off_topic'));const humanEnd=col(data.columns.indexOf('reader_initials'));
const review=await wb.render({sheetName:'reading_sheet',range:`${humanStart}1:${humanEnd}3`,scale:1,format:'png'});
await fs.writeFile(path.join(privateDir,'team_fields_preview.png'),new Uint8Array(await review.arrayBuffer()));
const xlsx=await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(privateDir,'reading_sheet_export.xlsx'));
console.log('WORKBOOK_EXPORT reading_sheet; rubric'+(data.supplement.length?'; supplement_proposed':'')+'; blank team input cells; previews saved privately');

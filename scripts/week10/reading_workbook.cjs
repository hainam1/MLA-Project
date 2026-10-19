// The sample is already fixed by random_reading.py. No data source files opened.
const fs = require('node:fs/promises');
const path = require('node:path');
const {createRequire} = require('node:module');
const bundledRequire = createRequire(path.join(process.env.W10_RUNTIME, 'package.json'));
const {Workbook, SpreadsheetFile} = bundledRequire('@oai/artifact-tool');

async function main() {
  let input='';
  process.stdin.setEncoding('utf8');
  for await (const chunk of process.stdin) input+=chunk;
  const data=JSON.parse(input);
  const wb=Workbook.create();
  function build(name, headers, records) {
    const sheet=wb.worksheets.add(name);
    const last=records.length+1;
    const end=String.fromCharCode(64+headers.length);
    sheet.getRange(`A1:${end}${last}`).values=[headers,...records.map(r=>headers.map(k=>r[k]))];
    sheet.getRange(`A1:${end}${last}`).format={font:{name:'Arial',size:11,color:'#243244'},columnWidth:23,rowHeight:24,verticalAlignment:'center'};
    sheet.getRange(`A1:${end}1`).format={fill:'#283A55',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:64,horizontalAlignment:'center',verticalAlignment:'center'};
    sheet.showGridLines=false;
    sheet.getRange(`A1:A${last}`).format.columnWidth=24;
    if (name==='reading_sheet') {
      sheet.getRange(`B1:B${last}`).format.columnWidth=15;
      sheet.getRange(`C1:C${last}`).format.columnWidth=14;
      sheet.getRange(`D1:D${last}`).format.columnWidth=150;
      sheet.getRange(`D2:D${last}`).format.wrapText=true;
      sheet.getRange(`D2:D${last}`).format.verticalAlignment='top';
      sheet.getRange(`E1:E${last}`).format.columnWidth=34;
      sheet.getRange(`E2:E${last}`).format.wrapText=true;
      sheet.getRange(`F1:H${last}`).format.columnWidth=29;
      sheet.getRange(`F2:H${last}`).format.fill='#FFF5CD';
      sheet.getRange(`G2:H${last}`).dataValidation={rule:{type:'list',values:['low','mid','high']}};
      sheet.getRange(`F2:F${last}`).setNumberFormat('0');
      records.forEach((r,i)=>{
        const lines=r.essay_text.split('\n').reduce((n,s)=>n+Math.max(1,Math.ceil(s.length/145)),0);
        sheet.getRange(`A${i+2}:H${i+2}`).format.rowHeight=Math.min(409,Math.max(70,16*(lines+2)));
      });
      sheet.tabColor='#283A55';
    } else {
      sheet.getRange(`B2:G${last}`).setNumberFormat('0.000');
      sheet.getRange(`H2:H${last}`).setNumberFormat('0');
      sheet.getRange(`I2:I${last}`).setNumberFormat('0.000');
      sheet.getRange(`J2:J${last}`).setNumberFormat('0');
      sheet.getRange(`K2:K${last}`).setNumberFormat('0.000');
      sheet.getRange(`I1:K${last}`).format.columnWidth=34;
    }
    sheet.tables.add(`A1:${end}${last}`,true,name==='reading_sheet'?'RandomReading':'UnblindAfter');
    sheet.freezePanes.freezeRows(1);
    sheet.freezePanes.freezeColumns(1);
    return sheet;
  }
  build('reading_sheet',data.reading_headers,data.reading);
  build('unblind_after',data.unblind_headers,data.unblind);
  wb.recalculate();
  // Inspect headers only: never log text, truth, predictions or tool values.
  for (const [name,headers] of [['reading_sheet',data.reading_headers],['unblind_after',data.unblind_headers]]) {
    const end=String.fromCharCode(64+headers.length);
    const result=await wb.inspect({kind:'table',range:`${name}!A1:${end}1`,include:'values',tableMaxRows:1,tableMaxCols:headers.length,maxChars:4000});
    if (!result.ndjson) throw new Error('Header inspection failed');
    const preview=await wb.render({sheetName:name,range:`A1:${end}1`,scale:1,format:'png'});
    await fs.writeFile(path.join(process.env.W10_PREVIEW,name+'_headers.png'),new Uint8Array(await preview.arrayBuffer()));
  }
  const exported=await SpreadsheetFile.exportXlsx(wb);
  await exported.save(process.env.W10_XLSX);
}
main().catch(error=>{console.error(error);process.exitCode=1;});

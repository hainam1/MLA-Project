const fs = require('node:fs/promises');
const path = require('node:path');
const {createRequire} = require('node:module');
const requireBundled=createRequire(path.join(process.env.R2_RUNTIME,'package.json'));
const {Workbook,SpreadsheetFile}=requireBundled('@oai/artifact-tool');

async function main() {
  let input=''; process.stdin.setEncoding('utf8');
  for await (const chunk of process.stdin) input+=chunk;
  const data=JSON.parse(input);
  const headers=['essay_id','first150_words','reader2_errors_first150','notes'];
  const workbook=Workbook.create();
  const sheet=workbook.worksheets.add('reader2');
  sheet.getRange('A1:D7').values=[headers,...data.rows.map(r=>headers.map(k=>r[k]))];
  sheet.getRange('A1:D7').format={font:{name:'Arial',size:11,color:'#243244'},verticalAlignment:'top',rowHeight:200,wrapText:true};
  sheet.getRange('A1:D1').format={fill:'#283A55',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:52,horizontalAlignment:'center',verticalAlignment:'center',wrapText:true};
  sheet.getRange('A1:A7').format.columnWidth=18;
  sheet.getRange('B1:B7').format.columnWidth=120;
  sheet.getRange('C1:C7').format.columnWidth=29;
  sheet.getRange('D1:D7').format.columnWidth=38;
  sheet.getRange('C2:D7').format.fill='#FFF5CD';
  sheet.getRange('C2:C7').setNumberFormat('0');
  sheet.showGridLines=false;
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(1);
  sheet.tables.add('A1:D7',true,'SecondReader');
  workbook.recalculate();
  if (JSON.stringify(sheet.getRange('A1:D1').values[0])!==JSON.stringify(headers)) throw new Error('Header check failed');
  // Header-only preview: never render essay text into a user-visible log.
  const preview=await workbook.render({sheetName:'reader2',range:'A1:D1',scale:1,format:'png'});
  await fs.writeFile(path.join(process.env.R2_RUNTIME,'headers.png'),new Uint8Array(await preview.arrayBuffer()));
  const exported=await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(process.env.R2_OUTPUT);
  await fs.rm(process.env.R2_OUTPUT+'.inspect.ndjson',{force:true});
}
main().catch(error=>{console.error('R2_AUTHORING_ERROR '+error.name);process.exitCode=1;});

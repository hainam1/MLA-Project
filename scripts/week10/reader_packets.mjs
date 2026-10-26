// Shared workbook renderer. Payloads stay in memory; never echo cell values/errors.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

let payloadText = '';
for await (const chunk of process.stdin) payloadText += chunk;
try {
  const p = JSON.parse(payloadText);
  const dependencies = process.env.READER_NODE_MODULES || path.join(os.homedir(),
    '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
  const runtime = path.join(os.tmpdir(), 'codex-independent-readers-runtime');
  await fs.mkdir(runtime, { recursive: true });
  try { await fs.symlink(dependencies, path.join(runtime, 'node_modules'), 'junction'); }
  catch (error) { if (error.code !== 'EEXIST') throw error; }
  const require = createRequire(path.join(runtime, 'loader.mjs'));
  const { Workbook, SpreadsheetFile } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
  const wb = Workbook.create();
  const color = '#263B58';
  function base(name, title, end = 'D', last = 60) {
    const s = wb.worksheets.add(name);
    s.showGridLines = false;
    s.getRange(`A1:${end}${last}`).format = {
      font: { name: 'Arial', size: 11, color: '#223047' }, rowHeight: 28,
      columnWidth: 27, wrapText: true, verticalAlignment: 'top'
    };
    s.mergeCells(`A2:${end}2`);
    s.getRange('A2').values = [[title]];
    s.getRange(`A2:${end}2`).format.font = { name: 'Arial', size: 16, bold: true, color };
    s.getRange(`A2:${end}2`).format.rowHeight = 40;
    return s;
  }
  function val(s, ref, v) { s.getRange(ref).values = [[v ?? null]]; }
  function header(s, range) {
    s.getRange(range).format = { fill: color, font: { name: 'Arial', size: 11, bold: true, color: '#FFFFFF' },
      wrapText: true, verticalAlignment: 'center', horizontalAlignment: 'center', rowHeight: 38 };
  }
  function choices(s, ref, values) { s.getRange(ref).dataValidation = { rule: { type: 'list', values } }; }
  function wide(s, ref, text, height = 36) {
    s.mergeCells(ref); s.getRange(ref).values = [[text]]; s.getRange(ref).format.rowHeight = height;
  }
  if (p.mode === 'comparison') {
    const s = base('So sánh', 'So sánh hai bản đọc độc lập', 'K', p.rows.length+6);
    s.getRange('A5:K5').values = [p.columns]; header(s, 'A5:K5');
    s.getRange('A5:K5').format.rowHeight = 60;
    s.getRange(`A6:K${p.rows.length+5}`).values = p.rows;
    s.getRange(`A6:K${p.rows.length+5}`).format.rowHeight = 140;
    s.getRange(`D5:I${p.rows.length+5}`).format.columnWidth = 55;
    s.freezePanes.freezeRows(5);
  } else {
    const group = 'điểm từ 4,0 trở lên ở đích bị sai';
    const guide = base('Hướng dẫn', 'Phiếu đọc độc lập — người ' + (p.reader || '___'), 'D', 26);
    wide(guide, 'A4:D4', 'Nhóm: ' + group, 34);
    const instructions = [
      `Seed xáo thứ tự: ${p.seed}. Mã R1–R5 chỉ có nghĩa trong file của bạn. Ô màu vàng dành cho người đọc, hiện để trống.`,
      '1. Điền họ tên và thời gian bắt đầu ở sheet Xác nhận. Không trao đổi hoặc xem bản của người kia trước khi cả hai nộp.',
      '2. Đọc sheet Bài và điểm. Đích bị sai được ghi ở đầu mỗi bài. Điền toàn bộ Phần A, chưa mở Thông tin mô hình.',
      '3. Gửi một bản sao giữ nguyên Phần A cho điều phối viên; tự ghi thời gian nộp A. Chỉ sau đó mới mở sheet 4.',
      '4. Đọc Thông tin mô hình, điền Phần B. Không sửa Phần A. Gửi bản cuối, ghi giờ nộp B, tự tick xác nhận độc lập và ký tên.',
      'Lỗi ngữ pháp: tự đếm trong 150 từ đầu (tách từ theo khoảng trắng). Nếu đoạn ngắn hơn, đếm toàn đoạn. Số 0 là hợp lệ.',
      'Mọi ô trả lời đều bắt buộc. Nếu không có nhận xét, chính người đọc ghi “không có”; không để trống. Mỗi ô lý do/nhận xét tối đa 3 câu.',
      'Phần B: nhập một hoặc nhiều mã nguyên nhân 1–8, ngăn bằng dấu chấm phẩy, ví dụ 1;3. Không có chọn sẵn. Nếu chọn 8, nhận xét bắt đầu “Khác:” và giải thích.',
      'Thời gian: YYYY-MM-DD HH:MM theo giờ Việt Nam (UTC+07:00). Ô xác nhận: chọn ☑ sau khi tự xác nhận; không tự động điền.',
      'Dữ liệu chỉ có nhãn/chủ đề trong trường prompt, không xác nhận đó là nguyên văn đề. Điểm thật là điểm tổng hợp đã lưu.',
      'Nguồn: validation_783.csv (bài, nhãn đề); development_features_with_targets.csv (đặc trưng/điểm); phase6/validation_predictions.csv (RF/Ridge).',
    ];
    instructions.forEach((v, i) => wide(guide, `A${i+6}:D${i+6}`, v, 52));
    wide(guide, 'A18:D18', 'Danh sách nguyên nhân chuẩn — chỉ chọn sau khi nộp Phần A', 36);
    p.causes.forEach((v, i) => wide(guide, `A${i+19}:D${i+19}`, `${i+1}. ${v}`, 28));

    const essays = base('Bài và điểm', 'Bài và điểm — ' + group, 'D', 260);
    essays.freezePanes.freezeRows(3);
    let row = 5;
    for (const item of p.items) {
      wide(essays, `A${row}:D${row}`, `${item.code} — Đích bị sai: ${item.target || '___'}`, 34);
      header(essays, `A${row}:D${row}`);
      essays.getRange(`A${row+1}:D${row+1}`).values = [['Từ vựng thật', item.Vocabulary ?? null, 'Ngữ pháp thật', item.Grammar ?? null]];
      wide(essays, `A${row+2}:D${row+2}`, 'Nhãn đề (prompt): ' + (item.prompt || 'chưa có dữ liệu'), 44);
      let rest = item.text || '';
      let chunks = [];
      while (rest.length) {
        let cut = rest.length <= 300 ? rest.length : rest.lastIndexOf(' ', 300)+1;
        if (cut < 1) cut = Math.min(300, rest.length);
        chunks.push(rest.slice(0, cut)); rest = rest.slice(cut);
      }
      if (!chunks.length) chunks = ['[Mẫu rỗng — không có văn bản bài]'];
      row += 4;
      for (const chunk of chunks) { wide(essays, `A${row}:D${row}`, chunk, 70); row++; }
      row += 2;
    }

    const judgments = ['hợp lý', 'hơi cao', 'hơi thấp', 'không chắc'];
    const errors = ['dự đoán thấp hơn điểm thật ở Từ vựng', 'dự đoán thấp hơn điểm thật ở Ngữ pháp', 'cả hai', 'khác'];
    function partSheet(part) {
      const s = base('Phần ' + part, part === 'A' ? 'Phần A — điền trước khi xem sheet 4' : 'Phần B — điền sau khi xem sheet 4', 'B', 40);
      s.getRange('A1:A40').format.columnWidth = 48; s.getRange('B1:B40').format.columnWidth = 90;
      const labels = part === 'A' ? ['Điểm thật ở đích bị sai có hợp lý?', 'Lý do (tối đa 3 câu)', 'Số lỗi ngữ pháp trong 150 từ đầu', 'Ghi chú từ vựng'] :
        ['Máy sai ở đâu?', 'Mã nguyên nhân (1–8; nhiều mã cách bởi ;)', 'Mức tự tin', 'Nhận xét tự do (tối đa 3 câu; chọn 8 thì ghi Khác:)'];
      for (let i = 0; i < 5; i++) {
        const r = 5 + i*7;
        wide(s, `A${r}:B${r}`, `${p.items[i].code} — Đích bị sai: ${p.items[i].target || '___'}`, 32);
        header(s, `A${r}:B${r}`);
        labels.forEach((label, j) => {
          val(s, `A${r+j+1}`, label); s.getRange(`B${r+j+1}`).format.fill = '#FFF4CE';
          s.getRange(`B${r+j+1}`).setNumberFormat('@');
        });
        s.getRange(`A${r+2}:B${r+2}`).format.rowHeight = 90;
        s.getRange(`A${r+4}:B${r+4}`).format.rowHeight = 90;
        if (part === 'A') {
          choices(s, `B${r+1}`, judgments);
          s.getRange(`B${r+3}`).setNumberFormat('0');
          s.dataValidations.add({range:`B${r+3}`,rule:{type:'whole',operator:'between',formula1:0,formula2:10000}});
        } else {
          choices(s, `B${r+1}`, errors); choices(s, `B${r+3}`, ['cao', 'vừa', 'thấp']);
        }
      }
    }
    partSheet('A');
    const model = base('Thông tin mô hình', 'Chỉ mở sau khi đã nộp Phần A', 'V', 12);
    model.unmergeCells('A2:V2'); model.mergeCells('A2:G2');
    model.getRange('A2:G2').format.rowHeight = 44;
    val(model, 'A3', 'Công cụ cũ: ước lượng 150 từ đầu = tỷ lệ toàn bài × min(150, số từ)/100; không đếm trực tiếp đoạn đầu.');
    model.mergeCells('A3:G3'); model.getRange('A3:G3').format.rowHeight = 50;
    const cols = ['Mã tạm', 'Từ vựng thật', 'Ngữ pháp thật', 'RF Từ vựng', 'RF Ngữ pháp', 'Ridge Từ vựng', 'Ridge Ngữ pháp', ...p.features, 'Công cụ cũ: ước lượng/150 từ đầu'];
    // 7 fixed columns + 14 features + 1 count = 22 columns (A:V).
    model.getRange('A5:V5').values = [cols]; header(model, 'A5:V5');
    model.getRange('A5:V5').format.rowHeight = 110;
    model.getRange('A6:V10').values = p.items.map(it => [it.code, it.Vocabulary ?? null, it.Grammar ?? null,
      it.predictions?.random_forest_vocabulary ?? null, it.predictions?.random_forest_grammar ?? null,
      it.predictions?.ridge_vocabulary ?? null, it.predictions?.ridge_grammar ?? null,
      ...p.features.map(f => it.features?.[f] ?? null), it.old_tool_first150_estimate ?? null]);
    model.getRange('A5:V10').format.columnWidth = 23; model.getRange('B6:V10').setNumberFormat('0.000000');
    model.freezePanes.freezeRows(5); model.freezePanes.freezeColumns(1);
    partSheet('B');
    const confirm = base('Xác nhận', 'Người đọc tự xác nhận và ký', 'B', 12);
    confirm.getRange('A1:A12').format.columnWidth = 72; confirm.getRange('B1:B12').format.columnWidth = 55;
    ['Họ tên', 'Thời gian bắt đầu', 'Thời gian nộp Phần A', 'Thời gian nộp Phần B',
      'Tôi chưa xem nhận xét của người đọc kia trước khi nộp (chọn ☑)', 'Chữ ký / tên'].forEach((label,i) => {
        val(confirm, `A${5+i}`,label); confirm.getRange(`B${5+i}`).format.fill = '#FFF4CE';
      });
    confirm.getRange('A5:B10').format.rowHeight = 52;
    confirm.getRange('B5:B10').setNumberFormat('@');
    choices(confirm, 'B9', ['☑']);
    // Fixtures contain synthetic answers only, never used by the real packet command.
    if (p.synthetic_data === true && p.responses) {
      for (const [sheet, entries] of Object.entries(p.responses))
        for (const [ref,value] of Object.entries(entries)) val(wb.worksheets.getItem(sheet), ref, value);
    }
  }
  wb.recalculate();
  if (p.preview_dir) {
    await fs.mkdir(p.preview_dir, { recursive: true });
    const views = [['Hướng dẫn','A2:D12'],['Bài và điểm','A2:D12'],['Phần A','A2:B10'],
      ['Thông tin mô hình','A2:G10'],['Phần B','A2:B10'],['Xác nhận','A2:B10']];
    for (let i=0;i<views.length;i++) {
      const blob = await wb.render({sheetName:views[i][0],range:views[i][1],scale:1,format:'png'});
      await fs.writeFile(path.join(p.preview_dir,`sheet_${i+1}.png`),new Uint8Array(await blob.arrayBuffer()));
    }
  }
  await fs.mkdir(path.dirname(p.output), { recursive:true });
  await (await SpreadsheetFile.exportXlsx(wb)).save(p.output);
} catch {
  process.stderr.write('Workbook rendering failed (cell values suppressed).\n');
  process.exitCode = 2;
}

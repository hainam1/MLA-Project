"""Part A only. Reuse the locked counter; never fit or count development in full."""
from pathlib import Path
import argparse
import contextlib
import csv
import hashlib
import io
import json
import os
import posixpath
import sys
import time
import zipfile
import xml.etree.ElementTree as ET

import gec_compare as g

LOCK = '68c050d3716197293713e753f4a1391ff922e3028932a950bd230921a2fa0240'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def reader_counts():
    """Resolve only ID and count cells, never essay cells or hidden-sheet values."""
    with zipfile.ZipFile(g.audit_read(g.ROOT / g.INPUTS[8])) as z:
        strings = ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS) if 'xl/sharedStrings.xml' in z.namelist() else []
        def value(cell):
            node = cell.find('s:v', NS)
            raw = node.text if node is not None else ''
            if cell.get('t') == 's':
                return ''.join(strings[int(raw)].itertext())
            if cell.get('t') == 'inlineStr':
                return ''.join(cell.find('s:is', NS).itertext())
            return raw
        rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheets = ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS)
        sheet = next(s for s in sheets if s.get('name') == 'reading_sheet')
        target = rels[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        rows = ET.fromstring(z.read(member)).findall('s:sheetData/s:row', NS)
        headers = {''.join(c for c in cell.get('r') if c.isalpha()): value(cell).strip() for cell in rows[0].findall('s:c', NS)}
        selected = {col: ('essay_id' if title == 'essay_id' else 'reader') for col, title in headers.items()
                    if title in {'essay_id', 'reader_errors_first150', 'Số lỗi ngữ pháp (150 từ đầu)'}}
        assert list(selected.values()).count('essay_id') == list(selected.values()).count('reader') == 1
        result = {}
        for row in rows[1:]:
            record = {}
            for cell in row.findall('s:c', NS):
                col = ''.join(c for c in cell.get('r') if c.isalpha())
                if col in selected:
                    assert cell.find('s:f', NS) is None
                    record[selected[col]] = value(cell).strip()
            if record.get('essay_id'):
                assert record['essay_id'] not in result
                result[record['essay_id']] = float(record['reader'])
        assert len(result) == 36
        return result


def samples():
    random_ids = g.read_csv(g.INPUTS[7])
    week9 = g.read_csv(g.INPUTS[2])
    readers = reader_counts()
    assert len(random_ids) == 36 and len(week9) == 32
    assert set(readers) == {r['essay_id'] for r in random_ids}
    eligible = {r['essay_id']: r for r in g.read_csv(g.INPUTS[0])}
    records = []
    for group, source in [('random36', random_ids), ('week9_32', week9)]:
        for r in source:
            essay_id = r['essay_id']
            e = eligible[essay_id]
            reader = readers[essay_id] if group == 'random36' else float(r['reader_error_count_first150'])
            assert reader >= 0 and reader.is_integer()
            n = float(e['word_count'])
            truth = (float(e['Vocabulary']) + float(e['Grammar']))/2
            band = '<2.5' if truth < 2.5 else ('>4.0' if truth > 4 else '2.5-4.0')
            records.append(dict(essay_id=essay_id, sample_group=group,
                                subgroup=r.get('sample_group', ''), band=band, reader=reader,
                                LT_estimate=float(e['detected_grammar_errors_per_100_words'])*min(150,n)/100))
            if group == 'random36':
                assert e['split'] == 'validation'
    records.sort(key=lambda r: (r['sample_group'], r['essay_id']))
    assert len({r['essay_id'] for r in records}) == 68, 'Samples must comprise 68 unique essays'
    print('JOIN_AUDIT random=36; week9=32; unique=68; all eligible; random subset is Validation; workbook only ID/reader cells resolved', flush=True)
    return records


def count_sample():
    started = time.perf_counter()
    records = samples()
    selected = {r['essay_id'] for r in records}
    texts = {}
    for path in g.INPUTS[3:5]:
        for row in g.read_csv(path, {'essay_id', 'essay_text'}):
            if row['essay_id'] in selected:
                assert row['essay_id'] not in texts
                texts[row['essay_id']] = row['essay_text']
    assert set(texts) == selected
    counter = g.Counter(g.OUT/'gec_assets/model', g.OUT/'gec_assets/verb-form-vocab.txt')
    path = g.OUT/'gec_part_a_counts.jsonl'
    assert not path.exists(), 'Refusing to rerun completed or partial Part A; preserve the original timing and records'
    inference_started = time.perf_counter()
    with path.open('x', encoding='utf-8') as stream:
        for i, record in enumerate(records, 1):
            text = ' '.join(texts[record['essay_id']].split()[:150])
            before = time.perf_counter()
            try:
                counts = counter.count(text)
            except Exception as error:
                print('COUNT_FAILURE id='+record['essay_id']+' type='+type(error).__name__, flush=True)
                raise RuntimeError('Part A failure; essay text suppressed') from None
            record.update(counts, config_sha256=LOCK, seconds=time.perf_counter()-before)
            stream.write(json.dumps(record, sort_keys=True)+'\n')
            stream.flush()
            print(f'PART_A_PROGRESS {i}/68 elapsed_seconds={time.perf_counter()-inference_started:.6f}', flush=True)
    elapsed = time.perf_counter()-inference_started
    end_to_end = time.perf_counter()-started
    timing = dict(n=68, count_seconds=elapsed, seconds_per_essay=elapsed/68,
                  end_to_end_seconds=end_to_end, expected_seconds=68*6.18,
                  actual_minus_expected=elapsed-68*6.18, actual_expected_ratio=elapsed/(68*6.18),
                  arithmetic=f'68*6.18={68*6.18:.17g}; {elapsed:.17g}/68={elapsed/68:.17g}; {elapsed:.17g}-{68*6.18:.17g}={elapsed-68*6.18:.17g}',
                  scope='first150 whitespace words only; earlier benchmark used full essays; loading excluded from count_seconds', config_sha256=LOCK)
    (g.OUT/'gec_part_a_timing.json').write_text(json.dumps(timing, indent=2),encoding='utf-8')
    print('PART_A_TIMING '+json.dumps(timing,sort_keys=True), flush=True)


def analyze():
    import numpy as np
    import scipy
    from scipy.stats import rankdata, pearsonr, spearmanr
    print('ANALYSIS_VERSIONS numpy='+np.__version__+' scipy='+scipy.__version__+' Python='+sys.version.split()[0])
    print('PRODUCER_SHA256='+hashlib.sha256(g.audit_read(Path(__file__)).read_bytes()).hexdigest())
    print('LOCKED_COUNTER_SHA256='+hashlib.sha256(g.audit_read(Path(g.__file__)).read_bytes()).hexdigest())
    timing = json.loads(g.audit_read(g.OUT/'gec_part_a_timing.json').read_text())
    print('PART_A_TIMING '+json.dumps(timing,sort_keys=True))
    raw = g.audit_read(g.OUT/'gec_part_a_run.log').read_bytes()
    run_log = raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')
    audit_lines = [line for line in run_log.splitlines() if line.startswith('READ_AUDIT ')]
    assert not any(any(term in line.casefold() for term in ['test', 'full_clean_corpus', 'combined']) for line in audit_lines)
    print('COUNT_PROCESS_READ_AUDIT_BEGIN')
    print('\n'.join(audit_lines))
    print('COUNT_PROCESS_READ_AUDIT_END; forbidden artifact path matches=0; Python open audit plus offline socket guard, not universal OS access proof')
    rows = [json.loads(line) for line in g.audit_read(g.OUT/'gec_part_a_counts.jsonl').read_text().splitlines()]
    assert len(rows) == 68 and len({r['essay_id'] for r in rows}) == 68
    for row in rows:
        assert row['config_sha256'] == LOCK and row['words'] <= 150
        assert row['edits_all'] == sum(row['per_type'].values())
        assert row['edits_grammar'] == sum(v for t,v in row['per_type'].items() if t.split(':',1)[-1].split(':')[0] not in {'SPELL','PUNCT','ORTH'})
    # Per-essay tables remain git-ignored. Aggregate output is appended separately.
    table_path = g.OUT/'gec_part_a_68.csv'
    columns = ['essay_id','sample_group','subgroup','band','reader','LT_estimate','edits_grammar','edits_all']
    with table_path.open('w',encoding='utf-8',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore'); writer.writeheader(); writer.writerows(rows)
    print('PER_ESSAY_TABLE '+str(table_path)+'; LT_estimate is historical scaled rate, not an observed first150 LT count')
    def corr(x,y):
        a=x-x.mean(); b=y-y.mean()
        aa, bb, ab = float(a@a), float(b@b), float(a@b)
        return (ab/np.sqrt(aa*bb) if aa*bb>0 else float('nan')), (aa,bb,ab)
    def values(reader,tool):
        pearson,_=corr(reader,tool)
        spearman,_=corr(rankdata(reader),rankdata(tool))
        return dict(reader_mean=reader.mean(), tool_mean=tool.mean(), reader_median=np.median(reader),
                    tool_median=np.median(tool), Spearman=spearman, Pearson=pearson,
                    absolute_mean_gap=abs(tool.mean()-reader.mean()),
                    mean_ratio=tool.mean()/reader.mean() if reader.mean() else np.nan)
    metrics=[]
    for group in ['pooled68','random36','week9_32']:
        selected=[r for r in rows if group=='pooled68' or r['sample_group']==group]
        reader=np.array([r['reader'] for r in selected]); n=len(reader)
        tools={name:np.array([r[name] for r in selected],dtype=float) for name in ['LT_estimate','edits_grammar','edits_all']}
        points={name:values(reader,tool) for name,tool in tools.items()}
        boot={name:{k:[] for k in points[name]} for name in tools}
        rng=np.random.default_rng(42)
        for rep in range(2000):
            ix=rng.integers(0,n,size=n)
            for name,tool in tools.items():
                for key,value in values(reader[ix],tool[ix]).items(): boot[name][key].append(float(value))
        for name,tool in tools.items():
            for key,point in points[name].items():
                draws=np.array(boot[name][key]); valid=draws[np.isfinite(draws)]
                lo,hi=np.percentile(valid,[2.5,97.5],method='linear') if len(valid) else (np.nan,np.nan)
                if key in {'Spearman','Pearson'}:
                    a,b=(rankdata(reader),rankdata(tool)) if key=='Spearman' else (reader,tool)
                    check,(aa,bb,ab)=corr(a,b)
                    direct=spearmanr(reader,tool).statistic if key=='Spearman' else pearsonr(reader,tool).statistic
                    assert np.isclose(check,direct,atol=1e-12)
                    arithmetic=f'{ab:.17g}/sqrt({aa:.17g}*{bb:.17g})={point:.17g}'
                elif key in {'reader_mean','tool_mean','absolute_mean_gap','mean_ratio'}:
                    arithmetic=f'reader_sum/n={reader.sum():.17g}/{n}={reader.mean():.17g}; tool_sum/n={tool.sum():.17g}/{n}={tool.mean():.17g}; abs(tool_mean-reader_mean)={abs(tool.mean()-reader.mean()):.17g}; tool_mean/reader_mean={tool.mean()/reader.mean():.17g}'
                else:
                    ordered=sorted(reader if key=='reader_median' else tool)
                    arithmetic=f'({ordered[(n-1)//2]:.17g}+{ordered[n//2]:.17g})/2={point:.17g}'
                bounds=[]
                ordered_draws=np.sort(valid)
                for q in [.025,.975]:
                    h=(len(valid)-1)*q; lower=int(np.floor(h)); upper=int(np.ceil(h)); fraction=h-lower
                    bounds.append(f'h=({len(valid)}-1)*{q}={h:.17g}; {ordered_draws[lower]:.17g}+{fraction:.17g}*({ordered_draws[upper]:.17g}-{ordered_draws[lower]:.17g})={np.percentile(valid,q*100,method="linear"):.17g}')
                metrics.append(dict(group=group,n=n,tool=name,metric=key,estimate=float(point),CI_low=float(lo),CI_high=float(hi),valid=len(valid),skipped=2000-len(valid),arithmetic=arithmetic,CI_arithmetic='; '.join(bounds)))
        for method in ['Spearman','Pearson']:
            a,b=tools['edits_grammar'],tools['LT_estimate']
            if method=='Spearman': a,b=rankdata(a),rankdata(b)
            value,(aa,bb,ab)=corr(a,b)
            print('NEW_VS_LT '+json.dumps(dict(group=group,method=method,correlation=float(value),arithmetic=f'{ab:.17g}/sqrt({aa:.17g}*{bb:.17g})={value:.17g}')))
    for row in metrics: print('METRIC '+json.dumps(row,sort_keys=True))
    print('\n| Sample | Tool | Spearman [95% CI] | Pearson [95% CI] | Reader mean | Tool mean | Absolute mean gap |')
    print('|---|---|---|---|---|---|---|')
    for group in ['pooled68','random36','week9_32']:
        for tool in ['LT_estimate','edits_grammar']:
            chosen={r['metric']:r for r in metrics if r['group']==group and r['tool']==tool}
            intervals=[f"{chosen[k]['estimate']:.6f} [{chosen[k]['CI_low']:.6f}, {chosen[k]['CI_high']:.6f}]" for k in ['Spearman','Pearson']]
            means=[f"{chosen[k]['estimate']:.6f}" for k in ['reader_mean','tool_mean','absolute_mean_gap']]
            print('| '+' | '.join([group,tool,*intervals,*means])+' |')
    def estimate(tool,key): return next(r['estimate'] for r in metrics if r['group']=='pooled68' and r['tool']==tool and r['metric']==key)
    rho_new,rho_lt=estimate('edits_grammar','Spearman'),estimate('LT_estimate','Spearman')
    gap_new,gap_lt=estimate('edits_grammar','absolute_mean_gap'),estimate('LT_estimate','absolute_mean_gap')
    accepted=bool(rho_new>rho_lt and gap_new<gap_lt)
    acceptance=dict(accepted=accepted,condition_i=bool(rho_new>rho_lt),condition_ii=bool(gap_new<gap_lt),
                    arithmetic=f'({rho_new:.17g}>{rho_lt:.17g}) AND ({gap_new:.17g}<{gap_lt:.17g}) = {accepted}',
                    definition='edits_grammar is PRIMARY; edits_all is sensitivity only; pooled 68')
    print('ACCEPTANCE '+json.dumps(acceptance,sort_keys=True))
    for band in ['<2.5','2.5-4.0','>4.0']:
        selected=[r for r in rows if r['sample_group']=='random36' and r['band']==band]
        print('RANDOM_BAND '+json.dumps(dict(band=band,n=len(selected),**{key+'_mean':sum(r[key] for r in selected)/len(selected) for key in ['reader','LT_estimate','edits_grammar']}, arithmetic={key:f'{sum(r[key] for r in selected):.17g}/{len(selected)}={sum(r[key] for r in selected)/len(selected):.17g}' for key in ['reader','LT_estimate','edits_grammar']})))
    print('BOOTSTRAP paired ordinary essay resamples, default_rng(42), reset per group; 2000; percentile linear 95%; tied ranks recalculated on every draw; undefined correlations skipped and counted. No prompt clustering. No OOF model was fitted in Part A; downstream OOF CIs, if later run, condition on fitted models.')
    result=dict(metrics=metrics,acceptance=acceptance)
    (g.OUT/'gec_part_a_statistics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count',action='store_true')
    parser.add_argument('--analyze',action='store_true')
    parser.add_argument('--append',action='store_true')
    args=parser.parse_args()
    assert g.DIGEST == LOCK, 'Locked preregistration changed'
    g.preregister()
    print('PART_A_ONLY; no Part B; no full-development count; input order sample_group then essay_id ascending')
    os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'
    # Report append is handled after the guarded analysis; only this exact report is authorized.
    report=g.OUT/'RESULTS_week10.md'
    previous=g.audit_read(report).read_bytes() if args.append else None
    heading='## Exploratory Part A: locked GECToR + ERRANT comparison on 68 reader-counted essays'
    if previous is not None: assert heading.encode() not in previous
    captured=io.StringIO()
    class Tee:
        def write(self,text): sys.__stdout__.write(text); captured.write(text)
        def flush(self): sys.__stdout__.flush()
    g.install_read_guard()
    with contextlib.redirect_stdout(Tee()):
        if args.count: count_sample()
        result=analyze() if args.analyze else None
        print('READ_GUARD allowlisted development inputs only; offline inference; no Test or combined corpus opened; no essay text printed; no fits')
    if args.append:
        assert result is not None
        # Append is an authorized report write; preserve the original prefix hash.
        section=('\n\n'+heading+'\n\n2026-10-24 (Asia/Saigon). Exploratory; Part A only. '
                 'Configuration unchanged: `'+LOCK+'`. Exact same Counter implementation as a85244c. '
                 'LT is the pre-registered historical first150 estimate, not a newly observed window count. '
                 'Per-essay counts: git-ignored `reports/week10/gec_part_a_68.csv`; never embed essay text.\n\n'
                 '```text\n'+captured.getvalue()+'```\n')
        # Python audit guard allows writes to this report but no additional reads.
        with report.open('ab') as stream: stream.write(section.encode('utf-8'))
        (g.OUT/'gec_part_a_report_prefix.json').write_text(json.dumps(dict(previous_bytes=len(previous),previous_sha256=hashlib.sha256(previous).hexdigest(),appended_bytes=len(section.encode('utf-8')))),encoding='utf-8')
        print('APPENDED bytes='+str(len(section.encode('utf-8')))+'; previous_SHA256='+hashlib.sha256(previous).hexdigest())


if __name__=='__main__': main()

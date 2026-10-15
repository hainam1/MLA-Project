"""Build the fixed-sample reading workbook; no human judgements are generated."""
import io
import json
import math
import os
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from t456_evidence import *
from validation_common import load

PRIVATE=OUT/'t4_private'
TEAM=['off_topic','unusual_vocabulary','tool_error_mismatch','coherence','length','unusual_syntax','rater_score_possibly_debatable','evidence_quote','likely_reason_model_wrong','confidence','reader_initials']
LEGACY=['reviewer','off_topic_task_response','unusual_vocabulary','grammar_checker_mismatch','coherence_content','length_observation','unusual_syntax','rater_ambiguity','manual_notes']
DEFINITIONS={
 'off_topic':'Whether the writing addresses the authoritative assigned task. The released short prompt name alone is insufficient.',
 'unusual_vocabulary':'Vocabulary observations supported by specific wording in the essay.',
 'tool_error_mismatch':'Possible mismatch between detected grammar-tool errors and the writing, supported by a quoted example.',
 'coherence':'Observations about organization, connections between ideas, or clarity of meaning.',
 'length':'Observations about writing length and its relevance to the task.',
 'unusual_syntax':'Syntax observations supported by specific constructions in the essay.',
 'rater_score_possibly_debatable':'Whether the reference rating may merit discussion, with evidence and uncertainty recorded.',
 'evidence_quote':'Verbatim essay excerpt supporting the reader observation.',
 'likely_reason_model_wrong':'Reader hypothesis about a model error, tied to recorded evidence.',
 'confidence':'Reader confidence in the observation: low, med, or high.',
 'reader_initials':'Initials identifying the team member who read the essay.',
}

def normalize_xlsx(path):
    # Stable ZIP serialization and relationship IDs; do not change cell values or links.
    data=path.read_bytes(); buf=io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source,zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as dest:
        relationships={}
        for name in sorted(source.namelist()):
            if name.endswith('.rels'):
                root=ET.fromstring(source.read(name))
                for relationship in sorted(root,key=lambda r:(r.attrib.get('Type',''),r.attrib.get('Target',''),r.attrib.get('TargetMode',''))):
                    old=relationship.attrib['Id']
                    assert old not in relationships, 'Unexpected repeated relationship ID across package parts'
                    relationships[old]='rIdCanonical'+str(len(relationships)+1)
        for name in sorted(source.namelist()):
            content=source.read(name)
            if name.endswith(('.xml','.rels')):
                for old,new in relationships.items():
                    content=content.replace(('"'+old+'"').encode(),('"'+new+'"').encode())
            if name=='docProps/core.xml':
                text=content.decode('utf-8')
                text=re.sub(r'(<dcterms:(?:created|modified)[^>]*>).*?(</dcterms:(?:created|modified)>)',r'\g<1>2000-01-01T00:00:00Z\2',text)
                content=text.encode('utf-8')
            entry=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0)); entry.compress_type=zipfile.ZIP_DEFLATED
            entry.external_attr=0o600<<16
            dest.writestr(entry,content)
    path.write_bytes(buf.getvalue())

def main():
    PRIVATE.mkdir(parents=True,exist_ok=True)
    print(LABEL,flush=True)
    print('COMMAND: .venv/Scripts/python.exe -u scripts/week9/t4_reading_sheet.py')
    print('SEED=42; fixed existing sample; no sampling or human judgement')
    paths=['docs/data/error_analysis/manual_error_review.csv','scripts/post_midterm_teacher_analysis.py','docs/data/error_analysis/README.md','data/03_clean_ready_to_use/validation_783.csv','data/05_model_features/development_features_with_targets.csv','outputs/phase6/validation_predictions.csv','reports/week9/t1_essay_level.csv','data/01_original_source/rater_scores/ellipsis_raw_rater_scores_anon_all_essay.csv']
    before={p:sha((ROOT/p).read_bytes()) for p in paths}
    sample=pd.read_csv(ROOT/paths[0],dtype=str,keep_default_na=False)
    assert len(sample)==32 and sample.essay_id.is_unique
    f=load()
    assert len(f)==762 and f.large_error.sum()==69
    already=set(); reconstructed=[]
    for group,mask,n,columns,ascending in [
      ('highest_rf_error',f.large_error,12,['RF_magnitude','essay_id'],[False,True]),
      ('shared_blind_spot',f.large_error & f.D.lt(.133989655155),10,['essay_id'],True),
      ('low_rf_error_comparison',f.RF_magnitude.lt(.5),10,['RF_magnitude','essay_id'],True)]:
        selected=f.loc[mask & ~f.essay_id.isin(already)].sort_values(columns,ascending=ascending).head(n)
        reconstructed.extend((i,group) for i in selected.essay_id); already.update(selected.essay_id)
    same=set(i for i,g in reconstructed)==set(sample.essay_id)
    same_group=dict(reconstructed)==dict(zip(sample.essay_id,sample.sample_group))
    if same:
        assert len(reconstructed)==32 and same_group
    save('t4_selection_check.csv',[dict(existing_n=len(sample),reproduced_n=len(reconstructed),same_ids=same,same_groups=same_group,missing=len(set(sample.essay_id)-already),extra=len(already-set(sample.essay_id)),action='existing sample retained unchanged')])
    print('SELECTION rule script lines 148-169; exact sequential highest-error, low-D large-error and low-error-control selection; source IDs are retained regardless of reproduction status.')
    if not same: print('PARTIAL selection rule does not reproduce; existing IDs retained unchanged as instructed')
    source_lines=(ROOT/paths[1]).read_text(encoding='utf-8').splitlines()
    for i in range(147,170): print(f'CODE scripts/post_midterm_teacher_analysis.py:{i+1}: {source_lines[i]}')
    median=.13398965515499994
    f['quadrant']=np.where(f.large_error,'large_error=yes; ','large_error=no; ')+np.where(f.D.lt(median),'D below median','D at-or-above median')
    f['sample_group']=f.essay_id.map(dict(zip(sample.essay_id,sample.sample_group)))
    chosen=f.loc[f.essay_id.isin(sample.essay_id)].copy()
    chosen['_order']=chosen.essay_id.map({e:i for i,e in enumerate(sample.essay_id)})
    chosen=chosen.sort_values('_order').drop(columns='_order')
    counts=chosen.groupby(['sample_group','quadrant'],sort=True).size().reset_index(name='n')
    save('t4_group_quadrant_counts.csv',counts)
    categories=pd.read_csv(ROOT/paths[6],dtype={'essay_id':str})[['essay_id','error_category']]
    mapping={'a_both_wrong_same_direction':'a','b_same_direction_Ridge_below_threshold':'b','c_opposite_sign':'c','not_large_error':'none','zero_Ridge_error':'none'}
    f=f.merge(categories,on='essay_id',validate='one_to_one',how='left')
    f['task1_category']=f.error_category.map(mapping)
    assert f.task1_category.notna().all()
    category_counts=f.loc[f.essay_id.isin(sample.essay_id)].groupby('task1_category').size().reindex(['a','b','c','none'],fill_value=0).reset_index(name='n')
    save('t4_category_counts.csv',category_counts)
    bcount=int((~chosen.large_error & chosen.D.ge(median)).sum())
    proposed=f.loc[~f.large_error].sort_values(['D','essay_id'],ascending=[False,True]).head(5).copy() if bcount<3 else f.iloc[0:0].copy()
    print(f'EXAMPLE_B high_disagreement_no_large_error_in_existing_sample={bcount}; high_disagreement means D >= {median:.17g}; supplement_proposed={len(proposed)}; supplementary rows never added to original sample')
    needed=set(sample.essay_id)|set(proposed.essay_id)
    clean=pd.read_csv(ROOT/paths[3],usecols=['essay_id','prompt','essay_text'],dtype={'essay_id':str},keep_default_na=False)
    clean=clean.loc[clean.essay_id.isin(needed)].copy()
    assert set(clean.essay_id)==needed
    # Raw-rater source is shared. Only allowlisted IDs are retained, before any score processing.
    retained=[]
    for chunk in pd.read_csv(ROOT/paths[7],usecols=['text_id_kaggle','Vocabulary_1','Vocabulary_2','Grammar_1','Grammar_2'],dtype={'text_id_kaggle':str},chunksize=1000):
        retained.append(chunk.loc[chunk.text_id_kaggle.isin(needed)].copy())
    ratings=pd.concat(retained,ignore_index=True).rename(columns={'text_id_kaggle':'essay_id','Vocabulary_1':'rater1_V','Vocabulary_2':'rater2_V','Grammar_1':'rater1_G','Grammar_2':'rater2_G'})
    assert ratings.essay_id.is_unique and set(ratings.essay_id)==needed
    values=f.loc[f.essay_id.isin(needed)].merge(clean[['essay_id','essay_text']],on='essay_id',validate='one_to_one').merge(ratings,on='essay_id',validate='one_to_one')
    for t in ['V','G']:
        assert np.isfinite(values[['rater1_'+t,'rater2_'+t]].to_numpy(dtype=float)).all()
        assert np.array_equal((values['rater1_'+t]+values['rater2_'+t])/2,values['y_'+t])
    features=pd.read_csv(ROOT/paths[4],usecols=['essay_id','detected_grammar_errors_per_100_words','mean_word_frequency'],dtype={'essay_id':str})
    values=values.merge(features,on='essay_id',validate='one_to_one')
    values=values.rename(columns={'prompt':'prompt_text'})
    values['full_prompt_text']=''
    values['prompt_text_status']='Released short prompt name only; authoritative full assignment wording unavailable'
    for col in TEAM: values[col]=''
    for col in LEGACY: values['source_'+col]=values.essay_id.map(dict(zip(sample.essay_id,sample[col]))).fillna('')
    base=['essay_id','sample_group','prompt_text','full_prompt_text','prompt_text_status','rater1_V','rater2_V','rater1_G','rater2_G','y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G','e_RF_V','e_RF_G','e_Ridge_V','e_Ridge_G','D','quadrant','task1_category','word_count','detected_grammar_errors_per_100_words','mean_word_frequency']
    columns=base+TEAM+['source_'+c for c in LEGACY]+['selection_provenance','essay_text']
    main=values.set_index('essay_id',drop=False).loc[sample.essay_id].reset_index(drop=True)
    main['selection_provenance']='Existing Week 8 selection; unchanged IDs and groups'
    for col in LEGACY: assert main['source_'+col].tolist()==sample[col].tolist()
    supplementary=values.set_index('essay_id',drop=False).loc[proposed.essay_id].reset_index(drop=True)
    supplementary['sample_group']='supplement_proposed'
    supplementary['selection_provenance']='Selected after Week 8 by fixed rule: five highest D among Validation A1 non-large-errors; essay_id ascending ties; proposal only'
    filled=sum(int(sample[col].ne('').sum()) for col in LEGACY)
    print(f'HUMAN_FIELDS legacy_nonempty_cells={filled}; copied verbatim in source_ columns; new_team_columns={len(TEAM)}; all new team cells empty')
    save('t4_manifest.csv',[dict(essay_id=row.essay_id,sample_group=row.sample_group,quadrant=row.quadrant,task1_category=row.task1_category) for row in main.itertuples()],echo=False)
    if len(supplementary): save('t4_supplement_proposed_ids.csv',supplementary[['essay_id','D','quadrant']])
    rubric=[dict(criterion=c,definition=DEFINITIONS[c],how_to_decide='') for c in TEAM]
    payload=dict(columns=columns,rows=main[columns].replace({np.nan:None}).to_dict('records'),supplement=supplementary[columns].replace({np.nan:None}).to_dict('records'),rubric=rubric)
    (PRIVATE/'payload.json').write_text(json.dumps(payload,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    marker=Path('C:/Users/LEGION/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.1013.11914/skills/spreadsheets/container_tools/mark_artifact_operation_started.mjs')
    if os.environ.get('T4_FIRST_EXPORT')=='1' and not (PRIVATE/'authoring_marker_completed.txt').exists():
        subprocess.run(['node',str(marker),'--operation-kind','create','--expected-output-count','1','--output-format','xlsx'],check=True)
        (PRIVATE/'authoring_marker_completed.txt').write_text('Authoring marker completed successfully before first export.',encoding='utf-8')
    result=subprocess.run(['node',str(ROOT/'scripts/week9/t4_workbook.mjs')],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    sys.stdout.buffer.write(result.stdout); sys.stdout.buffer.flush()
    assert result.returncode==0, 'Workbook builder failed; raw output retained'
    path=OUT/'t4_reading_sheet.xlsx'
    path.write_bytes((PRIVATE/'reading_sheet_export.xlsx').read_bytes())
    normalize_xlsx(path)
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        book=ET.fromstring(z.read('xl/workbook.xml'))
        names=[s.attrib['name'] for s in book.findall('s:sheets/s:sheet',ns)]
        assert names==['reading_sheet','rubric']+(['supplement_proposed'] if len(supplementary) else [])
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
        def cells(xml):
            rows=[]
            for r in xml.findall('s:sheetData/s:row',ns):
                row={}
                for c in r.findall('s:c',ns):
                    v=c.find('s:v',ns); t=c.attrib.get('t')
                    value=v.text if v is not None else None
                    if t=='s': value=strings[int(value)]
                    elif t=='inlineStr': value=''.join(c.find('s:is',ns).itertext())
                    elif value is not None and t not in ('str','e'): value=float(value)
                    row[c.attrib['r']]=value
                rows.append(row)
            return rows
        sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        allcells={k:v for r in cells(sheet) for k,v in r.items()}
        def letter(index):
            result=''; index+=1
            while index: index,rem=divmod(index-1,26); result=chr(65+rem)+result
            return result
        actual=[[allcells.get(letter(j)+str(i)) for j in range(len(columns))] for i in range(2,34)]
        assert len(sheet.findall('s:sheetData/s:row',ns))==33
        rubricxml=ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
        rubriccells={k:v for r in cells(rubricxml) for k,v in r.items()}
        assert all(rubriccells.get('C'+str(i)) in (None,'') for i in range(2,13))
        pane=sheet.find('s:sheetViews/s:sheetView/s:pane',ns)
        assert pane is not None and pane.attrib['topLeftCell']=='C2'
        lastcell=sheet.find(f'.//s:c[@r="{letter(len(columns)-1)}2"]',ns)
        styles=ET.fromstring(z.read('xl/styles.xml'))
        style=styles.find('s:cellXfs',ns)[int(lastcell.attrib.get('s','0'))]
        assert style.find('s:alignment',ns).attrib.get('wrapText') in ('1','true')
        validations=sheet.find('s:dataValidations',ns)
        assert validations is not None and 'low,med,high' in ''.join(validations.itertext())
    assert len(actual)==32
    assert [r[0] for r in actual]==sample.essay_id.tolist()
    for i,row in enumerate(actual):
        for j,col in enumerate(columns):
            expected=payload['rows'][i][col]; seen=row[j]
            assert seen==expected or (seen is None and expected=='') or (isinstance(expected,(int,float)) and isinstance(seen,(int,float)) and np.isclose(seen,expected,atol=1e-12,rtol=0)), (i,col)
    assert all(actual[i][columns.index(c)] in (None,'') for i in range(32) for c in TEAM)
    print('XLSX_CHECK rows, IDs, all source values and verbatim notes match payload; new human fields and rubric how_to_decide blank; essay text wrapped; headers/ID panes frozen; confidence validation present')
    assert before=={p:sha((ROOT/p).read_bytes()) for p in paths}
    save('t4_sources.csv',[dict(path=p,sha256=h) for p,h in before.items()],echo=False)
    canonical=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    save('t4_output_hashes.csv',[dict(path='reports/week9/t4_reading_sheet.xlsx',sha256=sha(path.read_bytes())),dict(path='workbook_source_payload_semantics',sha256=sha(canonical))])
    print('LIMITATION: authoritative full prompt wording is not available in released development metadata; prompt_text preserves the source short name, full_prompt_text is empty. Off-topic coding requires the team to obtain the full assignment.')
    print('STATUS: PARTIAL only for authoritative full-prompt wording; fixed-sample reading workbook, rater-score mean checks, source-note preservation and requested counts complete. No human judgement filled. No Official Test data file opened; shared raw-rater source retained only allowlisted Validation IDs.')

if __name__=='__main__':
    if '--capture' in sys.argv:
        capture('t4','t4_reading_sheet.py','PARTIAL: the workbook is complete for available source fields, but authoritative full assignment wording is absent. The released short prompt name is preserved and full_prompt_text is blank; the team must obtain the assignment before coding off-topic. All existing human cells are copied verbatim into source_ columns; requested new team columns and rubric how_to_decide remain empty. The sample reproduction, counts and workbook verification are evidenced below. The original sample is unchanged. Private text-bearing intermediates/previews and the workbook are ignored by Git. Authoring uses the bundled artifact-tool; verification inspects the exported XLSX XML directly with the standard library. ZIP timestamps, document timestamps and randomly assigned package relationship IDs are canonicalized solely for deterministic serialization; cell values and relationship targets are unchanged. Initial attempt logs are preserved: logs/t4_attempt1.log records the missing openpyxl verification dependency; logs/t4_attempt2.log records differing serialized hashes despite identical payloads, traced to random relationship IDs. No statistical result, text or sample changed to resolve these packaging issues.')
    else: main()

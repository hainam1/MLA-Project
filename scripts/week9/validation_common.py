"""Shared, explicitly allowlisted Validation-only evidence helpers."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/week9'
SEED = 42
N_BOOT = 2000
CENTERS = (3.26941940240918, 3.124225726952784)
SIGNALS = {'Disagreement': 'D', 'Ridge Extremity': 'extremity', 'Shortest-first': 'negative_word_count'}
SOURCES = [
    'outputs/phase6/validation_predictions.csv',
    'data/05_model_features/development_features_with_targets.csv',
    'data/03_clean_ready_to_use/validation_783.csv',
    'docs/data/error_analysis/manual_error_review.csv',
]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def csv_read(path, columns=None):
    return pd.read_csv(ROOT/path, usecols=columns, dtype={'essay_id':str})

def save(name, rows, echo=True):
    df = rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    df.to_csv(OUT/name,index=False,float_format='%.17g',lineterminator='\n')
    if echo:
        print('CSV '+name)
        print((OUT/name).read_text(),end='')
    return df

def top(frame, column):
    return frame.sort_values([column,'essay_id'],ascending=[False,True],kind='stable').head(153).index

def load():
    # No directory globbing or access to mixed corpus, raw ratings, Test or split manifest.
    p = csv_read(SOURCES[0]).rename(columns={'random_forest_vocabulary':'RF_V','random_forest_grammar':'RF_G','ridge_vocabulary':'Ridge_V','ridge_grammar':'Ridge_G'})
    dev = csv_read(SOURCES[1],['essay_id','split','source_partition','word_count','Vocabulary','Grammar'])
    assert dev.essay_id.is_unique and p.essay_id.is_unique
    base = dev.loc[dev.essay_id.isin(set(p.essay_id))].copy()
    assert len(base)==len(p)==762 and set(base.essay_id)==set(p.essay_id)
    assert base.split.eq('validation').all() and base.source_partition.eq('official_train').all()
    f = base.merge(p,on='essay_id',validate='one_to_one',sort=False).rename(columns={'Vocabulary':'y_V','Grammar':'y_G'})
    assert np.isfinite(f[['word_count','y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G']].to_numpy()).all()
    for t in ('V','G'):
        for m in ('RF','Ridge'):
            f[f'e_{m}_{t}']=f[f'{m}_{t}']-f[f'y_{t}']
        f[f'd_{t}']=abs(f[f'RF_{t}']-f[f'Ridge_{t}'])
    f['D']=f[['d_V','d_G']].max(axis=1)
    f['RF_magnitude']=f[['e_RF_V','e_RF_G']].abs().max(axis=1)
    f['Ridge_magnitude']=f[['e_Ridge_V','e_Ridge_G']].abs().max(axis=1)
    f['large_error']=f.RF_magnitude.ge(1.0)
    f['extremity']=np.maximum(abs(f.Ridge_V-CENTERS[0]),abs(f.Ridge_G-CENTERS[1]))
    f['negative_word_count']=-f.word_count
    observed = (int(f.large_error.sum()),*[int(f.loc[top(f,col),'large_error'].sum()) for col in SIGNALS.values()])
    assert observed==(69,15,10,15), f'DISCREPANCY A1: {observed}; expected K,D,Extremity,Shortest=(69,15,10,15)'
    print('A1_ASSERT_PASS K=69; Disagreement=15; Shortest-first=15; Ridge Extremity=10; N=762; budget=153')
    print(f'SEED={SEED}; bootstrap_resamples={N_BOOT}; random_draws=1000; threshold=1.0; budget=0.20; aggregation=max; tie=essay_id string ascending; centers={CENTERS}')
    # Only after the mandatory reproduction gate: add prompt and existing sample membership.
    labels=csv_read(SOURCES[2],['essay_id','prompt','vocabulary','grammar'])
    assert labels.essay_id.is_unique
    f=f.merge(labels,on='essay_id',how='left',validate='one_to_one',sort=False)
    assert f.prompt.notna().all()
    assert np.array_equal(f.y_V,f.vocabulary) and np.array_equal(f.y_G,f.grammar)
    f=f.drop(columns=['vocabulary','grammar'])
    sample_path=ROOT/SOURCES[3]
    if sample_path.exists():
        sample=csv_read(SOURCES[3],['essay_id'])
        assert len(sample)==32 and sample.essay_id.is_unique and set(sample.essay_id)<=set(f.essay_id), 'DISCREPANCY: existing sample is not 32 unique Validation IDs'
        f['in_32_sample']=np.where(f.essay_id.isin(sample.essay_id),'yes','no')
        print('SAMPLE existing docs/data/error_analysis/manual_error_review.csv; 32 unique Validation IDs; membership only; no human judgement read or written')
    else:
        f['in_32_sample']='UNKNOWN'
        print('PARTIAL: missing docs/data/error_analysis/manual_error_review.csv; in_32_sample=UNKNOWN')
    f['selected_by_Disagreement']=f.index.isin(top(f,'D'))
    v,g=abs(f.e_RF_V).ge(1),abs(f.e_RF_G).ge(1)
    f['trigger']=np.select([v&g,v,g],['both','V','G'],default='none')
    f['analysis_target']=np.where(f.large_error,np.where(abs(f.e_RF_V)>=abs(f.e_RF_G),'V','G'),'none')
    print('METHOD y_V/y_G are saved human two-rater means, reused without re-anchoring; equal to Validation clean-table targets. Both-trigger RF-error ties use V deterministically.')
    print('METHOD only allowlisted Validation predictions, development table, Validation clean table and existing Validation sample IDs are read; no Official Test file is opened.')
    return f

def auc(y,s):
    y=np.asarray(y,dtype=bool); s=np.asarray(s)
    pos=int(y.sum()); neg=len(y)-pos
    if not pos or not neg:
        return float('nan'),float('nan'),pos,neg
    u=float(rankdata(s,method='average')[y].sum()-pos*(pos+1)/2)
    return u/(pos*neg),u,pos,neg

def boot_aucs(f,y,anchor,prefix):
    y=np.asarray(y,dtype=bool)
    rng=np.random.default_rng(SEED)
    estimates={s:[] for s in SIGNALS}
    scores={s:f[col].to_numpy() for s,col in SIGNALS.items()}
    for _ in range(N_BOOT):
        indices=rng.integers(0,len(f),size=len(f))
        for s in SIGNALS:
            estimates[s].append(auc(y[indices],scores[s][indices])[0])
    rows=[]; draws=[]
    for s,col in SIGNALS.items():
        value,u,pos,neg=auc(y,scores[s]); values=np.array(estimates[s]); valid=values[np.isfinite(values)]
        lo,hi=np.percentile(valid,[2.5,97.5]) if len(valid) else (np.nan,np.nan)
        rows.append(dict(anchor=anchor,ranking=s,score=col,n=len(f),positives=pos,negatives=neg,auroc=value,ci_low=lo,ci_high=hi,bootstrap_resamples=N_BOOT,valid_resamples=len(valid),skipped_resamples=N_BOOT-len(valid),seed=SEED,u=u,auroc_arithmetic=f'{u}/({pos}*{neg})={value:.17g}'))
        draws.extend(dict(anchor=anchor,ranking=s,resample=i+1,auroc=float(x)) for i,x in enumerate(values))
    save(prefix+'_bootstrap.csv',draws,echo=False)
    return rows

def run_capture(task,script,narrative):
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'logs').mkdir(exist_ok=True)
    command=f'.venv/Scripts/python.exe scripts/week9/{script}'
    outputs=[]
    for i in (1,2):
        proc=subprocess.run([sys.executable,str(ROOT/'scripts/week9'/script)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        outputs.append(proc.stdout); (OUT/f'logs/{task}_run{i}.log').write_bytes(proc.stdout)
        sys.stdout.buffer.write(proc.stdout); sys.stdout.buffer.flush()
        if proc.returncode:
            (OUT/f'logs/{task}.log').write_bytes(b'\n'.join(outputs))
            raise SystemExit(f'DISCREPANCY: {task} stopped; see raw log. No task results appended.')
    proof=f'RUN1_SHA256={sha(outputs[0])}\nRUN2_SHA256={sha(outputs[1])}\nIDENTICAL_RAW_OUTPUT={outputs[0]==outputs[1]}\n'
    (OUT/f'logs/{task}.log').write_bytes(b'RUN 1\n'+outputs[0]+b'RUN 2\n'+outputs[1]+proof.encode())
    assert outputs[0]==outputs[1], 'DISCREPANCY: repeat differs'
    print(proof,end='')
    result=OUT/'RESULTS_week9.md'; previous=result.read_bytes()
    heading=f'## Task {task[1:]}'
    assert heading.encode() not in previous, 'Task section already exists; refusing to overwrite'
    excerpt=outputs[0].decode('utf-8')
    # Entire numeric summary is literal stdout; every table has a matching emitted CSV.
    section=f'\n{heading}\n\n{narrative}\n\nProducer: `scripts/week9/{script}`; shared calculations: `scripts/week9/validation_common.py`. Exact command: `{command} --capture`; each child command: `{command}`.\n\nRaw terminal output (first fresh process), including explicit arithmetic and CSV filenames:\n\n```text\n{excerpt}```\n\n[src: reports/week9/logs/{task}_run1.log; CSV data rows in each named CSV block, excluding its header]\n\nRepeat proof:\n\n```text\n{proof}```\n\n[src: reports/week9/logs/{task}.log final hash lines]\n'
    result.write_bytes(previous+section.encode('utf-8'))
    assert result.read_bytes()[:len(previous)]==previous

def integrity_start(task):
    OUT.mkdir(parents=True,exist_ok=True)
    paths=[p for p in SOURCES if (ROOT/p).exists()]
    snapshot={p:sha((ROOT/p).read_bytes()) for p in paths}
    print('COMMAND: .venv/Scripts/python.exe scripts/week9/'+task+'_analysis.py')
    return snapshot

def integrity_end(task,snapshot):
    assert snapshot=={p:sha((ROOT/p).read_bytes()) for p in snapshot}
    save(task+'_sources.csv',[dict(path=p,sha256=h) for p,h in snapshot.items()])
    outputs=sorted(p for p in OUT.glob(task+'_*.csv') if p.name!=task+'_output_hashes.csv')
    save(task+'_output_hashes.csv',[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes())) for p in outputs])
    print('INTEGRITY: all allowlisted source hashes unchanged; existing sample untouched; no model fit/predict; Task 0 section preserved by append-only writer.')

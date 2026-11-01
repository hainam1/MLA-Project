"""Text-free development-only arithmetic for the interview source dossier.

No training, corpus reads, Test inputs, or calls to other project entry points.
"""
from pathlib import Path
import csv, hashlib, json, math, subprocess, time, sys
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import GroupKFold

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/nguon_bao_cao_interview'
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
READS={}
NEW='TÍNH MỚI (dev)'
CMD='.venv/Scripts/python.exe scripts/build_interview_sources.py'
def read(path):
    # Exact allowlist: every data input is development-only or source metadata.
    allowed={
      'reports/week9/t3_eligible_development.csv','reports/week9/t3_heldout_predictions.csv',
      'reports/week10/b2_oof.csv','outputs/phase6/feature_schema.json',
      'outputs/phase6/training_summary.json',
      *[f'outputs/phase6/{m}_{t}.joblib' for m in ['ridge','random_forest'] for t in ['vocabulary','grammar']],
    }
    assert path in allowed, path
    p=ROOT/path;READS[path]=hashlib.sha256(p.read_bytes()).hexdigest();return p
def emit(name,rows,fields=None):
    rows=list(rows); assert len(rows)<=59
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def num(v):return format(float(v),'.12g')
def main():
    OUT.mkdir(exist_ok=True)
    start=time.perf_counter()
    # B: aggregate labels only, never essay text or prompt text exported.
    dev=pd.read_csv(read('reports/week9/t3_eligible_development.csv'),dtype={'essay_id':str})
    assert len(dev)==3812 and set(dev.source_partition)=={'official_train'}
    assert set(dev.privacy_review_status)=={'not_flagged'}
    dev=dev.sort_values('essay_id').reset_index(drop=True)
    features=json.loads(read('outputs/phase6/feature_schema.json').read_text())
    if isinstance(features,dict):features=features.get('feature_columns',features.get('features'))
    assert len(features)==14
    emit('b6_phan_bo_nhan_dev.csv',[
      dict(target=t,score=num(s),n=int((dev[t]==s).sum()),status=NEW,source='reports/week9/t3_eligible_development.csv',command=CMD)
      for t in ['Vocabulary','Grammar'] for s in np.arange(1,5.01,.5)])
    emit('c2_thieu_dac_trung.csv',[
      dict(feature=f,n=3812,missing=int(dev[f].isna().sum()),missing_share=num(dev[f].isna().mean()),status=NEW,source='reports/week9/t3_eligible_development.csv',command=CMD)
      for f in features])
    # C: inspect saved fitted coefficients/MDI only; no fit/predict.
    rows=[]
    for t in ['vocabulary','grammar']:
        ridge=joblib.load(read(f'outputs/phase6/ridge_{t}.joblib'))
        rf=joblib.load(read(f'outputs/phase6/random_forest_{t}.joblib'))
        assert ridge.n_features_in_==rf.n_features_in_==14
        for f,b,imp in zip(features,ridge.named_steps['model'].coef_,rf.named_steps['model'].feature_importances_):
            rows.append(dict(target=t,feature=f,ridge_coef_standardized_X=num(b),rf_impurity_importance=num(imp),fit_population='3050 model-train; saved Phase6 models',status=NEW,command=CMD))
    emit('c5_tam_quan_trong_dac_trung.csv',rows)
    # D: intercept-only mean predictions, GroupKFold same order as saved OOF.
    pred=pd.read_csv(read('reports/week9/t3_heldout_predictions.csv'),dtype={'essay_id':str})
    pred=pred[pred.split_type=='prompt_disjoint'].sort_values('essay_id').reset_index(drop=True)
    assert len(pred)==3812 and pred.essay_id.equals(dev.essay_id)
    y=dev[['Vocabulary','Grammar']].to_numpy(float);meanpred=np.empty_like(y)
    for fold,(tr,te) in enumerate(GroupKFold(5).split(dev,groups=dev.normalised_prompt),1):
        assert set(pred.iloc[te].fold)=={fold}
        meanpred[te]=y[tr].mean(axis=0)
    mean_mae=np.abs(meanpred-y).mean(axis=0)
    emit('d1_mean_dev.csv',[dict(target=t,n=3812,mae=num(mean_mae[j]),evaluation='pooled OOF GroupKFold(5) by normalised_prompt',status=NEW,command=CMD) for j,t in enumerate(['Vocabulary','Grammar'])])
    # E: export saved fold counts, not Monte Carlo reruns.
    foldrows=[];ranks={}
    for fold,g in pred.groupby('fold',sort=True):
        g=g.sort_values(['D','essay_id'],ascending=[False,True]);n=len(g);k=math.ceil(.2*n)
        large=(np.maximum(abs(g.y_V-g.RF_V),abs(g.y_G-g.RF_G))>=1)
        for rank,eid in enumerate(g.essay_id,1):ranks[eid]=(rank,k)
        foldrows.append(dict(fold=int(fold),N=n,large_errors=int(large.sum()),k=k,D_caught=int(large.iloc[:k].sum()),expected=num(k*large.sum()/n),status=NEW,source='reports/week9/t3_heldout_predictions.csv',command=CMD))
    assert sum(r['D_caught'] for r in foldrows)==88
    assert sum(r['large_errors'] for r in foldrows)==386
    emit('e5_bat_theo_fold.csv',foldrows)
    # F: no per-essay OOF tree spread was saved by its producer. Never replace
    # it with in-sample or fixed-model scores and call those OOF.
    # G: deterministic numerical examples, not newly authored human diagnoses.
    er=np.maximum(abs(pred.y_V-pred.RF_V),abs(pred.y_G-pred.RF_G))
    large=pred[er>=1].copy();large['error']=er[er>=1]
    ids=['0514D25768A0','684166ED2438']
    ids += [e for e in large.sort_values(['error','essay_id'],ascending=[False,True]).essay_id if e not in ids][:8]
    cases=[]
    for eid in ids:
        r=pred.set_index('essay_id').loc[eid];rank,k=ranks[eid]
        groups=[]
        for t in ['V','G']:
            if r[f'y_{t}']<2.5 and r[f'RF_{t}']>r[f'y_{t}']:groups.append(t+': diem thap du doan cao')
            elif r[f'y_{t}']>4 and r[f'RF_{t}']<r[f'y_{t}']:groups.append(t+': diem cao du doan thap')
        cases.append(dict(essay_id=eid,fold=int(r.fold),y_V=num(r.y_V),y_G=num(r.y_G),RF_V=num(r.RF_V),RF_G=num(r.RF_G),Ridge_V=num(r.Ridge_V),Ridge_G=num(r.Ridge_G),D=num(r.D),D_rank=rank,k=k,selected=rank<=k,tree_spread='KHÔNG CÓ NGUỒN OOF lưu theo bài',both_wrong=max(abs(r.y_V-r.Ridge_V),abs(r.y_G-r.Ridge_G))>=1,error_group='; '.join(groups) or 'sai lon khac (phan nhom so hoc)',status=NEW,command=CMD))
    emit('g1_ca_loi.csv',cases)
    # H: only saved predictions; fixed fold budgets; no tuning.
    h1=[]
    for budget in [.1,.2,.3]:
        caught=0;expected=0.;total_k=0
        for fold,g in pred.groupby('fold'):
            g=g.sort_values(['D','essay_id'],ascending=[False,True]);k=math.ceil(budget*len(g))
            a=np.maximum(abs(g.y_V-g.RF_V),abs(g.y_G-g.RF_G))>=1
            caught+=int(a.iloc[:k].sum());expected+=k*int(a.sum())/len(g);total_k+=k
        h1.append(dict(budget=num(budget),total_k=total_k,large_errors=386,D_caught=caught,tree_caught=96 if budget==.2 else 'KHÔNG CÓ NGUỒN OOF theo bài',expected=num(expected),status=NEW,tree_status='ĐÃ CÓ' if budget==.2 else 'KHÔNG CÓ NGUỒN',command=CMD,tree_source='reports/week9/RESULTS_week9.md:1436' if budget==.2 else 'producer tree_spread_oof.py retains scores in memory only'))
    emit('h1_doi_ngan_sach.csv',h1)
    h2=[]
    for threshold in [.75,1.,1.25]:
        caught=0;expected=0.;K=0
        for fold,g in pred.groupby('fold'):
            g=g.sort_values(['D','essay_id'],ascending=[False,True]);k=math.ceil(.2*len(g))
            a=np.maximum(abs(g.y_V-g.RF_V),abs(g.y_G-g.RF_G))>=threshold
            caught+=int(a.iloc[:k].sum());expected+=k*int(a.sum())/len(g);K+=int(a.sum())
        h2.append(dict(threshold=num(threshold),large_errors=K,D_caught=caught,expected=num(expected),status=NEW,command=CMD))
    emit('h2_doi_nguong.csv',h2)
    # I provenance for the exact allowlisted inputs and saved dev-only B2.
    read('reports/week10/b2_oof.csv');read('outputs/phase6/training_summary.json')
    # These are execution logs/aggregate result documents, not Test inputs.
    for p in ['reports/week9/logs/t3_training.log','reports/week10/b2_analysis.log',
              'reports/week10/RESULTS_week10.md','reports/week9/RESULTS_week9.md']:
        READS[p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    hashes=[]
    for p,h in READS.items():
        commit=subprocess.check_output(['git','log','-1','--format=%H','--',p],cwd=ROOT,text=True).strip()
        hashes.append(dict(file=p,sha256=h,last_file_commit=commit or 'KHÔNG CÓ: artifact gitignored; hash chốt trong commit đầu ra'))
    emit('i3_ma_bam_nguon_dev.csv',hashes)
    # K: commit metadata only, at the explicitly fixed pre-dossier snapshot.
    base='755929233dab6aee1983dfa028f2be1ed3e7f87c'
    raw=subprocess.check_output(['git','log',base,'--format=@@%an','--name-only'],cwd=ROOT,encoding='utf-8')
    authors={};author=None
    for line in raw.splitlines():
        if line.startswith('@@'):
            author=line[2:];authors.setdefault(author,{'count':0,'zones':set()});authors[author]['count']+=1
        elif line.strip():authors[author]['zones'].add(line.split('/')[0] if '/' in line else '[root]')
    emit('k1_tac_gia_git.csv',[dict(git_author=a,commit_count=d['count'],top_level_areas=';'.join(sorted(d['zones'])),status='ĐÃ CÓ',source_commit=base,command='git log 7559292 --format=%an --name-only (metadata only)') for a,d in sorted(authors.items())])
    elapsed=time.perf_counter()-start
    assert elapsed<600
    print(json.dumps(dict(status='OK',development_only=True,fit_calls=0,test_or_corpus_reads=0,seconds=elapsed,mean_mae_V=mean_mae[0],mean_mae_G=mean_mae[1],files=sorted(p.name for p in OUT.glob('*.csv'))),ensure_ascii=True))
if __name__=='__main__':main()

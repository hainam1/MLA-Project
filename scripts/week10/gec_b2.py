"""Exploratory frozen MiniLM + Ridge, with the b6398ea B2 configuration.

Separate encoding (.venv_gec) and OOF analysis (.venv) preserve baseline numerics.
No training or backward pass on the encoder; only fold-local regressors are fit.
"""
from pathlib import Path
import argparse
import contextlib
import csv
import hashlib
import importlib.metadata
import io
import json
import math
import os
import sys
import time

print('READ_AUDIT scripts/week10/information_sources_oof.py (import; git blob matched b6398ea)', flush=True)
import information_sources_oof as old

ROOT, OUT = old.ROOT, old.ROOT/'reports/week10'
REVISION='1110a243fdf4706b3f48f1d95db1a4f5529b4d41'
CONFIG=json.loads(json.dumps(old.CONFIG))
CONFIG.update(B2_revision=REVISION,
    B2_modules='Transformer -> attention-mask mean pooling -> model-native Normalize; encode normalize_embeddings=False unchanged',
    B2_max_seq_length=256, B2_dimension=384, B2_dtype='float32',
    B2_no_training='eval; requires_grad=False on every parameter; torch.inference_mode; no optimizer/backward',
    encoder_threads=1, benchmark='50 IDs without replacement, default_rng(42), from essay_id ascending; batch_size=32; exclude loading; stop if projected >7200 seconds',
    bootstrap_addendum='B2 vs RF/Ridge/B1 signed errors; same paired 2000 essay draws; pooled AUROC CIs and paired fixed-queue caught/AUC deltas; no prompt clustering',
    anchors='A1=RF max target abs error>=1; A3_B2=A1 & B2 max target abs error>=1; compare all three queues on identical labels',
    exact_p='per-fold hypergeom upper tail; pooled PMF convolution; independent-fold reference draws',
    caches='git-ignored embeddings and aligned ID manifest; no essay strings persisted')
CANONICAL=json.dumps(CONFIG,sort_keys=True)
DIGEST=hashlib.sha256(CANONICAL.encode()).hexdigest()
READS=set()
ALLOWED={(ROOT/p).resolve() for p in old.INPUTS+['outputs/phase6/validation_predictions.csv']}
REPORT=OUT/'RESULTS_week10.md'


def read(path):
    path=Path(path).resolve(); print('READ_AUDIT '+str(path),flush=True)
    return path


def audit(event,args):
    if event=='socket.connect': raise PermissionError('Offline analysis; essay text cannot leave the process')
    if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)): return
    p=Path(os.fsdecode(args[0])).resolve()
    try: rel=p.relative_to(ROOT)
    except ValueError: return
    if not rel.parts or rel.parts[0] not in {'data','outputs','docs','reports'}: return
    mode=args[1]; reading=not isinstance(mode,str) or not any(c in mode for c in 'wax')
    generated=(p.parent==OUT and p.name.startswith('b2_')) or OUT/'b2_assets' in p.parents
    report_ok=p==REPORT and (reading or (isinstance(mode,str) and mode.startswith('a')))
    if not generated and not report_ok and not (p in ALLOWED and reading):
        raise PermissionError('Outside B2 artifact allowlist')
    if reading:
        READS.add(rel.as_posix()); print('READ_AUDIT '+rel.as_posix(),flush=True)


def preregister():
    print('EXPLORATORY FIXED_CONFIGURATION_BEFORE_ENCODE_OR_FIT '+CANONICAL,flush=True)
    print('CONFIG_SHA256='+DIGEST,flush=True)
    print('PRODUCER_SHA256='+hashlib.sha256(read(__file__).read_bytes()).hexdigest(),flush=True)
    for name in ['torch','transformers','sentence-transformers','numpy','scipy','scikit-learn','pandas']:
        try: version=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: version='NOT_INSTALLED'
        print('PACKAGE '+name+'='+version,flush=True)


def encode():
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer
    torch.manual_seed(42); torch.set_num_threads(1); np.random.seed(42)
    ids=[]
    with read(ROOT/old.INPUTS[0]).open(encoding='utf-8-sig',newline='') as f:
        ids=sorted(r['essay_id'] for r in csv.DictReader(f))
    assert len(ids)==len(set(ids))==3812
    selected=set(ids); texts={}
    for relative in old.INPUTS[3:]:
        with read(ROOT/relative).open(encoding='utf-8-sig',newline='') as f:
            for r in csv.DictReader(f):
                if r['essay_id'] in selected:
                    assert r['essay_id'] not in texts
                    texts[r['essay_id']]=r['essay_text']
    assert set(texts)==selected
    path=OUT/'b2_assets/model'
    model=SentenceTransformer(str(path),device='cpu',local_files_only=True,trust_remote_code=False)
    model.eval()
    for p in model.parameters(): p.requires_grad_(False)
    assert model.max_seq_length==CONFIG['B2_max_seq_length']
    assert model.get_sentence_embedding_dimension()==384
    def parameter_hash():
        h=hashlib.sha256()
        for p in model.parameters(): h.update(p.detach().cpu().numpy().tobytes())
        return h.hexdigest()
    before=parameter_hash()
    print('FROZEN_ENCODER_PARAMETER_SHA256_BEFORE='+before+' parameters='+str(sum(p.numel() for p in model.parameters())),flush=True)
    indices=np.random.default_rng(42).choice(len(ids),size=50,replace=False)
    started=time.perf_counter()
    with torch.inference_mode():
        benchmark=model.encode([texts[ids[i]] for i in indices],batch_size=32,show_progress_bar=False,
                               normalize_embeddings=False,convert_to_numpy=True)
    elapsed=time.perf_counter()-started; projected=elapsed/50*3812
    timing=dict(config_sha256=DIGEST,benchmark_n=50,benchmark_seconds=elapsed,seconds_per_essay=elapsed/50,
                projected_seconds=projected,projected_minutes=projected/60,stop=projected>7200,
                arithmetic=f'{elapsed:.17g}/50={elapsed/50:.17g}; {elapsed/50:.17g}*3812={projected:.17g}; {projected:.17g}/60={projected/60:.17g}')
    print('ENCODE_BENCHMARK '+json.dumps(timing),flush=True)
    assert np.allclose(np.linalg.norm(benchmark,axis=1),1,atol=1e-5)
    (OUT/'b2_timing.json').write_text(json.dumps(timing,indent=2),encoding='utf-8')
    if timing['stop']:
        print('STOP projected encode time exceeds two hours; full encoding not started',flush=True); return
    assert not (OUT/'b2_embeddings_minilm.npy').exists(), 'Refusing to overwrite an existing embedding run'
    started=time.perf_counter()
    with torch.inference_mode():
        embeddings=model.encode([texts[i] for i in ids],batch_size=32,show_progress_bar=False,
                                normalize_embeddings=False,convert_to_numpy=True)
    full_seconds=time.perf_counter()-started
    assert embeddings.shape==(3812,384) and np.isfinite(embeddings).all()
    assert np.allclose(np.linalg.norm(embeddings,axis=1),1,atol=1e-5)
    assert np.allclose(benchmark,embeddings[indices],atol=1e-5)
    after=parameter_hash(); assert before==after
    assert all(not p.requires_grad and p.grad is None for p in model.parameters())
    np.save(OUT/'b2_embeddings_minilm.npy',embeddings,allow_pickle=False)
    manifest=dict(config_sha256=DIGEST,revision=REVISION,essay_ids=ids,shape=list(embeddings.shape),
                  encoder_parameter_sha256_before=before,encoder_parameter_sha256_after=after,
                  embedding_file_sha256=hashlib.sha256(read(OUT/'b2_embeddings_minilm.npy').read_bytes()).hexdigest())
    (OUT/'b2_embedding_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    timing.update(full_encode_seconds=full_seconds,full_seconds_per_essay=full_seconds/3812)
    (OUT/'b2_timing.json').write_text(json.dumps(timing,indent=2),encoding='utf-8')
    print('FULL_ENCODE '+json.dumps(timing),flush=True)
    print('VERIFY native L2 norms pass; 50 benchmark vectors match full-run rows; parameter SHA256 unchanged; gradients absent; full encode rows=3812',flush=True)


def table(name,rows):
    print(name,flush=True)
    print(pd.DataFrame(rows).to_csv(index=False,float_format='%.17g',lineterminator='\n'),end='',flush=True)


def fit():
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import GroupKFold
    from sklearn.feature_extraction.text import TfidfVectorizer
    f=pd.read_csv(ROOT/old.INPUTS[0],dtype={'essay_id':str}).sort_values('essay_id',kind='stable').reset_index(drop=True)
    composition=pd.read_csv(ROOT/old.INPUTS[1]); composition=composition.loc[composition.split_type.eq('prompt_disjoint')]
    features=json.loads(read(ROOT/old.INPUTS[2]).read_text())
    assert len(f)==3812 and f.essay_id.is_unique and f.normalised_prompt.nunique()==44
    assert f.source_partition.eq('official_train').all() and f.privacy_review_status.eq('not_flagged').all()
    assert f.eligible.all() and len(features)==14
    texts=pd.concat([pd.read_csv(ROOT/p,usecols=['essay_id','essay_text','vocabulary','grammar'],dtype={'essay_id':str},keep_default_na=False) for p in old.INPUTS[3:]],ignore_index=True)
    assert texts.essay_id.is_unique
    texts=texts.set_index('essay_id').loc[f.essay_id]
    assert np.array_equal(texts[['vocabulary','grammar']].to_numpy(),f[['Vocabulary','Grammar']].to_numpy())
    manifest=json.loads(read(OUT/'b2_embedding_manifest.json').read_text())
    assert manifest['config_sha256']==DIGEST and manifest['essay_ids']==f.essay_id.tolist()
    assert hashlib.sha256(read(OUT/'b2_embeddings_minilm.npy').read_bytes()).hexdigest()==manifest['embedding_file_sha256']
    x=np.load(OUT/'b2_embeddings_minilm.npy',allow_pickle=False)
    assert x.shape==(3812,384) and np.isfinite(x).all()
    predictions={name:np.full((len(f),2),np.nan) for name in ['RF','Ridge','B1','B2']}
    folds=np.zeros(len(f),dtype=int)
    for fold,(tr,held) in enumerate(GroupKFold(5).split(f,groups=f.normalised_prompt),1):
        train,val=f.iloc[tr],f.iloc[held]; saved=composition.loc[composition.fold.eq(fold)]
        assert val.groupby('normalised_prompt').size().to_dict()==saved.set_index('heldout_prompt').heldout_prompt_essays.to_dict()
        assert saved.train_essays.eq(len(tr)).all() and saved.heldout_essays.eq(len(held)).all()
        assert saved.k.eq(math.ceil(.2*len(held))).all()
        assert not set(train.normalised_prompt)&set(val.normalised_prompt)
        spec=dict(CONFIG['B1_TFIDF']); spec.pop('input'); spec['ngram_range']=tuple(spec['ngram_range']); spec['dtype']=np.float64
        tfidf=TfidfVectorizer(**spec); a=tfidf.fit_transform(texts.essay_text.iloc[tr]); b=tfidf.transform(texts.essay_text.iloc[held])
        for j,(target,alpha,leaf) in enumerate([('Vocabulary',100.,2),('Grammar',.1,5)]):
            rf=make_pipeline(SimpleImputer(strategy='median'),RandomForestRegressor(n_estimators=300,max_features='sqrt',max_depth=10,min_samples_leaf=leaf,random_state=42,n_jobs=1))
            ridge=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),Ridge(alpha=alpha))
            rf.fit(train[features],train[target]); ridge.fit(train[features],train[target])
            b1=Ridge(**CONFIG['B1_Ridge']); b1.fit(a,train[target])
            b2=Ridge(**CONFIG['B2_Ridge_if_offline']); b2.fit(x[tr],train[target])
            for name,model,values in [('RF',rf,val[features]),('Ridge',ridge,val[features]),('B1',b1,b),('B2',b2,x[held])]: predictions[name][held,j]=model.predict(values)
        folds[held]=fold
        print(f'FOLD_COMPLETE fold={fold} train={len(tr)} held={len(held)} k={math.ceil(.2*len(held))}; saved prompt composition matches; no train-held prompt overlap',flush=True)
    assert np.all(folds>0) and all(np.isfinite(p).all() for p in predictions.values())
    saved=f[['essay_id','Vocabulary','Grammar']].copy(); saved['fold']=folds
    for name,p in predictions.items():
        for j,t in enumerate(['V','G']): saved[name+'_'+t]=p[:,j]
    saved.to_csv(OUT/'b2_oof.csv',index=False,float_format='%.17g')
    return f,predictions,folds


def metrics(y,predictions):
    errors={name:p-y for name,p in predictions.items()}
    regression=[]
    for name,error in errors.items():
        for j,t in enumerate(['V','G']):
            sae=float(abs(error[:,j]).sum()); sse=float(error[:,j]@error[:,j]); centered=y[:,j]-y[:,j].mean(); sst=float(centered@centered)
            regression.append(dict(model=name,target=t,n=len(y),MAE=sae/len(y),R2=1-sse/sst,arithmetic=f'MAE={sae:.17g}/{len(y)}={sae/len(y):.17g}; R2=1-{sse:.17g}/{sst:.17g}={1-sse/sst:.17g}'))
    table('OOF_REGRESSION',regression)
    pairs=[('RF','Ridge'),('B1','RF'),('B1','Ridge'),('B2','RF'),('B2','Ridge'),('B2','B1')]
    specs=[(a,b,j,method) for a,b in pairs for j in range(2) for method in ['Spearman','Pearson']]
    variables={(name,j):e[:,j] for name,e in errors.items() for j in range(2)}
    inverse={key:np.unique(v,return_inverse=True)[1] for key,v in variables.items()}
    draws={spec:[] for spec in specs}; rng=np.random.default_rng(42); n=len(y)
    for rep in range(2000):
        w=np.bincount(rng.integers(0,n,n),minlength=n)
        ranks={key:old.weighted_ranks(inv,w) for key,inv in inverse.items()}
        for a,b,j,method in specs:
            source=ranks if method=='Spearman' else variables
            v=old.weighted_corr(source[a,j],source[b,j],w); draws[a,b,j,method].append(v)
            if rep==0:
                repeated=np.repeat(np.arange(n),w)
                direct=spearmanr(variables[a,j][repeated],variables[b,j][repeated]).statistic if method=='Spearman' else np.corrcoef(variables[a,j][repeated],variables[b,j][repeated])[0,1]
                assert np.isclose(v,direct,atol=1e-12,rtol=0)
    correlations=[]
    for a,b,j,method in specs:
        x,z=variables[a,j],variables[b,j]
        if method=='Spearman': x,z=rankdata(x),rankdata(z)
        xc,zc=x-x.mean(),z-z.mean(); aa=float(xc@xc); bb=float(zc@zc); ab=float(xc@zc)
        value=ab/np.sqrt(aa*bb); lo,hi,valid=old.intervals(draws[a,b,j,method])
        correlations.append(dict(model_a=a,model_b=b,target=['V','G'][j],method=method,correlation=float(value),CI_low=lo,CI_high=hi,below_095=bool(value<.95),entire_CI_below_095=bool(hi<.95),valid=valid,skipped=2000-valid,arithmetic=f'{ab:.17g}/sqrt({aa:.17g}*{bb:.17g})={value:.17g}'))
    table('SIGNED_ERROR_CORRELATIONS_ESSAY_BOOTSTRAP_95CI',correlations)
    return errors,regression,correlations


def signals(f,y,predictions,errors,folds):
    from scipy.stats import hypergeom
    large={name:np.max(abs(e),axis=1)>=1 for name,e in errors.items()}
    A1=large['RF']; A3old=A1&large['Ridge']; A3b2=A1&large['B2']
    assert A1.sum()==386 and A3old.sum()==276
    scores={name:np.max(abs(predictions['RF']-predictions[model]),axis=1) for name,model in [('D_old','Ridge'),('D_B1','B1'),('D_B2','B2')]}
    queues={}; probabilities=None
    for name,score in scores.items():
        queues[name],rate=old.select_queue(f.essay_id.to_numpy(),score,folds)
        if probabilities is None: probabilities=rate
        else: assert np.array_equal(probabilities,rate)
    assert (queues['D_old']&A1).sum()==88
    print('BASELINE_REPRODUCED A1=386; A3_old=276; D_old caught_A1=88',flush=True)
    captures=[]; aucs=[]; comparisons=[]
    for anchor,label in [('A1_RF',A1),('A3_RF_B2',A3b2)]:
        for signal,queue in queues.items():
            for fold in [1,2,3,4,5,'pooled']:
                mask=folds==fold if fold!='pooled' else np.ones(len(y),dtype=bool)
                n=int(mask.sum()); K=int(label[mask].sum()); k=int(queue[mask].sum()); caught=int((queue&label&mask).sum())
                if fold!='pooled':
                    expected=k*K/n; p=float(hypergeom.sf(caught-1,n,K,k)); arithmetic=f'{k}*{K}/{n}={expected:.17g}; hypergeom.sf({caught-1},{n},{K},{k})={p:.17g}'
                else:
                    pmf=np.array([1.]); terms=[]
                    for ff in range(1,6):
                        m=folds==ff; nf=int(m.sum()); kf=int(queue[m].sum()); Kf=int(label[m].sum())
                        terms.append((kf,Kf,nf)); pmf=np.convolve(pmf,hypergeom.pmf(np.arange(min(kf,Kf)+1),nf,Kf,kf))
                    assert abs(pmf.sum()-1)<1e-12
                    expected=sum(kf*Kf/nf for kf,Kf,nf in terms); p=float(pmf[caught:].sum())
                    arithmetic='+'.join(f'{kf}*{Kf}/{nf}' for kf,Kf,nf in terms)+f'={expected:.17g}; sum(convolved_PMF[{caught}:])={p:.17g}'
                captures.append(dict(anchor=anchor,signal=signal,fold=fold,n=n,K=K,k=k,caught=caught,expected=expected,exact_p=p,capture=caught/K if K else None,arithmetic=arithmetic))
        inv={name:np.unique(score,return_inverse=True)[1] for name,score in scores.items()}
        n=len(y); one=np.ones(n); points={name:old.auc(label,index,one) for name,index in inv.items()}
        caught={name:int((queue&label).sum()) for name,queue in queues.items()}; expected=float(np.dot(label,probabilities))
        samples={name:[] for name in scores}; delta={name:dict(caught=[],auc=[]) for name in ['D_old','D_B1']}; excess=[]
        rng=np.random.default_rng(42)
        for rep in range(2000):
            w=np.bincount(rng.integers(0,n,n),minlength=n)
            ac={name:old.auc(label,index,w) for name,index in inv.items()}
            ct={name:float(np.dot(w,label&queue)) for name,queue in queues.items()}
            for name in scores: samples[name].append(ac[name])
            for name in delta:
                delta[name]['caught'].append(ct['D_B2']-ct[name]); delta[name]['auc'].append(ac['D_B2']-ac[name])
            excess.append(ct['D_B2']-float(np.dot(w,label*probabilities)))
        for name in scores:
            lo,hi,valid=old.intervals(samples[name]); K=int(label.sum()); ranks=rankdata(scores[name]); u=float(ranks[label].sum()-K*(K+1)/2)
            assert np.isclose(u/(K*(n-K)),points[name],atol=1e-12)
            aucs.append(dict(anchor=anchor,signal=name,AUROC=float(points[name]),CI_low=lo,CI_high=hi,valid=valid,skipped=2000-valid,arithmetic=f'{u:.17g}/({K}*{n-K})={points[name]:.17g}'))
        for name in delta:
            for metric,point in [('caught',caught['D_B2']-caught[name]),('auc',points['D_B2']-points[name])]:
                lo,hi,valid=old.intervals(delta[name][metric]); comparisons.append(dict(anchor=anchor,comparison='D_B2-'+name,metric=metric,delta=float(point),CI_low=lo,CI_high=hi,valid=valid,arithmetic=f'{caught["D_B2"] if metric=="caught" else points["D_B2"]:.17g}-{caught[name] if metric=="caught" else points[name]:.17g}={point:.17g}'))
        lo,hi,valid=old.intervals(excess); comparisons.append(dict(anchor=anchor,comparison='D_B2-random_expectation',metric='caught',delta=caught['D_B2']-expected,CI_low=lo,CI_high=hi,valid=valid,arithmetic=f'{caught["D_B2"]}-{expected:.17g}={caught["D_B2"]-expected:.17g}'))
    shared=[]
    for name in ['B1','B2']:
        remaining=int((A3old&large[name]).sum()); fixed=int((A3old&~large[name]).sum()); assert remaining+fixed==276
        if name=='B1': assert remaining==203 and fixed==73
        shared.append(dict(model=name,A3_old=276,remain_wrong=remaining,fixed_both_targets_lt1=fixed,arithmetic=f'{remaining}+{fixed}=276; fixed share={fixed}/276={fixed/276:.17g}'))
    table('QUEUE_CAPTURE_EXACT_P_FOLD_AND_POOLED',captures); table('QUEUE_AUROC_POOLED_95CI',aucs); table('PAIRED_QUEUE_DIFFERENCES_95CI',comparisons); table('OLD_SHARED_ERRORS_REMAIN_OR_FIXED',shared)
    return captures,aucs,comparisons,shared


def analyze():
    global np,pd,rankdata,spearmanr
    import numpy as np
    import pandas as pd
    from scipy.stats import rankdata,spearmanr
    from threadpoolctl import threadpool_limits
    old.np=np; old.pd=pd
    for name in ['b2_download.log','b2_encode.log']:
        raw=read(OUT/name).read_bytes()
        content=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
        print('SETUP_LOG '+name+'\n'+content,flush=True)
    timing=json.loads(read(OUT/'b2_timing.json').read_text()); assert not timing['stop']
    print('ENCODE_TIMING '+json.dumps(timing,sort_keys=True),flush=True)
    before_hashes={name:hashlib.sha256(read(ROOT/name).read_bytes()).hexdigest() for name in old.INPUTS}
    for name,digest in before_hashes.items():
        print('INPUT_SHA256 '+name+'='+digest,flush=True)
    with threadpool_limits(limits=1):
        f,predictions,folds=fit(); y=f[['Vocabulary','Grammar']].to_numpy()
        errors,regression,correlations=metrics(y,predictions)
        captures,aucs,comparisons,shared=signals(f,y,predictions,errors,folds)
    result=dict(config_sha256=DIGEST,regression=regression,correlations=correlations,captures=captures,aucs=aucs,comparisons=comparisons,shared=shared)
    (OUT/'b2_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert before_hashes=={name:hashlib.sha256(read(ROOT/name).read_bytes()).hexdigest() for name in old.INPUTS}
    assert DIGEST==hashlib.sha256(json.dumps(CONFIG,sort_keys=True).encode()).hexdigest()
    print('VERIFY inputs unchanged; fixed configuration hash unchanged; eligible rows=3812; every row held out exactly once',flush=True)
    print('LIMITATIONS exploratory reused development; CIs condition on fitted OOF models and fixed fold queues, no refit or prompt clustering; pooled exact reference assumes independent fold reference draws despite overlapping OOF training sets; no claim of independent information from correlation alone.',flush=True)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--encode',action='store_true'); parser.add_argument('--analyze',action='store_true'); parser.add_argument('--append',action='store_true'); args=parser.parse_args()
    os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'; os.environ['HF_DATASETS_OFFLINE']='1'
    sys.addaudithook(audit)
    previous=read(REPORT).read_bytes() if args.append else None
    heading='## Exploratory B2: frozen all-MiniLM-L6-v2 + fold-local Ridge'
    if previous is not None: assert heading.encode() not in previous
    captured=io.StringIO()
    class Tee:
        def write(self,text): sys.__stdout__.write(text); captured.write(text)
        def flush(self): sys.__stdout__.flush()
    with contextlib.redirect_stdout(Tee()):
        preregister()
        if args.encode: encode()
        if args.analyze: analyze()
        for name in sorted(READS): print('READ_AUDIT '+name)
        print('READ_GUARD allowlisted artifact reads only; network disabled during encode/analysis; no Test/combined corpus; no essay strings printed or persisted',flush=True)
    if args.append:
        section='\n\n'+heading+'\n\n2026-10-24 (Asia/Saigon). Exploratory development only. Original b6398ea encoder/Ridge parameters unchanged; user confirmed normalize_embeddings=False. Native model Normalize produces L2 vectors.\n\n```text\n'+captured.getvalue()+'```\n'
        with REPORT.open('ab') as stream: stream.write(section.encode('utf-8'))
        assert read(REPORT).read_bytes()==previous+section.encode('utf-8')
        print('APPEND_ONLY_PREFIX_UNCHANGED=True previous_SHA256='+hashlib.sha256(previous).hexdigest(),flush=True)


if __name__=='__main__': main()

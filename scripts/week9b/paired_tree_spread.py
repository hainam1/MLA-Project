"""Paired development-only comparison; fixed queues, prompt-cluster bootstrap.

Run --append to append the raw results. No prediction/model artifacts are saved.
"""
import sys
sys.dont_write_bytecode = True
import contextlib
import hashlib
import io
import json
import math
import os

import tree_spread_oof as base
import numpy as np
import pandas as pd
from scipy.stats import hypergeom, spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

ROOT, DEST = base.ROOT, base.DEST
HEADING = '## Week 9b - paired tree-spread versus disagreement on held-out prompts'


def audit(event, args):
    # The existing aggregate results document may be hashed for append proof.
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        path = base.Path(os.fsdecode(args[0])).resolve()
        if path == DEST and args[1] in {'r', 'rb'}:
            return
    base.audit(event, args)


def overlap(scope, out):
    L, t, d = out.L, out.selected_tree_std, out.selected_D
    both, only_t, only_d, neither = [int(mask.sum()) for mask in
        [L&t&d, L&t&~d, L&~t&d, L&~t&~d]]
    ct, cd, K = both+only_t, both+only_d, int(L.sum())
    assert both+only_t+only_d+neither == K
    return dict(scope=scope,n=len(out),K=K,k=int(t.sum()),caught_tree=ct,caught_D=cd,
                difference=ct-cd,both=both,only_tree=only_t,only_D=only_d,neither=neither,
                arithmetic=f'{ct}-{cd}={ct-cd}; {only_t}-{only_d}={ct-cd}; K={both}+{only_t}+{only_d}+{neither}={K}')


def weighted_auc(y, inverse, weights):
    pos = np.bincount(inverse, weights=weights*y)
    neg = np.bincount(inverse, weights=weights*(~y), minlength=len(pos))
    npos, nneg = float(pos.sum()),float(neg.sum())
    if not npos or not nneg:
        return np.nan
    return float(np.dot(pos,np.cumsum(neg)-.5*neg)/(npos*nneg))


def main():
    print('EXPLORATORY DEVELOPMENT ONLY; same GroupKFold(5), 14 features and frozen RF/Ridge parameters as tree_spread_oof.py; seed=42; n_jobs=1; no search.')
    print('PARAMETERS RF trees=300,max_features=sqrt,max_depth=10,min_samples_leaf V=2/G=5; Ridge alpha V=100/G=0.1; train-only median imputation and Ridge StandardScaler.')
    print('DEFINITIONS tree_std=max target population std(ddof=0); D=max(abs(RF-Ridge)); A1=max(abs(y-RF))>=1; A2=max(abs(y-Ridge))>=1; A3=A1&A2; per-fold k=ceil(.20*n); scores descending, essay_id string ascending.')
    before = {p:base.sha(p) for p in base.INPUTS}
    f = pd.read_csv(ROOT/base.INPUTS[0],dtype={'essay_id':str}).sort_values('essay_id',kind='stable').reset_index(drop=True)
    composition = pd.read_csv(ROOT/base.INPUTS[1])
    composition = composition.loc[composition.split_type.eq('prompt_disjoint')]
    features = json.loads((ROOT/base.INPUTS[2]).read_text())
    assert len(f)==3812 and f.essay_id.is_unique and f.normalised_prompt.nunique()==44
    assert f.privacy_review_status.eq('not_flagged').all() and f.source_partition.eq('official_train').all()
    assert set(f.split)=={'model_train','validation'} and len(features)==14
    assert np.isfinite(f[features+['Vocabulary','Grammar']].to_numpy()).all()
    frames=[]
    for fold,(tr,held) in enumerate(GroupKFold(5).split(f,groups=f.normalised_prompt),1):
        train,val=f.iloc[tr],f.iloc[held]
        saved=composition.loc[composition.fold.eq(fold)]
        assert val.groupby('normalised_prompt').size().to_dict()==saved.set_index('heldout_prompt').heldout_prompt_essays.to_dict()
        assert not set(train.normalised_prompt)&set(val.normalised_prompt)
        assert saved.train_essays.eq(len(train)).all() and saved.heldout_essays.eq(len(val)).all()
        out=val[['essay_id','normalised_prompt','word_count']].reset_index(drop=True).copy()
        stds,rf_errors,ridge_errors,diffs=[],[],[],[]
        for target,alpha,leaf in [('Vocabulary',100.,2),('Grammar',.1,5)]:
            rf=make_pipeline(SimpleImputer(strategy='median'),RandomForestRegressor(
                n_estimators=300,max_features='sqrt',max_depth=10,min_samples_leaf=leaf,random_state=42,n_jobs=1))
            ridge=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),Ridge(alpha=alpha))
            rf.fit(train[features],train[target]); ridge.fit(train[features],train[target])
            x=rf[:-1].transform(val[features])
            trees=np.array([tree.predict(x) for tree in rf[-1].estimators_])
            rf_pred=rf.predict(val[features]); ridge_pred=ridge.predict(val[features])
            assert trees.shape==(300,len(val)) and np.allclose(trees.mean(axis=0),rf_pred,rtol=0,atol=1e-12)
            stds.append(trees.std(axis=0,ddof=0))
            rf_errors.append(abs(val[target].to_numpy()-rf_pred))
            ridge_errors.append(abs(val[target].to_numpy()-ridge_pred))
            diffs.append(abs(rf_pred-ridge_pred))
        out['tree_std']=np.maximum(*stds); out['D']=np.maximum(*diffs)
        out['RF_error']=np.maximum(*rf_errors)
        out['L']=out.RF_error.ge(1)
        out['A3']=out.L & (np.maximum(*ridge_errors)>=1)
        out['fold']=fold
        k=math.ceil(.2*len(out)); assert saved.k.eq(k).all()
        for signal in ['tree_std','D']:
            out['selected_'+signal]=out.index.isin(base.top(out,signal,k))
        frames.append(out)
        print(f'FIT_COMPLETE fold={fold}; n={len(out)}; k={k}; matching_t3_prompt_composition=True; overlapping_prompts=0',flush=True)
    pooled=pd.concat(frames,ignore_index=True)
    scopes=[('fold'+str(i),out) for i,out in enumerate(frames,1)]+[('pooled',pooled)]
    observed=[overlap(scope,out) for scope,out in scopes]
    assert (observed[-1]['caught_tree'],observed[-1]['caught_D'],int(pooled.L.sum()),int(pooled.A3.sum()))==(96,88,386,276)
    base.table('PAIRED_CAUGHT_AND_OVERLAP (A1)',observed)
    print('FOLD_SIGN_CHECK: report fold differences only; an exact paired permutation/sign check on five fold differences is not meaningful here (n=5); no sign-test p value computed.')
    print('BOOTSTRAP_CHOICE: 44 normalised-prompt clusters sampled with replacement, 44 draws per resample, 2000 resamples, default_rng(42). Keep fold queues and scores fixed; duplicate all essays of each sampled prompt. No reranking, refitting or budget recomputation. Resampled N and caught totals can vary.')
    prompt_codes,prompts=pd.factorize(pooled.normalised_prompt,sort=True)
    y=pooled.L.to_numpy()
    inv={name:np.unique(pooled[name],return_inverse=True)[1] for name in ['tree_std','D']}
    fixed_delta=y.astype(int)*(pooled.selected_tree_std.to_numpy().astype(int)-pooled.selected_D.to_numpy().astype(int))
    rng=np.random.default_rng(42); caught_samples=[]; auc_samples=[]
    for _ in range(2000):
        counts=np.bincount(rng.integers(0,len(prompts),len(prompts)),minlength=len(prompts))
        weights=counts[prompt_codes]
        caught_samples.append(int(np.dot(weights,fixed_delta)))
        a=weighted_auc(y,inv['tree_std'],weights); b=weighted_auc(y,inv['D'],weights)
        if np.isfinite(a) and np.isfinite(b): auc_samples.append(a-b)
    one=np.ones(len(pooled)); at=weighted_auc(y,inv['tree_std'],one); ad=weighted_auc(y,inv['D'],one)
    bootstrap=[]
    for name,point,values,formula in [
        ('caught_tree-caught_D',observed[-1]['difference'],caught_samples,'96-88=8'),
        ('AUROC_tree-AUROC_D',at-ad,auc_samples,f'{at:.17g}-{ad:.17g}={at-ad:.17g}')]:
        values=np.asarray(values); positive=int((values>0).sum())
        bootstrap.append(dict(metric=name,observed=point,arithmetic=formula,
            CI_low=float(np.percentile(values,2.5)),CI_high=float(np.percentile(values,97.5)),
            positive_resamples=positive,valid_resamples=len(values),skipped=2000-len(values),
            share_positive=positive/len(values),share_arithmetic=f'{positive}/{len(values)}={positive/len(values):.17g}',
            zero_resamples=int((values==0).sum()),negative_resamples=int((values<0).sum())))
    base.table('PAIRED_PROMPT_CLUSTER_BOOTSTRAP (95% percentile CI; linear interpolation)',bootstrap)
    print('A3_INTERPRETATION: evaluate the same whole-fold fixed queues against A3 labels (K=276); do not rank only the already-known positives, which would make capture tautological. N and per-fold budgets remain unchanged.')
    a3_rows=[]; corr=[]
    for scope,out in scopes:
        n,K=len(out),int(out.A3.sum())
        corr.append(dict(scope=scope,A3_n=K,spearman_tree_std_RF_error=float(spearmanr(out.loc[out.A3,'tree_std'],out.loc[out.A3,'RF_error']).statistic)))
        for signal in ['tree_std','D']:
            k=int(out['selected_'+signal].sum()); caught=int((out.A3&out['selected_'+signal]).sum())
            row=dict(scope=scope,signal=signal,n=n,K=K,k=k,caught=caught,capture=f'{caught}/{K}={caught/K:.17g}')
            if scope!='pooled':
                expected=k*K/n
                row.update(expected=expected,expected_arithmetic=f'{k}*{K}/{n}={expected:.17g}',
                    exact_p=float(hypergeom.sf(caught-1,n,K,k)),p_formula=f'hypergeom.sf({caught-1},{n},{K},{k})')
            else:
                terms=[(int(z['selected_'+signal].sum()),int(z.A3.sum()),len(z)) for z in frames]
                expected=sum(kf*Kf/nf for kf,Kf,nf in terms); dist=np.array([1.])
                for kf,Kf,nf in terms:
                    dist=np.convolve(dist,hypergeom.pmf(np.arange(min(kf,Kf)+1),nf,Kf,kf))
                assert abs(dist.sum()-1)<1e-12
                row.update(expected=expected,expected_arithmetic='+'.join(f'{kf}*{Kf}/{nf}' for kf,Kf,nf in terms)+f'={expected:.17g}',
                    exact_p=float(dist[caught:].sum()),p_formula=f'P(sum fold Hypergeom >= {caught}); exact convolution',
                    global_formula_p=float(hypergeom.sf(caught-1,n,K,k)),global_formula=f'hypergeom.sf({caught-1},{n},{K},{k}); global-uniform reference')
            a3_rows.append(row)
    base.table('A3_CAPTURE (same queues; pooled exact p respects fold budgets)',a3_rows)
    base.table('A3_ONLY_SPEARMAN (RF_error=max target abs RF error)',corr)
    print('CAVEATS: exploratory comparisons; fixed-score prompt bootstrap conditions on fitted OOF models and queues, without modeling retraining variability. Shared training data induces cross-fold dependence. Share of bootstrap differences >0 is not a permutation p value. A3 membership may arise from different triggering targets for the two models.')
    assert before=={p:base.sha(p) for p in base.INPUTS}
    for p in sorted(base.READS):print('READ_AUDIT '+p+' SHA256='+before[p])
    print(f'READ_GUARD artifact_reads={len(base.READS)}; allowlisted_only={base.READS<=set(base.INPUTS)}; blocked_attempts={len(base.BLOCKED)}; no Test prediction/label file opened; inputs_unchanged=True')
    print('ALL_NUMBERS_PRINTED=True')


if __name__=='__main__':
    sys.addaudithook(audit)
    capture=io.StringIO()
    class Tee:
        def write(self,text):sys.__stdout__.write(text); capture.write(text)
        def flush(self):sys.__stdout__.flush()
    with threadpool_limits(limits=1),contextlib.redirect_stdout(Tee()):main()
    if '--append' in sys.argv:
        old=DEST.read_bytes(); old_sha=hashlib.sha256(old).hexdigest()
        assert HEADING.encode() not in old,'Section already present; refusing duplicate append'
        text='\n\n'+HEADING+'\n\nProducer: `scripts/week9b/paired_tree_spread.py`; command: `.venv/Scripts/python.exe -u scripts/week9b/paired_tree_spread.py --append`. Exploratory development only.\n\n```text\n'+capture.getvalue()+'```\n'
        with DEST.open('ab') as stream:stream.write(text.encode('utf-8'))
        current=DEST.read_bytes(); prefix_sha=hashlib.sha256(current[:len(old)]).hexdigest()
        assert current.startswith(old) and old_sha==prefix_sha
        print(f'APPEND_PREFIX_UNCHANGED=True; old_bytes={len(old)}\nOLD_PREFIX_SHA256={old_sha}\nNEW_PREFIX_SHA256={prefix_sha}')

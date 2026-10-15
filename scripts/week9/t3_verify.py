"""Exploratory extension designed after Official Test was used."""
import math
import sys
import numpy as np
import pandas as pd
from scipy.stats import hypergeom
from sklearn.metrics import roc_auc_score,mean_absolute_error,mean_squared_error,r2_score
from sklearn.model_selection import GroupKFold,KFold
from t3_evidence import *

SCORES={'Disagreement':'D','Ridge Extremity':'extremity','Shortest-first':'negative_word_count'}

def read(name):
    return pd.read_csv(OUT/name,dtype={'essay_id':str},float_precision='round_trip')

def masks(frame):
    a1=np.maximum(abs(frame.RF_V-frame.y_V),abs(frame.RF_G-frame.y_G))>=1
    a2=np.maximum(abs(frame.Ridge_V-frame.y_V),abs(frame.Ridge_G-frame.y_G))>=1
    return {'A1_RF':np.asarray(a1),'A2_Ridge':np.asarray(a2),'A3_Both_wrong':np.asarray(a1&a2)}

def main():
    print(LABEL,flush=True)
    print('COMMAND: .venv/Scripts/python.exe -u scripts/week9/t3_verify.py')
    print('SEED=42; verification only; no fitting')
    dev=read('t3_eligible_development.csv').sort_values('essay_id').reset_index(drop=True)
    pred=read('t3_heldout_predictions.csv')
    composition=read('t3_fold_composition.csv'); audit=read('t3_training_audit.csv')
    ranks=read('t3_rankings.csv'); pooled=read('t3_pooled.csv')
    aucs=read('t3_auroc.csv'); boots=read('t3_bootstrap.csv')
    random=read('t3_random_draws.csv'); joints=read('t3_joint_random_draws.csv')
    regress=read('t3_regression.csv')
    for filename in ['t3_training_output_hashes.csv','t3_training_sources.csv','t3_eligibility_sources.csv']:
        for row in read(filename).itertuples():
            assert sha((ROOT/row.path).read_bytes())==row.sha256,row.path
    assert len(dev)==3812 and dev.normalised_prompt.nunique()==44
    assert len(pred)==2*len(dev)
    for split,splitter in [('prompt_disjoint',GroupKFold(5)),('ordinary_KFold',KFold(5,shuffle=True,random_state=42))]:
        p=pred.loc[pred.split_type.eq(split)].reset_index(drop=True)
        assert p.essay_id.is_unique and set(p.essay_id)==set(dev.essay_id)
        iterator=splitter.split(dev,groups=dev.normalised_prompt) if split=='prompt_disjoint' else splitter.split(dev)
        for fold,(train_ix,held_ix) in enumerate(iterator,1):
            train=dev.iloc[train_ix]; held=dev.iloc[held_ix]
            sub=p.loc[p.fold.eq(fold)].reset_index(drop=True)
            assert set(sub.essay_id)==set(held.essay_id)
            overlap=set(train.normalised_prompt)&set(held.normalised_prompt)
            if split=='prompt_disjoint': assert not overlap
            comp=composition.loc[composition.split_type.eq(split)&composition.fold.eq(fold)]
            assert set(comp.heldout_prompt)==set(held.normalised_prompt)
            assert comp.heldout_prompt_essays.sum()==len(held)
            assert (comp.overlap_prompt_count==len(overlap)).all()
            for row in comp.itertuples():
                assert row.train_same_prompt_essays==int(train.normalised_prompt.eq(row.heldout_prompt).sum())
            for row in audit.loc[audit.split_type.eq(split)&audit.fold.eq(fold)].itertuples():
                assert row.train_id_sha256==sha('\n'.join(train.essay_id).encode())
                assert row.heldout_id_sha256==sha('\n'.join(held.essay_id).encode())
                assert row.training_n==row.scaler_fit_n==len(train)
                assert row.rf_trees==300 and row.rf_random_state==42 and row.rf_n_jobs==1
                assert np.allclose(sub['median_ridge_'+row.target],row.ridge_training_prediction_median)
            k=math.ceil(.2*len(sub)); ys=masks(sub)
            assert np.array_equal(sub.D,np.maximum(abs(sub.RF_V-sub.Ridge_V),abs(sub.RF_G-sub.Ridge_G)))
            assert np.allclose(sub.extremity,np.maximum(abs(sub.Ridge_V-sub.median_ridge_V),abs(sub.Ridge_G-sub.median_ridge_G)),atol=1e-14,rtol=0)
            rng=np.random.default_rng(42)
            ix_draws=[rng.choice(len(sub),size=k,replace=False) for _ in range(1000)]
            for anchor,y in ys.items():
                assert np.array_equal(sub[anchor],y)
                saved=random.loc[random.split_type.eq(split)&random.fold.eq(fold)&random.anchor.eq(anchor)]
                recalculated=np.array([int(y[ix].sum()) for ix in ix_draws])
                assert np.array_equal(saved.caught,recalculated)
                assert np.allclose(saved.exact_hypergeom_p,hypergeom.sf(saved.caught-1,len(sub),int(y.sum()),k),atol=1e-14,rtol=0)
            for row in ranks.loc[ranks.split_type.eq(split)&ranks.fold.eq(fold)].itertuples():
                y=ys[row.anchor]; K=int(y.sum()); assert K==row.K and k==row.k
                if row.ranking!='Random':
                    ids=sub.sort_values([SCORES[row.ranking],'essay_id'],ascending=[False,True]).head(k).index
                    assert int(y[ids].sum())==row.caught
                    assert np.isclose(row.exact_hypergeom_p,hypergeom.sf(row.caught-1,len(sub),K,k),atol=1e-14,rtol=0)
                    assert np.array_equal(sub['selected_'+SCORES[row.ranking]],sub.index.isin(ids))
                else:
                    saved=random.loc[random.split_type.eq(split)&random.fold.eq(fold)&random.anchor.eq(row.anchor)]
                    assert np.isclose(row.caught,saved.caught.mean())
                    assert np.allclose([row.random_p2_5,row.random_p97_5],np.percentile(saved.caught,[2.5,97.5]))
                assert np.isclose(row.capture,row.caught/K)
                assert np.isclose(row.lift,row.caught/(k*K/len(sub)))
        # Rebuild independent-fold joint random selections exactly, not from tail summaries.
        rng=np.random.default_rng(42)
        groups={i:p.loc[p.fold.eq(i)].reset_index(drop=True) for i in range(1,6)}
        calculated={a:np.zeros((1000,5),dtype=int) for a in masks(p)}
        for iteration in range(1000):
            for fold,sub in groups.items():
                ix=rng.choice(len(sub),size=int(sub.budget_k.iloc[0]),replace=False)
                for anchor,y in masks(sub).items():
                    calculated[anchor][iteration,fold-1]=int(y[ix].sum())
        for anchor,values in calculated.items():
            saved=joints.loc[joints.split_type.eq(split)&joints.anchor.eq(anchor)].pivot(index='iteration',columns='fold',values='caught').to_numpy()
            assert np.array_equal(values,saved)
            total=values.sum(axis=1)
            for row in pooled.loc[pooled.split_type.eq(split)&pooled.anchor.eq(anchor)].itertuples():
                selected=ranks.loc[ranks.split_type.eq(split)&ranks.anchor.eq(anchor)&ranks.ranking.eq(row.ranking)]
                assert row.K==selected.K.sum() and row.k==selected.k.sum()
                assert np.isclose(row.expected_random,selected.expected_random.sum())
                if row.ranking!='Random':
                    assert row.caught==selected.caught.sum()
                    assert row.joint_draws_ge_observed==int((total>=row.caught).sum())
                    assert row.pooled_joint_random_p==int((total>=row.caught).sum())/1000
                else:
                    assert np.isclose(row.caught,total.mean())
                    assert np.allclose([row.random_p2_5,row.random_p97_5],np.percentile(total,[2.5,97.5]))
                assert np.isclose(row.lift,row.caught/row.expected_random)
        for scope in [str(i) for i in range(1,6)]+['pooled']:
            sub=p if scope=='pooled' else p.loc[p.fold.eq(int(scope))].reset_index(drop=True)
            for row in regress.loc[regress.split_type.eq(split)&regress.fold.astype(str).eq(scope)].itertuples():
                y=sub['y_'+row.target]; prediction=sub[row.model+'_'+row.target]
                assert np.allclose([row.MAE,row.RMSE,row.R2],[mean_absolute_error(y,prediction),np.sqrt(mean_squared_error(y,prediction)),r2_score(y,prediction)],atol=1e-14,rtol=0)
            ysets=masks(sub)
            for row in aucs.loc[aucs.split_type.eq(split)&aucs.fold.astype(str).eq(scope)].itertuples():
                y=ysets[row.anchor]; score=sub[row.score]
                assert np.isclose(row.AUROC,roc_auc_score(y,score),atol=1e-14,rtol=0)
                b=boots.loc[boots.split_type.eq(split)&boots.fold.astype(str).eq(scope)&boots.anchor.eq(row.anchor)&boots.ranking.eq(row.ranking),'AUROC'].to_numpy()
                assert len(b)==2000
                assert np.allclose(np.percentile(b[np.isfinite(b)],[2.5,97.5]),[row.CI_low,row.CI_high],atol=1e-14,rtol=0)
                # Independent sklearn checks of initial bootstrap replicates validate weighted implementation.
                rng=np.random.default_rng(42)
                for i in range(3):
                    ix=rng.integers(0,len(sub),size=len(sub))
                    assert np.isclose(b[i],roc_auc_score(y[ix],score.iloc[ix]),atol=1e-14,rtol=0)
    for tag in ['t3_eligibility','t3_training']:
        assert (OUT/f'logs/{tag}_run1.log').read_bytes()==(OUT/f'logs/{tag}_run2.log').read_bytes()
    print('PASS source/output hashes and exact eligible population; reconstructed GroupKFold/KFold memberships; prompt separation/overlap and training-ID/scaler-fit audits.')
    print('PASS all held-out labels, exact queue selections, captured counts, per-fold hypergeometric p values, every standalone random draw and every independent-fold joint draw.')
    print('PASS all pooled sums, expectations and empirical joint p values; no cross-fold queue reranking; all regression metrics independently recomputed.')
    print('PASS every AUROC checked with sklearn; every interval recomputed from saved bootstrap replicates; initial bootstrap replicates independently checked with sklearn.')
    print('PASS diagnosis and training each have identical fresh-process raw outputs; all recorded prediction/artifact hashes match.')

if __name__=='__main__':
    if '--capture' in sys.argv:
        repeat('t3_verify.py','t3_verification','Artifact verification',
          'Independent artifact checks use saved eligible-development and new Task 3 outputs only; no fitting or Official Test file access. Every AUROC is checked against scikit-learn, and initial bootstrap replicates are checked independently to validate the weighted-count implementation. All fold assignments, queue selections, random draws and pooled tail counts are reconstructed. Raw checks and fresh-process hashes follow.')
    else:
        main()

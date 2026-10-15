"""Exploratory extension designed after Official Test was used.

Fixed GroupKFold and KFold development extension. No search or Test access.
"""
import json
import math
import sys
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.stats import hypergeom
from sklearn.model_selection import GroupKFold, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from threadpoolctl import threadpool_limits
from t3_evidence import *

sys.path.insert(0,str(ROOT/'src'))
from mla_project.features.build_features import FEATURE_NAMES
from mla_project.models.train_ridge import build_ridge
from mla_project.models.train_random_forest import build_random_forest

SEED=42
SIGNALS={'Disagreement':'D','Ridge Extremity':'extremity','Shortest-first':'negative_word_count'}
ANCHORS=['A1_RF','A2_Ridge','A3_Both_wrong']

def labels(f):
    a1=np.maximum(abs(f.RF_V-f.y_V),abs(f.RF_G-f.y_G))>=1.0
    a2=np.maximum(abs(f.Ridge_V-f.y_V),abs(f.Ridge_G-f.y_G))>=1.0
    return {'A1_RF':np.asarray(a1),'A2_Ridge':np.asarray(a2),'A3_Both_wrong':np.asarray(a1&a2)}

def ordered(f,col,k):
    return f.sort_values([col,'essay_id'],ascending=[False,True],kind='stable').head(k).index.to_numpy()

def regression(f,split,fold):
    rows=[]
    for model in ['Ridge','RF']:
        for t in ['V','G']:
            y=f['y_'+t].to_numpy(); p=f[model+'_'+t].to_numpy()
            n=len(y); sae=float(abs(y-p).sum()); sse=float(((y-p)**2).sum()); sst=float(((y-y.mean())**2).sum())
            mae=float(mean_absolute_error(y,p)); rmse=float(np.sqrt(mean_squared_error(y,p))); r2=float(r2_score(y,p))
            rows.append(dict(split_type=split,fold=fold,model=model,target=t,n=n,MAE=mae,RMSE=rmse,R2=r2,sum_absolute_error=sae,sum_squared_error=sse,sum_squared_total=sst,mae_arithmetic=f'{sae:.17g}/{n}={mae:.17g}',rmse_arithmetic=f'sqrt({sse:.17g}/{n})={rmse:.17g}',r2_arithmetic=f'1-({sse:.17g}/{sst:.17g})={r2:.17g}'))
    return rows

def weighted_auc(y,inverse,weights,levels):
    positive=np.bincount(inverse,weights=weights*y,minlength=levels)
    negative=np.bincount(inverse,weights=weights*(~y),minlength=levels)
    npos=float(positive.sum()); nneg=float(negative.sum())
    if not npos or not nneg:
        return np.nan,np.nan,npos,nneg
    u=float(np.dot(positive,np.cumsum(negative)-0.5*negative))
    return u/(npos*nneg),u,npos,nneg

def aucs(f,split,fold):
    ys=labels(f); n=len(f); specs={}
    for ranking,col in SIGNALS.items():
        values,inverse=np.unique(f[col].to_numpy(),return_inverse=True)
        specs[ranking]=(inverse,len(values))
    estimates={(a,s):[] for a in ANCHORS for s in SIGNALS}
    rng=np.random.default_rng(SEED)
    for rep in range(2000):
        # Same ordinary essay bootstrap sample for all signals and anchors in a scope.
        indices=rng.integers(0,n,size=n)
        weights=np.bincount(indices,minlength=n)
        for a,y in ys.items():
            for ranking,(inverse,levels) in specs.items():
                estimates[a,ranking].append(weighted_auc(y,inverse,weights,levels)[0])
    rows=[]; bootstrap=[]
    for a,y in ys.items():
        for ranking,(inverse,levels) in specs.items():
            point,u,pos,neg=weighted_auc(y,inverse,np.ones(n),levels)
            values=np.array(estimates[a,ranking]); valid=values[np.isfinite(values)]
            lo,hi=np.percentile(valid,[2.5,97.5]) if len(valid) else (np.nan,np.nan)
            rows.append(dict(split_type=split,fold=fold,anchor=a,ranking=ranking,score=SIGNALS[ranking],n=n,K=int(pos),negative_n=int(neg),AUROC=point,CI_low=lo,CI_high=hi,u=u,auroc_arithmetic=f'{u:.17g}/({int(pos)}*{int(neg)})={point:.17g}' if pos and neg else 'NA one class',bootstrap_resamples=2000,valid_resamples=len(valid),skipped_resamples=2000-len(valid),seed=SEED))
            bootstrap.extend(dict(split_type=split,fold=fold,anchor=a,ranking=ranking,resample=i+1,AUROC=v) for i,v in enumerate(values))
    return rows,bootstrap

def metrics_row(split,fold,a,ranking,n,K,k,caught,expected,p,draws=None,pooled=False):
    capture=caught/K if K else np.nan
    precision=caught/k
    # Pooled lift compares caught against sum(k_f*K_f/n_f), respecting fold budgets/prevalences.
    lift=caught/expected if expected else np.nan
    return dict(split_type=split,fold=fold,anchor=a,ranking=ranking,n=n,K=K,k=k,caught=caught,capture=capture,precision=precision,lift=lift,expected_random=expected,exact_hypergeom_p=p if not pooled else np.nan,pooled_joint_random_p=p if pooled else np.nan,
        capture_arithmetic=f'{caught}/{K}={capture:.17g}' if K else 'NA K=0',precision_arithmetic=f'{caught}/{k}={precision:.17g}',lift_arithmetic=f'{caught}/{expected:.17g}={lift:.17g}' if expected else 'NA expected=0',expected_arithmetic='sum(per-fold k*K/n)' if pooled else f'{k}*{K}/{n}={expected:.17g}',p_expression=(f'joint_count_ge/{1000}={p:.17g}' if pooled and ranking!='Random' else (f'hypergeom.sf({caught-1},{n},{K},{k})={p:.17g}' if ranking!='Random' else 'NA Random mean is not an integer observation')),
        random_mean=float(np.mean(draws)) if draws is not None else np.nan,random_p2_5=float(np.percentile(draws,2.5)) if draws is not None else np.nan,random_p97_5=float(np.percentile(draws,97.5)) if draws is not None else np.nan,random_mean_arithmetic=f'{int(np.sum(draws))}/1000={float(np.mean(draws)):.17g}' if draws is not None else '',seed=SEED)

def main():
    print(LABEL,flush=True)
    print('COMMAND: .venv/Scripts/python.exe -u scripts/week9/t3_evaluate.py',flush=True)
    print(f'VERSIONS Python={sys.version.split()[0]}; numpy={np.__version__}; pandas={pd.__version__}; scipy={scipy.__version__}; sklearn={sklearn.__version__}',flush=True)
    print('SEEDS RF=42; ordinary_KFold=42; per-fold_random=42; joint_random=42; bootstrap=42; PYTHONHASHSEED=42; n_jobs=1; numeric threadpools=1',flush=True)
    files=['reports/week9/t3_eligible_development.csv','reports/week9/t3_eligibility_checks.csv','outputs/phase6/selected_parameters.json','docs/evaluation_protocol_freeze.md','src/mla_project/models/train_ridge.py','src/mla_project/models/train_random_forest.py','src/mla_project/features/build_features.py','scripts/week9/t3_evaluate.py','scripts/week9/t3_evidence.py']
    before={p:sha((ROOT/p).read_bytes()) for p in files}
    f=pd.read_csv(OUT/'t3_eligible_development.csv',dtype={'essay_id':str}).sort_values('essay_id',kind='stable').reset_index(drop=True)
    assert len(f)==3812 and f.normalised_prompt.nunique()==44 and f.essay_id.is_unique
    assert f.privacy_review_status.eq('not_flagged').all() and f.source_partition.eq('official_train').all()
    assert np.isfinite(f[[*FEATURE_NAMES,'Vocabulary','Grammar']].to_numpy()).all()
    frozen=json.loads((ROOT/'outputs/phase6/selected_parameters.json').read_text())
    expected={'ridge_vocabulary':{'alpha':100.0},'ridge_grammar':{'alpha':0.1},'random_forest_vocabulary':{'max_depth':10,'max_features':'sqrt','min_samples_leaf':2,'n_estimators':300},'random_forest_grammar':{'max_depth':10,'max_features':'sqrt','min_samples_leaf':5,'n_estimators':300}}
    assert frozen==expected, 'STOP: frozen parameters differ'
    protocol=(ROOT/'docs/evaluation_protocol_freeze.md').read_text()
    assert 'median of Ridge Vocabulary predictions' in protocol and 'eligible model-train essays' in protocol
    print('POPULATION eligible_model_train=3050; eligible_Validation=762; total=3812; normalised_prompt_groups=44; both designs use identical essay_id string ascending order',flush=True)
    print('BUDGET_RULE k=ceil(0.20*n), as frozen; centres=median of fold-trained Ridge predictions on fold training essays, separately per target; no held-out values used for centres',flush=True)
    print('PREPROCESSING project build_ridge: median imputation -> StandardScaler -> Ridge; project build_random_forest: median imputation -> RF; each pipeline is fitted on fold training rows only; no search',flush=True)
    print('POOLING selections are made within folds and summed, never re-ranked across folds; pooled expected=sum(k_f*K_f/n_f); pooled lift=caught/pooled expected; pooled p from independent-fold joint draws',flush=True)
    print('BOOTSTRAP ordinary essay resampling with replacement, 2000 resamples, default_rng(42) reset per scope, paired across anchors/signals; percentile CI with linear interpolation; single-class resamples skipped and counted; pooled AUROC uses concatenated raw scores, without changing within-fold selections',flush=True)
    regression_rows=[]; rankings=[]; pooled_rows=[]; auc_rows=[]; boot_rows=[]; composition=[]; predictions=[]; centres=[]; random_rows=[]; joint_rows=[]
    for split,splitter in [('prompt_disjoint',GroupKFold(n_splits=5)),('ordinary_KFold',KFold(n_splits=5,shuffle=True,random_state=SEED))]:
        split_frames=[]
        iterator=splitter.split(f,groups=f.normalised_prompt) if split=='prompt_disjoint' else splitter.split(f)
        for fold,(train_index,held_index) in enumerate(iterator,1):
            train=f.iloc[train_index]; held=f.iloc[held_index]
            train_prompts=set(train.normalised_prompt); held_prompts=set(held.normalised_prompt)
            overlap=train_prompts&held_prompts
            if split=='prompt_disjoint':
                assert not overlap
            n=len(held); k=math.ceil(.2*n)
            print(f'FOLD split={split}; fold={fold}; train_essays={len(train)}; heldout_essays={n}; train_prompts={len(train_prompts)}; heldout_prompts={len(held_prompts)}; overlapping_prompts={len(overlap)}; disjoint={not overlap}; k=ceil(0.20*{n})={k}',flush=True)
            for prompt,count in held.groupby('normalised_prompt',sort=True).size().items():
                composition.append(dict(split_type=split,fold=fold,train_essays=len(train),heldout_essays=n,train_prompt_count=len(train_prompts),heldout_prompt_count=len(held_prompts),overlap_prompt_count=len(overlap),disjoint=not overlap,heldout_prompt=prompt,heldout_prompt_essays=int(count),train_same_prompt_essays=int(train.normalised_prompt.eq(prompt).sum()),k=k))
                print(f'HELDOUT_PROMPT split={split}; fold={fold}; prompt={json.dumps(prompt)}; heldout_essays={int(count)}; train_essays={int(train.normalised_prompt.eq(prompt).sum())}',flush=True)
            out=held[['essay_id','normalised_prompt','word_count','Vocabulary','Grammar']].rename(columns={'Vocabulary':'y_V','Grammar':'y_G'}).copy().reset_index(drop=True)
            out['split_type']=split; out['fold']=fold
            xtrain=train[list(FEATURE_NAMES)]; xheld=held[list(FEATURE_NAMES)]
            centre_values={}
            for t,target,alpha,leaf in [('V','Vocabulary',100.0,2),('G','Grammar',.1,5)]:
                ridge=build_ridge(alpha=alpha)
                rf=build_random_forest(n_estimators=300,max_features='sqrt',max_depth=10,min_samples_leaf=leaf,random_state=SEED,n_jobs=1)
                ridge.fit(xtrain,train[target]); rf.fit(xtrain,train[target])
                assert int(ridge.named_steps['scaler'].n_samples_seen_)==len(train)
                assert np.allclose(ridge.named_steps['scaler'].mean_,xtrain.mean().to_numpy())
                out['Ridge_'+t]=ridge.predict(xheld); out['RF_'+t]=rf.predict(xheld)
                center=float(np.median(ridge.predict(xtrain))); centre_values[t]=center
                centres.append(dict(split_type=split,fold=fold,target=t,training_n=len(train),ridge_alpha=alpha,rf_trees=300,rf_max_features='sqrt',rf_max_depth=10,rf_min_samples_leaf=leaf,rf_random_state=42,rf_n_jobs=1,ridge_training_prediction_median=center,scaler_fit_n=int(ridge.named_steps['scaler'].n_samples_seen_),train_id_sha256=sha('\n'.join(train.essay_id).encode()),heldout_id_sha256=sha('\n'.join(held.essay_id).encode())))
            print(f'CENTRES split={split}; fold={fold}; median_ridge_vocabulary={centre_values["V"]:.17g}; median_ridge_grammar={centre_values["G"]:.17g}; fit_scaler_on_train_only=True; rf_random_state=42',flush=True)
            for t in ['V','G']:
                out['e_RF_'+t]=out['RF_'+t]-out['y_'+t]
                out['e_Ridge_'+t]=out['Ridge_'+t]-out['y_'+t]
                out['d_'+t]=abs(out['RF_'+t]-out['Ridge_'+t])
            out['D']=out[['d_V','d_G']].max(axis=1)
            out['extremity']=np.maximum(abs(out.Ridge_V-centre_values['V']),abs(out.Ridge_G-centre_values['G']))
            out['negative_word_count']=-out.word_count
            for t in ['V','G']:
                out['median_ridge_'+t]=centre_values[t]
            out['budget_k']=k
            ys=labels(out)
            rng=np.random.default_rng(SEED)
            indices=[rng.choice(n,size=k,replace=False) for _ in range(1000)]
            for a,y in ys.items():
                out[a]=y
                K=int(y.sum()); draws=np.array([int(y[ix].sum()) for ix in indices]); expectation=k*K/n
                for ranking,col in [('Random',None),*SIGNALS.items()]:
                    if col:
                        selected=ordered(out,col,k); caught=int(y[selected].sum())
                        out['selected_'+col]=out.index.isin(selected)
                        p=float(hypergeom.sf(caught-1,n,K,k))
                    else:
                        caught=float(draws.mean()); p=np.nan
                    rankings.append(metrics_row(split,fold,a,ranking,n,K,k,caught,expectation,p,draws if not col else None))
                for i,value in enumerate(draws):
                    random_rows.append(dict(split_type=split,fold=fold,anchor=a,draw=i+1,n=n,K=K,k=k,caught=int(value),exact_hypergeom_p=float(hypergeom.sf(value-1,n,K,k))))
            regression_rows.extend(regression(out,split,str(fold)))
            rows,boots=aucs(out,split,str(fold)); auc_rows.extend(rows); boot_rows.extend(boots)
            split_frames.append(out); predictions.append(out)
            print(f'FOLD_COMPLETE split={split}; fold={fold}; training_predictions_rankings_and_bootstrap_finished=True',flush=True)
        pooled=pd.concat(split_frames,ignore_index=True)
        assert len(pooled)==len(f) and pooled.essay_id.is_unique and set(pooled.essay_id)==set(f.essay_id)
        regression_rows.extend(regression(pooled,split,'pooled'))
        rows,boots=aucs(pooled,split,'pooled'); auc_rows.extend(rows); boot_rows.extend(boots)
        # Independent selections across folds for each joint replicate. Per-fold standalone
        # references above retain the required reset-to-42 seed; joint reference is separate.
        rng=np.random.default_rng(SEED)
        joint={a:np.zeros(1000,dtype=int) for a in ANCHORS}
        for iteration in range(1000):
            for fold,out in enumerate(split_frames,1):
                n=len(out); k=int(out.budget_k.iloc[0]); ix=rng.choice(n,size=k,replace=False)
                ys=labels(out)
                for a,y in ys.items():
                    caught=int(y[ix].sum()); joint[a][iteration]+=caught
                    joint_rows.append(dict(split_type=split,anchor=a,iteration=iteration+1,fold=fold,caught=caught))
        for a in ANCHORS:
            for ranking in ['Random',*SIGNALS]:
                fold_rows=[r for r in rankings if r['split_type']==split and r['anchor']==a and r['ranking']==ranking]
                K=sum(r['K'] for r in fold_rows); k=sum(r['k'] for r in fold_rows)
                expected_count=sum(r['expected_random'] for r in fold_rows)
                caught=float(joint[a].mean()) if ranking=='Random' else sum(r['caught'] for r in fold_rows)
                tail=int((joint[a]>=caught).sum()) if ranking!='Random' else None
                p=tail/1000 if tail is not None else np.nan
                row=metrics_row(split,'pooled',a,ranking,len(f),K,k,caught,expected_count,p,joint[a] if ranking=='Random' else None,pooled=True)
                row['joint_draws_ge_observed']=tail
                row['expected_arithmetic']='+'.join(f'{r["expected_random"]:.17g}' for r in fold_rows)+f'={expected_count:.17g}'
                row['caught_arithmetic']=('+' .join(str(r['caught']) for r in fold_rows)+f'={caught}') if ranking!='Random' else row['random_mean_arithmetic']
                row['K_arithmetic']='+'.join(str(r['K']) for r in fold_rows)+f'={K}'
                row['p_expression']=f'{tail}/1000={p:.17g}' if tail is not None else 'NA Random mean is not an integer observation'
                pooled_rows.append(row)
        print(f'SPLIT_COMPLETE split={split}; pooled_n={len(pooled)}; no_cross_fold_queue_reranking=True',flush=True)
    save('t3_fold_composition.csv',composition)
    save('t3_regression.csv',regression_rows)
    save('t3_rankings.csv',rankings)
    save('t3_auroc.csv',auc_rows)
    save('t3_pooled.csv',pooled_rows,True)
    save('t3_heldout_predictions.csv',pd.concat(predictions,ignore_index=True))
    save('t3_bootstrap.csv',boot_rows)
    save('t3_training_audit.csv',centres)
    save('t3_random_draws.csv',random_rows)
    save('t3_joint_random_draws.csv',joint_rows)
    summary=[]
    for split in ['prompt_disjoint','ordinary_KFold']:
        for a in ANCHORS:
            p=next(r for r in pooled_rows if r['split_type']==split and r['anchor']==a and r['ranking']=='Disagreement')
            row=dict(split_type=split,anchor=a,n=p['n'],K=p['K'],budget_k=p['k'],Disagreement_caught=p['caught'],expected_random=p['expected_random'],pooled_joint_random_p=p['pooled_joint_random_p'])
            for model in ['Ridge','RF']:
                for t in ['V','G']:
                    r=next(r for r in regression_rows if r['split_type']==split and r['fold']=='pooled' and r['model']==model and r['target']==t)
                    row[model+'_'+t+'_pooled_MAE']=r['MAE']
                    row[model+'_'+t+'_MAE_arithmetic']=r['mae_arithmetic']
            row['caught_arithmetic']=p['caught_arithmetic']; row['expected_arithmetic']=p['expected_arithmetic']; row['p_arithmetic']=p['p_expression']
            summary.append(row)
    save('t3_summary.csv',summary,True)
    assert before=={p:sha((ROOT/p).read_bytes()) for p in files}
    save('t3_training_sources.csv',[dict(path=p,sha256=h) for p,h in before.items()])
    names=['t3_fold_composition.csv','t3_regression.csv','t3_rankings.csv','t3_auroc.csv','t3_pooled.csv','t3_heldout_predictions.csv','t3_bootstrap.csv','t3_training_audit.csv','t3_random_draws.csv','t3_joint_random_draws.csv','t3_summary.csv','t3_training_sources.csv']
    save('t3_training_output_hashes.csv',[dict(path='reports/week9/'+name,sha256=sha((OUT/name).read_bytes())) for name in names],True)
    print('STATUS: Task 3 COMPLETE on documented eligible development population. All outputs exploratory; no interpretation beyond numbers. No tuning, Test files, existing model writes or manual sample changes.',flush=True)

if __name__=='__main__':
    if '--capture' in sys.argv:
        repeat('t3_evaluate.py','t3_training','Eligible-development evaluation results',
          'The diagnosis above passed before fitting. Both split designs use the identical documented eligible development population. All model factories and preprocessing come from the project; parameters are fixed and verified against the saved selected-parameter file. The table reports numbers only. Fold-level regression, labels, rankings, AUROC intervals and essay predictions are supplied in the linked CSVs. Pooled selection sums within-fold queues. Pooled expected counts sum fold expectations, pooled lift is caught divided by this expectation, and pooled p uses independent-fold joint random draws. Per-fold standalone random references reset the prescribed seed; the joint reference uses a separate master stream with that seed. Random aggregate p is NA, with actual per-fold integer-draw p values preserved. AUROC uses the exact three ranking scores; pooled AUROC uses concatenated raw scores and does not change queue selection. Identical fresh-process stdout includes hashes of every output, including all held-out predictions, confirming training-output determinism.',
          ('t3_summary.csv',))
    else:
        with threadpool_limits(limits=1):
            main()

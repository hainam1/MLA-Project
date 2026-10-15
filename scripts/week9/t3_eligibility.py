"""Exploratory extension designed after Official Test was used."""
import json
import sys
import pandas as pd
from t3_evidence import *

sys.path.insert(0,str(ROOT/'src'))
from mla_project.pipelines.training_pipeline import prepare_training_data

SOURCES=[
 'data/05_model_features/development_features_with_targets.csv',
 'data/02_split_manifest/essay_split_manifest.csv',
 'outputs/phase6/validation_predictions.csv',
 'outputs/phase6/training_summary.json',
 'outputs/phase6/artifact_manifest.json',
 'outputs/improvement_study/train_oof_predictions.csv',
 'reports/week9/t1_essay_level.csv',
 'src/mla_project/pipelines/training_pipeline.py',
 'scripts/phase8_evaluate_review_prioritization.py',
 'configs/phase6_training.yaml',
 'docs/evaluation_protocol_freeze.md',
]

def main():
    print(LABEL,flush=True)
    print('COMMAND: .venv/Scripts/python.exe -u scripts/week9/t3_eligibility.py')
    print('SEED=42; diagnosis only; no fitting or sampling')
    before={p:sha((ROOT/p).read_bytes()) for p in SOURCES}
    dev=pd.read_csv(ROOT/SOURCES[0],dtype={'essay_id':str})
    assert dev.essay_id.is_unique and set(dev.split)=={'model_train','validation'} and dev.source_partition.eq('official_train').all()
    ids=set(dev.essay_id)
    # Shared administrative manifest, metadata columns only, development-ID allowlist.
    # No Test source, feature, label or prediction file is opened.
    columns=['essay_id','source_partition','split','cv_fold','prompt_id','privacy_review_status']
    selected=[]
    for chunk in pd.read_csv(ROOT/SOURCES[1],usecols=columns,dtype={'essay_id':str},chunksize=1000):
        selected.append(chunk.loc[chunk.essay_id.isin(ids)].copy())
    manifest=pd.concat(selected,ignore_index=True)
    assert len(manifest)==len(dev) and set(manifest.essay_id)==ids
    assert manifest.source_partition.eq('official_train').all()
    prepared=prepare_training_data(dev,manifest,eligible_status='not_flagged')
    source=dev.merge(manifest[['essay_id','prompt_id','privacy_review_status']],on='essay_id',validate='one_to_one',sort=False)
    assert source.prompt_id.notna().all()
    source['normalised_prompt']=source.prompt_id.str.lower().str.split().str.join(' ')
    source['eligible']=source.privacy_review_status.eq('not_flagged')
    eligible=source.loc[source.eligible].copy().sort_values('essay_id',kind='stable').reset_index(drop=True)
    counts=[]
    for split,sub in source.groupby('split',sort=True):
        n=len(sub); kept=int(sub.eligible.sum()); excluded=n-kept
        counts.append(dict(split=split,source_essays=n,eligible_essays=kept,excluded_essays=excluded,arithmetic=f'{n}-{excluded}={kept}'))
    counts.append(dict(split='TOTAL',source_essays=len(source),eligible_essays=len(eligible),excluded_essays=len(source)-len(eligible),arithmetic=f'{len(source)}-{len(source)-len(eligible)}={len(eligible)}'))
    save('t3_eligibility_counts.csv',counts,True)
    reasons=source.groupby(['split','privacy_review_status','eligible'],sort=True).size().reset_index(name='n')
    save('t3_eligibility_reasons.csv',reasons,True)
    before_groups=set(source.normalised_prompt); after_groups=set(eligible.normalised_prompt)
    prompt_rows=[dict(normalised_prompt=p,before=int(source.normalised_prompt.eq(p).sum()),eligible=int(eligible.normalised_prompt.eq(p).sum()),lost_all=p not in after_groups) for p in sorted(before_groups)]
    save('t3_eligibility_prompts.csv',prompt_rows)
    print(f'PROMPTS before={len(before_groups)}; after={len(after_groups)}; groups_losing_all_essays={len(before_groups-after_groups)}; lost_groups={sorted(before_groups-after_groups)}')
    checks=[]
    val=set(eligible.loc[eligible.split.eq('validation'),'essay_id'])
    train=set(eligible.loc[eligible.split.eq('model_train'),'essay_id'])
    for path,column in [(SOURCES[2],'essay_id'),(SOURCES[6],'essay_id')]:
        saved=pd.read_csv(ROOT/path,usecols=[column],dtype={column:str})
        actual=set(saved[column]); same=val==actual and len(saved)==len(actual)
        checks.append(dict(check='eligible Validation ID equality',source=path,eligible_n=len(val),saved_n=len(saved),missing=len(val-actual),extra=len(actual-val),passed=same))
        assert same, f'Validation IDs differ from {path}'
    oof=pd.read_csv(ROOT/SOURCES[5],usecols=['essay_id','cv_fold'],dtype={'essay_id':str})
    assert oof.essay_id.is_unique
    same=train==set(oof.essay_id)
    checks.append(dict(check='eligible train ID equality with saved OOF',source=SOURCES[5],eligible_n=len(train),saved_n=len(oof),missing=len(train-set(oof.essay_id)),extra=len(set(oof.essay_id)-train),passed=same))
    assert same, 'OOF training IDs differ'
    folds=eligible.loc[eligible.split.eq('model_train'),['essay_id','cv_fold']].merge(oof,on='essay_id',validate='one_to_one',suffixes=('_manifest','_oof'))
    assert (folds.cv_fold_manifest==folds.cv_fold_oof).all()
    summary=json.loads((ROOT/SOURCES[3]).read_text())
    artifact=json.loads((ROOT/SOURCES[4]).read_text())
    for file in ['training_summary.json','validation_predictions.csv']:
        assert sha((ROOT/'outputs/phase6'/file).read_bytes()).upper()==artifact['sha256'][file]
    assert before[SOURCES[0]].upper()==summary['run_metadata']['development_sha256']
    assert before[SOURCES[1]].upper()==summary['run_metadata']['split_sha256']
    assert summary['eligible_privacy_status']=='not_flagged'
    assert summary['model_train_rows']==len(train)==3050 and summary['validation_rows']==len(val)==762
    for model,metadata in summary['model_metadata'].items():
        assert metadata['eligible_fit_rows']==len(train) and metadata['refit_on_all_eligible_rows']
        print(f'FROZEN_FIT_RECORD model={model}; eligible_fit_rows={metadata["eligible_fit_rows"]}; refit_on_all_eligible_rows={metadata["refit_on_all_eligible_rows"]}')
    assert set(prepared.train.essay_id)==train and set(prepared.validation.essay_id)==val
    assert len(eligible)==3812 and len(after_groups)==44
    save('t3_eligibility_checks.csv',checks,True)
    quotes=[]
    for path,lo,hi in [(SOURCES[7],72,73),(SOURCES[7],101,119),(SOURCES[7],127,129),(SOURCES[8],60,69),(SOURCES[8],85,88),(SOURCES[9],1,3),(SOURCES[10],54,64)]:
        lines=(ROOT/path).read_text(encoding='utf-8').splitlines()
        for number in range(lo,hi+1):
            quotes.append(dict(path=path,line=number,code=lines[number-1]))
            print(f'CODE {path}:{number}: {lines[number-1]}')
    save('t3_eligibility_code.csv',quotes)
    print('TRAIN_CROSSCHECK: saved training summary and development/manifest hashes identify the original fit population; all model records say refit on all eligible rows; saved train OOF IDs and cv_fold values match exactly. No separate per-model fit-ID list exists in the artifact manifest.')
    print('MANIFEST_ACCESS: shared administrative split metadata only, retained by development ID allowlist before prepare_training_data; no Official Test source, features, labels, predictions or evaluation outputs opened.')
    save('t3_eligible_development.csv',eligible)
    save('t3_development_eligibility_ids.csv',source[['essay_id','split','privacy_review_status','normalised_prompt','eligible']])
    assert before=={p:sha((ROOT/p).read_bytes()) for p in SOURCES}
    save('t3_eligibility_sources.csv',[dict(path=p,sha256=h) for p,h in before.items()],True)
    for filename in ['t3_eligible_development.csv','t3_development_eligibility_ids.csv','t3_eligibility_prompts.csv','t3_eligibility_code.csv']:
        print(f'OUTPUT_SHA256 {filename}={sha((OUT/filename).read_bytes())}')
    print('DECISION: PASS. Documented unchanged not_flagged rule yields 3050 model_train + 762 Validation = 3812 eligible essays and 44 normalised prompt groups; exact Validation and saved OOF training ID equality asserted. Task 3 training is now authorised by the supplied decision rule.')
    print('INTEGRITY: all sources unchanged; diagnosis appended before any new training results.')

if __name__=='__main__':
    if '--capture' in sys.argv:
        repeat('t3_eligibility.py','t3_eligibility','Eligibility diagnosis (before training)',
          'The earlier population stop counted the cleaned development table before the documented privacy gate. This diagnosis applies the existing `prepare_training_data(..., eligible_status="not_flagged")` function unchanged. Exact source lines and all counts are quoted in the raw transcript. The shared administrative manifest is used only to retain development-ID metadata; no Official Test feature, label, prediction or source file is opened. Training-ID evidence combines the saved frozen training-summary input hashes and refit declarations with exact saved training OOF ID/fold equality. No filter is invented or tuned. The decision gate must pass before training.',
          ('t3_eligibility_counts.csv','t3_eligibility_reasons.csv','t3_eligibility_checks.csv'))
    else:
        main()

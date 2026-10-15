"""Draft README diff only, using saved Week 9 evidence; never open Test data."""
import difflib
import subprocess
import sys
import pandas as pd
from t456_evidence import *

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print(LABEL,flush=True)
    print('COMMAND: .venv/Scripts/python.exe -u scripts/week9/t6_readme_draft.py')
    print('SEED=42; documentation only; no statistical computation or model evaluation')
    readme=ROOT/'README.md'; original_bytes=readme.read_bytes(); original=original_bytes.decode('utf-8')
    normalized=original.replace('\r\n','\n')
    inventory=pd.read_csv(OUT/'t0_inventory.csv',keep_default_na=False)
    t0=pd.read_csv(OUT/'t0_metrics.csv',float_precision='round_trip')
    t1q=pd.read_csv(OUT/'t1_quadrants.csv',float_precision='round_trip')
    t1c=pd.read_csv(OUT/'t1_categories.csv',float_precision='round_trip')
    t1corr=pd.read_csv(OUT/'t1_correlations.csv',float_precision='round_trip')
    t1auc=pd.read_csv(OUT/'t1_auroc.csv',float_precision='round_trip')
    t2=pd.read_csv(OUT/'t2_anchor.csv',float_precision='round_trip')
    t3=pd.read_csv(OUT/'t3_summary.csv',float_precision='round_trip')
    sources=['reports/week9/t0_inventory.csv','reports/week9/t0_metrics.csv','reports/week9/t1_quadrants.csv','reports/week9/t1_categories.csv','reports/week9/t1_correlations.csv','reports/week9/t1_auroc.csv','reports/week9/t2_anchor.csv','reports/week9/t3_summary.csv','reports/week9/t3_eligibility_counts.csv','reports/week9/t4_selection_check.csv','reports/week9/t4_output_hashes.csv','reports/week9/t5_fairness.csv']
    before={p:sha((ROOT/p).read_bytes()) for p in sources}
    assert t0.iloc[1].disagreement==47 and t0.iloc[1].K==208
    assert t0.iloc[0].disagreement==15 and t0.iloc[0].K==69
    prediction_paths=['outputs/phase6/validation_predictions.csv','outputs/predictions/phase7_validation_regression_predictions.csv','outputs/predictions/official_test_predictions.csv']
    tracking=[]
    for p in prediction_paths:
        # Git index metadata only. Never read or hash the Test CSV in this task.
        tracked=subprocess.check_output(['git','ls-files','--',p],cwd=ROOT).decode().strip()
        row=inventory.loc[inventory.path.eq(p)].iloc[0]
        assert not tracked, f'STOP: {p} is tracked, contradicting Task 0 provenance'
        tracking.append(dict(path=p,tracked=False,sha256_from_task0=row.sha256,task0_inventory_data_row=int(inventory.index[inventory.path.eq(p)][0])+1))
    save('t6_prediction_tracking.csv',tracking)
    commit_paths=['docs/evaluation_protocol_freeze.md','scripts/phase8_evaluate_review_prioritization.py','scripts/phase9_official_test_evaluation.py','docs/data/phase9_tables/artifact_manifest.json','docs/data/phase9_tables/large_error_labels.csv','docs/data/phase9_tables/random_reference_distribution.csv','docs/data/phase9_tables/review_strategy_comparison.csv']
    checks=[]
    for p in commit_paths:
        row=inventory.loc[inventory.path.eq(p)].iloc[0]
        first=row.first_commit.split('|'); last=row.last_commit.split('|')
        assert first[0]==last[0]=='2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d'
        checks.append(dict(path=p,first_commit=first[0],first_author_date=first[1],first_committer_date=first[2],last_commit=last[0]))
    save('t6_commit_checks.csv',checks)
    mtime_paths=['docs/data/phase8_tables/review_strategy_comparison.csv','docs/data/phase8_tables/random_reference_distribution.csv','docs/data/phase8_tables/large_error_labels.csv','docs/evaluation_protocol_freeze.md','scripts/phase9_official_test_evaluation.py','outputs/predictions/official_test_predictions.csv']
    mtimes=[]
    for p in mtime_paths:
        row=inventory.loc[inventory.path.eq(p)].iloc[0]
        mtimes.append(dict(path=p,modified_utc_from_task0=row.modified_utc,task0_inventory_data_row=int(inventory.index[inventory.path.eq(p)][0])+1))
    mtimes.sort(key=lambda r:r['modified_utc_from_task0'])
    save('t6_mtime_sequence.csv',mtimes)
    headline=[]
    def add(label,value,script,output,rows):
        headline.append(dict(headline=label,value=value,script=script,output=output,data_rows=rows))
    add('Frozen Test disagreement','47/208','scripts/week9/t0_provenance.py','reports/week9/t0_metrics.csv','2')
    add('Frozen Test random mean','41.427 (41.4 rounded to one decimal)','scripts/week9/t0_provenance.py','reports/week9/t0_metrics.csv','2')
    add('Frozen Test empirical p','165/1000 = 0.165','scripts/week9/t0_provenance.py','reports/week9/t0_metrics.csv','2')
    add('Frozen Test exact hypergeometric p',f'{t0.iloc[1].hypergeom_p:.15g} (0.188 rounded)','scripts/week9/t0_provenance.py','reports/week9/t0_metrics.csv','2')
    add('Frozen Validation disagreement','15/69','scripts/week9/t0_provenance.py','reports/week9/t0_metrics.csv','1')
    add('Validation large errors below median',f'36/69; median D={t1q.iloc[0].D_median:.17g}','scripts/week9/t1_analysis.py','reports/week9/t1_quadrants.csv','1')
    add('Validation both wrong, same direction','50/69','scripts/week9/t1_analysis.py','reports/week9/t1_categories.csv','1')
    add('Validation signed-error correlations',f'V={t1corr.iloc[2].spearman_rho:.15g}; G={t1corr.iloc[3].spearman_rho:.15g}','scripts/week9/t1_analysis.py','reports/week9/t1_correlations.csv','3-4')
    add('Validation D versus RF error magnitude',f'{t1corr.iloc[0].spearman_rho:.15g}','scripts/week9/t1_analysis.py','reports/week9/t1_correlations.csv','1')
    for i,r in t1auc.iterrows():
        add('Validation AUROC '+r.ranking,f'{r.auroc:.15g}; CI [{r.ci_low:.15g}, {r.ci_high:.15g}]','scripts/week9/t1_analysis.py','reports/week9/t1_auroc.csv',str(i+1))
    for i,r in t2.loc[t2.ranking.eq('Disagreement')].iterrows():
        add('Validation '+r.anchor+' disagreement',f'{int(r.caught)}/{int(r.K)}; p={r.exact_hypergeom_p:.15g}','scripts/week9/t2_analysis.py','reports/week9/t2_anchor.csv',str(i+1))
    for model in ['Ridge','RF']:
        for t in ['V','G']:
            add('Pooled MAE '+model+' '+t,f'prompt-disjoint={t3.iloc[0][model+"_"+t+"_pooled_MAE"]:.15g}; ordinary KFold={t3.iloc[3][model+"_"+t+"_pooled_MAE"]:.15g}','scripts/week9/t3_evaluate.py','reports/week9/t3_summary.csv','1,4')
    for i,r in t3.iterrows():
        add(r.split_type+' '+r.anchor+' pooled disagreement',f'{int(r.Disagreement_caught)}/{int(r.K)}; expected={r.expected_random:.15g}; joint p={r.pooled_joint_random_p:.15g}','scripts/week9/t3_evaluate.py','reports/week9/t3_summary.csv',str(i+1))
    save('t6_headline_provenance.csv',headline)
    section=['## Current status & result provenance','',
      'Week 9 Tasks 0–5 have produced their computational deliverables. Task 0 remains PARTIAL because first Test access and edit chronology cannot be established. Task 4 remains PARTIAL for authoritative full assignment wording: only released short prompt names are available. The fixed reading workbook is prepared and manual reading is in progress; no human judgements have been filled. Tasks 1–3 and the descriptive Task 5 table are complete. Task 6 is a documentation draft. See [Week 9 evidence](reports/week9/RESULTS_week9.md), [reading-sheet checks](reports/week9/t4_selection_check.csv), and [descriptive group captures](reports/week9/t5_fairness.csv).','',
      'The primary frozen RF-anchor result does not demonstrate that disagreement is better than random. The original ranking/draw implementation is `scripts/phase9_official_test_evaluation.py` with `src/mla_project/evaluation/phase8.py`; Task 0 reproduces its saved-prediction results without retraining.','',
      '### Freeze and chronology limitations','',
      'The [protocol](docs/evaluation_protocol_freeze.md) states that it was frozen on **2026-10-01**, after the primary Validation evaluation and before Test access. Its statement and filesystem mtimes are weak evidence, not proof of execution order. Task 0 recorded this UTC mtime sequence:','',
      '| Artifact | Filesystem mtime UTC, recorded by Task 0 |','|---|---|']
    section += [f'| `{r["path"]}` | `{r["modified_utc_from_task0"]}` |' for r in mtimes]
    section += ['',
      'The Validation result tables precede the protocol mtime; the Test script and saved Test predictions follow it. Filesystem clocks, copying and later edits can change mtimes. The first Test evaluation date cannot be established from these timestamps. Source: [Task 0 inventory](reports/week9/t0_inventory.csv) and [provenance limitations](reports/week9/t0_provenance.md).','',
      'The frozen evaluation code, protocol and **tracked Test result tables** first appear together in commit `2c7982e` (`2026-10-03T19:24:28+07:00`, both author and committer date). Git therefore cannot establish their order before that snapshot. The saved prediction CSVs listed below never entered Git; they are excluded from this statement about tracked artifacts. Source: [commit checks from the Task 0 inventory](reports/week9/t6_commit_checks.csv).','',
      '### Retrospective and exploratory analyses','',
      'Week 8 additions prepared after Test access—rater agreement, max-versus-mean disagreement sensitivity, prompt-length descriptions and the fairness table—are exploratory. See `scripts/post_midterm_teacher_analysis.py`, `docs/data/post_midterm/` and [teacher-feedback results](docs/post_midterm/teacher_feedback_results.md). All Week 9 tasks were designed after Test was used and are retrospective/exploratory work; Task 0 is a provenance reproduction rather than new confirmatory evidence. Task 3 is explicitly labelled **“Exploratory extension designed after Official Test was used.”** Exact access chronology remains unresolved.','',
      'All declared anchor results are retained. A2 derives its error label from Ridge; Ridge Extremity therefore shares the label-generating model. Under A1, RF is both the anchor and part of disagreement. These dependencies and the exploratory design must accompany the results. No anchor, threshold, model setting or ranking was selected on a new Test evaluation.','',
      '### Eligible population','',
      'The existing rule is `privacy_review_status == "not_flagged"` (`configs/phase6_training.yaml`, lines 1–3; `src/mla_project/pipelines/training_pipeline.py`, lines 72–73 and 127). It excludes both `flagged_by_rater` and `unresolved_raw_id_link`. Development has `3,911 − 99 = 3,812` eligible essays: `3,128 − 78 = 3,050` model-train and `783 − 21 = 762` Validation. All 44 normalized prompt groups remain. Eligible Validation IDs equal the saved prediction IDs exactly; train IDs and fold assignments match the saved OOF table. [Eligibility evidence](reports/week9/t3_eligibility_counts.csv), [exclusion reasons](reports/week9/t3_eligibility_reasons.csv), [ID checks](reports/week9/t3_eligibility_checks.csv).','',
      'The frozen eligible Test population is **2,518**, as reproduced in [Task 0 metrics, Test row](reports/week9/t0_metrics.csv). No new Test evaluation was used for the later Week 9 analyses.','',
      '### Headline numbers and their producers','',
      'Values below are displayed to at most 15 significant digits unless a rounding is explicitly labelled; full precision, explicit derived-metric arithmetic and raw terminal evidence are in the linked outputs and [Week 9 results](reports/week9/RESULTS_week9.md). CSV row numbers count data rows, excluding headers.','',
      '| Headline | Value | Producing script | Output and data row(s) |','|---|---|---|---|']
    section += [f'| {r["headline"]} | {r["value"]} | `{r["script"]}` | `{r["output"]}`, row(s) {r["data_rows"]} |' for r in headline]
    section += ['',
      '### Local artifacts and replication limits','',
      'The following prediction CSVs inventoried in Task 0 are **not tracked in Git**. Hashes are copied from that saved inventory, including the Test hash; Task 6 does not reopen Test predictions.','',
      '| Local prediction CSV | SHA-256 recorded in Task 0 |','|---|---|']
    section += [f'| `{r["path"]}` | `{r["sha256_from_task0"]}` |' for r in tracking]
    section += ['',
      'Source: [Task 0 artifact inventory](reports/week9/t0_inventory.csv) and [current Git-index checks](reports/week9/t6_prediction_tracking.csv). The repository alone does not reproduce the Test numbers: the approved private data and saved prediction artifacts must also be supplied and checked against their hashes. An identical rerun of local artifacts checks reproducibility within this environment; a public repository is **not an independent replication**. Independent replication requires a separate execution and audit of the data, split, code and provenance.','',
      'The student-text reading workbook and its private intermediates/previews are excluded by `.gitignore`. The original manual sample remains unchanged.','']
    text='\n'.join(section)
    anchor='## Data and reproducibility\n'
    assert normalized.count(anchor)==1 and '## Current status & result provenance' not in normalized
    proposed=normalized.replace(anchor,text+'\n'+anchor,1)
    (OUT/'t6_README_section.md').write_text(text,encoding='utf-8')
    (OUT/'t6_README_proposed.md').write_text(proposed,encoding='utf-8')
    diff=''.join(difflib.unified_diff(normalized.splitlines(keepends=True),proposed.splitlines(keepends=True),fromfile='a/README.md',tofile='b/README.md'))
    (OUT/'t6_README.diff').write_text(diff,encoding='utf-8')
    ignorediff=subprocess.run(['git','diff','--','.gitignore'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    (OUT/'t6_gitignore.diff').write_bytes(ignorediff.stdout)
    assert readme.read_bytes()==original_bytes
    assert before=={p:sha((ROOT/p).read_bytes()) for p in sources}
    save('t6_sources.csv',[dict(path=p,sha256=h) for p,h in before.items()]+[dict(path='README.md unchanged working-copy base',sha256=sha(original_bytes))],False)
    save('t6_output_hashes.csv',[dict(path='reports/week9/'+p,sha256=sha((OUT/p).read_bytes())) for p in ['t6_README.diff','t6_gitignore.diff','t6_README_proposed.md','t6_README_section.md','t6_headline_provenance.csv','t6_prediction_tracking.csv','t6_commit_checks.csv','t6_mtime_sequence.csv','t6_sources.csv']])
    print('CHECK README.md preserved byte-for-byte; proposed text and full diff only; no Git config change, staging, commit or push; no Official Test file opened')
    print('STATUS: documentation draft complete with explicit Task 0 chronology and Task 4 full-prompt limitations. Existing README is unchanged; .gitignore change is applied as expressly requested.')
    print('FULL_GITIGNORE_DIFF')
    print(ignorediff.stdout.decode('utf-8'),end='')
    print('FULL_README_PROPOSED_DIFF')
    print(diff,end='')

if __name__=='__main__':
    if '--capture' in sys.argv:
        capture('t6','t6_readme_draft.py','README diff only: README.md is not modified. The full proposed section is saved as t6_README_section.md; the complete working-copy-based proposal is t6_README_proposed.md; the applicable patch is t6_README.diff. The expressly authorized .gitignore edit is already applied and its full diff is t6_gitignore.diff. The draft distinguishes tracked Test result tables, which entered the recorded snapshot together, from untracked prediction CSVs. It preserves the actual PARTIAL limitations rather than declaring chronology or missing authoritative prompt wording complete. All Test numbers, dates and hashes are read solely from saved Task 0 evidence. The original Task sections are retained. Full diffs follow in the raw transcript; no commit, push or Git configuration change is performed. An initial terminal-encoding failure while printing the already-generated diff is preserved verbatim in logs/t6_attempt1.log; UTF-8 output resolves it without changing the draft.')
    else: main()

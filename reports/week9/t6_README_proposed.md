# Prioritizing Teacher Review of English Learner Writing

An academic decision-support project for English writing teachers using ELLIPSE. Four independently trained single-target models (Ridge and Random Forest for Vocabulary and Grammar) use the same 14 linguistic features.

```text
Essay -> linguistic features -> score predictions -> model disagreement -> review priority ranking
Teacher -> Review -> Interpret -> Decide
```

All core ML phases are complete. Models, splits and Official Test results are frozen. See [Project Freeze Status](docs/project_freeze_status.md), [final report](report/final_report.md), and [finalization evidence](docs/finalization_evidence.md).

RF Official Test MAE is 0.364197 for Vocabulary and 0.433587 for Grammar. At Top-20%, disagreement captured 47/208 large RF errors (22.596%). It had the highest observed capture among tested strategies, but empirical one-sided p=.165 does not establish statistical superiority over random. Disagreement is a ranking signal, not calibrated confidence or error probability.

Top-20% means **review first**. The remaining essays also require teacher grading; the teacher retains all official grading authority. ELLIPSE results do not establish validity for HANU; local validation and domain adaptation would be required.

## Current status & result provenance

Week 9 Tasks 0–5 have produced their computational deliverables. Task 0 remains PARTIAL because first Test access and edit chronology cannot be established. Task 4 remains PARTIAL for authoritative full assignment wording: only released short prompt names are available. The fixed reading workbook is prepared and manual reading is in progress; no human judgements have been filled. Tasks 1–3 and the descriptive Task 5 table are complete. Task 6 is a documentation draft. See [Week 9 evidence](reports/week9/RESULTS_week9.md), [reading-sheet checks](reports/week9/t4_selection_check.csv), and [descriptive group captures](reports/week9/t5_fairness.csv).

The primary frozen RF-anchor result does not demonstrate that disagreement is better than random. The original ranking/draw implementation is `scripts/phase9_official_test_evaluation.py` with `src/mla_project/evaluation/phase8.py`; Task 0 reproduces its saved-prediction results without retraining.

### Freeze and chronology limitations

The [protocol](docs/evaluation_protocol_freeze.md) states that it was frozen on **2026-10-01**, after the primary Validation evaluation and before Test access. Its statement and filesystem mtimes are weak evidence, not proof of execution order. Task 0 recorded this UTC mtime sequence:

| Artifact | Filesystem mtime UTC, recorded by Task 0 |
|---|---|
| `docs/data/phase8_tables/review_strategy_comparison.csv` | `2026-10-01T16:22:52.212306+00:00` |
| `docs/data/phase8_tables/random_reference_distribution.csv` | `2026-10-01T16:22:52.257898+00:00` |
| `docs/data/phase8_tables/large_error_labels.csv` | `2026-10-01T16:22:52.272121+00:00` |
| `docs/evaluation_protocol_freeze.md` | `2026-10-01T16:27:59.175393+00:00` |
| `scripts/phase9_official_test_evaluation.py` | `2026-10-01T16:44:55.498529+00:00` |
| `outputs/predictions/official_test_predictions.csv` | `2026-10-01T16:45:24.436881+00:00` |

The Validation result tables precede the protocol mtime; the Test script and saved Test predictions follow it. Filesystem clocks, copying and later edits can change mtimes. The first Test evaluation date cannot be established from these timestamps. Source: [Task 0 inventory](reports/week9/t0_inventory.csv) and [provenance limitations](reports/week9/t0_provenance.md).

The frozen evaluation code, protocol and **tracked Test result tables** first appear together in commit `2c7982e` (`2026-10-03T19:24:28+07:00`, both author and committer date). Git therefore cannot establish their order before that snapshot. The saved prediction CSVs listed below never entered Git; they are excluded from this statement about tracked artifacts. Source: [commit checks from the Task 0 inventory](reports/week9/t6_commit_checks.csv).

### Retrospective and exploratory analyses

Week 8 additions prepared after Test access—rater agreement, max-versus-mean disagreement sensitivity, prompt-length descriptions and the fairness table—are exploratory. See `scripts/post_midterm_teacher_analysis.py`, `docs/data/post_midterm/` and [teacher-feedback results](docs/post_midterm/teacher_feedback_results.md). All Week 9 tasks were designed after Test was used and are retrospective/exploratory work; Task 0 is a provenance reproduction rather than new confirmatory evidence. Task 3 is explicitly labelled **“Exploratory extension designed after Official Test was used.”** Exact access chronology remains unresolved.

All declared anchor results are retained. A2 derives its error label from Ridge; Ridge Extremity therefore shares the label-generating model. Under A1, RF is both the anchor and part of disagreement. These dependencies and the exploratory design must accompany the results. No anchor, threshold, model setting or ranking was selected on a new Test evaluation.

### Eligible population

The existing rule is `privacy_review_status == "not_flagged"` (`configs/phase6_training.yaml`, lines 1–3; `src/mla_project/pipelines/training_pipeline.py`, lines 72–73 and 127). It excludes both `flagged_by_rater` and `unresolved_raw_id_link`. Development has `3,911 − 99 = 3,812` eligible essays: `3,128 − 78 = 3,050` model-train and `783 − 21 = 762` Validation. All 44 normalized prompt groups remain. Eligible Validation IDs equal the saved prediction IDs exactly; train IDs and fold assignments match the saved OOF table. [Eligibility evidence](reports/week9/t3_eligibility_counts.csv), [exclusion reasons](reports/week9/t3_eligibility_reasons.csv), [ID checks](reports/week9/t3_eligibility_checks.csv).

The frozen eligible Test population is **2,518**, as reproduced in [Task 0 metrics, Test row](reports/week9/t0_metrics.csv). No new Test evaluation was used for the later Week 9 analyses.

### Headline numbers and their producers

Values below are displayed to at most 15 significant digits unless a rounding is explicitly labelled; full precision, explicit derived-metric arithmetic and raw terminal evidence are in the linked outputs and [Week 9 results](reports/week9/RESULTS_week9.md). CSV row numbers count data rows, excluding headers.

| Headline | Value | Producing script | Output and data row(s) |
|---|---|---|---|
| Frozen Test disagreement | 47/208 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
| Frozen Test random mean | 41.427 (41.4 rounded to one decimal) | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
| Frozen Test empirical p | 165/1000 = 0.165 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
| Frozen Test exact hypergeometric p | 0.188324671369221 (0.188 rounded) | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
| Frozen Validation disagreement | 15/69 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 1 |
| Validation large errors below median | 36/69; median D=0.13398965515499994 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_quadrants.csv`, row(s) 1 |
| Validation both wrong, same direction | 50/69 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_categories.csv`, row(s) 1 |
| Validation signed-error correlations | V=0.956277117218718; G=0.951854189994445 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_correlations.csv`, row(s) 3-4 |
| Validation D versus RF error magnitude | -0.00478127282758114 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_correlations.csv`, row(s) 1 |
| Validation AUROC Disagreement | 0.510676119371772; CI [0.432336289152627, 0.585208476579814] | `scripts/week9/t1_analysis.py` | `reports/week9/t1_auroc.csv`, row(s) 1 |
| Validation AUROC Ridge Extremity | 0.516364472886212; CI [0.445977573758215, 0.578892042777683] | `scripts/week9/t1_analysis.py` | `reports/week9/t1_auroc.csv`, row(s) 2 |
| Validation AUROC Shortest-first | 0.511334880900098; CI [0.437914589985434, 0.582646097231079] | `scripts/week9/t1_analysis.py` | `reports/week9/t1_auroc.csv`, row(s) 3 |
| Validation A1_RF disagreement | 15/69; p=0.409805547270715 | `scripts/week9/t2_analysis.py` | `reports/week9/t2_anchor.csv`, row(s) 2 |
| Validation A2_Ridge disagreement | 19/77; p=0.179714082645364 | `scripts/week9/t2_analysis.py` | `reports/week9/t2_anchor.csv`, row(s) 6 |
| Validation A3_Both_wrong disagreement | 9/51; p=0.728938261414719 | `scripts/week9/t2_analysis.py` | `reports/week9/t2_anchor.csv`, row(s) 10 |
| Pooled MAE Ridge V | prompt-disjoint=0.37342443714543; ordinary KFold=0.372304940106959 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
| Pooled MAE Ridge G | prompt-disjoint=0.463036537712484; ordinary KFold=0.461471100957794 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
| Pooled MAE RF V | prompt-disjoint=0.372165069040496; ordinary KFold=0.371663177019517 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
| Pooled MAE RF G | prompt-disjoint=0.455403719595917; ordinary KFold=0.454390747998969 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
| prompt_disjoint A1_RF pooled disagreement | 88/386; expected=77.362908429581; joint p=0.105 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1 |
| prompt_disjoint A2_Ridge pooled disagreement | 93/384; expected=76.9621199683931; joint p=0.022 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 2 |
| prompt_disjoint A3_Both_wrong pooled disagreement | 44/276; expected=55.3218568770231; joint p=0.97 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 3 |
| ordinary_KFold A1_RF pooled disagreement | 86/376; expected=75.4544844738444; joint p=0.087 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 4 |
| ordinary_KFold A2_Ridge pooled disagreement | 93/383; expected=76.8607857504051; joint p=0.013 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 5 |
| ordinary_KFold A3_Both_wrong pooled disagreement | 40/271; expected=54.384438757082; joint p=0.993 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 6 |

### Local artifacts and replication limits

The following prediction CSVs inventoried in Task 0 are **not tracked in Git**. Hashes are copied from that saved inventory, including the Test hash; Task 6 does not reopen Test predictions.

| Local prediction CSV | SHA-256 recorded in Task 0 |
|---|---|
| `outputs/phase6/validation_predictions.csv` | `6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab` |
| `outputs/predictions/phase7_validation_regression_predictions.csv` | `da86cf4be3b05790db65ceb6381d75ad77fce695694e8c62a9a03dcf7493c1d0` |
| `outputs/predictions/official_test_predictions.csv` | `48eb85d8bda27dd6261179d839fd5377d694741c5740f94ac88029b0593393e8` |

Source: [Task 0 artifact inventory](reports/week9/t0_inventory.csv) and [current Git-index checks](reports/week9/t6_prediction_tracking.csv). The repository alone does not reproduce the Test numbers: the approved private data and saved prediction artifacts must also be supplied and checked against their hashes. An identical rerun of local artifacts checks reproducibility within this environment; a public repository is **not an independent replication**. Independent replication requires a separate execution and audit of the data, split, code and provenance.

The student-text reading workbook and its private intermediates/previews are excluded by `.gitignore`. The original manual sample remains unchanged.

## Data and reproducibility

ELLIPSE (Crossley et al., 2023) is used under CC BY-NC-SA 4.0. Original local files stay read-only under `data/01_original_source/`; follow [data placement](data/README.md) and [source provenance](data/01_original_source/documentation/SOURCE.md). Private data and model artifacts are ignored by Git and must be supplied from the existing approved local snapshot on another machine.

The 3911-row development source is split into 3128 model_train and 783 Validation; the separate Official Test has 2571 rows. Privacy filtering leaves 3050/762/2518. Splitting is prompt-stratified across the prompt categories available in the dataset. Evaluation measures new essays under represented categories; unseen-prompt generalization is not established. The operational prompt-count discrepancy is documented in [finalization evidence](docs/finalization_evidence.md).

## Setup

Tested environment: Python **3.14.5**, scikit-learn **1.9.1**, spaCy **3.8.16**, en_core_web_sm **3.8.0**, LanguageTool Python **2.9.5**, LanguageTool **6.6**, Java **21.0.10**. The declared Python range is >=3.12,<3.15; this does not mean every version was tested. Use the frozen artifact environment and `uv.lock` for reproducibility, especially sklearn/joblib compatibility.

```powershell
uv sync --locked --python 3.14.5 --extra dev --extra analysis
.venv\Scripts\python.exe -m pytest
```

Java/JVM must be on PATH for LanguageTool (6.6 requires Java >=17; Java 21 was tested). spaCy requires en_core_web_sm; the locked dependency installs version 3.8.0. If missing in an alternative setup:

```powershell
.venv\Scripts\python.exe -m spacy download en_core_web_sm
```

Verify that model version matches 3.8.0. LanguageTool may download its 6.6 distribution on first use, requiring network access and a writable cache. Setup does not download ELLIPSE or the trained models. See [setup details](docs/setup.md).

## Single-essay prediction

Run from the repository root after setup and restoring the frozen artifacts:

```python
import json
from pathlib import Path
import joblib
from mla_project.features.build_features import load_default_extractor
from mla_project.pipelines.inference_pipeline import predict_essay, prioritize_essay_batch

names = ['ridge_vocabulary', 'ridge_grammar',
         'random_forest_vocabulary', 'random_forest_grammar']
models = {name: joblib.load(Path('outputs/phase6') / f'{name}.joblib')
          for name in names}
columns = json.loads(Path('outputs/phase6/feature_schema.json').read_text())
extractor = load_default_extractor()
try:
    result = predict_essay('A learner essay goes here.', extractor=extractor,
                          models=models, feature_columns=columns)
    print(result['scores'], result['review_priority_score'])
finally:
    extractor.grammar_checker.close()
```

Output includes Ridge, RF and auxiliary mean consensus per target, both disagreements and their maximum. The optional legacy `priority_for_teacher_review` field defaults to `None`. Explicit `review_threshold` retains reference-only behavior and does not implement a Top-20% policy. Consensus is not the confirmatory reference model.

## Batch review prioritization

Using the same loaded models and columns:

```python
extractor = load_default_extractor()
try:
    ranked = prioritize_essay_batch(
        {'essay-001': 'First learner essay.', 'essay-002': 'Second learner essay.'},
        extractor=extractor, models=models, feature_columns=columns,
        review_budget=0.20,
    )
    for row in ranked:
        print(row['rank'], row['essay_id'], row['review_priority_score'], row['review_first'])
finally:
    extractor.grammar_checker.close()
```

Input is a mapping of unique string IDs to essay text. Ranking is descending disagreement with ascending string ID ties. Exactly `ceil(N * budget)` essays are review-first; budget zero selects none and empty batches return `[]`. For 2 essays at .20, one is review-first. Scores remain continuous; no universal disagreement threshold applies.

## Evidence and scope

[Methodology](docs/methodology.md), [frozen evaluation protocol](docs/evaluation_protocol_freeze.md), [feature specification](docs/feature_specification.md), and [responsible use](docs/responsible_use.md) describe the study. [Changelog](docs/finalization_changelog.md) records finalization. Historical planning documents preserve earlier hypotheses; they do not define active scope. Train-only feature/model experiments remain exploratory and did not replace the frozen 14-feature models.

No retraining or tuning is needed for this freeze. Remaining work is weekly reporting, report writing, slides and oral defense. Saved-artifact supplementary analysis can be reproduced with `.venv\Scripts\python.exe scripts/finalization_supplement.py`.

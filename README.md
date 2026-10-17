# Prioritizing Teacher Review of English Learner Writing

An academic decision-support project for English writing teachers using ELLIPSE. Four independently trained single-target models (Ridge and Random Forest for Vocabulary and Grammar) use the same 14 linguistic features.

```text
Essay -> linguistic features -> score predictions -> model disagreement -> review priority ranking
Teacher -> Review -> Interpret -> Decide
```

All core ML phases are complete. Models, splits and Official Test results are frozen. See [Project Freeze Status](docs/project_freeze_status.md), [final report](report/final_report.md), and [finalization evidence](docs/finalization_evidence.md).

RF Official Test MAE is 0.364197 for Vocabulary and 0.433587 for Grammar. At Top-20%, disagreement captured 47/208 large RF errors (22.596%). Disagreement did not demonstrate better-than-random performance (empirical one-sided p=0.165; exact hypergeometric p=0.188). Disagreement is a ranking signal, not calibrated confidence or error probability.

Top-20% means **review first**. The remaining essays also require teacher grading; the teacher retains all official grading authority. ELLIPSE results do not establish validity for HANU; local validation and domain adaptation would be required.

## Current status & result provenance

Week 9 computational analyses are available. Task 0 remains PARTIAL because first Test access and edit chronology cannot be established. Tasks 1-3 and the descriptive Task 5 table are complete. Authoritative full assignment wording remains unavailable, so off-topic reading judgements remain unclear. No new commit has been made.

Reading notes for the fixed 32-essay sample were organised with support tools (an AI coding agent) following a two-pass protocol (pass 1 blind: prompt name and essay text only; pass 2: scores, predictions, errors and D revealed) and a 7-criterion rubric agreed before reading. The team re-read the essays and adopted these notes as its reading results; t4_reading_summary.csv is the text-free export. Support tools were also used to write analysis scripts and compute summary tables.

The 32-essay reading is complete. The [text-free reading summary](reports/week9/t4_reading_summary.csv) exports the adopted reading notes; the full reading sheet stays private and gitignored. See [reading-sheet checks](reports/week9/t4_selection_check.csv) and [descriptive group captures](reports/week9/t5_fairness.csv).

**Week 9 evidence log:** [RESULTS_week9.md](reports/week9/RESULTS_week9.md).

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

The frozen evaluation code, protocol and **tracked Test result tables** first appear together in commit `2c7982e` (`2026-10-03T19:24:28+07:00`, both author and committer date). Git therefore cannot establish their order before that snapshot. The three saved prediction CSVs listed below are included separately in this Week 9 report commit. Source: [commit checks from the Task 0 inventory](reports/week9/t6_commit_checks.csv).

`scripts/phase6_train_models.py` has the same bytes in commit `2c7982e` and the working tree, but its hash differs from the fit-time record, which reports a dirty worktree at training. The four frozen model files and Validation predictions still match their recorded hashes, so the existing saved frozen predictions are unaffected. The fit-time launcher changes and their effect on retraining remain UNKNOWN. Sources: `outputs/phase6/training_summary.json`, `outputs/phase6/artifact_manifest.json`, and protocol lines 13-16.

### Retrospective and exploratory analyses

Week 8 additions prepared after Test access—rater agreement, max-versus-mean disagreement sensitivity, prompt-length descriptions and the fairness table—are exploratory. See `scripts/post_midterm_teacher_analysis.py`, `docs/data/post_midterm/` and [teacher-feedback results](docs/post_midterm/teacher_feedback_results.md). All Week 9 tasks were designed after Test was used and are retrospective/exploratory work; Task 0 is a provenance reproduction rather than new confirmatory evidence. Task 3 is explicitly labelled **“Exploratory extension designed after Official Test was used.”** Exact access chronology remains unresolved.

All declared anchor results are retained. A2 derives its error label from Ridge; Ridge Extremity therefore shares the label-generating model. Under A1, RF is both the anchor and part of disagreement. These dependencies and the exploratory design must accompany the results. No anchor, threshold, model setting or ranking was selected on a new Test evaluation.

### Eligible population

The existing rule is `privacy_review_status == "not_flagged"` (`configs/phase6_training.yaml`, lines 1–3; `src/mla_project/pipelines/training_pipeline.py`, lines 72–73 and 127). It excludes both `flagged_by_rater` and `unresolved_raw_id_link`. Development has `3,911 − 99 = 3,812` eligible essays: `3,128 − 78 = 3,050` model-train and `783 − 21 = 762` Validation. All 44 normalized prompt groups remain. Eligible Validation IDs equal the saved prediction IDs exactly; train IDs and fold assignments match the saved OOF table. [Eligibility evidence](reports/week9/t3_eligibility_counts.csv), [exclusion reasons](reports/week9/t3_eligibility_reasons.csv), [ID checks](reports/week9/t3_eligibility_checks.csv).

The frozen eligible Test population is **2,518**, as reproduced in [Task 0 metrics, Test row](reports/week9/t0_metrics.csv). No new Test evaluation was used for the later Week 9 analyses.

### Headline numbers and their producers

Continuous values below use four decimal places and p-values use three significant digits; full precision, explicit derived-metric arithmetic and raw terminal evidence are in the linked outputs and [Week 9 results](reports/week9/RESULTS_week9.md). CSV row numbers count data rows, excluding headers.

| Headline | Value | Producing script | Output and data row(s) |
|---|---|---|---|
| Frozen Test disagreement | 47/208 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
| Frozen Test random mean | 41.4270 (41.4000 rounded to one decimal) | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
| Frozen Test empirical p | 165/1000 = 0.165 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
| Frozen Test exact hypergeometric p | 0.188 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
| Frozen Validation disagreement | 15/69 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 1 |
| Validation large errors below median | 36/69; median D=0.1340 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_quadrants.csv`, row(s) 1 |
| Validation both wrong, same direction | 50/69 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_categories.csv`, row(s) 1 |
| Validation signed-error correlations | V=0.9563; G=0.9519 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_correlations.csv`, row(s) 3-4 |
| Validation D versus RF error magnitude | -0.0048 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_correlations.csv`, row(s) 1 |
| Validation AUROC Disagreement | 0.5107; CI [0.4323, 0.5852] | `scripts/week9/t1_analysis.py` | `reports/week9/t1_auroc.csv`, row(s) 1 |
| Validation AUROC Ridge Extremity | 0.5164; CI [0.4460, 0.5789] | `scripts/week9/t1_analysis.py` | `reports/week9/t1_auroc.csv`, row(s) 2 |
| Validation AUROC Shortest-first | 0.5113; CI [0.4379, 0.5826] | `scripts/week9/t1_analysis.py` | `reports/week9/t1_auroc.csv`, row(s) 3 |
| Validation A1_RF disagreement | 15/69; p=0.410 | `scripts/week9/t2_analysis.py` | `reports/week9/t2_anchor.csv`, row(s) 2 |
| Validation A2_Ridge disagreement | 19/77; p=0.180 | `scripts/week9/t2_analysis.py` | `reports/week9/t2_anchor.csv`, row(s) 6 |
| Validation A3_Both_wrong disagreement | 9/51; p=0.729 | `scripts/week9/t2_analysis.py` | `reports/week9/t2_anchor.csv`, row(s) 10 |
| Pooled MAE Ridge V | prompt-disjoint=0.3734; ordinary KFold=0.3723 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
| Pooled MAE Ridge G | prompt-disjoint=0.4630; ordinary KFold=0.4615 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
| Pooled MAE RF V | prompt-disjoint=0.3722; ordinary KFold=0.3717 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
| Pooled MAE RF G | prompt-disjoint=0.4554; ordinary KFold=0.4544 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
| prompt_disjoint A1_RF pooled disagreement | 88/386; expected=77.3629; joint p=0.105 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1 |
| prompt_disjoint A2_Ridge pooled disagreement | 93/384; expected=76.9621; joint p=0.0220 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 2 |
| prompt_disjoint A3_Both_wrong pooled disagreement | 44/276; expected=55.3219; joint p=0.970 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 3 |
| ordinary_KFold A1_RF pooled disagreement | 86/376; expected=75.4545; joint p=0.0870 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 4 |
| ordinary_KFold A2_Ridge pooled disagreement | 93/383; expected=76.8608; joint p=0.0130 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 5 |
| ordinary_KFold A3_Both_wrong pooled disagreement | 40/271; expected=54.3844; joint p=0.993 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 6 |

**Multiple comparisons and decomposition.** The Week 9 analyses compare multiple split types, anchors, rankings and folds. Reported p-values are unadjusted exploratory results; isolated small p-values do not establish a confirmed improvement. All declared comparisons remain reported. For Disagreement, separate shared errors (A3) from A1-only and A2-only errors:

- prompt_disjoint: A3 44/276 = 0.1594; A1-only (88-44)/(386-276) = 44/110 = 0.4000; A2-only (93-44)/(384-276) = 49/108 = 0.4537.

- ordinary_KFold: A3 40/271 = 0.1476; A1-only (86-40)/(376-271) = 46/105 = 0.4381; A2-only (93-40)/(383-271) = 53/112 = 0.4732.

- Validation: A3 9/51 = 0.1765; A1-only (15-9)/(69-51) = 6/18 = 0.3333; A2-only (19-9)/(77-51) = 10/26 = 0.3846.

These are descriptive decompositions, not new rankings or independent replications. Random expectations for the parts use the actual per-fold budget fractions: prompt_disjoint folds 1-5 use 154/769, 154/768, 153/761, 149/745, 154/769; ordinary_KFold uses 153/763, 153/763, 153/762, 153/762, 153/762; Validation uses 153/762. Thus 0.2 * K_part is an approximation; the exact expectation is the sum of (k_fold/n_fold) * K_part,fold. Sources: `reports/week9/t3_pooled.csv` Disagreement data rows 2, 6, 10, 14, 18, 22; `reports/week9/t3_rankings.csv`; `reports/week9/t2_anchor.csv` data rows 2, 6, 10.

### Local artifacts and replication limits

The three prediction CSVs below are tracked in Git from this Week 9 report commit onward. Their Task 0 SHA256 values are retained below. Inclusion in this proposed commit does not establish an earlier creation or evaluation chronology.

| Local prediction CSV | SHA-256 recorded in Task 0 |
|---|---|
| `outputs/phase6/validation_predictions.csv` | `6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab` |
| `outputs/predictions/phase7_validation_regression_predictions.csv` | `da86cf4be3b05790db65ceb6381d75ad77fce695694e8c62a9a03dcf7493c1d0` |
| `outputs/predictions/official_test_predictions.csv` | `48eb85d8bda27dd6261179d839fd5377d694741c5740f94ac88029b0593393e8` |

From a fresh clone, install `python -m pip install -r scripts/week9/requirements.txt`, then run `python scripts/week9/t0_provenance.py` (or `--capture` for two fresh-process runs). The read-only command verifies all three prediction hashes and recomputes the frozen primary Validation/Test disagreement catches, random means and exact hypergeometric p values against `reports/week9/RESULTS_week9.md`. It creates no report files.

The prediction CSVs alone do not contain the Test human targets: reproduction also reads the already tracked Phase 8/9 label tables for `Vocabulary` and `Grammar`, recalculating error flags. `scripts/finalization_supplement.py` was only inventoried, never imported or called, and is not required. Original ELLIPSE data, feature tables, dataset inventory and shortest-first reproduction remain external. The legacy code is retained under `--external-data`; unavailable external steps print `SKIPPED: requires external ELLIPSE data (not distributed)`.

The public repo is not an independent replication. Independent replication requires a separate execution and audit of the data, split, code and provenance; first Test execution chronology remains unresolved.

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

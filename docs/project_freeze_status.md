# Project Freeze Status

Date: 2026-10-03. **PROJECT FREEZE READY**.

## 1. Final Research Question

At a fixed primary review budget of 20%, does Ridge/RF disagreement capture more large errors of the frozen RF reference predictor than same-size comparison queues? The system supports English writing teachers; all official grades remain human decisions.

## 2. Final System Architecture

Essay -> shared 14 linguistic features -> four independently trained single-target regressors (Ridge/RF x Vocabulary/Grammar) -> per-target absolute disagreement -> maximum disagreement -> batch ranking -> ceil(N * budget) review-first essays. Ties use ascending string essay ID. Empty batches return []; budget zero selects none. Single prediction has no default threshold decision; explicitly requested legacy threshold flags are reference-only. Mean consensus is auxiliary, without confirmatory promotion.

## 3. Frozen Dataset/Splits

ELLIPSE: 3911 development = 3128 model_train + 783 Validation; separate Official Test 2571. Privacy-eligible counts: 3050/762/2518. Split manifest and features are unchanged. Splitting is prompt-stratified across the prompt categories available in the dataset. All operational categories overlap across all splits. This evaluates new essays under represented categories, not unseen prompts. The 29-vs-44 discrepancy is explicitly unresolved because no authoritative canonical mapping exists locally; [evidence and crosstabs](finalization_evidence.md) preserve the exact observations.

No test target labels or test evaluation metrics were used for model selection or hyperparameter tuning. Deterministic test-text feature extraction occurred before final evaluation. No stable writer ID establishes unseen-writer independence.

## 4. Frozen Models

The four `outputs/phase6/*.joblib` models, schema and hashes in [evaluation freeze](evaluation_protocol_freeze.md) remain unchanged. No retraining, retuning, model-family extension, or official prediction regeneration occurred. Train-only improvement experiments remain supplementary historical experiments and were not deployed into this protocol.

## 5. Main Regression Results

| Official Test RF target | N | MAE |
|---|---:|---:|
| Vocabulary | 2518 | 0.364197 |
| Grammar | 2518 | 0.433587 |

RF won the lower-Validation-MAE selection rule for both targets. [Frozen regression table](data/phase9_tables/regression_metrics.csv) retains all models and metrics.

## 6. Main Triage Results

Large error of the frozen RF reference predictor: `max(abs(true_Vocabulary - RF_Vocabulary), abs(true_Grammar - RF_Grammar)) >= 1.0`. Evaluation concerns those RF errors.

| Primary Official Test metric | Frozen value |
|---|---:|
| Eligible essays | 2518 |
| RF large errors | 208 |
| Top-20% selected | 504 |
| Disagreement captured | 47 |
| Capture Rate | 22.596% |
| Precision | 9.325% |
| Lift | 1.128911 (1.129 rounded) |
| Random mean capture | 19.917% |
| Empirical one-sided p | .165 |
| Low-disagreement RF large errors | 97 |

The 97 shared blind spots use the frozen Validation-median analysis threshold 0.133989655155, not a production threshold. All Phase 8/9 official result tables and predictions are preserved.

## 7. Statistical Interpretation

Disagreement produced the highest observed capture rate among the tested strategies, but the evidence was insufficient to establish statistical superiority over random selection. The empirical one-sided p=.165 is 165 of 1000 saved random draws reaching at least 47 captures, not significant at alpha=.05. This is limited/directional evidence. No new random simulation or confirmatory test evaluation was run.

## 8. Known Limitations

- Same-category evaluation does not establish unseen-prompt or unseen-writer generalization.
- Shared-blind-spot qualitative causes remain unestablished. Shared features are a possible explanation only.
- Teacher-observable heuristics were explored only on Validation after feedback; no test-driven heuristic selection.
- Disagreement/extremity overlap is descriptive: 179/504, Jaccard .215923; caught by both/only disagreement/only extremity/neither = 18/29/25/136. The rankings provide partially different signals.
- Gender, Race/Ethnicity and SES results are a descriptive subgroup performance audit, with small groups flagged. Grade is not in the frozen fairness table. No fairness or causal claim follows.
- Aggregate labels reduce rater variance; model-to-aggregate and human-human errors are not directly comparable. No human superiority comparison.
- LanguageTool matches may be false positives. Consensus is auxiliary. Disagreement is not calibrated confidence or an error probability.
- HANU deployment requires local validation and domain adaptation. Top-20% means review-first; the remaining essays are also teacher graded.
- Fresh-machine installation was documented but not executed; actual local resource loading and frozen-model inference passed.

## 9. Teacher Feedback Addressed

The eight rows below group the feedback themes in the supplied finalization request; they are not a verbatim reconstruction of an absent original eight-item teacher document.

| # | Theme | Status/evidence |
|---|---|---|
| 1 | Prompt count and generalization | Addressed with explicit unresolved terminology, both crosstabs and seen-category boundary |
| 2 | Review-budget architecture | Addressed with deterministic ceil-sized batch API and tested legacy semantics |
| 3 | Practical teacher baseline | Addressed with prespecified exploratory Validation-only grammar-rate/shortest rules; stronger confirmatory teacher baseline remains future research |
| 4 | Disagreement vs extremity | Addressed with saved-prediction overlap and error partition |
| 5 | Shared blind spots | Addressed with 97 verified cases, no causal invention, reproducible text-free manual template |
| 6 | Fairness/subgroups | Addressed through descriptive-only interpretation and small-N warnings |
| 7 | Human-rater comparison | Addressed with three reference structures and aggregation caveat |
| 8 | Statistical value/responsible workflow | Addressed with p=.165, RF error reference, review-first and HANU boundaries |

Details: [finalization evidence](finalization_evidence.md), [final report](../report/final_report.md), [changelog](finalization_changelog.md).

## 10. Remaining Work

Weekly progress reports; research report writing/editing; presentation slides; Q&A/oral defense. Optional future research: stronger predeclared teacher baseline, unseen-prompt evaluation, human-coded blind-spot study, and local HANU validation. No core coding task remains.

## Verification and repository record

Initial branch: main; HEAD 2c7982e. Last five commits: 2c7982e, 8e436d7, 7447e5c, e3830f5, 68f31e7. Initially no tracked modifications; untracked `MLA-Project/`, `scratch_prompt.txt`, `scratch_slide_script.txt`, `scratch_step_151.txt` were preserved without deletion or edits.

Baseline `.venv\Scripts\python.exe -m pytest`: 72 passed. Final tests and smoke/static commands are recorded in [changelog](finalization_changelog.md). Forty-four protected local artifacts were snapshotted before edits; all hashes matched afterward, including the split manifest, four core models, saved official predictions and Phase 8/9 tables. Original Phase 9 manifest output hashes also matched. The ignored local integrity snapshot is `data/04_intermediate_work/finalization_integrity_before.json`.

Historical proposals and original evaluation provenance retain their original assumptions/interpretive labels; current final interpretation is this document and the final report. Changes are left reviewable in the working tree; no commit or deletion was made.

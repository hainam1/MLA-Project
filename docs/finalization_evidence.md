# Finalization evidence (2026-10-03)

## Prompt terminology and generalization

Repo contains 44 distinct values in the operational `prompt` field, while the lecturer referred to 29 prompts. The repository does not contain enough authoritative metadata to reconcile the two counts.

Both original final corpus CSVs contain 44 distinct short prompt-name strings and one distinct `task` value. No separate canonical prompt ID or full assignment-text mapping is supplied in those tables. The raw-rater table has no prompt/task field. The local upstream README and source documentation do not establish a mapping to 29. `prompt_id` in the loader/manifest is a rename of the source string, not a new canonical identifier; cleaned `prompt` exactly matches it by essay ID. Neither count is a headline claim in the final report.

Use: **prompt-stratified across the prompt categories available in the dataset.**

[Full crosstab](data/finalization_tables/prompt_crosstab_all.csv) and [privacy-eligible crosstab](data/finalization_tables/prompt_crosstab_eligible.csv) have columns model_train, validation, official_test. Every observed category has nonzero counts in all three partitions; there are no Train-only, Validation-only, or Test-only categories. Totals are 3128/783/2571 before filtering and 3050/762/2518 after filtering.

Current evaluation primarily measures generalization to new essays under prompt categories represented during development, rather than generalization to completely unseen prompts. No stable writer ID supports unseen-writer claims either.

## Reference errors and inference

Large error of the frozen Random Forest reference predictor means `max(abs(Vocabulary - RF_Vocabulary), abs(Grammar - RF_Grammar)) >= 1.0`. RF was selected using lower Validation MAE for both traits. Triage evaluation therefore measures the ability of disagreement to identify large errors of the RF reference predictor. This definition was verified in `evaluation.phase8.add_review_signals` and preserved.

There are two supervised regression targets implemented with independently trained single-target models: four fitted target/family pairs. Single-essay output retains the auxiliary Ridge/RF mean; it is not a promoted confirmatory predictor. `review_priority_score` is maximum target disagreement. Batch selection ranks descending, breaks ties by ascending string essay ID, and selects `ceil(N * review_budget)`. Budget zero selects none. Every official grade remains the teacher's responsibility.

## Teacher-observable baseline

The two rules were specified in `scripts/finalization_supplement.py` before execution: descending detected grammar matches per 100 words and ascending word count, with no weights or tuning. Only eligible Validation IDs, existing features, and frozen RF labels were used. This is **exploratory validation-only analysis added after teacher feedback**, outside the Phase 9 confirmatory comparison.

| Strategy | N | Selected | Large errors | Captured | Capture | Precision | Lift |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grammar-error-rate-first | 762 | 153 | 69 | 11 | 15.942% | 7.190% | 0.793976 |
| Shortest-first | 762 | 153 | 69 | 15 | 21.739% | 9.804% | 1.082694 |
| Frozen disagreement (context) | 762 | 153 | 69 | 15 | 21.739% | 9.804% | 1.082694 |

Grammar matches require LanguageTool and are automated screening rather than human-coded errors; shortest-first is directly observable without ML. Random alone is an insufficient practical comparator. These results neither establish optimal teacher behavior nor justify choosing a new Official Test strategy. A stronger teacher-designed baseline remains future confirmatory research.

## Saved-prediction supplementary comparison

| Comparison (Official Test, Top-20%) | Value |
|---|---:|
| Overlap | 179/504 = 35.516% |
| Jaccard | 179/829 = 0.215923 |
| Large errors caught by both | 18 |
| Only disagreement | 29 |
| Only extremity | 25 |
| Neither | 136 |
| Spearman disagreement vs extremity | 0.107009 |

The two rankings provide partially different signals. This is descriptive supplementary analysis, not proof of independent superiority. No model predictions were rerun. The frozen comparison still has 47 disagreement captures and 43 extremity captures.

From the 1000 saved random draws at threshold 1.0 and budget .20, 165 captured at least 47 errors. The empirical one-sided tail proportion is `165/1000 = .165` (unadjusted empirical convention), not significant at alpha .05. No random simulation was rerun. Disagreement produced the highest observed capture rate among the tested strategies, but the evidence was insufficient to establish statistical superiority over random selection.

## Shared blind spots and manual review

The frozen Validation-median threshold is 0.133989655155. There are 97 Official Test RF large errors below it. One possible explanation is that both models share the same feature representation, but the project has not yet established the qualitative causes of these shared blind spots.

[Manual-analysis sample](data/finalization_tables/manual_analysis_sample.csv) contains 12 shared blind spots, 10 high-disagreement large errors, and 5 low-disagreement non-large-error cases, sampled by ascending string ID within each category. It contains numeric observations and blank notes, no essay text or invented human coding. Original eligible texts remain private for future authorized manual analysis.

## Subgroups and human raters

The preserved Gender, Race/Ethnicity and SES artifacts contain N, RF MAE, RF large-error prevalence, selection and capture; N<20 is flagged. This is a **descriptive subgroup performance audit**, not causal or fairness evidence. Grade is source metadata but is not included in the existing frozen fairness table; no Grade fairness conclusion is claimed.

Human-human disagreement, model-to-aggregate error and model-to-individual-rater error use different references. Aggregate labels reduce rater variance, so model-to-aggregate error is not directly comparable with human-to-human disagreement. No superiority over human raters is established.

## Reproduction

Run `.venv\Scripts\python.exe scripts/finalization_supplement.py` from the project root. It reads saved predictions and features, writes only `docs/data/finalization_tables/`, and verifies the original Phase 9 manifest output hashes. This does not run training or regenerate official metrics. Original source documentation, proposal history and frozen Phase 9 narrative remain provenance; the final report and freeze status govern current interpretation.

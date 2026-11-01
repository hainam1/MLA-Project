# Post-Midterm Supplementary Research Results

The original Ridge/RF + 14-feature baseline and frozen Official Test results remain primary. This document records instructor-requested work after midterm; it does not rewrite confirmatory findings.

## P0 completed first

[Next-week update](../weekly_reports/week_next_teacher_feedback.md) contains the fixed RF large-deviation definition, verified human-rater metrics and saved Ridge Validation results. All four ranking strategies use the same RF binary labels. RF reference was recorded frozen on 2026-10-01 after lower-Validation-MAE selection. Aggregate labels are uncertain; >=1.0 is an operational deviation, not objective wrongness.

Raw paired Validation raters differ by exactly 1 point in 303/762 Vocabulary cases and 371/762 Grammar cases. More-than-one differences are 7/762 and 19/762. The within-1 agreement statistic includes exact-one cases; do not call >=1 rater disagreement rare.

## Max rationale and sensitivity

D=max(dV,dG) preserves one severe trait disagreement for an either-trait review queue; averaging can dilute it (dV=.8,dG=0 -> max=.8, mean=.4). This is a workflow rationale, not evidence of superiority. No weights were tuned.

Post-midterm validation sensitivity analysis requested by instructor, N=762, RF large errors=69, K=ceil(.2*762)=153:

| Aggregation | Captured | Capture | Precision | Lift |
|---|---:|---:|---:|---:|
| Max (frozen) | 15 | 21.739% | 9.804% | 1.082694 |
| Mean (supplementary) | 17 | 24.638% | 11.111% | 1.227053 |

Selected-set overlap: 131/153=85.621%; Jaccard=131/175=.748571. Mean has a higher observed Validation point estimate by 2 errors; this analysis has no superiority test and does not promote a new frozen strategy. Revisit aggregation in future prespecified research.

## Canonical prompts and unseen-prompt status

[Source investigation](prompt_reconciliation.md) confirms 29 in the original abstract, but 44 categories in released metadata and detailed preprint statistics/figure. No crosswalk reconciles them. [Unseen-prompt design](unseen_prompt_design.md) is ready, but canonical evaluation is blocked pending mapping. No proxy grouping, new model fitting or fabricated result was substituted.

Eligible-development length by operational prompt: 3812 essays, 44 categories; mean lengths range from 169.000 to 523.308 words. Between-category sum-of-squares fraction (descriptive eta-squared)=0.078263. The distribution differs observably across categories, but this is not a canonical-prompt causal effect. CSV includes N, mean, median, SD and IQR for each category.

## Exploratory Validation feature/error characteristics

Compare 69 large-RF-error essays with 693 non-large-error essays, using existing predictions and 14 saved features. The complete table includes means, medians, signed mean differences and pooled-SD standardized mean differences. No significance tests, causal labels or tuning follow.

Large-error essays average 416.551 vs 430.837 words (standardized difference -.075), so they are not substantially shorter by this comparison. They have lower detected grammar error rates (.858 vs 1.065 per 100 words), higher MTLD (56.566 vs 52.607), and lower mean Zipf frequency (6.030 vs 6.080). Most differences are small/modest; tool-detected issues do not equal reference score deviations. Syntactic ratios/estimated clauses are slightly lower, without establishing a qualitative cause.

[Human-coding sheet](../data/error_analysis/manual_error_review.csv): 32 unique eligible Validation essays, all human fields blank. Qualitative coding remains for human group members; automated descriptive analysis is complete.

## Actual 14-feature training example

Essay ID `1E4E4216EB39`, model_train, privacy status not_flagged. Vocabulary label=4.0; Grammar label=3.5. Selected deterministically nearest eligible model_train median word count, then ascending string ID. No raw text is exposed; not_flagged is a privacy screen, not a guarantee for publishing learner text.

| Feature | Actual value |
|---|---:|
| word_count | 400.0 |
| sentence_count | 22.0 |
| mean_sentence_length | 18.1818181818 |
| mtld | 56.6471229888 |
| mattr | 0.759772079772 |
| mean_word_frequency | 6.098375 |
| mean_word_length | 4.1425 |
| lexical_density | 0.4925 |
| noun_diversity | 0.285714285714 |
| detected_grammar_errors_per_100_words | 0.25 |
| detected_error_free_sentence_ratio | 0.954545454545 |
| complex_sentence_ratio | 0.545454545455 |
| estimated_clauses_per_sentence | 2.36363636364 |
| subordinate_clause_ratio | 0.403846153846 |

## Explicit subgroup evaluation plan

Descriptive subgroup performance auditing by Gender, Grade, Race/Ethnicity and SES will report subgroup N, RF MAE per target, RF large-error rate, and triage selection/capture where reference labels exist, alongside Shortest-first selection and uniform-random expected selection. Flag N<20 and zero-error denominators; report observed differences without claiming fairness, lack of bias or causation.

The new supplementary Validation table includes Grade; Grade 9 has N=4 and zero large errors, so capture is undefined and the estimate is especially unstable. The original frozen Official Test audit remains unchanged and does not acquire a new Grade analysis by implication.

## Future transformer plan

[Plan only](transformer_future_plan.md): raw-text models could diversify representation/errors. No guaranteed improvement, no implementation, and no inclusion in frozen baseline findings.

## Scientific provenance

All new numeric research outputs are under `docs/data/post_midterm/`, with the instructor-requested manual sheet under `docs/data/error_analysis/`. The script only uses Validation predictions/labels for sensitivity/error/subgroup/rater comparisons; development features support length descriptions/example selection. It never trains, predicts on Official Test, or changes baseline artifacts. Input hashes are saved in analysis_summary.json. The 48-file frozen integrity snapshot remains matched.

Verification on 2026-10-03: the full test suite passed (93 tests, including five new supplementary-analysis cases); the final script rerun reproduced the sensitivity results and checked all 48 protected hashes without mismatch. The original 44-file finalization hash inventory also remained matched. `git diff --check` passed. Canonical unseen-prompt evaluation and human qualitative coding remain explicitly pending.

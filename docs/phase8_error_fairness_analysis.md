# Phase 8B: Validation Error Analysis and Fairness Audit

> Descriptive validation-only analysis under the frozen Phase 8 protocol. No model was retrained, no feature or threshold was changed, and no official-test prediction or label was accessed.

## Error quadrants

High disagreement is frozen for this analysis as D >= the validation-population median, 0.133989655155.

| error_quadrant | n | percentage | mean_disagreement | mean_max_rf_error | mean_word_count |
|---|---|---|---|---|---|
| High disagreement + Large error | 33 | 4.330709 | 0.277730 | 1.215917 | 427.060606 |
| High disagreement + No large error | 348 | 45.669291 | 0.220963 | 0.502302 | 445.158046 |
| Low disagreement + Large error | 36 | 4.724409 | 0.076405 | 1.186774 | 406.916667 |
| Low disagreement + No large error | 345 | 45.275591 | 0.076876 | 0.506319 | 416.391304 |

The low-disagreement plus large-error quadrant is the shared-blind-spot group: both model families are relatively close while the selected RF reference prediction is still wrong by at least one point on one or both traits. This is an observed error pattern, not evidence of a causal mechanism.

### Shared-blind-spot detail

| n | percentage | mean_disagreement | mean_max_rf_error | vocabulary_overprediction_rate | grammar_overprediction_rate | vocabulary_human_score_distribution | grammar_human_score_distribution |
|---|---|---|---|---|---|---|---|
| 36 | 4.724409 | 0.076405 | 1.186774 | 0.527778 | 0.583333 | {"2":8,"2.5":5,"3":8,"3.5":7,"4":2,"4.5":3,"5":3} | {"1.5":1,"2":13,"2.5":4,"3":1,"3.5":5,"4":7,"4.5":3,"5":2} |

## Errors by essay length

| length_band | n | large_error_prevalence | mean_max_rf_error | vocabulary_mean_signed_error | grammar_mean_signed_error |
|---|---|---|---|---|---|
| Q1 | 185 | 0.102703 | 0.567075 | 0.034416 | 0.026807 |
| Q2 | 187 | 0.085561 | 0.554757 | -0.046993 | -0.043057 |
| Q3 | 202 | 0.084158 | 0.559915 | -0.020932 | -0.061988 |
| Q4 | 188 | 0.090426 | 0.588185 | 0.036709 | 0.016928 |

## Errors by human score level and direction

| target | human_score | n | mean_target_absolute_error | mean_target_signed_error | overprediction_rate | underprediction_rate | large_error_prevalence |
|---|---|---|---|---|---|---|---|
| Vocabulary | 1.000000 | 1 | 2.100199 | 2.100199 | 1.000000 | 0.000000 | 1.000000 |
| Vocabulary | 1.500000 | 2 | 1.249850 | 1.249850 | 1.000000 | 0.000000 | 1.000000 |
| Vocabulary | 2.000000 | 26 | 0.930659 | 0.930659 | 1.000000 | 0.000000 | 0.461538 |
| Vocabulary | 2.500000 | 99 | 0.487483 | 0.487483 | 1.000000 | 0.000000 | 0.090909 |
| Vocabulary | 3.000000 | 311 | 0.236443 | 0.145275 | 0.713826 | 0.286174 | 0.048232 |
| Vocabulary | 3.500000 | 185 | 0.256065 | -0.196529 | 0.210811 | 0.789189 | 0.059459 |
| Vocabulary | 4.000000 | 113 | 0.546505 | -0.541048 | 0.035398 | 0.964602 | 0.035398 |
| Vocabulary | 4.500000 | 18 | 0.887025 | -0.887025 | 0.000000 | 1.000000 | 0.500000 |
| Vocabulary | 5.000000 | 7 | 1.217627 | -1.217627 | 0.000000 | 1.000000 | 0.857143 |
| Grammar | 1.000000 | 2 | 1.673390 | 1.673390 | 1.000000 | 0.000000 | 1.000000 |
| Grammar | 1.500000 | 3 | 1.160981 | 1.160981 | 1.000000 | 0.000000 | 0.666667 |
| Grammar | 2.000000 | 108 | 0.701460 | 0.701460 | 1.000000 | 0.000000 | 0.203704 |
| Grammar | 2.500000 | 163 | 0.348729 | 0.301080 | 0.803681 | 0.196319 | 0.055215 |
| Grammar | 3.000000 | 192 | 0.288245 | -0.026836 | 0.447917 | 0.552083 | 0.005208 |
| Grammar | 3.500000 | 192 | 0.354094 | -0.315346 | 0.161458 | 0.838542 | 0.041667 |
| Grammar | 4.000000 | 75 | 0.691513 | -0.691513 | 0.000000 | 1.000000 | 0.146667 |
| Grammar | 4.500000 | 23 | 0.913369 | -0.913369 | 0.000000 | 1.000000 | 0.434783 |
| Grammar | 5.000000 | 4 | 1.381254 | -1.381254 | 0.000000 | 1.000000 | 1.000000 |

Positive signed error is overprediction and negative signed error is underprediction. The observed pattern is regression toward the middle of the score scale; extreme score levels have very small samples and must be interpreted cautiously.

## Errors by prompt

The table below is limited to prompts with at least 20 eligible validation essays for readability. The complete 44-prompt descriptive table, including small groups, is in `error_by_prompt.csv`.

| prompt_id | n | large_error_prevalence | mean_max_rf_error | vocabulary_mean_signed_error | grammar_mean_signed_error |
|---|---|---|---|---|---|
| Positive attitudes | 36 | 0.138889 | 0.650341 | -0.143431 | -0.089838 |
| Individuality | 29 | 0.137931 | 0.632191 | 0.094288 | -0.026228 |
| Success and failure | 42 | 0.119048 | 0.610301 | 0.079960 | 0.223706 |
| First impressions | 34 | 0.117647 | 0.544877 | 0.015752 | -0.136001 |
| Distance learning | 57 | 0.105263 | 0.541245 | 0.077131 | -0.030974 |
| Three-year high school program | 29 | 0.103448 | 0.606130 | 0.002957 | -0.105268 |
| Trying something beyond what you have mastered | 32 | 0.093750 | 0.478307 | -0.067089 | 0.068841 |
| Four-day work week | 27 | 0.074074 | 0.527236 | 0.091264 | -0.095363 |
| Career commitment | 43 | 0.069767 | 0.503584 | 0.037828 | 0.029925 |
| Self-reliance | 25 | 0.040000 | 0.581655 | -0.012667 | 0.088658 |
| Working with a group or alone | 27 | 0.037037 | 0.644181 | -0.032089 | 0.063239 |
| Impact of technology | 35 | 0.028571 | 0.522527 | 0.014224 | 0.018684 |
| Being busy | 41 | 0.024390 | 0.437765 | 0.044781 | -0.069296 |

## Fairness audit

Demographic attributes are used only for this validation audit. They are not among the 14 model predictors.

| attribute | group | n | vocabulary_mae | grammar_mae | large_error_prevalence | disagreement_selection_rate | within_group_capture_rate | shortest_first_selection_rate | random_expected_selection_rate | small_n_flag |
|---|---|---|---|---|---|---|---|---|---|---|
| gender | Female | 327 | 0.379599 | 0.458751 | 0.094801 | 0.177370 | 0.225806 | 0.146789 | 0.200787 | False |
| gender | Male | 435 | 0.368000 | 0.439411 | 0.087356 | 0.218391 | 0.210526 | 0.241379 | 0.200787 | False |
| race_ethnicity | American Indian/Alaskan Native | 2 | 0.231986 | 0.559207 | 0.000000 | 0.000000 | NA | 0.000000 | 0.200787 | True |
| race_ethnicity | Asian/Pacific Islander | 98 | 0.409860 | 0.472611 | 0.142857 | 0.224490 | 0.428571 | 0.163265 | 0.200787 | False |
| race_ethnicity | Black/African American | 70 | 0.388590 | 0.442332 | 0.057143 | 0.214286 | 0.000000 | 0.142857 | 0.200787 | False |
| race_ethnicity | Hispanic/Latino | 527 | 0.365493 | 0.435839 | 0.079696 | 0.193548 | 0.142857 | 0.214421 | 0.200787 | False |
| race_ethnicity | Two or more races/Other | 6 | 0.476727 | 0.726659 | 0.333333 | 0.333333 | 0.500000 | 0.166667 | 0.200787 | True |
| race_ethnicity | White | 59 | 0.354272 | 0.486618 | 0.118644 | 0.203390 | 0.285714 | 0.220339 | 0.200787 | False |
| SES | Economically disadvantaged | 512 | 0.380148 | 0.443505 | 0.097656 | 0.199219 | 0.180000 | 0.203125 | 0.200787 | False |
| SES | Not economically disadvantaged | 250 | 0.358291 | 0.456323 | 0.076000 | 0.204000 | 0.315789 | 0.196000 | 0.200787 | False |

These are subgroup disparities or observed differences; this audit does not establish causation or justify labeling them as bias.

## Sensitivity analysis

The primary threshold remains 1.0 and the primary budget remains 20%. Thresholds 0.5 and 1.5 and budgets 10% and 30% are predeclared sensitivity analyses, not settings searched for favorable disagreement performance.

| strategy | selected_count | large_error_count | captured_count | capture_rate | precision | lift |
|---|---|---|---|---|---|---|
| Random | 153 | 69 | 13.946000 | 0.202116 | 0.091150 | 1.006617 |
| Shortest-first | 153 | 69 | 15.000000 | 0.217391 | 0.098039 | 1.082694 |
| Ridge extremity | 153 | 69 | 10.000000 | 0.144928 | 0.065359 | 0.721796 |
| Ridge-RF disagreement | 153 | 69 | 15.000000 | 0.217391 | 0.098039 | 1.082694 |

All predeclared combinations are in `docs/data/phase8_tables/sensitivity_analysis.csv`.

## Human-rater context

| trait | n_samples | human_human_mae | within_0_5_points_rate | quadratic_weighted_kappa | model_aggregate_human_mae | model_individual_human_mae |
|---|---|---|---|---|---|---|
| Vocabulary | 762 | 0.416010 | 0.593176 | 0.501748 | 0.372977 | 0.457250 |
| Grammar | 762 | 0.536745 | 0.488189 | 0.513990 | 0.447710 | 0.556102 |

Human-human MAE compares two individual ratings. Model-aggregate MAE compares a model with the released aggregate label, while model-individual MAE averages comparisons with each individual rater. These quantities have different reference structures. A smaller model-aggregate MAE than human-human MAE is therefore not proof that the model is better than human raters; the results provide context for label uncertainty only.

## Analysis definitions and cautions

- Length bands use eligible model-train word-count quartiles with left-closed intervals and edges `[-Infinity, 293.0, 400.0, 523.0, Infinity]`.
- Human-score and prompt results are descriptive. Overprediction and underprediction use RF prediction minus human aggregate score and make no causal claim.
- 2 fairness rows have N < 20 and are explicitly flagged; estimates for these groups are unstable.
- Prompt-level results include many small groups and should not be ranked as if their estimates had equal precision.

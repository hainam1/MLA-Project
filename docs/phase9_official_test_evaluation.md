# Phase 9: One-Time Official-Test Evaluation

> Confirmatory evaluation under the frozen protocol. Models, features, reference predictors, thresholds, budgets, rankings, and metrics were not changed after test access.

## Population and integrity

- Official-test rows: 2,571; privacy-eligible rows evaluated: 2,518.
- Primary review budget: 20%, K = 504.
- All four Phase 6 and four reconstructed Phase 5 length-only model hashes matched before prediction.
- No model was retrained during Phase 9.

## Regression metrics

| model | target | n | mae | rmse | qwk |
|---|---|---|---|---|---|
| Ridge | Vocabulary | 2518 | 0.367881 | 0.467167 | 0.484352 |
| Random Forest | Vocabulary | 2518 | 0.364197 | 0.462448 | 0.478500 |
| Mean-score baseline | Vocabulary | 2518 | 0.471199 | 0.574540 | 0.000000 |
| Length-only Ridge | Vocabulary | 2518 | 0.430174 | 0.545681 | 0.209612 |
| Length-only Random Forest | Vocabulary | 2518 | 0.457027 | 0.578527 | 0.210388 |
| Length-only consensus | Vocabulary | 2518 | 0.432209 | 0.549125 | 0.214684 |
| Ridge | Grammar | 2518 | 0.443020 | 0.550719 | 0.504522 |
| Random Forest | Grammar | 2518 | 0.433587 | 0.537710 | 0.505689 |
| Mean-score baseline | Grammar | 2518 | 0.531507 | 0.672112 | 0.000000 |
| Length-only Ridge | Grammar | 2518 | 0.531556 | 0.661097 | 0.043688 |
| Length-only Random Forest | Grammar | 2518 | 0.585616 | 0.725139 | 0.065648 |
| Length-only consensus | Grammar | 2518 | 0.548777 | 0.676852 | 0.075342 |

## Large errors

There were 208 large errors (8.260524%): 61 Vocabulary-only, 126 Grammar-only, and 21 on both traits.

## Frozen primary review comparison

| strategy | selected_count | large_error_count | captured_count | capture_rate | precision | lift |
|---|---|---|---|---|---|---|
| Random | 504 | 208 | 41.427000 | 0.199168 | 0.082196 | 0.995051 |
| Shortest-first | 504 | 208 | 37.000000 | 0.177885 | 0.073413 | 0.888717 |
| Ridge extremity | 504 | 208 | 43.000000 | 0.206731 | 0.085317 | 1.032833 |
| Ridge-RF disagreement | 504 | 208 | 47.000000 | 0.225962 | 0.093254 | 1.128911 |

Random empirical intervals: Capture Rate 0.153846-0.250120; Precision 0.063492-0.103224; Lift 0.768620-1.249608.

## Error quadrants

The high-disagreement threshold remained the frozen validation median, D = 0.133989655155.

| error_quadrant | n | percentage | mean_disagreement | mean_max_rf_error | mean_word_count |
|---|---|---|---|---|---|
| High disagreement + Large error | 111 | 4.408261 | 0.230810 | 1.203798 | 475.477477 |
| High disagreement + No large error | 1057 | 41.977760 | 0.228007 | 0.487965 | 442.408704 |
| Low disagreement + Large error | 97 | 3.852264 | 0.082000 | 1.190247 | 427.773196 |
| Low disagreement + No large error | 1253 | 49.761716 | 0.081223 | 0.482869 | 400.152434 |

## Fairness audit

| attribute | group | n | vocabulary_mae | grammar_mae | large_error_prevalence | disagreement_selection_rate | within_group_capture_rate | shortest_first_selection_rate | random_expected_selection_rate | small_n_flag |
|---|---|---|---|---|---|---|---|---|---|---|
| gender | Female | 1101 | 0.375846 | 0.446728 | 0.100817 | 0.217075 | 0.225225 | 0.167121 | 0.200159 | False |
| gender | Male | 1417 | 0.355147 | 0.423376 | 0.068454 | 0.187015 | 0.226804 | 0.225829 | 0.200159 | False |
| race_ethnicity | American Indian/Alaskan Native | 4 | 0.281769 | 0.410734 | 0.000000 | 0.250000 | NA | 0.250000 | 0.200159 | True |
| race_ethnicity | Asian/Pacific Islander | 301 | 0.365085 | 0.404708 | 0.069767 | 0.196013 | 0.190476 | 0.139535 | 0.200159 | False |
| race_ethnicity | Black/African American | 189 | 0.348331 | 0.441090 | 0.089947 | 0.179894 | 0.176471 | 0.142857 | 0.200159 | False |
| race_ethnicity | Hispanic/Latino | 1832 | 0.367109 | 0.441348 | 0.086245 | 0.201419 | 0.227848 | 0.219432 | 0.200159 | False |
| race_ethnicity | Two or more races/Other | 10 | 0.325904 | 0.354038 | 0.100000 | 0.000000 | 0.000000 | 0.100000 | 0.200159 | True |
| race_ethnicity | White | 182 | 0.353810 | 0.400306 | 0.060440 | 0.225275 | 0.363636 | 0.170330 | 0.200159 | False |
| SES | Economically disadvantaged | 1764 | 0.359880 | 0.430447 | 0.078798 | 0.201247 | 0.215827 | 0.204082 | 0.200159 | False |
| SES | Not economically disadvantaged | 753 | 0.374747 | 0.441018 | 0.091633 | 0.197875 | 0.246377 | 0.191235 | 0.200159 | False |
| SES | Missing | 1 | 0.035389 | 0.376291 | 0.000000 | 0.000000 | NA | 0.000000 | 0.200159 | True |

These are observed subgroup differences, not automatic evidence of bias or unfairness. Demographics were not model predictors.

## Diagnostics

- disagreement_vs_actual_max_rf_error: Spearman rho = 0.022103
- disagreement_vs_ridge_extremity: Spearman rho = 0.107009
- disagreement_vs_word_count: Spearman rho = 0.044617

## Validation versus official test

| metric | validation | official_test |
|---|---|---|
| Ridge Vocabulary MAE | 0.374814 | 0.367881 |
| RF Vocabulary MAE | 0.372977 | 0.364197 |
| Ridge Grammar MAE | 0.456298 | 0.443020 |
| RF Grammar MAE | 0.447710 | 0.433587 |
| Large-error prevalence | 0.090551 | 0.082605 |
| Random Capture Rate @20% | 0.202116 | 0.199168 |
| Shortest Capture Rate @20% | 0.217391 | 0.177885 |
| Ridge Extremity Capture Rate @20% | 0.144928 | 0.206731 |
| Disagreement Capture Rate @20% | 0.217391 | 0.225962 |
| Disagreement Precision @20% | 0.098039 | 0.093254 |
| Disagreement Lift @20% | 1.082694 | 1.128911 |
| Shared-blind-spot proportion | 0.047244 | 0.038523 |

## Confirmatory interpretation

**A. Supports added value of disagreement**

This classification follows the frozen comparison against random selection, shortest-first, and Ridge extremity. Test results were not used to alter the protocol. All predeclared sensitivity combinations are reported in `sensitivity_analysis.csv`.

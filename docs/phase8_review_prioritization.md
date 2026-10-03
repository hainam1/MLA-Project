# Phase 8: Validation Review Prioritization

> Validation only: 762 privacy-eligible essays. No official-test predictions or labels were loaded or evaluated.

## Frozen primary result

| strategy | selected_count | large_error_count | captured_count | capture_rate | precision | lift |
|---|---|---|---|---|---|---|
| Random | 153 | 69 | 13.946000 | 0.202116 | 0.091150 | 1.006617 |
| Shortest-first | 153 | 69 | 15.000000 | 0.217391 | 0.098039 | 1.082694 |
| Ridge extremity | 153 | 69 | 10.000000 | 0.144928 | 0.065359 | 0.721796 |
| Ridge-RF disagreement | 153 | 69 | 15.000000 | 0.217391 | 0.098039 | 1.082694 |

Random values are means over 1,000 uniform selections without replacement. Its 2.5th-97.5th percentiles are empirical random-selection reference intervals, not bootstrap confidence intervals.

| metric | mean | reference_2.5_percentile | reference_97.5_percentile |
|---|---|---|---|
| capture_rate | 0.202116 | 0.115942 | 0.289855 |
| precision | 0.091150 | 0.052288 | 0.130719 |
| lift | 1.006617 | 0.577437 | 1.443592 |

## Correlations

| comparison | spearman_rho |
|---|---|
| disagreement_vs_actual_max_rf_error | -0.004781 |
| disagreement_vs_ridge_extremity | 0.018409 |
| disagreement_vs_word_count | 0.015569 |

## RF reference-predictor metrics

| target | mae | rmse | r2 | qwk |
|---|---|---|---|---|
| Vocabulary | 0.372977 | 0.480023 | 0.300018 | 0.431970 |
| Grammar | 0.447710 | 0.554622 | 0.337743 | 0.483119 |

## Protocol

- Primary large error: maximum RF absolute error >= 1.0.
- Primary review budget: 20%, selecting 153 essays by ceiling.
- Ridge centers are medians of predictions on 3,050 eligible model-train essays: Vocabulary 3.26941940241, Grammar 3.12422572695.
- Shortest-first ranks word count ascending; extremity and disagreement rank descending; deterministic ties use ascending string essay ID.
- Disagreement is a triage signal, not a probability of error or calibrated confidence.
- Thresholds 0.5 and 1.5 and budgets 10% and 30% are sensitivity analyses in the output table; they do not replace the primary result.

## Interpretation

Ridge-RF disagreement ties with Shortest-first for the highest deterministic validation capture rate under the frozen primary protocol.

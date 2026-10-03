# Train-only Model Improvement Screening

> Uses only 3,050 privacy-eligible model-train essays and frozen folds. Validation rows used: 0. Official-test rows used: 0.

This is a predeclared challenger screening study, not a new independent performance estimate. Calibration is nested within each outer fold; all imputation, scaling, weighting, fitting, and calibration parameters are learned without the active holdout fold.

## Overall OOF metrics

| target | variant | mae | macro_band_mae | rmse | r2 | within_0_5_points_rate | within_1_0_point_rate | calibration_slope | fold_mae_ci95_lower | fold_mae_ci95_upper |
|---|---|---|---|---|---|---|---|---|---|---|
| Grammar | rf_absolute_error_weighted | 0.459610 | 0.516148 | 0.576897 | 0.332101 | 0.607541 | 0.920656 | 0.912129 | 0.429995 | 0.489227 |
| Grammar | rf_weighted | 0.459344 | 0.519373 | 0.573788 | 0.339279 | 0.610164 | 0.923934 | 0.962637 | 0.432305 | 0.486382 |
| Grammar | ordinal_logistic | 0.451838 | 0.524173 | 0.563440 | 0.362896 | 0.618361 | 0.928852 | 1.009189 | 0.421315 | 0.482363 |
| Grammar | rf_linear_calibrated | 0.456825 | 0.527986 | 0.572042 | 0.343295 | 0.611148 | 0.922295 | 0.997466 | 0.426016 | 0.487633 |
| Grammar | rf_isotonic_calibrated | 0.457979 | 0.528808 | 0.573686 | 0.339515 | 0.618689 | 0.917705 | 0.963894 | 0.429709 | 0.486249 |
| Grammar | ridge_weighted | 0.467963 | 0.531875 | 0.582401 | 0.319294 | 0.596393 | 0.919672 | 0.883285 | 0.443354 | 0.492575 |
| Grammar | rf_baseline | 0.457694 | 0.532327 | 0.572443 | 0.342373 | 0.611803 | 0.923279 | 1.047734 | 0.426710 | 0.488678 |
| Grammar | rf_absolute_error | 0.453664 | 0.532388 | 0.573055 | 0.340967 | 0.610492 | 0.925246 | 1.051433 | 0.418258 | 0.489076 |
| Grammar | ridge_baseline | 0.463644 | 0.546279 | 0.577230 | 0.331328 | 0.601311 | 0.918033 | 0.986268 | 0.434608 | 0.492683 |
| Grammar | huber | 0.464022 | 0.547688 | 0.577730 | 0.330170 | 0.599672 | 0.917049 | 0.972193 | 0.434668 | 0.493379 |
| Vocabulary | ridge_weighted | 0.377650 | 0.463591 | 0.475291 | 0.343677 | 0.715738 | 0.965574 | 0.854152 | 0.364298 | 0.391002 |
| Vocabulary | ordinal_logistic | 0.366556 | 0.466911 | 0.465685 | 0.369940 | 0.729508 | 0.967869 | 0.988940 | 0.356305 | 0.376807 |
| Vocabulary | rf_weighted | 0.375941 | 0.469270 | 0.475505 | 0.343087 | 0.717049 | 0.959016 | 0.932800 | 0.365048 | 0.386835 |
| Vocabulary | rf_absolute_error_weighted | 0.375135 | 0.471356 | 0.477127 | 0.338599 | 0.717705 | 0.960000 | 0.941492 | 0.362497 | 0.387775 |
| Vocabulary | rf_linear_calibrated | 0.372676 | 0.477267 | 0.473707 | 0.348044 | 0.720000 | 0.962295 | 1.005980 | 0.360002 | 0.385349 |
| Vocabulary | rf_isotonic_calibrated | 0.374373 | 0.477862 | 0.475672 | 0.342625 | 0.725246 | 0.962623 | 0.974669 | 0.362409 | 0.386338 |
| Vocabulary | ridge_baseline | 0.372441 | 0.478112 | 0.471126 | 0.355131 | 0.730820 | 0.966557 | 1.013001 | 0.362946 | 0.381935 |
| Vocabulary | huber | 0.372337 | 0.479157 | 0.471756 | 0.353405 | 0.729180 | 0.966885 | 1.014409 | 0.362907 | 0.381766 |
| Vocabulary | rf_baseline | 0.372617 | 0.487099 | 0.474572 | 0.345662 | 0.717377 | 0.962623 | 1.091851 | 0.360146 | 0.385087 |
| Vocabulary | rf_absolute_error | 0.372635 | 0.511123 | 0.487210 | 0.310348 | 0.714754 | 0.960328 | 1.260648 | 0.359290 | 0.385979 |

## Predeclared acceptance checks

| target | variant | overall_mae_change | macro_band_mae_improvement_fraction | max_tail_bias_reduction_fraction | maximum_band_mae_increase | improved_folds | all_acceptance_rules_pass |
|---|---|---|---|---|---|---|---|
| Vocabulary | ridge_baseline | -0.000176 | 0.018449 | 0.011822 | 0.009953 | 3 | False |
| Vocabulary | ridge_weighted | 0.005033 | 0.048261 | 0.111334 | 0.039229 | 2 | False |
| Vocabulary | rf_weighted | 0.003324 | 0.036602 | 0.083963 | 0.028592 | 1 | False |
| Vocabulary | rf_absolute_error | 0.000018 | -0.049322 | -0.128831 | 0.079377 | 1 | False |
| Vocabulary | rf_absolute_error_weighted | 0.002518 | 0.032321 | 0.047512 | 0.023861 | 1 | False |
| Vocabulary | huber | -0.000280 | 0.016305 | -0.005535 | 0.008190 | 3 | False |
| Vocabulary | ordinal_logistic | -0.006061 | 0.041444 | 0.056077 | 0.010519 | 4 | False |
| Vocabulary | rf_linear_calibrated | 0.000059 | 0.020185 | 0.031296 | 0.011610 | 2 | False |
| Vocabulary | rf_isotonic_calibrated | 0.001756 | 0.018963 | 0.036966 | 0.014567 | 2 | False |
| Grammar | ridge_baseline | 0.005950 | -0.026209 | -0.043873 | 0.033159 | 1 | False |
| Grammar | ridge_weighted | 0.010269 | 0.000848 | 0.077277 | 0.073095 | 1 | False |
| Grammar | rf_weighted | 0.001650 | 0.024334 | 0.092567 | 0.017616 | 1 | False |
| Grammar | rf_absolute_error | -0.004030 | -0.000115 | -0.027109 | 0.020488 | 3 | False |
| Grammar | rf_absolute_error_weighted | 0.001916 | 0.030394 | 0.103388 | 0.032294 | 1 | False |
| Grammar | huber | 0.006328 | -0.028857 | -0.053573 | 0.040714 | 1 | False |
| Grammar | ordinal_logistic | -0.005856 | 0.015318 | 0.018947 | -0.000382 | 5 | False |
| Grammar | rf_linear_calibrated | -0.000869 | 0.008154 | 0.018770 | 0.009574 | 5 | False |
| Grammar | rf_isotonic_calibrated | 0.000285 | 0.006610 | 0.027472 | 0.007277 | 2 | False |

No challenger satisfies every predeclared acceptance rule; feature extractor v2 remains justified but is not started automatically.

No prediction was rounded or clipped.

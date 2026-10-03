# Phase 7 — Validation Regression Evaluation

> **Scope:** eligible validation rows only; no model fitting, tuning, disagreement queue, or official-test access.

## Evaluation population

Phase 7 joins the text-free Phase 6 predictions to human Vocabulary and Grammar scores by `essay_id`.
The evaluation population contains **762 eligible validation essays** (each essay contributes four model/target error rows). The 21 excluded validation rows remain outside prediction and metrics.

Phase 5 baseline artifacts were re-hashed and their metrics recomputed before comparison. The Phase 5 summary records 762 eligible validation rows; Phase 6 records 762 predictions.

## Regression metrics

| model | target | n_samples | mae | rmse | r2 |
|---|---|---|---|---|---|
| Ridge | Vocabulary | 762 | 0.374814 | 0.478538 | 0.304342 |
| Random Forest | Vocabulary | 762 | 0.372977 | 0.480023 | 0.300018 |
| Ridge | Grammar | 762 | 0.456298 | 0.560330 | 0.324042 |
| Random Forest | Grammar | 762 | 0.447710 | 0.554622 | 0.337743 |

Predictions are continuous values exactly as saved by Phase 6; no rounding or clipping was applied before metric computation.

## Human and machine score statistics

The human rows describe the reference-score distribution. Ridge and Random Forest rows describe continuous, unrounded machine predictions on the same 762 essays.

| target | scorer | n_samples | mean | standard_deviation | minimum | q25 | median | q75 | maximum |
|---|---|---|---|---|---|---|---|---|---|
| Vocabulary | Human | 762 | 3.217848 | 0.574121 | 1.000000 | 3.000000 | 3.000000 | 3.500000 | 5.000000 |
| Vocabulary | Ridge | 762 | 3.222072 | 0.336443 | 1.694235 | 3.034833 | 3.256044 | 3.447715 | 4.094229 |
| Vocabulary | Random Forest | 762 | 3.218179 | 0.309988 | 2.349768 | 3.021995 | 3.205236 | 3.408950 | 4.191393 |
| Grammar | Human | 762 | 3.020341 | 0.681976 | 1.000000 | 2.500000 | 3.000000 | 3.500000 | 5.000000 |
| Grammar | Ridge | 762 | 3.012946 | 0.402432 | 0.774876 | 2.776664 | 3.085150 | 3.304294 | 3.868940 |
| Grammar | Random Forest | 762 | 3.004027 | 0.388417 | 2.173087 | 2.702245 | 2.997503 | 3.323522 | 4.045836 |

Machine behavior at each observed human-score level is reported below. `mean_difference_machine_minus_human` is positive for overprediction and negative for underprediction. Tolerance rates use raw continuous predictions.

| target | model | human_score | n_samples | mean_machine_score | mean_difference_machine_minus_human | mae | within_0_5_points_rate | within_1_0_point_rate |
|---|---|---|---|---|---|---|---|---|
| Vocabulary | Ridge | 1.000000 | 1 | 2.544067 | 1.544067 | 1.544067 | 0.000000 | 0.000000 |
| Vocabulary | Ridge | 1.500000 | 2 | 2.037191 | 0.537191 | 0.537191 | 0.500000 | 1.000000 |
| Vocabulary | Ridge | 2.000000 | 26 | 2.921343 | 0.921343 | 0.921343 | 0.153846 | 0.538462 |
| Vocabulary | Ridge | 2.500000 | 99 | 2.966635 | 0.466635 | 0.488547 | 0.484848 | 0.959596 |
| Vocabulary | Ridge | 3.000000 | 311 | 3.148876 | 0.148876 | 0.270613 | 0.874598 | 1.000000 |
| Vocabulary | Ridge | 3.500000 | 185 | 3.332584 | -0.167416 | 0.224232 | 0.940541 | 1.000000 |
| Vocabulary | Ridge | 4.000000 | 113 | 3.468678 | -0.531322 | 0.532604 | 0.442478 | 0.964602 |
| Vocabulary | Ridge | 4.500000 | 18 | 3.603216 | -0.896784 | 0.896784 | 0.000000 | 0.666667 |
| Vocabulary | Ridge | 5.000000 | 7 | 3.757344 | -1.242656 | 1.242656 | 0.000000 | 0.142857 |
| Vocabulary | Random Forest | 1.000000 | 1 | 3.100199 | 2.100199 | 2.100199 | 0.000000 | 0.000000 |
| Vocabulary | Random Forest | 1.500000 | 2 | 2.749850 | 1.249850 | 1.249850 | 0.000000 | 0.000000 |
| Vocabulary | Random Forest | 2.000000 | 26 | 2.930659 | 0.930659 | 0.930659 | 0.038462 | 0.538462 |
| Vocabulary | Random Forest | 2.500000 | 99 | 2.987483 | 0.487483 | 0.487483 | 0.525253 | 0.959596 |
| Vocabulary | Random Forest | 3.000000 | 311 | 3.145275 | 0.145275 | 0.236443 | 0.890675 | 1.000000 |
| Vocabulary | Random Forest | 3.500000 | 185 | 3.303471 | -0.196529 | 0.256065 | 0.886486 | 1.000000 |
| Vocabulary | Random Forest | 4.000000 | 113 | 3.458952 | -0.541048 | 0.546505 | 0.451327 | 0.982301 |
| Vocabulary | Random Forest | 4.500000 | 18 | 3.612975 | -0.887025 | 0.887025 | 0.111111 | 0.611111 |
| Vocabulary | Random Forest | 5.000000 | 7 | 3.782373 | -1.217627 | 1.217627 | 0.000000 | 0.142857 |
| Grammar | Ridge | 1.000000 | 2 | 1.655697 | 0.655697 | 0.880821 | 0.500000 | 0.500000 |
| Grammar | Ridge | 1.500000 | 3 | 2.505725 | 1.005725 | 1.005725 | 0.000000 | 0.666667 |
| Grammar | Ridge | 2.000000 | 108 | 2.700476 | 0.700476 | 0.724482 | 0.250000 | 0.750000 |
| Grammar | Ridge | 2.500000 | 163 | 2.822781 | 0.322781 | 0.447302 | 0.564417 | 0.981595 |
| Grammar | Ridge | 3.000000 | 192 | 2.999168 | -0.000832 | 0.264560 | 0.890625 | 1.000000 |
| Grammar | Ridge | 3.500000 | 192 | 3.196867 | -0.303133 | 0.318242 | 0.817708 | 1.000000 |
| Grammar | Ridge | 4.000000 | 75 | 3.312220 | -0.687780 | 0.687780 | 0.173333 | 0.906667 |
| Grammar | Ridge | 4.500000 | 23 | 3.517586 | -0.982414 | 0.982414 | 0.000000 | 0.565217 |
| Grammar | Ridge | 5.000000 | 4 | 3.577869 | -1.422131 | 1.422131 | 0.000000 | 0.000000 |
| Grammar | Random Forest | 1.000000 | 2 | 2.673390 | 1.673390 | 1.673390 | 0.000000 | 0.000000 |
| Grammar | Random Forest | 1.500000 | 3 | 2.660981 | 1.160981 | 1.160981 | 0.000000 | 0.333333 |
| Grammar | Random Forest | 2.000000 | 108 | 2.701460 | 0.701460 | 0.701460 | 0.277778 | 0.851852 |
| Grammar | Random Forest | 2.500000 | 163 | 2.801080 | 0.301080 | 0.348729 | 0.723926 | 0.975460 |
| Grammar | Random Forest | 3.000000 | 192 | 2.973164 | -0.026836 | 0.288245 | 0.854167 | 1.000000 |
| Grammar | Random Forest | 3.500000 | 192 | 3.184654 | -0.315346 | 0.354094 | 0.723958 | 0.989583 |
| Grammar | Random Forest | 4.000000 | 75 | 3.308487 | -0.691513 | 0.691513 | 0.266667 | 0.866667 |
| Grammar | Random Forest | 4.500000 | 23 | 3.586631 | -0.913369 | 0.913369 | 0.043478 | 0.695652 |
| Grammar | Random Forest | 5.000000 | 4 | 3.618746 | -1.381254 | 1.381254 | 0.000000 | 0.000000 |

## Comparison with Phase 5 baselines

| model | target | baseline | baseline_mae | full_feature_mae | mae_improvement_pct |
|---|---|---|---|---|---|
| Ridge | Vocabulary | train_mean | 0.465594 | 0.374814 | 19.497849 |
| Ridge | Vocabulary | length_only_ridge | 0.436107 | 0.374814 | 14.054595 |
| Ridge | Vocabulary | length_only_random_forest | 0.458045 | 0.374814 | 18.170985 |
| Ridge | Vocabulary | length_only_consensus | 0.437708 | 0.374814 | 14.369096 |
| Random Forest | Vocabulary | train_mean | 0.465594 | 0.372977 | 19.892273 |
| Random Forest | Vocabulary | length_only_ridge | 0.436107 | 0.372977 | 14.475688 |
| Random Forest | Vocabulary | length_only_random_forest | 0.458045 | 0.372977 | 18.571910 |
| Random Forest | Vocabulary | length_only_consensus | 0.437708 | 0.372977 | 14.788648 |
| Ridge | Grammar | train_mean | 0.549460 | 0.456298 | 16.955203 |
| Ridge | Grammar | length_only_ridge | 0.542828 | 0.456298 | 15.940711 |
| Ridge | Grammar | length_only_random_forest | 0.566177 | 0.456298 | 19.407222 |
| Ridge | Grammar | length_only_consensus | 0.543179 | 0.456298 | 15.995048 |
| Random Forest | Grammar | train_mean | 0.549460 | 0.447710 | 18.518061 |
| Random Forest | Grammar | length_only_ridge | 0.542828 | 0.447710 | 17.522661 |
| Random Forest | Grammar | length_only_random_forest | 0.566177 | 0.447710 | 20.923935 |
| Random Forest | Grammar | length_only_consensus | 0.543179 | 0.447710 | 17.575976 |

Positive improvement means the full-feature model has lower MAE. Negative values are retained as evidence that the model did not beat that baseline.
Every full-feature model has lower MAE than all four available Phase 5 baselines.

## Point predictor selected per target

| target | ridge_mae | random_forest_mae | selected_model | tie_within_atol |
|---|---|---|---|---|
| Vocabulary | 0.374814 | 0.372977 | Random Forest | False |
| Grammar | 0.456298 | 0.447710 | Random Forest | False |

The rule is applied separately to Vocabulary and Grammar: lower validation MAE wins; Ridge is selected when the MAEs tie within 1e-12. The two predictions are not averaged.

## Error analysis

| model | target | mean_residual | median_absolute_error | p90_absolute_error | max_absolute_error | predictions_below_1 | predictions_above_5 |
|---|---|---|---|---|---|---|---|
| Ridge | Vocabulary | 0.004224 | 0.304306 | 0.778792 | 1.544067 | 0 | 0 |
| Random Forest | Vocabulary | 0.000331 | 0.302790 | 0.798214 | 2.100199 | 0 | 0 |
| Ridge | Grammar | -0.007396 | 0.388196 | 0.905131 | 1.619311 | 1 | 0 |
| Random Forest | Grammar | -0.016314 | 0.399518 | 0.908145 | 2.173693 | 0 | 0 |

- **Vocabulary (Random Forest):** mean residual 0.0003, 90th-percentile absolute error 0.7982, and maximum absolute error 2.1002 on essay `48EA282A4EAF` (human 1.00, prediction 3.1002).
- **Grammar (Random Forest):** mean residual -0.0163, 90th-percentile absolute error 0.9081, and maximum absolute error 2.1737 on essay `48EA282A4EAF` (human 1.00, prediction 3.1737).

The score-band pattern is consistent with regression toward the middle of the rubric: errors are larger at lower and higher reference-score bands than in the central band. Near-zero overall mean residuals therefore do not imply uniformly unbiased predictions across score levels.

- **Vocabulary:** MAE is 0.5797 for scores 2–<3 and 0.6250 for scores 4+, versus 0.2438 in the central 3–<4 band.
- **Grammar:** MAE is 0.4893 for scores 2–<3 and 0.7686 for scores 4+, versus 0.3212 in the central 3–<4 band.

One raw prediction falls outside the 1–5 rubric: Ridge Grammar predicts 0.7749 for essay `CA3EB3AA11FC`. It remains unclipped in every metric.

The largest absolute-error table contains IDs and scores only; essay text is not copied into any Phase 7 output.

Top absolute-error rows (for diagnostic follow-up):

| essay_id | model | target | actual | prediction | residual | absolute_error |
|---|---|---|---|---|---|---|
| 48EA282A4EAF | Random Forest | Grammar | 1.000000 | 3.173693 | 2.173693 | 2.173693 |
| 48EA282A4EAF | Random Forest | Vocabulary | 1.000000 | 3.100199 | 2.100199 | 2.100199 |
| 0AFC8CE27321 | Random Forest | Grammar | 5.000000 | 3.260484 | -1.739516 | 1.739516 |
| 0AFC8CE27321 | Ridge | Grammar | 5.000000 | 3.380689 | -1.619311 | 1.619311 |
| 48EA282A4EAF | Ridge | Vocabulary | 1.000000 | 2.544067 | 1.544067 | 1.544067 |
| 48EA282A4EAF | Ridge | Grammar | 1.000000 | 2.536518 | 1.536518 | 1.536518 |
| BC8115EEB029 | Ridge | Vocabulary | 2.000000 | 3.532720 | 1.532720 | 1.532720 |
| 52DC3B7C3952 | Random Forest | Grammar | 5.000000 | 3.530297 | -1.469703 | 1.469703 |
| D1D770AF6855 | Random Forest | Vocabulary | 5.000000 | 3.534387 | -1.465613 | 1.465613 |
| 53CF6D801CAF | Ridge | Vocabulary | 5.000000 | 3.545782 | -1.454218 | 1.454218 |

## Subgroup checks

Length groups use quartile cut points derived from model-train `word_count`; score bands are fixed exploratory intervals. Groups with fewer than 20 validation essays are omitted.

| group_type | group | target | selected_model | n_samples | mae | rmse | r2 |
|---|---|---|---|---|---|---|---|
| length_band | Q1 | Vocabulary | Random Forest | 185 | 0.360030 | 0.480990 | 0.182574 |
| length_band | Q2 | Vocabulary | Random Forest | 187 | 0.376240 | 0.489411 | 0.242893 |
| length_band | Q3 | Vocabulary | Random Forest | 202 | 0.335141 | 0.430576 | 0.333902 |
| length_band | Q4 | Vocabulary | Random Forest | 188 | 0.423125 | 0.518493 | 0.220404 |
| length_band | Q1 | Grammar | Random Forest | 185 | 0.445539 | 0.560376 | 0.239474 |
| length_band | Q2 | Grammar | Random Forest | 187 | 0.432465 | 0.541233 | 0.354430 |
| length_band | Q3 | Grammar | Random Forest | 202 | 0.465198 | 0.563342 | 0.358094 |
| length_band | Q4 | Grammar | Random Forest | 188 | 0.446221 | 0.552642 | 0.340552 |
| score_band | 2-<3 | Vocabulary | Random Forest | 125 | 0.579663 | 0.663907 | -9.702525 |
| score_band | 3-<4 | Vocabulary | Random Forest | 496 | 0.243762 | 0.306038 | -0.601929 |
| score_band | 4+ | Vocabulary | Random Forest | 138 | 0.624963 | 0.693744 | -5.886177 |
| score_band | 2-<3 | Grammar | Random Forest | 271 | 0.489301 | 0.587885 | -4.767302 |
| score_band | 3-<4 | Grammar | Random Forest | 384 | 0.321170 | 0.395358 | -1.500928 |
| score_band | 4+ | Grammar | Random Forest | 102 | 0.768588 | 0.831064 | -8.526961 |

## Outputs and limitations

- Metrics are validation-based and support model selection; they are not an independent final test estimate.
- This phase does not compute model disagreement, review priority, error capture, ablations, or official-test performance.
- Residuals and subgroup results describe observed validation behavior and do not establish causal explanations.
- Official-test features and labels were not read, loaded, previewed, or used.

Generated figures:

- `outputs/figures/phase7/phase7_predicted_vs_human.png`
- `outputs/figures/phase7/phase7_residual_distributions.png`
- `outputs/figures/phase7/phase7_mae_by_length_band.png`

Reproduce with:

```powershell
uv run --extra analysis python scripts/phase7_evaluate_regression_models.py
```

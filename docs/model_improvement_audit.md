# Model Improvement Audit — Human Reliability and Controlled Errors

> Baseline v1 is frozen. This audit does not fit a model, tune on validation, or evaluate official test.

## Human–human and model–human comparison

| trait | n_samples | human_human_mae | exact_agreement_rate | within_0_5_points_rate | quadratic_weighted_kappa | icc_a_1 | model_aggregate_human_mae | model_individual_human_mae |
|---|---|---|---|---|---|---|---|---|
| Vocabulary | 762 | 0.416010 | 0.593176 | 0.593176 | 0.501748 | 0.502077 | 0.372977 | 0.457250 |
| Grammar | 762 | 0.536745 | 0.488189 | 0.488189 | 0.513990 | 0.514318 | 0.447710 | 0.556102 |

`model_aggregate_human_mae` is the frozen RF error against the released aggregate target. `model_individual_human_mae` averages RF error against each raw rater separately and is the more direct comparison with human–human disagreement.

## Model error versus rater disagreement

| trait | n_samples | spearman_human_disagreement_vs_model_absolute_error | mean_model_error_when_raters_agree | mean_model_error_when_raters_disagree | top_10pct_model_error_with_rater_disagreement_rate |
|---|---|---|---|---|---|
| Vocabulary | 762 | 0.021540 | 0.373015 | 0.372922 | 0.402597 |
| Grammar | 762 | -0.156632 | 0.504370 | 0.393666 | 0.363636 |

## Controlled manual-audit sample

The text-free audit table contains 30 rows: five Vocabulary and five Grammar rows in each of low-score overprediction, high-score underprediction, and good-prediction categories. The private, git-ignored copy adds essay text for manual inspection. Rare extreme scores are stored separately as case studies and are not treated as stable subgroups.

- `docs/data/improvement_tables/controlled_error_audit_sample.csv`
- `data/04_intermediate_work/improvement_audit/controlled_error_audit_private.csv`
- `docs/data/improvement_tables/rare_extreme_case_studies.csv`

## Isolation guarantees

The raw-rater loader retained exactly 3812 allowlisted, privacy-eligible development rows. It retained 0 of 2571 forbidden official-test IDs. Raw scores are audit-only and are not model inputs.

## Human-machine comparison figures

The regenerated figures use the same 762 eligible validation essays and continuous, unrounded
Phase 7 predictions. Calibration marker size reflects the number of essays at each human-score
level; confidence intervals at rare extreme scores should be interpreted cautiously.

- `outputs/figures/human_machine_comparison/human_machine_score_distributions.png`
- `outputs/figures/human_machine_comparison/human_machine_calibration_by_score.png`
- `outputs/figures/human_machine_comparison/human_machine_bias_by_score.png`
- `outputs/figures/human_machine_comparison/human_machine_reliability_mae.png`

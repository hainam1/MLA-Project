# Methodology

The project predicts ELLIPSE Vocabulary and Grammar scores separately. The official training file
is split 80/20 into model-train and validation data with normalized exact duplicates kept together
and prompt proportions stratified using seed 42. Five-fold StratifiedGroupKFold inside model-train
uses prompt as the stratum and normalized-text hash as the group. The official test file is the
final held-out test and is not repartitioned. No stable writer ID exists, so same-writer grouping
cannot be guaranteed. Feature extraction is shared across partitions, and imputation and scaling
live inside scikit-learn pipelines fitted without validation/test rows.

Beginning with Phase 5, model development and evaluation include only rows whose frozen manifest
status is `not_flagged`. Flagged and unresolved rows remain in the manifest for auditability but do
not influence diagnostics, learned preprocessing, model fitting, thresholds, or metrics. This
leaves 3,050 model-train and 762 validation essays.

For each target, Ridge Regression supplies a regularized linear model and Random Forest Regression
supplies a nonlinear comparison. Per-target disagreement is their absolute prediction difference;
the essay-level review score is the maximum of the Vocabulary and Grammar disagreements. The
Phase 8 reference predictor is Random Forest for both targets under the already-presented lower
validation-MAE selection rule; the two model predictions are not averaged. An essay is a
large-error case when either RF prediction differs from its human score by at least 1.0 point.
Disagreement is neither calibrated confidence nor a probability of error. The Ridge/RF mean used
in Phase 5 remains a historical provisional baseline and is not the Phase 8 reference predictor.

Report MAE, RMSE, and R-squared for both models and targets. The primary review comparison is Large
Error Capture Rate at a 20% review budget against 1,000 uniform random selections of the same size;
10% and 30% are sensitivity budgets. Random-selection metrics are summarized by their mean and
2.5th-97.5th percentile empirical reference interval, which is not a bootstrap confidence
interval. Residual and subgroup error analysis is permitted only where reference scores exist.

Phase 5 baselines use the eligible model-train rows only. The mean baseline predicts the target's
train mean. The length-only condition fits fixed-config Ridge and Random Forest models using only
word count, sentence count, and mean sentence length; their mean supplies the provisional
length-only consensus, and their maximum target disagreement supplies the baseline review ranking.

Phase 6 tunes each of the four target/model pairs separately using the five frozen model-train
folds through `PredefinedSplit`. Ridge searches alpha values 0.1, 1, 10, 100, and 1000. Random
Forest searches the frozen combinations in `configs/phase6_training.yaml`; its estimator and
search both use one worker for reproducible aggregation. Selection minimizes cross-validated MAE.
The chosen pipeline is refitted on all 3,050 eligible model-train rows and generates predictions
for 762 eligible validation rows.
Task 6 does not calculate validation metrics or review-queue performance; those are deferred to
Task 7. Predictions remain continuous and are neither rounded nor clipped.

Task 7 evaluates the saved Phase 6 predictions on exactly those 762 eligible validation essays. It
reports MAE, RMSE, and R-squared separately for each model and target, verifies the Phase 5 mean and
length-only Ridge baselines from their text-free artifacts, and computes signed MAE improvement
relative to both baselines. A single point predictor is selected per target by lower validation MAE,
with Ridge as the deterministic tie-break; the two model predictions are not averaged. Residuals,
train-derived length-band errors, fixed score-band exploratory errors, and predicted-vs-human plots
are descriptive only. Task 7 does not fit or tune models, build a disagreement queue, or access the
official test.

Task 8 evaluates four validation-only review strategies at the same population, queue size, and RF
large-error labels: uniform random selection, shortest-first, raw Ridge prediction extremity, and
Ridge/RF disagreement. Ridge extremity is centered on the median Ridge predictions generated for
the 3,050 eligible model-train essays. All deterministic ties use ascending string essay ID. Model
QWK rounds predictions half-up to the nearest 0.5 and clips to the fixed 1.0-5.0 ELLIPSE grid only
for QWK; MAE and RMSE continue to use unmodified continuous predictions.

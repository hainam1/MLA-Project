# Model Improvement Protocol — Baseline v1 and Tail-Bias Study

## Frozen baseline v1

The Phase 6–7 artifacts are frozen as baseline v1. Random Forest is the selected point predictor
for both traits. Its eligible-validation MAE is **0.372977** for Vocabulary and **0.447710** for
Grammar. These 762 validation essays have already influenced model-family selection and must not be
reused to choose new features, objectives, weights, calibration methods, or hyperparameters.

The official test remains unopened. No improvement experiment may load an official-test feature,
text, target, or raw-rater row. Predictions remain continuous and unclipped.

## Development population and evaluation

All new model comparisons use only the 3,050 privacy-eligible model-train essays and their five
frozen CV folds. Score bands are low (1–2.5), middle (3–3.5), and high (4–5). Reports must include
overall MAE, macro band MAE, signed band bias, tolerance within 0.5 and 1.0 points, RMSE, R-squared,
calibration slope, and fold-level uncertainty.

## Predeclared acceptance rules

A challenger is acceptable only when all conditions hold against the frozen-parameter RF OOF
baseline for the same trait:

- overall MAE increases by no more than 0.005;
- macro band MAE improves by at least 10%;
- the maximum absolute low/high band bias falls by at least 20%;
- no score band with at least 20 essays worsens by more than 0.05 MAE;
- fold MAE improves in at least four of five frozen folds.

The machine–human comparison uses the aggregate ELLIPSE target. Human–human reliability is also
reported because aggregate-target MAE and individual-rater MAE answer different questions.

## Raw-rater isolation

The raw-rater source mixes essays from multiple partitions. The audit loader therefore requires a
development-ID allowlist, rejects any overlap with official-test IDs, retains only allowlisted rows,
and verifies that no forbidden ID reaches an output or metric. Raw scores are audit material only;
they are never model inputs.

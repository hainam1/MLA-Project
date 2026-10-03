# Evaluation Protocol Freeze

> Frozen after the Phase 8 primary validation evaluation on 2026-10-01. The observed validation
> result below is evidence, not a basis for modifying this protocol. No official-test predictions
> or labels were accessed when creating this freeze.

## Frozen artifacts and features

The four Phase 6 model artifacts are fixed by SHA-256:

| Model artifact | SHA-256 |
|---|---|
| `ridge_vocabulary.joblib` | `14591A1822FFA4FC7C9006A5ABD270928401721739BEA3F9FE5A76852780EF64` |
| `ridge_grammar.joblib` | `812885CAAB21DAC6508835C83DC91DE75B23D622577BA15A8E37E207E59B085F` |
| `random_forest_vocabulary.joblib` | `899E9283E2EB01B4DF6913EADD6CF8A4A823DF0298DDFE820D14BA5912FFE7BE` |
| `random_forest_grammar.joblib` | `BC285A202DE126247240982696CA94C16DBEE82BF15906D8E75EBDF4405A8F91` |

The frozen 14-feature schema, in order, is:

1. `word_count`
2. `sentence_count`
3. `mean_sentence_length`
4. `mtld`
5. `mattr`
6. `mean_word_frequency`
7. `mean_word_length`
8. `lexical_density`
9. `noun_diversity`
10. `detected_grammar_errors_per_100_words`
11. `detected_error_free_sentence_ratio`
12. `complex_sentence_ratio`
13. `estimated_clauses_per_sentence`
14. `subordinate_clause_ratio`

Demographic attributes and prompt are not model predictors.

## Frozen evaluation definitions

- Reference predictor for Vocabulary: Random Forest (`random_forest_vocabulary`).
- Reference predictor for Grammar: Random Forest (`random_forest_grammar`).
- For essay (i), the large-error indicator is
  \[
  L_i=\mathbf 1\left[\max\left(
  |\hat y^{RF}_{i,V}-y_{i,V}|,
  |\hat y^{RF}_{i,G}-y_{i,G}|
  \right)\ge 1.0\right].
  \]
- Primary review budget: 20%; sensitivity budgets: 10% and 30%.
- At budget (b) on a population of (N), every queue selects exactly
  (K_b=\lceil bN\rceil) essays.
- Random reference: 1,000 uniform draws without replacement, exactly (K_b) essays per draw,
  NumPy random seed 42. Percentile ranges are empirical random-selection reference intervals,
  not bootstrap confidence intervals.
- Shortest-first: rank recomputed `word_count` ascending.
- Ridge extremity: first compute the median of Ridge Vocabulary predictions and the median of
  Ridge Grammar predictions over the 3,050 eligible model-train essays. For validation essay (i),
  \[
  E_i=\max\left(
  |\hat y^{Ridge}_{i,V}-\operatorname{median}(\hat y^{Ridge}_{train,V})|,
  |\hat y^{Ridge}_{i,G}-\operatorname{median}(\hat y^{Ridge}_{train,G})|
  \right).
  \]
  Rank raw rubric-point distance descending; do not standardize the primary baseline.
- Ridge-RF disagreement:
  \[
  D_i=\max\left(
  |\hat y^{Ridge}_{i,V}-\hat y^{RF}_{i,V}|,
  |\hat y^{Ridge}_{i,G}-\hat y^{RF}_{i,G}|
  \right),
  \]
  ranked descending. Disagreement is a triage signal, not a probability of error or confidence.
- Deterministic ties: ascending `essay_id` interpreted as a string.

With selected indicator (S_i), total large errors (M=\sum_i L_i), and queue size (K):

\[
\text{Capture Rate}=\frac{\sum_i S_iL_i}{M},\qquad
\text{Precision}=\frac{\sum_i S_iL_i}{K},\qquad
\text{Lift}=\frac{\text{Precision}}{M/N}.
\]

Capture Rate and Lift are `NA` when (M=0).

For model QWK only, continuous predictions are rounded half-up to the nearest 0.5, then clipped
to `[1.0, 5.0]`, encoded on the fixed ordered levels
`1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0`, and evaluated using quadratic-weighted Cohen
kappa. MAE, RMSE, and R-squared use the original continuous predictions.

## Phase 8 validation evidence observed after protocol definition

The frozen primary validation population had (N=762), (K=153), and 69 large-error essays.

| Strategy | Selected | Captured | Capture Rate | Precision | Lift |
|---|---:|---:|---:|---:|---:|
| Random, mean of 1,000 draws | 153 | 13.946 | 0.202116 | 0.091150 | 1.006617 |
| Shortest-first | 153 | 15 | 0.217391 | 0.098039 | 1.082694 |
| Ridge extremity | 153 | 10 | 0.144928 | 0.065359 | 0.721796 |
| Ridge-RF disagreement | 153 | 15 | 0.217391 | 0.098039 | 1.082694 |

Ridge-RF disagreement tied shortest-first for the highest deterministic primary validation Capture
Rate. This observation does not change any definition above.

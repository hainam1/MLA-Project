# Task 6 — Four-Model Training with the Frozen 14 Features

> **Prepared:** 2026-09-24  
> **Status:** Training run completed; evaluation is intentionally deferred to Task 7  
> **Official test:** Locked and not loaded

## Training contract

The official Phase 6 entry point is `scripts/phase6_train_models.py`. It reads only:

- `data/05_model_features/development_features_with_targets.csv`;
- `data/02_split_manifest/essay_split_manifest.csv`;
- the Ridge, Random Forest, and Phase 6 YAML configurations.

It trains four target/model pairs: Ridge Vocabulary, Ridge Grammar, Random Forest Vocabulary, and
Random Forest Grammar. The input matrix is exactly the 14 ordered features in `FEATURE_NAMES`.
Essay ID, split metadata, prompt, privacy status, demographics, and human scores are never input
features.

The task description uses a few alternate feature labels. The repository schema is authoritative:

| Task 6 label | Repository column |
|---|---|
| `mean_zipf_frequency` | `mean_word_frequency` |
| `noun_lemma_diversity` | `noun_diversity` |
| `grammar_issues_per_100_words` | `detected_grammar_errors_per_100_words` |
| `sentence_without_detected_grammar_issue_ratio` | `detected_error_free_sentence_ratio` |

The extractor and formulas are not changed for Task 6.

## Mandatory guards

Before fitting, the pipeline verifies:

- development and manifest IDs are unique and their source/split/fold metadata agree;
- no official-test row is present;
- only `privacy_review_status=not_flagged` rows are eligible;
- the exact frozen 14-feature schema is used;
- all features and targets are numeric, complete, and finite;
- Vocabulary and Grammar targets are within 1.0–5.0;
- model-train has fixed folds 0–4 and validation has no CV fold;
- model-train and validation IDs are disjoint.

The real-data preflight passed with 3,050 model-train rows, 762 validation rows, and CV fold sizes
609, 610, 610, 611, and 610. The development and manifest hashes match the Phase 3–4 audit files.

## Model selection

Each target/model pair is tuned independently with `PredefinedSplit` over the five frozen folds.
All learned preprocessing remains inside its scikit-learn pipeline. The selection metric is MAE.
Task 6 records only CV results; it does not compute validation metrics or a review queue.

- Ridge alpha: 0.1, 1, 10, 100, 1000.
- Random Forest: 300 trees; depth 10 or `None`; minimum leaf size 2 or 5; feature sampling
  `sqrt` or 1.0.
- Random seed: 42.
- Search and Random Forest workers: 1 for reproducible aggregation.

Predictions remain continuous and are not rounded or clipped. Validation target values are not
copied into the prediction file.

The completed Task 6 run selected these configurations from model-train CV. The values below are
CV selection evidence only; they are not validation results and are not used to declare a winning
model:

| Model | Target | Best parameters | Mean CV MAE | SD CV MAE |
|---|---|---|---:|---:|
| Ridge | Vocabulary | `alpha=100` | 0.372441 | 0.006839 |
| Ridge | Grammar | `alpha=0.1` | 0.463645 | 0.020917 |
| Random Forest | Vocabulary | `300 trees, depth=10, leaf=2, max_features=sqrt` | 0.372616 | 0.008983 |
| Random Forest | Grammar | `300 trees, depth=10, leaf=5, max_features=sqrt` | 0.457694 | 0.022319 |

## Commands

Validate the data contract without fitting:

```powershell
uv run python scripts/phase6_train_models.py --preflight-only
```

After reviewing `configs/phase6_training.yaml`, run model selection and export validation
predictions:

```powershell
uv run python scripts/phase6_train_models.py
```

The command refuses to overwrite an existing artifact manifest unless `--overwrite` is supplied
explicitly.

## Saved evidence

The default output directory is `outputs/phase6/`. A successful run saves:

- four `.joblib` model pipelines;
- `feature_schema.json` and `selected_parameters.json`;
- `cv_results.csv` with fold-level, mean/std MAE and best-parameter candidates;
- `validation_predictions.csv` with only `essay_id` and the four model predictions;
- `training_summary.json` with row counts, privacy counts, hashes, versions, protocol flags, and
  explicit metadata for each of the four model/target pairs;
- `artifact_manifest.json` with SHA-256 hashes for every saved artifact.

`load_model_artifacts()` verifies every hash and the exact feature schema before returning models
for inference. Each model metadata record contains its family, target, ordered 14 features,
eligible fit-row count, fixed `PredefinedSplit` protocol, fold counts, best parameters, CV MAE
summary, Python/package versions, and code/config provenance. Code provenance includes the Git
commit/dirty-worktree state plus SHA-256 IDs for the training source files; configuration
provenance includes SHA-256 IDs for all three YAML files.

The regression suite also reloads every saved model and compares its validation predictions with
the text-free prediction file. A target-isolation test changes Vocabulary or Grammar independently
and verifies that only the corresponding target model changes.

## Task 6 boundary

Task 6 does not compare models, calculate validation performance, create a disagreement queue, run
error analysis, perform ablations, or open the official test. Those actions belong to Task 7 and
later. Official-test features and labels remain unavailable to this command.

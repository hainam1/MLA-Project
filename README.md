# Prioritizing Teacher Review of English Learner Writing

This project studies vocabulary and grammar score prediction for English learner essays using
interpretable linguistic features. It compares Ridge Regression with Random Forest Regression and
uses their absolute prediction difference to prioritize essays for teacher review.

The system is educational decision support. It does not replace a teacher, assign consequential
grades, or interpret model disagreement as a confidence score or probability of error.

## Current status

Phases 1â€“5 are complete: the research protocol, dataset audit, frozen leakage-safe split, exact
14-feature extractor, feature audit, and validation baselines are documented and reproducible.
Task 6 is now complete: four fitted models, fixed-fold CV results, and 762 text-free validation
predictions were exported using only 3,050 privacy-eligible model-train rows. Each artifact set
includes explicit per-model metadata, code/config provenance, integrity hashes, and reload-prediction
regression checks. Task 7 validation evaluation is also complete: MAE, RMSE, R-squared, baseline
comparisons, point-predictor selection, residual summaries, and text-free diagnostic outputs are
recorded for the same 762 eligible validation essays. Disagreement review and official-test
evaluation remain locked for later tasks.

## Dataset

The project uses the ELLIPSE Corpus (Crossley et al., 2023), licensed under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Original CSV files and the
official rubric belong in `data/01_original_source/` and are treated as read-only. See
[data/README.md](data/README.md) and [docs/dataset.md](docs/dataset.md) for provenance, placement,
schema, and license notes.

Input is an essay in `full_text` with `text_id_kaggle` as its ID. Training additionally uses the
human-rated `Vocabulary` and `Grammar` columns. The frozen Phase 1 output contract includes two
model estimates and their mean consensus estimate per target, per-target disagreement, and one
essay-level review score equal to the maximum target disagreement. The inference API exposes this
full contract while keeping teacher review authority explicit.

## Features and models

The shared extractor used for every split and for new essays has four feature groups:

- Length (3): word count, sentence count, and mean sentence length.
- Vocabulary (6): MTLD, MATTR, mean Zipf word frequency, mean word length, lexical density, and
  noun diversity.
- Detected grammar issues (2): grammar matches per 100 words and the ratio of sentences without a
  detected grammar match. Matches are not proven learner errors.
- Syntax (3): complex-sentence ratio, estimated clauses per sentence, and subordinate-clause ratio.

Definitions and edge-case rules are frozen in
[docs/feature_specification.md](docs/feature_specification.md). Reproduce the local tables with
`uv run python scripts/phase4_extract_features.py`.

Four target/model pairs are fitted: Ridge Vocabulary, Ridge Grammar, Random Forest Vocabulary, and
Random Forest Grammar. Imputation and Ridge scaling are inside scikit-learn pipelines so learned
preprocessing is fitted only on training rows.

## Environment

Python 3.12 is the supported baseline. `pyproject.toml` is the canonical dependency declaration;
`uv.lock` pins the environment. The requirements files are compatibility entry points only.

```powershell
uv sync --locked --extra dev --extra analysis
uv run --extra analysis python scripts/phase5_feature_audit_and_baselines.py
uv run python scripts/phase6_train_models.py --preflight-only
uv run pytest -q
```

The Java runtime required by `language-tool-python` must be installed before grammar features are
extracted. The locked environment installs the pinned spaCy model, but never downloads ELLIPSE.

## Dataset placement

Place the untouched source files at the paths declared in `configs/paths.yaml`:

```text
data/01_original_source/official_corpus/ELLIPSE_Final_github_train.csv
data/01_original_source/official_corpus/ELLIPSE_Final_github_test.csv
data/01_original_source/rater_scores/ellipsis_raw_rater_scores_anon_all_essay.csv
data/01_original_source/documentation/ELL_Rubrics.docx
```

The repository already contains these local files; do not download or overwrite them. Dataset
content is ignored by Git while provenance documentation and `.gitkeep` files remain trackable.

## Intended commands

Phase 6 provides a guarded command-line training entry point. Run the preflight first, then run the
CV search and validation fit only after the configuration is reviewed:

```powershell
uv run python scripts/phase6_train_models.py --preflight-only
uv run python scripts/phase6_train_models.py
```

The command reads only the development feature table and frozen manifest. It rejects official-test
rows, applies the privacy gate, and writes four models plus text-free evidence to `outputs/phase6/`.

Package APIs remain available for individual stages:

```text
validate data       mla_project.data.load_data.load_ellipse
extract features    mla_project.features.extract_features
prepare/train/save  mla_project.pipelines.training_pipeline
evaluate            mla_project.evaluation.regression_metrics.regression_metrics
predict one essay   mla_project.pipelines.inference_pipeline.predict_essay
```

## Repository structure

```text
configs/                          Paths, feature settings, and model hyperparameters
data/01_original_source/         Untouched corpus, rater scores, and official documentation
data/02_split_manifest/          Frozen train/validation/test ID manifest
data/03_clean_ready_to_use/      Clean essay tables for EDA, training, and evaluation
data/04_intermediate_work/       Temporary checkpoints and private audit material
data/05_model_features/          Final numeric feature tables
docs/                             Dataset, method, governance, and planning documentation
notebooks/                        Supporting exploration; never production logic
outputs/                          Ignored figures, metrics, models, predictions, and tables
report/                           Final-report source and ignored exported binaries
src/mla_project/                  Installable project package
tests/                            Fast unit and smoke tests
```

Detailed methodology is in [docs/methodology.md](docs/methodology.md), and limitations and use
constraints are in [docs/responsible_use.md](docs/responsible_use.md).
Verified local dataset counts, schemas, target distributions, duplicate checks, privacy findings,
and the allowed-column catalog are in [docs/data_inventory.md](docs/data_inventory.md).
The frozen model-train/validation/test manifest, CV folds, and leakage-control rules are documented
in [docs/split_and_leakage_protocol.md](docs/split_and_leakage_protocol.md).
The Phase 4 implementation, verified row counts, QA results, and generated-table hashes are in
[docs/phase4_feature_extraction_report.md](docs/phase4_feature_extraction_report.md).
The Phase 5 feature audit, mean/length-only prediction baselines, and random-review baseline are in
[docs/phase5_feature_audit_and_baselines.md](docs/phase5_feature_audit_and_baselines.md).
The Phase 6 training contract, search space, artifacts, and preflight evidence are in
[docs/phase6_training_readiness.md](docs/phase6_training_readiness.md).
The train-only experiment with nine new rubric-oriented features and its acceptance results are in
[docs/feature_v2_train_only_results.md](docs/feature_v2_train_only_results.md).

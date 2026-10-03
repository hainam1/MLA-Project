# Project evidence mapping

Status is based on repository evidence, not planned work.

| Criterion | Current design | Evidence | Status |
|---|---|---|---|
| Task | Essay to Vocabulary/Grammar estimates and review prioritization | `README.md`, `docs/project_scope.md` | Implemented foundation |
| Dataset | ELLIPSE provenance, license, rubric, and checksums | `data/README.md`, `data/01_original_source/documentation/SOURCE.md`, `docs/dataset.md` | Verified locally |
| Leakage control | Official test frozen; prompt-stratified 80/20 development split; exact-text grouping; fixed five-fold CV; preprocessing inside fitted pipelines | `docs/split_and_leakage_protocol.md`, `data/02_split_manifest/essay_split_manifest.csv`, `src/mla_project/data`, tests | Phase 3 manifest and audit complete; unit tested |
| Features | Length, vocabulary, detected grammar issues, syntax | `configs/features.yaml`, `src/mla_project/features` | Extracted for all 6,482 rows; QA complete |
| Models | Ridge and Random Forest for two targets | `configs/phase6_training.yaml`, `src/mla_project/pipelines/training_pipeline.py` | Four-model fixed-fold CV training completed; Task 6 artifacts saved |
| Review signal | Maximum per-target absolute disagreement as one essay-level queue score | `docs/phase1_problem_definition.md`, `src/mla_project/review` | Reserved for Task 7; not computed by Task 6 |
| Evaluation | MAE/RMSE/R-squared plus fixed-budget capture, precision, lift and random baseline | `scripts/phase7_evaluate_regression_models.py`, `docs/phase7_regression_evaluation.md`, `docs/data/phase7_tables/` | Task 7 regression evaluation complete; disagreement/review queue remains reserved for a later task |
| Inference | Four estimates, two disagreements, transparent priority rule | `src/mla_project/pipelines/inference_pipeline.py`, `tests/test_inference.py` | Output contract tested |
| Responsible use | Teacher support only; limitations documented | `docs/responsible_use.md` | Documented |
| Reproducibility | Locked dependencies, fixed folds, input/config hashes, model manifests, tests | repository root, `scripts/phase6_train_models.py` | Train preflight and artifact integrity checks implemented |

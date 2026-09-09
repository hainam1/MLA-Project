# Project Handoff

## Active contract

The repository targets one supervised task: English sentence CEFR classification from A1 to C1.
The required comparison is K-Nearest Neighbors versus Decision Tree on a shared, leakage-safe
split and the same linguistic feature set. Frozen DeBERTa embeddings are an optional feature
extension and are not a required model family.

## Current assets worth retaining

- UniversalCEFR sentence provenance and license notes.
- Sentence cleaning, feature extraction, and grouped-split logic.
- Twenty-five existing linguistic/readability features.
- Existing short/complex-sentence hypotheses, retained only as questions to retest.

## Important technical debt

- Existing benchmark reports and runtime metadata came from different experiment configurations.
  They are historical evidence only; Phase 6 must generate one authoritative run.
- Three sentence features depend on an auxiliary CEFR word list. Keep the resource clearly
  separated and run an ablation without these features.
- Frozen DeBERTa/PCA experiments are described in reports but are not yet represented as a clean,
  reproducible source module. PCA must be fitted on training data only.
- The old split script mixed five unrelated tasks. It must be reduced to reusable sentence-only
  functions with saved split manifests.
- Hyperparameter search, final experiment locking, paired comparison, and full error-analysis
  outputs still need to be completed for KNN and Decision Tree.

## Source of truth

- Research design and exit gates: `final-project-plan.md`
- Action checklist: `TASKS.md`
- Dataset/license record: `reports/00_dataset_licenses.md`
- Task definition: `reports/01_task_formulation.md`

## Results rule

Historical result tables were removed from the active report set to prevent accidental reuse. Only
populate `reports/model_comparison.md`, and regenerate every final figure, from the frozen
KNN-versus-Decision-Tree run.

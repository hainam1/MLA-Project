# Project Progress

## 2026-09-08 — Scope reset

- Frozen one task: English sentence CEFR classification (A1-C1).
- Selected required comparison: K-Nearest Neighbors versus Decision Tree, both taught in class.
- Defined frozen DeBERTa embeddings as a feature extension, not automatically a third family.
- Removed translation, word-classifier, lexical retrieval, generation, rewriting, quality-auditor,
  API, release, and their datasets/reports from the active repository.
- Replaced the broad CapyVocab plan with a phase-gated research plan mapped to the assessment rubric.
- Preserved sentence data provenance, sentence features, grouped splitting logic, historical sentence
  results, and the optional auxiliary lexical resource.
- Updated the plan, task checklist, configuration, training candidates, and defense notes for the
  official KNN-versus-Decision-Tree comparison.
- Next gate: regenerate the data audit and split manifest before any hyperparameter tuning.

## 2026-09-08 — Phase 0 completed (Scope & Rubric locked)

- Finalized task scope: English sentence CEFR level classification (A1-C1).
- Locked the two official model families: K-Nearest Neighbors (distance/instance-based) and Decision Tree (tree-based), with Majority Classifier as sanity baseline.
- Verified all deliverables and technical contracts across `final-project-plan.md`, `TASKS.md`, `configs/config.yaml`, `reports/01_task_formulation.md`, `docs/oral_defense.md`, and `docs/llm_disclosure.md`.
- Completed formal rubric alignment matrix in `docs/rubric_mapping.md` covering all 10 course criteria with 100% evidence mapping.
- Phase 0 exit gate passed: Project can be fully explained in 1 minute with correct scope and exact 2 classifiers. Ready for Phase 1.

## 2026-09-08 — Phase 1 completed (Dataset, License, Cleaning, Audit & EDA)

- Downloaded primary sentence datasets (`cefr_sp_en` rev `b78901348bda9f5a823cd3da1f3fcb2dcc6c5725`, `readme_en` rev `88ce5b3736bdb666b1f64f738451676b12028a33`) and auxiliary word survey (Zenodo 12501).
- Computed and recorded SHA-256 checksums, access timestamps, and licenses in `reports/00_dataset_licenses.md` and `data/raw/*/SOURCE.md`.
- Ran sentence cleaning and generated `data/processed/data_audit.json`:
  - 10,004 (`cefr_sp_en`) + 2,822 (`readme_en`) = 12,826 raw rows.
  - Excluded: 301 C2 rows, 2 within-source duplicates, 2 conflicting-label rows (group "If you saw the first one...").
  - Retained: exactly 12,521 sentences across A1-C1 (reconciled 100% back to raw data).
- Cleaned auxiliary lexicon to 5,697 entries (`data/processed/cefr_wordlist_clean.csv`).
- Generated quantitative EDA figures in `reports/figures/` and metrics in `reports/eda_summary.json`:
  - Class distribution (A1: 2.44%, A2: 15.52%, B1: 31.36%, B2: 33.74%, C1: 16.94%).
  - Distribution by source (`cefr_sp_en` vs `readme_en`).
  - Sentence length monotonic increase (A1 mean 6.17 words $\to$ C1 mean 19.24 words).
  - Lexical rarity trends (Zipf frequency declines, rare word ratio quadruples from 5.6% to 20.1%).
- Populated `docs/data_card.md` with complete, verified real numbers.
- Phase 1 exit gate passed: `data_audit.json` reconciles 100% to raw data. Ready for Phase 2.



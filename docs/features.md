# Phase 4 Feature Extractor

`mla_project.features.extract_features(essay)` is the public single-essay API. It returns exactly
14 ordered floating-point values. `FeatureExtractor` holds the reusable spaCy and LanguageTool
resources used by batch extraction, training, validation, final test, and new-essay inference.

The frozen definitions, edge-case rules, and known limitations are in
[`feature_specification.md`](feature_specification.md). The machine-readable order and tool settings
are in [`configs/features.yaml`](../configs/features.yaml).

## Reproduce the Phase 4 tables

1. Install the locked environment and the parser model:
   `uv sync --locked --extra dev --extra analysis`; the locked dependency graph installs
   `en_core_web_sm`.
2. Run `uv run python scripts/phase4_extract_features.py`.
3. The script uses a local LanguageTool 6.6 server, resumes from a text-free numeric checkpoint,
   validates the ID joins, and writes the outputs listed below.

| Output | Contents | Target policy |
|---|---|---|
| `data/05_model_features/essay_features.csv` | ID, source/split metadata, exactly 14 features; 6,482 rows | No targets |
| `data/05_model_features/development_features_with_targets.csv` | Model-train + validation features joined to Vocabulary and Grammar by ID | Development targets only |
| `data/05_model_features/official_test_features.csv` | Frozen official-test IDs and features | No test targets loaded |
| `docs/data/phase4_tables/feature_summary_by_split.csv` | Aggregate feature QA by split | No targets |
| `docs/data/phase4_tables/manual_feature_review.csv` | 25-row edge/random review checklist without text | No targets |
| `docs/data/phase4_tables/phase4_audit_summary.json` | Row counts, integrity checks, versions, and output hashes | No targets |

The raw essays, privacy flags, prompt, demographics, source-provided feature columns, and human
scores other than the two development targets are never written into the model feature matrix.
Official-test labels remain isolated for the later one-time final evaluation.

Feature extraction is deterministic and does not learn corpus statistics, so the same frozen
extractor may transform every split. Any later imputation, scaling, feature selection, or model
fitting must still follow the train-only rules in
[`split_and_leakage_protocol.md`](split_and_leakage_protocol.md).

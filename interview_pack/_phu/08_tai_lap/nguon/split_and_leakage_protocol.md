# Nguồn: docs/split_and_leakage_protocol.md
SHA256 toàn file: dd7b40a1d0d1a4161bd958bec7a2efa30ba3ed01bb7078379a73ac795ddc2369

Trích chọn metadata/số liệu; không chứa bài luận.

1: # Phase 3 Data Split and Leakage-Control Protocol
2: 
3: > **Frozen on:** 2026-09-23  
4: > **Status:** Split design and leakage audit passed.  
5: > **Privacy gate update:** Phase 5 excludes every row not marked `not_flagged`; development baseline
6: > fitting is permitted under this rule. Official test remains frozen.
7: 
8: ## Outcome
9: 
10: The official ELLIPSE test file remains unchanged as the final held-out test. The 3,911 rows in the
11: official training file were divided into 3,128 model-train rows and 783 validation rows. Every
12: model-train row also has one of five fixed cross-validation holdout folds.
13: 
14: | Partition | Rows | Purpose | May influence feature/hyperparameter/threshold decisions? |
15: |---|---:|---|---|
16: | Model train | 3,128 | Fit models and learned preprocessing; run five-fold CV | Yes, through fold-safe CV |
17: | Validation | 783 | Select frozen feature condition, model configuration, and any operational threshold | Yes, after model-train tuning |
18: | Official test | 2,571 | One final confirmatory evaluation after all choices are frozen | No |
19: 
20: The frozen manifest is `data/02_split_manifest/essay_split_manifest.csv` (nguồn gốc trong repository: `../data/02_split_manifest/essay_split_manifest.csv`). It is generated
21: by `scripts/phase3_build_split.py` (nguồn gốc trong repository: `../scripts/phase3_build_split.py`); rerunning the script with the
22: same local source snapshot and seed must reproduce the same manifest hash recorded in
23: `split_audit_summary.json` (nguồn gốc trong repository: `data/phase3_tables/split_audit_summary.json`).
24: 
25: Frozen manifest SHA-256:
26: `A998E6ED7EDD1361DE31739F4E3474A248A3EDA7F705EE8E2A8EBA36D396CC96`.
27: 
28: ## Split topology
29: 
30: ```mermaid
31: flowchart TD
32:     OT[Official train<br/>3,911 rows]
33:     MT[Model train<br/>3,128 rows]
34:     VA[Validation<br/>783 rows]
35:     CV[Five fixed CV holdout folds<br/>625 or 626 rows each]
36:     TE[Official test<br/>2,571 rows<br/>never repartitioned]
37:     OT -->|grouped exact-text hash + prompt stratification<br/>seed 42| MT
38:     OT -->|20%| VA
39:     MT -->|StratifiedGroupKFold<br/>prompt + text hash, seed 42| CV
40:     TE --> FINAL[One final evaluation only]
41: ```
42: 
43: The raw individual-rater file is not part of the modeling split. It is used only to attach the
44: binary privacy-review status already identified in Phase 2.
45: 
46: ## Reproducible split procedure
47: 
48: 1. Load the official train columns `text_id_kaggle`, `full_text`, `prompt`, `Vocabulary`,
49:    `Grammar`, and `set`.
50: 2. Load the official test file **without any score columns**. The Phase 3 script reads only

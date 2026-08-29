# CapyVocab ML — Task Status

Updated: 2026-08-28

## Completed

- [x] Collect, license-review and clean Model 1/2/3 datasets.
- [x] Restrict primary CEFR scope to A1–C1.
- [x] Build shared Model 2a/2b feature package in `src/features/`.
- [x] Remove Model 2a train-serving-only features.
- [x] Collapse Model 2a to unique words and group split by `word`.
- [x] Rebuild feature tables and all 70/15/15 splits.
- [x] Retrain and evaluate Model 2a and Model 2b.
- [x] Fix Translator baseline checkpoint selection.
- [x] Use seeded random Translator evaluation; support full evaluation.
- [x] Add real unit/integration tests.
- [x] Integrate Translator → CEFR classifier MVP.
- [x] Create word-conditioned Model 3a pairs.
- [x] Limit Model 3b dataset to simplification/preserve.
- [x] Add truthful configuration, runtime GPU validation and artifact manifest.
- [x] Synchronize README and handoff documentation.
- [x] Calibrate Model 2a/2b probabilities and add `needs_review` thresholds.
- [x] Select FLAN-T5-small as the CPU-compatible Model 3a baseline.
- [x] Fine-tune and evaluate Model 3a on controlled seeded samples.
- [x] Measure lexical satisfaction, CEFR alignment, BLEU and ROUGE-L.
- [x] Add Model 3a inference service and integrate it after Model 2a.
- [x] Train Model 3b simplification/preserve baseline on `model3b_rewrite_*`.
- [x] Measure SARI, semantic similarity, target readability drift and CEFR alignment.
- [x] Add Model 3b inference service after Model 2b.
- [x] Reject `upgrade` because no bidirectional training data exists.
- [x] Build a real held-out Model 3a/3b failure-candidate review queue.
- [x] Add stable candidate IDs and a human review CLI without synthetic labels.
- [x] Human-review at least 100 candidates, including 50 confirmed failures.
- [x] Train Model 4 (Second Pair of Eyes Meta-Classifier) and evaluate 5-fold CV.
- [x] Fine-tune Model 1 (Translator) via LoRA/PEFT on full dataset and evaluate.
- [x] Add FastAPI adapter and structured error handling.
- [x] Build reproducible source/model bundles and publish source checksums on tags.

## Pending — Final Polish and Release

- [ ] Add a user-facing UI adapter.
- [ ] Publish non-commercial model weights only to an approved restricted store.
- [ ] Replace or relicense non-commercial corpora before commercial deployment.

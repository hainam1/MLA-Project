# CapyVocab ML — Engineering Handoff

Updated: 2026-08-28 (v0.3 semantics-first lexical pipeline)

## Active Serving Contract

- Input is one Vietnamese vocabulary item or lexical phrase, with at most three tokens.
- `target_level` is required and must be A1, A2, B1, B2, or C1.
- Serving selects a semantically expanded English candidate, verifies its word CEFR, and returns a complete example sentence verified at the requested CEFR.
- Complete Vietnamese sentences are rejected. Model 3b remains a research artefact but is not served.
- Candidate selection is semantics-first: AVDict bilingual senses and multilingual E5 establish a semantic/POS candidate set before CEFR is visible.
- Marian and WordNet generate candidates only; every model candidate must pass bilingual validation. Local English WordNet never provides CEFR labels.
- Exact CEFR lookup is keyed by lemma+POS. Model 2a estimates never set `target_match: true`; unavailable requested levels return `no_exact_level_match` without semantic drift.

## Hardware & Runtime Environment

- **Target GPU**: NVIDIA GeForce RTX 5060 Laptop GPU (Blackwell architecture `sm_120`, 8,151 MiB VRAM).
- **Driver & CUDA**: NVIDIA Driver 596.36 (CUDA 13.2 runtime compatibility).
- **PyTorch Stack**: `torch==2.11.0+cu128`, `torchvision==0.26.0+cu128`, `torchaudio==2.11.0+cu128` (native `sm_120` support via CUDA 12.8 wheels).
- **Hardware Performance**: Matmul $8192 \times 8192$ float32 benchmark achieves 11.39 TFLOPS on CUDA (vs 0.20 TFLOPS on CPU, **~57x speedup**).
- **Environment Integrity**:
  - `python -m src._env_check` passes with `cuda_usable: True` and zero fallback warnings.
  - Windows OpenMP DLL conflict resolved by importing PyTorch before C++ NLP libraries (`import torch` in `tests/conftest.py`, `src/features/__init__.py`, and `src/pipeline/predict_cefr.py`).
  - Windows console Unicode handling configured via `sys.stdout.reconfigure(encoding="utf-8")` across training entrypoints.
- **Test Suite**: 49/49 pytest test suites passing in 17.56s.

## Current Contract

- CEFR scope: A1, A2, B1, B2, C1. C2 is future work.
- Input router: at most three whitespace tokens without terminal punctuation is `word_mode`; otherwise `sentence_mode`.
- Production MVP: Vietnamese vocabulary + required CEFR target → MarianMT candidates → WordNet semantic expansion → verified word selection → verified example sentence.
- Model 1, Model 3a, and Model 3b checkpoints are local. Model 4 is not implemented.
- A 33-row held-out failure-candidate queue exists, but zero rows are human-reviewed; Model 4 training is intentionally blocked by the readiness policy.
- FastAPI, CI and reproducible release tooling are implemented. No external model artefact has been uploaded and no commercial release is permitted.
- Non-commercial datasets are present; commercial deployment is not cleared.

## Important Implementation Decisions

1. `src/features/` is the only feature implementation for Model 2a/2b.
2. Model 2a excludes POS and dataset-only Google N-gram features. It contains one sample per spelling and is group-split by `word`.
3. Model 2b training data is rebuilt by the same extractor used at inference.
4. Translator baseline is saved to `checkpoint-best` before optimizer updates. Evaluation samples are random with seed 42; `--eval_samples 0` means full split.
5. SentencePiece assets are staged into an ASCII temporary path on Windows when the repository path contains Unicode. The 287 MB model is not copied.
6. Model 3a data schema is `target_word,target_level,prompt,target_sentence`.
7. Model 3b is limited to `simplify` and `preserve`; it does not claim sentence upgrading from ASSET.
8. Model 3a uses FLAN-T5-small. Serving first generates naturally, retries with an explicit exact-form instruction, then uses a local decoder-prefix fallback. This avoids `trust_remote_code=True` after constrained beam search moved out of Transformers core.
9. Model 3b uses FLAN-T5-small and rejects targets above the predicted source level. Sentence-mode defaults to one CEFR level lower; A1 defaults to preserve. Unchanged simplification output is returned with an explicit warning.
10. Model 4 candidates use stable SHA-256-derived IDs. Automatic reasons only prioritize review; they never count as human labels. Training requires at least 100 reviewed rows and 50 human-confirmed failures.
11. `/health/live` never loads models; `/health/ready` checks local artefact presence. `/v1/process` loads the pipeline lazily and returns structured errors with request IDs.
12. CI runs tests marked `not integration` on clean clones. Local/full integration tests require the ignored datasets and approximately 0.94 GB of model artefacts.
13. Tagged releases publish a checksummed source-only GitHub Release. A full local model bundle requires explicit `--allow-noncommercial` acknowledgement.
14. **Technical Warning — Checkpoint Selection Gate Fragility**: The current checkpoint selection gate in `src/models/example_generator/train.py` and `src/models/sentence_rewriter/train.py` relies on comparing a single composite validation score (`rouge_l_f1 + 0.25 * lexical_constraint` for Model 3a; `sari + 20 * semantic_tfidf_cosine` for Model 3b) against the raw pre-trained baseline (`google/flan-t5-small`) without any safety margin.
    - *Incident Log (2026-08-28)*: In Model 3a, the raw untrained model achieves an artificially high lexical constraint score (0.778) simply by echoing the input prompt verbatim, yielding a high baseline score of 0.3340. On GPU, floating-point reduction order nuances in CUDA cu128 yielded validation scores of 0.3042–0.3187 across epochs 1–3, causing the gate to reject all fine-tuned epochs (`selected = False`) and silently fall back to the raw untrained model. This produced misleading test metrics (`SacreBLEU = 0.00`, `CEFR exact = 24.20%` from single-word echoes) without an explicit warning.
    - *Future Improvement Recommendation*: Add an explicit safety margin/adjusted baseline for prompt-echoing models, or log a prominent warning whenever the system falls back to the un-finetuned raw base checkpoint to distinguish between "suboptimal training" and "untrained raw model fallback".

## Latest Reproducible Metrics

### Model 1: Translator (MarianMT VI $\to$ EN)
* **Execution Device**: CUDA (`GeForce RTX 5060 Laptop GPU`).
* **Training Time**: 185.88s total (~3.10 min for 3 epochs + 5 eval passes), averaging **31.6s/epoch** on GPU (vs ~210s/epoch CPU, **~6.6x training speedup**).
* **Peak GPU VRAM**: 3,750.41 MiB / 8,151 MiB (~46% capacity, zero OOM).
* **Training Loss Progression**: Epoch 1: 4.4858 | Epoch 2: 3.7969 | Epoch 3: 3.5986.
* **Evaluation Metrics (1,000 Test Samples)**:
  * Baseline Pretrained: SacreBLEU = **31.89** | ChrF++ = **53.86**
  * Validation SacreBLEU: Baseline = **33.75** | Ep 1 = 31.54 | Ep 2 = 30.15 | Ep 3 = 29.71
  * Best Checkpoint: `Epoch 0 (Base Pretrained)` retained in `src/models/translator/checkpoint-best/` (286.8 MB safetensors) by strict anti-forgetting gate.

### Model 2a & Model 2b: CEFR Classifiers

| Model | Split policy | Accuracy | Macro F1 |
|---|---|---:|---:|
| Model 2a Logistic Regression | unseen `word` groups | 0.3608 | 0.3665 |
| Model 2b Random Forest Tuned | unseen near-duplicate clusters | 0.5429 | 0.5260 |

Temperature scaling preserves these predictions. Model 2a uses a 0.42 review threshold; Model 2b uses 0.62. Inputs below the applicable threshold return `needs_review: true`. On test data, accepted predictions reach 44.44% accuracy for Model 2a and 64.64% for Model 2b, at 20.00% and 27.12% coverage respectively.

### Model 3a: Example Generator (FLAN-T5-small)
Fine-tuned for one epoch on a seeded 10,000-row subset and evaluated on 500 seeded held-out test rows. Unconstrained test generation reached 65.00% exact lexical satisfaction, SacreBLEU 1.43, ROUGE-L F1 0.1765, CEFR exact alignment 35.80%, and CEFR within-one-level alignment 81.80%. These are controlled baseline metrics, not full-split metrics.

### Model 3b: Sentence Rewriter (FLAN-T5-small)
* **Execution Device**: CUDA (`GeForce RTX 5060 Laptop GPU`).
* **Training Time**: 184.28s total (~3.07 min for 1 epoch + validation + test evaluation) on GPU (vs 1281.97s (~21.37 min) CPU, **~7.0x training speedup**).
* **Peak GPU VRAM**: 3,063.0 MiB / 8,151 MiB (~37% capacity, zero OOM).
* **Training Loss**: 1.0511.
* **Selection Score (Validation)**: 56.300 (SARI 37.89 + 20 * TF-IDF cosine 0.9205 > baseline 48.038, `selected = True`, `best_epoch = 1`).
* **Test Evaluation (500 seeded tasks)**: SARI 36.29, best-reference ROUGE-L F1 0.8008, semantic TF-IDF cosine 0.9228, target-FKGL MAE 3.25, direction success 56.40%, strict simplification success 48.51%, preserve success 72.56%, CEFR exact alignment 20.24%, within-one alignment 57.09%.

## Quality Failure Review & Model 4 Queue

* **Total Candidates In Queue**: 33
* **Review Status**: 33 reviewed (100% completed of existing queue), 0 pending.
* **Human Confirmed Failures**: 18 confirmed failures, 15 acceptable.
* **Model 4 Gate Status**: `model4_training_ready: false` (Progress: 33/100 reviewed, 18/50 confirmed failures required by policy).

## Dataset Inventory

- Model 1: 132,589 cleaned VI–EN pairs.
- Model 2a: 5,116 unique context-free words, six serving-safe features.
- Model 2b: 12,521 sentences, 25 shared features.
- Model 3a: 115,426 word-conditioned pairs, group-split by target word.
- Model 3b: 22,811 supported simplification/preserve pairs, group-split by original.

## Verification

Run from repository root with activated virtual environment (`.\.venv\Scripts\python.exe`):

```powershell
# 1. Environment and GPU Hardware Check
python -m src._env_check

# 2. Test Suites (49 tests)
python -m pytest -q

# 3. Pipeline Spot-Check (CUDA or CPU)
python -m src.pipeline.run_pipeline "tốt" --target-level B2 --device cuda

# 4. Manifest and Failure Review
python -m src.artifacts.build_manifest
python -m src.quality.failure_review list --limit 20

# 5. API Server
uvicorn src.api.app:app --host 127.0.0.1 --port 8000

# 6. Release Verification
python -m src.release.build_release verify dist/capyvocab-ml-0.3.0
```

## Next Work

1. Collect more opt-in failure candidates (e.g. from user traffic or extended evaluation) to reach the $\ge 100$ reviewed / $\ge 50$ confirmed failure gate for Model 4.
2. Train Model 4 (Error Detection / Quality Reranker) only after the failure queue gate is satisfied.
3. Add authentication / API rate limiting and user-facing UI before public network exposure.

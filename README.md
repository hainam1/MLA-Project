# English Sentence CEFR Classification

This repository contains one focused final-project pipeline: classify an English sentence into
CEFR levels A1-C1 for language-learning support.

**Official model comparison:** K-Nearest Neighbors (distance/instance-based family) versus
Decision Tree (tree-based family), using the same interpretable linguistic features and the same
leakage-safe data split. Frozen DeBERTa embeddings remain an optional feature extension only.

## Scope

```text
English sentence
  -> licensed UniversalCEFR data
  -> cleaning and near-duplicate grouping
  -> leakage-safe train/validation/test split
  -> interpretable linguistic features
  -> KNN: imputation + train-only scaling
  -> Decision Tree: imputation + validation-selected pruning
  -> KNN vs Decision Tree
  -> Macro F1, QWK, comparison, and error analysis
```

Translation, word-level prediction, sentence generation, rewriting, quality auditing, and a
production API are intentionally out of scope.

## Project status

The repository has been narrowed from an earlier multipurpose product pipeline. Existing sentence
classification results are historical baselines and must be reproduced after the final experiment
protocol is implemented. Do not combine figures from different metadata or experimental runs.

The detailed roadmap and acceptance gates are in
[`final-project-plan.md`](final-project-plan.md). Current work items are in [`TASKS.md`](TASKS.md).

## Data

The primary datasets are:

- `UniversalCEFR/cefr_sp_en`
- `UniversalCEFR/readme_en`

Raw and processed data are intentionally ignored by Git. Provenance and current license notes are
recorded in [`data/raw/cefr_sentence/SOURCE.md`](data/raw/cefr_sentence/SOURCE.md) and
[`reports/00_dataset_licenses.md`](reports/00_dataset_licenses.md).

The word-level CEFR survey is permitted only as an auxiliary lexical resource for aggregate
sentence features. It is not a separate task or model, and the final experiments must include an
ablation without it.

## Planned commands

The following command contract will be completed and verified phase by phase:

```powershell
python -m src.data.download_datasets
python -m src.data.download_datasets --include-auxiliary-lexicon
python -m src.data.clean_cefr_sentences
python -m src.data.clean_cefr_wordlist
python -m src.data.build_sentence_cefr_features --full
python -m src.data.split_datasets
python -m src.models.sentence_cefr.train
python -m src.inference "Despite the rain, the expedition continued."
python -m pytest -q
```

Python 3.12 is the target environment. Install the development dependencies and spaCy model with:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m spacy download en_core_web_sm
```

Install `requirements-contextual.txt` only when implementing/running the optional DeBERTa
extension. It is not needed for the two required model families.

## Results policy

Old model tables were removed from the active project to prevent accidental mixing of incompatible
experiments. [`reports/model_comparison.md`](reports/model_comparison.md) is the only active
result-table template. Fill it only with outputs from the frozen KNN-versus-Decision-Tree protocol;
regenerate all final figures from that same run.

## Responsible use

This is an academic, non-commercial project. CEFR predictions are estimates and must not be used as
high-stakes judgments about a learner. LLM assistance is supporting-only and will be disclosed; no
LLM supplies labels or runtime predictions.

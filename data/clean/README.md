# Cleaned & Standardized Datasets (`data/clean/`)

This directory contains the cleaned, standardized, and partition-ready ELLIPSE datasets.
All columns follow canonical `snake_case` naming, redundant raw columns are removed, and text is normalized.

## Files

| File | Rows | Columns | Split | Primary Purpose |
|---|---|---|---|---|
| `train.csv` | 3,128 | 16 | `model_train` | Model training & 5-fold CV (`cv_fold` column 0–4) |
| `val.csv` | 783 | 15 | `validation` | Hyperparameter selection & validation checkpoints |
| `test.csv` | 2,571 | 15 | `official_test` | Official held-out evaluation partition |
| `all_essays_clean.csv` | 6,482 | 19 | All splits | Full cleaned corpus for exploratory analysis & reference |

## Standard Schema (`train.csv`, `val.csv`, `test.csv`)

| Column | Type | Example | Description |
|---|---|---|---|
| `essay_id` | `str` | `5661280443` | Unique essay identifier |
| `prompt` | `str` | `Benefits of a problem` | Writing prompt topic |
| `essay_text` | `str` | `Imagine if you could...` | Original text (whitespace trimmed) |
| `clean_text` | `str` | `Imagine if you could...` | Normalized text (Unicode NFKC + clean spaces) |
| `vocabulary` | `float` | `3.5` | Human Vocabulary score [1.0 – 5.0, step 0.5] |
| `grammar` | `float` | `4.0` | Human Grammar score [1.0 – 5.0, step 0.5] |
| `overall` | `float` | `4.0` | Human Holistic score [1.0 – 5.0, step 0.5] |
| `cohesion` | `float` | `3.5` | Human Cohesion score [1.0 – 5.0, step 0.5] |
| `syntax` | `float` | `4.0` | Human Syntax score [1.0 – 5.0, step 0.5] |
| `phraseology` | `float` | `3.5` | Human Phraseology score [1.0 – 5.0, step 0.5] |
| `conventions` | `float` | `4.0` | Human Conventions score [1.0 – 5.0, step 0.5] |
| `grade` | `int` | `8` | Learner grade level (8, 9, 10, 11, 12) |
| `gender` | `str` | `Male` | Learner gender (Male, Female) |
| `race_ethnicity` | `str` | `Hispanic/Latino` | Learner racial/ethnic background |
| `ses` | `str` | `Economically disadvantaged` | Socio-economic status |
| `cv_fold` | `Int64` | `0` | *(Only in `train.csv`)* Cross-validation fold index (0–4) |

`all_essays_clean.csv` also includes:
- `split`: Partition name (`model_train`, `validation`, `official_test`)
- `source_partition`: Original ELLIPSE partition (`official_train`, `official_test`)
- `privacy_review_status`: PII screening status (`not_flagged`, `flagged_by_rater`)

## How to Load in Python

```python
from mla_project.data import load_clean_data

# Load train set (3,128 rows, includes cv_fold 0-4)
train_df = load_clean_data("train")

# Load validation set (783 rows)
val_df = load_clean_data("val")

# Load official test set (2,571 rows)
test_df = load_clean_data("test")

# Load full corpus (6,482 rows)
all_df = load_clean_data("all")
```

## How to Regenerate

To rebuild these clean CSVs from raw snapshots and the frozen split manifest:

```bash
python scripts/build_clean_dataset.py
```

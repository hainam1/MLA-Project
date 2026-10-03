# Dataset

ELLIPSE is the primary dataset. The three source CSV files and official `ELL_Rubrics.docx` are kept
together in `data/01_original_source/` because the rubric defines the human scores in those source tables. This is
preferable to `docs/references/` here: the rubric is a versioned part of the raw dataset snapshot,
not project-authored documentation.

The canonical project mapping is `text_id_kaggle` to `essay_id` and `full_text` to `essay_text`.
The prediction targets are the original numeric `Vocabulary` and `Grammar` columns. Source files
are never edited in place. Derived feature tables belong in `data/05_model_features/`, temporary artifacts
in `data/04_intermediate_work/`, and split manifests in `data/02_split_manifest/`.

Source: ELLIPSE Corpus by Crossley et al. (2023). License: CC BY-NC-SA 4.0. Exact local checksums
and citation details are recorded in `data/01_original_source/documentation/SOURCE.md`.

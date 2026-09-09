# Task Formulation

## Problem

Given one English sentence `x`, predict its CEFR difficulty `y` from the ordered label set
`{A1, A2, B1, B2, C1}`. Labels are encoded as integers `0..4` only for training and ordinal-error
calculation; the user-facing output remains the CEFR label.

This is a supervised ordinal multi-class classification task for language-learning support.

## Why machine learning is central

Sentence difficulty depends on interacting lexical, syntactic, semantic, and readability signals.
Sentence length or a single readability threshold cannot represent short advanced constructions,
rare vocabulary, ambiguous labels, or domain effects. The project therefore learns decision
boundaries from labeled examples and evaluates their generalization on unseen sentence clusters.

## Inputs, features, and labels

- **Input unit:** one English sentence.
- **Ground-truth label:** dataset-provided CEFR level A1-C1.
- **Interpretable features:** surface length, syllables, word frequency/rarity, optional aggregate
  lexical CEFR values, dependency/POS statistics, and standard readability indices.
- **Contextual extension:** frozen DeBERTa sentence embeddings reduced with train-only PCA.
- **Forbidden features:** target labels, textual label names, source IDs, cluster IDs, split IDs, or
  any metadata derived from validation/test labels.

## Model families

1. K-Nearest Neighbors: distance/instance-based family. Median imputation and scaling are fitted on
   training data before neighbor distances are calculated.
2. Decision Tree: tree-based family. Depth and minimum-node-size parameters are selected on
   validation data to control overfitting.

A majority-class classifier is a sanity baseline, not a third family. Frozen DeBERTa, if the
optional extension is run, is a feature extractor rather than one of the two required families.

## Research questions

- How do KNN and Decision Tree compare on the same linguistic features and split?
- Which linguistic feature groups contribute most, including the optional word-CEFR aggregates?
- Which CEFR levels and sentence types remain difficult, and why?

## Evaluation

- Primary: Macro F1.
- Ordinal: Quadratic Weighted Kappa.
- Secondary: accuracy, weighted F1, adjacent accuracy, mean absolute level error, per-class metrics.
- Analysis: paired bootstrap intervals, confusion matrices, source/length/rarity/syntax slices, and
  deterministic qualitative error review.

## Intended and excluded uses

The prediction can help a teacher or learner inspect candidate learning material. It is not a
certification score, a learner assessment, or a replacement for expert judgment. The project does
not infer a person's proficiency and does not use personal/student data.

## LLM boundary

LLMs may assist planning, code review, debugging, and writing. They do not provide dataset labels,
replace model training, or generate the runtime CEFR prediction. All ML conclusions come from saved
experiments on the declared datasets.

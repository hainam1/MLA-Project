# Data Card — English Sentence CEFR Classification

## 1. Dataset Identity & Provenance

* **Primary Sources:**
  - `UniversalCEFR/cefr_sp_en` (revision `b78901348bda9f5a823cd3da1f3fcb2dcc6c5725`)
  - `UniversalCEFR/readme_en` (revision `88ce5b3736bdb666b1f64f738451676b12028a33`)
* **Language & Unit:** English, single sentences.
* **Target Label Space:** CEFR 5-point ordinal scale `{A1, A2, B1, B2, C1}` (mapped to integers `0..4`).
* **Intended Application:** Assessing sentence difficulty for language learners and pedagogical material recommendation.
* **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International ([CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)).
* **Access Date:** 2026-09-08.
* **Auxiliary Resource:** Sohsah, Ünal, and Güzey (2015; Zenodo 12501, CC BY 4.0) word-level CEFR difficulty survey, used exclusively for aggregate sentence feature extraction (5,697 clean entries).
* **Primary dataset citations:** Arase, Uchida, and Kajiwara (2022), *CEFR-Based Sentence-Difficulty Annotation and Assessment*; Naous et al. (2024), *ReadMe++: Benchmarking Multilingual Language Models for Multi-Domain Readability Assessment*. Full references are in `reports/00_dataset_licenses.md`.

---

## 2. Raw Corpus Verification & Checksums

| Dataset Source | Raw Rows | Raw File Size | SHA-256 Checksum |
|---|---:|---:|---|
| `cefr_sp_en_train.csv` | 10,004 | 1,399,579 bytes | `bf497fa063a0cc5e7518b36297027ce32400f94642b729eadf9e697546955673` |
| `readme_en_train.csv` | 2,822 | 501,983 bytes | `5b328e95accf4cb0675bbc0079029b9efa46ca0ba2b10f9dbf0d619ef11e2f8c` |
| **Total Raw** | **12,826** | **1,901,562 bytes** | — |

| Processed Output | Rows | File Size | SHA-256 Checksum |
|---|---:|---:|---|
| `cefr_sentences_clean.csv` | 12,521 | 1,600,670 bytes | `b6c7a42f8464714874d6fdace5b37f88c307cff0abe86903baa0d91707b0231b` |
| `cefr_wordlist_clean.csv` | 5,697 | 203,776 bytes | `1214fad631143bc6bc319416e37c4375b9128b03a4efbd5675adc805617c6c5a` |

---

## 3. Data Cleaning & Audit Reconciliation

All cleaning operations are strictly logged in `data/processed/data_audit.json`:

```text
Raw Rows (12,826)
  ├── cefr_sp_en: 10,004 rows
  │     ├── Excluded C2: -230 rows
  │     ├── Merged exact duplicate: -1 row (rows 4456 & 4457: "At 10.00 am there was a large crowd...")
  │     └── Retained: 9,773 rows
  └── readme_en: 2,822 rows
        ├── Excluded C2: -71 rows
        ├── Merged exact duplicate: -1 row (rows 19 & 418: "The social psychology can be divided...")
        ├── Conflicting label group: -2 rows (rows 1047 & 1054: "If you saw the first one...", labeled both A2 and B1)
        └── Retained: 2,748 rows
  ────────────────────────────────────────────
  Retained Total: 9,773 + 2,748 = 12,521 clean rows
```

* **Exclusion Summary:**
  - Empty text rows: 0
  - Invalid CEFR labels: 0
  - Excluded C2 rows: 301
  - Merged exact duplicates (within-source): 2 rows
  - Conflicting text groups removed: 1 group (2 rows)
  - Cross-source conflicts / duplicates: 0
* **Retained Total:** **12,521** sentences.

---

## 4. Label Distribution & Source Breakdown

| CEFR Level | `cefr_sp_en` (Count / %) | `readme_en` (Count / %) | Overall Combined (Count / %) |
|:---:|---:|---:|---:|
| **A1** | 124 (1.27%) | 182 (6.62%) | **306 (2.44%)** |
| **A2** | 1,271 (13.01%) | 672 (24.45%) | **1,943 (15.52%)** |
| **B1** | 3,304 (33.81%) | 622 (22.63%) | **3,926 (31.36%)** |
| **B2** | 3,330 (34.07%) | 895 (32.57%) | **4,225 (33.74%)** |
| **C1** | 1,744 (17.85%) | 377 (13.72%) | **2,121 (16.94%)** |
| **Total** | **9,773 (100.0%)** | **2,748 (100.0%)** | **12,521 (100.0%)** |

---

## 5. Quantitative Exploratory Data Analysis (EDA)

### A. Sentence Length Characteristics

| CEFR Level | Mean Word Count $\pm$ SD | Median Words | Mean Char Count $\pm$ SD | Median Chars |
|:---:|---:|---:|---:|---:|
| **A1** | $6.17 \pm 2.85$ | 6.0 | $32.32 \pm 14.73$ | 29.0 |
| **A2** | $8.99 \pm 4.20$ | 8.0 | $47.69 \pm 22.45$ | 42.0 |
| **B1** | $12.38 \pm 5.58$ | 11.0 | $71.32 \pm 32.89$ | 65.0 |
| **B2** | $16.79 \pm 7.41$ | 16.0 | $102.94 \pm 46.54$ | 97.0 |
| **C1** | $19.24 \pm 10.21$ | 17.0 | $122.37 \pm 67.92$ | 112.0 |

*Observation:* Sentence length exhibits a strict monotonic increase from A1 (mean 6.17 words) to C1 (mean 19.24 words). However, standard deviations overlap substantially, confirming that length alone cannot reliably separate adjacent CEFR levels.

### B. Lexical Rarity & Frequency Characteristics

| CEFR Level | Mean Word Zipf | Min Word Zipf (Rarest Word) | Rare Word Ratio (Zipf < 4.0) Mean | Rare Word Ratio Median |
|:---:|---:|---:|---:|---:|
| **A1** | 5.795 | 4.233 | 0.056 (5.6%) | 0.000 |
| **A2** | 5.886 | 4.169 | 0.056 (5.6%) | 0.000 |
| **B1** | 5.795 | 3.768 | 0.072 (7.2%) | 0.053 |
| **B2** | 5.616 | 2.968 | 0.130 (13.0%) | 0.114 |
| **C1** | 5.400 | 2.237 | 0.201 (20.1%) | 0.182 |

*Observation:* As difficulty increases from A1 to C1:
- Average word Zipf frequency steadily declines (higher proportion of lower-frequency vocabulary).
- Minimum Zipf frequency drops drastically from 4.233 (A1) to 2.237 (C1), indicating the introduction of specialized/rare terms.
- The proportion of rare words nearly quadruples from 5.6% in A1/A2 to 20.1% in C1.

---

## 6. Generated Visualizations

All figures are generated deterministically by `src/data/generate_eda.py` and saved under `reports/figures/`:
1. `reports/figures/cefr_sentence_distribution.png`: Overall 5-class distribution highlighting class imbalance.
2. `reports/figures/cefr_distribution_by_source.png`: Comparative grouped bar plot across sources (`cefr_sp_en` vs `readme_en`).
3. `reports/figures/sentence_length_distribution.png`: Box plots of word and character count by CEFR level.
4. `reports/figures/lexical_rarity_distribution.png`: Box plots of average Zipf frequency and rare word proportions.

---

## 7. Known Data Risks & Limitations

1. **Class Imbalance:** A1 represents only 2.44% of the dataset (306 sentences), whereas B1 and B2 together account for 65.10%. Models evaluated purely on overall accuracy would naturally bias toward predicting B1/B2. This justifies the mandatory adoption of **Macro F1** as primary selection metric.
2. **Domain Diversity:** `cefr_sp_en` stems from general learner/reference material, while `readme_en` is a multi-domain readability corpus that includes technical, academic, literary, review and other genres. Label proportions differ between sources (e.g., A2 is 13.0% in `cefr_sp_en` vs 24.5% in `readme_en`).
3. **Subjective Annotation Noise:** CEFR level assignment is inherently continuous and subject to annotator boundary variance, as evidenced by conflicting text samples observed during audit.
4. **Scope Limitation:** The dataset evaluates the estimated linguistic complexity of English sentences; it does not measure or represent the proficiency of human individuals.

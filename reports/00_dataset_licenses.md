# Dataset Provenance and License Register

This document records the provenance, licensing, access timestamps, and cryptographic checksums for all datasets utilized in the English Sentence CEFR Classification project.

---

## 1. Summary of Registered Resources

| Role | Resource | Upstream Identifier / URL | Revision / Version | Recorded License | Access Date | Raw Rows | Retained Rows |
|---|---|---|---|---|---|---:|---:|
| **Primary Sentence Data** | `UniversalCEFR/cefr_sp_en` | [HuggingFace: cefr_sp_en](https://huggingface.co/datasets/UniversalCEFR/cefr_sp_en) | `b78901348bda9f5a823cd3da1f3fcb2dcc6c5725` | CC BY-NC-SA 4.0 | 2026-09-08 | 10,004 | 9,773 |
| **Primary Sentence Data** | `UniversalCEFR/readme_en` | [HuggingFace: readme_en](https://huggingface.co/datasets/UniversalCEFR/readme_en) | `88ce5b3736bdb666b1f64f738451676b12028a33` | CC BY-NC-SA 4.0 | 2026-09-08 | 2,822 | 2,748 |
| **Combined Clean Corpus** | Sentence Dataset (`combined`) | `data/processed/cefr_sentences_clean.csv` | Pipeline output | CC BY-NC-SA 4.0 | 2026-09-08 | 12,826 | **12,521** |
| **Auxiliary Lexicon** | Guzey et al. Word-Level Survey | [Zenodo Record 12501](https://doi.org/10.5281/zenodo.12501) | Record 12501 | CC BY 4.0 | 2026-09-08 | ~10,000 entries | 5,697 clean entries |

---

## 2. Cryptographic Checksums (SHA-256)

All raw and processed files have been cryptographically verified:

| File Path | Size (Bytes) | SHA-256 Checksum |
|---|---:|---|
| `data/raw/cefr_sentence/cefr_sp_en_train.csv` | 1,399,579 | `bf497fa063a0cc5e7518b36297027ce32400f94642b729eadf9e697546955673` |
| `data/raw/cefr_sentence/readme_en_train.csv` | 501,983 | `5b328e95accf4cb0675bbc0079029b9efa46ca0ba2b10f9dbf0d619ef11e2f8c` |
| `data/raw/cefr_wordlist/word-level-survey.tar.gz` | 2,084,084 | `95eccf38b5bb11d54d23960ce8e45055cc03c88edf8361d5c096e3182182c90c` |
| `data/raw/cefr_wordlist/WordsTeachersLevelsGoogleFrequenciesPredictions.csv` | 711,308 | `4395fc0df1d06971eb2e0ad98dc41c6c461c122c3da83b3537c28767127b99c1` |
| `data/processed/cefr_sentences_clean.csv` | 1,600,670 | `b6c7a42f8464714874d6fdace5b37f88c307cff0abe86903baa0d91707b0231b` |
| `data/processed/cefr_wordlist_clean.csv` | 203,776 | `1214fad631143bc6bc319416e37c4375b9128b03a4efbd5675adc805617c6c5a` |

---

## 3. Academic Citations & Author Attribution

### UniversalCEFR Corpora

* **Dataset identifiers:** `UniversalCEFR/cefr_sp_en`, `UniversalCEFR/readme_en`.
* **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International ([CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/))
* **Attribution Statement:** Used strictly for non-commercial, academic research in course MLA (Machine Learning & Applications). No derivative datasets are sold or commercialized.
* **Required citations:**
  1. Arase, Y., Uchida, S., & Kajiwara, T. (2022). *CEFR-Based Sentence-Difficulty Annotation and Assessment*. In Proceedings of EMNLP 2022. Source dataset: [CEFR-SP](https://huggingface.co/datasets/UniversalCEFR/cefr_sp_en).
  2. Naous, T., Ryan, M. J., Lavrouk, A., Chandra, M., & Xu, W. (2024). *ReadMe++: Benchmarking Multilingual Language Models for Multi-Domain Readability Assessment*. In Proceedings of EMNLP 2024, pp. 12230–12266. Source dataset: [ReadMe++](https://huggingface.co/datasets/UniversalCEFR/readme_en).

### Guzey et al. Auxiliary Word Lexicon
* **Source and citation:** Sohsah, G. N., Ünal, M. E., & Güzey, O. (2015). *Classification of word levels with usage frequency, expert opinions and machine learning*. British Journal of Educational Technology, 46, 1097–1101. https://doi.org/10.1111/bjet.12338. The accompanying word-level survey is archived at Zenodo record 12501.
* **DOI:** [10.5281/zenodo.12501](https://doi.org/10.5281/zenodo.12501)
* **License:** Creative Commons Attribution 4.0 International ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))
* **Role in Project:** Permitted exclusively for computing aggregate lexical features (`avg_word_cefr`, `max_word_cefr`, `word_oov_ratio`). Never used as a second prediction target. Mandatory feature ablation without this resource is enforced.

---

## 4. Data Governance & Privacy Statement

1. **Academic & Non-commercial:** This project is conducted solely for educational and research evaluation purposes under CC BY-NC-SA 4.0 and CC BY 4.0.
2. **Zero Student/Personal Data:** No personally identifiable information (PII), real learner profiles, or private student exam submissions are used.
3. **Leakage Prevention:** Metadata attributes (`source`, IDs) are preserved for auditability and stratified clustering, but strictly blocked from entering feature matrix $X$.
4. **Data Versioning Policy:** Large raw CSV and binary archives are git-ignored (`.gitignore`). Only reproducible downloader scripts, audit manifests (`data_audit.json`), and EDA summaries are tracked in version control.

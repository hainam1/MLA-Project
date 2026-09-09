# UniversalCEFR English Sentence Sources

Primary sentence datasets for English CEFR classification:

| Dataset ID | Revision | Raw Rows | Retained (A1-C1) | License | SHA-256 Checksum |
|---|---|---:|---:|---|---|
| `UniversalCEFR/cefr_sp_en` | `b78901348bda9f5a823cd3da1f3fcb2dcc6c5725` | 10,004 | 9,773 | CC BY-NC-SA 4.0 | `bf497fa063a0cc5e7518b36297027ce32400f94642b729eadf9e697546955673` |
| `UniversalCEFR/readme_en` | `88ce5b3736bdb666b1f64f738451676b12028a33` | 2,822 | 2,748 | CC BY-NC-SA 4.0 | `5b328e95accf4cb0675bbc0079029b9efa46ca0ba2b10f9dbf0d619ef11e2f8c` |

Upstream dataset cards:
- https://huggingface.co/datasets/UniversalCEFR/cefr_sp_en
- https://huggingface.co/datasets/UniversalCEFR/readme_en

Access date: `2026-09-08`.

Downloaded raw file locations:
```text
data/raw/cefr_sentence/cefr_sp_en_train.csv
data/raw/cefr_sentence/readme_en_train.csv
```

All raw files are intentionally excluded from Git. Reproducible downloading is handled by:
```powershell
python -m src.data.download_datasets
```
Emitted clean file: `data/processed/cefr_sentences_clean.csv` (12,521 sentences across A1-C1).

Required academic citations:

1. Arase, Y., Uchida, S., & Kajiwara, T. (2022). *CEFR-Based Sentence-Difficulty Annotation and Assessment*. EMNLP 2022.
2. Naous, T., Ryan, M. J., Lavrouk, A., Chandra, M., & Xu, W. (2024). *ReadMe++: Benchmarking Multilingual Language Models for Multi-Domain Readability Assessment*. EMNLP 2024, pp. 12230–12266.

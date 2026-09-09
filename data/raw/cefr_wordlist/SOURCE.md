# Optional Auxiliary CEFR Word Lexicon

Source: Sohsah, G. N., Ünal, M. E., & Güzey, O. (2015). *Classification of word levels with usage frequency, expert opinions and machine learning*. British Journal of Educational Technology, 46, 1097–1101. Zenodo record 12501 is the accompanying data archive.

- DOI: https://doi.org/10.5281/zenodo.12501
- Recorded license: CC BY 4.0.
- Access date: `2026-09-08`.
- Role in this project: optional aggregate sentence features only (`avg_word_cefr`, `max_word_cefr`, `word_oov_ratio`).
- It is NOT used to train or evaluate a separate word-level classifier.
- A final feature ablation without these three columns is required.

Local raw files and checksums (SHA-256):
- `data/raw/cefr_wordlist/word-level-survey.tar.gz`: `95eccf38b5bb11d54d23960ce8e45055cc03c88edf8361d5c096e3182182c90c` (2,084,084 bytes)
- `data/raw/cefr_wordlist/WordsTeachersLevelsGoogleFrequenciesPredictions.csv`: `4395fc0df1d06971eb2e0ad98dc41c6c461c122c3da83b3537c28767127b99c1` (711,308 bytes)

Cleaned auxiliary output:
- `data/processed/cefr_wordlist_clean.csv` (5,697 cleaned vocabulary entries with CEFR labels).

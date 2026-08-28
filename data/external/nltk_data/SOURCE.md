# NLTK WordNet runtime data

Install the English WordNet and Open Multilingual WordNet corpora locally:

```powershell
python -m nltk.downloader -d data/external/nltk_data wordnet
```

The serving pipeline uses English WordNet only to expand ranked MarianMT
translations with semantic alternatives. It never assigns CEFR levels from
WordNet; candidates are still filtered by the project's CEFR wordlist and
Model 2a.

- WordNet: Princeton WordNet License
- NLTK data index: https://www.nltk.org/nltk_data/

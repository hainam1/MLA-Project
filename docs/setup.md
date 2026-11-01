# Frozen-artifact setup

The actual test and training environment is Python 3.14.5, sklearn 1.9.1, numpy 2.4.6, pandas 2.3.3 and joblib 1.6.0. NLP uses spaCy 3.8.16, en_core_web_sm 3.8.0, language-tool-python 2.9.5 and LanguageTool 6.6. Java 21.0.10 was verified locally; the installed LanguageTool wrapper requires Java >=17 for 6.6.

`pyproject.toml` declares >=3.12,<3.15, but only the actual environment above is verified for this freeze. `uv.lock` is the pinned dependency source. On a clean machine run `uv sync --locked --python 3.14.5 --extra dev --extra analysis`. Do not update the lock or load sklearn artifacts under an unverified sklearn version. A fresh-machine installation was not executed during finalization; dependency and resource checks plus real local inference were executed.

The lock includes the spaCy model wheel. If missing, run `.venv\Scripts\python.exe -m spacy download en_core_web_sm` and verify version 3.8.0. Java must be installed separately and available on PATH (`java -version`). LanguageTool may download 6.6 on first initialization; network access and a writable local cache are then necessary. Feature extraction uses `load_default_extractor()` to explicitly request 6.6.

Ignored local dataset files, split manifest, feature tables, fitted models and saved predictions are not recreated by installation. Restore the existing approved snapshot at the paths in `configs/paths.yaml`; preserve privacy restrictions and the SHA-256 values in the model/evaluation manifests. For inference the four `outputs/phase6/*.joblib` models and `feature_schema.json` are required. Do not retrain to satisfy setup.

Run `.venv\Scripts\python.exe -m pytest` for unit checks and `.venv\Scripts\python.exe scripts/finalization_smoke.py` for real frozen-model single/batch inference using spaCy and LanguageTool. The latter can trigger the first-run LanguageTool resource download. It uses synthetic text and does not access Official Test.

# Generated artifacts

`manifest.json` records size and SHA-256 for every trained model used by the
MVP. Large weights are intentionally excluded from Git. Rebuild classifiers
with their training modules and restore the translator baseline from
`Helsinki-NLP/opus-mt-vi-en`, then run:

```bash
python -m src.artifacts.build_manifest
python -m src.artifacts.build_manifest --verify
```

Never load an untrusted `.pkl`; joblib/pickle can execute code while loading.

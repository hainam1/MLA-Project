# Semantic reranker checkpoint

- Model: `intfloat/multilingual-e5-small`
- Revision: `0e60b8d9d2166d80387f86e3b48ec9ced55f4d15`
- Source: https://huggingface.co/intfloat/multilingual-e5-small
- License: MIT
- Retrieved: 2026-08-28
- Runtime role: rerank bilingual lexical candidates before CEFR lookup.

The checkpoint is loaded locally with `local_files_only=True`; serving never
silently downloads a mutable model revision.

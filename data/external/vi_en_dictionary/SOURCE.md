# Vietnamese-English lexical dictionary

- Source: `chuongmep/vi-en-dictionary`
- Repository: https://github.com/chuongmep/vi-en-dictionary
- Upstream file: `vi_en_dict.db`
- License: MIT (copyright 2026 Chuong Ho)
- Retrieved: 2026-08-28
- Purpose: lexical candidate retrieval only. The dictionary is never treated as
  a CEFR authority; CEFR is resolved after meaning and part of speech.

The SQLite binary is intentionally excluded from Git. Run
`python -m src.data.prepare_vi_en_lexicon` to validate the locally staged source
and build the normalized runtime index.

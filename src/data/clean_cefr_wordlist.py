"""Prepare the optional CEFR word lexicon used by aggregate sentence features."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

LABEL_MAPPING = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4}


def score_to_cefr(score: float) -> str:
    if score < 1.5:
        return "A1"
    if score <= 2.5:
        return "A2"
    if score < 3.5:
        return "B1"
    if score <= 4.5:
        return "B2"
    if score <= 5.5:
        return "C1"
    return "C2"


def clean_auxiliary_lexicon(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"Word", "PoS", "Teachers Avg", "Level.Teachers.Average"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Auxiliary lexicon is missing columns: {sorted(missing)}")

    working = frame.copy()
    working["word"] = working["Word"].astype(str).str.strip().str.casefold()
    working["pos"] = working["PoS"].astype(str).str.strip().str.upper()
    working = working[
        (working["word"] != "")
        & ~working["Level.Teachers.Average"].isin(["Unknown", "C2"])
        & working["Teachers Avg"].notna()
    ]

    rows = []
    for (word, part_of_speech), group in working.groupby(["word", "pos"], sort=True):
        mean_score = float(group["Teachers Avg"].mean())
        level = score_to_cefr(mean_score)
        if level in LABEL_MAPPING:
            rows.append(
                {
                    "word": word,
                    "pos": part_of_speech,
                    "teachers_avg": round(mean_score, 4),
                    "cefr_level": level,
                    "cefr_label": LABEL_MAPPING[level],
                }
            )
    result = pd.DataFrame(rows)
    return result.replace([np.inf, -np.inf], np.nan).dropna(subset=["cefr_label"])


def main() -> None:
    source = Path("data/raw/cefr_wordlist/WordsTeachersLevelsGoogleFrequenciesPredictions.csv")
    destination = Path("data/processed/cefr_wordlist_clean.csv")
    if not source.exists():
        raise FileNotFoundError(
            f"Missing {source}; run the downloader with --include-auxiliary-lexicon"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    result = clean_auxiliary_lexicon(pd.read_csv(source))
    result.to_csv(destination, index=False, encoding="utf-8")
    print(f"Wrote {len(result):,} auxiliary entries to {destination}")


if __name__ == "__main__":
    main()

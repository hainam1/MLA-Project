"""Shared pytest fixtures for the writing-score regression project."""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def essay_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "essay_id": [f"e{i}" for i in range(8)],
            "essay_text": [f"Learner essay number {i}." for i in range(8)],
            "Vocabulary": [1, 2, 2, 3, 3, 4, 4, 5],
            "Grammar": [1, 2, 2, 3, 3, 4, 4, 5],
            "learner_id": ["l1", "l1", "l2", "l2", "l3", "l3", "l4", "l4"],
            "prompt_id": ["p1", "p2"] * 4,
        }
    )

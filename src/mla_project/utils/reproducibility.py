"""Reproducibility helpers."""

from __future__ import annotations

import random

import numpy as np


def set_random_seed(seed: int) -> None:
    """Seed Python and NumPy random number generators."""
    random.seed(seed)
    np.random.seed(seed)

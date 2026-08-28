import torch  # noqa: F401 - Initialize torch C++/CUDA runtime before spaCy/thinc

from .sentence import SENTENCE_FEATURE_COLUMNS, SentenceFeatureExtractor
from .word import WORD_FEATURE_COLUMNS, extract_word_features

__all__ = [
    "SENTENCE_FEATURE_COLUMNS",
    "SentenceFeatureExtractor",
    "WORD_FEATURE_COLUMNS",
    "extract_word_features",
]

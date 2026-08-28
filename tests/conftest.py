import torch  # noqa: F401 - Initialize torch C++/CUDA DLL paths before other imports

import pytest

from src.pipeline.predict_cefr import CEFRInferenceEngine


@pytest.fixture(scope="session")
def cefr_engine():
    return CEFRInferenceEngine()

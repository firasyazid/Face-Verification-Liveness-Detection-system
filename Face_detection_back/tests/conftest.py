import sys
from unittest.mock import MagicMock

# Mock deepface and tensorflow if they fail to import (common in CI)
try:
    import deepface
except ImportError:
    sys.modules["deepface"] = MagicMock()
    sys.modules["deepface.DeepFace"] = MagicMock()

try:
    import tensorflow
except ImportError:
    sys.modules["tensorflow"] = MagicMock()
    sys.modules["tensorflow.keras"] = MagicMock()
    sys.modules["tensorflow.keras.preprocessing"] = MagicMock()
    sys.modules["tensorflow.keras.preprocessing.image"] = MagicMock()

# Specifically handle the deepface import chain issue
sys.modules["tensorflow.keras"] = MagicMock()
sys.modules["tensorflow.keras.models"] = MagicMock()  # <--- Added this line
sys.modules["tensorflow.keras.preprocessing"] = MagicMock()
sys.modules["tensorflow.keras.preprocessing.image"] = MagicMock()

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Get path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test."""
    yield
    # Add cleanup code here if needed

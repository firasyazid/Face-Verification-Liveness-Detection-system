import sys
from unittest.mock import MagicMock



# 1. Mock DeepFace
sys.modules["deepface"] = MagicMock()
sys.modules["deepface.DeepFace"] = MagicMock()

# 2. Mock TensorFlow and Keras
sys.modules["tensorflow"] = mock_tf
sys.modules["tensorflow.keras"] = MagicMock()
sys.modules["tensorflow.keras.models"] = MagicMock()
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

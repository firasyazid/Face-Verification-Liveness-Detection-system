import sys
from unittest.mock import MagicMock
# 1. Mock DeepFace
deepface_mock = MagicMock()
# Configure verify to return a success dict by default
deepface_mock.verify.return_value = {
    "verified": True, 
    "distance": 0.1, 
    "threshold": 0.4,
    "model": "Facenet512",
    "similarity_metric": "cosine"
}
sys.modules["deepface"] = deepface_mock
sys.modules["deepface.DeepFace"] = deepface_mock

# 2. Mock TensorFlow and Keras
mock_tf = MagicMock()
sys.modules["tensorflow"] = mock_tf
sys.modules["tensorflow.keras"] = MagicMock()
sys.modules["tensorflow.keras.models"] = MagicMock()
sys.modules["tensorflow.keras.preprocessing"] = MagicMock()
sys.modules["tensorflow.keras.preprocessing.image"] = MagicMock()

# 3. Mock OpenCV (cv2)
# Prevents 'ImportError: libGL.so.1: cannot open shared object file'
try:
    import cv2
except ImportError:
    sys.modules["cv2"] = MagicMock()
    # Ensure specific cv2 constants/attributes exist on the mock
    cv2_mock = MagicMock()
    cv2_mock.VideoCapture = MagicMock()
    cv2_mock.CAP_PROP_FRAME_COUNT = 7
    cv2_mock.CAP_PROP_POS_FRAMES = 1
    cv2_mock.ROTATE_90_CLOCKWISE = 0
    cv2_mock.COLOR_BGR2RGB = 4
    sys.modules["cv2"] = cv2_mock

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

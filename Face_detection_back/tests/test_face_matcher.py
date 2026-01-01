"""Unit tests for face matching service."""
import numpy as np
from unittest.mock import patch, MagicMock
import pytest
from app.services.face_matcher import verify_faces


class TestFaceMatcher:
    """Test cases for face verification."""

    def test_verify_faces_same_person(self):
        """Test verification with same person (should match)."""
        with patch('app.services.face_matcher.DeepFace.verify') as mock_verify:
            mock_verify.return_value = {
                'verified': True,
                'distance': 0.3,
                'threshold': 0.5
            }
            
            result = verify_faces(
                'profile.jpg',
                np.zeros((480, 640, 3), dtype=np.uint8)
            )
            
            assert result['verified'] is True
            assert result['distance'] == 0.3
            assert 'error' not in result
            assert result['model'] == 'Facenet512'

    def test_verify_faces_different_person(self):
        """Test verification with different person (should not match)."""
        with patch('app.services.face_matcher.DeepFace.verify') as mock_verify:
            mock_verify.return_value = {
                'verified': False,
                'distance': 0.8,
                'threshold': 0.5
            }
            
            result = verify_faces(
                'profile.jpg',
                np.zeros((480, 640, 3), dtype=np.uint8)
            )
            
            assert result['verified'] is False
            assert result['distance'] == 0.8
            assert result['threshold'] == 0.5

    def test_verify_faces_returns_dict(self):
        """Test that verify_faces returns a dictionary."""
        with patch('app.services.face_matcher.DeepFace.verify') as mock_verify:
            mock_verify.return_value = {
                'verified': True,
                'distance': 0.4,
                'threshold': 0.5
            }
            
            result = verify_faces(
                'profile.jpg',
                np.zeros((480, 640, 3), dtype=np.uint8)
            )
            
            assert isinstance(result, dict)
            assert 'verified' in result
            assert 'distance' in result

    def test_verify_faces_validation_error(self):
        """Test face validation error handling."""
        with patch('app.services.face_matcher.DeepFace.verify') as mock_verify:
            mock_verify.side_effect = ValueError("Face not detected")
            
            result = verify_faces(
                'profile.jpg',
                np.zeros((480, 640, 3), dtype=np.uint8)
            )
            
            assert result['verified'] is False
            assert 'error' in result
            assert result['distance'] == 1.0
            assert 'Face validation failed' in result.get('message', '')

    def test_verify_faces_unexpected_error(self):
        """Test unexpected error handling."""
        with patch('app.services.face_matcher.DeepFace.verify') as mock_verify:
            mock_verify.side_effect = Exception("Service error")
            
            result = verify_faces(
                'profile.jpg',
                np.zeros((480, 640, 3), dtype=np.uint8)
            )
            
            assert result['verified'] is False
            assert 'error' in result
            assert result['message'] == "Verification service error"
            assert result['distance'] == 1.0

    def test_verify_faces_with_multiple_frames(self):
        """Test verification with different frame sizes."""
        with patch('app.services.face_matcher.DeepFace.verify') as mock_verify:
            mock_verify.return_value = {
                'verified': True,
                'distance': 0.35,
                'threshold': 0.5
            }
            
            frame = np.random.randint(0, 255, (640, 480, 3), dtype=np.uint8)
            result = verify_faces('profile.jpg', frame)
            
            assert result['verified'] is True
            mock_verify.assert_called_once()

    def test_verify_faces_threshold_value(self):
        """Test that threshold is correctly returned."""
        with patch('app.services.face_matcher.DeepFace.verify') as mock_verify:
            mock_verify.return_value = {
                'verified': False,
                'distance': 0.7,
                'threshold': 0.5
            }
            
            result = verify_faces(
                'profile.jpg',
                np.zeros((480, 640, 3), dtype=np.uint8)
            )
            
            assert result['threshold'] == 0.5
            assert 'threshold' in result

    def test_verify_faces_model_name(self):
        """Test that model name is in result."""
        with patch('app.services.face_matcher.DeepFace.verify') as mock_verify:
            mock_verify.return_value = {
                'verified': True,
                'distance': 0.3,
                'threshold': 0.5
            }
            
            result = verify_faces(
                'profile.jpg',
                np.zeros((480, 640, 3), dtype=np.uint8)
            )
            
            assert result['model'] == 'Facenet512'

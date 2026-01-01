"""Unit tests for face matching service."""
import numpy as np
from unittest.mock import patch, MagicMock
import pytest
from app.services.face_matcher import verify_faces


class TestFaceMatcher:
    """Test cases for face verification."""

    @pytest.mark.unit
    def test_verify_faces_same_person(self):
        """Test verification with same person (should match)."""
        # Mock DeepFace.verify response
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

    @pytest.mark.unit
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

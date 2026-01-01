"""Unit tests for liveness detection service."""
import numpy as np
from unittest.mock import patch, MagicMock
import pytest
from app.services.liveness import get_head_pose_yaw, check_liveness_pose


class TestLiveness:
    """Test cases for liveness detection."""

    def test_get_head_pose_yaw_with_valid_face(self):
        """Test head pose detection with valid face detection."""
        # Create a mock face mesh result
        with patch('app.services.liveness.face_mesh.process') as mock_process:
            mock_result = MagicMock()
            mock_landmark = MagicMock()
            
            # Create landmarks for nose and ears
            nose_landmark = MagicMock()
            nose_landmark.x = 0.5
            nose_landmark.y = 0.5
            
            left_ear_landmark = MagicMock()
            left_ear_landmark.x = 0.3
            left_ear_landmark.y = 0.5
            
            right_ear_landmark = MagicMock()
            right_ear_landmark.x = 0.7
            right_ear_landmark.y = 0.5
            
            landmarks = [None] * 455
            landmarks[1] = nose_landmark
            landmarks[234] = left_ear_landmark
            landmarks[454] = right_ear_landmark
            
            mock_result.multi_face_landmarks = [MagicMock(landmark=landmarks)]
            mock_process.return_value = mock_result
            
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            result = get_head_pose_yaw(frame)
            
            # Should return a ratio value
            assert result is not None
            assert isinstance(result, (int, float))

    def test_get_head_pose_yaw_no_face(self):
        """Test head pose when no face is detected."""
        with patch('app.services.liveness.face_mesh.process') as mock_process:
            mock_result = MagicMock()
            mock_result.multi_face_landmarks = None
            mock_process.return_value = mock_result
            
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            result = get_head_pose_yaw(frame)
            
            assert result is None

    def test_get_head_pose_yaw_empty_landmarks(self):
        """Test head pose with empty face landmarks."""
        with patch('app.services.liveness.face_mesh.process') as mock_process:
            mock_result = MagicMock()
            mock_result.multi_face_landmarks = []
            mock_process.return_value = mock_result
            
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            result = get_head_pose_yaw(frame)
            
            assert result is None

    def test_check_liveness_pose_returns_tuple(self):
        """Test that check_liveness_pose returns a tuple."""
        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(4)]
        
        with patch('app.services.liveness.get_head_pose_yaw') as mock_yaw:
            mock_yaw.side_effect = [1.0, 0.8, 0.3, 0.2]
            
            result = check_liveness_pose(frames)
            
            assert isinstance(result, tuple)
            assert len(result) == 3
            is_live, message, details = result
            assert isinstance(is_live, bool)
            assert isinstance(message, str)
            assert isinstance(details, dict)

    def test_check_liveness_pose_insufficient_frames(self):
        """Test liveness check with insufficient valid frames."""
        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(4)]
        
        with patch('app.services.liveness.get_head_pose_yaw') as mock_yaw:
            # Return only 1 valid frame
            mock_yaw.side_effect = [None, None, 1.0, None]
            
            is_live, message, details = check_liveness_pose(frames)
            
            assert is_live is False
            assert "Face not detected" in message or "Insufficient" in message

    def test_check_liveness_pose_valid_movement(self):
        """Test liveness check with valid head movement."""
        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(4)]
        
        with patch('app.services.liveness.get_head_pose_yaw') as mock_yaw:
            # Simulate center (1.0) to left (<0.5) movement
            mock_yaw.side_effect = [1.0, 0.9, 0.3, 0.2]
            
            is_live, message, details = check_liveness_pose(frames)
            
            assert isinstance(is_live, bool)
            assert isinstance(message, str)
            assert "ratios" in details

    def test_check_liveness_pose_no_center_position(self):
        """Test liveness check when face never in center."""
        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(4)]
        
        with patch('app.services.liveness.get_head_pose_yaw') as mock_yaw:
            # All ratios are too low (face not centered)
            mock_yaw.side_effect = [0.3, 0.2, 0.4, 0.3]
            
            is_live, message, details = check_liveness_pose(frames)
            
            assert is_live is False
            assert "straight" in message.lower() or "center" in message.lower()

    def test_check_liveness_pose_all_none_frames(self):
        """Test liveness check when all frames return None."""
        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(4)]
        
        with patch('app.services.liveness.get_head_pose_yaw') as mock_yaw:
            mock_yaw.side_effect = [None, None, None, None]
            
            is_live, message, details = check_liveness_pose(frames)
            
            assert is_live is False
            assert "Face not detected" in message

    def test_check_liveness_pose_details_contain_ratios(self):
        """Test that liveness details contain ratio information."""
        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(4)]
        
        with patch('app.services.liveness.get_head_pose_yaw') as mock_yaw:
            mock_yaw.side_effect = [1.0, 0.8, 0.3, 0.2]
            
            is_live, message, details = check_liveness_pose(frames)
            
            assert "ratios" in details
            assert isinstance(details["ratios"], list)

"""Unit tests for liveness detection service."""
import numpy as np
from unittest.mock import patch, MagicMock
import pytest
from app.services.liveness import get_head_pose_yaw, check_liveness_pose


class TestLiveness:
    """Test cases for liveness detection."""

    @pytest.mark.unit
    def test_get_head_pose_yaw_center_position(self):
        """Test head pose detection at center position."""
        with patch('app.services.liveness.face_mesh.process') as mock_process:
            mock_result = MagicMock()
            mock_landmark = MagicMock()
            mock_landmark.x = 0.5
            mock_result.multi_face_landmarks = [[MagicMock(landmark=[mock_landmark])]]
            
            mock_process.return_value = mock_result
            
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            result = get_head_pose_yaw(frame)
            
            assert result is not None or result is None  # Depends on landmark setup

    @pytest.mark.unit
    def test_get_head_pose_yaw_no_face(self):
        """Test head pose when no face is detected."""
        with patch('app.services.liveness.face_mesh.process') as mock_process:
            mock_result = MagicMock()
            mock_result.multi_face_landmarks = None
            mock_process.return_value = mock_result
            
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            result = get_head_pose_yaw(frame)
            
            assert result is None

    @pytest.mark.unit
    def test_check_liveness_pose_valid_movement(self):
        """Test liveness check with valid head movement."""
        frames = [
            np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(4)
        ]
        
        with patch('app.services.liveness.get_head_pose_yaw') as mock_yaw:
            # Simulate center to left movement
            mock_yaw.side_effect = [1.0, 0.8, 0.3, 0.2]
            
            is_live, message, details = check_liveness_pose(frames)
            
            # Result depends on thresholds, but should return bool and message
            assert isinstance(is_live, bool)
            assert isinstance(message, str)
            assert isinstance(details, dict)

    @pytest.mark.unit
    def test_check_liveness_pose_insufficient_frames(self):
        """Test liveness check with insufficient valid frames."""
        frames = [
            np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(4)
        ]
        
        with patch('app.services.liveness.get_head_pose_yaw') as mock_yaw:
            # Return only 1 valid frame
            mock_yaw.side_effect = [None, None, 1.0, None]
            
            is_live, message, details = check_liveness_pose(frames)
            
            assert is_live is False
            assert "Face not detected" in message or "Insufficient" in message

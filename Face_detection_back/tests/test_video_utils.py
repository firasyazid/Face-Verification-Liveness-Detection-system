"""Additional tests for video utilities service."""
import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock
from app.services.video_utils import extract_frames_from_video, save_temp_video


class TestVideoUtils:
    """Test cases for video utility functions."""

    def test_save_temp_video_creates_file(self):
        """Test that save_temp_video creates a temporary file."""
        video_data = b"fake video data"
        
        result = save_temp_video(video_data)
        
        assert result is not None
        assert os.path.exists(result)
        assert result.endswith('.mp4')
        
        # Cleanup
        if os.path.exists(result):
            os.remove(result)

    def test_save_temp_video_writes_content(self):
        """Test that video data is written to file."""
        video_data = b"test video content"
        
        result = save_temp_video(video_data)
        
        with open(result, 'rb') as f:
            content = f.read()
        
        assert content == video_data
        
        # Cleanup
        os.remove(result)

    @patch('app.services.video_utils.cv2.VideoCapture')
    def test_extract_frames_success(self, mock_capture):
        """Test successful frame extraction."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30  # FPS
        mock_cap.read.side_effect = [
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (False, None)
        ]
        mock_capture.return_value = mock_cap
        
        frames = extract_frames_from_video("test.mp4", num_frames=4)
        
        assert len(frames) == 4
        assert all(isinstance(f, np.ndarray) for f in frames)
        mock_cap.release.assert_called_once()

    @patch('app.services.video_utils.cv2.VideoCapture')
    def test_extract_frames_video_not_opened(self, mock_capture):
        """Test handling when video cannot be opened."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_capture.return_value = mock_cap
        
        frames = extract_frames_from_video("invalid.mp4")
        
        assert frames == []
        mock_cap.release.assert_called_once()

    @patch('app.services.video_utils.cv2.VideoCapture')
    def test_extract_frames_custom_count(self, mock_capture):
        """Test extracting custom number of frames."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30
        mock_cap.read.side_effect = [
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (False, None)
        ]
        mock_capture.return_value = mock_cap
        
        frames = extract_frames_from_video("test.mp4", num_frames=2)
        
        assert len(frames) == 2

    def test_save_temp_video_empty_data(self):
        """Test handling empty video data."""
        result = save_temp_video(b"")
        
        assert os.path.exists(result)
        assert os.path.getsize(result) == 0
        
        os.remove(result)

    @patch('app.services.video_utils.cv2.VideoCapture')
    def test_extract_frames_handles_read_failure(self, mock_capture):
        """Test handling when frame read fails mid-extraction."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30
        mock_cap.read.side_effect = [
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (False, None)
        ]
        mock_capture.return_value = mock_cap
        
        frames = extract_frames_from_video("test.mp4", num_frames=4)
        
        assert len(frames) >= 1
        mock_cap.release.assert_called_once()

"""Tests for video utilities."""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile
from app.services.video_utils import extract_frames_from_video

@pytest.mark.asyncio
class TestVideoUtils:
    """Test cases for video utility functions."""

    @patch('app.services.video_utils.cv2.VideoCapture')
    @patch('app.services.video_utils.tempfile.NamedTemporaryFile')
    async def test_extract_frames_success(self, mock_temp, mock_capture):
        """Test successful frame extraction."""
        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = "test.mp4"
        mock_temp.return_value.__enter__.return_value = mock_file
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30  # Frame count
        
        # Mock frames reading
        mock_cap.read.side_effect = [
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),  # Frame 1
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),  # Frame 2
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),  # Frame 3
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),  # Frame 4
            (False, None)
        ]
        mock_capture.return_value = mock_cap
        
        # Mock UploadFile
        mock_upload = MagicMock(spec=UploadFile)
        mock_upload.read = AsyncMock(return_value=b"fake-video-content")
        
        frames = await extract_frames_from_video(mock_upload, num_frames=4)
        
        assert len(frames) == 4
        assert isinstance(frames[0], np.ndarray)
        mock_cap.release.assert_called_once()

    @patch('app.services.video_utils.cv2.VideoCapture')
    @patch('app.services.video_utils.tempfile.NamedTemporaryFile')
    async def test_extract_frames_video_not_opened(self, mock_temp, mock_capture):
        """Test handling when video cannot be opened."""
        mock_file = MagicMock()
        mock_file.name = "test.mp4"
        mock_temp.return_value.__enter__.return_value = mock_file
        
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_capture.return_value = mock_cap
        
        mock_upload = MagicMock(spec=UploadFile)
        mock_upload.read = AsyncMock(return_value=b"bad-content")
        
        frames = await extract_frames_from_video(mock_upload)
        
        assert frames == []
        mock_cap.release.assert_not_called()  # Release might not be called if not opened, depends on logic

    @patch('app.services.video_utils.cv2.VideoCapture')
    @patch('app.services.video_utils.tempfile.NamedTemporaryFile')
    async def test_extract_frames_empty_video(self, mock_temp, mock_capture):
        """Test handling when video has no frames."""
        mock_file = MagicMock()
        mock_file.name = "test.mp4"
        mock_temp.return_value.__enter__.return_value = mock_file
        
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 0  # 0 frames
        mock_capture.return_value = mock_cap
        
        mock_upload = MagicMock(spec=UploadFile)
        mock_upload.read = AsyncMock(return_value=b"empty")
        
        frames = await extract_frames_from_video(mock_upload)
        
        assert frames == []

    @patch('app.services.video_utils.cv2.VideoCapture')
    @patch('app.services.video_utils.tempfile.NamedTemporaryFile')
    async def test_extract_frames_exception_handling(self, mock_temp, mock_capture):
        """Test handling exceptions during extraction."""
        mock_upload = MagicMock(spec=UploadFile)
        mock_upload.read = AsyncMock(side_effect=Exception("Read error"))
        
        frames = await extract_frames_from_video(mock_upload)
        
        assert frames == []


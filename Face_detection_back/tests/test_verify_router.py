"""Tests for verify router."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


class TestVerifyRouter:
    """Test cases for verification endpoint."""

    @patch('app.routers.verify.verify_faces')
    @patch('app.routers.verify.check_liveness_pose')
    @patch('app.routers.verify.extract_frames_from_video')
    def test_verify_endpoint_success(self, mock_extract, mock_liveness, mock_verify):
        """Test successful verification flow."""
        mock_extract.return_value = [MagicMock()]
        mock_liveness.return_value = (True, "Liveness verified", {})
        mock_verify.return_value = {
            "verified": True,
            "distance": 0.3,
            "threshold": 0.5,
            "model": "Facenet512"
        }
        
        files = {
            "profile_image": ("profile.jpg", b"fake image", "image/jpeg"),
            "live_video": ("video.mp4", b"fake video", "video/mp4")
        }
        
        response = client.post("/api/verify_identity", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["liveness"]["passed"] is True
        assert data["verification"]["verified"] is True

    def test_verify_endpoint_missing_files(self):
        """Test verification with missing files."""
        # Sending empty files dict causing validation error or custom check
        files = {
             "profile_image": ("", b"", ""), 
             "live_video": ("", b"", "")
        }
        response = client.post("/api/verify_identity", files=files)
        # Verify.py line 45 checks for filename presence
        assert response.status_code == 400

    @patch('app.routers.verify.verify_faces')
    @patch('app.routers.verify.check_liveness_pose')
    @patch('app.routers.verify.extract_frames_from_video')
    def test_verify_endpoint_liveness_failed(self, mock_extract, mock_liveness, mock_verify):
        """Test verification when liveness check fails."""
        mock_extract.return_value = [MagicMock()]
        mock_liveness.return_value = (False, "No movement detected", {})
        
        files = {
            "profile_image": ("profile.jpg", b"fake image", "image/jpeg"),
            "live_video": ("video.mp4", b"fake video", "video/mp4")
        }
        
        response = client.post("/api/verify_identity", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["liveness"]["passed"] is False

    @patch('app.routers.verify.verify_faces')
    @patch('app.routers.verify.check_liveness_pose')
    @patch('app.routers.verify.extract_frames_from_video')
    def test_verify_endpoint_verification_failed(self, mock_extract, mock_liveness, mock_verify):
        """Test verification when face matching fails."""
        mock_extract.return_value = [MagicMock()]
        mock_liveness.return_value = (True, "Liveness verified", {})
        mock_verify.return_value = {
            "verified": False,
            "distance": 0.8,
            "threshold": 0.5,
            "model": "Facenet512",
            "message": "Mismatch"
        }
        
        files = {
            "profile_image": ("profile.jpg", b"fake image", "image/jpeg"),
            "live_video": ("video.mp4", b"fake video", "video/mp4")
        }
        
        response = client.post("/api/verify_identity", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["verification"]["verified"] is False

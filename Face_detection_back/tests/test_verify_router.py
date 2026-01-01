"""Additional tests for verify router."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


class TestVerifyRouter:
    """Test cases for verification endpoint."""

    @patch('app.routers.verify.verify_faces')
    @patch('app.routers.verify.check_liveness')
    @patch('app.routers.verify.extract_frames_from_video')
    @patch('app.routers.verify.save_temp_video')
    def test_verify_endpoint_success(self, mock_save, mock_extract, mock_liveness, mock_verify):
        """Test successful verification flow."""
        mock_save.return_value = "temp.mp4"
        mock_extract.return_value = [MagicMock()]
        mock_liveness.return_value = {
            "passed": True,
            "message": "Liveness verified",
            "details": {}
        }
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
        
        response = client.post("/api/verify", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["liveness"]["passed"] is True
        assert data["verification"]["verified"] is True

    @patch('app.routers.verify.save_temp_video')
    def test_verify_endpoint_missing_files(self, mock_save):
        """Test verification with missing files."""
        response = client.post("/api/verify", files={})
        
        assert response.status_code == 422

    @patch('app.routers.verify.verify_faces')
    @patch('app.routers.verify.check_liveness')
    @patch('app.routers.verify.extract_frames_from_video')
    @patch('app.routers.verify.save_temp_video')
    def test_verify_endpoint_liveness_failed(self, mock_save, mock_extract, mock_liveness, mock_verify):
        """Test verification when liveness check fails."""
        mock_save.return_value = "temp.mp4"
        mock_extract.return_value = [MagicMock()]
        mock_liveness.return_value = {
            "passed": False,
            "message": "No movement detected",
            "details": {}
        }
        
        files = {
            "profile_image": ("profile.jpg", b"fake image", "image/jpeg"),
            "live_video": ("video.mp4", b"fake video", "video/mp4")
        }
        
        response = client.post("/api/verify", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["liveness"]["passed"] is False

    @patch('app.routers.verify.verify_faces')
    @patch('app.routers.verify.check_liveness')
    @patch('app.routers.verify.extract_frames_from_video')
    @patch('app.routers.verify.save_temp_video')
    def test_verify_endpoint_verification_failed(self, mock_save, mock_extract, mock_liveness, mock_verify):
        """Test verification when face matching fails."""
        mock_save.return_value = "temp.mp4"
        mock_extract.return_value = [MagicMock()]
        mock_liveness.return_value = {
            "passed": True,
            "message": "Liveness verified",
            "details": {}
        }
        mock_verify.return_value = {
            "verified": False,
            "distance": 0.8,
            "threshold": 0.5,
            "model": "Facenet512"
        }
        
        files = {
            "profile_image": ("profile.jpg", b"fake image", "image/jpeg"),
            "live_video": ("video.mp4", b"fake video", "video/mp4")
        }
        
        response = client.post("/api/verify", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["verification"]["verified"] is False

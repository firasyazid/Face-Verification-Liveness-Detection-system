"""Tests for main FastAPI application."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.unit
    def test_root_endpoint(self, client):
        """Test root endpoint health check."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "version" in response.json()

    @pytest.mark.unit
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "version" in response.json()

    @pytest.mark.unit
    def test_nonexistent_endpoint(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404

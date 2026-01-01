"""Tests for main FastAPI application."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint health check."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"

    def test_root_response_format(self, client):
        """Test root response has correct format."""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"
        
    def test_health_response_format(self, client):
        """Test health response has correct format."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_nonexistent_endpoint(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404

    def test_multiple_health_checks(self, client):
        """Test multiple consecutive health checks."""
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    def test_root_and_health_consistency(self, client):
        """Test root and health endpoints return same version."""
        root_response = client.get("/").json()
        health_response = client.get("/health").json()
        
        assert root_response["version"] == health_response["version"]
        assert root_response["status"] == health_response["status"]

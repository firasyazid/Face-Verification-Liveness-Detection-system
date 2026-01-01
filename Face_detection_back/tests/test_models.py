"""Unit tests for Pydantic models."""
import pytest
from pydantic import ValidationError
from app.models import (
    LivenessResult,
    VerificationResult,
    VerificationResponse,
    ErrorResponse,
    HealthResponse
)


class TestLivenessResult:
    """Test cases for LivenessResult model."""

    def test_liveness_result_passed(self):
        """Test liveness result when passed."""
        result = LivenessResult(
            passed=True,
            message="Liveness verified",
            details={"ratio": 0.95}
        )
        
        assert result.passed is True
        assert result.message == "Liveness verified"
        assert result.details == {"ratio": 0.95}

    def test_liveness_result_failed(self):
        """Test liveness result when failed."""
        result = LivenessResult(
            passed=False,
            message="No movement detected"
        )
        
        assert result.passed is False
        assert result.message == "No movement detected"
        assert result.details is None

    def test_liveness_result_with_details(self):
        """Test liveness result with detailed information."""
        result = LivenessResult(
            passed=True,
            message="Success",
            details={
                "min_ratio": 0.4,
                "max_ratio": 1.2,
                "ratios": [0.95, 1.0, 0.4]
            }
        )
        
        assert "min_ratio" in result.details
        assert "max_ratio" in result.details


class TestVerificationResult:
    """Test cases for VerificationResult model."""

    def test_verification_result_success(self):
        """Test successful verification result."""
        result = VerificationResult(
            verified=True,
            distance=0.35,
            threshold=0.50,
            model="Facenet512"
        )
        
        assert result.verified is True
        assert result.distance == 0.35
        assert result.threshold == 0.50
        assert result.model == "Facenet512"
        assert result.error is None

    def test_verification_result_failure(self):
        """Test failed verification result."""
        result = VerificationResult(
            verified=False,
            distance=0.85,
            threshold=0.50,
            model="Facenet512",
            message="Distance exceeds threshold"
        )
        
        assert result.verified is False
        assert result.distance == 0.85
        assert result.message == "Distance exceeds threshold"

    def test_verification_result_with_error(self):
        """Test verification result with error."""
        result = VerificationResult(
            verified=False,
            distance=1.0,
            model="Facenet512",
            error="Face not detected",
            message="Verification failed"
        )
        
        assert result.verified is False
        assert result.error == "Face not detected"
        assert result.message == "Verification failed"


class TestVerificationResponse:
    """Test cases for VerificationResponse model."""

    def test_verification_response_success(self):
        """Test complete successful verification response."""
        response = VerificationResponse(
            status="success",
            liveness=LivenessResult(
                passed=True,
                message="Liveness verified"
            ),
            verification=VerificationResult(
                verified=True,
                distance=0.35,
                threshold=0.50,
                model="Facenet512"
            )
        )
        
        assert response.status == "success"
        assert response.liveness.passed is True
        assert response.verification.verified is True

    def test_verification_response_failed(self):
        """Test failed verification response."""
        response = VerificationResponse(
            status="failed",
            liveness=LivenessResult(
                passed=False,
                message="No movement"
            ),
            verification=VerificationResult(
                verified=False,
                distance=1.0,
                threshold=0.50,
                model="Facenet512",
                message="Liveness check failed"
            )
        )
        
        assert response.status == "failed"
        assert response.liveness.passed is False
        assert response.verification.verified is False


class TestErrorResponse:
    """Test cases for ErrorResponse model."""

    def test_error_response_basic(self):
        """Test basic error response."""
        error = ErrorResponse(
            message="File upload failed"
        )
        
        assert error.status == "error"
        assert error.message == "File upload failed"
        assert error.error_code is None

    def test_error_response_with_code(self):
        """Test error response with error code."""
        error = ErrorResponse(
            message="Invalid file format",
            error_code="INVALID_FORMAT"
        )
        
        assert error.status == "error"
        assert error.message == "Invalid file format"
        assert error.error_code == "INVALID_FORMAT"


class TestHealthResponse:
    """Test cases for HealthResponse model."""

    def test_health_response(self):
        """Test health check response."""
        health = HealthResponse(version="1.0.0")
        
        assert health.status == "healthy"
        assert health.version == "1.0.0"

    def test_health_response_different_version(self):
        """Test health response with different version."""
        health = HealthResponse(version="2.0.0")
        
        assert health.status == "healthy"
        assert health.version == "2.0.0"

from pydantic import BaseModel, Field
from typing import Optional, Any


class VerificationRequest(BaseModel):
    profile_image: str = Field(..., description="Profile image file")
    live_video: str = Field(..., description="Video file for liveness detection")


class LivenessResult(BaseModel):
    passed: bool
    message: str
    details: Optional[dict] = None


class VerificationResult(BaseModel):
    verified: bool
    distance: Optional[float] = None
    threshold: Optional[float] = None
    model: str
    error: Optional[str] = None
    message: Optional[str] = None


class VerificationResponse(BaseModel):
    status: str = Field(..., description="success, failed, or error")
    liveness: LivenessResult
    verification: VerificationResult


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str

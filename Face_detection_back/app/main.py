from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import verify
from app.config import get_settings
from app.logger import setup_logging, get_logger
from app.models import HealthResponse

setup_logging()
logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version
)

app.include_router(verify.router)


@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    """Root endpoint returning API health status."""
    return HealthResponse(version=settings.app_version)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(version=settings.app_version)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error"}
    )

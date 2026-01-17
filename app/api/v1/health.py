"""Health Check Endpoints"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify service is running.
    
    Returns:
        HealthResponse with status information
    """
    return HealthResponse(status="healthy", version="0.1.0")

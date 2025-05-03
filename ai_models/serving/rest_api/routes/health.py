"""
Health check routes for REST API server.

This module provides route handlers for health checks.
"""

# Try to import FastAPI
try:
    from fastapi import APIRouter
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for type hints
    class APIRouter:
        pass

    class BaseModel:
        pass

    Field = lambda *args, **kwargs: None


# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(tags=["Health"])
else:
    router = None


# Define response models
if FASTAPI_AVAILABLE:

    class HealthResponse(BaseModel):
        """
        Response model for health check.
        """

        status: str = Field(..., description="Status of the server")
        version: str = Field(..., description="Version of the server")
        model_id: str = Field(..., description="ID of the loaded model")
        model_type: str = Field(..., description="Type of the loaded model")
        uptime: float = Field(..., description="Uptime in seconds")


# Define route handlers
if FASTAPI_AVAILABLE:

    @router.get("/health", response_model=HealthResponse)
    async def health_check(server=None):
        """
        Check the health of the server.

        Args:
            server: Server instance (injected by dependency)

        Returns:
            Health status
        """
        # Get server info
        info = server.get_info()

        # Create response
        return {
            "status": "ok",
            "version": info.get("version", "unknown"),
            "model_id": info.get("model_id", "unknown"),
            "model_type": info.get("model_type", "unknown"),
            "uptime": info.get("uptime", 0),
        }

"""
"""
Health check routes for REST API server.
Health check routes for REST API server.


This module provides route handlers for health checks.
This module provides route handlers for health checks.
"""
"""


from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, ConfigDict, Field


FASTAPI_AVAILABLE
FASTAPI_AVAILABLE


# Try to import FastAPI
# Try to import FastAPI
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False


    # Create dummy classes for type hints
    # Create dummy classes for type hints
    class APIRouter:
    class APIRouter:
    pass
    pass


    class BaseModel:
    class BaseModel:
    pass
    pass


    def Field(*args, **kwargs):
    def Field(*args, **kwargs):
    return None
    return None




    # Create router
    # Create router
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:
    router = APIRouter(tags=["Health"])
    router = APIRouter(tags=["Health"])
    else:
    else:
    router = None
    router = None




    # Define response models
    # Define response models
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    class HealthResponse(BaseModel):
    class HealthResponse(BaseModel):
    """
    """
    Response model for health check.
    Response model for health check.
    """
    """


    model_config = ConfigDict(protected_namespaces=())
    model_config = ConfigDict(protected_namespaces=())


    status: str = Field(..., description="Status of the server")
    status: str = Field(..., description="Status of the server")
    version: str = Field(..., description="Version of the server")
    version: str = Field(..., description="Version of the server")
    model_id: str = Field(..., description="ID of the loaded model")
    model_id: str = Field(..., description="ID of the loaded model")
    model_type: str = Field(..., description="Type of the loaded model")
    model_type: str = Field(..., description="Type of the loaded model")
    uptime: float = Field(..., description="Uptime in seconds")
    uptime: float = Field(..., description="Uptime in seconds")




    # Define route handlers
    # Define route handlers
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    @router.get("/health", response_model=HealthResponse)
    @router.get("/health", response_model=HealthResponse)
    async def health_check(server=None):
    async def health_check(server=None):
    """
    """
    Check the health of the server.
    Check the health of the server.


    Args:
    Args:
    server: Server instance (injected by dependency)
    server: Server instance (injected by dependency)


    Returns:
    Returns:
    Health status
    Health status
    """
    """
    # Get server info
    # Get server info
    info = server.get_info()
    info = server.get_info()


    # Create response
    # Create response
    return {
    return {
    "status": "ok",
    "status": "ok",
    "version": info.get("version", "unknown"),
    "version": info.get("version", "unknown"),
    "model_id": info.get("model_id", "unknown"),
    "model_id": info.get("model_id", "unknown"),
    "model_type": info.get("model_type", "unknown"),
    "model_type": info.get("model_type", "unknown"),
    "uptime": info.get("uptime", 0),
    "uptime": info.get("uptime", 0),
    }
    }
"""
FastAPI application for the API server.

This module provides a FastAPI application instance for the API server.
"""


from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import niche_analysis_router



# Create FastAPI app
app = FastAPI(
    title="pAIssive Income API",
    description="RESTful API for pAIssive Income services",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    niche_analysis_router,
    prefix="/api/v1/niche-analysis",
    tags=["Niche Analysis"],
)


# Add health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

Returns:
        Health status
    """
                return {"status": "ok"}


# Add version endpoint
@app.get("/api/version", tags=["Version"])
async def get_version():
    """
    Get API version.

Returns:
        API version information
    """
                return {
        "version": "1.0.0",
        "name": "pAIssive Income API",
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handle HTTP exceptions.

Args:
        request: Request that caused the exception
        exc: HTTP exception

Returns:
        JSON response with error details
    """
                return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail}},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handle general exceptions.

Args:
        request: Request that caused the exception
        exc: Exception

Returns:
        JSON response with error details
    """
                return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": 500, "message": "Internal server error"}},
    )
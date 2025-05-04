"""
"""
FastAPI application for the API server.
FastAPI application for the API server.


This module provides a FastAPI application instance for the API server.
This module provides a FastAPI application instance for the API server.
"""
"""




from fastapi import FastAPI, HTTPException, status
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse


from .routes import niche_analysis_router
from .routes import niche_analysis_router


# Create FastAPI app
# Create FastAPI app
app = FastAPI(
app = FastAPI(
title="pAIssive Income API",
title="pAIssive Income API",
description="RESTful API for pAIssive Income services",
description="RESTful API for pAIssive Income services",
version="1.0.0",
version="1.0.0",
docs_url="/api/docs",
docs_url="/api/docs",
redoc_url="/api/redoc",
redoc_url="/api/redoc",
)
)


# Add CORS middleware
# Add CORS middleware
app.add_middleware(
app.add_middleware(
CORSMiddleware,
CORSMiddleware,
allow_origins=["*"],  # In production, replace with specific origins
allow_origins=["*"],  # In production, replace with specific origins
allow_credentials=True,
allow_credentials=True,
allow_methods=["*"],
allow_methods=["*"],
allow_headers=["*"],
allow_headers=["*"],
)
)


# Include routers
# Include routers
app.include_router(
app.include_router(
niche_analysis_router,
niche_analysis_router,
prefix="/api/v1/niche-analysis",
prefix="/api/v1/niche-analysis",
tags=["Niche Analysis"],
tags=["Niche Analysis"],
)
)




# Add health check endpoint
# Add health check endpoint
@app.get("/api/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    async def health_check():
    """
    """
    Health check endpoint.
    Health check endpoint.


    Returns:
    Returns:
    Health status
    Health status
    """
    """
    return {"status": "ok"}
    return {"status": "ok"}




    # Add version endpoint
    # Add version endpoint
    @app.get("/api/version", tags=["Version"])
    @app.get("/api/version", tags=["Version"])
    async def get_version():
    async def get_version():
    """
    """
    Get API version.
    Get API version.


    Returns:
    Returns:
    API version information
    API version information
    """
    """
    return {
    return {
    "version": "1.0.0",
    "version": "1.0.0",
    "name": "pAIssive Income API",
    "name": "pAIssive Income API",
    }
    }




    # Error handlers
    # Error handlers
    @app.exception_handler(HTTPException)
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
    async def http_exception_handler(request, exc):
    """
    """
    Handle HTTP exceptions.
    Handle HTTP exceptions.


    Args:
    Args:
    request: Request that caused the exception
    request: Request that caused the exception
    exc: HTTP exception
    exc: HTTP exception


    Returns:
    Returns:
    JSON response with error details
    JSON response with error details
    """
    """
    return JSONResponse(
    return JSONResponse(
    status_code=exc.status_code,
    status_code=exc.status_code,
    content={"error": {"code": exc.status_code, "message": exc.detail}},
    content={"error": {"code": exc.status_code, "message": exc.detail}},
    )
    )




    @app.exception_handler(Exception)
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
    async def general_exception_handler(request, exc):
    """
    """
    Handle general exceptions.
    Handle general exceptions.


    Args:
    Args:
    request: Request that caused the exception
    request: Request that caused the exception
    exc: Exception
    exc: Exception


    Returns:
    Returns:
    JSON response with error details
    JSON response with error details
    """
    """
    return JSONResponse(
    return JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={"error": {"code": 500, "message": "Internal server error"}},
    content={"error": {"code": 500, "message": "Internal server error"}},
    )
    )
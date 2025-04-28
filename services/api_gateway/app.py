"""
API Gateway service for pAIssive income microservices architecture.

This module provides the API Gateway implementation, which serves as the entry point
for all client requests to the microservices architecture.
"""

import os
import logging
import argparse
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from services.service_discovery.registration import (
    register_service,
    get_service_metadata,
    get_default_tags
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="pAIssive Income API Gateway",
    description="API Gateway for pAIssive Income microservices architecture",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
service_registration = None


@app.get("/")
async def root():
    """Root endpoint for API Gateway."""
    return {"message": "pAIssive Income API Gateway", "status": "running"}


@app.get("/api/status")
async def api_status():
    """API status endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "api-gateway"
    }


@app.get("/api/services")
async def list_services():
    """List all available services."""
    if not service_registration or not service_registration.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service discovery not available"
        )
    
    try:
        services = service_registration.client.discover_all_services()
        return {"services": {name: [s.dict() for s in instances] for name, instances in services.items()}}
    except Exception as e:
        logger.error(f"Error discovering services: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover services: {str(e)}"
        )


@app.middleware("http")
async def route_requests(request: Request, call_next):
    """
    Route requests to the appropriate microservice.
    
    This middleware intercepts all requests and routes them to the appropriate
    microservice based on the URL path.
    """
    path = request.url.path
    
    # Skip routing for API Gateway's own endpoints
    if path == "/" or path.startswith("/api/status") or path.startswith("/api/services") or path.startswith("/health"):
        return await call_next(request)
    
    # Extract service name from path (e.g., /api/niche-analysis/... -> niche-analysis)
    parts = path.split("/")
    if len(parts) >= 3 and parts[1] == "api":
        service_name = parts[2]
        
        # Map service name from URL to actual service name
        service_name_map = {
            "niche-analysis": "niche-analysis-service",
            "ai-models": "ai-models-service",
            "marketing": "marketing-service",
            "monetization": "monetization-service",
            "agent-team": "agent-team-service",
            "ui": "ui-service",
            "auth": "authentication-service"
        }
        
        target_service = service_name_map.get(service_name, service_name)
        
        # Forward request to target service
        if service_registration and service_registration.client:
            try:
                # Get service URL
                service_url = service_registration.client.get_service_url(target_service)
                if service_url:
                    # TODO: Implement request forwarding to the target service
                    # For now, just return a mock response
                    return JSONResponse(
                        content={
                            "message": f"Request would be forwarded to {target_service}",
                            "path": path,
                            "target_url": service_url
                        }
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Service '{target_service}' not found"
                    )
            except Exception as e:
                logger.error(f"Error routing request to {target_service}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to route request: {str(e)}"
                )
    
    # If we get here, just pass the request through
    return await call_next(request)


def check_service_health() -> bool:
    """
    Check if this service is healthy.
    
    Returns:
        bool: True if healthy, False otherwise
    """
    # For now, always return True
    # In a real implementation, check database connections, etc.
    return True


def register_with_service_registry(port: int):
    """
    Register this service with the service registry.
    
    Args:
        port: Port this service is running on
    """
    global service_registration
    
    # Get metadata and tags
    metadata = get_service_metadata()
    tags = get_default_tags() + ["api", "gateway", "entry-point"]
    
    # Register service
    service_registration = register_service(
        app=app,
        service_name="api-gateway",
        port=port,
        version="1.0.0",
        health_check_path="/health",
        check_functions=[check_service_health],
        tags=tags,
        metadata=metadata
    )
    
    if service_registration:
        logger.info("Successfully registered API Gateway with service registry")
    else:
        logger.warning("Failed to register with service registry, continuing without service discovery")


def start_api_gateway(host: str = "0.0.0.0", port: int = 8000):
    """
    Start the API Gateway service.
    
    Args:
        host: Host to bind to
        port: Port to listen on
    """
    import uvicorn
    
    # Register with service registry
    register_with_service_registry(port)
    
    # Start the API Gateway
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="API Gateway service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    
    args = parser.parse_args()
    
    # Start the API Gateway
    start_api_gateway(host=args.host, port=args.port)
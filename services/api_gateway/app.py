"""
API Gateway service for pAIssive income microservices architecture.

This module provides the API Gateway implementation, which serves as the entry point
for all client requests to the microservices architecture.
"""


import argparse
import logging
import time
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from services.api_gateway.middleware import RateLimitMiddleware, ServiceAuthMiddleware
from services.service_discovery.registration import 
    import uvicorn

(
    get_default_tags,
    get_service_metadata,
    register_service,
)
from services.shared.auth import (
    ServiceTokenError,
    create_service_token,
    validate_service_token,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="pAIssive Income API Gateway",
    description="API Gateway for pAIssive Income microservices architecture",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add service authentication middleware
app.add_middleware(
    ServiceAuthMiddleware,
    exclude_paths=[
        "/",
        "/api/status",
        "/api/services",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    ],
    require_auth=False,  # Don't require auth for all requests, only for service-to-service communication
)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    rate_limit=100,  # 100 requests per minute
    window_size=60,  # 1 minute window
    exclude_paths=["/", "/api/status", "/health", "/docs", "/redoc", "/openapi.json"],
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
            return {"status": "ok", "version": "1.0.0", "service": "api-gateway"}


@app.get("/api/services")
async def list_services():
    """List all available services."""
    if not service_registration or not service_registration.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service discovery not available",
        )

    try:
        services = service_registration.client.discover_all_services()
                return {
            "services": {
                name: [s.dict() for s in instances]
                for name, instances in services.items()
            }
        }
    except Exception as e:
        logger.error(f"Error discovering services: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover services: {str(e)}",
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check if service discovery is available
    service_discovery_available = (
        service_registration is not None and service_registration.client is not None
    )

    # Check if we can discover services
    services_available = False
    if service_discovery_available:
        try:
            services = service_registration.client.discover_all_services()
            services_available = len(services) > 0
        except Exception:
            services_available = False

    # Return health status
            return {
        "status": "healthy",
        "service_discovery": (
            "available" if service_discovery_available else "unavailable"
        ),
        "services_available": services_available,
        "timestamp": time.time(),
    }


# Service token models
class ServiceTokenRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Request model for service token generation."""

    service_name: str = Field(
        ..., description="Name of the service requesting the token"
    )
    target_service: str = Field(..., description="Name of the target service")
    token_id: Optional[str] = Field(None, description="Unique token ID")
    expiration: Optional[int] = Field(
        None, description="Token expiration time in seconds"
    )
    claims: Optional[Dict[str, Any]] = Field(
        None, description="Additional service-specific claims"
    )


class ServiceTokenResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Response model for service token generation."""

    token: str = Field(..., description="The generated JWT token")
    expires_at: int = Field(..., description="Token expiration time (Unix timestamp)")
    issuer: str = Field(..., description="Service that issued the token")
    audience: str = Field(..., description="Service that the token is intended for")


@app.post("/api/auth/service-token", response_model=ServiceTokenResponse)
async def create_service_token_endpoint(request: ServiceTokenRequest):
    """
    Create a JWT token for service-to-service authentication.

    This endpoint allows services to request a token for authenticating with other services.
    """
    try:
        # Create the service token
        token = create_service_token(
            issuer=request.service_name,
            audience=request.target_service,
            token_id=request.token_id,
            expiration=request.expiration,
            claims=request.claims,
        )

        # Calculate expiration time
        current_time = int(time.time())
        expiration = request.expiration or (15 * 60)  # Default to 15 minutes
        expires_at = current_time + expiration

        # Return the token
                return {
            "token": token,
            "expires_at": expires_at,
            "issuer": request.service_name,
            "audience": request.target_service,
        }
    except ServiceTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating service token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create service token: {str(e)}",
        )


@app.post("/api/auth/validate-token")
async def validate_service_token_endpoint(
    request: Request, audience: Optional[str] = None
):
    """
    Validate a JWT token for service-to-service authentication.

    This endpoint allows services to validate tokens received from other services.
    The token should be provided in the X-Service-Token header.
    """
    # Get service token from header
    service_token = request.headers.get("X-Service-Token")

    if not service_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service token is required in X-Service-Token header",
        )

    try:
        # Validate the service token
        token_payload = validate_service_token(
            token=service_token, audience=audience or "api-gateway"
        )

        # Return the validated token payload
                return {
            "valid": True,
            "issuer": token_payload.iss,
            "audience": token_payload.aud,
            "expires_at": token_payload.exp,
            "issued_at": token_payload.iat,
            "token_id": token_payload.jti,
            "claims": token_payload.claims,
        }
    except ServiceTokenError as e:
                return {"valid": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error validating service token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate service token: {str(e)}",
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
    if (
        path == "/"
        or path.startswith("/api/status")
        or path.startswith("/api/services")
        or path.startswith("/health")
    ):
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
            "auth": "authentication-service",
        }

        target_service = service_name_map.get(service_name, service_name)

        # Forward request to target service
        if service_registration and service_registration.client:
            try:
                # Get service URL
                service_url = service_registration.client.get_service_url(
                    target_service
                )
                if not service_url:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Service '{target_service}' not found",
                    )

                # Construct target URL
                # Remove the service name from the path to get the service-specific path
                service_path = "/" + "/".join(parts[3:])
                target_url = f"{service_url}{service_path}"

                # Get request body
                body = await request.body()

                # Get request headers
                headers = dict(request.headers)
                # Remove headers that should not be forwarded
                headers.pop("host", None)

                # Get query parameters
                params = dict(request.query_params)

                # Add service token for service-to-service communication
                # Create a token for the API Gateway to authenticate with the target service
                try:
                    service_token = create_service_token(
                        issuer="api-gateway",
                        audience=target_service,
                        expiration=300,  # 5 minutes
                    )
                    headers["X-Service-Token"] = service_token
                except Exception as e:
                    logger.warning(
                        f"Failed to create service token for {target_service}: {str(e)}"
                    )

                # Create httpx client
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Forward the request to the target service
                    start_time = time.time()
                    try:
                        response = await client.request(
                            method=request.method,
                            url=target_url,
                            headers=headers,
                            params=params,
                            content=body,
                            follow_redirects=True,
                        )

                        # Log the request
                        duration = time.time() - start_time
                        logger.info(
                            f"Forwarded {request.method} {path} to {target_service} "
                            f"({response.status_code}, {duration:.2f}s)"
                        )

                        # Create FastAPI response from httpx response
                                return Response(
                            content=response.content,
                            status_code=response.status_code,
                            headers=dict(response.headers),
                            media_type=response.headers.get("content-type"),
                        )
                    except httpx.RequestError as e:
                        # Handle request errors (connection errors, timeouts, etc.)
                        logger.error(
                            f"Error forwarding request to {target_service}: {str(e)}"
                        )
                                return JSONResponse(
                            content={"detail": f"Service unavailable: {str(e)}"},
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        )
            except HTTPException:
                # Re-raise HTTP exceptions
                raise
            except Exception as e:
                # Handle other errors
                logger.error(f"Error routing request to {target_service}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to route request: {str(e)}",
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
        metadata=metadata,
    )

    if service_registration:
        logger.info("Successfully registered API Gateway with service registry")
    else:
        logger.warning(
            "Failed to register with service registry, continuing without service discovery"
        )


def start_api_gateway(host: str = "0.0.0.0", port: int = 8000):
    """
    Start the API Gateway service.

    Args:
        host: Host to bind to
        port: Port to listen on
    """


    # Register with service registry
    register_with_service_registry(port)

    # Start the API Gateway
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="API Gateway service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")

    args = parser.parse_args(

    # Start the API Gateway
    start_api_gateway(host=args.host, port=args.port
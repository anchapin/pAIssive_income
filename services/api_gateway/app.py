"""
"""
API Gateway service for pAIssive income microservices architecture.
API Gateway service for pAIssive income microservices architecture.


This module provides the API Gateway implementation, which serves as the entry point
This module provides the API Gateway implementation, which serves as the entry point
for all client requests to the microservices architecture.
for all client requests to the microservices architecture.
"""
"""




import argparse
import argparse
import logging
import logging
import time
import time
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


import httpx
import httpx
import uvicorn
import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, ConfigDict, Field


from services.api_gateway.middleware import (RateLimitMiddleware,
from services.api_gateway.middleware import (RateLimitMiddleware,
ServiceAuthMiddleware)
ServiceAuthMiddleware)


(
(
get_default_tags,
get_default_tags,
get_service_metadata,
get_service_metadata,
register_service,
register_service,
)
)
from services.shared.auth import (ServiceTokenError, create_service_token,
from services.shared.auth import (ServiceTokenError, create_service_token,
validate_service_token)
validate_service_token)


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Create FastAPI application
# Create FastAPI application
app = FastAPI(
app = FastAPI(
title="pAIssive Income API Gateway",
title="pAIssive Income API Gateway",
description="API Gateway for pAIssive Income microservices architecture",
description="API Gateway for pAIssive Income microservices architecture",
version="1.0.0",
version="1.0.0",
)
)


# Add CORS middleware
# Add CORS middleware
app.add_middleware(
app.add_middleware(
CORSMiddleware,
CORSMiddleware,
allow_origins=["*"],  # In production, specify actual origins
allow_origins=["*"],  # In production, specify actual origins
allow_credentials=True,
allow_credentials=True,
allow_methods=["*"],
allow_methods=["*"],
allow_headers=["*"],
allow_headers=["*"],
)
)


# Add service authentication middleware
# Add service authentication middleware
app.add_middleware(
app.add_middleware(
ServiceAuthMiddleware,
ServiceAuthMiddleware,
exclude_paths=[
exclude_paths=[
"/",
"/",
"/api/status",
"/api/status",
"/api/services",
"/api/services",
"/health",
"/health",
"/docs",
"/docs",
"/redoc",
"/redoc",
"/openapi.json",
"/openapi.json",
],
],
require_auth=False,  # Don't require auth for all requests, only for service-to-service communication
require_auth=False,  # Don't require auth for all requests, only for service-to-service communication
)
)


# Add rate limiting middleware
# Add rate limiting middleware
app.add_middleware(
app.add_middleware(
RateLimitMiddleware,
RateLimitMiddleware,
rate_limit=100,  # 100 requests per minute
rate_limit=100,  # 100 requests per minute
window_size=60,  # 1 minute window
window_size=60,  # 1 minute window
exclude_paths=["/", "/api/status", "/health", "/docs", "/redoc", "/openapi.json"],
exclude_paths=["/", "/api/status", "/health", "/docs", "/redoc", "/openapi.json"],
)
)


# Global variables
# Global variables
service_registration = None
service_registration = None




@app.get("/")
@app.get("/")
async def root():
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

    token: str = Field(..., description="The generated JWT token")
    expires_at: int = Field(..., description="Token expiration time (Unix timestamp)")
    issuer: str = Field(..., description="Service that issued the token")
    audience: str = Field(..., description="Service that the token is intended for")


    @app.post("/api/auth/service-token", response_model=ServiceTokenResponse)
    async def create_service_token_endpoint(request: ServiceTokenRequest):
    """
    """
    Create a JWT token for service-to-service authentication.
    Create a JWT token for service-to-service authentication.


    This endpoint allows services to request a token for authenticating with other services.
    This endpoint allows services to request a token for authenticating with other services.
    """
    """
    try:
    try:
    # Create the service token
    # Create the service token
    token = create_service_token(
    token = create_service_token(
    issuer=request.service_name,
    issuer=request.service_name,
    audience=request.target_service,
    audience=request.target_service,
    token_id=request.token_id,
    token_id=request.token_id,
    expiration=request.expiration,
    expiration=request.expiration,
    claims=request.claims,
    claims=request.claims,
    )
    )


    # Calculate expiration time
    # Calculate expiration time
    current_time = int(time.time())
    current_time = int(time.time())
    expiration = request.expiration or (15 * 60)  # Default to 15 minutes
    expiration = request.expiration or (15 * 60)  # Default to 15 minutes
    expires_at = current_time + expiration
    expires_at = current_time + expiration


    # Return the token
    # Return the token
    return {
    return {
    "token": token,
    "token": token,
    "expires_at": expires_at,
    "expires_at": expires_at,
    "issuer": request.service_name,
    "issuer": request.service_name,
    "audience": request.target_service,
    "audience": request.target_service,
    }
    }
except ServiceTokenError as e:
except ServiceTokenError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
except Exception as e:
except Exception as e:
    logger.error(f"Error creating service token: {str(e)}")
    logger.error(f"Error creating service token: {str(e)}")
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=f"Failed to create service token: {str(e)}",
    detail=f"Failed to create service token: {str(e)}",
    )
    )




    @app.post("/api/auth/validate-token")
    @app.post("/api/auth/validate-token")
    async def validate_service_token_endpoint(
    async def validate_service_token_endpoint(
    request: Request, audience: Optional[str] = None
    request: Request, audience: Optional[str] = None
    ):
    ):
    """
    """
    Validate a JWT token for service-to-service authentication.
    Validate a JWT token for service-to-service authentication.


    This endpoint allows services to validate tokens received from other services.
    This endpoint allows services to validate tokens received from other services.
    The token should be provided in the X-Service-Token header.
    The token should be provided in the X-Service-Token header.
    """
    """
    # Get service token from header
    # Get service token from header
    service_token = request.headers.get("X-Service-Token")
    service_token = request.headers.get("X-Service-Token")


    if not service_token:
    if not service_token:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Service token is required in X-Service-Token header",
    detail="Service token is required in X-Service-Token header",
    )
    )


    try:
    try:
    # Validate the service token
    # Validate the service token
    token_payload = validate_service_token(
    token_payload = validate_service_token(
    token=service_token, audience=audience or "api-gateway"
    token=service_token, audience=audience or "api-gateway"
    )
    )


    # Return the validated token payload
    # Return the validated token payload
    return {
    return {
    "valid": True,
    "valid": True,
    "issuer": token_payload.iss,
    "issuer": token_payload.iss,
    "audience": token_payload.aud,
    "audience": token_payload.aud,
    "expires_at": token_payload.exp,
    "expires_at": token_payload.exp,
    "issued_at": token_payload.iat,
    "issued_at": token_payload.iat,
    "token_id": token_payload.jti,
    "token_id": token_payload.jti,
    "claims": token_payload.claims,
    "claims": token_payload.claims,
    }
    }
except ServiceTokenError as e:
except ServiceTokenError as e:
    return {"valid": False, "error": str(e)}
    return {"valid": False, "error": str(e)}
except Exception as e:
except Exception as e:
    logger.error(f"Error validating service token: {str(e)}")
    logger.error(f"Error validating service token: {str(e)}")
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=f"Failed to validate service token: {str(e)}",
    detail=f"Failed to validate service token: {str(e)}",
    )
    )




    @app.middleware("http")
    @app.middleware("http")
    async def route_requests(request: Request, call_next):
    async def route_requests(request: Request, call_next):
    """
    """
    Route requests to the appropriate microservice.
    Route requests to the appropriate microservice.


    This middleware intercepts all requests and routes them to the appropriate
    This middleware intercepts all requests and routes them to the appropriate
    microservice based on the URL path.
    microservice based on the URL path.
    """
    """
    path = request.url.path
    path = request.url.path


    # Skip routing for API Gateway's own endpoints
    # Skip routing for API Gateway's own endpoints
    if (
    if (
    path == "/"
    path == "/"
    or path.startswith("/api/status")
    or path.startswith("/api/status")
    or path.startswith("/api/services")
    or path.startswith("/api/services")
    or path.startswith("/health")
    or path.startswith("/health")
    ):
    ):
    return await call_next(request)
    return await call_next(request)


    # Extract service name from path (e.g., /api/niche-analysis/... -> niche-analysis)
    # Extract service name from path (e.g., /api/niche-analysis/... -> niche-analysis)
    parts = path.split("/")
    parts = path.split("/")
    if len(parts) >= 3 and parts[1] == "api":
    if len(parts) >= 3 and parts[1] == "api":
    service_name = parts[2]
    service_name = parts[2]


    # Map service name from URL to actual service name
    # Map service name from URL to actual service name
    service_name_map = {
    service_name_map = {
    "niche-analysis": "niche-analysis-service",
    "niche-analysis": "niche-analysis-service",
    "ai-models": "ai-models-service",
    "ai-models": "ai-models-service",
    "marketing": "marketing-service",
    "marketing": "marketing-service",
    "monetization": "monetization-service",
    "monetization": "monetization-service",
    "agent-team": "agent-team-service",
    "agent-team": "agent-team-service",
    "ui": "ui-service",
    "ui": "ui-service",
    "auth": "authentication-service",
    "auth": "authentication-service",
    }
    }


    target_service = service_name_map.get(service_name, service_name)
    target_service = service_name_map.get(service_name, service_name)


    # Forward request to target service
    # Forward request to target service
    if service_registration and service_registration.client:
    if service_registration and service_registration.client:
    try:
    try:
    # Get service URL
    # Get service URL
    service_url = service_registration.client.get_service_url(
    service_url = service_registration.client.get_service_url(
    target_service
    target_service
    )
    )
    if not service_url:
    if not service_url:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Service '{target_service}' not found",
    detail=f"Service '{target_service}' not found",
    )
    )


    # Construct target URL
    # Construct target URL
    # Remove the service name from the path to get the service-specific path
    # Remove the service name from the path to get the service-specific path
    service_path = "/" + "/".join(parts[3:])
    service_path = "/" + "/".join(parts[3:])
    target_url = f"{service_url}{service_path}"
    target_url = f"{service_url}{service_path}"


    # Get request body
    # Get request body
    body = await request.body()
    body = await request.body()


    # Get request headers
    # Get request headers
    headers = dict(request.headers)
    headers = dict(request.headers)
    # Remove headers that should not be forwarded
    # Remove headers that should not be forwarded
    headers.pop("host", None)
    headers.pop("host", None)


    # Get query parameters
    # Get query parameters
    params = dict(request.query_params)
    params = dict(request.query_params)


    # Add service token for service-to-service communication
    # Add service token for service-to-service communication
    # Create a token for the API Gateway to authenticate with the target service
    # Create a token for the API Gateway to authenticate with the target service
    try:
    try:
    service_token = create_service_token(
    service_token = create_service_token(
    issuer="api-gateway",
    issuer="api-gateway",
    audience=target_service,
    audience=target_service,
    expiration=300,  # 5 minutes
    expiration=300,  # 5 minutes
    )
    )
    headers["X-Service-Token"] = service_token
    headers["X-Service-Token"] = service_token
except Exception as e:
except Exception as e:
    logger.warning(
    logger.warning(
    f"Failed to create service token for {target_service}: {str(e)}"
    f"Failed to create service token for {target_service}: {str(e)}"
    )
    )


    # Create httpx client
    # Create httpx client
    async with httpx.AsyncClient(timeout=30.0) as client:
    async with httpx.AsyncClient(timeout=30.0) as client:
    # Forward the request to the target service
    # Forward the request to the target service
    start_time = time.time()
    start_time = time.time()
    try:
    try:
    response = await client.request(
    response = await client.request(
    method=request.method,
    method=request.method,
    url=target_url,
    url=target_url,
    headers=headers,
    headers=headers,
    params=params,
    params=params,
    content=body,
    content=body,
    follow_redirects=True,
    follow_redirects=True,
    )
    )


    # Log the request
    # Log the request
    duration = time.time() - start_time
    duration = time.time() - start_time
    logger.info(
    logger.info(
    f"Forwarded {request.method} {path} to {target_service} "
    f"Forwarded {request.method} {path} to {target_service} "
    f"({response.status_code}, {duration:.2f}s)"
    f"({response.status_code}, {duration:.2f}s)"
    )
    )


    # Create FastAPI response from httpx response
    # Create FastAPI response from httpx response
    return Response(
    return Response(
    content=response.content,
    content=response.content,
    status_code=response.status_code,
    status_code=response.status_code,
    headers=dict(response.headers),
    headers=dict(response.headers),
    media_type=response.headers.get("content-type"),
    media_type=response.headers.get("content-type"),
    )
    )
except httpx.RequestError as e:
except httpx.RequestError as e:
    # Handle request errors (connection errors, timeouts, etc.)
    # Handle request errors (connection errors, timeouts, etc.)
    logger.error(
    logger.error(
    f"Error forwarding request to {target_service}: {str(e)}"
    f"Error forwarding request to {target_service}: {str(e)}"
    )
    )
    return JSONResponse(
    return JSONResponse(
    content={"detail": f"Service unavailable: {str(e)}"},
    content={"detail": f"Service unavailable: {str(e)}"},
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )
    )
except HTTPException:
except HTTPException:
    # Re-raise HTTP exceptions
    # Re-raise HTTP exceptions
    raise
    raise
except Exception as e:
except Exception as e:
    # Handle other errors
    # Handle other errors
    logger.error(f"Error routing request to {target_service}: {str(e)}")
    logger.error(f"Error routing request to {target_service}: {str(e)}")
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=f"Failed to route request: {str(e)}",
    detail=f"Failed to route request: {str(e)}",
    )
    )


    # If we get here, just pass the request through
    # If we get here, just pass the request through
    return await call_next(request)
    return await call_next(request)




    def check_service_health() -> bool:
    def check_service_health() -> bool:
    """
    """
    Check if this service is healthy.
    Check if this service is healthy.


    Returns:
    Returns:
    bool: True if healthy, False otherwise
    bool: True if healthy, False otherwise
    """
    """
    # For now, always return True
    # For now, always return True
    # In a real implementation, check database connections, etc.
    # In a real implementation, check database connections, etc.
    return True
    return True




    def register_with_service_registry(port: int):
    def register_with_service_registry(port: int):
    """
    """
    Register this service with the service registry.
    Register this service with the service registry.


    Args:
    Args:
    port: Port this service is running on
    port: Port this service is running on
    """
    """
    global service_registration
    global service_registration


    # Get metadata and tags
    # Get metadata and tags
    metadata = get_service_metadata()
    metadata = get_service_metadata()
    tags = get_default_tags() + ["api", "gateway", "entry-point"]
    tags = get_default_tags() + ["api", "gateway", "entry-point"]


    # Register service
    # Register service
    service_registration = register_service(
    service_registration = register_service(
    app=app,
    app=app,
    service_name="api-gateway",
    service_name="api-gateway",
    port=port,
    port=port,
    version="1.0.0",
    version="1.0.0",
    health_check_path="/health",
    health_check_path="/health",
    check_functions=[check_service_health],
    check_functions=[check_service_health],
    tags=tags,
    tags=tags,
    metadata=metadata,
    metadata=metadata,
    )
    )


    if service_registration:
    if service_registration:
    logger.info("Successfully registered API Gateway with service registry")
    logger.info("Successfully registered API Gateway with service registry")
    else:
    else:
    logger.warning(
    logger.warning(
    "Failed to register with service registry, continuing without service discovery"
    "Failed to register with service registry, continuing without service discovery"
    )
    )




    def start_api_gateway(host: str = "0.0.0.0", port: int = 8000):
    def start_api_gateway(host: str = "0.0.0.0", port: int = 8000):
    """
    """
    Start the API Gateway service.
    Start the API Gateway service.


    Args:
    Args:
    host: Host to bind to
    host: Host to bind to
    port: Port to listen on
    port: Port to listen on
    """
    """




    # Register with service registry
    # Register with service registry
    register_with_service_registry(port)
    register_with_service_registry(port)


    # Start the API Gateway
    # Start the API Gateway
    uvicorn.run(app, host=host, port=port)
    uvicorn.run(app, host=host, port=port)




    if __name__ == "__main__":
    if __name__ == "__main__":
    # Parse command line arguments
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="API Gateway service")
    parser = argparse.ArgumentParser(description="API Gateway service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")


    args = parser.parse_args(
    args = parser.parse_args(


    # Start the API Gateway
    # Start the API Gateway
    start_api_gateway(host=args.host, port=args.port
    start_api_gateway(host=args.host, port=args.port
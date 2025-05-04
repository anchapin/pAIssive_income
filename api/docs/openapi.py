"""
OpenAPI documentation customization.

This module provides functions for customizing the OpenAPI documentation.
"""


import logging
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi as fastapi_get_openapi

FASTAPI_AVAILABLE

# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    = True
except ImportError:
    logger.warning("FastAPI is required for OpenAPI documentation")
    FASTAPI_AVAILABLE = False


    def get_openapi_schema(
    app: Any, title: str, version: str, description: str
    ) -> Dict[str, Any]:
    """
    Get the OpenAPI schema for the API server.

    Args:
    app: FastAPI application
    title: API title
    version: API version
    description: API description

    Returns:
    OpenAPI schema
    """
    if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI is required for OpenAPI documentation")
    return {}

    # Create OpenAPI schema
    openapi_schema = fastapi_get_openapi(
    title=title,
    version=version,
    description=description,
    routes=app.routes,
    )

    # Add custom components
    openapi_schema["components"] = openapi_schema.get("components", {})

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
    "ApiKeyAuth": {
    "type": "apiKey",
    "in": "header",
    "name": "X-API-Key",
    "description": "API key authentication",
    },
    "BearerAuth": {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT",
    "description": "JWT authentication",
    },
    }

    # Add security requirement
    openapi_schema["security"] = [{"ApiKeyAuth": []}, {"BearerAuth": []}]

    # Add custom info
    openapi_schema["info"] = {
    "title": title,
    "version": version,
    "description": description,
    "termsOfService": "https://example.com/terms/",
    "contact": {
    "name": "pAIssive Income Support",
    "url": "https://example.com/contact/",
    "email": "support@example.com",
    },
    "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    }

    # Add servers
    openapi_schema["servers"] = [
    {"url": "/", "description": "Current server"},
    {"url": "https://api.example.com", "description": "Production server"},
    {"url": "https://staging-api.example.com", "description": "Staging server"},
    ]

    # Add tags
    openapi_schema["tags"] = [
    {
    "name": "Niche Analysis",
    "description": "Operations related to niche analysis",
    "externalDocs": {
    "description": "Niche Analysis Documentation",
    "url": "https://example.com/docs/niche-analysis/",
    },
    },
    {
    "name": "Monetization",
    "description": "Operations related to monetization",
    "externalDocs": {
    "description": "Monetization Documentation",
    "url": "https://example.com/docs/monetization/",
    },
    },
    {
    "name": "Marketing",
    "description": "Operations related to marketing",
    "externalDocs": {
    "description": "Marketing Documentation",
    "url": "https://example.com/docs/marketing/",
    },
    },
    {
    "name": "AI Models",
    "description": "Operations related to AI models",
    "externalDocs": {
    "description": "AI Models Documentation",
    "url": "https://example.com/docs/ai-models/",
    },
    },
    {
    "name": "Agent Team",
    "description": "Operations related to agent teams",
    "externalDocs": {
    "description": "Agent Team Documentation",
    "url": "https://example.com/docs/agent-team/",
    },
    },
    {
    "name": "User",
    "description": "Operations related to users",
    "externalDocs": {
    "description": "User Documentation",
    "url": "https://example.com/docs/user/",
    },
    },
    {
    "name": "Dashboard",
    "description": "Operations related to the dashboard",
    "externalDocs": {
    "description": "Dashboard Documentation",
    "url": "https://example.com/docs/dashboard/",
    },
    },
    ]

    # Add external docs
    openapi_schema["externalDocs"] = {
    "description": "pAIssive Income Documentation",
    "url": "https://example.com/docs/",
    }

    return openapi_schema


    def setup_openapi(app: Any, title: str, version: str, description: str) -> None:
    """
    Set up OpenAPI documentation for the API server.

    Args:
    app: FastAPI application
    title: API title
    version: API version
    description: API description
    """
    if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI is required for OpenAPI documentation")
    return # Create OpenAPI schema
    openapi_schema = get_openapi_schema(app, title, version, description)

    # Set OpenAPI schema
    app.openapi_schema = openapi_schema

    # Override the openapi function
    def custom_openapi() -> Dict[str, Any]:
    return app.openapi_schema

    app.openapi = custom_openapi
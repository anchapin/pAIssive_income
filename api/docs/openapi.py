"""
"""
OpenAPI documentation customization.
OpenAPI documentation customization.


This module provides functions for customizing the OpenAPI documentation.
This module provides functions for customizing the OpenAPI documentation.
"""
"""




import logging
import logging
from typing import Any, Dict
from typing import Any, Dict


from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi as fastapi_get_openapi
from fastapi.openapi.utils import get_openapi as fastapi_get_openapi


FASTAPI_AVAILABLE
FASTAPI_AVAILABLE


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


# Try to import FastAPI
# Try to import FastAPI
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning("FastAPI is required for OpenAPI documentation")
    logger.warning("FastAPI is required for OpenAPI documentation")
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False




    def get_openapi_schema(
    def get_openapi_schema(
    app: Any, title: str, version: str, description: str
    app: Any, title: str, version: str, description: str
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get the OpenAPI schema for the API server.
    Get the OpenAPI schema for the API server.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    title: API title
    title: API title
    version: API version
    version: API version
    description: API description
    description: API description


    Returns:
    Returns:
    OpenAPI schema
    OpenAPI schema
    """
    """
    if not FASTAPI_AVAILABLE:
    if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI is required for OpenAPI documentation")
    logger.warning("FastAPI is required for OpenAPI documentation")
    return {}
    return {}


    # Create OpenAPI schema
    # Create OpenAPI schema
    openapi_schema = fastapi_get_openapi(
    openapi_schema = fastapi_get_openapi(
    title=title,
    title=title,
    version=version,
    version=version,
    description=description,
    description=description,
    routes=app.routes,
    routes=app.routes,
    )
    )


    # Add custom components
    # Add custom components
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"] = openapi_schema.get("components", {})


    # Add security schemes
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
    openapi_schema["components"]["securitySchemes"] = {
    "ApiKeyAuth": {
    "ApiKeyAuth": {
    "type": "apiKey",
    "type": "apiKey",
    "in": "header",
    "in": "header",
    "name": "X-API-Key",
    "name": "X-API-Key",
    "description": "API key authentication",
    "description": "API key authentication",
    },
    },
    "BearerAuth": {
    "BearerAuth": {
    "type": "http",
    "type": "http",
    "scheme": "bearer",
    "scheme": "bearer",
    "bearerFormat": "JWT",
    "bearerFormat": "JWT",
    "description": "JWT authentication",
    "description": "JWT authentication",
    },
    },
    }
    }


    # Add security requirement
    # Add security requirement
    openapi_schema["security"] = [{"ApiKeyAuth": []}, {"BearerAuth": []}]
    openapi_schema["security"] = [{"ApiKeyAuth": []}, {"BearerAuth": []}]


    # Add custom info
    # Add custom info
    openapi_schema["info"] = {
    openapi_schema["info"] = {
    "title": title,
    "title": title,
    "version": version,
    "version": version,
    "description": description,
    "description": description,
    "termsOfService": "https://example.com/terms/",
    "termsOfService": "https://example.com/terms/",
    "contact": {
    "contact": {
    "name": "pAIssive Income Support",
    "name": "pAIssive Income Support",
    "url": "https://example.com/contact/",
    "url": "https://example.com/contact/",
    "email": "support@example.com",
    "email": "support@example.com",
    },
    },
    "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    }
    }


    # Add servers
    # Add servers
    openapi_schema["servers"] = [
    openapi_schema["servers"] = [
    {"url": "/", "description": "Current server"},
    {"url": "/", "description": "Current server"},
    {"url": "https://api.example.com", "description": "Production server"},
    {"url": "https://api.example.com", "description": "Production server"},
    {"url": "https://staging-api.example.com", "description": "Staging server"},
    {"url": "https://staging-api.example.com", "description": "Staging server"},
    ]
    ]


    # Add tags
    # Add tags
    openapi_schema["tags"] = [
    openapi_schema["tags"] = [
    {
    {
    "name": "Niche Analysis",
    "name": "Niche Analysis",
    "description": "Operations related to niche analysis",
    "description": "Operations related to niche analysis",
    "externalDocs": {
    "externalDocs": {
    "description": "Niche Analysis Documentation",
    "description": "Niche Analysis Documentation",
    "url": "https://example.com/docs/niche-analysis/",
    "url": "https://example.com/docs/niche-analysis/",
    },
    },
    },
    },
    {
    {
    "name": "Monetization",
    "name": "Monetization",
    "description": "Operations related to monetization",
    "description": "Operations related to monetization",
    "externalDocs": {
    "externalDocs": {
    "description": "Monetization Documentation",
    "description": "Monetization Documentation",
    "url": "https://example.com/docs/monetization/",
    "url": "https://example.com/docs/monetization/",
    },
    },
    },
    },
    {
    {
    "name": "Marketing",
    "name": "Marketing",
    "description": "Operations related to marketing",
    "description": "Operations related to marketing",
    "externalDocs": {
    "externalDocs": {
    "description": "Marketing Documentation",
    "description": "Marketing Documentation",
    "url": "https://example.com/docs/marketing/",
    "url": "https://example.com/docs/marketing/",
    },
    },
    },
    },
    {
    {
    "name": "AI Models",
    "name": "AI Models",
    "description": "Operations related to AI models",
    "description": "Operations related to AI models",
    "externalDocs": {
    "externalDocs": {
    "description": "AI Models Documentation",
    "description": "AI Models Documentation",
    "url": "https://example.com/docs/ai-models/",
    "url": "https://example.com/docs/ai-models/",
    },
    },
    },
    },
    {
    {
    "name": "Agent Team",
    "name": "Agent Team",
    "description": "Operations related to agent teams",
    "description": "Operations related to agent teams",
    "externalDocs": {
    "externalDocs": {
    "description": "Agent Team Documentation",
    "description": "Agent Team Documentation",
    "url": "https://example.com/docs/agent-team/",
    "url": "https://example.com/docs/agent-team/",
    },
    },
    },
    },
    {
    {
    "name": "User",
    "name": "User",
    "description": "Operations related to users",
    "description": "Operations related to users",
    "externalDocs": {
    "externalDocs": {
    "description": "User Documentation",
    "description": "User Documentation",
    "url": "https://example.com/docs/user/",
    "url": "https://example.com/docs/user/",
    },
    },
    },
    },
    {
    {
    "name": "Dashboard",
    "name": "Dashboard",
    "description": "Operations related to the dashboard",
    "description": "Operations related to the dashboard",
    "externalDocs": {
    "externalDocs": {
    "description": "Dashboard Documentation",
    "description": "Dashboard Documentation",
    "url": "https://example.com/docs/dashboard/",
    "url": "https://example.com/docs/dashboard/",
    },
    },
    },
    },
    ]
    ]


    # Add external docs
    # Add external docs
    openapi_schema["externalDocs"] = {
    openapi_schema["externalDocs"] = {
    "description": "pAIssive Income Documentation",
    "description": "pAIssive Income Documentation",
    "url": "https://example.com/docs/",
    "url": "https://example.com/docs/",
    }
    }


    return openapi_schema
    return openapi_schema




    def setup_openapi(app: Any, title: str, version: str, description: str) -> None:
    def setup_openapi(app: Any, title: str, version: str, description: str) -> None:
    """
    """
    Set up OpenAPI documentation for the API server.
    Set up OpenAPI documentation for the API server.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    title: API title
    title: API title
    version: API version
    version: API version
    description: API description
    description: API description
    """
    """
    if not FASTAPI_AVAILABLE:
    if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI is required for OpenAPI documentation")
    logger.warning("FastAPI is required for OpenAPI documentation")
    return # Create OpenAPI schema
    return # Create OpenAPI schema
    openapi_schema = get_openapi_schema(app, title, version, description)
    openapi_schema = get_openapi_schema(app, title, version, description)


    # Set OpenAPI schema
    # Set OpenAPI schema
    app.openapi_schema = openapi_schema
    app.openapi_schema = openapi_schema


    # Override the openapi function
    # Override the openapi function
    def custom_openapi() -> Dict[str, Any]:
    def custom_openapi() -> Dict[str, Any]:
    return app.openapi_schema
    return app.openapi_schema


    app.openapi = custom_openapi
    app.openapi = custom_openapi
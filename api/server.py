"""
RESTful API server for the pAIssive Income project.
"""

import logging
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import config
from .config import APIConfig, APIVersion

# Import middleware
from .middleware.auth import AuthMiddleware, verify_token
from .middleware.webhook_security import WebhookIPAllowlistMiddleware, 
    WebhookRateLimitMiddleware
from .routes.agent_team_router import router as agent_team_router
from .routes.ai_models_router import router as ai_models_router
from .routes.analytics_router import router as analytics_router
from .routes.api_key_router import router as api_key_router
from .routes.dashboard_router import router as dashboard_router
from .routes.developer_router import router as developer_router
from .routes.marketing_router import router as marketing_router
from .routes.monetization_router import router as monetization_router

# Import routers
from .routes.niche_analysis_router import router as niche_analysis_router
from .routes.user_router import router as user_router
from .routes.webhook_router import router as webhook_router

# Import security services
from .services.webhook_security import WebhookIPAllowlist, WebhookRateLimiter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIServer:
    """RESTful API server for all core services."""

    def __init__(self, config: APIConfig):
        """Initialize the API server."""
        self.config = config
        self.app = FastAPI(
            title=config.title or "pAIssive Income API",
            description=config.description or "RESTful API for pAIssive Income services",
                
            version=config.version.value,
            docs_url=config.docs_url,
            openapi_url=config.openapi_url,
            redoc_url=config.redoc_url,
        )
        self._setup_middleware()
        self._setup_routes()
        self._setup_exception_handlers()

    def _setup_middleware(self) -> None:
        """Set up middleware for the server."""
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=[" * "],
            allow_headers=[" * "],
        )

        # Add security middleware
        if self.config.enable_auth:
            # Create security services
            webhook_ip_allowlist = WebhookIPAllowlist()
            webhook_rate_limiter = WebhookRateLimiter(limit=100, window_seconds=60)

            # Configure default allowed IPs for webhooks
            for ip in self.config.webhook_allowed_ips:
                webhook_ip_allowlist.add_ip(ip)

            # Add security middleware
            self.app.add_middleware(
                AuthMiddleware,
                public_paths=[" / health", " / version", " / docs", " / redoc", 
                    " / openapi.json"],
            )
            self.app.add_middleware(
                WebhookIPAllowlistMiddleware,
                allowlist=webhook_ip_allowlist,
                webhook_path_prefix=" / api / v1 / webhooks",
            )
            self.app.add_middleware(
                WebhookRateLimitMiddleware,
                rate_limiter=webhook_rate_limiter,
                webhook_path_prefix=" / api / v1 / webhooks",
            )

    def _setup_exception_handlers(self) -> None:
        """Set up exception handlers for the server."""

        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            """Global exception handler."""
            logger.error(f"Unhandled exception: {str(exc)}")
            return JSONResponse(
                status_code=500,
                content={"error": {"message": "Internal server error", 
                    "details": str(exc)}},
            )

    def _setup_routes(self) -> None:
        """Set up routes for the server."""

        # Add health check endpoint
        @self.app.get(" / health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "ok"}

        # Add API version endpoint
        @self.app.get(" / version")
        async def version():
            """API version endpoint."""
            return {"version": self.config.version.value}

        # Set up routes for each active version
        for version in self.config.active_versions:
            self._setup_version_routes(version)

    def _setup_version_routes(self, version: APIVersion) -> None:
        """Set up routes for a specific API version."""
        # Create version prefix
        version_prefix = f" / api / v{version.value}"

        # Include core routers with proper tags
        self.app.include_router(user_router, prefix=f"{version_prefix}/user", 
            tags=["User"])

        if self.config.enable_auth:
            self.app.include_router(
                api_key_router,
                prefix=f"{version_prefix}/api - keys",
                tags=["API Keys"],
                dependencies=[Depends(verify_token)],
            )

        if self.config.enable_niche_analysis:
            self.app.include_router(
                niche_analysis_router,
                prefix=f"{version_prefix}/niche - analysis",
                tags=["Niche Analysis"],
            )

        if self.config.enable_monetization:
            self.app.include_router(
                monetization_router, prefix=f"{version_prefix}/monetization", 
                    tags=["Monetization"]
            )

        if self.config.enable_marketing:
            self.app.include_router(
                marketing_router, prefix=f"{version_prefix}/marketing", 
                    tags=["Marketing"]
            )

        if self.config.enable_ai_models:
            self.app.include_router(
                ai_models_router, prefix=f"{version_prefix}/ai - models", 
                    tags=["AI Models"]
            )

        if self.config.enable_agent_team:
            self.app.include_router(
                agent_team_router, prefix=f"{version_prefix}/agent - team", 
                    tags=["Agent Team"]
            )

        if self.config.enable_dashboard:
            self.app.include_router(
                dashboard_router, prefix=f"{version_prefix}/dashboard", 
                    tags=["Dashboard"]
            )

        if self.config.enable_analytics:
            self.app.include_router(
                analytics_router, prefix=f"{version_prefix}/analytics", 
                    tags=["Analytics"]
            )

        if self.config.enable_developer:
            self.app.include_router(
                developer_router, prefix=f"{version_prefix}/developer", 
                    tags=["Developer"]
            )

        # Webhook router should be protected by auth
        if self.config.enable_auth:
            self.app.include_router(
                webhook_router, prefix=f"{version_prefix}/webhooks", tags=["Webhooks"]
            )

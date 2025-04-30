"""
RESTful API server for the pAIssive Income project.
"""

import logging
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from .routes.niche_analysis_router import router as niche_analysis_router
from .routes.monetization_router import router as monetization_router
from .routes.marketing_router import router as marketing_router
from .routes.ai_models_router import router as ai_models_router
from .routes.agent_team_router import router as agent_team_router
from .routes.user_router import router as user_router
from .routes.dashboard_router import router as dashboard_router
from .routes.api_key_router import router as api_key_router
from .routes.webhook_router import router as webhook_router
from .routes.analytics_router import router as analytics_router
from .routes.developer_router import router as developer_router

# Import middleware
from .middleware.auth import verify_token

# Import config
from .config import APIConfig, APIVersion

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIServer:
    """RESTful API server for all core services."""

    def __init__(self, config: APIConfig):
        """Initialize the API server."""
        self.config = config
        self.app = FastAPI(
            title=config.title,
            description=config.description,
            version=config.version
        )
        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self) -> None:
        """Set up middleware for the server."""
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )

    def _setup_routes(self) -> None:
        """Set up routes for the server."""
        # Set up routes for each active version
        for version in self.config.active_versions:
            self._setup_version_routes(version)

    def _setup_version_routes(self, version: APIVersion) -> None:
        """Set up routes for a specific API version."""
        # Include routers based on configuration
        if self.config.enable_niche_analysis:
            self.app.include_router(niche_analysis_router, prefix="/niche-analysis")

        if self.config.enable_monetization:
            self.app.include_router(monetization_router, prefix="/monetization")

        if self.config.enable_marketing:
            self.app.include_router(marketing_router, prefix="/marketing")

        if self.config.enable_ai_models:
            self.app.include_router(ai_models_router, prefix="/ai-models")

        if self.config.enable_agent_team:
            self.app.include_router(agent_team_router, prefix="/agent-team")

        # User router - always enabled
        self.app.include_router(user_router, prefix="/user")

        if self.config.enable_dashboard:
            self.app.include_router(dashboard_router, prefix="/dashboard")

        if self.config.enable_auth:
            self.app.include_router(api_key_router, prefix="/api-keys")
            self.app.include_router(webhook_router, prefix="/webhooks")

        if self.config.enable_analytics:
            self.app.include_router(analytics_router, prefix="/analytics")

        if self.config.enable_developer:
            self.app.include_router(developer_router, prefix="/developer")

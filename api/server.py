"""
API server for the pAIssive Income project.

This module provides a RESTful API server for all core services.
"""

import os
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Union, Type, Tuple

from .config import APIConfig, APIVersion
from .middleware import setup_middleware
from .version_manager import VersionManager
from .routes import (
    niche_analysis_router,
    monetization_router,
    marketing_router,
    ai_models_router,
    agent_team_router,
    user_router,
    dashboard_router,
    api_key_router
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    import uvicorn
    from fastapi import FastAPI, Depends
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI and uvicorn are required for API server")
    FASTAPI_AVAILABLE = False


class APIServer:
    """
    RESTful API server for all core services.
    """

    def __init__(self, config: APIConfig):
        """
        Initialize the API server.

        Args:
            config: Server configuration
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI and uvicorn are required for API server")

        self.config = config

        # Initialize server
        self.app = None
        self.server = None
        self.server_thread = None
        self.start_time = None

        # Initialize version manager
        self.version_manager = VersionManager()

        # Initialize metrics
        self.request_count = 0
        self.error_count = 0
        self.latencies = []

    def start(self) -> None:
        """
        Start the API server.
        """
        if self.is_running():
            logger.warning("Server is already running")
            return

        # Create FastAPI app
        self.app = FastAPI(
            title="pAIssive Income API",
            description="RESTful API for pAIssive Income services",
            version=self.config.version.value,
            docs_url=self.config.docs_url,
            openapi_url=self.config.openapi_url,
            redoc_url=self.config.redoc_url,
            terms_of_service="/api/docs/terms",
            contact={
                "name": "API Support",
                "email": "api-support@paissive-income.com",
                "url": "https://paissive-income.com/support",
            },
            license_info={
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT",
            },
        )

        # Add custom OpenAPI info
        def custom_openapi():
            if self.app.openapi_schema:
                return self.app.openapi_schema

            openapi_schema = get_openapi(
                title=self.app.title,
                version=self.app.version,
                description=self.app.description + "\n\n" + self._get_version_info_description(),
                routes=self.app.routes,
                terms_of_service=self.app.terms_of_service,
                contact=self.app.contact,
                license_info=self.app.license_info,
            )

            # Add API version information
            openapi_schema["info"]["x-api-versions"] = {
                "current": self.config.version.value,
                "active": [v.value for v in self.config.active_versions],
                "latest": APIVersion.latest_version().value,
                "deprecated": [
                    v.value for v in self.config.active_versions
                    if any(
                        change.get("from_version") == v.value
                        for change in self.version_manager.get_deprecated_endpoints()
                    )
                ],
            }

            self.app.openapi_schema = openapi_schema
            return self.app.openapi_schema

        # Import get_openapi here to avoid circular imports
        from fastapi.openapi.utils import get_openapi
        self.app.openapi = custom_openapi

        # Set up middleware
        setup_middleware(self.app, self.config, self.version_manager)

        # Set up routes
        self._setup_routes()

        # Start server
        self.start_time = time.time()
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self.server_thread.start()

        logger.info(f"Server started at http://{self.config.host}:{self.config.port}")

    def stop(self) -> None:
        """
        Stop the API server.
        """
        if not self.is_running():
            logger.warning("Server is not running")
            return

        # Stop server
        if self.server:
            self.server.should_exit = True
            self.server.force_exit = True
            self.server = None

        # Wait for server thread to stop
        if self.server_thread:
            self.server_thread.join(timeout=5)
            self.server_thread = None

        logger.info("Server stopped")

    def is_running(self) -> bool:
        """
        Check if the server is running.

        Returns:
            True if the server is running, False otherwise
        """
        return self.server_thread is not None and self.server_thread.is_alive()

    def get_uptime(self) -> float:
        """
        Get the server uptime in seconds.

        Returns:
            Server uptime in seconds
        """
        if self.start_time is None:
            return 0

        return time.time() - self.start_time

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get server metrics.

        Returns:
            Server metrics
        """
        uptime = self.get_uptime()

        return {
            "uptime": uptime,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(1, self.request_count),
            "requests_per_second": self.request_count / max(1, uptime),
            "average_latency": sum(self.latencies) / max(1, len(self.latencies)) if self.latencies else 0,
        }

    def _get_version_info_description(self) -> str:
        """
        Get version information for the API documentation.

        Returns:
            Markdown-formatted version information
        """
        active_versions = [v.value for v in self.config.active_versions]
        latest_version = APIVersion.latest_version().value
        current_version = self.config.version.value

        # Get deprecated versions
        deprecated_versions = [
            v.value for v in self.config.active_versions
            if any(
                change.get("from_version") == v.value
                for change in self.version_manager.get_deprecated_endpoints()
            )
        ]

        # Build description
        description = "## API Versioning\n\n"
        description += "This API supports multiple versions. "
        description += "The version is specified in the URL path (e.g., `/api/v1/niche-analysis`).\n\n"

        description += "### Available Versions\n\n"
        description += "| Version | Status | Notes |\n"
        description += "|---------|--------|-------|\n"

        for version in sorted(active_versions):
            status = "Latest" if version == latest_version else "Active"
            status = "Deprecated" if version in deprecated_versions else status
            status = f"**{status}**" if version == current_version else status

            notes = []
            if version == latest_version:
                notes.append("Recommended for new integrations")
            if version in deprecated_versions:
                # Get sunset date
                sunset_dates = [
                    change.get("sunset_date")
                    for change in self.version_manager.get_deprecated_endpoints()
                    if change.get("from_version") == version and change.get("sunset_date")
                ]
                if sunset_dates:
                    notes.append(f"Will be removed on {min(sunset_dates)}")

            description += f"| {version} | {status} | {', '.join(notes)} |\n"

        description += "\n### Version Discovery\n\n"
        description += "You can discover available API versions using the following endpoints:\n\n"
        description += f"- `GET {self.config.prefix}/versions`: Returns a list of available API versions.\n"
        description += f"- `GET {self.config.prefix}/changelog`: Returns a changelog for all API versions.\n"
        description += f"- `GET {self.config.prefix}/changelog/{{version}}`: Returns a changelog for a specific API version.\n\n"

        description += "For more information on the API versioning strategy, see the [API Versioning Documentation](/api/docs/versioning).\n"

        return description

    def _run_server(self) -> None:
        """
        Run the uvicorn server.
        """
        # Set up uvicorn config
        uvicorn_config = uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            workers=1,
            timeout_keep_alive=60,
            log_level=self.config.log_level.lower(),
            ssl_keyfile=self.config.ssl_keyfile if self.config.enable_https else None,
            ssl_certfile=self.config.ssl_certfile if self.config.enable_https else None
        )

        # Create and run server
        self.server = uvicorn.Server(uvicorn_config)
        self.server.run()

    def _setup_routes(self) -> None:
        """
        Set up routes for the server.
        """
        # Set up routes for each active version
        for version in self.config.active_versions:
            self._setup_version_routes(version)

        # Set up version-agnostic routes (like health checks, version info, etc.)
        self._setup_version_info_routes()

    def _setup_version_routes(self, version: APIVersion) -> None:
        """
        Set up routes for a specific API version.

        Args:
            version: API version to set up routes for
        """
        api_prefix = f"{self.config.prefix}/{version}"
        version_tag = f"v{version}"

        # Add module-specific routes
        if self.config.enable_niche_analysis:
            self.app.include_router(
                niche_analysis_router,
                prefix=f"{api_prefix}/niche-analysis",
                tags=[f"Niche Analysis {version_tag}"]
            )

        if self.config.enable_monetization:
            self.app.include_router(
                monetization_router,
                prefix=f"{api_prefix}/monetization",
                tags=[f"Monetization {version_tag}"]
            )

        if self.config.enable_marketing:
            self.app.include_router(
                marketing_router,
                prefix=f"{api_prefix}/marketing",
                tags=[f"Marketing {version_tag}"]
            )

        if self.config.enable_ai_models:
            self.app.include_router(
                ai_models_router,
                prefix=f"{api_prefix}/ai-models",
                tags=[f"AI Models {version_tag}"]
            )

        if self.config.enable_agent_team:
            self.app.include_router(
                agent_team_router,
                prefix=f"{api_prefix}/agent-team",
                tags=[f"Agent Team {version_tag}"]
            )

        if self.config.enable_user:
            self.app.include_router(
                user_router,
                prefix=f"{api_prefix}/user",
                tags=[f"User {version_tag}"]
            )

        if self.config.enable_dashboard:
            self.app.include_router(
                dashboard_router,
                prefix=f"{api_prefix}/dashboard",
                tags=[f"Dashboard {version_tag}"]
            )

        # Add API key routes
        if self.config.enable_auth:
            self.app.include_router(
                api_key_router,
                prefix=f"{api_prefix}",
                tags=[f"API Keys {version_tag}"]
            )

    def _setup_version_info_routes(self) -> None:
        """
        Set up routes for version information.
        """
        if not FASTAPI_AVAILABLE:
            return

        from fastapi import APIRouter, Response, HTTPException
        from pydantic import BaseModel

        # Create router for version info
        version_router = APIRouter()

        # Define response models
        class VersionInfo(BaseModel):
            version: str
            is_latest: bool
            is_deprecated: bool = False
            sunset_date: Optional[str] = None

        class VersionsResponse(BaseModel):
            versions: List[VersionInfo]
            latest_version: str

        class ChangelogResponse(BaseModel):
            changelog: Dict[str, List[Dict[str, Any]]]

        # Get versions endpoint
        @version_router.get(
            "/versions",
            response_model=VersionsResponse,
            tags=["API Versions"],
            summary="Get available API versions"
        )
        async def get_versions():
            versions = []
            latest = APIVersion.latest_version().value

            for version in self.config.active_versions:
                version_value = version.value
                deprecated_endpoints = self.version_manager.get_deprecated_endpoints()

                # Check if this version has any deprecated endpoints
                is_deprecated = any(
                    change.get("from_version") == version_value
                    for change in deprecated_endpoints
                )

                # Get the earliest sunset date for this version's deprecated endpoints
                sunset_dates = [
                    change.get("sunset_date")
                    for change in deprecated_endpoints
                    if change.get("from_version") == version_value
                ]
                sunset_date = min(sunset_dates) if sunset_dates else None

                versions.append(
                    VersionInfo(
                        version=version_value,
                        is_latest=(version_value == latest),
                        is_deprecated=is_deprecated,
                        sunset_date=sunset_date
                    )
                )

            return VersionsResponse(
                versions=versions,
                latest_version=latest
            )

        # Get changelog endpoint
        @version_router.get(
            "/changelog",
            response_model=ChangelogResponse,
            tags=["API Versions"],
            summary="Get API changelog"
        )
        async def get_changelog():
            return ChangelogResponse(
                changelog=self.version_manager.get_changelog()
            )

        # Get version-specific changelog endpoint
        @version_router.get(
            "/changelog/{version}",
            tags=["API Versions"],
            summary="Get changelog for a specific API version"
        )
        async def get_version_changelog(version: str):
            if not APIVersion.is_valid_version(version):
                raise HTTPException(status_code=404, detail=f"Version {version} not found")

            for v in APIVersion:
                if v.value == version:
                    return {"changes": self.version_manager.get_changes_for_version(v)}

            raise HTTPException(status_code=404, detail=f"Version {version} not found")

        # Include the version router
        self.app.include_router(
            version_router,
            prefix=f"{self.config.prefix}",
            tags=["API Versions"]
        )

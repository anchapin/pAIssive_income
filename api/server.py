"""
API server for the pAIssive Income project.

This module provides a RESTful API server for all core services.
"""

import os
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Union, Type, Tuple

from .config import APIConfig
from .middleware import setup_middleware
from .routes import (
    niche_analysis_router,
    monetization_router,
    marketing_router,
    ai_models_router,
    agent_team_router,
    user_router,
    dashboard_router
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
            version=self.config.version,
            docs_url=self.config.docs_url,
            openapi_url=self.config.openapi_url,
            redoc_url=self.config.redoc_url
        )
        
        # Set up middleware
        setup_middleware(self.app, self.config)
        
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
        api_prefix = f"{self.config.prefix}/{self.config.version}"
        
        # Add module-specific routes
        if self.config.enable_niche_analysis:
            self.app.include_router(
                niche_analysis_router,
                prefix=f"{api_prefix}/niche-analysis",
                tags=["Niche Analysis"]
            )
        
        if self.config.enable_monetization:
            self.app.include_router(
                monetization_router,
                prefix=f"{api_prefix}/monetization",
                tags=["Monetization"]
            )
        
        if self.config.enable_marketing:
            self.app.include_router(
                marketing_router,
                prefix=f"{api_prefix}/marketing",
                tags=["Marketing"]
            )
        
        if self.config.enable_ai_models:
            self.app.include_router(
                ai_models_router,
                prefix=f"{api_prefix}/ai-models",
                tags=["AI Models"]
            )
        
        if self.config.enable_agent_team:
            self.app.include_router(
                agent_team_router,
                prefix=f"{api_prefix}/agent-team",
                tags=["Agent Team"]
            )
        
        if self.config.enable_user:
            self.app.include_router(
                user_router,
                prefix=f"{api_prefix}/user",
                tags=["User"]
            )
        
        if self.config.enable_dashboard:
            self.app.include_router(
                dashboard_router,
                prefix=f"{api_prefix}/dashboard",
                tags=["Dashboard"]
            )

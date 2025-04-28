"""
Configuration for the API server.

This module provides configuration classes for the API server.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class APIVersion(str, Enum):
    """API version enumeration."""
    V1 = "v1"


@dataclass
class APIConfig:
    """
    Configuration for the API server.
    """
    # Basic configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # API configuration
    version: APIVersion = APIVersion.V1
    prefix: str = "/api"
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    
    # Middleware configuration
    enable_cors: bool = True
    enable_gzip: bool = True
    enable_https: bool = False
    enable_auth: bool = False
    enable_rate_limit: bool = False
    
    # HTTPS configuration
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    
    # Authentication configuration
    api_keys: List[str] = field(default_factory=list)
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24  # 24 hours
    
    # Rate limiting configuration
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # 1 minute
    
    # Module configuration
    enable_niche_analysis: bool = True
    enable_monetization: bool = True
    enable_marketing: bool = True
    enable_ai_models: bool = True
    enable_agent_team: bool = True
    enable_user: bool = True
    enable_dashboard: bool = True
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

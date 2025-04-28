"""
Middleware for the API server.

This module provides middleware components for the API server.
"""

from .auth import AuthMiddleware
from .rate_limit import RateLimitMiddleware
from .cors import CORSMiddleware
from .version import VersionMiddleware
from .setup import setup_middleware

__all__ = [
    'AuthMiddleware',
    'RateLimitMiddleware',
    'CORSMiddleware',
    'VersionMiddleware',
    'setup_middleware',
]

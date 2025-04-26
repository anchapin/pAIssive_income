"""
REST API server for AI models.

This package provides a REST API server for serving AI models.
"""

from .server import RESTServer, RESTConfig
from .middleware import AuthMiddleware, RateLimitMiddleware
from .routes import (
    text_generation_router, text_classification_router,
    embedding_router, image_router, audio_router
)

__all__ = [
    'RESTServer',
    'RESTConfig',
    'AuthMiddleware',
    'RateLimitMiddleware',
    'text_generation_router',
    'text_classification_router',
    'embedding_router',
    'image_router',
    'audio_router',
]

"""
REST API server for AI models.

This package provides a REST API server for serving AI models.
"""


from .middleware import AuthMiddleware, RateLimitMiddleware
from .server import RESTConfig, RESTServer

__all__

(
audio_router,
embedding_router,
image_router,
text_classification_router,
text_generation_router,
)
= [
"RESTServer",
"RESTConfig",
"AuthMiddleware",
"RateLimitMiddleware",
"text_generation_router",
"text_classification_router",
"embedding_router",
"image_router",
"audio_router",
]
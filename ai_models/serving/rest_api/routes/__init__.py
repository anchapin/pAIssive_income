"""
Routes for REST API server.

This package provides route handlers for the REST API server.
"""


from .audio import router as audio_router
from .embedding import router as embedding_router
from .health import router as health_router
from .image import router as image_router
from .metrics import router as metrics_router
from .text_classification import router as text_classification_router
from .text_generation import router as text_generation_router

__all__

= [
"text_generation_router",
"text_classification_router",
"embedding_router",
"image_router",
"audio_router",
"health_router",
"metrics_router",
]
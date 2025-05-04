"""
"""
REST API server for AI models.
REST API server for AI models.


This package provides a REST API server for serving AI models.
This package provides a REST API server for serving AI models.
"""
"""




from .middleware import AuthMiddleware, RateLimitMiddleware
from .middleware import AuthMiddleware, RateLimitMiddleware
from .server import RESTConfig, RESTServer
from .server import RESTConfig, RESTServer


__all__
__all__


(
(
audio_router,
audio_router,
embedding_router,
embedding_router,
image_router,
image_router,
text_classification_router,
text_classification_router,
text_generation_router,
text_generation_router,
)
)
= [
= [
"RESTServer",
"RESTServer",
"RESTConfig",
"RESTConfig",
"AuthMiddleware",
"AuthMiddleware",
"RateLimitMiddleware",
"RateLimitMiddleware",
"text_generation_router",
"text_generation_router",
"text_classification_router",
"text_classification_router",
"embedding_router",
"embedding_router",
"image_router",
"image_router",
"audio_router",
"audio_router",
]
]
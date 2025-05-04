"""
"""
Embedding routes for REST API server.
Embedding routes for REST API server.


This module provides route handlers for embeddings.
This module provides route handlers for embeddings.
"""
"""




from typing import Dict, List, Optional, Union
from typing import Dict, List, Optional, Union


from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, ConfigDict, Field


FASTAPI_AVAILABLE
FASTAPI_AVAILABLE


# Try to import FastAPI
# Try to import FastAPI
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False


    # Create dummy classes for type hints
    # Create dummy classes for type hints
    class APIRouter:
    class APIRouter:
    pass
    pass


    class BaseModel:
    class BaseModel:
    pass
    pass


    def Field(*args, **kwargs):
    def Field(*args, **kwargs):
    return None
    return None




    # Create router
    # Create router
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/v1", tags=["Embeddings"])
    router = APIRouter(prefix="/v1", tags=["Embeddings"])
    else:
    else:
    router = None
    router = None




    # Define request and response models
    # Define request and response models
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    class EmbeddingRequest(BaseModel):
    class EmbeddingRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Request model for embeddings.
    Request model for embeddings.
    """
    """


    input: Union[str, List[str]] = Field(
    input: Union[str, List[str]] = Field(
    ..., description="Input text(s) for embedding"
    ..., description="Input text(s) for embedding"
    )
    )
    model: Optional[str] = Field(None, description="Model to use for embedding")
    model: Optional[str] = Field(None, description="Model to use for embedding")


    class EmbeddingData(BaseModel):
    class EmbeddingData(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Model for embedding data.
    Model for embedding data.
    """
    """


    embedding: List[float] = Field(..., description="Embedding vector")
    embedding: List[float] = Field(..., description="Embedding vector")
    index: int = Field(..., description="Index of the input")
    index: int = Field(..., description="Index of the input")


    class EmbeddingResponse(BaseModel):
    class EmbeddingResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Response model for embeddings.
    Response model for embeddings.
    """
    """


    data: List[EmbeddingData] = Field(..., description="Embedding data")
    data: List[EmbeddingData] = Field(..., description="Embedding data")
    model: str = Field(..., description="Model used for embedding")
    model: str = Field(..., description="Model used for embedding")
    usage: Dict[str, int] = Field(..., description="Token usage information")
    usage: Dict[str, int] = Field(..., description="Token usage information")




    # Define route handlers
    # Define route handlers
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    @router.post("/embeddings", response_model=EmbeddingResponse)
    @router.post("/embeddings", response_model=EmbeddingResponse)
    async def get_embeddings(request: EmbeddingRequest, model=None):
    async def get_embeddings(request: EmbeddingRequest, model=None):
    """
    """
    Get embeddings for text.
    Get embeddings for text.


    Args:
    Args:
    request: Embedding request
    request: Embedding request
    model: Model instance (injected by dependency)
    model: Model instance (injected by dependency)


    Returns:
    Returns:
    Embedding result
    Embedding result
    """
    """
    if model is None:
    if model is None:
    raise HTTPException(status_code=500, detail="Model not loaded")
    raise HTTPException(status_code=500, detail="Model not loaded")


    try:
    try:
    # Get embeddings
    # Get embeddings
    result = await _get_embeddings(model, request)
    result = await _get_embeddings(model, request)
    return result
    return result


except Exception as e:
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    # Helper functions
    # Helper functions
    async def _get_embeddings(model, request):
    async def _get_embeddings(model, request):
    """
    """
    Get embeddings for text.
    Get embeddings for text.


    Args:
    Args:
    model: Model instance
    model: Model instance
    request: Embedding request
    request: Embedding request


    Returns:
    Returns:
    Embedding result
    Embedding result
    """
    """
    # Convert input to list if it's a string
    # Convert input to list if it's a string
    inputs = request.input if isinstance(request.input, list) else [request.input]
    inputs = request.input if isinstance(request.input, list) else [request.input]


    # Get embeddings
    # Get embeddings
    embeddings = model.get_embeddings(inputs)
    embeddings = model.get_embeddings(inputs)


    # Count tokens
    # Count tokens
    total_tokens = sum(model.count_tokens(text) for text in inputs)
    total_tokens = sum(model.count_tokens(text) for text in inputs)


    # Create response
    # Create response
    data = []
    data = []
    for i, embedding in enumerate(embeddings:
    for i, embedding in enumerate(embeddings:
    data.append({"embedding": embedding, "index": i}
    data.append({"embedding": embedding, "index": i}


    return {
    return {
    "data": data,
    "data": data,
    "model": request.model or model.model_id,
    "model": request.model or model.model_id,
    "usage": {"prompt_tokens": total_tokens, "total_tokens": total_tokens},
    "usage": {"prompt_tokens": total_tokens, "total_tokens": total_tokens},
    }
    }
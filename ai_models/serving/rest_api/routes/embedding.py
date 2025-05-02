"""
Embedding routes for REST API server.

This module provides route handlers for embeddings.
"""

from typing import Dict, List, Optional, Union

# Try to import FastAPI
try:
    from fastapi import APIRouter, Depends, HTTPException
    from pydantic import BaseModel, ConfigDict, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for type hints
    class APIRouter:
        pass

    class BaseModel:
        pass

    def Field(*args, **kwargs):
        return None


# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/v1", tags=["Embeddings"])
else:
    router = None


# Define request and response models
if FASTAPI_AVAILABLE:

    class EmbeddingRequest(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Request model for embeddings.
        """

        input: Union[str, List[str]] = Field(
            ..., description="Input text(s) for embedding"
        )
        model: Optional[str] = Field(None, description="Model to use for embedding")

    class EmbeddingData(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Model for embedding data.
        """

        embedding: List[float] = Field(..., description="Embedding vector")
        index: int = Field(..., description="Index of the input")

    class EmbeddingResponse(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Response model for embeddings.
        """

        data: List[EmbeddingData] = Field(..., description="Embedding data")
        model: str = Field(..., description="Model used for embedding")
        usage: Dict[str, int] = Field(..., description="Token usage information")


# Define route handlers
if FASTAPI_AVAILABLE:

    @router.post("/embeddings", response_model=EmbeddingResponse)
    async def get_embeddings(request: EmbeddingRequest, model=None):
        """
        Get embeddings for text.

        Args:
            request: Embedding request
            model: Model instance (injected by dependency)

        Returns:
            Embedding result
        """
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        try:
            # Get embeddings
            result = await _get_embeddings(model, request)
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# Helper functions
async def _get_embeddings(model, request):
    """
    Get embeddings for text.

    Args:
        model: Model instance
        request: Embedding request

    Returns:
        Embedding result
    """
    # Convert input to list if it's a string
    inputs = request.input if isinstance(request.input, list) else [request.input]

    # Get embeddings
    embeddings = model.get_embeddings(inputs)

    # Count tokens
    total_tokens = sum(model.count_tokens(text) for text in inputs)

    # Create response
    data = []
    for i, embedding in enumerate(embeddings):
        data.append({"embedding": embedding, "index": i})

    return {
        "data": data,
        "model": request.model or model.model_id,
        "usage": {"prompt_tokens": total_tokens, "total_tokens": total_tokens},
    }

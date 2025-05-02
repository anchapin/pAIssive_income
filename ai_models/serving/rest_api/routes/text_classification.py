"""
Text classification routes for REST API server.

This module provides route handlers for text classification.
"""

from typing import List

# Try to import FastAPI
try:
    from fastapi import APIRouter, HTTPException, Depends
    from pydantic import BaseModel, Field, ConfigDict

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for type hints
    class APIRouter:
        pass

    class BaseModel:
        pass

    Field = lambda *args, **kwargs: None


# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/v1", tags=["Text Classification"])
else:
    router = None


# Define request and response models
if FASTAPI_AVAILABLE:

    class ClassificationRequest(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Request model for text classification.
        """

        text: str = Field(..., description="Input text for classification")

    class ClassificationLabel(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Model for a classification label.
        """

        label: str = Field(..., description="Classification label")
        score: float = Field(..., description="Confidence score")

    class ClassificationResponse(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        """
        Response model for text classification.
        """

        labels: List[ClassificationLabel] = Field(
            ..., description="Classification labels"
        )
        top_label: str = Field(..., description="Top classification label")
        tokens: int = Field(..., description="Number of tokens in the input")


# Define route handlers
if FASTAPI_AVAILABLE:

    @router.post("/classify", response_model=ClassificationResponse)
    async def classify_text(request: ClassificationRequest, model=None):
        """
        Classify text.

        Args:
            request: Classification request
            model: Model instance (injected by dependency)

        Returns:
            Classification result
        """
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        try:
            # Classify text
            result = await _classify_text(model, request)
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# Helper functions
async def _classify_text(model, request):
    """
    Classify text.

    Args:
        model: Model instance
        request: Classification request

    Returns:
        Classification result
    """
    # Classify text
    result = model.classify_text(request.text)

    # Count tokens
    tokens = model.count_tokens(request.text)

    # Create response
    return {
        "labels": result["labels"],
        "top_label": result["top_label"],
        "tokens": tokens,
    }

"""
"""
Text classification routes for REST API server.
Text classification routes for REST API server.


This module provides route handlers for text classification.
This module provides route handlers for text classification.
"""
"""




from typing import List
from typing import List


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
    router = APIRouter(prefix="/v1", tags=["Text Classification"])
    router = APIRouter(prefix="/v1", tags=["Text Classification"])
    else:
    else:
    router = None
    router = None




    # Define request and response models
    # Define request and response models
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    class ClassificationRequest(BaseModel):
    class ClassificationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Request model for text classification.
    Request model for text classification.
    """
    """


    text: str = Field(..., description="Input text for classification")
    text: str = Field(..., description="Input text for classification")


    class ClassificationLabel(BaseModel):
    class ClassificationLabel(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Model for a classification label.
    Model for a classification label.
    """
    """


    label: str = Field(..., description="Classification label")
    label: str = Field(..., description="Classification label")
    score: float = Field(..., description="Confidence score")
    score: float = Field(..., description="Confidence score")


    class ClassificationResponse(BaseModel):
    class ClassificationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """
    """
    Response model for text classification.
    Response model for text classification.
    """
    """


    labels: List[ClassificationLabel] = Field(
    labels: List[ClassificationLabel] = Field(
    ..., description="Classification labels"
    ..., description="Classification labels"
    )
    )
    top_label: str = Field(..., description="Top classification label")
    top_label: str = Field(..., description="Top classification label")
    tokens: int = Field(..., description="Number of tokens in the input")
    tokens: int = Field(..., description="Number of tokens in the input")




    # Define route handlers
    # Define route handlers
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    @router.post("/classify", response_model=ClassificationResponse)
    @router.post("/classify", response_model=ClassificationResponse)
    async def classify_text(request: ClassificationRequest, model=None):
    async def classify_text(request: ClassificationRequest, model=None):
    """
    """
    Classify text.
    Classify text.


    Args:
    Args:
    request: Classification request
    request: Classification request
    model: Model instance (injected by dependency)
    model: Model instance (injected by dependency)


    Returns:
    Returns:
    Classification result
    Classification result
    """
    """
    if model is None:
    if model is None:
    raise HTTPException(status_code=500, detail="Model not loaded")
    raise HTTPException(status_code=500, detail="Model not loaded")


    try:
    try:
    # Classify text
    # Classify text
    result = await _classify_text(model, request)
    result = await _classify_text(model, request)
    return result
    return result


except Exception as e:
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    # Helper functions
    # Helper functions
    async def _classify_text(model, request):
    async def _classify_text(model, request):
    """
    """
    Classify text.
    Classify text.


    Args:
    Args:
    model: Model instance
    model: Model instance
    request: Classification request
    request: Classification request


    Returns:
    Returns:
    Classification result
    Classification result
    """
    """
    # Classify text
    # Classify text
    result = model.classify_text(request.text
    result = model.classify_text(request.text


    # Count tokens
    # Count tokens
    tokens = model.count_tokens(request.text
    tokens = model.count_tokens(request.text


    # Create response
    # Create response
    return {
    return {
    "labels": result["labels"],
    "labels": result["labels"],
    "top_label": result["top_label"],
    "top_label": result["top_label"],
    "tokens": tokens,
    "tokens": tokens,
    }
    }
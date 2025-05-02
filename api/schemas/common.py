"""
Common schemas for the API server.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: Dict[str, Any] = Field(
        ...,
        description="Error details",
        example={
            "code": "invalid_request",
            "message": "Invalid request parameters",
            "details": {
                "field": "email",
                "reason": "Invalid email format"
            }
        }
    )

class SuccessResponse(BaseModel):
    """Schema for success responses."""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")

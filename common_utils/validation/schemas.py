"""schemas - Module for common_utils/validation.schemas."""

# Standard library imports
from typing import Any, Optional

# Third-party imports
from pydantic import BaseModel, conint

# Local imports


class ErrorDetail(BaseModel):
    """Schema for error details."""

    field: Optional[str] = None
    message: str
    type: str = "validation_error"


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    status: str = "error"
    message: str = "An error occurred"
    error_code: str = "validation_error"
    errors: list[ErrorDetail]


class SuccessResponse(BaseModel):
    """Schema for success responses."""

    status: str = "success"
    message: Optional[str] = None
    data: dict[str, Any]


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""

    page: conint(ge=1) = 1
    limit: conint(ge=1, le=100) = 10

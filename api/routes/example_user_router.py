"""
Example user router demonstrating centralized validation per project standards.

See: docs/input_validation_and_error_handling_standards.md
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from common_utils.logging import get_logger
from common_utils.validation.core import (
    ValidationError,
    validate_input,
    validation_error_response,
)

# Initialize logger
logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/example_users", tags=["example_users"])


class CreateUserModel(BaseModel):
    """Data model for user creation requests."""

    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    age: int = Field(..., ge=0, le=120)


@router.post("/", summary="Create a new user")
async def create_user(request: Request) -> dict[str, Any]:
    """Create a new user with validated input data."""
    try:
        payload = await request.json()
        user_in = validate_input(CreateUserModel, payload)
        # ... Insert user creation logic here ...
        return {"message": "User created", "user": user_in.model_dump()}
    except ValidationError as exc:
        result: dict[str, Any] = validation_error_response(exc)
        return result
    except Exception as exc:
        logger.exception("An unexpected error occurred")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc

"""Reusable error models and global HTTPException handler for API."""

from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

__all__ = ["ErrorResponse", "http_exception_handler"]

class ErrorResponse(BaseModel):
    """Standard error response model for API endpoints."""

    message: str = Field(..., description="Error message")
    code: int = Field(..., description="HTTP status code")


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """
    Convert HTTPException into a consistent JSON error response.

    Args:
        _request: The request that caused the exception (unused).
        exc: The HTTPException instance.

    Returns:
        JSONResponse: Error response with standardized shape.

    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.detail, code=exc.status_code).model_dump(),
    )
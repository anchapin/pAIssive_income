"""Tool Router: Exposes math utility functions as API endpoints with API key authentication and audit logging."""

from __future__ import annotations

import logging
import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from utils.math_utils import add, average, divide, multiply, subtract

# --- Settings ---
API_KEY = os.getenv("TOOL_API_KEY")
if not API_KEY:
    msg = "TOOL_API_KEY environment variable not set"
    raise ValueError(msg)

# --- Logging setup ---
logger = logging.getLogger("tool_api_audit")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)


# --- API Key Auth Dependency ---
def api_key_auth(request: Request) -> str:
    """Authenticate API key from request headers."""
    header_key = request.headers.get("x-api-key")
    if not header_key or header_key != API_KEY:
        logger.info("[AUTH FAIL] Attempted access with invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return header_key


# --- Request Models ---
class BinaryOpRequest(BaseModel):
    """Request model for binary operations."""

    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")


class AverageRequest(BaseModel):
    """Request model for average calculation."""

    numbers: list[float] = Field(..., description="List of numbers")


# --- Router ---
router = APIRouter(
    prefix="/tools", tags=["Tools"], responses={401: {"description": "Unauthorized"}}
)


@router.post(
    "/add", summary="Add two numbers", response_description="Sum of the numbers"
)
async def add_endpoint(
    payload: BinaryOpRequest,
    api_key: Annotated[str, Depends(api_key_auth)],  # noqa: ARG001
) -> dict[str, float]:
    """Add two numbers."""
    result = add(payload.a, payload.b)
    logger.info("[AUDIT] tool=add, params=%s, api_key=***", payload.model_dump())
    return {"result": result}


@router.post(
    "/subtract",
    summary="Subtract two numbers",
    response_description="Difference of the numbers",
)
async def subtract_endpoint(
    payload: BinaryOpRequest,
    api_key: Annotated[str, Depends(api_key_auth)],  # noqa: ARG001
) -> dict[str, float]:
    """Subtract two numbers."""
    result = subtract(payload.a, payload.b)
    logger.info("[AUDIT] tool=subtract, params=%s, api_key=***", payload.model_dump())
    return {"result": result}


@router.post(
    "/multiply",
    summary="Multiply two numbers",
    response_description="Product of the numbers",
)
async def multiply_endpoint(
    payload: BinaryOpRequest,
    api_key: Annotated[str, Depends(api_key_auth)],  # noqa: ARG001
) -> dict[str, float]:
    """Multiply two numbers."""
    result = multiply(payload.a, payload.b)
    logger.info("[AUDIT] tool=multiply, params=%s, api_key=***", payload.model_dump())
    return {"result": result}


@router.post(
    "/divide",
    summary="Divide two numbers",
    response_description="Quotient of the numbers",
)
async def divide_endpoint(
    payload: BinaryOpRequest,
    api_key: Annotated[str, Depends(api_key_auth)],  # noqa: ARG001
) -> dict[str, float]:
    """Divide two numbers."""
    try:
        result = divide(payload.a, payload.b)
    except ZeroDivisionError as e:
        logger.info(
            "[AUDIT] tool=divide, params=%s, api_key=***, error=ZeroDivisionError",
            payload.model_dump(),
        )
        raise HTTPException(status_code=400, detail="Cannot divide by zero") from e
    else:
        logger.info("[AUDIT] tool=divide, params=%s, api_key=***", payload.model_dump())
        return {"result": result}


@router.post(
    "/average",
    summary="Average a list of numbers",
    response_description="Average value",
)
async def average_endpoint(
    payload: AverageRequest,
    api_key: Annotated[str, Depends(api_key_auth)],  # noqa: ARG001
) -> dict[str, float]:
    """Calculate average of a list of numbers."""
    try:
        result = average(payload.numbers)
    except ValueError as e:
        logger.info(
            "[AUDIT] tool=average, params=%s, api_key=***, error=ValueError",
            payload.model_dump(),
        )
        raise HTTPException(
            status_code=400, detail="Cannot calculate average of empty list"
        ) from e
    else:
        logger.info(
            "[AUDIT] tool=average, params=%s, api_key=***", payload.model_dump()
        )
        return {"result": result}

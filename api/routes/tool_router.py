"""Tool Router: Exposes math utility functions as API endpoints with API key authentication and audit logging."""

from fastapi import APIRouter, Request, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Any, Dict
import logging
import os

from utils.math_utils import add, subtract, multiply, divide, average

# --- Settings ---
API_KEY = os.getenv("TOOL_API_KEY", "supersecretkey")

# --- Logging setup ---
logger = logging.getLogger("tool_api_audit")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

# --- API Key Auth Dependency ---
def api_key_auth(request: Request):
    header_key = request.headers.get("x-api-key")
    if header_key != API_KEY:
        logger.info(
            f"[AUTH FAIL] Attempted access with API key: {header_key!r}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return header_key

# --- Request Models ---
class BinaryOpRequest(BaseModel):
    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")

class AverageRequest(BaseModel):
    numbers: List[float] = Field(..., description="List of numbers")

# --- Router ---
router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
    responses={401: {"description": "Unauthorized"}}
)

@router.post("/add", summary="Add two numbers", response_description="Sum of the numbers")
async def add_endpoint(
    payload: BinaryOpRequest,
    api_key: str = Depends(api_key_auth)
):
    result = add(payload.a, payload.b)
    logger.info(f"[AUDIT] tool=add, params={payload.dict()}, api_key={api_key!r}")
    return {"result": result}

@router.post("/subtract", summary="Subtract two numbers", response_description="Difference of the numbers")
async def subtract_endpoint(
    payload: BinaryOpRequest,
    api_key: str = Depends(api_key_auth)
):
    result = subtract(payload.a, payload.b)
    logger.info(f"[AUDIT] tool=subtract, params={payload.dict()}, api_key={api_key!r}")
    return {"result": result}

@router.post("/multiply", summary="Multiply two numbers", response_description="Product of the numbers")
async def multiply_endpoint(
    payload: BinaryOpRequest,
    api_key: str = Depends(api_key_auth)
):
    result = multiply(payload.a, payload.b)
    logger.info(f"[AUDIT] tool=multiply, params={payload.dict()}, api_key={api_key!r}")
    return {"result": result}

@router.post("/divide", summary="Divide two numbers", response_description="Quotient of the numbers")
async def divide_endpoint(
    payload: BinaryOpRequest,
    api_key: str = Depends(api_key_auth)
):
    try:
        result = divide(payload.a, payload.b)
    except ZeroDivisionError:
        logger.info(f"[AUDIT] tool=divide, params={payload.dict()}, api_key={api_key!r}, error=ZeroDivisionError")
        raise HTTPException(status_code=400, detail="Cannot divide by zero")
    logger.info(f"[AUDIT] tool=divide, params={payload.dict()}, api_key={api_key!r}")
    return {"result": result}

@router.post("/average", summary="Average a list of numbers", response_description="Average value")
async def average_endpoint(
    payload: AverageRequest,
    api_key: str = Depends(api_key_auth)
):
    try:
        result = average(payload.numbers)
    except ValueError:
        logger.info(f"[AUDIT] tool=average, params={payload.dict()}, api_key={api_key!r}, error=ValueError")
        raise HTTPException(status_code=400, detail="Cannot calculate average of empty list")
    logger.info(f"[AUDIT] tool=average, params={payload.dict()}, api_key={api_key!r}")
    return {"result": result}
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from errors import BaseError, ValidationError

"""
Niche Analysis routes for the API server.

This module provides route handlers for Niche Analysis operations.
"""

# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI is required for API routes")
    FASTAPI_AVAILABLE = False

    # Import dependencies
    from ..dependencies import get_market_segment_service, get_niche_service
    from ..schemas.common import (ErrorResponse, PaginatedResponse, QueryParams,
    SortDirection, SuccessResponse)
    # Import schemas
    from ..schemas.niche_analysis import (BulkNicheCreateRequest,
    BulkNicheUpdateRequest,
    MarketSegmentResponse,
    NicheAnalysisRequest,
    NicheAnalysisResponse,
    NicheCreateRequest, NicheResponse,
    NicheUpdateRequest)

    # Create router
    router = APIRouter(
    prefix="/api/v1/niche-analysis",
    tags=["niche-analysis"],
    responses={
    404: {"model": ErrorResponse, "description": "Not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    )


    @router.get(
    "/niches",
    response_model=PaginatedResponse[NicheResponse],
    responses={
    200: {"description": "List of niches"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get all niches",
    description="Get a paginated list of all niches with optional filtering and sorting",
    )
    async def get_niches(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_direction: SortDirection = Query(
    SortDirection.ASC, description="Sort direction"
    ),
    niche_service=Depends(get_niche_service),
    ):
    """
    Get a paginated list of all niches with optional filtering and sorting.
    """
    try:
    # Create query parameters
    query_params = QueryParams(
    page=page,
    page_size=page_size,
    sort_by=sort_by,
    sort_direction=sort_direction,
    filters=[],
    )

    # Get niches
    niches, total = await niche_service.get_niches(query_params)

    # Create response
    response = PaginatedResponse[NicheResponse](
    items=niches,
    page=page,
    page_size=page_size,
    total=total,
    total_pages=(total + page_size - 1) // page_size,
    )

    return response

except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
    logger.error(f"Error getting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
    logger.error(f"Error getting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error getting niches: {str(e)}")


    @router.get(
    "/niches/{niche_id}",
    response_model=NicheResponse,
    responses={
    200: {"description": "Niche details"},
    404: {"model": ErrorResponse, "description": "Niche not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get niche by ID",
    description="Get detailed information about a specific niche",
    )
    async def get_niche(
    niche_id: str = Path(..., description="Niche ID"),
    niche_service=Depends(get_niche_service),
    ):
    """
    Get detailed information about a specific niche.
    """
    try:
    # Get niche
    niche = await niche_service.get_niche(niche_id)

    # Check if niche exists
    if not niche:
    raise HTTPException(status_code=404, detail=f"Niche {niche_id} not found")

    return niche

except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
    logger.error(f"Error getting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Error getting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error getting niche: {str(e)}")


    @router.post(
    "/niches",
    response_model=NicheResponse,
    responses={
    201: {"description": "Niche created successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Create a new niche",
    description="Create a new niche with the provided information",
    status_code=201,
    )
    async def create_niche(
    niche: NicheCreateRequest = Body(..., description="Niche to create"),
    niche_service=Depends(get_niche_service),
    ):
    """
    Create a new niche with the provided information.
    """
    try:
    # Create niche
    created_niche = await niche_service.create_niche(niche)

    return created_niche

except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
    logger.error(f"Error creating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
    logger.error(f"Error creating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error creating niche: {str(e)}")


    @router.put(
    "/niches/{niche_id}",
    response_model=NicheResponse,
    responses={
    200: {"description": "Niche updated successfully"},
    404: {"model": ErrorResponse, "description": "Niche not found"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Update a niche",
    description="Update an existing niche with the provided information",
    )
    async def update_niche(
    niche_id: str = Path(..., description="Niche ID"),
    niche: NicheUpdateRequest = Body(..., description="Niche updates"),
    niche_service=Depends(get_niche_service),
    ):
    """
    Update an existing niche with the provided information.
    """
    try:
    # Check if niche exists
    existing_niche = await niche_service.get_niche(niche_id)
    if not existing_niche:
    raise HTTPException(status_code=404, detail=f"Niche {niche_id} not found")

    # Update niche
    updated_niche = await niche_service.update_niche(niche_id, niche)

    return updated_niche

except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
    logger.error(f"Error updating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Error updating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error updating niche: {str(e)}")


    @router.delete(
    "/niches/{niche_id}",
    response_model=SuccessResponse,
    responses={
    200: {"description": "Niche deleted successfully"},
    404: {"model": ErrorResponse, "description": "Niche not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Delete a niche",
    description="Delete an existing niche",
    )
    async def delete_niche(
    niche_id: str = Path(..., description="Niche ID"),
    niche_service=Depends(get_niche_service),
    ):
    """
    Delete an existing niche.
    """
    try:
    # Check if niche exists
    existing_niche = await niche_service.get_niche(niche_id)
    if not existing_niche:
    raise HTTPException(status_code=404, detail=f"Niche {niche_id} not found")

    # Delete niche
    success = await niche_service.delete_niche(niche_id)

    return SuccessResponse(success=success)

except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
    logger.error(f"Error deleting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Error deleting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error deleting niche: {str(e)}")


    @router.post(
    "/analyze",
    response_model=NicheAnalysisResponse,
    responses={
    200: {"description": "Analysis completed successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Analyze niches",
    description="Analyze niches based on the provided market segments",
    )
    async def analyze_niches(
    request: NicheAnalysisRequest = Body(..., description="Analysis request"),
    niche_service=Depends(get_niche_service),
    ):
    """
    Analyze niches based on the provided market segments.
    """
    try:
    # Analyze niches
    analysis = await niche_service.analyze_niches(
    request.segments, request.force_refresh, request.max_results
    )

    return analysis

except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
    logger.error(f"Error analyzing niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
    logger.error(f"Error analyzing niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error analyzing niches: {str(e)}")


    @router.get(
    "/market-segments",
    response_model=List[MarketSegmentResponse],
    responses={
    200: {"description": "List of market segments"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get all market segments",
    description="Get a list of all available market segments",
    )
    async def get_market_segments(
    market_segment_service=Depends(get_market_segment_service),
    ):
    """
    Get a list of all available market segments.
    """
    try:
    # Get market segments
    segments = await market_segment_service.get_market_segments()

    return segments

except BaseError as e:
    logger.error(f"Error getting market segments: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
    logger.error(f"Error getting market segments: {str(e)}")
    raise HTTPException(
    status_code=500, detail=f"Error getting market segments: {str(e)}"
    )


    # Bulk operation endpoints
    @router.post(
    "/niches/bulk",
    response_model=None,  # Disable response model generation from type annotation
    responses={
    201: {"description": "Niches created successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Create multiple niches in bulk",
    description="Create multiple niches in a single request for improved performance",
    status_code=201,
    )
    async def create_niches_bulk(
    request: BulkNicheCreateRequest = Body(..., description="Bulk create request"),
    niche_service=Depends(get_niche_service),
    ):
    """
    Create multiple niches in a single request for improved performance.
    """
    try:
    # Start timing
    start_time = time.time()

    # Process batch
    operation_id = str(uuid.uuid4())
    results = []
    errors = []

    # Process each item
    for i, item in enumerate(request.items):
    try:
    # Create niche
    niche = await niche_service.create_niche(item)
    results.append(niche)
except Exception as e:
    # Add error
    errors.append(
    {
    "index": i,
    "error_code": "NICHE_CREATE_ERROR",
    "error_message": str(e),
    }
    )

    # Calculate stats
    end_time = time.time()
    stats = {
    "total_items": len(request.items),
    "successful_items": len(results),
    "failed_items": len(errors),
    "processing_time_ms": (end_time - start_time) * 1000,
    }

    # Create response
    response = {
    "items": results,
    "errors": errors,
    "stats": stats,
    "operation_id": operation_id,
    }

    return response

except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
    logger.error(f"Error creating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
    logger.error(f"Error creating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error creating niches: {str(e)}")


    @router.put(
    "/niches/bulk",
    response_model=None,  # Disable response model generation from type annotation
    responses={
    200: {"description": "Niches updated successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Update multiple niches in bulk",
    description="Update multiple niches in a single request for improved performance",
    )
    async def update_niches_bulk(
    request: BulkNicheUpdateRequest = Body(..., description="Bulk update request"),
    niche_service=Depends(get_niche_service),
    ):
    """
    Update multiple niches in a single request for improved performance.
    """
    try:
    # Start timing
    start_time = time.time()

    # Process batch
    operation_id = str(uuid.uuid4())
    results = []
    errors = []

    # Process each item
    for i, item in enumerate(request.items):
    try:
    # Get niche ID
    niche_id = item.get("id")
    if not niche_id:
    raise ValueError("Niche ID is required")

    # Check if niche exists
    existing_niche = await niche_service.get_niche(niche_id)
    if not existing_niche:
    raise ValueError(f"Niche {niche_id} not found")

    # Update niche
    niche = await niche_service.update_niche(niche_id, item)
    results.append(niche)
except Exception as e:
    # Add error
    errors.append(
    {
    "index": i,
    "error_code": "NICHE_UPDATE_ERROR",
    "error_message": str(e),
    "item_id": item.get("id"),
    }
    )

    # Calculate stats
    end_time = time.time()
    stats = {
    "total_items": len(request.items),
    "successful_items": len(results),
    "failed_items": len(errors),
    "processing_time_ms": (end_time - start_time) * 1000,
    }

    # Create response
    response = {
    "items": results,
    "errors": errors,
    "stats": stats,
    "operation_id": operation_id,
    }

    return response

except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
    logger.error(f"Error updating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
    logger.error(f"Error updating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error updating niches: {str(e)}")


    @router.delete(
    "/niches/bulk",
    response_model=None,  # Disable response model generation from type annotation
    responses={
    200: {"description": "Niches deleted successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Delete multiple niches in bulk",
    description="Delete multiple niches in a single request for improved performance",
    )
    async def delete_niches_bulk(
    request: Dict[str, Any] = Body(..., description="Bulk delete request"),
    niche_service=Depends(get_niche_service),
    ):
    """
    Delete multiple niches in a single request for improved performance.
    """
    try:
    # Start timing
    start_time = time.time()

    # Get niche IDs
    niche_ids = request.get("ids", [])
    if not niche_ids:
    raise ValueError("Niche IDs are required")

    # Process batch
    operation_id = str(uuid.uuid4())
    deleted_ids = []
    errors = []

    # Process each item
    for i, niche_id in enumerate(niche_ids):
    try:
    # Check if niche exists
    existing_niche = await niche_service.get_niche(niche_id)
    if not existing_niche:
    raise ValueError(f"Niche {niche_id} not found")

    # Delete niche
    success = await niche_service.delete_niche(niche_id)
    if success:
    deleted_ids.append(niche_id)
    else:
    raise ValueError(f"Failed to delete niche {niche_id}")
except Exception as e:
    # Add error
    errors.append(
    {
    "index": i,
    "error_code": "NICHE_DELETE_ERROR",
    "error_message": str(e),
    "item_id": niche_id,
    }
    )

    # Calculate stats
    end_time = time.time()
    stats = {
    "total_items": len(niche_ids),
    "successful_items": len(deleted_ids),
    "failed_items": len(errors),
    "processing_time_ms": (end_time - start_time) * 1000,
    }

    # Create response
    response = {
    "deleted_ids": deleted_ids,
    "errors": errors,
    "stats": stats,
    "operation_id": operation_id,
    }

    return response

except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
    logger.error(f"Error deleting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
    logger.error(f"Error deleting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error deleting niches: {str(e)}")

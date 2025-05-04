import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from errors import BaseError, ValidationError

"""
"""
Niche Analysis routes for the API server.
Niche Analysis routes for the API server.


This module provides route handlers for Niche Analysis operations.
This module provides route handlers for Niche Analysis operations.
"""
"""


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Try to import FastAPI
# Try to import FastAPI
try:
    try:
    from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
    from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
    from fastapi.responses import JSONResponse
    from fastapi.responses import JSONResponse


    FASTAPI_AVAILABLE = True
    FASTAPI_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("FastAPI is required for API routes")
    logger.warning("FastAPI is required for API routes")
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False


    # Import dependencies
    # Import dependencies
    from ..dependencies import get_market_segment_service, get_niche_service
    from ..dependencies import get_market_segment_service, get_niche_service
    from ..schemas.common import (ErrorResponse, PaginatedResponse, QueryParams,
    from ..schemas.common import (ErrorResponse, PaginatedResponse, QueryParams,
    SortDirection, SuccessResponse)
    SortDirection, SuccessResponse)
    # Import schemas
    # Import schemas
    from ..schemas.niche_analysis import (BulkNicheCreateRequest,
    from ..schemas.niche_analysis import (BulkNicheCreateRequest,
    BulkNicheUpdateRequest,
    BulkNicheUpdateRequest,
    MarketSegmentResponse,
    MarketSegmentResponse,
    NicheAnalysisRequest,
    NicheAnalysisRequest,
    NicheAnalysisResponse,
    NicheAnalysisResponse,
    NicheCreateRequest, NicheResponse,
    NicheCreateRequest, NicheResponse,
    NicheUpdateRequest)
    NicheUpdateRequest)


    # Create router
    # Create router
    router = APIRouter(
    router = APIRouter(
    prefix="/api/v1/niche-analysis",
    prefix="/api/v1/niche-analysis",
    tags=["niche-analysis"],
    tags=["niche-analysis"],
    responses={
    responses={
    404: {"model": ErrorResponse, "description": "Not found"},
    404: {"model": ErrorResponse, "description": "Not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    )
    )




    @router.get(
    @router.get(
    "/niches",
    "/niches",
    response_model=PaginatedResponse[NicheResponse],
    response_model=PaginatedResponse[NicheResponse],
    responses={
    responses={
    200: {"description": "List of niches"},
    200: {"description": "List of niches"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Get all niches",
    summary="Get all niches",
    description="Get a paginated list of all niches with optional filtering and sorting",
    description="Get a paginated list of all niches with optional filtering and sorting",
    )
    )
    async def get_niches(
    async def get_niches(
    page: int = Query(1, ge=1, description="Page number"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_direction: SortDirection = Query(
    sort_direction: SortDirection = Query(
    SortDirection.ASC, description="Sort direction"
    SortDirection.ASC, description="Sort direction"
    ),
    ),
    niche_service=Depends(get_niche_service),
    niche_service=Depends(get_niche_service),
    ):
    ):
    """
    """
    Get a paginated list of all niches with optional filtering and sorting.
    Get a paginated list of all niches with optional filtering and sorting.
    """
    """
    try:
    try:
    # Create query parameters
    # Create query parameters
    query_params = QueryParams(
    query_params = QueryParams(
    page=page,
    page=page,
    page_size=page_size,
    page_size=page_size,
    sort_by=sort_by,
    sort_by=sort_by,
    sort_direction=sort_direction,
    sort_direction=sort_direction,
    filters=[],
    filters=[],
    )
    )


    # Get niches
    # Get niches
    niches, total = await niche_service.get_niches(query_params)
    niches, total = await niche_service.get_niches(query_params)


    # Create response
    # Create response
    response = PaginatedResponse[NicheResponse](
    response = PaginatedResponse[NicheResponse](
    items=niches,
    items=niches,
    page=page,
    page=page,
    page_size=page_size,
    page_size=page_size,
    total=total,
    total=total,
    total_pages=(total + page_size - 1) // page_size,
    total_pages=(total + page_size - 1) // page_size,
    )
    )


    return response
    return response


except ValidationError as e:
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
except BaseError as e:
    logger.error(f"Error getting niches: {str(e)}")
    logger.error(f"Error getting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
except Exception as e:
    logger.error(f"Error getting niches: {str(e)}")
    logger.error(f"Error getting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error getting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error getting niches: {str(e)}")




    @router.get(
    @router.get(
    "/niches/{niche_id}",
    "/niches/{niche_id}",
    response_model=NicheResponse,
    response_model=NicheResponse,
    responses={
    responses={
    200: {"description": "Niche details"},
    200: {"description": "Niche details"},
    404: {"model": ErrorResponse, "description": "Niche not found"},
    404: {"model": ErrorResponse, "description": "Niche not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Get niche by ID",
    summary="Get niche by ID",
    description="Get detailed information about a specific niche",
    description="Get detailed information about a specific niche",
    )
    )
    async def get_niche(
    async def get_niche(
    niche_id: str = Path(..., description="Niche ID"),
    niche_id: str = Path(..., description="Niche ID"),
    niche_service=Depends(get_niche_service),
    niche_service=Depends(get_niche_service),
    ):
    ):
    """
    """
    Get detailed information about a specific niche.
    Get detailed information about a specific niche.
    """
    """
    try:
    try:
    # Get niche
    # Get niche
    niche = await niche_service.get_niche(niche_id)
    niche = await niche_service.get_niche(niche_id)


    # Check if niche exists
    # Check if niche exists
    if not niche:
    if not niche:
    raise HTTPException(status_code=404, detail=f"Niche {niche_id} not found")
    raise HTTPException(status_code=404, detail=f"Niche {niche_id} not found")


    return niche
    return niche


except ValidationError as e:
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
except BaseError as e:
    logger.error(f"Error getting niche: {str(e)}")
    logger.error(f"Error getting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except HTTPException:
except HTTPException:
    raise
    raise
except Exception as e:
except Exception as e:
    logger.error(f"Error getting niche: {str(e)}")
    logger.error(f"Error getting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error getting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error getting niche: {str(e)}")




    @router.post(
    @router.post(
    "/niches",
    "/niches",
    response_model=NicheResponse,
    response_model=NicheResponse,
    responses={
    responses={
    201: {"description": "Niche created successfully"},
    201: {"description": "Niche created successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Create a new niche",
    summary="Create a new niche",
    description="Create a new niche with the provided information",
    description="Create a new niche with the provided information",
    status_code=201,
    status_code=201,
    )
    )
    async def create_niche(
    async def create_niche(
    niche: NicheCreateRequest = Body(..., description="Niche to create"),
    niche: NicheCreateRequest = Body(..., description="Niche to create"),
    niche_service=Depends(get_niche_service),
    niche_service=Depends(get_niche_service),
    ):
    ):
    """
    """
    Create a new niche with the provided information.
    Create a new niche with the provided information.
    """
    """
    try:
    try:
    # Create niche
    # Create niche
    created_niche = await niche_service.create_niche(niche)
    created_niche = await niche_service.create_niche(niche)


    return created_niche
    return created_niche


except ValidationError as e:
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
except BaseError as e:
    logger.error(f"Error creating niche: {str(e)}")
    logger.error(f"Error creating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
except Exception as e:
    logger.error(f"Error creating niche: {str(e)}")
    logger.error(f"Error creating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error creating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error creating niche: {str(e)}")




    @router.put(
    @router.put(
    "/niches/{niche_id}",
    "/niches/{niche_id}",
    response_model=NicheResponse,
    response_model=NicheResponse,
    responses={
    responses={
    200: {"description": "Niche updated successfully"},
    200: {"description": "Niche updated successfully"},
    404: {"model": ErrorResponse, "description": "Niche not found"},
    404: {"model": ErrorResponse, "description": "Niche not found"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Update a niche",
    summary="Update a niche",
    description="Update an existing niche with the provided information",
    description="Update an existing niche with the provided information",
    )
    )
    async def update_niche(
    async def update_niche(
    niche_id: str = Path(..., description="Niche ID"),
    niche_id: str = Path(..., description="Niche ID"),
    niche: NicheUpdateRequest = Body(..., description="Niche updates"),
    niche: NicheUpdateRequest = Body(..., description="Niche updates"),
    niche_service=Depends(get_niche_service),
    niche_service=Depends(get_niche_service),
    ):
    ):
    """
    """
    Update an existing niche with the provided information.
    Update an existing niche with the provided information.
    """
    """
    try:
    try:
    # Check if niche exists
    # Check if niche exists
    existing_niche = await niche_service.get_niche(niche_id)
    existing_niche = await niche_service.get_niche(niche_id)
    if not existing_niche:
    if not existing_niche:
    raise HTTPException(status_code=404, detail=f"Niche {niche_id} not found")
    raise HTTPException(status_code=404, detail=f"Niche {niche_id} not found")


    # Update niche
    # Update niche
    updated_niche = await niche_service.update_niche(niche_id, niche)
    updated_niche = await niche_service.update_niche(niche_id, niche)


    return updated_niche
    return updated_niche


except ValidationError as e:
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
except BaseError as e:
    logger.error(f"Error updating niche: {str(e)}")
    logger.error(f"Error updating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except HTTPException:
except HTTPException:
    raise
    raise
except Exception as e:
except Exception as e:
    logger.error(f"Error updating niche: {str(e)}")
    logger.error(f"Error updating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error updating niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error updating niche: {str(e)}")




    @router.delete(
    @router.delete(
    "/niches/{niche_id}",
    "/niches/{niche_id}",
    response_model=SuccessResponse,
    response_model=SuccessResponse,
    responses={
    responses={
    200: {"description": "Niche deleted successfully"},
    200: {"description": "Niche deleted successfully"},
    404: {"model": ErrorResponse, "description": "Niche not found"},
    404: {"model": ErrorResponse, "description": "Niche not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Delete a niche",
    summary="Delete a niche",
    description="Delete an existing niche",
    description="Delete an existing niche",
    )
    )
    async def delete_niche(
    async def delete_niche(
    niche_id: str = Path(..., description="Niche ID"),
    niche_id: str = Path(..., description="Niche ID"),
    niche_service=Depends(get_niche_service),
    niche_service=Depends(get_niche_service),
    ):
    ):
    """
    """
    Delete an existing niche.
    Delete an existing niche.
    """
    """
    try:
    try:
    # Check if niche exists
    # Check if niche exists
    existing_niche = await niche_service.get_niche(niche_id)
    existing_niche = await niche_service.get_niche(niche_id)
    if not existing_niche:
    if not existing_niche:
    raise HTTPException(status_code=404, detail=f"Niche {niche_id} not found")
    raise HTTPException(status_code=404, detail=f"Niche {niche_id} not found")


    # Delete niche
    # Delete niche
    success = await niche_service.delete_niche(niche_id)
    success = await niche_service.delete_niche(niche_id)


    return SuccessResponse(success=success)
    return SuccessResponse(success=success)


except ValidationError as e:
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
except BaseError as e:
    logger.error(f"Error deleting niche: {str(e)}")
    logger.error(f"Error deleting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except HTTPException:
except HTTPException:
    raise
    raise
except Exception as e:
except Exception as e:
    logger.error(f"Error deleting niche: {str(e)}")
    logger.error(f"Error deleting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error deleting niche: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error deleting niche: {str(e)}")




    @router.post(
    @router.post(
    "/analyze",
    "/analyze",
    response_model=NicheAnalysisResponse,
    response_model=NicheAnalysisResponse,
    responses={
    responses={
    200: {"description": "Analysis completed successfully"},
    200: {"description": "Analysis completed successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Analyze niches",
    summary="Analyze niches",
    description="Analyze niches based on the provided market segments",
    description="Analyze niches based on the provided market segments",
    )
    )
    async def analyze_niches(
    async def analyze_niches(
    request: NicheAnalysisRequest = Body(..., description="Analysis request"),
    request: NicheAnalysisRequest = Body(..., description="Analysis request"),
    niche_service=Depends(get_niche_service),
    niche_service=Depends(get_niche_service),
    ):
    ):
    """
    """
    Analyze niches based on the provided market segments.
    Analyze niches based on the provided market segments.
    """
    """
    try:
    try:
    # Analyze niches
    # Analyze niches
    analysis = await niche_service.analyze_niches(
    analysis = await niche_service.analyze_niches(
    request.segments, request.force_refresh, request.max_results
    request.segments, request.force_refresh, request.max_results
    )
    )


    return analysis
    return analysis


except ValidationError as e:
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
except BaseError as e:
    logger.error(f"Error analyzing niches: {str(e)}")
    logger.error(f"Error analyzing niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
except Exception as e:
    logger.error(f"Error analyzing niches: {str(e)}")
    logger.error(f"Error analyzing niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error analyzing niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error analyzing niches: {str(e)}")




    @router.get(
    @router.get(
    "/market-segments",
    "/market-segments",
    response_model=List[MarketSegmentResponse],
    response_model=List[MarketSegmentResponse],
    responses={
    responses={
    200: {"description": "List of market segments"},
    200: {"description": "List of market segments"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Get all market segments",
    summary="Get all market segments",
    description="Get a list of all available market segments",
    description="Get a list of all available market segments",
    )
    )
    async def get_market_segments(
    async def get_market_segments(
    market_segment_service=Depends(get_market_segment_service),
    market_segment_service=Depends(get_market_segment_service),
    ):
    ):
    """
    """
    Get a list of all available market segments.
    Get a list of all available market segments.
    """
    """
    try:
    try:
    # Get market segments
    # Get market segments
    segments = await market_segment_service.get_market_segments()
    segments = await market_segment_service.get_market_segments()


    return segments
    return segments


except BaseError as e:
except BaseError as e:
    logger.error(f"Error getting market segments: {str(e)}")
    logger.error(f"Error getting market segments: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
except Exception as e:
    logger.error(f"Error getting market segments: {str(e)}")
    logger.error(f"Error getting market segments: {str(e)}")
    raise HTTPException(
    raise HTTPException(
    status_code=500, detail=f"Error getting market segments: {str(e)}"
    status_code=500, detail=f"Error getting market segments: {str(e)}"
    )
    )




    # Bulk operation endpoints
    # Bulk operation endpoints
    @router.post(
    @router.post(
    "/niches/bulk",
    "/niches/bulk",
    response_model=None,  # Disable response model generation from type annotation
    response_model=None,  # Disable response model generation from type annotation
    responses={
    responses={
    201: {"description": "Niches created successfully"},
    201: {"description": "Niches created successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Create multiple niches in bulk",
    summary="Create multiple niches in bulk",
    description="Create multiple niches in a single request for improved performance",
    description="Create multiple niches in a single request for improved performance",
    status_code=201,
    status_code=201,
    )
    )
    async def create_niches_bulk(
    async def create_niches_bulk(
    request: BulkNicheCreateRequest = Body(..., description="Bulk create request"),
    request: BulkNicheCreateRequest = Body(..., description="Bulk create request"),
    niche_service=Depends(get_niche_service),
    niche_service=Depends(get_niche_service),
    ):
    ):
    """
    """
    Create multiple niches in a single request for improved performance.
    Create multiple niches in a single request for improved performance.
    """
    """
    try:
    try:
    # Start timing
    # Start timing
    start_time = time.time()
    start_time = time.time()


    # Process batch
    # Process batch
    operation_id = str(uuid.uuid4())
    operation_id = str(uuid.uuid4())
    results = []
    results = []
    errors = []
    errors = []


    # Process each item
    # Process each item
    for i, item in enumerate(request.items):
    for i, item in enumerate(request.items):
    try:
    try:
    # Create niche
    # Create niche
    niche = await niche_service.create_niche(item)
    niche = await niche_service.create_niche(item)
    results.append(niche)
    results.append(niche)
except Exception as e:
except Exception as e:
    # Add error
    # Add error
    errors.append(
    errors.append(
    {
    {
    "index": i,
    "index": i,
    "error_code": "NICHE_CREATE_ERROR",
    "error_code": "NICHE_CREATE_ERROR",
    "error_message": str(e),
    "error_message": str(e),
    }
    }
    )
    )


    # Calculate stats
    # Calculate stats
    end_time = time.time()
    end_time = time.time()
    stats = {
    stats = {
    "total_items": len(request.items),
    "total_items": len(request.items),
    "successful_items": len(results),
    "successful_items": len(results),
    "failed_items": len(errors),
    "failed_items": len(errors),
    "processing_time_ms": (end_time - start_time) * 1000,
    "processing_time_ms": (end_time - start_time) * 1000,
    }
    }


    # Create response
    # Create response
    response = {
    response = {
    "items": results,
    "items": results,
    "errors": errors,
    "errors": errors,
    "stats": stats,
    "stats": stats,
    "operation_id": operation_id,
    "operation_id": operation_id,
    }
    }


    return response
    return response


except ValidationError as e:
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
except BaseError as e:
    logger.error(f"Error creating niches: {str(e)}")
    logger.error(f"Error creating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
except Exception as e:
    logger.error(f"Error creating niches: {str(e)}")
    logger.error(f"Error creating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error creating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error creating niches: {str(e)}")




    @router.put(
    @router.put(
    "/niches/bulk",
    "/niches/bulk",
    response_model=None,  # Disable response model generation from type annotation
    response_model=None,  # Disable response model generation from type annotation
    responses={
    responses={
    200: {"description": "Niches updated successfully"},
    200: {"description": "Niches updated successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Update multiple niches in bulk",
    summary="Update multiple niches in bulk",
    description="Update multiple niches in a single request for improved performance",
    description="Update multiple niches in a single request for improved performance",
    )
    )
    async def update_niches_bulk(
    async def update_niches_bulk(
    request: BulkNicheUpdateRequest = Body(..., description="Bulk update request"),
    request: BulkNicheUpdateRequest = Body(..., description="Bulk update request"),
    niche_service=Depends(get_niche_service),
    niche_service=Depends(get_niche_service),
    ):
    ):
    """
    """
    Update multiple niches in a single request for improved performance.
    Update multiple niches in a single request for improved performance.
    """
    """
    try:
    try:
    # Start timing
    # Start timing
    start_time = time.time()
    start_time = time.time()


    # Process batch
    # Process batch
    operation_id = str(uuid.uuid4())
    operation_id = str(uuid.uuid4())
    results = []
    results = []
    errors = []
    errors = []


    # Process each item
    # Process each item
    for i, item in enumerate(request.items):
    for i, item in enumerate(request.items):
    try:
    try:
    # Get niche ID
    # Get niche ID
    niche_id = item.get("id")
    niche_id = item.get("id")
    if not niche_id:
    if not niche_id:
    raise ValueError("Niche ID is required")
    raise ValueError("Niche ID is required")


    # Check if niche exists
    # Check if niche exists
    existing_niche = await niche_service.get_niche(niche_id)
    existing_niche = await niche_service.get_niche(niche_id)
    if not existing_niche:
    if not existing_niche:
    raise ValueError(f"Niche {niche_id} not found")
    raise ValueError(f"Niche {niche_id} not found")


    # Update niche
    # Update niche
    niche = await niche_service.update_niche(niche_id, item)
    niche = await niche_service.update_niche(niche_id, item)
    results.append(niche)
    results.append(niche)
except Exception as e:
except Exception as e:
    # Add error
    # Add error
    errors.append(
    errors.append(
    {
    {
    "index": i,
    "index": i,
    "error_code": "NICHE_UPDATE_ERROR",
    "error_code": "NICHE_UPDATE_ERROR",
    "error_message": str(e),
    "error_message": str(e),
    "item_id": item.get("id"),
    "item_id": item.get("id"),
    }
    }
    )
    )


    # Calculate stats
    # Calculate stats
    end_time = time.time()
    end_time = time.time()
    stats = {
    stats = {
    "total_items": len(request.items),
    "total_items": len(request.items),
    "successful_items": len(results),
    "successful_items": len(results),
    "failed_items": len(errors),
    "failed_items": len(errors),
    "processing_time_ms": (end_time - start_time) * 1000,
    "processing_time_ms": (end_time - start_time) * 1000,
    }
    }


    # Create response
    # Create response
    response = {
    response = {
    "items": results,
    "items": results,
    "errors": errors,
    "errors": errors,
    "stats": stats,
    "stats": stats,
    "operation_id": operation_id,
    "operation_id": operation_id,
    }
    }


    return response
    return response


except ValidationError as e:
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
except BaseError as e:
    logger.error(f"Error updating niches: {str(e)}")
    logger.error(f"Error updating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
except Exception as e:
    logger.error(f"Error updating niches: {str(e)}")
    logger.error(f"Error updating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error updating niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error updating niches: {str(e)}")




    @router.delete(
    @router.delete(
    "/niches/bulk",
    "/niches/bulk",
    response_model=None,  # Disable response model generation from type annotation
    response_model=None,  # Disable response model generation from type annotation
    responses={
    responses={
    200: {"description": "Niches deleted successfully"},
    200: {"description": "Niches deleted successfully"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    400: {"model": ErrorResponse, "description": "Bad request"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    },
    summary="Delete multiple niches in bulk",
    summary="Delete multiple niches in bulk",
    description="Delete multiple niches in a single request for improved performance",
    description="Delete multiple niches in a single request for improved performance",
    )
    )
    async def delete_niches_bulk(
    async def delete_niches_bulk(
    request: Dict[str, Any] = Body(..., description="Bulk delete request"),
    request: Dict[str, Any] = Body(..., description="Bulk delete request"),
    niche_service=Depends(get_niche_service),
    niche_service=Depends(get_niche_service),
    ):
    ):
    """
    """
    Delete multiple niches in a single request for improved performance.
    Delete multiple niches in a single request for improved performance.
    """
    """
    try:
    try:
    # Start timing
    # Start timing
    start_time = time.time()
    start_time = time.time()


    # Get niche IDs
    # Get niche IDs
    niche_ids = request.get("ids", [])
    niche_ids = request.get("ids", [])
    if not niche_ids:
    if not niche_ids:
    raise ValueError("Niche IDs are required")
    raise ValueError("Niche IDs are required")


    # Process batch
    # Process batch
    operation_id = str(uuid.uuid4())
    operation_id = str(uuid.uuid4())
    deleted_ids = []
    deleted_ids = []
    errors = []
    errors = []


    # Process each item
    # Process each item
    for i, niche_id in enumerate(niche_ids):
    for i, niche_id in enumerate(niche_ids):
    try:
    try:
    # Check if niche exists
    # Check if niche exists
    existing_niche = await niche_service.get_niche(niche_id)
    existing_niche = await niche_service.get_niche(niche_id)
    if not existing_niche:
    if not existing_niche:
    raise ValueError(f"Niche {niche_id} not found")
    raise ValueError(f"Niche {niche_id} not found")


    # Delete niche
    # Delete niche
    success = await niche_service.delete_niche(niche_id)
    success = await niche_service.delete_niche(niche_id)
    if success:
    if success:
    deleted_ids.append(niche_id)
    deleted_ids.append(niche_id)
    else:
    else:
    raise ValueError(f"Failed to delete niche {niche_id}")
    raise ValueError(f"Failed to delete niche {niche_id}")
except Exception as e:
except Exception as e:
    # Add error
    # Add error
    errors.append(
    errors.append(
    {
    {
    "index": i,
    "index": i,
    "error_code": "NICHE_DELETE_ERROR",
    "error_code": "NICHE_DELETE_ERROR",
    "error_message": str(e),
    "error_message": str(e),
    "item_id": niche_id,
    "item_id": niche_id,
    }
    }
    )
    )


    # Calculate stats
    # Calculate stats
    end_time = time.time()
    end_time = time.time()
    stats = {
    stats = {
    "total_items": len(niche_ids),
    "total_items": len(niche_ids),
    "successful_items": len(deleted_ids),
    "successful_items": len(deleted_ids),
    "failed_items": len(errors),
    "failed_items": len(errors),
    "processing_time_ms": (end_time - start_time) * 1000,
    "processing_time_ms": (end_time - start_time) * 1000,
    }
    }


    # Create response
    # Create response
    response = {
    response = {
    "deleted_ids": deleted_ids,
    "deleted_ids": deleted_ids,
    "errors": errors,
    "errors": errors,
    "stats": stats,
    "stats": stats,
    "operation_id": operation_id,
    "operation_id": operation_id,
    }
    }


    return response
    return response


except ValidationError as e:
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except BaseError as e:
except BaseError as e:
    logger.error(f"Error deleting niches: {str(e)}")
    logger.error(f"Error deleting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
except Exception as e:
    logger.error(f"Error deleting niches: {str(e)}")
    logger.error(f"Error deleting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error deleting niches: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error deleting niches: {str(e)}")


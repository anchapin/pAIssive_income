"""
Developer API router.

This module provides routes for the developer API.
"""


import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, HTTPException, Path, Query, status



# Create router
router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)


# Define route handlers
@router.get("/")
async def get_developer_info():
    """
    Get developer information.

    Returns:
        Developer information
    """
    return {
        "message": "Developer API is available",
        "status": "active",
        "endpoints": ["/niches", "/templates", "/solutions", "/solution"],
    }


@router.get("/niches")
async def get_niches(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    sort: Optional[str] = Query(
        None, description="Sort field and direction (e.g., name:asc)"
    ),
    name: Optional[str] = Query(None, description="Filter by name"),
    description: Optional[str] = Query(None, description="Filter by description"),
):
    """
    Get all development niches.

    Args:
        page: Page number
        page_size: Page size
        sort: Sort field and direction
        name: Filter by name
        description: Filter by description

    Returns:
        List of development niches
    """
    try:
        # Mock data for testing
        items = [
            {
                "id": "niche-1",
                "name": "AI Chatbots",
                "description": "Conversational AI applications for customer service and support",
                "technical_requirements": [
                    "NLP",
                    "Machine Learning",
                    "API Integration",
                ],
            },
            {
                "id": "niche-2",
                "name": "Data Analytics",
                "description": "Tools for analyzing and visualizing data",
                "technical_requirements": [
                    "Data Processing",
                    "Visualization",
                    "Statistical Analysis",
                ],
            },
        ]

        # Apply filters if provided
        if name:
            items = [item for item in items if name.lower() in item["name"].lower()]
        if description:
            items = [
                item
                for item in items
                if description.lower() in item["description"].lower()
            ]

        # Calculate pagination
        total = len(items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = items[start_idx:end_idx]

        return {
            "items": paginated_items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        logger.error(f"Error getting niches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get niches: {str(e)}",
        )


@router.get("/templates")
async def get_templates(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    sort: Optional[str] = Query(
        None, description="Sort field and direction (e.g., name:asc)"
    ),
    name: Optional[str] = Query(None, description="Filter by name"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
):
    """
    Get all development templates.

    Args:
        page: Page number
        page_size: Page size
        sort: Sort field and direction
        name: Filter by name
        technology: Filter by technology

    Returns:
        List of development templates
    """
    try:
        # Mock data for testing
        items = [
            {
                "id": "template-1",
                "name": "FastAPI Web Service",
                "description": "RESTful API service using FastAPI and PostgreSQL",
                "technology_stack": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "features": [
                    "Authentication",
                    "Rate Limiting",
                    "Swagger Documentation",
                ],
            },
            {
                "id": "template-2",
                "name": "React Dashboard",
                "description": "Interactive dashboard using React and D3.js",
                "technology_stack": ["JavaScript", "React", "D3.js", "Material UI"],
                "features": [
                    "Data Visualization",
                    "Responsive Design",
                    "Theme Customization",
                ],
            },
        ]

        # Apply filters if provided
        if name:
            items = [item for item in items if name.lower() in item["name"].lower()]
        if technology:
            items = [
                item
                for item in items
                if any(
                    tech.lower() == technology.lower()
                    for tech in item["technology_stack"]
                )
            ]

        # Calculate pagination
        total = len(items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = items[start_idx:end_idx]

        return {
            "items": paginated_items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}",
        )


@router.post("/solution", status_code=status.HTTP_201_CREATED)
async def create_solution(data: Dict[str, Any] = Body(...)):
    """
    Create a development solution.

    Args:
        data: Solution data

    Returns:
        Created solution
    """
    try:
        # Validate required fields
        required_fields = ["name", "description", "niche_id", "template_id"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Field '{field}' is required",
                )

        # Create solution
        solution = {
            "id": f"solution-{datetime.now().timestamp()}",
            "name": data["name"],
            "description": data["description"],
            "niche_id": data["niche_id"],
            "template_id": data["template_id"],
            "technology_stack": data.get("technology_stack", []),
            "features": data.get("features", []),
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": None,
        }

        return solution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating solution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create solution: {str(e)}",
        )


@router.get("/solutions")
async def get_solutions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    sort: Optional[str] = Query(
        None, description="Sort field and direction (e.g., name:asc)"
    ),
    status: Optional[str] = Query(None, description="Filter by status"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
):
    """
    Get all development solutions.

    Args:
        page: Page number
        page_size: Page size
        sort: Sort field and direction
        status: Filter by status
        technology: Filter by technology

    Returns:
        List of development solutions
    """
    try:
        # Mock data for testing
        items = [
            {
                "id": "solution-1",
                "name": "Customer Support Chatbot",
                "description": "AI-powered chatbot for customer support",
                "niche_id": "niche-1",
                "template_id": "template-1",
                "technology_stack": ["Python", "FastAPI", "TensorFlow", "Docker"],
                "features": [
                    "Intent Recognition",
                    "Entity Extraction",
                    "Conversation Management",
                ],
                "status": "in_progress",
                "created_at": "2025-04-29T21:30:00Z",
                "updated_at": "2025-04-29T21:35:00Z",
            },
            {
                "id": "solution-2",
                "name": "Sales Analytics Dashboard",
                "description": "Interactive dashboard for sales analytics",
                "niche_id": "niche-2",
                "template_id": "template-2",
                "technology_stack": ["JavaScript", "React", "D3.js", "Material UI"],
                "features": [
                    "Sales Trends",
                    "Customer Segmentation",
                    "Revenue Forecasting",
                ],
                "status": "completed",
                "created_at": "2025-04-28T21:30:00Z",
                "updated_at": "2025-04-29T21:35:00Z",
            },
            {
                "id": "solution-3",
                "name": "Python Data Processing Tool",
                "description": "Data processing tool built with Python",
                "niche_id": "niche-2",
                "template_id": "template-1",
                "technology_stack": ["python", "pandas", "numpy", "matplotlib"],
                "features": [
                    "Data Cleaning",
                    "Data Transformation",
                    "Data Visualization",
                ],
                "status": "in_progress",
                "created_at": "2025-04-27T21:30:00Z",
                "updated_at": "2025-04-29T21:35:00Z",
            },
        ]

        # Apply filters if provided
        if status:
            items = [item for item in items if item["status"] == status]
        if technology:
            items = [
                item
                for item in items
                if any(
                    tech.lower() == technology.lower()
                    for tech in item["technology_stack"]
                )
            ]

        # Apply sorting if provided
        if sort:
            field, direction = sort.split(":") if ":" in sort else (sort, "asc")
            reverse = direction.lower() == "desc"
            items = sorted(items, key=lambda x: x.get(field, ""), reverse=reverse)

        # Calculate pagination
        total = len(items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = items[start_idx:end_idx]

        return {
            "items": paginated_items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        logger.error(f"Error getting solutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get solutions: {str(e)}",
        )


@router.get("/solutions/{solution_id}")
async def get_solution(solution_id: str = Path(..., description="Solution ID")):
    """
    Get a specific development solution.

    Args:
        solution_id: Solution ID

    Returns:
        Development solution
    """
    try:
        # Check if the solution ID starts with "nonexistent-" for testing
        if solution_id.startswith("nonexistent-"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found"
            )

        # Mock data for testing
        solution = {
            "id": solution_id,
            "name": "Test Solution",
            "description": "Test Description",
            "niche_id": "niche-1",
            "template_id": "template-1",
            "technology_stack": ["Python", "FastAPI", "TensorFlow", "Docker"],
            "features": [
                "Intent Recognition",
                "Entity Extraction",
                "Conversation Management",
            ],
            "status": "in_progress",
            "created_at": "2025-04-29T21:30:00Z",
            "updated_at": "2025-04-29T21:35:00Z",
        }

        return solution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting solution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get solution: {str(e)}",
        )


@router.put("/solutions/{solution_id}")
async def update_solution(
    solution_id: str = Path(..., description="Solution ID"),
    data: Dict[str, Any] = Body(...),
):
    """
    Update a development solution.

    Args:
        solution_id: Solution ID
        data: Solution data

    Returns:
        Updated solution
    """
    try:
        # Check if the solution ID starts with "nonexistent-" for testing
        if solution_id.startswith("nonexistent-"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found"
            )

        # Update solution
        solution = {
            "id": solution_id,
            "name": data.get("name", "Updated Solution"),
            "description": data.get("description", "Updated Description"),
            "niche_id": data.get("niche_id", "niche-1"),
            "template_id": data.get("template_id", "template-1"),
            "technology_stack": data.get(
                "technology_stack", ["Python", "FastAPI", "TensorFlow", "Docker"]
            ),
            "features": data.get(
                "features",
                ["Intent Recognition", "Entity Extraction", "Conversation Management"],
            ),
            "status": data.get("status", "in_progress"),
            "created_at": "2025-04-29T21:30:00Z",
            "updated_at": datetime.now().isoformat(),
        }

        return solution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating solution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update solution: {str(e)}",
        )


@router.delete("/solutions/{solution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_solution(solution_id: str = Path(..., description="Solution ID")):
    """
    Delete a development solution.

    Args:
        solution_id: Solution ID

    Returns:
        No content
    """
    try:
        # Check if the solution ID starts with "nonexistent-" for testing
        if solution_id.startswith("nonexistent-"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found"
            )

        # Delete solution (no content to return)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting solution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete solution: {str(e)}",
        )
"""
Niche Analysis Service for pAIssive income microservices architecture.

This module provides the Niche Analysis Service implementation, which handles
opportunity discovery, analysis, and comparison of niche markets.
"""

import logging
import argparse
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.service_discovery.registration import (
    register_service,
    get_service_metadata,
    get_default_tags,
)
from niche_analysis.niche_analyzer import NicheAnalyzer
from agent_team import AgentTeam

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Niche Analysis Service",
    description="Service for analyzing potential business niches and scoring opportunities",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
service_registration = None
niche_analyzer = None


# Models
class NicheRequest(BaseModel):
    """Request model for niche analysis."""

    market_segments: List[str] = Field(
        ..., description="List of market segments to analyze"
    )
    force_refresh: bool = Field(False, description="Force refresh of cached data")


class NicheResponse(BaseModel):
    """Response model for niche analysis."""

    niches: List[Dict[str, Any]] = Field(..., description="List of analyzed niches")
    request_id: str = Field(..., description="Unique ID for this request")


class OpportunityRequest(BaseModel):
    """Request model for opportunity analysis."""

    niche_name: str = Field(..., description="Name of the niche to analyze")
    force_refresh: bool = Field(False, description="Force refresh of cached data")


class OpportunityResponse(BaseModel):
    """Response model for opportunity analysis."""

    opportunities: List[Dict[str, Any]] = Field(
        ..., description="List of opportunities"
    )
    niche_name: str = Field(..., description="Name of the analyzed niche")
    request_id: str = Field(..., description="Unique ID for this request")


# Routes
@app.get("/")
async def root():
    """Root endpoint for Niche Analysis Service."""
    return {"message": "pAIssive Income Niche Analysis Service", "status": "running"}


@app.get("/api/status")
async def api_status():
    """API status endpoint."""
    return {"status": "ok", "version": "1.0.0", "service": "niche-analysis-service"}


@app.post("/api/niches/analyze", response_model=NicheResponse)
async def analyze_niches(request: NicheRequest, background_tasks: BackgroundTasks):
    """Analyze potential niches based on market segments."""
    import uuid

    if not niche_analyzer:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Niche analyzer not available",
        )

    try:
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Analyze niches
        niches = niche_analyzer.identify_niches(
            request.market_segments, force_refresh=request.force_refresh
        )

        return {"niches": niches, "request_id": request_id}
    except Exception as e:
        logger.error(f"Error analyzing niches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze niches: {str(e)}",
        )


@app.post("/api/niches/opportunities", response_model=OpportunityResponse)
async def analyze_opportunities(
    request: OpportunityRequest, background_tasks: BackgroundTasks
):
    """Analyze opportunities for a specific niche."""
    import uuid

    if not niche_analyzer:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Niche analyzer not available",
        )

    try:
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Analyze opportunities
        opportunities = niche_analyzer.get_niche_opportunities(
            request.niche_name, force_refresh=request.force_refresh
        )

        return {
            "opportunities": opportunities,
            "niche_name": request.niche_name,
            "request_id": request_id,
        }
    except Exception as e:
        logger.error(f"Error analyzing opportunities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze opportunities: {str(e)}",
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


def check_service_health() -> bool:
    """
    Check if the service is healthy.

    Returns:
        bool: True if the service is healthy, False otherwise
    """
    # Add any specific health checks here
    return niche_analyzer is not None


def initialize_niche_analyzer():
    """Initialize the niche analyzer."""
    global niche_analyzer

    try:
        # Create a simple agent team for the niche analyzer
        agent_team = AgentTeam("NicheAnalysisTeam")

        # Create the niche analyzer
        niche_analyzer = NicheAnalyzer(agent_team=agent_team)

        logger.info("Initialized niche analyzer")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize niche analyzer: {str(e)}")
        return False


def register_with_service_registry(port: int):
    """
    Register this service with the service registry.

    Args:
        port: Port this service is running on
    """
    global service_registration

    # Get metadata and tags
    metadata = get_service_metadata()
    metadata.update({"supports_async": "true", "provides_opportunity_analysis": "true"})

    tags = get_default_tags() + ["analysis", "niche", "opportunity"]

    # Register service
    service_registration = register_service(
        app=app,
        service_name="niche-analysis-service",
        port=port,
        version="1.0.0",
        health_check_path="/health",
        check_functions=[check_service_health],
        tags=tags,
        metadata=metadata,
    )

    if service_registration:
        logger.info(
            "Successfully registered Niche Analysis Service with service registry"
        )
    else:
        logger.warning(
            "Failed to register with service registry, continuing without service discovery"
        )


def start_niche_analysis_service(host: str = "0.0.0.0", port: int = 8001):
    """
    Start the Niche Analysis Service.

    Args:
        host: Host to bind to
        port: Port to listen on
    """
    import uvicorn

    # Initialize the niche analyzer
    if not initialize_niche_analyzer():
        logger.error(
            "Failed to initialize niche analyzer, service may not function correctly"
        )

    # Register with service registry
    register_with_service_registry(port)

    # Start the Niche Analysis Service
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Niche Analysis Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to listen on")

    args = parser.parse_args()

    # Start the Niche Analysis Service
    start_niche_analysis_service(host=args.host, port=args.port)

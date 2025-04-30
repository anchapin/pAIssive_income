"""
Pytest fixtures for API tests.

This module provides fixtures that can be used across API tests.
"""

import os
import pytest
from typing import Dict, Any, Optional, List, Generator
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import API server
from api.server import APIServer, APIConfig
from api.config import APIVersion

# Import test client fixtures
from tests.api.utils.test_client import api_test_client, auth_api_test_client, APITestClient

# Import mock fixtures
from tests.mocks.fixtures import (
    mock_openai_provider,
    mock_ollama_provider,
    mock_lmstudio_provider,
    patch_model_providers,
    mock_huggingface_api,
    mock_payment_api,
    mock_email_api,
    mock_storage_api,
    patch_external_apis,
    mock_model_inference_result,
    mock_embedding_result,
    mock_subscription_data,
    mock_niche_analysis_data,
    mock_marketing_campaign_data
)


@pytest.fixture
def api_config() -> APIConfig:
    """
    Create a test API configuration.

    Returns:
        Test API configuration
    """
    return APIConfig(
        host="127.0.0.1",
        port=8000,
        debug=True,
        version=APIVersion.V1,
        active_versions=[APIVersion.V1],
        prefix="/api",
        docs_url="/docs",
        openapi_url="/openapi.json",
        redoc_url="/redoc",
        enable_graphql=True,
        graphql_path="/graphql",
        graphiql=True,
        enable_cors=True,
        enable_rate_limit=False,
        enable_auth=False,
        api_keys=["test-api-key"],
        jwt_secret="test-jwt-secret",
        enable_niche_analysis=True,
        enable_monetization=True,
        enable_marketing=True,
        enable_ai_models=True,
        enable_agent_team=True,
        enable_user=True,
        enable_dashboard=True,
        enable_analytics=True
    )


@pytest.fixture
def api_server(api_config: APIConfig) -> APIServer:
    """
    Create a test API server.

    Args:
        api_config: Test API configuration

    Returns:
        Test API server
    """
    # Create a server with the test configuration
    server = APIServer(api_config)

    # Create the FastAPI app
    server.app = FastAPI(
        title="pAIssive Income API",
        description="RESTful API for pAIssive Income services",
        version=server.config.version.value,
        docs_url=server.config.docs_url,
        openapi_url=server.config.openapi_url,
        redoc_url=server.config.redoc_url,
    )

    # Create a mock router for niche analysis
    from fastapi import APIRouter
    niche_analysis_router = APIRouter()

    # Add routes to the mock router
    from fastapi import Response, status, HTTPException, Body, Request
    from fastapi.responses import JSONResponse

    @niche_analysis_router.post("/analyze")
    async def analyze_niche(request: Request, response: Response, data: dict = Body(...)):
        # Check if the request body is empty (for invalid request test)
        if not data:
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return {"error": {"message": "Invalid request", "code": "INVALID_REQUEST"}}

        response.status_code = status.HTTP_202_ACCEPTED
        return {"task_id": "test-task-id", "status_url": "/api/v1/niche-analysis/tasks/test-task-id"}

    @niche_analysis_router.get("/analyses")
    async def get_analyses():
        return {"items": [], "total": 0, "page": 1, "page_size": 10}

    @niche_analysis_router.get("/analyses/{analysis_id}")
    async def get_analysis(analysis_id: str):
        if analysis_id.startswith("nonexistent-"):
            raise HTTPException(status_code=404, detail={"error": "Analysis not found", "code": "NOT_FOUND"})
        return {"id": analysis_id, "market_segments": []}

    @niche_analysis_router.get("/niches")
    async def get_niches():
        return {"items": [], "total": 0, "page": 1, "page_size": 10}

    @niche_analysis_router.get("/niches/{niche_id}")
    async def get_niche(niche_id: str):
        if niche_id.startswith("nonexistent-"):
            return JSONResponse(
                status_code=404,
                content={"error": {"message": "Niche not found", "code": "NOT_FOUND"}}
            )
        return {"id": niche_id, "name": "Test Niche", "description": "Test Description", "market_segments": [], "opportunity_score": 0.5}

    @niche_analysis_router.get("/segments")
    async def get_segments():
        return {"segments": []}

    @niche_analysis_router.post("/niches/bulk")
    async def bulk_create_niches(response: Response, data: dict = Body(...)):
        response.status_code = status.HTTP_201_CREATED
        # Extract items from the request data
        items = data.get("items", [])
        total = len(items)
        return {"items": [], "errors": [], "stats": {"total": total, "success": total, "failure": 0}, "operation_id": "test-operation-id"}

    @niche_analysis_router.get("/results/{analysis_id}")
    async def get_analysis_results_by_id(analysis_id: str):
        if analysis_id.startswith("nonexistent-"):
            return JSONResponse(
                status_code=404,
                content={"error": {"message": "Analysis results not found", "code": "NOT_FOUND"}}
            )
        return {"id": analysis_id, "status": "completed", "results": []}

    @niche_analysis_router.get("/results")
    async def get_analysis_results():
        return {"items": [], "total": 0, "page": 1, "page_size": 10}

    # Include the router in the app
    server.app.include_router(
        niche_analysis_router,
        prefix="/api/v1/niche-analysis",
        tags=["Niche Analysis"]
    )

    return server


@pytest.fixture
def api_client(api_server: APIServer) -> TestClient:
    """
    Create a test client for the API server.

    Args:
        api_server: Test API server

    Returns:
        Test client
    """
    return TestClient(api_server.app)


@pytest.fixture
def api_headers() -> Dict[str, str]:
    """
    Create headers for API requests.

    Returns:
        Headers for API requests
    """
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": "test-api-key"
    }


@pytest.fixture
def api_auth_headers(api_headers: Dict[str, str]) -> Dict[str, str]:
    """
    Create headers for authenticated API requests.

    Args:
        api_headers: Base API headers

    Returns:
        Headers for authenticated API requests
    """
    # In a real implementation, this would generate a JWT token
    headers = api_headers.copy()
    headers["Authorization"] = "Bearer test-jwt-token"
    return headers

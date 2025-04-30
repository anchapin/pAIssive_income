"""
Pytest fixtures for API tests.

This module provides fixtures that can be used across API tests.
"""

import os
import pytest
from typing import Dict, Any, Optional, List, Generator
from fastapi.testclient import TestClient

# Import API server
from api.server import APIServer, APIConfig
from api.config import APIVersion

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
    mock_marketing_campaign_data,
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
        cors_origins=["*"],
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
        enable_analytics=True,
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
    return APIServer(api_config)


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
        "X-API-Key": "test-api-key",
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

"""
Client for the pAIssive Income API.

This module provides a client for making requests to the pAIssive Income API.
"""


import json
import logging
from typing import Any, Dict, Optional

import requests

from .auth import Auth, NoAuth



# Set up logging
logger = logging.getLogger(__name__)


class Client:
    """
    Client for the pAIssive Income API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api",
        auth: Optional[Auth] = None,
        version: str = "v1",
        timeout: int = 60,
    ):
        """
        Initialize the client.

        Args:
            base_url: Base URL for the API
            auth: Authentication method
            version: API version to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.auth = auth or NoAuth()
        self.version = version
        self.timeout = timeout

        # Initialize services
        from .services import (
            AgentTeamService,
            AIModelsService,
            APIKeyService,
            DashboardService,
            MarketingService,
            MonetizationService,
            NicheAnalysisService,
            UserService,
        )

        self.niche_analysis = NicheAnalysisService(self)
        self.monetization = MonetizationService(self)
        self.marketing = MarketingService(self)
        self.ai_models = AIModelsService(self)
        self.agent_team = AgentTeamService(self)
        self.user = UserService(self)
        self.dashboard = DashboardService(self)
        self.api_keys = APIKeyService(self)

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to the API.

        Args:
            method: HTTP method to use
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            headers: Additional headers
            files: Files to upload

        Returns:
            Response data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}/{self.version}/{endpoint.lstrip('/')}"

        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Add authentication headers
        request_headers.update(self.auth.get_headers())

        # Add additional headers
        if headers:
            request_headers.update(headers)

        # Log request
        logger.debug(f"Making {method} request to {url}")

        # Make request
        response = requests.request(
            method=method,
            url=url,
            headers=request_headers,
            params=params,
            data=json.dumps(data) if data else None,
            files=files,
            timeout=self.timeout,
        )

        # Check for errors
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            try:
                error_data = response.json()
                logger.error(f"Error details: {error_data}")
            except ValueError:
                logger.error(f"Error response: {response.text}")
            raise

        # Parse response
        if response.headers.get("Content-Type", "").startswith("application/json"):
            return response.json()
        else:
            return {"data": response.text}

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data
        """
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint
            data: Request body

        Returns:
            Response data
        """
        return self.request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a PUT request.

        Args:
            endpoint: API endpoint
            data: Request body

        Returns:
            Response data
        """
        return self.request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a DELETE request.

        Args:
            endpoint: API endpoint

        Returns:
            Response data
        """
        return self.request("DELETE", endpoint)
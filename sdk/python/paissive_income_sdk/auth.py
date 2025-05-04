"""
Authentication classes for the pAIssive Income SDK.

This module provides authentication classes for the pAIssive Income API.
"""

from typing import Dict

class Auth:
    """
    Base authentication class.
    """

    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Authentication headers
        """
        return {}

class APIKeyAuth(Auth):
    """
    API key authentication.
    """

    def __init__(self, api_key: str):
        """
        Initialize API key authentication.

        Args:
            api_key: API key
        """
        self.api_key = api_key

    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Authentication headers
        """
        return {"X - API - Key": self.api_key}

class JWTAuth(Auth):
    """
    JWT authentication.
    """

    def __init__(self, token: str):
        """
        Initialize JWT authentication.

        Args:
            token: JWT token
        """
        self.token = token

    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Authentication headers
        """
        return {"Authorization": f"Bearer {self.token}"}

class NoAuth(Auth):
    """
    No authentication.
    """

    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Empty headers
        """
        return {}

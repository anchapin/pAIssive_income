"""
"""
Base service class for the pAIssive Income API.
Base service class for the pAIssive Income API.


This module provides a base service class that all other service classes inherit from.
This module provides a base service class that all other service classes inherit from.
"""
"""




from typing import Any, Dict, Optional
from typing import Any, Dict, Optional




class BaseService:
    class BaseService:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    Base service class.
    Base service class.
    """
    """


    def __init__(self, client):
    def __init__(self, client):
    """
    """
    Initialize the service.
    Initialize the service.


    Args:
    Args:
    client: API client
    client: API client
    """
    """
    self.client = client
    self.client = client


    def _get(
    def _get(
    self, endpoint: str, params: Optional[Dict[str, Any]] = None
    self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Make a GET request.
    Make a GET request.


    Args:
    Args:
    endpoint: API endpoint
    endpoint: API endpoint
    params: Query parameters
    params: Query parameters


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    return self.client.get(endpoint, params=params)
    return self.client.get(endpoint, params=params)


    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Make a POST request.
    Make a POST request.


    Args:
    Args:
    endpoint: API endpoint
    endpoint: API endpoint
    data: Request body
    data: Request body


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    return self.client.post(endpoint, data=data)
    return self.client.post(endpoint, data=data)


    def _put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    def _put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Make a PUT request.
    Make a PUT request.


    Args:
    Args:
    endpoint: API endpoint
    endpoint: API endpoint
    data: Request body
    data: Request body


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    return self.client.put(endpoint, data=data)
    return self.client.put(endpoint, data=data)


    def _delete(self, endpoint: str) -> Dict[str, Any]:
    def _delete(self, endpoint: str) -> Dict[str, Any]:
    """
    """
    Make a DELETE request.
    Make a DELETE request.


    Args:
    Args:
    endpoint: API endpoint
    endpoint: API endpoint


    Returns:
    Returns:
    Response data
    Response data
    """
    """
    return self.client.delete(endpoint)
    return self.client.delete(endpoint)
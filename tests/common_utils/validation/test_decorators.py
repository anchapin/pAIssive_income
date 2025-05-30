"""Test module for common_utils.validation.decorators."""

import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from common_utils.validation.decorators import (
    validate_path_params,
    validate_query_params,
    validate_request_body,
)


class MockRequest:
    """Mock request class for testing."""

    def __init__(self, json_data=None, query_params=None, path_params=None):
        """Initialize the mock request."""
        self.json_data = json_data or {}
        self.query_params = query_params or {}
        self.path_params = path_params or {}
        self.get_json = AsyncMock(return_value=self.json_data)


class TestModel(BaseModel):
    """Test model for validation."""

    name: str
    age: int = Field(gt=0)


class TestValidateRequestBody:
    """Test suite for validate_request_body decorator."""

    @pytest.mark.asyncio
    async def test_valid_request_body(self):
        """Test validate_request_body with valid request body."""
        # Define a test handler function
        @validate_request_body(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request with valid data
        request = MockRequest(json_data={"name": "Test User", "age": 30})

        # Call the handler
        response = await handler(request)

        # Check the response
        assert response["status"] == "success"
        assert response["data"]["name"] == "Test User"
        assert response["data"]["age"] == 30

    @pytest.mark.asyncio
    async def test_invalid_request_body(self):
        """Test validate_request_body with invalid request body."""
        # Define a test handler function
        @validate_request_body(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request with invalid data (negative age)
        request = MockRequest(json_data={"name": "Test User", "age": -5})

        # Call the handler
        response = await handler(request)

        # Check the response contains validation error
        assert "errors" in response
        assert len(response["errors"]) > 0
        assert "age" in response["errors"][0]["field"]

    @pytest.mark.asyncio
    async def test_missing_required_field(self):
        """Test validate_request_body with missing required field."""
        # Define a test handler function
        @validate_request_body(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request with missing required field (name)
        request = MockRequest(json_data={"age": 30})

        # Call the handler
        response = await handler(request)

        # Check the response contains validation error
        assert "errors" in response
        assert len(response["errors"]) > 0
        assert "name" in response["errors"][0]["field"]

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test validate_request_body handles exceptions."""
        # Define a test handler function
        @validate_request_body(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request that raises an exception when get_json is called
        request = MockRequest()
        request.get_json = AsyncMock(side_effect=Exception("Test exception"))

        # Call the handler
        response = await handler(request)

        # Check the response contains error
        assert "errors" in response
        assert len(response["errors"]) > 0
        assert "message" in response["errors"][0]
        # The actual error message depends on how the validation is implemented
        # Just check that there is a message, not its specific content
        assert isinstance(response["errors"][0]["message"], str)


class TestValidateQueryParams:
    """Test suite for validate_query_params decorator."""

    @pytest.mark.asyncio
    async def test_valid_query_params(self):
        """Test validate_query_params with valid query parameters."""
        # Define a test handler function
        @validate_query_params(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request with valid query parameters
        request = MockRequest(query_params={"name": "Test User", "age": "30"})

        # Call the handler
        response = await handler(request)

        # Check the response
        assert response["status"] == "success"
        assert response["data"]["name"] == "Test User"
        assert response["data"]["age"] == 30

    @pytest.mark.asyncio
    async def test_invalid_query_params(self):
        """Test validate_query_params with invalid query parameters."""
        # Define a test handler function
        @validate_query_params(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request with invalid query parameters (negative age)
        request = MockRequest(query_params={"name": "Test User", "age": "-5"})

        # Call the handler
        response = await handler(request)

        # Check the response contains validation error
        assert "errors" in response
        assert len(response["errors"]) > 0

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test validate_query_params handles exceptions."""
        # Define a test handler function
        @validate_query_params(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request that raises an exception
        request = MagicMock()
        request.query_params = MagicMock(side_effect=Exception("Test exception"))

        # Call the handler
        response = await handler(request)

        # Check the response contains error
        assert "errors" in response
        assert len(response["errors"]) > 0
        assert "message" in response["errors"][0]
        # The actual error message depends on how the validation is implemented
        # Just check that there is a message, not its specific content
        assert isinstance(response["errors"][0]["message"], str)


class TestValidatePathParams:
    """Test suite for validate_path_params decorator."""

    @pytest.mark.asyncio
    async def test_valid_path_params(self):
        """Test validate_path_params with valid path parameters."""
        # Define a test handler function
        @validate_path_params(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request with valid path parameters
        request = MockRequest(path_params={"name": "Test User", "age": "30"})

        # Call the handler
        response = await handler(request)

        # Check the response
        assert response["status"] == "success"
        assert response["data"]["name"] == "Test User"
        assert response["data"]["age"] == 30

    @pytest.mark.asyncio
    async def test_invalid_path_params(self):
        """Test validate_path_params with invalid path parameters."""
        # Define a test handler function
        @validate_path_params(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request with invalid path parameters (negative age)
        request = MockRequest(path_params={"name": "Test User", "age": "-5"})

        # Call the handler
        response = await handler(request)

        # Check the response contains validation error
        assert "errors" in response
        assert len(response["errors"]) > 0

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test validate_path_params handles exceptions."""
        # Define a test handler function
        @validate_path_params(TestModel)
        async def handler(request, model):
            return {"status": "success", "data": model.dict()}

        # Create a mock request that raises an exception
        request = MagicMock()
        request.path_params = MagicMock(side_effect=Exception("Test exception"))

        # Call the handler
        response = await handler(request)

        # Check the response contains error
        assert "errors" in response
        assert len(response["errors"]) > 0
        assert "message" in response["errors"][0]
        # The actual error message depends on how the validation is implemented
        # Just check that there is a message, not its specific content
        assert isinstance(response["errors"][0]["message"], str)

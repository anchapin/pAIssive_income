"""
Tests for the AI models API.

This module contains tests for the AI models API endpoints.
"""

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_ai_model_data, generate_id
from tests.api.utils.test_validators import (
    validate_bulk_response,
    validate_error_response,
    validate_field_equals,
    validate_field_exists,
    validate_field_not_empty,
    validate_field_type,
    validate_json_response,
    validate_list_contains,
    validate_list_contains_dict_with_field,
    validate_list_length,
    validate_list_max_length,
    validate_list_min_length,
    validate_list_not_empty,
    validate_paginated_response,
    validate_status_code,
    validate_success_response,
)


class TestAIModelsAPI:
    """Tests for the AI models API."""

    def test_get_models(self, api_test_client: APITestClient):
        """Test getting all AI models."""
        # Make request
        response = api_test_client.get("ai-models/models")

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

    def test_get_model(self, api_test_client: APITestClient):
        """Test getting a specific AI model."""
        # Generate a random ID
        model_id = generate_id()

        # Make request
        response = api_test_client.get(f"ai-models/models/{model_id}")

        # This might return 404 if the model doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", model_id)
            validate_field_exists(result, "name")
            validate_field_type(result, "name", str)
            validate_field_exists(result, "description")
            validate_field_type(result, "description", str)
            validate_field_exists(result, "model_type")
            validate_field_type(result, "model_type", str)
            validate_field_exists(result, "provider")
            validate_field_type(result, "provider", str)
            validate_field_exists(result, "version")
            validate_field_type(result, "version", str)
            validate_field_exists(result, "capabilities")
            validate_field_type(result, "capabilities", list)

    def test_run_inference(self, api_test_client: APITestClient):
        """Test running inference on an AI model."""
        # Generate a random ID
        model_id = generate_id()

        # Generate test data
        data = {
            "model_id": model_id,
            "input": "Hello, world!",
            "parameters": {"temperature": 0.7, "max_tokens": 100},
        }

        # Make request
        response = api_test_client.post("ai-models/inference", data)

        # This might return 404 if the model doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "model_id")
            validate_field_equals(result, "model_id", model_id)
            validate_field_exists(result, "output")
            validate_field_type(result, "output", str)
            validate_field_exists(result, "metrics")
            validate_field_type(result, "metrics", dict)

    def test_get_model_metrics(self, api_test_client: APITestClient):
        """Test getting metrics for a specific AI model."""
        # Generate a random ID
        model_id = generate_id()

        # Make request
        response = api_test_client.get(f"ai-models/models/{model_id}/metrics")

        # This might return 404 if the model doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "model_id")
            validate_field_equals(result, "model_id", model_id)
            validate_field_exists(result, "request_count")
            validate_field_type(result, "request_count", int)
            validate_field_exists(result, "error_count")
            validate_field_type(result, "error_count", int)
            validate_field_exists(result, "token_count")
            validate_field_type(result, "token_count", int)
            validate_field_exists(result, "latency_mean_ms")
            assert isinstance(result["latency_mean_ms"], (int, float))
            validate_field_exists(result, "latency_p90_ms")
            assert isinstance(result["latency_p90_ms"], (int, float))
            validate_field_exists(result, "latency_p99_ms")
            assert isinstance(result["latency_p99_ms"], (int, float))

    def test_get_model_providers(self, api_test_client: APITestClient):
        """Test getting all AI model providers."""
        # Make request
        response = api_test_client.get("ai-models/providers")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "providers")
        validate_field_type(result, "providers", list)

    def test_get_model_types(self, api_test_client: APITestClient):
        """Test getting all AI model types."""
        # Make request
        response = api_test_client.get("ai-models/types")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "types")
        validate_field_type(result, "types", list)

    def test_batch_inference(self, api_test_client: APITestClient):
        """Test batch inference on an AI model."""
        # Generate a random ID
        model_id = generate_id()

        # Generate test data
        data = {
            "model_id": model_id,
            "inputs": ["Hello, world!", "How are you?", "What is AI?"],
            "parameters": {"temperature": 0.7, "max_tokens": 100},
        }

        # Make request
        response = api_test_client.post("ai-models/batch-inference", data)

        # This might return 404 if the model doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response, 202)  # Accepted (async operation)

            # Validate fields
            validate_field_exists(result, "task_id")
            validate_field_type(result, "task_id", str)
            validate_field_not_empty(result, "task_id")
            validate_field_exists(result, "status_url")
            validate_field_type(result, "status_url", str)
            validate_field_not_empty(result, "status_url")

    def test_filter_models(self, api_test_client: APITestClient):
        """Test filtering AI models."""
        # Make request with filter
        response = api_test_client.get(
            "ai-models/models",
            params={"filter": "provider:eq:openai", "sort": "name:asc", "page": 1, "page_size": 10},
        )

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

        # If there are items, validate that they match the filter
        if result["items"]:
            for item in result["items"]:
                validate_field_exists(item, "provider")
                validate_field_equals(item, "provider", "openai")

    def test_invalid_inference_request(self, api_test_client: APITestClient):
        """Test invalid inference request."""
        # Make request with invalid data
        response = api_test_client.post("ai-models/inference", {})

        # Validate error response
        validate_error_response(response, 422)  # Unprocessable Entity

    def test_nonexistent_model(self, api_test_client: APITestClient):
        """Test getting a nonexistent AI model."""
        # Generate a random ID that is unlikely to exist
        model_id = "nonexistent-" + generate_id()

        # Make request
        response = api_test_client.get(f"ai-models/models/{model_id}")

        # Validate error response
        validate_error_response(response, 404)  # Not Found

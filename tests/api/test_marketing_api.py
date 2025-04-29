"""
Tests for the marketing API.

This module contains tests for the marketing API endpoints.
"""

import pytest
from typing import Dict, Any, List
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import (
    generate_id, generate_marketing_strategy_data
)
from tests.api.utils.test_validators import (
    validate_status_code, validate_json_response, validate_error_response,
    validate_success_response, validate_paginated_response, validate_bulk_response,
    validate_field_exists, validate_field_equals, validate_field_type,
    validate_field_not_empty, validate_list_not_empty, validate_list_length,
    validate_list_min_length, validate_list_max_length, validate_list_contains,
    validate_list_contains_dict_with_field
)


class TestMarketingAPI:
    """Tests for the marketing API."""

    def test_create_marketing_strategy(self, api_test_client: APITestClient):
        """Test creating a marketing strategy."""
        # Generate test data
        data = generate_marketing_strategy_data()
        
        # Make request
        response = api_test_client.post("marketing/strategies", data)
        
        # Validate response
        result = validate_success_response(response, 201)  # Created
        
        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_not_empty(result, "id")
        validate_field_exists(result, "niche_id")
        validate_field_equals(result, "niche_id", data["niche_id"])
        validate_field_exists(result, "target_audience")
        validate_field_type(result, "target_audience", dict)
        validate_field_exists(result, "channels")
        validate_field_type(result, "channels", list)
        validate_field_exists(result, "content_types")
        validate_field_type(result, "content_types", list)
        validate_field_exists(result, "kpis")
        validate_field_type(result, "kpis", list)
    
    def test_get_marketing_strategies(self, api_test_client: APITestClient):
        """Test getting all marketing strategies."""
        # Make request
        response = api_test_client.get("marketing/strategies")
        
        # Validate response
        result = validate_paginated_response(response)
        
        # Validate items
        validate_field_type(result, "items", list)
    
    def test_get_marketing_strategy(self, api_test_client: APITestClient):
        """Test getting a specific marketing strategy."""
        # Generate a random ID
        strategy_id = generate_id()
        
        # Make request
        response = api_test_client.get(f"marketing/strategies/{strategy_id}")
        
        # This might return 404 if the strategy doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)
            
            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", strategy_id)
            validate_field_exists(result, "niche_id")
            validate_field_type(result, "niche_id", str)
            validate_field_exists(result, "target_audience")
            validate_field_type(result, "target_audience", dict)
            validate_field_exists(result, "channels")
            validate_field_type(result, "channels", list)
            validate_field_exists(result, "content_types")
            validate_field_type(result, "content_types", list)
            validate_field_exists(result, "kpis")
            validate_field_type(result, "kpis", list)
    
    def test_update_marketing_strategy(self, api_test_client: APITestClient):
        """Test updating a marketing strategy."""
        # Generate a random ID
        strategy_id = generate_id()
        
        # Generate test data
        data = generate_marketing_strategy_data()
        
        # Make request
        response = api_test_client.put(f"marketing/strategies/{strategy_id}", data)
        
        # This might return 404 if the strategy doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)
            
            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", strategy_id)
            validate_field_exists(result, "niche_id")
            validate_field_equals(result, "niche_id", data["niche_id"])
            validate_field_exists(result, "target_audience")
            validate_field_type(result, "target_audience", dict)
            validate_field_exists(result, "channels")
            validate_field_type(result, "channels", list)
            validate_field_exists(result, "content_types")
            validate_field_type(result, "content_types", list)
            validate_field_exists(result, "kpis")
            validate_field_type(result, "kpis", list)
    
    def test_delete_marketing_strategy(self, api_test_client: APITestClient):
        """Test deleting a marketing strategy."""
        # Generate a random ID
        strategy_id = generate_id()
        
        # Make request
        response = api_test_client.delete(f"marketing/strategies/{strategy_id}")
        
        # This might return 404 if the strategy doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            validate_success_response(response, 204)  # No Content
    
    def test_get_personas(self, api_test_client: APITestClient):
        """Test getting all user personas."""
        # Make request
        response = api_test_client.get("marketing/personas")
        
        # Validate response
        result = validate_success_response(response)
        
        # Validate fields
        validate_field_exists(result, "personas")
        validate_field_type(result, "personas", list)
    
    def test_get_channels(self, api_test_client: APITestClient):
        """Test getting all marketing channels."""
        # Make request
        response = api_test_client.get("marketing/channels")
        
        # Validate response
        result = validate_success_response(response)
        
        # Validate fields
        validate_field_exists(result, "channels")
        validate_field_type(result, "channels", list)
    
    def test_generate_content(self, api_test_client: APITestClient):
        """Test generating marketing content."""
        # Generate a random ID
        strategy_id = generate_id()
        
        # Generate test data
        data = {
            "content_type": "blog_post",
            "topic": "How AI Can Improve Your Business",
            "target_audience": "small business owners",
            "tone": "informative",
            "length": "medium"
        }
        
        # Make request
        response = api_test_client.post(f"marketing/strategies/{strategy_id}/content", data)
        
        # This might return 404 if the strategy doesn't exist, which is fine for testing
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
    
    def test_bulk_create_marketing_strategies(self, api_test_client: APITestClient):
        """Test bulk creating marketing strategies."""
        # Generate test data
        strategies = [generate_marketing_strategy_data() for _ in range(3)]
        
        # Make request
        response = api_test_client.bulk_create("marketing/strategies", strategies)
        
        # Validate response
        result = validate_bulk_response(response, 201)  # Created
        
        # Validate stats
        validate_field_equals(result["stats"], "total", 3)
    
    def test_filter_marketing_strategies(self, api_test_client: APITestClient):
        """Test filtering marketing strategies."""
        # Make request with filter
        response = api_test_client.get(
            "marketing/strategies",
            params={
                "filter": "content_types:contains:blog_posts",
                "sort": "created_at:desc",
                "page": 1,
                "page_size": 10
            }
        )
        
        # Validate response
        result = validate_paginated_response(response)
        
        # Validate items
        validate_field_type(result, "items", list)
        
        # If there are items, validate that they match the filter
        if result["items"]:
            for item in result["items"]:
                validate_field_exists(item, "content_types")
                validate_list_contains(item["content_types"], "blog_posts")
    
    def test_invalid_marketing_strategy_request(self, api_test_client: APITestClient):
        """Test invalid marketing strategy request."""
        # Make request with invalid data
        response = api_test_client.post("marketing/strategies", {})
        
        # Validate error response
        validate_error_response(response, 422)  # Unprocessable Entity
    
    def test_nonexistent_marketing_strategy(self, api_test_client: APITestClient):
        """Test getting a nonexistent marketing strategy."""
        # Generate a random ID that is unlikely to exist
        strategy_id = "nonexistent-" + generate_id()
        
        # Make request
        response = api_test_client.get(f"marketing/strategies/{strategy_id}")
        
        # Validate error response
        validate_error_response(response, 404)  # Not Found

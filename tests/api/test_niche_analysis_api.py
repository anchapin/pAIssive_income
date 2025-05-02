"""
Tests for the niche analysis API.

This module contains tests for the niche analysis API endpoints.
"""

import pytest
from typing import Dict, Any, List
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import (
    generate_id, generate_niche_analysis_data, generate_niche_data
)
from tests.api.utils.test_validators import (
    validate_status_code, validate_json_response, validate_error_response,
    validate_success_response, validate_paginated_response, validate_bulk_response,
    validate_field_exists, validate_field_equals, validate_field_type,
    validate_field_not_empty, validate_list_not_empty, validate_list_length,
    validate_list_min_length, validate_list_max_length, validate_list_contains,
    validate_list_contains_dict_with_field
)


class TestNicheAnalysisAPI:
    """Tests for the niche analysis API."""

    def test_analyze_niche(self, api_test_client: APITestClient):
        """Test analyzing a niche."""
        # Generate test data
        data = generate_niche_analysis_data()
        
        # Make request
        response = api_test_client.post("niche-analysis/analyze", data)
        
        # Validate response
        result = validate_success_response(response, 202)  # Accepted (async operation)
        
        # Validate fields
        validate_field_exists(result, "task_id")
        validate_field_type(result, "task_id", str)
        validate_field_not_empty(result, "task_id")
        
        # Validate that the response includes a status URL
        validate_field_exists(result, "status_url")
        validate_field_type(result, "status_url", str)
        validate_field_not_empty(result, "status_url")
    
    def test_get_analyses(self, api_test_client: APITestClient):
        """Test getting all niche analyses."""
        # Make request
        response = api_test_client.get("niche-analysis/analyses")
        
        # Validate response
        result = validate_paginated_response(response)
        
        # Validate items
        validate_field_type(result, "items", list)
    
    def test_get_analysis(self, api_test_client: APITestClient):
        """Test getting a specific niche analysis."""
        # Generate a random ID
        analysis_id = generate_id()
        
        # Make request
        response = api_test_client.get(f"niche-analysis/analyses/{analysis_id}")
        
        # This might return 404 if the analysis doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)
            
            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", analysis_id)
            validate_field_exists(result, "market_segments")
            validate_field_type(result, "market_segments", list)
    
    def test_get_niches(self, api_test_client: APITestClient):
        """Test getting all niches."""
        # Make request
        response = api_test_client.get("niche-analysis/niches")
        
        # Validate response
        result = validate_paginated_response(response)
        
        # Validate items
        validate_field_type(result, "items", list)
    
    def test_get_niche(self, api_test_client: APITestClient):
        """Test getting a specific niche."""
        # Generate a random ID
        niche_id = generate_id()
        
        # Make request
        response = api_test_client.get(f"niche-analysis/niches/{niche_id}")
        
        # This might return 404 if the niche doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)
            
            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", niche_id)
            validate_field_exists(result, "name")
            validate_field_type(result, "name", str)
            validate_field_exists(result, "description")
            validate_field_type(result, "description", str)
            validate_field_exists(result, "market_segments")
            validate_field_type(result, "market_segments", list)
            validate_field_exists(result, "opportunity_score")
            assert isinstance(result["opportunity_score"], (int, float))
    
    def test_get_segments(self, api_test_client: APITestClient):
        """Test getting all market segments."""
        # Make request
        response = api_test_client.get("niche-analysis/segments")
        
        # Validate response
        result = validate_success_response(response)
        
        # Validate fields
        validate_field_exists(result, "segments")
        validate_field_type(result, "segments", list)
    
    def test_bulk_create_niches(self, api_test_client: APITestClient):
        """Test bulk creating niches."""
        # Generate test data
        niches = [generate_niche_data() for _ in range(3)]
        
        # Make request
        response = api_test_client.bulk_create("niche-analysis/niches", niches)
        
        # Validate response
        result = validate_bulk_response(response, 201)  # Created
        
        # Validate stats
        validate_field_equals(result["stats"], "total", 3)
    
    def test_filter_niches(self, api_test_client: APITestClient):
        """Test filtering niches."""
        # Make request with filter
        response = api_test_client.get(
            "niche-analysis/niches",
            params={
                "filter": "market_segments:contains:e-commerce",
                "sort": "opportunity_score:desc",
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
                validate_field_exists(item, "market_segments")
                validate_list_contains(item["market_segments"], "e-commerce")
    
    def test_invalid_analysis_request(self, api_test_client: APITestClient):
        """Test invalid analysis request."""
        # Make request with invalid data
        response = api_test_client.post("niche-analysis/analyze", {})
        
        # Validate error response
        validate_error_response(response, 422)  # Unprocessable Entity
    
    def test_nonexistent_niche(self, api_test_client: APITestClient):
        """Test getting a nonexistent niche."""
        # Generate a random ID that is unlikely to exist
        niche_id = "nonexistent-" + generate_id()
        
        # Make request
        response = api_test_client.get(f"niche-analysis/niches/{niche_id}")
        
        # Validate error response
        validate_error_response(response, 404)  # Not Found
    
    def test_get_analysis_results_by_id(self, api_test_client: APITestClient):
        """Test getting analysis results by ID."""
        # First create an analysis
        data = generate_niche_analysis_data()
        analysis_response = api_test_client.post("niche-analysis/analyze", data)
        analysis_result = validate_success_response(analysis_response, 202)
        analysis_id = analysis_result["task_id"]
        
        # Make request for results
        response = api_test_client.get(f"niche-analysis/results/{analysis_id}")
        
        # Handle both completed and in-progress states
        if response.status_code == 200:
            # Analysis complete
            result = validate_success_response(response)
            
            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", analysis_id)
            validate_field_exists(result, "status")
            validate_field_equals(result, "status", "completed")
            validate_field_exists(result, "results")
            validate_field_type(result, "results", list)
            
            # Validate result items
            if result["results"]:
                first_result = result["results"][0]
                validate_field_exists(first_result, "niche_name")
                validate_field_exists(first_result, "opportunity_score")
                validate_field_exists(first_result, "market_size")
                validate_field_exists(first_result, "competition_level")
                validate_field_exists(first_result, "trend_analysis")
        elif response.status_code == 202:
            # Analysis still in progress
            result = validate_success_response(response, 202)
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", analysis_id)
            validate_field_exists(result, "status")
            validate_field_equals(result, "status", "in_progress")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

    def test_get_all_analysis_results(self, api_test_client: APITestClient):
        """Test getting all analysis results."""
        # Make request
        response = api_test_client.get("niche-analysis/results")
        
        # Validate response
        result = validate_paginated_response(response)
        
        # Validate items structure
        validate_field_type(result, "items", list)
        
        # If there are items, validate their structure
        if result["items"]:
            first_item = result["items"][0]
            validate_field_exists(first_item, "id")
            validate_field_exists(first_item, "status")
            validate_field_exists(first_item, "created_at")
            validate_field_exists(first_item, "updated_at")
            
            # If the analysis is complete, validate results
            if first_item["status"] == "completed":
                validate_field_exists(first_item, "results")
                validate_field_type(first_item["results"], list)

    def test_get_analysis_results_with_filters(self, api_test_client: APITestClient):
        """Test getting analysis results with filters."""
        # Make request with filters
        response = api_test_client.get(
            "niche-analysis/results",
            params={
                "status": "completed",
                "sort": "created_at:desc",
                "page": 1,
                "page_size": 10
            }
        )
        
        # Validate response
        result = validate_paginated_response(response)
        
        # Validate items
        validate_field_type(result, "items", list)
        
        # If there are items, validate they match the filter
        if result["items"]:
            for item in result["items"]:
                validate_field_equals(item, "status", "completed")

    def test_nonexistent_analysis_results(self, api_test_client: APITestClient):
        """Test getting results for a nonexistent analysis."""
        # Generate a random ID that is unlikely to exist
        analysis_id = "nonexistent-" + generate_id()
        
        # Make request
        response = api_test_client.get(f"niche-analysis/results/{analysis_id}")
        
        # Validate error response
        validate_error_response(response, 404)  # Not Found

    def test_update_niche(self, api_test_client: APITestClient):
        """Test updating a niche."""
        # Generate a random ID and test data
        niche_id = generate_id()
        data = {
            "name": "Updated AI Assistant Niche",
            "description": "Updated description for AI assistant tools",
            "market_segments": ["productivity", "software-development", "content-creation"],
            "target_audience": ["developers", "content creators", "knowledge workers"],
            "opportunity_score_threshold": 0.8,
            "metadata": {
                "complexity": "medium",
                "implementation_time": "3-6 months",
                "initial_investment": "medium"
            }
        }

        # Make request
        response = api_test_client.put(f"niche-analysis/niches/{niche_id}", data)

        # This might return 404 if the niche doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", niche_id)
            validate_field_exists(result, "name")
            validate_field_equals(result, "name", data["name"])
            validate_field_exists(result, "description")
            validate_field_equals(result, "description", data["description"])
            validate_field_exists(result, "market_segments")
            validate_field_type(result, "market_segments", list)
            for segment in data["market_segments"]:
                validate_list_contains(result["market_segments"], segment)
            validate_field_exists(result, "target_audience")
            validate_field_type(result, "target_audience", list)
            validate_field_exists(result, "opportunity_score")
            assert isinstance(result["opportunity_score"], (int, float))
            validate_field_exists(result, "metadata")
            validate_field_type(result, "metadata", dict)
            validate_field_exists(result, "updated_at")
            validate_field_type(result, "updated_at", str)

    def test_delete_niche(self, api_test_client: APITestClient):
        """Test deleting a niche."""
        # Generate a random ID
        niche_id = generate_id()

        # Make request
        response = api_test_client.delete(f"niche-analysis/niches/{niche_id}")

        # This might return 404 if the niche doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            validate_success_response(response, 204)  # No Content

    def test_bulk_update_niches(self, api_test_client: APITestClient):
        """Test bulk updating niches."""
        # Generate test data for multiple niches
        niches = [
            {
                "id": generate_id(),
                "name": f"Updated Niche {i}",
                "description": f"Updated description for niche {i}",
                "market_segments": ["segment-1", "segment-2"],
                "opportunity_score_threshold": 0.7 + (i * 0.1)
            }
            for i in range(3)
        ]

        # Make request
        response = api_test_client.bulk_update("niche-analysis/niches", niches)

        # Validate response
        result = validate_bulk_response(response)

        # Validate stats
        validate_field_exists(result, "stats")
        validate_field_exists(result["stats"], "total")
        validate_field_equals(result["stats"], "total", len(niches))
        validate_field_exists(result["stats"], "updated")
        validate_field_exists(result["stats"], "failed")
        assert result["stats"]["updated"] + result["stats"]["failed"] == len(niches)

        # Validate updated items
        validate_field_exists(result, "items")
        validate_field_type(result, "items", list)
        for item in result["items"]:
            validate_field_exists(item, "id")
            validate_field_exists(item, "success")
            if item["success"]:
                validate_field_exists(item, "data")
                validate_field_type(item, "data", dict)
                validate_field_exists(item["data"], "name")
                validate_field_exists(item["data"], "description")
                validate_field_exists(item["data"], "market_segments")
                validate_field_exists(item["data"], "opportunity_score")
            else:
                validate_field_exists(item, "error")
                validate_field_type(item, "error", dict)

    def test_bulk_delete_niches(self, api_test_client: APITestClient):
        """Test bulk deleting niches."""
        # Generate niche IDs to delete
        niche_ids = [generate_id() for _ in range(3)]

        # Make request
        response = api_test_client.bulk_delete("niche-analysis/niches", niche_ids)

        # Validate response
        result = validate_bulk_response(response)

        # Validate stats
        validate_field_exists(result, "stats")
        validate_field_exists(result["stats"], "total")
        validate_field_equals(result["stats"], "total", len(niche_ids))
        validate_field_exists(result["stats"], "deleted")
        validate_field_exists(result["stats"], "failed")
        assert result["stats"]["deleted"] + result["stats"]["failed"] == len(niche_ids)

        # Validate results for each ID
        validate_field_exists(result, "items")
        validate_field_type(result, "items", list)
        for item in result["items"]:
            validate_field_exists(item, "id")
            validate_field_exists(item, "success")
            if not item["success"]:
                validate_field_exists(item, "error")
                validate_field_type(item, "error", dict)

    def test_invalid_niche_operations(self, api_test_client: APITestClient):
        """Test invalid niche operations."""
        # Test invalid niche update
        niche_id = generate_id()
        response = api_test_client.put(f"niche-analysis/niches/{niche_id}", {
            "name": "",  # Empty name
            "market_segments": "invalid"  # Should be a list
        })
        validate_error_response(response, 422)  # Unprocessable Entity

        # Test update with nonexistent ID
        response = api_test_client.put("niche-analysis/niches/nonexistent-id", {
            "name": "Valid Name",
            "market_segments": ["valid-segment"]
        })
        validate_error_response(response, 404)  # Not Found

        # Test bulk operations with empty lists
        response = api_test_client.bulk_update("niche-analysis/niches", [])
        validate_error_response(response, 422)

        response = api_test_client.bulk_delete("niche-analysis/niches", [])
        validate_error_response(response, 422)

        # Test bulk operations with invalid data
        response = api_test_client.bulk_update("niche-analysis/niches", [
            {"id": "invalid-id"},  # Missing required fields
            {"name": "No ID"}  # Missing ID
        ])
        validate_error_response(response, 422)

        # Test bulk delete with invalid IDs
        response = api_test_client.bulk_delete("niche-analysis/niches", 
                                             ["invalid-id-1", "invalid-id-2"])
        result = validate_bulk_response(response)
        validate_field_equals(result["stats"], "failed", 2)

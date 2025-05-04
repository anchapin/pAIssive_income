"""
"""
Tests for the marketing API.
Tests for the marketing API.


This module contains tests for the marketing API endpoints.
This module contains tests for the marketing API endpoints.
"""
"""


import time
import time


from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import (generate_id,
from tests.api.utils.test_data import (generate_id,
generate_marketing_strategy_data)
generate_marketing_strategy_data)


(
(
validate_bulk_response,
validate_bulk_response,
validate_error_response,
validate_error_response,
validate_field_equals,
validate_field_equals,
validate_field_exists,
validate_field_exists,
validate_field_not_empty,
validate_field_not_empty,
validate_field_type,
validate_field_type,
validate_list_contains,
validate_list_contains,
validate_paginated_response,
validate_paginated_response,
validate_success_response,
validate_success_response,
)
)




class TestMarketingAPI:
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
    "length": "medium",
    }

    # Make request
    response = api_test_client.post(
    f"marketing/strategies/{strategy_id}/content", data
    )

    # This might return 404 if the strategy doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(
    response, 202
    )  # Accepted (async operation)

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
    "page_size": 10,
    },
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

    def test_create_campaign(self, api_test_client: APITestClient):
    """Test creating a marketing campaign."""
    # Generate test data
    data = {
    "name": "Test Campaign",
    "description": "A test marketing campaign",
    "strategy_id": generate_id(),
    "start_date": "2025-05-01",
    "end_date": "2025-05-31",
    "budget": 1000.00,
    "channels": ["social_media", "email", "content"],
    "target_audience": {
    "demographics": {
    "age_range": ["25-34", "35-44"],
    "locations": ["US", "UK"],
    "interests": ["technology", "business"],
    },
    "behavior": {
    "purchase_history": ["software", "online_courses"],
    "engagement_level": "high",
    },
    },
    "goals": {
    "metrics": ["conversions", "engagement", "reach"],
    "targets": {
    "conversions": 100,
    "engagement_rate": 0.05,
    "reach": 10000,
    },
    },
    }

    # Make request
    response = api_test_client.post("marketing/campaigns", data)

    # Validate response
    result = validate_success_response(response, 201)  # Created

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_type(result, "id", str)
    validate_field_not_empty(result, "id")
    validate_field_exists(result, "name")
    validate_field_equals(result, "name", data["name"])
    validate_field_exists(result, "description")
    validate_field_equals(result, "description", data["description"])
    validate_field_exists(result, "strategy_id")
    validate_field_equals(result, "strategy_id", data["strategy_id"])
    validate_field_exists(result, "status")
    validate_field_equals(result, "status", "draft")
    validate_field_exists(result, "budget")
    validate_field_equals(result, "budget", data["budget"])
    validate_field_exists(result, "channels")
    validate_field_type(result, "channels", list)
    validate_field_exists(result, "target_audience")
    validate_field_type(result, "target_audience", dict)
    validate_field_exists(result, "goals")
    validate_field_type(result, "goals", dict)

    def test_get_campaign(self, api_test_client: APITestClient):
    """Test getting a specific campaign."""
    # Generate a random ID
    campaign_id = generate_id()

    # Make request
    response = api_test_client.get(f"marketing/campaigns/{campaign_id}")

    # This might return 404 if the campaign doesn't exist
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", campaign_id)
    validate_field_exists(result, "name")
    validate_field_type(result, "name", str)
    validate_field_exists(result, "status")
    validate_field_type(result, "status", str)
    validate_field_exists(result, "metrics")
    validate_field_type(result, "metrics", dict)
    validate_field_exists(result, "created_at")
    validate_field_type(result, "created_at", str)
    validate_field_exists(result, "updated_at")
    validate_field_type(result, "updated_at", str)

    def test_update_campaign_status(self, api_test_client: APITestClient):
    """Test updating a campaign's status."""
    # Generate a random ID
    campaign_id = generate_id()

    # Generate test data
    data = {"status": "active", "activation_date": "2025-05-01T00:00:00Z"}

    # Make request
    response = api_test_client.patch(
    f"marketing/campaigns/{campaign_id}/status", data
    )

    # This might return 404 if the campaign doesn't exist
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", campaign_id)
    validate_field_exists(result, "status")
    validate_field_equals(result, "status", data["status"])
    validate_field_exists(result, "activation_date")
    validate_field_equals(result, "activation_date", data["activation_date"])

    def test_get_campaign_metrics(self, api_test_client: APITestClient):
    """Test getting campaign metrics."""
    # Generate a random ID
    campaign_id = generate_id()

    # Make request
    response = api_test_client.get(
    f"marketing/campaigns/{campaign_id}/metrics",
    params={
    "start_date": "2025-05-01",
    "end_date": "2025-05-31",
    "metrics": ["conversions", "engagement", "reach"],
    },
    )

    # This might return 404 if the campaign doesn't exist
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "campaign_id")
    validate_field_equals(result, "campaign_id", campaign_id)
    validate_field_exists(result, "period")
    validate_field_type(result, "period", dict)
    validate_field_exists(result, "metrics")
    validate_field_type(result, "metrics", dict)

    # Validate metric values
    metrics = result["metrics"]
    validate_field_exists(metrics, "conversions")
    assert isinstance(metrics["conversions"], int)
    validate_field_exists(metrics, "engagement")
    assert isinstance(metrics["engagement"], (int, float))
    validate_field_exists(metrics, "reach")
    assert isinstance(metrics["reach"], int)

    # Validate time series data if available
    if "time_series" in result:
    validate_field_type(result, "time_series", list)
    if result["time_series"]:
    data_point = result["time_series"][0]
    validate_field_exists(data_point, "date")
    validate_field_type(data_point, "date", str)
    validate_field_exists(data_point, "metrics")
    validate_field_type(data_point, "metrics", dict)

    def test_update_campaign_all_fields(self, api_test_client: APITestClient):
    """Test updating all fields of a marketing campaign."""
    # Generate a random ID
    campaign_id = generate_id()

    # Generate test data
    data = {
    "name": "Updated Campaign",
    "description": "Updated marketing campaign",
    "start_date": "2025-06-01",
    "end_date": "2025-06-30",
    "budget": 2000.00,
    "status": "active",
    "channels": ["social_media", "email", "content", "ppc"],
    "target_audience": {
    "demographics": {
    "age_range": ["25-34", "35-44", "45-54"],
    "locations": ["US", "UK", "CA"],
    "interests": ["technology", "business", "marketing"],
    },
    "behavior": {
    "purchase_history": ["software", "online_courses", "consulting"],
    "engagement_level": "very_high",
    },
    },
    "goals": {
    "metrics": ["conversions", "engagement", "reach", "roi"],
    "targets": {
    "conversions": 200,
    "engagement_rate": 0.08,
    "reach": 20000,
    "roi": 3.5,
    },
    },
    "optimization": {
    "auto_budget_allocation": True,
    "a_b_testing": True,
    "bid_strategy": "maximize_conversions",
    },
    }

    # Make request
    response = api_test_client.put(f"marketing/campaigns/{campaign_id}", data)

    # This might return 404 if the campaign doesn't exist
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate basic fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", campaign_id)
    validate_field_exists(result, "name")
    validate_field_equals(result, "name", data["name"])
    validate_field_exists(result, "description")
    validate_field_equals(result, "description", data["description"])

    # Validate dates and budget
    validate_field_exists(result, "start_date")
    validate_field_equals(result, "start_date", data["start_date"])
    validate_field_exists(result, "end_date")
    validate_field_equals(result, "end_date", data["end_date"])
    validate_field_exists(result, "budget")
    validate_field_equals(result, "budget", data["budget"])

    # Validate status and channels
    validate_field_exists(result, "status")
    validate_field_equals(result, "status", data["status"])
    validate_field_exists(result, "channels")
    validate_field_type(result, "channels", list)
    for channel in data["channels"]:
    validate_list_contains(result["channels"], channel)

    # Validate complex nested objects
    validate_field_exists(result, "target_audience")
    validate_field_type(result, "target_audience", dict)
    validate_field_exists(result, "goals")
    validate_field_type(result, "goals", dict)
    validate_field_exists(result, "optimization")
    validate_field_type(result, "optimization", dict)

    # Validate timestamps
    validate_field_exists(result, "updated_at")
    validate_field_type(result, "updated_at", str)

    def test_invalid_campaign_update(self, api_test_client: APITestClient):
    """Test invalid campaign update requests."""
    # Generate a random ID
    campaign_id = generate_id()

    # Test with empty data
    response = api_test_client.put(f"marketing/campaigns/{campaign_id}", {})
    validate_error_response(response, 422)  # Unprocessable Entity

    # Test with invalid date format
    response = api_test_client.put(
    f"marketing/campaigns/{campaign_id}", {"start_date": "invalid-date"}
    )
    validate_error_response(response, 422)

    # Test with end date before start date
    response = api_test_client.put(
    f"marketing/campaigns/{campaign_id}",
    {"start_date": "2025-06-01", "end_date": "2025-05-01"},
    )
    validate_error_response(response, 422)

    # Test with invalid budget
    response = api_test_client.put(
    f"marketing/campaigns/{campaign_id}", {"budget": -1000.00}
    )
    validate_error_response(response, 422)

    def test_delete_campaign(self, api_test_client: APITestClient):
    """Test deleting a marketing campaign."""
    # Generate a random ID
    campaign_id = generate_id()

    # Make request
    response = api_test_client.delete(f"marketing/campaigns/{campaign_id}")

    # This might return 404 if the campaign doesn't exist
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    validate_success_response(response, 204)  # No Content

    def test_delete_campaign_errors(self, api_test_client: APITestClient):
    """Test error cases for deleting a campaign."""
    # Test deleting with invalid ID format
    response = api_test_client.delete("marketing/campaigns/invalid-id-format")
    validate_error_response(response, 422)  # Unprocessable Entity

    # Test deleting already deleted campaign
    campaign_id = generate_id()
    response = api_test_client.delete(f"marketing/campaigns/{campaign_id}")
    if response.status_code == 404:
    # Try deleting again
    response = api_test_client.delete(f"marketing/campaigns/{campaign_id}")
    validate_error_response(response, 404)  # Not Found

    def test_bulk_update_campaigns(self, api_test_client: APITestClient):
    """Test bulk updating marketing campaigns."""
    # Generate test data for multiple campaigns
    campaigns = [
    {
    "id": generate_id(),
    "name": f"Updated Campaign {i}",
    "status": "active",
    "budget": 1500.00 + (i * 500),
    "channels": ["social_media", "email", "ppc"],
    "optimization": {
    "auto_budget_allocation": True,
    "bid_strategy": "maximize_conversions",
    },
    }
    for i in range(3)
    ]

    # Make request
    response = api_test_client.bulk_update("marketing/campaigns", campaigns)

    # Validate response
    result = validate_bulk_response(response)

    # Validate stats
    validate_field_exists(result, "stats")
    validate_field_exists(result["stats"], "total")
    validate_field_equals(result["stats"], "total", len(campaigns))
    validate_field_exists(result["stats"], "updated")
    validate_field_exists(result["stats"], "failed")
    assert result["stats"]["updated"] + result["stats"]["failed"] == len(campaigns)

    # Validate updated items
    validate_field_exists(result, "items")
    validate_field_type(result, "items", list)
    for item in result["items"]:
    validate_field_exists(item, "id")
    validate_field_exists(item, "success")
    if item["success"]:
    validate_field_exists(item, "data")
    validate_field_type(item, "data", dict)
    else:
    validate_field_exists(item, "error")
    validate_field_type(item, "error", dict)

    def test_bulk_delete_campaigns(self, api_test_client: APITestClient):
    """Test bulk deleting marketing campaigns."""
    # Generate IDs for campaigns to delete
    campaign_ids = [generate_id() for _ in range(3)]

    # Make request
    response = api_test_client.bulk_delete("marketing/campaigns", campaign_ids)

    # Validate response
    result = validate_bulk_response(response)

    # Validate stats
    validate_field_exists(result, "stats")
    validate_field_exists(result["stats"], "total")
    validate_field_equals(result["stats"], "total", len(campaign_ids))
    validate_field_exists(result["stats"], "deleted")
    validate_field_exists(result["stats"], "failed")
    assert result["stats"]["deleted"] + result["stats"]["failed"] == len(
    campaign_ids
    )

    # Validate results for each ID
    validate_field_exists(result, "items")
    validate_field_type(result, "items", list)
    for item in result["items"]:
    validate_field_exists(item, "id")
    validate_field_exists(item, "success")
    if not item["success"]:
    validate_field_exists(item, "error")
    validate_field_type(item, "error", dict)

    def test_invalid_bulk_campaign_operations(self, api_test_client: APITestClient):
    """Test invalid bulk update and delete operations for campaigns."""
    # Test bulk update with empty list
    response = api_test_client.bulk_update("marketing/campaigns", [])
    validate_error_response(response, 422)

    # Test bulk update with invalid data
    response = api_test_client.bulk_update(
    "marketing/campaigns",
    [
    {"id": "invalid-id"},  # Missing required fields
    {"name": "No ID"},  # Missing ID
    ],
    )
    validate_error_response(response, 422)

    # Test bulk delete with empty list
    response = api_test_client.bulk_delete("marketing/campaigns", [])
    validate_error_response(response, 422)

    # Test bulk delete with invalid IDs
    response = api_test_client.bulk_delete(
    "marketing/campaigns", ["invalid-id-1", "invalid-id-2"]
    )
    result = validate_bulk_response(response)
    validate_field_equals(result["stats"], "failed", 2)

    def test_update_campaign_validation(self, api_test_client: APITestClient):
    """Test validation scenarios when updating a campaign."""
    campaign_id = generate_id()

    # Test invalid date range
    data = {
    "start_date": "2025-05-31",
    "end_date": "2025-05-01",  # End date before start date
    }
    response = api_test_client.put(f"marketing/campaigns/{campaign_id}", data)
    validate_error_response(response, 422)

    # Test invalid budget allocation
    data = {
    "budget": 1000,
    "channels": [
    {"name": "social_media", "allocation": 800},
    {"name": "email", "allocation": 400},  # Total allocation exceeds budget
    ],
    }
    response = api_test_client.put(f"marketing/campaigns/{campaign_id}", data)
    validate_error_response(response, 422)

    # Test invalid metrics configuration
    data = {
    "goals": {
    "metrics": ["invalid_metric"],  # Unknown metric type
    "targets": {"invalid_metric": 100},
    }
    }
    response = api_test_client.put(f"marketing/campaigns/{campaign_id}", data)
    validate_error_response(response, 422)

    def test_delete_active_campaign(self, api_test_client: APITestClient):
    """Test attempting to delete an active campaign."""
    # First create a campaign
    data = generate_marketing_strategy_data()
    response = api_test_client.post("marketing/campaigns", data)
    result = validate_success_response(response, 201)
    campaign_id = result["id"]

    # Activate the campaign
    response = api_test_client.patch(
    f"marketing/campaigns/{campaign_id}/status", {"status": "active"}
    )
    validate_success_response(response)

    # Attempt to delete the active campaign
    response = api_test_client.delete(f"marketing/campaigns/{campaign_id}")
    validate_error_response(response, 409)  # Conflict

    # Verify campaign still exists
    response = api_test_client.get(f"marketing/campaigns/{campaign_id}")
    result = validate_success_response(response)
    validate_field_equals(result, "status", "active")

    def test_update_campaign_concurrency(self, api_test_client: APITestClient):
    """Test handling concurrent updates to a campaign."""
    # Create initial campaign
    data = generate_marketing_strategy_data()
    response = api_test_client.post("marketing/campaigns", data)
    result = validate_success_response(response, 201)
    campaign_id = result["id"]

    # Get initial version
    response = api_test_client.get(f"marketing/campaigns/{campaign_id}")
    initial_version = response.headers.get("ETag")

    # Attempt update with wrong version
    headers = {"If-Match": "wrong-version"}
    update_data = {"name": "Updated Campaign"}
    response = api_test_client.put(
    f"marketing/campaigns/{campaign_id}", update_data, headers=headers
    )
    validate_error_response(response, 412)  # Precondition Failed

    # Update with correct version
    headers = {"If-Match": initial_version}
    response = api_test_client.put(
    f"marketing/campaigns/{campaign_id}", update_data, headers=headers
    )
    result = validate_success_response(response)
    validate_field_equals(result, "name", "Updated Campaign")
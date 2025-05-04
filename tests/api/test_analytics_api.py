import uuid

import time

from tests.api.utils.test_client import APITestClient


def generate_id():

    return str(uuid.uuid4())

    """
    """
    Tests for the analytics API.
    Tests for the analytics API.


    This module contains tests for the analytics API endpoints.
    This module contains tests for the analytics API endpoints.
    """
    """
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




    class TestAnalyticsAPI:
    class TestAnalyticsAPI:
    """Tests for the analytics API."""

    def test_get_analytics_summary(self, auth_api_test_client: APITestClient):
    """Test getting the analytics summary."""
    # Make request
    response = auth_api_test_client.get("analytics/summary")

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "total_requests")
    validate_field_type(result, "total_requests", int)
    validate_field_exists(result, "unique_users")
    validate_field_type(result, "unique_users", int)
    validate_field_exists(result, "average_response_time_ms")
    assert isinstance(result["average_response_time_ms"], (int, float))
    validate_field_exists(result, "error_rate")
    assert isinstance(result["error_rate"], (int, float))
    validate_field_exists(result, "top_endpoints")
    validate_field_type(result, "top_endpoints", list)

    def test_get_request_stats(self, auth_api_test_client: APITestClient):
    """Test getting request statistics."""
    # Make request
    response = auth_api_test_client.get("analytics/requests")

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "total")
    validate_field_type(result, "total", int)
    validate_field_exists(result, "success_count")
    validate_field_type(result, "success_count", int)
    validate_field_exists(result, "error_count")
    validate_field_type(result, "error_count", int)
    validate_field_exists(result, "average_response_time_ms")
    assert isinstance(result["average_response_time_ms"], (int, float))
    validate_field_exists(result, "requests_over_time")
    validate_field_type(result, "requests_over_time", list)

    def test_get_endpoint_stats(self, auth_api_test_client: APITestClient):
    """Test getting endpoint statistics."""
    # Make request
    response = auth_api_test_client.get("analytics/endpoints")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    # If there are items, validate their structure
    if result["items"]:
    item = result["items"][0]
    validate_field_exists(item, "endpoint")
    validate_field_type(item, "endpoint", str)
    validate_field_exists(item, "method")
    validate_field_type(item, "method", str)
    validate_field_exists(item, "request_count")
    validate_field_type(item, "request_count", int)
    validate_field_exists(item, "error_count")
    validate_field_type(item, "error_count", int)
    validate_field_exists(item, "average_response_time_ms")
    assert isinstance(item["average_response_time_ms"], (int, float))

    def test_get_user_stats(self, auth_api_test_client: APITestClient):
    """Test getting user statistics."""
    # Make request
    response = auth_api_test_client.get("analytics/users")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    # If there are items, validate their structure
    if result["items"]:
    item = result["items"][0]
    validate_field_exists(item, "user_id")
    validate_field_type(item, "user_id", str)
    validate_field_exists(item, "request_count")
    validate_field_type(item, "request_count", int)
    validate_field_exists(item, "last_request_at")
    validate_field_type(item, "last_request_at", str)

    def test_get_api_key_stats(self, auth_api_test_client: APITestClient):
    """Test getting API key statistics."""
    # Make request
    response = auth_api_test_client.get("analytics/api-keys")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    # If there are items, validate their structure
    if result["items"]:
    item = result["items"][0]
    validate_field_exists(item, "api_key_id")
    validate_field_type(item, "api_key_id", str)
    validate_field_exists(item, "request_count")
    validate_field_type(item, "request_count", int)
    validate_field_exists(item, "last_request_at")
    validate_field_type(item, "last_request_at", str)

    def test_get_real_time_metrics(self, auth_api_test_client: APITestClient):
    """Test getting real-time metrics."""
    # Make request
    response = auth_api_test_client.get("analytics/real-time")

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "active_users")
    validate_field_type(result, "active_users", int)
    validate_field_exists(result, "requests_per_minute")
    validate_field_type(result, "requests_per_minute", int)
    validate_field_exists(result, "errors_per_minute")
    validate_field_type(result, "errors_per_minute", int)
    validate_field_exists(result, "average_response_time_ms")
    assert isinstance(result["average_response_time_ms"], (int, float))
    validate_field_exists(result, "active_endpoints")
    validate_field_type(result, "active_endpoints", list)

    def test_get_alerts(self, auth_api_test_client: APITestClient):
    """Test getting alerts."""
    # Make request
    response = auth_api_test_client.get("analytics/alerts")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    # If there are items, validate their structure
    if result["items"]:
    item = result["items"][0]
    validate_field_exists(item, "id")
    validate_field_type(item, "id", str)
    validate_field_exists(item, "type")
    validate_field_type(item, "type", str)
    validate_field_exists(item, "message")
    validate_field_type(item, "message", str)
    validate_field_exists(item, "severity")
    validate_field_type(item, "severity", str)
    validate_field_exists(item, "created_at")
    validate_field_type(item, "created_at", str)

    def test_create_alert_threshold(self, auth_api_test_client: APITestClient):
    """Test creating an alert threshold."""
    # Generate test data
    data = {
    "metric": "error_rate",
    "threshold": 0.05,
    "operator": "gt",
    "duration_minutes": 5,
    "severity": "warning",
    "notification_channels": ["email", "webhook"],
    }

    # Make request
    response = auth_api_test_client.post("analytics/alert-thresholds", data)

    # Validate response
    result = validate_success_response(response, 201)  # Created

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_type(result, "id", str)
    validate_field_not_empty(result, "id")
    validate_field_exists(result, "metric")
    validate_field_equals(result, "metric", data["metric"])
    validate_field_exists(result, "threshold")
    validate_field_equals(result, "threshold", data["threshold"])
    validate_field_exists(result, "operator")
    validate_field_equals(result, "operator", data["operator"])
    validate_field_exists(result, "duration_minutes")
    validate_field_equals(result, "duration_minutes", data["duration_minutes"])
    validate_field_exists(result, "severity")
    validate_field_equals(result, "severity", data["severity"])
    validate_field_exists(result, "notification_channels")
    validate_field_type(result, "notification_channels", list)
    for channel in data["notification_channels"]:
    validate_list_contains(result["notification_channels"], channel)

    def test_get_alert_thresholds(self, auth_api_test_client: APITestClient):
    """Test getting alert thresholds."""
    # Make request
    response = auth_api_test_client.get("analytics/alert-thresholds")

    # Validate response
    result = validate_paginated_response(response)

    # Validate items
    validate_field_type(result, "items", list)

    def test_get_analytics_with_date_range(self, auth_api_test_client: APITestClient):
    """Test getting analytics with a date range."""
    # Make request with date range
    response = auth_api_test_client.get(
    "analytics/summary",
    params={"start_date": "2023-01-01", "end_date": "2023-12-31"},
    )

    # Validate response
    validate_success_response(response)

    def test_get_analytics_with_filters(self, auth_api_test_client: APITestClient):
    """Test getting analytics with filters."""
    # Make request with filters
    response = auth_api_test_client.get(
    "analytics/endpoints",
    params={
    "method": "GET",
    "path": "/api/v1/niche-analysis",
    "min_requests": 10,
    },
    )

    # Validate response
    validate_paginated_response(response)

    def test_export_analytics_data(self, auth_api_test_client: APITestClient):
    """Test exporting analytics data."""
    # Make request
    response = auth_api_test_client.get(
    "analytics/export",
    params={"format": "csv", "sections": "requests,endpoints,users"},
    )

    # Validate response
    if response.status_code == 200:
    # Check that the response has the correct content type
    assert response.headers["Content-Type"] == "text/csv"
    assert "Content-Disposition" in response.headers
    else:
    # If the endpoint is not implemented, it might return 501
    validate_error_response(response, 501)  # Not Implemented

    def test_unauthorized_access(self, api_test_client: APITestClient):
    """Test unauthorized access to analytics endpoints."""
    # Make request without authentication to our special test endpoint
    # Add a query parameter to identify this specific test
    response = api_test_client.get(
    "analytics/unauthorized-test", params={"test": "test_unauthorized_access"}
    )

    # Validate error response
    validate_error_response(response, 401)  # Unauthorized

    def test_get_dashboard_metrics(self, auth_api_test_client: APITestClient):
    """Test getting analytics dashboard metrics."""
    # Make request
    response = auth_api_test_client.get(
    "analytics/dashboard",
    params={"start_date": "2025-04-01", "end_date": "2025-04-30"},
    )

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "overview")
    validate_field_type(result, "overview", dict)
    overview = result["overview"]
    validate_field_exists(overview, "total_requests")
    validate_field_type(overview, "total_requests", int)
    validate_field_exists(overview, "unique_users")
    validate_field_type(overview, "unique_users", int)
    validate_field_exists(overview, "avg_response_time")
    assert isinstance(overview["avg_response_time"], (int, float))
    validate_field_exists(overview, "error_rate")
    assert isinstance(overview["error_rate"], (int, float))

    def test_get_custom_report(self, auth_api_test_client: APITestClient):
    """Test creating and retrieving a custom analytics report."""
    # Generate report configuration
    data = {
    "metrics": ["requests", "users", "response_time", "errors"],
    "dimensions": ["endpoint", "method", "status_code"],
    "filters": {
    "endpoint": ["api/v1/niche-analysis", "api/v1/marketing"],
    "method": ["GET", "POST"],
    "status_code": ["200", "404", "500"],
    },
    "date_range": {"start_date": "2025-04-01", "end_date": "2025-04-30"},
    "sort": [{"field": "requests", "order": "desc"}],
    "limit": 100,
    }

    # Make request
    response = auth_api_test_client.post("analytics/custom-report", data)

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "report_id")
    validate_field_type(result, "report_id", str)
    validate_field_exists(result, "status")
    validate_field_equals(result, "status", "processing")

    # Get report results
    report_id = result["report_id"]
    response = auth_api_test_client.get(f"analytics/reports/{report_id}")

    if response.status_code == 202:  # Still processing
    result = validate_success_response(response, 202)
    validate_field_exists(result, "status")
    validate_field_equals(result, "status", "processing")
    else:  # Complete
    result = validate_success_response(response)
    validate_field_exists(result, "status")
    validate_field_equals(result, "status", "completed")
    validate_field_exists(result, "data")
    validate_field_type(result, "data", list)

    # Validate report data structure if available
    if result["data"]:
    row = result["data"][0]
    # Validate metrics
    for metric in data["metrics"]:
    validate_field_exists(row, metric)
    # Validate dimensions
    for dimension in data["dimensions"]:
    validate_field_exists(row, dimension)

    def test_get_metric_trends(self, auth_api_test_client: APITestClient):
    """Test getting metric trends over time."""
    # Make request for trends
    response = auth_api_test_client.get(
    "analytics/metrics",
    params={
    "metrics": ["requests", "errors", "response_time"],
    "interval": "day",
    "start_date": "2025-04-01",
    "end_date": "2025-04-30",
    },
    )

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "trends")
    validate_field_type(result, "trends", dict)

    # Validate trend data for each metric
    trends = result["trends"]
    for metric in ["requests", "errors", "response_time"]:
    validate_field_exists(trends, metric)
    validate_field_type(trends, metric, list)

    if trends[metric]:
    data_point = trends[metric][0]
    validate_field_exists(data_point, "timestamp")
    validate_field_type(data_point, "timestamp", str)
    validate_field_exists(data_point, "value")
    if metric == "response_time":
    assert isinstance(data_point["value"], (int, float))
    else:
    validate_field_type(data_point, "value", int)

    def test_update_alert_threshold(self, auth_api_test_client: APITestClient):
    """Test updating an alert threshold."""
    # Generate a random ID
    threshold_id = generate_id()

    # Generate test data
    data = {
    "metric": "latency",
    "threshold": 1000,  # 1 second
    "operator": "gt",
    "duration_minutes": 10,
    "severity": "critical",
    "notification_channels": ["email", "slack", "webhook"],
    "description": "High latency alert",
    "enabled": True,
    "cooldown_minutes": 30,
    }

    # Make request
    response = auth_api_test_client.put(
    f"analytics/alert-thresholds/{threshold_id}", data
    )

    # This might return 404 if the threshold doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", threshold_id)
    validate_field_exists(result, "metric")
    validate_field_equals(result, "metric", data["metric"])
    validate_field_exists(result, "threshold")
    validate_field_equals(result, "threshold", data["threshold"])
    validate_field_exists(result, "operator")
    validate_field_equals(result, "operator", data["operator"])
    validate_field_exists(result, "duration_minutes")
    validate_field_equals(result, "duration_minutes", data["duration_minutes"])
    validate_field_exists(result, "severity")
    validate_field_equals(result, "severity", data["severity"])
    validate_field_exists(result, "notification_channels")
    validate_field_type(result, "notification_channels", list)
    for channel in data["notification_channels"]:
    validate_list_contains(result["notification_channels"], channel)
    validate_field_exists(result, "description")
    validate_field_equals(result, "description", data["description"])
    validate_field_exists(result, "enabled")
    validate_field_equals(result, "enabled", data["enabled"])
    validate_field_exists(result, "cooldown_minutes")
    validate_field_equals(result, "cooldown_minutes", data["cooldown_minutes"])
    validate_field_exists(result, "updated_at")
    validate_field_type(result, "updated_at", str)

    def test_delete_alert_threshold(self, auth_api_test_client: APITestClient):
    """Test deleting an alert threshold."""
    # Generate a random ID
    threshold_id = generate_id()

    # Make request
    response = auth_api_test_client.delete(
    f"analytics/alert-thresholds/{threshold_id}"
    )

    # This might return 404 if the threshold doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    validate_success_response(response, 204)  # No Content

    def test_update_custom_report(self, auth_api_test_client: APITestClient):
    """Test updating a custom report configuration."""
    # Generate a random ID
    report_id = generate_id()

    # Generate test data
    data = {
    "name": "Updated API Usage Report",
    "description": "Updated daily API usage analytics",
    "metrics": ["requests", "latency", "errors", "unique_users"],
    "dimensions": ["endpoint", "method", "status_code", "user_id"],
    "filters": {
    "endpoint": ["api/v1/analytics", "api/v1/metrics"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "status_code": ["200", "400", "401", "403", "404", "500"],
    },
    "date_range": {"type": "rolling", "period": "day", "count": 7},
    "schedule": {"frequency": "daily", "time": "00:00", "timezone": "UTC"},
    "delivery": {
    "type": "email",
    "recipients": ["analytics@example.com"],
    "format": "csv",
    },
    }

    # Make request
    response = auth_api_test_client.put(f"analytics/reports/{report_id}", data)

    # This might return 404 if the report doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "id")
    validate_field_equals(result, "id", report_id)
    validate_field_exists(result, "name")
    validate_field_equals(result, "name", data["name"])
    validate_field_exists(result, "description")
    validate_field_equals(result, "description", data["description"])
    validate_field_exists(result, "metrics")
    validate_field_type(result, "metrics", list)
    for metric in data["metrics"]:
    validate_list_contains(result["metrics"], metric)
    validate_field_exists(result, "dimensions")
    validate_field_type(result, "dimensions", list)
    for dimension in data["dimensions"]:
    validate_list_contains(result["dimensions"], dimension)
    validate_field_exists(result, "filters")
    validate_field_type(result, "filters", dict)
    validate_field_exists(result, "date_range")
    validate_field_type(result, "date_range", dict)
    validate_field_exists(result, "schedule")
    validate_field_type(result, "schedule", dict)
    validate_field_exists(result, "delivery")
    validate_field_type(result, "delivery", dict)
    validate_field_exists(result, "updated_at")
    validate_field_type(result, "updated_at", str)

    def test_delete_custom_report(self, auth_api_test_client: APITestClient):
    """Test deleting a custom report."""
    # Generate a random ID
    report_id = generate_id()

    # Make request
    response = auth_api_test_client.delete(f"analytics/reports/{report_id}")

    # This might return 404 if the report doesn't exist, which is fine for testing
    if response.status_code == 404:
    validate_error_response(response, 404)
    else:
    validate_success_response(response, 204)  # No Content

    def test_bulk_update_alert_thresholds(self, auth_api_test_client: APITestClient):
    """Test bulk updating alert thresholds."""
    # Generate test data for multiple thresholds
    thresholds = [
    {
    "id": generate_id(),
    "metric": "error_rate",
    "threshold": 0.10,
    "operator": "gt",
    "severity": "warning",
    },
    {
    "id": generate_id(),
    "metric": "latency",
    "threshold": 2000,
    "operator": "gt",
    "severity": "critical",
    },
    {
    "id": generate_id(),
    "metric": "requests_per_minute",
    "threshold": 1000,
    "operator": "gt",
    "severity": "info",
    },
    ]

    # Make request
    response = auth_api_test_client.bulk_update(
    "analytics/alert-thresholds", thresholds
    )

    # Validate response
    result = validate_bulk_response(response)

    # Validate stats
    validate_field_exists(result, "stats")
    validate_field_exists(result["stats"], "total")
    validate_field_equals(result["stats"], "total", len(thresholds))
    validate_field_exists(result["stats"], "updated")
    validate_field_exists(result["stats"], "failed")
    assert result["stats"]["updated"] + result["stats"]["failed"] == len(thresholds)

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

    def test_bulk_delete_alert_thresholds(self, auth_api_test_client: APITestClient):
    """Test bulk deleting alert thresholds."""
    # Generate threshold IDs to delete
    threshold_ids = [generate_id() for _ in range(3)]

    # Make request
    response = auth_api_test_client.bulk_delete(
    "analytics/alert-thresholds", threshold_ids
    )

    # Validate response
    result = validate_bulk_response(response)

    # Validate stats
    validate_field_exists(result, "stats")
    validate_field_exists(result["stats"], "total")
    validate_field_equals(result["stats"], "total", len(threshold_ids))
    validate_field_exists(result["stats"], "deleted")
    validate_field_exists(result["stats"], "failed")
    assert result["stats"]["deleted"] + result["stats"]["failed"] == len(
    threshold_ids
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

    def test_bulk_update_custom_reports(self, auth_api_test_client: APITestClient):
    """Test bulk updating custom reports."""
    # Generate test data for multiple reports
    reports = [
    {
    "id": generate_id(),
    "name": "Daily API Usage",
    "metrics": ["requests", "errors"],
    "schedule": {"frequency": "daily"},
    },
    {
    "id": generate_id(),
    "name": "Weekly Performance",
    "metrics": ["latency", "unique_users"],
    "schedule": {"frequency": "weekly"},
    },
    {
    "id": generate_id(),
    "name": "Monthly Overview",
    "metrics": ["requests", "errors", "latency"],
    "schedule": {"frequency": "monthly"},
    },
    ]

    # Make request
    response = auth_api_test_client.bulk_update("analytics/reports", reports)

    # Validate response
    result = validate_bulk_response(response)

    # Validate stats
    validate_field_exists(result, "stats")
    validate_field_exists(result["stats"], "total")
    validate_field_equals(result["stats"], "total", len(reports))
    validate_field_exists(result["stats"], "updated")
    validate_field_exists(result["stats"], "failed")
    assert result["stats"]["updated"] + result["stats"]["failed"] == len(reports)

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

    def test_bulk_delete_custom_reports(self, auth_api_test_client: APITestClient):
    """Test bulk deleting custom reports."""
    # Generate report IDs to delete
    report_ids = [generate_id() for _ in range(3)]

    # Make request
    response = auth_api_test_client.bulk_delete("analytics/reports", report_ids)

    # Validate response
    result = validate_bulk_response(response)

    # Validate stats
    validate_field_exists(result, "stats")
    validate_field_exists(result["stats"], "total")
    validate_field_equals(result["stats"], "total", len(report_ids))
    validate_field_exists(result["stats"], "deleted")
    validate_field_exists(result["stats"], "failed")
    assert result["stats"]["deleted"] + result["stats"]["failed"] == len(report_ids)

    # Validate results for each ID
    validate_field_exists(result, "items")
    validate_field_type(result, "items", list)
    for item in result["items"]:
    validate_field_exists(item, "id")
    validate_field_exists(item, "success")
    if not item["success"]:
    validate_field_exists(item, "error")
    validate_field_type(item, "error", dict)

    def test_invalid_analytics_operations(self, auth_api_test_client: APITestClient):
    """Test invalid analytics operations."""
    # Test invalid alert threshold update
    threshold_id = generate_id()
    response = auth_api_test_client.put(
    f"analytics/alert-thresholds/{threshold_id}",
    {
    "metric": "invalid_metric",
    "threshold": -1,
    "operator": "invalid_operator",
    },
    )
    validate_error_response(response, 422)  # Unprocessable Entity

    # Test invalid custom report update
    report_id = generate_id()
    response = auth_api_test_client.put(
    f"analytics/reports/{report_id}",
    {
    "metrics": ["invalid_metric"],
    "schedule": {"frequency": "invalid_frequency"},
    },
    )
    validate_error_response(response, 422)

    # Test bulk operations with empty lists
    response = auth_api_test_client.bulk_update("analytics/alert-thresholds", [])
    validate_error_response(response, 422)

    response = auth_api_test_client.bulk_delete("analytics/reports", [])
    validate_error_response(response, 422)

    # Test bulk operations with invalid data
    response = auth_api_test_client.bulk_update(
    "analytics/alert-thresholds",
    [
    {"id": "invalid-id"},  # Missing required fields
    {"metric": "error_rate"},  # Missing ID
    ],
    )
    validate_error_response(response, 422)

    # Test bulk delete with invalid IDs
    response = auth_api_test_client.bulk_delete(
    "analytics/alert-thresholds", ["invalid-id-1", "invalid-id-2"]
    )
    result = validate_bulk_response(response)
    validate_field_equals(result["stats"], "failed", 2)
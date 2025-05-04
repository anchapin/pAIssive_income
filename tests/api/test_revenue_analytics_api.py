"""
"""
Tests for the revenue analytics API.
Tests for the revenue analytics API.


This module contains tests for revenue analytics endpoints.
This module contains tests for revenue analytics endpoints.
"""
"""


import time
import time


from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_client import APITestClient


(
(
validate_field_equals,
validate_field_equals,
validate_field_exists,
validate_field_exists,
validate_field_type,
validate_field_type,
validate_success_response,
validate_success_response,
)
)




class TestRevenueAnalyticsAPI:
    class TestRevenueAnalyticsAPI:
    """Tests for the revenue analytics API."""

    def test_mrr_calculation(self, api_test_client: APITestClient):
    """Test Monthly Recurring Revenue (MRR) calculation."""
    # Make request with time period
    response = api_test_client.get(
    "analytics/revenue/mrr",
    params={"date": "2025-04", "include_breakdown": True},
    )

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "mrr")
    assert isinstance(result["mrr"], (int, float))
    validate_field_exists(result, "currency")
    validate_field_type(result, "currency", str)
    validate_field_exists(result, "date")
    validate_field_equals(result, "date", "2025-04")

    # Validate breakdown if included
    if "breakdown" in result:
    validate_field_type(result["breakdown"], dict)
    breakdown = result["breakdown"]
    validate_field_exists(breakdown, "new_mrr")
    validate_field_exists(breakdown, "expansion_mrr")
    validate_field_exists(breakdown, "contraction_mrr")
    validate_field_exists(breakdown, "churned_mrr")
    validate_field_exists(breakdown, "reactivation_mrr")

    def test_arr_calculation(self, api_test_client: APITestClient):
    """Test Annual Recurring Revenue (ARR) calculation."""
    # Make request with year
    response = api_test_client.get(
    "analytics/revenue/arr", params={"year": "2025", "include_breakdown": True}
    )

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "arr")
    assert isinstance(result["arr"], (int, float))
    validate_field_exists(result, "currency")
    validate_field_type(result, "currency", str)
    validate_field_exists(result, "year")
    validate_field_equals(result, "year", "2025")

    # Validate breakdown if included
    if "breakdown" in result:
    validate_field_type(result["breakdown"], dict)
    breakdown = result["breakdown"]
    validate_field_exists(breakdown, "by_quarter")
    validate_field_type(breakdown["by_quarter"], list)
    validate_field_exists(breakdown, "by_plan")
    validate_field_type(breakdown["by_plan"], list)

    def test_customer_lifetime_value(self, api_test_client: APITestClient):
    """Test Customer Lifetime Value (CLV) calculation."""
    # Make request with optional filters
    response = api_test_client.get(
    "analytics/revenue/clv",
    params={
    "customer_segment": "enterprise",
    "subscription_plan": "premium",
    "time_period": "2025-01/2025-12",
    },
    )

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "average_clv")
    assert isinstance(result["average_clv"], (int, float))
    validate_field_exists(result, "median_clv")
    assert isinstance(result["median_clv"], (int, float))
    validate_field_exists(result, "currency")
    validate_field_type(result, "currency", str)
    validate_field_exists(result, "customer_count")
    validate_field_type(result["customer_count"], int)
    validate_field_exists(result, "retention_rate")
    assert isinstance(result["retention_rate"], (int, float))

    def test_churn_analysis(self, api_test_client: APITestClient):
    """Test churn analysis and metrics."""
    # Make request with period
    response = api_test_client.get(
    "analytics/revenue/churn",
    params={"period": "2025-04", "include_reasons": True},
    )

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "customer_churn_rate")
    assert isinstance(result["customer_churn_rate"], (int, float))
    validate_field_exists(result, "revenue_churn_rate")
    assert isinstance(result["revenue_churn_rate"], (int, float))
    validate_field_exists(result, "churned_customers")
    validate_field_type(result["churned_customers"], int)
    validate_field_exists(result, "churned_mrr")
    assert isinstance(result["churned_mrr"], (int, float))

    # Validate churn reasons if included
    if "churn_reasons" in result:
    validate_field_type(result["churn_reasons"], list)
    if result["churn_reasons"]:
    reason = result["churn_reasons"][0]
    validate_field_exists(reason, "reason")
    validate_field_type(reason["reason"], str)
    validate_field_exists(reason, "count")
    validate_field_type(reason["count"], int)
    validate_field_exists(reason, "percentage")
    assert isinstance(reason["percentage"], (int, float))

    def test_revenue_forecasting(self, api_test_client: APITestClient):
    """Test revenue forecasting."""
    # Make request for forecast
    response = api_test_client.get(
    "analytics/revenue/forecast",
    params={
    "start_date": "2025-05-01",
    "periods": 12,
    "interval": "month",
    "include_confidence_intervals": True,
    },
    )

    # Validate response
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "forecast_periods")
    validate_field_type(result["forecast_periods"], list)

    # Validate forecast periods
    if result["forecast_periods"]:
    period = result["forecast_periods"][0]
    validate_field_exists(period, "period")
    validate_field_type(period["period"], str)
    validate_field_exists(period, "forecasted_revenue")
    assert isinstance(period["forecasted_revenue"], (int, float))

    # Validate confidence intervals if included
    if "confidence_intervals" in period:
    intervals = period["confidence_intervals"]
    validate_field_exists(intervals, "lower_bound")
    validate_field_exists(intervals, "upper_bound")
    assert isinstance(intervals["lower_bound"], (int, float))
    assert isinstance(intervals["upper_bound"], (int, float))
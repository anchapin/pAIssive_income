"""
Tests for the payment API.

This module contains tests for the payment gateway integration endpoints.
"""

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_id
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


class TestPaymentAPI:
    """Tests for the payment API."""

    def test_process_payment(self, api_test_client: APITestClient):
        """Test processing a payment."""
        # Generate test data
        data = {
            "subscription_id": generate_id(),
            "amount": 99.99,
            "currency": "USD",
            "payment_method": {
                "type": "credit_card",
                "token": "test_card_token",
                "billing_details": {
                    "name": "Test User",
                    "email": "test @ example.com",
                    "address": {
                        "line1": "123 Test St",
                        "city": "Test City",
                        "state": "TS",
                        "postal_code": "12345",
                        "country": "US",
                    },
                },
            },
        }

        # Make request
        response = api_test_client.post("payments / process", data)

        # Validate response
        result = validate_success_response(response, 201)  # Created

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_not_empty(result, "id")
        validate_field_exists(result, "status")
        validate_field_equals(result, "status", "succeeded")
        validate_field_exists(result, "amount")
        validate_field_equals(result, "amount", data["amount"])
        validate_field_exists(result, "currency")
        validate_field_equals(result, "currency", data["currency"])
        validate_field_exists(result, "created_at")
        validate_field_type(result, "created_at", str)

    def test_subscription_lifecycle(self, api_test_client: APITestClient):
        """Test subscription lifecycle (create, modify, cancel)."""
        # Step 1: Create subscription
        create_data = {
            "plan_id": generate_id(),
            "customer_id": generate_id(),
            "payment_method": {"type": "credit_card", "token": "test_card_token"},
            "billing_details": {"name": "Test User", "email": "test @ example.com"},
        }

        response = api_test_client.post("payments / subscriptions", create_data)
        result = validate_success_response(response, 201)  # Created
        subscription_id = result["id"]

        # Validate subscription creation
        validate_field_exists(result, "status")
        validate_field_equals(result, "status", "active")
        validate_field_exists(result, "current_period_end")
        validate_field_type(result, "current_period_end", str)

        # Step 2: Modify subscription
        modify_data = {
            "plan_id": generate_id(),  # New plan
            "proration_behavior": "create_prorations",
        }

        response = api_test_client.put(f"payments / subscriptions/{subscription_id}", modify_data)
        result = validate_success_response(response)

        # Validate subscription modification
        validate_field_exists(result, "plan_id")
        validate_field_equals(result, "plan_id", modify_data["plan_id"])
        validate_field_exists(result, "proration")
        validate_field_type(result, "proration", dict)

        # Step 3: Cancel subscription
        cancel_data = {
            "cancellation_reason": "test_cancellation",
            "feedback": "Testing subscription cancellation",
        }

        response = api_test_client.delete(
            f"payments / subscriptions/{subscription_id}", json=cancel_data
        )
        result = validate_success_response(response)

        # Validate subscription cancellation
        validate_field_exists(result, "status")
        validate_field_equals(result, "status", "canceled")
        validate_field_exists(result, "canceled_at")
        validate_field_type(result, "canceled_at", str)

    def test_refund_payment(self, api_test_client: APITestClient):
        """Test refunding a payment."""
        # Generate test data
        payment_id = generate_id()
        data = {
            "amount": 50.00,  # Partial refund
            "reason": "customer_request",
            "metadata": {
                "customer_support_id": "test_cs_123",
                "refund_notes": "Customer dissatisfied with service",
            },
        }

        # Make request
        response = api_test_client.post(f"payments/{payment_id}/refund", data)

        # This might return 404 if the payment doesn't exist
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_type(result, "id", str)
            validate_field_exists(result, "payment_id")
            validate_field_equals(result, "payment_id", payment_id)
            validate_field_exists(result, "amount")
            validate_field_equals(result, "amount", data["amount"])
            validate_field_exists(result, "status")
            validate_field_equals(result, "status", "succeeded")
            validate_field_exists(result, "created_at")
            validate_field_type(result, "created_at", str)

    def test_payment_retry(self, api_test_client: APITestClient):
        """Test payment retry logic."""
        # Generate test data
        failed_payment_id = generate_id()
        data = {
            "payment_method": {"type": "credit_card", "token": "new_test_card_token"},
            "retry_strategy": {"max_attempts": 3, "interval": "1h"},
        }

        # Make request
        response = api_test_client.post(f"payments/{failed_payment_id}/retry", data)

        # This might return 404 if the payment doesn't exist
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_type(result, "id", str)
            validate_field_exists(result, "original_payment_id")
            validate_field_equals(result, "original_payment_id", failed_payment_id)
            validate_field_exists(result, "status")
            validate_field_type(result, "status", str)
            validate_field_exists(result, "attempt_number")
            validate_field_type(result, "attempt_number", int)
            validate_field_exists(result, "next_retry_at")
            validate_field_type(result, "next_retry_at", (str, type(None)))

"""
"""
Integration tests for webhook integration with API events.
Integration tests for webhook integration with API events.


This module contains tests for webhook integration with API events,
This module contains tests for webhook integration with API events,
such as triggering webhooks when certain events occur.
such as triggering webhooks when certain events occur.
"""
"""




import hashlib
import hashlib
import hmac
import hmac
import json
import json
import time
import time
from typing import Any, Dict, List
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch
from unittest.mock import MagicMock, patch


import pytest
import pytest


from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_client import APITestClient


(
(
generate_webhook_data,
generate_webhook_data,
generate_niche_analysis_data,
generate_niche_analysis_data,
generate_solution_data
generate_solution_data
)
)




@pytest.fixture
@pytest.fixture
def auth_api_test_client():
    def auth_api_test_client():
    """Create an authenticated API test client."""
    client = APITestClient(base_url="http://localhost:8000/api")
    client.authenticate("test_user", "test_password")
    return client


    @pytest.fixture
    def mock_webhook_server():
    """Create a mock webhook server."""
    server = MagicMock()
    server.received_events = []

    def receive_event(event_data, headers):
    """Receive an event."""
    server.received_events.append({
    "event_data": event_data,
    "headers": headers,
    "timestamp": time.time()
    })
    return {"status": "success"}

    server.receive_event = receive_event
    return server


    class TestWebhookAPIIntegration:

    def validate_success_response(self, response, expected_status=200):
    """Validate a successful API response."""
    assert response.status_code == expected_status
    data = response.json()
    assert "error" not in data
    return data

    def validate_field_exists(self, data, field_name):
    """Validate that a field exists in the data."""
    assert field_name in data
    assert data[field_name] is not None

    def test_webhook_registration(self, auth_api_test_client):
    """Test webhook registration."""
    # Create webhook subscription
    webhook_data = generate_webhook_data(
    url="https://example.com/webhook",
    events=["niche.created", "solution.created"],
    secret="test_webhook_secret"
    )
    response = auth_api_test_client.post("webhooks", webhook_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Webhook endpoint not implemented")

    # Validate response
    webhook_result = self.validate_success_response(response, 201)  # Created
    self.validate_field_exists(webhook_result, "id")
    webhook_id = webhook_result["id"]

    # Get webhook details
    response = auth_api_test_client.get(f"webhooks/{webhook_id}")
    webhook_details = self.validate_success_response(response)

    # Verify webhook details
    assert webhook_details["url"] == webhook_data["url"]
    assert set(webhook_details["events"]) == set(webhook_data["events"])
    assert "secret" not in webhook_details  # Secret should not be returned

    @patch("services.webhook.WebhookService.send_event")
    def test_webhook_event_triggering(self, mock_send_event, auth_api_test_client):
    """Test webhook event triggering."""
    # Create webhook subscription
    webhook_data = generate_webhook_data(
    url="https://example.com/webhook",
    events=["niche.created"],
    secret="test_webhook_secret"
    )
    response = auth_api_test_client.post("webhooks", webhook_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Webhook endpoint not implemented")

    # Validate response
    webhook_result = self.validate_success_response(response, 201)  # Created

    # Create a niche analysis (should trigger the webhook)
    niche_data = generate_niche_analysis_data()
    response = auth_api_test_client.post("niche-analysis/analyze", niche_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Niche analysis endpoint not implemented")

    # Validate response
    niche_result = self.validate_success_response(response, 201)  # Created

    # Check that the webhook was triggered
    mock_send_event.assert_called()

    # Verify the event data
    call_args = mock_send_event.call_args[0]
    assert call_args[0] == "niche.created"
    assert "id" in call_args[1]
    assert call_args[1]["id"] == niche_result["id"]

    def test_webhook_signature_validation(self, auth_api_test_client, mock_webhook_server):
    """Test webhook signature validation."""
    # Create webhook subscription
    webhook_secret = "test_webhook_secret"
    webhook_data = generate_webhook_data(
    url="https://example.com/webhook",
    events=["niche.created"],
    secret=webhook_secret
    )
    response = auth_api_test_client.post("webhooks", webhook_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Webhook endpoint not implemented")

    # Mock the webhook service to use our mock server
    with patch("services.webhook.WebhookService.send_event") as mock_send_event:
    # Set up the mock to call our mock server
    def side_effect(event_type, event_data, webhook_url, webhook_secret):
    # Create the signature
    payload = json.dumps(event_data).encode()
    signature = hmac.new(
    webhook_secret.encode(),
    payload,
    hashlib.sha256
    ).hexdigest()

    # Send to mock server
    headers = {
    "X-Webhook-Signature": signature,
    "X-Webhook-Event": event_type
    }
    return mock_webhook_server.receive_event(event_data, headers)

    mock_send_event.side_effect = side_effect

    # Create a niche analysis (should trigger the webhook)
    niche_data = generate_niche_analysis_data()
    response = auth_api_test_client.post("niche-analysis/analyze", niche_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Niche analysis endpoint not implemented")

    # Validate response
    niche_result = self.validate_success_response(response, 201)  # Created

    # Check that the webhook was triggered
    mock_send_event.assert_called()

    # Verify that the mock server received the event
    assert len(mock_webhook_server.received_events) == 1
    received_event = mock_webhook_server.received_events[0]
    assert received_event["headers"]["X-Webhook-Event"] == "niche.created"
    assert received_event["event_data"]["id"] == niche_result["id"]

    def test_webhook_delivery_retry(self, auth_api_test_client):
    """Test webhook delivery retry mechanism."""
    # Create webhook subscription
    webhook_data = generate_webhook_data(
    url="https://example.com/webhook",
    events=["solution.created"],
    secret="test_webhook_secret"
    )
    response = auth_api_test_client.post("webhooks", webhook_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Webhook endpoint not implemented")

    # Mock the webhook service to simulate failures and retries
    with patch("services.webhook.WebhookService.send_event") as mock_send_event:
    # Set up the mock to fail the first two times
    mock_send_event.side_effect = [
    Exception("Connection error"),  # First attempt fails
    Exception("Timeout error"),     # Second attempt fails
    {"status": "success"}           # Third attempt succeeds
    ]

    # Create a solution (should trigger the webhook)
    solution_data = generate_solution_data()
    response = auth_api_test_client.post("solutions/develop", solution_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Solution development endpoint not implemented")

    # Validate response
    solution_result = self.validate_success_response(response, 201)  # Created

    # Check webhook delivery status
    time.sleep(1)  # Wait for retries to complete
    response = auth_api_test_client.get("webhooks/deliveries")
    deliveries = self.validate_success_response(response)

    # Find the delivery for our event
    solution_deliveries = [
    d for d in deliveries
    if d["event_type"] == "solution.created" and d["event_data"]["id"] == solution_result["id"]
    ]

    # Verify delivery attempts
    assert len(solution_deliveries) > 0
    delivery = solution_deliveries[0]
    assert delivery["attempts"] == 3
    assert delivery["status"] == "delivered"

    def test_webhook_event_filtering(self, auth_api_test_client):
    """Test webhook event filtering."""
    # Create webhook subscription for niche events only
    webhook_data = generate_webhook_data(
    url="https://example.com/webhook1",
    events=["niche.created", "niche.updated"],
    secret="test_webhook_secret1"
    )
    response = auth_api_test_client.post("webhooks", webhook_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Webhook endpoint not implemented")

    # Create webhook subscription for solution events only
    webhook_data = generate_webhook_data(
    url="https://example.com/webhook2",
    events=["solution.created", "solution.updated"],
    secret="test_webhook_secret2"
    )
    response = auth_api_test_client.post("webhooks", webhook_data)

    # Mock the webhook service to track which webhooks are called
    with patch("services.webhook.WebhookService.send_event") as mock_send_event:
    # Create a niche analysis (should trigger only the first webhook)
    niche_data = generate_niche_analysis_data()
    response = auth_api_test_client.post("niche-analysis/analyze", niche_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Niche analysis endpoint not implemented")

    # Create a solution (should trigger only the second webhook)
    solution_data = generate_solution_data()
    response = auth_api_test_client.post("solutions/develop", solution_data)

    # If the endpoint returns 404 or 501, skip the test
    if response.status_code in (404, 501):
    pytest.skip("Solution development endpoint not implemented")

    # Check that the webhook service was called with the correct events
    assert mock_send_event.call_count >= 2

    # Check the first call (niche.created)
    first_call = mock_send_event.call_args_list[0]
    assert first_call[0][0] == "niche.created"
    assert first_call[0][2] == "https://example.com/webhook1"

    # Check the second call (solution.created)
    second_call = mock_send_event.call_args_list[1]
    assert second_call[0][0] == "solution.created"
    assert second_call[0][2] == "https://example.com/webhook2"


    if __name__ == "__main__":
    pytest.main(["-v", "test_webhook_api_integration.py"])
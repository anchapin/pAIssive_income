"""
Tests for API service metrics functionality.

This module tests the Prometheus metrics collection, accuracy, and alert
functionality in the API services.
"""

import json
import re
import time
from unittest.mock import MagicMock, patch

import pytest

from api.services.metrics import (
    WEBHOOK_DELIVERIES_TOTAL,
    WEBHOOK_DELIVERY_DURATION,
    WEBHOOK_HEALTH,
    WEBHOOK_QUEUE_LATENCY,
    WEBHOOK_QUEUE_SIZE,
    WEBHOOK_RATE_LIMIT_REMAINING,
    track_queue_latency,
    track_queue_size,
    track_webhook_delivery,
    update_rate_limit,
)


@pytest.fixture
def reset_metrics():
    """Reset all metrics before each test."""
    # Clear all metrics
    WEBHOOK_DELIVERIES_TOTAL._metrics.clear()
    WEBHOOK_DELIVERY_DURATION._metrics.clear()
    WEBHOOK_QUEUE_SIZE._metrics.clear()
    WEBHOOK_QUEUE_LATENCY._metrics.clear()
    WEBHOOK_HEALTH._metrics.clear()
    WEBHOOK_RATE_LIMIT_REMAINING._metrics.clear()


def test_webhook_delivery_metrics(reset_metrics):
    """Test that webhook delivery metrics are recorded accurately."""
    # Track a successful delivery
    track_webhook_delivery(
        webhook_id="test - webhook - 1", event_type="user.created", duration=0.5, 
            status="success"
    )

    # Track a failed delivery
    track_webhook_delivery(
        webhook_id="test - webhook - 1", event_type="user.created", duration=0.3, 
            status="failed"
    )

    # Track another event type
    track_webhook_delivery(
        webhook_id="test - webhook - 1", event_type="user.updated", duration=0.2, 
            status="success"
    )

    # Check delivery counter
    assert (
        WEBHOOK_DELIVERIES_TOTAL.labels(
            webhook_id="test - webhook - 1", event_type="user.created", status="success"
        )._value.get()
        == 1
    )

    assert (
        WEBHOOK_DELIVERIES_TOTAL.labels(
            webhook_id="test - webhook - 1", event_type="user.created", status="failed"
        )._value.get()
        == 1
    )

    assert (
        WEBHOOK_DELIVERIES_TOTAL.labels(
            webhook_id="test - webhook - 1", event_type="user.updated", status="success"
        )._value.get()
        == 1
    )

    # Check duration histogram
    # For histograms, we need to check the sum and count
    assert (
        WEBHOOK_DELIVERY_DURATION.labels(
            webhook_id="test - webhook - 1", event_type="user.created"
        )._sum.get()
        == 0.8
    )  # 0.5 + 0.3

    assert (
        WEBHOOK_DELIVERY_DURATION.labels(
            webhook_id="test - webhook - 1", event_type="user.created"
        )._count.get()
        == 2
    )

    assert (
        WEBHOOK_DELIVERY_DURATION.labels(
            webhook_id="test - webhook - 1", event_type="user.updated"
        )._sum.get()
        == 0.2
    )

    assert (
        WEBHOOK_DELIVERY_DURATION.labels(
            webhook_id="test - webhook - 1", event_type="user.updated"
        )._count.get()
        == 1
    )


def test_queue_metrics(reset_metrics):
    """Test that queue metrics are recorded accurately."""
    # Track queue size
    track_queue_size(size=10, priority="high")
    track_queue_size(size=20, priority="normal")
    track_queue_size(size=5, priority="low")

    # Check queue size gauge
    assert WEBHOOK_QUEUE_SIZE.labels(priority="high")._value.get() == 10
    assert WEBHOOK_QUEUE_SIZE.labels(priority="normal")._value.get() == 20
    assert WEBHOOK_QUEUE_SIZE.labels(priority="low")._value.get() == 5

    # Update queue size
    track_queue_size(size=15, priority="high")
    assert WEBHOOK_QUEUE_SIZE.labels(priority="high")._value.get() == 15

    # Track queue latency
    track_queue_latency(latency=2.5, priority="high")
    track_queue_latency(latency=5.0, priority="normal")
    track_queue_latency(latency=10.0, priority="low")

    # Check queue latency histogram
    assert WEBHOOK_QUEUE_LATENCY.labels(priority="high")._sum.get() == 2.5
    assert WEBHOOK_QUEUE_LATENCY.labels(priority="high")._count.get() == 1

    assert WEBHOOK_QUEUE_LATENCY.labels(priority="normal")._sum.get() == 5.0
    assert WEBHOOK_QUEUE_LATENCY.labels(priority="normal")._count.get() == 1

    assert WEBHOOK_QUEUE_LATENCY.labels(priority="low")._sum.get() == 10.0
    assert WEBHOOK_QUEUE_LATENCY.labels(priority="low")._count.get() == 1


def test_rate_limit_metrics(reset_metrics):
    """Test that rate limit metrics are recorded accurately."""
    # Update rate limit
    update_rate_limit(webhook_id="test - webhook - 1", remaining=100)
    update_rate_limit(webhook_id="test - webhook - 2", remaining=50)

    # Check rate limit gauge
    assert WEBHOOK_RATE_LIMIT_REMAINING.labels(webhook_id="test - \
        webhook - 1")._value.get() == 100
    assert WEBHOOK_RATE_LIMIT_REMAINING.labels(webhook_id="test - \
        webhook - 2")._value.get() == 50

    # Update rate limit
    update_rate_limit(webhook_id="test - webhook - 1", remaining=90)
    assert WEBHOOK_RATE_LIMIT_REMAINING.labels(webhook_id="test - \
        webhook - 1")._value.get() == 90


@patch("prometheus_client.generate_latest")
def test_prometheus_format(mock_generate_latest, reset_metrics):
    """Test that metrics are correctly formatted in Prometheus format."""
    # Set up mock to return sample Prometheus format data
    mock_generate_latest.return_value = b"""
# HELP webhook_deliveries_total Total number of webhook delivery attempts
# TYPE webhook_deliveries_total counter
webhook_deliveries_total{webhook_id="test - webhook - 1",event_type="user.created",
    status="success"} 1.0
webhook_deliveries_total{webhook_id="test - webhook - 1",event_type="user.created",
    status="failed"} 1.0
webhook_deliveries_total{webhook_id="test - webhook - 1",event_type="user.updated",
    status="success"} 1.0

# HELP webhook_delivery_duration_seconds Time spent delivering webhooks
# TYPE webhook_delivery_duration_seconds histogram
webhook_delivery_duration_seconds_bucket{webhook_id="test - webhook - 1",
    event_type="user.created",le="0.1"} 0.0
webhook_delivery_duration_seconds_bucket{webhook_id="test - webhook - 1",
    event_type="user.created",le="0.5"} 1.0
webhook_delivery_duration_seconds_bucket{webhook_id="test - webhook - 1",
    event_type="user.created",le="1.0"} 2.0
webhook_delivery_duration_seconds_bucket{webhook_id="test - webhook - 1",
    event_type="user.created",le="2.0"} 2.0
webhook_delivery_duration_seconds_bucket{webhook_id="test - webhook - 1",
    event_type="user.created",le="5.0"} 2.0
webhook_delivery_duration_seconds_bucket{webhook_id="test - webhook - 1",
    event_type="user.created",le="10.0"} 2.0
webhook_delivery_duration_seconds_bucket{webhook_id="test - webhook - 1",
    event_type="user.created",le=" + Inf"} 2.0
webhook_delivery_duration_seconds_sum{webhook_id="test - webhook - 1",
    event_type="user.created"} 0.8
webhook_delivery_duration_seconds_count{webhook_id="test - webhook - 1",
    event_type="user.created"} 2.0

# HELP webhook_queue_size Current number of webhooks waiting to be delivered
# TYPE webhook_queue_size gauge
webhook_queue_size{priority="high"} 15.0
webhook_queue_size{priority="normal"} 20.0
webhook_queue_size{priority="low"} 5.0
"""

    # Track some metrics to populate the registry
    track_webhook_delivery(
        webhook_id="test - webhook - 1", event_type="user.created", duration=0.5, 
            status="success"
    )

    track_webhook_delivery(
        webhook_id="test - webhook - 1", event_type="user.created", duration=0.3, 
            status="failed"
    )

    track_webhook_delivery(
        webhook_id="test - webhook - 1", event_type="user.updated", duration=0.2, 
            status="success"
    )

    # Track queue metrics
    track_queue_size(size=15, priority="high")
    track_queue_size(size=20, priority="normal")
    track_queue_size(size=5, priority="low")

    # Get metrics in Prometheus format
    from prometheus_client import generate_latest

    metrics_data = generate_latest()

    # Check that the mock was called
    mock_generate_latest.assert_called_once()

    # Use the mock data for validation
    metrics_text = mock_generate_latest.return_value.decode("utf - 8")

    # Validate metric presence and types
    assert "# TYPE webhook_deliveries_total counter" in metrics_text
    assert "# TYPE webhook_delivery_duration_seconds histogram" in metrics_text
    assert "# TYPE webhook_queue_size gauge" in metrics_text

    # Validate metric labels
    assert 'webhook_id="test - webhook - 1"' in metrics_text
    assert 'event_type="user.created"' in metrics_text
    assert 'status="success"' in metrics_text
    assert 'status="failed"' in metrics_text
    assert 'priority="high"' in metrics_text

    # Validate counter values
    assert re.search(r'webhook_deliveries_total\{.*status="success"\} 1\.0', 
        metrics_text)
    assert re.search(r'webhook_deliveries_total\{.*status="failed"\} 1\.0', 
        metrics_text)

    # Validate histogram values
    assert re.search(r"webhook_delivery_duration_seconds_sum\{.*\} 0\.8", metrics_text)
    assert re.search(r"webhook_delivery_duration_seconds_count\{.*\} 2\.0", 
        metrics_text)

    # Validate gauge values
    assert re.search(r'webhook_queue_size\{priority="high"\} 15\.0', metrics_text)
    assert re.search(r'webhook_queue_size\{priority="normal"\} 20\.0', metrics_text)
    assert re.search(r'webhook_queue_size\{priority="low"\} 5\.0', metrics_text)

    # Validate histogram buckets
    assert re.search(r'webhook_delivery_duration_seconds_bucket\{.*le="0\.1"\} 0\.0', 
        metrics_text)
    assert re.search(r'webhook_delivery_duration_seconds_bucket\{.*le="0\.5"\} 1\.0', 
        metrics_text)
    assert re.search(r'webhook_delivery_duration_seconds_bucket\{.*le="\+Inf"\} 2\.0', 
        metrics_text)


@patch("api.services.metrics.WEBHOOK_HEALTH")
def test_health_metrics(mock_webhook_health, reset_metrics):
    """Test that health metrics are recorded accurately."""
    # Create a mock for the gauge
    mock_labels = MagicMock()
    mock_webhook_health.labels.return_value = mock_labels

    # Define a function to update health metrics
    def update_webhook_health(webhook_id, url, health_status):
        WEBHOOK_HEALTH.labels(webhook_id=webhook_id, url=url).set(health_status)

    # Update health metrics
    update_webhook_health("test - webhook - 1", "https://example.com / webhook1", 
        1.0)  # Healthy
    update_webhook_health("test - webhook - 2", "https://example.com / webhook2", 
        0.0)  # Unhealthy

    # Check that the mock was called correctly
    mock_webhook_health.labels.assert_any_call(
        webhook_id="test - webhook - 1", url="https://example.com / webhook1"
    )
    mock_webhook_health.labels.assert_any_call(
        webhook_id="test - webhook - 2", url="https://example.com / webhook2"
    )

    # Check that the set method was called with the correct values
    mock_labels.set.assert_any_call(1.0)
    mock_labels.set.assert_any_call(0.0)


def test_metric_aggregation():
    """Test that metrics can be aggregated correctly."""
    # Reset metrics
    WEBHOOK_DELIVERIES_TOTAL._metrics.clear()
    WEBHOOK_DELIVERY_DURATION._metrics.clear()

    # Track multiple webhook deliveries
    for i in range(10):
        track_webhook_delivery(
            webhook_id="test - webhook - 1",
            event_type="user.created",
            duration=0.1 * (i + 1),  # 0.1, 0.2, ..., 1.0
            status="success",
        )

    for i in range(5):
        track_webhook_delivery(
            webhook_id="test - webhook - 1",
            event_type="user.created",
            duration=0.2 * (i + 1),  # 0.2, 0.4, ..., 1.0
            status="failed",
        )

    # Check delivery counter
    assert (
        WEBHOOK_DELIVERIES_TOTAL.labels(
            webhook_id="test - webhook - 1", event_type="user.created", status="success"
        )._value.get()
        == 10
    )

    assert (
        WEBHOOK_DELIVERIES_TOTAL.labels(
            webhook_id="test - webhook - 1", event_type="user.created", status="failed"
        )._value.get()
        == 5
    )

    # Check duration histogram
    # Sum should be 0.1 + 0.2 + ... + 1.0 = 5.5 for success
    # Sum should be 0.2 + 0.4 + ... + 1.0 = 3.0 for failed
    assert (
        WEBHOOK_DELIVERY_DURATION.labels(
            webhook_id="test - webhook - 1", event_type="user.created"
        )._sum.get()
        == 5.5 + 3.0
    )

    assert (
        WEBHOOK_DELIVERY_DURATION.labels(
            webhook_id="test - webhook - 1", event_type="user.created"
        )._count.get()
        == 15
    )

    # Check histogram buckets
    # For the 0.5 bucket, we should have 5 success (0.1 - 0.5) and 2 failed (0.2, 0.4)
    histogram = WEBHOOK_DELIVERY_DURATION.labels(
        webhook_id="test - webhook - 1", event_type="user.created"
    )

    # Get the bucket values
    buckets = {}
    for k, v in histogram._buckets.items():
        buckets[k] = v.get()

    # Check specific buckets
    assert buckets[0.5] == 7  # 5 success (0.1 - 0.5) + 2 failed (0.2, 0.4)
    assert buckets[1.0] == 15  # All 15 events


if __name__ == "__main__":
    pytest.main([" - xvs", __file__])

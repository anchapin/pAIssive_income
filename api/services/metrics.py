"""Metrics collection for webhook service."""

from prometheus_client import Counter, Gauge, Histogram

# Delivery metrics
WEBHOOK_DELIVERIES_TOTAL = Counter(
    "webhook_deliveries_total",
    "Total number of webhook delivery attempts",
    ["webhook_id", "event_type", "status"],
)

WEBHOOK_DELIVERY_DURATION = Histogram(
    "webhook_delivery_duration_seconds",
    "Time spent delivering webhooks",
    ["webhook_id", "event_type"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],  # 100ms to 10s
)

# Queue metrics
WEBHOOK_QUEUE_SIZE = Gauge(
    "webhook_queue_size",
    "Current number of webhooks waiting to be delivered",
    ["priority"],
)

WEBHOOK_QUEUE_LATENCY = Histogram(
    "webhook_queue_latency_seconds",
    "Time spent in queue before delivery",
    ["priority"],
    buckets=[1.0, 5.0, 15.0, 30.0, 60.0, 300.0],  # 1s to 5m
)

# Retry metrics
WEBHOOK_RETRY_COUNT = Counter(
    "webhook_retry_count_total",
    "Total number of webhook delivery retries",
    ["webhook_id", "event_type"],
)

WEBHOOK_MAX_RETRIES_EXCEEDED = Counter(
    "webhook_max_retries_exceeded_total",
    "Total number of webhooks that exceeded max retries",
    ["webhook_id", "event_type"],
)

# Error metrics
WEBHOOK_ERRORS_TOTAL = Counter(
    "webhook_errors_total",
    "Total number of webhook errors",
    ["webhook_id", "event_type", "error_type"],
)

# Health metrics
WEBHOOK_HEALTH = Gauge(
    "webhook_health", "Health status of webhook endpoints", ["webhook_id", "url"]
)

# Rate limiting metrics
WEBHOOK_RATE_LIMIT_REMAINING = Gauge(
    "webhook_rate_limit_remaining",
    "Remaining rate limit for webhook endpoints",
    ["webhook_id"],
)


def track_webhook_delivery(
    webhook_id: str, event_type: str, duration: float, status: str
):
    """Track a webhook delivery attempt."""
    WEBHOOK_DELIVERIES_TOTAL.labels(
        webhook_id=webhook_id, event_type=event_type, status=status
    ).inc()

    WEBHOOK_DELIVERY_DURATION.labels(
        webhook_id=webhook_id, event_type=event_type
    ).observe(duration)


def track_webhook_error(webhook_id: str, event_type: str, error_type: str):
    """Track a webhook error."""
    WEBHOOK_ERRORS_TOTAL.labels(
        webhook_id=webhook_id, event_type=event_type, error_type=error_type
    ).inc()


def track_webhook_retry(webhook_id: str, event_type: str):
    """Track a webhook retry attempt."""
    WEBHOOK_RETRY_COUNT.labels(webhook_id=webhook_id, event_type=event_type).inc()


def update_webhook_health(webhook_id: str, url: str, is_healthy: bool):
    """Update webhook endpoint health status."""
    WEBHOOK_HEALTH.labels(webhook_id=webhook_id, url=url).set(1 if is_healthy else 0)


def update_queue_size(size: int, priority: str = "normal"):
    """Update the current webhook queue size."""
    WEBHOOK_QUEUE_SIZE.labels(priority=priority).set(size)


def track_queue_latency(latency: float, priority: str = "normal"):
    """Track how long a webhook spent in the queue."""
    WEBHOOK_QUEUE_LATENCY.labels(priority=priority).observe(latency)


def update_rate_limit(webhook_id: str, remaining: int):
    """Update remaining rate limit for a webhook."""
    WEBHOOK_RATE_LIMIT_REMAINING.labels(webhook_id=webhook_id).set(remaining)

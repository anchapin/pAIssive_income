"""
Metrics routes for REST API server.

This module provides route handlers for metrics.
"""

from typing import Dict, Any, List

# Try to import FastAPI
try:
    from fastapi import APIRouter, Depends
    from fastapi.responses import PlainTextResponse
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for type hints
    class APIRouter:
        pass

    class BaseModel:
        pass

    Field = lambda *args, **kwargs: None


# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(tags=["Metrics"])
else:
    router = None


# Define response models
if FASTAPI_AVAILABLE:

    class MetricValue(BaseModel):
        """
        Model for a metric value.
        """

        name: str = Field(..., description="Name of the metric")
        value: float = Field(..., description="Value of the metric")
        labels: Dict[str, str] = Field(
            default_factory=dict, description="Labels for the metric"
        )

    class MetricsResponse(BaseModel):
        """
        Response model for metrics.
        """

        metrics: List[MetricValue] = Field(..., description="List of metrics")


# Define route handlers
if FASTAPI_AVAILABLE:

    @router.get("/metrics", response_model=MetricsResponse)
    async def get_metrics(server=None):
        """
        Get server metrics.

        Args:
            server: Server instance (injected by dependency)

        Returns:
            Server metrics
        """
        # Get server metrics
        metrics = server.get_metrics()

        # Create response
        return {"metrics": metrics}

    @router.get("/metrics/prometheus", response_class=PlainTextResponse)
    async def get_prometheus_metrics(server=None):
        """
        Get server metrics in Prometheus format.

        Args:
            server: Server instance (injected by dependency)

        Returns:
            Server metrics in Prometheus format
        """
        # Get server metrics
        metrics = server.get_metrics()

        # Convert to Prometheus format
        prometheus_metrics = []

        for metric in metrics:
            # Create metric name
            name = f"ai_models_{metric['name']}"

            # Create labels string
            labels_str = ""
            if metric.get("labels"):
                labels = []
                for key, value in metric["labels"].items():
                    labels.append(f'{key}="{value}"')
                labels_str = "{" + ",".join(labels) + "}"

            # Add metric
            prometheus_metrics.append(f"{name}{labels_str} {metric['value']}")

        # Return metrics
        return "\n".join(prometheus_metrics)

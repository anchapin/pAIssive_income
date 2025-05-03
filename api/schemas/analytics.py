"""
API schemas for analytics.

This module provides Pydantic models for API analytics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RequestStatsResponse(BaseModel):
    """Pydantic model for API request statistics."""

    id: str = Field(..., description="Request ID")
    timestamp: str = Field(..., description="Request timestamp")
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    endpoint: str = Field(..., description="Endpoint name")
    version: Optional[str] = Field(None, description="API version")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    user_id: Optional[str] = Field(None, description="User ID")
    api_key_id: Optional[str] = Field(None, description="API key ID")
    client_ip: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    request_size: Optional[int] = Field(None, description="Request size in bytes")
    response_size: Optional[int] = Field(None, description="Response size in bytes")
    query_params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    error_type: Optional[str] = Field(None, description="Error type")
    error_message: Optional[str] = Field(None, description="Error message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DailyMetricsResponse(BaseModel):
    """Pydantic model for daily aggregated metrics."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    endpoint: str = Field(..., description="Endpoint name")
    version: Optional[str] = Field(None, description="API version")
    request_count: int = Field(..., description="Number of requests")
    error_count: int = Field(..., description="Number of errors")
    avg_response_time: float = Field(..., description="Average response time in seconds")
    min_response_time: float = Field(..., description="Minimum response time in seconds")
    max_response_time: float = Field(..., description="Maximum response time in seconds")
    p95_response_time: float = Field(..., description="95th percentile response time in seconds")
    total_request_size: int = Field(..., description="Total request size in bytes")
    total_response_size: int = Field(..., description="Total response size in bytes")
    unique_users: int = Field(..., description="Number of unique users")
    unique_api_keys: int = Field(..., description="Number of unique API keys")


class EndpointStatsResponse(BaseModel):
    """Pydantic model for endpoint statistics."""

    endpoint: str = Field(..., description="Endpoint name")
    version: Optional[str] = Field(None, description="API version")
    total_requests: int = Field(..., description="Total number of requests")
    total_errors: int = Field(..., description="Total number of errors")
    avg_response_time: float = Field(..., description="Average response time in seconds")
    min_response_time: float = Field(..., description="Minimum response time in seconds")
    max_response_time: float = Field(..., description="Maximum response time in seconds")
    total_request_size: int = Field(..., description="Total request size in bytes")
    total_response_size: int = Field(..., description="Total response size in bytes")
    total_unique_users: int = Field(..., description="Total number of unique users")
    total_unique_api_keys: int = Field(..., description="Total number of unique API keys")


class UserStatsResponse(BaseModel):
    """Pydantic model for user statistics."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    user_id: str = Field(..., description="User ID")
    request_count: int = Field(..., description="Number of requests")
    error_count: int = Field(..., description="Number of errors")
    total_response_time: float = Field(..., description="Total response time in seconds")
    endpoints_used: List[str] = Field(..., description="List of endpoints used")


class ApiKeyStatsResponse(BaseModel):
    """Pydantic model for API key statistics."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    api_key_id: str = Field(..., description="API key ID")
    request_count: int = Field(..., description="Number of requests")
    error_count: int = Field(..., description="Number of errors")
    total_response_time: float = Field(..., description="Total response time in seconds")
    endpoints_used: List[str] = Field(..., description="List of endpoints used")


class AnalyticsSummaryResponse(BaseModel):
    """Pydantic model for API usage summary."""

    total_requests: int = Field(..., description="Total number of requests")
    total_errors: int = Field(..., description="Total number of errors")
    error_rate: float = Field(..., description="Error rate (errors / total requests)")
    avg_response_time: float = Field(..., description="Average response time in seconds")
    unique_users: int = Field(..., description="Number of unique users")
    unique_api_keys: int = Field(..., description="Number of unique API keys")
    top_endpoints: List[EndpointStatsResponse] = Field(
        ..., description="Top endpoints by request count"
    )


class EndpointRealTimeMetrics(BaseModel):
    """Schema for real-time metrics for a specific endpoint."""

    request_count: int = Field(..., description="Number of requests")
    error_count: int = Field(..., description="Number of errors")
    error_rate: float = Field(..., description="Error rate")
    avg_response_time: float = Field(..., description="Average response time in milliseconds")
    requests_per_minute: float = Field(..., description="Requests per minute")


class RealTimeMetricsResponse(BaseModel):
    """Schema for real-time API metrics."""

    request_count: int = Field(..., description="Total number of requests")
    error_count: int = Field(..., description="Total number of errors")
    error_rate: float = Field(..., description="Error rate")
    avg_response_time: float = Field(..., description="Average response time in milliseconds")
    p95_response_time: float = Field(
        ..., description="95th percentile response time in milliseconds"
    )
    requests_per_minute: float = Field(..., description="Requests per minute")
    endpoints: Dict[str, EndpointRealTimeMetrics] = Field(..., description="Metrics by endpoint")
    timestamp: str = Field(..., description="Timestamp of the metrics")


class AlertResponse(BaseModel):
    """Schema for API alert."""

    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    timestamp: str = Field(..., description="Alert timestamp")
    data: Dict[str, Any] = Field(..., description="Alert data")


class AlertThresholdRequest(BaseModel):
    """Schema for setting alert thresholds."""

    metric: str = Field(
        ..., description="Metric name (error_rate, response_time, requests_per_minute)"
    )
    threshold: float = Field(..., description="Threshold value")


class AlertThresholdResponse(BaseModel):
    """Schema for alert threshold response."""

    metric: str = Field(..., description="Metric name")
    threshold: float = Field(..., description="Threshold value")
    message: str = Field(..., description="Success message")

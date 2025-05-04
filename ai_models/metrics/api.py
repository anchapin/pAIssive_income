import contextlib
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

from ai_models.metrics.dashboard import MetricsDashboard

(

"""
"""
API for model performance metrics.
API for model performance metrics.


This module provides simplified interfaces for recording and accessing
This module provides simplified interfaces for recording and accessing
model performance metrics throughout the application.
model performance metrics throughout the application.
"""
"""




# Set up logging
# Set up logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)
# Import metrics classes
# Import metrics classes
from ai_models.metrics.enhanced_metrics import (EnhancedInferenceTracker,
from ai_models.metrics.enhanced_metrics import (EnhancedInferenceTracker,
EnhancedPerformanceMonitor)
EnhancedPerformanceMonitor)




class MetricsAPI:
    class MetricsAPI:
    """
    """
    API for tracking and accessing model performance metrics.
    API for tracking and accessing model performance metrics.


    This class provides simplified interfaces for recording and accessing
    This class provides simplified interfaces for recording and accessing
    model performance metrics throughout the application.
    model performance metrics throughout the application.
    """
    """


    _instance = None
    _instance = None


    @classmethod
    @classmethod
    def get_instance(cls, config=None, db_path: str = None):
    def get_instance(cls, config=None, db_path: str = None):
    """
    """
    Get or create a singleton instance of the metrics API.
    Get or create a singleton instance of the metrics API.


    This ensures that metrics are consistently tracked across the application.
    This ensures that metrics are consistently tracked across the application.


    Args:
    Args:
    config: Optional configuration to use when creating the instance
    config: Optional configuration to use when creating the instance
    db_path: Optional database path to use when creating the instance
    db_path: Optional database path to use when creating the instance


    Returns:
    Returns:
    MetricsAPI instance
    MetricsAPI instance
    """
    """
    if cls._instance is None:
    if cls._instance is None:
    cls._instance = cls(config, db_path)
    cls._instance = cls(config, db_path)
    return cls._instance
    return cls._instance


    def __init__(self, config=None, db_path: str = None):
    def __init__(self, config=None, db_path: str = None):
    """
    """
    Initialize the metrics API.
    Initialize the metrics API.


    Args:
    Args:
    config: Model configuration object or dict
    config: Model configuration object or dict
    db_path: Path to the metrics database
    db_path: Path to the metrics database
    """
    """
    self.monitor = EnhancedPerformanceMonitor(config, db_path)
    self.monitor = EnhancedPerformanceMonitor(config, db_path)
    self._dashboard = None
    self._dashboard = None


    # Store registered model costs
    # Store registered model costs
    self.registered_models = {}
    self.registered_models = {}


    def register_model(
    def register_model(
    self,
    self,
    model_id: str,
    model_id: str,
    model_name: str = None,
    model_name: str = None,
    prompt_cost_per_1k: float = 0.0,
    prompt_cost_per_1k: float = 0.0,
    completion_cost_per_1k: float = 0.0,
    completion_cost_per_1k: float = 0.0,
    ) -> None:
    ) -> None:
    """
    """
    Register model information including cost rates.
    Register model information including cost rates.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    model_name: Human-readable name of the model
    model_name: Human-readable name of the model
    prompt_cost_per_1k: Cost per 1000 prompt tokens
    prompt_cost_per_1k: Cost per 1000 prompt tokens
    completion_cost_per_1k: Cost per 1000 completion tokens
    completion_cost_per_1k: Cost per 1000 completion tokens
    """
    """
    self.registered_models[model_id] = {
    self.registered_models[model_id] = {
    "model_name": model_name or model_id,
    "model_name": model_name or model_id,
    "prompt_cost_per_1k": prompt_cost_per_1k,
    "prompt_cost_per_1k": prompt_cost_per_1k,
    "completion_cost_per_1k": completion_cost_per_1k,
    "completion_cost_per_1k": completion_cost_per_1k,
    }
    }


    # Register cost rates with the monitor
    # Register cost rates with the monitor
    self.monitor.set_model_cost_rates(
    self.monitor.set_model_cost_rates(
    model_id, prompt_cost_per_1k, completion_cost_per_1k
    model_id, prompt_cost_per_1k, completion_cost_per_1k
    )
    )


    logger.info(
    logger.info(
    f"Registered model {model_id} with prompt cost: ${prompt_cost_per_1k}/1k, "
    f"Registered model {model_id} with prompt cost: ${prompt_cost_per_1k}/1k, "
    f"completion cost: ${completion_cost_per_1k}/1k"
    f"completion cost: ${completion_cost_per_1k}/1k"
    )
    )


    @contextlib.contextmanager
    @contextlib.contextmanager
    def track_inference(
    def track_inference(
    self,
    self,
    model_id: str,
    model_id: str,
    input_text: str = "",
    input_text: str = "",
    input_tokens: int = 0,
    input_tokens: int = 0,
    batch_id: str = None,
    batch_id: str = None,
    user_id: str = None,
    user_id: str = None,
    session_id: str = None,
    session_id: str = None,
    deployment_env: str = None,
    deployment_env: str = None,
    tags: List[str] = None,
    tags: List[str] = None,
    ) -> EnhancedInferenceTracker:
    ) -> EnhancedInferenceTracker:
    """
    """
    Context manager for tracking model inferences.
    Context manager for tracking model inferences.


    Example usage:
    Example usage:
    ```
    ```
    with metrics_api.track_inference("gpt4", input_text="Hello") as tracker:
    with metrics_api.track_inference("gpt4", input_text="Hello") as tracker:
    response = call_model("gpt4", "Hello")
    response = call_model("gpt4", "Hello")
    tracker.record_first_token()  # Call when first token is received
    tracker.record_first_token()  # Call when first token is received
    # ...later...
    # ...later...
    # The tracker.stop() will be called automatically at the end of the block
    # The tracker.stop() will be called automatically at the end of the block
    # with the response text
    # with the response text
    ```
    ```


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    input_text: Input text for the inference
    input_text: Input text for the inference
    input_tokens: Optional pre-computed input token count
    input_tokens: Optional pre-computed input token count
    batch_id: Optional batch ID for grouping related inferences
    batch_id: Optional batch ID for grouping related inferences
    user_id: Optional ID of the user making the request
    user_id: Optional ID of the user making the request
    session_id: Optional ID of the user session
    session_id: Optional ID of the user session
    deployment_env: Optional deployment environment (e.g., "prod", "staging")
    deployment_env: Optional deployment environment (e.g., "prod", "staging")
    tags: Optional list of tags for the request
    tags: Optional list of tags for the request


    Returns:
    Returns:
    EnhancedInferenceTracker instance within a context manager
    EnhancedInferenceTracker instance within a context manager
    """
    """
    # Create tracker
    # Create tracker
    tracker = self.monitor.track_enhanced_inference(model_id, batch_id)
    tracker = self.monitor.track_enhanced_inference(model_id, batch_id)


    # Track when tracking was requested (for queue time)
    # Track when tracking was requested (for queue time)
    tracker.track_queue_time()
    tracker.track_queue_time()


    # Add request context
    # Add request context
    if user_id or session_id or tags:
    if user_id or session_id or tags:
    tracker.add_request_context(
    tracker.add_request_context(
    user_id=user_id, session_id=session_id, tags=tags
    user_id=user_id, session_id=session_id, tags=tags
    )
    )


    # Add system context
    # Add system context
    if deployment_env:
    if deployment_env:
    tracker.add_system_context(deployment_env=deployment_env)
    tracker.add_system_context(deployment_env=deployment_env)


    try:
    try:
    # Start tracking
    # Start tracking
    tracker.start(input_text=input_text, input_tokens=input_tokens)
    tracker.start(input_text=input_text, input_tokens=input_tokens)


    # Return tracker to the context manager
    # Return tracker to the context manager
    yield tracker
    yield tracker


except Exception as e:
except Exception as e:
    # Record error if exception occurs
    # Record error if exception occurs
    tracker.record_error(error_type=type(e).__name__, error_message=str(e))
    tracker.record_error(error_type=type(e).__name__, error_message=str(e))
    tracker.stop()
    tracker.stop()
    raise
    raise


    if not tracker._has_stopped:
    if not tracker._has_stopped:
    # Stop tracking if not already stopped
    # Stop tracking if not already stopped
    tracker.stop()
    tracker.stop()


    def track_inference_decorator(self, model_id: str):
    def track_inference_decorator(self, model_id: str):
    """
    """
    Decorator for tracking model inferences in function calls.
    Decorator for tracking model inferences in function calls.


    Example usage:
    Example usage:
    ```python
    ```python
    @metrics_api.track_inference_decorator("gpt4")
    @metrics_api.track_inference_decorator("gpt4")
    def generate_text(prompt, **kwargs):
    def generate_text(prompt, **kwargs):
    # Call model and return response
    # Call model and return response
    return model_response
    return model_response
    ```
    ```


    Args:
    Args:
    model_id: ID of the model to track
    model_id: ID of the model to track


    Returns:
    Returns:
    Decorator function
    Decorator function
    """
    """


    def decorator(func):
    def decorator(func):
    @wraps(func)
    @wraps(func)
    def wrapper(*args, **kwargs):
    def wrapper(*args, **kwargs):
    input_text = ""
    input_text = ""
    if args and isinstance(args[0], str):
    if args and isinstance(args[0], str):
    input_text = args[0]
    input_text = args[0]
    elif "prompt" in kwargs and isinstance(kwargs["prompt"], str):
    elif "prompt" in kwargs and isinstance(kwargs["prompt"], str):
    input_text = kwargs["prompt"]
    input_text = kwargs["prompt"]


    # Extract optional context from kwargs
    # Extract optional context from kwargs
    user_id = kwargs.pop("user_id", None)
    user_id = kwargs.pop("user_id", None)
    session_id = kwargs.pop("session_id", None)
    session_id = kwargs.pop("session_id", None)
    tags = kwargs.pop("tags", None)
    tags = kwargs.pop("tags", None)


    with self.track_inference(
    with self.track_inference(
    model_id=model_id,
    model_id=model_id,
    input_text=input_text,
    input_text=input_text,
    user_id=user_id,
    user_id=user_id,
    session_id=session_id,
    session_id=session_id,
    tags=tags,
    tags=tags,
    ) as tracker:
    ) as tracker:
    # Call the original function
    # Call the original function
    response = func(*args, **kwargs)
    response = func(*args, **kwargs)


    # Extract output text if response is a string or has a "text" attribute
    # Extract output text if response is a string or has a "text" attribute
    output_text = ""
    output_text = ""
    if isinstance(response, str):
    if isinstance(response, str):
    output_text = response
    output_text = response
    elif hasattr(response, "text") and isinstance(response.text, str):
    elif hasattr(response, "text") and isinstance(response.text, str):
    output_text = response.text
    output_text = response.text


    # Stop tracking with output text
    # Stop tracking with output text
    tracker.stop(output_text=output_text)
    tracker.stop(output_text=output_text)


    return response
    return response


    return wrapper
    return wrapper


    return decorator
    return decorator


    def get_dashboard(self, output_dir: str = None):
    def get_dashboard(self, output_dir: str = None):
    """
    """
    Get the dashboard generator.
    Get the dashboard generator.


    Args:
    Args:
    output_dir: Optional output directory for dashboard files
    output_dir: Optional output directory for dashboard files


    Returns:
    Returns:
    MetricsDashboard instance
    MetricsDashboard instance
    """
    """
    if self._dashboard is None or (
    if self._dashboard is None or (
    output_dir and output_dir != self._dashboard.output_dir
    output_dir and output_dir != self._dashboard.output_dir
    ):
    ):
    self._dashboard = MetricsDashboard(
    self._dashboard = MetricsDashboard(
    performance_monitor=self.monitor, output_dir=output_dir
    performance_monitor=self.monitor, output_dir=output_dir
    )
    )
    return self._dashboard
    return self._dashboard


    def generate_model_dashboard(
    def generate_model_dashboard(
    self, model_id: str, days: int = 30, output_dir: str = None
    self, model_id: str, days: int = 30, output_dir: str = None
    ) -> str:
    ) -> str:
    """
    """
    Generate a model performance dashboard.
    Generate a model performance dashboard.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    days: Number of days of data to include
    days: Number of days of data to include
    output_dir: Optional output directory for dashboard files
    output_dir: Optional output directory for dashboard files


    Returns:
    Returns:
    Path to the generated dashboard HTML file
    Path to the generated dashboard HTML file
    """
    """
    dashboard = self.get_dashboard(output_dir)
    dashboard = self.get_dashboard(output_dir)
    return dashboard.generate_model_dashboard(model_id=model_id, days=days)
    return dashboard.generate_model_dashboard(model_id=model_id, days=days)


    def generate_model_comparison(
    def generate_model_comparison(
    self, model_ids: List[str], days: int = 30, output_dir: str = None
    self, model_ids: List[str], days: int = 30, output_dir: str = None
    ) -> str:
    ) -> str:
    """
    """
    Generate a model comparison dashboard.
    Generate a model comparison dashboard.


    Args:
    Args:
    model_ids: List of model IDs to compare
    model_ids: List of model IDs to compare
    days: Number of days of data to include
    days: Number of days of data to include
    output_dir: Optional output directory for dashboard files
    output_dir: Optional output directory for dashboard files


    Returns:
    Returns:
    Path to the generated comparison dashboard HTML file
    Path to the generated comparison dashboard HTML file
    """
    """
    dashboard = self.get_dashboard(output_dir)
    dashboard = self.get_dashboard(output_dir)


    # Use registered model names if available
    # Use registered model names if available
    model_names = []
    model_names = []
    for model_id in model_ids:
    for model_id in model_ids:
    if model_id in self.registered_models:
    if model_id in self.registered_models:
    model_names.append(
    model_names.append(
    self.registered_models[model_id].get("model_name", model_id)
    self.registered_models[model_id].get("model_name", model_id)
    )
    )
    else:
    else:
    model_names.append(model_id)
    model_names.append(model_id)


    return dashboard.generate_model_comparison_dashboard(
    return dashboard.generate_model_comparison_dashboard(
    model_ids=model_ids, model_names=model_names, days=days
    model_ids=model_ids, model_names=model_names, days=days
    )
    )


    def get_token_usage_summary(
    def get_token_usage_summary(
    self, model_id: Optional[str] = None, days: int = 30, include_costs: bool = True
    self, model_id: Optional[str] = None, days: int = 30, include_costs: bool = True
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get a summary of token usage and costs.
    Get a summary of token usage and costs.


    Args:
    Args:
    model_id: Optional ID of the model to filter by
    model_id: Optional ID of the model to filter by
    days: Number of days to include
    days: Number of days to include
    include_costs: Whether to include cost calculations
    include_costs: Whether to include cost calculations


    Returns:
    Returns:
    Dictionary with token usage summary
    Dictionary with token usage summary
    """
    """
    # Get time range
    # Get time range
    end_time = datetime.now()
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    start_time = end_time - timedelta(days=days)
    time_range = (start_time, end_time)
    time_range = (start_time, end_time)


    # Prepare filters for database query
    # Prepare filters for database query
    db_filters = {"time_range": time_range}
    db_filters = {"time_range": time_range}
    if model_id:
    if model_id:
    db_filters["model_id"] = model_id
    db_filters["model_id"] = model_id


    # Get metrics from database
    # Get metrics from database
    metrics_data = self.monitor.metrics_db.get_metrics(**db_filters, limit=10000)
    metrics_data = self.monitor.metrics_db.get_metrics(**db_filters, limit=10000)


    # Aggregate token usage
    # Aggregate token usage
    model_usage = {}
    model_usage = {}
    total_prompt_tokens = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_completion_tokens = 0
    total_tokens = 0
    total_tokens = 0
    total_prompt_cost = 0.0
    total_prompt_cost = 0.0
    total_completion_cost = 0.0
    total_completion_cost = 0.0
    total_cost = 0.0
    total_cost = 0.0


    for metric in metrics_data:
    for metric in metrics_data:
    current_model_id = metric["model_id"]
    current_model_id = metric["model_id"]


    # Initialize model usage entry if needed
    # Initialize model usage entry if needed
    if current_model_id not in model_usage:
    if current_model_id not in model_usage:
    model_name = (
    model_name = (
    self.registered_models.get(current_model_id, {}).get("model_name")
    self.registered_models.get(current_model_id, {}).get("model_name")
    or current_model_id
    or current_model_id
    )
    )
    model_usage[current_model_id] = {
    model_usage[current_model_id] = {
    "model_name": model_name,
    "model_name": model_name,
    "prompt_tokens": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "total_tokens": 0,
    "prompt_cost": 0.0,
    "prompt_cost": 0.0,
    "completion_cost": 0.0,
    "completion_cost": 0.0,
    "total_cost": 0.0,
    "total_cost": 0.0,
    "num_requests": 0,
    "num_requests": 0,
    }
    }


    # Extract token usage from metadata if available
    # Extract token usage from metadata if available
    token_usage = {}
    token_usage = {}
    if (
    if (
    isinstance(metric.get("metadata"), dict)
    isinstance(metric.get("metadata"), dict)
    and "token_usage" in metric["metadata"]
    and "token_usage" in metric["metadata"]
    ):
    ):
    token_usage = metric["metadata"]["token_usage"]
    token_usage = metric["metadata"]["token_usage"]


    # Get token counts
    # Get token counts
    prompt_tokens = token_usage.get("prompt_tokens", 0)
    prompt_tokens = token_usage.get("prompt_tokens", 0)
    completion_tokens = token_usage.get("completion_tokens", 0)
    completion_tokens = token_usage.get("completion_tokens", 0)


    # Fall back to input/output tokens if token usage not available
    # Fall back to input/output tokens if token usage not available
    if prompt_tokens == 0 and "input_tokens" in metric:
    if prompt_tokens == 0 and "input_tokens" in metric:
    prompt_tokens = metric["input_tokens"]
    prompt_tokens = metric["input_tokens"]


    if completion_tokens == 0 and "output_tokens" in metric:
    if completion_tokens == 0 and "output_tokens" in metric:
    completion_tokens = metric["output_tokens"]
    completion_tokens = metric["output_tokens"]


    # Update model-specific token counts
    # Update model-specific token counts
    model_usage[current_model_id]["prompt_tokens"] += prompt_tokens
    model_usage[current_model_id]["prompt_tokens"] += prompt_tokens
    model_usage[current_model_id]["completion_tokens"] += completion_tokens
    model_usage[current_model_id]["completion_tokens"] += completion_tokens
    model_usage[current_model_id]["total_tokens"] += (
    model_usage[current_model_id]["total_tokens"] += (
    prompt_tokens + completion_tokens
    prompt_tokens + completion_tokens
    )
    )
    model_usage[current_model_id]["num_requests"] += 1
    model_usage[current_model_id]["num_requests"] += 1


    # Update token costs
    # Update token costs
    if include_costs:
    if include_costs:
    # Get cost from token usage if available
    # Get cost from token usage if available
    prompt_cost = token_usage.get("prompt_cost", 0.0)
    prompt_cost = token_usage.get("prompt_cost", 0.0)
    completion_cost = token_usage.get("completion_cost", 0.0)
    completion_cost = token_usage.get("completion_cost", 0.0)


    # If not available in token usage, calculate based on registered rates
    # If not available in token usage, calculate based on registered rates
    if (
    if (
    prompt_cost == 0.0
    prompt_cost == 0.0
    and completion_cost == 0.0
    and completion_cost == 0.0
    and current_model_id in self.registered_models
    and current_model_id in self.registered_models
    ):
    ):
    rates = self.registered_models[current_model_id]
    rates = self.registered_models[current_model_id]
    prompt_cost = (prompt_tokens / 1000) * rates.get(
    prompt_cost = (prompt_tokens / 1000) * rates.get(
    "prompt_cost_per_1k", 0.0
    "prompt_cost_per_1k", 0.0
    )
    )
    completion_cost = (completion_tokens / 1000) * rates.get(
    completion_cost = (completion_tokens / 1000) * rates.get(
    "completion_cost_per_1k", 0.0
    "completion_cost_per_1k", 0.0
    )
    )


    # Fall back to estimated_cost if needed
    # Fall back to estimated_cost if needed
    if (
    if (
    prompt_cost == 0.0
    prompt_cost == 0.0
    and completion_cost == 0.0
    and completion_cost == 0.0
    and "estimated_cost" in metric
    and "estimated_cost" in metric
    ):
    ):
    # Split estimated cost proportionally between prompt and completion
    # Split estimated cost proportionally between prompt and completion
    total = prompt_tokens + completion_tokens
    total = prompt_tokens + completion_tokens
    if total > 0:
    if total > 0:
    prompt_ratio = prompt_tokens / total
    prompt_ratio = prompt_tokens / total
    completion_ratio = completion_tokens / total
    completion_ratio = completion_tokens / total
    prompt_cost = metric["estimated_cost"] * prompt_ratio
    prompt_cost = metric["estimated_cost"] * prompt_ratio
    completion_cost = metric["estimated_cost"] * completion_ratio
    completion_cost = metric["estimated_cost"] * completion_ratio


    model_usage[current_model_id]["prompt_cost"] += prompt_cost
    model_usage[current_model_id]["prompt_cost"] += prompt_cost
    model_usage[current_model_id]["completion_cost"] += completion_cost
    model_usage[current_model_id]["completion_cost"] += completion_cost
    model_usage[current_model_id]["total_cost"] += (
    model_usage[current_model_id]["total_cost"] += (
    prompt_cost + completion_cost
    prompt_cost + completion_cost
    )
    )


    # Update totals
    # Update totals
    total_prompt_tokens += prompt_tokens
    total_prompt_tokens += prompt_tokens
    total_completion_tokens += completion_tokens
    total_completion_tokens += completion_tokens
    total_tokens += prompt_tokens + completion_tokens
    total_tokens += prompt_tokens + completion_tokens
    total_prompt_cost += prompt_cost if include_costs else 0.0
    total_prompt_cost += prompt_cost if include_costs else 0.0
    total_completion_cost += completion_cost if include_costs else 0.0
    total_completion_cost += completion_cost if include_costs else 0.0
    total_cost += (prompt_cost + completion_cost) if include_costs else 0.0
    total_cost += (prompt_cost + completion_cost) if include_costs else 0.0


    # Create summary
    # Create summary
    summary = {
    summary = {
    "start_date": start_time.isoformat(),
    "start_date": start_time.isoformat(),
    "end_date": end_time.isoformat(),
    "end_date": end_time.isoformat(),
    "days": days,
    "days": days,
    "total_prompt_tokens": total_prompt_tokens,
    "total_prompt_tokens": total_prompt_tokens,
    "total_completion_tokens": total_completion_tokens,
    "total_completion_tokens": total_completion_tokens,
    "total_tokens": total_tokens,
    "total_tokens": total_tokens,
    "num_requests": len(metrics_data),
    "num_requests": len(metrics_data),
    "model_breakdown": model_usage,
    "model_breakdown": model_usage,
    }
    }


    if include_costs:
    if include_costs:
    summary["total_prompt_cost"] = total_prompt_cost
    summary["total_prompt_cost"] = total_prompt_cost
    summary["total_completion_cost"] = total_completion_cost
    summary["total_completion_cost"] = total_completion_cost
    summary["total_cost"] = total_cost
    summary["total_cost"] = total_cost


    # Add cost per 1k tokens
    # Add cost per 1k tokens
    if total_tokens > 0:
    if total_tokens > 0:
    summary["cost_per_1k_tokens"] = (total_cost * 1000) / total_tokens
    summary["cost_per_1k_tokens"] = (total_cost * 1000) / total_tokens


    return summary
    return summary


    def set_alert_threshold(
    def set_alert_threshold(
    self,
    self,
    model_id: str,
    model_id: str,
    metric_name: str,
    metric_name: str,
    threshold_value: float,
    threshold_value: float,
    is_upper_bound: bool = True,
    is_upper_bound: bool = True,
    cooldown_minutes: int = 60,
    cooldown_minutes: int = 60,
    notification_channels: List[str] = None,
    notification_channels: List[str] = None,
    ) -> None:
    ) -> None:
    """
    """
    Set an alert threshold for a model metric.
    Set an alert threshold for a model metric.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    metric_name: Name of the metric to monitor (e.g., "latency_ms", "tokens_per_second")
    metric_name: Name of the metric to monitor (e.g., "latency_ms", "tokens_per_second")
    threshold_value: Value to trigger alert
    threshold_value: Value to trigger alert
    is_upper_bound: If True, alert when value > threshold
    is_upper_bound: If True, alert when value > threshold
    If False, alert when value < threshold
    If False, alert when value < threshold
    cooldown_minutes: Minimum minutes between repeated alerts
    cooldown_minutes: Minimum minutes between repeated alerts
    notification_channels: List of notification channels
    notification_channels: List of notification channels
    """
    """
    self.monitor.set_alert_threshold(
    self.monitor.set_alert_threshold(
    model_id=model_id,
    model_id=model_id,
    metric_name=metric_name,
    metric_name=metric_name,
    threshold_value=threshold_value,
    threshold_value=threshold_value,
    is_upper_bound=is_upper_bound,
    is_upper_bound=is_upper_bound,
    cooldown_minutes=cooldown_minutes,
    cooldown_minutes=cooldown_minutes,
    notification_channels=notification_channels or ["log"],
    notification_channels=notification_channels or ["log"],
    )
    )


    logger.info(
    logger.info(
    f"Alert set for {model_id} - {metric_name} "
    f"Alert set for {model_id} - {metric_name} "
    f"{'>' if is_upper_bound else '<'} {threshold_value}"
    f"{'>' if is_upper_bound else '<'} {threshold_value}"
    )
    )


    def register_alert_handler(self, channel: str, handler_func) -> None:
    def register_alert_handler(self, channel: str, handler_func) -> None:
    """
    """
    Register a handler function for alert notifications.
    Register a handler function for alert notifications.


    Args:
    Args:
    channel: Channel name for the handler
    channel: Channel name for the handler
    handler_func: Function to call when an alert is triggered.
    handler_func: Function to call when an alert is triggered.
    Should accept (message, alert_config, value)
    Should accept (message, alert_config, value)
    """
    """
    self.monitor.register_alert_handler(channel, handler_func)
    self.monitor.register_alert_handler(channel, handler_func)
    logger.info(f"Registered alert handler for channel: {channel}")
    logger.info(f"Registered alert handler for channel: {channel}")


    def cleanup_old_metrics(self, days: int = 180) -> int:
    def cleanup_old_metrics(self, days: int = 180) -> int:
    """
    """
    Remove metrics older than the specified number of days.
    Remove metrics older than the specified number of days.


    Args:
    Args:
    days: Number of days to keep
    days: Number of days to keep


    Returns:
    Returns:
    Number of records deleted
    Number of records deleted
    """
    """
    return self.monitor.metrics_db.cleanup_old_metrics(days)
    return self.monitor.metrics_db.cleanup_old_metrics(days)




    # Create a global instance of the metrics API
    # Create a global instance of the metrics API
    metrics_api = MetricsAPI.get_instance())
    metrics_api = MetricsAPI.get_instance())
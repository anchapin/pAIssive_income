
import logging
import os
import statistics
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from ai_models.performance_monitor import 

import logging
import os
import statistics
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


            import matplotlib.pyplot
            import numpy
            import pandas
            from matplotlib.dates import DateFormatter
        except ImportError
            import traceback
            import psutil
                import resource

(

"""
Enhanced performance metrics for AI models.

This module extends the base performance monitoring with advanced metrics tracking,
cost calculation, and model comparison features.
"""





# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import base metrics classes
from ai_models.performance_monitor import (
    InferenceMetrics,
    ModelComparisonReport,
    ModelPerformanceReport,
    PerformanceMonitor,
)


@dataclass
class TokenUsageMetrics:
    """
    Enhanced token usage tracking metrics.
    """

    # Basic token counts
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Token rates
    tokens_per_second: float = 0.0
    prompt_tokens_per_second: float = 0.0
    completion_tokens_per_second: float = 0.0

    # Token ratio
    completion_to_prompt_ratio: float = 0.0

    # Cost calculations
    prompt_cost: float = 0.0
    completion_cost: float = 0.0
    total_cost: float = 0.0

    # Cost per token
    cost_per_prompt_token: float = 0.0
    cost_per_completion_token: float = 0.0
    cost_per_token: float = 0.0

    # Currency
    currency: str = "USD"

    def calculate_metrics(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_time: float,
        prompt_time: float = 0.0,
        completion_time: float = 0.0,
        prompt_cost_per_1k: float = 0.0,
        completion_cost_per_1k: float = 0.0,
    ) -> None:
        """
        Calculate token usage metrics.

        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            total_time: Total time in seconds
            prompt_time: Time to process prompt in seconds
            completion_time: Time to generate completion in seconds
            prompt_cost_per_1k: Cost per 1000 prompt tokens
            completion_cost_per_1k: Cost per 1000 completion tokens
        """
        # Set token counts
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens

        # Calculate token rates
        if total_time > 0:
            self.tokens_per_second = self.total_tokens / total_time

            if prompt_time > 0:
                self.prompt_tokens_per_second = prompt_tokens / prompt_time

            if completion_time > 0:
                self.completion_tokens_per_second = completion_tokens / completion_time

        # Calculate token ratio
        if prompt_tokens > 0:
            self.completion_to_prompt_ratio = completion_tokens / prompt_tokens

        # Calculate costs
        self.prompt_cost = (prompt_tokens / 1000) * prompt_cost_per_1k
        self.completion_cost = (completion_tokens / 1000) * completion_cost_per_1k
        self.total_cost = self.prompt_cost + self.completion_cost

        # Calculate cost per token
        if prompt_tokens > 0:
            self.cost_per_prompt_token = self.prompt_cost / prompt_tokens

        if completion_tokens > 0:
            self.cost_per_completion_token = self.completion_cost / completion_tokens

        if self.total_tokens > 0:
            self.cost_per_token = self.total_cost / self.total_tokens


@dataclass
class EnhancedInferenceMetrics(InferenceMetrics):
    """
    Enhanced metrics for model inferences with more detailed token tracking.
    """

    # Token tracking
    token_usage: TokenUsageMetrics = field(default_factory=TokenUsageMetrics)

    # Additional timing metrics
    queue_time_ms: float = 0.0  # Time spent in queue before processing
    prompt_processing_time_ms: float = 0.0  # Time to process the prompt
    completion_time_ms: float = 0.0  # Time to generate the completion

    # Rate limiting metrics
    rate_limited: bool = False
    rate_limit_reason: str = ""

    # Error tracking
    error_occurred: bool = False
    error_type: str = ""
    error_message: str = ""

    # Request context
    project_id: str = ""
    user_id: str = ""
    session_id: str = ""
    request_tags: List[str] = field(default_factory=list)

    # System context
    deployment_env: str = ""  # e.g., "production", "staging", "development"
    api_version: str = ""
    client_info: Dict[str, Any] = field(default_factory=dict)

    # Cache metrics
    cache_hit: bool = False
    cache_key: str = ""
    cache_ttl_seconds: int = 0

    def update_token_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        prompt_cost_per_1k: float = 0.0,
        completion_cost_per_1k: float = 0.0,
    ) -> None:
        """
        Update token usage metrics and calculate derived metrics.

        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            prompt_cost_per_1k: Cost per 1000 prompt tokens
            completion_cost_per_1k: Cost per 1000 completion tokens
        """
        # Update base token counts
        self.input_tokens = prompt_tokens
        self.output_tokens = completion_tokens

        # Calculate prompt processing and completion times
        prompt_time = (
            self.time_to_first_token
            if self.time_to_first_token > 0
            else self.total_time * 0.1
        )
        completion_time = (
            self.total_time - prompt_time
            if self.total_time > prompt_time
            else self.total_time * 0.9
        )

        # Update token usage metrics
        self.token_usage.calculate_metrics(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_time=self.total_time,
            prompt_time=prompt_time,
            completion_time=completion_time,
            prompt_cost_per_1k=prompt_cost_per_1k,
            completion_cost_per_1k=completion_cost_per_1k,
        )

        # Update base cost estimate
        self.estimated_cost = self.token_usage.total_cost
        self.currency = self.token_usage.currency

        # Calculate any other derived metrics
        self.calculate_derived_metrics()


@dataclass
class EnhancedPerformanceReport(ModelPerformanceReport):
    """
    Enhanced performance report with more detailed metrics.
    """

    # Token usage metrics
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    avg_prompt_tokens: float = 0.0
    avg_completion_tokens: float = 0.0
    avg_completion_to_prompt_ratio: float = 0.0

    # Cost metrics
    total_prompt_cost: float = 0.0
    total_completion_cost: float = 0.0
    avg_prompt_cost: float = 0.0
    avg_completion_cost: float = 0.0
    cost_per_1k_tokens: float = 0.0

    # Performance metrics
    avg_queue_time_ms: float = 0.0
    avg_prompt_processing_time_ms: float = 0.0
    avg_completion_time_ms: float = 0.0

    # Error rates
    error_rate: float = 0.0
    error_types: Dict[str, int] = field(default_factory=dict)

    # Cache metrics
    cache_hit_rate: float = 0.0

    # Rate limiting metrics
    rate_limit_rate: float = 0.0

    def calculate_from_metrics(self, metrics_data: List[Dict[str, Any]]) -> None:
        """
        Calculate enhanced report metrics from raw metrics data.

        Args:
            metrics_data: List of metrics dictionaries
        """
        if not metrics_data:
                    return # Initialize counters for additional metrics
        total_prompt_tokens = 0
        total_completion_tokens = 0
        prompt_costs = 0.0
        completion_costs = 0.0
        queue_times = []
        prompt_times = []
        completion_times = []
        completion_to_prompt_ratios = []
        error_count = 0
        error_types_count = {}
        cache_hit_count = 0
        rate_limit_count = 0

        # Process each metric
        for metric in metrics_data:
            # Extract token usage from metadata if available
            token_usage = None
            if "metadata" in metric and isinstance(metric["metadata"], dict):
                token_usage = metric["metadata"].get("token_usage", {})

            # Token counts
            prompt_tokens = token_usage.get("prompt_tokens", 0) if token_usage else 0
            completion_tokens = (
                token_usage.get("completion_tokens", 0) if token_usage else 0
            )

            if prompt_tokens == 0 and "input_tokens" in metric:
                prompt_tokens = metric["input_tokens"]

            if completion_tokens == 0 and "output_tokens" in metric:
                completion_tokens = metric["output_tokens"]

            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens

            # Cost metrics
            if token_usage:
                prompt_costs += token_usage.get("prompt_cost", 0.0)
                completion_costs += token_usage.get("completion_cost", 0.0)

                if prompt_tokens > 0 and completion_tokens > 0:
                    ratio = completion_tokens / prompt_tokens
                    completion_to_prompt_ratios.append(ratio)

            # Timing metrics
            if "queue_time_ms" in metric and metric["queue_time_ms"] > 0:
                queue_times.append(metric["queue_time_ms"])

            if (
                "prompt_processing_time_ms" in metric
                and metric["prompt_processing_time_ms"] > 0
            ):
                prompt_times.append(metric["prompt_processing_time_ms"])

            if "completion_time_ms" in metric and metric["completion_time_ms"] > 0:
                completion_times.append(metric["completion_time_ms"])

            # Error metrics
            if "error_occurred" in metric and metric["error_occurred"]:
                error_count += 1
                error_type = metric.get("error_type", "unknown")
                if error_type not in error_types_count:
                    error_types_count[error_type] = 0
                error_types_count[error_type] += 1

            # Cache metrics
            if "cache_hit" in metric and metric["cache_hit"]:
                cache_hit_count += 1

            # Rate limiting metrics
            if "rate_limited" in metric and metric["rate_limited"]:
                rate_limit_count += 1

        # Set token metrics
        self.total_prompt_tokens = total_prompt_tokens
        self.total_completion_tokens = total_completion_tokens

        if self.num_inferences > 0:
            self.avg_prompt_tokens = total_prompt_tokens / self.num_inferences
            self.avg_completion_tokens = total_completion_tokens / self.num_inferences

        if completion_to_prompt_ratios:
            self.avg_completion_to_prompt_ratio = statistics.mean(
                completion_to_prompt_ratios
            )

        # Set cost metrics
        self.total_prompt_cost = prompt_costs
        self.total_completion_cost = completion_costs

        if self.num_inferences > 0:
            self.avg_prompt_cost = prompt_costs / self.num_inferences
            self.avg_completion_cost = completion_costs / self.num_inferences

        total_tokens = total_prompt_tokens + total_completion_tokens
        if total_tokens > 0:
            self.cost_per_1k_tokens = (
                (prompt_costs + completion_costs) * 1000
            ) / total_tokens

        # Set timing metrics
        if queue_times:
            self.avg_queue_time_ms = statistics.mean(queue_times)

        if prompt_times:
            self.avg_prompt_processing_time_ms = statistics.mean(prompt_times)

        if completion_times:
            self.avg_completion_time_ms = statistics.mean(completion_times)

        # Set error metrics
        if self.num_inferences > 0:
            self.error_rate = error_count / self.num_inferences
        self.error_types = error_types_count

        # Set cache metrics
        if self.num_inferences > 0:
            self.cache_hit_rate = cache_hit_count / self.num_inferences

        # Set rate limiting metrics
        if self.num_inferences > 0:
            self.rate_limit_rate = rate_limit_count / self.num_inferences


class EnhancedPerformanceMonitor(PerformanceMonitor):
    """
    Enhanced performance monitoring with advanced metrics and token tracking.
    """

    def __init__(self, config=None, db_path: str = None):
        """
        Initialize the enhanced performance monitor.

        Args:
            config: Model configuration object or dict
            db_path: Path to the metrics database
        """
        super().__init__(config, db_path)
        self.model_cost_rates = {}  # To store cost rates for different models

    def set_model_cost_rates(
        self, model_id: str, prompt_cost_per_1k: float, completion_cost_per_1k: float
    ) -> None:
        """
        Set cost rates for a specific model.

        Args:
            model_id: ID of the model
            prompt_cost_per_1k: Cost per 1000 prompt tokens
            completion_cost_per_1k: Cost per 1000 completion tokens
        """
        self.model_cost_rates[model_id] = {
            "prompt_cost_per_1k": prompt_cost_per_1k,
            "completion_cost_per_1k": completion_cost_per_1k,
        }
        logger.info(
            f"Set cost rates for model {model_id}: prompt=${prompt_cost_per_1k}/1k, completion=${completion_cost_per_1k}/1k"
        )

    def get_model_cost_rates(self, model_id: str) -> Dict[str, float]:
        """
        Get cost rates for a specific model.

        Args:
            model_id: ID of the model

        Returns:
            Dict with prompt_cost_per_1k and completion_cost_per_1k
        """
                return self.model_cost_rates.get(
            model_id, {"prompt_cost_per_1k": 0.0, "completion_cost_per_1k": 0.0}
        )

    def track_enhanced_inference(
        self, model_id: str, batch_id: str = None
    ) -> "EnhancedInferenceTracker":
        """
        Create a new enhanced inference tracker.

        Args:
            model_id: ID of the model
            batch_id: Optional batch ID to group related inferences

        Returns:
            EnhancedInferenceTracker: A tracker object for monitoring the inference
        """
                return EnhancedInferenceTracker(self, model_id, batch_id)

    def generate_enhanced_report(
        self,
        model_id: str,
        model_name: str = None,
        time_range: Tuple[datetime, datetime] = None,
        batch_id: str = None,
        include_metrics: bool = False,
    ) -> EnhancedPerformanceReport:
        """
        Generate an enhanced performance report for a model.

        Args:
            model_id: ID of the model
            model_name: Optional name of the model (defaults to model_id)
            time_range: Optional time range to filter metrics (start_time, end_time)
            batch_id: Optional batch ID to filter metrics
            include_metrics: Whether to include raw metrics in the report

        Returns:
            EnhancedPerformanceReport: A report of the model's performance
        """
        # First generate the base report
        base_report = super().generate_report(
            model_id=model_id,
            model_name=model_name,
            time_range=time_range,
            batch_id=batch_id,
            include_metrics=True,  # We need the raw metrics
        )

        # Create and populate enhanced report
        enhanced_report = EnhancedPerformanceReport(**asdict(base_report))

        # Calculate enhanced metrics from raw data
        enhanced_report.calculate_from_metrics(base_report.raw_metrics)

        # Remove raw metrics if not requested
        if not include_metrics:
            enhanced_report.raw_metrics = []

                return enhanced_report

    def compare_models_enhanced(
        self,
        model_ids: List[str],
        model_names: List[str] = None,
        title: str = "Enhanced Model Comparison",
        time_range: Tuple[datetime, datetime] = None,
    ) -> ModelComparisonReport:
        """
        Compare performance across multiple models with enhanced metrics.

        Args:
            model_ids: List of model IDs to compare
            model_names: Optional list of model names
            title: Title for the comparison
            time_range: Optional time range to filter metrics

        Returns:
            ModelComparisonReport: A comparison of the models' performance
        """
        comparison = ModelComparisonReport(title=title)

        # Generate enhanced reports for each model
        model_names = model_names or model_ids
        if len(model_names) < len(model_ids):
            model_names = model_names + model_ids[len(model_names) :]

        metrics_to_compare = [
            "avg_inference_time",
            "median_inference_time",
            "min_inference_time",
            "max_inference_time",
            "avg_latency_ms",
            "avg_time_to_first_token",
            "avg_tokens_per_second",
            "avg_memory_usage_mb",
            "avg_cpu_percent",
            "avg_gpu_percent",
            "avg_prompt_tokens",
            "avg_completion_tokens",
            "avg_completion_to_prompt_ratio",
            "cost_per_1k_tokens",
            "avg_queue_time_ms",
            "error_rate",
            "cache_hit_rate",
        ]

        for idx, model_id in enumerate(model_ids):
            # Generate an enhanced report for this model
            model_name = model_names[idx] if idx < len(model_names) else model_id
            report = self.generate_enhanced_report(
                model_id=model_id, model_name=model_name, time_range=time_range
            )

            # Add to comparison metrics
            comparison.comparison_metrics[model_id] = {
                "model_name": model_name,
                "num_inferences": report.num_inferences,
            }

            # Add selected metrics
            for metric in metrics_to_compare:
                if hasattr(report, metric) and getattr(report, metric) > 0:
                    comparison.comparison_metrics[model_id][metric] = getattr(
                        report, metric
                    )

        # Calculate percent differences
        comparison.calculate_percent_differences(
            [
                "avg_inference_time",
                "avg_latency_ms",
                "avg_tokens_per_second",
                "cost_per_1k_tokens",
            ]
        )

                return comparison

    def save_enhanced_metrics(self, metrics: EnhancedInferenceMetrics) -> None:
        """
        Save enhanced metrics to the database.

        Args:
            metrics: The enhanced metrics to save
        """
        # First store the token usage in metadata
        if not hasattr(metrics, "metadata"):
            metrics.metadata = {}

        metrics.metadata["token_usage"] = asdict(metrics.token_usage)

        # Then save using the parent method
        super().save_metrics(metrics)

    def visualize_token_usage(
        self, model_id: str, days: int = 30, save_path: str = None
    ) -> List[str]:
        """
        Visualize token usage metrics.

        Args:
            model_id: ID of the model
            days: Number of days of data to include
            save_path: Directory to save visualizations in

        Returns:
            List of paths to generated visualization files
        """
        try:
as plt
 as np
 as pd
:
            logger.error(
                "Visualization requires matplotlib and pandas. Install with: pip install matplotlib pandas"
            )
                    return []

        # Get metrics
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        time_range = (start_time, end_time)

        metrics_data = self.metrics_db.get_metrics(
            model_id=model_id, time_range=time_range, limit=10000
        )

        if not metrics_data:
            logger.warning(
                f"No metrics found for model {model_id} in the last {days} days"
            )
                    return []

        # Extract token usage from metadata
        token_data = []
        for metric in metrics_data:
            if not isinstance(metric.get("metadata"), dict):
                continue

            token_usage = metric.get("metadata", {}).get("token_usage", {})
            if not token_usage:
                continue

            entry = {
                "timestamp": metric["timestamp"],
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
                "prompt_cost": token_usage.get("prompt_cost", 0.0),
                "completion_cost": token_usage.get("completion_cost", 0.0),
                "total_cost": token_usage.get("total_cost", 0.0),
            }
            token_data.append(entry)

        if not token_data:
            # Try to use input/output tokens if enhanced metrics not available
            for metric in metrics_data:
                entry = {
                    "timestamp": metric["timestamp"],
                    "prompt_tokens": metric.get("input_tokens", 0),
                    "completion_tokens": metric.get("output_tokens", 0),
                    "total_tokens": metric.get("input_tokens", 0)
                    + metric.get("output_tokens", 0),
                }
                token_data.append(entry)

        if not token_data:
            logger.warning(f"No token usage data found for model {model_id}")
                    return []

        # Convert to DataFrame
        df = pd.DataFrame(token_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

        # Create save directory if needed
        if save_path:
            os.makedirs(save_path, exist_ok=True)
        else:
            save_path = os.path.join(os.getcwd(), "model_performance_viz")
            os.makedirs(save_path, exist_ok=True)

        # Generate visualizations
        generated_files = []

        # 1. Token usage over time
        if "total_tokens" in df.columns and df["total_tokens"].max() > 0:
            try:
                plt.figure(figsize=(12, 8))

                # Create a daily aggregation
                df["date"] = df["timestamp"].dt.date
                daily_df = (
                    df.groupby("date")
                    .agg(
                        {
                            "prompt_tokens": "sum",
                            "completion_tokens": "sum",
                            "total_tokens": "sum",
                        }
                    )
                    .reset_index()
                )
                daily_df["date"] = pd.to_datetime(daily_df["date"])

                plt.bar(
                    daily_df["date"],
                    daily_df["prompt_tokens"],
                    label="Prompt Tokens",
                    alpha=0.7,
                )
                plt.bar(
                    daily_df["date"],
                    daily_df["completion_tokens"],
                    bottom=daily_df["prompt_tokens"],
                    label="Completion Tokens",
                    alpha=0.7,
                )

                plt.title(f"Daily Token Usage - Model {model_id}")
                plt.xlabel("Date")
                plt.ylabel("Tokens")
                plt.grid(True, alpha=0.3)
                plt.legend()

                # Format x-axis date labels
                date_format = DateFormatter("%Y-%m-%d")
                plt.gca().xaxis.set_major_formatter(date_format)
                plt.xticks(rotation=45)

                # Save figure
                filename = f"{model_id}_token_usage_{int(time.time())}.png"
                filepath = os.path.join(save_path, filename)
                plt.tight_layout()
                plt.savefig(filepath)
                plt.close()

                generated_files.append(filepath)

            except Exception as e:
                logger.error(f"Error generating token usage visualization: {e}")

        # 2. Cost visualization if available
        if "total_cost" in df.columns and df["total_cost"].max() > 0:
            try:
                plt.figure(figsize=(12, 8))

                # Create a daily aggregation
                df["date"] = df["timestamp"].dt.date
                daily_df = (
                    df.groupby("date")
                    .agg(
                        {
                            "prompt_cost": "sum",
                            "completion_cost": "sum",
                            "total_cost": "sum",
                        }
                    )
                    .reset_index()
                )
                daily_df["date"] = pd.to_datetime(daily_df["date"])

                plt.bar(
                    daily_df["date"],
                    daily_df["prompt_cost"],
                    label="Prompt Cost",
                    alpha=0.7,
                )
                plt.bar(
                    daily_df["date"],
                    daily_df["completion_cost"],
                    bottom=daily_df["prompt_cost"],
                    label="Completion Cost",
                    alpha=0.7,
                )

                plt.title(f"Daily Token Cost - Model {model_id}")
                plt.xlabel("Date")
                plt.ylabel("Cost (USD)")
                plt.grid(True, alpha=0.3)
                plt.legend()

                # Calculate total cost
                total_cost = daily_df["total_cost"].sum()
                plt.text(
                    0.02,
                    0.95,
                    f"Total Cost: ${total_cost:.2f}",
                    transform=plt.gca().transAxes,
                    bbox=dict(facecolor="white", alpha=0.8),
                )

                # Format x-axis date labels
                date_format = DateFormatter("%Y-%m-%d")
                plt.gca().xaxis.set_major_formatter(date_format)
                plt.xticks(rotation=45)

                # Save figure
                filename = f"{model_id}_token_cost_{int(time.time())}.png"
                filepath = os.path.join(save_path, filename)
                plt.tight_layout()
                plt.savefig(filepath)
                plt.close()

                generated_files.append(filepath)

            except Exception as e:
                logger.error(f"Error generating cost visualization: {e}")

                return generated_files


class EnhancedInferenceTracker:
    """
    Enhanced utility for tracking detailed performance metrics of model inferences.
    """

    def __init__(
        self,
        performance_monitor: EnhancedPerformanceMonitor,
        model_id: str,
        batch_id: Optional[str] = None,
    ):
        self.performance_monitor = performance_monitor
        self.model_id = model_id
        self.batch_id = batch_id or str(uuid.uuid4())
        self.metrics = EnhancedInferenceMetrics(
            model_id=model_id, batch_id=self.batch_id
        )
        self._has_started = False
        self._has_stopped = False
        self._queue_start_time = None

        # Get cost rates for the model
        cost_rates = performance_monitor.get_model_cost_rates(model_id)
        self.prompt_cost_per_1k = cost_rates.get("prompt_cost_per_1k", 0.0)
        self.completion_cost_per_1k = cost_rates.get("completion_cost_per_1k", 0.0)

    def track_queue_time(self, start_queue_time: Optional[float] = None) -> None:
        """
        Track the time spent in queue before processing.

        Args:
            start_queue_time: Optional start time for queue (defaults to current time)
        """
        self._queue_start_time = start_queue_time or time.time()

    def start(self, input_text: str = "", input_tokens: int = 0) -> None:
        """
        Start tracking an inference.

        Args:
            input_text: Input text for the inference
            input_tokens: Number of tokens in the input (calculated if not provided)
        """
        if self._has_started:
            logger.warning("Tracker has already been started")
                    return self._has_started = True
        now = time.time()
        self.metrics.start_time = now
        self.metrics.input_text = input_text
        self.metrics.input_tokens = input_tokens or self._estimate_tokens(input_text)

        # Calculate queue time if applicable
        if self._queue_start_time:
            self.metrics.queue_time_ms = (now - self._queue_start_time) * 1000

        # Capture initial memory usage
        self._capture_system_metrics()

    def record_first_token(self) -> None:
        """
        Record when the first token is generated.
        """
        if not self._has_started:
            logger.warning("Tracker hasn't been started")
                    return now = time.time()
        self.metrics.time_to_first_token = now - self.metrics.start_time
        self.metrics.latency_ms = self.metrics.time_to_first_token * 1000

        # Update prompt processing time
        self.metrics.prompt_processing_time_ms = self.metrics.latency_ms

    def record_cache_hit(self, cache_key: str, ttl_seconds: int = 0) -> None:
        """
        Record a cache hit.

        Args:
            cache_key: The cache key that was hit
            ttl_seconds: Time to live for the cache entry in seconds
        """
        self.metrics.cache_hit = True
        self.metrics.cache_key = cache_key
        self.metrics.cache_ttl_seconds = ttl_seconds

    def record_error(self, error_type: str, error_message: str) -> None:
        """
        Record an error during inference.

        Args:
            error_type: Type of error
            error_message: Error message
        """
        self.metrics.error_occurred = True
        self.metrics.error_type = error_type
        self.metrics.error_message = error_message

    def record_rate_limit(self, reason: str) -> None:
        """
        Record a rate limit event.

        Args:
            reason: Reason for rate limiting
        """
        self.metrics.rate_limited = True
        self.metrics.rate_limit_reason = reason

    def add_request_context(
        self,
        project_id: str = "",
        user_id: str = "",
        session_id: str = "",
        tags: List[str] = None,
    ) -> None:
        """
        Add request context information.

        Args:
            project_id: ID of the project
            user_id: ID of the user
            session_id: ID of the session
            tags: List of tags for the request
        """
        self.metrics.project_id = project_id
        self.metrics.user_id = user_id
        self.metrics.session_id = session_id
        self.metrics.request_tags = tags or []

    def add_system_context(
        self,
        deployment_env: str = "",
        api_version: str = "",
        client_info: Dict[str, Any] = None,
    ) -> None:
        """
        Add system context information.

        Args:
            deployment_env: Deployment environment
            api_version: API version
            client_info: Client information
        """
        self.metrics.deployment_env = deployment_env
        self.metrics.api_version = api_version
        self.metrics.client_info = client_info or {}

    def stop(
        self, output_text: str = "", output_tokens: int = 0
    ) -> EnhancedInferenceMetrics:
        """
        Stop tracking and save the metrics.

        Args:
            output_text: Output text from the inference
            output_tokens: Number of tokens in the output (calculated if not provided)

        Returns:
            EnhancedInferenceMetrics: The collected metrics
        """
        if not self._has_started:
            logger.warning("Tracker hasn't been started")
                    return self.metrics

        if self._has_stopped:
            logger.warning("Tracker has already been stopped")
                    return self.metrics

        self._has_stopped = True
        now = time.time()
        self.metrics.end_time = now
        self.metrics.total_time = now - self.metrics.start_time

        # Record output information
        self.metrics.output_text = output_text
        self.metrics.output_tokens = output_tokens or self._estimate_tokens(output_text)

        # Calculate completion time
        if self.metrics.time_to_first_token > 0:
            completion_time = self.metrics.total_time - self.metrics.time_to_first_token
            self.metrics.completion_time_ms = completion_time * 1000

        # Capture final memory and system metrics
        self._capture_system_metrics()

        # Update token usage metrics
        self.metrics.update_token_usage(
            prompt_tokens=self.metrics.input_tokens,
            completion_tokens=self.metrics.output_tokens,
            prompt_cost_per_1k=self.prompt_cost_per_1k,
            completion_cost_per_1k=self.completion_cost_per_1k,
        )

        # Save the metrics
        try:
            self.performance_monitor.save_enhanced_metrics(self.metrics)
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")


            traceback.print_exc()

                return self.metrics

    def _capture_system_metrics(self) -> None:
        """
        Capture system metrics like memory usage and CPU/GPU usage.
        """
        # Use the same implementation as the base class
        try:


            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            self.metrics.memory_usage_mb = memory_info.rss / (
                1024 * 1024
            )  # Convert bytes to MB
            self.metrics.cpu_percent = process.cpu_percent()
        except ImportError:
            # psutil not available, use generic memory info
            try:


                self.metrics.memory_usage_mb = (
                    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
                )  # kB to MB
            except ImportError:
                pass
        except Exception as e:
            logger.debug(f"Error capturing system metrics: {e}")

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in the text.

        This is a very simple estimation - in a real system, you'd use
        the actual tokenizer from the model.
        """
        if not text:
                    return 0
        # Simple estimate: ~4 characters per token for English text
                return max(1, len(text) // 4))
"""
Model performance monitoring and benchmarking.

This module provides tools for tracking, analyzing, and reporting on model
performance metrics across various dimensions including latency, throughput,
memory usage, and quality metrics.
"""

import csv
import json
import logging
import os
import sqlite3
import statistics
import threading
import time
import traceback
import uuid
import warnings
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DB_SCHEMA_VERSION = "1.0"
DEFAULT_DB_PATH = os.path.expanduser("~/.paissive_income/performance_metrics.db")
DEFAULT_METRICS_RETENTION_DAYS = 180  # Keep metrics for 6 months by default


@dataclass
class InferenceMetrics:
    """
    Holds metrics for a single model inference.
    """

    # Identifiers
    model_id: str
    inference_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    batch_id: Optional[str] = None

    # Input/Output metrics
    input_tokens: int = 0
    output_tokens: int = 0

    # Time metrics
    start_time: float = 0.0
    end_time: float = 0.0
    total_time: float = 0.0  # Total inference time in seconds
    latency_ms: float = 0.0  # Time to first token in milliseconds
    time_to_first_token: float = 0.0  # Time to first token in seconds

    # Derived metrics
    tokens_per_second: float = 0.0  # Total tokens / total time

    # Memory metrics
    memory_usage_mb: float = 0.0  # Memory used during inference in MB
    peak_cpu_memory_mb: float = 0.0  # Peak CPU memory used
    peak_gpu_memory_mb: float = 0.0  # Peak GPU memory used

    # System metrics
    cpu_percent: float = 0.0
    gpu_percent: float = 0.0

    # Quality metrics
    perplexity: float = 0.0
    bleu_score: float = 0.0
    rouge_score: float = 0.0

    # Cost metrics
    estimated_cost: float = 0.0
    currency: str = "USD"

    # Context
    input_text: str = ""
    output_text: str = ""
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary, excluding input/output text by default.
        """
        result = asdict(self)
        # Remove large fields for storage
        result.pop("input_text", None)
        result.pop("output_text", None)
        return result

    def calculate_derived_metrics(self) -> None:
        """
        Calculate derived metrics based on raw measurements.
        """
        # Calculate total time if not already set
        if self.total_time == 0.0 and self.start_time > 0 and self.end_time > 0:
            self.total_time = self.end_time - self.start_time

        # Calculate tokens per second
        total_tokens = self.input_tokens + self.output_tokens
        if total_tokens > 0 and self.total_time > 0:
            self.tokens_per_second = total_tokens / self.total_time

        # Convert time_to_first_token to latency_ms if not set
        if self.latency_ms == 0.0 and self.time_to_first_token > 0:
            self.latency_ms = self.time_to_first_token * 1000


@dataclass
class ModelPerformanceReport:
    """
    Performance report for a model across multiple inferences.
    """

    model_id: str
    model_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Query parameters
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    # Summary count
    num_inferences: int = 0

    # Time metrics
    avg_inference_time: float = 0.0
    min_inference_time: float = 0.0
    max_inference_time: float = 0.0
    median_inference_time: float = 0.0
    stddev_inference_time: float = 0.0
    p90_inference_time: float = 0.0
    p95_inference_time: float = 0.0
    p99_inference_time: float = 0.0
    avg_latency_ms: float = 0.0
    avg_time_to_first_token: float = 0.0

    # Token metrics
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    avg_input_tokens: float = 0.0
    avg_output_tokens: float = 0.0
    avg_tokens_per_second: float = 0.0

    # Memory metrics
    avg_memory_usage_mb: float = 0.0
    max_memory_usage_mb: float = 0.0
    avg_peak_cpu_memory_mb: float = 0.0
    avg_peak_gpu_memory_mb: float = 0.0

    # System metrics
    avg_cpu_percent: float = 0.0
    avg_gpu_percent: float = 0.0

    # Quality metrics
    avg_perplexity: float = 0.0
    avg_bleu_score: float = 0.0
    avg_rouge_score: float = 0.0

    # Cost metrics
    total_estimated_cost: float = 0.0
    avg_cost_per_inference: float = 0.0
    currency: str = "USD"

    # Raw metrics for further analysis
    raw_metrics: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        """
        result = asdict(self)
        # Remove raw metrics
        result.pop("raw_metrics", None)
        return result


@dataclass
class ModelComparisonReport:
    """
    Report comparing the performance of multiple models.
    """

    title: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    comparison_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        """
        return asdict(self)

    def calculate_percent_differences(self, key_metrics: List[str]) -> None:
        """
        Calculate percent differences between models for key metrics.

        For each metric, find the best value across all models and calculate
        the percent difference for each model relative to the best.
        """
        for metric in key_metrics:
            # Determine if lower is better (time metrics) or higher is better (throughput)
            lower_is_better = (
                "time" in metric or "latency" in metric or "memory" in metric
            )

            # Find the best value
            values = []
            for model_key in self.comparison_metrics:
                if metric in self.comparison_metrics[model_key]:
                    values.append(self.comparison_metrics[model_key][metric])

            if not values:
                continue

            best_value = min(values) if lower_is_better else max(values)
            if best_value == 0:
                continue

            # Calculate percent differences
            for model_key in self.comparison_metrics:
                if metric in self.comparison_metrics[model_key]:
                    current_value = self.comparison_metrics[model_key][metric]
                    if current_value == 0:
                        continue

                    # Calculate percent difference
                    if lower_is_better:
                        # (current - best) / best * 100
                        # Positive: current is worse (higher)
                        # Negative: current is better (lower)
                        percent_diff = (current_value - best_value) / best_value * 100
                    else:
                        # (best - current) / best * 100
                        # Positive: current is worse (lower)
                        # Negative: current is better (higher)
                        percent_diff = (best_value - current_value) / best_value * 100

                    self.comparison_metrics[model_key][
                        f"{metric}_percent_diff"
                    ] = percent_diff


class AlertConfig:
    """
    Configuration for performance metric alerts.
    """

    def __init__(
        self,
        model_id: str,
        metric_name: str,
        threshold_value: float,
        is_upper_bound: bool = True,
        cooldown_minutes: int = 60,
        notification_channels: List[str] = None,
    ):
        self.model_id = model_id
        self.metric_name = metric_name
        self.threshold_value = threshold_value
        self.is_upper_bound = is_upper_bound  # True: alert if value > threshold
        self.cooldown_minutes = cooldown_minutes
        self.notification_channels = notification_channels or ["log"]
        self.last_triggered = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "model_id": self.model_id,
            "metric_name": self.metric_name,
            "threshold_value": self.threshold_value,
            "is_upper_bound": self.is_upper_bound,
            "cooldown_minutes": self.cooldown_minutes,
            "notification_channels": self.notification_channels,
            "last_triggered": (
                self.last_triggered.isoformat() if self.last_triggered else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertConfig":
        """Create from dictionary."""
        alert = cls(
            model_id=data["model_id"],
            metric_name=data["metric_name"],
            threshold_value=data["threshold_value"],
            is_upper_bound=data.get("is_upper_bound", True),
            cooldown_minutes=data.get("cooldown_minutes", 60),
            notification_channels=data.get("notification_channels", ["log"]),
        )
        if data.get("last_triggered"):
            alert.last_triggered = datetime.fromisoformat(data["last_triggered"])
        return alert

    def check_alert(self, metric_value: float) -> bool:
        """
        Check if the metric value triggers an alert.

        Returns:
            bool: True if alert should be triggered
        """
        # Check if value triggers alert
        if self.is_upper_bound and metric_value <= self.threshold_value:
            return False
        if not self.is_upper_bound and metric_value >= self.threshold_value:
            return False

        # Check cooldown period
        if self.last_triggered:
            now = datetime.now()
            cooldown = timedelta(minutes=self.cooldown_minutes)
            if now - self.last_triggered < cooldown:
                return False

        return True

    def trigger(self) -> None:
        """Mark this alert as triggered."""
        self.last_triggered = datetime.now()


class InferenceTracker:
    """
    A utility for tracking performance metrics of model inferences.
    """

    def __init__(
        self,
        performance_monitor: "PerformanceMonitor",
        model_id: str,
        batch_id: Optional[str] = None,
    ):
        self.performance_monitor = performance_monitor
        self.model_id = model_id
        self.batch_id = batch_id or str(uuid.uuid4())
        self.metrics = InferenceMetrics(model_id=model_id, batch_id=self.batch_id)
        self._has_started = False
        self._has_stopped = False

    def start(self, input_text: str = "", input_tokens: int = 0) -> None:
        """
        Start tracking an inference.
        """
        if self._has_started:
            logger.warning("Tracker has already been started")
            return

        self._has_started = True
        self.metrics.start_time = time.time()
        self.metrics.input_text = input_text
        self.metrics.input_tokens = input_tokens or self._estimate_tokens(input_text)

        # Capture initial memory usage
        self._capture_system_metrics()

    def record_first_token(self) -> None:
        """
        Record when the first token is generated.
        """
        if not self._has_started:
            logger.warning("Tracker hasn't been started")
            return

        now = time.time()
        self.metrics.time_to_first_token = now - self.metrics.start_time
        self.metrics.latency_ms = self.metrics.time_to_first_token * 1000

    def stop(self, output_text: str = "", output_tokens: int = 0) -> InferenceMetrics:
        """
        Stop tracking and save the metrics.
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

        # Capture final memory and system metrics
        self._capture_system_metrics()

        # Calculate derived metrics
        self.metrics.calculate_derived_metrics()

        # Save the metrics
        try:
            self.performance_monitor.save_metrics(self.metrics)
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            traceback.print_exc()

        return self.metrics

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the metrics.
        """
        self.metrics.metadata[key] = value

    def _capture_system_metrics(self) -> None:
        """
        Capture system metrics like memory usage and CPU/GPU usage.
        """
        # Measure memory usage - we'll use a very simple approach here
        # In a real implementation, this would use process-specific metrics
        try:
            import psutil

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            self.metrics.memory_usage_mb = memory_info.rss / (
                1024 * 1024
            )  # Convert bytes to MB
            self.metrics.cpu_percent = process.cpu_percent()
        except ImportError:
            # psutil not available, use generic memory info
            import resource

            self.metrics.memory_usage_mb = (
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            )  # kB to MB
        except Exception as e:
            logger.debug(f"Error capturing system metrics: {e}")

        # GPU metrics - would typically use NVIDIA SMI or equivalent
        try:
            # This is a placeholder - real implementation would use
            # libraries like pynvml for NVIDIA GPUs
            pass
        except Exception:
            pass

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in the text.

        This is a very simple estimation - in a real system, you'd use
        the actual tokenizer from the model.
        """
        if not text:
            return 0
        # Simple estimate: ~4 characters per token for English text
        return max(1, len(text) // 4)


class MetricsDatabase:
    """
    Manages storage and retrieval of performance metrics in SQLite.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize the metrics database.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self._ensure_db_dir()
        self._connect()
        self._init_schema()

    def _ensure_db_dir(self) -> None:
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def _connect(self) -> None:
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def _init_schema(self) -> None:
        """Initialize the database schema if needed."""
        cursor = self.conn.cursor()

        # Check if the schema version table exists
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='schema_version'
        """
        )

        if not cursor.fetchone():
            # Create schema version table
            cursor.execute(
                """
                CREATE TABLE schema_version (
                    version TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                "INSERT INTO schema_version (version) VALUES (?)", (DB_SCHEMA_VERSION,)
            )

            # Create tables
            cursor.execute(
                """
                CREATE TABLE inference_metrics (
                    id TEXT PRIMARY KEY,
                    model_id TEXT NOT NULL,
                    batch_id TEXT,
                    timestamp TEXT NOT NULL,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    total_time REAL DEFAULT 0,
                    latency_ms REAL DEFAULT 0,
                    time_to_first_token REAL DEFAULT 0,
                    tokens_per_second REAL DEFAULT 0,
                    memory_usage_mb REAL DEFAULT 0,
                    peak_cpu_memory_mb REAL DEFAULT 0,
                    peak_gpu_memory_mb REAL DEFAULT 0,
                    cpu_percent REAL DEFAULT 0,
                    gpu_percent REAL DEFAULT 0,
                    perplexity REAL DEFAULT 0,
                    bleu_score REAL DEFAULT 0,
                    rouge_score REAL DEFAULT 0,
                    estimated_cost REAL DEFAULT 0,
                    currency TEXT DEFAULT 'USD',
                    request_id TEXT,
                    metadata TEXT
                )
            """
            )

            # Create indexes
            cursor.execute(
                "CREATE INDEX idx_inference_model_id ON inference_metrics(model_id)"
            )
            cursor.execute(
                "CREATE INDEX idx_inference_timestamp ON inference_metrics(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX idx_inference_batch_id ON inference_metrics(batch_id)"
            )

            # Create alerts table
            cursor.execute(
                """
                CREATE TABLE alert_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    threshold_value REAL NOT NULL,
                    is_upper_bound INTEGER DEFAULT 1,
                    cooldown_minutes INTEGER DEFAULT 60,
                    notification_channels TEXT DEFAULT 'log',
                    last_triggered TEXT,
                    UNIQUE(model_id, metric_name)
                )
            """
            )

            # Create alert history table
            cursor.execute(
                """
                CREATE TABLE alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    threshold_value REAL NOT NULL,
                    actual_value REAL NOT NULL,
                    triggered_at TEXT NOT NULL,
                    message TEXT
                )
            """
            )

            self.conn.commit()

    def save_metrics(self, metrics: InferenceMetrics) -> None:
        """
        Save inference metrics to the database.

        Args:
            metrics: The metrics to save
        """
        cursor = self.conn.cursor()

        # Convert metadata dict to JSON string
        metadata_json = json.dumps(metrics.metadata) if metrics.metadata else "{}"

        # Insert the metrics
        cursor.execute(
            """
            INSERT OR REPLACE INTO inference_metrics (
                id, model_id, batch_id, timestamp,
                input_tokens, output_tokens,
                total_time, latency_ms, time_to_first_token,
                tokens_per_second,
                memory_usage_mb, peak_cpu_memory_mb, peak_gpu_memory_mb,
                cpu_percent, gpu_percent,
                perplexity, bleu_score, rouge_score,
                estimated_cost, currency,
                request_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metrics.inference_id,
                metrics.model_id,
                metrics.batch_id,
                metrics.timestamp,
                metrics.input_tokens,
                metrics.output_tokens,
                metrics.total_time,
                metrics.latency_ms,
                metrics.time_to_first_token,
                metrics.tokens_per_second,
                metrics.memory_usage_mb,
                metrics.peak_cpu_memory_mb,
                metrics.peak_gpu_memory_mb,
                metrics.cpu_percent,
                metrics.gpu_percent,
                metrics.perplexity,
                metrics.bleu_score,
                metrics.rouge_score,
                metrics.estimated_cost,
                metrics.currency,
                metrics.request_id,
                metadata_json,
            ),
        )

        self.conn.commit()

    def get_metrics(
        self,
        model_id: str = None,
        batch_id: str = None,
        time_range: Tuple[datetime, datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Get metrics from the database.

        Args:
            model_id: Filter by model ID
            batch_id: Filter by batch ID
            time_range: Filter by time range (start_time, end_time)
            limit: Maximum number of records to return

        Returns:
            List of metrics dictionaries
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM inference_metrics"
        params = []
        where_clauses = []

        if model_id:
            where_clauses.append("model_id = ?")
            params.append(model_id)

        if batch_id:
            where_clauses.append("batch_id = ?")
            params.append(batch_id)

        if time_range:
            start_time, end_time = time_range
            where_clauses.append("timestamp >= ?")
            params.append(start_time.isoformat())
            where_clauses.append("timestamp <= ?")
            params.append(end_time.isoformat())

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        results = []

        for row in cursor.fetchall():
            metric = dict(row)
            # Parse metadata
            if "metadata" in metric and metric["metadata"]:
                try:
                    metric["metadata"] = json.loads(metric["metadata"])
                except:
                    metric["metadata"] = {}

            results.append(metric)

        return results

    def save_alert_config(self, alert_config: AlertConfig) -> None:
        """
        Save an alert configuration to the database.

        Args:
            alert_config: The alert configuration to save
        """
        cursor = self.conn.cursor()

        # Convert notification channels to JSON string
        notification_channels = json.dumps(alert_config.notification_channels)

        # Insert or update
        cursor.execute(
            """
            INSERT OR REPLACE INTO alert_configs (
                model_id, metric_name, threshold_value, 
                is_upper_bound, cooldown_minutes, notification_channels, 
                last_triggered
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                alert_config.model_id,
                alert_config.metric_name,
                alert_config.threshold_value,
                1 if alert_config.is_upper_bound else 0,
                alert_config.cooldown_minutes,
                notification_channels,
                (
                    alert_config.last_triggered.isoformat()
                    if alert_config.last_triggered
                    else None
                ),
            ),
        )

        self.conn.commit()

    def get_alert_configs(self, model_id: str = None) -> List[AlertConfig]:
        """
        Get alert configurations from the database.

        Args:
            model_id: Filter by model ID

        Returns:
            List of AlertConfig objects
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM alert_configs"
        params = []

        if model_id:
            query += " WHERE model_id = ?"
            params.append(model_id)

        cursor.execute(query, params)
        results = []

        for row in cursor.fetchall():
            # Convert row to dict
            data = dict(row)

            # Parse notification channels
            try:
                notification_channels = json.loads(data["notification_channels"])
            except:
                notification_channels = ["log"]

            # Create AlertConfig
            alert_config = AlertConfig(
                model_id=data["model_id"],
                metric_name=data["metric_name"],
                threshold_value=data["threshold_value"],
                is_upper_bound=bool(data["is_upper_bound"]),
                cooldown_minutes=data["cooldown_minutes"],
                notification_channels=notification_channels,
            )

            # Set last_triggered
            if data["last_triggered"]:
                alert_config.last_triggered = datetime.fromisoformat(
                    data["last_triggered"]
                )

            results.append(alert_config)

        return results

    def save_alert_history(
        self,
        model_id: str,
        metric_name: str,
        threshold_value: float,
        actual_value: float,
        message: str = None,
    ) -> None:
        """
        Save an alert event to the alert history.

        Args:
            model_id: The model ID
            metric_name: The metric name
            threshold_value: The threshold value
            actual_value: The actual value that triggered the alert
            message: Optional message describing the alert
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO alert_history (
                model_id, metric_name, threshold_value,
                actual_value, triggered_at, message
            ) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                model_id,
                metric_name,
                threshold_value,
                actual_value,
                datetime.now().isoformat(),
                message,
            ),
        )

        self.conn.commit()

    def get_alert_history(
        self, model_id: str = None, days: int = 7, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get alert history from the database.

        Args:
            model_id: Filter by model ID
            days: Number of days of history to retrieve
            limit: Maximum number of records to return

        Returns:
            List of alert history dictionaries
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM alert_history"
        params = []
        where_clauses = []

        if model_id:
            where_clauses.append("model_id = ?")
            params.append(model_id)

        if days > 0:
            start_time = datetime.now() - timedelta(days=days)
            where_clauses.append("triggered_at >= ?")
            params.append(start_time.isoformat())

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY triggered_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def cleanup_old_metrics(self, days: int = DEFAULT_METRICS_RETENTION_DAYS) -> int:
        """
        Remove metrics older than the specified number of days.

        Args:
            days: Number of days to keep

        Returns:
            Number of records deleted
        """
        if days <= 0:
            return 0

        cursor = self.conn.cursor()
        threshold_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute(
            "DELETE FROM inference_metrics WHERE timestamp < ?", (threshold_date,)
        )
        count = cursor.rowcount
        self.conn.commit()

        return count

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self, "conn"):
            self.conn.close()


class PerformanceMonitor:
    """Monitors model performance metrics."""

    def __init__(
        self,
        db_path: str,
        notification_channels: Optional[List[str]] = None,
        logging_level: int = logging.INFO,
    ) -> None:
        self.db_path = db_path
        self._notification_channels: List[str] = notification_channels or []
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._metrics_db: MetricsDatabase = MetricsDatabase(db_path)

        # Set up logging
        logging.basicConfig(level=logging_level)

    def track_inference(
        self,
        model_id: str,
        batch_id: Optional[str] = None,
        request_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        client_info: Optional[Dict[str, Any]] = None,
    ) -> InferenceTracker:
        """Create a tracker for monitoring a model inference."""
        tracker = InferenceTracker(
            performance_monitor=self, model_id=model_id, batch_id=batch_id
        )
        if request_id:
            tracker.metrics.request_id = request_id
        if tags:
            tracker.metrics.metadata["tags"] = tags
        if client_info:
            tracker.metrics.metadata["client_info"] = client_info
        return tracker

    def save_metrics(self, metrics: InferenceMetrics) -> None:
        """Save inference metrics to the database."""
        self._metrics_db.save_metrics(metrics)

    def get_metrics(
        self,
        model_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get metrics from the database."""
        return self._metrics_db.get_metrics(
            model_id=model_id, batch_id=batch_id, time_range=time_range, limit=limit
        )

    def set_alert_threshold(
        self,
        model_id: str,
        metric_name: str,
        threshold_value: float,
        is_upper_bound: bool = True,
        cooldown_minutes: int = 60,
        notification_channels: Optional[List[str]] = None,
    ) -> None:
        """Set an alert threshold for a metric."""
        alert_config = AlertConfig(
            model_id=model_id,
            metric_name=metric_name,
            threshold_value=threshold_value,
            is_upper_bound=is_upper_bound,
            cooldown_minutes=cooldown_minutes,
            notification_channels=notification_channels or self._notification_channels,
        )
        self._metrics_db.save_alert_config(alert_config)

    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        self._start_time = datetime.now()
        self.logger.info("Started performance monitoring")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self._end_time = datetime.now()
        self.logger.info("Stopped performance monitoring")

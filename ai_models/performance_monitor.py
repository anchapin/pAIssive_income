"""
Model performance monitoring and benchmarking.

This module provides tools for tracking, analyzing, and reporting on model
performance metrics across various dimensions including latency, throughput,
memory usage, and quality metrics.
"""

import os
import csv
import json
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
import statistics
import threading
import sqlite3
import uuid

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

    model_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    batch_id: Optional[str] = None
    inference_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Time metrics
    total_time: float = 0.0  # Total inference time in seconds
    latency_ms: float = 0.0  # Latency in milliseconds
    time_to_first_token: float = 0.0  # Time until first token generated
    start_time: float = 0.0  # Start time in seconds since epoch
    end_time: float = 0.0  # End time in seconds since epoch

    # Token metrics
    input_tokens: int = 0
    output_tokens: int = 0
    tokens_per_second: float = 0.0
    input_text: str = ""
    output_text: str = ""

    # Memory metrics
    memory_usage_mb: float = 0.0
    peak_cpu_memory_mb: float = 0.0
    peak_gpu_memory_mb: float = 0.0

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

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Request info
    request_id: Optional[str] = None

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
    model_name: str = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if self.model_name is None:
            self.model_name = self.model_id

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
        monitor: "PerformanceMonitor",
        model_id: str,
        batch_id: Optional[str] = None,
    ):
        self.monitor = monitor
        self.model_id = model_id
        self.batch_id = batch_id or str(uuid.uuid4())
        self.metrics = InferenceMetrics(model_id=model_id, batch_id=self.batch_id)
        self._has_started = False
        self._has_stopped = False
        self.start_time = None
        self.end_time = None
        self.input_tokens = 0
        self.output_tokens = 0
        self.memory_usage_start = 0
        self.memory_usage_end = 0

    def start(self, input_text: str = "", input_tokens: int = 0) -> None:
        """
        Start tracking an inference.
        """
        if self._has_started:
            logger.warning("Tracker has already been started")
            return

        self._has_started = True
        self.start_time = time.time()
        self.metrics.start_time = self.start_time
        self.metrics.input_text = input_text
        self.input_tokens = input_tokens or self._estimate_tokens(input_text)
        self.metrics.input_tokens = self.input_tokens

        # Capture initial memory usage
        self._capture_system_metrics(is_start=True)

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
        self.end_time = time.time()
        self.metrics.end_time = self.end_time
        self.metrics.total_time = self.end_time - self.start_time

        # Record output information
        self.metrics.output_text = output_text
        self.output_tokens = output_tokens or self._estimate_tokens(output_text)
        self.metrics.output_tokens = self.output_tokens

        # Capture final memory and system metrics
        self._capture_system_metrics(is_start=False)

        # Calculate derived metrics
        self.metrics.calculate_derived_metrics()

        # Set latency if not already set
        if self.metrics.latency_ms == 0:
            self.metrics.latency_ms = self.metrics.total_time * 1000

        # Save the metrics
        try:
            self.monitor.save_metrics(self.metrics)
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            traceback.print_exc()

        return self.metrics

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the metrics.
        """
        self.metrics.metadata[key] = value

    def _capture_system_metrics(self, is_start: bool = True) -> None:
        """
        Capture system metrics like memory usage and CPU/GPU usage.

        Args:
            is_start: Whether this is the start of tracking (True) or end (False)
        """
        # Measure memory usage - we'll use a very simple approach here
        # In a real implementation, this would use process-specific metrics
        try:
            import psutil

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)  # Convert bytes to MB

            if is_start:
                self.memory_usage_start = memory_mb
                self.metrics.memory_usage_mb = memory_mb
            else:
                self.memory_usage_end = memory_mb
                # Update the metrics with the higher value
                self.metrics.memory_usage_mb = max(self.memory_usage_start, memory_mb)

            self.metrics.cpu_percent = process.cpu_percent()
        except ImportError:
            # psutil not available, use generic memory info
            import resource

            memory_mb = (
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            )  # kB to MB

            if is_start:
                self.memory_usage_start = memory_mb
                self.metrics.memory_usage_mb = memory_mb
            else:
                self.memory_usage_end = memory_mb
                # Update the metrics with the higher value
                self.metrics.memory_usage_mb = max(self.memory_usage_start, memory_mb)
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
                except Exception:
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
            except Exception:
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
    def __init__(self, config=None, db_path: str = None):
        """
        Initialize the performance monitor.

        Args:
            config: Model configuration object or dict
            db_path: Path to the metrics database (default: ~/.paissive_income/performance_metrics.db)
        """
        self.config = config or {}
        self.metrics_db = MetricsDatabase(db_path)
        self.metrics_history = {}  # Dict to store metrics by model_id
        self.report_cache = {}  # Cache for generated reports
        self._lock = threading.Lock()
        self._alert_handlers = {"log": self._log_alert}

    def track_inference(
        self,
        model=None,
        model_id: str = None,
        batch_id: str = None,
        input_text: str = None,
        output_text: str = None,
    ) -> InferenceMetrics:
        """
        Track a model inference and return metrics.

        Args:
            model: The model object (optional)
            model_id: ID of the model (required if model not provided)
            batch_id: Optional batch ID to group related inferences
            input_text: Optional input text for the inference
            output_text: Optional output text from the inference

        Returns:
            InferenceMetrics: The metrics for the inference
        """
        if model is None and model_id is None:
            raise ValueError("Either model or model_id must be provided")

        model_id = model_id or model.id
        tracker = InferenceTracker(self, model_id, batch_id)

        # Start tracking
        start_time = time.time()
        tracker.start(input_text=input_text)

        # If output text is provided, stop tracking and return metrics
        if output_text:
            # Add a small delay to ensure latency is measurable
            time.sleep(0.01)
            metrics = tracker.stop(output_text=output_text)

            # Ensure latency is set
            if metrics.latency_ms <= 0:
                end_time = time.time()
                metrics.latency_ms = (end_time - start_time) * 1000

            return metrics

        # If no output text, create and return metrics directly
        end_time = time.time()
        metrics = InferenceMetrics(
            model_id=model_id,
            batch_id=batch_id,
            input_text=input_text,
            output_text="",
            input_tokens=tracker.input_tokens,
            output_tokens=0,
            start_time=start_time,
            end_time=end_time,
            total_time=end_time - start_time,
            latency_ms=(end_time - start_time) * 1000,  # Convert to milliseconds
        )

        # Save to history
        if model_id not in self.metrics_history:
            self.metrics_history[model_id] = []
        self.metrics_history[model_id].append(metrics)

        return metrics

    def save_metrics(self, metrics: InferenceMetrics) -> None:
        """
        Save metrics to the database and update metrics history.

        Args:
            metrics: The metrics to save
        """
        with self._lock:
            # Save to database
            self.metrics_db.save_metrics(metrics)

            # Update metrics history
            if metrics.model_id not in self.metrics_history:
                self.metrics_history[metrics.model_id] = []
            self.metrics_history[metrics.model_id].append(metrics)

        # Check for alerts
        self._check_alerts(metrics)

    def _check_alerts(self, metrics: InferenceMetrics) -> None:
        """
        Check if any metrics have triggered alerts.

        Args:
            metrics: The metrics to check
        """
        alert_configs = self.metrics_db.get_alert_configs(model_id=metrics.model_id)

        for alert_config in alert_configs:
            # Get the metric value
            metric_value = getattr(metrics, alert_config.metric_name, None)

            if metric_value is None:
                continue

            # Check if alert is triggered
            if alert_config.check_alert(metric_value):
                # Log the alert
                alert_msg = (
                    f"Alert triggered for {metrics.model_id}: "
                    f"{alert_config.metric_name} = {metric_value} "
                    f"{'>' if alert_config.is_upper_bound else '<'} {alert_config.threshold_value}"
                )

                # Save to history
                self.metrics_db.save_alert_history(
                    model_id=metrics.model_id,
                    metric_name=alert_config.metric_name,
                    threshold_value=alert_config.threshold_value,
                    actual_value=metric_value,
                    message=alert_msg,
                )

                # Mark as triggered
                alert_config.trigger()
                self.metrics_db.save_alert_config(alert_config)

                # Send notifications via registered handlers
                for channel in alert_config.notification_channels:
                    handler = self._alert_handlers.get(channel)
                    if handler:
                        handler(alert_msg, alert_config, metric_value)

    def _log_alert(self, message: str, alert_config: AlertConfig, value: float) -> None:
        """
        Log an alert to the logger.

        Args:
            message: The alert message
            alert_config: The alert configuration
            value: The value that triggered the alert
        """
        logger.warning(message)

    def register_alert_handler(self, channel: str, handler_func) -> None:
        """
        Register a handler function for an alert notification channel.

        Args:
            channel: The channel name
            handler_func: Function to call when an alert is triggered.
                        Should accept (message, alert_config, value)
        """
        self._alert_handlers[channel] = handler_func

    def generate_report(
        self,
        model_id: str,
        model_name: str = None,
        time_range: Tuple[datetime, datetime] = None,
        batch_id: str = None,
        include_metrics: bool = False,
    ) -> ModelPerformanceReport:
        """
        Generate a performance report for a model.

        Args:
            model_id: ID of the model
            model_name: Optional name of the model (defaults to model_id)
            time_range: Optional time range to filter metrics (start_time, end_time)
            batch_id: Optional batch ID to filter metrics
            include_metrics: Whether to include raw metrics in the report

        Returns:
            ModelPerformanceReport: A report of the model's performance
        """
        # First check if we have metrics in memory
        if model_id in self.metrics_history and self.metrics_history[model_id]:
            metrics_list = self.metrics_history[model_id]
            # Convert metrics to dictionaries
            metrics_data = [metric.to_dict() for metric in metrics_list]
        else:
            # Fall back to database if no in-memory metrics
            metrics_data = self.metrics_db.get_metrics(
                model_id=model_id, time_range=time_range, batch_id=batch_id, limit=10000
            )

        if not metrics_data:
            logger.warning(f"No metrics found for model {model_id}")
            return ModelPerformanceReport(
                model_id=model_id, model_name=model_name or model_id
            )

        # Create report
        report = ModelPerformanceReport(
            model_id=model_id, model_name=model_name or model_id
        )

        # Set time range
        if time_range:
            report.start_time = time_range[0].isoformat()
            report.end_time = time_range[1].isoformat()
        else:
            # Find min/max timestamps
            all_timestamps = [
                datetime.fromisoformat(m["timestamp"]) for m in metrics_data
            ]
            if all_timestamps:
                report.start_time = min(all_timestamps).isoformat()
                report.end_time = max(all_timestamps).isoformat()

        # Number of inferences
        report.num_inferences = len(metrics_data)

        # Time metrics
        inference_times = [m["total_time"] for m in metrics_data if m["total_time"] > 0]
        if inference_times:
            report.avg_inference_time = statistics.mean(inference_times)
            report.min_inference_time = min(inference_times)
            report.max_inference_time = max(inference_times)
            report.median_inference_time = statistics.median(inference_times)

            if len(inference_times) > 1:
                report.stddev_inference_time = statistics.stdev(inference_times)

            # Percentiles
            sorted_times = sorted(inference_times)
            report.p90_inference_time = sorted_times[int(len(sorted_times) * 0.9)]
            report.p95_inference_time = sorted_times[int(len(sorted_times) * 0.95)]
            report.p99_inference_time = sorted_times[int(len(sorted_times) * 0.99)]

        # Latency metrics
        latency_values = [m["latency_ms"] for m in metrics_data if m["latency_ms"] > 0]
        if latency_values:
            report.avg_latency_ms = statistics.mean(latency_values)

        ttft_values = [
            m["time_to_first_token"]
            for m in metrics_data
            if m["time_to_first_token"] > 0
        ]
        if ttft_values:
            report.avg_time_to_first_token = statistics.mean(ttft_values)

        # Token metrics
        report.total_input_tokens = sum(m["input_tokens"] for m in metrics_data)
        report.total_output_tokens = sum(m["output_tokens"] for m in metrics_data)

        if report.num_inferences > 0:
            report.avg_input_tokens = report.total_input_tokens / report.num_inferences
            report.avg_output_tokens = (
                report.total_output_tokens / report.num_inferences
            )

        tokens_per_second = [
            m["tokens_per_second"] for m in metrics_data if m["tokens_per_second"] > 0
        ]
        if tokens_per_second:
            report.avg_tokens_per_second = statistics.mean(tokens_per_second)

        # Memory metrics
        memory_values = [
            m["memory_usage_mb"] for m in metrics_data if m["memory_usage_mb"] > 0
        ]
        if memory_values:
            report.avg_memory_usage_mb = statistics.mean(memory_values)
            report.max_memory_usage_mb = max(memory_values)

        cpu_memory_values = [
            m["peak_cpu_memory_mb"] for m in metrics_data if m["peak_cpu_memory_mb"] > 0
        ]
        if cpu_memory_values:
            report.avg_peak_cpu_memory_mb = statistics.mean(cpu_memory_values)

        gpu_memory_values = [
            m["peak_gpu_memory_mb"] for m in metrics_data if m["peak_gpu_memory_mb"] > 0
        ]
        if gpu_memory_values:
            report.avg_peak_gpu_memory_mb = statistics.mean(gpu_memory_values)

        # System metrics
        cpu_values = [m["cpu_percent"] for m in metrics_data if m["cpu_percent"] > 0]
        if cpu_values:
            report.avg_cpu_percent = statistics.mean(cpu_values)

        gpu_values = [m["gpu_percent"] for m in metrics_data if m["gpu_percent"] > 0]
        if gpu_values:
            report.avg_gpu_percent = statistics.mean(gpu_values)

        # Quality metrics
        perplexity_values = [
            m["perplexity"] for m in metrics_data if m["perplexity"] > 0
        ]
        if perplexity_values:
            report.avg_perplexity = statistics.mean(perplexity_values)

        bleu_values = [m["bleu_score"] for m in metrics_data if m["bleu_score"] > 0]
        if bleu_values:
            report.avg_bleu_score = statistics.mean(bleu_values)

        rouge_values = [m["rouge_score"] for m in metrics_data if m["rouge_score"] > 0]
        if rouge_values:
            report.avg_rouge_score = statistics.mean(rouge_values)

        # Cost metrics
        report.total_estimated_cost = sum(m["estimated_cost"] for m in metrics_data)
        if report.num_inferences > 0 and report.total_estimated_cost > 0:
            report.avg_cost_per_inference = (
                report.total_estimated_cost / report.num_inferences
            )
            # Use consistent currency across all metrics
            currencies = {m["currency"] for m in metrics_data if m["currency"]}
            if len(currencies) == 1:
                report.currency = list(currencies)[0]

        # Include raw metrics if requested
        if include_metrics:
            report.raw_metrics = metrics_data

        return report

    def compare_models(
        self,
        model_ids: List[str],
        model_names: List[str] = None,
        title: str = "Model Comparison",
        time_range: Tuple[datetime, datetime] = None,
    ) -> ModelComparisonReport:
        """
        Compare performance across multiple models.

        Args:
            model_ids: List of model IDs to compare
            model_names: Optional list of model names
            title: Title for the comparison
            time_range: Optional time range to filter metrics

        Returns:
            ModelComparisonReport: A comparison of the models' performance
        """
        comparison = ModelComparisonReport(title=title)

        # Generate reports for each model
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
            "avg_perplexity",
            "avg_bleu_score",
            "avg_rouge_score",
        ]

        for idx, model_id in enumerate(model_ids):
            # Generate a report for this model
            model_name = model_names[idx] if idx < len(model_names) else model_id
            report = self.generate_report(
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
                "avg_memory_usage_mb",
                "avg_time_to_first_token",
            ]
        )

        return comparison

    def set_alert_threshold(
        self,
        model_id: str,
        metric_name: str,
        threshold_value: float,
        is_upper_bound: bool = True,
        cooldown_minutes: int = 60,
        notification_channels: List[str] = None,
    ) -> None:
        """
        Set an alert threshold for a model metric.

        Args:
            model_id: ID of the model
            metric_name: Name of the metric to monitor
            threshold_value: Value to trigger alert
            is_upper_bound: If True, alert when value > threshold
                          If False, alert when value < threshold
            cooldown_minutes: Minimum minutes between repeated alerts
            notification_channels: List of notification channels
        """
        alert_config = AlertConfig(
            model_id=model_id,
            metric_name=metric_name,
            threshold_value=threshold_value,
            is_upper_bound=is_upper_bound,
            cooldown_minutes=cooldown_minutes,
            notification_channels=notification_channels or ["log"],
        )

        self.metrics_db.save_alert_config(alert_config)

    def get_alert_configs(self, model_id: str = None) -> List[AlertConfig]:
        """
        Get alert configurations.

        Args:
            model_id: Optional model ID to filter by

        Returns:
            List of AlertConfig objects
        """
        return self.metrics_db.get_alert_configs(model_id=model_id)

    def get_alert_history(
        self, model_id: str = None, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get alert history.

        Args:
            model_id: Optional model ID to filter by
            days: Number of days of history to retrieve

        Returns:
            List of alert history entries
        """
        return self.metrics_db.get_alert_history(model_id=model_id, days=days)

    def visualize_metrics(
        self,
        model_id: str,
        metric_names: List[str] = None,
        days: int = 30,
        save_path: str = None,
    ) -> List[str]:
        """
        Visualize model performance metrics.

        Args:
            model_id: ID of the model
            metric_names: List of metrics to visualize (default: latency_ms, tokens_per_second)
            days: Number of days of data to include
            save_path: Directory to save visualizations in

        Returns:
            List of paths to generated visualization files
        """
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            from matplotlib.dates import DateFormatter
        except ImportError:
            logger.error(
                "Visualization requires matplotlib and pandas. Install with: pip install matplotlib pandas"
            )
            return []

        metric_names = metric_names or [
            "latency_ms",
            "tokens_per_second",
            "memory_usage_mb",
        ]

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

        # Convert to pandas DataFrame
        df = pd.DataFrame(metrics_data)
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

        for metric_name in metric_names:
            if metric_name not in df.columns or df[metric_name].max() <= 0:
                logger.warning(f"No data for metric {metric_name}")
                continue

            try:
                plt.figure(figsize=(10, 6))
                plt.plot(df["timestamp"], df[metric_name])
                plt.title(f"{metric_name} - Model {model_id}")
                plt.xlabel("Time")
                plt.ylabel(metric_name)
                plt.grid(True)

                # Format x-axis date labels
                date_format = DateFormatter("%Y-%m-%d")
                plt.gca().xaxis.set_major_formatter(date_format)
                plt.xticks(rotation=45)

                # Add trend line
                try:
                    import numpy as np
                    from scipy import stats

                    # Convert timestamps to numbers for correlation
                    x = np.array(
                        [
                            (t - df["timestamp"].min()).total_seconds()
                            for t in df["timestamp"]
                        ]
                    )
                    y = df[metric_name].values

                    # Calculate trend line
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                    trend_y = intercept + slope * x

                    # Add trend line to plot
                    plt.plot(
                        df["timestamp"],
                        trend_y,
                        "r--",
                        alpha=0.7,
                        label=f"Trend (r={r_value:.2f})",
                    )
                    plt.legend()

                    # Add trend information to title
                    direction = "increasing" if slope > 0 else "decreasing"
                    plt.title(f"{metric_name} - Model {model_id} (Trend: {direction})")
                except ImportError:
                    pass

                # Save figure
                filename = f"{model_id}_{metric_name}_{int(time.time())}.png"
                filepath = os.path.join(save_path, filename)
                plt.tight_layout()
                plt.savefig(filepath)
                plt.close()

                generated_files.append(filepath)

            except Exception as e:
                logger.error(f"Error generating visualization for {metric_name}: {e}")

        return generated_files

    def export_metrics_csv(
        self,
        model_id: str,
        time_range: Tuple[datetime, datetime] = None,
        batch_id: str = None,
        filename: str = None,
    ) -> str:
        """
        Export metrics to a CSV file.

        Args:
            model_id: ID of the model
            time_range: Optional time range to filter metrics
            batch_id: Optional batch ID to filter metrics
            filename: Output CSV filename

        Returns:
            Path to the exported CSV file
        """
        # Get metrics from database
        metrics_data = self.metrics_db.get_metrics(
            model_id=model_id,
            time_range=time_range,
            batch_id=batch_id,
            limit=100000,  # Higher limit for exports
        )

        if not metrics_data:
            logger.warning(f"No metrics found for model {model_id}")
            return None

        # Determine output filename
        if not filename:
            timestamp = int(time.time())
            filename = f"{model_id}_metrics_{timestamp}.csv"

        # Write CSV
        try:
            with open(filename, "w", newline="") as f:
                # Determine the fields to include
                fieldnames = list(metrics_data[0].keys())

                # Remove large/complex fields
                if "metadata" in fieldnames:
                    fieldnames.remove("metadata")

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for row in metrics_data:
                    # Make a copy without excluded fields
                    row_copy = {k: v for k, v in row.items() if k in fieldnames}
                    writer.writerow(row_copy)

            return os.path.abspath(filename)

        except Exception as e:
            logger.error(f"Error exporting metrics to CSV: {e}")
            return None

    def cleanup(self, days: int = DEFAULT_METRICS_RETENTION_DAYS) -> int:
        """
        Clean up old data from the metrics database.

        Args:
            days: Number of days of data to keep

        Returns:
            Number of records deleted
        """
        return self.metrics_db.cleanup_old_metrics(days)

    def close(self) -> None:
        """
        Close the metrics database connection.
        """
        self.metrics_db.close()

    def get_model_metrics(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Get all metrics for a model.

        Args:
            model_id: ID of the model

        Returns:
            List of metric dictionaries or InferenceMetrics objects
        """
        # First check if we have metrics in memory
        if model_id in self.metrics_history and self.metrics_history[model_id]:
            return self.metrics_history[model_id]

        # Fall back to database if no in-memory metrics
        return self.metrics_db.get_metrics(model_id=model_id)

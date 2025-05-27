#!/usr/bin/env python


# Configure logging
logger = logging.getLogger(__name__)

"""
Log Dashboard - An advanced web-based dashboard for visualizing application logs.

This tool provides a comprehensive web interface for viewing, filtering, analyzing,
and visualizing log files from the pAIssive_income project. It helps developers and
administrators monitor application behavior, troubleshoot issues, and gain insights
from log data.

Features:
- Real-time log streaming and viewing
- Advanced filtering by log level, module, time range, and custom fields
- Interactive log statistics and visualizations
- Pattern detection and anomaly highlighting
- Performance metrics visualization
- Error rate tracking and alerting
- Integration with ELK stack (Elasticsearch, Logstash, Kibana)
- Export capabilities for logs and visualizations
- Customizable dashboards and views

Usage:
    python tools/log_dashboard.py [--port PORT] [--log-dir LOG_DIR] [--es-host ES_HOST] [--es-port ES_PORT]

Arguments:
    --port PORT       Port to run the dashboard on (default: 8050)
    --log-dir LOG_DIR Directory containing log files (default: current directory)
    --es-host ES_HOST Elasticsearch host for advanced analytics (default: None)
    --es-port ES_PORT Elasticsearch port (default: 9200)
    --refresh SECONDS Refresh interval in seconds (default: 30)
"""

import argparse
import datetime
import glob
import json
import logging
import os
import re
import sys
import traceback
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

# Import alert system
from common_utils.logging.alert_system import (
    AlertCondition,
    AlertRule,
    AlertSeverity,
    AlertSystem,
    InAppNotifier,
)

# Import dashboard authentication
from common_utils.logging.dashboard_auth import (
    DashboardAuth,
    Role,
    User,
    require_permission,
)

# Import machine learning log analysis
from common_utils.logging.ml_log_analysis import (
    LogAnalyzer,
)

# Configure logging

try:
    import dash
    import dash_bootstrap_components as dbc
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from dash import dash_table, dcc, html
    from dash.dependencies import ALL, MATCH, Input, Output, State
    from plotly.subplots import make_subplots
    from scipy import stats

    from tools.predefined_dashboards import get_dashboard_layout
except ImportError as e:
    logger.error(f"Required packages not installed: {e}")
    logger.info("Install required packages with: pip install dash dash-bootstrap-components pandas plotly numpy scipy")
    sys.exit(1)

# Try to import Elasticsearch
try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    logger.warning("Elasticsearch package not installed. ELK integration will be disabled.")
    logger.info("Install with: pip install elasticsearch")
    ELASTICSEARCH_AVAILABLE = False

# Log entry pattern
LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?) - "
    r"(?P<name>[^-]+) - "
    r"(?P<level>[A-Z]+) - "
    r"(?P<message>.*)"
)

# Log level colors
LOG_COLORS = {
    "DEBUG": "#6c757d",    # Gray
    "INFO": "#17a2b8",     # Cyan
    "WARNING": "#ffc107",  # Yellow
    "ERROR": "#dc3545",    # Red
    "CRITICAL": "#721c24", # Dark red
}

# JSON log pattern
JSON_LOG_PATTERN = re.compile(r"^\s*\{.*\}\s*$")

# Dashboard themes
THEMES = {
    "light": dbc.themes.BOOTSTRAP,
    "dark": dbc.themes.DARKLY,
    "cerulean": dbc.themes.CERULEAN,
    "cosmo": dbc.themes.COSMO,
    "flatly": dbc.themes.FLATLY,
    "journal": dbc.themes.JOURNAL,
    "litera": dbc.themes.LITERA,
    "lumen": dbc.themes.LUMEN,
    "lux": dbc.themes.LUX,
    "materia": dbc.themes.MATERIA,
    "minty": dbc.themes.MINTY,
    "pulse": dbc.themes.PULSE,
    "sandstone": dbc.themes.SANDSTONE,
    "simplex": dbc.themes.SIMPLEX,
    "sketchy": dbc.themes.SKETCHY,
    "spacelab": dbc.themes.SPACELAB,
    "united": dbc.themes.UNITED,
    "yeti": dbc.themes.YETI,
}

# Performance patterns to extract metrics from log messages
PERFORMANCE_PATTERNS = {
    "api_latency": re.compile(r"API request completed in (\d+\.?\d*) ms"),
    "db_query_time": re.compile(r"Database query took (\d+\.?\d*) ms"),
    "response_time": re.compile(r"Response time: (\d+\.?\d*) ms"),
    "processing_time": re.compile(r"Processing took (\d+\.?\d*) ms"),
    "memory_usage": re.compile(r"Memory usage: (\d+\.?\d*) MB"),
}

# Error patterns to look for in log messages
ERROR_PATTERNS = [
    re.compile(r"Exception|Error|Traceback", re.IGNORECASE),
    re.compile(r"Failed to|Unable to|Cannot|Could not", re.IGNORECASE),
    re.compile(r"Invalid|Illegal|Timeout|Timed out", re.IGNORECASE),
    re.compile(r"Connection refused|Connection reset|Connection closed", re.IGNORECASE),
]

def parse_log_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a log file into a list of log entries.

    Supports both standard log format and JSON logs.

    Args:
        file_path: Path to the log file

    Returns:
        List of dictionaries containing log entries

    """
    log_entries = []

    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                # Try to parse as JSON first
                if JSON_LOG_PATTERN.match(line.strip()):
                    try:
                        entry = json.loads(line.strip())
                        # Ensure required fields exist
                        if "timestamp" in entry:
                            # Convert timestamp to datetime
                            if isinstance(entry["timestamp"], str):
                                try:
                                    # Try ISO format first
                                    entry["timestamp"] = datetime.datetime.fromisoformat(
                                        entry["timestamp"].replace("Z", "+00:00")
                                    )
                                except ValueError:
                                    # Try other common formats
                                    try:
                                        entry["timestamp"] = datetime.datetime.strptime(
                                            entry["timestamp"].split(".")[0],
                                            "%Y-%m-%d %H:%M:%S"
                                        )
                                    except ValueError:
                                        # Keep as string if parsing fails
                                        pass
                        else:
                            # Use file modification time if timestamp is missing
                            entry["timestamp"] = datetime.datetime.fromtimestamp(
                                os.path.getmtime(file_path)
                            )

                        # Ensure level exists
                        if "level" not in entry and "levelname" in entry:
                            entry["level"] = entry["levelname"]
                        elif "level" not in entry:
                            entry["level"] = "INFO"

                        # Ensure name exists
                        if "name" not in entry and "logger" in entry:
                            entry["name"] = entry["logger"]
                        elif "name" not in entry:
                            entry["name"] = os.path.basename(file_path)

                        # Ensure message exists
                        if "message" not in entry and "msg" in entry:
                            entry["message"] = entry["msg"]
                        elif "message" not in entry:
                            entry["message"] = str(entry)

                        log_entries.append(entry)
                    except json.JSONDecodeError:
                        # Not valid JSON, try standard format
                        match = LOG_PATTERN.match(line.strip())
                        if match:
                            entry = match.groupdict()
                            entry["timestamp"] = datetime.datetime.strptime(
                                entry["timestamp"].split(".")[0],
                                "%Y-%m-%d %H:%M:%S"
                            )
                            log_entries.append(entry)
                        elif log_entries:
                            # Handle multi-line entries (e.g., tracebacks)
                            log_entries[-1]["message"] += "\n" + line.strip()
                else:
                    # Try standard format
                    match = LOG_PATTERN.match(line.strip())
                    if match:
                        entry = match.groupdict()
                        entry["timestamp"] = datetime.datetime.strptime(
                            entry["timestamp"].split(".")[0],
                            "%Y-%m-%d %H:%M:%S"
                        )
                        log_entries.append(entry)
                    elif log_entries:
                        # Handle multi-line entries (e.g., tracebacks)
                        log_entries[-1]["message"] += "\n" + line.strip()
    except Exception as e:
        logger.error(f"Error parsing log file {file_path}: {e}")
        logger.debug(traceback.format_exc())

    return log_entries

def get_log_files(log_dir: str) -> List[str]:
    """
    Get all log files in the specified directory.

    Args:
        log_dir: Directory containing log files

    Returns:
        List of log file paths

    """
    # Get all .log files
    log_files = glob.glob(os.path.join(log_dir, "*.log"))

    # Also get .json log files
    log_files.extend(glob.glob(os.path.join(log_dir, "*.json")))

    # Get logs in subdirectories
    for subdir in os.listdir(log_dir):
        subdir_path = os.path.join(log_dir, subdir)
        if os.path.isdir(subdir_path):
            log_files.extend(glob.glob(os.path.join(subdir_path, "*.log")))
            log_files.extend(glob.glob(os.path.join(subdir_path, "*.json")))

    return sorted(log_files)

def get_log_statistics(log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics from log entries.

    Args:
        log_entries: List of log entries

    Returns:
        Dictionary containing log statistics

    """
    if not log_entries:
        return {
            "total": 0,
            "by_level": {},
            "by_module": {},
            "by_hour": {},
            "by_date": {},
            "by_minute": {},
            "error_rate": 0,
            "performance_metrics": {},
            "common_patterns": {},
            "anomalies": [],
        }

    # Count by level
    level_counts = Counter(entry["level"] for entry in log_entries)

    # Count by module
    module_counts = Counter(entry["name"] for entry in log_entries)

    # Count by hour
    hour_counts = Counter(entry["timestamp"].hour for entry in log_entries)

    # Count by date
    date_counts = Counter(entry["timestamp"].date() for entry in log_entries)

    # Count by minute (for more granular time series)
    minute_counts = Counter(
        f"{entry['timestamp'].hour:02d}:{entry['timestamp'].minute:02d}"
        for entry in log_entries
    )

    # Calculate error rate
    error_count = sum(
        1 for entry in log_entries
        if entry["level"] in ["ERROR", "CRITICAL"]
    )
    error_rate = error_count / len(log_entries) if log_entries else 0

    # Extract performance metrics
    performance_metrics = defaultdict(list)
    for entry in log_entries:
        message = entry.get("message", "")
        for metric_name, pattern in PERFORMANCE_PATTERNS.items():
            match = pattern.search(message)
            if match:
                try:
                    value = float(match.group(1))
                    performance_metrics[metric_name].append(value)
                except (ValueError, IndexError):
                    pass

    # Calculate performance metric statistics
    performance_stats = {}
    for metric, values in performance_metrics.items():
        if values:
            performance_stats[metric] = {
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "median": sorted(values)[len(values) // 2],
                "p95": sorted(values)[int(len(values) * 0.95)],
                "count": len(values),
            }

    # Find common patterns
    common_patterns = {}
    for entry in log_entries:
        message = entry.get("message", "")
        for pattern in ERROR_PATTERNS:
            if pattern.search(message):
                pattern_str = pattern.pattern
                if pattern_str not in common_patterns:
                    common_patterns[pattern_str] = 0
                common_patterns[pattern_str] += 1

    # Detect anomalies (simple z-score based)
    timestamps = [entry["timestamp"] for entry in log_entries]
    if timestamps:
        # Convert to UNIX timestamps
        unix_timestamps = [ts.timestamp() for ts in timestamps]
        # Calculate time differences
        time_diffs = np.diff(sorted(unix_timestamps))
        if len(time_diffs) > 1:
            # Calculate z-scores
            z_scores = stats.zscore(time_diffs)
            # Find anomalies (z-score > 3)
            anomaly_indices = np.where(np.abs(z_scores) > 3)[0]
            anomalies = []
            for idx in anomaly_indices:
                anomalies.append({
                    "timestamp": datetime.datetime.fromtimestamp(unix_timestamps[idx]),
                    "z_score": float(z_scores[idx]),
                    "time_diff": float(time_diffs[idx]),
                })
        else:
            anomalies = []
    else:
        anomalies = []

    return {
        "total": len(log_entries),
        "by_level": dict(level_counts),
        "by_module": dict(module_counts),
        "by_hour": dict(hour_counts),
        "by_date": {str(date): count for date, count in date_counts.items()},
        "by_minute": dict(minute_counts),
        "error_rate": error_rate,
        "performance_metrics": performance_stats,
        "common_patterns": common_patterns,
        "anomalies": anomalies,
    }

def fetch_logs_from_elasticsearch(
    es_host: str,
    es_port: int,
    index_pattern: str = "logs-*",
    size: int = 1000,
    query: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch logs from Elasticsearch.

    Args:
        es_host: Elasticsearch host
        es_port: Elasticsearch port
        index_pattern: Index pattern to search
        size: Maximum number of logs to return
        query: Elasticsearch query

    Returns:
        List of log entries

    """
    if not ELASTICSEARCH_AVAILABLE:
        logger.warning("Elasticsearch package not installed. Cannot fetch logs from Elasticsearch.")
        return []

    try:
        # Create Elasticsearch client
        es = Elasticsearch([f"http://{es_host}:{es_port}"])

        # Create query
        if query is None:
            query = {"match_all": {}}

        # Execute search
        response = es.search(
            index=index_pattern,
            body={
                "query": query,
                "size": size,
                "sort": [{"@timestamp": {"order": "desc"}}],
            },
        )

        # Extract log entries
        log_entries = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            entry = {
                "timestamp": datetime.datetime.fromisoformat(
                    source.get("@timestamp", "").replace("Z", "+00:00")
                ),
                "level": source.get("level", "INFO"),
                "name": source.get("logger", source.get("name", "unknown")),
                "message": source.get("message", str(source)),
                "source": "elasticsearch",
                "index": hit["_index"],
                "id": hit["_id"],
            }
            log_entries.append(entry)

        return log_entries
    except Exception as e:
        logger.error(f"Error fetching logs from Elasticsearch: {e}")
        logger.debug(traceback.format_exc())
        return []

def detect_log_patterns(log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect patterns in log entries.

    Args:
        log_entries: List of log entries

    Returns:
        Dictionary containing pattern information

    """
    if not log_entries:
        return {
            "frequent_patterns": [],
            "error_patterns": [],
            "performance_patterns": [],
        }

    # Extract messages
    messages = [entry.get("message", "") for entry in log_entries]

    # Find frequent patterns (simple approach: common prefixes)
    prefixes = []
    for message in messages:
        words = message.split()
        if len(words) >= 3:
            prefix = " ".join(words[:3])
            prefixes.append(prefix)

    # Count prefixes
    prefix_counts = Counter(prefixes)
    frequent_patterns = [
        {"pattern": pattern, "count": count}
        for pattern, count in prefix_counts.most_common(10)
        if count > 1
    ]

    # Find error patterns
    error_patterns = []
    for pattern in ERROR_PATTERNS:
        pattern_str = pattern.pattern
        count = sum(1 for message in messages if pattern.search(message))
        if count > 0:
            error_patterns.append({"pattern": pattern_str, "count": count})

    # Find performance patterns
    performance_patterns = []
    for metric_name, pattern in PERFORMANCE_PATTERNS.items():
        pattern_str = pattern.pattern
        count = sum(1 for message in messages if pattern.search(message))
        if count > 0:
            performance_patterns.append({
                "pattern": pattern_str,
                "metric": metric_name,
                "count": count,
            })

    return {
        "frequent_patterns": frequent_patterns,
        "error_patterns": error_patterns,
        "performance_patterns": performance_patterns,
    }

def create_dashboard(
    log_dir: str,
    es_host: Optional[str] = None,
    es_port: int = 9200,
    refresh_interval: int = 30,
    enable_auth: bool = False,
    secret_key: Optional[str] = None,
    session_expiry: int = 3600,
    enable_csrf_protection: bool = True,
    rate_limit_auth: bool = True,
    max_auth_attempts: int = 5,
    lockout_time: int = 300,
    audit_logging: bool = True,
) -> dash.Dash:
    """
    Create the Dash application for the log dashboard.

    Args:
        log_dir: Directory containing log files
        es_host: Elasticsearch host (optional)
        es_port: Elasticsearch port
        refresh_interval: Refresh interval in seconds
        enable_auth: Enable authentication
        secret_key: Secret key for authentication
        session_expiry: Session expiry time in seconds (default: 3600)
        enable_csrf_protection: Enable CSRF protection (default: True)
        rate_limit_auth: Enable rate limiting for authentication attempts (default: True)
        max_auth_attempts: Maximum number of failed authentication attempts before lockout (default: 5)
        lockout_time: Lockout time in seconds after max failed attempts (default: 300)
        audit_logging: Enable audit logging for security events (default: True)

    Returns:
        Dash application

    """
    # Create Dash app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="pAIssive_income Log Dashboard",
        suppress_callback_exceptions=True,
    )

    # Create alert system
    alert_system = AlertSystem()

    # Create machine learning log analyzer
    log_analyzer = LogAnalyzer()

    # Add default alert rules
    alert_system.add_rule(
        AlertRule(
            name="High Error Rate",
            description="Alert when error rate exceeds threshold",
            condition=AlertCondition.THRESHOLD,
            parameters={
                "metric": "error_rate",
                "threshold": 0.05,  # 5%
                "window": 300,  # 5 minutes
                "operator": ">",
            },
            severity=AlertSeverity.WARNING,
            notifiers=["in-app"],
        )
    )

    alert_system.add_rule(
        AlertRule(
            name="API Latency Spike",
            description="Alert when API latency spikes",
            condition=AlertCondition.ANOMALY,
            parameters={
                "metric": "api_latency",
                "sensitivity": 3.0,  # z-score threshold
                "window": 600,  # 10 minutes
            },
            severity=AlertSeverity.WARNING,
            notifiers=["in-app"],
        )
    )

    alert_system.add_rule(
        AlertRule(
            name="Database Query Time Spike",
            description="Alert when database query time spikes",
            condition=AlertCondition.ANOMALY,
            parameters={
                "metric": "db_query_time",
                "sensitivity": 3.0,  # z-score threshold
                "window": 600,  # 10 minutes
            },
            severity=AlertSeverity.WARNING,
            notifiers=["in-app"],
        )
    )

    alert_system.add_rule(
        AlertRule(
            name="Exception Pattern",
            description="Alert when exception patterns are detected",
            condition=AlertCondition.PATTERN,
            parameters={
                "pattern": "Exception|Error|Traceback",
                "min_matches": 3,
            },
            severity=AlertSeverity.ERROR,
            notifiers=["in-app"],
        )
    )

    # Add in-app notifier
    def in_app_notification_callback(alert_rule, context):
        """Callback for in-app notifications."""
        # This will be used to store alerts that will be displayed in the UI
        if not hasattr(app, "alerts"):
            app.alerts = []

        app.alerts.append({
            "id": len(app.alerts) + 1,
            "time": datetime.datetime.now().isoformat(),
            "name": alert_rule.name,
            "description": alert_rule.description,
            "severity": alert_rule.severity,
            "context": context,
            "read": False,
        })

        # Keep only the last 100 alerts
        if len(app.alerts) > 100:
            app.alerts = app.alerts[-100:]

    alert_system.add_notifier(InAppNotifier(callback=in_app_notification_callback))

    # Store global state
    app.es_host = es_host
    app.es_port = es_port
    app.log_dir = log_dir
    app.refresh_interval = refresh_interval
    app.alert_system = alert_system
    app.log_analyzer = log_analyzer
    app.alerts = []
    app.ml_analysis_results = {
        "anomalies": [],
        "patterns": [],
        "clusters": [],
        "last_analyzed": None,
    }

    # Set up authentication if enabled
    if enable_auth:
        # Create authentication system
        auth = DashboardAuth(
            secret_key=secret_key,
            session_expiry=session_expiry,
        )

        # Add default users
        auth.add_user(
            User(
                username="admin",
                password_hash=auth.hash_password("admin"),
                roles=["admin"],
            )
        )
        auth.add_user(
            User(
                username="user",
                password_hash=auth.hash_password("user"),
                roles=["viewer"],
            )
        )

        # Add roles
        auth.add_role(
            Role(
                name="admin",
                permissions=[
                    "view_logs",
                    "view_analytics",
                    "view_alerts",
                    "manage_alerts",
                    "view_ml_analysis",
                    "run_ml_analysis",
                    "view_settings",
                    "manage_settings",
                    "manage_users",
                    "manage_roles",
                ],
                description="Administrator role",
            )
        )
        auth.add_role(
            Role(
                name="viewer",
                permissions=[
                    "view_logs",
                    "view_analytics",
                    "view_alerts",
                    "view_ml_analysis",
                ],
                description="Viewer role",
            )
        )

        auth.add_role(
            Role(
                name="analyst",
                permissions=[
                    "view_logs",
                    "view_analytics",
                    "view_alerts",
                    "view_ml_analysis",
                    "run_ml_analysis",
                ],
                description="Analyst role",
            )
        )

        # Set up rate limiting for authentication
        if rate_limit_auth:
            auth.enable_rate_limiting(max_attempts=max_auth_attempts, lockout_time=lockout_time)

        # Set up CSRF protection
        if enable_csrf_protection:
            auth.enable_csrf_protection()

        # Set up audit logging
        if audit_logging:
            auth.enable_audit_logging()

        # Initialize app with authentication
        auth.init_app(app)

    # Define layout with tabs for different views
    app.layout = dbc.Container(
        [
            # Header with navigation
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.NavbarBrand("pAIssive_income Log Dashboard", className="ms-2"),
                        dbc.NavbarToggler(id="navbar-toggler"),
                        dbc.Collapse(
                            dbc.Nav(
                                [
                                    dbc.NavItem(dbc.NavLink("Dashboard", href="#", id="nav-dashboard")),
                                    dbc.NavItem(dbc.NavLink("Analytics", href="#", id="nav-analytics")),
                                    dbc.NavItem(dbc.NavLink("Alerts", href="#", id="nav-alerts")),
                                    dbc.NavItem(dbc.NavLink("ML Analysis", href="#", id="nav-ml-analysis")),
                                    dbc.NavItem(dbc.NavLink("Users", href="#", id="nav-users")),
                                    dbc.NavItem(dbc.NavLink("Settings", href="#", id="nav-settings")),
                                    dbc.NavItem(dbc.NavLink("Help", href="#", id="nav-help")),
                                    dbc.DropdownMenu(
                                        [
                                            dbc.DropdownMenuItem("Main Dashboard", id="dashboard-main"),
                                            dbc.DropdownMenuItem("Error Monitoring", id="dashboard-error"),
                                            dbc.DropdownMenuItem("Performance Monitoring", id="dashboard-performance"),
                                            dbc.DropdownMenuItem("Security Monitoring", id="dashboard-security"),
                                            dbc.DropdownMenuItem("Service Health", id="dashboard-service-health"),
                                        ],
                                        label="Dashboards",
                                        nav=True,
                                    ),
                                ],
                                className="ms-auto",
                                navbar=True,
                            ),
                            id="navbar-collapse",
                            navbar=True,
                        ),
                    ]
                ),
                color="primary",
                dark=True,
                className="mb-4",
            ),

            # Container for selected dashboard from dropdown
            html.Div(id="selected-dashboard-container", className="mb-4"),

            # Main content with tabs
            dbc.Tabs(
                [
                    # Dashboard Tab
                    dbc.Tab(
                        [
            dbc.Row(
                dbc.Col(
                    html.H1("pAIssive_income Log Dashboard", className="text-center my-4"),
                    width=12,
                )
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Log Files"),
                                dbc.CardBody(
                                    [
                                        dcc.Dropdown(
                                            id="log-file-dropdown",
                                            options=[
                                                {"label": os.path.basename(f), "value": f}
                                                for f in get_log_files(log_dir)
                                            ],
                                            value=get_log_files(log_dir)[0] if get_log_files(log_dir) else None,
                                            clearable=False,
                                        ),
                                        html.Div(id="log-file-info", className="mt-3"),
                                    ]
                                ),
                            ]
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Filters"),
                                dbc.CardBody(
                                    [
                                        html.Label("Log Level"),
                                        dcc.Dropdown(
                                            id="level-filter",
                                            options=[
                                                {"label": level, "value": level}
                                                for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                                            ],
                                            multi=True,
                                            placeholder="Select log levels",
                                        ),
                                        html.Label("Module", className="mt-3"),
                                        dcc.Dropdown(
                                            id="module-filter",
                                            multi=True,
                                            placeholder="Select modules",
                                        ),
                                        html.Label("Time Range", className="mt-3"),
                                        dcc.DatePickerRange(
                                            id="date-filter",
                                            start_date_placeholder_text="Start Date",
                                            end_date_placeholder_text="End Date",
                                            clearable=True,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        width=8,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Log Level Distribution"),
                                dbc.CardBody(dcc.Graph(id="level-chart")),
                            ]
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Logs by Module"),
                                dbc.CardBody(dcc.Graph(id="module-chart")),
                            ]
                        ),
                        width=6,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Logs by Time"),
                                dbc.CardBody(dcc.Graph(id="time-chart")),
                            ]
                        ),
                        width=12,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Log Entries"),
                                dbc.CardBody(
                                    [
                                        dbc.InputGroup(
                                            [
                                                dbc.InputGroupText("Search"),
                                                dbc.Input(id="search-input", placeholder="Search log messages..."),
                                                dbc.Button("Search", id="search-button"),
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Div(id="log-entries"),
                                    ]
                                ),
                            ]
                        ),
                        width=12,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                dbc.Col(
                    html.Footer(
                        [
                            html.Hr(),
                            html.P(
                                "pAIssive_income Log Dashboard - Refresh every 30 seconds",
                                className="text-center text-muted",
                            ),
                        ]
                    ),
                    width=12,
                )
            ),
            dcc.Interval(
                id="interval-component",
                interval=30 * 1000,  # 30 seconds in milliseconds
                n_intervals=0,
            ),
            # Store for log entries
            dcc.Store(id="log-entries-store"),
                        ],
                        label="Dashboard",
                        tab_id="tab-dashboard",
                    ),

                    # Analytics Tab
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Error Rate Over Time"),
                                                dbc.CardBody(dcc.Graph(id="error-rate-chart")),
                                            ]
                                        ),
                                        width=6,
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Performance Metrics"),
                                                dbc.CardBody(dcc.Graph(id="performance-chart")),
                                            ]
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Log Patterns"),
                                                dbc.CardBody(
                                                    [
                                                        dbc.Tabs(
                                                            [
                                                                dbc.Tab(
                                                                    dcc.Graph(id="frequent-patterns-chart"),
                                                                    label="Frequent Patterns",
                                                                ),
                                                                dbc.Tab(
                                                                    dcc.Graph(id="error-patterns-chart"),
                                                                    label="Error Patterns",
                                                                ),
                                                                dbc.Tab(
                                                                    dcc.Graph(id="performance-patterns-chart"),
                                                                    label="Performance Patterns",
                                                                ),
                                                            ]
                                                        )
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Anomaly Detection"),
                                                dbc.CardBody(
                                                    [
                                                        dcc.Graph(id="anomaly-chart"),
                                                        html.Div(id="anomaly-details"),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                        ],
                        label="Analytics",
                        tab_id="tab-analytics",
                    ),

                    # ML Analysis Tab
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Machine Learning Analysis"),
                                                dbc.CardBody(
                                                    [
                                                        dbc.Button(
                                                            "Run ML Analysis",
                                                            id="run-ml-analysis-button",
                                                            color="primary",
                                                            className="mb-3",
                                                        ),
                                                        html.Div(id="ml-analysis-status"),
                                                        dbc.Spinner(id="ml-analysis-spinner", color="primary", type="grow"),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),

                    # Predefined Dashboards Tab
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Predefined Dashboards"),
                                                dbc.CardBody(
                                                    [
                                                        dbc.Tabs(
                                                            [
                                                                dbc.Tab(
                                                                    html.Div(id="error-monitoring-dashboard"),
                                                                    label="Error Monitoring",
                                                                    tab_id="tab-error-monitoring",
                                                                ),
                                                                dbc.Tab(
                                                                    html.Div(id="performance-monitoring-dashboard"),
                                                                    label="Performance Monitoring",
                                                                    tab_id="tab-performance-monitoring",
                                                                ),
                                                                dbc.Tab(
                                                                    html.Div(id="security-monitoring-dashboard"),
                                                                    label="Security Monitoring",
                                                                    tab_id="tab-security-monitoring",
                                                                ),
                                                                dbc.Tab(
                                                                    html.Div(id="service-health-dashboard"),
                                                                    label="Service Health",
                                                                    tab_id="tab-service-health",
                                                                ),
                                                            ],
                                                            id="predefined-dashboards-tabs",
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dcc.Store(id="predefined-dashboards-store"),
                        ],
                        label="Predefined Dashboards",
                        tab_id="tab-predefined-dashboards",
                    ),

                    # User Management Tab
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("User Management"),
                                                dbc.CardBody(
                                                    [
                                                        html.H5("Users"),
                                                        html.Div(id="user-list"),
                                                        html.Hr(),
                                                        html.H5("Add New User", className="mt-4"),
                                                        dbc.Form(
                                                            [
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Username", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="new-user-username",
                                                                                placeholder="Enter username",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                        dbc.Label("Password", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="new-user-password",
                                                                                placeholder="Enter password",
                                                                                type="password",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Roles", width=2),
                                                                        dbc.Col(
                                                                            dcc.Dropdown(
                                                                                id="new-user-roles",
                                                                                multi=True,
                                                                                placeholder="Select roles",
                                                                            ),
                                                                            width=10,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Col(
                                                                            dbc.Button(
                                                                                "Add User",
                                                                                id="add-user-button",
                                                                                color="primary",
                                                                            ),
                                                                            width=12,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                html.Div(id="add-user-status"),
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Role Management"),
                                                dbc.CardBody(
                                                    [
                                                        html.H5("Roles"),
                                                        html.Div(id="role-list"),
                                                        html.Hr(),
                                                        html.H5("Add New Role", className="mt-4"),
                                                        dbc.Form(
                                                            [
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Role Name", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="new-role-name",
                                                                                placeholder="Enter role name",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                        dbc.Label("Description", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="new-role-description",
                                                                                placeholder="Enter description",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Permissions", width=2),
                                                                        dbc.Col(
                                                                            dcc.Dropdown(
                                                                                id="new-role-permissions",
                                                                                multi=True,
                                                                                placeholder="Select permissions",
                                                                            ),
                                                                            width=10,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Col(
                                                                            dbc.Button(
                                                                                "Add Role",
                                                                                id="add-role-button",
                                                                                color="primary",
                                                                            ),
                                                                            width=12,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                html.Div(id="add-role-status"),
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Audit Logs"),
                                                dbc.CardBody(
                                                    [
                                                        html.H5("Security Audit Logs"),
                                                        html.Div(id="audit-log-list"),
                                                        dbc.Button(
                                                            "Refresh Audit Logs",
                                                            id="refresh-audit-logs-button",
                                                            color="secondary",
                                                            className="mt-3",
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dcc.Store(id="user-management-store"),
                        ],
                        label="User Management",
                        tab_id="tab-users",
                    ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Anomaly Detection"),
                                                dbc.CardBody(
                                                    [
                                                        html.Div(id="anomaly-detection-results"),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Pattern Recognition"),
                                                dbc.CardBody(
                                                    [
                                                        html.Div(id="pattern-recognition-results"),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=6,
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Log Clustering"),
                                                dbc.CardBody(
                                                    [
                                                        html.Div(id="log-clustering-results"),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dcc.Store(id="ml-analysis-store"),
                        ],
                        label="ML Analysis",
                        tab_id="tab-ml-analysis",
                    ),

                    # Alerts Tab
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Alert Configuration"),
                                                dbc.CardBody(
                                                    [
                                                        html.H5("Alert Rules"),
                                                        html.Div(id="alert-rules-list"),
                                                        html.Hr(),
                                                        html.H5("Add New Alert Rule", className="mt-4"),
                                                        dbc.Form(
                                                            [
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Name", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="alert-name-input",
                                                                                placeholder="Alert name",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                        dbc.Label("Severity", width=2),
                                                                        dbc.Col(
                                                                            dcc.Dropdown(
                                                                                id="alert-severity-dropdown",
                                                                                options=[
                                                                                    {"label": "Info", "value": "info"},
                                                                                    {"label": "Warning", "value": "warning"},
                                                                                    {"label": "Error", "value": "error"},
                                                                                    {"label": "Critical", "value": "critical"},
                                                                                ],
                                                                                value="warning",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Description", width=2),
                                                                        dbc.Col(
                                                                            dbc.Textarea(
                                                                                id="alert-description-input",
                                                                                placeholder="Alert description",
                                                                            ),
                                                                            width=10,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Condition", width=2),
                                                                        dbc.Col(
                                                                            dcc.Dropdown(
                                                                                id="alert-condition-dropdown",
                                                                                options=[
                                                                                    {"label": "Pattern", "value": "pattern"},
                                                                                    {"label": "Threshold", "value": "threshold"},
                                                                                    {"label": "Anomaly", "value": "anomaly"},
                                                                                    {"label": "Frequency", "value": "frequency"},
                                                                                    {"label": "Absence", "value": "absence"},
                                                                                ],
                                                                                value="pattern",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                        dbc.Col(
                                                                            html.Div(id="alert-condition-params"),
                                                                            width=6,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Notifiers", width=2),
                                                                        dbc.Col(
                                                                            dcc.Checklist(
                                                                                id="alert-notifiers-checklist",
                                                                                options=[
                                                                                    {"label": "In-App", "value": "in-app"},
                                                                                    {"label": "Email", "value": "email"},
                                                                                    {"label": "Webhook", "value": "webhook"},
                                                                                ],
                                                                                value=["in-app"],
                                                                                inline=True,
                                                                            ),
                                                                            width=10,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Col(
                                                                            dbc.Button(
                                                                                "Add Alert Rule",
                                                                                id="add-alert-rule-button",
                                                                                color="primary",
                                                                            ),
                                                                            width={"size": 2, "offset": 2},
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Active Alerts"),
                                                dbc.CardBody(
                                                    [
                                                        html.Div(id="active-alerts-list"),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dcc.Interval(
                                id="alert-refresh-interval",
                                interval=5 * 1000,  # 5 seconds
                                n_intervals=0,
                            ),
                            dcc.Store(id="alerts-store"),
                        ],
                        label="Alerts",
                        tab_id="tab-alerts",
                    ),

                    # ELK Integration Tab
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Elasticsearch Connection"),
                                                dbc.CardBody(
                                                    [
                                                        dbc.Form(
                                                            [
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Host", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="es-host-input",
                                                                                placeholder="localhost",
                                                                                value=es_host or "",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                        dbc.Label("Port", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="es-port-input",
                                                                                placeholder="9200",
                                                                                value=str(es_port),
                                                                                type="number",
                                                                            ),
                                                                            width=2,
                                                                        ),
                                                                        dbc.Col(
                                                                            dbc.Button(
                                                                                "Connect",
                                                                                id="es-connect-button",
                                                                                color="primary",
                                                                            ),
                                                                            width=2,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Index Pattern", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="es-index-input",
                                                                                placeholder="logs-*",
                                                                                value="logs-*",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                        dbc.Label("Max Results", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="es-size-input",
                                                                                placeholder="1000",
                                                                                value="1000",
                                                                                type="number",
                                                                            ),
                                                                            width=2,
                                                                        ),
                                                                        dbc.Col(
                                                                            dbc.Button(
                                                                                "Fetch Logs",
                                                                                id="es-fetch-button",
                                                                                color="primary",
                                                                            ),
                                                                            width=2,
                                                                        ),
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                        html.Div(id="es-connection-status", className="mt-3"),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Elasticsearch Logs"),
                                                dbc.CardBody(
                                                    [
                                                        dash_table.DataTable(
                                                            id="es-logs-table",
                                                            columns=[
                                                                {"name": "Timestamp", "id": "timestamp"},
                                                                {"name": "Level", "id": "level"},
                                                                {"name": "Logger", "id": "name"},
                                                                {"name": "Message", "id": "message"},
                                                            ],
                                                            data=[],
                                                            style_table={"overflowX": "auto"},
                                                            style_cell={
                                                                "overflow": "hidden",
                                                                "textOverflow": "ellipsis",
                                                                "maxWidth": 0,
                                                            },
                                                            style_data_conditional=[
                                                                {
                                                                    "if": {"filter_query": "{level} = 'ERROR'"},
                                                                    "backgroundColor": "rgba(220, 53, 69, 0.2)",
                                                                },
                                                                {
                                                                    "if": {"filter_query": "{level} = 'WARNING'"},
                                                                    "backgroundColor": "rgba(255, 193, 7, 0.2)",
                                                                },
                                                                {
                                                                    "if": {"filter_query": "{level} = 'CRITICAL'"},
                                                                    "backgroundColor": "rgba(114, 28, 36, 0.2)",
                                                                },
                                                            ],
                                                            page_size=15,
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                        ],
                        label="ELK Integration",
                        tab_id="tab-elk",
                        disabled=not ELASTICSEARCH_AVAILABLE,
                    ),

                    # Settings Tab
                    dbc.Tab(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Dashboard Settings"),
                                                dbc.CardBody(
                                                    [
                                                        dbc.Form(
                                                            [
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Theme", width=2),
                                                                        dbc.Col(
                                                                            dcc.Dropdown(
                                                                                id="theme-dropdown",
                                                                                options=[
                                                                                    {"label": theme.capitalize(), "value": theme}
                                                                                    for theme in THEMES
                                                                                ],
                                                                                value="light",
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Refresh Interval (seconds)", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="refresh-input",
                                                                                type="number",
                                                                                min=5,
                                                                                max=300,
                                                                                step=5,
                                                                                value=refresh_interval,
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Label("Log Directory", width=2),
                                                                        dbc.Col(
                                                                            dbc.Input(
                                                                                id="log-dir-input",
                                                                                value=log_dir,
                                                                                disabled=True,
                                                                            ),
                                                                            width=4,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Col(
                                                                            dbc.Button(
                                                                                "Apply Settings",
                                                                                id="apply-settings-button",
                                                                                color="primary",
                                                                            ),
                                                                            width={"size": 2, "offset": 2},
                                                                        ),
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Export Options"),
                                                dbc.CardBody(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    dbc.Button(
                                                                        "Export Logs as CSV",
                                                                        id="export-csv-button",
                                                                        color="primary",
                                                                        className="me-2",
                                                                    ),
                                                                    width="auto",
                                                                ),
                                                                dbc.Col(
                                                                    dbc.Button(
                                                                        "Export Logs as JSON",
                                                                        id="export-json-button",
                                                                        color="primary",
                                                                        className="me-2",
                                                                    ),
                                                                    width="auto",
                                                                ),
                                                                dbc.Col(
                                                                    dbc.Button(
                                                                        "Export Charts",
                                                                        id="export-charts-button",
                                                                        color="primary",
                                                                    ),
                                                                    width="auto",
                                                                ),
                                                            ]
                                                        ),
                                                        dcc.Download(id="download-csv"),
                                                        dcc.Download(id="download-json"),
                                                        dcc.Download(id="download-charts"),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=12,
                                    ),
                                ],
                                className="mb-4",
                            ),
                        ],
                        label="Settings",
                        tab_id="tab-settings",
                    ),
                ],
                id="tabs",
                active_tab="tab-dashboard",
            ),

            # Footer
            dbc.Row(
                dbc.Col(
                    html.Footer(
                        [
                            html.Hr(),
                            html.P(
                                [
                                    f"pAIssive_income Log Dashboard - Refresh every {refresh_interval} seconds - ",
                                    html.A("View Documentation", href="#", id="view-docs-link"),
                                ],
                                className="text-center text-muted",
                            ),
                        ]
                    ),
                    width=12,
                )
            ),

            # Interval for refreshing data
            dcc.Interval(
                id="interval-component",
                interval=refresh_interval * 1000,  # Convert to milliseconds
                n_intervals=0,
            ),

            # Stores for data
            dcc.Store(id="log-entries-store"),
            dcc.Store(id="log-stats-store"),
            dcc.Store(id="es-logs-store"),
            dcc.Store(id="settings-store"),

            # Help modal
            dbc.Modal(
                [
                    dbc.ModalHeader("Log Dashboard Help"),
                    dbc.ModalBody(
                        [
                            html.H5("Dashboard Tab"),
                            html.P("View and filter log entries from files in the specified directory."),
                            html.H5("Analytics Tab"),
                            html.P("Analyze log patterns, detect anomalies, and view performance metrics."),
                            html.H5("ELK Integration Tab"),
                            html.P("Connect to Elasticsearch to fetch and analyze logs from the ELK stack."),
                            html.H5("Settings Tab"),
                            html.P("Configure dashboard settings and export options."),
                            html.H5("Keyboard Shortcuts"),
                            html.Ul(
                                [
                                    html.Li("Ctrl+F: Focus search box"),
                                    html.Li("Ctrl+R: Refresh data"),
                                    html.Li("Ctrl+E: Export logs as CSV"),
                                    html.Li("Ctrl+1-4: Switch tabs"),
                                ]
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close-help-button", className="ms-auto")
                    ),
                ],
                id="help-modal",
                size="lg",
            ),
        ],
        fluid=True,
    )

    # Define callbacks
    @app.callback(
        [
            Output("log-entries-store", "data"),
            Output("log-file-info", "children"),
            Output("module-filter", "options"),
        ],
        [
            Input("log-file-dropdown", "value"),
            Input("interval-component", "n_intervals"),
        ],
    )
    def update_log_entries(log_file: str, n_intervals: int) -> Tuple[List[Dict[str, Any]], List[html.Div], List[Dict[str, str]]]:
        """
        Update log entries when the log file changes or on interval.

        Args:
            log_file: Selected log file
            n_intervals: Number of interval refreshes

        Returns:
            Tuple of (log entries, file info, module options)

        """
        if not log_file:
            return [], [], []

        # Parse log file
        log_entries = parse_log_file(log_file)

        # Get file info
        file_size = os.path.getsize(log_file) / 1024  # KB
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(log_file))

        file_info = [
            html.Div(f"Entries: {len(log_entries)}"),
            html.Div(f"Size: {file_size:.2f} KB"),
            html.Div(f"Last Modified: {file_modified.strftime('%Y-%m-%d %H:%M:%S')}"),
        ]

        # Get unique modules
        modules = sorted(set(entry["name"] for entry in log_entries))
        module_options = [{"label": module, "value": module} for module in modules]

        return log_entries, file_info, module_options

    @app.callback(
        [
            Output("level-chart", "figure"),
            Output("module-chart", "figure"),
            Output("time-chart", "figure"),
        ],
        [
            Input("log-entries-store", "data"),
            Input("level-filter", "value"),
            Input("module-filter", "value"),
            Input("date-filter", "start_date"),
            Input("date-filter", "end_date"),
        ],
    )
    def update_charts(
        log_entries: List[Dict[str, Any]],
        level_filter: List[str],
        module_filter: List[str],
        start_date: str,
        end_date: str,
    ) -> Tuple[go.Figure, go.Figure, go.Figure]:
        """
        Update charts based on log entries and filters.

        Args:
            log_entries: List of log entries
            level_filter: Selected log levels
            module_filter: Selected modules
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            Tuple of (level chart, module chart, time chart)

        """
        if not log_entries:
            empty_fig = go.Figure().update_layout(
                title="No data available",
                xaxis={"visible": False},
                yaxis={"visible": False},
            )
            return empty_fig, empty_fig, empty_fig

        # Convert log entries to DataFrame
        df = pd.DataFrame(log_entries)

        # Apply filters
        if level_filter:
            df = df[df["level"].isin(level_filter)]

        if module_filter:
            df = df[df["name"].isin(module_filter)]

        if start_date:
            df = df[df["timestamp"] >= datetime.datetime.fromisoformat(start_date)]

        if end_date:
            df = df[df["timestamp"] <= datetime.datetime.fromisoformat(end_date)]

        if df.empty:
            empty_fig = go.Figure().update_layout(
                title="No data available with current filters",
                xaxis={"visible": False},
                yaxis={"visible": False},
            )
            return empty_fig, empty_fig, empty_fig

        # Create level chart
        level_counts = df["level"].value_counts().reset_index()
        level_counts.columns = ["Level", "Count"]
        level_fig = px.pie(
            level_counts,
            values="Count",
            names="Level",
            color="Level",
            color_discrete_map=LOG_COLORS,
            title="Log Level Distribution",
        )

        # Create module chart
        module_counts = df["name"].value_counts().reset_index()
        module_counts.columns = ["Module", "Count"]
        module_fig = px.bar(
            module_counts,
            x="Module",
            y="Count",
            title="Logs by Module",
        )

        # Create time chart
        df["hour"] = df["timestamp"].dt.hour
        df["date"] = df["timestamp"].dt.date
        time_counts = df.groupby(["date", "hour", "level"]).size().reset_index(name="Count")
        time_fig = px.line(
            time_counts,
            x="hour",
            y="Count",
            color="level",
            facet_row="date",
            color_discrete_map=LOG_COLORS,
            title="Logs by Time",
        )

        return level_fig, module_fig, time_fig

    @app.callback(
        Output("log-entries", "children"),
        [
            Input("log-entries-store", "data"),
            Input("level-filter", "value"),
            Input("module-filter", "value"),
            Input("date-filter", "start_date"),
            Input("date-filter", "end_date"),
            Input("search-button", "n_clicks"),
        ],
        [
            State("search-input", "value"),
        ],
    )
    def update_log_table(
        log_entries: List[Dict[str, Any]],
        level_filter: List[str],
        module_filter: List[str],
        start_date: str,
        end_date: str,
        n_clicks: int,
        search_query: str,
    ) -> List[html.Div]:
        """
        Update log table based on log entries and filters.

        Args:
            log_entries: List of log entries
            level_filter: Selected log levels
            module_filter: Selected modules
            start_date: Start date for filtering
            end_date: End date for filtering
            n_clicks: Number of search button clicks
            search_query: Search query

        Returns:
            List of log entry divs

        """
        if not log_entries:
            return [html.Div("No log entries found", className="text-muted")]

        # Filter log entries
        filtered_entries = log_entries.copy()

        if level_filter:
            filtered_entries = [entry for entry in filtered_entries if entry["level"] in level_filter]

        if module_filter:
            filtered_entries = [entry for entry in filtered_entries if entry["name"] in module_filter]

        if start_date:
            start_dt = datetime.datetime.fromisoformat(start_date)
            filtered_entries = [entry for entry in filtered_entries if entry["timestamp"] >= start_dt]

        if end_date:
            end_dt = datetime.datetime.fromisoformat(end_date)
            filtered_entries = [entry for entry in filtered_entries if entry["timestamp"] <= end_dt]

        if search_query:
            filtered_entries = [
                entry for entry in filtered_entries
                if search_query.lower() in entry["message"].lower()
            ]

        # Sort by timestamp (newest first)
        filtered_entries = sorted(filtered_entries, key=lambda x: x["timestamp"], reverse=True)

        # Process logs through alert system
        if hasattr(app, "alert_system") and filtered_entries:
            app.alert_system.process_logs(filtered_entries)

        # Limit to 100 entries for performance
        filtered_entries = filtered_entries[:100]

        if not filtered_entries:
            return [html.Div("No log entries match the current filters", className="text-muted")]

        # Create log entry divs
        log_divs = []
        for entry in filtered_entries:
            log_divs.append(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                                    className="text-muted me-2",
                                ),
                                html.Span(
                                    entry["level"],
                                    className="badge me-2",
                                    style={"backgroundColor": LOG_COLORS.get(entry["level"], "#6c757d")},
                                ),
                                html.Span(
                                    entry["name"],
                                    className="text-primary me-2",
                                ),
                            ],
                            className="d-flex align-items-center",
                        ),
                        html.Div(
                            entry["message"],
                            className="mt-1 mb-2",
                            style={"whiteSpace": "pre-wrap"},
                        ),
                        html.Hr(),
                    ],
                    className="log-entry",
                )
            )

        return log_divs

    @app.callback(
        Output("alert-condition-params", "children"),
        [Input("alert-condition-dropdown", "value")],
    )
    def update_alert_condition_params(condition: str) -> List[html.Div]:
        """
        Update alert condition parameters based on selected condition.

        Args:
            condition: Selected alert condition

        Returns:
            List of parameter input components

        """
        if condition == "pattern":
            return [
                dbc.Row(
                    [
                        dbc.Label("Pattern", width=4),
                        dbc.Col(
                            dbc.Input(
                                id="alert-pattern-input",
                                placeholder="Regex pattern",
                                value="Exception|Error",
                            ),
                            width=8,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Label("Min Matches", width=4),
                        dbc.Col(
                            dbc.Input(
                                id="alert-min-matches-input",
                                placeholder="Minimum matches",
                                value="1",
                                type="number",
                            ),
                            width=8,
                        ),
                    ],
                ),
            ]
        if condition == "threshold":
            return [
                dbc.Row(
                    [
                        dbc.Label("Metric", width=4),
                        dbc.Col(
                            dcc.Dropdown(
                                id="alert-metric-dropdown",
                                options=[
                                    {"label": "Error Rate", "value": "error_rate"},
                                    {"label": "API Latency", "value": "api_latency"},
                                    {"label": "DB Query Time", "value": "db_query_time"},
                                    {"label": "Response Time", "value": "response_time"},
                                    {"label": "Processing Time", "value": "processing_time"},
                                    {"label": "Memory Usage", "value": "memory_usage"},
                                ],
                                value="error_rate",
                            ),
                            width=8,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Label("Threshold", width=4),
                        dbc.Col(
                            dbc.Input(
                                id="alert-threshold-input",
                                placeholder="Threshold value",
                                value="0.05",
                                type="number",
                                step=0.01,
                            ),
                            width=8,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Label("Operator", width=4),
                        dbc.Col(
                            dcc.Dropdown(
                                id="alert-operator-dropdown",
                                options=[
                                    {"label": ">", "value": ">"},
                                    {"label": ">=", "value": ">="},
                                    {"label": "<", "value": "<"},
                                    {"label": "<=", "value": "<="},
                                    {"label": "==", "value": "=="},
                                    {"label": "!=", "value": "!="},
                                ],
                                value=">",
                            ),
                            width=8,
                        ),
                    ],
                ),
            ]
        if condition == "anomaly":
            return [
                dbc.Row(
                    [
                        dbc.Label("Metric", width=4),
                        dbc.Col(
                            dcc.Dropdown(
                                id="alert-metric-dropdown",
                                options=[
                                    {"label": "API Latency", "value": "api_latency"},
                                    {"label": "DB Query Time", "value": "db_query_time"},
                                    {"label": "Response Time", "value": "response_time"},
                                    {"label": "Processing Time", "value": "processing_time"},
                                    {"label": "Memory Usage", "value": "memory_usage"},
                                ],
                                value="api_latency",
                            ),
                            width=8,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Label("Sensitivity", width=4),
                        dbc.Col(
                            dbc.Input(
                                id="alert-sensitivity-input",
                                placeholder="Z-score threshold",
                                value="3.0",
                                type="number",
                                step=0.1,
                            ),
                            width=8,
                        ),
                    ],
                ),
            ]
        if condition == "frequency":
            return [
                dbc.Row(
                    [
                        dbc.Label("Threshold", width=4),
                        dbc.Col(
                            dbc.Input(
                                id="alert-frequency-threshold-input",
                                placeholder="Frequency threshold",
                                value="10",
                                type="number",
                            ),
                            width=8,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Label("Level", width=4),
                        dbc.Col(
                            dcc.Dropdown(
                                id="alert-level-dropdown",
                                options=[
                                    {"label": "Any", "value": ""},
                                    {"label": "DEBUG", "value": "DEBUG"},
                                    {"label": "INFO", "value": "INFO"},
                                    {"label": "WARNING", "value": "WARNING"},
                                    {"label": "ERROR", "value": "ERROR"},
                                    {"label": "CRITICAL", "value": "CRITICAL"},
                                ],
                                value="ERROR",
                            ),
                            width=8,
                        ),
                    ],
                ),
            ]
        if condition == "absence":
            return [
                dbc.Row(
                    [
                        dbc.Label("Pattern", width=4),
                        dbc.Col(
                            dbc.Input(
                                id="alert-absence-pattern-input",
                                placeholder="Expected pattern",
                                value="Heartbeat",
                            ),
                            width=8,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Label("Window (sec)", width=4),
                        dbc.Col(
                            dbc.Input(
                                id="alert-window-input",
                                placeholder="Time window in seconds",
                                value="300",
                                type="number",
                            ),
                            width=8,
                        ),
                    ],
                ),
            ]
        return []

    @app.callback(
        Output("alert-rules-list", "children"),
        [Input("add-alert-rule-button", "n_clicks"), Input("alert-refresh-interval", "n_intervals")],
        [
            State("alert-name-input", "value"),
            State("alert-description-input", "value"),
            State("alert-severity-dropdown", "value"),
            State("alert-condition-dropdown", "value"),
            State("alert-notifiers-checklist", "value"),
            # Pattern condition states
            State("alert-pattern-input", "value"),
            State("alert-min-matches-input", "value"),
            # Threshold condition states
            State("alert-metric-dropdown", "value"),
            State("alert-threshold-input", "value"),
            State("alert-operator-dropdown", "value"),
            # Anomaly condition states
            State("alert-sensitivity-input", "value"),
            # Frequency condition states
            State("alert-frequency-threshold-input", "value"),
            State("alert-level-dropdown", "value"),
            # Absence condition states
            State("alert-absence-pattern-input", "value"),
            State("alert-window-input", "value"),
        ],
    )
    @require_permission("view_alerts")
    def update_alert_rules(
        n_clicks, n_intervals, name, description, severity, condition, notifiers,
        pattern, min_matches, metric, threshold, operator, sensitivity,
        frequency_threshold, level, absence_pattern, window
    ):
        """
        Update alert rules list and add new rules when button is clicked.

        Returns:
            List of alert rule components

        """
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

        # Add new rule if button was clicked
        if triggered_id == "add-alert-rule-button" and n_clicks and name:
            # Check if user has permission to manage alerts
            has_permission = True
            if hasattr(app, "auth"):
                # Get username from session
                username = None
                if "auth" in flask.session:
                    session_data = flask.session["auth"]
                    username = session_data.get("username")

                if username:
                    has_permission = app.auth.has_permission(username, "manage_alerts")

            if not has_permission:
                return html.Div("You don't have permission to add alert rules", className="text-danger")
            # Create parameters based on condition
            parameters = {}
            if condition == "pattern":
                parameters = {
                    "pattern": pattern or "Exception|Error",
                    "min_matches": int(min_matches or 1),
                }
            elif condition == "threshold":
                parameters = {
                    "metric": metric or "error_rate",
                    "threshold": float(threshold or 0.05),
                    "operator": operator or ">",
                    "window": int(window or 300),
                }
            elif condition == "anomaly":
                parameters = {
                    "metric": metric or "api_latency",
                    "sensitivity": float(sensitivity or 3.0),
                    "window": int(window or 600),
                }
            elif condition == "frequency":
                parameters = {
                    "threshold": int(frequency_threshold or 10),
                    "level": level,
                    "window": int(window or 60),
                }
            elif condition == "absence":
                parameters = {
                    "pattern": absence_pattern or "Heartbeat",
                    "window": int(window or 300),
                }

            # Create and add rule
            rule = AlertRule(
                name=name,
                description=description or f"Alert for {condition} condition",
                condition=condition,
                parameters=parameters,
                severity=severity or "warning",
                notifiers=notifiers or ["in-app"],
            )

            app.alert_system.add_rule(rule)

        # Create list of current rules
        rules = []
        for rule in app.alert_system.rules:
            rules.append(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            rule.name,
                                            className="me-2",
                                        ),
                                        html.Span(
                                            rule.severity.upper(),
                                            className="badge",
                                            style={
                                                "backgroundColor": {
                                                    "info": "#17a2b8",
                                                    "warning": "#ffc107",
                                                    "error": "#dc3545",
                                                    "critical": "#721c24",
                                                }.get(rule.severity, "#6c757d"),
                                            },
                                        ),
                                    ],
                                    className="d-flex justify-content-between align-items-center",
                                )
                            ]
                        ),
                        dbc.CardBody(
                            [
                                html.P(rule.description),
                                html.P(f"Condition: {rule.condition}"),
                                html.P(f"Parameters: {json.dumps(rule.parameters)}"),
                                html.P(f"Notifiers: {', '.join(rule.notifiers)}"),
                                dbc.Button(
                                    "Remove",
                                    id={"type": "remove-rule-button", "index": rule.id},
                                    color="danger",
                                    size="sm",
                                    className="mt-2",
                                ),
                            ]
                        ),
                    ],
                    className="mb-3",
                )
            )

        if not rules:
            return html.Div("No alert rules configured", className="text-muted")

        return rules

    @app.callback(
        Output("active-alerts-list", "children"),
        [Input("alert-refresh-interval", "n_intervals")],
    )
    def update_active_alerts(n_intervals):
        """
        Update active alerts list.

        Returns:
            List of active alert components

        """
        if not hasattr(app, "alerts") or not app.alerts:
            return html.Div("No active alerts", className="text-muted")

        # Sort alerts by time (newest first)
        sorted_alerts = sorted(app.alerts, key=lambda x: x["time"], reverse=True)

        # Create alert cards
        alert_cards = []
        for alert in sorted_alerts:
            alert_cards.append(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            alert["name"],
                                            className="me-2",
                                        ),
                                        html.Span(
                                            alert["severity"].upper(),
                                            className="badge",
                                            style={
                                                "backgroundColor": {
                                                    "info": "#17a2b8",
                                                    "warning": "#ffc107",
                                                    "error": "#dc3545",
                                                    "critical": "#721c24",
                                                }.get(alert["severity"], "#6c757d"),
                                            },
                                        ),
                                        html.Span(
                                            datetime.datetime.fromisoformat(alert["time"]).strftime("%Y-%m-%d %H:%M:%S"),
                                            className="ms-auto text-muted",
                                        ),
                                    ],
                                    className="d-flex justify-content-between align-items-center",
                                )
                            ]
                        ),
                        dbc.CardBody(
                            [
                                html.P(alert["description"]),
                                html.Div(
                                    [
                                        html.H6("Context:"),
                                        html.Pre(
                                            json.dumps(alert["context"], indent=2),
                                            style={"whiteSpace": "pre-wrap"},
                                        ),
                                    ]
                                ),
                                dbc.Button(
                                    "Mark as Read",
                                    id={"type": "mark-read-button", "index": alert["id"]},
                                    color="primary",
                                    size="sm",
                                    className="mt-2 me-2",
                                ),
                                dbc.Button(
                                    "Dismiss",
                                    id={"type": "dismiss-alert-button", "index": alert["id"]},
                                    color="danger",
                                    size="sm",
                                    className="mt-2",
                                ),
                            ]
                        ),
                    ],
                    className="mb-3",
                    color="warning" if not alert["read"] else None,
                    outline=True,
                )
            )

        return alert_cards

    @app.callback(
        Output("alerts-store", "data"),
        [Input({"type": "mark-read-button", "index": ALL}, "n_clicks"),
         Input({"type": "dismiss-alert-button", "index": ALL}, "n_clicks")],
        [State({"type": "mark-read-button", "index": ALL}, "id"),
         State({"type": "dismiss-alert-button", "index": ALL}, "id")],
    )
    def handle_alert_actions(mark_read_clicks, dismiss_clicks, mark_read_ids, dismiss_ids):
        """
        Handle alert actions (mark as read, dismiss).

        Returns:
            Updated alerts data

        """
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Parse the JSON from the string
        if "{" in triggered_id:
            button_data = json.loads(triggered_id)
            button_type = button_data["type"]
            alert_id = button_data["index"]

            # Handle mark as read
            if button_type == "mark-read-button":
                for alert in app.alerts:
                    if alert["id"] == alert_id:
                        alert["read"] = True
                        break

            # Handle dismiss
            elif button_type == "dismiss-alert-button":
                app.alerts = [alert for alert in app.alerts if alert["id"] != alert_id]

        return app.alerts

    @app.callback(
        Output("alert-rules-list", "children", allow_duplicate=True),
        [Input({"type": "remove-rule-button", "index": ALL}, "n_clicks")],
        [State({"type": "remove-rule-button", "index": ALL}, "id")],
        prevent_initial_call=True,
    )
    def handle_remove_rule(n_clicks, button_ids):
        """
        Handle remove rule button clicks.

        Returns:
            Updated alert rules list

        """
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Parse the JSON from the string
        if "{" in triggered_id:
            button_data = json.loads(triggered_id)
            rule_id = button_data["index"]

            # Remove the rule
            app.alert_system.remove_rule(rule_id)

        # Create list of current rules
        rules = []
        for rule in app.alert_system.rules:
            rules.append(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            rule.name,
                                            className="me-2",
                                        ),
                                        html.Span(
                                            rule.severity.upper(),
                                            className="badge",
                                            style={
                                                "backgroundColor": {
                                                    "info": "#17a2b8",
                                                    "warning": "#ffc107",
                                                    "error": "#dc3545",
                                                    "critical": "#721c24",
                                                }.get(rule.severity, "#6c757d"),
                                            },
                                        ),
                                    ],
                                    className="d-flex justify-content-between align-items-center",
                                )
                            ]
                        ),
                        dbc.CardBody(
                            [
                                html.P(rule.description),
                                html.P(f"Condition: {rule.condition}"),
                                html.P(f"Parameters: {json.dumps(rule.parameters)}"),
                                html.P(f"Notifiers: {', '.join(rule.notifiers)}"),
                                dbc.Button(
                                    "Remove",
                                    id={"type": "remove-rule-button", "index": rule.id},
                                    color="danger",
                                    size="sm",
                                    className="mt-2",
                                ),
                            ]
                        ),
                    ],
                    className="mb-3",
                )
            )

        if not rules:
            return html.Div("No alert rules configured", className="text-muted")

        return rules

    @app.callback(
        [
            Output("ml-analysis-spinner", "children"),
            Output("ml-analysis-status", "children"),
            Output("ml-analysis-store", "data"),
        ],
        [Input("run-ml-analysis-button", "n_clicks")],
        [State("log-entries-store", "data")],
    )
    @require_permission("run_ml_analysis")
    def run_ml_analysis(n_clicks, log_entries):
        """
        Run machine learning analysis on log entries.

        Args:
            n_clicks: Number of button clicks
            log_entries: List of log entries

        Returns:
            Spinner children, status message, and analysis results

        """
        if not n_clicks:
            return None, "", None

        if not log_entries:
            return None, html.Div("No log entries to analyze", className="text-danger"), None

        # Run analysis
        try:
            # Update status
            status = html.Div(
                f"Analyzing {len(log_entries)} log entries...",
                className="text-info",
            )

            # Run analysis
            results = app.log_analyzer.analyze_logs(log_entries)

            # Update app state
            app.ml_analysis_results = {
                "anomalies": results["anomalies"],
                "patterns": results["patterns"],
                "clusters": results["clusters"],
                "last_analyzed": datetime.datetime.now().isoformat(),
            }

            # Update status
            status = html.Div(
                [
                    html.Span("Analysis complete. "),
                    html.Span(f"Found {len(results['anomalies'])} anomalies, "),
                    html.Span(f"{len(results['patterns'])} patterns, and "),
                    html.Span(f"{len(results['clusters'])} clusters."),
                ],
                className="text-success",
            )

            return None, status, app.ml_analysis_results
        except Exception as e:
            # Update status
            status = html.Div(
                f"Error running analysis: {e!s}",
                className="text-danger",
            )

            return None, status, None

    @app.callback(
        Output("anomaly-detection-results", "children"),
        [Input("ml-analysis-store", "data")],
    )
    def update_anomaly_detection_results(analysis_results):
        """
        Update anomaly detection results.

        Args:
            analysis_results: Analysis results

        Returns:
            Anomaly detection results components

        """
        if not analysis_results or "anomalies" not in analysis_results:
            return html.Div("No anomaly detection results available", className="text-muted")

        anomalies = analysis_results["anomalies"]

        if not anomalies:
            return html.Div("No anomalies detected", className="text-success")

        # Create anomaly cards
        anomaly_cards = []
        for i, anomaly in enumerate(anomalies[:10]):  # Limit to 10 anomalies
            anomaly_cards.append(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            f"Anomaly #{i+1}",
                                            className="me-2",
                                        ),
                                        html.Span(
                                            anomaly.get("level", "UNKNOWN"),
                                            className="badge",
                                            style={
                                                "backgroundColor": LOG_COLORS.get(
                                                    anomaly.get("level", "INFO"), "#6c757d"
                                                ),
                                            },
                                        ),
                                        html.Span(
                                            f"Score: {anomaly.get('anomaly_score', 0):.3f}",
                                            className="ms-auto",
                                        ),
                                    ],
                                    className="d-flex justify-content-between align-items-center",
                                )
                            ]
                        ),
                        dbc.CardBody(
                            [
                                html.P(
                                    anomaly.get("message", ""),
                                    style={"whiteSpace": "pre-wrap"},
                                ),
                                html.Div(
                                    [
                                        html.H6("Features:"),
                                        html.Pre(
                                            json.dumps(
                                                anomaly.get("feature_values", {}),
                                                indent=2,
                                            ),
                                            style={"whiteSpace": "pre-wrap"},
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    className="mb-3",
                    color="danger",
                    outline=True,
                )
            )

        return html.Div(
            [
                html.H5(f"Found {len(anomalies)} anomalies"),
                html.Div(anomaly_cards),
            ]
        )

    @app.callback(
        Output("pattern-recognition-results", "children"),
        [Input("ml-analysis-store", "data")],
    )
    def update_pattern_recognition_results(analysis_results):
        """
        Update pattern recognition results.

        Args:
            analysis_results: Analysis results

        Returns:
            Pattern recognition results components

        """
        if not analysis_results or "patterns" not in analysis_results:
            return html.Div("No pattern recognition results available", className="text-muted")

        patterns = analysis_results["patterns"]

        if not patterns:
            return html.Div("No patterns recognized", className="text-muted")

        # Create pattern cards
        pattern_cards = []
        for i, pattern in enumerate(patterns[:10]):  # Limit to 10 patterns
            # Get examples
            examples = pattern.get("examples", [])
            example_items = []
            for example in examples[:3]:  # Limit to 3 examples
                example_items.append(
                    html.Li(
                        example.get("message", ""),
                        style={"whiteSpace": "pre-wrap"},
                    )
                )

            pattern_cards.append(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            f"Pattern: {pattern.get('pattern', '')}",
                                            className="me-2",
                                        ),
                                        html.Span(
                                            f"Count: {pattern.get('count', 0)}",
                                            className="ms-auto",
                                        ),
                                    ],
                                    className="d-flex justify-content-between align-items-center",
                                )
                            ]
                        ),
                        dbc.CardBody(
                            [
                                html.H6("Examples:"),
                                html.Ul(example_items),
                            ]
                        ),
                    ],
                    className="mb-3",
                )
            )

        return html.Div(
            [
                html.H5(f"Found {len(patterns)} patterns"),
                html.Div(pattern_cards),
            ]
        )

    @app.callback(
        Output("log-clustering-results", "children"),
        [Input("ml-analysis-store", "data")],
    )
    def update_log_clustering_results(analysis_results):
        """
        Update log clustering results.

        Args:
            analysis_results: Analysis results

        Returns:
            Log clustering results components

        """
        if not analysis_results or "clusters" not in analysis_results:
            return html.Div("No log clustering results available", className="text-muted")

        clusters = analysis_results["clusters"]

        if not clusters:
            return html.Div("No clusters found", className="text-muted")

        # Create cluster cards
        cluster_cards = []
        for i, cluster in enumerate(clusters):
            # Get example items
            examples = cluster.get("examples", [])
            example_items = [html.Li(example) for example in examples[:3]]

            cluster_cards.append(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            f"Cluster #{cluster.get('cluster_id', i)}",
                                            className="me-2",
                                        ),
                                        html.Span(
                                            f"Size: {cluster.get('size', 0)}",
                                            className="ms-auto",
                                        ),
                                    ],
                                    className="d-flex justify-content-between align-items-center",
                                )
                            ]
                        ),
                        dbc.CardBody(
                            [
                                html.H6("Common Terms:"),
                                html.P(", ".join(cluster.get("common_terms", []))),
                                html.H6("Examples:"),
                                html.Ul(example_items),
                            ]
                        ),
                    ],
                    className="mb-3",
                )
            )

        return html.Div(
            [
                html.H5(f"Found {len(clusters)} clusters"),
                html.Div(cluster_cards),
            ]
        )

    # User Management Callbacks
    @app.callback(
        Output("new-user-roles", "options"),
        [Input("user-management-store", "data")],
    )
    @require_permission("manage_users")
    def update_role_options(data):
        """
        Update role options for new user form.

        Args:
            data: User management data

        Returns:
            Role options

        """
        roles = list(app.auth.roles.values())
        return [{"label": role.name, "value": role.name} for role in roles]

    @app.callback(
        Output("new-role-permissions", "options"),
        [Input("user-management-store", "data")],
    )
    @require_permission("manage_roles")
    def update_permission_options(data):
        """
        Update permission options for new role form.

        Args:
            data: User management data

        Returns:
            Permission options

        """
        permissions = list(app.auth.permissions.values())
        return [{"label": perm.name, "value": perm.name} for perm in permissions]

    @app.callback(
        [
            Output("user-list", "children"),
            Output("user-management-store", "data"),
        ],
        [
            Input("add-user-button", "n_clicks"),
            Input("refresh-audit-logs-button", "n_clicks"),
        ],
        [
            State("new-user-username", "value"),
            State("new-user-password", "value"),
            State("new-user-roles", "value"),
            State("user-management-store", "data"),
        ],
    )
    @require_permission("manage_users")
    def manage_users(add_clicks, refresh_clicks, username, password, roles, data):
        """
        Manage users.

        Args:
            add_clicks: Add user button clicks
            refresh_clicks: Refresh button clicks
            username: New username
            password: New password
            roles: New user roles
            data: User management data

        Returns:
            User list and updated data

        """
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

        # Initialize data if None
        if data is None:
            data = {"last_updated": datetime.datetime.now().isoformat()}

        # Add user
        if triggered_id == "add-user-button" and add_clicks:
            if username and password:
                # Check if user already exists
                if username in app.auth.users:
                    return html.Div(f"User {username} already exists", className="text-danger"), data

                # Add user
                app.auth.add_user(
                    User(
                        username=username,
                        password_hash=app.auth.hash_password(password),
                        roles=roles or [],
                    )
                )

                # Log audit event
                app.auth.log_audit_event("user_created", session["auth"]["username"], {
                    "created_username": username,
                    "roles": roles or [],
                })

                # Update data
                data["last_updated"] = datetime.datetime.now().isoformat()

        # Create user list
        users = list(app.auth.users.values())

        if not users:
            return html.Div("No users found"), data

        # Create user cards
        user_cards = []
        for user in users:
            # Get user permissions
            permissions = app.auth.get_user_permissions(user.username)

            user_cards.append(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5(user.username),
                        ),
                        dbc.CardBody(
                            [
                                html.P(f"Roles: {', '.join(user.roles) if user.roles else 'None'}"),
                                html.P(f"Permissions: {', '.join(permissions) if permissions else 'None'}"),
                                html.P(f"Last Login: {user.last_login or 'Never'}"),
                                html.P(f"Active: {'Yes' if user.is_active else 'No'}"),
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "Edit",
                                            id={"type": "edit-user-button", "index": user.username},
                                            color="primary",
                                            className="me-2",
                                        ),
                                        dbc.Button(
                                            "Deactivate" if user.is_active else "Activate",
                                            id={"type": "toggle-user-button", "index": user.username},
                                            color="warning" if user.is_active else "success",
                                            className="me-2",
                                        ),
                                        dbc.Button(
                                            "Delete",
                                            id={"type": "delete-user-button", "index": user.username},
                                            color="danger",
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    className="mb-3",
                )
            )

        return html.Div(user_cards), data

    @app.callback(
        [
            Output("role-list", "children"),
            Output("add-role-status", "children"),
        ],
        [
            Input("add-role-button", "n_clicks"),
            Input("user-management-store", "data"),
        ],
        [
            State("new-role-name", "value"),
            State("new-role-description", "value"),
            State("new-role-permissions", "value"),
        ],
    )
    @require_permission("manage_roles")
    def manage_roles(add_clicks, data, name, description, permissions):
        """
        Manage roles.

        Args:
            add_clicks: Add role button clicks
            data: User management data
            name: New role name
            description: New role description
            permissions: New role permissions

        Returns:
            Role list and status

        """
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

        status = None

        # Add role
        if triggered_id == "add-role-button" and add_clicks:
            if name:
                # Check if role already exists
                if name in app.auth.roles:
                    status = html.Div(f"Role {name} already exists", className="text-danger")
                else:
                    # Add role
                    app.auth.add_role(
                        Role(
                            name=name,
                            permissions=permissions or [],
                            description=description,
                        )
                    )

                    # Log audit event
                    app.auth.log_audit_event("role_created", session["auth"]["username"], {
                        "role_name": name,
                        "permissions": permissions or [],
                    })

                    status = html.Div(f"Role {name} added successfully", className="text-success")

        # Create role list
        roles = list(app.auth.roles.values())

        if not roles:
            return html.Div("No roles found"), status

        # Create role cards
        role_cards = []
        for role in roles:
            role_cards.append(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5(role.name),
                        ),
                        dbc.CardBody(
                            [
                                html.P(f"Description: {role.description or 'None'}"),
                                html.P(f"Permissions: {', '.join(role.permissions) if role.permissions else 'None'}"),
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "Edit",
                                            id={"type": "edit-role-button", "index": role.name},
                                            color="primary",
                                            className="me-2",
                                        ),
                                        dbc.Button(
                                            "Delete",
                                            id={"type": "delete-role-button", "index": role.name},
                                            color="danger",
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    className="mb-3",
                )
            )

        return html.Div(role_cards), status

    # Callback for dashboard dropdown menu
    @app.callback(
        Output("selected-dashboard-container", "children"),
        [
            Input("dashboard-main", "n_clicks"),
            Input("dashboard-error", "n_clicks"),
            Input("dashboard-performance", "n_clicks"),
            Input("dashboard-security", "n_clicks"),
            Input("dashboard-service-health", "n_clicks"),
        ],
    )
    def switch_dashboard(*args):
        """
        Switch between predefined dashboards based on dropdown selection.

        Returns:
            Selected dashboard layout

        """
        ctx = dash.callback_context
        if not ctx.triggered:
            # Default to empty on initial load
            return []

        # Get the ID of the clicked dropdown item
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Return the appropriate dashboard layout based on the clicked item
        if button_id == "dashboard-error":
            return get_dashboard_layout("error_monitoring")
        if button_id == "dashboard-performance":
            return get_dashboard_layout("performance_monitoring")
        if button_id == "dashboard-security":
            return get_dashboard_layout("security_monitoring")
        if button_id == "dashboard-service-health":
            return get_dashboard_layout("service_health")
        if button_id == "dashboard-main":
            # Return the main dashboard (could be a custom layout or empty)
            return html.Div([
                html.H3("Main Dashboard", className="text-center mb-4"),
                html.P("Select a specialized dashboard from the dropdown menu or use the tabs below for detailed log analysis.")
            ])

        # Default case
        return []

    # Predefined Dashboards Callbacks
    @app.callback(
        Output("error-monitoring-dashboard", "children"),
        [Input("predefined-dashboards-tabs", "active_tab")],
    )
    def load_error_monitoring_dashboard(active_tab):
        """
        Load the error monitoring dashboard.

        Args:
            active_tab: Active tab

        Returns:
            Dashboard layout

        """
        if active_tab == "tab-error-monitoring":
            return get_dashboard_layout("error_monitoring")
        return []

    @app.callback(
        Output("performance-monitoring-dashboard", "children"),
        [Input("predefined-dashboards-tabs", "active_tab")],
    )
    def load_performance_monitoring_dashboard(active_tab):
        """
        Load the performance monitoring dashboard.

        Args:
            active_tab: Active tab

        Returns:
            Dashboard layout

        """
        if active_tab == "tab-performance-monitoring":
            return get_dashboard_layout("performance_monitoring")
        return []

    @app.callback(
        Output("security-monitoring-dashboard", "children"),
        [Input("predefined-dashboards-tabs", "active_tab")],
    )
    def load_security_monitoring_dashboard(active_tab):
        """
        Load the security monitoring dashboard.

        Args:
            active_tab: Active tab

        Returns:
            Dashboard layout

        """
        if active_tab == "tab-security-monitoring":
            return get_dashboard_layout("security_monitoring")
        return []

    @app.callback(
        Output("service-health-dashboard", "children"),
        [Input("predefined-dashboards-tabs", "active_tab")],
    )
    def load_service_health_dashboard(active_tab):
        """
        Load the service health dashboard.

        Args:
            active_tab: Active tab

        Returns:
            Dashboard layout

        """
        if active_tab == "tab-service-health":
            return get_dashboard_layout("service_health")
        return []

    # Callbacks for individual dashboard components

    # Error Monitoring Dashboard Callbacks
    @app.callback(
        Output("error-rate-graph", "figure"),
        [Input("selected-dashboard-container", "children")],
    )
    def update_error_rate_graph(dashboard):
        """
        Update the error rate graph.

        Args:
            dashboard: Selected dashboard

        Returns:
            Error rate graph figure

        """
        # This is a placeholder for actual implementation
        # In a real implementation, you would fetch data and create a figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3, 4, 5], y=[0.01, 0.03, 0.02, 0.05, 0.01],
                                mode="lines+markers", name="Error Rate"))
        fig.update_layout(title="Error Rate Over Time",
                        xaxis_title="Time",
                        yaxis_title="Error Rate")
        return fig

    @app.callback(
        Output("error-module-distribution", "figure"),
        [Input("selected-dashboard-container", "children")],
    )
    def update_error_module_distribution(dashboard):
        """
        Update the error module distribution graph.

        Args:
            dashboard: Selected dashboard

        Returns:
            Error module distribution figure

        """
        # This is a placeholder for actual implementation
        fig = go.Figure(data=[go.Bar(
            x=["Module A", "Module B", "Module C", "Module D"],
            y=[10, 5, 15, 8]
        )])
        fig.update_layout(title="Error Distribution by Module",
                        xaxis_title="Module",
                        yaxis_title="Error Count")
        return fig

    # Performance Monitoring Dashboard Callbacks
    @app.callback(
        Output("api-latency-graph", "figure"),
        [Input("selected-dashboard-container", "children")],
    )
    def update_api_latency_graph(dashboard):
        """
        Update the API latency graph.

        Args:
            dashboard: Selected dashboard

        Returns:
            API latency graph figure

        """
        # This is a placeholder for actual implementation
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3, 4, 5], y=[120, 150, 100, 180, 130],
                                mode="lines+markers", name="API Latency"))
        fig.update_layout(title="API Latency Over Time",
                        xaxis_title="Time",
                        yaxis_title="Latency (ms)")
        return fig

    # Security Monitoring Dashboard Callbacks
    @app.callback(
        Output("auth-attempts-graph", "figure"),
        [Input("selected-dashboard-container", "children")],
    )
    def update_auth_attempts_graph(dashboard):
        """
        Update the authentication attempts graph.

        Args:
            dashboard: Selected dashboard

        Returns:
            Authentication attempts graph figure

        """
        # This is a placeholder for actual implementation
        fig = go.Figure()
        fig.add_trace(go.Bar(x=["Success", "Failure"], y=[85, 15], name="Authentication Attempts"))
        fig.update_layout(title="Authentication Attempts",
                        xaxis_title="Result",
                        yaxis_title="Count")
        return fig

    # Service Health Dashboard Callbacks
    @app.callback(
        Output("service-uptime-graph", "figure"),
        [Input("selected-dashboard-container", "children")],
    )
    def update_service_uptime_graph(dashboard):
        """
        Update the service uptime graph.

        Args:
            dashboard: Selected dashboard

        Returns:
            Service uptime graph figure

        """
        # This is a placeholder for actual implementation
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = 99.8,
            title = {"text": "Uptime (%)"},
            gauge = {
                "axis": {"range": [None, 100]},
                "bar": {"color": "green"},
                "steps": [
                    {"range": [0, 90], "color": "red"},
                    {"range": [90, 99], "color": "yellow"},
                    {"range": [99, 100], "color": "green"}
                ]
            }
        ))
        return fig

    # Audit logs callback (moved from above)
    @app.callback(
        Output("audit-log-list", "children"),
        [Input("refresh-audit-logs-button", "n_clicks")],
    )
    @require_permission("manage_settings")
    def display_audit_logs(n_clicks):
        """
        Display audit logs.

        Args:
            n_clicks: Refresh button clicks

        Returns:
            Audit log list

        """
        if not app.auth.audit_logging_enabled:
            return html.Div("Audit logging is not enabled", className="text-warning")

        # Get audit logs
        logs = app.auth.get_audit_logs(limit=100)

        if not logs:
            return html.Div("No audit logs found")

        # Create audit log table
        return dash_table.DataTable(
            id="audit-log-table",
            columns=[
                {"name": "Timestamp", "id": "timestamp"},
                {"name": "Event Type", "id": "event_type"},
                {"name": "Username", "id": "username"},
                {"name": "IP Address", "id": "ip_address"},
                {"name": "Details", "id": "details"},
            ],
            data=[
                {
                    "timestamp": log["timestamp"],
                    "event_type": log["event_type"],
                    "username": log["username"] or "N/A",
                    "ip_address": log["ip_address"] or "N/A",
                    "details": json.dumps(log["details"]) if log["details"] else "N/A",
                }
                for log in logs
            ],
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "padding": "10px",
            },
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
            },
            page_size=10,
        )


def main() -> int:
    """Main function."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Advanced Log Dashboard for pAIssive_income")
    parser.add_argument("--port", type=int, default=8050, help="Port to run the dashboard on")
    parser.add_argument("--log-dir", type=str, default=".", help="Directory containing log files")
    parser.add_argument("--es-host", type=str, help="Elasticsearch host for advanced analytics")
    parser.add_argument("--es-port", type=int, default=9200, help="Elasticsearch port")
    parser.add_argument("--refresh", type=int, default=30, help="Refresh interval in seconds")
    parser.add_argument("--theme", type=str, default="light", choices=list(THEMES.keys()), help="Dashboard theme")
    parser.add_argument("--enable-auth", action="store_true", help="Enable authentication")
    parser.add_argument("--secret-key", type=str, help="Secret key for authentication")
    parser.add_argument("--session-expiry", type=int, default=3600, help="Session expiry time in seconds")
    parser.add_argument("--disable-csrf", action="store_true", help="Disable CSRF protection")
    parser.add_argument("--disable-rate-limit", action="store_true", help="Disable rate limiting for authentication")
    parser.add_argument("--max-auth-attempts", type=int, default=5, help="Maximum number of failed authentication attempts")
    parser.add_argument("--lockout-time", type=int, default=300, help="Lockout time in seconds after max failed attempts")
    parser.add_argument("--disable-audit-logging", action="store_true", help="Disable audit logging for security events")
    args = parser.parse_args()

    # Check if log directory exists
    if not os.path.isdir(args.log_dir):
        logger.error(f"Log directory does not exist: {args.log_dir}")
        return 1

    # Check if log files exist
    log_files = get_log_files(args.log_dir)
    if not log_files:
        logger.warning(f"No log files found in directory: {args.log_dir}")

    # Check Elasticsearch connection if provided
    if args.es_host and ELASTICSEARCH_AVAILABLE:
        try:
            es = Elasticsearch([f"http://{args.es_host}:{args.es_port}"])
            if es.ping():
                logger.info(f"Successfully connected to Elasticsearch at {args.es_host}:{args.es_port}")
            else:
                logger.warning(f"Could not ping Elasticsearch at {args.es_host}:{args.es_port}")
        except Exception as e:
            logger.warning(f"Error connecting to Elasticsearch: {e}")

    # Create and run dashboard
    app = create_dashboard(
        log_dir=args.log_dir,
        es_host=args.es_host,
        es_port=args.es_port,
        refresh_interval=args.refresh,
        enable_auth=args.enable_auth,
        secret_key=args.secret_key,
        session_expiry=args.session_expiry,
        enable_csrf_protection=not args.disable_csrf,
        rate_limit_auth=not args.disable_rate_limit,
        max_auth_attempts=args.max_auth_attempts,
        lockout_time=args.lockout_time,
        audit_logging=not args.disable_audit_logging,
    )

    # Set theme
    app.external_stylesheets = [THEMES.get(args.theme, dbc.themes.BOOTSTRAP)]

    # Start the server
    logger.info(f"Starting log dashboard on http://localhost:{args.port}")
    logger.info(f"Using theme: {args.theme}")
    logger.info(f"Refresh interval: {args.refresh} seconds")

    app.run_server(debug=True, port=args.port)

    return 0

if __name__ == "__main__":
    sys.exit(main())

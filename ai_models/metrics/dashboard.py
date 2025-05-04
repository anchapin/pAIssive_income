
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import List, Optional

from ai_models.metrics import EnhancedPerformanceMonitor


class MetricsDashboard:
    import jinja2
    import matplotlib
    import pandas
    import plotly
    import plotly.express
    import plotly.graph_objects
    from plotly.subplots import make_subplots
except ImportError
    import jinja2
    import pandas
    import plotly.express
    import plotly.graph_objects

    """
    """
    Dashboard generation for model performance metrics.
    Dashboard generation for model performance metrics.


    This module provides tools for generating interactive dashboards and reports
    This module provides tools for generating interactive dashboards and reports
    to visualize model performance metrics, token usage, and cost data.
    to visualize model performance metrics, token usage, and cost data.
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
    :
    :
    """
    """
    Dashboard generator for model performance metrics.
    Dashboard generator for model performance metrics.


    This class provides functionality to generate interactive dashboards and reports
    This class provides functionality to generate interactive dashboards and reports
    for visualizing model performance metrics, both as HTML reports and charts.
    for visualizing model performance metrics, both as HTML reports and charts.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    performance_monitor: Optional[EnhancedPerformanceMonitor] = None,
    performance_monitor: Optional[EnhancedPerformanceMonitor] = None,
    output_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    ):
    ):
    """
    """
    Initialize the dashboard generator.
    Initialize the dashboard generator.


    Args:
    Args:
    performance_monitor: Performance monitor instance to use
    performance_monitor: Performance monitor instance to use
    output_dir: Directory to save dashboard files (default: ./model_dashboards)
    output_dir: Directory to save dashboard files (default: ./model_dashboards)
    """
    """
    self.performance_monitor = performance_monitor or EnhancedPerformanceMonitor()
    self.performance_monitor = performance_monitor or EnhancedPerformanceMonitor()
    self.output_dir = output_dir or os.path.join(os.getcwd(), "model_dashboards")
    self.output_dir = output_dir or os.path.join(os.getcwd(), "model_dashboards")
    os.makedirs(self.output_dir, exist_ok=True)
    os.makedirs(self.output_dir, exist_ok=True)


    # Check for dependencies
    # Check for dependencies
    self._check_dependencies()
    self._check_dependencies()


    def _check_dependencies(self) -> None:
    def _check_dependencies(self) -> None:
    """Check if required packages for visualization are installed."""
    missing_deps = []

    try:

except ImportError:
    missing_deps.append("matplotlib")

    try:

except ImportError:
    missing_deps.append("pandas")

    try:

except ImportError:
    missing_deps.append("plotly")

    try:

except ImportError:
    missing_deps.append("jinja2")

    if missing_deps:
    logger.warning(
    f"Missing packages for full dashboard functionality: {', '.join(missing_deps)}. "
    f"Install with: pip install {' '.join(missing_deps)}"
    )

    def generate_model_dashboard(
    self,
    model_id: str,
    days: int = 30,
    include_token_usage: bool = True,
    include_latency: bool = True,
    include_cost: bool = True,
    include_errors: bool = True,
    ) -> str:
    """
    """
    Generate a comprehensive dashboard for a model.
    Generate a comprehensive dashboard for a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    days: Number of days of data to include
    days: Number of days of data to include
    include_token_usage: Whether to include token usage charts
    include_token_usage: Whether to include token usage charts
    include_latency: Whether to include latency/performance charts
    include_latency: Whether to include latency/performance charts
    include_cost: Whether to include cost charts
    include_cost: Whether to include cost charts
    include_errors: Whether to include error charts
    include_errors: Whether to include error charts


    Returns:
    Returns:
    Path to the generated dashboard HTML file
    Path to the generated dashboard HTML file
    """
    """
    try:
    try:


    as pd
    as pd
    as px
    as px
    as go
    as go
    :
    :
    logger.error(
    logger.error(
    "Dashboard generation requires additional packages. Install with: "
    "Dashboard generation requires additional packages. Install with: "
    "pip install pandas plotly jinja2"
    "pip install pandas plotly jinja2"
    )
    )
    return ""
    return ""


    # Get time range
    # Get time range
    end_time = datetime.now()
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    start_time = end_time - timedelta(days=days)
    time_range = (start_time, end_time)
    time_range = (start_time, end_time)


    # Get metrics data
    # Get metrics data
    metrics_data = self.performance_monitor.metrics_db.get_metrics(
    metrics_data = self.performance_monitor.metrics_db.get_metrics(
    model_id=model_id, time_range=time_range, limit=10000
    model_id=model_id, time_range=time_range, limit=10000
    )
    )


    if not metrics_data:
    if not metrics_data:
    logger.warning(
    logger.warning(
    f"No metrics found for model {model_id} in the last {days} days"
    f"No metrics found for model {model_id} in the last {days} days"
    )
    )
    return ""
    return ""


    # Generate report
    # Generate report
    report = self.performance_monitor.generate_enhanced_report(
    report = self.performance_monitor.generate_enhanced_report(
    model_id=model_id, time_range=time_range, include_metrics=True
    model_id=model_id, time_range=time_range, include_metrics=True
    )
    )


    # Process metrics for visualization
    # Process metrics for visualization
    df = pd.DataFrame(metrics_data)
    df = pd.DataFrame(metrics_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df = df.sort_values("timestamp")


    # Extract token usage and cost data from metadata
    # Extract token usage and cost data from metadata
    token_data = []
    token_data = []
    for metric in metrics_data:
    for metric in metrics_data:
    if not isinstance(metric.get("metadata"), dict):
    if not isinstance(metric.get("metadata"), dict):
    continue
    continue


    token_usage = metric.get("metadata", {}).get("token_usage", {})
    token_usage = metric.get("metadata", {}).get("token_usage", {})
    if token_usage:
    if token_usage:
    entry = {
    entry = {
    "timestamp": pd.to_datetime(metric["timestamp"]),
    "timestamp": pd.to_datetime(metric["timestamp"]),
    "prompt_tokens": token_usage.get("prompt_tokens", 0),
    "prompt_tokens": token_usage.get("prompt_tokens", 0),
    "completion_tokens": token_usage.get("completion_tokens", 0),
    "completion_tokens": token_usage.get("completion_tokens", 0),
    "total_tokens": token_usage.get("total_tokens", 0),
    "total_tokens": token_usage.get("total_tokens", 0),
    "prompt_cost": token_usage.get("prompt_cost", 0.0),
    "prompt_cost": token_usage.get("prompt_cost", 0.0),
    "completion_cost": token_usage.get("completion_cost", 0.0),
    "completion_cost": token_usage.get("completion_cost", 0.0),
    "total_cost": token_usage.get("total_cost", 0.0),
    "total_cost": token_usage.get("total_cost", 0.0),
    }
    }
    token_data.append(entry)
    token_data.append(entry)


    token_df = pd.DataFrame(token_data)
    token_df = pd.DataFrame(token_data)


    # Create plots
    # Create plots
    plots = {}
    plots = {}


    # 1. Latency over time
    # 1. Latency over time
    if include_latency and not df["latency_ms"].isnull().all():
    if include_latency and not df["latency_ms"].isnull().all():
    fig = px.scatter(
    fig = px.scatter(
    df,
    df,
    x="timestamp",
    x="timestamp",
    y="latency_ms",
    y="latency_ms",
    title=f"Latency Over Time ({model_id})",
    title=f"Latency Over Time ({model_id})",
    labels={"latency_ms": "Latency (ms)", "timestamp": "Time"},
    labels={"latency_ms": "Latency (ms)", "timestamp": "Time"},
    color_discrete_sequence=["blue"],
    color_discrete_sequence=["blue"],
    )
    )
    fig.add_trace(
    fig.add_trace(
    go.Scatter(
    go.Scatter(
    x=df["timestamp"],
    x=df["timestamp"],
    y=df["latency_ms"].rolling(10).mean(),
    y=df["latency_ms"].rolling(10).mean(),
    mode="lines",
    mode="lines",
    name="10-point Moving Average",
    name="10-point Moving Average",
    line=dict(color="red", width=2),
    line=dict(color="red", width=2),
    )
    )
    )
    )
    plots["latency_plot"] = fig.to_html(full_html=False, include_plotlyjs=False)
    plots["latency_plot"] = fig.to_html(full_html=False, include_plotlyjs=False)


    # 2. Token usage over time
    # 2. Token usage over time
    if include_token_usage and len(token_df) > 0:
    if include_token_usage and len(token_df) > 0:
    # Create a daily aggregation
    # Create a daily aggregation
    token_df["date"] = token_df["timestamp"].dt.date
    token_df["date"] = token_df["timestamp"].dt.date
    daily_tokens = (
    daily_tokens = (
    token_df.groupby("date")
    token_df.groupby("date")
    .agg(
    .agg(
    {
    {
    "prompt_tokens": "sum",
    "prompt_tokens": "sum",
    "completion_tokens": "sum",
    "completion_tokens": "sum",
    "total_tokens": "sum",
    "total_tokens": "sum",
    }
    }
    )
    )
    .reset_index()
    .reset_index()
    )
    )
    daily_tokens["date"] = pd.to_datetime(daily_tokens["date"])
    daily_tokens["date"] = pd.to_datetime(daily_tokens["date"])


    fig = go.Figure()
    fig = go.Figure()
    fig.add_trace(
    fig.add_trace(
    go.Bar(
    go.Bar(
    x=daily_tokens["date"],
    x=daily_tokens["date"],
    y=daily_tokens["prompt_tokens"],
    y=daily_tokens["prompt_tokens"],
    name="Prompt Tokens",
    name="Prompt Tokens",
    marker_color="lightblue",
    marker_color="lightblue",
    )
    )
    )
    )
    fig.add_trace(
    fig.add_trace(
    go.Bar(
    go.Bar(
    x=daily_tokens["date"],
    x=daily_tokens["date"],
    y=daily_tokens["completion_tokens"],
    y=daily_tokens["completion_tokens"],
    name="Completion Tokens",
    name="Completion Tokens",
    marker_color="darkblue",
    marker_color="darkblue",
    )
    )
    )
    )
    fig.update_layout(
    fig.update_layout(
    title=f"Daily Token Usage ({model_id})",
    title=f"Daily Token Usage ({model_id})",
    xaxis_title="Date",
    xaxis_title="Date",
    yaxis_title="Tokens",
    yaxis_title="Tokens",
    barmode="stack",
    barmode="stack",
    )
    )
    plots["token_usage_plot"] = fig.to_html(
    plots["token_usage_plot"] = fig.to_html(
    full_html=False, include_plotlyjs=False
    full_html=False, include_plotlyjs=False
    )
    )


    # 3. Cost over time
    # 3. Cost over time
    if include_cost and len(token_df) > 0 and token_df["total_cost"].sum() > 0:
    if include_cost and len(token_df) > 0 and token_df["total_cost"].sum() > 0:
    # Create a daily aggregation
    # Create a daily aggregation
    daily_costs = (
    daily_costs = (
    token_df.groupby("date")
    token_df.groupby("date")
    .agg(
    .agg(
    {
    {
    "prompt_cost": "sum",
    "prompt_cost": "sum",
    "completion_cost": "sum",
    "completion_cost": "sum",
    "total_cost": "sum",
    "total_cost": "sum",
    }
    }
    )
    )
    .reset_index()
    .reset_index()
    )
    )


    fig = go.Figure()
    fig = go.Figure()
    fig.add_trace(
    fig.add_trace(
    go.Bar(
    go.Bar(
    x=daily_costs["date"],
    x=daily_costs["date"],
    y=daily_costs["prompt_cost"],
    y=daily_costs["prompt_cost"],
    name="Prompt Cost",
    name="Prompt Cost",
    marker_color="lightgreen",
    marker_color="lightgreen",
    )
    )
    )
    )
    fig.add_trace(
    fig.add_trace(
    go.Bar(
    go.Bar(
    x=daily_costs["date"],
    x=daily_costs["date"],
    y=daily_costs["completion_cost"],
    y=daily_costs["completion_cost"],
    name="Completion Cost",
    name="Completion Cost",
    marker_color="darkgreen",
    marker_color="darkgreen",
    )
    )
    )
    )
    fig.update_layout(
    fig.update_layout(
    title=f"Daily Token Cost ({model_id})",
    title=f"Daily Token Cost ({model_id})",
    xaxis_title="Date",
    xaxis_title="Date",
    yaxis_title="Cost (USD)",
    yaxis_title="Cost (USD)",
    barmode="stack",
    barmode="stack",
    )
    )
    plots["cost_plot"] = fig.to_html(full_html=False, include_plotlyjs=False)
    plots["cost_plot"] = fig.to_html(full_html=False, include_plotlyjs=False)


    # Also create a cumulative cost plot
    # Also create a cumulative cost plot
    daily_costs["cumulative_cost"] = daily_costs["total_cost"].cumsum()
    daily_costs["cumulative_cost"] = daily_costs["total_cost"].cumsum()
    fig = px.line(
    fig = px.line(
    daily_costs,
    daily_costs,
    x="date",
    x="date",
    y="cumulative_cost",
    y="cumulative_cost",
    title=f"Cumulative Cost ({model_id})",
    title=f"Cumulative Cost ({model_id})",
    labels={"cumulative_cost": "Cumulative Cost (USD)", "date": "Date"},
    labels={"cumulative_cost": "Cumulative Cost (USD)", "date": "Date"},
    color_discrete_sequence=["green"],
    color_discrete_sequence=["green"],
    )
    )
    plots["cumulative_cost_plot"] = fig.to_html(
    plots["cumulative_cost_plot"] = fig.to_html(
    full_html=False, include_plotlyjs=False
    full_html=False, include_plotlyjs=False
    )
    )


    # 4. Inference time distributions
    # 4. Inference time distributions
    if "total_time" in df.columns and not df["total_time"].isnull().all():
    if "total_time" in df.columns and not df["total_time"].isnull().all():
    fig = px.histogram(
    fig = px.histogram(
    df,
    df,
    x="total_time",
    x="total_time",
    title=f"Inference Time Distribution ({model_id})",
    title=f"Inference Time Distribution ({model_id})",
    labels={"total_time": "Inference Time (s)"},
    labels={"total_time": "Inference Time (s)"},
    color_discrete_sequence=["purple"],
    color_discrete_sequence=["purple"],
    )
    )
    plots["inference_time_hist"] = fig.to_html(
    plots["inference_time_hist"] = fig.to_html(
    full_html=False, include_plotlyjs=False
    full_html=False, include_plotlyjs=False
    )
    )


    # 5. Error rate over time
    # 5. Error rate over time
    if include_errors and "error_occurred" in df.columns:
    if include_errors and "error_occurred" in df.columns:
    # Group by date and calculate error rate
    # Group by date and calculate error rate
    df["date"] = df["timestamp"].dt.date
    df["date"] = df["timestamp"].dt.date
    daily_errors = (
    daily_errors = (
    df.groupby("date")
    df.groupby("date")
    .agg({"error_occurred": "sum", "model_id": "count"})
    .agg({"error_occurred": "sum", "model_id": "count"})
    .reset_index()
    .reset_index()
    )
    )
    daily_errors["date"] = pd.to_datetime(daily_errors["date"])
    daily_errors["date"] = pd.to_datetime(daily_errors["date"])
    daily_errors["error_rate"] = (
    daily_errors["error_rate"] = (
    daily_errors["error_occurred"] / daily_errors["model_id"]
    daily_errors["error_occurred"] / daily_errors["model_id"]
    )
    )


    if (
    if (
    not daily_errors["error_occurred"].isnull().all()
    not daily_errors["error_occurred"].isnull().all()
    and daily_errors["error_occurred"].sum() > 0
    and daily_errors["error_occurred"].sum() > 0
    ):
    ):
    fig = px.line(
    fig = px.line(
    daily_errors,
    daily_errors,
    x="date",
    x="date",
    y="error_rate",
    y="error_rate",
    title=f"Daily Error Rate ({model_id})",
    title=f"Daily Error Rate ({model_id})",
    labels={"error_rate": "Error Rate", "date": "Date"},
    labels={"error_rate": "Error Rate", "date": "Date"},
    color_discrete_sequence=["red"],
    color_discrete_sequence=["red"],
    )
    )
    plots["error_rate_plot"] = fig.to_html(
    plots["error_rate_plot"] = fig.to_html(
    full_html=False, include_plotlyjs=False
    full_html=False, include_plotlyjs=False
    )
    )


    # Generate HTML dashboard using Jinja2
    # Generate HTML dashboard using Jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))


    # Create a template string within the code instead of requiring an external file
    # Create a template string within the code instead of requiring an external file
    template_str = """
    template_str = """
    <!DOCTYPE html>
    <!DOCTYPE html>
    <html>
    <html>
    <head>
    <head>
    <title>{{ model_id }} - Performance Dashboard</title>
    <title>{{ model_id }} - Performance Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    <style>
    body { padding: 20px; }
    body { padding: 20px; }
    .card { margin-bottom: 20px; }
    .card { margin-bottom: 20px; }
    .summary-card { background-color: #f8f9fa; }
    .summary-card { background-color: #f8f9fa; }
    .plot-container { height: 400px; }
    .plot-container { height: 400px; }
    </style>
    </style>
    </head>
    </head>
    <body>
    <body>
    <div class="container">
    <div class="container">
    <h1>{{ model_id }} - Performance Dashboard</h1>
    <h1>{{ model_id }} - Performance Dashboard</h1>
    <p class="text-muted">Report generated on {{ generation_time }} | Data range: {{ start_date }} to {{ end_date }}</p>
    <p class="text-muted">Report generated on {{ generation_time }} | Data range: {{ start_date }} to {{ end_date }}</p>


    <div class="row">
    <div class="row">
    <div class="col-md-4">
    <div class="col-md-4">
    <div class="card summary-card">
    <div class="card summary-card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Usage Summary</h5>
    <h5 class="card-title">Usage Summary</h5>
    <p class="card-text">Inferences: {{ report.num_inferences }}</p>
    <p class="card-text">Inferences: {{ report.num_inferences }}</p>
    <p class="card-text">Total Tokens: {{ total_tokens }}</p>
    <p class="card-text">Total Tokens: {{ total_tokens }}</p>
    <p class="card-text">Avg. Latency: {{ "%.2"|format(report.avg_latency_ms) }} ms</p>
    <p class="card-text">Avg. Latency: {{ "%.2"|format(report.avg_latency_ms) }} ms</p>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    <div class="col-md-4">
    <div class="col-md-4">
    <div class="card summary-card">
    <div class="card summary-card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Cost Summary</h5>
    <h5 class="card-title">Cost Summary</h5>
    <p class="card-text">Total Cost: ${{ "%.2"|format(total_cost) }}</p>
    <p class="card-text">Total Cost: ${{ "%.2"|format(total_cost) }}</p>
    <p class="card-text">Average Cost: ${{ "%.4"|format(avg_cost_per_inference) }}</p>
    <p class="card-text">Average Cost: ${{ "%.4"|format(avg_cost_per_inference) }}</p>
    <p class="card-text">Cost per 1K Tokens: ${{ "%.4"|format(report.cost_per_1k_tokens or 0) }}</p>
    <p class="card-text">Cost per 1K Tokens: ${{ "%.4"|format(report.cost_per_1k_tokens or 0) }}</p>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    <div class="col-md-4">
    <div class="col-md-4">
    <div class="card summary-card">
    <div class="card summary-card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Performance Summary</h5>
    <h5 class="card-title">Performance Summary</h5>
    <p class="card-text">Avg. Inference Time: {{ "%.2"|format(report.avg_inference_time) }} s</p>
    <p class="card-text">Avg. Inference Time: {{ "%.2"|format(report.avg_inference_time) }} s</p>
    <p class="card-text">Tokens per Second: {{ "%.2"|format(report.avg_tokens_per_second) }}</p>
    <p class="card-text">Tokens per Second: {{ "%.2"|format(report.avg_tokens_per_second) }}</p>
    <p class="card-text">Error Rate: {{ "%.2f"|format(error_rate * 100) }}%</p>
    <p class="card-text">Error Rate: {{ "%.2f"|format(error_rate * 100) }}%</p>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>


    {% if 'latency_plot' in plots %}
    {% if 'latency_plot' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Latency Over Time</h5>
    <h5 class="card-title">Latency Over Time</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.latency_plot | safe }}
    {{ plots.latency_plot | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'token_usage_plot' in plots %}
    {% if 'token_usage_plot' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Token Usage</h5>
    <h5 class="card-title">Token Usage</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.token_usage_plot | safe }}
    {{ plots.token_usage_plot | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'cost_plot' in plots %}
    {% if 'cost_plot' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Cost Analysis</h5>
    <h5 class="card-title">Cost Analysis</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.cost_plot | safe }}
    {{ plots.cost_plot | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'cumulative_cost_plot' in plots %}
    {% if 'cumulative_cost_plot' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Cumulative Cost</h5>
    <h5 class="card-title">Cumulative Cost</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.cumulative_cost_plot | safe }}
    {{ plots.cumulative_cost_plot | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'inference_time_hist' in plots %}
    {% if 'inference_time_hist' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Inference Time Distribution</h5>
    <h5 class="card-title">Inference Time Distribution</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.inference_time_hist | safe }}
    {{ plots.inference_time_hist | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'error_rate_plot' in plots %}
    {% if 'error_rate_plot' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Error Rate</h5>
    <h5 class="card-title">Error Rate</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.error_rate_plot | safe }}
    {{ plots.error_rate_plot | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Detailed Metrics</h5>
    <h5 class="card-title">Detailed Metrics</h5>
    <table class="table table-striped">
    <table class="table table-striped">
    <thead>
    <thead>
    <tr>
    <tr>
    <th>Metric</th>
    <th>Metric</th>
    <th>Value</th>
    <th>Value</th>
    </tr>
    </tr>
    </thead>
    </thead>
    <tbody>
    <tbody>
    {% for key, value in detailed_metrics.items() %}
    {% for key, value in detailed_metrics.items() %}
    <tr>
    <tr>
    <td>{{ key }}</td>
    <td>{{ key }}</td>
    <td>{{ value }}</td>
    <td>{{ value }}</td>
    </tr>
    </tr>
    {% endfor %}
    {% endfor %}
    </tbody>
    </tbody>
    </table>
    </table>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </body>
    </body>
    </html>
    </html>
    """
    """


    template = env.from_string(template_str)
    template = env.from_string(template_str)


    # Prepare template variables
    # Prepare template variables
    total_tokens = report.total_prompt_tokens + report.total_completion_tokens
    total_tokens = report.total_prompt_tokens + report.total_completion_tokens
    total_cost = report.total_prompt_cost + report.total_completion_cost
    total_cost = report.total_prompt_cost + report.total_completion_cost
    avg_cost_per_inference = (
    avg_cost_per_inference = (
    total_cost / report.num_inferences if report.num_inferences > 0 else 0
    total_cost / report.num_inferences if report.num_inferences > 0 else 0
    )
    )
    error_rate = report.error_rate if hasattr(report, "error_rate") else 0
    error_rate = report.error_rate if hasattr(report, "error_rate") else 0


    # Prepare detailed metrics table
    # Prepare detailed metrics table
    detailed_metrics = {}
    detailed_metrics = {}
    for key, value in report.__dict__.items():
    for key, value in report.__dict__.items():
    if isinstance(value, (int, float, str)) and not key.startswith("_"):
    if isinstance(value, (int, float, str)) and not key.startswith("_"):
    if isinstance(value, float):
    if isinstance(value, float):
    # Format float values
    # Format float values
    if abs(value) >= 1000:
    if abs(value) >= 1000:
    formatted_value = f"{value:.2f}"
    formatted_value = f"{value:.2f}"
    else:
    else:
    formatted_value = f"{value:.4f}"
    formatted_value = f"{value:.4f}"
    detailed_metrics[key] = formatted_value
    detailed_metrics[key] = formatted_value
    else:
    else:
    detailed_metrics[key] = value
    detailed_metrics[key] = value


    # Render template
    # Render template
    html_content = template.render(
    html_content = template.render(
    model_id=model_id,
    model_id=model_id,
    report=report,
    report=report,
    plots=plots,
    plots=plots,
    generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    start_date=start_time.strftime("%Y-%m-%d"),
    start_date=start_time.strftime("%Y-%m-%d"),
    end_date=end_time.strftime("%Y-%m-%d"),
    end_date=end_time.strftime("%Y-%m-%d"),
    total_tokens=total_tokens,
    total_tokens=total_tokens,
    total_cost=total_cost,
    total_cost=total_cost,
    avg_cost_per_inference=avg_cost_per_inference,
    avg_cost_per_inference=avg_cost_per_inference,
    error_rate=error_rate,
    error_rate=error_rate,
    detailed_metrics=detailed_metrics,
    detailed_metrics=detailed_metrics,
    )
    )


    # Save dashboard HTML
    # Save dashboard HTML
    filename = f"{model_id}_dashboard_{int(time.time())}.html"
    filename = f"{model_id}_dashboard_{int(time.time())}.html"
    filepath = os.path.join(self.output_dir, filename)
    filepath = os.path.join(self.output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
    with open(filepath, "w", encoding="utf-8") as f:
    f.write(html_content)
    f.write(html_content)


    logger.info(f"Dashboard generated at: {filepath}")
    logger.info(f"Dashboard generated at: {filepath}")
    return filepath
    return filepath


    def generate_model_comparison_dashboard(
    def generate_model_comparison_dashboard(
    self,
    self,
    model_ids: List[str],
    model_ids: List[str],
    model_names: Optional[List[str]] = None,
    model_names: Optional[List[str]] = None,
    days: int = 30,
    days: int = 30,
    ) -> str:
    ) -> str:
    """
    """
    Generate a dashboard comparing multiple models.
    Generate a dashboard comparing multiple models.


    Args:
    Args:
    model_ids: List of model IDs to compare
    model_ids: List of model IDs to compare
    model_names: Optional list of model names
    model_names: Optional list of model names
    days: Number of days of data to include
    days: Number of days of data to include


    Returns:
    Returns:
    Path to the generated comparison dashboard HTML file
    Path to the generated comparison dashboard HTML file
    """
    """
    try:
    try:


    as pd
    as pd
    as px
    as px
    as go
    as go
except ImportError:
except ImportError:
    logger.error(
    logger.error(
    "Dashboard generation requires additional packages. Install with: "
    "Dashboard generation requires additional packages. Install with: "
    "pip install pandas plotly jinja2"
    "pip install pandas plotly jinja2"
    )
    )
    return ""
    return ""


    # Get time range
    # Get time range
    end_time = datetime.now()
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    start_time = end_time - timedelta(days=days)
    time_range = (start_time, end_time)
    time_range = (start_time, end_time)


    # Generate comparison report
    # Generate comparison report
    comparison = self.performance_monitor.compare_models_enhanced(
    comparison = self.performance_monitor.compare_models_enhanced(
    model_ids=model_ids,
    model_ids=model_ids,
    model_names=model_names,
    model_names=model_names,
    time_range=time_range,
    time_range=time_range,
    title="Model Performance Comparison",
    title="Model Performance Comparison",
    )
    )


    # Create individual report for each model for more detailed data
    # Create individual report for each model for more detailed data
    reports = {}
    reports = {}
    for model_id in model_ids:
    for model_id in model_ids:
    report = self.performance_monitor.generate_enhanced_report(
    report = self.performance_monitor.generate_enhanced_report(
    model_id=model_id, time_range=time_range
    model_id=model_id, time_range=time_range
    )
    )
    reports[model_id] = report
    reports[model_id] = report


    # Generate comparison charts
    # Generate comparison charts
    plots = {}
    plots = {}


    # 1. Inference time comparison
    # 1. Inference time comparison
    metrics_to_plot = {
    metrics_to_plot = {
    "avg_inference_time": "Average Inference Time (s)",
    "avg_inference_time": "Average Inference Time (s)",
    "avg_latency_ms": "Average Latency (ms)",
    "avg_latency_ms": "Average Latency (ms)",
    "avg_tokens_per_second": "Tokens per Second",
    "avg_tokens_per_second": "Tokens per Second",
    "cost_per_1k_tokens": "Cost per 1K Tokens ($)",
    "cost_per_1k_tokens": "Cost per 1K Tokens ($)",
    }
    }


    for metric, title in metrics_to_plot.items():
    for metric, title in metrics_to_plot.items():
    # Extract data
    # Extract data
    plot_data = []
    plot_data = []
    for model_id in model_ids:
    for model_id in model_ids:
    if model_id in comparison.comparison_metrics:
    if model_id in comparison.comparison_metrics:
    model_data = comparison.comparison_metrics[model_id]
    model_data = comparison.comparison_metrics[model_id]
    if metric in model_data and model_data[metric] > 0:
    if metric in model_data and model_data[metric] > 0:
    model_name = model_data.get("model_name", model_id)
    model_name = model_data.get("model_name", model_id)
    plot_data.append(
    plot_data.append(
    {
    {
    "model": model_name,
    "model": model_name,
    "value": model_data[metric],
    "value": model_data[metric],
    "percent_dif": model_data.get(
    "percent_dif": model_data.get(
    f"{metric}_percent_dif", 0
    f"{metric}_percent_dif", 0
    ),
    ),
    }
    }
    )
    )


    if plot_data:
    if plot_data:
    df = pd.DataFrame(plot_data)
    df = pd.DataFrame(plot_data)
    fig = px.bar(
    fig = px.bar(
    df,
    df,
    x="model",
    x="model",
    y="value",
    y="value",
    title=f"{title} Comparison",
    title=f"{title} Comparison",
    labels={"value": title, "model": "Model"},
    labels={"value": title, "model": "Model"},
    color="model",
    color="model",
    )
    )
    plots[f"{metric}_comparison"] = fig.to_html(
    plots[f"{metric}_comparison"] = fig.to_html(
    full_html=False, include_plotlyjs=False
    full_html=False, include_plotlyjs=False
    )
    )


    # 2. Cost comparison if available
    # 2. Cost comparison if available
    cost_data = []
    cost_data = []
    for model_id in model_ids:
    for model_id in model_ids:
    if model_id in reports:
    if model_id in reports:
    report = reports[model_id]
    report = reports[model_id]
    if hasattr(report, "total_prompt_cost") and hasattr(
    if hasattr(report, "total_prompt_cost") and hasattr(
    report, "total_completion_cost"
    report, "total_completion_cost"
    ):
    ):
    model_name = comparison.comparison_metrics.get(model_id, {}).get(
    model_name = comparison.comparison_metrics.get(model_id, {}).get(
    "model_name", model_id
    "model_name", model_id
    )
    )
    cost_data.append(
    cost_data.append(
    {
    {
    "model": model_name,
    "model": model_name,
    "prompt_cost": report.total_prompt_cost,
    "prompt_cost": report.total_prompt_cost,
    "completion_cost": report.total_completion_cost,
    "completion_cost": report.total_completion_cost,
    "total_cost": report.total_prompt_cost
    "total_cost": report.total_prompt_cost
    + report.total_completion_cost,
    + report.total_completion_cost,
    }
    }
    )
    )


    if cost_data:
    if cost_data:
    df = pd.DataFrame(cost_data)
    df = pd.DataFrame(cost_data)
    fig = px.bar(
    fig = px.bar(
    df,
    df,
    x="model",
    x="model",
    y=["prompt_cost", "completion_cost"],
    y=["prompt_cost", "completion_cost"],
    title="Cost Comparison",
    title="Cost Comparison",
    labels={"value": "Cost ($)", "model": "Model", "variable": "Cost Type"},
    labels={"value": "Cost ($)", "model": "Model", "variable": "Cost Type"},
    barmode="stack",
    barmode="stack",
    )
    )
    plots["cost_comparison"] = fig.to_html(
    plots["cost_comparison"] = fig.to_html(
    full_html=False, include_plotlyjs=False
    full_html=False, include_plotlyjs=False
    )
    )


    # 3. Token usage comparison
    # 3. Token usage comparison
    token_data = []
    token_data = []
    for model_id in model_ids:
    for model_id in model_ids:
    if model_id in reports:
    if model_id in reports:
    report = reports[model_id]
    report = reports[model_id]
    if hasattr(report, "total_prompt_tokens") and hasattr(
    if hasattr(report, "total_prompt_tokens") and hasattr(
    report, "total_completion_tokens"
    report, "total_completion_tokens"
    ):
    ):
    model_name = comparison.comparison_metrics.get(model_id, {}).get(
    model_name = comparison.comparison_metrics.get(model_id, {}).get(
    "model_name", model_id
    "model_name", model_id
    )
    )
    token_data.append(
    token_data.append(
    {
    {
    "model": model_name,
    "model": model_name,
    "prompt_tokens": report.total_prompt_tokens,
    "prompt_tokens": report.total_prompt_tokens,
    "completion_tokens": report.total_completion_tokens,
    "completion_tokens": report.total_completion_tokens,
    "total_tokens": report.total_prompt_tokens
    "total_tokens": report.total_prompt_tokens
    + report.total_completion_tokens,
    + report.total_completion_tokens,
    }
    }
    )
    )


    if token_data:
    if token_data:
    df = pd.DataFrame(token_data)
    df = pd.DataFrame(token_data)
    fig = px.bar(
    fig = px.bar(
    df,
    df,
    x="model",
    x="model",
    y=["prompt_tokens", "completion_tokens"],
    y=["prompt_tokens", "completion_tokens"],
    title="Token Usage Comparison",
    title="Token Usage Comparison",
    labels={"value": "Tokens", "model": "Model", "variable": "Token Type"},
    labels={"value": "Tokens", "model": "Model", "variable": "Token Type"},
    barmode="stack",
    barmode="stack",
    )
    )
    plots["token_comparison"] = fig.to_html(
    plots["token_comparison"] = fig.to_html(
    full_html=False, include_plotlyjs=False
    full_html=False, include_plotlyjs=False
    )
    )


    # Generate HTML dashboard using Jinja2
    # Generate HTML dashboard using Jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))


    # Create a template string within the code instead of requiring an external file
    # Create a template string within the code instead of requiring an external file
    template_str = """
    template_str = """
    <!DOCTYPE html>
    <!DOCTYPE html>
    <html>
    <html>
    <head>
    <head>
    <title>Model Comparison Dashboard</title>
    <title>Model Comparison Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    <style>
    body { padding: 20px; }
    body { padding: 20px; }
    .card { margin-bottom: 20px; }
    .card { margin-bottom: 20px; }
    .plot-container { height: 400px; }
    .plot-container { height: 400px; }
    .table-container { max-height: 600px; overflow-y: auto; }
    .table-container { max-height: 600px; overflow-y: auto; }
    </style>
    </style>
    </head>
    </head>
    <body>
    <body>
    <div class="container">
    <div class="container">
    <h1>Model Performance Comparison</h1>
    <h1>Model Performance Comparison</h1>
    <p class="text-muted">Report generated on {{ generation_time }} | Data range: {{ start_date }} to {{ end_date }}</p>
    <p class="text-muted">Report generated on {{ generation_time }} | Data range: {{ start_date }} to {{ end_date }}</p>


    <div class="row">
    <div class="row">
    <div class="col-md-12">
    <div class="col-md-12">
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Models Included</h5>
    <h5 class="card-title">Models Included</h5>
    <ul class="list-group">
    <ul class="list-group">
    {% for model_id, model_name in models %}
    {% for model_id, model_name in models %}
    <li class="list-group-item">{{ model_name }} ({{ model_id }})</li>
    <li class="list-group-item">{{ model_name }} ({{ model_id }})</li>
    {% endfor %}
    {% endfor %}
    </ul>
    </ul>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>


    {% if 'avg_inference_time_comparison' in plots %}
    {% if 'avg_inference_time_comparison' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Inference Time Comparison</h5>
    <h5 class="card-title">Inference Time Comparison</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.avg_inference_time_comparison | safe }}
    {{ plots.avg_inference_time_comparison | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'avg_latency_ms_comparison' in plots %}
    {% if 'avg_latency_ms_comparison' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Latency Comparison</h5>
    <h5 class="card-title">Latency Comparison</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.avg_latency_ms_comparison | safe }}
    {{ plots.avg_latency_ms_comparison | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'avg_tokens_per_second_comparison' in plots %}
    {% if 'avg_tokens_per_second_comparison' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Throughput Comparison</h5>
    <h5 class="card-title">Throughput Comparison</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.avg_tokens_per_second_comparison | safe }}
    {{ plots.avg_tokens_per_second_comparison | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'cost_per_1k_tokens_comparison' in plots %}
    {% if 'cost_per_1k_tokens_comparison' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Cost Efficiency Comparison</h5>
    <h5 class="card-title">Cost Efficiency Comparison</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.cost_per_1k_tokens_comparison | safe }}
    {{ plots.cost_per_1k_tokens_comparison | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'cost_comparison' in plots %}
    {% if 'cost_comparison' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Total Cost Comparison</h5>
    <h5 class="card-title">Total Cost Comparison</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.cost_comparison | safe }}
    {{ plots.cost_comparison | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    {% if 'token_comparison' in plots %}
    {% if 'token_comparison' in plots %}
    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Token Usage Comparison</h5>
    <h5 class="card-title">Token Usage Comparison</h5>
    <div class="plot-container">
    <div class="plot-container">
    {{ plots.token_comparison | safe }}
    {{ plots.token_comparison | safe }}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    {% endif %}
    {% endif %}


    <div class="card">
    <div class="card">
    <div class="card-body">
    <div class="card-body">
    <h5 class="card-title">Detailed Comparison Table</h5>
    <h5 class="card-title">Detailed Comparison Table</h5>
    <div class="table-container">
    <div class="table-container">
    <table class="table table-striped">
    <table class="table table-striped">
    <thead>
    <thead>
    <tr>
    <tr>
    <th>Metric</th>
    <th>Metric</th>
    {% for model_id, model_name in models %}
    {% for model_id, model_name in models %}
    <th>{{ model_name }}</th>
    <th>{{ model_name }}</th>
    {% endfor %}
    {% endfor %}
    </tr>
    </tr>
    </thead>
    </thead>
    <tbody>
    <tbody>
    {% for metric_name, metric_label in metrics_list.items() %}
    {% for metric_name, metric_label in metrics_list.items() %}
    <tr>
    <tr>
    <td>{{ metric_label }}</td>
    <td>{{ metric_label }}</td>
    {% for model_id, _ in models %}
    {% for model_id, _ in models %}
    <td>
    <td>
    {% if model_metrics[model_id][metric_name] is defined %}
    {% if model_metrics[model_id][metric_name] is defined %}
    {{ model_metrics[model_id][metric_name] }}
    {{ model_metrics[model_id][metric_name] }}
    {% else %}
    {% else %}
    N/A
    N/A
    {% endif %}
    {% endif %}
    </td>
    </td>
    {% endfor %}
    {% endfor %}
    </tr>
    </tr>
    {% endfor %}
    {% endfor %}
    </tbody>
    </tbody>
    </table>
    </table>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </body>
    </body>
    </html>
    </html>
    """
    """


    template = env.from_string(template_str)
    template = env.from_string(template_str)


    # Prepare model names
    # Prepare model names
    models_list = []
    models_list = []
    for idx, model_id in enumerate(model_ids):
    for idx, model_id in enumerate(model_ids):
    model_name = (
    model_name = (
    model_names[idx] if model_names and idx < len(model_names) else model_id
    model_names[idx] if model_names and idx < len(model_names) else model_id
    )
    )
    models_list.append((model_id, model_name))
    models_list.append((model_id, model_name))


    # Prepare metrics list
    # Prepare metrics list
    metrics_list = {
    metrics_list = {
    "num_inferences": "Number of Inferences",
    "num_inferences": "Number of Inferences",
    "avg_inference_time": "Avg. Inference Time (s)",
    "avg_inference_time": "Avg. Inference Time (s)",
    "avg_latency_ms": "Avg. Latency (ms)",
    "avg_latency_ms": "Avg. Latency (ms)",
    "avg_time_to_first_token": "Avg. Time to First Token (s)",
    "avg_time_to_first_token": "Avg. Time to First Token (s)",
    "avg_tokens_per_second": "Tokens per Second",
    "avg_tokens_per_second": "Tokens per Second",
    "total_prompt_tokens": "Total Prompt Tokens",
    "total_prompt_tokens": "Total Prompt Tokens",
    "total_completion_tokens": "Total Completion Tokens",
    "total_completion_tokens": "Total Completion Tokens",
    "avg_prompt_tokens": "Avg. Prompt Tokens",
    "avg_prompt_tokens": "Avg. Prompt Tokens",
    "avg_completion_tokens": "Avg. Completion Tokens",
    "avg_completion_tokens": "Avg. Completion Tokens",
    "total_prompt_cost": "Total Prompt Cost ($)",
    "total_prompt_cost": "Total Prompt Cost ($)",
    "total_completion_cost": "Total Completion Cost ($)",
    "total_completion_cost": "Total Completion Cost ($)",
    "avg_memory_usage_mb": "Avg. Memory Usage (MB)",
    "avg_memory_usage_mb": "Avg. Memory Usage (MB)",
    "cost_per_1k_tokens": "Cost per 1K Tokens ($)",
    "cost_per_1k_tokens": "Cost per 1K Tokens ($)",
    }
    }


    # Prepare model metrics
    # Prepare model metrics
    model_metrics = {}
    model_metrics = {}
    for model_id in model_ids:
    for model_id in model_ids:
    model_metrics[model_id] = {}
    model_metrics[model_id] = {}
    # Add comparison metrics
    # Add comparison metrics
    if model_id in comparison.comparison_metrics:
    if model_id in comparison.comparison_metrics:
    for key, value in comparison.comparison_metrics[model_id].items():
    for key, value in comparison.comparison_metrics[model_id].items():
    if isinstance(value, float):
    if isinstance(value, float):
    if abs(value) >= 1000:
    if abs(value) >= 1000:
    model_metrics[model_id][key] = f"{value:.2f}"
    model_metrics[model_id][key] = f"{value:.2f}"
    else:
    else:
    model_metrics[model_id][key] = f"{value:.4f}"
    model_metrics[model_id][key] = f"{value:.4f}"
    else:
    else:
    model_metrics[model_id][key] = value
    model_metrics[model_id][key] = value


    # Add report metrics
    # Add report metrics
    if model_id in reports:
    if model_id in reports:
    for key, value in reports[model_id].__dict__.items():
    for key, value in reports[model_id].__dict__.items():
    if key in metrics_list and key not in model_metrics[model_id]:
    if key in metrics_list and key not in model_metrics[model_id]:
    if isinstance(value, float):
    if isinstance(value, float):
    if abs(value) >= 1000:
    if abs(value) >= 1000:
    model_metrics[model_id][key] = f"{value:.2f}"
    model_metrics[model_id][key] = f"{value:.2f}"
    else:
    else:
    model_metrics[model_id][key] = f"{value:.4f}"
    model_metrics[model_id][key] = f"{value:.4f}"
    else:
    else:
    model_metrics[model_id][key] = value
    model_metrics[model_id][key] = value


    # Render template
    # Render template
    html_content = template.render(
    html_content = template.render(
    models=models_list,
    models=models_list,
    plots=plots,
    plots=plots,
    metrics_list=metrics_list,
    metrics_list=metrics_list,
    model_metrics=model_metrics,
    model_metrics=model_metrics,
    generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    start_date=start_time.strftime("%Y-%m-%d"),
    start_date=start_time.strftime("%Y-%m-%d"),
    end_date=end_time.strftime("%Y-%m-%d"),
    end_date=end_time.strftime("%Y-%m-%d"),
    )
    )


    # Save dashboard HTML
    # Save dashboard HTML
    filename = f"model_comparison_{int(time.time())}.html"
    filename = f"model_comparison_{int(time.time())}.html"
    filepath = os.path.join(self.output_dir, filename)
    filepath = os.path.join(self.output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
    with open(filepath, "w", encoding="utf-8") as f:
    f.write(html_content)
    f.write(html_content)


    logger.info(f"Comparison dashboard generated at: {filepath}")
    logger.info(f"Comparison dashboard generated at: {filepath}")
    return filepath
    return filepath


    def export_metrics_to_json(
    def export_metrics_to_json(
    self, model_id: str, days: int = 30, output_file: Optional[str] = None
    self, model_id: str, days: int = 30, output_file: Optional[str] = None
    ) -> str:
    ) -> str:
    """
    """
    Export metrics to a JSON file.
    Export metrics to a JSON file.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    days: Number of days of data to include
    days: Number of days of data to include
    output_file: Optional output filename
    output_file: Optional output filename


    Returns:
    Returns:
    Path to the exported JSON file
    Path to the exported JSON file
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


    # Get metrics data
    # Get metrics data
    metrics_data = self.performance_monitor.metrics_db.get_metrics(
    metrics_data = self.performance_monitor.metrics_db.get_metrics(
    model_id=model_id, time_range=time_range, limit=10000
    model_id=model_id, time_range=time_range, limit=10000
    )
    )


    # Generate report
    # Generate report
    report = self.performance_monitor.generate_enhanced_report(
    report = self.performance_monitor.generate_enhanced_report(
    model_id=model_id, time_range=time_range
    model_id=model_id, time_range=time_range
    )
    )


    # Prepare export data
    # Prepare export data
    export_data = {
    export_data = {
    "model_id": model_id,
    "model_id": model_id,
    "export_date": datetime.now().isoformat(),
    "export_date": datetime.now().isoformat(),
    "date_range": {
    "date_range": {
    "start": start_time.isoformat(),
    "start": start_time.isoformat(),
    "end": end_time.isoformat(),
    "end": end_time.isoformat(),
    },
    },
    "summary": {},
    "summary": {},
    "metrics": metrics_data,
    "metrics": metrics_data,
    }
    }


    # Add report summary
    # Add report summary
    for key, value in report.__dict__.items():
    for key, value in report.__dict__.items():
    if not key.startswith("_") and key != "raw_metrics":
    if not key.startswith("_") and key != "raw_metrics":
    if isinstance(value, (int, float, str, bool, dict)) or value is None:
    if isinstance(value, (int, float, str, bool, dict)) or value is None:
    export_data["summary"][key] = value
    export_data["summary"][key] = value


    # Determine output filename
    # Determine output filename
    if not output_file:
    if not output_file:
    output_file = os.path.join(
    output_file = os.path.join(
    self.output_dir, f"{model_id}_metrics_{int(time.time())}.json"
    self.output_dir, f"{model_id}_metrics_{int(time.time())}.json"
    )
    )


    # Export to JSON
    # Export to JSON
    with open(output_file, "w", encoding="utf-8") as f:
    with open(output_file, "w", encoding="utf-8") as f:
    json.dump(export_data, f, indent=2)
    json.dump(export_data, f, indent=2)


    logger.info(f"Metrics exported to JSON: {output_file}")
    logger.info(f"Metrics exported to JSON: {output_file}")
    return output_file
    return output_file
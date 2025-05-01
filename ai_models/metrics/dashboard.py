"""
Dashboard generation for model performance metrics.

This module provides tools for generating interactive dashboards and reports
to visualize model performance metrics, token usage, and cost data.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import metrics classes
from ai_models.metrics import EnhancedPerformanceMonitor, EnhancedPerformanceReport


class MetricsDashboard:
    """
    Dashboard generator for model performance metrics.

    This class provides functionality to generate interactive dashboards and reports
    for visualizing model performance metrics, both as HTML reports and charts.
    """

    def __init__(
        self,
        performance_monitor: Optional[EnhancedPerformanceMonitor] = None,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize the dashboard generator.

        Args:
            performance_monitor: Performance monitor instance to use
            output_dir: Directory to save dashboard files (default: ./model_dashboards)
        """
        self.performance_monitor = performance_monitor or EnhancedPerformanceMonitor()
        self.output_dir = output_dir or os.path.join(os.getcwd(), "model_dashboards")
        os.makedirs(self.output_dir, exist_ok=True)

        # Check for dependencies
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Check if required packages for visualization are installed."""
        missing_deps = []

        try:
            import matplotlib
        except ImportError:
            missing_deps.append("matplotlib")

        try:
            import pandas
        except ImportError:
            missing_deps.append("pandas")

        try:
            import plotly
        except ImportError:
            missing_deps.append("plotly")

        try:
            import jinja2
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
        Generate a comprehensive dashboard for a model.

        Args:
            model_id: ID of the model
            days: Number of days of data to include
            include_token_usage: Whether to include token usage charts
            include_latency: Whether to include latency/performance charts
            include_cost: Whether to include cost charts
            include_errors: Whether to include error charts

        Returns:
            Path to the generated dashboard HTML file
        """
        try:
            import jinja2
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            logger.error(
                "Dashboard generation requires additional packages. Install with: "
                "pip install pandas plotly jinja2"
            )
            return ""

        # Get time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        time_range = (start_time, end_time)

        # Get metrics data
        metrics_data = self.performance_monitor.metrics_db.get_metrics(
            model_id=model_id, time_range=time_range, limit=10000
        )

        if not metrics_data:
            logger.warning(
                f"No metrics found for model {model_id} in the last {days} days"
            )
            return ""

        # Generate report
        report = self.performance_monitor.generate_enhanced_report(
            model_id=model_id, time_range=time_range, include_metrics=True
        )

        # Process metrics for visualization
        df = pd.DataFrame(metrics_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

        # Extract token usage and cost data from metadata
        token_data = []
        for metric in metrics_data:
            if not isinstance(metric.get("metadata"), dict):
                continue

            token_usage = metric.get("metadata", {}).get("token_usage", {})
            if token_usage:
                entry = {
                    "timestamp": pd.to_datetime(metric["timestamp"]),
                    "prompt_tokens": token_usage.get("prompt_tokens", 0),
                    "completion_tokens": token_usage.get("completion_tokens", 0),
                    "total_tokens": token_usage.get("total_tokens", 0),
                    "prompt_cost": token_usage.get("prompt_cost", 0.0),
                    "completion_cost": token_usage.get("completion_cost", 0.0),
                    "total_cost": token_usage.get("total_cost", 0.0),
                }
                token_data.append(entry)

        token_df = pd.DataFrame(token_data)

        # Create plots
        plots = {}

        # 1. Latency over time
        if include_latency and not df["latency_ms"].isnull().all():
            fig = px.scatter(
                df,
                x="timestamp",
                y="latency_ms",
                title=f"Latency Over Time ({model_id})",
                labels={"latency_ms": "Latency (ms)", "timestamp": "Time"},
                color_discrete_sequence=["blue"],
            )
            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=df["latency_ms"].rolling(10).mean(),
                    mode="lines",
                    name="10-point Moving Average",
                    line=dict(color="red", width=2),
                )
            )
            plots["latency_plot"] = fig.to_html(full_html=False, include_plotlyjs=False)

        # 2. Token usage over time
        if include_token_usage and len(token_df) > 0:
            # Create a daily aggregation
            token_df["date"] = token_df["timestamp"].dt.date
            daily_tokens = (
                token_df.groupby("date")
                .agg(
                    {
                        "prompt_tokens": "sum",
                        "completion_tokens": "sum",
                        "total_tokens": "sum",
                    }
                )
                .reset_index()
            )
            daily_tokens["date"] = pd.to_datetime(daily_tokens["date"])

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=daily_tokens["date"],
                    y=daily_tokens["prompt_tokens"],
                    name="Prompt Tokens",
                    marker_color="lightblue",
                )
            )
            fig.add_trace(
                go.Bar(
                    x=daily_tokens["date"],
                    y=daily_tokens["completion_tokens"],
                    name="Completion Tokens",
                    marker_color="darkblue",
                )
            )
            fig.update_layout(
                title=f"Daily Token Usage ({model_id})",
                xaxis_title="Date",
                yaxis_title="Tokens",
                barmode="stack",
            )
            plots["token_usage_plot"] = fig.to_html(
                full_html=False, include_plotlyjs=False
            )

        # 3. Cost over time
        if include_cost and len(token_df) > 0 and token_df["total_cost"].sum() > 0:
            # Create a daily aggregation
            daily_costs = (
                token_df.groupby("date")
                .agg(
                    {
                        "prompt_cost": "sum",
                        "completion_cost": "sum",
                        "total_cost": "sum",
                    }
                )
                .reset_index()
            )

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=daily_costs["date"],
                    y=daily_costs["prompt_cost"],
                    name="Prompt Cost",
                    marker_color="lightgreen",
                )
            )
            fig.add_trace(
                go.Bar(
                    x=daily_costs["date"],
                    y=daily_costs["completion_cost"],
                    name="Completion Cost",
                    marker_color="darkgreen",
                )
            )
            fig.update_layout(
                title=f"Daily Token Cost ({model_id})",
                xaxis_title="Date",
                yaxis_title="Cost (USD)",
                barmode="stack",
            )
            plots["cost_plot"] = fig.to_html(full_html=False, include_plotlyjs=False)

            # Also create a cumulative cost plot
            daily_costs["cumulative_cost"] = daily_costs["total_cost"].cumsum()
            fig = px.line(
                daily_costs,
                x="date",
                y="cumulative_cost",
                title=f"Cumulative Cost ({model_id})",
                labels={"cumulative_cost": "Cumulative Cost (USD)", "date": "Date"},
                color_discrete_sequence=["green"],
            )
            plots["cumulative_cost_plot"] = fig.to_html(
                full_html=False, include_plotlyjs=False
            )

        # 4. Inference time distributions
        if "total_time" in df.columns and not df["total_time"].isnull().all():
            fig = px.histogram(
                df,
                x="total_time",
                title=f"Inference Time Distribution ({model_id})",
                labels={"total_time": "Inference Time (s)"},
                color_discrete_sequence=["purple"],
            )
            plots["inference_time_hist"] = fig.to_html(
                full_html=False, include_plotlyjs=False
            )

        # 5. Error rate over time
        if include_errors and "error_occurred" in df.columns:
            # Group by date and calculate error rate
            df["date"] = df["timestamp"].dt.date
            daily_errors = (
                df.groupby("date")
                .agg({"error_occurred": "sum", "model_id": "count"})
                .reset_index()
            )
            daily_errors["date"] = pd.to_datetime(daily_errors["date"])
            daily_errors["error_rate"] = (
                daily_errors["error_occurred"] / daily_errors["model_id"]
            )

            if (
                not daily_errors["error_occurred"].isnull().all()
                and daily_errors["error_occurred"].sum() > 0
            ):
                fig = px.line(
                    daily_errors,
                    x="date",
                    y="error_rate",
                    title=f"Daily Error Rate ({model_id})",
                    labels={"error_rate": "Error Rate", "date": "Date"},
                    color_discrete_sequence=["red"],
                )
                plots["error_rate_plot"] = fig.to_html(
                    full_html=False, include_plotlyjs=False
                )

        # Generate HTML dashboard using Jinja2
        env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))

        # Create a template string within the code instead of requiring an external file
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ model_id }} - Performance Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { padding: 20px; }
                .card { margin-bottom: 20px; }
                .summary-card { background-color: #f8f9fa; }
                .plot-container { height: 400px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{{ model_id }} - Performance Dashboard</h1>
                <p class="text-muted">Report generated on {{ generation_time }} | Data range: {{ start_date }} to {{ end_date }}</p>
                
                <div class="row">
                    <div class="col-md-4">
                        <div class="card summary-card">
                            <div class="card-body">
                                <h5 class="card-title">Usage Summary</h5>
                                <p class="card-text">Inferences: {{ report.num_inferences }}</p>
                                <p class="card-text">Total Tokens: {{ total_tokens }}</p>
                                <p class="card-text">Avg. Latency: {{ "%.2f"|format(report.avg_latency_ms) }} ms</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card summary-card">
                            <div class="card-body">
                                <h5 class="card-title">Cost Summary</h5>
                                <p class="card-text">Total Cost: ${{ "%.2f"|format(total_cost) }}</p>
                                <p class="card-text">Average Cost: ${{ "%.4f"|format(avg_cost_per_inference) }}</p>
                                <p class="card-text">Cost per 1K Tokens: ${{ "%.4f"|format(report.cost_per_1k_tokens or 0) }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card summary-card">
                            <div class="card-body">
                                <h5 class="card-title">Performance Summary</h5>
                                <p class="card-text">Avg. Inference Time: {{ "%.2f"|format(report.avg_inference_time) }} s</p>
                                <p class="card-text">Tokens per Second: {{ "%.2f"|format(report.avg_tokens_per_second) }}</p>
                                <p class="card-text">Error Rate: {{ "%.2f"|format(error_rate * 100) }}%</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                {% if 'latency_plot' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Latency Over Time</h5>
                        <div class="plot-container">
                            {{ plots.latency_plot | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'token_usage_plot' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Token Usage</h5>
                        <div class="plot-container">
                            {{ plots.token_usage_plot | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'cost_plot' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Cost Analysis</h5>
                        <div class="plot-container">
                            {{ plots.cost_plot | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'cumulative_cost_plot' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Cumulative Cost</h5>
                        <div class="plot-container">
                            {{ plots.cumulative_cost_plot | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'inference_time_hist' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Inference Time Distribution</h5>
                        <div class="plot-container">
                            {{ plots.inference_time_hist | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'error_rate_plot' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Error Rate</h5>
                        <div class="plot-container">
                            {{ plots.error_rate_plot | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Detailed Metrics</h5>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for key, value in detailed_metrics.items() %}
                                <tr>
                                    <td>{{ key }}</td>
                                    <td>{{ value }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        template = env.from_string(template_str)

        # Prepare template variables
        total_tokens = report.total_prompt_tokens + report.total_completion_tokens
        total_cost = report.total_prompt_cost + report.total_completion_cost
        avg_cost_per_inference = (
            total_cost / report.num_inferences if report.num_inferences > 0 else 0
        )
        error_rate = report.error_rate if hasattr(report, "error_rate") else 0

        # Prepare detailed metrics table
        detailed_metrics = {}
        for key, value in report.__dict__.items():
            if isinstance(value, (int, float, str)) and not key.startswith("_"):
                if isinstance(value, float):
                    # Format float values
                    if abs(value) >= 1000:
                        formatted_value = f"{value:.2f}"
                    else:
                        formatted_value = f"{value:.4f}"
                    detailed_metrics[key] = formatted_value
                else:
                    detailed_metrics[key] = value

        # Render template
        html_content = template.render(
            model_id=model_id,
            report=report,
            plots=plots,
            generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            start_date=start_time.strftime("%Y-%m-%d"),
            end_date=end_time.strftime("%Y-%m-%d"),
            total_tokens=total_tokens,
            total_cost=total_cost,
            avg_cost_per_inference=avg_cost_per_inference,
            error_rate=error_rate,
            detailed_metrics=detailed_metrics,
        )

        # Save dashboard HTML
        filename = f"{model_id}_dashboard_{int(time.time())}.html"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Dashboard generated at: {filepath}")
        return filepath

    def generate_model_comparison_dashboard(
        self,
        model_ids: List[str],
        model_names: Optional[List[str]] = None,
        days: int = 30,
    ) -> str:
        """
        Generate a dashboard comparing multiple models.

        Args:
            model_ids: List of model IDs to compare
            model_names: Optional list of model names
            days: Number of days of data to include

        Returns:
            Path to the generated comparison dashboard HTML file
        """
        try:
            import jinja2
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go
        except ImportError:
            logger.error(
                "Dashboard generation requires additional packages. Install with: "
                "pip install pandas plotly jinja2"
            )
            return ""

        # Get time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        time_range = (start_time, end_time)

        # Generate comparison report
        comparison = self.performance_monitor.compare_models_enhanced(
            model_ids=model_ids,
            model_names=model_names,
            time_range=time_range,
            title="Model Performance Comparison",
        )

        # Create individual report for each model for more detailed data
        reports = {}
        for model_id in model_ids:
            report = self.performance_monitor.generate_enhanced_report(
                model_id=model_id, time_range=time_range
            )
            reports[model_id] = report

        # Generate comparison charts
        plots = {}

        # 1. Inference time comparison
        metrics_to_plot = {
            "avg_inference_time": "Average Inference Time (s)",
            "avg_latency_ms": "Average Latency (ms)",
            "avg_tokens_per_second": "Tokens per Second",
            "cost_per_1k_tokens": "Cost per 1K Tokens ($)",
        }

        for metric, title in metrics_to_plot.items():
            # Extract data
            plot_data = []
            for model_id in model_ids:
                if model_id in comparison.comparison_metrics:
                    model_data = comparison.comparison_metrics[model_id]
                    if metric in model_data and model_data[metric] > 0:
                        model_name = model_data.get("model_name", model_id)
                        plot_data.append(
                            {
                                "model": model_name,
                                "value": model_data[metric],
                                "percent_diff": model_data.get(
                                    f"{metric}_percent_diff", 0
                                ),
                            }
                        )

            if plot_data:
                df = pd.DataFrame(plot_data)
                fig = px.bar(
                    df,
                    x="model",
                    y="value",
                    title=f"{title} Comparison",
                    labels={"value": title, "model": "Model"},
                    color="model",
                )
                plots[f"{metric}_comparison"] = fig.to_html(
                    full_html=False, include_plotlyjs=False
                )

        # 2. Cost comparison if available
        cost_data = []
        for model_id in model_ids:
            if model_id in reports:
                report = reports[model_id]
                if hasattr(report, "total_prompt_cost") and hasattr(
                    report, "total_completion_cost"
                ):
                    model_name = comparison.comparison_metrics.get(model_id, {}).get(
                        "model_name", model_id
                    )
                    cost_data.append(
                        {
                            "model": model_name,
                            "prompt_cost": report.total_prompt_cost,
                            "completion_cost": report.total_completion_cost,
                            "total_cost": report.total_prompt_cost
                            + report.total_completion_cost,
                        }
                    )

        if cost_data:
            df = pd.DataFrame(cost_data)
            fig = px.bar(
                df,
                x="model",
                y=["prompt_cost", "completion_cost"],
                title="Cost Comparison",
                labels={"value": "Cost ($)", "model": "Model", "variable": "Cost Type"},
                barmode="stack",
            )
            plots["cost_comparison"] = fig.to_html(
                full_html=False, include_plotlyjs=False
            )

        # 3. Token usage comparison
        token_data = []
        for model_id in model_ids:
            if model_id in reports:
                report = reports[model_id]
                if hasattr(report, "total_prompt_tokens") and hasattr(
                    report, "total_completion_tokens"
                ):
                    model_name = comparison.comparison_metrics.get(model_id, {}).get(
                        "model_name", model_id
                    )
                    token_data.append(
                        {
                            "model": model_name,
                            "prompt_tokens": report.total_prompt_tokens,
                            "completion_tokens": report.total_completion_tokens,
                            "total_tokens": report.total_prompt_tokens
                            + report.total_completion_tokens,
                        }
                    )

        if token_data:
            df = pd.DataFrame(token_data)
            fig = px.bar(
                df,
                x="model",
                y=["prompt_tokens", "completion_tokens"],
                title="Token Usage Comparison",
                labels={"value": "Tokens", "model": "Model", "variable": "Token Type"},
                barmode="stack",
            )
            plots["token_comparison"] = fig.to_html(
                full_html=False, include_plotlyjs=False
            )

        # Generate HTML dashboard using Jinja2
        env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))

        # Create a template string within the code instead of requiring an external file
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Model Comparison Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { padding: 20px; }
                .card { margin-bottom: 20px; }
                .plot-container { height: 400px; }
                .table-container { max-height: 600px; overflow-y: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Model Performance Comparison</h1>
                <p class="text-muted">Report generated on {{ generation_time }} | Data range: {{ start_date }} to {{ end_date }}</p>
                
                <div class="row">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Models Included</h5>
                                <ul class="list-group">
                                    {% for model_id, model_name in models %}
                                    <li class="list-group-item">{{ model_name }} ({{ model_id }})</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                {% if 'avg_inference_time_comparison' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Inference Time Comparison</h5>
                        <div class="plot-container">
                            {{ plots.avg_inference_time_comparison | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'avg_latency_ms_comparison' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Latency Comparison</h5>
                        <div class="plot-container">
                            {{ plots.avg_latency_ms_comparison | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'avg_tokens_per_second_comparison' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Throughput Comparison</h5>
                        <div class="plot-container">
                            {{ plots.avg_tokens_per_second_comparison | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'cost_per_1k_tokens_comparison' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Cost Efficiency Comparison</h5>
                        <div class="plot-container">
                            {{ plots.cost_per_1k_tokens_comparison | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'cost_comparison' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Total Cost Comparison</h5>
                        <div class="plot-container">
                            {{ plots.cost_comparison | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if 'token_comparison' in plots %}
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Token Usage Comparison</h5>
                        <div class="plot-container">
                            {{ plots.token_comparison | safe }}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Detailed Comparison Table</h5>
                        <div class="table-container">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Metric</th>
                                        {% for model_id, model_name in models %}
                                        <th>{{ model_name }}</th>
                                        {% endfor %}
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for metric_name, metric_label in metrics_list.items() %}
                                    <tr>
                                        <td>{{ metric_label }}</td>
                                        {% for model_id, _ in models %}
                                        <td>
                                            {% if model_metrics[model_id][metric_name] is defined %}
                                            {{ model_metrics[model_id][metric_name] }}
                                            {% else %}
                                            N/A
                                            {% endif %}
                                        </td>
                                        {% endfor %}
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        template = env.from_string(template_str)

        # Prepare model names
        models_list = []
        for idx, model_id in enumerate(model_ids):
            model_name = (
                model_names[idx] if model_names and idx < len(model_names) else model_id
            )
            models_list.append((model_id, model_name))

        # Prepare metrics list
        metrics_list = {
            "num_inferences": "Number of Inferences",
            "avg_inference_time": "Avg. Inference Time (s)",
            "avg_latency_ms": "Avg. Latency (ms)",
            "avg_time_to_first_token": "Avg. Time to First Token (s)",
            "avg_tokens_per_second": "Tokens per Second",
            "total_prompt_tokens": "Total Prompt Tokens",
            "total_completion_tokens": "Total Completion Tokens",
            "avg_prompt_tokens": "Avg. Prompt Tokens",
            "avg_completion_tokens": "Avg. Completion Tokens",
            "total_prompt_cost": "Total Prompt Cost ($)",
            "total_completion_cost": "Total Completion Cost ($)",
            "avg_memory_usage_mb": "Avg. Memory Usage (MB)",
            "cost_per_1k_tokens": "Cost per 1K Tokens ($)",
        }

        # Prepare model metrics
        model_metrics = {}
        for model_id in model_ids:
            model_metrics[model_id] = {}
            # Add comparison metrics
            if model_id in comparison.comparison_metrics:
                for key, value in comparison.comparison_metrics[model_id].items():
                    if isinstance(value, float):
                        if abs(value) >= 1000:
                            model_metrics[model_id][key] = f"{value:.2f}"
                        else:
                            model_metrics[model_id][key] = f"{value:.4f}"
                    else:
                        model_metrics[model_id][key] = value

            # Add report metrics
            if model_id in reports:
                for key, value in reports[model_id].__dict__.items():
                    if key in metrics_list and key not in model_metrics[model_id]:
                        if isinstance(value, float):
                            if abs(value) >= 1000:
                                model_metrics[model_id][key] = f"{value:.2f}"
                            else:
                                model_metrics[model_id][key] = f"{value:.4f}"
                        else:
                            model_metrics[model_id][key] = value

        # Render template
        html_content = template.render(
            models=models_list,
            plots=plots,
            metrics_list=metrics_list,
            model_metrics=model_metrics,
            generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            start_date=start_time.strftime("%Y-%m-%d"),
            end_date=end_time.strftime("%Y-%m-%d"),
        )

        # Save dashboard HTML
        filename = f"model_comparison_{int(time.time())}.html"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Comparison dashboard generated at: {filepath}")
        return filepath

    def export_metrics_to_json(
        self, model_id: str, days: int = 30, output_file: Optional[str] = None
    ) -> str:
        """
        Export metrics to a JSON file.

        Args:
            model_id: ID of the model
            days: Number of days of data to include
            output_file: Optional output filename

        Returns:
            Path to the exported JSON file
        """
        # Get time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        time_range = (start_time, end_time)

        # Get metrics data
        metrics_data = self.performance_monitor.metrics_db.get_metrics(
            model_id=model_id, time_range=time_range, limit=10000
        )

        # Generate report
        report = self.performance_monitor.generate_enhanced_report(
            model_id=model_id, time_range=time_range
        )

        # Prepare export data
        export_data = {
            "model_id": model_id,
            "export_date": datetime.now().isoformat(),
            "date_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
            "summary": {},
            "metrics": metrics_data,
        }

        # Add report summary
        for key, value in report.__dict__.items():
            if not key.startswith("_") and key != "raw_metrics":
                if isinstance(value, (int, float, str, bool, dict)) or value is None:
                    export_data["summary"][key] = value

        # Determine output filename
        if not output_file:
            output_file = os.path.join(
                self.output_dir, f"{model_id}_metrics_{int(time.time())}.json"
            )

        # Export to JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Metrics exported to JSON: {output_file}")
        return output_file

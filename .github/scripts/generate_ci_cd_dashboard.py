#!/usr/bin/env python3
"""Generate CI/CD dashboard visualizations from workflow metrics.

This script processes workflow metrics data and generates HTML dashboard with
visualizations to track CI/CD performance metrics including:
- Workflow success/failure rates
- Average workflow durations
- Daily/weekly build trends
- Per-branch performance
"""

# Standard library imports
import argparse
import json
import logging
import os

from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt

# Third-party imports
import pandas as pd

# Constants
DEFAULT_LOOKBACK_DAYS = 30
COLORS = {
    "success": "#28a745",
    "failure": "#dc3545",
    "cancelled": "#6c757d",
    "skipped": "#ffc107",
    "neutral": "#17a2b8",
    "unknown": "#6c757d",
}

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def load_metrics(input_file: str) -> list[dict[str, Any]]:
    """Load workflow metrics from JSON file(s).

    Args:
        input_file (str): Path to input JSON file or directory

    Returns:
        list: List of workflow metrics records

    """
    metrics_data = []

    if os.path.isdir(input_file):
        # Load multiple files from directory
        for filename in os.listdir(input_file):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(input_file, filename)) as f:
                        metrics = json.load(f)
                        if isinstance(metrics, list):
                            metrics_data.extend(metrics)
                        else:
                            metrics_data.append(metrics)
                except (OSError, json.JSONDecodeError) as e:
                    logging.warning(f"Error loading {filename}: {e}")
    else:
        # Load single file
        try:
            with open(input_file) as f:
                metrics = json.load(f)
                if isinstance(metrics, list):
                    metrics_data.extend(metrics)
                else:
                    metrics_data.append(metrics)
        except (OSError, json.JSONDecodeError) as e:
            logging.warning(f"Error loading {input_file}: {e}")
            return []

    return metrics_data


def process_metrics(metrics_data: list[dict[str, Any]]) -> pd.DataFrame:
    """Process raw metrics into pandas DataFrame.

    Args:
        metrics_data (list): List of workflow metrics records

    Returns:
        pandas.DataFrame: Processed metrics data

    """
    if not metrics_data:
        logging.warning("No metrics data to process")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(metrics_data)

    # Convert timestamps to datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date

    # Ensure duration is numeric
    if "duration" in df.columns:
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0)

    # Add derived columns
    if "status" in df.columns:
        df["is_success"] = df["status"] == "success"

    return df


def generate_success_rate_chart(df: pd.DataFrame, output_dir: str) -> None:
    """Generate success rate chart.

    Args:
        df (pandas.DataFrame): Processed metrics data
        output_dir (str): Output directory for charts

    """
    if df.empty or "status" not in df.columns:
        logging.warning("No status data available for success rate chart")
        return

    plt.figure(figsize=(10, 6))

    # Group by workflow and count statuses
    workflow_status = df.groupby(["workflow", "status"]).size().unstack(fill_value=0)

    # Calculate success rate
    workflow_status["total"] = workflow_status.sum(axis=1)
    workflow_status["success_rate"] = (
        workflow_status.get("success", 0) / workflow_status["total"]
    ) * 100

    # Plot data
    ax = workflow_status["success_rate"].plot(kind="bar", color=COLORS["success"])

    # Add labels
    plt.title("Workflow Success Rates", fontsize=16)
    plt.xlabel("Workflow", fontsize=12)
    plt.ylabel("Success Rate (%)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Add value labels on bars
    for i, v in enumerate(workflow_status["success_rate"]):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center")

    # Save chart
    plt.savefig(os.path.join(output_dir, "success_rate_chart.png"))
    plt.close()


def generate_duration_chart(df: pd.DataFrame, output_dir: str) -> None:
    """Generate workflow duration chart.

    Args:
        df (pandas.DataFrame): Processed metrics data
        output_dir (str): Output directory for charts

    """
    if df.empty or "duration" not in df.columns:
        logging.warning("No duration data available for duration chart")
        return

    plt.figure(figsize=(10, 6))

    # Calculate average duration per workflow
    avg_duration = (
        df.groupby("workflow")["duration"].mean().sort_values(ascending=False)
    )

    # Convert seconds to minutes for display
    avg_duration_min = avg_duration / 60

    # Plot data
    ax = avg_duration_min.plot(kind="bar", color=COLORS["neutral"])

    # Add labels
    plt.title("Average Workflow Duration", fontsize=16)
    plt.xlabel("Workflow", fontsize=12)
    plt.ylabel("Duration (minutes)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Add value labels on bars
    for i, v in enumerate(avg_duration_min):
        ax.text(i, v + 0.1, f"{v:.1f}", ha="center")

    # Save chart
    plt.savefig(os.path.join(output_dir, "duration_chart.png"))
    plt.close()


def generate_trend_chart(df: pd.DataFrame, output_dir: str) -> None:
    """Generate workflow trend chart showing success/failure over time.

    Args:
        df (pandas.DataFrame): Processed metrics data
        output_dir (str): Output directory for charts

    """
    if df.empty or "date" not in df.columns:
        logging.warning("No date data available for trend chart")
        return

    plt.figure(figsize=(12, 6))

    # Group by date and status
    daily_status = df.groupby(["date", "status"]).size().unstack(fill_value=0)

    # Fill missing statuses
    for status in ["success", "failure", "cancelled", "skipped"]:
        if status not in daily_status.columns:
            daily_status[status] = 0

    # Plot data
    daily_status.plot(
        kind="bar",
        stacked=True,
        color=[COLORS.get(s, "#777") for s in daily_status.columns],
    )

    # Add labels
    plt.title("Daily Workflow Runs", fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Number of Runs", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend(title="Status")

    # Save chart
    plt.savefig(os.path.join(output_dir, "trend_chart.png"))
    plt.close()


def generate_branch_performance_chart(df: pd.DataFrame, output_dir: str) -> None:
    """Generate branch performance chart.

    Args:
        df (pandas.DataFrame): Processed metrics data
        output_dir (str): Output directory for charts

    """
    if df.empty or "branch" not in df.columns:
        logging.warning("No branch data available for branch performance chart")
        return

    plt.figure(figsize=(10, 6))

    # Get top branches by run count
    top_branches = df["branch"].value_counts().nlargest(10).index.tolist()

    # Filter for top branches
    branch_df = df[df["branch"].isin(top_branches)]

    # Calculate success rate per branch
    branch_success = branch_df.groupby("branch")["is_success"].agg(["mean", "count"])
    branch_success["success_rate"] = branch_success["mean"] * 100
    branch_success = branch_success.sort_values("count", ascending=False)

    # Plot data
    ax = branch_success["success_rate"].plot(kind="bar", color=COLORS["success"])

    # Add labels
    plt.title("Branch Success Rates", fontsize=16)
    plt.xlabel("Branch", fontsize=12)
    plt.ylabel("Success Rate (%)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Add value labels on bars
    for i, v in enumerate(branch_success["success_rate"]):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center")

    # Save chart
    plt.savefig(os.path.join(output_dir, "branch_chart.png"))
    plt.close()


def generate_html_dashboard(output_dir: str) -> None:
    """Generate HTML dashboard from charts.

    Args:
        output_dir (str): Output directory for dashboard

    """
    # Format the timestamp separately to keep line length under limit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dashboard_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CI/CD Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            header {{
                background-color: #333;
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 5px;
            }}
            h1, h2, h3 {{
                margin: 0;
            }}
            .timestamp {{
                color: #ccc;
                font-size: 14px;
                margin-top: 10px;
            }}
            .dashboard-row {{
                display: flex;
                flex-wrap: wrap;
                margin: 0 -10px;
                margin-bottom: 20px;
            }}
            .dashboard-column {{
                flex: 1;
                padding: 10px;
                min-width: 300px;
            }}
            .dashboard-card {{
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .card-header {{
                background-color: #4e73df;
                color: white;
                padding: 15px;
                font-weight: bold;
            }}
            .card-body {{
                padding: 15px;
                text-align: center;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>CI/CD Dashboard</h1>
                <div class="timestamp">Generated on {timestamp} UTC</div>
            </header>

            <div class="dashboard-row">
                <div class="dashboard-column">
                    <div class="dashboard-card">
                        <div class="card-header">Success Rate by Workflow</div>
                        <div class="card-body">
                            <img src="success_rate_chart.png" alt="Success Rate Chart">
                        </div>
                    </div>
                </div>
                <div class="dashboard-column">
                    <div class="dashboard-card">
                        <div class="card-header">Average Workflow Duration</div>
                        <div class="card-body">
                            <img src="duration_chart.png" alt="Duration Chart">
                        </div>
                    </div>
                </div>
            </div>

            <div class="dashboard-row">
                <div class="dashboard-column">
                    <div class="dashboard-card">
                        <div class="card-header">Daily Workflow Runs</div>
                        <div class="card-body">
                            <img src="trend_chart.png" alt="Trend Chart">
                        </div>
                    </div>
                </div>
                <div class="dashboard-column">
                    <div class="dashboard-card">
                        <div class="card-header">Branch Success Rates</div>
                        <div class="card-body">
                            <img src="branch_chart.png" alt="Branch Chart">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(dashboard_html)

    logging.info(f"Dashboard generated: {os.path.join(output_dir, 'index.html')}")


def main() -> int:
    """Implement the main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate CI/CD dashboard from workflow metrics"
    )
    parser.add_argument(
        "--input", required=True, help="Path to input metrics JSON file or directory"
    )
    parser.add_argument(
        "--output-dir", required=True, help="Output directory for dashboard"
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Load and process metrics
    metrics_data = load_metrics(args.input)
    df = process_metrics(metrics_data)

    if df.empty:
        logging.warning("No metrics data available to generate dashboard")
        return 1

    # Generate charts
    generate_success_rate_chart(df, args.output_dir)
    generate_duration_chart(df, args.output_dir)
    generate_trend_chart(df, args.output_dir)
    generate_branch_performance_chart(df, args.output_dir)

    # Generate HTML dashboard
    generate_html_dashboard(args.output_dir)

    logging.info(f"CI/CD dashboard generated successfully in {args.output_dir}")
    return 0


if __name__ == "__main__":
    main()

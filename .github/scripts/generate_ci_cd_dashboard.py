#!/usr / bin / env python3
"""
Script to generate a CI / CD metrics dashboard.

This script generates a dashboard of CI / CD metrics based on the collected
workflow metrics data.
"""

import argparse
import datetime
import json
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd


def get_status_class(recent_runs):
    """Return the CSS class based on the status of the most recent run."""
    if recent_runs.empty:
        return ""
    return "success" if recent_runs.iloc[0]["status"].lower() == \
        "success" else "failure"


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate CI / CD metrics dashboard")
    parser.add_argument("--input", required=True, help="Input metrics file path")
    parser.add_argument("--output - dir", required=True, 
        help="Output directory for dashboard files")
    return parser.parse_args()


def load_metrics(file_path):
    """Load metrics from file."""
    if not os.path.exists(file_path):
        print(f"Error: Metrics file {file_path} does not exist")
        return None

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not parse metrics file {file_path}")
        return None


def create_dataframe(metrics):
    """Create a pandas DataFrame from metrics data."""
    if not metrics or "workflows" not in metrics or not metrics["workflows"]:
        print("Error: No workflow metrics found")
        return None

    df = pd.DataFrame(metrics["workflows"])

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Sort by timestamp
    df = df.sort_values("timestamp")

    return df


def generate_workflow_status_chart(df, output_dir):
    """Generate a chart of workflow status over time."""
    if df is None or df.empty:
        return

    # Count status by day
    df["date"] = df["timestamp"].dt.date
    status_counts = df.groupby(["date", "status"]).size().unstack().fillna(0)

    # Plot
    plt.figure(figsize=(12, 6))
    status_counts.plot(kind="bar", stacked=True)
    plt.title("Workflow Status by Day")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.tight_layout()

    # Save
    output_path = os.path.join(output_dir, "workflow_status.png")
    plt.savefig(output_path)
    plt.close()

    return output_path


def generate_workflow_duration_chart(df, output_dir):
    """Generate a chart of workflow duration over time."""
    if df is None or df.empty:
        return

    # Group by workflow and date
    df["date"] = df["timestamp"].dt.date
    duration_by_workflow = df.groupby(["date", 
        "workflow"])["duration_seconds"].mean().unstack()

    # Plot
    plt.figure(figsize=(12, 6))
    duration_by_workflow.plot(kind="line", marker="o")
    plt.title("Average Workflow Duration by Day")
    plt.xlabel("Date")
    plt.ylabel("Duration (seconds)")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Save
    output_path = os.path.join(output_dir, "workflow_duration.png")
    plt.savefig(output_path)
    plt.close()

    return output_path


def generate_workflow_success_rate_chart(df, output_dir):
    """Generate a chart of workflow success rate over time."""
    if df is None or df.empty:
        return

    # Calculate success rate by day
    df["date"] = df["timestamp"].dt.date
    df["is_success"] = df["status"].str.lower() == "success"

    success_rate = df.groupby(["date", "workflow"])["is_success"].mean().unstack() * 100

    # Plot
    plt.figure(figsize=(12, 6))
    success_rate.plot(kind="line", marker="o")
    plt.title("Workflow Success Rate by Day")
    plt.xlabel("Date")
    plt.ylabel("Success Rate (%)")
    plt.ylim(0, 100)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Save
    output_path = os.path.join(output_dir, "workflow_success_rate.png")
    plt.savefig(output_path)
    plt.close()

    return output_path


def generate_html_dashboard(df, chart_paths, output_dir):
    """Generate an HTML dashboard with metrics and charts."""
    if df is None or df.empty:
        return

    # Calculate summary metrics
    total_runs = len(df)
    success_runs = len(df[df["status"].str.lower() == "success"])
    success_rate = (success_runs / total_runs) * 100 if total_runs > 0 else 0
    avg_duration = df["duration_seconds"].mean()

    # Get recent runs
    recent_runs = df.sort_values("timestamp", ascending=False).head(10)

    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CI / CD Metrics Dashboard</title>
        <style>
            body {{ font - family: Arial, sans - serif; margin: 20px; }}
            .summary {{ display: flex; justify - \
                content: space - between; margin - bottom: 20px; }}
            .metric {{ background - \
                color: #f5f5f5; padding: 15px; border - radius: 5px; width: 22%; }}
            .metric h3 {{ margin - top: 0; color: #333; }}
            .metric p {{ font - size: 24px; font - weight: bold; margin: 5px 0; }}
            .chart {{ margin - bottom: 30px; }}
            table {{ width: 100%; border - collapse: collapse; margin - top: 20px; }}
            th, 
                td {{ padding: 8px; text - align: left; border - bottom: 1px solid #ddd; }}
            th {{ background - color: #f2f2f2; }}
            tr:hover {{ background - color: #f5f5f5; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>CI / CD Metrics Dashboard</h1>
        <p>Generated on {datetime.datetime.now().strftime(' % Y-%m-%d %H:%M:%S')}</p>

        <div class="summary">
            <div class="metric">
                <h3>Total Runs</h3>
                <p>{total_runs}</p>
            </div>
            <div class="metric">
                <h3>Success Rate</h3>
                <p>{success_rate:.1f}%</p>
            </div>
            <div class="metric">
                <h3>Avg Duration</h3>
                <p>{avg_duration:.1f}s</p>
            </div>
            <div class="metric">
                <h3>Last Run</h3>
                <p class="{get_status_class(
                    recent_runs) if not recent_runs.empty else ''}">
                    {recent_runs.iloc[0]['status'] if not recent_runs.empty else 'N / \
                        A'}
                </p>
            </div>
        </div>

        <div class="charts">
    """

    # Add charts
    for chart_path in chart_paths:
        if chart_path:
            chart_filename = os.path.basename(chart_path)
            html += f"""
            <div class="chart">
                <img src="{chart_filename}" alt="{chart_filename}" style="width: 100%;">
            </div>
            """

    # Add recent runs table
    html += """
        </div>

        <h2>Recent Workflow Runs</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Workflow</th>
                <th>Status</th>
                <th>Duration (s)</th>
                <th>Branch</th>
            </tr>
    """

    for _, run in recent_runs.iterrows():
        status_class = "success" if run["status"].lower() == "success" else "failure"
        html += f"""
            <tr>
                <td>{run["timestamp"].strftime(' % Y-%m-%d %H:%M:%S')}</td>
                <td>{run["workflow"]}</td>
                <td class="{status_class}">{run["status"]}</td>
                <td>{run["duration_seconds"]:.1f}</td>
                <td>{run["branch"]}</td>
            </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    # Save HTML
    output_path = os.path.join(output_dir, "dashboard.html")
    with open(output_path, "w") as f:
        f.write(html)

    return output_path


def main():
    """Main function."""
    args = parse_args()

    # Load metrics
    metrics = load_metrics(args.input)
    if not metrics:
        return 1

    # Create DataFrame
    df = create_dataframe(metrics)
    if df is None:
        return 1

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate charts
    chart_paths = [
        generate_workflow_status_chart(df, args.output_dir),
        generate_workflow_duration_chart(df, args.output_dir),
        generate_workflow_success_rate_chart(df, args.output_dir)
    ]

    # Generate HTML dashboard
    dashboard_path = generate_html_dashboard(df, chart_paths, args.output_dir)

    if dashboard_path:
        print(f"Dashboard generated at {dashboard_path}")
        return 0
    else:
        print("Failed to generate dashboard")
        return 1


if __name__ == "__main__":
    sys.exit(main())

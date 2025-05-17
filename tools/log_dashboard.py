#!/usr/bin/env python
"""
Log Dashboard - A simple web-based dashboard for visualizing application logs.

This tool provides a web interface for viewing, filtering, and analyzing log files
from the pAIssive_income project. It helps developers and administrators monitor
application behavior and troubleshoot issues.

Features:
- Real-time log viewing
- Filtering by log level, module, and time range
- Log statistics and visualizations
- Search functionality

Usage:
    python tools/log_dashboard.py [--port PORT] [--log-dir LOG_DIR]

Arguments:
    --port PORT       Port to run the dashboard on (default: 8050)
    --log-dir LOG_DIR Directory containing log files (default: current directory)
"""

import argparse
import datetime
import glob
import json
import logging
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

try:
    import dash
    from dash import dcc, html
    from dash.dependencies import Input, Output, State
    import dash_bootstrap_components as dbc
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError as e:
    logger.error(f"Required packages not installed: {e}")
    logger.info("Install required packages with: pip install dash dash-bootstrap-components pandas plotly")
    sys.exit(1)

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

def parse_log_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse a log file into a list of log entries.
    
    Args:
        file_path: Path to the log file
        
    Returns:
        List of dictionaries containing log entries
    """
    log_entries = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                match = LOG_PATTERN.match(line.strip())
                if match:
                    entry = match.groupdict()
                    entry["timestamp"] = datetime.datetime.strptime(
                        entry["timestamp"].split(".")[0],
                        "%Y-%m-%d %H:%M:%S"
                    )
                    log_entries.append(entry)
                else:
                    # Handle multi-line entries (e.g., tracebacks)
                    if log_entries:
                        log_entries[-1]["message"] += "\n" + line.strip()
    except Exception as e:
        logger.error(f"Error parsing log file {file_path}: {e}")
    
    return log_entries

def get_log_files(log_dir: str) -> List[str]:
    """Get all log files in the specified directory.
    
    Args:
        log_dir: Directory containing log files
        
    Returns:
        List of log file paths
    """
    return glob.glob(os.path.join(log_dir, "*.log"))

def get_log_statistics(log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics from log entries.
    
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
        }
    
    # Count by level
    level_counts = Counter(entry["level"] for entry in log_entries)
    
    # Count by module
    module_counts = Counter(entry["name"] for entry in log_entries)
    
    # Count by hour
    hour_counts = Counter(entry["timestamp"].hour for entry in log_entries)
    
    # Count by date
    date_counts = Counter(entry["timestamp"].date() for entry in log_entries)
    
    return {
        "total": len(log_entries),
        "by_level": dict(level_counts),
        "by_module": dict(module_counts),
        "by_hour": dict(hour_counts),
        "by_date": {str(date): count for date, count in date_counts.items()},
    }

def create_dashboard(log_dir: str) -> dash.Dash:
    """Create the Dash application for the log dashboard.
    
    Args:
        log_dir: Directory containing log files
        
    Returns:
        Dash application
    """
    # Create Dash app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="pAIssive_income Log Dashboard",
    )
    
    # Define layout
    app.layout = dbc.Container(
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
        """Update log entries when the log file changes or on interval.
        
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
        """Update charts based on log entries and filters.
        
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
        """Update log table based on log entries and filters.
        
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
                                    className=f"badge me-2",
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
    
    return app

def main() -> int:
    """Main function.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Log Dashboard for pAIssive_income")
    parser.add_argument("--port", type=int, default=8050, help="Port to run the dashboard on")
    parser.add_argument("--log-dir", type=str, default=".", help="Directory containing log files")
    args = parser.parse_args()
    
    # Check if log directory exists
    if not os.path.isdir(args.log_dir):
        logger.error(f"Log directory does not exist: {args.log_dir}")
        return 1
    
    # Check if log files exist
    log_files = get_log_files(args.log_dir)
    if not log_files:
        logger.warning(f"No log files found in directory: {args.log_dir}")
    
    # Create and run dashboard
    app = create_dashboard(args.log_dir)
    logger.info(f"Starting log dashboard on http://localhost:{args.port}")
    app.run_server(debug=True, port=args.port)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

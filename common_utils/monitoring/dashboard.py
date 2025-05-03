"""
Monitoring dashboard for pAIssive_income application.

This module provides a web-based dashboard for visualizing metrics, logs, and system
health information. It integrates with the monitoring system and can be embedded
in the application or run as a standalone service.
"""

import time


import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

import pkg_resources
from datetime import datetime, timedelta

from common_utils.logging import get_logger
from common_utils.monitoring.metrics import export_metrics, get_metrics
from common_utils.monitoring.health import get_health_status
from common_utils.monitoring.system import get_system_metrics, monitor_resources

logger 
    import dash
    from dash import dcc, html
    import plotly.graph_objs as go
    import pandas as pd
    DASHBOARD_AVAILABLE 
        
        import random
    import argparse

= get_logger(__name__)

# Check if dashboard dependencies are installed
DASHBOARD_AVAILABLE = False
try:

= True
except ImportError:
    logger.warning("Dashboard dependencies not installed. Run 'pip install dash plotly pandas' to enable the monitoring dashboard.")


class MonitoringDashboard:
    """
    Web-based dashboard for monitoring application metrics and logs.
    
    This class provides a Dash application for visualizing metrics,
    system health, and logs in a web browser.
    """
    
    def __init__(self, app_name: str = "pAIssive Income Monitoring"):
        """
        Initialize the monitoring dashboard.
        
        Args:
            app_name: Name of the application to display in the dashboard
        """
        if not DASHBOARD_AVAILABLE:
            raise ImportError("Dashboard dependencies not installed. Run 'pip install dash plotly pandas' to enable the monitoring dashboard.")
        
        self.app_name = app_name
        self.dash_app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.setup_layout()
        self.register_callbacks()
    
    def setup_layout(self):
        """Set up the dashboard layout."""
        self.dash_app.layout = html.Div([
            html.H1(f"{self.app_name} Dashboard"),
            
            dcc.Tabs([
                # Overview Tab
                dcc.Tab(label='Overview', children=[
                    html.Div([
                        html.H2('System Health'),
                        html.Div(id='health-status'),
                        
                        html.H2('System Resources'),
                        dcc.Graph(id='cpu-gauge'),
                        dcc.Graph(id='memory-gauge'),
                        
                        html.H2('API Response Times'),
                        dcc.Graph(id='api-response-times'),
                        
                        dcc.Interval(
                            id='interval-overview',
                            interval=5000,  # in milliseconds
                            n_intervals=0
                        )
                    ])
                ]),
                
                # Metrics Tab
                dcc.Tab(label='Metrics', children=[
                    html.Div([
                        html.H2('Application Metrics'),
                        
                        # Metric filters
                        html.Div([
                            html.Label('Filter by Category:'),
                            dcc.Dropdown(
                                id='metric-category-filter',
                                options=[
                                    {'label': 'All', 'value': 'all'},
                                    {'label': 'System', 'value': 'system'},
                                    {'label': 'API', 'value': 'api'},
                                    {'label': 'Database', 'value': 'db'},
                                    {'label': 'Models', 'value': 'model'},
                                ],
                                value='all'
                            ),
                        ]),
                        
                        html.Div(id='metrics-container'),
                        
                        dcc.Interval(
                            id='interval-metrics',
                            interval=10000,  # in milliseconds
                            n_intervals=0
                        )
                    ])
                ]),
                
                # Logs Tab
                dcc.Tab(label='Logs', children=[
                    html.Div([
                        html.H2('Application Logs'),
                        
                        # Log filters
                        html.Div([
                            html.Label('Log Level:'),
                            dcc.Dropdown(
                                id='log-level-filter',
                                options=[
                                    {'label': 'All', 'value': 'all'},
                                    {'label': 'DEBUG', 'value': 'debug'},
                                    {'label': 'INFO', 'value': 'info'},
                                    {'label': 'WARNING', 'value': 'warning'},
                                    {'label': 'ERROR', 'value': 'error'},
                                    {'label': 'CRITICAL', 'value': 'critical'},
                                ],
                                value='all'
                            ),
                            
                            html.Label('Time Range:'),
                            dcc.Dropdown(
                                id='log-time-filter',
                                options=[
                                    {'label': 'Last 15 minutes', 'value': '15m'},
                                    {'label': 'Last hour', 'value': '1h'},
                                    {'label': 'Last 4 hours', 'value': '4h'},
                                    {'label': 'Last 24 hours', 'value': '24h'},
                                    {'label': 'Last 7 days', 'value': '7d'},
                                ],
                                value='1h'
                            ),
                            
                            html.Label('Search:'),
                            dcc.Input(id='log-search', type='text', placeholder='Search logs...'),
                            
                            html.Button('Refresh', id='log-refresh-button'),
                        ]),
                        
                        # Log table
                        html.Div(id='logs-container'),
                        
                        # Pagination
                        html.Div([
                            html.Button('Previous', id='logs-previous'),
                            html.Span(id='logs-page-info'),
                            html.Button('Next', id='logs-next'),
                        ], style={'marginTop': '10px'}),
                        
                        dcc.Store(id='logs-current-page', data=1),
                        dcc.Store(id='logs-total-pages', data=1),
                        
                        dcc.Interval(
                            id='interval-logs',
                            interval=60000,  # in milliseconds
                            n_intervals=0
                        )
                    ])
                ]),
                
                # System Metrics Tab
                dcc.Tab(label='System', children=[
                    html.Div([
                        html.H2('System Metrics'),
                        
                        html.Div([
                            dcc.Graph(id='cpu-timeline'),
                            dcc.Graph(id='memory-timeline'),
                            dcc.Graph(id='disk-timeline'),
                            dcc.Graph(id='network-timeline'),
                        ]),
                        
                        dcc.Interval(
                            id='interval-system',
                            interval=15000,  # in milliseconds
                            n_intervals=0
                        )
                    ])
                ]),
            ])
        ])
    
    def register_callbacks(self):
        """Register the dashboard callbacks for updating data."""
        @self.dash_app.callback(
            [
                dash.dependencies.Output('health-status', 'children'),
                dash.dependencies.Output('cpu-gauge', 'figure'),
                dash.dependencies.Output('memory-gauge', 'figure'),
                dash.dependencies.Output('api-response-times', 'figure')
            ],
            [dash.dependencies.Input('interval-overview', 'n_intervals')]
        )
        def update_overview(n):
            # Get system metrics
            metrics = get_system_metrics()
            health = get_health_status()
            
            # Create health status display
            health_status = html.Div([
                html.H3(f"Status: {health.get('status', 'Unknown')}",
                        style={'color': 'green' if health.get('status') == 'healthy' else 'red'}),
                html.Div([
                    html.H4(component),
                    html.P(f"Status: {details.get('status', 'Unknown')}"),
                    html.P(f"Details: {json.dumps(details.get('details', {}), indent=2)}")
                ]) for component, details in health.get('components', {}).items()
            ])
            
            # Create CPU gauge
            cpu_data = metrics.get('cpu', {})
            cpu_figure = go.Figure(go.Indicator(
                mode="gauge+number",
                value=cpu_data.get('usage_percent', 0),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "CPU Usage (%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "green"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                }
            ))
            
            # Create memory gauge
            memory_data = metrics.get('memory', {})
            memory_figure = go.Figure(go.Indicator(
                mode="gauge+number",
                value=memory_data.get('usage_percent', 0),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Memory Usage (%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "green"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                }
            ))
            
            # Create API response times graph
            # This would normally use real metrics data
            api_figure = go.Figure()
            
            # Example: Using fake data for now
            api_figure.add_trace(go.Scatter(
                x=[datetime.now() - timedelta(minutes=i) for i in range(10, 0, -1)],
                y=[50, 45, 60, 55, 70, 65, 75, 80, 65, 90],
                mode='lines+markers',
                name='API Response Time (ms)'
            ))
            
            api_figure.update_layout(
                title='API Response Times',
                xaxis_title='Time',
                yaxis_title='Response Time (ms)'
            )
            
                    return health_status, cpu_figure, memory_figure, api_figure
        
        @self.dash_app.callback(
            dash.dependencies.Output('metrics-container', 'children'),
            [
                dash.dependencies.Input('interval-metrics', 'n_intervals'),
                dash.dependencies.Input('metric-category-filter', 'value')
            ]
        )
        def update_metrics(n, category):
            # Force metrics export to ensure we have the latest values
            export_metrics()
            
            # Get metrics
            metrics_data = get_metrics()
            
            # Filter metrics by category if specified
            if category != 'all':
                metrics_data = {
                    k: v for k, v in metrics_data.items()
                    if k.startswith(category)
                }
            
            # Create a table of metrics
            metrics_table = html.Table(
                # Header
                [html.Tr([
                    html.Th("Name"),
                    html.Th("Type"),
                    html.Th("Value"),
                    html.Th("Description"),
                    html.Th("Last Updated")
                ])] +
                # Body
                [html.Tr([
                    html.Td(name),
                    html.Td(data["type"]),
                    html.Td(json.dumps(data["value"])),
                    html.Td(data["description"]),
                    html.Td(datetime.fromtimestamp(data["last_updated"]).strftime("%Y-%m-%d %H:%M:%S"))
                ]) for name, data in sorted(metrics_data.items())]
            )
            
                    return metrics_table
        
        @self.dash_app.callback(
            dash.dependencies.Output('logs-container', 'children'),
            [
                dash.dependencies.Input('interval-logs', 'n_intervals'),
                dash.dependencies.Input('log-refresh-button', 'n_clicks'),
                dash.dependencies.Input('logs-current-page', 'data')
            ],
            [
                dash.dependencies.State('log-level-filter', 'value'),
                dash.dependencies.State('log-time-filter', 'value'),
                dash.dependencies.State('log-search', 'value')
            ]
        )
        def update_logs(n_intervals, n_clicks, page, level, time_range, search):
            # Convert filters to API parameters
            limit = 50  # logs per page
            offset = (page - 1) * limit
            
            level = None if level == "all" else level
            
            # Convert time range to datetime
            end_time = datetime.now()
            if time_range == "15m":
                start_time = end_time - timedelta(minutes=15)
            elif time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "4h":
                start_time = end_time - timedelta(hours=4)
            elif time_range == "24h":
                start_time = end_time - timedelta(hours=24)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(hours=1)  # default to 1 hour
            
            # In a real application, this would call the API to get logs
            # For this example, we'll simulate logs
            logs = self._simulate_logs(
                start_time, 
                end_time, 
                level, 
                limit, 
                offset, 
                search
            )
            
            # Create logs table
            logs_table = html.Table(
                # Header
                [html.Tr([
                    html.Th("Time"),
                    html.Th("Level"),
                    html.Th("Message"),
                    html.Th("Component"),
                    html.Th("Details")
                ])] +
                # Body
                [html.Tr([
                    html.Td(log.get("timestamp", "")),
                    html.Td(log.get("level", ""), style={
                        'color': 'red' if log.get("level") in ["ERROR", "CRITICAL"] else 
                                 'orange' if log.get("level") == "WARNING" else
                                 'blue' if log.get("level") == "INFO" else 'gray'
                    }),
                    html.Td(log.get("message", "")),
                    html.Td(log.get("component", "")),
                    html.Td(json.dumps({k: v for k, v in log.items() if k not in ["timestamp", "level", "message", "component"]}))
                ]) for log in logs.get("logs", [])]
            )
            
            if not logs.get("logs"):
                        return html.Div("No logs found matching the criteria")
            
                    return logs_table
        
        @self.dash_app.callback(
            [
                dash.dependencies.Output('logs-page-info', 'children'),
                dash.dependencies.Output('logs-total-pages', 'data')
            ],
            [
                dash.dependencies.Input('logs-container', 'children'),
                dash.dependencies.Input('logs-current-page', 'data')
            ],
            [
                dash.dependencies.State('log-level-filter', 'value'),
                dash.dependencies.State('log-time-filter', 'value'),
                dash.dependencies.State('log-search', 'value')
            ]
        )
        def update_page_info(logs_container, current_page, level, time_range, search):
            # In a real application, this would call the API to get total count
            # For this example, we'll simulate
            total_logs = 532  # simulated total
            logs_per_page = 50
            total_pages = (total_logs + logs_per_page - 1) // logs_per_page
            
                    return f"Page {current_page} of {total_pages}", total_pages
        
        @self.dash_app.callback(
            dash.dependencies.Output('logs-current-page', 'data'),
            [
                dash.dependencies.Input('logs-previous', 'n_clicks'),
                dash.dependencies.Input('logs-next', 'n_clicks'),
                dash.dependencies.Input('log-refresh-button', 'n_clicks')
            ],
            [
                dash.dependencies.State('logs-current-page', 'data'),
                dash.dependencies.State('logs-total-pages', 'data')
            ]
        )
        def update_page(prev_clicks, next_clicks, refresh_clicks, current_page, total_pages):
            ctx = dash.callback_context
            if not ctx.triggered:
                # No clicks yet, return current page
                        return current_page
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'logs-previous':
                # Go to previous page, but not below 1
                        return max(current_page - 1, 1)
            elif button_id == 'logs-next':
                # Go to next page, but not above total
                        return min(current_page + 1, total_pages)
            elif button_id == 'log-refresh-button':
                # Refresh resets to page 1
                        return 1
            else:
                # Default: stay on current page
                        return current_page
        
        @self.dash_app.callback(
            [
                dash.dependencies.Output('cpu-timeline', 'figure'),
                dash.dependencies.Output('memory-timeline', 'figure'),
                dash.dependencies.Output('disk-timeline', 'figure'),
                dash.dependencies.Output('network-timeline', 'figure')
            ],
            [dash.dependencies.Input('interval-system', 'n_intervals')]
        )
        def update_system_timelines(n):
            # In a real application, this would retrieve historic data points
            # Here we'll generate sample data
            
            # Generate timestamps for the past 24 hours
            timestamps = [datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)]
            
            # CPU timeline
            cpu_figure = go.Figure()
            cpu_figure.add_trace(go.Scatter(
                x=timestamps,
                y=[min(95, max(20, 50 + (i % 7) * 5 - (i % 3) * 8)) for i in range(24)],  # Sample CPU usage
                mode='lines+markers',
                name='CPU Usage (%)'
            ))
            cpu_figure.update_layout(
                title='CPU Usage Over Time',
                xaxis_title='Time',
                yaxis_title='Usage (%)',
                yaxis=dict(range=[0, 100])
            )
            
            # Memory timeline
            memory_figure = go.Figure()
            memory_figure.add_trace(go.Scatter(
                x=timestamps,
                y=[min(90, max(30, 60 + (i % 5) * 4 - (i % 2) * 10)) for i in range(24)],  # Sample memory usage
                mode='lines+markers',
                name='Memory Usage (%)'
            ))
            memory_figure.update_layout(
                title='Memory Usage Over Time',
                xaxis_title='Time',
                yaxis_title='Usage (%)',
                yaxis=dict(range=[0, 100])
            )
            
            # Disk timeline
            disk_figure = go.Figure()
            disk_figure.add_trace(go.Scatter(
                x=timestamps,
                y=[min(85, max(70, 75 + i * 0.2)) for i in range(24)],  # Sample disk usage (steadily increasing)
                mode='lines+markers',
                name='Disk Usage (%)'
            ))
            disk_figure.update_layout(
                title='Disk Usage Over Time',
                xaxis_title='Time',
                yaxis_title='Usage (%)',
                yaxis=dict(range=[0, 100])
            )
            
            # Network timeline
            network_figure = go.Figure()
            network_figure.add_trace(go.Scatter(
                x=timestamps,
                y=[max(0.1, min(10, 2 + (i % 12) * 0.5 + (i % 4) * 1)) for i in range(24)],  # Sample network MB/s
                mode='lines+markers',
                name='Network Traffic (MB/s)',
                line=dict(color='blue')
            ))
            network_figure.update_layout(
                title='Network Traffic Over Time',
                xaxis_title='Time',
                yaxis_title='Traffic (MB/s)'
            )
            
                    return cpu_figure, memory_figure, disk_figure, network_figure
    
    def _simulate_logs(self, start_time, end_time, level, limit, offset, search_term):
        """Generate simulated logs for demonstration purposes."""
        # In a real application, this would make an API call
        
        # Generate random log entries
        components = ['api', 'model', 'database', 'ui', 'scheduler', 'auth']
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        messages = [
            'Request processed successfully',
            'Database query completed',
            'Model inference completed',
            'API request received',
            'User authentication successful',
            'Cache miss, fetching from database',
            'Background job scheduled',
            'Data synchronization completed',
            'Failed to connect to database',
            'API rate limit exceeded',
            'Model loading error',
            'Validation failed for input data',
            'Security warning: multiple failed login attempts'
        ]

        
        logs = []
        for i in range(offset, offset + limit):
            # Generate a random time within the range
            time_range = (end_time - start_time).total_seconds()
            random_seconds = random.randint(0, int(time_range))
            log_time = start_time + timedelta(seconds=random_seconds)
            
            # Generate a random log level, weighted towards INFO
            rand_level = random.choices(
                levels, 
                weights=[0.1, 0.6, 0.15, 0.1, 0.05],
                k=1
            )[0]
            
            # Skip if filtering by level
            if level and level.upper() != rand_level:
                continue
            
            # Generate a random component and message
            component = random.choice(components)
            message = random.choice(messages)
            
            # Skip if filtering by search term
            if search_term and search_term.lower() not in message.lower():
                continue
            
            # Generate additional details based on the message
            details = {}
            if 'database' in message.lower():
                details['query_time_ms'] = random.randint(5, 500)
                details['rows_affected'] = random.randint(0, 100)
            elif 'model' in message.lower():
                details['model_name'] = f"model-v{random.randint(1, 3)}"
                details['inference_time_ms'] = random.randint(50, 2000)
                details['tokens'] = random.randint(10, 1000)
            elif 'api' in message.lower():
                details['endpoint'] = f"/{random.choice(['users', 'products', 'orders'])}"
                details['method'] = random.choice(['GET', 'POST', 'PUT', 'DELETE'])
                details['status_code'] = random.choice([200, 201, 400, 401, 403, 404, 500])
            
            logs.append({
                "timestamp": log_time.strftime("%Y-%m-%d %H:%M:%S.%")[:-3],
                "level": rand_level,
                "component": component,
                "message": message,
                **details
            })
        
        # In a real application, we'd return the actual count
        total = random.randint(max(limit, 100), 1000)  # Simulated total
        
                return {
            "logs": logs,
            "total": total,
            "metadata": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "level": level,
                "limit": limit,
                "offset": offset,
                "search_term": search_term,
            }
        }
    
    def run_server(self, host: str = '0.0.0.0', port: int = 8050, debug: bool = False):
        """
        Run the dashboard server.
        
        Args:
            host: Host to bind the server to
            port: Port to bind the server to
            debug: Whether to run in debug mode
        """
        logger.info(f"Starting monitoring dashboard on http://{host}:{port}")
        
        # Start system monitoring in the background
        monitor_resources(interval=15, start_monitoring=True)
        
        # Run the Dash application
        self.dash_app.run_server(
            host=host,
            port=port,
            debug=debug
        )


# Function to start the dashboard
def start_dashboard(
    host: str = '0.0.0.0',
    port: int = 8050,
    debug: bool = False,
    open_browser: bool = True
):
    """
    Start the monitoring dashboard.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to run in debug mode
        open_browser: Whether to automatically open the dashboard in a browser
    """
    try:
        dashboard = MonitoringDashboard()
        dashboard.run_server(host, port, debug)
    except ImportError as e:
        logger.error(f"Could not start dashboard: {e}")
        print("Could not start the monitoring dashboard. Please install the required dependencies:")
        print("pip install dash plotly pandas")
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")
        print(f"Error starting dashboard: {e}")


if __name__ == "__main__":
    # This allows running the dashboard as a standalone module

    
    parser = argparse.ArgumentParser(description="Start the monitoring dashboard")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8050, help="Port to bind the server to")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    
    start_dashboard(args.host, args.port, args.debug)
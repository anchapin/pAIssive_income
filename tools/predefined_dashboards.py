"""Predefined dashboard layouts for common monitoring scenarios."""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_error_monitoring_dashboard():
    """
    Create an error monitoring dashboard.

    Returns:
        Dashboard layout components

    """
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Error Rate Over Time"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="error-rate-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Error Distribution by Module"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="error-module-distribution"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Error Patterns"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="error-patterns-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Exception Stack Traces"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="exception-stack-traces"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Recent Errors"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="recent-errors-table"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        dcc.Store(id="error-monitoring-store"),
    ]


def create_performance_monitoring_dashboard():
    """
    Create a performance monitoring dashboard.

    Returns:
        Dashboard layout components

    """
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("API Latency"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="api-latency-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Database Query Time"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="db-query-time-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Response Time Distribution"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="response-time-distribution"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Memory Usage"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="memory-usage-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Performance Bottlenecks"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="performance-bottlenecks"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        dcc.Store(id="performance-monitoring-store"),
    ]


def create_security_monitoring_dashboard():
    """
    Create a security monitoring dashboard.

    Returns:
        Dashboard layout components

    """
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Authentication Attempts"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="auth-attempts-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Authorization Failures"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="auth-failures-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Suspicious Activity"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="suspicious-activity"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Security Alerts"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="security-alerts"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Audit Logs"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="security-audit-logs"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        dcc.Store(id="security-monitoring-store"),
    ]


def create_service_health_dashboard():
    """
    Create a service health dashboard.

    Returns:
        Dashboard layout components

    """
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Service Uptime"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="service-uptime-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Error Rates by Service"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="service-error-rates"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Response Times by Service"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="service-response-times"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Resource Usage by Service"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="service-resource-usage"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                    lg=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Health Checks"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="health-checks"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        dcc.Store(id="service-health-store"),
    ]


def get_dashboard_layout(dashboard_type):
    """
    Get the layout for a specific dashboard type.

    Args:
        dashboard_type: Type of dashboard to create

    Returns:
        Dashboard layout components

    """
    if dashboard_type == "error_monitoring":
        return create_error_monitoring_dashboard()
    if dashboard_type == "performance_monitoring":
        return create_performance_monitoring_dashboard()
    if dashboard_type == "security_monitoring":
        return create_security_monitoring_dashboard()
    if dashboard_type == "service_health":
        return create_service_health_dashboard()
    return html.Div("Unknown dashboard type")

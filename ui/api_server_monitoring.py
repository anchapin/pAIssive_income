"""
Monitoring endpoints for the API server.

This module provides endpoints for monitoring the API server.
"""

import logging
import os
import platform
from datetime import datetime

import psutil

from flask import Blueprint, current_app, jsonify
from monitoring.health import health_check
from monitoring.metrics import get_metrics

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/api/monitoring")


@monitoring_bp.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.

    Returns:
        JSON response with health check results
    """
    return jsonify(health_check())


@monitoring_bp.route("/metrics", methods=["GET"])
def metrics():
    """
    Metrics endpoint.

    Returns:
        JSON response with metrics
    """
    return jsonify(get_metrics())


@monitoring_bp.route("/info", methods=["GET"])
def info():
    """
    System information endpoint.

    Returns:
        JSON response with system information
    """
    # Get process information
    process = psutil.Process(os.getpid())

    # Get memory information
    memory_info = process.memory_info()

    # Get CPU information
    cpu_percent = process.cpu_percent(interval=0.1)

    # Get uptime
    start_time = datetime.fromtimestamp(process.create_time())
    uptime = (datetime.now() - start_time).total_seconds()

    # Get system information
    system_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
    }

    # Get Flask information
    flask_info = {
        "version": current_app.config.get("VERSION", "unknown"),
        "debug": current_app.debug,
        "testing": current_app.testing,
        "secret_key": bool(current_app.secret_key),
    }

    # Return information
    return jsonify(
        {
            "process": {
                "pid": process.pid,
                "memory_rss": memory_info.rss,
                "memory_vms": memory_info.vms,
                "cpu_percent": cpu_percent,
                "threads": process.num_threads(),
                "start_time": start_time.isoformat(),
                "uptime": uptime,
            },
            "system": system_info,
            "flask": flask_info,
        }
    )


def init_app(app):
    """
    Initialize the monitoring blueprint.

    Args:
        app: Flask application
    """
    app.register_blueprint(monitoring_bp)

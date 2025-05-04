"""
Service discovery setup script for pAIssive income microservices.

This module provides utilities for setting up and configuring service discovery
in different environments (development, testing, production).
"""


import logging
import os
import subprocess
import time
from typing import Any, Dict, Optional

import requests

logger
import json
import argparse
import sys

= logging.getLogger(__name__)


class ServiceDiscoverySetup:
    """Utility for setting up service discovery in different environments."""

    @staticmethod
    def check_consul_running(host: str = "localhost", port: int = 8500) -> bool:
    """
    Check if Consul is running at the specified host and port.

    Args:
    host: Consul host (default: localhost)
    port: Consul port (default: 8500)

    Returns:
    bool: True if Consul is running, False otherwise
    """
    try:
    response = requests.get(f"http://{host}:{port}/v1/status/leader", timeout=2)
    return response.status_code == 200
except requests.exceptions.RequestException:
    return False

    @staticmethod
    def start_consul_dev(
    data_dir: str = "./consul_data",
    config_dir: Optional[str] = None,
    ui: bool = True,
    server: bool = True,
    dev_mode: bool = True,
    wait: bool = True,
    ) -> subprocess.Popen:
    """
    Start Consul in development mode.

    Args:
    data_dir: Directory for Consul data
    config_dir: Directory for Consul configuration
    ui: Whether to enable the web UI (default: True)
    server: Whether to run in server mode (default: True)
    dev_mode: Whether to run in dev mode (default: True)
    wait: Whether to wait for Consul to start (default: True)

    Returns:
    subprocess.Popen: The Consul process
    """
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    # Build command
    cmd = ["consul", "agent", "-data-dir", data_dir]

    if config_dir:
    cmd.extend(["-config-dir", config_dir])

    if ui:
    cmd.append("-ui")

    if server:
    cmd.append("-server")
    cmd.append("-bootstrap-expect=1")

    if dev_mode:
    cmd.append("-dev")

    # Run Consul
    logger.info(f"Starting Consul with command: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for Consul to start
    if wait:
    max_attempts = 10
    attempt = 0

    while attempt < max_attempts:
    if ServiceDiscoverySetup.check_consul_running():
    logger.info("Consul is running")
    break

    logger.info(
    f"Waiting for Consul to start (attempt {attempt + 1}/{max_attempts})..."
    )
    time.sleep(1)
    attempt += 1

    if attempt == max_attempts:
    logger.warning("Consul may not have started properly")

    return process

    @staticmethod
    def generate_consul_config(
    config_dir: str,
    datacenter: str = "dc1",
    bind_addr: str = "0.0.0.0",
    client_addr: str = "0.0.0.0",
    server: bool = True,
    bootstrap: bool = True,
    ui: bool = True,
    services: Optional[Dict[str, Any]] = None,
    ) -> None:
    """
    Generate Consul configuration files.

    Args:
    config_dir: Directory for configuration files
    datacenter: Datacenter name
    bind_addr: Address to bind Consul to
    client_addr: Address for client interfaces
    server: Whether this is a server node
    bootstrap: Whether this is a bootstrap node
    ui: Whether to enable the web UI
    services: Dictionary of services to register at startup
    """


    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Create base configuration
    base_config = {
    "datacenter": datacenter,
    "data_dir": "./data",
    "log_level": "INFO",
    "bind_addr": bind_addr,
    "client_addr": client_addr,
    "server": server,
    "ui": ui,
    }

    if server and bootstrap:
    base_config["bootstrap"] = True

    # Write base configuration
    with open(os.path.join(config_dir, "config.json"), "w") as f:
    json.dump(base_config, f, indent=2)

    # Write service configurations if provided
    if services:
    for service_name, service_config in services.items():
    with open(
    os.path.join(config_dir, f"service-{service_name}.json"), "w"
    ) as f:
    json.dump({"service": service_config}, f, indent=2)

    logger.info(f"Generated Consul configuration in {config_dir}")

    @staticmethod
    def create_demo_services_config(config_dir: str) -> None:
    """
    Create demo service configurations for testing.

    Args:
    config_dir: Directory for configuration files
    """
    services = {
    "api-gateway": {
    "name": "api-gateway",
    "port": 8000,
    "tags": ["api", "gateway", "entry-point"],
    "check": {"http": "http://localhost:8000/health", "interval": "10s"},
    },
    "ui-service": {
    "name": "ui-service",
    "port": 3000,
    "tags": ["ui", "frontend", "react"],
    "check": {"http": "http://localhost:3000/health", "interval": "10s"},
    },
    "niche-analysis-service": {
    "name": "niche-analysis-service",
    "port": 8001,
    "tags": ["backend", "analysis"],
    "check": {"http": "http://localhost:8001/health", "interval": "10s"},
    },
    "ai-models-service": {
    "name": "ai-models-service",
    "port": 8002,
    "tags": ["backend", "ai"],
    "check": {"http": "http://localhost:8002/health", "interval": "10s"},
    },
    "marketing-service": {
    "name": "marketing-service",
    "port": 8003,
    "tags": ["backend", "marketing"],
    "check": {"http": "http://localhost:8003/health", "interval": "10s"},
    },
    }

    ServiceDiscoverySetup.generate_consul_config(
    config_dir=config_dir, services=services
    )


    # Command-line interface
    if __name__ == "__main__":



    # Configure logging
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Parse arguments
    parser = argparse.ArgumentParser(description="Service discovery setup")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Start Consul command
    start_parser = subparsers.add_parser("start-consul", help="Start Consul")
    start_parser.add_argument(
    "--data-dir", default="./consul_data", help="Data directory"
    )
    start_parser.add_argument(
    "--config-dir", default=None, help="Configuration directory"
    )
    start_parser.add_argument(
    "--no-ui", action="store_false", dest="ui", help="Disable UI"
    )
    start_parser.add_argument(
    "--no-server", action="store_false", dest="server", help="Disable server mode"
    )
    start_parser.add_argument(
    "--no-dev", action="store_false", dest="dev_mode", help="Disable dev mode"
    )

    # Generate config command
    config_parser = subparsers.add_parser(
    "generate-config", help="Generate Consul configuration"
    )
    config_parser.add_argument(
    "--config-dir", required=True, help="Configuration directory"
    )
    config_parser.add_argument("--datacenter", default="dc1", help="Datacenter name")
    config_parser.add_argument("--bind-addr", default="0.0.0.0", help="Bind address")
    config_parser.add_argument(
    "--client-addr", default="0.0.0.0", help="Client address"
    )
    config_parser.add_argument(
    "--no-server", action="store_false", dest="server", help="Disable server mode"
    )
    config_parser.add_argument(
    "--no-bootstrap",
    action="store_false",
    dest="bootstrap",
    help="Disable bootstrap mode",
    )
    config_parser.add_argument(
    "--no-ui", action="store_false", dest="ui", help="Disable UI"
    )

    # Create demo services command
    demo_parser = subparsers.add_parser(
    "create-demo", help="Create demo service configurations"
    )
    demo_parser.add_argument(
    "--config-dir", required=True, help="Configuration directory"
    )

    # Check status command
    check_parser = subparsers.add_parser("check", help="Check if Consul is running")
    check_parser.add_argument("--host", default="localhost", help="Consul host")
    check_parser.add_argument("--port", type=int, default=8500, help="Consul port")

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == "start-consul":
    try:
    process = ServiceDiscoverySetup.start_consul_dev(
    data_dir=args.data_dir,
    config_dir=args.config_dir,
    ui=args.ui,
    server=args.server,
    dev_mode=args.dev_mode,
    )

    # Keep the script running while Consul is running
    logger.info("Consul started. Press Ctrl+C to stop.")
    try:
    process.wait()
except KeyboardInterrupt:
    process.terminate()
    logger.info("Stopping Consul...")
    process.wait()
    logger.info("Consul stopped.")
except Exception as e:
    logger.error(f"Failed to start Consul: {str(e)}")
    sys.exit(1)

    elif args.command == "generate-config":
    try:
    ServiceDiscoverySetup.generate_consul_config(
    config_dir=args.config_dir,
    datacenter=args.datacenter,
    bind_addr=args.bind_addr,
    client_addr=args.client_addr,
    server=args.server,
    bootstrap=args.bootstrap,
    ui=args.ui,
    )
except Exception as e:
    logger.error(f"Failed to generate Consul configuration: {str(e)}")
    sys.exit(1)

    elif args.command == "create-demo":
    try:
    ServiceDiscoverySetup.create_demo_services_config(args.config_dir)
except Exception as e:
    logger.error(f"Failed to create demo services: {str(e)}")
    sys.exit(1)

    elif args.command == "check":
    running = ServiceDiscoverySetup.check_consul_running(
    host=args.host, port=args.port
    )
    if running:
    logger.info("Consul is running.")
    else:
    logger.info("Consul is NOT running.")
    sys.exit(1)

    else:
    parser.print_help()
    sys.exit(1)
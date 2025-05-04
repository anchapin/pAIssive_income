
import argparse
import logging
import os
import subprocess
import sys
import time

#!/usr/bin/env python
"""
"""
Startup script for the pAIssive income microservices architecture.
Startup script for the pAIssive income microservices architecture.


This script starts all the required components for the microservices architecture,
This script starts all the required components for the microservices architecture,
including the service registry and the microservices.
including the service registry and the microservices.
"""
"""














# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




def check_consul_installation() -> bool:
    def check_consul_installation() -> bool:
    """
    """
    Check if Consul is installed.
    Check if Consul is installed.


    Returns:
    Returns:
    bool: True if Consul is installed, False otherwise
    bool: True if Consul is installed, False otherwise
    """
    """
    try:
    try:
    result = subprocess.run(
    result = subprocess.run(
    ["consul", "--version"],
    ["consul", "--version"],
    stdout=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    text=True,
    )
    )
    return result.returncode == 0
    return result.returncode == 0
except FileNotFoundError:
except FileNotFoundError:
    return False
    return False




    def start_consul(data_dir: str = "./consul_data", port: int = 8500) -> subprocess.Popen:
    def start_consul(data_dir: str = "./consul_data", port: int = 8500) -> subprocess.Popen:
    """
    """
    Start Consul in development mode.
    Start Consul in development mode.


    Args:
    Args:
    data_dir: Directory for Consul data (default: "./consul_data")
    data_dir: Directory for Consul data (default: "./consul_data")
    port: Port for Consul HTTP API (default: 8500)
    port: Port for Consul HTTP API (default: 8500)


    Returns:
    Returns:
    subprocess.Popen: The Consul process
    subprocess.Popen: The Consul process
    """
    """
    # Create data directory if it doesn't exist
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)


    # Command to start Consul in development mode
    # Command to start Consul in development mode
    cmd = [
    cmd = [
    "consul",
    "consul",
    "agent",
    "agent",
    "-dev",
    "-dev",
    "-data-dir",
    "-data-dir",
    data_dir,
    data_dir,
    "-ui",
    "-ui",
    "-bind",
    "-bind",
    "127.0.0.1",
    "127.0.0.1",
    "-client",
    "-client",
    "0.0.0.0",
    "0.0.0.0",
    ]
    ]


    if port != 8500:
    if port != 8500:
    cmd.extend(["-http-port", str(port)])
    cmd.extend(["-http-port", str(port)])


    logger.info(f"Starting Consul with command: {' '.join(cmd)}")
    logger.info(f"Starting Consul with command: {' '.join(cmd)}")
    process = subprocess.Popen(
    process = subprocess.Popen(
    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    )


    # Wait for Consul to start
    # Wait for Consul to start
    max_attempts = 10
    max_attempts = 10
    attempt = 0
    attempt = 0


    while attempt < max_attempts:
    while attempt < max_attempts:
    try:
    try:
    result = subprocess.run(
    result = subprocess.run(
    ["consul", "catalog", "services"],
    ["consul", "catalog", "services"],
    stdout=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    text=True,
    )
    )
    if result.returncode == 0:
    if result.returncode == 0:
    logger.info("Consul is running")
    logger.info("Consul is running")
    break
    break
except Exception:
except Exception:
    pass
    pass


    logger.info(
    logger.info(
    f"Waiting for Consul to start (attempt {attempt + 1}/{max_attempts})..."
    f"Waiting for Consul to start (attempt {attempt + 1}/{max_attempts})..."
    )
    )
    time.sleep(1)
    time.sleep(1)
    attempt += 1
    attempt += 1


    if attempt == max_attempts:
    if attempt == max_attempts:
    logger.warning("Consul may not have started properly")
    logger.warning("Consul may not have started properly")


    return process
    return process




    def start_service(service_name: str, script_path: str, port: int) -> subprocess.Popen:
    def start_service(service_name: str, script_path: str, port: int) -> subprocess.Popen:
    """
    """
    Start a microservice.
    Start a microservice.


    Args:
    Args:
    service_name: Name of the service
    service_name: Name of the service
    script_path: Path to the service script
    script_path: Path to the service script
    port: Port for the service to listen on
    port: Port for the service to listen on


    Returns:
    Returns:
    subprocess.Popen: The service process
    subprocess.Popen: The service process
    """
    """
    # Make sure the directory exists
    # Make sure the directory exists
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    os.makedirs(os.path.dirname(script_path), exist_ok=True)


    logger.info(f"Starting {service_name} on port {port}")
    logger.info(f"Starting {service_name} on port {port}")


    # Set up environment variables for service registration
    # Set up environment variables for service registration
    env = os.environ.copy()
    env = os.environ.copy()
    env["SERVICE_REGISTRY_HOST"] = "localhost"
    env["SERVICE_REGISTRY_HOST"] = "localhost"
    env["SERVICE_REGISTRY_PORT"] = "8500"
    env["SERVICE_REGISTRY_PORT"] = "8500"
    env["ENVIRONMENT"] = "development"
    env["ENVIRONMENT"] = "development"
    env["PYTHONPATH"] = os.getcwd()
    env["PYTHONPATH"] = os.getcwd()


    process = subprocess.Popen(
    process = subprocess.Popen(
    [sys.executable, script_path, "--port", str(port)],
    [sys.executable, script_path, "--port", str(port)],
    stdout=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    text=True,
    env=env,
    env=env,
    )
    )


    return process
    return process




    def main():
    def main():
    """Main function to start all services."""
    parser = argparse.ArgumentParser(description="Start pAIssive income microservices")
    parser.add_argument(
    "--no-consul", action="store_true", help="Don't start Consul (use existing)"
    )
    parser.add_argument(
    "--consul-port", type=int, default=8500, help="Port for Consul HTTP API"
    )
    parser.add_argument(
    "--api-gateway-port", type=int, default=8000, help="Port for API Gateway"
    )
    parser.add_argument("--ui-port", type=int, default=3000, help="Port for UI Service")
    parser.add_argument(
    "--ai-models-port", type=int, default=8002, help="Port for AI Models Service"
    )
    parser.add_argument(
    "--niche-analysis-port",
    type=int,
    default=8001,
    help="Port for Niche Analysis Service",
    )

    args = parser.parse_args()

    processes = {}

    try:
    # Check if Consul is installed
    if not check_consul_installation():
    logger.error(
    "Consul is not installed. Please install Consul before running this script."
    )
    logger.error(
    "See https://developer.hashicorp.com/consul/downloads for installation instructions."
    )
    return 1

    # Start Consul if requested
    if not args.no_consul:
    processes["consul"] = start_consul(port=args.consul_port)
    time.sleep(2)  # Wait for Consul to initialize

    # Start API Gateway service
    api_gateway_path = os.path.join("services", "api_gateway", "app.py")
    processes["api_gateway"] = start_service(
    service_name="API Gateway",
    script_path=api_gateway_path,
    port=args.api_gateway_port,
    )

    # Start UI Service
    ui_service_path = os.path.join("services", "ui_service", "app.py")
    processes["ui_service"] = start_service(
    service_name="UI Service", script_path=ui_service_path, port=args.ui_port
    )

    # Start AI Models Service
    ai_models_service_path = os.path.join("services", "ai_models_service", "app.py")
    processes["ai_models_service"] = start_service(
    service_name="AI Models Service",
    script_path=ai_models_service_path,
    port=args.ai_models_port,
    )

    # Start Niche Analysis Service
    niche_analysis_service_path = os.path.join(
    "services", "niche_analysis_service", "app.py"
    )
    processes["niche_analysis_service"] = start_service(
    service_name="Niche Analysis Service",
    script_path=niche_analysis_service_path,
    port=args.niche_analysis_port,
    )

    # Print access information
    logger.info("\n" + "=" * 80)
    logger.info("pAIssive Income Microservices are running!")
    logger.info("=" * 80)
    logger.info(f"Consul UI:           http://localhost:{args.consul_port}/ui/")
    logger.info(f"API Gateway:         http://localhost:{args.api_gateway_port}/")
    logger.info(f"UI Service:          http://localhost:{args.ui_port}/")
    logger.info(f"AI Models API:       http://localhost:{args.ai_models_port}/docs")
    logger.info(
    f"Niche Analysis API:  http://localhost:{args.niche_analysis_port}/docs"
    )
    logger.info("=" * 80)
    logger.info("Press Ctrl+C to stop all services.")

    # Keep the script running
    while True:
    time.sleep(1)

    # Check if any process has terminated
    for name, process in list(processes.items()):
    if process.poll() is not None:
    logger.error(
    f"{name} terminated unexpectedly with return code {process.returncode}"
    )

    # Get the error output
    stderr = process.stderr.read() if process.stderr else ""
    if stderr:
    logger.error(f"{name} error output: {stderr}")

    # Remove from processes dict
    del processes[name]

    # Exit if all processes have terminated
    if not processes:
    logger.error("All services have terminated. Exiting.")
    return 1

except KeyboardInterrupt:
    logger.info("Stopping all services...")

finally:
    # Terminate all processes
    for name, process in processes.items():
    logger.info(f"Terminating {name}...")
    process.terminate()
    try:
    process.wait(timeout=5)
except subprocess.TimeoutExpired:
    logger.warning(f"{name} did not terminate gracefully. Killing...")
    process.kill()

    logger.info("All services stopped.")

    return 0


    if __name__ == "__main__":
    sys.exit(main())
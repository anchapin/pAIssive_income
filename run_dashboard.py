
import argparse
import sys
from pathlib import Path


from common_utils.logging import LogLevel, setup_logging

setup_logging
    from common_utils.monitoring.dashboard import start_dashboard
except ImportError as e

#!/usr/bin/env python
"""
Dashboard launcher for the pAIssive_income monitoring system.

This script launches the monitoring dashboard as a standalone web application,
allowing users to monitor metrics, logs, and system health.
"""


# Ensure the application root is in the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Set up logging before importing the dashboard
(
    level=LogLevel.INFO,
    log_file="logs/dashboard.log",
    log_to_console=True,
    log_to_file=True,
)

# Import the dashboard module
try:
:
    print(f"Error importing dashboard module: {e}")
    print("\nMake sure you have the required dependencies installed:")
    print("pip install dash plotly pandas")
    sys.exit(1)


def main():
    """Parse command line arguments and start the dashboard."""
    parser = argparse.ArgumentParser(description="Start the monitoring dashboard")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument(
        "--port", type=int, default=8050, help="Port to bind the server to"
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

args = parser.parse_args()

print(
        f"Starting pAIssive Income Monitoring Dashboard on http://{args.host}:{args.port}"
    )
    print("Press Ctrl+C to stop the server")

try:
        # Start the dashboard
        start_dashboard(args.host, args.port, args.debug)
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
    except Exception as e:
        print(f"Error running dashboard: {e}")
                    return 1

            return 0


if __name__ == "__main__":
    sys.exit(main())
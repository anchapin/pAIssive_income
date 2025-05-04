"""
Example of API versioning configuration.

This module demonstrates how to configure API versioning.
"""


import logging
import os
import sys
import time
from datetime import datetime, timedelta

from api.config import APIConfig, APIVersion
from api.server import APIServer
from api.version_manager import VersionManager

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# Import API server
# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def configure_version_manager(version_manager: VersionManager) -> None:
    """
    Configure the version manager with sample changes.

    Args:
    version_manager: Version manager to configure
    """
    # Add changes for v1
    version_manager.add_endpoint(
    endpoint="/api/v1/niche-analysis/analyze",
    version=APIVersion.V1,
    description="Start a niche analysis",
    )

    version_manager.add_endpoint(
    endpoint="/api/v1/niche-analysis/analyses",
    version=APIVersion.V1,
    description="Get all niche analyses",
    )

    version_manager.add_endpoint(
    endpoint="/api/v1/monetization/subscription-models",
    version=APIVersion.V1,
    description="Get all subscription models",
    )

    # Add changes for v2
    version_manager.add_endpoint(
    endpoint="/api/v2/niche-analysis/analyze-batch",
    version=APIVersion.V2,
    description="Start a batch niche analysis",
    )

    version_manager.modify_endpoint(
    endpoint="/api/v2/niche-analysis/analyze",
    version=APIVersion.V2,
    description="Modified to support additional parameters",
    )

    # Deprecate an endpoint in v2
    version_manager.deprecate_endpoint(
    endpoint="/api/v1/niche-analysis/analyses",
    version=APIVersion.V2,
    description="Use /api/v2/niche-analysis/analyses instead",
    sunset_date=datetime.now() + timedelta(days=180),
    )

    # Remove an endpoint in v2
    version_manager.remove_endpoint(
    endpoint="/api/v1/monetization/subscription-models",
    version=APIVersion.V2,
    description="Replaced by /api/v2/monetization/subscription-models",
    from_version=APIVersion.V1,
    )


    def create_server() -> APIServer:
    """
    Create an API server with versioning configuration.

    Returns:
    Configured API server
    """
    # Create API configuration
    config = APIConfig(
    # Basic configuration
    host="0.0.0.0",
    port=8000,
    debug=True,
    # API configuration
    version=APIVersion.V2,  # Default to v2
    active_versions=[APIVersion.V1, APIVersion.V2],  # Both v1 and v2 are active
    # Enable all modules
    enable_niche_analysis=True,
    enable_monetization=True,
    enable_marketing=True,
    enable_ai_models=True,
    enable_agent_team=True,
    enable_user=True,
    enable_dashboard=True,
    )

    # Create API server
    server = APIServer(config)

    # Configure version manager
    configure_version_manager(server.version_manager)

    return server


    def main() -> None:
    """
    Main entry point for the example.
    """
    # Create API server
    server = create_server()

    # Start server
    try:
    server.start()

    # Keep the main thread alive


    while True:
    time.sleep(1)

except KeyboardInterrupt:
    logger.info("Stopping server...")
    server.stop()

except Exception as e:
    logger.error(f"Error running server: {str(e)}")
    server.stop()
    sys.exit(1)


    if __name__ == "__main__":
    main()
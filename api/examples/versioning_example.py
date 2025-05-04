"""
"""
Example of API versioning configuration.
Example of API versioning configuration.


This module demonstrates how to configure API versioning.
This module demonstrates how to configure API versioning.
"""
"""




import logging
import logging
import os
import os
import sys
import sys
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta


from api.config import APIConfig, APIVersion
from api.config import APIConfig, APIVersion
from api.server import APIServer
from api.server import APIServer
from api.version_manager import VersionManager
from api.version_manager import VersionManager


# Add the project root to the path so we can import modules
# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# Import API server
# Import API server
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




def configure_version_manager(version_manager: VersionManager) -> None:
    def configure_version_manager(version_manager: VersionManager) -> None:
    """
    """
    Configure the version manager with sample changes.
    Configure the version manager with sample changes.


    Args:
    Args:
    version_manager: Version manager to configure
    version_manager: Version manager to configure
    """
    """
    # Add changes for v1
    # Add changes for v1
    version_manager.add_endpoint(
    version_manager.add_endpoint(
    endpoint="/api/v1/niche-analysis/analyze",
    endpoint="/api/v1/niche-analysis/analyze",
    version=APIVersion.V1,
    version=APIVersion.V1,
    description="Start a niche analysis",
    description="Start a niche analysis",
    )
    )


    version_manager.add_endpoint(
    version_manager.add_endpoint(
    endpoint="/api/v1/niche-analysis/analyses",
    endpoint="/api/v1/niche-analysis/analyses",
    version=APIVersion.V1,
    version=APIVersion.V1,
    description="Get all niche analyses",
    description="Get all niche analyses",
    )
    )


    version_manager.add_endpoint(
    version_manager.add_endpoint(
    endpoint="/api/v1/monetization/subscription-models",
    endpoint="/api/v1/monetization/subscription-models",
    version=APIVersion.V1,
    version=APIVersion.V1,
    description="Get all subscription models",
    description="Get all subscription models",
    )
    )


    # Add changes for v2
    # Add changes for v2
    version_manager.add_endpoint(
    version_manager.add_endpoint(
    endpoint="/api/v2/niche-analysis/analyze-batch",
    endpoint="/api/v2/niche-analysis/analyze-batch",
    version=APIVersion.V2,
    version=APIVersion.V2,
    description="Start a batch niche analysis",
    description="Start a batch niche analysis",
    )
    )


    version_manager.modify_endpoint(
    version_manager.modify_endpoint(
    endpoint="/api/v2/niche-analysis/analyze",
    endpoint="/api/v2/niche-analysis/analyze",
    version=APIVersion.V2,
    version=APIVersion.V2,
    description="Modified to support additional parameters",
    description="Modified to support additional parameters",
    )
    )


    # Deprecate an endpoint in v2
    # Deprecate an endpoint in v2
    version_manager.deprecate_endpoint(
    version_manager.deprecate_endpoint(
    endpoint="/api/v1/niche-analysis/analyses",
    endpoint="/api/v1/niche-analysis/analyses",
    version=APIVersion.V2,
    version=APIVersion.V2,
    description="Use /api/v2/niche-analysis/analyses instead",
    description="Use /api/v2/niche-analysis/analyses instead",
    sunset_date=datetime.now() + timedelta(days=180),
    sunset_date=datetime.now() + timedelta(days=180),
    )
    )


    # Remove an endpoint in v2
    # Remove an endpoint in v2
    version_manager.remove_endpoint(
    version_manager.remove_endpoint(
    endpoint="/api/v1/monetization/subscription-models",
    endpoint="/api/v1/monetization/subscription-models",
    version=APIVersion.V2,
    version=APIVersion.V2,
    description="Replaced by /api/v2/monetization/subscription-models",
    description="Replaced by /api/v2/monetization/subscription-models",
    from_version=APIVersion.V1,
    from_version=APIVersion.V1,
    )
    )




    def create_server() -> APIServer:
    def create_server() -> APIServer:
    """
    """
    Create an API server with versioning configuration.
    Create an API server with versioning configuration.


    Returns:
    Returns:
    Configured API server
    Configured API server
    """
    """
    # Create API configuration
    # Create API configuration
    config = APIConfig(
    config = APIConfig(
    # Basic configuration
    # Basic configuration
    host="0.0.0.0",
    host="0.0.0.0",
    port=8000,
    port=8000,
    debug=True,
    debug=True,
    # API configuration
    # API configuration
    version=APIVersion.V2,  # Default to v2
    version=APIVersion.V2,  # Default to v2
    active_versions=[APIVersion.V1, APIVersion.V2],  # Both v1 and v2 are active
    active_versions=[APIVersion.V1, APIVersion.V2],  # Both v1 and v2 are active
    # Enable all modules
    # Enable all modules
    enable_niche_analysis=True,
    enable_niche_analysis=True,
    enable_monetization=True,
    enable_monetization=True,
    enable_marketing=True,
    enable_marketing=True,
    enable_ai_models=True,
    enable_ai_models=True,
    enable_agent_team=True,
    enable_agent_team=True,
    enable_user=True,
    enable_user=True,
    enable_dashboard=True,
    enable_dashboard=True,
    )
    )


    # Create API server
    # Create API server
    server = APIServer(config)
    server = APIServer(config)


    # Configure version manager
    # Configure version manager
    configure_version_manager(server.version_manager)
    configure_version_manager(server.version_manager)


    return server
    return server




    def main() -> None:
    def main() -> None:
    """
    """
    Main entry point for the example.
    Main entry point for the example.
    """
    """
    # Create API server
    # Create API server
    server = create_server()
    server = create_server()


    # Start server
    # Start server
    try:
    try:
    server.start()
    server.start()


    # Keep the main thread alive
    # Keep the main thread alive




    while True:
    while True:
    time.sleep(1)
    time.sleep(1)


except KeyboardInterrupt:
except KeyboardInterrupt:
    logger.info("Stopping server...")
    logger.info("Stopping server...")
    server.stop()
    server.stop()


except Exception as e:
except Exception as e:
    logger.error(f"Error running server: {str(e)}")
    logger.error(f"Error running server: {str(e)}")
    server.stop()
    server.stop()
    sys.exit(1)
    sys.exit(1)




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()
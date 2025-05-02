"""
Example of API rate limiting configuration.

This module demonstrates how to configure API rate limiting.
"""

import logging
import os
import sys

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.config import APIConfig, RateLimitScope, RateLimitStrategy

# Import API server
from api.server import APIServer

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_server() -> APIServer:
    """
    Create an API server with rate limiting configuration.

    Returns:
        Configured API server
    """
    # Create API configuration
    config = APIConfig(
        # Basic configuration
        host="0.0.0.0",
        port=8000,
        debug=True,
        # Rate limiting configuration
        enable_rate_limit=True,
        rate_limit_strategy=RateLimitStrategy.TOKEN_BUCKET,
        rate_limit_scope=RateLimitScope.IP,
        rate_limit_requests=100,  # 100 requests per minute
        rate_limit_period=60,  # 1 minute
        rate_limit_burst=50,  # Allow bursts of up to 50 requests
        # Rate limit tiers
        rate_limit_tiers={
            "default": 100,
            "basic": 300,
            "premium": 1000,
            "unlimited": 0,  # 0 means no limit
        },
        # Endpoint-specific rate limits
        endpoint_rate_limits={
            "/api/v1/ai-models/inference": 20,  # Limit expensive endpoints
            "/api/v2/ai-models/inference": 30,
        },
        # Rate limit exemptions
        rate_limit_exempt_ips={"127.0.0.1", "::1"},  # Exempt localhost
        rate_limit_exempt_api_keys={"test-api-key"},  # Exempt test API key
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
        import time

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

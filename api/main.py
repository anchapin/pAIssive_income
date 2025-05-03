"""
Main entry point for the API server.

This module provides the main entry point for running the API server.
"""

import argparse
import logging
import os
import sys
from typing import Any, Dict, Optional

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.config import APIConfig, APIVersion, RateLimitScope, RateLimitStrategy

# Import API server
from api.server import APIServer

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="pAIssive Income API Server")

    # Basic configuration
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    # API configuration
    parser.add_argument("--prefix", type=str, default="/api", help="API prefix")
    parser.add_argument("--version", type=str, default="v2", help="Default API version")
    parser.add_argument(
        "--active-versions",
        type=str,
        default="v1,v2",
        help="Comma-separated list of active API versions",
    )
    parser.add_argument(
        "--disable-version-header", action="store_true", help="Disable API version header"
    )
    parser.add_argument(
        "--disable-deprecation-header", action="store_true", help="Disable API deprecation header"
    )

    # GraphQL configuration
    parser.add_argument("--disable-graphql", action="store_true", help="Disable GraphQL API")
    parser.add_argument(
        "--graphql-path", type=str, default="/graphql", help="GraphQL endpoint path"
    )
    parser.add_argument(
        "--disable-graphiql", action="store_true", help="Disable GraphiQL interface"
    )
    parser.add_argument(
        "--disable-graphql-batch", action="store_true", help="Disable GraphQL batch processing"
    )
    parser.add_argument(
        "--disable-graphql-introspection",
        action="store_true",
        help="Disable GraphQL schema introspection",
    )
    parser.add_argument(
        "--disable-graphql-playground", action="store_true", help="Disable GraphQL Playground"
    )

    # Security configuration
    parser.add_argument("--enable-auth", action="store_true", help="Enable authentication")
    parser.add_argument("--enable-https", action="store_true", help="Enable HTTPS")
    parser.add_argument("--ssl-keyfile", type=str, help="SSL key file")
    parser.add_argument("--ssl-certfile", type=str, help="SSL certificate file")

    # Rate limiting configuration
    parser.add_argument("--enable-rate-limit", action="store_true", help="Enable rate limiting")
    parser.add_argument(
        "--rate-limit-strategy",
        type=str,
        default="token_bucket",
        choices=["fixed", "token_bucket", "leaky_bucket", "sliding_window"],
        help="Rate limiting strategy",
    )
    parser.add_argument(
        "--rate-limit-scope",
        type=str,
        default="ip",
        choices=["global", "ip", "api_key", "user", "endpoint"],
        help="Rate limiting scope",
    )
    parser.add_argument(
        "--rate-limit-requests", type=int, default=100, help="Maximum number of requests per period"
    )
    parser.add_argument(
        "--rate-limit-period", type=int, default=60, help="Rate limit period in seconds"
    )
    parser.add_argument(
        "--rate-limit-burst", type=int, default=50, help="Burst size for token bucket algorithm"
    )
    parser.add_argument(
        "--disable-rate-limit-headers", action="store_true", help="Disable rate limit headers"
    )

    # Analytics configuration
    parser.add_argument("--disable-analytics", action="store_true", help="Disable API analytics")
    parser.add_argument("--analytics-db-path", type=str, help="Path to analytics database")
    parser.add_argument(
        "--analytics-retention-days",
        type=int,
        default=365,
        help="Number of days to retain analytics data",
    )
    parser.add_argument(
        "--disable-analytics-dashboard", action="store_true", help="Disable analytics dashboard"
    )
    parser.add_argument(
        "--analytics-dashboard-path",
        type=str,
        default="/analytics",
        help="Path to analytics dashboard",
    )
    parser.add_argument(
        "--disable-analytics-export", action="store_true", help="Disable analytics export"
    )

    # Module configuration
    parser.add_argument(
        "--disable-niche-analysis", action="store_true", help="Disable niche analysis module"
    )
    parser.add_argument(
        "--disable-monetization", action="store_true", help="Disable monetization module"
    )
    parser.add_argument("--disable-marketing", action="store_true", help="Disable marketing module")
    parser.add_argument("--disable-ai-models", action="store_true", help="Disable AI models module")
    parser.add_argument(
        "--disable-agent-team", action="store_true", help="Disable agent team module"
    )
    parser.add_argument("--disable-user", action="store_true", help="Disable user module")
    parser.add_argument("--disable-dashboard", action="store_true", help="Disable dashboard module")

    return parser.parse_args()


def create_config(args: argparse.Namespace) -> APIConfig:
    """
    Create API configuration from command-line arguments.

    Args:
        args: Command-line arguments

    Returns:
        API configuration
    """
    # Parse active versions
    active_versions = []
    for version_str in args.active_versions.split(","):
        version_str = version_str.strip()
        if APIVersion.is_valid_version(version_str):
            for version in APIVersion:
                if version.value == version_str:
                    active_versions.append(version)
                    break
        else:
            logger.warning(f"Invalid API version: {version_str}")

    # If no valid versions were provided, use all available versions
    if not active_versions:
        active_versions = list(APIVersion)

    # Parse default version
    default_version = None
    if APIVersion.is_valid_version(args.version):
        for version in APIVersion:
            if version.value == args.version:
                default_version = version
                break

    # If default version is not valid or not in active versions, use the latest active version
    if default_version is None or default_version not in active_versions:
        default_version = max(active_versions, key=lambda v: list(APIVersion).index(v))

    config = APIConfig(
        # Basic configuration
        host=args.host,
        port=args.port,
        debug=args.debug,
        # API configuration
        prefix=args.prefix,
        version=default_version,
        active_versions=active_versions,
        enable_version_header=not args.disable_version_header,
        enable_version_deprecation_header=not args.disable_deprecation_header,
        # GraphQL configuration
        enable_graphql=not args.disable_graphql,
        graphql_path=args.graphql_path,
        graphiql=not args.disable_graphiql,
        graphql_batch_enabled=not args.disable_graphql_batch,
        graphql_introspection_enabled=not args.disable_graphql_introspection,
        graphql_playground=not args.disable_graphql_playground,
        # Security configuration
        enable_auth=args.enable_auth,
        enable_https=args.enable_https,
        ssl_keyfile=args.ssl_keyfile,
        ssl_certfile=args.ssl_certfile,
        # Rate limiting configuration
        enable_rate_limit=args.enable_rate_limit,
        rate_limit_strategy=RateLimitStrategy(args.rate_limit_strategy),
        rate_limit_scope=RateLimitScope(args.rate_limit_scope),
        rate_limit_requests=args.rate_limit_requests,
        rate_limit_period=args.rate_limit_period,
        rate_limit_burst=args.rate_limit_burst,
        enable_rate_limit_headers=not args.disable_rate_limit_headers,
        # Analytics configuration
        enable_analytics=not args.disable_analytics,
        analytics_db_path=args.analytics_db_path,
        analytics_retention_days=args.analytics_retention_days,
        analytics_dashboard_enabled=not args.disable_analytics_dashboard,
        analytics_dashboard_path=args.analytics_dashboard_path,
        analytics_export_enabled=not args.disable_analytics_export,
        # Module configuration
        enable_niche_analysis=not args.disable_niche_analysis,
        enable_monetization=not args.disable_monetization,
        enable_marketing=not args.disable_marketing,
        enable_ai_models=not args.disable_ai_models,
        enable_agent_team=not args.disable_agent_team,
        enable_user=not args.disable_user,
        enable_dashboard=not args.disable_dashboard,
    )

    return config


def main() -> None:
    """
    Main entry point for the API server.
    """
    # Parse command-line arguments
    args = parse_args()

    # Create API configuration
    config = create_config(args)

    # Create API server
    server = APIServer(config)

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

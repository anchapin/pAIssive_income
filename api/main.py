"""
"""
Main entry point for the API server.
Main entry point for the API server.


This module provides the main entry point for running the API server.
This module provides the main entry point for running the API server.
"""
"""




import argparse
import argparse
import logging
import logging
import os
import os
import sys
import sys
import time
import time


from api.config import APIConfig, APIVersion, RateLimitScope, RateLimitStrategy
from api.config import APIConfig, APIVersion, RateLimitScope, RateLimitStrategy
from api.server import APIServer
from api.server import APIServer


# Add the project root to the path so we can import modules
# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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




def parse_args() -> argparse.Namespace:
    def parse_args() -> argparse.Namespace:
    """
    """
    Parse command-line arguments.
    Parse command-line arguments.


    Returns:
    Returns:
    Parsed arguments
    Parsed arguments
    """
    """
    parser = argparse.ArgumentParser(description="pAIssive Income API Server")
    parser = argparse.ArgumentParser(description="pAIssive Income API Server")


    # Basic configuration
    # Basic configuration
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")


    # API configuration
    # API configuration
    parser.add_argument("--prefix", type=str, default="/api", help="API prefix")
    parser.add_argument("--prefix", type=str, default="/api", help="API prefix")
    parser.add_argument("--version", type=str, default="v2", help="Default API version")
    parser.add_argument("--version", type=str, default="v2", help="Default API version")
    parser.add_argument(
    parser.add_argument(
    "--active-versions",
    "--active-versions",
    type=str,
    type=str,
    default="v1,v2",
    default="v1,v2",
    help="Comma-separated list of active API versions",
    help="Comma-separated list of active API versions",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-version-header",
    "--disable-version-header",
    action="store_true",
    action="store_true",
    help="Disable API version header",
    help="Disable API version header",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-deprecation-header",
    "--disable-deprecation-header",
    action="store_true",
    action="store_true",
    help="Disable API deprecation header",
    help="Disable API deprecation header",
    )
    )


    # GraphQL configuration
    # GraphQL configuration
    parser.add_argument(
    parser.add_argument(
    "--disable-graphql", action="store_true", help="Disable GraphQL API"
    "--disable-graphql", action="store_true", help="Disable GraphQL API"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--graphql-path", type=str, default="/graphql", help="GraphQL endpoint path"
    "--graphql-path", type=str, default="/graphql", help="GraphQL endpoint path"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-graphiql", action="store_true", help="Disable GraphiQL interface"
    "--disable-graphiql", action="store_true", help="Disable GraphiQL interface"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-graphql-batch",
    "--disable-graphql-batch",
    action="store_true",
    action="store_true",
    help="Disable GraphQL batch processing",
    help="Disable GraphQL batch processing",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-graphql-introspection",
    "--disable-graphql-introspection",
    action="store_true",
    action="store_true",
    help="Disable GraphQL schema introspection",
    help="Disable GraphQL schema introspection",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-graphql-playground",
    "--disable-graphql-playground",
    action="store_true",
    action="store_true",
    help="Disable GraphQL Playground",
    help="Disable GraphQL Playground",
    )
    )


    # Security configuration
    # Security configuration
    parser.add_argument(
    parser.add_argument(
    "--enable-auth", action="store_true", help="Enable authentication"
    "--enable-auth", action="store_true", help="Enable authentication"
    )
    )
    parser.add_argument("--enable-https", action="store_true", help="Enable HTTPS")
    parser.add_argument("--enable-https", action="store_true", help="Enable HTTPS")
    parser.add_argument("--ssl-keyfile", type=str, help="SSL key file")
    parser.add_argument("--ssl-keyfile", type=str, help="SSL key file")
    parser.add_argument("--ssl-certfile", type=str, help="SSL certificate file")
    parser.add_argument("--ssl-certfile", type=str, help="SSL certificate file")


    # Rate limiting configuration
    # Rate limiting configuration
    parser.add_argument(
    parser.add_argument(
    "--enable-rate-limit", action="store_true", help="Enable rate limiting"
    "--enable-rate-limit", action="store_true", help="Enable rate limiting"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--rate-limit-strategy",
    "--rate-limit-strategy",
    type=str,
    type=str,
    default="token_bucket",
    default="token_bucket",
    choices=["fixed", "token_bucket", "leaky_bucket", "sliding_window"],
    choices=["fixed", "token_bucket", "leaky_bucket", "sliding_window"],
    help="Rate limiting strategy",
    help="Rate limiting strategy",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--rate-limit-scope",
    "--rate-limit-scope",
    type=str,
    type=str,
    default="ip",
    default="ip",
    choices=["global", "ip", "api_key", "user", "endpoint"],
    choices=["global", "ip", "api_key", "user", "endpoint"],
    help="Rate limiting scope",
    help="Rate limiting scope",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--rate-limit-requests",
    "--rate-limit-requests",
    type=int,
    type=int,
    default=100,
    default=100,
    help="Maximum number of requests per period",
    help="Maximum number of requests per period",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--rate-limit-period", type=int, default=60, help="Rate limit period in seconds"
    "--rate-limit-period", type=int, default=60, help="Rate limit period in seconds"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--rate-limit-burst",
    "--rate-limit-burst",
    type=int,
    type=int,
    default=50,
    default=50,
    help="Burst size for token bucket algorithm",
    help="Burst size for token bucket algorithm",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-rate-limit-headers",
    "--disable-rate-limit-headers",
    action="store_true",
    action="store_true",
    help="Disable rate limit headers",
    help="Disable rate limit headers",
    )
    )


    # Analytics configuration
    # Analytics configuration
    parser.add_argument(
    parser.add_argument(
    "--disable-analytics", action="store_true", help="Disable API analytics"
    "--disable-analytics", action="store_true", help="Disable API analytics"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--analytics-db-path", type=str, help="Path to analytics database"
    "--analytics-db-path", type=str, help="Path to analytics database"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--analytics-retention-days",
    "--analytics-retention-days",
    type=int,
    type=int,
    default=365,
    default=365,
    help="Number of days to retain analytics data",
    help="Number of days to retain analytics data",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-analytics-dashboard",
    "--disable-analytics-dashboard",
    action="store_true",
    action="store_true",
    help="Disable analytics dashboard",
    help="Disable analytics dashboard",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--analytics-dashboard-path",
    "--analytics-dashboard-path",
    type=str,
    type=str,
    default="/analytics",
    default="/analytics",
    help="Path to analytics dashboard",
    help="Path to analytics dashboard",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-analytics-export",
    "--disable-analytics-export",
    action="store_true",
    action="store_true",
    help="Disable analytics export",
    help="Disable analytics export",
    )
    )


    # Module configuration
    # Module configuration
    parser.add_argument(
    parser.add_argument(
    "--disable-niche-analysis",
    "--disable-niche-analysis",
    action="store_true",
    action="store_true",
    help="Disable niche analysis module",
    help="Disable niche analysis module",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-monetization",
    "--disable-monetization",
    action="store_true",
    action="store_true",
    help="Disable monetization module",
    help="Disable monetization module",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-marketing", action="store_true", help="Disable marketing module"
    "--disable-marketing", action="store_true", help="Disable marketing module"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-ai-models", action="store_true", help="Disable AI models module"
    "--disable-ai-models", action="store_true", help="Disable AI models module"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-agent-team", action="store_true", help="Disable agent team module"
    "--disable-agent-team", action="store_true", help="Disable agent team module"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-user", action="store_true", help="Disable user module"
    "--disable-user", action="store_true", help="Disable user module"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--disable-dashboard", action="store_true", help="Disable dashboard module"
    "--disable-dashboard", action="store_true", help="Disable dashboard module"
    )
    )


    return parser.parse_args()
    return parser.parse_args()




    def create_config(args: argparse.Namespace) -> APIConfig:
    def create_config(args: argparse.Namespace) -> APIConfig:
    """
    """
    Create API configuration from command-line arguments.
    Create API configuration from command-line arguments.


    Args:
    Args:
    args: Command-line arguments
    args: Command-line arguments


    Returns:
    Returns:
    API configuration
    API configuration
    """
    """
    # Parse active versions
    # Parse active versions
    active_versions = []
    active_versions = []
    for version_str in args.active_versions.split(","):
    for version_str in args.active_versions.split(","):
    version_str = version_str.strip()
    version_str = version_str.strip()
    if APIVersion.is_valid_version(version_str):
    if APIVersion.is_valid_version(version_str):
    for version in APIVersion:
    for version in APIVersion:
    if version.value == version_str:
    if version.value == version_str:
    active_versions.append(version)
    active_versions.append(version)
    break
    break
    else:
    else:
    logger.warning(f"Invalid API version: {version_str}")
    logger.warning(f"Invalid API version: {version_str}")


    # If no valid versions were provided, use all available versions
    # If no valid versions were provided, use all available versions
    if not active_versions:
    if not active_versions:
    active_versions = list(APIVersion)
    active_versions = list(APIVersion)


    # Parse default version
    # Parse default version
    default_version = None
    default_version = None
    if APIVersion.is_valid_version(args.version):
    if APIVersion.is_valid_version(args.version):
    for version in APIVersion:
    for version in APIVersion:
    if version.value == args.version:
    if version.value == args.version:
    default_version = version
    default_version = version
    break
    break


    # If default version is not valid or not in active versions, use the latest active version
    # If default version is not valid or not in active versions, use the latest active version
    if default_version is None or default_version not in active_versions:
    if default_version is None or default_version not in active_versions:
    default_version = max(active_versions, key=lambda v: list(APIVersion).index(v))
    default_version = max(active_versions, key=lambda v: list(APIVersion).index(v))


    config = APIConfig(
    config = APIConfig(
    # Basic configuration
    # Basic configuration
    host=args.host,
    host=args.host,
    port=args.port,
    port=args.port,
    debug=args.debug,
    debug=args.debug,
    # API configuration
    # API configuration
    prefix=args.prefix,
    prefix=args.prefix,
    version=default_version,
    version=default_version,
    active_versions=active_versions,
    active_versions=active_versions,
    enable_version_header=not args.disable_version_header,
    enable_version_header=not args.disable_version_header,
    enable_version_deprecation_header=not args.disable_deprecation_header,
    enable_version_deprecation_header=not args.disable_deprecation_header,
    # GraphQL configuration
    # GraphQL configuration
    enable_graphql=not args.disable_graphql,
    enable_graphql=not args.disable_graphql,
    graphql_path=args.graphql_path,
    graphql_path=args.graphql_path,
    graphiql=not args.disable_graphiql,
    graphiql=not args.disable_graphiql,
    graphql_batch_enabled=not args.disable_graphql_batch,
    graphql_batch_enabled=not args.disable_graphql_batch,
    graphql_introspection_enabled=not args.disable_graphql_introspection,
    graphql_introspection_enabled=not args.disable_graphql_introspection,
    graphql_playground=not args.disable_graphql_playground,
    graphql_playground=not args.disable_graphql_playground,
    # Security configuration
    # Security configuration
    enable_auth=args.enable_auth,
    enable_auth=args.enable_auth,
    enable_https=args.enable_https,
    enable_https=args.enable_https,
    ssl_keyfile=args.ssl_keyfile,
    ssl_keyfile=args.ssl_keyfile,
    ssl_certfile=args.ssl_certfile,
    ssl_certfile=args.ssl_certfile,
    # Rate limiting configuration
    # Rate limiting configuration
    enable_rate_limit=args.enable_rate_limit,
    enable_rate_limit=args.enable_rate_limit,
    rate_limit_strategy=RateLimitStrategy(args.rate_limit_strategy),
    rate_limit_strategy=RateLimitStrategy(args.rate_limit_strategy),
    rate_limit_scope=RateLimitScope(args.rate_limit_scope),
    rate_limit_scope=RateLimitScope(args.rate_limit_scope),
    rate_limit_requests=args.rate_limit_requests,
    rate_limit_requests=args.rate_limit_requests,
    rate_limit_period=args.rate_limit_period,
    rate_limit_period=args.rate_limit_period,
    rate_limit_burst=args.rate_limit_burst,
    rate_limit_burst=args.rate_limit_burst,
    enable_rate_limit_headers=not args.disable_rate_limit_headers,
    enable_rate_limit_headers=not args.disable_rate_limit_headers,
    # Analytics configuration
    # Analytics configuration
    enable_analytics=not args.disable_analytics,
    enable_analytics=not args.disable_analytics,
    analytics_db_path=args.analytics_db_path,
    analytics_db_path=args.analytics_db_path,
    analytics_retention_days=args.analytics_retention_days,
    analytics_retention_days=args.analytics_retention_days,
    analytics_dashboard_enabled=not args.disable_analytics_dashboard,
    analytics_dashboard_enabled=not args.disable_analytics_dashboard,
    analytics_dashboard_path=args.analytics_dashboard_path,
    analytics_dashboard_path=args.analytics_dashboard_path,
    analytics_export_enabled=not args.disable_analytics_export,
    analytics_export_enabled=not args.disable_analytics_export,
    # Module configuration
    # Module configuration
    enable_niche_analysis=not args.disable_niche_analysis,
    enable_niche_analysis=not args.disable_niche_analysis,
    enable_monetization=not args.disable_monetization,
    enable_monetization=not args.disable_monetization,
    enable_marketing=not args.disable_marketing,
    enable_marketing=not args.disable_marketing,
    enable_ai_models=not args.disable_ai_models,
    enable_ai_models=not args.disable_ai_models,
    enable_agent_team=not args.disable_agent_team,
    enable_agent_team=not args.disable_agent_team,
    enable_user=not args.disable_user,
    enable_user=not args.disable_user,
    enable_dashboard=not args.disable_dashboard,
    enable_dashboard=not args.disable_dashboard,
    )
    )


    return config
    return config




    def main() -> None:
    def main() -> None:
    """
    """
    Main entry point for the API server.
    Main entry point for the API server.
    """
    """
    # Parse command-line arguments
    # Parse command-line arguments
    args = parse_args()
    args = parse_args()


    # Create API configuration
    # Create API configuration
    config = create_config(args)
    config = create_config(args)


    # Create API server
    # Create API server
    server = APIServer(config)
    server = APIServer(config)


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
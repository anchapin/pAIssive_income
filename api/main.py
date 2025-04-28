"""
Main entry point for the API server.

This module provides the main entry point for running the API server.
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import API server
from api.server import APIServer
from api.config import APIConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # API configuration
    parser.add_argument("--prefix", type=str, default="/api", help="API prefix")
    parser.add_argument("--version", type=str, default="v1", help="API version")
    
    # Security configuration
    parser.add_argument("--enable-auth", action="store_true", help="Enable authentication")
    parser.add_argument("--enable-https", action="store_true", help="Enable HTTPS")
    parser.add_argument("--ssl-keyfile", type=str, help="SSL key file")
    parser.add_argument("--ssl-certfile", type=str, help="SSL certificate file")
    
    # Module configuration
    parser.add_argument("--disable-niche-analysis", action="store_true", help="Disable niche analysis module")
    parser.add_argument("--disable-monetization", action="store_true", help="Disable monetization module")
    parser.add_argument("--disable-marketing", action="store_true", help="Disable marketing module")
    parser.add_argument("--disable-ai-models", action="store_true", help="Disable AI models module")
    parser.add_argument("--disable-agent-team", action="store_true", help="Disable agent team module")
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
    config = APIConfig(
        # Basic configuration
        host=args.host,
        port=args.port,
        debug=args.debug,
        
        # API configuration
        prefix=args.prefix,
        version=args.version,
        
        # Security configuration
        enable_auth=args.enable_auth,
        enable_https=args.enable_https,
        ssl_keyfile=args.ssl_keyfile,
        ssl_certfile=args.ssl_certfile,
        
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

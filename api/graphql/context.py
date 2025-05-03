"""
Context module for GraphQL requests.

This module provides context for GraphQL requests, including access to
services, repositories, and other dependencies needed by resolvers.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import Request

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def get_context(request: Request) -> Dict[str, Any]:
    """
    Get GraphQL context for a request.

    This function is called for each GraphQL request to provide
    the context object that will be passed to all resolvers.

    Args:
        request: FastAPI request object

    Returns:
        GraphQL context dictionary
    """
    # Get services from app state
    services = {}

    if hasattr(request.app, "state"):
        # Get niche analysis service
        if hasattr(request.app.state, "niche_analysis_service"):
            services["niche_analysis"] = request.app.state.niche_analysis_service

        # Get monetization service
        if hasattr(request.app.state, "monetization_service"):
            services["monetization"] = request.app.state.monetization_service

        # Get marketing service
        if hasattr(request.app.state, "marketing_service"):
            services["marketing"] = request.app.state.marketing_service

        # Get ai models service
        if hasattr(request.app.state, "ai_models_service"):
            services["ai_models"] = request.app.state.ai_models_service

        # Get agent team service
        if hasattr(request.app.state, "agent_team_service"):
            services["agent_team"] = request.app.state.agent_team_service

        # Get user service
        if hasattr(request.app.state, "user_service"):
            services["user"] = request.app.state.user_service

    # Basic context
    context = {
        "request": request,
        "services": services,
        "user": None,  # Will be set by auth middleware if applicable
    }

    # Get user from request state (if authenticated)
    if hasattr(request.state, "user"):
        context["user"] = request.state.user

    return context

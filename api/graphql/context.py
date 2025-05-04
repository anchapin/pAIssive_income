"""
"""
Context module for GraphQL requests.
Context module for GraphQL requests.


This module provides context for GraphQL requests, including access to
This module provides context for GraphQL requests, including access to
services, repositories, and other dependencies needed by resolvers.
services, repositories, and other dependencies needed by resolvers.
"""
"""




import logging
import logging
from typing import Any, Dict
from typing import Any, Dict


from fastapi import Request
from fastapi import Request


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




async def get_context(request: Request) -> Dict[str, Any]:
    async def get_context(request: Request) -> Dict[str, Any]:
    """
    """
    Get GraphQL context for a request.
    Get GraphQL context for a request.


    This function is called for each GraphQL request to provide
    This function is called for each GraphQL request to provide
    the context object that will be passed to all resolvers.
    the context object that will be passed to all resolvers.


    Args:
    Args:
    request: FastAPI request object
    request: FastAPI request object


    Returns:
    Returns:
    GraphQL context dictionary
    GraphQL context dictionary
    """
    """
    # Get services from app state
    # Get services from app state
    services = {}
    services = {}


    if hasattr(request.app, "state"):
    if hasattr(request.app, "state"):
    # Get niche analysis service
    # Get niche analysis service
    if hasattr(request.app.state, "niche_analysis_service"):
    if hasattr(request.app.state, "niche_analysis_service"):
    services["niche_analysis"] = request.app.state.niche_analysis_service
    services["niche_analysis"] = request.app.state.niche_analysis_service


    # Get monetization service
    # Get monetization service
    if hasattr(request.app.state, "monetization_service"):
    if hasattr(request.app.state, "monetization_service"):
    services["monetization"] = request.app.state.monetization_service
    services["monetization"] = request.app.state.monetization_service


    # Get marketing service
    # Get marketing service
    if hasattr(request.app.state, "marketing_service"):
    if hasattr(request.app.state, "marketing_service"):
    services["marketing"] = request.app.state.marketing_service
    services["marketing"] = request.app.state.marketing_service


    # Get ai models service
    # Get ai models service
    if hasattr(request.app.state, "ai_models_service"):
    if hasattr(request.app.state, "ai_models_service"):
    services["ai_models"] = request.app.state.ai_models_service
    services["ai_models"] = request.app.state.ai_models_service


    # Get agent team service
    # Get agent team service
    if hasattr(request.app.state, "agent_team_service"):
    if hasattr(request.app.state, "agent_team_service"):
    services["agent_team"] = request.app.state.agent_team_service
    services["agent_team"] = request.app.state.agent_team_service


    # Get user service
    # Get user service
    if hasattr(request.app.state, "user_service"):
    if hasattr(request.app.state, "user_service"):
    services["user"] = request.app.state.user_service
    services["user"] = request.app.state.user_service


    # Basic context
    # Basic context
    context = {
    context = {
    "request": request,
    "request": request,
    "services": services,
    "services": services,
    "user": None,  # Will be set by auth middleware if applicable
    "user": None,  # Will be set by auth middleware if applicable
    }
    }


    # Get user from request state (if authenticated)
    # Get user from request state (if authenticated)
    if hasattr(request.state, "user"):
    if hasattr(request.state, "user"):
    context["user"] = request.state.user
    context["user"] = request.state.user


    return context
    return context
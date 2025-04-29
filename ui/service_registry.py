"""
Service registry module.

This module provides functions for registering and accessing services
without creating circular dependencies.
"""

from typing import Any, Type
from dependency_container import get_container

def register_ui_services():
    """Register UI services in the dependency container."""
    from interfaces.ui_interfaces import (
        IAgentTeamService, INicheAnalysisService, IDeveloperService,
        IMonetizationService, IMarketingService
    )
    from .services.agent_team_service import AgentTeamService
    from .services.niche_analysis_service import NicheAnalysisService
    from .services.developer_service import DeveloperService
    from .services.monetization_service import MonetizationService
    from .services.marketing_service import MarketingService

    container = get_container()

    # Register agent team service
    container.register(
        IAgentTeamService,
        lambda: AgentTeamService(agent_team=container.resolve('IAgentTeam')),
        singleton=True
    )

    # Register niche analysis service
    container.register(
        INicheAnalysisService,
        lambda: NicheAnalysisService(),
        singleton=True
    )

    # Register developer service
    container.register(
        IDeveloperService,
        lambda: DeveloperService(),
        singleton=True
    )

    # Register monetization service
    container.register(
        IMonetizationService,
        lambda: MonetizationService(),
        singleton=True
    )

    # Register marketing service
    container.register(
        IMarketingService,
        lambda: MarketingService(),
        singleton=True
    )

def get_service(service_type: Type) -> Any:
    """
    Get any service from the dependency container.
    This is the main service locator function to be used by all modules.

    Args:
        service_type: Type of service to get

    Returns:
        Service instance
    """
    container = get_container()
    return container.resolve(service_type)

def get_ui_service(service_type: Type) -> Any:
    """
    Get a UI service from the dependency container.
    This is a specialized service locator function for UI services.

    Args:
        service_type: Type of UI service to get (should be one of the UI interface types)

    Returns:
        UI service instance
    """
    return get_service(service_type)
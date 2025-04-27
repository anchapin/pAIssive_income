"""
Service initialization for the pAIssive_income project.

This module provides functions for initializing and configuring services
used by the project, including dependency injection setup.
"""

import os
import logging
from typing import Dict, Any, Optional, Type

from dependency_container import get_container, DependencyContainer
from interfaces.agent_interfaces import IAgentTeam, IAgentProfile, IResearchAgent
from interfaces.model_interfaces import IModelManager, IModelConfig, IModelAdapter
from interfaces.niche_interfaces import INicheAnalyzer
from interfaces.monetization_interfaces import IMonetizationCalculator
from interfaces.marketing_interfaces import IMarketingStrategy

from agent_team import AgentTeam, ResearchAgent, AgentProfile

from ai_models.model_manager import ModelManager
from ai_models.model_config import ModelConfig
from ai_models.adapters import get_adapter_factory

from niche_analysis.niche_analyzer import NicheAnalyzer
from monetization.calculator import MonetizationCalculator
from marketing.strategy_generator import StrategyGenerator

# Set up logging
logger = logging.getLogger(__name__)


def initialize_services(config: Optional[Dict[str, Any]] = None) -> DependencyContainer:
    """
    Initialize all services and register them in the dependency container.

    Args:
        config: Optional configuration dictionary

    Returns:
        Dependency container with registered services
    """
    container = get_container()

    # Register configuration
    _register_configuration(container, config)

    # Register AI models
    _register_ai_models(container)

    # Register agent team
    _register_agent_team(container)

    # Register niche analysis
    _register_niche_analysis(container)

    # Register monetization
    _register_monetization(container)

    # Register marketing
    _register_marketing(container)

    logger.info("All services initialized and registered")
    return container


def _register_configuration(container: DependencyContainer, config: Optional[Dict[str, Any]] = None) -> None:
    """
    Register configuration in the dependency container.

    Args:
        container: Dependency container
        config: Optional configuration dictionary
    """
    # Register model configuration
    if config and "model_config" in config:
        model_config = ModelConfig(**config["model_config"])
    else:
        model_config = ModelConfig.get_default()

    container.register(IModelConfig, lambda: model_config, singleton=True)
    logger.info("Registered model configuration")


def _register_ai_models(container: DependencyContainer) -> None:
    """
    Register AI model services in the dependency container.

    Args:
        container: Dependency container
    """
    # Register model manager
    container.register(
        IModelManager,
        lambda: ModelManager(config=container.resolve(IModelConfig)),
        singleton=True
    )

    # Register adapter factory
    adapter_factory = get_adapter_factory()
    container.register_instance("adapter_factory", adapter_factory)

    logger.info("Registered AI model services")


def _register_agent_team(container: DependencyContainer) -> None:
    """
    Register agent team services in the dependency container.

    Args:
        container: Dependency container
    """
    # Register agent profile
    container.register(
        IAgentProfile,
        lambda: AgentProfile(name="default"),
        singleton=True
    )

    # Register research agent
    container.register(
        IResearchAgent,
        lambda: ResearchAgent(
            profile=container.resolve(IAgentProfile),
            model_manager=container.resolve(IModelManager)
        ),
        singleton=True
    )

    # Register agent team
    container.register(
        IAgentTeam,
        lambda: AgentTeam(
            research_agent=container.resolve(IResearchAgent)
        ),
        singleton=True
    )

    logger.info("Registered agent team services")


def _register_niche_analysis(container: DependencyContainer) -> None:
    """
    Register niche analysis services in the dependency container.

    Args:
        container: Dependency container
    """
    # Register niche analyzer
    container.register(
        INicheAnalyzer,
        lambda: NicheAnalyzer(
            agent_team=container.resolve(IAgentTeam)
        ),
        singleton=True
    )

    logger.info("Registered niche analysis services")


def _register_monetization(container: DependencyContainer) -> None:
    """
    Register monetization services in the dependency container.

    Args:
        container: Dependency container
    """
    # Register monetization calculator
    container.register(
        IMonetizationCalculator,
        lambda: MonetizationCalculator(),
        singleton=True
    )

    logger.info("Registered monetization services")


def _register_marketing(container: DependencyContainer) -> None:
    """
    Register marketing services in the dependency container.

    Args:
        container: Dependency container
    """
    # Register marketing strategy generator
    container.register(
        IMarketingStrategy,
        lambda: StrategyGenerator(
            agent_team=container.resolve(IAgentTeam)
        ),
        singleton=True
    )

    logger.info("Registered marketing services")


def get_service(service_type: Type) -> Any:
    """
    Get a service from the dependency container.

    Args:
        service_type: Type of service to get

    Returns:
        Service instance
    """
    container = get_container()
    return container.resolve(service_type)
